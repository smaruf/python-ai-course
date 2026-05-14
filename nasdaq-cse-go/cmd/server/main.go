// Package main provides the main HTTP server for the Gold Derivatives Trading Simulator
package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/aiassistant"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/communication"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/dealer"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/marketdata"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/oms"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/rms"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/storage"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/terminal"
)

// Server holds all service dependencies
type Server struct {
	db              *storage.DatabaseManager
	jsonStorage     *storage.JSONStorage
	marketData      *marketdata.MarketDataService
	orderManager    *oms.OrderManager
	riskManager     *rms.RiskManager
	tradingBot      *aiassistant.TradingBot
	commManager     *communication.CommunicationManager
	dealerManager   *dealer.Manager
	terminalParser  *terminal.Parser
	wsConnections   map[*websocket.Conn]bool
	wsUpgrader      websocket.Upgrader
}

// NewServer creates a new server instance
func NewServer() (*Server, error) {
	// Initialize database
	db, err := storage.NewDatabaseManager("./trading_simulator.db")
	if err != nil {
		return nil, fmt.Errorf("failed to initialize database: %w", err)
	}

	// Initialize JSON storage
	jsonStorage, err := storage.NewJSONStorage("./data")
	if err != nil {
		return nil, fmt.Errorf("failed to initialize JSON storage: %w", err)
	}

	// Initialize services
	marketData := marketdata.NewMarketDataService()
	orderManager := oms.NewOrderManager(db.GetDB())
	riskManager := rms.NewRiskManager(db.GetDB())
	tradingBot := aiassistant.NewTradingBot()
	commManager := communication.NewCommunicationManager()
	dealerMgr := dealer.NewManager(db.GetDB())
	termParser := terminal.NewParser(dealerMgr)

	// WebSocket upgrader
	wsUpgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true // Allow all origins for demo
		},
	}

	server := &Server{
		db:             db,
		jsonStorage:    jsonStorage,
		marketData:     marketData,
		orderManager:   orderManager,
		riskManager:    riskManager,
		tradingBot:     tradingBot,
		commManager:    commManager,
		dealerManager:  dealerMgr,
		terminalParser: termParser,
		wsConnections:  make(map[*websocket.Conn]bool),
		wsUpgrader:     wsUpgrader,
	}

	// Start background tasks
	go server.marketDataUpdater()
	go server.positionUpdater()

	return server, nil
}

// Close closes all server resources
func (s *Server) Close() error {
	if err := s.commManager.Disconnect(); err != nil {
		log.Printf("Error disconnecting communication manager: %v", err)
	}
	return s.db.Close()
}

// setupRoutes sets up all HTTP routes
func (s *Server) setupRoutes() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()

	// CORS middleware
	router.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Accept, Authorization")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		
		c.Next()
	})

	// Serve static files
	router.Static("/static", "./web/static")

	// Main trading interface
	router.GET("/", s.handleRoot)

	// API routes
	api := router.Group("/api")
	{
		// Market data
		api.GET("/market-data", s.handleGetMarketData)
		api.GET("/charts/price", s.handleGetPriceChart)
		api.GET("/charts/pnl", s.handleGetPnLChart)

		// Orders
		api.POST("/orders", s.handleSubmitOrder)
		api.DELETE("/orders/:order_id", s.handleCancelOrder)
		api.GET("/orders", s.handleGetOrders)

		// Trades and positions
		api.GET("/trades", s.handleGetTrades)
		api.GET("/positions", s.handleGetPositions)

		// AI assistant
		api.POST("/ai/chat", s.handleAIChat)
		api.POST("/ai/analyze", s.handleAIAnalyze)

		// Risk management
		api.GET("/risk/report", s.handleRiskReport)
		api.GET("/risk/margin", s.handleMarginStatus)

		// Multi-BO dealer workstation
		api.POST("/terminal/command", s.handleTerminalCommand)
		api.GET("/dealer/context", s.handleGetDealerContext)
		api.POST("/dealer/switch-bo", s.handleSwitchBO)
		api.GET("/dealer/bo-list", s.handleListBOs)
		api.GET("/dealer/groups", s.handleListGroups)
		api.GET("/dealer/risk-dashboard", s.handleDealerRiskDashboard)
		api.GET("/dealer/audit", s.handleGetAuditLog)
		api.GET("/bo/:bo_id/dashboard", s.handleBODashboard)
		api.GET("/bo/:bo_id/positions", s.handleBOPositions)
		api.GET("/bo/:bo_id/orders", s.handleBOOrders)
		api.GET("/bo/:bo_id/watchlist", s.handleGetWatchlist)
		api.POST("/bo/:bo_id/watchlist", s.handleAddWatchlist)
		api.GET("/bo/search", s.handleBOSearch)
		api.POST("/bo/order", s.handleSubmitBOOrder)
		api.POST("/bo/group-order", s.handleGroupOrder)
		api.POST("/bo/basket-order", s.handleBasketOrder)
		api.POST("/bo/alloc-order", s.handleAllocOrder)
		api.POST("/bo/clone-order", s.handleCloneOrder)
	}

	// WebSocket endpoint
	router.GET("/ws", s.handleWebSocket)

	return router
}

// handleRoot serves the Bloomberg-style multi-BO dealer workstation UI
func (s *Server) handleRoot(c *gin.Context) {
	html := `<!DOCTYPE html>
<html>
<head>
    <title>Bloomberg-Lite Multi-BO Dealer Workstation</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Courier New', monospace; background: #0a0a0a; color: #e0e0e0; height: 100vh; overflow: hidden; }
        /* Header */
        #header { background: #1a1a2e; color: #f0c040; padding: 6px 12px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f0c040; font-size: 13px; }
        #header h1 { font-size: 14px; letter-spacing: 2px; }
        #active-bo { background: #222; color: #4fc3f7; padding: 3px 10px; border: 1px solid #4fc3f7; border-radius: 3px; font-size: 12px; }
        /* Main layout */
        #workspace { display: grid; grid-template-columns: 200px 1fr 280px; grid-template-rows: 1fr 180px; height: calc(100vh - 36px); gap: 2px; background: #111; padding: 2px; }
        /* Panels */
        .panel { background: #0f0f1a; border: 1px solid #2a2a4a; overflow: hidden; display: flex; flex-direction: column; }
        .panel-title { background: #1a1a3e; color: #f0c040; padding: 4px 8px; font-size: 11px; font-weight: bold; letter-spacing: 1px; border-bottom: 1px solid #2a2a4a; flex-shrink: 0; }
        .panel-body { flex: 1; overflow-y: auto; padding: 6px; font-size: 11px; }
        /* BO List */
        #bo-list-panel { grid-row: 1 / 3; }
        .bo-item { padding: 4px 6px; cursor: pointer; border-bottom: 1px solid #1a1a2e; border-radius: 2px; }
        .bo-item:hover { background: #1a2a3a; }
        .bo-item.active { background: #0a2a4a; border-left: 3px solid #4fc3f7; }
        .bo-id { color: #4fc3f7; font-weight: bold; font-size: 12px; }
        .bo-name { color: #aaa; font-size: 10px; }
        .bo-bp { color: #4caf50; font-size: 10px; }
        /* Main area */
        #main-area { grid-column: 2; grid-row: 1; display: grid; grid-template-rows: 1fr 1fr; gap: 2px; }
        /* Positions & depth */
        #depth-panel { }
        #positions-panel { }
        table { width: 100%; border-collapse: collapse; font-size: 11px; }
        th { background: #1a1a3e; color: #f0c040; padding: 3px 6px; text-align: left; position: sticky; top: 0; }
        td { padding: 3px 6px; border-bottom: 1px solid #1a1a2e; }
        tr:hover td { background: #1a1a2e; }
        .pos { color: #4caf50; }
        .neg { color: #ef5350; }
        /* Orders panel */
        #orders-panel { grid-column: 3; grid-row: 1; }
        /* Dashboard */
        #dashboard-panel { grid-column: 2 / 4; grid-row: 2; }
        /* Terminal */
        #terminal-panel { grid-column: 2 / 4; grid-row: 2; display: flex; flex-direction: column; }
        #terminal-output { flex: 1; overflow-y: auto; padding: 6px; font-size: 11px; font-family: 'Courier New', monospace; background: #050510; color: #c8e6c9; white-space: pre-wrap; }
        #terminal-input-row { display: flex; padding: 4px; background: #0a0a1a; border-top: 1px solid #2a2a4a; }
        #terminal-prompt { color: #f0c040; padding: 4px 6px; font-size: 12px; }
        #terminal-input { flex: 1; background: transparent; border: none; color: #e0e0e0; font-family: 'Courier New', monospace; font-size: 12px; outline: none; }
        .cmd-ok { color: #4caf50; }
        .cmd-err { color: #ef5350; }
        .cmd-info { color: #4fc3f7; }
        /* Market strip */
        #market-strip { background: #050518; border-bottom: 1px solid #2a2a4a; padding: 3px 8px; font-size: 11px; display: flex; gap: 20px; flex-wrap: wrap; }
        .quote-item { display: flex; gap: 6px; }
        .sym { color: #f0c040; font-weight: bold; }
        .ltp { color: #e0e0e0; }
        .chg-pos { color: #4caf50; }
        .chg-neg { color: #ef5350; }
        /* Scrollbar */
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0a0a0a; }
        ::-webkit-scrollbar-thumb { background: #2a2a4a; border-radius: 2px; }
        .badge-hni { color: #ff9800; } .badge-margin { color: #ef5350; } .badge-inst { color: #9c27b0; }
        .badge-prop { color: #f0c040; } .badge-family { color: #4fc3f7; }
    </style>
</head>
<body>
<div id="header">
    <h1>&#9632; BLOOMBERG-LITE DEALER WORKSTATION &mdash; CSE/DSE</h1>
    <div style="display:flex;gap:10px;align-items:center;">
        <div id="ws-status" style="color:#ef5350;font-size:11px;">&#9679; WS</div>
        <div>Dealer: <strong style="color:#f0c040;">demo_trader</strong></div>
        <div id="active-bo">Active BO: NONE</div>
        <div id="clock" style="color:#888;font-size:11px;"></div>
    </div>
</div>

<div id="market-strip" id="market-strip">
    <span class="quote-item"><span class="sym">GP</span> <span class="ltp" id="q-GP">350.00</span> <span class="chg-pos">+1.50</span></span>
    <span class="quote-item"><span class="sym">BATBC</span> <span class="ltp" id="q-BATBC">25.40</span> <span class="chg-neg">-0.10</span></span>
    <span class="quote-item"><span class="sym">SQPH</span> <span class="ltp" id="q-SQPH">220.00</span> <span class="chg-pos">+2.00</span></span>
    <span class="quote-item"><span class="sym">BRAC</span> <span class="ltp" id="q-BRAC">45.00</span> <span class="chg-pos">+0.50</span></span>
    <span class="quote-item"><span class="sym">ROBI</span> <span class="ltp" id="q-ROBI">18.50</span> <span class="chg-neg">-0.20</span></span>
    <span class="quote-item"><span class="sym">LHBL</span> <span class="ltp" id="q-LHBL">60.00</span> <span class="chg-pos">+1.00</span></span>
</div>

<div id="workspace">
    <!-- BO List -->
    <div class="panel" id="bo-list-panel">
        <div class="panel-title">&#9632; BO ACCOUNTS</div>
        <div class="panel-body" id="bo-list">Loading...</div>
    </div>

    <!-- Main area: depth + positions -->
    <div id="main-area">
        <div class="panel" id="positions-panel">
            <div class="panel-title">&#9632; POSITIONS</div>
            <div class="panel-body">
                <table id="pos-table">
                    <thead><tr><th>Symbol</th><th>Qty</th><th>Avg</th><th>LTP</th><th>P/L</th></tr></thead>
                    <tbody id="pos-body"><tr><td colspan="5" style="color:#666;">Select a BO account</td></tr></tbody>
                </table>
            </div>
        </div>
        <div class="panel" id="depth-panel">
            <div class="panel-title">&#9632; OPEN ORDERS</div>
            <div class="panel-body">
                <table id="ord-table">
                    <thead><tr><th>ID</th><th>Side</th><th>Symbol</th><th>Qty</th><th>Price</th><th>Status</th></tr></thead>
                    <tbody id="ord-body"><tr><td colspan="6" style="color:#666;">Select a BO account</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Right: Orders / Dashboard -->
    <div class="panel" id="orders-panel">
        <div class="panel-title">&#9632; BO DASHBOARD</div>
        <div class="panel-body" id="bo-dashboard">
            <div style="color:#666;margin-top:20px;text-align:center;">Select a BO account<br>or type: dashboard BO1001</div>
        </div>
    </div>

    <!-- Terminal (bottom) -->
    <div class="panel" id="terminal-panel">
        <div class="panel-title">&#9632; TERMINAL &mdash; type <span style="color:#4fc3f7;">help</span> for commands</div>
        <div id="terminal-output">Bloomberg-Lite Terminal ready. Type <span class="cmd-info">help</span> for command reference.
Type <span class="cmd-info">b BO1001 GP 100 350</span> to buy, <span class="cmd-info">s BO1002 BATBC 500 25.4</span> to sell.
Type <span class="cmd-info">bo maruf</span> to search BO accounts.
</div>
        <div id="terminal-input-row">
            <span id="terminal-prompt">TERMINAL&gt;</span>
            <input id="terminal-input" type="text" autocomplete="off" spellcheck="false" placeholder="Enter command...">
        </div>
    </div>
</div>

<script>
const DEALER_ID = 1;
let activeBOID = null;
let ws = null;
let cmdHistory = [];
let histIdx = -1;

// Clock
function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString('en-GB');
}
setInterval(updateClock, 1000);
updateClock();

// WebSocket
function connectWS() {
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(proto + '//' + location.host + '/ws');
    ws.onopen = () => { document.getElementById('ws-status').style.color = '#4caf50'; };
    ws.onclose = () => { document.getElementById('ws-status').style.color = '#ef5350'; setTimeout(connectWS, 3000); };
    ws.onmessage = (e) => {
        try {
            const d = JSON.parse(e.data);
            if (d.type === 'market_data') updateMarketStrip(d.data);
        } catch(ex) {}
    };
}
connectWS();

function updateMarketStrip(data) {
    if (data.price) document.getElementById('q-GP').textContent = data.price.toFixed(2);
}

// Load BO list
function loadBOList() {
    fetch('/api/dealer/bo-list?dealer_id=' + DEALER_ID)
        .then(r => r.json())
        .then(bos => {
            const el = document.getElementById('bo-list');
            if (!bos || bos.length === 0) { el.textContent = 'No BO accounts'; return; }
            el.innerHTML = '';
            bos.forEach(bo => {
                const div = document.createElement('div');
                div.className = 'bo-item' + (bo.bo_id === activeBOID ? ' active' : '');
                div.dataset.boid = bo.bo_id;
                const badgeClass = {HNI:'badge-hni',MARGIN:'badge-margin',INSTITUTIONAL:'badge-inst',PROP:'badge-prop',FAMILY_OFFICE:'badge-family'}[bo.group_type] || '';
                div.innerHTML = '<div class="bo-id">' + bo.bo_id + '</div>' +
                    '<div class="bo-name">' + bo.client_name + '</div>' +
                    '<div class="bo-bp">BP: ' + formatNum(bo.buying_power) + ' <span class="' + badgeClass + '">' + bo.group_type + '</span></div>';
                div.onclick = () => selectBO(bo.bo_id);
                el.appendChild(div);
            });
        })
        .catch(() => {});
}

function selectBO(boID) {
    activeBOID = boID;
    document.getElementById('active-bo').textContent = 'Active BO: ' + boID;
    document.querySelectorAll('.bo-item').forEach(el => {
        el.classList.toggle('active', el.dataset.boid === boID);
    });
    loadBODashboard(boID);
    loadBOPositions(boID);
    loadBOOrders(boID);
    // Also switch server context
    fetch('/api/dealer/switch-bo', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({bo_id: boID, dealer_id: DEALER_ID})
    }).catch(() => {});
}

function loadBODashboard(boID) {
    fetch('/api/bo/' + boID + '/dashboard')
        .then(r => r.json())
        .then(d => {
            const el = document.getElementById('bo-dashboard');
            const pnlClass = d.unrealized_pnl >= 0 ? 'pos' : 'neg';
            el.innerHTML = '<div style="padding:8px;line-height:1.8">' +
                '<div>&#9632; <strong style="color:#4fc3f7">' + d.bo_id + '</strong> &mdash; ' + d.client_name + '</div>' +
                '<div>Buying Power: <strong style="color:#4caf50">' + formatNum(d.buying_power) + '</strong></div>' +
                '<div>Exposure: <strong>' + formatNum(d.exposure) + '</strong></div>' +
                '<div>Margin: <strong style="color:' + (d.margin_status==='OK'?'#4caf50':'#ef5350') + '">' + d.margin_status + '</strong></div>' +
                '<div>Holdings: <strong>' + d.holdings + '</strong></div>' +
                '<div>P/L: <strong class="' + pnlClass + '">' + formatNum(d.unrealized_pnl) + '</strong></div>' +
                '<div>Pending Orders: <strong>' + d.pending_orders + '</strong></div>' +
                '</div>';
        })
        .catch(() => {});
}

function loadBOPositions(boID) {
    fetch('/api/bo/' + boID + '/positions')
        .then(r => r.json())
        .then(positions => {
            const tbody = document.getElementById('pos-body');
            if (!positions || positions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="color:#666;">No open positions</td></tr>';
                return;
            }
            tbody.innerHTML = positions.map(p => {
                const pnlClass = p.unrealized_pnl >= 0 ? 'pos' : 'neg';
                return '<tr><td style="color:#f0c040">' + p.symbol + '</td>' +
                    '<td>' + p.quantity.toFixed(0) + '</td>' +
                    '<td>' + p.avg_price.toFixed(2) + '</td>' +
                    '<td>' + (p.ltp||0).toFixed(2) + '</td>' +
                    '<td class="' + pnlClass + '">' + (p.unrealized_pnl||0).toFixed(2) + '</td></tr>';
            }).join('');
        })
        .catch(() => {});
}

function loadBOOrders(boID) {
    fetch('/api/bo/' + boID + '/orders?limit=15')
        .then(r => r.json())
        .then(orders => {
            const tbody = document.getElementById('ord-body');
            if (!orders || orders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="color:#666;">No orders</td></tr>';
                return;
            }
            tbody.innerHTML = orders.map(o => {
                const sideColor = o.side === 'BUY' ? '#4caf50' : '#ef5350';
                const price = o.price ? o.price.toFixed(2) : 'MKT';
                return '<tr>' +
                    '<td style="color:#888">' + o.order_id.substring(0,8) + '</td>' +
                    '<td style="color:' + sideColor + '">' + o.side + '</td>' +
                    '<td style="color:#f0c040">' + o.symbol + '</td>' +
                    '<td>' + o.quantity.toFixed(0) + '</td>' +
                    '<td>' + price + '</td>' +
                    '<td style="color:#888">' + o.status + '</td></tr>';
            }).join('');
        })
        .catch(() => {});
}

// Terminal
const termInput = document.getElementById('terminal-input');
const termOutput = document.getElementById('terminal-output');

termInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
        const cmd = termInput.value.trim();
        if (!cmd) return;
        cmdHistory.unshift(cmd);
        histIdx = -1;
        termInput.value = '';
        appendTerminal('> ' + cmd, 'cmd-info');
        executeCommand(cmd);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (histIdx < cmdHistory.length - 1) { histIdx++; termInput.value = cmdHistory[histIdx]; }
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (histIdx > 0) { histIdx--; termInput.value = cmdHistory[histIdx]; }
        else { histIdx = -1; termInput.value = ''; }
    }
});

function executeCommand(cmd) {
    fetch('/api/terminal/command', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({command: cmd, dealer_id: DEALER_ID})
    })
    .then(r => r.json())
    .then(resp => {
        if (resp.success) {
            appendTerminal(resp.output, 'cmd-ok');
        } else {
            appendTerminal(resp.output || resp.error, 'cmd-err');
        }
        // Refresh if order-related command
        if (activeBOID && /^(b |bm |s |sm |clone|repeat|reverse|basket|alloc)/i.test(cmd)) {
            loadBOPositions(activeBOID);
            loadBOOrders(activeBOID);
            loadBODashboard(activeBOID);
            loadBOList();
        }
        if (/^switch/i.test(cmd)) {
            const m = cmd.match(/switch\s+(\S+)/i);
            if (m) { selectBO(m[1].toUpperCase()); }
        }
    })
    .catch(err => appendTerminal('Network error: ' + err, 'cmd-err'));
}

function appendTerminal(text, cls) {
    const span = document.createElement('span');
    span.className = cls || '';
    span.textContent = text + '\n';
    termOutput.appendChild(span);
    termOutput.scrollTop = termOutput.scrollHeight;
}

function formatNum(n) {
    if (!n && n !== 0) return '-';
    if (Math.abs(n) >= 1e7) return (n/1e7).toFixed(2) + 'Cr';
    if (Math.abs(n) >= 1e5) return (n/1e5).toFixed(2) + 'L';
    if (Math.abs(n) >= 1e3) return (n/1e3).toFixed(2) + 'K';
    return n.toFixed(2);
}

// Init
loadBOList();
termInput.focus();

// Refresh every 15s
setInterval(() => {
    loadBOList();
    if (activeBOID) {
        loadBOPositions(activeBOID);
        loadBODashboard(activeBOID);
    }
}, 15000);
</script>
</body>
</html>`
	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}
</head>
<body>
    <div class="header">
        <h1>🏆 NASDAQ CSE Gold Derivatives Trading Simulator</h1>
        <p>Advanced trading simulator with AI assistance and real-time risk management</p>
    </div>
    
    <div class="status disconnected" id="connectionStatus">
        🔴 Disconnected from WebSocket
    </div>
    
    <div class="container">
        <div class="card">
            <h2>📈 Current Gold Price</h2>
            <div class="price" id="currentPrice">Loading...</div>
            <div class="change" id="priceChange">--</div>
            <div style="margin-top: 10px;">
                <strong>Bid:</strong> <span id="bidPrice">--</span> | 
                <strong>Ask:</strong> <span id="askPrice">--</span>
            </div>
            <div><strong>Volume:</strong> <span id="volume">--</span></div>
        </div>
        
        <div class="card">
            <h2>🎯 Quick Actions</h2>
            <button onclick="submitTestOrder('BUY')" style="padding: 10px 20px; margin: 5px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer;">
                Buy Gold Futures
            </button>
            <button onclick="submitTestOrder('SELL')" style="padding: 10px 20px; margin: 5px; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer;">
                Sell Gold Futures
            </button>
            <div style="margin-top: 15px;">
                <h3>🤖 AI Assistant</h3>
                <input type="text" id="chatInput" placeholder="Ask me about trading..." style="width: 70%; padding: 8px;">
                <button onclick="sendChatMessage()" style="padding: 8px 15px; background: #3498db; color: white; border: none; border-radius: 3px; cursor: pointer;">Send</button>
                <div id="chatResponse" style="margin-top: 10px; padding: 10px; background: #ecf0f1; border-radius: 5px; min-height: 40px;"></div>
            </div>
        </div>
    </div>
    
    <div class="container" style="margin-top: 20px;">
        <div class="card">
            <h2>📊 System Features</h2>
            <ul>
                <li>✅ Real-time market data with WebSocket updates</li>
                <li>✅ AI-powered trading analysis and suggestions</li>
                <li>✅ Order Management System (OMS)</li>
                <li>✅ Risk Management System (RMS)</li>
                <li>✅ FIX/FAST protocol simulation</li>
                <li>✅ JSON data persistence</li>
                <li>✅ Interactive charts and analytics</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🛠️ API Endpoints</h2>
            <ul>
                <li><strong>GET /api/market-data</strong> - Current market data</li>
                <li><strong>POST /api/orders</strong> - Submit new order</li>
                <li><strong>GET /api/positions</strong> - Get user positions</li>
                <li><strong>POST /api/ai/chat</strong> - Chat with AI assistant</li>
                <li><strong>GET /api/risk/report</strong> - Risk analysis report</li>
                <li><strong>GET /ws</strong> - WebSocket for live updates</li>
            </ul>
        </div>
    </div>

    <script>
        let ws = null;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            
            ws.onopen = function() {
                document.getElementById('connectionStatus').innerHTML = '🟢 Connected to WebSocket';
                document.getElementById('connectionStatus').className = 'status connected';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'market_data') {
                    updateMarketData(data.data);
                }
            };
            
            ws.onclose = function() {
                document.getElementById('connectionStatus').innerHTML = '🔴 Disconnected from WebSocket';
                document.getElementById('connectionStatus').className = 'status disconnected';
                setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds
            };
        }
        
        function updateMarketData(data) {
            document.getElementById('currentPrice').textContent = '$' + data.price.toFixed(2);
            document.getElementById('bidPrice').textContent = '$' + data.bid.toFixed(2);
            document.getElementById('askPrice').textContent = '$' + data.ask.toFixed(2);
            document.getElementById('volume').textContent = data.volume.toLocaleString();
            
            const changeEl = document.getElementById('priceChange');
            const changePercent = (data.change_percent * 100).toFixed(2);
            changeEl.textContent = (data.change_percent >= 0 ? '+' : '') + changePercent + '%';
            changeEl.className = 'change ' + (data.change_percent >= 0 ? 'positive' : 'negative');
        }
        
        function submitTestOrder(side) {
            const orderData = {
                contract_symbol: 'GOLD2024DEC',
                side: side,
                order_type: 'MARKET',
                quantity: 1
            };
            
            fetch('/api/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Order submitted successfully! Order ID: ' + data.order_id);
                } else {
                    alert('Order failed: ' + data.error);
                }
            })
            .catch(error => alert('Error: ' + error));
        }
        
        function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (!message) return;
            
            fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, user_id: 1 })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('chatResponse').innerHTML = '<strong>AI:</strong> ' + data.response;
                input.value = '';
            })
            .catch(error => {
                document.getElementById('chatResponse').innerHTML = '<strong>Error:</strong> ' + error;
            });
        }
        
        // Initialize
        connectWebSocket();
        
        // Fetch initial market data
        fetch('/api/market-data')
            .then(response => response.json())
            .then(data => updateMarketData(data))
            .catch(error => console.error('Error fetching market data:', error));
    </script>
</body>
</html>`
	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// handleGetMarketData returns current market data
func (s *Server) handleGetMarketData(c *gin.Context) {
	marketData := s.marketData.GetCurrentPrice()
	c.JSON(http.StatusOK, marketData)
}

// handleGetPriceChart returns price chart data
func (s *Server) handleGetPriceChart(c *gin.Context) {
	hoursStr := c.DefaultQuery("hours", "24")
	hours, err := strconv.Atoi(hoursStr)
	if err != nil {
		hours = 24
	}

	chartData := s.marketData.GetPriceChartData(hours)
	c.JSON(http.StatusOK, map[string]interface{}{
		"chart": chartData,
	})
}

// handleGetPnLChart returns P&L chart data
func (s *Server) handleGetPnLChart(c *gin.Context) {
	userIDStr := c.DefaultQuery("user_id", "1")
	userID, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		userID = 1
	}

	// Get user positions for P&L calculation
	positions, err := s.orderManager.GetUserPositions(uint(userID))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	chartData := s.marketData.GetPnLChartData(positions)
	c.JSON(http.StatusOK, map[string]interface{}{
		"chart": chartData,
	})
}

// handleSubmitOrder handles order submission
func (s *Server) handleSubmitOrder(c *gin.Context) {
	var orderRequest core.OrderCreateRequest
	if err := c.ShouldBindJSON(&orderRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	userIDStr := c.DefaultQuery("user_id", "1")
	userID, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		userID = 1
	}

	// Check pre-trade risk
	riskCheck := s.riskManager.CheckPreTradeRisk(uint(userID), orderRequest)
	if !riskCheck["allowed"].(bool) {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   riskCheck["reason"],
		})
		return
	}

	result := s.orderManager.SubmitOrder(uint(userID), orderRequest)
	c.JSON(http.StatusOK, result)
}

// handleCancelOrder handles order cancellation
func (s *Server) handleCancelOrder(c *gin.Context) {
	orderID := c.Param("order_id")
	userIDStr := c.DefaultQuery("user_id", "1")
	userID, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		userID = 1
	}

	result := s.orderManager.CancelOrder(orderID, uint(userID))
	c.JSON(http.StatusOK, result)
}

// handleGetOrders returns user orders
func (s *Server) handleGetOrders(c *gin.Context) {
	userIDStr := c.DefaultQuery("user_id", "1")
	userID, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		userID = 1
	}

	limitStr := c.DefaultQuery("limit", "100")
	limit, err := strconv.Atoi(limitStr)
	if err != nil {
		limit = 100
	}

	orders, err := s.orderManager.GetUserOrders(uint(userID), limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, orders)
}

// handleGetTrades returns user trades
func (s *Server) handleGetTrades(c *gin.Context) {
	userIDStr := c.DefaultQuery("user_id", "1")
	userID, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		userID = 1
	}

	limitStr := c.DefaultQuery("limit", "100")
	limit, err := strconv.Atoi(limitStr)
	if err != nil {
		limit = 100
	}

	trades, err := s.orderManager.GetUserTrades(uint(userID), limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, trades)
}

// handleGetPositions returns user positions
func (s *Server) handleGetPositions(c *gin.Context) {
	userIDStr := c.DefaultQuery("user_id", "1")
	userID, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		userID = 1
	}

	positions, err := s.orderManager.GetUserPositions(uint(userID))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, positions)
}

// handleAIChat handles AI chat requests
func (s *Server) handleAIChat(c *gin.Context) {
	var chatRequest core.ChatMessageRequest
	if err := c.ShouldBindJSON(&chatRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get trading context
	context := make(map[string]interface{})
	context["market_data"] = s.marketData.GetCurrentPrice()
	
	positions, err := s.orderManager.GetUserPositions(chatRequest.UserID)
	if err == nil {
		context["positions"] = positions
	}

	response := s.tradingBot.ChatResponse(chatRequest.Message, context)
	c.JSON(http.StatusOK, gin.H{"response": response})
}

// handleAIAnalyze handles AI analysis requests
func (s *Server) handleAIAnalyze(c *gin.Context) {
	var contextRequest core.TradingContextRequest
	if err := c.ShouldBindJSON(&contextRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	marketData := s.marketData.GetCurrentPrice()
	positions, err := s.orderManager.GetUserPositions(contextRequest.UserID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	analysis := s.tradingBot.AnalyzeTradeOpportunity(marketData, positions)
	c.JSON(http.StatusOK, analysis)
}

// handleRiskReport returns risk analysis report
func (s *Server) handleRiskReport(c *gin.Context) {
	userIDStr := c.DefaultQuery("user_id", "1")
	userID, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		userID = 1
	}

	// Mock current prices for risk calculation
	currentPrices := map[uint]float64{
		1: s.marketData.GetCurrentPrice().Price,
		2: s.marketData.GetCurrentPrice().Price + 5,
		3: s.marketData.GetCurrentPrice().Price + 10,
	}

	report := s.riskManager.GenerateRiskReport(uint(userID), currentPrices)
	c.JSON(http.StatusOK, report)
}

// handleMarginStatus returns margin status
func (s *Server) handleMarginStatus(c *gin.Context) {
	userIDStr := c.DefaultQuery("user_id", "1")
	userID, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		userID = 1
	}

	currentPrices := map[uint]float64{
		1: s.marketData.GetCurrentPrice().Price,
		2: s.marketData.GetCurrentPrice().Price + 5,
		3: s.marketData.GetCurrentPrice().Price + 10,
	}

	marginStatus := s.riskManager.MonitorMarginRequirements(uint(userID), currentPrices)
	c.JSON(http.StatusOK, marginStatus)
}

// handleWebSocket handles WebSocket connections
func (s *Server) handleWebSocket(c *gin.Context) {
	conn, err := s.wsUpgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}
	defer conn.Close()

	s.wsConnections[conn] = true
	defer delete(s.wsConnections, conn)

	// Keep connection alive and handle incoming messages
	for {
		_, _, err := conn.ReadMessage()
		if err != nil {
			break
		}
	}
}

// broadcastToWebSockets broadcasts message to all WebSocket connections
func (s *Server) broadcastToWebSockets(message interface{}) {
	for conn := range s.wsConnections {
		if err := conn.WriteJSON(message); err != nil {
			log.Printf("WebSocket write error: %v", err)
			conn.Close()
			delete(s.wsConnections, conn)
		}
	}
}

// marketDataUpdater updates market data periodically
func (s *Server) marketDataUpdater() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		marketData := s.marketData.GetCurrentPrice()
		
		message := map[string]interface{}{
			"type": "market_data",
			"data": marketData,
		}
		
		s.broadcastToWebSockets(message)
	}
}

// positionUpdater updates position P&L periodically
func (s *Server) positionUpdater() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		currentPrices := map[uint]float64{
			1: s.marketData.GetCurrentPrice().Price,
			2: s.marketData.GetCurrentPrice().Price + 5,
			3: s.marketData.GetCurrentPrice().Price + 10,
		}

		if err := s.orderManager.UpdatePositionPnL(currentPrices); err != nil {
			log.Printf("Error updating position P&L: %v", err)
		}
	}
}

func main() {
	// Initialize server
	server, err := NewServer()
	if err != nil {
		log.Fatalf("Failed to initialize server: %v", err)
	}
	defer server.Close()

	// Setup routes
	router := server.setupRoutes()

	// Setup graceful shutdown
	srv := &http.Server{
		Addr:    ":8080",
		Handler: router,
	}

	// Start server in goroutine
	go func() {
		fmt.Println("🚀 Starting NASDAQ CSE Gold Derivatives Trading Simulator")
		fmt.Println("📊 Server running on http://localhost:8080")
		fmt.Println("🌐 WebSocket endpoint: ws://localhost:8080/ws")
		fmt.Println("📖 API documentation available at endpoints")
		
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed to start: %v", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	fmt.Println("\n🛑 Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	fmt.Println("✅ Server shutdown complete")
}