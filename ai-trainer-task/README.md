Absolutely. Based specifically on the uploaded `rv` document, here is a **personal working guideline for you as a Realm SWE task author/reviewer**. I’m keeping the terminology and rules from the document rather than adding undocumented requirements. 

# Realm SWE — Personal Working Guideline

## 1. Objective

Your goal is to produce **high-quality, solvable Harbor/SWE tasks with minimal rework**.

Use `rv` throughout the lifecycle rather than waiting until the end.

The core principle is:

> **Don't consider a task finished just because the reference solution works.**

You need to establish that:

1. the task is well specified,
2. the reference solution works,
3. the verifier correctly evaluates the outcome,
4. a real agent can interact with the task,
5. the tests are not under- or over-specified,
6. there is no problematic leakage,
7. the final submission passes the required checks. 

---

# 2. Environment Setup

## Required tools

You should have:

* Docker Desktop
* `uv`
* OpenCode
* Google Cloud CLI
* `rv` / `realm-verifier`

Check the basic environment:

```bash
docker --version
docker compose version
python3 --version
```

The document notes that alternatives such as Colima or Rancher should also work instead of Docker Desktop. 

---

# 3. Authenticate Before Installing `rv`

Use your Micro1 account:

```bash
gcloud auth login
gcloud auth application-default login
```

Configure private registry authentication:

```bash
uv tool install keyring --with keyrings.google-artifactregistry-auth
```

Install/update `rv`:

```bash
uv tool install --upgrade --keyring-provider subprocess \
  --index https://oauth2accesstoken@us-central1-python.pkg.dev/m1-rl-envs/rv-coding/simple/ \
  realm-verifier --python 3.14
```

Then:

```bash
rv health
rv auth
```

`rv auth` is a **one-time credential provisioning step**. 

### Windows

If PowerShell gives problems with `rv`, the document recommends trying Command Prompt; you may also need to use:

```text
rv.exe
```



---

# 4. Before Starting a Task

Run:

```bash
rv health
```

You want the environment to be ready before spending time on the task.

Then create the task from the appropriate Realm template:

```bash
rv init <task_name>
cd <task_name>
```

`rv init` interactively selects/scaffolds a Realm template. 

---

# 5. Your Main Task Lifecycle

Use this as your **standard workflow**:

```text
                 TASK IDEA
                    │
                    ▼
              rv init <name>
                    │
                    ▼
              BUILD THE TASK
                    │
                    ▼
                rv check
                    │
                    ▼
               rv oracle
                    │
                    ▼
                 rv run
                    │
                    ▼
               rv analyze
                    │
                    ▼
             REVIEW PROBES
                    │
                    ▼
             FIX / REVISE TASK
                    │
                    ▼
              rv check AGAIN
                    │
                    ▼
               rv submit
```

The most important point is that **`rv run` and `rv analyze` remain your responsibility even though `rv submit` performs its own validation pipeline**. 

---

# 6. `rv check` — Your First Quality Gate

Run:

```bash
rv check
```

It performs:

* deterministic lint checks
* LLM-judged quality rubrics

The documented rubrics include:

* **verifiable**
* **well-specified**
* **solvable**
* **outcome-verified**



### Guideline

Do not immediately treat a failed check as something to bypass.

Instead:

```text
CHECK FAILURE
     ↓
Understand why
     ↓
Fix task/spec/tests
     ↓
Run check again
```

The purpose of `rv` is specifically to reduce rework and improve quality. 

---

# 7. `rv oracle` — Prove the Task Is Solvable

Run:

```bash
rv oracle
```

This runs the task's `solve.sh` reference solution through the verifier.

Its purpose is:

> **Prove that the task is actually solvable.**



### Your rule

Never assume:

> "I wrote the solution, therefore the task is solvable."

Instead prove it through the Oracle.

---

# 8. `rv run` — Test a Real Agent

Run:

```bash
rv run
```

This evaluates a real LLM agent such as OpenCode or Claude Code against your task. 

This is fundamentally different from `rv oracle`.

### Think of it as:

```text
Oracle
  =
Can the intended/reference solution solve it?

Agent
  =
Can a real coding agent solve it?
```

You need both.

---

# 9. `rv analyze` — Inspect the Agent's Thinking/Trajectory

After the agent run:

```bash
rv analyze
```

Use it to inspect the trial trajectories.

The goal is not merely:

> PASS / FAIL

Instead, understand **how the agent approached the task**.

Look for:

* unexpected interpretation
* confusion caused by specification
* incorrect assumptions
* test exploitation
* legitimate alternative implementation
* environmental leakage
* other evidence that the task isn't behaving as intended

The document explicitly says that `rv submit` **does not run a real agent evaluation or analyze a trajectory**, so this remains your responsibility. 

---

# 10. Probe the Quality of Your Hidden Tests

For SWE realms, probes are integrated into `rv check`.

Therefore, don't expect to use:

```bash
rv probe
```

as a separate command.

Instead:

```bash
rv check --stage probes
```

when you want to run only the probe stage. 

There are four probe categories.

---

## 10.1 Gameability

### Question

> Can an agent pass the hidden tests without actually solving the task?

This detects **under-specified tests**.

Example conceptually:

```text
Task:
"Implement feature X correctly."

Tests:
Only check that file X exists.

Agent:
Creates empty file X.

Tests:
PASS
```

That's a gameability problem.

Your tests need to verify the **actual requested behavior**, not merely superficial characteristics.

---

# 11. Altsolve

### Question

> Can an agent produce a valid alternative solution that the tests incorrectly reject?

This detects **over-specified tests**. 

Think:

```text
Requirement
    ↓
Many valid implementations
    ↓
Tests should accept valid implementations
```

Don't accidentally encode:

```text
Requirement
    ↓
Only MY implementation
    ↓
Everything else fails
```

unless the task genuinely requires that specific behavior.

---

# 12. Alignment

### Question

> Do the tests actually grade what the instruction asks for?

This is one of the most important checks.

You should compare:

```text
TASK INSTRUCTION
       ↓
EXPECTED BEHAVIOR
       ↓
VERIFIER / TESTS
```

All three should correspond.

If the task asks for:

> behavior A

but tests primarily verify:

> behavior B

you have an alignment problem.

---

# 13. Leakage

### Question

> Can the agent find the answer somewhere in the environment?

This tests whether the intended challenge has accidentally been compromised by environmental information. 

When reviewing leakage findings, don't automatically assume the tool is correct.

The documentation explicitly says probe findings are **LLM-assisted** and you should open the linked Harbor job and inspect the agent's diff before deciding what to do. 

---

# 14. Probe Finding ≠ Automatic Failure

This is important.

Probe findings are:

* non-blocking
* informational
* LLM-assisted

A finding does **not automatically mean you must reject the task**.

Your procedure should be:

```text
Probe finding
     ↓
Open Harbor job
     ↓
Read agent diff
     ↓
Understand the finding
     ↓
Decide whether it is legitimate
     ↓
Fix if necessary
     ↓
Re-run validation
```



---

# 15. `rv check` vs `rv submit`

This distinction should be memorized.

### `rv check`

Runs:

```text
Deterministic lint
+
LLM quality rubrics
```

### `rv submit`

On a SWE Realm, runs:

```text
Deterministic lint
+
LLM quality rubrics
+
Oracle × 3
+
Probes
```

The Oracle is run three times to catch flaky behavior.

Results can be cached, so after a green `check`, submitting can replay checks without unnecessary additional work. 

### But:

`rv submit` does **NOT**:

```text
❌ run a real agent evaluation
❌ analyze an agent trajectory
```

Therefore your pre-submit workflow remains:

```bash
rv check
rv oracle
rv run
rv analyze
rv submit
```



---

# 16. Recommended "Definition of Done"

I would use this as your personal definition of a completed task:

```text
TASK IS NOT DONE UNTIL:

[ ] Task is correctly scaffolded
[ ] Specification is clear
[ ] Tests/verifier reflect the specification
[ ] Reference solution exists
[ ] rv check passes
[ ] rv oracle succeeds
[ ] Real agent has been evaluated
[ ] Agent trajectory has been analyzed
[ ] Gameability checked
[ ] Altsolve checked
[ ] Alignment checked
[ ] Leakage checked
[ ] Any legitimate findings addressed
[ ] Final rv check passes
[ ] rv submit succeeds
```

The last three items are particularly important: **don't confuse "submission succeeded" with "I properly evaluated the task."**

---

# 17. Useful `rv` Commands Cheat Sheet

```bash
# Environment
rv health
rv auth
rv update

# Task creation
rv init <task_name>

# Quality
rv check

# Reference solution
rv oracle

# Real agent
rv run

# Analyze agent
rv analyze

# Probe tests
rv check --stage probes

# Interactive trajectory viewer
rv view

# Enter task container
rv shell

# Final submission
rv submit
```



---

# 18. Troubleshooting

### `gcloud` authentication problem

Don't repeatedly experiment with credentials.

Contact a:

* HDM
* HDL
* SPL

The document explicitly recommends this for `gcloud` authentication issues. 

### `rv` not working

First:

```bash
rv health
```

### `rv` version/problem after project changes

Try:

```bash
rv update
```

### Windows

If `rv` behaves strangely in PowerShell:

```text
Try Command Prompt
```

and potentially:

```text
rv.exe
```



---

# 19. The Mental Model I Recommend You Use

When authoring, think about your task from **four perspectives**:

```text
┌──────────────────────────────┐
│ 1. HUMAN                     │
│ Is the requirement clear?    │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 2. REFERENCE SOLUTION        │
│ Is it actually solvable?     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 3. REAL AGENT                │
│ Can an agent solve it?       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 4. ADVERSARIAL AGENT         │
│ Can it exploit the tests?    │
│ Can valid solutions fail?    │
│ Can it exploit leakage?      │
└──────────────────────────────┘
```

That is the most useful way to internalize the `rv` documentation.

## Your golden rule

> **Author → Check → Prove → Agent-test → Analyze → Adversarially test → Fix → Submit.**

And specifically, **never skip `rv run` + `rv analyze` just because `rv check` is green or `rv submit` succeeds**. The uploaded document explicitly distinguishes those responsibilities. 
