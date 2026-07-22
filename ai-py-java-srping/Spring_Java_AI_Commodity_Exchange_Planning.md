Building a **Commodity Exchange** introduces unique complexities compared to standard equity trading (like Nasdaq). Commodities involve **futures/options contracts, physical delivery logistics, margin/risk management, and high-frequency time-series market data**.

Here is the comprehensive Feature List and Project Plan, adapting our **Java/Spring Inner Loop** and **Python Outer Loop** architecture specifically for a Commodity Exchange.

---

# 📋 1. Commodity Exchange Feature List

### A. Core Trading & Matching Engine
*   **Contract Management**: Define commodity contracts (e.g., Gold 1kg, Crude Oil 1000 bbl), lot sizes, tick sizes, expiry months, and delivery locations.
*   **Order Types**: Market, Limit, Stop, Iceberg (hidden quantity), and Fill-or-Kill (FOK).
*   **Matching Engine**: Ultra-low latency Price-Time priority matching engine.
*   **FIX Gateway**: QuickFIX/J integration for institutional brokers to route orders via FIX 4.4/5.0.

### B. Clearing, Risk & Margin Management (Crucial for Commodities)
*   **Margin Calculation**: Initial Margin (IM) and Variation Margin (VM) calculations (e.g., SPAN-like risk models).
*   **Mark-to-Market (MTM)**: Daily settlement processes calculating daily P&L based on settlement prices.
*   **Margin Calls**: Automated generation of margin calls and forced liquidation (haircut) if accounts fall below maintenance margin.
*   **Position Limits**: Regulatory enforcement of maximum open positions per trader/commodity.

### C. Physical Delivery & Logistics (If applicable)
*   **E-Warehouse Receipts (EWR)**: Digital tokenization/registration of physical commodities stored in approved warehouses.
*   **Delivery Scheduling**: Matching buyers and sellers for physical delivery at contract expiry.
*   **Quality & Grading**: Integration with surveyor APIs (e.g., SGS) for commodity quality certification.

### D. Market Data & Analytics
*   **Time-Series Data**: Tick-by-tick trade data, order book snapshots (L2/L3), and historical OHLCV.
*   **Data Feeds**: REST, WebSocket, and FIX Market Data (MsgType=W) for real-time broadcasting.

### E. AI Assistant (Spring AI)
*   **Natural Language Trading**: "Buy 50 lots of December Gold Futures at $2,000."
*   **Risk & Margin Queries**: "What is the initial margin requirement for a short position in 100 lots of WTI Crude?"
*   **Market Intelligence**: "Summarize the order book depth for Copper and suggest an optimal limit price to avoid slippage."

---

# 🏗️ 2. Architecture Adjustments for Commodities

To support commodities, we tweak the previous architecture:

1.  **Database Shift**: 
    *   *PostgreSQL*: Ledger, Contracts, User Accounts, E-Warehouse Receipts.
    *   *TimescaleDB (or InfluxDB)*: **New addition.** High-performance time-series database for tick-by-tick market data and order book history.
    *   *Redis*: In-memory Order Book state, FIX session caching.
    *   *Kafka*: Event streaming (Trade matched -> Clearing -> Market Data broadcast).
2.  **Matching Engine Isolation**: The Matching Engine must be completely decoupled from the REST/Web APIs. It should consume order events from Kafka, match them in memory, and publish `TradeExecuted` events back to Kafka.

---

# 🐍 3. Python "Outer Loop" for Commodity Testing

Commodities require rigorous testing for edge cases in margin calculations and high-frequency data.

### A. E2E & Scenario Testing (`pytest`)
*   **Margin Scenario Testing**: Python scripts that simulate complex portfolio scenarios (e.g., hedged positions across correlated commodities like Heating Oil and Crude) and assert the Java Spring Risk Engine calculates the correct margin.
*   **Physical Delivery Flow**: PyTest scripts that simulate the full lifecycle: Contract creation -> Trading -> Expiry -> EWR generation -> Physical delivery settlement.

### B. Market Data Load Testing (`locust`)
*   **WebSocket & FIX Feed Stress Test**: Locust scripts simulating 10,000+ concurrent market data consumers to ensure the Spring WebFlux/Netty layer and Kafka consumers don't drop ticks during high volatility (e.g., during a major economic data release).

### C. AI Financial Guardrails (`eval_ai_tools.py`)
*   **Hallucination Prevention**: Using Ragas to ensure the AI *never* hallucinates contract specifications (e.g., it must know that 1 Gold contract = 100 oz, not 10 oz) and strictly enforces margin rules in its responses.

---

# ☁️ 4. Infrastructure & CI/CD (Pulumi + Python)

### Infrastructure as Code (`infra/__main__.py`)
Using Pulumi (Python) to provision a highly available, low-latency cloud environment:
*   **Compute**: AWS EKS (Kubernetes) with **node placement groups** to ensure the Matching Engine and Kafka pods run on physically close hardware to reduce network latency.
*   **Data**: Amazon RDS (Postgres), Amazon Timestream/TimescaleDB (Market Data), Amazon MSK (Kafka).
*   **Networking**: AWS Direct Connect or low-latency VPC setups for FIX gateway connectivity.

### CI/CD Pipeline (`ci-cd.yml`)
```yaml
# Specialized Commodity CI/CD Steps
jobs:
  risk-and-margin-validation:
    runs-on: ubuntu-latest
    steps:
      - name: Run Complex Margin Scenarios
        run: python scripts/testing/test_margin_scenarios.py
      
  market-data-load-test:
    runs-on: ubuntu-latest
    steps:
      - name: High-Frequency Tick Data Load Test
        run: locust -f scripts/load/market_data_locust.py --headless -u 5000 --run-time 5m
```

---

# 📅 5. Project Planning & Roadmap (16 Weeks)

Building an exchange is highly regulated and complex. We use an iterative, phased approach.

### Phase 1: Core Trading & Cash Settlement (Weeks 1-4)
*   **Java/Spring**: Build the Matching Engine, Contract Management, and basic Order Routing.
*   **FIX**: Implement QuickFIX/J Gateway for NewOrderSingle (D) and ExecutionReport (8).
*   **Python**: Write `mock_fix_server.py` to simulate broker connections. Set up WSL/Docker local dev environment.
*   **Milestone**: Users can place orders via FIX/REST, and the engine matches them in a cash-settled environment.

### Phase 2: Clearing, Risk & Margin (Weeks 5-8)
*   **Java/Spring**: Implement the Clearing House module. Build the Initial/Variation Margin calculators and Daily Mark-to-Market (MTM) Spring Batch jobs.
*   **Database**: Integrate TimescaleDB for historical trade and settlement data.
*   **Python**: Write PyTest scenarios for complex margin calculations and forced liquidation (haircut) logic.
*   **Milestone**: The system can safely manage leveraged commodity futures positions and handle margin calls.

### Phase 3: Market Data & High-Frequency Feeds (Weeks 9-11)
*   **Java/Spring**: Build the Market Data publishers. Implement L1/L2 order book broadcasting via WebSockets and FIX MarketDataSnapshotFullRefresh (W).
*   **Python**: Run Locust load tests to ensure the system can handle 50,000+ ticks per second without dropping data.
*   **Milestone**: Real-time, reliable market data feeds are operational for external consumers.

### Phase 4: Physical Delivery & AI Assistant (Weeks 12-14)
*   **Java/Spring**: Build the E-Warehouse Receipt (EWR) module and physical delivery scheduling. Integrate Spring AI for natural language trading and risk queries.
*   **Python**: Run AI evaluation scripts (`eval_ai_tools.py`) to ensure the LLM accurately understands commodity contract specs and margin rules.
*   **Milestone**: Full lifecycle from trading to physical delivery, plus AI-assisted user experience.

### Phase 5: Cloud Deployment, IaC & Hardening (Weeks 15-16)
*   **Python/IaC**: Finalize Pulumi scripts for AWS/GCP production deployment. Implement automated blue/green deployments.
*   **Security**: Penetration testing, FIX protocol certification, and regulatory audit log verification.
*   **Milestone**: Production-ready Commodity Exchange.

---

# 🛡️ 6. Clean Code & Domain Rules for Commodities

1.  **Decimal Precision is Law**: Never use `double` or `float` for prices, quantities, or margins. Use Java `BigDecimal` or primitive `long` (with implicit scaling) to prevent floating-point rounding errors in financial calculations.
2.  **Deterministic Matching**: The Matching Engine must be strictly single-threaded per order book to ensure deterministic, race-condition-free price-time matching.
3.  **Audit Everything**: Every order modification, cancellation, margin call, and AI prompt must be immutably logged. In commodity exchanges, regulatory bodies can demand replay of exact market states.
4.  **Idempotent FIX**: Ensure `ClOrdID` and `OrigClOrdID` are strictly validated to prevent duplicate order routing from brokers.
