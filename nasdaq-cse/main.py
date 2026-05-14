"""
Main FastAPI application for the Gold Derivatives Trading Simulator
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our modules
from core.models import OrderCreate, UserCreate
from storage.database import db_manager, json_storage
from market_data.provider import gold_price_provider, chart_generator
from ai_assistant.bot import trading_bot
from oms.manager import order_manager
from rms.manager import risk_manager
from terminal.commands import TerminalCommandExecutor
from terminal.symbols import autocomplete as symbol_autocomplete


# Background task for updating market data and positions
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(market_data_updater())
    asyncio.create_task(position_updater())
    yield
    # Shutdown
    pass

app = FastAPI(
    title="NASDAQ CSE Gold Derivatives Trading Simulator",
    description="Advanced trading simulator with AI assistant and real-time charts",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Terminal executor (shared, user_id resolved per-request)
_terminal_executor_cache: Dict[int, TerminalCommandExecutor] = {}


def get_terminal_executor(user_id: int) -> TerminalCommandExecutor:
    if user_id not in _terminal_executor_cache:
        _terminal_executor_cache[user_id] = TerminalCommandExecutor(
            order_manager=order_manager,
            user_id=user_id,
        )
    return _terminal_executor_cache[user_id]


# Pydantic models for API
class ChatMessage(BaseModel):
    message: str
    user_id: int = 1


class TerminalCommand(BaseModel):
    command: str
    user_id: int = 1

class TradingContext(BaseModel):
    user_id: int = 1

# API Routes
@app.get("/")
async def read_root():
    """Serve the main trading interface"""
    return HTMLResponse(content=get_main_html(), status_code=200)

@app.get("/api/market-data")
async def get_market_data():
    """Get current market data"""
    try:
        current_price = await gold_price_provider.get_current_price()
        return JSONResponse(content=current_price)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/charts/price")
async def get_price_chart(hours: int = 24):
    """Get price chart data"""
    try:
        chart_json = chart_generator.create_price_chart(hours)
        return JSONResponse(content={"chart": chart_json})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/charts/pnl")
async def get_pnl_chart(user_id: int = 1):
    """Get P&L chart for user"""
    try:
        positions = await order_manager.get_user_positions(user_id)
        chart_json = chart_generator.create_pnl_chart(positions)
        return JSONResponse(content={"chart": chart_json})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders")
async def submit_order(order: OrderCreate, user_id: int = 1):
    """Submit a new trading order"""
    try:
        # Check pre-trade risk
        order_dict = order.model_dump()
        risk_check = await risk_manager.check_pre_trade_risk(user_id, order_dict)
        if not risk_check['allowed']:
            raise HTTPException(status_code=400, detail=risk_check['reason'])
        
        # Submit order
        result = await order_manager.submit_order(user_id, order_dict)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Check post-trade risk
        await risk_manager.check_post_trade_risk(user_id)
        
        # Save to JSON storage
        trades_data = json_storage.load_trades()
        trades_data[result['order_id']] = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'order': order_dict,
            'result': result
        }
        json_storage.save_trades(trades_data)
        
        # Broadcast update to WebSocket clients
        await manager.broadcast(json.dumps({
            'type': 'order_update',
            'data': result
        }))
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders")
async def get_orders(user_id: int = 1, limit: int = 100):
    """Get user's orders"""
    try:
        orders = await order_manager.get_user_orders(user_id, limit)
        return JSONResponse(content=orders)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions")
async def get_positions(user_id: int = 1):
    """Get user's positions"""
    try:
        positions = await order_manager.get_user_positions(user_id)
        return JSONResponse(content=positions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades")
async def get_trades(user_id: int = 1, limit: int = 100):
    """Get user's trade history"""
    try:
        trades = await order_manager.get_user_trades(user_id, limit)
        return JSONResponse(content=trades)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-report")
async def get_risk_report(user_id: int = 1):
    """Get comprehensive risk report"""
    try:
        # Get current prices for risk calculations
        current_price_data = await gold_price_provider.get_current_price()
        current_prices = {1: current_price_data['price']}  # Simplified - map contract IDs to prices
        
        risk_report = await risk_manager.generate_risk_report(user_id, current_prices)
        return JSONResponse(content=risk_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/chat")
async def chat_with_ai(message: ChatMessage):
    """Chat with AI trading assistant"""
    try:
        # Get trading context
        positions = await order_manager.get_user_positions(message.user_id)
        market_data = await gold_price_provider.get_current_price()
        
        context = {
            'positions': positions,
            'market_data': market_data,
            'account_balance': 100000.0  # This should come from user data
        }
        
        # Get AI response
        response = await trading_bot.chat_response(message.message, context)
        
        # Save interaction to JSON storage
        ai_data = json_storage.load_ai_analysis()
        interaction_id = f"chat_{datetime.utcnow().timestamp()}"
        ai_data[interaction_id] = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': message.user_id,
            'user_message': message.message,
            'ai_response': response,
            'context': context
        }
        json_storage.save_ai_analysis(ai_data)
        
        return JSONResponse(content={'response': response})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Terminal / Command Mode endpoints ─────────────────────────────────────────

@app.post("/api/terminal/execute")
async def terminal_execute(cmd_body: TerminalCommand):
    """
    Execute a terminal-style order command.

    Examples::

        {"command": "b BATBC 100 25.40", "user_id": 1}
        {"command": "bm GP 200",          "user_id": 1}
        {"command": "c 982734",            "user_id": 1}
    """
    try:
        executor = get_terminal_executor(cmd_body.user_id)
        results = await executor.execute(cmd_body.command)
        return JSONResponse(content={
            "results": [r.to_dict() for r in results],
            "command": cmd_body.command,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/terminal/complete")
async def terminal_autocomplete(prefix: str = "", max_results: int = 10):
    """Return symbol autocomplete suggestions for the given prefix."""
    matches = symbol_autocomplete(prefix, max_results=max_results)
    return JSONResponse(content={"suggestions": matches})


@app.get("/api/terminal/history")
async def terminal_history(user_id: int = 1, limit: int = 50):
    """Return the command history for a user."""
    executor = get_terminal_executor(user_id)
    history = executor.history[-limit:]
    return JSONResponse(content={"history": history})

@app.get("/api/ai/analysis")
async def get_ai_analysis(user_id: int = 1):
    """Get AI trading analysis"""
    try:
        positions = await order_manager.get_user_positions(user_id)
        market_data = await gold_price_provider.get_current_price()
        
        # Get different types of analysis
        trade_analysis = await trading_bot.analyze_trade_opportunity(market_data, positions)
        risk_analysis = await trading_bot.analyze_risk(positions, 100000.0)
        hedging_analysis = await trading_bot.suggest_hedging_strategy(positions, market_data)
        
        return JSONResponse(content={
            'trade_analysis': trade_analysis,
            'risk_analysis': risk_analysis,
            'hedging_analysis': hedging_analysis
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic market data updates
            market_data = await gold_price_provider.get_current_price()
            await websocket.send_text(json.dumps({
                'type': 'market_data',
                'data': market_data
            }))
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task for updating market data and positions

async def market_data_updater():
    """Update market data periodically"""
    while True:
        try:
            current_price_data = await gold_price_provider.get_current_price()
            
            # Broadcast to WebSocket clients
            await manager.broadcast(json.dumps({
                'type': 'market_data',
                'data': current_price_data
            }))
            
        except Exception as e:
            print(f"Error updating market data: {e}")
        
        await asyncio.sleep(10)  # Update every 10 seconds

async def position_updater():
    """Update position P&L periodically"""
    while True:
        try:
            current_price_data = await gold_price_provider.get_current_price()
            current_prices = {1: current_price_data['price']}  # Map contract IDs to prices
            
            await order_manager.update_position_pnl(current_prices)
            
        except Exception as e:
            print(f"Error updating positions: {e}")
        
        await asyncio.sleep(30)  # Update every 30 seconds

def get_main_html():
    """Get the main HTML interface"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NASDAQ CSE Gold Derivatives Trading Simulator</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 1.8rem;
        }
        .header .subtitle {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 0.9rem;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
            padding: 1rem;
            height: calc(100vh - 120px);
        }
        .panel {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .panel-header {
            background: #f8f9fa;
            padding: 1rem;
            border-bottom: 1px solid #e9ecef;
            font-weight: 600;
            color: #495057;
        }
        .panel-content {
            padding: 1rem;
            flex: 1;
            overflow-y: auto;
        }
        .market-price {
            font-size: 2rem;
            font-weight: bold;
            color: #28a745;
            text-align: center;
            margin: 1rem 0;
        }
        .price-change {
            text-align: center;
            font-size: 1.1rem;
        }
        .price-change.positive {
            color: #28a745;
        }
        .price-change.negative {
            color: #dc3545;
        }
        .order-form {
            display: grid;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .form-group label {
            font-weight: 600;
            color: #495057;
        }
        .form-group input, .form-group select {
            padding: 0.75rem;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 1rem;
        }
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background: #0056b3;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: #f8f9fa;
            margin-bottom: 1rem;
        }
        .chat-message {
            margin-bottom: 1rem;
            padding: 0.75rem;
            border-radius: 8px;
        }
        .chat-message.user {
            background: #007bff;
            color: white;
            margin-left: 20%;
        }
        .chat-message.bot {
            background: #e9ecef;
            color: #495057;
            margin-right: 20%;
        }
        .chat-input {
            display: flex;
            gap: 0.5rem;
        }
        .chat-input input {
            flex: 1;
            padding: 0.75rem;
            border: 1px solid #ced4da;
            border-radius: 4px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        .status-connected {
            background: #28a745;
        }
        .status-disconnected {
            background: #dc3545;
        }
        .chart-container {
            height: 300px;
            margin: 1rem 0;
        }
        .position-item {
            background: #f8f9fa;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }
        .position-item.profit {
            border-left-color: #28a745;
        }
        .position-item.loss {
            border-left-color: #dc3545;
        }
        /* ── OMS Terminal overlay ──────────────────────────────────────── */
        #terminalOverlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.55);
            z-index: 9000;
            align-items: flex-start;
            justify-content: center;
            padding-top: 80px;
        }
        #terminalOverlay.open { display: flex; }
        #terminalBox {
            background: #0d1117;
            color: #c9d1d9;
            font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
            font-size: 0.92rem;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.7);
            width: min(720px, 95vw);
            display: flex;
            flex-direction: column;
        }
        #terminalHeader {
            background: #161b22;
            padding: 0.6rem 1rem;
            border-radius: 8px 8px 0 0;
            border-bottom: 1px solid #30363d;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: #58a6ff;
            font-weight: 600;
        }
        #terminalHeader .kbd {
            font-size: 0.78rem;
            color: #8b949e;
            font-weight: normal;
        }
        #terminalOutput {
            padding: 0.75rem 1rem;
            min-height: 140px;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        #terminalOutput .line-ok   { color: #3fb950; }
        #terminalOutput .line-err  { color: #f85149; }
        #terminalOutput .line-cmd  { color: #e3b341; }
        #terminalOutput .line-hint { color: #8b949e; font-style: italic; }
        #terminalPreview {
            border-top: 1px solid #21262d;
            padding: 0.4rem 1rem;
            color: #8b949e;
            font-size: 0.85rem;
            min-height: 1.5rem;
        }
        #terminalInputRow {
            border-top: 1px solid #21262d;
            display: flex;
            align-items: center;
            padding: 0.5rem 1rem;
            gap: 0.5rem;
        }
        #terminalInputRow span { color: #58a6ff; }
        #terminalInput {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #c9d1d9;
            font-family: inherit;
            font-size: inherit;
            caret-color: #58a6ff;
        }
        #terminalSuggest {
            padding: 0 1rem 0.6rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        .suggest-chip {
            background: #21262d;
            color: #58a6ff;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            border: 1px solid #30363d;
        }
        .suggest-chip:hover { background: #30363d; }
        #terminalToggleBtn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 8999;
            background: #1f6feb;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 0.65rem 1.2rem;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        }
        #terminalToggleBtn:hover { background: #388bfd; }
    </style>
</head>
<body>
    <!-- ── OMS Terminal floating overlay ──────────────────────────────── -->
    <div id="terminalOverlay" role="dialog" aria-label="OMS Terminal">
        <div id="terminalBox">
            <div id="terminalHeader">
                <span>⚡ OMS Terminal — FastTrade CMD</span>
                <span class="kbd">Ctrl+Space / Alt+T to toggle &nbsp;|&nbsp; Enter to submit &nbsp;|&nbsp; ↑↓ history &nbsp;|&nbsp; Esc to close</span>
            </div>
            <div id="terminalOutput">
                <span class="line-hint">Type a command and press Enter.  Examples:
  b BATBC 100 25.40     → Limit buy
  bm GP 200             → Market buy
  s BATBC 50 25.60      → Limit sell
  c &lt;order_id&gt;          → Cancel
  m &lt;order_id&gt; 25.80 100 → Modify
  b BATBC 5k 25.40      → qty shorthand (5k=5000)
  help                  → full command reference
</span>
            </div>
            <div id="terminalPreview"></div>
            <div id="terminalInputRow">
                <span>&gt;</span>
                <input id="terminalInput" type="text" placeholder="b BATBC 100 25.40" autocomplete="off" spellcheck="false"/>
            </div>
            <div id="terminalSuggest"></div>
        </div>
    </div>
    <button id="terminalToggleBtn" onclick="toggleTerminal()" title="Open OMS Terminal (Ctrl+Space)">⚡ Terminal</button>
    <div class="header">
        <h1>🏛️ NASDAQ CSE Gold Derivatives Trading Simulator</h1>
        <div class="subtitle">
            <span class="status-indicator" id="connectionStatus"></span>
            Advanced Trading Platform with AI Assistant & Real-time Analytics
        </div>
    </div>
    
    <div class="container">
        <!-- Market Data Panel -->
        <div class="panel">
            <div class="panel-header">📈 Market Data & Charts</div>
            <div class="panel-content">
                <div class="market-price" id="currentPrice">Loading...</div>
                <div class="price-change" id="priceChange">--</div>
                <div class="chart-container" id="priceChart"></div>
                <button class="btn btn-primary" onclick="refreshChart()">🔄 Refresh Chart</button>
            </div>
        </div>
        
        <!-- Trading Panel -->
        <div class="panel">
            <div class="panel-header">⚡ Order Management System</div>
            <div class="panel-content">
                <div class="order-form">
                    <div class="form-group">
                        <label>Contract:</label>
                        <select id="contractSymbol">
                            <option value="GOLD2024DEC">GOLD2024DEC</option>
                            <option value="GOLD2025MAR">GOLD2025MAR</option>
                            <option value="GOLD2025JUN">GOLD2025JUN</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Side:</label>
                        <select id="orderSide">
                            <option value="BUY">BUY</option>
                            <option value="SELL">SELL</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Order Type:</label>
                        <select id="orderType">
                            <option value="MARKET">MARKET</option>
                            <option value="LIMIT">LIMIT</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Quantity:</label>
                        <input type="number" id="quantity" value="1" min="1">
                    </div>
                    <div class="form-group" id="priceGroup" style="display: none;">
                        <label>Price:</label>
                        <input type="number" id="orderPrice" step="0.01">
                    </div>
                    <button class="btn btn-success" onclick="submitOrder()">📤 Submit Order</button>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h4>Recent Orders</h4>
                    <div id="ordersList"></div>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h4>Current Positions</h4>
                    <div id="positionsList"></div>
                </div>
            </div>
        </div>
        
        <!-- AI Assistant Panel -->
        <div class="panel">
            <div class="panel-header">🤖 AI Trading Assistant</div>
            <div class="panel-content">
                <div class="chat-container">
                    <div class="chat-messages" id="chatMessages">
                        <div class="chat-message bot">
                            👋 Hi! I'm your AI trading assistant. I can help you with:
                            <br>• Market analysis and price predictions
                            <br>• Risk assessment and warnings
                            <br>• Trading suggestions and strategies
                            <br>• Hedging recommendations
                            <br><br>Ask me anything about your trading!
                        </div>
                    </div>
                    <div class="chat-input">
                        <input type="text" id="chatInput" placeholder="Ask me about trading..." onkeypress="handleChatKeyPress(event)">
                        <button class="btn btn-primary" onclick="sendChatMessage()">💬 Send</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let currentMarketData = null;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function(event) {
                console.log('WebSocket connected');
                document.getElementById('connectionStatus').className = 'status-indicator status-connected';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            ws.onclose = function(event) {
                console.log('WebSocket disconnected');
                document.getElementById('connectionStatus').className = 'status-indicator status-disconnected';
                // Reconnect after 5 seconds
                setTimeout(connectWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function handleWebSocketMessage(data) {
            if (data.type === 'market_data') {
                updateMarketData(data.data);
            } else if (data.type === 'order_update') {
                refreshOrders();
                refreshPositions();
            }
        }
        
        function updateMarketData(data) {
            currentMarketData = data;
            document.getElementById('currentPrice').textContent = `$${data.price.toFixed(2)}`;
            
            const changeElement = document.getElementById('priceChange');
            const changePercent = data.change_percent * 100;
            changeElement.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`;
            changeElement.className = `price-change ${changePercent >= 0 ? 'positive' : 'negative'}`;
        }
        
        async function refreshChart() {
            try {
                const response = await fetch('/api/charts/price?hours=24');
                const data = await response.json();
                const chart = JSON.parse(data.chart);
                Plotly.newPlot('priceChart', chart.data, chart.layout, {responsive: true});
            } catch (error) {
                console.error('Error loading chart:', error);
            }
        }
        
        function handleOrderTypeChange() {
            const orderType = document.getElementById('orderType').value;
            const priceGroup = document.getElementById('priceGroup');
            priceGroup.style.display = orderType === 'LIMIT' ? 'block' : 'none';
        }
        
        async function submitOrder() {
            const orderData = {
                contract_symbol: document.getElementById('contractSymbol').value,
                side: document.getElementById('orderSide').value,
                order_type: document.getElementById('orderType').value,
                quantity: parseFloat(document.getElementById('quantity').value),
                price: document.getElementById('orderType').value === 'LIMIT' ? 
                       parseFloat(document.getElementById('orderPrice').value) : null
            };
            
            try {
                const response = await fetch('/api/orders', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(orderData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    addChatMessage('bot', `✅ Order submitted successfully! Order ID: ${result.order_id}`);
                    refreshOrders();
                    refreshPositions();
                } else {
                    addChatMessage('bot', `❌ Order failed: ${result.detail}`);
                }
            } catch (error) {
                addChatMessage('bot', `❌ Error submitting order: ${error.message}`);
            }
        }
        
        async function refreshOrders() {
            try {
                const response = await fetch('/api/orders?limit=5');
                const orders = await response.json();
                
                const ordersList = document.getElementById('ordersList');
                ordersList.innerHTML = orders.map(order => `
                    <div class="position-item">
                        <strong>${order.side} ${order.quantity}</strong> ${order.contract_id}<br>
                        <small>Status: ${order.status} | Price: $${order.price || 'Market'}</small>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading orders:', error);
            }
        }
        
        async function refreshPositions() {
            try {
                const response = await fetch('/api/positions');
                const positions = await response.json();
                
                const positionsList = document.getElementById('positionsList');
                positionsList.innerHTML = positions.map(pos => `
                    <div class="position-item ${pos.unrealized_pnl >= 0 ? 'profit' : 'loss'}">
                        <strong>Qty: ${pos.quantity}</strong> | Avg: $${pos.avg_entry_price.toFixed(2)}<br>
                        <small>P&L: $${pos.unrealized_pnl.toFixed(2)}</small>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading positions:', error);
            }
        }
        
        function handleChatKeyPress(event) {
            if (event.key === 'Enter') {
                sendChatMessage();
            }
        }
        
        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            addChatMessage('user', message);
            input.value = '';
            
            try {
                const response = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, user_id: 1})
                });
                
                const result = await response.json();
                addChatMessage('bot', result.response);
            } catch (error) {
                addChatMessage('bot', `❌ Error: ${error.message}`);
            }
        }
        
        function addChatMessage(sender, message) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;
            messageDiv.innerHTML = message;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // Event listeners
        document.getElementById('orderType').addEventListener('change', handleOrderTypeChange);
        
        // Initialize
        window.onload = function() {
            connectWebSocket();
            refreshChart();
            refreshOrders();
            refreshPositions();
            initTerminal();
        };

        // ── OMS Terminal ──────────────────────────────────────────────────
        const termOverlay  = document.getElementById('terminalOverlay');
        const termInput    = document.getElementById('terminalInput');
        const termOutput   = document.getElementById('terminalOutput');
        const termPreview  = document.getElementById('terminalPreview');
        const termSuggest  = document.getElementById('terminalSuggest');
        let termHistory    = [];
        let termHistIdx    = -1;
        let suggestDebounce = null;

        function initTerminal() {
            // Keyboard shortcut: Ctrl+Space or Alt+T
            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey && e.code === 'Space') || (e.altKey && e.key === 't')) {
                    e.preventDefault();
                    toggleTerminal();
                }
                if (e.key === 'Escape' && termOverlay.classList.contains('open')) {
                    closeTerminal();
                }
            });

            termInput.addEventListener('keydown', handleTerminalKeyDown);
            termInput.addEventListener('input', onTerminalInput);
            termOverlay.addEventListener('click', (e) => {
                if (e.target === termOverlay) closeTerminal();
            });
        }

        function toggleTerminal() {
            if (termOverlay.classList.contains('open')) {
                closeTerminal();
            } else {
                openTerminal();
            }
        }

        function openTerminal() {
            termOverlay.classList.add('open');
            termInput.focus();
        }

        function closeTerminal() {
            termOverlay.classList.remove('open');
        }

        async function handleTerminalKeyDown(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                await submitTerminalCommand();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                navigateHistory(1);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                navigateHistory(-1);
            } else if (e.key === 'Tab') {
                e.preventDefault();
                applyFirstSuggestion();
            }
        }

        function navigateHistory(direction) {
            if (termHistory.length === 0) return;
            termHistIdx = Math.max(0, Math.min(termHistory.length - 1, termHistIdx + direction));
            termInput.value = termHistory[termHistory.length - 1 - termHistIdx] || '';
            updatePreview();
        }

        function onTerminalInput() {
            termHistIdx = -1;
            clearTimeout(suggestDebounce);
            suggestDebounce = setTimeout(() => {
                updatePreview();
                fetchSuggestions();
            }, 80);
        }

        function updatePreview() {
            const cmd = termInput.value.trim();
            if (!cmd) { termPreview.textContent = ''; return; }
            // Client-side lightweight preview (no server call needed)
            const tokens = cmd.split(/\s+/);
            const verb = (tokens[0] || '').toLowerCase();
            const typeMap = {b:'Buy', buy:'Buy', bm:'Buy Market', s:'Sell', sell:'Sell', sm:'Sell Market',
                             c:'Cancel', cancel:'Cancel', m:'Modify', modify:'Modify', rr:'Repeat last', help:'Help','?':'Help'};
            const type = typeMap[verb] || '';
            if (!type) { termPreview.textContent = ''; return; }
            const symbol = tokens[1] ? tokens[1].toUpperCase() : '';
            const qty    = tokens[2] ? parseQtyShorthand(tokens[2]) : null;
            const price  = tokens[3] ? parseFloat(tokens[3]) : null;
            let preview  = type;
            if (symbol) preview += `  ${symbol}`;
            if (qty !== null && !isNaN(qty)) preview += `  qty=${qty.toLocaleString()}`;
            if (price !== null && !isNaN(price)) {
                preview += `  @ ${price.toFixed(2)}`;
                if (qty) preview += `  ≈ ${(qty * price).toLocaleString(undefined,{maximumFractionDigits:0})} BDT`;
            }
            termPreview.textContent = preview;
        }

        function parseQtyShorthand(s) {
            s = s.replace('%','').toLowerCase();
            if (s.endsWith('k')) return parseFloat(s) * 1000;
            if (s.endsWith('m')) return parseFloat(s) * 1_000_000;
            return parseFloat(s);
        }

        async function fetchSuggestions() {
            const tokens = termInput.value.trim().split(/\s+/);
            if (tokens.length < 2) { termSuggest.innerHTML = ''; return; }
            const verb = tokens[0].toLowerCase();
            if (!['b','s','bm','sm','buy','sell'].includes(verb)) {
                termSuggest.innerHTML = ''; return;
            }
            const prefix = tokens[1] || '';
            if (prefix.length < 1) { termSuggest.innerHTML = ''; return; }
            try {
                const resp = await fetch(`/api/terminal/complete?prefix=${encodeURIComponent(prefix)}&max_results=6`);
                const data = await resp.json();
                renderSuggestions(data.suggestions || []);
            } catch(_) {}
        }

        function renderSuggestions(suggestions) {
            termSuggest.innerHTML = suggestions.map(s =>
                `<span class="suggest-chip" onclick="applySuggestion('${s.symbol}')" title="${s.name}">${s.symbol}</span>`
            ).join('');
        }

        function applySuggestion(sym) {
            const tokens = termInput.value.trim().split(/\s+/);
            tokens[1] = sym;
            termInput.value = tokens.join(' ') + ' ';
            termInput.focus();
            termSuggest.innerHTML = '';
            updatePreview();
        }

        function applyFirstSuggestion() {
            const first = termSuggest.querySelector('.suggest-chip');
            if (first) first.click();
        }

        async function submitTerminalCommand() {
            const cmd = termInput.value.trim();
            if (!cmd) return;

            appendLine('line-cmd', '> ' + cmd);
            termHistory.push(cmd);
            termHistIdx = -1;
            termInput.value = '';
            termPreview.textContent = '';
            termSuggest.innerHTML = '';

            try {
                const resp = await fetch('/api/terminal/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd, user_id: 1})
                });
                const data = await resp.json();
                for (const r of (data.results || [])) {
                    appendLine(r.success ? 'line-ok' : 'line-err', r.message);
                    if (r.order_id) refreshOrders();
                }
            } catch(err) {
                appendLine('line-err', '❌ Network error: ' + err.message);
            }
        }

        function appendLine(cls, text) {
            const span = document.createElement('span');
            span.className = cls;
            span.textContent = text + '\n';
            termOutput.appendChild(span);
            termOutput.scrollTop = termOutput.scrollHeight;
        }
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)