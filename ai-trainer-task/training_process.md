# Step-by-Step Walkthrough: Your jiff POSIX TZ Task

Let me walk you through exactly how this task gets built, tested, and submitted using your uploaded files as the example.

## Phase 1: Understand Your File Structure

Based on what you've uploaded, here's what you have and what you still need:

### ✅ Files You Have
```
task.toml              # Metadata (category, language, timeouts)
instruction.md         # Agent-facing prompt (symptom only)
reasoning.md           # Your expert annotation (root cause, why it's hard)
solution/solve.sh      # Oracle script that applies gold_patch.diff
```

### ❌ Files You Still Need to Create
```
environment/
├── Dockerfile         # Builds the agent's container
└── repo/              # Vendored jiff repo (buggy starting state)
solution/
└── gold_patch.diff    # Your verified fix (production code only)
tests/
├── test.sh            # Verifier entrypoint (realm-managed template)
├── config.json        # F2P/P2P test names, test_cmd, log_parser
├── test_patch.diff    # Hidden F2P + P2P tests
└── log_parsers.py     # Parses test output (realm-managed template)
```

## Phase 2: Build the Missing Pieces

### Step 2.1: Vendor the jiff Repo

```bash
# Clone jiff at the base commit from your task.toml
git clone https://github.com/BurntSushi/jiff.git
cd jiff
git checkout 06564abdf4352f89d7e91ccb95f5bbfebff6a404

# Copy into your task directory
cp -r jiff/ ../environment/repo/

# Flatten history (so agent can't read upstream solution)
cd ../environment/repo/
rm -rf .git
git init
git add .
git commit -m "Initial vendored state"
```

### Step 2.2: Create the Gold Patch

Based on your `reasoning.md`, your fix adds a year-rollover collapse to `dst_info_utc`. Generate the diff:

```bash
cd environment/repo/
# Make your fix (the ~14 lines described in reasoning.md)
# ... edit the POSIX TZ module ...

# Generate the patch
git diff > ../../solution/gold_patch.diff
```

Your `gold_patch.diff` should contain ONLY production code changes — no test changes.

### Step 2.3: Write the Hidden Tests

Based on your `reasoning.md`, you need:

**Fail-to-Pass (F2P) tests** — 3 permanent-DST zones:
1. Africa/Casablanca 2087 rule (DST behind standard)
2. East-of-standard variant
3. Behind-standard variant ending at 24:00

**Pass-to-Pass (P2P) tests** — 4 guard rails:
1. Zone starts Jan 1 on DST but falls back later (east-of-standard)
2. Zone starts Jan 1 on DST but falls back later (west-of-standard)
3. Zone starts DST mid-year (July) with year-end wrap
4. Existing neighbouring POSIX test

Create `tests/test_patch.diff`:

```bash
cd environment/repo/
# Add your test files (must have "sequoia" in name)
# e.g., tests/test_sequoia_posix_yearend.rs

git add tests/
git diff --cached > ../../tests/test_patch.diff
```

### Step 2.4: Configure tests/config.json

```json
{
  "fail_to_pass": [
    "test_sequoia_posix_yearend::casablanca_2087_permanent_dst",
    "test_sequoia_posix_yearend::east_of_standard_permanent_dst",
    "test_sequoia_posix_yearend::behind_standard_24h_permanent_dst"
  ],
  "pass_to_pass": [
    "test_sequoia_posix_yearend::jan1_dst_falls_back_east",
    "test_sequoia_posix_yearend::jan1_dst_falls_back_west",
    "test_sequoia_posix_yearend::mid_year_dst_with_wrap",
    "test_sequoia_posix_yearend::existing_posix_test"
  ],
  "test_cmd": "cargo test --test test_sequoia_posix_yearend",
  "log_parser": "parse_log_cargo"
}
```

### Step 2.5: Create environment/Dockerfile

```dockerfile
FROM rust:1.75-slim

# Copy vendored repo
COPY repo/ /app/
WORKDIR /app

# Flatten history
RUN cd /app && \
    rm -rf .git && \
    git init && \
    git add . && \
    git -c user.email="task@sequoia" -c user.name="Task" commit -m "Initial state"
```

## Phase 3: Run the rv Workflow

### Step 3.1: Lint Check

```bash
cd your-task-directory/
rv check
```

**What this does:**
- Validates file structure (all required files present)
- Checks patch hygiene (gold_patch.diff is valid, test_patch.diff applies cleanly)
- Validates repo size/recency
- Runs LLM rubrics on instruction.md (checks for leaks)
- Validates reasoning.md against rubrics

**Expected output:** All checks pass. If anything fails, fix it before proceeding.

### Step 3.2: Verify Oracle (Critical!)

```bash
rv oracle
```

**What this does:**
1. Builds the Docker environment from `environment/Dockerfile`
2. Copies `environment/repo/` into `/app`
3. Applies `solution/gold_patch.diff`
4. Applies `tests/test_patch.diff`
5. Runs `test_cmd` from `tests/config.json`
6. Parses output with `log_parser`
7. Checks that **all F2P tests pass** and **all P2P tests pass**
8. Asserts reward == 1.0

**Expected output:**
```
✓ F2P tests: 3/3 passed
✓ P2P tests: 4/4 passed
✓ Reward: 1.0
```

**If this fails:** Your gold patch is wrong, or your tests are broken. Go back and fix.

### Step 3.3: Test Against Real Agents

```bash
rv run
```

**What this does:**
- Runs the realm's default agent (e.g., Opus, Claude, GPT) against the task
- Agent gets only `instruction.md` + the buggy repo
- Agent tries to fix the bug
- Verifier applies the agent's patch + your hidden tests
- Scores F2P/P2P

**Expected output:**
```
Agent: opus-4.8
F2P: 1/3 passed
P2P: 4/4 passed
Reward: 0.33
```

**This is expected to fail!** Your task should be hard enough that frontier models pass ≤1/5 rollouts.

### Step 3.4: Analyze Trajectories

```bash
rv analyze
```

**What this does:**
- Opens the agent's trial logs
- Shows what the agent tried
- Shows why it failed (or passed)

**What to look for:**
- Did the agent understand the symptom correctly?
- Did it find the right file/function?
- Did it propose a plausible fix?
- If it passed, was it a genuine fix or a lucky guess?

**If the agent passed too easily:** Your tests are too weak or your prompt leaks too much. Strengthen tests or tighten prompt.

**If the agent failed for the wrong reason:** Maybe the bug is too obscure or the prompt is unclear. Adjust instruction.md.

### Step 3.5: Run Multiple Rollouts

Per AGENTS.md, you need to run 5 rollouts each on:
- Opus 4.8
- GPT 5.5
- Gemini 3.5 Flash
- GLM 5.2
- MiniMax M3
- Qwen 3.7 Max

```bash
# Run 5 times per model
for i in {1..5}; do
  rv run --model opus-4.8
  rv run --model gpt-5.5
  # ... etc
done
```

**Label each rollout:**
- True pass: Agent understood and fixed correctly
- False pass: Agent got lucky or tests are weak
- True fail: Agent genuinely couldn't solve it
- False fail: Agent's fix was correct but tests rejected it

**Fix any false verdicts** before proceeding.

### Step 3.6: Final Submission

```bash
rv submit
```

**What this does:**
1. Runs `rv check` (lint + rubrics)
2. Runs `rv oracle` (gold scores 1.0)
3. Runs adversarial probes (over/under-specification checks)
4. Zips everything into `submission.zip`

**Expected output:**
```
✓ All checks passed
✓ Oracle: 1.0
✓ Probes: No issues found
✓ Packaged: submission.zip
```

## Phase 4: What Makes This Task Good

Based on your `reasoning.md`, here's why this task meets the difficulty bar:

### ✅ Non-Trivial Reasoning Required
- Agent must understand POSIX TZ rule semantics
- Must distinguish between "DST all year" vs "DST starts Jan 1 but falls back"
- Must derive the year-rollover test (not obvious)

### ✅ Cause and Symptom Are Separated
- Symptom: wrong offset at year-end
- Cause: missing year-rollover collapse in `dst_info_utc`
- Agent can't just pattern-match; must reason about the data flow

### ✅ Tests Are Behavioural
- Assert exact computed boundaries (not internal state)
- Guard tests pin both halves of the collapse condition
- Naive fixes (offset-direction heuristic, Jan-1-only check) fail guard tests

### ✅ Prompt Doesn't Leak
- States symptom only (wrong offset at year-end)
- Doesn't name the buggy function or the fix
- Doesn't hint at the year-rollover test

## Phase 5: Common Pitfalls to Avoid

### ❌ Don't Do This
```markdown
# Bad instruction.md (leaks the fix)
The bug is in `dst_info_utc` where we need to add a year-rollover check
to collapse permanent-DST zones. The fix is about 14 lines.
```

### ✅ Do This Instead
```markdown
# Good instruction.md (symptom only)
We build time zones from POSIX TZ strings with jiff and look up UTC offsets
from them, and for some zones the offset comes out wrong at the very end of
the year. The zones that go wrong are the ones whose rule keeps them on their
alternate (summer) offset for the entire year...
```

### ❌ Don't Do This
```rust
// Bad test (asserts internal state)
assert_eq!(zone.dst_info_utc.collapse_applied, true);
```

### ✅ Do This Instead
```rust
// Good test (asserts observable behaviour)
let boundary = zone.year_end_boundary();
assert_eq!(boundary, datetime!(2087-12-31 23:59:59));
```

## Summary: Your Action Items

1. **Create missing files:** Dockerfile, repo/, gold_patch.diff, test_patch.diff, config.json
2. **Run `rv check`** → fix any lint/rubric failures
3. **Run `rv oracle`** → must score 1.0
4. **Run `rv run`** (5× per model) → expect ≤1/5 passes
5. **Run `rv analyze`** → label each rollout, fix false verdicts
6. **Run `rv submit`** → package for submission

You're in good shape — your `reasoning.md` shows deep understanding of the bug, and your `instruction.md` doesn't leak the fix. The main work now is building the test harness and verifying the oracle.

Want me to help you draft any of the missing files (Dockerfile, config.json, test_patch.diff)?
