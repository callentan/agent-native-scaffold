"""Task15 fix1: I1/I2/M1 real fixtures; I3 safely intercepted local metadata.

No test invokes Git against an include-bearing fixture or accesses a UNC
endpoint. I3 RED is a pre-invocation refusal failure, not a live network repro.
"""

from __future__ import annotations

import builtins
from contextlib import contextmanager, ExitStack
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import patch

from artifact_io import ArtifactInputError
import check_artifacts
from tests.helpers import WORKTREE, directory_link, git, source_bytes
from tests.test_domain_source import DomainFixture, digest


INCLUDE = b'\n[include]\n\tpath = //never-contact.invalid/share/unapproved.conf\n'


def _network_file(value):
    try:
        text = os.fsdecode(os.fspath(value))
    except TypeError:
        return False  # File descriptors are not filesystem path requests.
    return text.startswith(("//", "\\\\"))


@contextmanager
def blocked_git_and_network_files():
    """Fail BEFORE executing Git or crossing a network filesystem boundary."""
    attempts = []
    original_run = subprocess.run

    def no_git(command, *args, **kwargs):
        if Path(command[0]).name.casefold() in ("git", "git.exe"):
            attempts.append("Git invocation intercepted before execution")
            raise AssertionError("I3 safety tripwire: affected Git must not be invoked")
        return original_run(command, *args, **kwargs)

    with ExitStack() as stack:
        stack.enter_context(patch("subprocess.run", side_effect=no_git))
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                            (os, "stat"), (os, "lstat"), (Path, "resolve")):
            original = getattr(owner, name)

            def local_only(path, *args, _original=original, **kwargs):
                if _network_file(path):
                    attempts.append("Network filesystem request intercepted before access")
                    raise AssertionError("I3 safety tripwire: no UNC access is authorized")
                return _original(path, *args, **kwargs)

            stack.enter_context(patch.object(owner, name, local_only))
        yield attempts


class Fix1Fixture(DomainFixture):
    def owned_modules_staged_deletion(self, relative=".gitmodules"):
        path = self.root / relative
        path.write_bytes(b'# Owner metadata\n[submodule "owner"]\n\tpath = owner-data\n\turl = ../owner-data\n')
        git(self.root, "add", "--", relative)
        git(self.root, "commit", "--quiet", "-m", "Owned native metadata before Task15")
        git(self.root, "rm", "--cached", "--", relative)
        self.assertEqual("", git(self.root, "ls-files", "--stage", "--", relative))
        self.assertTrue(path.is_file())

    def source_arguments(self):
        return ["--root", str(self.root), "--config", "bc-config.yaml", "--source-id", self.declaration["id"],
                "--kind", "git", "--source-root", self.declaration["root"], "--source-path", "domain-model",
                "--baseline", self.version, "--read-only"]

    def changed_config_bytes(self):
        return self.config.read_bytes().replace(b"projectId: owned", b"projectId: owner-B").replace(
            b"id: CTX-001", b"id: CTX-B002"
        )

    def shared_metadata_fixture(self, root):
        """Owned native Gitfile/commondir layout, not an app/real worktree operation."""
        common = self.workspace / (root.name + " common metadata")
        (root / ".git").rename(common)
        selected = common / "worktrees/owned-fixture"
        selected.mkdir(parents=True)
        for name in ("HEAD", "index"):
            if (common / name).exists():
                shutil.copyfile(common / name, selected / name)
        (selected / "commondir").write_bytes(b"../..\n")
        (selected / "gitdir").write_text((root / ".git").as_posix() + "\n", encoding="utf-8")
        (root / ".git").write_text("gitdir: " + selected.as_posix() + "\n", encoding="utf-8")
        return common, selected

    def assert_guarded_inspect(self, source=None):
        before = source_bytes(self.workspace)
        with blocked_git_and_network_files() as attempts:
            result = self.tool().inspect_domain_source(self.root, source or self.declaration)
        self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]), result)
        self.assertIn("GIT_CONFIG_INCLUDES_UNSUPPORTED", self.codes(result))
        self.assertEqual([], result["written"])
        self.assertEqual([], attempts)
        self.assertEqual(before, source_bytes(self.workspace))
        self.assertNotIn("never-contact.invalid", json.dumps(result))
        return result


class IndexIntentFixTests(Fix1Fixture):
    def test_i1_first_new_target_inspect_rejects_head_gitmodules_staged_deletion(self):
        self.owned_modules_staged_deletion()
        result = self.inspect(operation="submodule", target="new domain")
        self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]), result)
        self.assertIn("INDEX_CONFLICT", self.codes(result))
        self.assertFalse((self.root / "new domain").exists())
        self.assertFalse((self.root / ".git/modules").exists())

    def test_i1_index_consent_cannot_reverse_owner_deletion_during_apply(self):
        self.owned_modules_staged_deletion()
        plan = self.inspect(operation="submodule", target="new domain")
        before = self.snapshot()
        result = self.tool().apply_domain_source(
            self.root, self.declaration, operation="submodule", config_path="bc-config.yaml",
            expected=plan["preflight"], owned=True, index_consent=True, target="new domain",
        )
        self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]), result)
        self.assertIn("INDEX_CONFLICT", self.codes(result))
        self.assertEqual([], result["written"])
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / "new domain").exists())

    def test_i1_cli_new_target_does_not_restage_deleted_owner_metadata(self):
        self.owned_modules_staged_deletion()
        before = self.snapshot()
        run, result = self.cli("--operation", "submodule", "--target", "new domain")
        self.assertEqual((1, "conflict"), (run.returncode, result["status"]), result)
        self.assertIn("INDEX_CONFLICT", self.codes(result))
        self.assertEqual(before, self.snapshot())

    def test_i1_head_metadata_case_alias_deletion_is_not_resurrected_as_lowercase(self):
        self.owned_modules_staged_deletion(".GitModules")
        result = self.inspect(operation="submodule", target="new domain")
        self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]), result)
        self.assertIn("INDEX_CONFLICT", self.codes(result))
        self.assertFalse((self.root / "new domain").exists())

    def test_i1_staged_metadata_case_alias_is_not_silently_replaced(self):
        path = self.root / ".GitModules"
        path.write_bytes(b"# Staged owner metadata with case alias\n")
        git(self.root, "add", "--", ".GitModules")
        result = self.inspect(operation="submodule", target="new domain")
        self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]), result)
        self.assertIn("INDEX_CONFLICT", self.codes(result))
        self.assertFalse((self.root / ".git/modules").exists())

    def test_i1_truly_new_untracked_gitmodules_preserves_other_staged_entries(self):
        original = b'# New local owner metadata, never in HEAD\n[submodule "other"]\n\tpath = other\n\turl = ../other\n'
        (self.root / ".gitmodules").write_bytes(original)
        (self.root / "owner staged.txt").write_bytes(b"Unrelated staged owner bytes\n")
        git(self.root, "add", "--", "owner staged.txt")
        staged = git(self.root, "ls-files", "--stage", "--", "owner staged.txt")
        source = source_bytes(self.source)
        result = self.apply(operation="submodule", target="new domain", owned=True, index_consent=True)
        self.assertEqual("materialized", result["outcome"], result)
        self.assertTrue((self.root / ".gitmodules").read_bytes().startswith(original))
        self.assertEqual(staged, git(self.root, "ls-files", "--stage", "--", "owner staged.txt"))
        self.assertEqual(source, source_bytes(self.source))

    def test_i1_genuinely_unborn_parent_can_materialize_new_metadata_without_commit(self):
        root = self.workspace / "unborn BC"
        root.mkdir()
        git(root, "init", "--quiet", "--template=")
        (root / "docs").mkdir()
        (root / "docs/development.md").write_bytes((self.root / "docs/development.md").read_bytes())
        (root / "bc-config.yaml").write_bytes(self.config.read_bytes())
        head = (root / ".git/HEAD").read_bytes()
        plan = self.tool().inspect_domain_source(root, self.declaration, operation="submodule", target="domain")
        self.assertEqual("ready", plan["status"], plan)
        result = self.tool().apply_domain_source(
            root, self.declaration, operation="submodule", config_path="bc-config.yaml",
            expected=plan["preflight"], owned=True, index_consent=True, target="domain",
        )
        self.assertEqual("materialized", result["outcome"], result)
        self.assertEqual(head, (root / ".git/HEAD").read_bytes())
        self.assertEqual("", git(root, "for-each-ref", "--format=%(refname)"))
        self.assertIn("160000 " + self.version, git(root, "ls-files", "--stage", "--", "domain"))


class ConfigSnapshotFixTests(Fix1Fixture):
    def test_i2_project_context_edit_during_inspect_is_input_changed_not_mixed_token(self):
        tool = self.tool()
        acquired = tool._config
        changed = self.changed_config_bytes()
        before = self.snapshot()

        def owner_edit_after_acquisition(*args, **kwargs):
            result = acquired(*args, **kwargs)
            self.config.write_bytes(changed)
            return result

        with patch.object(tool, "_config", side_effect=owner_edit_after_acquisition):
            result = tool.inspect_domain_source(self.root, self.declaration)
        self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]), result)
        self.assertIn("INPUT_CHANGED", self.codes(result))
        self.assertIsNone(result["preflight"])
        self.assertEqual(changed, self.config.read_bytes())
        after = self.snapshot()
        self.assertEqual(before[1], after[1])
        self.assertEqual({k: v for k, v in before[0].items() if k != "bc-config.yaml"},
                         {k: v for k, v in after[0].items() if k != "bc-config.yaml"})

    def test_i2_no_change_path_still_checks_the_exact_parsed_configuration_bytes(self):
        self.write_config([self.declaration])
        tool = self.tool()
        acquired = tool._config
        changed = self.changed_config_bytes()

        def owner_edit(*args, **kwargs):
            result = acquired(*args, **kwargs)
            self.config.write_bytes(changed)
            return result

        with patch.object(tool, "_config", side_effect=owner_edit):
            result = tool.inspect_domain_source(self.root, self.declaration)
        self.assertEqual("conflict", result["status"], result)
        self.assertIn("INPUT_CHANGED", self.codes(result))
        self.assertEqual(changed, self.config.read_bytes())

    def test_i2_a_mixed_inspection_cannot_supply_a_token_for_stable_owner_B_apply(self):
        tool = self.tool()
        acquired = tool._config
        changed = self.changed_config_bytes()

        def owner_edit(*args, **kwargs):
            result = acquired(*args, **kwargs)
            self.config.write_bytes(changed)
            return result

        with patch.object(tool, "_config", side_effect=owner_edit):
            plan = tool.inspect_domain_source(self.root, self.declaration)
        before = self.snapshot()
        result = tool.apply_domain_source(
            self.root, self.declaration, operation="register", config_path="bc-config.yaml",
            expected=plan["preflight"], owned=True,
        )
        self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]), result)
        self.assertIn("PREFLIGHT_REQUIRED", self.codes(result))
        self.assertEqual(changed, self.config.read_bytes())
        self.assertEqual(before, self.snapshot())

    def test_i2_real_cli_controlled_during_acquisition_edit_preserves_B_and_refuses(self):
        changed = self.changed_config_bytes()
        probe = (
            "import sys\nfrom pathlib import Path\n"
            f"sys.path.insert(0, {str(WORKTREE / '.github/utilities')!r})\n"
            "import setup_domain_source as m\n"
            "original=m._config\n"
            f"config=Path({str(self.config)!r})\nchanged=bytes.fromhex({changed.hex()!r})\n"
            "def owner_edit(*args,**kwargs):\n"
            " result=original(*args,**kwargs)\n config.write_bytes(changed)\n return result\n"
            "m._config=owner_edit\nraise SystemExit(m.main(sys.argv[1:]))\n"
        )
        before_source = source_bytes(self.source)
        run = subprocess.run([sys.executable, "-B", "-X", "utf8", "-c", probe, *self.source_arguments()],
                             cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(1, run.returncode, run.stdout + run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual("conflict", result["status"])
        self.assertIn("INPUT_CHANGED", self.codes(result))
        self.assertEqual(changed, self.config.read_bytes())
        self.assertEqual(before_source, source_bytes(self.source))


class WritableOverlapFixTests(Fix1Fixture):
    def test_m1_target_metadata_case_and_descendant_overlap_is_preflight_conflict(self):
        for target in (".gitmodules", ".GitModules", ".gitmodules/checkout", ".GITMODULES/nested"):
            with self.subTest(target=target):
                result = self.inspect(operation="submodule", target=target)
                self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]), result)
                self.assertIn("TARGET_CONFLICT", self.codes(result))
                self.assertEqual([], result["written"])
                self.assertFalse((self.root / ".git/modules").exists())

    def test_m1_apply_impossible_target_never_creates_partial_checkout_or_module(self):
        plan = self.inspect(operation="submodule", target=".gitmodules")
        before = self.snapshot()
        result = self.tool().apply_domain_source(
            self.root, self.declaration, operation="submodule", config_path="bc-config.yaml",
            expected=plan["preflight"], owned=True, index_consent=True, target=".gitmodules",
        )
        self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]), result)
        self.assertIn("TARGET_CONFLICT", self.codes(result))
        self.assertEqual([], result["written"])
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / ".gitmodules").exists())
        self.assertFalse((self.root / ".git/modules").exists())

    def test_m1_real_cli_rejects_metadata_target_before_any_native_setup(self):
        before = self.snapshot()
        run, result = self.cli("--operation", "submodule", "--target", ".gitmodules")
        self.assertEqual((1, "conflict"), (run.returncode, result["status"]), result)
        self.assertIn("TARGET_CONFLICT", self.codes(result))
        self.assertEqual(before, self.snapshot())


class GitConfigBoundaryFixTests(Fix1Fixture):
    def test_i3_source_include_and_conditional_case_variants_refused_before_git(self):
        config = self.source / ".git/config"
        original = config.read_bytes()
        for declaration in (
            INCLUDE,
            b'\n[includeIf "gitdir:**"]\n\tpath = //never-contact.invalid/share/a.conf\n',
            b'\n[InClUdEiF "onbranch:*"]\n\tpath = //never-contact.invalid/share/b.conf\n',
            b'\n[core] [include]\n\tpath = //never-contact.invalid/share/c.conf\n',
        ):
            with self.subTest(declaration=declaration.splitlines()[1]):
                config.write_bytes(original + declaration)
                self.assert_guarded_inspect()
        config.write_bytes(original)

    def test_i3_parent_include_refused_before_parent_git_even_for_content_baseline(self):
        config = self.root / ".git/config"
        config.write_bytes(config.read_bytes() + INCLUDE)
        local = dict(self.declaration, kind="local", path="domain-model/规则.md",
                     baseline=digest((self.source / "domain-model/规则.md").read_bytes()))
        self.assert_guarded_inspect(local)

    def test_i3_local_content_source_metadata_include_is_not_ignored(self):
        config = self.source / ".git/config"
        config.write_bytes(config.read_bytes() + INCLUDE)
        local = dict(self.declaration, kind="local", path="domain-model/规则.md",
                     baseline=digest((self.source / "domain-model/规则.md").read_bytes()))
        self.assert_guarded_inspect(local)

    def test_i3_shared_commit_reader_refuses_includes_before_its_first_git_command(self):
        config = self.source / ".git/config"
        config.write_bytes(config.read_bytes() + INCLUDE)
        before = self.snapshot()
        with blocked_git_and_network_files() as attempts:
            with self.assertRaises(ArtifactInputError) as caught:
                check_artifacts._git(self.source, "rev-parse", "--show-toplevel")
        self.assertEqual("GIT_CONFIG_INCLUDES_UNSUPPORTED", caught.exception.code)
        self.assertEqual([], attempts)
        self.assertEqual(before, self.snapshot())
        self.assertNotIn("never-contact.invalid", str(caught.exception))

    def test_i3_native_parent_config_refused_before_spawn(self):
        config = self.root / ".git/config"
        config.write_bytes(config.read_bytes() + INCLUDE)
        before = self.snapshot()
        with blocked_git_and_network_files() as attempts:
            with self.assertRaises(ArtifactInputError) as caught:
                self.tool()._native(self.root, "rev-parse", "--show-toplevel")
        self.assertEqual("GIT_CONFIG_INCLUDES_UNSUPPORTED", caught.exception.code)
        self.assertEqual([], attempts)
        self.assertEqual(before, self.snapshot())

    def test_i3_native_local_clone_rechecks_source_metadata_before_spawn(self):
        config = self.source / ".git/config"
        config.write_bytes(config.read_bytes() + INCLUDE)
        target = self.root / "never-created"
        before = self.snapshot()
        with blocked_git_and_network_files() as attempts:
            with self.assertRaises(ArtifactInputError) as caught:
                self.tool()._native(
                    self.root, "clone", "--local", "--no-hardlinks", "--no-checkout", "--template=",
                    "--", str(self.source), str(target), local_clone=True,
                )
        self.assertEqual("GIT_CONFIG_INCLUDES_UNSUPPORTED", caught.exception.code)
        self.assertEqual([], attempts)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(target.exists())

    def test_i3_explicit_gitmodules_config_include_never_reaches_git_config(self):
        path = self.root / ".gitmodules"
        path.write_bytes(INCLUDE)
        before = self.snapshot()
        with blocked_git_and_network_files() as attempts:
            with self.assertRaises(ArtifactInputError) as caught:
                self.tool()._module_values(self.root, path)
        self.assertEqual("GIT_CONFIG_INCLUDES_UNSUPPORTED", caught.exception.code)
        self.assertEqual([], attempts)
        self.assertEqual(before, self.snapshot())

    def test_i3_relative_explicit_config_is_guarded_against_its_git_cwd_not_process_cwd(self):
        path = self.root / ".gitmodules"
        path.write_bytes(INCLUDE)
        before = self.snapshot()
        with blocked_git_and_network_files() as attempts:
            with self.assertRaises(ArtifactInputError) as caught:
                self.tool()._native(self.root, "config", "--no-includes", "--file", ".gitmodules", "--list")
        self.assertEqual("GIT_CONFIG_INCLUDES_UNSUPPORTED", caught.exception.code)
        self.assertEqual([], attempts)
        self.assertEqual(before, self.snapshot())

    def test_i3_common_config_include_refused_via_owned_gitfile_commondir(self):
        common, _ = self.shared_metadata_fixture(self.source)
        config = common / "config"
        config.write_bytes(config.read_bytes() + INCLUDE)
        self.assert_guarded_inspect()

    def test_i3_per_worktree_config_include_refused_before_git_or_unc_access(self):
        common, selected = self.shared_metadata_fixture(self.source)
        config = common / "config"
        config.write_bytes(config.read_bytes() + b"\n[extensions]\n\tworktreeConfig = true\n")
        (selected / "config.worktree").write_bytes(INCLUDE)
        self.assert_guarded_inspect()

    def test_i3_network_gitfile_and_commondir_pointers_never_resolve_or_invoke_git(self):
        original_git = self.source / ".git"
        moved = self.workspace / "owned ordinary metadata"
        original_git.rename(moved)
        original_git.write_bytes(b"gitdir: //never-contact.invalid/share/metadata\n")
        before = source_bytes(self.workspace)
        with blocked_git_and_network_files() as attempts:
            result = self.tool().inspect_domain_source(self.root, self.declaration)
        self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]), result)
        self.assertIn("GIT_CONFIG_UNSAFE", self.codes(result))
        self.assertEqual([], attempts)
        self.assertEqual(before, source_bytes(self.workspace))
        original_git.write_text("gitdir: " + moved.as_posix() + "\n", encoding="utf-8")
        (moved / "commondir").write_bytes(b"//never-contact.invalid/share/common\n")
        before = source_bytes(self.workspace)
        with blocked_git_and_network_files() as attempts:
            result = self.tool().inspect_domain_source(self.root, self.declaration)
        self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]), result)
        self.assertIn("GIT_CONFIG_UNSAFE", self.codes(result))
        self.assertEqual([], attempts)
        self.assertEqual(before, source_bytes(self.workspace))

    def test_i3_config_directory_is_refused_as_nonregular_before_git(self):
        config = self.source / ".git/config"
        config.rename(self.source / ".git/config.saved")
        config.mkdir()
        before = self.snapshot()
        with blocked_git_and_network_files() as attempts:
            result = self.tool().inspect_domain_source(self.root, self.declaration)
        self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]), result)
        self.assertIn("GIT_CONFIG_UNSAFE", self.codes(result))
        self.assertEqual([], attempts)
        self.assertEqual(before, self.snapshot())

    def test_i3_incomplete_metadata_cannot_trigger_ancestor_git_discovery(self):
        head = self.source / ".git/HEAD"
        original = head.read_bytes()
        for value in (None, b"not a Git HEAD\n"):
            with self.subTest(value=value):
                if value is None:
                    head.unlink()
                else:
                    head.write_bytes(value)
                before = self.snapshot()
                with blocked_git_and_network_files() as attempts:
                    result = self.tool().inspect_domain_source(self.root, self.declaration)
                self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]), result)
                self.assertTrue(self.codes(result) & {"BASE_UNAVAILABLE", "GIT_CONFIG_UNSAFE"})
                self.assertEqual([], attempts)
                self.assertEqual(before, self.snapshot())
        head.write_bytes(original)

    def test_i3_linked_config_is_refused_without_reading_its_local_target(self):
        config = self.source / ".git/config"
        config.rename(self.source / ".git/config.saved")
        outside = self.workspace / "local config target"
        outside.mkdir()
        (outside / "marker").write_bytes(b"Local guard fixture, not a network endpoint\n")
        with directory_link(config, outside):
            before = source_bytes(self.workspace)
            with blocked_git_and_network_files() as attempts:
                result = self.tool().inspect_domain_source(self.root, self.declaration)
            self.assertEqual("unavailable", result["status"], result)
            self.assertTrue(self.codes(result) & {"GIT_CONFIG_UNSAFE", "UNSAFE_ROOT"})
            self.assertEqual([], attempts)
            self.assertEqual(before, source_bytes(self.workspace))

    def test_i3_real_cli_preinvocation_refusal_does_not_execute_a_network_repro(self):
        config = self.source / ".git/config"
        config.write_bytes(config.read_bytes() + INCLUDE)
        probe = (
            "import sys,subprocess\nfrom pathlib import Path\n"
            f"sys.path.insert(0, {str(WORKTREE / '.github/utilities')!r})\n"
            "import setup_domain_source as m\n"
            "def blocked(*args,**kwargs):\n"
            " raise AssertionError('I3 CLI safety tripwire: no Git invocation authorized')\n"
            "subprocess.run=blocked\nraise SystemExit(m.main(sys.argv[1:]))\n"
        )
        before = self.snapshot()
        run = subprocess.run([sys.executable, "-B", "-X", "utf8", "-c", probe, *self.source_arguments()],
                             cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertTrue(run.stdout.strip(), run.stderr)
        result = json.loads(run.stdout)
        self.assertIn("GIT_CONFIG_INCLUDES_UNSUPPORTED", self.codes(result))
        self.assertNotIn("never-contact.invalid", run.stdout + run.stderr)
        self.assertEqual(before, self.snapshot())

    def test_i3_plain_self_contained_config_comments_and_literal_values_remain_readable(self):
        config = self.source / ".git/config"
        original = config.read_bytes()
        config.write_bytes(original + b'\n# [include] is a comment, not a declaration\n'
                           b'[alias]\n\tnote = "literal [includeIf] text"\n')
        result = self.inspect()
        self.assertEqual("ready", result["status"], result)
        self.assertEqual(self.version, result["location"]["baseline"])

    def test_i3_plain_local_content_source_without_git_metadata_still_registers(self):
        source = self.workspace / "plain local source"
        source.mkdir()
        raw = b"Exact local file bytes\r\n"
        (source / "rule.md").write_bytes(raw)
        selected = dict(self.declaration, kind="local", root="../plain local source",
                        path="rule.md", baseline=digest(raw))
        result = self.inspect(selected)
        self.assertEqual("ready", result["status"], result)
        self.assertEqual("registered", self.apply(selected, owned=True)["outcome"])
        self.assertEqual(raw, (source / "rule.md").read_bytes())

    def test_i3_owned_common_metadata_remains_readable_but_native_shared_setup_is_refused(self):
        self.shared_metadata_fixture(self.source)
        before = source_bytes(self.workspace)
        result = self.tool().inspect_domain_source(self.root, self.declaration)
        self.assertEqual("ready", result["status"], result)
        native = self.tool().inspect_domain_source(self.root, self.declaration,
                                                   operation="submodule", target="domain")
        self.assertEqual("conflict", native["status"], native)
        self.assertIn("SHARED_METADATA", self.codes(native))
        self.assertEqual(before, source_bytes(self.workspace))
