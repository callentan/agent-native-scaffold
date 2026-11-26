import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parents[1]
REPO = CLI_DIR.parent
MANIFEST = "docs/distribution-manifest.json"


def run_cli(cwd: Path, *arguments: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(CLI_DIR), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, "-B", "-X", "utf8", "-m", "ddd_scaffold", *arguments],
                          cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8",
                          shell=False, check=False)


def copy_source(destination: Path) -> list[dict]:
    entries = json.loads((REPO / MANIFEST).read_text(encoding="utf-8"))["files"]
    for entry in entries:
        target = destination / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / entry["path"], target)
    return entries


class ScaffoldCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="ddd cli 项目 ")
        self.addCleanup(self._temp.cleanup)
        self.work = Path(self._temp.name).resolve()
        self.source = self.work / "source"
        self.entries = copy_source(self.source)
        self.parent = self.work / "parent"
        self.parent.mkdir()

    def install(self, name: str = "demo") -> Path:
        result = run_cli(self.parent, name, "--source", str(self.source))
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.parent / name

    def test_install_copies_every_manifest_file_with_name_and_markers(self):
        project = self.install("demo")
        for entry in self.entries:
            self.assertTrue((project / entry["path"]).is_file(), entry["path"])
        project_md = (project / "PROJECT.md").read_text(encoding="utf-8")
        self.assertTrue(project_md.startswith("# demo\n"))
        self.assertIn("| Project name | demo |", project_md)
        self.assertTrue((project / "AGENTS.md").read_text(encoding="utf-8").startswith("<!-- scaffold: locked -->"))
        self.assertTrue((project / "stakeholder-requirements/product.md").read_bytes()
                        == (self.source / "stakeholder-requirements/product.md").read_bytes())
        skill = (project / ".github/skills/implement-task/SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\nname: implement-task"))
        self.assertIn("\n---\n<!-- scaffold: locked -->\n", skill)
        locked = (project / ".scaffold/locked.txt").read_text(encoding="utf-8").splitlines()
        self.assertIn("AGENTS.md", locked)
        self.assertNotIn("PROJECT.md", locked)
        self.assertEqual(run_cli(project, "verify").returncode, 0)

    def test_install_refuses_non_empty_target_and_bad_names(self):
        (self.parent / "taken").mkdir()
        (self.parent / "taken" / "file.txt").write_text("keep", encoding="utf-8")
        result = run_cli(self.parent, "taken", "--source", str(self.source))
        self.assertEqual(result.returncode, 2)
        self.assertEqual((self.parent / "taken" / "file.txt").read_text(encoding="utf-8"), "keep")
        for bad in ("..", "a/b", "con", "update", "-x", "a b"):
            with self.subTest(name=bad):
                result = run_cli(self.parent, "install", bad, "--source", str(self.source))
                self.assertNotEqual(result.returncode, 0)
        self.assertEqual([p.name for p in self.parent.iterdir()], ["taken"])

    def test_verify_reports_modified_and_missing_locked_files(self):
        project = self.install()
        (project / "AGENTS.md").write_text("changed", encoding="utf-8")
        (project / "README.md").unlink()
        (project / "PROJECT.md").write_text("project edits are fine", encoding="utf-8")
        result = run_cli(project, "verify")
        self.assertEqual(result.returncode, 1)
        self.assertIn("modified: AGENTS.md", result.stdout)
        self.assertIn("missing: README.md", result.stdout)
        self.assertNotIn("PROJECT.md", result.stdout)

    def test_update_without_receipt_is_refused(self):
        result = run_cli(self.parent, "update", "--source", str(self.source))
        self.assertEqual(result.returncode, 2)

    def test_update_dry_run_then_apply_follows_ownership(self):
        project = self.install()
        (project / "stakeholder-requirements/product.md").write_text("my product", encoding="utf-8")
        (project / "domain-model/overview.md").write_text("my overview", encoding="utf-8")
        agents = self.source / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8") + "\nnew rule\n", encoding="utf-8")
        product = self.source / "stakeholder-requirements/product.md"
        product.write_text(product.read_text(encoding="utf-8") + "\nnew section\n", encoding="utf-8")
        (self.source / "docs/extra-guide.md").write_text("# Extra\n", encoding="utf-8")
        manifest = json.loads((self.source / MANIFEST).read_text(encoding="utf-8"))
        manifest["files"].append({"path": "docs/extra-guide.md", "component": "basic-guidance"})
        (self.source / MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")

        before = (project / "AGENTS.md").read_bytes()
        dry = run_cli(project, "update", "--source", str(self.source))
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertIn("update: AGENTS.md", dry.stdout)
        self.assertIn("add: docs/extra-guide.md", dry.stdout)
        self.assertIn("review: stakeholder-requirements/product.md", dry.stdout)
        self.assertEqual((project / "AGENTS.md").read_bytes(), before)
        self.assertFalse((project / "docs/extra-guide.md").exists())

        applied = run_cli(project, "update", "--source", str(self.source), "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertIn("new rule", (project / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertTrue((project / "docs/extra-guide.md").read_text(encoding="utf-8").startswith("<!-- scaffold: locked -->"))
        self.assertEqual((project / "stakeholder-requirements/product.md").read_text(encoding="utf-8"), "my product")
        self.assertEqual((project / "domain-model/overview.md").read_text(encoding="utf-8"), "my overview")
        report = (project / ".scaffold/update-report.md").read_text(encoding="utf-8")
        self.assertIn("+new section", report)
        self.assertEqual(run_cli(project, "verify").returncode, 0)
        again = run_cli(project, "update", "--source", str(self.source))
        self.assertIn("Everything is up to date.", again.stdout)

    def test_modified_locked_file_conflicts_until_forced_with_backup(self):
        project = self.install()
        (project / "AGENTS.md").write_text("local edit", encoding="utf-8")
        agents = self.source / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8") + "\nnew rule\n", encoding="utf-8")
        result = run_cli(project, "update", "--source", str(self.source), "--apply")
        self.assertEqual(result.returncode, 1)
        self.assertIn("conflict: AGENTS.md", result.stdout)
        self.assertEqual((project / "AGENTS.md").read_text(encoding="utf-8"), "local edit")
        forced = run_cli(project, "update", "--source", str(self.source), "--apply", "--force-locked")
        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertIn("new rule", (project / "AGENTS.md").read_text(encoding="utf-8"))
        backups = list((project / ".scaffold/overwritten").glob("*/AGENTS.md"))
        self.assertEqual([b.read_text(encoding="utf-8") for b in backups], ["local edit"])

    def test_apply_refuses_dirty_git_workspace(self):
        project = self.install()
        subprocess.run(["git", "init", "-q"], cwd=project, check=True, shell=False)
        result = run_cli(project, "update", "--source", str(self.source), "--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("uncommitted", result.stderr)
        allowed = run_cli(project, "update", "--source", str(self.source), "--apply", "--allow-dirty")
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_unsafe_manifest_path_is_rejected(self):
        manifest = json.loads((self.source / MANIFEST).read_text(encoding="utf-8"))
        manifest["files"].append({"path": "../escape.txt", "component": "basic-guidance"})
        (self.source / MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
        result = run_cli(self.parent, "demo", "--source", str(self.source))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(list(self.parent.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
