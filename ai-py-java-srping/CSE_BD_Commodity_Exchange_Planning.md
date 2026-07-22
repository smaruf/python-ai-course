Optimizing the architecture for the **Chittagong Stock Exchange (CSE) of Bangladesh** requires adapting the platform to the specific regulatory, economic, and infrastructural context of Bangladesh. 

The CSE commodity exchange focuses heavily on **agricultural price stabilization** (rice, jute, spices), **RMG (Ready-Made Garments) raw materials** (cotton, yarn), and **precious metals** (gold). Furthermore, it must comply with **BSEC (Bangladesh Securities and Exchange Commission)** regulations, integrate with **CDBL (Central Depository Bangladesh Limited)**, support **Shariah-compliant trading**, and handle local payment rails like **BEFTN** and **MFS (bKash/Nagad)**.

Here is the optimized, localized Master Plan.

---

# 🇧🇩 1. CSE-BD Specific Feature List

### A. Localized Commodity & Contract Management
*   **Agri-Commodities**: Paddy, Fine/Coarse Rice, Jute, Red Chilli, Turmeric, Mustard Seed.
*   **Industrial/RMG**: Raw Cotton, Cotton Yarn, Steel Billets.
*   **Precious Metals**: Gold (1 Pokti / 116.64 grams standard).
*   **Contract Specs**: Tailored to local harvest seasons and RMG import cycles. Lot sizes adjusted for local SME and farmer accessibility.

### B. Regulatory, Shariah & Clearing Integration
*   **Shariah Compliance Engine**: Strict enforcement of Islamic trading rules (No short selling, no excessive speculation/Gharar, mandatory physical delivery intent or valid Tawarruq structures).
*   **CDBL Integration**: Automated API/Batch integration with the Central Depository Bangladesh Limited for issuing, transferring, and pledging **Electronic Warehouse Receipts (EWR)**.
*   **BSEC Reporting**: Automated generation of daily trade reports, margin reports, and large exposure reports in the exact XML/CSV formats mandated by BSEC.

### C. Localized Payment & Settlement Rails
*   **BEFTN (Bulk)**: Integration with Bangladesh Electronic Funds Transfer Network for daily bulk settlement of margin calls and payouts to broker bank accounts.
*   **MFS (Retail)**: Integration with bKash, Nagad, and Rocket for retail farmers and small traders to deposit/withdraw margin.
*   **NPSB/RTGS**: Real-time gross settlement for high-value institutional transfers.

### D. Accessibility & Market Data
*   **Low-Bandwidth Optimization**: APIs designed for 3G/4G mobile networks prevalent in rural BD. Payloads are heavily compressed.
*   **Bangla Language Support**: Full localization of API error messages, SMS alerts, and AI Assistant responses.
*   **SMS/IVR Fallback**: Integration with local SMS gateways (e.g., SSL Wireless, BulkSMSBD) for trade confirmations and margin calls for users without smartphones.

---

# 🏗️ 2. Architecture Adjustments for CSE-BD

### A. Data Residency & Local Cloud
BSEC mandates that financial data must reside within Bangladesh. 
*   **Infrastructure**: Deploy on local Tier-3/4 Data Centers (e.g., BTCL, Rankers, or local AWS/Azure outposts if compliant) rather than global public clouds, or use a hybrid model where the core ledger stays on-prem/local.
*   **Pulumi (Python)**: IaC scripts must provision local VPCs, on-prem Kubernetes clusters, or compliant local cloud instances.

### B. Legacy Broker Integration
Many local CSE brokers use older, desktop-based trading software.
*   **Adapter Layer**: Add a specific Spring Boot module that exposes a legacy SOAP/Flat-file API alongside modern REST/WebSockets, allowing older broker software to connect without rewriting their front-ends.

### C. Matching Engine Tweaks
*   **Price Bands**: Implement BSEC-mandated "Circuit Breakers" and price bands (e.g., ±10% movement limits) directly in the Matching Engine to prevent extreme volatility in illiquid agri-commodities.

---

# 🐍 3. Python "Outer Loop" for CSE-BD Context

The Python scripts must be tailored to test local integrations, regulatory compliance, and local network conditions.

### A. Local Payment & CDBL E2E Testing (`test_local_integrations.py`)
*   **BEFTN File Generation**: PyTest scripts that trigger a settlement run, assert the Java app generates the exact NPSB/BEFTN ASCII file format, and parse it to verify correctness.
*   **CDBL Mock**: A Python mock server simulating the CDBL EWR API, testing the creation and transfer of digital warehouse receipts for Jute and Rice.

### B. Shariah & Regulatory Guardrails (`eval_shariah_compliance.py`)
*   **Rule Testing**: Automated tests ensuring the engine rejects illegal orders (e.g., short selling of physical Rice). 
*   **AI Evaluation (Ragas)**: Evaluating the Spring AI Assistant to ensure it answers in Bangla, understands local units of measurement (e.g., *Mond*, *Khol*, *Pokti*), and refuses to give non-Shariah-compliant trading advice.

### C. Rural Network Load Testing (`locust_mobile_sim.py`)
*   **High-Latency Simulation**: Locust scripts configured to simulate 3G/4G network profiles (high latency, packet loss) to ensure the WebSocket market data feeds gracefully degrade and reconnect without duplicating trades.

---

# ☁️ 4. Infrastructure as Code (Pulumi + Python)

```python
# infra/__main__.py (Conceptual Pulumi for BD Data Residency)
import pulumi
import pulumi_kubernetes as k8s

# Enforce local data residency
local_cluster = k8s.Provider("bd-local-provider", 
    kubeconfig=config.get("bd_local_kubeconfig")
)

# Core Trading Engine (Must run in BD)
trading_deployment = k8s.apps.v1.Deployment("cse-trading-engine",
    spec={...},
    opts=pulumi.ResourceOptions(provider=local_cluster)
)

# Local Database (PostgreSQL) - Encrypted at rest per BSEC rules
ledger_db = pulumi.Command("setup-db",
    create="psql -c 'CREATE DATABASE cse_ledger;'"
)
```

---

# 🔄 5. CI/CD Pipeline Adjustments

```yaml
# .github/workflows/cse-bd-pipeline.yml
jobs:
  # 1. Core Java Build
  build-java:
    # ... standard gradle build ...

  # 2. Localized E2E & Regulatory Tests (Python)
  bd-regulatory-tests:
    needs: build-java
    steps:
      - name: Test BEFTN & CDBL File Formats
        run: pytest scripts/testing/test_local_integrations.py
      - name: Verify Shariah & Circuit Breaker Rules
        run: pytest scripts/testing/test_bd_market_rules.py
      - name: AI Bangla & Local Unit Evaluation
        run: python scripts/testing/eval_shariah_compliance.py

  # 3. Low-Bandwidth Load Test
  rural-network-load-test:
    steps:
      - name: Simulate 3G/4G Mobile Traffic
        run: locust -f scripts/load/locust_mobile_sim.py --headless -u 2000 --run-time 5m

  # 4. Deploy to Local BD Data Center
  deploy-local:
    needs: bd-regulatory-tests
    steps:
      - name: Deploy to On-Prem / Local Cloud
        run: pulumi up --yes --stack bd-prod
```

---

# 📅 6. Execution Roadmap (16 Weeks)

### Phase 1: Core Engine & Local Setup (Weeks 1-4)
*   Initialize Java/Spring modules. Set up WSL/Docker local env via Python.
*   Build the Matching Engine with **BSEC Circuit Breakers/Price Bands**.
*   Define local commodity contracts (Rice, Jute, Cotton, Gold).

### Phase 2: Clearing, CDBL & Shariah (Weeks 5-8)
*   Implement the **Shariah Compliance Engine** (blocking short sales, enforcing delivery).
*   Build the **CDBL Integration Module** for E-Warehouse Receipts.
*   Implement Initial/Variation Margin calculations tailored to local agri-volatility.

### Phase 3: Local Payments & Broker Adapters (Weeks 9-12)
*   Build the **BEFTN Bulk Settlement** generator and parser.
*   Integrate **bKash/Nagad** APIs for retail margin funding.
*   Build the Legacy Adapter for older CSE broker desktop software.

### Phase 4: AI, Market Data & Mobile Optimization (Weeks 13-14)
*   Integrate **Spring AI** with Bangla language prompts and local unit conversions.
*   Optimize WebSocket payloads for low-bandwidth mobile networks.
*   Integrate SSL Wireless SMS gateway for trade alerts.

### Phase 5: Testing, BSEC Audit & Go-Live (Weeks 15-16)
*   Run Python E2E tests for CDBL and BEFTN.
*   Conduct low-bandwidth Locust load tests.
*   **BSEC Regulatory Audit**: Present system architecture, audit logs, and Shariah compliance reports to the Bangladesh Securities and Exchange Commission.
*   **Go Live.**

---

# 🛡️ 7. Clean Code & Domain Rules for CSE-BD

1.  **Strict Decimal & Unit Handling**: Use `BigDecimal` for all prices. Create specific Value Objects for local units (e.g., `class Pokti`, `class Mond`) to prevent conversion errors between metric and local traditional weights.
2.  **Immutability for BSEC Audit**: BSEC requires strict audit trails. Use Event Sourcing or append-only audit tables for every state change. Never overwrite trade records.
3.  **Data Localization**: Ensure no PII (Personally Identifiable Information) or financial ledger data is cached in global CDNs or external S3 buckets. All data must be encrypted and stored locally.
4.  **Graceful Degradation**: If the MFS (bKash) or SMS gateway goes down, the core trading engine must continue to function. Use the **Circuit Breaker pattern** (via Resilience4j in Spring) to isolate external local payment APIs from the core matching engine.
