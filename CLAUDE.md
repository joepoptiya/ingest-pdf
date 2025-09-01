# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Porject Rules (enforced by hooks)

### Workflow Phases

- plan -> confirm -> execute

### Before ANY Edit/Writes

- Output JSON: {"phase":"plan","steps":[...]}
- Wait for explicit approval (approval token minted by `.claude/hooks/approve.sh`)and wait for approval.

### After Writes

- Run quality check (format/lint/tests)
- If checks fail, fix them before continuing

### Agent selection (handoff requied)

- agent-creator -> For identifying gaps in currentt agent capabilities, desigining/refining specialized agents, hooks, or prompts
- python-pro -> For all Python tasks: code creation, test case creation, data science workflows, Pydantic patterns, production-quality enforcement
- uv-pro -> For all python environment setup, UV tasks and commands, executing tests, executing python scripts

**Main actor rules**

- Main MUST NOT call Edit/Write/Bash.
- Main only analyzes, chooses the apprpriate agent and hands off.

### Never

- Touch secrets or environment files
- Run migrations or commits without explicit approval
- Bypass the plan -> confirm -> execture flow
- Nevr use pip/poetry/pyenv/venv; use uv only (enforced by hooks)

