# Hybrid Go + Python Fraud Risk Platform — project plan

## 1. Architecture overview

```
                        +-------------------------+
                        |       Client apps        |
                        |    (Mobile + Web/Desktop)|
                        +------------+--------------+
                                     |
                                     | HTTPS / gRPC-Web (TLS)
                                     v
        +--------------------------------------------------------+
        |              Backend infrastructure                     |
        |                                                          |
        |  +------------------------+   gRPC   +------------------+|
        |  |   Edge gateway (Go)    | -------> | AI + banking core||
        |  |  - TLS termination     |          |     (Python)     ||
        |  |  - Auth / session      | <------- |  - Risk scoring  ||
        |  |  - Request validation  |  verdict |  - Transactions  ||
        |  |  - Timeout + fallback  |          |                  ||
        |  +------------------------+          +------------------+|
        |                                                          |
        +--------------------------------------------------------+
```

## 2. User action / data flow

```
[Client app: mobile or web]
        |
        v
[Go edge gateway]
  - authenticate request
  - validate payload
  - forward over gRPC
        |
        v
[Python AI core]
  - parse transaction + telemetry
  - compute risk score
        |
        +------------------+------------------+
        |                                     |
        v                                     v
[Approve]                          [Block / challenge MFA]
  low risk score                      high risk score
```

## 3. Phased implementation plan

```
Phase 1 — Minimal viable core
  [ ] Go gateway: standard TLS, REST or gRPC-Web, JWT/session auth
  [ ] Go gateway: timeout + safe fallback if AI core is slow/down
  [ ] Python core: gRPC service with placeholder rules-based logic
  [ ] End-to-end request path validated (no real ML yet)
        |
        v
Phase 2 — Client support, both platforms
  [ ] Single consistent API surface (REST or gRPC-Web)
  [ ] Mobile client (iOS/Android or cross-platform) wired to gateway
  [ ] Web/desktop client wired to same gateway endpoints
  [ ] Optional device/browser telemetry field added to request
        |
        v
Phase 3 — Incremental security hardening
  [ ] Rate limiting + basic abuse detection at gateway
  [ ] Structured logging / observability across both services
  [ ] TLS certificate pinning on mobile clients
  [ ] Evaluate need for custom obfuscation only if real threat observed
        |
        v
Phase 4 — Real AI model
  [ ] Swap placeholder rules for trained model (e.g. XGBoost)
  [ ] Keep same gRPC contract so gateway code is unchanged
  [ ] Add feedback loop / retraining once volume justifies it
```

## 4. SWOT summary

```
+-----------------------------+-----------------------------+
| STRENGTHS                   | WEAKNESSES                   |
| - Mature, hireable stacks   | - Two toolchains to maintain |
| - Decoupled via gRPC        | - Custom crypto = risk early |
| - Placeholder-first testing | - Tight latency budget       |
+-----------------------------+-----------------------------+
| OPPORTUNITIES               | THREATS                      |
| - Swappable/splittable core | - Compliance/explainability  |
| - One API for all clients   | - Over-engineering edge first|
|                              | - No fallback if core is down|
+-----------------------------+-----------------------------+
```

## 5. BCG-style portfolio view

```
STARS (invest)                  QUESTION MARKS (validate first)
- Go edge gateway                - Real ML fraud model
- gRPC contract

CASH COWS (low effort, keep)    DOGS (deprioritize)
- Standard TLS auth              - Custom obfuscation layer
                                  - Bespoke behavioral biometrics
```

## 6. Resourcing notes

- One owner for Go gateway + client contracts.
- One owner for Python core + model.
- Compute budget for the AI service is the main constraint on model
  choice and the most likely thing to break the latency target —
  size the model to the hardware, not the other way around.
