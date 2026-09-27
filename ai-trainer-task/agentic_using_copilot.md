Use **GitHub Copilot CLI** by installing it, launching `copilot` inside your repo, and then driving work with slash commands like **`/plan`** plus normal-language prompts. Copilot CLI is GitHub’s terminal-native coding agent and supports planning, code changes, GitHub context, custom agents, and an optional autopilot mode. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))

## Quick start

### 1) Install
Common install options include:

```bash
# npm
npm install -g @github/copilot

# Homebrew
brew install copilot-cli

# Windows
winget install GitHub.Copilot
```

GitHub also publishes an install script for macOS/Linux. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))

### 2) Launch
From your project directory:

```bash
copilot
```

If you are not authenticated yet, use the `/login` flow in the CLI, or authenticate with a PAT that has **Copilot Requests** permission. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))

## What “agentic dev” looks like

A typical workflow is:

### A. Ask for a plan first
```text
/plan
Add JWT auth to this Express API with refresh tokens and route protection.
```

Copilot CLI has a dedicated **plan mode** for building a structured implementation plan before making changes. ([docs.github.com](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli?utm_source=openai))

### B. Let it implement iteratively
After the plan, continue with something like:

```text
Implement step 1.
```

or

```text
Apply the full plan, but show me each change before executing.
```

The CLI is designed to build, edit, debug, and refactor code while keeping you in control of execution. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))

### C. Use autopilot when you want it to keep going
You can enable experimental features and use **autopilot** so the agent keeps working until it decides the task is complete:

```bash
copilot --experimental
```

Then in the CLI, switch modes or use the CLI options documented for autopilot. The command reference describes `--autopilot` as continuation mode where the agent keeps working until task completion. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))

## Useful commands/features

- **`/plan`**: create an implementation plan. ([github.com](https://github.com/features/copilot/cli?utm_source=openai))
- **`/model`**: switch models. The docs note multiple model options are available. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))
- **`/agent`**: shape behavior with custom agents. ([github.com](https://github.com/features/copilot/cli?utm_source=openai))
- **`/skills`**: use skills/instructions to guide specialized work. ([github.com](https://github.com/features/copilot/cli?utm_source=openai))
- **`/lsp`**: inspect Language Server Protocol setup/status if configured. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))
- **`/experimental`**: enable experimental features. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))

## Best-practice workflow

A good pattern is:

1. Open your repo in terminal.
2. Start `copilot`.
3. Run `/plan`.
4. Give a specific task.
5. Review the plan.
6. Ask it to implement one step at a time, or all steps with confirmation.
7. Run your tests/build yourself and feed failures back into the agent.
8. Ask it to refine, refactor, or write docs/tests afterward.

This works especially well because Copilot CLI is built for natural-language interaction with local code plus GitHub context. ([github.com](https://github.com/github/copilot-cli?locale=en-US&utm_source=openai))

## Example prompts

Try prompts like:

```text
/plan
Trace the login flow in this repo and propose the smallest safe fix for session expiry.
```

```text
Find why the tests in auth are flaky and suggest a minimal patch.
```

```text
Refactor this module to separate validation from persistence, then add unit tests.
```

```text
Review the current branch changes and summarize risks before I open a PR.
```

## Team/project customization

Copilot CLI supports:
- **custom agents**
- **shared repo-level config**
- **AGENTS.md / agent instructions**
- **LSP integration** for richer code intelligence

These features help standardize behavior across sessions and repos. ([github.com](https://github.com/features/copilot/cli?utm_source=openai))

## Important note for CI/GitHub Actions

If you mean “agentic dev in automation,” GitHub Docs recommend using **GitHub Agentic Workflows** instead of invoking Copilot CLI directly in `run` steps, due to security and governance concerns. ([docs.github.com](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/copilot-cli-in-github-actions?utm_source=openai))

If you want, I can give you:
1. a **minimal install + first-session tutorial**, or  
2. a **real example workflow for your stack** like Node, Python, or Go.
