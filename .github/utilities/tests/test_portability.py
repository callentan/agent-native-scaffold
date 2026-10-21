"""Portable entrypoints and workflow launchers for the DDD maintenance tools."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import yaml

from tests.helpers import WORKTREE, directory_link, temporary_workspace


UTILITIES = WORKTREE / ".github" / "utilities"


def run_tool(script, *arguments, cwd):
    result = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(UTILITIES / script), *map(str, arguments)],
        cwd=cwd, shell=False, capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    return result, json.loads(result.stdout)


class PortabilityTests(unittest.TestCase):
    def test_paths_through_an_ancestor_link_work_like_their_resolved_paths(self):
        # macOS /tmp and /var, Windows junctioned folders and symlinked homes are ordinary paths.
        with temporary_workspace() as name:
            workspace = Path(name)
            real = workspace / "real"
            for role in ("base", "local", "candidate"):
                (real / role).mkdir(parents=True)
                (real / role / "rules.md").write_bytes(b"old\n" if role != "candidate" else b"new\n")
            (real / "notes.md").write_bytes(b"# Notes\n\nRule: keep owner bytes.\n")
            with directory_link(workspace / "via", real) as via:
                results = {}
                for label, parent in (("link", via), ("resolved", real)):
                    plan, plan_payload = run_tool(
                        "plan_template_update.py", "--base", parent / "base",
                        "--local", parent / "local", "--candidate", parent / "candidate", cwd=workspace)
                    extract, extract_payload = run_tool(
                        "extract_source.py", "--root", parent, "--source", "notes.md",
                        "--kind", "markdown", cwd=workspace)
                    self.assertEqual(0, plan.returncode, label + plan.stdout + plan.stderr)
                    self.assertEqual(0, extract.returncode, label + extract.stdout + extract.stderr)
                    results[label] = (plan_payload["status"], [c["path"] for c in plan_payload["changes"]],
                                      len(extract_payload["candidates"]))
                self.assertEqual(results["resolved"], results["link"])
                self.assertEqual("proposed", results["link"][0])
                report = via / "proposal.json"
                plan, _ = run_tool("plan_template_update.py", "--base", via / "base", "--local", via / "local",
                                   "--candidate", via / "candidate", "--output", report, cwd=workspace)
                self.assertEqual(0, plan.returncode, plan.stdout + plan.stderr)
                self.assertTrue((real / "proposal.json").is_file())

    def test_git_runtime_location_is_not_discarded_with_repository_overrides(self):
        from check_artifacts import _git_environment
        from hook_checks import git_environment
        with patch.dict(os.environ, GIT_EXEC_PATH="host-selected-git-tools",
                        GIT_DIR="unrelated-repository", GIT_WORK_TREE="unrelated-tree"):
            for environment in (_git_environment(), git_environment()):
                self.assertEqual("host-selected-git-tools", environment["GIT_EXEC_PATH"])
                self.assertNotIn("GIT_DIR", environment)
                self.assertNotIn("GIT_WORK_TREE", environment)

    def test_all_cli_entrypoints_start_outside_the_checkout(self):
        utilities = WORKTREE / ".github" / "utilities"
        scripts = []
        for path in sorted(utilities.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            if any(isinstance(node, ast.If)
                   and ast.unparse(node.test) == "__name__ == '__main__'"
                   for node in tree.body):
                scripts.append(path)
        scripts.extend(WORKTREE / ".github" / "hooks" / hook
                       for hook in ("pre-commit", "commit-msg"))
        self.assertGreaterEqual(len(scripts), 18)
        with temporary_workspace() as name:
            directory = Path(name) / "DDD проект € with spaces"
            directory.mkdir()
            for script in scripts:
                with self.subTest(script=script.name):
                    result = subprocess.run(
                        [sys.executable, "-B", "-X", "utf8", str(script), "--help"],
                        cwd=directory, shell=False, capture_output=True, timeout=30,
                    )
                    self.assertEqual(0, result.returncode,
                                     result.stdout.decode("utf-8", errors="replace")
                                     + result.stderr.decode("utf-8", errors="replace"))
                    self.assertIn(b"usage:", result.stdout.lower())
            self.assertEqual([], list(directory.iterdir()))

    def test_workflows_use_portable_python_launchers(self):
        workflows = WORKTREE / ".github" / "workflows"
        for path in sorted(workflows.glob("*.yml")):
            with self.subTest(workflow=path.name):
                workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
                for job in workflow["jobs"].values():
                    self.assertEqual("python", job["defaults"]["run"]["shell"])
                    for step in job["steps"]:
                        if "run" in step:
                            compile(step["run"], f"{path.name}:{step['name']}", "exec")
                            self.assertNotIn("/bin/python", step["run"])
                            self.assertNotIn("Scripts/python.exe", step["run"])

    def test_ci_covers_all_supported_hosts_without_shared_artifact_names(self):
        path = WORKTREE / ".github" / "workflows" / "tooling-tests.yml"
        job = yaml.safe_load(path.read_text(encoding="utf-8"))["jobs"]["tooling"]
        self.assertEqual(
            {"ubuntu-24.04", "windows-latest", "macos-latest"},
            set(job["strategy"]["matrix"]["os"]),
        )
        self.assertFalse(job["strategy"]["fail-fast"])
        artifact = next(step for step in job["steps"]
                        if step.get("uses", "").startswith("actions/upload-artifact@"))
        self.assertIn("${{ matrix.os }}", artifact["with"]["name"])


if __name__ == "__main__":
    unittest.main()
