@AGENTS.md

## Claude Code notes

- Use the `pilot-workflow` skill when starting, continuing, or releasing the pilot.
- Use the vendor's own skill (installed under `.claude/skills/`) before writing code that calls it.
- Use the `python-lint` skill before calling any Python change done.
- Use the `git-commit-helper` skill before proposing or creating a commit, and wait for approval.
- Keep private analysis in `temp/`. It is gitignored and must not leak into commits or public docs.
