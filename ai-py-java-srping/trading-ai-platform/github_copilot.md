# GitHub Copilot Workspace Instructions

This file provides context for GitHub Copilot (and other AI code completion tools) working inside the **Trading AI Platform** project.

---

## Project Purpose

This is a **financial trading platform** integrating:
- **Spring Boot 3 / Java 21** — backend core
- **QuickFIX/J** — FIX 4.4/5.0 SP2 session management and order routing
- **Nassau (ITCH 5.0)** — Nasdaq TotalView market data feed parsing
- **OpenFAST** — CME-style binary fast message encoding/decoding
- **Spring AI** — LLM tool-calling, RAG, and WebSocket chat
- **Python scripts** — DevOps, E2E testing (PyTest), load testing (Locust), AI evaluation (Ragas)

---

## Copilot Preferences for This Repo

### Java / Spring Boot
- Target **Java 21**. Use Records, sealed classes, pattern matching, and virtual threads where appropriate.
- Use **Hexagonal Architecture** (ports and adapters) inside each module under `app/`.
- Prefer constructor injection over field injection (`@Autowired` on fields is discouraged).
- Use `@Slf4j` (Lombok) for logging — no `System.out.println`.
- Exception handling: create domain-specific exceptions in `shared-kernel`; never swallow exceptions silently.

### QuickFIX/J
- Implement `quickfix.Application` interface in `fix-nasdaq-engine`.
- FIX session config lives in `src/main/resources/quickfix.cfg`.
- Message handlers must be **non-blocking** — offload to Kafka or a thread pool immediately.
- Use `quickfix.field.*` constants, never raw tag integers.

### Nassau ITCH 5.0
- Use `com.paritytrading.nassau` classes to parse the binary ITCH feed.
- The `BinaryFeedClient` connects to the Nasdaq multicast feed.
- Message handlers implement the `com.paritytrading.nassau.MessageListener` interface.

### OpenFAST
- Load template XML from `src/main/resources/fast-templates/`.
- Use `org.openfast.Context` and `org.openfast.Message` for encode/decode.
- Templates are exchange-specific; keep them versioned in source control.

### Spring AI
- Tool methods are annotated with `@Tool` from `org.springframework.ai.tool`.
- All tools that modify state must follow the HITL pattern: return a `ProposedAction` record instead of executing directly.
- Use `ChatMemory` scoped to the authenticated user's session.

### Python Scripts
- Use `asyncio` for the `mock_fix_server.py` TCP socket server.
- PyTest fixtures in `conftest.py` should handle app startup/teardown.
- Locust tasks extend `HttpUser` or `FastHttpUser`.

---

## What Copilot Should NOT Do

- Do **not** auto-generate code that executes trades or payment transfers without a confirmation step.
- Do **not** hard-code connection strings, API keys, or credentials.
- Do **not** use `Thread.sleep()` inside FIX message handlers.
- Do **not** create new top-level packages — follow the existing `com.tradingai.<module>` package structure.
- Do **not** skip the audit log when writing FIX messages or AI tool invocations.

---

## Package Structure

```
com.tradingai.gateway          ← ai-gateway module
com.tradingai.fix              ← fix-nasdaq-engine module
com.tradingai.payment          ← payment-ledger module
com.tradingai.shared           ← shared-kernel module
com.tradingai.app              ← bootstrap module
```

---

## Common Patterns

### Publishing a Domain Event
```java
// In a @Service
applicationEventPublisher.publishEvent(new OrderCreatedEvent(orderId, symbol, qty));
```

### Non-blocking FIX handler
```java
@Override
public void fromApp(Message message, SessionID sessionID) throws FieldNotFound {
    kafkaTemplate.send("fix.inbound", message.toString());  // non-blocking
}
```

### HITL tool example
```java
@Tool(description = "Propose a new equity order — requires user confirmation before execution")
public ProposedAction proposeTrade(String symbol, int qty, String side) {
    return new ProposedAction("trade", Map.of("symbol", symbol, "qty", qty, "side", side));
}
```
