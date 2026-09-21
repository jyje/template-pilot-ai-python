#!/usr/bin/env python3
"""Turn this template into a pilot repository. Standard library only.

Usage:
    python3 scripts/init_pilot.py pilot-topic --description "what it studies"
    python3 scripts/init_pilot.py pilot-topic --description "..." --owner someone --dry-run

What it does:
- renames `template-pilot-ai-python` to the new repository name everywhere (text files, uv.lock);
- sets the package description and the README tagline in all languages;
- drops the "Use this template" blocks from the READMEs;
- deletes itself and its own test (src/tests/test_init_pilot.py), unless --keep-script is given.

It does not touch git. Commit the result yourself: `🎉 init: set up pilot-topic`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TEMPLATE_NAME = "template-pilot-ai-python"
TEMPLATE_OWNER = "jyje"
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "temp", "node_modules"}
TAGLINE = re.compile(r"(<!-- pilot:tagline -->).*?(<!-- /pilot:tagline -->)", re.S)
TEMPLATE_BLOCK = re.compile(r"<!-- template:begin -->.*?<!-- template:end -->\n*", re.S)
TEMPLATE_ONLY_FILES = ("scripts/init_pilot.py", "src/tests/test_init_pilot.py")
NAME_RE = re.compile(r"^pilot-[a-z0-9]+(-[a-z0-9]+)*$")
REMOTE_OWNER = re.compile(r"github\.com[:/]([^/\s]+)/[^/\s]+?(?:\.git)?/?$")


def detect_owner(root: Path) -> str:
    """Owner of the `origin` remote, so a repo made from the template keeps its own owner."""
    try:
        url = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return TEMPLATE_OWNER
    match = REMOTE_OWNER.search(url)
    return match.group(1) if match else TEMPLATE_OWNER


def text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        yield path


def transform(text: str, path: Path, name: str, owner: str, description: str) -> str:
    text = text.replace(f"{TEMPLATE_OWNER}/{TEMPLATE_NAME}", f"{owner}/{name}")
    text = text.replace(TEMPLATE_NAME, name)
    # The tagline sits between the markers as its own paragraph, so GitHub renders it under the logo.
    text = TAGLINE.sub(lambda m: f"{m.group(1)}\n\n🚀 Pilot project for {description}\n\n{m.group(2)}", text)
    text = TEMPLATE_BLOCK.sub("", text)
    if path.name == "pyproject.toml":
        description_value = json.dumps(description, ensure_ascii=False)
        text = re.sub(
            r'^description = ".*"$', lambda _: f"description = {description_value}", text, flags=re.M
        )
    return text


def main(argv: list[str], root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description="Turn this template into a pilot repository.")
    parser.add_argument("name", help="new repository name, for example pilot-my-topic")
    parser.add_argument("--description", required=True, help="one sentence: what the pilot studies")
    parser.add_argument("--owner", help="GitHub owner (default: owner of the origin remote)")
    parser.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    parser.add_argument("--keep-script", action="store_true", help="do not delete this script")
    args = parser.parse_args(argv)

    if not NAME_RE.match(args.name):
        parser.error("name must look like pilot-some-topic (lowercase letters, digits, hyphens)")
    root = root or Path(__file__).resolve().parent.parent
    owner = args.owner or detect_owner(root)

    changed = 0
    for path in text_files(root):
        old = path.read_text(encoding="utf-8")
        new = transform(old, path, args.name, owner, args.description)
        if new != old:
            changed += 1
            print(("would update " if args.dry_run else "updated ") + str(path.relative_to(root)))
            if not args.dry_run:
                path.write_text(new, encoding="utf-8")

    if not args.keep_script and not args.dry_run:
        for leftover in TEMPLATE_ONLY_FILES:
            if (root / leftover).exists():
                (root / leftover).unlink()
                print(f"deleted {leftover}")

    print(f"\n{changed} file(s) {'would change' if args.dry_run else 'changed'}.")
    if not args.dry_run:
        print(
            "Next: cd src && uv sync && cp ../.env.sample ../.env, fill GOAL.md and PLAN.md,\n"
            f"then commit: 🎉 init: set up {args.name}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
