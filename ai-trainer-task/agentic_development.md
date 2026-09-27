`AGENTS.md` is for **repository instruction/context**, while **custom agents**, **skills**, and **personal instructions** are for more targeted behavior shaping. In practice: put always-relevant repo rules in `AGENTS.md` or repo instructions, put reusable specialist behavior in a custom agent, and put task-specific playbooks in skills. ([docs.github.com](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/comparing-cli-features?utm_source=openai))

## The main customization layers

### 1) `AGENTS.md`
Copilot CLI can load repository instruction files from default repo locations including `AGENTS.md` and `.github/copilot-instructions.md`; it can also use a personal instructions file at `~/.copilot/copilot-instructions.md`. GitHub’s guidance is to use these instruction files for broad, always-applicable guidance, and avoid stuffing them with large specialized procedures that would be better as skills or custom agents. ([docs.github.com](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/comparing-cli-features?utm_source=openai))

Good things to put in `AGENTS.md`:
- architecture constraints
- coding conventions
- repo-specific workflow rules
- test commands
- “do/don’t” guidance
- review expectations

Example:

````markdown name=AGENTS.md
# Agent instructions

## Project overview
- This is a Node.js monorepo with apps in `apps/` and shared packages in `packages/`.

## Coding rules
- Prefer TypeScript strict mode.
- Do not introduce default exports in shared packages.
- Reuse existing helpers in `packages/utils` before adding new abstractions.

## Testing
- For API changes, run:
  - `pnpm test`
  - `pnpm lint`
  - `pnpm --filter api test`

## Change policy
- Keep changes minimal and localized.
- Do not rename public API symbols without explicit request.
- If schema files change, update generated types.

## PR expectations
- Summarize risk areas.
- Call out migrations, env var changes, and breaking changes.
````

## 2) Personal instructions
A global instructions file lives at `~/.copilot/copilot-instructions.md` and applies to all sessions, which makes it useful for your personal preferences like “be concise,” “prefer tests first,” or “always explain tradeoffs before destructive commands.” ([docs.github.com](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference?utm_source=openai))

Use this for:
- your preferred communication style
- your default coding philosophy
- general shell safety habits
- preferences that span all repos

## 3) Custom agents
Custom agents are Markdown files with YAML frontmatter, typically stored at:
- user level: `~/.copilot/agents`
- repo level: `.github/agents`
- org level: `/agents` in the org `.github` or `.github-private` repo. ([docs.github.com](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents?utm_source=openai))

They define a named specialist agent with its own instructions, tools, and optional MCP settings. The filename becomes the agent ID, and GitHub docs note deduplication/precedence is based on filename, with lower-level config taking precedence. ([docs.github.com](https://docs.github.com/en/copilot/reference/custom-agents-configuration?utm_source=openai))

Example:

````markdown name=.github/agents/python-reviewer.agent.md
---
description: Reviews Python changes for correctness, tests, and maintainability.
model: claude-sonnet-4.6
tools: ["runTests", "readFiles", "search"]
---

You are a Python code review specialist.

Focus on:
- correctness bugs
- missing edge-case tests
- unsafe async/concurrency behavior
- unnecessary complexity

When reviewing:
1. Start with likely defects.
2. Recommend the smallest safe change.
3. Mention test gaps explicitly.
4. Avoid noisy style-only feedback unless it affects readability or maintainability.
````

You can invoke/select custom agents in Copilot CLI with `/agent`. Copilot CLI also includes built-in agents such as `code-review`, `explore`, `general-purpose`, and `research`. ([docs.github.com](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents?utm_source=openai))

## 4) Skills
Skills are structured reusable playbooks. For Copilot CLI, each skill lives in its own directory with a required `SKILL.md` file, and can live in:
- project: `.github/skills`, `.claude/skills`, or `.agents/skills`
- personal: `~/.copilot/skills` or `~/.agents/skills`. ([docs.github.com](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills?utm_source=openai))

`SKILL.md` uses YAML frontmatter with at least:
- `name` required
- `description` required
- `license` optional. ([docs.github.com](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills?utm_source=openai))

GitHub recommends skills for detailed instructions that should be pulled in only when relevant, instead of always being present like repo instructions. ([docs.github.com](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills?utm_source=openai))

Example:

````markdown name=.github/skills/api-regression-testing/SKILL.md
---
name: api-regression-testing
description: Use when changing API handlers, middleware, serialization, or auth behavior.
---

# API regression testing skill

When working on API changes:
1. Identify all touched routes and middleware.
2. Check request validation, auth, and response shape changes.
3. Add or update integration tests first where possible.
4. Verify error responses and status codes.
5. Call out backward compatibility risks.

## Commands
- `pnpm --filter api test`
- `pnpm --filter api lint`

## Checklist
- [ ] Auth behavior verified
- [ ] Validation behavior verified
- [ ] Error responses verified
- [ ] Contract changes documented
````

## 5) Config directory and settings
Copilot CLI stores local config and customization under `~/.copilot`. GitHub documents top-level items such as:
- `agents/`
- `copilot-instructions.md`
- `extensions/`
- `hooks/`
- `skills/`
- `config.json` and related state. ([docs.github.com](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference?utm_source=openai))

The config docs also mention settings such as additional `skillDirectories`, plus saved permissions and related local state. ([docs.github.com](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference?utm_source=openai))

## 6) Hooks and extensions
Copilot CLI supports:
- **hooks** in `~/.copilot/hooks/` and repo-level `.github/hooks/`
- **extensions** in `~/.copilot/extensions/`. ([docs.github.com](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference?utm_source=openai))

Hooks are useful for shell-side automation or guardrails around tasks; extensions are for broader CLI customization. GitHub also says hooks can be defined inline in `~/.copilot/settings.json` via the `hooks` key. ([docs.github.com](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference?utm_source=openai))

## What to use when

Use this rule of thumb:

- **`AGENTS.md` / `.github/copilot-instructions.md`**: “things Copilot should almost always know in this repo.” ([docs.github.com](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/comparing-cli-features?utm_source=openai))
- **`~/.copilot/copilot-instructions.md`**: “things Copilot should know about me everywhere.” ([docs.github.com](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference?utm_source=openai))
- **custom agent**: “act like a specialist reviewer/implementer for a category of work.” ([docs.github.com](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents?utm_source=openai))
- **skill**: “when task X happens, inject this playbook/checklist/process.” ([docs.github.com](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills?utm_source=openai))
- **hooks/extensions**: “change CLI behavior or automate local workflows.” ([docs.github.com](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference?utm_source=openai))

## A practical setup I’d recommend

For a real repo, start with:

1. `AGENTS.md`
   - architecture notes
   - code conventions
   - test/lint commands
   - safety rules

2. `.github/agents/code-reviewer.agent.md`
   - focused review persona

3. `.github/skills/`
   - `backend-testing`
   - `db-migrations`
   - `release-checklist`

4. `~/.copilot/copilot-instructions.md`
   - your personal preferences like concise output, explain commands before running, prefer small diffs

That gives you:
- stable repo guidance
- reusable specialists
- task-specific playbooks
- global personal defaults

## One important caveat
GitHub’s CLI command reference notes that a custom agent spawned as a **subagent** does **not** automatically receive repository instruction files like `copilot-instructions.md`, `AGENTS.md`, or `CLAUDE.md` by default. So if you rely heavily on repo instructions, test your custom-agent workflow carefully. ([docs.github.com](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference?utm_source=openai))

If you want, I can next give you either:
1. a **copy-paste starter `AGENTS.md`** for a typical app repo, or  
2. a **full example folder structure** for `.github/agents`, `.github/skills`, and `~/.copilot/`.
