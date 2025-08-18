# NASDAQ CSE Gold Derivatives Trading Simulator (Go Version)

A comprehensive, high-performance gold derivatives trading simulator built in Go, featuring AI-powered assistance, real-time risk management, and educational trading tools.

## 🎯 Overview

This Go implementation is a complete port of the Python trading simulator, providing:

- **Real-time Trading Simulation** - Market data, order execution, and position management
- **AI-Powered Assistant** - ML-based trading analysis and chat interface  
- **Risk Management System** - Real-time margin monitoring and risk analytics
- **Order Management System** - Professional-grade order processing and execution
- **FIX/FAST Protocol Simulation** - Industry-standard communication protocols
- **WebSocket Live Updates** - Real-time market data and position updates
- **JSON Data Persistence** - Reloadable trading scenarios and state

## 🚀 Quick Start

### Prerequisites

- Go 1.21 or higher
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/smaruf/python-ai-course.git
cd python-ai-course/nasdaq-cse-go

# Install dependencies
go mod tidy

# Run the server
go run main.go
# OR
go run ./cmd/server
```

### Access the Application

- **Trading Interface**: http://localhost:8080
- **WebSocket Endpoint**: ws://localhost:8080/ws
- **API Documentation**: Available through the web interface

## 📊 System Architecture

### Core Packages

- **`internal/core`** - Data models and structures
- **`internal/aiassistant`** - AI trading bot and analysis
- **`internal/communication`** - FIX/FAST protocol simulation
- **`internal/marketdata`** - Real-time market data provider
- **`internal/oms`** - Order Management System
- **`internal/rms`** - Risk Management System
- **`internal/storage`** - Database and JSON persistence

### Technology Stack

- **Web Framework**: Gin HTTP framework
- **Database**: GORM with SQLite
- **WebSockets**: Gorilla WebSocket
- **Real-time Updates**: Go channels and goroutines
- **JSON Processing**: Built-in encoding/json
- **Testing**: Built-in testing framework

## 🔧 Features

### Real-time Market Data
- Live gold price feeds with bid/ask spreads
- Historical price data and analytics
- Interactive chart data generation
- WebSocket-based live updates

### AI Trading Assistant
- Market condition analysis and predictions
- Risk assessment and exposure monitoring  
- Hedging strategy recommendations
- Natural language chat interface
- Technical indicator calculations (RSI, volatility, moving averages)

### Order Management System (OMS)
- Market and limit order processing
- Real-time order matching engine
- Position tracking and P&L calculation
- Trade history and reporting
- Order lifecycle management

### Risk Management System (RMS)
- Pre-trade risk checks
- Real-time margin monitoring
- Value at Risk (VaR) calculations
- Position concentration limits
- Automated risk alerts and recommendations

### Communication Protocols
- FIX 4.4 protocol simulation
- FAST message encoding/decoding
- Order routing simulation
- Market data subscription handling

## 📡 API Endpoints

### Market Data
- `GET /api/market-data` - Current market data
- `GET /api/charts/price?hours=24` - Price chart data
- `GET /api/charts/pnl?user_id=1` - P&L chart data

### Trading Operations
- `POST /api/orders` - Submit new order
- `DELETE /api/orders/{order_id}` - Cancel order
- `GET /api/orders?user_id=1` - Get user orders
- `GET /api/trades?user_id=1` - Get user trades
- `GET /api/positions?user_id=1` - Get user positions

### AI Assistant
- `POST /api/ai/chat` - Chat with AI assistant
- `POST /api/ai/analyze` - Get AI trading analysis

### Risk Management
- `GET /api/risk/report?user_id=1` - Comprehensive risk report
- `GET /api/risk/margin?user_id=1` - Margin status

### WebSocket
- `GET /ws` - WebSocket connection for live updates

## 💡 Usage Examples

### Submit a Market Order

```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "contract_symbol": "GOLD2024DEC",
    "side": "BUY", 
    "order_type": "MARKET",
    "quantity": 5
  }'
```

### Chat with AI Assistant

```bash
curl -X POST http://localhost:8080/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current gold price?",
    "user_id": 1
  }'
```

### Get Risk Report

```bash
curl http://localhost:8080/api/risk/report?user_id=1
```

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
go test ./tests/...

# Run specific test file
go test ./tests/oms_test.go
go test ./tests/aiassistant_test.go

# Run with verbose output
go test -v ./tests/...

# Run with coverage
go test -cover ./tests/...
```

### Test Coverage

The test suite covers:
- Order Management System functionality
- AI Assistant analysis and chat features
- Risk management calculations
- Market data processing
- Database operations

## 📁 Project Structure

```
nasdaq-cse-go/
├── cmd/server/           # Main application entry point
├── internal/             # Internal packages
│   ├── core/            # Data models and types
│   ├── aiassistant/     # AI trading bot
│   ├── communication/   # FIX/FAST protocols
│   ├── marketdata/      # Market data provider
│   ├── oms/             # Order Management System
│   ├── rms/             # Risk Management System
│   └── storage/         # Database and JSON storage
├── tests/               # Unit tests
├── data/                # JSON data files
├── web/static/          # Static web assets
├── main.go              # Convenience entry point
├── go.mod               # Go module definition
└── README.md            # This file
```

## 🔄 JSON Data Persistence

The system maintains persistent state through JSON files:

- **`data/trades.json`** - Historical trade records
- **`data/user_decisions.json`** - User trading decisions and AI interactions
- **`data/ai_analysis.json`** - AI analysis results and recommendations

These files allow for:
- Educational scenario replay
- System state recovery
- Analysis of trading patterns
- Performance evaluation

## 🎯 Key Improvements over Python Version

### Performance
- **Concurrent Processing** - Go's goroutines handle multiple operations simultaneously
- **Memory Efficiency** - Lower memory footprint compared to Python
- **Fast Startup** - Compiled binary starts instantly
- **Efficient JSON Processing** - Built-in JSON handling with struct marshaling

### Architecture
- **Type Safety** - Compile-time type checking prevents runtime errors
- **Clean Interfaces** - Well-defined contracts between components
- **Modular Design** - Clear separation of concerns across packages
- **Error Handling** - Explicit error handling throughout the codebase

### Maintainability
- **Self-Documenting Code** - Exported functions and types have clear documentation
- **Comprehensive Tests** - Unit tests for all critical business logic
- **Consistent Patterns** - Idiomatic Go patterns throughout the codebase
- **Minimal Dependencies** - Relies primarily on Go standard library

## 🛠️ Configuration

The system uses sensible defaults but can be configured through environment variables:

```bash
# Database path (default: ./trading_simulator.db)
export DB_PATH="./custom_trading.db"

# Server port (default: 8080)
export PORT="8080"

# JSON storage directory (default: ./data)
export DATA_DIR="./custom_data"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following Go conventions
4. Add tests for new functionality
5. Ensure all tests pass (`go test ./tests/...`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the original repository LICENSE file for details.

## 🙏 Acknowledgments

- Original Python implementation by @smaruf
- Go community for excellent tooling and libraries
- Financial industry for FIX protocol standards
- Trading and risk management best practices from industry professionals

---

**Ready to start trading? Run `go run main.go` and visit http://localhost:8080** 🚀