# WhatsApp Medical Report Vault - MVP

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [AI Development Project](../ai-development-project/) | [Fintech Tools](../fintech-tools/) | [Web Applications](../web-applications-project/)

A secure, HIPAA-conscious WhatsApp-based medical document vault that enables users to store, organize, and retrieve their medical reports entirely through WhatsApp conversation.

## 🎯 Project Overview

This system allows users to:
- 📤 Upload medical reports (PDF/JPG/PNG) via WhatsApp
- 🗂️ Organize reports with metadata (date, hospital, type)
- 🔍 Search and retrieve reports using simple commands
- 🔒 Securely store documents with encryption
- 📊 (Optional) Generate analytics and insights

## 🏗️ Architecture

### **Webhook/Pub-Sub & Push-Pull Pattern**

The system uses a modern, scalable architecture:

1. **Webhook Endpoint (Push)**: Receives WhatsApp messages as webhooks
2. **Message Queue (Pub-Sub)**: Decouples ingestion from processing
3. **Worker Pool (Pull)**: Processes messages asynchronously
4. **Outbound Queue**: Manages message delivery to WhatsApp

### Architecture Diagrams

All architecture diagrams are available in PlantUML format in the `docs/diagrams/` directory:

- **[System Architecture](docs/diagrams/system-architecture.puml)**: Complete system overview showing webhook/pub-sub and push-pull patterns
- **[Component Diagram](docs/diagrams/component-diagram.puml)**: Detailed component interactions using C4 model
- **[Upload Flow Sequence](docs/diagrams/sequence-upload-flow.puml)**: Step-by-step document upload process
- **[Retrieval Flow Sequence](docs/diagrams/sequence-retrieval-flow.puml)**: Document retrieval and command processing
- **[Data Model](docs/diagrams/data-model.puml)**: Complete database schema
- **[Deployment Architecture](docs/diagrams/deployment-architecture.puml)**: Cloud deployment on AWS/DigitalOcean

#### Viewing PlantUML Diagrams

You can view the diagrams using:

1. **VS Code Extension**: Install "PlantUML" extension
2. **Online**: Visit [PlantUML Web Server](http://www.plantuml.com/plantuml/uml/)
3. **Command Line**: Install PlantUML and run:
   ```bash
   plantuml docs/diagrams/*.puml
   ```

## 📋 MVP Features

### ✅ Implemented (Documentation & Architecture)

Based on the 10 EPICs from the requirements:

#### **EPIC 1: WhatsApp Business API Integration**
- Webhook endpoint for incoming messages
- Support for text, images, and PDFs
- Message acknowledgment within time limits

#### **EPIC 2: Media Download & Validation**
- Secure media fetching
- File format validation (PDF/JPG/PNG)
- File size limits
- Optional virus scanning

#### **EPIC 3: Conversational Metadata Collection**
- Session management per phone number
- Multi-step conversation flow
- Input validation and re-prompting
- Cancel/restart support
- Timeout handling

#### **EPIC 4: Secure File Storage**
- AWS S3 or DigitalOcean Spaces integration
- Private bucket configuration
- Server-side encryption
- Structured naming: `/users/{phone}/reports/{year}/{uuid}.{ext}`

#### **EPIC 5: Metadata Persistence**
- PostgreSQL database schema
- Comprehensive metadata fields
- Indexing for fast retrieval
- Soft delete support

#### **EPIC 6: Report Retrieval**
- Command-based retrieval: `LIST`, `LIST <year>`, `GET <id>`, `LATEST`
- Pagination for long results
- Secure file re-delivery

#### **EPIC 7: Privacy & Security**
- Phone-based access control
- No sensitive data in logs
- Secure environment variables
- Audit trail

#### **EPIC 8: Error Handling & UX**
- Friendly error messages
- Retry prompts
- Help command
- Clear confirmations

#### **EPIC 9: Observability**
- Request logging
- Error tracking
- Health checks

#### **EPIC 10: Deployment**
- Environment setup
- Documentation
- Deployment guides

## 🛠️ Technology Stack

### **Core**
- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Async Workers**: Celery / RQ
- **Message Queue**: Redis / RabbitMQ

### **Storage**
- **Database**: PostgreSQL 15+
- **Cache/Queue**: Redis 7+
- **Object Storage**: AWS S3 / DigitalOcean Spaces

### **WhatsApp Integration**
- **Provider Options**:
  - Meta WhatsApp Business API
  - Twilio WhatsApp API
  - 360dialog

### **Deployment**
- **Container**: Docker
- **Orchestration**: Kubernetes / ECS Fargate
- **Cloud**: AWS / DigitalOcean
- **CI/CD**: GitHub Actions

### **Monitoring**
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: CloudWatch / ELK Stack
- **Error Tracking**: Sentry

## 📁 Project Structure

```
whatsapp-medical-vault/
├── src/
│   └── whatsapp_vault/
│       ├── __init__.py
│       ├── api/                    # FastAPI webhook endpoints
│       │   ├── __init__.py
│       │   ├── webhook.py         # WhatsApp webhook handler
│       │   ├── health.py          # Health check endpoints
│       │   └── middleware.py      # Request validation, rate limiting
│       ├── services/              # Business logic
│       │   ├── __init__.py
│       │   ├── session_manager.py # Conversation state management
│       │   ├── media_service.py   # Media download & validation
│       │   ├── metadata_collector.py # Metadata collection flow
│       │   ├── storage_service.py # S3/Spaces integration
│       │   ├── retrieval_service.py # Report search & retrieval
│       │   ├── command_processor.py # Command parsing & execution
│       │   ├── auth_service.py    # Phone-based authorization
│       │   └── audit_service.py   # Audit logging
│       ├── models/                # Database models
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── report.py
│       │   ├── session.py
│       │   ├── metadata.py
│       │   └── audit.py
│       ├── workers/               # Async task workers
│       │   ├── __init__.py
│       │   ├── message_processor.py # Main message processing
│       │   ├── media_processor.py   # Media handling
│       │   └── delivery_worker.py   # Outbound message delivery
│       ├── utils/                 # Utilities
│       │   ├── __init__.py
│       │   ├── config.py          # Configuration management
│       │   ├── logger.py          # Structured logging
│       │   ├── validators.py      # Input validation
│       │   └── security.py        # Security utilities
│       └── analytics/             # Optional analytics
│           ├── __init__.py
│           ├── analyzer.py        # Data analysis
│           └── report_generator.py # Report generation
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_webhook.py
│   ├── test_session_manager.py
│   ├── test_media_service.py
│   ├── test_metadata_collector.py
│   ├── test_retrieval_service.py
│   └── test_commands.py
├── docs/                          # Documentation
│   ├── diagrams/                  # PlantUML diagrams
│   │   ├── system-architecture.puml
│   │   ├── component-diagram.puml
│   │   ├── sequence-upload-flow.puml
│   │   ├── sequence-retrieval-flow.puml
│   │   ├── data-model.puml
│   │   └── deployment-architecture.puml
│   ├── ARCHITECTURE.md            # Architecture documentation
│   ├── API.md                     # API documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── SECURITY.md                # Security considerations
│   └── EPICS.md                   # Detailed EPICS documentation
├── configs/                       # Configuration files
│   ├── development.yaml
│   ├── production.yaml
│   └── test.yaml
├── examples/                      # Example usage
│   ├── example_conversation.md
│   └── example_commands.md
├── scripts/                       # Utility scripts
│   ├── setup_db.py
│   ├── migrate.py
│   └── seed_data.py
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions workflow
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- AWS Account (for S3) or DigitalOcean Account (for Spaces)
- WhatsApp Business API credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/smaruf/python-ai-course.git
   cd python-ai-course/whatsapp-medical-vault
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   python scripts/setup_db.py
   ```

5. **Run with Docker Compose** (Recommended)
   ```bash
   docker-compose up -d
   ```

   Or **run locally**:
   ```bash
   # Terminal 1: API Server
   uvicorn src.whatsapp_vault.api.webhook:app --reload --port 8000

   # Terminal 2: Worker
   celery -A src.whatsapp_vault.workers.message_processor worker --loglevel=info

   # Terminal 3: Delivery Worker
   celery -A src.whatsapp_vault.workers.delivery_worker worker --loglevel=info
   ```

### Configuration

Edit `.env` file:

```bash
# WhatsApp Configuration
WHATSAPP_PROVIDER=meta  # meta, twilio, or 360dialog
WHATSAPP_API_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_id_here
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_verify_token_here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/whatsapp_vault
REDIS_URL=redis://localhost:6379/0

# Storage
STORAGE_PROVIDER=s3  # s3 or spaces
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1

# Security
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Optional: Virus Scanning
ENABLE_VIRUS_SCAN=false
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
```

## 📱 User Commands

Users interact via WhatsApp text messages:

### Upload Flow
1. Send PDF/image to WhatsApp
2. System asks for report date
3. User provides date (DD/MM/YYYY)
4. System asks for hospital name
5. User provides hospital
6. System asks for report type
7. User provides type (Blood Test, MRI, etc.)
8. System confirms upload

### Retrieval Commands

- `LIST` - List all reports
- `LIST 2025` - List reports from 2025
- `GET 1` - Get report with ID 1
- `LATEST` - Get the most recent report
- `HELP` - Show available commands
- `CANCEL` - Cancel current operation

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/whatsapp_vault --cov-report=html

# Run specific test
pytest tests/test_webhook.py -v
```

## 🔒 Security Considerations

- ✅ Phone-based access control (users can only access their own files)
- ✅ Server-side encryption for files at rest
- ✅ HTTPS/TLS for all communications
- ✅ Webhook signature verification
- ✅ No sensitive data in application logs
- ✅ Phone number masking in logs
- ✅ Rate limiting to prevent abuse
- ✅ Environment variable management for secrets
- ✅ Audit trail for all access
- ✅ Soft delete (no permanent data loss)
- ✅ Session expiration and timeout
- ✅ Input validation and sanitization

## 📊 Optional: Analytics & Reporting

The system includes optional analytics features:

- **Usage Analytics**: Track upload/download patterns
- **Report Insights**: Most common report types, hospitals
- **User Engagement**: Active users, retention metrics
- **Health Metrics**: System performance, error rates

Enable in config:
```yaml
analytics:
  enabled: true
  retention_days: 90
```

## 🏥 HIPAA & Compliance Notes

While this MVP is HIPAA-conscious, full HIPAA compliance requires:

1. **Business Associate Agreement (BAA)** with cloud providers
2. **Encryption** at rest and in transit (✅ implemented)
3. **Access Controls** and audit trails (✅ implemented)
4. **Data Backup** and disaster recovery
5. **Security Risk Assessment**
6. **Staff Training**
7. **Incident Response Plan**

Consult with legal/compliance experts before production use with real medical data.

## 🚀 Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions for:

- AWS (ECS Fargate, RDS, S3, ElastiCache)
- DigitalOcean (App Platform, Managed Database, Spaces)
- Kubernetes (Self-hosted)

## 📚 Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md) - Detailed design decisions
- [API Documentation](docs/API.md) - WhatsApp webhook API
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Security Guide](docs/SECURITY.md) - Security best practices
- [EPICS Documentation](docs/EPICS.md) - Detailed feature breakdown

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- WhatsApp Business API Documentation
- FastAPI Framework
- Celery Distributed Task Queue
- PostgreSQL Database
- Redis Cache & Queue

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation
- Review the architecture diagrams

## 🔄 Roadmap

### Phase 2 (Future)
- 🔍 OCR & text extraction from documents
- 🤖 AI-based report summarization
- 🔎 Search by medical terms/keywords
- 👨‍👩‍👧‍👦 Multi-user family accounts
- 💻 Web dashboard for browsing
- 📧 Email integration
- 📱 Mobile app

### Phase 3 (Future)
- 🌍 Multi-language support
- 📊 Advanced analytics dashboard
- 🔔 Reminder notifications
- 🔗 Integration with health systems
- 📅 Appointment scheduling
- 💊 Medication tracking

---

**Note**: This project is currently in the documentation and architecture phase. Implementation of the actual code will follow the architecture defined in this repository.
