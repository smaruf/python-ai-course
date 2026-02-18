# Fintech Tools Project 🏦

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.

A comprehensive fintech toolkit for banking operations, payment processing, financial messaging protocols (FIX/FAST/ITCH), and account management with back-office capabilities. Built with FastAPI, featuring robust security and authentication.

## 🎯 Overview

This project provides a complete suite of tools for financial technology applications, including:

- **Banking Operations**: Core banking functionalities including account management, transactions, and balance tracking
- **Payment Processing**: Payment gateway integration, transaction processing, and settlement
- **Financial Protocols**: Implementation of industry-standard messaging protocols (FIX, FAST, ITCH)
- **Account Management**: Both Back Office (BO) and Client account management systems
- **Back Office Operations**: Comprehensive back-office tools for trade reconciliation, settlement, and reporting
- **Security & Authentication**: JWT-based authentication, role-based access control (RBAC), and API security

## 📁 Project Structure

```
fintech-tools/
├── src/                        # Source code
│   ├── bank/                   # Banking operations module
│   │   ├── __init__.py
│   │   ├── models.py          # Bank account models
│   │   ├── services.py        # Banking services
│   │   └── transactions.py    # Transaction processing
│   ├── payment/                # Payment processing module
│   │   ├── __init__.py
│   │   ├── models.py          # Payment models
│   │   ├── gateway.py         # Payment gateway integration
│   │   └── processor.py       # Payment processing logic
│   ├── protocols/              # Financial messaging protocols
│   │   ├── __init__.py
│   │   ├── fix_protocol.py    # FIX protocol implementation
│   │   ├── fast_protocol.py   # FAST protocol implementation
│   │   └── itch_protocol.py   # ITCH protocol implementation
│   ├── account/                # Account management
│   │   ├── __init__.py
│   │   ├── models.py          # Account models
│   │   ├── bo_accounts.py     # Back Office accounts
│   │   └── client_accounts.py # Client accounts
│   ├── backoffice/             # Back office operations
│   │   ├── __init__.py
│   │   ├── reconciliation.py  # Trade reconciliation
│   │   ├── settlement.py      # Settlement operations
│   │   └── reporting.py       # Reporting and analytics
│   ├── auth/                   # Authentication & Security
│   │   ├── __init__.py
│   │   ├── jwt_handler.py     # JWT token handling
│   │   ├── models.py          # User and auth models
│   │   └── security.py        # Security utilities
│   └── __init__.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_bank.py
│   ├── test_payment.py
│   ├── test_protocols.py
│   ├── test_account.py
│   ├── test_backoffice.py
│   └── test_auth.py
├── examples/                   # Usage examples
│   ├── basic_banking.py
│   ├── payment_flow.py
│   ├── protocol_examples.py
│   └── auth_example.py
├── docs/                       # Documentation
│   ├── BANKING.md             # Banking module documentation
│   ├── PAYMENT.md             # Payment module documentation
│   ├── PROTOCOLS.md           # Protocols documentation
│   ├── AUTHENTICATION.md      # Auth and security guide
│   └── API.md                 # API documentation
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd fintech-tools

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the FastAPI server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access the interactive API documentation
# Open your browser to: http://localhost:8000/docs
```

### First Steps

```python
# Example: Basic banking operations
from src.bank.services import BankingService
from src.bank.models import Account

# Create a banking service
service = BankingService()

# Create an account
account = service.create_account(
    account_number="1234567890",
    account_type="savings",
    initial_balance=1000.0,
    customer_name="John Doe"
)

# Make a transaction
transaction = service.process_transaction(
    from_account="1234567890",
    to_account="0987654321",
    amount=100.0,
    transaction_type="transfer"
)
```

## 🔐 Authentication & Security

### JWT Authentication Setup

```bash
# Generate a secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set the secret key in your environment:
```bash
export SECRET_KEY="your-generated-secret-key"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Authentication Flow

1. **Register a User**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe",
    "role": "client"
  }'
```

2. **Login to Get Token**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePassword123!"
```

3. **Use Token for Protected Endpoints**
```bash
curl -X GET "http://localhost:8000/accounts/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Role-Based Access Control (RBAC)

Available roles:
- **admin**: Full system access
- **backoffice**: Back-office operations access
- **trader**: Trading and account management
- **client**: Limited access to own accounts

### Security Features

- **Password Hashing**: Bcrypt-based password hashing
- **JWT Tokens**: Secure token-based authentication
- **HTTPS Support**: SSL/TLS configuration ready
- **Rate Limiting**: API rate limiting to prevent abuse
- **Input Validation**: Pydantic models for data validation
- **SQL Injection Protection**: ORM-based database access
- **CORS Configuration**: Configurable CORS policies

## 📚 Module Documentation

### Banking Module

The banking module provides core banking operations:

```python
from src.bank.services import BankingService

service = BankingService()

# Account operations
account = service.create_account(account_number, account_type, balance)
balance = service.get_balance(account_number)
history = service.get_transaction_history(account_number)

# Transactions
service.deposit(account_number, amount)
service.withdraw(account_number, amount)
service.transfer(from_account, to_account, amount)
```

See [docs/BANKING.md](docs/BANKING.md) for detailed documentation.

### Payment Module

Process payments through various gateways:

```python
from src.payment.processor import PaymentProcessor

processor = PaymentProcessor()

# Process a payment
result = processor.process_payment(
    amount=100.0,
    currency="USD",
    payment_method="card",
    card_details={...}
)

# Check payment status
status = processor.get_payment_status(transaction_id)
```

See [docs/PAYMENT.md](docs/PAYMENT.md) for detailed documentation.

### Protocols Module

Implement financial messaging protocols:

```python
from src.protocols.fix_protocol import FIXProtocol
from src.protocols.fast_protocol import FASTProtocol
from src.protocols.itch_protocol import ITCHProtocol

# FIX Protocol (Financial Information eXchange)
fix = FIXProtocol()
message = fix.create_new_order(symbol="AAPL", side="BUY", quantity=100, price=150.0)
parsed = fix.parse_message(message)

# FAST Protocol (FIX Adapted for STreaming)
fast = FASTProtocol()
encoded = fast.encode_message(market_data)
decoded = fast.decode_message(encoded)

# ITCH Protocol (NASDAQ TotalView-ITCH)
itch = ITCHProtocol()
order_message = itch.create_add_order(stock="AAPL", shares=100, price=150.0)
```

See [docs/PROTOCOLS.md](docs/PROTOCOLS.md) for detailed documentation.

### Account Management

Manage both client and back-office accounts:

```python
from src.account.client_accounts import ClientAccountManager
from src.account.bo_accounts import BackOfficeAccountManager

# Client accounts
client_mgr = ClientAccountManager()
client_account = client_mgr.create_account(client_id, account_type)
portfolio = client_mgr.get_portfolio(client_id)

# Back-office accounts
bo_mgr = BackOfficeAccountManager()
bo_account = bo_mgr.create_clearing_account(broker_id)
positions = bo_mgr.get_positions(account_id)
```

### Back Office Operations

Handle trade lifecycle and settlements:

```python
from src.backoffice.reconciliation import ReconciliationService
from src.backoffice.settlement import SettlementService
from src.backoffice.reporting import ReportingService

# Reconciliation
recon = ReconciliationService()
mismatches = recon.reconcile_trades(trade_date)

# Settlement
settlement = SettlementService()
settlement.process_settlements(settlement_date)

# Reporting
reporting = ReportingService()
report = reporting.generate_daily_report(date)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module tests
python -m pytest tests/test_bank.py -v
python -m pytest tests/test_payment.py -v
python -m pytest tests/test_protocols.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## 📊 API Endpoints

### Authentication Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive JWT token
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

### Banking Endpoints

- `GET /bank/accounts` - List all accounts
- `POST /bank/accounts` - Create new account
- `GET /bank/accounts/{id}` - Get account details
- `POST /bank/transactions` - Process transaction
- `GET /bank/transactions/{id}` - Get transaction details

### Payment Endpoints

- `POST /payments/process` - Process a payment
- `GET /payments/{id}` - Get payment status
- `POST /payments/refund` - Process refund
- `GET /payments/history` - Get payment history

### Account Management Endpoints

- `GET /accounts/clients` - List client accounts
- `POST /accounts/clients` - Create client account
- `GET /accounts/backoffice` - List back-office accounts
- `GET /accounts/{id}/positions` - Get account positions

### Back Office Endpoints

- `POST /backoffice/reconcile` - Run reconciliation
- `POST /backoffice/settle` - Process settlements
- `GET /backoffice/reports` - Generate reports
- `GET /backoffice/trades` - List trades

### Protocol Endpoints

- `POST /protocols/fix/send` - Send FIX message
- `POST /protocols/fast/encode` - Encode FAST message
- `POST /protocols/itch/parse` - Parse ITCH message

## 🔧 Configuration

Create a `.env` file in the project root:

```env
# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./fintech.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Payment Gateway (Example)
PAYMENT_GATEWAY_API_KEY=your-payment-api-key
PAYMENT_GATEWAY_URL=https://api.payment-gateway.com
```

## 📖 Additional Resources

### Financial Protocols

- **FIX Protocol**: Used for real-time electronic exchange of securities transactions
  - Standard messaging format for trade-related messages
  - Supports order entry, execution reports, trade confirmations
  
- **FAST Protocol**: Optimized encoding for high-frequency FIX messages
  - Reduces bandwidth and latency
  - Used in market data distribution
  
- **ITCH Protocol**: NASDAQ's market data protocol
  - Real-time order book updates
  - Trade execution notifications

### Back Office Operations

Back-office functions include:
- **Trade Capture**: Recording executed trades
- **Reconciliation**: Matching internal records with counterparties
- **Settlement**: Finalizing trade obligations
- **Reporting**: Regulatory and internal reporting
- **Position Management**: Tracking security positions

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is part of the python-ai-course repository and follows the same license.

## 🔗 Related Projects

- [NASDAQ CSE Trading Simulator](../nasdaq-cse/) - Full trading simulator with AI
- [Web Applications Project](../web-applications-project/) - FastAPI and Flask examples
- [AI Development Project](../ai-development-project/) - AI integration patterns

## 📧 Support

For questions or issues:
- Open an issue in the repository
- Check the documentation in the `docs/` directory
- Review the examples in the `examples/` directory

## 🎓 Educational Value

This project demonstrates:
- **FastAPI**: Modern async web framework
- **Security Best Practices**: JWT, RBAC, encryption
- **Financial Domain Knowledge**: Banking, payments, protocols
- **Clean Architecture**: Modular, testable code structure
- **API Design**: RESTful principles and documentation
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear, detailed documentation

## 🚀 Roadmap

Future enhancements:
- [ ] WebSocket support for real-time updates
- [ ] Blockchain integration for transparent settlements
- [ ] Advanced fraud detection with ML
- [ ] Multi-currency support
- [ ] Regulatory reporting automation
- [ ] Mobile SDK for client applications
- [ ] Performance optimization for high-frequency trading
- [ ] Distributed system support with message queues
