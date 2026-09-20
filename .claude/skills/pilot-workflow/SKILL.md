---
name: pilot-workflow
description: How to run a Python pilot that follows the agreed conventions and starts from template-pilot-ai-python. Use when a repo has GOAL.md, PLAN.md, and src/pilot_kit, or when asked to start, continue, verify, document, or release a pilot from this template. Covers init, requirements questions, the checklist plan (one item is one commit), provider setup (ChatGPT Codex and NVIDIA NIM), three-tier verification with repeated experiments, docs with Mermaid and four languages, code review, and the v0.1.0 release.
---

# Pilot workflow

The repo you are in came from `template-pilot-ai-python`. Follow this order. Read `AGENTS.md` first.

## 1. Init (once)

```bash
python3 scripts/init_pilot.py pilot-<topic> --description "what it studies"
cd src && uv sync && cp ../.env.sample ../.env    # fill in the keys
uv run python doctor.py
```

Commit the result as `🎉 init: set up pilot-<topic>`. Create the GitHub repo with description
`🚀 Pilot project for <topic>` if it does not exist yet.

## 2. Requirements

Read `GOAL.md`. Ask the user only about what the request and the code cannot settle: the product
and its docs URL, the cases to build, the Python version if not 3.13, the extra skills to install.
Never ask about layout, test tools, or doc structure. Follow the template and say so.

- **Read local before fetching.** Sibling repos under `~/repo/jyje/` are already on the machine. Do
  not clone them. If one is missing, fetch single files with `gh api`.
- Keep private analysis in `temp/` (gitignored). Never publish it.
- Install the vendor's own skill with `npx skills add <vendor>/skills --skill <skill> --agent claude-code --copy -y`.

## 3. Plan with a checklist

Edit `PLAN.md`. **One checklist item is one meaningful piece of work and one commit**, with the commit
title after it. Tick an item only after it ran. Add items as work turns up and backfill items for
work done before it had one.

## 4. Build

- Put pilot code in `src/`: shared code in `pilot_kit/`, one folder per case (`case01_<name>/` with
  `graph.py` and `main.py`), tests in `tests/`, notebooks in `notebooks/`.
- Put every call to the vendor behind one gateway class, typed as a `Protocol`, with `ask` and `aask`,
  so tests inject a fake that returns the SDK's real response type.
- Chat models come from `pilot_kit.llm.make_chat_model()`. Never hard-code a provider in a case.
- Retry the chat model call only, never a whole graph or agent run (a replay calls the vendor again).
- Follow the `python-lint` skill before calling any Python change done.

## 5. Verify in three tiers

1. Unit: `pytest` offline with fakes.
2. Scripts: `doctor.py` and each case's `main.py` against live services.
3. Notebooks: executed, outputs kept. **Repeat each experiment** (10 runs for cheap vendor calls with
   `asyncio.gather`, 3 to 5 for slow chat-model runs), add a hand-written scenario sweep with expected
   outcomes, and print Markdown tables with agreement counts and mean (min to max).

Run slow work in the background (`nohup` scripts, one at a time: hosted NIM slows under concurrent
load). Say plainly what was not verified.

## 6. Docs

README short and visual: goal, the cases with diagrams and results, quick start, links. Detail goes in
`docs/`. Use Mermaid for structure and sequences, and render every block with
`npx -y -p @mermaid-js/mermaid-cli mmdc` before publishing. Languages, always in this order: English,
Korean, Japanese, Simplified Chinese. Translate in the main session, editing only the changed
sections. Do not spawn subagents for translation: each one re-reads sources and rewrites files, which
is costly. Use a subagent only when a genuinely clean context is needed, such as an independent code
review.

## 7. Secrets

Keys live in the repo-root `.env` (gitignored); `.env.sample` holds format only. Never print, log, or
commit a key; check `.env` by variable name with values masked. On macOS, keep keys in the keychain
(service = key type, account = project) and add a new item per project; do not overwrite another
project's item. Never read or copy `~/.codex/auth.json`.

## 8. Commits and release

- Commits follow `git-commit-helper`. Propose the messages and **wait for approval** before committing
  or pushing. Never add session IDs, session URLs, or co-author trailers.
- When every `PLAN.md` box is ticked: run a code review, apply the valid findings, then delete
  `PLAN.md` (history keeps it), remove its links, commit `🚀 release: v0.1.0`, tag `v0.1.0`, push, and
  create the GitHub release. The `release.yml` workflow does the last step for tags.
- Add the finished pilot to the `jyje/awesome-pilots` index.
