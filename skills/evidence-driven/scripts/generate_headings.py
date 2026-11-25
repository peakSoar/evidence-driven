#!/usr/bin/env python3
"""Generate a heading-only document from a bundled Harness template."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scaffold_harness import MANIFEST, configure_output


DOCUMENTS = dict(zip(
    ("agents", "plan", "handoff", "verification", "stage", "acceptance"),
    MANIFEST,
    strict=True,
))


def extract_headings(content: str) -> str:
    headings = []
    fence = None
    for line in content.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, tail = marker.groups()
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not tail.strip():
                fence = None
            continue
        if fence is None and re.match(r"^#{1,6} +\S", line):
            headings.append(line)
    if not headings:
        raise ValueError("Template contains no Markdown headings.")
    return "\n\n".join(headings) + "\n"


def main() -> int:
    configure_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document", required=True, choices=DOCUMENTS)
    parser.add_argument("--project-name", help="Replace {{PROJECT_NAME}} in headings.")
    parser.add_argument("--title", help="Replace the document's level-one heading (without #).")
    parser.add_argument("--output", type=Path, help="Create a new file; default: print to stdout.")
    args = parser.parse_args()
    if args.title is not None and (not args.title.strip() or "\n" in args.title or "\r" in args.title):
        parser.error("--title must be a non-empty single line.")
    if args.project_name is not None and ("\n" in args.project_name or "\r" in args.project_name):
        parser.error("--project-name must be a single line.")

    template = Path(__file__).resolve().parents[1] / "assets" / "harness-template" / DOCUMENTS[args.document]
    content = extract_headings(template.read_text(encoding="utf-8"))
    if args.project_name is not None:
        content = content.replace("{{PROJECT_NAME}}", args.project_name)
    if args.title is not None:
        content = re.sub(r"^# .*$", lambda match: "# " + args.title, content, count=1, flags=re.MULTILINE)
    if args.output is None:
        sys.stdout.write(content)
        return 0
    try:
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(content)
    except OSError as error:
        print(f"Cannot create output: {error}", file=sys.stderr)
        return 2
    print(f"Created heading skeleton: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
