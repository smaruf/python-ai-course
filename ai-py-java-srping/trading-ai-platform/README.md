# Trading AI Platform 🏦

> **Part of [Python AI Course](../../README.md)** | [Planning Document](../Spring_Java_AI_Payment_NASDAQ_Planning.md)

An AI-powered payment and Nasdaq FIX trading platform built with Java 21 + Spring Boot 3, integrating **QuickFIX/J**, **Nasdaq ITCH 5.0** (via Nassau), and **OpenFAST** for market data. The Python "Outer Loop" handles DevOps, testing, and AI evaluation.

---

## 📁 Project Structure

```text
trading-ai-platform/
├── app/                          # 🟢 Java Core (Inner Loop)
│   ├── ai-gateway/               # Spring AI, Tool Calling, Chat Memory
│   ├── fix-nasdaq-engine/        # QuickFIX/J, ITCH 5.0, OpenFAST, Order Routing
│   ├── payment-ledger/           # Double-entry bookkeeping, Wallets
│   ├── shared-kernel/            # Domain events, Security, Audit, Utils
│   └── bootstrap/                # Spring Boot Main Application
├── scripts/                      # 🐍 Python Outer Loop
│   ├── devops/
│   │   ├── setup_wsl_docker.py   # Local env bootstrapper
│   │   └── deploy_cloud.py       # CI/CD deployment glue
│   ├── testing/
│   │   ├── mock_fix_server.py    # TCP socket mock for Nasdaq FIX
│   │   ├── test_e2e_trading.py   # PyTest E2E flows
│   │   └── eval_ai_tools.py      # Ragas AI evaluation
│   └── load/
│       └── locustfile.py         # Locust load testing
├── infra/                        # ☁️ Infrastructure as Code (Pulumi/Python)
├── docker/                       # 🐳 Containerisation
│   ├── docker-compose.yml
│   └── Dockerfile
├── .github/workflows/
│   └── ci-cd.yml                 # Build → Test → Deploy
├── pom.xml                       # Maven parent POM (multi-module)
├── build.gradle                  # Gradle root build
├── settings.gradle               # Gradle settings (all modules)
├── claude.md                     # AI coding guidelines
└── github_copilot.md             # GitHub Copilot workspace instructions
```

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|---|---|---|
| **Core Framework** | Java 21, Spring Boot 3.3 | High-performance backend |
| **AI Integration** | Spring AI | LLM orchestration, Tool calling, RAG |
| **FIX Protocol** | QuickFIX/J 2.3 | Nasdaq FIX session, message routing |
| **Market Data** | Nassau (ITCH 5.0) | Nasdaq TotalView-ITCH feed processing |
| **Fast Encoding** | OpenFAST | CME/exchange fast binary message encoding |
| **Databases** | PostgreSQL, Redis | ACID Ledger (SQL), Cache (NoSQL) |
| **Messaging** | Apache Kafka | Async domain events |
| **Testing (Python)** | PyTest, Locust, Ragas | E2E, Load, AI evaluation |
| **IaC** | Pulumi (Python) | Cloud provisioning |
| **CI/CD** | GitHub Actions | Automated build → test → deploy |

---

## 🚀 Quick Start

### Prerequisites
- Java 21+, Maven 3.9+ **or** Gradle 8+
- Docker Desktop (for local dependencies)
- Python 3.12+ (for scripts)

### Build with Maven
```bash
# From project root
mvn clean install -DskipTests

# Run the bootstrap application
mvn spring-boot:run -pl app/bootstrap
```

### Build with Gradle
```bash
# From project root
./gradlew build -x test

# Run the bootstrap application
./gradlew :app:bootstrap:bootRun
```

### Start Local Dependencies (Docker)
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Python Setup (Testing & DevOps scripts)
```bash
pip install -r scripts/requirements.txt
python scripts/devops/setup_wsl_docker.py
```

---

## 📦 Key Dependencies

### QuickFIX/J (FIX Protocol)
```xml
<dependency>
  <groupId>org.quickfixj</groupId>
  <artifactId>quickfixj-core</artifactId>
  <version>2.3.1</version>
</dependency>
```

### Nassau — Nasdaq ITCH 5.0
```xml
<dependency>
  <groupId>com.paritytrading.nassau</groupId>
  <artifactId>nassau-core</artifactId>
  <version>0.15.0</version>
</dependency>
```

### OpenFAST
```xml
<dependency>
  <groupId>org.openfast</groupId>
  <artifactId>openfast</artifactId>
  <version>1.1.2</version>
</dependency>
```

---

## 🔐 Financial Safety Rules

1. **Idempotency**: Every FIX order must carry a unique `ClOrdID`; duplicates are rejected.
2. **Human-in-the-Loop (HITL)**: The AI never executes trades automatically — it returns a "Proposed Action" requiring explicit user confirmation.
3. **Thread Isolation**: QuickFIX/J runs on dedicated threads; FIX processing must never block the Spring Tomcat pool.
4. **Immutable Audit Log**: Every AI prompt, tool call, and FIX message is written to an append-only audit store.

---

## 📅 Roadmap

| Phase | Weeks | Focus |
|---|---|---|
| **1 — Foundation** | 1-2 | Repo setup, Docker local env, Shared Kernel |
| **2 — Core Engines** | 3-5 | Payment Ledger, FIX/ITCH/OpenFAST engine, MockFIX server |
| **3 — AI Integration** | 6-7 | Spring AI tools, WebSocket chat, HITL flow |
| **4 — Python Outer Loop** | 8-9 | PyTest E2E, Locust load tests, Ragas AI eval |
| **5 — Cloud IaC & CI/CD** | 10-11 | Pulumi AWS, GitHub Actions pipeline, staging deploy |
| **6 — Production** | 12 | Security audit, FIX certification, Go Live |

---

## 🤝 Contributing

See `claude.md` for AI-assisted coding guidelines and `github_copilot.md` for Copilot workspace instructions.
