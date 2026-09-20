# Plan

This file is the single source of truth for scope and progress. **When every box below is checked,
v0.1.0 is ready to publish.** Delete this file at release; git history keeps it.

## Goal

<!-- One paragraph, taken from GOAL.md. -->

## How to use this checklist

- One checklist item is one meaningful piece of work and **one commit**. The commit title is in
  backticks after each item.
- Tick an item only after the work has run and been verified.
- New work that turns up gets a new item. Work finished before it had an item is added afterwards.
- Commits and pushes happen only after explicit approval, following
  `.claude/skills/git-commit-helper/SKILL.md`. Never add session IDs, session URLs, or co-author
  trailers.

## Decisions

| Topic | Decision |
| --- | --- |
| Python | 3.13 |
| Inference layer | One factory, `LLM_PROVIDER=openai` (1) or `nim` (2). Unset picks the first configured |
| Layout | Flat uv app in `src/`, shared code in `src/pilot_kit/`, one folder per case |
| Docs | README short and visual, detail in `docs/` with Mermaid. English, Korean, Japanese, Simplified Chinese, in that order |
| Secrets | Repo-root `.env`, `.env.sample` holds format only |

## Verification strategy

| Tier | What | Needs keys |
| --- | --- | --- |
| 1. Unit | `pytest` with fakes | no |
| 2. Script | `doctor.py` and each case's `main.py` | yes |
| 3. Notebook | executed end to end, experiments repeated, results as tables | yes |

## Checklist

### Foundation

- [x] Template: license, `.gitignore`, skills, `.agents` link, uv app, providers, CI &mdash; from `template-pilot-ai-python`
- [ ] Repository basics for this pilot (`init_pilot.py`, `.env`, vendor skill installed) &mdash; `🎉 init: set up <repo>`

### Core library

- [ ] Gateway to the vendor's API (sync and async, typed as a `Protocol`) &mdash; `✨ feat(<vendor>): add the gateway`
- [ ] The pilot's policy in plain code &mdash; `✨ feat(policy): ...`

### Cases

- [ ] Case 01, with tests &mdash; `✨ feat(<case>): ...`
- [ ] Case 02, with tests &mdash; `✨ feat(<case>): ...`
- [ ] `doctor.py` checks the vendor's API &mdash; `✨ feat(doctor): ...`

### Verification evidence

- [ ] Notebooks executed, experiments repeated, results tabulated &mdash; `✅ test(notebooks): ...`
- [ ] Live check on both providers (ChatGPT, NVIDIA NIM) &mdash; no commit

### Quality gate

- [ ] `python-lint` steps clean (ruff, ty, pytest)
- [ ] Code review by a read-only subagent, valid findings applied

### Documentation

- [ ] English README and `docs/` with Mermaid diagrams &mdash; `📄 docs(en): ...`
- [ ] Korean &mdash; `📄 docs(ko): ...`
- [ ] Japanese &mdash; `📄 docs(ja): ...`
- [ ] Simplified Chinese &mdash; `📄 docs(zh-cn): ...`
- [ ] Agent context (`AGENTS.md`) matches the repo &mdash; `📄 docs(agents): ...`

### Release gate (checks, no commit)

- [ ] `ruff check`, `ruff format --check`, `ty check`, `pytest` green
- [ ] Every Mermaid block renders
- [ ] Every relative Markdown link resolves in all languages
- [ ] No secret values in any file that would be committed

### Publish

- [ ] Commits created one by one from this checklist, after approval
- [ ] Delete `PLAN.md`, remove its links, commit `🚀 release: v0.1.0`
- [ ] Tag `v0.1.0`, push, create the GitHub release
- [ ] Add the pilot to the `jyje/awesome-pilots` index
