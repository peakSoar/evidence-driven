#!/usr/bin/env python3
"""Create the complete evidence-driven Harness structure from bundled assets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


MANIFEST = (
    Path("AGENTS.md"),
    Path("docs/改造计划与进度.md"),
    Path("docs/当前阶段与下一步.md"),
    Path("docs/验证规则.md"),
    Path("docs/阶段/S00-阶段模板.md"),
    Path("docs/验收/当前验收.md"),
)
PROJECT_NAME_TOKEN = "{{PROJECT_NAME}}"


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the complete evidence-driven Harness file structure."
    )
    parser.add_argument("--target", required=True, help="Target repository directory.")
    parser.add_argument(
        "--project-name",
        help="Value used for {{PROJECT_NAME}}; defaults to the target directory name.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the plan without writing files.",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Keep existing manifest files and create only missing files.",
    )
    return parser.parse_args()


def validate_template(template_root: Path) -> None:
    actual = {
        path.relative_to(template_root)
        for path in template_root.rglob("*")
        if path.is_file()
    }
    expected = set(MANIFEST)
    if actual != expected:
        missing = sorted(str(path) for path in expected - actual)
        unexpected = sorted(str(path) for path in actual - expected)
        details = []
        if missing:
            details.append(f"missing={missing}")
        if unexpected:
            details.append(f"unexpected={unexpected}")
        raise RuntimeError("Template manifest drift: " + ", ".join(details))


def validate_target(target: Path, skill_root: Path) -> None:
    filesystem_root = Path(target.anchor).resolve()
    home = Path.home().resolve()
    if (
        target in {filesystem_root, home}
        or target == skill_root
        or target.is_relative_to(skill_root)
    ):
        raise ValueError(f"Refusing unsafe target: {target}")
    if target.exists() and not target.is_dir():
        raise ValueError(f"Target is not a directory: {target}")


def required_directories(target: Path, destinations: list[Path]) -> list[Path]:
    directories = {target}
    for destination in destinations:
        parent = destination.parent
        while parent != target.parent and parent.is_relative_to(target):
            directories.add(parent)
            if parent == target:
                break
            parent = parent.parent
    return sorted(directories, key=lambda path: len(path.parts))


def create_structure(
    template_root: Path,
    target: Path,
    project_name: str,
    keep_existing: bool,
    dry_run: bool,
) -> int:
    destinations = [target / relative for relative in MANIFEST]
    conflicts = [path for path in destinations if path.exists()]
    if conflicts and not keep_existing:
        print(
            "Existing files block generation; no files were written:", file=sys.stderr
        )
        for path in conflicts:
            print(f"  {path}", file=sys.stderr)
        return 2

    for relative, destination in zip(MANIFEST, destinations, strict=True):
        action = "KEEP" if destination.exists() else "CREATE"
        print(f"[{action}] {relative}")

    if dry_run:
        print("Dry run complete; no files were written.")
        return 0

    created_files: list[Path] = []
    created_directories: list[Path] = []
    try:
        for directory in required_directories(target, destinations):
            if directory.exists():
                if not directory.is_dir():
                    raise NotADirectoryError(directory)
                continue
            directory.mkdir()
            created_directories.append(directory)

        for relative, destination in zip(MANIFEST, destinations, strict=True):
            if destination.exists():
                continue
            source = template_root / relative
            content = source.read_text(encoding="utf-8")
            content = content.replace(PROJECT_NAME_TOKEN, project_name)
            with destination.open("x", encoding="utf-8", newline="") as output:
                output.write(content)
            created_files.append(destination)
    except Exception:
        for path in reversed(created_files):
            path.unlink(missing_ok=True)
        for path in reversed(created_directories):
            try:
                path.rmdir()
            except OSError:
                pass
        raise

    print(
        f"Created {len(created_files)} file(s); kept {len(conflicts)} existing file(s)."
    )
    return 0


def main() -> int:
    configure_output()
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    template_root = skill_root / "assets" / "harness-template"
    target = Path(args.target).expanduser().resolve()
    project_name = args.project_name or target.name

    validate_template(template_root)
    validate_target(target, skill_root)
    return create_structure(
        template_root=template_root,
        target=target,
        project_name=project_name,
        keep_existing=args.keep_existing,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
