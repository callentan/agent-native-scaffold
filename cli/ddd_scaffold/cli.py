from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import ScaffoldError, install, update, verify


def _source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", help="Scaffold git URL or local checkout (default: the official repository)")
    parser.add_argument("--ref", help="Tag or branch to fetch (default: latest tag)")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ddd-scaffold", description="Install or update the DDD scaffold.")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")
    inst = sub.add_parser("install", help="Install into ./<name> (the default when a name is given)")
    inst.add_argument("name", nargs="?")
    _source_arguments(inst)
    up = sub.add_parser("update", help="Plan or apply a scaffold update (dry run unless --apply)")
    _source_arguments(up)
    up.add_argument("--root", default=".", help="Project directory (default: current directory)")
    up.add_argument("--apply", action="store_true", help="Write the planned changes")
    up.add_argument("--force-locked", action="store_true",
                    help="Overwrite locally modified locked files after backing them up")
    up.add_argument("--allow-dirty", action="store_true", help="Apply even with uncommitted Git changes")
    ver = sub.add_parser("verify", help="Report locked files that differ from the installed receipt")
    ver.add_argument("--root", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in {"install", "update", "verify", "-h", "--help", "--version"}:
        argv = ["install", *argv]
    args = _parser().parse_args(argv)
    try:
        if args.command == "install":
            name = args.name if args.name is not None else input("Project name: ")
            target = install(name, Path.cwd(), args.source, args.ref)
            print(f"Installed the scaffold into {target}")
            print("Next: read AGENTS.md, then fill in PROJECT.md with the project-onboarding method.")
            print("Commit the result before running 'ddd-scaffold update'.")
            return 0
        if args.command == "update":
            plan, report = update(Path(args.root).resolve(), args.source, args.ref, args.apply,
                                  args.force_locked, args.allow_dirty)
            print(report, end="")
            if not args.apply:
                print("Dry run: nothing was written. Re-run with --apply to write.")
            return 1 if plan.conflicts else 0
        problems = verify(Path(args.root).resolve())
        for problem in problems:
            print(f"{problem.kind}: {problem.path}")
        print(f"{len(problems)} locked file(s) differ from the receipt.")
        return 1 if problems else 0
    except ScaffoldError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
