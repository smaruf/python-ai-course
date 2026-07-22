# claude.md — AI Coding Guidelines for Trading AI Platform

Behavioral guidelines for AI-assisted development in this repository.
These rules apply to all AI assistants (Claude, Copilot, etc.) working on this project.

---

## 1. Think Before Coding

**Don't assume. Surface tradeoffs. Ask when unclear.**

- State assumptions explicitly before implementing.
- If multiple design options exist, present them — don't pick silently.
- If something is financially sensitive (orders, ledger, FIX messages), **stop and ask**.
- Prefer clarity over cleverness in financial code.

---

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No premature abstraction for single-use code.
- Java 21 features (Records, Pattern Matching, Virtual Threads) are preferred where they add clarity.
- Keep Spring `@Service` classes under 200 lines.

---

## 3. Surgical Changes

**Touch only what you must.**

- Don't "improve" adjacent code or comments unless asked.
- Match existing style in the module you are editing.
- Remove only imports/symbols that *your* changes made unused.
- If you spot unrelated dead code, mention it — don't delete it.

---

## 4. Financial Domain Rules (Non-Negotiable)

These are hard rules for this project, not suggestions:

| Rule | Detail |
|---|---|
| **Idempotency** | FIX `NewOrderSingle` must use unique `ClOrdID`. Backend must detect and reject duplicate IDs. |
| **HITL** | AI tools (`propose_trade`, `fund_account`) must NEVER auto-execute. Always return a pending confirmation payload. |
| **Thread Isolation** | QuickFIX/J message handlers run on the FIX session thread. Never block with synchronous DB calls there — publish to Kafka and process asynchronously. |
| **Audit Log** | Every AI prompt, LLM reasoning step, tool invocation, and FIX message must be appended to the audit table/topic. No exceptions. |
| **No Secret Commits** | Never commit API keys, FIX credentials, or database passwords. Use environment variables or Vault references. |

---

## 5. Module-Specific Notes

### `fix-nasdaq-engine`
- QuickFIX/J `Application` callbacks (`onMessage`, `toApp`, `fromApp`) must be non-blocking.
- ITCH 5.0 feed parsing (Nassau) should use a dedicated `ExecutorService`.
- OpenFAST templates must be loaded from classpath; never hard-code field IDs.

### `ai-gateway`
- Spring AI `@Tool` methods must be annotated with `@Tool(returnDirect = false)` to force the HITL confirmation step.
- Chat memory must be scoped per authenticated user session.

### `payment-ledger`
- All ledger writes must be within a `@Transactional(isolation = SERIALIZABLE)` boundary.
- Double-entry: every debit must have a corresponding credit in the same transaction.

### `shared-kernel`
- Domain events are immutable records: `record OrderCreatedEvent(UUID orderId, ...)`.
- Published via Spring `ApplicationEventPublisher`; consumed by Kafka listeners in other modules.

---

## 6. Testing Standards

- Unit tests: JUnit 5 + Mockito — one test class per production class.
- Integration tests: Spring Boot Test with `@Testcontainers` for Postgres/Kafka/Redis.
- E2E tests: Python PyTest scripts in `scripts/testing/`.
- AI evaluation: Ragas in `scripts/testing/eval_ai_tools.py`.
- Target: **80 % line coverage** on `fix-nasdaq-engine` and `payment-ledger`.

---

## 7. Build & Verify

```bash
# Maven
mvn clean verify

# Gradle
./gradlew check

# Python tests
pytest scripts/testing/ -v
```

Always run the build before declaring work complete.
