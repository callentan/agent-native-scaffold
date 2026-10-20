"""ENH-11 / UPDATE-01..16: real read-only trees, local objects and CLI proposals."""

from __future__ import annotations

import contextlib
import hashlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

import yaml

from artifact_io import ArtifactInputError
from tests.helpers import WORKTREE, directory_link, git, source_bytes, temporary_workspace


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def content_version(root, selection=None):
    """Independent recipe from the input contract, never the production builder."""
    paths = sorted(selection) if selection is not None else sorted(
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    )
    records = []
    for relative in paths:
        path = root / relative
        if path.is_file():
            raw = path.read_bytes()
            records.append({"path": relative, "sha256": digest(raw), "size": len(raw)})
    return digest(json.dumps({"files": records, "selection": None if selection is None else paths},
                             sort_keys=True, separators=(",", ":")).encode("utf-8"))


class UpdateFixture(unittest.TestCase):
    def setUp(self):
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.base, self.local, self.candidate = (
            self.workspace / name for name in ("old base", "owner 本地", "new candidate")
        )
        for root in (self.base, self.local, self.candidate):
            root.mkdir()

    def tool(self):
        self.assertIsNotNone(importlib.util.find_spec("plan_template_update"),
                             "Task11 read-only planner is not implemented")
        return importlib.import_module("plan_template_update")

    def write(self, root, path, raw):
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        return destination

    def triplet(self, path, base, local, candidate):
        for root, raw in zip((self.base, self.local, self.candidate), (base, local, candidate)):
            if raw is not None:
                self.write(root, path, raw)

    def snapshot(self):
        return tuple(source_bytes(root) for root in (self.base, self.local, self.candidate))

    def plan(self):
        before = self.snapshot()
        result = self.tool().plan_update(self.base, self.local, self.candidate)
        self.assertEqual(before, self.snapshot(), "The API must not change any input byte/file set")
        return result

    def error(self, code, *sources):
        with self.assertRaises(ArtifactInputError) as caught:
            self.tool().plan_update(*(sources or (self.base, self.local, self.candidate)))
        self.assertEqual(code, caught.exception.code, str(caught.exception))
        return caught.exception

    def cli(self, *args):
        script = WORKTREE / ".github/utilities/plan_template_update.py"
        self.assertTrue(script.is_file(), "Task11 CLI is not implemented")
        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(script),
             "--base", str(self.base), "--local", str(self.local),
             "--candidate", str(self.candidate), *map(str, args)],
            cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertTrue(run.stdout.strip(), "The real CLI must return a proposal or input-error")
        return run

    def assert_item(self, item, action, reason, states, paths=None):
        self.assertTrue(hasattr(item, "action"), "Every item needs its operation and source identities")
        self.assertEqual(action, item.action)
        self.assertEqual(reason, item.reason)
        for role, state, path in zip(("base", "local", "candidate"), states,
                                     paths or (item.path,) * 3):
            identity = getattr(item, role)
            self.assertEqual(path, identity.path)
            self.assertEqual(role, identity.source)
            self.assertEqual(None if state is None else digest(state), identity.sha256)
            self.assertEqual(None if state is None else len(state), identity.size)
            self.assertTrue(identity.version, "Even absence belongs to an identified source")


class ThreeWayTests(UpdateFixture):
    def test_update_01_identical_bytes_are_preserved(self):
        self.triplet("AGENTS.md", b"old\n", b"old\n", b"old\n")
        result = self.plan()
        self.assertEqual("no-change", result.status)
        self.assertEqual((), result.changes)
        self.assertEqual((), result.conflicts)
        self.assertEqual(["AGENTS.md"], [item.path for item in result.preserved])
        self.assert_item(result.preserved[0], "preserve", "UNCHANGED", (b"old\n",) * 3)

    def test_update_02_local_edit_is_not_reset_to_old_candidate(self):
        self.triplet("rules.md", b"old", b"owner", b"old")
        result = self.plan()
        self.assertEqual("no-change", result.status)
        self.assertEqual(1, len(result.preserved))
        self.assert_item(result.preserved[0], "preserve", "LOCAL_MODIFIED",
                         (b"old", b"owner", b"old"))

    def test_update_03_candidate_change_is_only_a_proposal(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        result = self.plan()
        self.assertEqual("proposed", result.status)
        self.assertEqual((), result.conflicts)
        self.assert_item(result.changes[0], "modify", "CANDIDATE_MODIFIED",
                         (b"old", b"old", b"new"))
        sources = {source.role: source for source in result.sources}
        self.assertEqual({"base", "local", "candidate"}, set(sources))
        for role in sources:
            self.assertEqual(sources[role].version, getattr(result.changes[0], role).version)

    def test_update_04_equal_edits_are_aligned_not_proposed_again(self):
        self.triplet("rules.md", b"old", b"new", b"new")
        result = self.plan()
        self.assertEqual("no-change", result.status)
        self.assertEqual(1, len(result.preserved))
        self.assert_item(result.preserved[0], "preserve", "ALREADY_ALIGNED",
                         (b"old", b"new", b"new"))

    def test_update_05_different_edits_are_conflict_not_skipped_success(self):
        self.triplet("AGENTS.md", b"base rule\n", b"owner rule\n", b"new template rule\n")
        result = self.plan()
        self.assertEqual(["AGENTS.md"], [item.path for item in result.conflicts])
        self.assertEqual((), result.changes)
        self.assertEqual("conflict", result.status)
        self.assert_item(result.conflicts[0], "conflict", "BOTH_MODIFIED",
                         (b"base rule\n", b"owner rule\n", b"new template rule\n"))

    def test_update_06_candidate_deletion_is_proposed_not_applied(self):
        self.triplet("obsolete.md", b"old", b"old", None)
        result = self.plan()
        self.assertEqual(1, len(result.changes))
        self.assert_item(result.changes[0], "delete", "CANDIDATE_DELETED",
                         (b"old", b"old", None))

    def test_update_07_candidate_deletion_conflicts_with_owner_edit(self):
        self.triplet("rules.md", b"old", b"owner", None)
        result = self.plan()
        self.assertEqual(1, len(result.conflicts))
        self.assert_item(result.conflicts[0], "conflict", "DELETE_MODIFY",
                         (b"old", b"owner", None))

    def test_update_08_owner_deletion_is_intentional_not_resurrected(self):
        self.triplet("removed.md", b"old", None, b"old")
        result = self.plan()
        self.assertEqual("no-change", result.status)
        self.assertEqual(1, len(result.preserved))
        self.assert_item(result.preserved[0], "preserve", "LOCAL_DELETED", (b"old", None, b"old"))

    def test_update_09_candidate_modification_conflicts_with_owner_deletion(self):
        self.triplet("rules.md", b"old", None, b"new")
        result = self.plan()
        self.assertEqual(1, len(result.conflicts))
        self.assert_item(result.conflicts[0], "conflict", "MODIFY_DELETE", (b"old", None, b"new"))

    def test_update_10_candidate_addition_does_not_create_owner_file(self):
        self.triplet("new.md", None, None, b"new")
        result = self.plan()
        self.assertEqual(1, len(result.changes))
        self.assert_item(result.changes[0], "add", "CANDIDATE_ADDED", (None, None, b"new"))

    def test_update_11_add_add_conflict_retains_both_identities(self):
        self.triplet("rules.md", None, b"owner", b"new")
        result = self.plan()
        self.assertEqual(1, len(result.conflicts))
        self.assert_item(result.conflicts[0], "conflict", "ADD_ADD", (None, b"owner", b"new"))

    def test_update_12_owner_only_business_data_is_preserved(self):
        self.triplet("business/native layout.json", None, b'{"owner": true}', None)
        result = self.plan()
        self.assertEqual("no-change", result.status)
        self.assertEqual(1, len(result.preserved))
        self.assert_item(result.preserved[0], "preserve", "LOCAL_ONLY",
                         (None, b'{"owner": true}', None))

    def test_equal_additions_and_both_deletions_remain_explicitly_preserved(self):
        self.triplet("added.md", None, b"new", b"new")
        self.triplet("removed.md", b"old", None, None)
        result = self.plan()
        self.assertEqual(["added.md", "removed.md"], [item.path for item in result.preserved])
        self.assert_item(result.preserved[0], "preserve", "SAME_ADDITION", (None, b"new", b"new"))
        self.assert_item(result.preserved[1], "preserve", "BOTH_DELETED", (b"old", None, None))

    def test_update_14_raw_binary_bom_newline_unicode_and_stable_order(self):
        cases = [
            ("资料/中文 路径.md", b"line\n", b"line\r\n", b"line\n", "LOCAL_MODIFIED"),
            ("z.bin", b"\x00\xff\x01", b"\x00\xff\x01", b"\x00\xfe\x01", "CANDIDATE_MODIFIED"),
            ("BOM.md", b"text", b"\xef\xbb\xbftext", b"text", "LOCAL_MODIFIED"),
            ("a.txt", b"old", b"old", b"new", "CANDIDATE_MODIFIED"),
        ]
        for path, old, owner, new, _ in cases:
            self.triplet(path, old, owner, new)
        first, second = self.plan(), self.plan()
        self.assertTrue(hasattr(first, "to_dict"), "The plan needs a deterministic JSON contract")
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(["a.txt", "z.bin"], [item.path for item in first.changes])
        self.assertEqual(["BOM.md", "资料/中文 路径.md"], [item.path for item in first.preserved])
        actual = {item.path: item for item in (*first.changes, *first.preserved)}
        for path, old, owner, new, reason in cases:
            self.assert_item(actual[path], "preserve" if reason == "LOCAL_MODIFIED" else "modify",
                             reason, (old, owner, new))
        self.assertNotIn("line", json.dumps(first.to_dict()), "Do not expose source contents")


class SourceBoundaryTests(UpdateFixture):
    def test_update_13_missing_base_is_error_not_empty_ancestor(self):
        self.triplet("rules.md", b"old", b"owner", b"new")
        (self.base / "rules.md").unlink()
        self.base.rmdir()
        before = self.snapshot()
        self.error("INVALID_ROOT")
        self.assertEqual(before, self.snapshot())

    def test_missing_local_or_candidate_is_not_absence_of_all_files(self):
        for root in (self.local, self.candidate):
            with self.subTest(role=root.name):
                root.rmdir()
                self.error("INVALID_ROOT")
                root.mkdir()

    def test_unusable_and_network_roots_are_rejected(self):
        wrong = self.write(self.workspace, "not a directory", b"owner")
        for root in (wrong, "", None, "//server/share", r"\\server\share",
                     "https://example.invalid/source", "C:relative"):
            with self.subTest(root=root):
                self.error("INVALID_ROOT", root, self.local, self.candidate)
        self.assertEqual(b"owner", wrong.read_bytes())

    def test_overlapping_roots_are_not_a_coherent_three_way_input(self):
        nested = self.base / "nested"
        nested.mkdir()
        self.error("OVERLAPPING_ROOTS", self.base, self.base, self.candidate)
        self.error("OVERLAPPING_ROOTS", self.base, nested, self.candidate)

    def test_update_15_exclusions_are_root_relative_not_venv_ancestor_based(self):
        self.triplet(".github/skills/real/SKILL.md", b"old", b"old", b"new")
        self.triplet("_templates/items/form.md", b"old", b"old", b"new")
        for relative in (".git/config", ".venv/a.bin", "node_modules/a", "__pycache__/a.pyc",
                         "tests/a.txt", "fixtures/source.txt", ".pytest_cache/state"):
            self.triplet(relative, b"old", b"owner", b"new")
        result = self.plan()
        self.assertEqual([".github/skills/real/SKILL.md", "_templates/items/form.md"],
                         [item.path for item in result.changes])
        for source in result.sources:
            self.assertEqual({".git/", ".venv/", "node_modules/", "__pycache__/",
                              "tests/", "fixtures/", ".pytest_cache/"},
                             {entry.path for entry in source.excluded})

    def test_update_15_directory_links_are_not_followed_even_inside_root(self):
        target = self.workspace / "not an input"
        target.mkdir()
        self.write(target, "sensitive.txt", b"PRIVATE MUST NOT APPEAR")
        before = source_bytes(target)
        for destination in (target, self.local):
            with self.subTest(destination=destination.name):
                with directory_link(self.candidate / "alias", destination):
                    self.error("UNSAFE_PATH")
        self.assertEqual(before, source_bytes(target))

    def test_unreadable_directory_is_not_reported_as_an_empty_tree(self):
        scandir = os.scandir
        def refuse(directory):
            if Path(directory) == self.base:
                raise PermissionError("injected directory read refusal")
            return scandir(directory)
        with patch("os.scandir", side_effect=refuse):
            self.error("DIRECTORY_READ_ERROR")

    def test_unreadable_file_is_not_a_deletion(self):
        path = self.write(self.base, "rules.md", b"old")
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.CreateFileW.argtypes = (
                wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
            )
            kernel.CreateFileW.restype = wintypes.HANDLE
            kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
            handle = kernel.CreateFileW(str(path), 0x80000000, 0, None, 3, 0x80, None)
            self.assertNotEqual(ctypes.c_void_p(-1).value, handle)
            try:
                self.error("FILE_READ_ERROR")
            finally:
                kernel.CloseHandle(handle)
        else:
            path.chmod(0)
            try:
                if os.access(path, os.R_OK):
                    self.skipTest("Host privilege bypasses the real unreadable-file fixture")
                self.error("FILE_READ_ERROR")
            finally:
                path.chmod(0o600)



class SingleCliTests(UpdateFixture):
    def test_real_cli_proposal_nochange_and_conflict_exit_codes_keep_source_bytes(self):
        for owner, new, status, exit_code in (
            (b"old", b"old", "no-change", 0),
            (b"old", b"new", "proposed", 0),
            (b"owner", b"new", "conflict", 1),
        ):
            with self.subTest(status=status):
                self.triplet("rules.md", b"old", owner, new)
                before = self.snapshot()
                run = self.cli()
                self.assertEqual(exit_code, run.returncode, run.stderr + run.stdout)
                data = json.loads(run.stdout)
                self.assertEqual(status, data["status"])
                self.assertEqual(before, self.snapshot())
                self.assertEqual("", run.stderr)

    def test_missing_base_cli_exits_two_and_does_not_create_explicit_output(self):
        self.base.rmdir()
        output = self.workspace / "error proposal.json"
        run = self.cli("--output", output)
        self.assertEqual(2, run.returncode, run.stderr + run.stdout)
        data = json.loads(run.stdout)
        self.assertEqual("input-error", data["status"])
        self.assertEqual("INVALID_ROOT", data["findings"][0]["code"])
        self.assertFalse(output.exists())

    def test_update_16_explicit_new_output_is_separate_and_never_replaces_history(self):
        self.triplet("rules.md", b"old", b"owner", b"new")
        before = self.snapshot()
        output = self.workspace / "提案 with spaces.json"
        run = self.cli("--output", output)
        self.assertEqual(1, run.returncode, run.stderr + run.stdout)
        self.assertEqual(json.loads(run.stdout), json.loads(output.read_bytes()))
        saved = output.read_bytes()
        rejected = self.cli("--output", output)
        self.assertEqual(2, rejected.returncode)
        self.assertEqual("REPORT_CONFLICT", json.loads(rejected.stdout)["findings"][0]["code"])
        self.assertEqual(saved, output.read_bytes())
        self.assertEqual(before, self.snapshot())

    def test_new_output_in_any_input_or_git_cache_subtree_is_refused(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        for root in (self.base, self.local, self.candidate):
            for relative in ("proposal.json", ".git/proposal.json"):
                with self.subTest(root=root.name, relative=relative):
                    (root / ".git").mkdir(exist_ok=True)
                    before = self.snapshot()
                    run = self.cli("--output", root / relative)
                    self.assertEqual(2, run.returncode, run.stderr + run.stdout)
                    self.assertEqual("REPORT_CONFLICT", json.loads(run.stdout)["findings"][0]["code"])
                    self.assertEqual(before, self.snapshot())

    def test_output_alias_and_missing_parent_are_refused_without_creating_directories(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        with directory_link(self.workspace / "alias", self.local):
            run = self.cli("--output", self.workspace / "alias/new.json")
            self.assertEqual(2, run.returncode, run.stderr + run.stdout)
            self.assertEqual("REPORT_CONFLICT", json.loads(run.stdout)["findings"][0]["code"])
        missing = self.workspace / "not created/new.json"
        run = self.cli("--output", missing)
        self.assertEqual(2, run.returncode, run.stderr + run.stdout)
        self.assertFalse(missing.parent.exists())

    def test_input_error_and_output_errors_never_expose_source_contents(self):
        self.triplet("rules.md", b"PRIVATE OLD", b"PRIVATE OWNER", b"PRIVATE CANDIDATE")
        for output in ("https://example.invalid/report.json", r"\\server\share\new.json", "wrong.txt"):
            run = self.cli("--output", output)
            self.assertEqual(2, run.returncode, run.stderr + run.stdout)
            self.assertNotIn("PRIVATE", run.stdout + run.stderr)
            self.assertEqual("input-error", json.loads(run.stdout)["status"])

    def test_no_apply_or_remote_operation_flag_is_accepted(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        before = self.snapshot()
        script = WORKTREE / ".github/utilities/plan_template_update.py"
        for flag in ("--apply", "--push", "--clone", "--commit", "--pr"):
            run = subprocess.run(
                [sys.executable, "-B", "-X", "utf8", str(script), "--base", str(self.base),
                 "--local", str(self.local), "--candidate", str(self.candidate), flag],
                cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(2, run.returncode, run.stdout + run.stderr)
            self.assertEqual(before, self.snapshot())

    def test_rejected_uri_diagnostics_do_not_echo_untrusted_values(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        before = self.snapshot()
        marker = "OWNED_TEST_MARKER_NOT_A_CREDENTIAL"
        for flag, value in (
            ("--base", "https://" + marker + "@example.invalid/source"),
            ("--base", "//server/" + marker),
            ("--output", "https://" + marker + "@example.invalid/report.json"),
            ("--output", "//server/" + marker + "/report.json"),
        ):
            with self.subTest(flag=flag):
                run = self.cli(flag, value)
                self.assertEqual(2, run.returncode, run.stderr + run.stdout)
                self.assertNotIn(marker, run.stdout + run.stderr)
                self.assertEqual("input-error", json.loads(run.stdout)["status"])
                self.assertEqual(before, self.snapshot())


class VersionScopeTests(UpdateFixture):
    def source(self, root, version=None, files=None):
        module = self.tool()
        self.assertTrue(hasattr(module, "TreeSource"), "Explicit versions/file scopes need a narrow input record")
        return module.TreeSource(root, version, files)

    def test_update_13_supplied_content_version_is_verified_not_just_reported(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        sources = [self.source(root, content_version(root))
                   for root in (self.base, self.local, self.candidate)]
        before = self.snapshot()
        plan = self.tool().plan_update(*sources)
        self.assertEqual("proposed", plan.status)
        self.assertEqual([content_version(root) for root in (self.base, self.local, self.candidate)],
                         [identity.version for identity in plan.sources])
        wrong = self.source(self.base, "sha256:" + "0" * 64)
        self.error("BASE_MISMATCH", wrong, sources[1], sources[2])
        self.assertEqual(before, self.snapshot())

    def test_invalid_version_labels_never_fall_back_to_head_or_content(self):
        for version in ("HEAD", "main", "", "a" * 7, "sha256:abc", "x" * 40, True, 1):
            with self.subTest(version=version):
                self.error("INVALID_BASE", self.source(self.base, version), self.local, self.candidate)

    def test_exact_real_git_commits_and_raw_blobs_are_checked_without_filters(self):
        self.triplet("rules.md", b"line\n", b"line\n", b"candidate\n")
        commits = []
        for root in (self.base, self.local, self.candidate):
            git(root, "init", "--quiet", "--template=")
            git(root, "add", "--", "rules.md")
            git(root, "commit", "--quiet", "-m", "Exact local source")
            commits.append(git(root, "rev-parse", "HEAD"))
        before = self.snapshot()
        sources = [self.source(root, commit)
                   for root, commit in zip((self.base, self.local, self.candidate), commits)]
        result = self.tool().plan_update(*sources)
        self.assertEqual("proposed", result.status)
        self.assertEqual(commits, [identity.version for identity in result.sources])
        self.assertEqual(before, self.snapshot(), "Git reads must not refresh index/config/logs")
        (self.local / "rules.md").write_bytes(b"line\r\n")
        before = self.snapshot()
        self.error("BASE_MISMATCH", *sources)
        self.assertEqual(before, self.snapshot())
        tree = git(self.base, "rev-parse", "HEAD^{tree}")
        self.error("BASE_UNAVAILABLE", self.source(self.base, tree), self.local, self.candidate)
        self.error("BASE_UNAVAILABLE", self.source(self.base, "f" * 40), self.local, self.candidate)

    def test_git_version_does_not_ignore_extra_or_missing_in_scope_files(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        git(self.base, "init", "--quiet", "--template=")
        git(self.base, "add", "--", ".")
        git(self.base, "commit", "--quiet", "-m", "Exact file set")
        commit = git(self.base, "rev-parse", "HEAD")
        fixed = self.source(self.base, commit)
        self.write(self.base, "extra.txt", b"not in supplied commit")
        self.error("BASE_MISMATCH", fixed, self.local, self.candidate)
        (self.base / "extra.txt").unlink()
        (self.base / "rules.md").unlink()
        self.error("BASE_MISMATCH", fixed, self.local, self.candidate)

    def test_explicit_file_selection_has_its_own_verified_identity_and_no_fanout(self):
        self.triplet("verification/only.feature", b"old", b"old", b"new")
        self.triplet("model.yaml", b"old model", b"owner model", b"new model")
        self.write(self.local, "business/private.txt", b"OWNER DATA NOT SELECTED")
        files = ("verification/only.feature",)
        sources = [self.source(root, content_version(root, files), files)
                   for root in (self.base, self.local, self.candidate)]
        before = self.snapshot()
        result = self.tool().plan_update(*sources)
        self.assertEqual(["verification/only.feature"], [item.path for item in result.changes])
        self.assertEqual((), result.conflicts)
        self.assertEqual((), result.preserved)
        self.assertEqual(files, result.sources[0].selection)
        self.assertEqual(before, self.snapshot())
        self.assertNotIn("private.txt", json.dumps(result.to_dict()))
        self.error("BASE_MISMATCH", self.source(self.base, content_version(self.base), files),
                   sources[1], sources[2])

    def test_unsafe_duplicate_excluded_or_mismatched_file_scopes_are_rejected(self):
        for files in ((), "rules.md", ("../escape",), ("/absolute",), ("C:/absolute",),
                      (r"a\b",), ("a//b",), ("./a",), (".git/config",),
                      ("tests/data.feature",), ("a", "a"), ("a", "A")):
            with self.subTest(files=files):
                self.error("INVALID_SCOPE", self.source(self.base, files=files),
                           self.source(self.local, files=files), self.source(self.candidate, files=files))
        self.error("INVALID_SCOPE", self.source(self.base, files=("a.feature",)),
                   self.source(self.local, files=("b.feature",)), self.candidate)

    def test_file_directory_and_case_collisions_stop_instead_of_proposing_owner_overwrite(self):
        self.write(self.local, "settings/owner.md", b"owner business")
        self.write(self.candidate, "settings", b"candidate regular file")
        before = self.snapshot()
        self.error("PATH_TYPE_CONFLICT")
        self.assertEqual(before, self.snapshot())
        (self.candidate / "settings").unlink()
        self.write(self.base, "Same.txt", b"old")
        self.write(self.candidate, "same.txt", b"new")
        self.error("PATH_COLLISION")

    def test_cli_versions_must_match_actual_selected_inputs(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        run = self.cli("--base-version", content_version(self.base),
                       "--local-version", content_version(self.local),
                       "--candidate-version", content_version(self.candidate))
        self.assertEqual(0, run.returncode, run.stderr + run.stdout)
        data = json.loads(run.stdout)
        self.assertEqual("proposed", data["status"])
        wrong = self.cli("--base-version", "sha256:" + "0" * 64)
        self.assertEqual(2, wrong.returncode, wrong.stderr + wrong.stdout)
        self.assertEqual("BASE_MISMATCH", json.loads(wrong.stdout)["findings"][0]["code"])

    def test_selected_file_disappearing_after_stat_is_read_error_not_verified_absence(self):
        self.triplet("rules.md", b"old", b"old", b"new")
        sources = [self.source(root, files=("rules.md",))
                   for root in (self.base, self.local, self.candidate)]
        original_read = Path.read_bytes
        path = self.base / "rules.md"
        def disappear(actual):
            if actual == path:
                actual.unlink()  # Real disappearance between lstat and opening.
            return original_read(actual)
        with patch.object(Path, "read_bytes", disappear):
            self.error("FILE_READ_ERROR", *sources)
        self.assertEqual(b"old", (self.local / "rules.md").read_bytes())


class BatchProposalTests(UpdateFixture):
    def setUp(self):
        super().setUp()
        self.source_file = "scenarios/接收 场景.feature"
        self.target_file = "verification/incoming.feature"
        self.old = b"Feature: decision\n  Scenario: accept old\n"
        self.new = b"Feature: decision\n  Scenario: accept candidate\n"
        self.owner = b"Feature: decision\n  Scenario: owner-specific rule\n"
        self.triplet(self.source_file, self.old, self.old, self.new)
        self.triplet("model.yaml", b"old model", b"PRIVATE MODEL", b"unselected new model")
        self.targets = {}
        entries = []
        for name, raw in (("aligned", self.new), ("clean", self.old),
                          ("conflict", self.owner), ("missing", None)):
            root = self.workspace / ("BC " + name)
            self.targets[name] = root
            if name != "missing":
                root.mkdir()
                self.write(root, self.target_file, raw)
                self.write(root, "business/owner.md", b"PRIVATE BUSINESS NOT COPIED")
            entries.append({
                "id": name, "repository": "sample/bc-" + name, "scope": "sample/CTX-" + name,
                "local": {"root": root.name, "version": content_version(root, (self.target_file,))},
                "files": [{"source": self.source_file, "path": self.target_file}],
            })
        self.registration = self.workspace / "targets 选择.yaml"
        self.data = {
            "schemaVersion": 1,
            "source": {
                "repository": "sample/domain",
                "base": {"root": self.base.name, "version": content_version(self.base, (self.source_file,))},
                "candidate": {"root": self.candidate.name, "version": content_version(self.candidate, (self.source_file,))},
                "files": [{"scenario": "sample/CTX-domain/TS-001#accept", "path": self.source_file}],
            },
            "targets": entries,
        }
        self.save_registration()

    def save_registration(self):
        self.registration.write_text(yaml.safe_dump(self.data, allow_unicode=True, sort_keys=False),
                                     encoding="utf-8", newline="\n")

    def batch(self, ids=("aligned", "clean", "conflict", "missing", "unregistered")):
        module = self.tool()
        self.assertTrue(hasattr(module, "plan_batch"), "Task11 explicit multi-target proposals are not implemented")
        before = source_bytes(self.workspace)
        result = module.plan_batch(self.registration, ids)
        self.assertEqual(before, source_bytes(self.workspace), "Batch API must not write any target or input")
        return result

    def batch_error(self, code, ids=("clean",)):
        module = self.tool()
        self.assertTrue(hasattr(module, "plan_batch"), "Task11 registration reader is not implemented")
        before = source_bytes(self.workspace)
        with self.assertRaises(ArtifactInputError) as caught:
            module.plan_batch(self.registration, ids)
        self.assertEqual(code, caught.exception.code, str(caught.exception))
        self.assertEqual(before, source_bytes(self.workspace))

    def batch_cli(self, ids=("clean",), *args):
        script = WORKTREE / ".github/utilities/plan_template_update.py"
        argv = [sys.executable, "-B", "-X", "utf8", str(script), "--registration", str(self.registration)]
        for name in ids:
            argv.extend(("--target", name))
        return subprocess.run([*argv, *map(str, args)], cwd=self.workspace, shell=False,
                              capture_output=True, text=True, encoding="utf-8")

    def test_mixed_batch_preserves_five_independent_outcomes_and_mapped_source_identities(self):
        result = self.batch()
        self.assertEqual("input-error", result.status)
        self.assertEqual("sample/domain", result.source_repository)
        actual = {target.id: target for target in result.targets}
        self.assertEqual(["aligned", "clean", "conflict", "missing", "unregistered"],
                         [target.id for target in result.targets])
        self.assertEqual({"aligned": "no-change", "clean": "proposed", "conflict": "conflict",
                          "missing": "unavailable", "unregistered": "unavailable"},
                         {key: value.status for key, value in actual.items()})
        self.assertEqual("sample/CTX-clean", actual["clean"].scope)
        self.assertEqual("sample/bc-clean", actual["clean"].repository)
        item = actual["clean"].plan.changes[0]
        self.assertEqual(self.target_file, item.path)
        self.assert_item(item, "modify", "CANDIDATE_MODIFIED", (self.old, self.old, self.new),
                         (self.source_file, self.target_file, self.source_file))
        mapping = actual["clean"].mappings[0]
        self.assertEqual(("sample/CTX-domain/TS-001#accept", self.source_file, self.target_file),
                         (mapping.scenario, mapping.source, mapping.target))
        self.assertEqual("BOTH_MODIFIED", actual["conflict"].plan.conflicts[0].reason)
        self.assertIsNone(actual["missing"].plan)
        self.assertEqual("INVALID_ROOT", actual["missing"].findings[0].code)
        self.assertIsNone(actual["unregistered"].repository)
        self.assertIsNone(actual["unregistered"].scope)
        self.assertEqual("UNKNOWN_TARGET", actual["unregistered"].findings[0].code)
        text = json.dumps(result.to_dict())
        self.assertNotIn("model.yaml", text)
        self.assertNotIn("PRIVATE", text)
        self.assertNotIn(str(self.workspace), text, "Registration-root-relative references must stay portable")

    def test_batch_cli_propagates_zero_one_two_and_retains_each_target_on_stdout(self):
        for ids, status, code in (
            (("aligned",), "no-change", 0), (("clean",), "proposed", 0),
            (("conflict",), "conflict", 1), (("missing",), "input-error", 2),
            (("clean", "conflict", "missing", "unregistered"), "input-error", 2),
        ):
            with self.subTest(ids=ids):
                before = source_bytes(self.workspace)
                run = self.batch_cli(ids)
                self.assertEqual(code, run.returncode, run.stderr + run.stdout)
                self.assertTrue(run.stdout.strip(), "Per-target failures must remain in stdout JSON")
                data = json.loads(run.stdout)
                self.assertEqual(status, data["status"])
                self.assertEqual(sorted(ids), [target["id"] for target in data["targets"]])
                self.assertEqual(before, source_bytes(self.workspace))
                self.assertEqual("", run.stderr)

    def test_target_selection_is_explicit_nonempty_unique_and_not_a_default_all(self):
        for ids in ((), [], "clean", None, ("clean", "clean"), ("not a target",)):
            with self.subTest(ids=ids):
                self.batch_error("INVALID_TARGETS", ids)
        run = self.batch_cli(())
        self.assertEqual(2, run.returncode, run.stderr + run.stdout)

    def test_missing_target_registration_fields_are_unavailable_not_guessed(self):
        original = json.loads(json.dumps(self.data))
        for field in ("repository", "scope", "files", "root", "version"):
            with self.subTest(field=field):
                self.data = json.loads(json.dumps(original))
                target = self.data["targets"][0]
                del (target["local"] if field in ("root", "version") else target)[field]
                self.save_registration()
                result = self.batch(("aligned", "clean"))
                self.assertEqual("input-error", result.status)
                actual = {target.id: target for target in result.targets}
                self.assertEqual("unavailable", actual["aligned"].status)
                self.assertEqual("INVALID_TARGET_REGISTRATION", actual["aligned"].findings[0].code)
                self.assertEqual("proposed", actual["clean"].status)

    def test_unregistered_file_or_nonfeature_fanout_is_refused_for_that_target(self):
        self.data["targets"][0]["files"][0]["source"] = "model.yaml"
        self.save_registration()
        result = self.batch(("aligned", "clean"))
        actual = {target.id: target for target in result.targets}
        self.assertEqual("TARGET_FILE_NOT_ALLOWED", actual["aligned"].findings[0].code)
        self.assertEqual("proposed", actual["clean"].status)
        self.data["source"]["files"][0]["path"] = "model.yaml"
        self.save_registration()
        self.batch_error("INVALID_REGISTRATION")

    def test_safe_yaml_rejects_duplicate_recursive_and_object_construction_inputs(self):
        original = self.registration.read_bytes()
        for text, code in (
            ("schemaVersion: 1\nschemaVersion: 1\n", "DUPLICATE_YAML_KEY"),
            ("source:\n  base:\n    root: a\n    root: b\n", "DUPLICATE_YAML_KEY"),
            ("source: &loop\n  root: *loop\n", "INVALID_YAML"),
            ("source: !!python/object/apply:builtins.print [MUST_NOT_EXECUTE]\n", "INVALID_YAML"),
            ("source: &a {base: one}\nother: {<<: *a, base: two}\n", "DUPLICATE_YAML_KEY"),
        ):
            with self.subTest(code=code):
                self.registration.write_text(text, encoding="utf-8")
                self.batch_error(code)
        self.registration.write_bytes(original)

    def test_registration_rejects_unknown_execution_fields_versions_and_duplicate_identities(self):
        original = json.loads(json.dumps(self.data))
        mutations = (
            lambda d: d.update(apply=True),
            lambda d: d.update(schemaVersion=True),
            lambda d: d["source"].update(command="must-not-execute"),
            lambda d: d["source"]["base"].update(version="HEAD"),
            lambda d: d["source"]["base"].update(root="https://example.invalid/source"),
            lambda d: d["source"]["files"].append(dict(d["source"]["files"][0])),
            lambda d: d["targets"].append(dict(d["targets"][0])),
        )
        for mutate in mutations:
            self.data = json.loads(json.dumps(original))
            mutate(self.data)
            self.save_registration()
            self.batch_error("INVALID_REGISTRATION")

    def test_missing_source_base_and_wrong_source_version_do_not_create_empty_success(self):
        original_root = self.data["source"]["base"]["root"]
        self.data["source"]["base"]["root"] = "unavailable old source"
        self.save_registration()
        result = self.batch(("aligned", "clean"))
        self.assertEqual(["unavailable", "unavailable"], [target.status for target in result.targets])
        self.assertEqual(["INVALID_ROOT", "INVALID_ROOT"], [target.findings[0].code for target in result.targets])
        self.data["source"]["base"]["root"] = original_root
        self.data["source"]["base"]["version"] = "sha256:" + "0" * 64
        self.save_registration()
        result = self.batch(("aligned", "clean"))
        self.assertEqual(["BASE_MISMATCH", "BASE_MISMATCH"], [target.findings[0].code for target in result.targets])

    def test_target_wrong_version_and_unreadable_root_do_not_erase_other_proposals(self):
        self.data["targets"][0]["local"]["version"] = "sha256:" + "0" * 64
        self.save_registration()
        result = self.batch(("aligned", "clean"))
        self.assertEqual("BASE_MISMATCH", result.targets[0].findings[0].code)
        self.assertEqual("proposed", result.targets[1].status)
        scandir = os.scandir
        def refuse(directory):
            if Path(directory) == self.targets["conflict"]:
                raise PermissionError("injected target enumeration refusal")
            return scandir(directory)
        module = self.tool()
        with patch("os.scandir", side_effect=refuse):
            result = module.plan_batch(self.registration, ("clean", "conflict"))
        self.assertEqual("proposed", result.targets[0].status)
        self.assertEqual("DIRECTORY_READ_ERROR", result.targets[1].findings[0].code)

    def test_explicit_mappings_include_addition_deletion_and_no_whole_repository_copy(self):
        added, removed = "scenarios/added.feature", "scenarios/removed.feature"
        self.write(self.candidate, added, b"new scenario")
        self.write(self.base, removed, b"retired scenario")
        local = self.targets["clean"]
        self.write(local, "verification/removed.feature", b"retired scenario")
        target = self.data["targets"][1]
        self.data["source"]["files"].extend((
            {"scenario": "sample/CTX-domain/TS-002#added", "path": added},
            {"scenario": "sample/CTX-domain/TS-003#removed", "path": removed},
        ))
        target["files"].extend((
            {"source": added, "path": "verification/added.feature"},
            {"source": removed, "path": "verification/removed.feature"},
        ))
        selected_source = tuple(entry["path"] for entry in self.data["source"]["files"])
        for role, root in (("base", self.base), ("candidate", self.candidate)):
            self.data["source"][role]["version"] = content_version(root, selected_source)
        selected_local = tuple(entry["path"] for entry in target["files"])
        target["local"]["version"] = content_version(local, selected_local)
        self.save_registration()
        result = self.batch(("clean",))
        changes = result.targets[0].plan.changes
        self.assertEqual([("verification/added.feature", "add"), (self.target_file, "modify"),
                          ("verification/removed.feature", "delete")],
                         [(item.path, item.action) for item in changes])
        self.assertEqual((None, digest(b"new scenario")), (changes[0].base.sha256, changes[0].candidate.sha256))
        self.assertEqual((digest(b"retired scenario"), None), (changes[2].base.sha256, changes[2].candidate.sha256))

    def test_exact_commits_can_identify_only_registered_feature_scope(self):
        commits = {}
        for root in (self.base, self.candidate, self.targets["clean"]):
            git(root, "init", "--quiet", "--template=")
            git(root, "add", "--", ".")
            git(root, "commit", "--quiet", "-m", "Local scoped source")
            commits[root] = git(root, "rev-parse", "HEAD")
        self.data["source"]["base"]["version"] = commits[self.base]
        self.data["source"]["candidate"]["version"] = commits[self.candidate]
        self.data["targets"][1]["local"]["version"] = commits[self.targets["clean"]]
        self.save_registration()
        result = self.batch(("clean",))
        self.assertEqual("proposed", result.status)
        self.assertEqual([commits[self.base], commits[self.targets["clean"]], commits[self.candidate]],
                         [source.version for source in result.targets[0].plan.sources])

    def test_batch_output_is_new_and_outside_all_registered_roots_including_unselected_missing_target(self):
        output = self.workspace / "batch proposal.json"
        run = self.batch_cli(("clean", "conflict", "missing", "unregistered"), "--output", output)
        self.assertEqual(2, run.returncode, run.stderr + run.stdout)
        self.assertTrue(output.is_file(), "A complete per-target error report may be explicitly saved")
        self.assertEqual(json.loads(run.stdout), json.loads(output.read_bytes()))
        old = output.read_bytes()
        run = self.batch_cli(("clean",), "--output", output)
        self.assertEqual(2, run.returncode)
        self.assertEqual(old, output.read_bytes())
        for root in (self.base, self.candidate, *self.targets.values()):
            with self.subTest(root=root.name):
                before = source_bytes(self.workspace)
                run = self.batch_cli(("clean",), "--output", root / "new report.json")
                self.assertEqual(2, run.returncode, run.stderr + run.stdout)
                self.assertEqual("REPORT_CONFLICT", json.loads(run.stdout)["findings"][0]["code"])
                self.assertEqual(before, source_bytes(self.workspace))

    def test_unprotectable_declared_location_blocks_output_but_retains_stdout_results(self):
        del self.data["targets"][0]["local"]["root"]
        self.save_registration()
        output = self.workspace / "must not create.json"
        run = self.batch_cli(("aligned", "clean"), "--output", output)
        self.assertEqual(2, run.returncode, run.stderr + run.stdout)
        self.assertTrue(run.stdout.strip())
        data = json.loads(run.stdout)
        self.assertEqual(["unavailable", "proposed"], [target["status"] for target in data["targets"]])
        self.assertEqual("REPORT_CONFLICT", data["findings"][0]["code"])
        self.assertFalse(output.exists())

    def test_batch_order_is_deterministic(self):
        first = self.batch(("conflict", "aligned", "clean"))
        second = self.batch(("clean", "conflict", "aligned"))
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_nonexistent_declared_source_file_cannot_be_a_fake_nochange_scenario(self):
        self.data["source"]["files"][0]["path"] = "scenarios/not there.feature"
        self.data["targets"][1]["files"][0]["source"] = "scenarios/not there.feature"
        for role, root in (("base", self.base), ("candidate", self.candidate)):
            self.data["source"][role]["version"] = content_version(root, ("scenarios/not there.feature",))
        self.save_registration()
        result = self.batch(("clean",))
        self.assertEqual("unavailable", result.targets[0].status)
        self.assertEqual("SOURCE_FILE_MISSING", result.targets[0].findings[0].code)

    def test_failure_diagnostics_distinguish_source_version_from_target_local_version(self):
        self.data["source"]["base"]["version"] = "sha256:" + "0" * 64
        self.save_registration()
        source_error = self.batch(("clean",)).targets[0].findings[0]
        self.assertEqual("source/base", source_error.path)
        self.data["source"]["base"]["version"] = content_version(self.base, (self.source_file,))
        self.data["targets"][0]["local"]["version"] = "sha256:" + "0" * 64
        self.save_registration()
        target_error = self.batch(("aligned",)).targets[0].findings[0]
        self.assertEqual("targets/aligned/local", target_error.path)

    def test_core_consumer_needs_no_maintainer_tests_history_workflow_or_application(self):
        consumer = self.workspace / "standalone updater"
        consumer.mkdir()
        for name in ("plan_template_update.py", "artifact_io.py", "check_artifacts.py"):
            shutil.copyfile(WORKTREE / ".github/utilities" / name, consumer / name)
        before = source_bytes(self.workspace)
        env = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(consumer / "plan_template_update.py"),
             "--registration", str(self.registration), "--target", "aligned", "--target", "clean",
             "--target", "conflict", "--target", "missing", "--target", "unregistered"],
            cwd=consumer, env=env, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        data = json.loads(run.stdout)
        self.assertEqual(["no-change", "proposed", "conflict", "unavailable", "unavailable"],
                         [target["status"] for target in data["targets"]])
        self.assertEqual("", run.stderr)
        self.assertEqual(before, source_bytes(self.workspace))

    def test_output_reservation_resolution_failure_is_refused_without_losing_target_results(self):
        module = self.tool()
        output = self.workspace / "must remain absent.json"
        before = source_bytes(self.workspace)
        resolve = Path.resolve
        def refuse(path, *args, **kwargs):
            if path == self.targets["missing"]:
                raise OSError("injected unresolved target-location boundary")
            return resolve(path, *args, **kwargs)
        stdout = io.StringIO()
        try:
            with patch.object(Path, "resolve", refuse), contextlib.redirect_stdout(stdout):
                code = module.main(["--registration", str(self.registration), "--target", "clean",
                                    "--output", str(output)])
        except OSError as error:
            self.fail("Output boundary failures must return input-error/2, not escape: " + str(error))
        self.assertEqual(2, code)
        payload = json.loads(stdout.getvalue())
        self.assertEqual("REPORT_CONFLICT", payload["findings"][0]["code"])
        self.assertEqual("proposed", payload["targets"][0]["status"])
        self.assertFalse(output.exists())
        self.assertEqual(before, source_bytes(self.workspace))


class PathAndReservationTests(UpdateFixture):
    """ENH-11 / T11-I1..I3: actual topology/traversal/reservations, not mocked paths."""

    def registration(self, relative="targets.yaml"):
        source_file, target_file = "scenarios/allow.feature", "verification/allow.feature"
        self.write(self.base, source_file, b"Feature: old\n")
        self.write(self.candidate, source_file, b"Feature: candidate\n")
        self.write(self.local, target_file, b"Feature: old\n")
        self.write(self.local, "business/owner.md", b"Owner-only data stays in scope\n")
        path = self.workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        roots = {role: os.path.relpath(root, path.parent).replace("\\", "/")
                 for role, root in (("base", self.base), ("local", self.local),
                                    ("candidate", self.candidate))}
        data = {
            "schemaVersion": 1,
            "source": {
                "repository": "fixture/domain",
                "base": {"root": roots["base"], "version": content_version(self.base, (source_file,))},
                "candidate": {"root": roots["candidate"],
                              "version": content_version(self.candidate, (source_file,))},
                "files": [{"scenario": "fixture/CTX-domain/TS-001#allow", "path": source_file}],
            },
            "targets": [{
                "id": "clean", "repository": "fixture/bc-clean", "scope": "fixture/CTX-clean",
                "local": {"root": roots["local"], "version": content_version(self.local, (target_file,))},
                "files": [{"source": source_file, "path": target_file}],
            }],
        }
        self.save(path, data)
        return path, data, source_file, target_file

    def save(self, path, data):
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
                        encoding="utf-8", newline="\n")

    def batch_cli(self, registration, *targets, output=None):
        script = WORKTREE / ".github/utilities/plan_template_update.py"
        argv = [sys.executable, "-B", "-X", "utf8", str(script),
                "--registration", str(registration)]
        for target in targets:
            argv.extend(("--target", target))
        if output is not None:
            argv.extend(("--output", str(output)))
        run = subprocess.run(argv, cwd=self.workspace, shell=False, capture_output=True,
                             text=True, encoding="utf-8")
        self.assertTrue(run.stdout.strip(), run.stderr)
        return run, json.loads(run.stdout)

    def extra_target(self, data, root, target_file, *, id="unsafe"):
        data["targets"].append({
            "id": id, "repository": "fixture/bc-" + id, "scope": "fixture/CTX-" + id,
            "local": {"root": root,
                      "version": content_version(self.local, (target_file,))},
            "files": [{"source": data["source"]["files"][0]["path"], "path": target_file}],
        })

    def assert_output_refused(self, registration, output, *selected, expected_states=None):
        before = source_bytes(self.workspace)
        run, payload = self.batch_cli(registration, *selected, output=output)
        after = source_bytes(self.workspace)
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertEqual("input-error", payload["status"])
        self.assertFalse(output.exists(), "A report cannot occupy the declared source hierarchy")
        self.assertEqual(before, after, "Rejection must preserve every owned file and file set")
        self.assertTrue(payload.get("findings"), run.stdout + run.stderr)
        self.assertEqual("REPORT_CONFLICT", payload["findings"][0]["code"])
        self.assertEqual(expected_states or ["proposed"], [t["status"] for t in payload["targets"]])

    def test_fix1_i1_complete_tree_directory_case_alias_is_not_a_clean_add(self):
        self.write(self.local, "settings/owner.md", b"Owner data must not be hidden\n")
        self.write(self.candidate, "Settings", b"candidate file")
        before = self.snapshot()
        try:
            self.error("PATH_TYPE_CONFLICT")
        finally:
            self.assertEqual(before, self.snapshot())

    def test_fix1_i1_case_folded_file_parent_blocks_candidate_descendants(self):
        self.write(self.local, "settings", b"owner regular file")
        self.write(self.candidate, "Settings/child.md", b"new candidate child")
        before = self.snapshot()
        try:
            self.error("PATH_TYPE_CONFLICT")
        finally:
            self.assertEqual(before, self.snapshot())

    def test_fix1_i1_case_only_directory_prefixes_do_not_hide_owner_files(self):
        self.write(self.local, "settings/owner.md", b"owner-only file")
        self.write(self.candidate, "Settings/new.md", b"candidate-only file")
        before = self.snapshot()
        try:
            self.error("PATH_COLLISION")
        finally:
            self.assertEqual(before, self.snapshot())

    def test_fix1_i1_mapped_directory_file_alias_is_unavailable_beside_clean_target(self):
        path, data, _, target_file = self.registration()
        unsafe = self.workspace / "mapped owner"
        self.write(unsafe, "settings.feature/owner.md", b"owner-only data")
        self.extra_target(data, unsafe.name, "Settings.feature")
        data["targets"][-1]["local"]["version"] = content_version(unsafe, ("Settings.feature",))
        self.save(path, data)
        before = source_bytes(self.workspace)
        run, payload = self.batch_cli(path, "clean", "unsafe")
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertEqual(["proposed", "unavailable"], [t["status"] for t in payload["targets"]])
        self.assertEqual("PATH_TYPE_CONFLICT", payload["targets"][1]["findings"][0]["code"])
        self.assertEqual(["verification/allow.feature"],
                         [item["path"] for item in payload["targets"][0]["plan"]["changes"]])
        self.assertEqual(before, source_bytes(self.workspace))

    def test_fix1_i1_mapped_missing_file_checks_actual_directory_prefix_spelling(self):
        path, data, source_file, target_file = self.registration()
        (self.base / source_file).unlink()
        (self.local / target_file).unlink()
        data["source"]["base"]["version"] = content_version(self.base, (source_file,))
        data["targets"][0]["local"]["version"] = content_version(self.local, (target_file,))
        unsafe = self.workspace / "mapped owner"
        self.write(unsafe, "settings/owner.md", b"Unselected owner content is not disposable\n")
        self.extra_target(data, unsafe.name, "Settings/new.feature")
        data["targets"][-1]["local"]["version"] = content_version(unsafe, ("Settings/new.feature",))
        self.save(path, data)
        before = source_bytes(self.workspace)
        run, payload = self.batch_cli(path, "clean", "unsafe")
        self.assertEqual(before, source_bytes(self.workspace))
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertEqual(["proposed", "unavailable"], [t["status"] for t in payload["targets"]])
        self.assertEqual("PATH_COLLISION", payload["targets"][1]["findings"][0]["code"])
        self.assertEqual("add", payload["targets"][0]["plan"]["changes"][0]["action"])

    def test_fix1_i2_normal_sibling_roots_keep_exact_git_versions_and_owner_bytes(self):
        path, data, _, _ = self.registration("configuration/targets.yaml")
        commits = []
        for root in (self.base, self.local, self.candidate):
            git(root, "init", "--quiet", "--template=")
            git(root, "add", "--", ".")
            git(root, "commit", "--quiet", "-m", "Owned fix1 sibling identity")
            commits.append(git(root, "rev-parse", "HEAD"))
        data["source"]["base"]["version"], data["source"]["candidate"]["version"] = commits[0], commits[2]
        data["targets"][0]["local"]["version"] = commits[1]
        self.save(path, data)
        before = source_bytes(self.workspace)
        run, payload = self.batch_cli(path, "clean")
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        plan = payload["targets"][0]["plan"]
        self.assertEqual(["../old base", "../owner 本地", "../new candidate"],
                         [source["root"] for source in plan["sources"]])
        self.assertEqual(commits, [source["version"] for source in plan["sources"]])
        self.assertEqual(before, source_bytes(self.workspace), "Local Git reads must not change owner or metadata bytes")

    def test_fix1_i3_unselected_missing_target_file_ancestor_is_protected(self):
        path, data, _, target_file = self.registration()
        for root, output in (("proposal.json/checkout", "proposal.json"),
                             ("deeper.json/future/checkout", "deeper.json")):
            with self.subTest(root=root):
                data["targets"] = data["targets"][:1]
                self.extra_target(data, root, target_file, id="future")
                self.save(path, data)
                self.assert_output_refused(path, self.workspace / output, "clean")

    def test_fix1_i3_selected_unavailable_target_keeps_clean_proposal_when_output_refused(self):
        path, data, _, target_file = self.registration()
        self.extra_target(data, "proposal.json/checkout", target_file, id="future")
        self.save(path, data)
        self.assert_output_refused(path, self.workspace / "proposal.json", "clean", "future",
                                   expected_states=["proposed", "unavailable"])

    def test_fix1_i3_missing_source_root_file_ancestor_is_also_protected(self):
        path, data, source_file, _ = self.registration()
        data["source"]["base"] = {
            "root": "proposal.json/source",
            "version": content_version(self.workspace / "proposal.json/source", (source_file,)),
        }
        self.save(path, data)
        self.assert_output_refused(path, self.workspace / "proposal.json", "clean",
                                   expected_states=["unavailable"])

    def test_fix1_i3_equal_below_and_file_ancestor_guards_are_consistent(self):
        path, data, _, target_file = self.registration()
        self.extra_target(data, "reserved.json/checkout.json", target_file, id="future")
        self.save(path, data)
        for relative in ("reserved.json/checkout.json", "reserved.json/checkout.json/new.json",
                         "reserved.json"):
            with self.subTest(relative=relative):
                self.assert_output_refused(path, self.workspace / relative, "clean")


if __name__ == "__main__":
    unittest.main()
