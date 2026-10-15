"""Maintainer-only unittest runner: retain real counts and reject empty/skipped success."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest


class CountedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started_ids = set()

    def startTest(self, test):
        self.started_ids.add(id(test))
        super().startTest(test)


def _inputs():
    utilities = Path(__file__).resolve().parents[1]
    github = utilities.parent
    paths = [path for path in utilities.rglob("*.py") if "__pycache__" not in path.parts]
    paths.extend((github / "contracts").glob("*.json"))
    paths.extend(path for path in (github / "hooks").glob("*") if path.is_file())
    paths.extend(utilities.glob("requirements.*"))
    return {str(path.relative_to(github)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}


def _new_path(value, suffix):
    if value is None:
        return None
    if value.startswith(("//", "\\\\")) or "://" in value:
        raise ValueError("Output must be a local new file")
    path = Path(value).absolute()
    if (path.suffix != suffix or path.exists() or path.is_symlink()
            or not path.parent.is_dir() or path.parent.resolve() != path.parent):
        raise ValueError(f"Output requires an existing local parent and absent {suffix} file: {path}")
    return path


def _baseline(utilities, base):
    # This is provenance only, not discovery selection. Reuse the same strict
    # local Git-object contract as validation; never resolve a branch fallback.
    sys.path.insert(0, str(utilities))
    from hook_checks import git_scope, _parent
    from check_artifacts import _commit_tree
    root = utilities.parent.parent
    scope = git_scope(root)
    exact, tree, _ = _commit_tree(root, base) if base is not None else (None, None, None)
    return {"root": scope["root"], "head": _parent(root), "base_sha": exact, "base_tree": tree}


def main():
    utilities = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-directory", default=str(utilities / "tests"))
    parser.add_argument("--top-level-directory", default=str(utilities))
    parser.add_argument("--pattern", default="test_*.py")
    parser.add_argument("--report")
    parser.add_argument("--raw-output")
    parser.add_argument("--base", help="Exact local PR comparison commit, never a branch or abbreviated ID")
    args = parser.parse_args()
    payload = {
        "status": "input-error", "exit_code": 2, "cwd": str(Path.cwd()), "argv": sys.argv,
        "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
        "start_directory": str(Path(args.start_directory).absolute()),
        "top_level_directory": str(Path(args.top_level_directory).absolute()), "pattern": args.pattern,
        "discovered_count": 0, "run_count": 0, "executed_count": 0, "skipped_count": 0,
    }
    stream = io.StringIO()
    start = time.monotonic()
    report = raw_output = None
    try:
        report = _new_path(args.report, ".json")
        raw_output = _new_path(args.raw_output, ".txt")
        before = _inputs()
        payload["baseline"] = _baseline(utilities, args.base)
        loader = unittest.TestLoader()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            suite = loader.discover(args.start_directory, pattern=args.pattern,
                                    top_level_dir=args.top_level_directory)
            discovered = suite.countTestCases()
            result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=CountedResult).run(suite)
        method_skips = sum(id(test) in result.started_ids for test, _ in result.skipped)
        executed = result.testsRun - method_skips
        gate = discovered > 0 and executed > 0 and result.wasSuccessful()
        payload.update(
            status="passed" if gate else "failed", exit_code=0 if gate else 1,
            discovered_count=discovered, run_count=result.testsRun, executed_count=executed,
            skipped_count=len(result.skipped), skipped_test_count=method_skips,
            skipped_other_count=len(result.skipped) - method_skips,
            failure_count=len(result.failures), error_count=len(result.errors),
            expected_failure_count=len(result.expectedFailures),
            unexpected_success_count=len(result.unexpectedSuccesses),
            skipped=[{"test": str(test), "reason": reason} for test, reason in result.skipped],
            gate_reason="nonempty executed suite" if gate else
            "test failure/error" if not result.wasSuccessful() else
            "zero discovery" if not discovered else "all tests skipped",
            input_sha256=before, inputs_unchanged=before == _inputs(),
        )
        if not payload["inputs_unchanged"]:
            payload.update(status="input-error", exit_code=2, gate_reason="Tested tool inputs changed during execution")
    except (OSError, ValueError, ImportError) as error:
        payload.update(status="input-error", exit_code=2, error=str(error),
                       error_code=getattr(error, "code", "RUNNER_INPUT_ERROR"))
    payload["duration_seconds"] = time.monotonic() - start
    try:
        if raw_output:
            with raw_output.open("x", encoding="utf-8", newline="\n") as output:
                output.write(stream.getvalue())
            payload["raw_output"] = str(raw_output)
        if report:
            with report.open("x", encoding="utf-8", newline="\n") as output:
                output.write(json.dumps(payload, ensure_ascii=True, indent=2) + "\n")
    except (OSError, ValueError, ImportError) as error:
        payload.update(status="input-error", exit_code=2, error=str(error),
                       error_code="RUNNER_OUTPUT_ERROR")
    print(stream.getvalue(), file=sys.stderr, end="")
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return payload["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
