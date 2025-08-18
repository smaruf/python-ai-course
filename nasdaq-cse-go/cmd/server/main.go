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
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/marketdata"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/oms"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/rms"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/storage"
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

	// WebSocket upgrader
	wsUpgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true // Allow all origins for demo
		},
	}

	server := &Server{
		db:            db,
		jsonStorage:   jsonStorage,
		marketData:    marketData,
		orderManager:  orderManager,
		riskManager:   riskManager,
		tradingBot:    tradingBot,
		commManager:   commManager,
		wsConnections: make(map[*websocket.Conn]bool),
		wsUpgrader:    wsUpgrader,
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
	}

	// WebSocket endpoint
	router.GET("/ws", s.handleWebSocket)

	return router
}

// handleRoot serves the main trading interface
func (s *Server) handleRoot(c *gin.Context) {
	html := `
<!DOCTYPE html>
<html>
<head>
    <title>NASDAQ CSE Gold Derivatives Trading Simulator</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .price { font-size: 2em; font-weight: bold; color: #2ecc71; }
        .change { font-weight: bold; }
        .positive { color: #27ae60; }
        .negative { color: #e74c3c; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .connected { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .disconnected { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
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