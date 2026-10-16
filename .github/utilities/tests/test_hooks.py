"""ENH-10 / HOOK-01..12, CI-01/03: real index, installer and native Git tests.

These self-owned repositories never use the helpers.git commit-signing override.
Host Git configuration is isolated at fixture creation; actual commits use the
installed hooks without --no-verify, hooksPath overrides or signing overrides.
CI-02 discovery controls are separate runner experiments, not self-count tests.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
import venv

from tests.helpers import WORKTREE, metadata, write_artifact, write_delivery_fixture, write_metadata


UTILITIES = WORKTREE / ".github" / "utilities"
REVIEW = "\n\nReviewed-by: Fixture Reviewer"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class HookFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="task10-hooks-", dir=WORKTREE / ".venv")
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "项目 with spaces"
        self.root.mkdir()
        self.receipts = []
        self.addCleanup(self.save_receipts)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0",
                        PYTHONDONTWRITEBYTECODE="1")
        # Only downstream runtime modules/contracts, no maker tests or records.
        target = self.root / ".github" / "utilities"
        target.mkdir(parents=True)
        for path in UTILITIES.iterdir():
            if path.suffix == ".py" or path.name in ("requirements.txt", "requirements.lock"):
                shutil.copyfile(path, target / path.name)
        shutil.copytree(WORKTREE / ".github" / "contracts", self.root / ".github" / "contracts")
        hooks = WORKTREE / ".github" / "hooks"
        if hooks.is_dir():
            shutil.copytree(hooks, self.root / ".github" / "hooks")
        (self.root / ".gitignore").write_bytes(b".venv/\n")
        self.git("init", "--quiet", "--template=")
        self.git("config", "--local", "user.name", "Native fixture")
        self.git("config", "--local", "user.email", "fixture@example.invalid")
        self.git("config", "--local", "core.autocrlf", "false")
        self.git("add", "--", ".")
        self.git("commit", "--quiet", "-m", "Fixture baseline before optional installation")
        self.parent = self.git("rev-parse", "HEAD").strip()

    def save_receipts(self):
        destination = os.environ.get("TASK10_RECEIPTS")
        if destination:
            path = Path(destination)
            if not path.is_absolute() or not path.is_dir():
                raise AssertionError("TASK10_RECEIPTS must be an existing absolute evidence directory")
            with (path / (self.id().replace(".", "_") + ".json")).open("x", encoding="utf-8") as out:
                json.dump({"test": self.id(), "commands": self.receipts},
                          out, ensure_ascii=False, indent=2)

    def call(self, args, *, env=None, input=None):
        result = subprocess.run(args, cwd=self.root, env=env or self.env, input=input,
                                shell=False, capture_output=True, timeout=90)
        self.receipts.append({
            "argv": [str(a) for a in args], "cwd": str(self.root),
            "returncode": result.returncode,
            "stdout": result.stdout.decode("utf-8", errors="replace"),
            "stderr": result.stderr.decode("utf-8", errors="replace"),
        })
        return result

    def git(self, *args, input=None):
        result = self.call(["git", "--no-pager", *args], input=input)
        self.assertEqual(0, result.returncode, self.receipts[-1])
        return result.stdout.decode("utf-8")

    def installer(self, *args, hooks=("pre-commit", "commit-msg"), python=None, restore=False):
        script = self.root / ".github/utilities/install_hooks.py"
        self.assertTrue(script.is_file(), "Task10 optional installer is not implemented")
        arguments = [sys.executable, "-B", "-X", "utf8", str(script),
                     "--root", str(self.root)]
        for hook in hooks:
            arguments += ["--hook", hook]
        if restore:
            arguments += ["--restore"]
        else:
            arguments += ["--python", str(python or sys.executable)]
        return self.call([*arguments, *args])

    def install(self, **kwargs):
        result = self.installer("--apply", **kwargs)
        self.assertEqual(0, result.returncode, self.receipts[-1])
        payload = json.loads(result.stdout)
        self.assertEqual("installed", payload["status"])
        return payload

    def check(self, *args, env=None):
        script = self.root / ".github/utilities/hook_checks.py"
        self.assertTrue(script.is_file(), "Task10 shared index adapter is not implemented")
        return self.call([sys.executable, "-B", "-X", "utf8", str(script),
                          "pre-commit", "--root", str(self.root), *args], env=env)

    def state(self):
        files = {}
        for path in self.root.rglob("*"):
            relative = path.relative_to(self.root)
            if path.is_file() and not {".git", ".venv"}.intersection(relative.parts):
                files[relative.as_posix()] = sha(path.read_bytes())
        hooks = self.root / ".git/hooks"
        result = {
            "head": self.git("rev-parse", "--verify", "HEAD").strip(),
            "entries": self.git("ls-files", "--stage", "-z"),
            "index_sha256": sha((self.root / ".git/index").read_bytes()),
            "config_sha256": sha((self.root / ".git/config").read_bytes()),
            "files": files,
            "hooks": {p.name: sha(p.read_bytes()) for p in hooks.iterdir() if p.is_file()}
            if hooks.exists() else {},
        }
        self.receipts.append({"observation": "protected_state", "state": result})
        return result

    def native_commit(self, message="Native controlled commit" + REVIEW, *extra, env=None):
        return self.call(["git", "--no-pager", "commit", "--quiet", "-m", message, *extra], env=env)

    def native_reports(self, result):
        reports = []
        for line in (result.stdout + b"\n" + result.stderr).decode("utf-8").splitlines():
            if line.startswith("{"):
                value = json.loads(line)
                if "hook" in value:
                    reports.append(value)
        return reports

    def stage_artifact(self, *, name="stakeholder-requirements/REQ-001.md"):
        path = write_artifact(self.root, relative_path=name)
        self.git("add", "--", name)
        return path

    def finding_codes(self, payload):
        return {finding["code"] for finding in payload["findings"]}

    def private_runtime(self, *, full_interpreter=False):
        """Only fixture-local binaries/config/.pth; never install a package."""
        environment = self.root / ".venv"
        venv.EnvBuilder(with_pip=False).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        site = environment / ("Lib/site-packages" if os.name == "nt"
                              else f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
        import yaml
        dependencies = Path(yaml.__file__).parent.parent
        (site / "maintenance.pth").write_text(str(dependencies) + "\n", encoding="utf-8")
        copied = []
        if full_interpreter and os.name == "nt":
            # Real full binaries, not the stock Windows redirector and not a
            # mocked prefix. This fixture needs explicit HOME/PATH below.
            base = Path(sys._base_executable).parent
            for name in ("python.exe", f"python{sys.version_info.major}{sys.version_info.minor}.dll",
                         "python3.dll"):
                source, target = base / name, python.parent / name
                shutil.copyfile(source, target)
                copied.append({"source": str(source), "destination": str(target),
                               "sha256": sha(target.read_bytes())})
        self.receipts.append({"observation": "private_runtime", "selected": str(python),
                              "copied_real_binaries": copied, "global_installs": False})
        return environment, python, site, dependencies


class InstallerTests(HookFixture):
    def test_hook01_inspection_proposes_exact_selected_paths_without_writes(self):
        before = self.state()
        result = self.installer(hooks=("pre-commit",))
        self.assertEqual(0, result.returncode, self.receipts[-1])
        payload = json.loads(result.stdout)
        self.assertEqual("proposed", payload["status"])
        self.assertEqual([str(self.root / ".git/hooks/pre-commit")],
                         [action["path"] for action in payload["actions"]])
        self.assertEqual([], payload["config_changes"])
        self.assertEqual(before, self.state())

    def test_hook02_owner_hook_conflict_is_atomic_and_preserves_unrelated_hooks(self):
        hooks = self.root / ".git/hooks"
        hooks.mkdir(exist_ok=True)
        (hooks / "commit-msg").write_bytes(b"owner bytes\r\n")
        (hooks / "post-commit").write_bytes(b"unrelated owner\n")
        before = self.state()
        result = self.installer("--apply")
        self.assertEqual(2, result.returncode)
        self.assertEqual("conflict", json.loads(result.stdout)["status"])
        self.assertEqual(before, self.state())
        self.assertFalse((hooks / "pre-commit").exists())

    def test_hook02_configured_hooks_path_is_not_overwritten_or_ignored(self):
        self.git("config", "--local", "core.hooksPath", "owner hooks")
        before = self.state()
        result = self.installer("--apply")
        self.assertEqual(2, result.returncode)
        self.assertIn("HOOKS_PATH_CONFLICT", self.finding_codes(json.loads(result.stdout)))
        self.assertEqual(before, self.state())

    def test_hook08_missing_interpreter_is_preflight_error_without_installation(self):
        before = self.state()
        result = self.installer("--apply", python=self.workspace / "missing python")
        self.assertEqual(2, result.returncode)
        self.assertIn("INTERPRETER_UNAVAILABLE", self.finding_codes(json.loads(result.stdout)))
        self.assertEqual(before, self.state())

    def test_missing_distributed_helper_is_rejected_before_any_hook_is_written(self):
        (self.root / ".github/utilities/check_traceability.py").unlink()
        before = self.state()
        result = self.installer("--apply")
        self.assertEqual(2, result.returncode)
        self.assertIn("SOURCE_UNAVAILABLE", self.finding_codes(json.loads(result.stdout)))
        self.assertEqual(before, self.state())

    def test_owner_hook_directory_link_is_not_followed(self):
        from tests.helpers import directory_link
        owner = self.workspace / "owner hooks"
        owner.mkdir()
        (owner / "pre-commit").write_bytes(b"owner content\n")
        hooks = self.root / ".git/hooks"
        if hooks.exists():
            hooks.rmdir()
        with directory_link(hooks, owner):
            result = self.installer("--apply")
            self.assertEqual(2, result.returncode)
            self.assertEqual(b"owner content\n", (owner / "pre-commit").read_bytes())
            self.assertEqual(["pre-commit"], [p.name for p in owner.iterdir()])

    def test_hook10_restore_refuses_owner_edit_before_deleting_any_selected_file(self):
        installed = self.install()
        hook = self.root / ".git/hooks/commit-msg"
        owned = hook.read_bytes()
        hook.write_bytes(owned + b"\n# later owner edit\n")
        before = self.state()
        result = self.installer("--apply", restore=True)
        self.assertEqual(2, result.returncode)
        self.assertIn("OWNERSHIP_CONFLICT", self.finding_codes(json.loads(result.stdout)))
        self.assertEqual(before, self.state())
        self.assertEqual(2, len(installed["actions"]))

    def test_hook10_exact_owned_restore_leaves_config_sources_and_unrelated_hook(self):
        hooks = self.root / ".git/hooks"
        hooks.mkdir(exist_ok=True)
        (hooks / "post-commit").write_bytes(b"unrelated owner\n")
        before = self.state()
        self.install()
        inspection = self.installer(restore=True)
        self.assertEqual("restore-proposed", json.loads(inspection.stdout)["status"])
        result = self.installer("--apply", restore=True)
        self.assertEqual(0, result.returncode, self.receipts[-1])
        self.assertEqual("restored", json.loads(result.stdout)["status"])
        self.assertEqual(before, self.state())

    def test_hook10_owner_edited_receipt_is_a_conflict_not_partial_restoration(self):
        self.install()
        receipt = self.root / ".git/hooks/commit-msg.artifact-maintenance.json"
        for edited in (b"[]\n", b"owner edited non-JSON\n"):
            with self.subTest(edited=edited):
                receipt.write_bytes(edited)
                before = self.state()
                result = self.installer("--apply", restore=True)
                self.assertEqual(2, result.returncode)
                self.assertIn("OWNERSHIP_CONFLICT", self.finding_codes(json.loads(result.stdout)))
                self.assertEqual(before, self.state())

    def fault_install(self, target_name, failure, *, later_owner_edit=False):
        """Inject only fixture file I/O; all Git/interpreter/filesystem work is real."""
        target = self.root / ".git/hooks" / target_name
        script = textwrap.dedent("""\
            import errno, json, sys
            from pathlib import Path
            from unittest.mock import patch
            sys.path.insert(0, sys.argv[1])
            from install_hooks import install
            target, failure = Path(sys.argv[3]), sys.argv[4]
            owner_edit = sys.argv[5] == "yes"
            original_open = Path.open
            class ControlledFile:
                def __init__(self, stream):
                    self.stream = stream
                def __enter__(self):
                    return self
                def write(self, raw):
                    if failure in ("write", "short"):
                        count = self.stream.write(raw[:17])
                        self.stream.flush()
                        if failure == "short":
                            return count
                        raise OSError(errno.ENOSPC, "controlled fixture write boundary")
                    return self.stream.write(raw)
                def __exit__(self, exc_type, exc, tb):
                    try:
                        if exc_type is None and failure == "flush":
                            self.stream.flush()
                            raise OSError(errno.ENOSPC, "controlled fixture flush boundary")
                    finally:
                        self.stream.close()
                    if exc_type is None and failure == "close":
                        if owner_edit:
                            (target.parent / "pre-commit").write_bytes(b"later owner bytes\\n")
                        raise OSError(errno.EIO, "controlled fixture close boundary")
            def controlled_open(path, *args, **kwargs):
                stream = original_open(path, *args, **kwargs)
                return ControlledFile(stream) if path == target and args == ("xb",) else stream
            with patch.object(Path, "open", controlled_open):
                payload = install(sys.argv[2], ["pre-commit"], sys.executable, apply=True)
            print(json.dumps(payload))
            raise SystemExit(payload["exit_code"])
            """)
        return self.call([sys.executable, "-B", "-X", "utf8", "-c", script,
                          str(self.root / ".github/utilities"), str(self.root),
                          str(target), failure, "yes" if later_owner_edit else "no"])

    def test_m1_partial_hook_and_receipt_write_flush_close_are_exactly_accounted(self):
        hooks = self.root / ".git/hooks"
        hooks.mkdir(exist_ok=True)
        (hooks / "post-commit").write_bytes(b"unrelated owner bytes\n")
        hook, receipt = hooks / "pre-commit", hooks / "pre-commit.artifact-maintenance.json"
        for target in (hook, receipt):
            for failure in ("write", "flush", "close"):
                with self.subTest(target=target.name, failure=failure):
                    before = self.state()
                    try:
                        result = self.fault_install(target.name, failure)
                        self.assertEqual(2, result.returncode, self.receipts[-1])
                        payload = json.loads(result.stdout)
                        expected = [str(hook)] if target == hook else [str(hook), str(receipt)]
                        self.assertEqual(expected, payload["written"])
                        self.assertEqual("manual-required", payload["recovery"]["state"])
                        self.assertFalse(payload["recovery"]["automatic_cleanup"])
                        self.assertEqual(expected, [item["path"] for item in payload["recovery"]["files"]])
                        self.assertFalse(payload["recovery"]["files"][-1]["write_complete"])
                        for item in payload["recovery"]["files"]:
                            raw = Path(item["path"]).read_bytes()
                            self.assertEqual((len(raw), sha(raw)), (item["bytes"], item["sha256"]))
                        after = self.state()
                        for key in ("head", "entries", "index_sha256", "config_sha256", "files"):
                            self.assertEqual(before[key], after[key], key)
                        self.assertEqual(b"unrelated owner bytes\n", (hooks / "post-commit").read_bytes())
                    finally:
                        # Exact test-owned files only, so independent injections
                        # share no residue. Production recovery never does this.
                        for path in (receipt, hook):
                            if path.is_file():
                                path.unlink()

    def test_m1_short_write_is_an_error_with_a_retained_partial_path(self):
        result = self.fault_install("pre-commit", "short")
        self.assertEqual(2, result.returncode, self.receipts[-1])
        payload = json.loads(result.stdout)
        hook = self.root / ".git/hooks/pre-commit"
        self.assertEqual([str(hook)], payload["written"])
        self.assertEqual(17, len(hook.read_bytes()))
        self.assertFalse((hook.parent / "pre-commit.artifact-maintenance.json").exists())
        self.assertEqual("manual-required", payload["recovery"]["state"])

    def test_m1_recovery_keeps_later_owner_edits_and_refuses_automatic_reinstallation(self):
        result = self.fault_install("pre-commit.artifact-maintenance.json", "close",
                                    later_owner_edit=True)
        self.assertEqual(2, result.returncode, self.receipts[-1])
        payload = json.loads(result.stdout)
        hook = self.root / ".git/hooks/pre-commit"
        self.assertEqual(b"later owner bytes\n", hook.read_bytes())
        self.assertEqual([str(hook), str(hook.parent / "pre-commit.artifact-maintenance.json")],
                         payload["written"])
        self.assertFalse(payload["recovery"]["files"][0]["matches_expected"])
        before = self.state()
        retry = self.installer("--apply", hooks=("pre-commit",))
        self.assertEqual(2, retry.returncode)
        self.assertIn("HOOK_CONFLICT", self.finding_codes(json.loads(retry.stdout)))
        restore = self.installer("--apply", hooks=("pre-commit",), restore=True)
        self.assertEqual(2, restore.returncode)
        self.assertIn("OWNERSHIP_CONFLICT", self.finding_codes(json.loads(restore.stdout)))
        self.assertEqual(before, self.state())


class NativeHookTests(HookFixture):
    def test_i1_native_unmanaged_commit_reaches_both_installed_hooks(self):
        self.install()
        (self.root / "unmanaged.txt").write_bytes(b"native unmanaged change\n")
        self.git("add", "--", "unmanaged.txt")
        result = self.native_commit("Unmanaged without a reviewer line")
        self.assertEqual(0, result.returncode, self.receipts[-1])
        reports = self.native_reports(result)
        self.assertEqual(["pre-commit", "commit-msg"], [report["hook"] for report in reports])
        self.assertFalse(reports[1]["policy"]["required"])
        self.assertEqual(str(Path(sys.executable).absolute()), reports[1]["runtime"]["executable"])

    def configuration_loss(self, *, full_interpreter):
        environment, python, _, dependencies = self.private_runtime(full_interpreter=full_interpreter)
        self.install(hooks=("pre-commit",), python=python)
        native_env = dict(self.env, PYTHONPATH=str(dependencies),
                          TEMP=str(self.workspace), TMP=str(self.workspace))
        if full_interpreter and os.name == "nt":
            native_env["PYTHONHOME"] = sys.base_prefix
        self.receipts.append({
            "observation": "configuration_loss_boundary",
            "variant": "full-interpreter" if full_interpreter else "standard-loader",
            "host": os.name, "POSIX_executed_on_Windows": False,
            "environment": {key: native_env.get(key) for key in ("PYTHONHOME", "PYTHONPATH", "TEMP", "TMP")},
        })
        path = self.stage_artifact()
        accepted = self.native_commit(env=native_env)
        self.assertEqual(0, accepted.returncode, self.receipts[-1])
        self.assertEqual(str(environment), self.native_reports(accepted)[0]["runtime"]["prefix"])
        cfg = environment / "pyvenv.cfg"
        cfg_hash, exe_hash = sha(cfg.read_bytes()), sha(python.read_bytes())
        cfg.rename(environment / "pyvenv.cfg.saved")
        control = self.call([
            str(python), "-B", "-X", "utf8", "-c",
            "import sys,json; print(json.dumps({'prefix':sys.prefix,'base_prefix':sys.base_prefix,"
            "'executable':sys.executable}))",
        ], env=native_env)
        if full_interpreter or os.name != "nt":
            self.assertEqual(0, control.returncode, self.receipts[-1])
            facts = json.loads(control.stdout)
            self.assertEqual(facts["base_prefix"], facts["prefix"])
            self.assertEqual(str(python), facts["executable"])
        else:
            # This control already passed before the fix. The stock Windows
            # loader, not hook_checks, refuses before Python can report JSON.
            self.assertNotEqual(0, control.returncode)
            self.assertIn(b"pyvenv.cfg", control.stderr)
        path.write_bytes(path.read_bytes() + b"\nConfiguration-loss controlled change.\n")
        self.git("add", "--", str(path))
        before = self.state()
        refused = self.native_commit(env=native_env)
        self.assertNotEqual(0, refused.returncode, self.receipts[-1])
        reports = self.native_reports(refused)
        if full_interpreter or os.name != "nt":
            self.assertEqual(1, len(reports))
            self.assertEqual(2, reports[0]["exit_code"])
            self.assertIn("ENVIRONMENT_UNAVAILABLE", self.finding_codes(reports[0]))
            self.assertEqual({}, reports[0]["snapshot"])
            self.assertNotIn("checks", reports[0])
            self.assertIn("pyvenv.cfg", reports[0]["findings"][0]["message"])
            self.assertIn("requirements.lock", reports[0]["findings"][0]["message"])
        else:
            self.assertEqual([], reports)
            self.assertIn(b"pyvenv.cfg", refused.stderr)
        after = self.state()
        for key in ("head", "entries", "files", "config_sha256", "hooks"):
            self.assertEqual(before[key], after[key], key)
        self.assertFalse(cfg.exists())
        self.assertEqual(cfg_hash, sha((environment / "pyvenv.cfg.saved").read_bytes()))
        self.assertEqual(exe_hash, sha(python.read_bytes()))

    def test_i2_native_configuration_loss_with_a_real_full_interpreter_cannot_use_base(self):
        self.configuration_loss(full_interpreter=True)

    def test_i2_native_standard_loader_configuration_loss_is_a_separate_control(self):
        self.configuration_loss(full_interpreter=False)

    def dependency_version_drift(self, hook):
        environment, python, site, _ = self.private_runtime()
        self.install(hooks=(hook,), python=python)
        # Genuine local dist-info version drift, not a mocked import or prefix.
        info = site / "jsonschema-0.0.dist-info"
        info.mkdir()
        (info / "METADATA").write_bytes(b"Metadata-Version: 2.1\nName: jsonschema\nVersion: 0.0\n")
        self.stage_artifact()
        before = self.state()
        result = self.native_commit()
        self.assertNotEqual(0, result.returncode, self.receipts[-1])
        report = self.native_reports(result)[0]
        self.assertEqual(2, report["exit_code"])
        self.assertIn("DEPENDENCY_UNAVAILABLE", self.finding_codes(report))
        self.assertEqual({}, report["snapshot"])
        self.assertNotIn("checks", report)
        self.assertIn("requirements.lock", report["findings"][0]["message"])
        self.assertEqual(str(environment), report["runtime"]["prefix"])
        after = self.state()
        for key in ("head", "entries", "files", "config_sha256", "hooks"):
            self.assertEqual(before[key], after[key], key)

    def test_i2_native_pre_commit_refuses_dependency_version_drift_before_source_checks(self):
        self.dependency_version_drift("pre-commit")

    def test_i2_native_commit_msg_refuses_dependency_version_drift_before_source_checks(self):
        self.dependency_version_drift("commit-msg")

    def test_runtime_tool_identity_is_not_mislabeled_as_the_staged_tool_blob(self):
        self.install(hooks=("pre-commit",))
        self.stage_artifact()
        source = self.root / ".github/utilities/hook_checks.py"
        staged = source.read_bytes()
        changed = staged + b"\n# Explicit unstaged runtime identity fixture.\n"
        source.write_bytes(changed)
        result = self.native_commit()
        self.assertEqual(0, result.returncode, self.receipts[-1])
        report = self.native_reports(result)[0]
        self.assertIn("tool_sources", report["runtime"])
        self.assertEqual(sha(changed), report["runtime"]["tool_sources"][".github/utilities/hook_checks.py"])
        entry = next(e for e in report["snapshot"]["entries"] if e["path"] == ".github/utilities/hook_checks.py")
        self.assertEqual(sha(staged), entry["sha256"])
        self.assertEqual(changed, source.read_bytes())

    def test_hook03_hook09_native_commit_uses_selected_python_spaces_unicode_and_index(self):
        self.install()
        path = self.stage_artifact(name="stakeholder-requirements/条目 space/REQ-001.md")
        blob = self.git("rev-parse", ":stakeholder-requirements/条目 space/REQ-001.md").strip()
        expected_tree = self.git("write-tree").strip()
        native_env = dict(self.env)
        native_env.pop("PYTHONDONTWRITEBYTECODE", None)
        result = self.native_commit(env=native_env)
        self.assertEqual(0, result.returncode, self.receipts[-1])
        reports = self.native_reports(result)
        self.assertEqual(["pre-commit", "commit-msg"], [r["hook"] for r in reports])
        pre = reports[0]
        self.assertEqual(str(Path(sys.executable).absolute()), pre["runtime"]["executable"])
        self.assertEqual(sys.prefix, pre["runtime"]["prefix"])
        self.assertEqual([], list((self.root / ".github").rglob("*.pyc")))
        self.assertEqual(self.parent, pre["snapshot"]["parent"])
        self.assertEqual(expected_tree, pre["snapshot"]["index_tree"])
        self.assertEqual(1, pre["checked_count"])
        entry = next(e for e in pre["snapshot"]["entries"] if e["path"].endswith("REQ-001.md"))
        self.assertEqual(("100644", blob, sha(path.read_bytes())),
                         (entry["mode"], entry["blob"], entry["sha256"]))
        self.assertEqual(expected_tree, self.git("rev-parse", "HEAD^{tree}").strip())
        self.assertEqual("not-applicable", pre["checks"]["coverage"]["status"])
        self.assertFalse(reports[1]["policy"]["authenticated"])

    def test_hook04_native_invalid_index_cannot_be_hidden_by_unstaged_repair(self):
        self.install(hooks=("pre-commit",))
        path = self.stage_artifact()
        good = path.read_bytes()
        path.write_bytes(good.replace(b"schemaVersion: 1", b"schemaVersion: 9"))
        self.git("add", "--", str(path))
        path.write_bytes(good)
        before = self.state()
        result = self.native_commit()
        self.assertNotEqual(0, result.returncode)
        report = self.native_reports(result)[0]
        self.assertEqual(2, report["exit_code"])
        self.assertIn("UNSUPPORTED_SCHEMA_VERSION", self.finding_codes(report))
        after = self.state()
        for key in ("head", "entries", "files", "config_sha256", "hooks"):
            self.assertEqual(before[key], after[key], key)
        self.assertEqual(good, path.read_bytes())

    def test_hook05_native_valid_index_ignores_and_preserves_unstaged_breakage(self):
        self.install(hooks=("pre-commit",))
        path = self.stage_artifact()
        staged = path.read_bytes()
        path.write_bytes(b"broken unstaged owner file\n")
        result = self.native_commit()
        self.assertEqual(0, result.returncode, self.receipts[-1])
        self.assertEqual(b"broken unstaged owner file\n", path.read_bytes())
        committed = self.call(["git", "show", "HEAD:stakeholder-requirements/REQ-001.md"])
        self.assertEqual(staged, committed.stdout)
        self.assertEqual("git-index", self.native_reports(result)[0]["snapshot"]["target"])

    def test_hook06_deleted_reference_fails_then_staged_rename_and_repair_succeed(self):
        self.install(hooks=("pre-commit",))
        path = write_metadata(self.root, metadata(), "# Requirement\n\n[Guide](../guide.md)\n",
                              "stakeholder-requirements/REQ-001.md")
        (self.root / "guide.md").write_bytes(b"# Reference\n")
        self.git("add", "--", ".")
        self.assertEqual(0, self.native_commit().returncode)
        self.git("rm", "--", "guide.md")
        result = self.native_commit()
        self.assertNotEqual(0, result.returncode)
        report = self.native_reports(result)[0]
        finding = next(f for f in report["findings"] if f["code"] == "BROKEN_LINK")
        self.assertEqual("sample/CTX-001/REQ-001", finding["owner"])
        self.assertEqual("../guide.md", finding["target"])
        self.assertEqual(path, Path(finding["path"]))
        self.assertEqual(10, finding["line"])
        self.assertNotIn("artifact-index-", finding["message"])
        path.write_text(path.read_text(encoding="utf-8").replace("../guide.md", "../renamed guide.md"),
                        encoding="utf-8", newline="\n")
        # A link destination containing a space must use the supported angle form.
        path.write_text(path.read_text(encoding="utf-8").replace("(../renamed guide.md)", "(<../renamed guide.md>)"),
                        encoding="utf-8", newline="\n")
        (self.root / "renamed guide.md").write_bytes(b"# Reference\n")
        self.git("add", "--", ".")
        repaired = self.native_commit()
        self.assertEqual(0, repaired.returncode, self.receipts[-1])
        changes = self.native_reports(repaired)[0]["snapshot"]["changes"]
        self.assertIn(("guide.md", "deleted"), {(c["path"], c["status"]) for c in changes})
        self.assertIn(("renamed guide.md", "added"), {(c["path"], c["status"]) for c in changes})

    def test_hook08_native_missing_selected_interpreter_never_falls_back(self):
        # A private venv shares only the existing dependencies; no pip/install.
        environment = self.root / ".venv"
        venv.EnvBuilder(with_pip=False).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        site = environment / ("Lib/site-packages" if os.name == "nt"
                              else f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
        import yaml
        (site / "maintenance.pth").write_text(str(Path(yaml.__file__).parent.parent) + "\n", encoding="utf-8")
        self.install(hooks=("pre-commit",), python=python)
        self.stage_artifact()
        python.rename(python.with_name("unavailable-python"))
        before = self.state()
        result = self.native_commit()
        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"interpreter", result.stderr.lower() + result.stdout.lower())
        self.assertEqual(before["head"], self.state()["head"])

    def test_hook08_native_missing_dependencies_reports_input_error_without_fallback(self):
        environment = self.root / ".venv"
        venv.EnvBuilder(with_pip=False).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        site = environment / ("Lib/site-packages" if os.name == "nt"
                              else f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
        missing = self.installer("--apply", hooks=("pre-commit",), python=python)
        self.assertEqual(2, missing.returncode)
        import yaml
        reference = site / "maintenance.pth"
        reference.write_text(str(Path(yaml.__file__).parent.parent) + "\n", encoding="utf-8")
        self.install(hooks=("pre-commit",), python=python)
        reference.unlink()
        self.stage_artifact()
        result = self.native_commit()
        self.assertNotEqual(0, result.returncode)
        report = self.native_reports(result)[0]
        self.assertEqual(2, report["exit_code"])
        self.assertIn("DEPENDENCY_UNAVAILABLE", self.finding_codes(report))

    def test_hook11_managed_reviewed_by_is_format_only_no_fixup_or_merge_exemptions(self):
        self.install(hooks=("commit-msg",))
        self.stage_artifact()
        for message in ("Managed change", "fixup! managed change", "Merge controlled change",
                        "squash! managed change", "Managed\n\nReviewed-by: TODO",
                        "Managed\n\nReviewed-by: reviewer", "Managed\n\nReviewed-by: <name>"):
            with self.subTest(message=message):
                result = self.native_commit(message)
                self.assertNotEqual(0, result.returncode)
                report = self.native_reports(result)[0]
                self.assertEqual(1, report["exit_code"])
                self.assertFalse(report["policy"]["authenticated"])
                self.assertEqual(self.parent, self.git("rev-parse", "HEAD").strip())
        result = self.native_commit("Managed\n\nreviewed-by: 测试 Reviewer")
        self.assertEqual(0, result.returncode, self.receipts[-1])
        self.assertEqual("Managed\n\nreviewed-by: 测试 Reviewer",
                         self.git("log", "-1", "--format=%B").strip())

    def test_hook11_unmanaged_change_needs_no_review_line_but_deleted_companion_does(self):
        companion = self.root / "verification/VT-001.feature"
        companion.parent.mkdir()
        companion.write_bytes(b"Feature: text companion\n")
        self.git("add", "--", ".")
        self.git("commit", "--quiet", "-m", "Fixture companion before installation")
        self.install(hooks=("commit-msg",))
        (self.root / "source.txt").write_bytes(b"unmanaged\n")
        self.git("add", "--", "source.txt")
        result = self.native_commit("Unmanaged")
        self.assertEqual(0, result.returncode, self.receipts[-1])
        self.assertFalse(self.native_reports(result)[0]["policy"]["required"])
        self.git("rm", "--", "verification/VT-001.feature")
        result = self.native_commit("Delete companion")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(["verification/VT-001.feature"],
                         self.native_reports(result)[0]["policy"]["managed_paths"])

    def test_hook09_launcher_quotes_shell_metacharacters_as_path_bytes(self):
        changed = self.workspace / "本地 ' $; & repo"
        self.root.rename(changed)
        self.root = changed
        self.install()
        self.stage_artifact()
        result = self.native_commit()
        self.assertEqual(0, result.returncode, self.receipts[-1])
        self.assertEqual(str(self.root), self.native_reports(result)[0]["snapshot"]["root"])

    def test_hook12_native_symlink_and_gitlink_are_rejected_without_dereference(self):
        self.install(hooks=("pre-commit",))
        outside = self.workspace / "outside.txt"
        outside.write_bytes(b"must not be read as an artifact\n")
        for mode, blob in (
            ("120000", self.git("hash-object", "-w", "--stdin", input=str(outside).encode()).strip()),
            ("160000", self.parent),
        ):
            with self.subTest(mode=mode):
                self.git("update-index", "--add", "--cacheinfo", mode, blob, "unsafe")
                result = self.native_commit()
                self.assertNotEqual(0, result.returncode)
                report = self.native_reports(result)[0]
                self.assertEqual(2, report["exit_code"])
                self.assertIn("UNSAFE_INDEX_ENTRY", self.finding_codes(report))
                self.assertEqual(self.parent, self.git("rev-parse", "HEAD").strip())
                self.assertEqual(b"must not be read as an artifact\n", outside.read_bytes())
                self.git("update-index", "--force-remove", "--", "unsafe")


class IndexValidationTests(HookFixture):
    def test_i1_optional_message_after_root_and_before_root_have_the_same_contract(self):
        self.stage_artifact()
        message = self.workspace / "提交 message.txt"
        message.write_text("Controlled review text" + REVIEW, encoding="utf-8")
        before = self.state()
        results = []
        for arguments in (
            ["commit-msg", "--root", str(self.root), str(message)],
            ["commit-msg", str(message), "--root", str(self.root)],
        ):
            result = self.call([sys.executable, "-B", "-X", "utf8",
                                str(self.root / ".github/utilities/hook_checks.py"), *arguments])
            self.assertEqual(0, result.returncode, self.receipts[-1])
            results.append(json.loads(result.stdout))
        self.assertEqual(results[0]["policy"], results[1]["policy"])
        self.assertEqual(before, self.state())

    def test_directory_case_aliases_are_rejected_before_snapshot_materialization(self):
        blob = self.git("hash-object", "-w", "--stdin", input=b"case aliases\n").strip()
        self.git("update-index", "--add", "--cacheinfo", "100644", blob, "Alias/a.txt")
        self.git("update-index", "--add", "--cacheinfo", "100644", blob, "alias/b.txt")
        before = self.state()
        result = self.check()
        self.assertEqual(2, result.returncode)
        self.assertIn("UNSAFE_INDEX_ENTRY", self.finding_codes(json.loads(result.stdout)))
        self.assertEqual(before, self.state())

    def test_report_output_is_explicit_new_and_never_overwrites_owner_bytes(self):
        report = self.workspace / "new report.json"
        before = self.state()
        result = self.check("--report", str(report))
        self.assertEqual(0, result.returncode, self.receipts[-1])
        self.assertEqual("empty", json.loads(report.read_text(encoding="utf-8"))["status"])
        raw = report.read_bytes()
        result = self.check("--report", str(report))
        self.assertEqual(2, result.returncode)
        self.assertIn("REPORT_CONFLICT", self.finding_codes(json.loads(result.stdout)))
        self.assertEqual(raw, report.read_bytes())
        self.assertEqual(before, self.state())

    def test_hook07_invalid_explicit_bases_fail_even_when_snapshot_is_empty(self):
        for base in ("main", self.parent[:8], "f" * 40):
            with self.subTest(base=base):
                before = self.state()
                result = self.check("--base", base)
                self.assertEqual(2, result.returncode)
                self.assertTrue(self.finding_codes(json.loads(result.stdout))
                                & {"INVALID_BASE", "BASE_UNAVAILABLE"})
                self.assertEqual(before, self.state())

    def test_hook07_unborn_context_is_explicit_not_failed_base_fallback(self):
        self.git("update-ref", "-d", "HEAD")
        result = self.check()
        self.assertEqual(0, result.returncode, self.receipts[-1])
        payload = json.loads(result.stdout)
        self.assertTrue(payload["snapshot"]["unborn"])
        self.assertIsNone(payload["snapshot"]["parent"])
        self.assertIsNone(payload["snapshot"]["base_sha"])
        invalid = self.check("--base", "f" * 40)
        self.assertEqual(2, invalid.returncode)

    def test_coverage_uses_all_owner_acceptances_not_existing_vt_targets(self):
        write_delivery_fixture(self.root, omit_software_reject=True)
        self.git("add", "--", ".")
        before = self.state()
        result = self.check()
        self.assertEqual(1, result.returncode, self.receipts[-1])
        payload = json.loads(result.stdout)
        self.assertEqual(4, payload["checks"]["coverage"]["acceptance_count"])
        finding = next(f for f in payload["findings"] if f["code"] == "UNCOVERED_ACCEPTANCE")
        self.assertEqual("sample/CTX-001/SR-001#sr-001-ac-02", finding["target"])
        self.assertEqual(before, self.state())

    def test_empty_owner_inventory_does_not_hide_dangling_plan_targets(self):
        write_delivery_fixture(self.root)
        for name in ("stakeholder-requirements/REQ-001.md", "software-requirements/SR-001.md"):
            (self.root / name).unlink()
        self.git("add", "--", ".")
        result = self.check()
        self.assertEqual(1, result.returncode, self.receipts[-1])
        payload = json.loads(result.stdout)
        self.assertEqual(0, payload["checks"]["coverage"]["acceptance_count"])
        self.assertIn("DANGLING_TARGET", self.finding_codes(payload))

    def test_exact_parent_retains_formal_identity_when_staged_metadata_is_removed(self):
        self.stage_artifact(name="domain-model/arbitrary.md")
        self.git("commit", "--quiet", "-m", "Formal identity before installation")
        (self.root / "domain-model/arbitrary.md").write_bytes(b"# Ordinary guide now\n")
        self.git("add", "--", ".")
        result = self.check()
        self.assertEqual(2, result.returncode)
        self.assertIn("MISSING_FRONTMATTER", self.finding_codes(json.loads(result.stdout)))

    def test_ci01_ci03_downstream_only_snapshot_reports_real_empty_valid_invalid_error(self):
        self.assertFalse((self.root / ".github/utilities/tests").exists())
        self.assertFalse((self.root / "docs/research").exists())
        empty = self.check("--base", self.parent)
        self.assertEqual(0, empty.returncode, self.receipts[-1])
        self.assertEqual("empty", json.loads(empty.stdout)["status"])
        path = self.stage_artifact()
        valid = self.check("--base", self.parent)
        self.assertEqual(0, valid.returncode)
        self.assertEqual(1, json.loads(valid.stdout)["checked_count"])
        path.write_bytes(path.read_bytes() + b"\nTODO\n")
        self.git("add", "--", str(path))
        invalid = self.check("--base", self.parent)
        self.assertEqual(1, invalid.returncode)
        path.write_bytes(b"not formal metadata\n")
        self.git("add", "--", str(path))
        error = self.check("--base", self.parent)
        self.assertEqual(2, error.returncode)

    def test_native_partial_commit_honors_git_supplied_alternate_index(self):
        self.install(hooks=("pre-commit",))
        first = self.stage_artifact()
        self.assertEqual(0, self.native_commit().returncode)
        first.write_bytes(b"invalid staged file deliberately excluded from partial commit\n")
        self.git("add", "--", str(first))
        (self.root / "unrelated.txt").write_bytes(b"selected partial commit\n")
        # --only uses Git's actual temporary GIT_INDEX_FILE. No hook bypass.
        self.git("add", "--", "unrelated.txt")
        result = self.native_commit("Partial commit", "--only", "--", "unrelated.txt")
        self.assertEqual(0, result.returncode, self.receipts[-1])
        payload = self.native_reports(result)[0]
        self.assertNotEqual(str(self.root / ".git/index"), payload["snapshot"]["index_path"])
        self.assertEqual("100644", next(e for e in payload["snapshot"]["entries"]
                                      if e["path"].endswith("REQ-001.md"))["mode"])
        self.assertEqual(2, self.check().returncode)

    def test_unmerged_and_intent_to_add_index_inputs_are_explicit_errors(self):
        blob = self.git("hash-object", "-w", "--stdin", input=b"conflict bytes\n").strip()
        self.git("update-index", "--index-info",
                 input=f"100644 {blob} 1\tconflicted.md\n100644 {blob} 2\tconflicted.md\n".encode())
        result = self.check()
        self.assertEqual(2, result.returncode)
        self.assertIn("UNMERGED_INDEX", self.finding_codes(json.loads(result.stdout)))
        self.git("update-index", "--force-remove", "--", "conflicted.md")
        (self.root / "intent.txt").write_bytes(b"not actually staged\n")
        self.git("add", "-N", "--", "intent.txt")
        result = self.check()
        self.assertEqual(2, result.returncode)
        self.assertIn("INTENT_TO_ADD", self.finding_codes(json.loads(result.stdout)))

    def test_hook12_missing_blob_returns_input_error_not_empty_inventory(self):
        self.git("update-index", "--add", "--cacheinfo", "100644", "f" * 40, "missing.md")
        before = self.state()
        result = self.check()
        self.assertEqual(2, result.returncode)
        self.assertIn("INDEX_UNAVAILABLE", self.finding_codes(json.loads(result.stdout)))
        self.assertEqual(before, self.state())


if __name__ == "__main__":
    unittest.main()
