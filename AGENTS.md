# AGENTS.md

Context for AI coding agents (Claude Code, Codex, Hermes, Copilot). This repo came from the
`template-pilot-ai-python` template. Scope and progress live in [`PLAN.md`](PLAN.md); the intent lives in
[`GOAL.md`](GOAL.md). Read the `pilot-workflow` skill before you start.

## Purpose

<!-- One paragraph: what this pilot studies and why. -->

## Structure

```
.claude/skills/            skills (real files); .agents is a symlink to .claude
  pilot-workflow/          how to run a pilot from this template, read it first
  python-lint/             ruff, ty, pytest before any Python change is done
  git-commit-helper/       commit message policy
  centered-readme/         README hero block style
docs/                      guides with Mermaid diagrams
temp/                      gitignored private notes, never publish or commit
scripts/init_pilot.py      renames the template into a pilot, then delete it
src/                       uv app, Python 3.13
  pilot_kit/               shared code: env, llm factory, retry, text, chatgpt_login, chatgpt_models
  case01_hello/            example graph, replace it with the pilot's cases
  notebooks/               executed verification notebooks
  tests/                   offline pytest suite
  doctor.py                environment and connectivity diagnostics
  langgraph.json           graphs for `langgraph dev`
```

## Commands (run in `src/`)

```bash
uv sync                                  # add --extra deepagents --extra notebook --extra studio as needed
uv run python doctor.py                  # env, chat model
uv run pytest                            # offline unit tests
uv run ruff check --fix . && uv run ruff format . && uv run ty check .   # python-lint skill
uv run python -m case01_hello.main
uv run python -m pilot_kit.chatgpt_login # once, for the ChatGPT provider
uv run langgraph dev                     # needs --extra studio
```

## Environment (`.env` at the repo root, template in `.env.sample`)

| Variable | Required | Notes |
| --- | --- | --- |
| `LLM_PROVIDER` | no | (1) `openai` ChatGPT subscription, (2) `nim` NVIDIA NIM. Unset picks the first configured |
| `LLM_MODEL` | no | defaults: `gpt-5.5` (openai), `nvidia/nemotron-3.5-lightning-30b-a3b` (nim) |
| `LLM_TIMEOUT` | no | seconds, default 180. Hosted NIM calls can take over a minute |
| `LLM_ENABLE_THINKING` | no | `false` sends `enable_thinking: false` to NIM reasoning models |
| `NVIDIA_API_KEY` | nim | https://build.nvidia.com |
| `NVIDIA_BASE_URL` | no | self-hosted NIM |

## Conventions

- Source code, comments, `AGENTS.md`, `PLAN.md`, and `docs/` are English. The README and each `docs/`
  page have translated twins, always in this order: English (default), Korean (`-ko`), Japanese
  (`-ja`), Simplified Chinese (`-zh-CN`). Edit English first, then the twins, in the main session.
- Keep the README short and visual. Put detail and Mermaid diagrams in `docs/`.
- Code and tests must pass `ruff check --fix`, `ruff format`, `ty check`, and `pytest`. Suppress a
  finding only with the exact rule and a reason.
- Reach the vendor only through a gateway class typed as a `Protocol`, so tests can swap in a fake.
- Retry the chat model call only, never a whole graph or agent run (a replay calls the vendor again).
- Model names are account specific. Find them with `python -m pilot_kit.chatgpt_models`, and keep
  account-specific names out of public docs. A model listed in the NIM catalog can still return
  `410 Gone`: call it before relying on it.
- The `openai` provider uses ChatGPT OAuth, never `OPENAI_API_KEY`. It is experimental and unofficial,
  so keep the terms warning. Never read or copy `~/.codex/auth.json`.
- The `.env` file is gitignored. Never print, log, or commit key values.
- Sibling repos under `~/repo/jyje` are already on the machine: read them there, never clone them.
- Simple, long-running work goes to the background. Do multilingual work in the main session. Use
  subagents only for a genuinely clean context, such as an independent code review.
- Commits follow `.claude/skills/git-commit-helper/SKILL.md`. One `PLAN.md` item is one commit. Never
  commit or push without explicit approval, and never put session IDs, session URLs, or co-author
  trailers in a commit.
