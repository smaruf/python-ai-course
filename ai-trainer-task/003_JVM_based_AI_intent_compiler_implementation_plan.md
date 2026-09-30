# Implementation Plan

## Guiding principles

1. **Build deterministic first, add AI last.** Phases 1-3 have no LLM. If the language isn't useful without AI, AI won't rescue it.
2. **The interpreter is the oracle.** Every later stage (JVM backend, optimizations, AI-produced IR) is tested against it.
3. **AI only interprets.** Intent → Logic IR lowering is deterministic rules for the first slice. LLM synthesis of implementations is deferred.
4. **The accepted IR is committed like a lockfile.** Builds never call a model.

## Scope decision (Phase 0, ~1 week)

Pick one domain: **application/business logic over entities with effects** (find, filter, iterate, send, transfer). Drop streaming and latency SLOs for now. Deliverables:

- A one-page semantics document covering evaluation order, rule conflicts, null handling (options only, no nulls), and time.
- A **corpus of 30-50 intents** with hand-written expected specs, including deliberately ambiguous ones ("recently", "applicable tax"). This corpus becomes the evaluation set.
- Success metrics, defined now so you can't rationalize later (see Phase 8).

## Phase 1: Core language, Logic IR, reference interpreter (~5-6 weeks)

- **Implementation language:** Java 21+ (sealed interfaces, records, and pattern matching suit IR work).
- **Parser:** I'd use ANTLR or a hand-written recursive-descent parser rather than Yacc. You need lexer modes so natural-language blocks under `goal:` are captured as opaque text, and Yacc makes that awkward.
- **Logic IR:** typed, immutable, and small: entities, expressions, predicates, `forEach`, `find`, `effect` calls, and contracts as annotations.
- **Effect system:** every operation declares its effects (`pure`, `db.read`, `db.write`, `email.send`). Effects are part of the type, so the compiler always knows what a program can touch.
- **Interpreter:** executes Logic IR against in-memory entity stores and mock effect handlers. This is the reference semantics.

**Exit criterion:** the corpus's exact-syntax programs run correctly in the interpreter.

## Phase 2: JVM backend (~4-5 weeks)

- Use **ASM** (mature) or the JDK Class-File API (check which version you target).
- Emit one class per flow. Effects become calls into a small **runtime library** behind interfaces (`EmailPort`, `Repository<T>`), which are your FFI nodes.
- Emit `LineNumberTable` and source maps pointing to *intent/IR node IDs*, not Java lines. This is what makes the "abstracted error reporting" idea possible later.
- **Differential testing:** generate random inputs and assert that the interpreter and compiled bytecode agree. Run ASM's `CheckClassAdapter` on all output.
- Don't inject GC hints. Emit clean bytecode and let the JIT work.

**Exit criterion:** 100% agreement between interpreter and JVM on the corpus plus a fuzzed input set.

## Phase 3: Intent IR and the semantic engine (~4 weeks)

- Define Intent IR as sealed types: `Goal`, `Entity`, `Predicate`, `Preconditions`, `Postconditions`, `Invariants`, `Constraints`, `Effects`. Generate the **JSON Schema** from these types so the two can't drift.
- **Entity catalog:** entities, fields, and available operations, declared in the language. This is the context the AI sees and the reference the validator checks against.
- **Glossary (a key piece):** project-level definitions such as `recently = 30.days` or `inactive = lastLogin < now - recently`. Vocabulary is defined once by humans, so the AI resolves terms rather than inventing thresholds. This directly addresses type-correct but semantically wrong interpretations.
- **Validator:** resolve names, type-check predicates, check that the effects the intent needs are permitted, and reject unknown fields with helpful messages.
- **Deterministic lowering:** Intent IR → Logic IR through explicit rewrite rules. Hand-write Intent IR for the corpus first and confirm end-to-end compilation works before any model is involved.

**Exit criterion:** hand-authored Intent IR for the whole corpus compiles and passes differential tests.

## Phase 4: AI interpretation layer (~4 weeks)

- **Input to the model:** entity catalog, glossary, allowed operations, the Intent IR schema, and the intent text.
- **Output:** schema-constrained structured output (JSON Schema or grammar-constrained decoding), never free text.
- **Ambiguity as a first-class result:** the schema includes a `needs_clarification` variant with structured questions ("'recently' isn't in the glossary; define it?"). Reward asking over guessing.
- **Provider abstraction:** one `Interpreter` interface so the model is swappable. Record model ID, prompt hash, and schema version with every result.
- **Repair loop:** on validation failure, feed the structured errors back for up to N retries, then fail loudly.

**Exit criterion:** measured interpretation accuracy on the corpus, with results per ambiguity category.

## Phase 5: Confirmation UX and the lockfile (~3 weeks)

- **Example-based confirmation:** instead of a prose restatement, generate concrete cases from fixtures: "These 3 users would be notified: … These 2 would not: … because …". The examples come from running the interpreter on the candidate IR, so they show what the interpretation *does*.
- **Lockfile:** `notify_users.intent.lock` stores the accepted Intent IR, a hash of the source text, the glossary version, and the model and prompt provenance.
- **Toolchain rules:**
  - `flowc build` uses only the lock and never calls a model.
  - If the text hash differs from the lock, the build fails with a "re-interpret and re-accept" message.
  - If the glossary changes, dependent locks are flagged as stale.
- Show a diff of the *IR* on re-interpretation, not of the text.

## Phase 6: Verification (~5-6 weeks, overlaps with Phase 5)

Layer these from cheapest to hardest:

1. **Property tests generated from contracts** (jqwik or similar). "One email per user" becomes a generated test over random inputs against the interpreter and the bytecode.
2. **SMT checking** (Z3) for the pure fragment: pre/postconditions on arithmetic and predicates, such as `transfer` preserving the total balance.
3. **Bounded model checking** for effect ordering and concurrency, only if the first two prove insufficient.

Be clear about which checks run at compile time and which are enforced by the runtime. Constraints like `atomic`, `exactly_once`, and `one_email_per_user` need **runtime machinery**: idempotency keys, transactional ports, and dedupe stores in the runtime library. The IR must define their exact semantics, and the backend must implement them. Constraints the backend can't enforce should be a compile error, not a comment.

## Phase 7: Tooling and observability (~4 weeks)

- CLI: `flowc interpret | check | build | explain`
- **`explain`:** shows the chain from source text → accepted IR → lowered Logic IR → bytecode.
- Runtime failures reported in intent terms ("constraint `do_not_send_to_unsubscribed` blocked 12 sends") using the source maps from Phase 2.
- An LSP server for diagnostics, with inline lock-drift warnings.

## Phase 8: Evaluation (ongoing, formal pass ~3 weeks)

This phase tests whether the approach is actually better than the alternative. Measure:

| Question | Metric |
|---|---|
| Does the AI interpret correctly? | Accuracy on the corpus, split by ambiguity level |
| Does it know what it doesn't know? | Clarification rate on ambiguous vs. clear intents |
| Do humans catch wrong interpretations? | Seed subtly wrong IRs into the confirmation screen and measure catch rate for example-based vs. prose confirmation |
| Is it deterministic where promised? | Identical builds from identical locks, across machines |
| Is the backend correct? | Interpreter/JVM disagreement rate under fuzzing |
| **Is it better than the baseline?** | Same corpus given to "LLM writes Java + tests": compare defect rate and review effort |

The last row is the whole thesis. If the formal-artifact route doesn't beat the baseline on defects or review effort, that's crucial to know early.

## Later

- Second backend (WASM) to validate the target-agnostic IR.
- LLM-assisted *synthesis* for intents the deterministic rules can't lower, gated by the Phase 6 verifiers.
- AI optimization suggestions as an optional pass, accepted only after checking equivalence against the interpreter.
- Streaming and latency-bound dataflow, as a separate product decision.

## Suggested repo layout

```
flow/
├── spec/            # semantics doc, corpus, glossary format
├── syntax/          # lexer, parser
├── ir/              # intent/, logic/, effects/
├── semantic/        # resolver, type checker, validator
├── lowering/        # Intent IR → Logic IR rules
├── interp/          # reference interpreter
├── backend-jvm/     # ASM emitter, source maps
├── runtime/         # effect ports, idempotency, transactions
├── ai/              # Interpreter interface, prompts, schema, repair loop
├── verify/          # property tests, SMT encoders
├── lock/            # lockfile format, drift detection
├── cli/ + lsp/
└── eval/            # corpus runner, baselines, metrics
```

## Timeline and risks

Roughly **6-8 months for one or two strong engineers** to reach an evaluated MVP, with Phases 1-3 (about 3 months) usable with no AI at all.

| Risk | Mitigation |
|---|---|
| Users rubber-stamp confirmations | Example-based screens, seeded-error testing, and a glossary that shrinks the interpretation space |
| Constraint semantics get hand-wavy | Require a runtime enforcement path for every constraint, or reject it |
| Scope creep into streaming/GPU | Keep those out until the CRUD slice passes evaluation |
| Model updates change behavior | Pinned provenance in the lock and no model calls in builds |
| Interpretation and synthesis blur | Keep lowering deterministic until the verifiers exist |

I can also put this into a document you can keep, or expand any phase, for example the Intent IR schema and glossary format from Phase 3.
