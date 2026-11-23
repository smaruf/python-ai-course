# Matching Engine Project Plan (Java + Go)

Prepared 23 November 2026. Estimates are rough planning figures, to be replaced by measured data after the first phases.

## 1. Goal and scope

Build a new, scalable exchange matching engine from scratch, with modern protocols and an architecture that can grow from a single-market deployment to many markets and higher volumes. FIXimulator (github.com/iTasks/FIXimulator, a fork of FIXimulator/FIXimulator) is used as a **reference and test tool**, not as the code base.

**In scope**

- Order book and matching core (price-time priority first)
- FIX gateway for order entry, with a low-latency binary entry port later
- Market data publication (incremental feed and snapshots)
- Event journal, recovery and replication
- Test harness, conformance suite and benchmarks

**Out of scope for the first release** (planned as later work): clearing and settlement, full surveillance, a participant web portal, cross-market routing.

## 2. Assumptions and open questions

| Item | Status |
| --- | --- |
| Target market and its rules (tick sizes, lot sizes, price bands, sessions, auctions) | To be defined in Phase 0 |
| FIX versions required by participants (4.2 / 4.4 / 5.0 SP2) | To be confirmed with the target market and participants |
| Asset classes (equities first assumed) | To be confirmed |
| Deployment model (on-premise or cloud) | Open |
| Regulatory and certification path | Open, needs early engagement |
| FIXimulator licence terms | Not verified; no LICENSE file was visible in the repo root listing. Check before reusing any code |

## 3. Design principles

1. **Event log is the source of truth.** Every input command and output event is sequenced and persisted. State is rebuilt by replay.
2. **Deterministic core.** Same input log gives the same output log. No wall-clock reads, random numbers or I/O inside the engine; time arrives as an event.
3. **Single writer per partition.** One thread owns each symbol or symbol group. Scale by adding partitions, not locks.
4. **Gateways are separate** from the engine and scale out independently.
5. **Integer arithmetic.** Prices and quantities are fixed-point integers, never floating point.
6. **Specification first.** Behaviour is defined in language-neutral scenario files so Java and Go components can be checked against the same expectations.

## 4. Target architecture

```
Clients -> FIX / binary gateways -> Sequencer -> Matching partitions (by symbol)
(buy side)   (scale out)           (single writer)   deterministic, single-threaded
                                                          |
                                          Replicated event log (source of truth)
                                                          |
                         +--------------------------------+-----------------------+
                         |                                |                       |
                   Market data feed               Drop copy / audit      Reports, surveillance
```

**Components**

- **Gateways:** session handling, validation, translation between wire messages and core commands. No book state.
- **Sequencer:** assigns a global or per-partition sequence number and timestamp, then appends to the log.
- **Matching partitions:** hold order books for their symbols, consume commands, emit events.
- **Event log:** append-only, replicated, with periodic snapshots.
- **Projections:** market data, drop copy, reports and surveillance read the log and never touch the hot path.

## 5. Technology decisions

| Area | Choice | Reason |
| --- | --- | --- |
| Matching core and FIX gateway | Java | QuickFIX/J is mature; low-latency libraries (Agrona, Aeron, Chronicle Queue, Disruptor) are available |
| Market data fan-out, admin APIs, load generators, replay tools | Go | Simple concurrency and deployment; strong for network services |
| Replication and HA | Aeron Cluster (Raft-style) or an equivalent replicated log | Engine runs as a deterministic state machine on top |
| Wire encoding (binary) | SBE with FIXP session layer, plus an OUCH-style entry port and ITCH-style market data | Industry standards, low overhead |
| Message specs | FIX Orchestra | Generates validation and documentation; helps certification |
| Build | Maven or Gradle (Java), Go modules, CI on every commit | Reproducible builds |

Building the same engine fully in both languages doubles cost. Build the engine once, in Java, and use the shared scenario suite to add Go components safely. If a Go engine is wanted later as a comparison, the scenario suite is the conformance test.

## 6. Protocol roadmap

| Layer | Initial | Later |
| --- | --- | --- |
| Order entry | FIX 4.4 | FIX 5.0 SP2 over FIXT 1.1; OUCH-style binary port; SBE with FIXP |
| Market data | Simple snapshot plus incremental over TCP | ITCH-style binary feed with multicast option |
| Drop copy | FIX execution report copy | Binary variants |
| Admin | REST or gRPC | Web console |

Confirm which FIX versions the target participants need before fixing the scope.

## 7. Core engine design

**Order book**

- Per symbol: price levels on each side, FIFO queue per level, indexed by order ID for cancel and replace.
- Data structures: sorted structure for price levels (tree or array-based by tick), intrusive linked list per level, hash map for order lookup. Pre-allocate and reuse objects on the hot path to avoid garbage.

**Order types and rules (phased)**

- Phase 1: limit, market, day, cancel, cancel/replace.
- Phase 3: IOC, FOK, stop and stop-limit, iceberg (optional), opening and closing auctions, halts, circuit breakers and price bands, self-trade prevention, trade busts.

**Order state machine**

- Follow the FIX order state model exactly, including pending-cancel and pending-replace and the rules for what replace does to time priority.

**Events (minimum set)**

- OrderAccepted, OrderRejected, OrderCancelled, OrderReplaced, TradeExecuted, BookUpdated, SessionStateChanged, InstrumentStateChanged.
- Every event carries: sequence number, nanosecond timestamp, partition ID, symbol, and order or trade IDs.

**Identifiers**

- Exchange order IDs generated by the engine; client order IDs mapped per session with idempotent handling of retransmits.

## 8. Phased roadmap

| Phase | Scope | Deliverables | Exit criteria | Rough time |
| --- | --- | --- | --- | --- |
| 0. Specification | Market rules, order types, event schema, scenario file format | Spec document, schema, ADRs | Spec reviewed and signed off | 1 to 2 weeks |
| 1. Core book | Limit and market orders, price-time priority, cancel, replace | Core library, unit and property tests | All Phase 1 scenarios pass deterministically | 3 to 4 weeks |
| 2. FIX gateway | FIX 4.4 session and order flow, execution reports, rejects, sequence recovery | Gateway module, Banzai and fixclient demos | End-to-end order flow with automated tests | 3 to 4 weeks |
| 3. Rules and order types | IOC, FOK, stops, auctions, halts, price bands, self-trade prevention | Extended core, scenario packs | Rule scenarios pass; replay equals live | 4 to 6 weeks |
| 4. Market data and binary entry | Incremental feed and snapshots, OUCH-style entry | Publisher, binary gateway, Go fan-out service | Consistent book reconstruction by a test subscriber | 4 to 6 weeks |
| 5. Durability and HA | Journal, snapshots, replay, replicated log, failover | Recovery tooling, failover drills | Restart and failover without data loss in drills | 3 to 5 weeks |
| 6. Hardening | Benchmarks, soak and chaos tests, security, conformance | Performance report, certification pack | Targets met on agreed hardware | ongoing |

Total to a first deployable release is roughly 5 to 7 months for a small team, based on these estimates. Re-estimate at the end of Phase 1.

## 9. Testing strategy

1. **Golden scenario suite:** text files listing input commands and the expected output events. Run against every implementation and every change.
2. **Property-based tests:** invariants such as no crossed book, quantity conservation, price-time priority, no trade outside price bands.
3. **Replay tests:** feeding the recorded input log must reproduce the exact output log.
4. **FIX conformance and session tests:** logon, heartbeat, test request, sequence gap and resend, reject handling.
5. **Load and latency tests:** a Go or Java load generator drives many sessions; record latency percentiles and throughput.
6. **Chaos and failover tests:** kill nodes during load, verify recovery.
7. **Differential checks:** compare behaviour with FIXimulator where it applies.

**Role of FIXimulator and other tools**

- FIXimulator is a sell-side acceptor, so it cannot connect to your engine as a peer. Use it as a **behaviour reference** for order lifecycle flows, as a **downstream venue** if you later build a router, and for **client testing**.
- Use Banzai and the repo's `fixclient` as **buy-side initiators** for manual and scripted tests.
- Use your own load generator for volume.

## 10. Non-functional targets

Set these after the Phase 1 and 2 benchmarks, then track them. Suggested starting points to confirm or change:

- Deterministic replay: 100 percent of scenarios.
- Latency: measure per-hop (gateway, sequencer, matching) and publish percentiles, not only averages.
- Throughput: define target orders per second per partition and for the whole system.
- Availability: define recovery time and recovery point objectives for the first deployment.
- Security: authenticated sessions, TLS where supported, access control on admin interfaces, audit logging.

## 11. Team and roles

| Role | Responsibility |
| --- | --- |
| Tech lead / architect | Architecture, ADRs, reviews |
| Core engine engineers (Java) | Book, rules, journal, replication |
| Gateway and protocol engineer | FIX, binary protocols, Orchestra |
| Go services engineer | Market data fan-out, admin APIs, tools |
| QA / test automation | Scenario suite, load and chaos tests |
| Domain expert | Market rules, regulatory liaison |

A very small team can combine roles; keep the test automation role from the start.

## 12. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Subtle matching and replace semantics bugs | Property tests, golden scenarios, FIX spec review |
| Scope creep into clearing and surveillance | Fixed scope per phase; later work tracked separately |
| Latency spikes from garbage collection | Pre-allocated structures, allocation-free hot path, GC tuning, measurement from Phase 1 |
| Rework from late protocol changes | FIX Orchestra, gateway isolated from the core |
| Regulatory and certification delays | Start engagement during Phase 0 |
| Licence issues with reused code | Verify FIXimulator licence; reference behaviour, write original code |
| Key-person dependence | Documentation, ADRs, code review, shared scenario suite |

The FIXimulator README itself states it is a learning and testing tool, not a production exchange; do not connect it to live systems.

## 13. Repository and tooling

```
engine/
  core/            matching library (Java)
  gateway-fix/     FIX gateway (Java)
  gateway-binary/  OUCH/SBE gateway
  journal/         event log, snapshots, replication glue
  marketdata/      publisher
go-services/
  mdfanout/        market data distribution
  admin/           admin APIs
  loadgen/         load generator
scenarios/         golden input/expected-event files
docs/              spec, ADRs, runbooks
bench/             benchmark harnesses
```

Tooling: CI on every commit (build, unit, property and scenario tests), benchmark runs on a fixed machine, static analysis, dependency scanning.

## 14. First 30 days

1. Week 1: write the market rules spec; confirm FIX versions and asset classes; check the FIXimulator licence.
2. Week 1 to 2: define the event schema and scenario file format; agree numeric and time conventions.
3. Week 2 to 3: implement the in-memory order book with price-time priority and tests.
4. Week 3 to 4: build the first scenario pack (limit, market, cancel, replace, partial fills).
5. Week 4: minimal FIX 4.4 gateway; test with Banzai and `fixclient`; record the first benchmark.

## 15. Decisions to settle now

- Fixed-point scale for prices and quantities per instrument.
- Sequence number scheme (global or per partition) and nanosecond timestamp source.
- Order ID and idempotency scheme.
- Order state machine rules, including time priority on replace.
- Which FIX versions ship first.
- Replication approach (Aeron Cluster or an alternative) and the snapshot interval.
- Deployment target and hardware for benchmarks.
