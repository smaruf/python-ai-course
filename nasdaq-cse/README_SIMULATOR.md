# Gold Derivatives Trading Simulator

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the trading simulator:
```bash
python main.py
```

3. Access the web interface:
- Trading Interface: http://localhost:8000
- Market Data Charts: http://localhost:8000/market-data
- AI Assistant: http://localhost:8000/ai-assistant
- OMS Dashboard: http://localhost:8000/oms
- Risk Management: http://localhost:8000/rms

## Features

### Real-time Market Data
- Live gold price feeds from international markets
- Interactive charts with technical indicators
- Price alerts and notifications

### AI Trading Assistant
- Real-time trade analysis and suggestions
- Risk assessment and hedging recommendations
- Strategy insights based on market patterns
- Chat interface for natural language queries

### Order Management System (OMS)
- Order entry and modification
- Position tracking and P&L monitoring
- Trade history and reporting
- Automated order routing

### Risk Management System (RMS)
- Real-time margin calculations
- Position limits and exposure monitoring
- Risk alerts and warnings
- Automated risk controls

### Educational Features
- Simulated trading environment
- Historical scenario replay
- Risk management tutorials
- Strategy backtesting

## Architecture

The simulator is built with:
- **Backend**: FastAPI with WebSocket support
- **Database**: SQLAlchemy with in-memory SQLite
- **Charting**: Plotly for interactive charts
- **AI**: Scikit-learn for trade analysis
- **Frontend**: HTML/CSS/JavaScript with WebSocket
- **Protocols**: FIX/FAST simulation for market connectivity