"""Domain-source setup: real local sources, bytes, native Git, index intent and metadata."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

import yaml

from tests.helpers import WORKTREE, directory_link, git, seed_git_repo, source_bytes, temporary_workspace


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


class DomainFixture(unittest.TestCase):
    def setUp(self):
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "owner BC проект €"
        self.source = self.workspace / "домен € source"
        seed_git_repo(self.root)
        seed_git_repo(self.source)
        (self.source / "domain-model").mkdir()
        (self.source / "domain-model/правило.md").write_bytes(b"# Owned rule\n\nlimit = 2\n")
        git(self.source, "add", "--", "domain-model")
        git(self.source, "commit", "--quiet", "-m", "Fixed domain fixture")
        self.version = git(self.source, "rev-parse", "HEAD")
        self.config = self.root / "bc-config.yaml"
        (self.root / "docs").mkdir()
        (self.root / "docs/development.md").write_bytes(
            b'# Fixture only\n<a id="project-registration"></a>\n## Registration\n'
        )
        self.write_config([])
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Owned configuration fixture")
        self.declaration = {
            "id": "fixed-domain", "kind": "git", "root": "../домен € source",
            "path": "domain-model", "baseline": self.version, "readOnly": True,
        }

    def write_config(self, sources):
        data = {
            "schemaVersion": 1, "projectId": "owned",
            "boundedContexts": [{"id": "CTX-001"}], "domainSources": sources,
            "developmentRegistration": "docs/development.md#project-registration",
        }
        raw = ("# Owner header: preserve bytes\r\n"
               + yaml.safe_dump(data, sort_keys=False, allow_unicode=True).replace("\n", "\r\n")
               + "# Owner footer: preserve bytes\r\n").encode("utf-8")
        self.config.write_bytes(raw)
        return data

    def tool(self):
        self.assertIsNotNone(importlib.util.find_spec("setup_domain_source"),
                             "Task15 source inspection/setup is not implemented")
        return importlib.import_module("setup_domain_source")

    def snapshot(self):
        return source_bytes(self.root), source_bytes(self.source)

    def owner_repository_state(self, root):
        return (
            source_bytes(root, include_git=False),
            git(root, "rev-parse", "HEAD"),
            git(root, "write-tree"),
            git(root, "status", "--porcelain=v1", "--untracked-files=all"),
            git(root, "for-each-ref", "--format=%(refname) %(objectname)"),
            (root / ".git" / "config").read_bytes(),
        )

    def inspect(self, declaration=None, **kwargs):
        before, cwd = self.snapshot(), Path.cwd()
        result = self.tool().inspect_domain_source(
            self.root, self.declaration if declaration is None else declaration, **kwargs
        )
        self.assertEqual(before, self.snapshot(), "Inspect must retain files, objects, index, refs and config")
        self.assertEqual(cwd, Path.cwd(), "Inspect must not change global cwd")
        return result

    def apply(self, declaration=None, *, operation="register", expected=None, **kwargs):
        source = self.declaration if declaration is None else declaration
        if expected is None:
            expected = self.inspect(source, operation=operation, **{
                key: value for key, value in kwargs.items() if key == "target"
            }).get("preflight")
        return self.tool().apply_domain_source(
            self.root, source, operation=operation, config_path="bc-config.yaml",
            expected=expected, **kwargs
        )

    def codes(self, result):
        return {item["code"] for item in result["findings"]}

    def cli(self, *extra, proposed=True):
        script = WORKTREE / ".github/utilities/setup_domain_source.py"
        self.assertTrue(script.is_file(), "Task15 CLI is not implemented")
        args = [sys.executable, "-B", "-X", "utf8", str(script), "--root", str(self.root),
                "--config", "bc-config.yaml", "--source-id", "fixed-domain"]
        if proposed:
            args += ["--kind", "git", "--source-root", self.declaration["root"],
                     "--source-path", self.declaration["path"], "--baseline", self.version, "--read-only"]
        run = subprocess.run(args + list(map(str, extra)), cwd=self.workspace, shell=False,
                             capture_output=True, text=True, encoding="utf-8")
        self.assertTrue(run.stdout.strip(), run.stderr)
        return run, json.loads(run.stdout)


class SourceInspectionTests(DomainFixture):
    def test_source_01_missing_fields_are_unavailable_not_inferred(self):
        for field in self.declaration:
            with self.subTest(field=field):
                source = dict(self.declaration)
                del source[field]
                result = self.inspect(source)
                self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]))
                self.assertIn("INVALID_SOURCE_CONFIG", self.codes(result))
                self.assertEqual([], result["written"])

    def test_source_01_none_and_nonmapping_inputs_are_explicit_errors(self):
        for value in (None, [], "HEAD", {}):
            with self.subTest(value=value):
                result = self.tool().inspect_domain_source(self.root, value)
                self.assertEqual("unavailable", result["status"])
                self.assertIn("INVALID_SOURCE_CONFIG", self.codes(result))

    def test_source_02_exact_commit_and_selected_location_are_read_only(self):
        result = self.inspect()
        self.assertEqual(("ready", 0, "proposed"),
                         (result["status"], result["exit_code"], result["outcome"]))
        self.assertEqual(self.declaration, result["source"])
        self.assertEqual({
            "root": str(self.source), "path": "domain-model",
            "selected": str(self.source / "domain-model"), "baseline": self.version,
        }, result["location"])
        self.assertEqual(True, result["ownership"]["readOnly"])
        self.assertEqual(False, result["ownership"]["os_enforced"])
        self.assertEqual([], result["written"])
        self.assertEqual(["register"], [item["operation"] for item in result["actions"]])
        self.assertTrue(result["preflight"].startswith("sha256:"))

    def test_source_02_local_file_uses_raw_content_not_decoded_text(self):
        raw = b"\xef\xbb\xbf# Local rule\r\n"
        path = self.source / "domain-model/правило.md"
        path.write_bytes(raw)
        source = dict(self.declaration, kind="local", path="domain-model/правило.md", baseline=digest(raw))
        result = self.inspect(source)
        self.assertEqual("ready", result["status"])
        self.assertEqual(digest(raw), result["location"]["baseline"])
        path.write_bytes(raw.replace(b"\r\n", b"\n"))
        mismatch = self.inspect(source)
        self.assertEqual("conflict", mismatch["status"])
        self.assertIn("BASE_MISMATCH", self.codes(mismatch))

    def test_source_02_old_fixed_commit_never_selects_current_head(self):
        git(self.source, "commit", "--allow-empty", "--quiet", "-m", "Later head, identical selected bytes")
        self.assertNotEqual(self.version, git(self.source, "rev-parse", "HEAD"))
        result = self.inspect()
        self.assertEqual("ready", result["status"])
        self.assertEqual(self.version, result["location"]["baseline"])

    def test_source_03_wrong_nested_root_is_not_trimmed(self):
        source = dict(self.declaration, root="../домен € source/domain-model")
        result = self.inspect(source)
        self.assertEqual("unavailable", result["status"])
        self.assertEqual(str(self.source / "domain-model/domain-model"), result["location"]["selected"])
        self.assertTrue(self.codes(result) & {"FILE_NOT_FOUND", "OBJECT_PATH_MISSING", "BASE_UNAVAILABLE"})

    def test_source_04_existing_domain_guide_does_not_block_registration(self):
        (self.root / "domain-model").mkdir()
        guide = self.root / "domain-model/README.md"
        guide.write_bytes(b"Owner guide, not an empty placeholder.\n")
        before = guide.read_bytes()
        self.assertEqual("ready", self.inspect()["status"])
        result = self.apply(owned=True)
        self.assertEqual("registered", result["outcome"])
        self.assertEqual(before, guide.read_bytes())

    def test_source_06_missing_symbolic_abbreviated_and_unavailable_versions_fail(self):
        for version in ("", "HEAD", "main", "master", "staged", self.version[:12], "0" * 40):
            with self.subTest(version=version):
                result = self.inspect(dict(self.declaration, baseline=version))
                self.assertEqual("unavailable", result["status"])
                self.assertEqual(2, result["exit_code"])
                self.assertTrue(self.codes(result) & {"INVALID_SOURCE_CONFIG", "BASE_UNAVAILABLE"})

    def test_source_06_tree_blob_and_tag_are_not_commit_baselines(self):
        git(self.source, "tag", "-a", "v-fixture", "-m", "Not a commit object")
        objects = [
            git(self.source, "rev-parse", "HEAD^{tree}"),
            git(self.source, "rev-parse", "HEAD:domain-model/правило.md"),
            git(self.source, "rev-parse", "refs/tags/v-fixture"),
        ]
        for version in objects:
            with self.subTest(version=version):
                result = self.inspect(dict(self.declaration, baseline=version))
                self.assertEqual("unavailable", result["status"])
                self.assertIn("BASE_UNAVAILABLE", self.codes(result))

    def test_source_07_read_only_and_owned_flags_do_not_grant_source_writes(self):
        for read_only in (True, False):
            with self.subTest(read_only=read_only):
                source = dict(self.declaration, readOnly=read_only)
                before = source_bytes(self.source)
                result = self.inspect(source)
                self.assertEqual(read_only, result["ownership"]["readOnly"])
                self.assertFalse(result["ownership"]["source_writes"])
                result = self.apply(source, owned=True)
                self.assertEqual("ready", result["status"])
                self.assertEqual(before, source_bytes(self.source))
                self.write_config([])

    def test_source_07_owner_hooks_and_filters_are_never_executed(self):
        marker = self.workspace / "UNEXPECTED-EXECUTION"
        hooks = self.source / ".git/hooks"
        hooks.mkdir(exist_ok=True)
        for name in ("post-checkout", "post-merge", "pre-commit"):
            path = hooks / name
            path.write_text(f"#!/bin/sh\ntouch '{marker.as_posix()}'\n", encoding="utf-8")
            path.chmod(0o755)
        git(self.source, "config", "filter.poison.smudge", f"touch '{marker.as_posix()}'")
        git(self.source, "config", "filter.poison.clean", f"touch '{marker.as_posix()}'")
        git(self.source, "config", "filter.poison.required", "true")
        # Raw Git objects are seeded before the poisonous attribute is present.
        (self.source / ".gitattributes").write_bytes(b"* filter=poison\n")
        self.assertEqual("ready", self.inspect()["status"])
        self.assertEqual("registered", self.apply(owned=True)["outcome"])
        self.assertFalse(marker.exists())

    def test_source_08_source_id_collision_and_duplicate_ids_are_conflicts(self):
        self.write_config([dict(self.declaration, baseline="0" * 40)])
        result = self.inspect()
        self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]))
        self.assertIn("SOURCE_ID_CONFLICT", self.codes(result))
        self.write_config([self.declaration, dict(self.declaration, readOnly=False)])
        duplicate = self.inspect()
        self.assertEqual("conflict", duplicate["status"])
        self.assertIn("DUPLICATE_DOMAIN_SOURCE", self.codes(duplicate))

    def test_source_08_same_location_under_another_id_is_not_silently_aliased(self):
        self.write_config([dict(self.declaration, id="owner-other-id")])
        result = self.inspect()
        self.assertEqual("conflict", result["status"])
        self.assertIn("SOURCE_ALIAS", self.codes(result))

    def test_source_08_invalid_config_never_becomes_write_permission(self):
        for raw in (b"schemaVersion: 9\n", b"schemaVersion: 1\nschemaVersion: 1\n",
                    b"!!python/object:builtins.object {}\n"):
            with self.subTest(raw=raw):
                self.config.write_bytes(raw)
                result = self.inspect()
                self.assertEqual("unavailable", result["status"])
                applied = self.apply(owned=True)
                self.assertEqual([], applied["written"])
                self.assertEqual(raw, self.config.read_bytes())

    def test_source_09_network_sources_do_not_call_git_or_discover_credentials(self):
        for root in ("https://example.invalid/private.git", "ssh://user@example.invalid/private",
                     "git@example.invalid:private.git", "//server/share", r"\\server\share"):
            with self.subTest(root=root):
                # This spy rejects any external command; it never supplies canned stdout.
                with patch("subprocess.run", side_effect=AssertionError("Network inspect invoked an external tool")):
                    result = self.tool().inspect_domain_source(self.root, dict(self.declaration, root=root))
                self.assertEqual("unavailable", result["status"])
                self.assertIn("NETWORK_NOT_AUTHORIZED", self.codes(result))
                self.assertEqual([], result["written"])
                self.assertNotIn(root, json.dumps(result))

    def test_source_12_unicode_spaces_and_exact_relative_file_are_supported(self):
        name = "domain-model/Ωmega € with spaces.md"
        raw = "Факт не одобрение €.\r\n".encode("utf-8")
        (self.source / name).write_bytes(raw)
        result = self.inspect(dict(self.declaration, kind="local", path=name, baseline=digest(raw)))
        self.assertEqual("ready", result["status"])
        self.assertEqual(str(self.source / name), result["location"]["selected"])

    def test_source_12_traversal_metadata_and_absolute_paths_are_rejected(self):
        for path in ("../owner BC проект €", "/domain-model", "domain-model/../README.md",
                     "domain-model//правило.md", r"domain-model\правило.md", ".git/config", ".GIT/config"):
            with self.subTest(path=path):
                result = self.inspect(dict(self.declaration, path=path))
                self.assertEqual("unavailable", result["status"])
                self.assertEqual([], result["written"])

    def test_source_12_source_root_reached_through_a_link_reads_the_linked_source(self):
        alias = self.workspace / "alias"
        with directory_link(alias, self.source):
            for root in ("../alias", "../alias/../домен € source"):
                with self.subTest(root=root):
                    result = self.inspect(dict(self.declaration, root=root))
                    self.assertEqual("ready", result["status"], result)
                    self.assertEqual(str(self.source.resolve()), result["location"]["root"])
                    self.assertEqual([], result["written"])

    def test_source_12_selected_path_link_cannot_escape_or_alias(self):
        alias = self.source / "domain-model/alias"
        with directory_link(alias, self.root):
            result = self.inspect()
            self.assertEqual("unavailable", result["status"])
            self.assertTrue(self.codes(result) & {"OUTSIDE_ROOT", "UNSAFE_ROOT"})

    def test_source_12_changed_file_set_or_bytes_are_not_matching_baselines(self):
        (self.source / "domain-model/extra.md").write_bytes(b"Owner extra\n")
        result = self.inspect()
        self.assertEqual("conflict", result["status"])
        self.assertIn("BASE_MISMATCH", self.codes(result))


class SourceRegistrationTests(DomainFixture):
    def test_source_05_identical_registration_and_repeat_apply_are_no_change(self):
        self.assertEqual("registered", self.apply(owned=True)["outcome"])
        before = self.snapshot()
        result = self.inspect()
        self.assertEqual(("ready", "no-change", []), (result["status"], result["outcome"], result["actions"]))
        repeated = self.apply(owned=True)
        self.assertEqual(("ready", "no-change", []),
                         (repeated["status"], repeated["outcome"], repeated["written"]))
        self.assertEqual(before, self.snapshot())
        self.assertEqual(1, len(yaml.safe_load(self.config.read_bytes())["domainSources"]))

    def test_source_08_registration_preserves_owner_bytes_entries_index_and_refs(self):
        raw = b"Standalone owner file\n"
        (self.root / "owner rule.md").write_bytes(raw)
        other_path = self.root / "owner rule.md"
        other = {"id": "other", "kind": "local", "root": ".", "path": "owner rule.md",
                 "baseline": digest(raw), "readOnly": False}
        self.write_config([other])
        before = self.snapshot()
        old = self.config.read_bytes()
        result = self.apply(owned=True)
        self.assertEqual(("ready", "registered"), (result["status"], result["outcome"]))
        current = self.config.read_bytes()
        self.assertTrue(current.startswith(old[:old.index(b"developmentRegistration:")]))
        self.assertTrue(current.endswith(old[old.index(b"developmentRegistration:"):]))
        self.assertEqual([other, self.declaration], yaml.safe_load(current)["domainSources"])
        after = self.snapshot()
        self.assertEqual(before[1], after[1])
        self.assertEqual({k: v for k, v in before[0].items() if k != "bc-config.yaml"},
                         {k: v for k, v in after[0].items() if k != "bc-config.yaml"})
        self.assertEqual(raw, other_path.read_bytes())

    def test_source_08_json_or_flow_config_is_not_reformatted_to_apply(self):
        data = self.write_config([])
        self.config.write_text(json.dumps(data), encoding="utf-8")
        before = self.snapshot()
        result = self.apply(owned=True)
        self.assertEqual("unavailable", result["status"])
        self.assertIn("CONFIG_EDIT_UNSUPPORTED", self.codes(result))
        self.assertEqual(before, self.snapshot())

    def test_source_10_apply_requires_target_ownership_and_exact_preflight(self):
        before = self.snapshot()
        no_consent = self.apply()
        self.assertEqual("unavailable", no_consent["status"])
        self.assertIn("OWNERSHIP_CONSENT_REQUIRED", self.codes(no_consent))
        missing = self.tool().apply_domain_source(
            self.root, self.declaration, operation="register", config_path="bc-config.yaml",
            expected=None, owned=True,
        )
        self.assertEqual("unavailable", missing["status"])
        self.assertIn("PREFLIGHT_REQUIRED", self.codes(missing))
        self.assertEqual(before, self.snapshot())

    def test_source_12_changed_config_after_inspect_stops_before_writing(self):
        expected = self.inspect()["preflight"]
        self.config.write_bytes(self.config.read_bytes() + b"# Later owner edit\n")
        before = self.snapshot()
        result = self.apply(expected=expected, owned=True)
        self.assertEqual("conflict", result["status"])
        self.assertIn("INPUT_CHANGED", self.codes(result))
        self.assertEqual(before, self.snapshot())

    def test_source_12_changed_source_after_inspect_is_not_setup_success(self):
        expected = self.inspect()["preflight"]
        (self.source / "domain-model/правило.md").write_bytes(b"Owner changed source\n")
        before = self.snapshot()
        result = self.apply(expected=expected, owned=True)
        self.assertNotEqual("ready", result["status"])
        self.assertEqual([], result["written"])
        self.assertEqual(before, self.snapshot())

    def test_source_12_registration_cannot_rewrite_a_selected_source(self):
        source = dict(self.declaration, kind="local", root=".", path="bc-config.yaml",
                      baseline=digest(self.config.read_bytes()))
        result = self.inspect(source)
        self.assertEqual("conflict", result["status"])
        self.assertIn("SOURCE_OUTPUT_OVERLAP", self.codes(result))

    def test_source_11_atomic_replace_error_preserves_original_and_exposes_partial_temp(self):
        expected = self.inspect()["preflight"]
        before = self.snapshot()
        with patch("os.replace", side_effect=OSError("injected replacement boundary failure")):
            result = self.apply(expected=expected, owned=True)
        self.assertEqual("unavailable", result["status"])
        self.assertEqual("partial", result["outcome"])
        self.assertFalse(result["recovery"]["automatic_cleanup"])
        self.assertEqual("manual-required", result["recovery"]["state"])
        self.assertEqual(before[1], source_bytes(self.source))
        after = source_bytes(self.root)
        self.assertEqual(before[0], {k: v for k, v in after.items() if k in before[0]})
        new = set(after) - set(before[0])
        self.assertEqual(1, len(new))
        partial = self.root / new.pop()
        self.assertIn(str(partial), [item["path"] for item in result["recovery"]["paths"]])
        self.assertEqual([self.declaration], yaml.safe_load(partial.read_bytes())["domainSources"])
        # Recovery is an explicit owner action in this test, not a product rollback.
        partial.unlink()
        self.assertEqual("registered", self.apply(owned=True)["outcome"])


class SourceSubmoduleTests(DomainFixture):
    def setup_submodule(self, **kwargs):
        return self.apply(operation="submodule", target="external domain", owned=True,
                          index_consent=True, **kwargs)

    def test_source_04_nonempty_materialization_target_is_a_conflict(self):
        target = self.root / "domain-model"
        target.mkdir()
        (target / "README.md").write_bytes(b"Owner content must survive\n")
        before = (
            self.owner_repository_state(self.root),
            self.owner_repository_state(self.source),
        )
        result = self.inspect(operation="submodule", target="domain-model")
        self.assertEqual(("conflict", 1), (result["status"], result["exit_code"]))
        self.assertIn("TARGET_CONFLICT", self.codes(result))
        applied = self.apply(operation="submodule", target="domain-model", owned=True, index_consent=True)
        self.assertEqual("conflict", applied["status"])
        self.assertEqual(
            before,
            (
                self.owner_repository_state(self.root),
                self.owner_repository_state(self.source),
            ),
        )

    def test_source_10_optional_submodule_discloses_native_metadata_and_separate_index_consent(self):
        result = self.inspect(operation="submodule", target="external domain")
        self.assertEqual("ready", result["status"])
        operations = {item["operation"] for item in result["actions"]}
        self.assertTrue({"clone-local-no-checkout", "materialize-blobs", "gitmodules", "local-config", "git-index"}
                        <= operations)
        self.assertEqual("external domain", result["suggested_registration"]["root"])
        before = self.snapshot()
        refused = self.apply(operation="submodule", target="external domain", owned=True)
        self.assertEqual("unavailable", refused["status"])
        self.assertIn("INDEX_CONSENT_REQUIRED", self.codes(refused))
        self.assertEqual(before, self.snapshot())

    def test_source_10_native_local_submodule_uses_fixed_commit_and_no_commit_or_bc_write(self):
        parent_head = git(self.root, "rev-parse", "HEAD")
        before_config = self.config.read_bytes()
        source_before = source_bytes(self.source)
        result = self.setup_submodule()
        self.assertEqual(("ready", "materialized"), (result["status"], result["outcome"]), result)
        target = self.root / "external domain"
        self.assertEqual(self.version, git(target, "rev-parse", "HEAD"))
        self.assertEqual("true", git(target, "rev-parse", "--is-inside-work-tree"))
        self.assertEqual((self.source / "domain-model/правило.md").read_bytes(),
                         (target / "domain-model/правило.md").read_bytes())
        self.assertEqual(parent_head, git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(before_config, self.config.read_bytes(), "Materialization must not imply BC registration")
        self.assertEqual(source_before, source_bytes(self.source))
        self.assertEqual("external domain", git(self.root, "config", "-f", ".gitmodules",
                                               "submodule.fixed-domain.path"))
        self.assertIn(f"160000 {self.version} 0\texternal domain",
                      git(self.root, "ls-files", "--stage", "--", "external domain"))
        status = git(self.root, "submodule", "status", "--", "external domain")
        self.assertIn(self.version, status)
        self.assertFalse(status.startswith("-"), "The native submodule must be initialized, not just described")
        self.assertEqual([], json.loads(json.dumps(result))["findings"])
        self.assertTrue(result["native"], "Retain actual native operations, exits and cwd")
        self.assertTrue(all(item["returncode"] == 0 for item in result["native"]))

    def test_source_05_repeated_submodule_setup_is_no_change_without_duplicate_metadata(self):
        self.assertEqual("materialized", self.setup_submodule()["outcome"])
        before = self.snapshot()
        result = self.inspect(operation="submodule", target="external domain")
        self.assertEqual(("ready", "no-change", []), (result["status"], result["outcome"], result["actions"]))
        repeated = self.setup_submodule()
        self.assertEqual(("ready", "no-change", []),
                         (repeated["status"], repeated["outcome"], repeated["written"]))
        self.assertEqual(before, self.snapshot())

    def test_source_07_materialization_bypasses_hook_and_smudge_even_at_exact_commit(self):
        marker = self.workspace / "UNEXPECTED-SMUDGE"
        (self.source / ".gitattributes").write_bytes(b"*.md filter=poison\n")
        git(self.source, "add", "--", ".gitattributes")
        git(self.source, "commit", "--quiet", "-m", "Attribute in exact object")
        self.version = git(self.source, "rev-parse", "HEAD")
        self.declaration["baseline"] = self.version
        for root in (self.root, self.source):
            git(root, "config", "filter.poison.smudge", f"touch '{marker.as_posix()}'")
            git(root, "config", "filter.poison.clean", f"touch '{marker.as_posix()}'")
            git(root, "config", "filter.poison.required", "true")
            hooks = root / ".git/hooks"
            hooks.mkdir(exist_ok=True)
            hook = hooks / "post-checkout"
            hook.write_text(f"#!/bin/sh\ntouch '{marker.as_posix()}'\n", encoding="utf-8")
            hook.chmod(0o755)
        before = source_bytes(self.source)
        self.assertEqual("materialized", self.setup_submodule()["outcome"])
        self.assertFalse(marker.exists())
        self.assertEqual(before, source_bytes(self.source))

    def test_source_08_submodule_preserves_unrelated_gitmodules_config_and_staged_files(self):
        (self.root / ".gitmodules").write_bytes(
            b'# Owner module entry\n[submodule "other"]\n\tpath = other\n\turl = ../other\n'
        )
        git(self.root, "add", "--", ".gitmodules")
        (self.root / "unrelated.txt").write_bytes(b"Owner staged bytes\n")
        git(self.root, "add", "--", "unrelated.txt")
        old_modules = (self.root / ".gitmodules").read_bytes()
        old_config = (self.root / ".git/config").read_bytes()
        old_index = git(self.root, "ls-files", "--stage", "--", "unrelated.txt")
        self.assertEqual("materialized", self.setup_submodule()["outcome"])
        self.assertTrue((self.root / ".gitmodules").read_bytes().startswith(old_modules))
        self.assertTrue((self.root / ".git/config").read_bytes().startswith(old_config))
        self.assertEqual(old_index, git(self.root, "ls-files", "--stage", "--", "unrelated.txt"))

    def test_source_08_conflicting_gitmodule_identity_or_staged_owner_version_stops(self):
        for raw in (
            b'[submodule "fixed-domain"]\n\tpath = owner-path\n\turl = ../owner\n',
            b'[submodule "other"]\n\tpath = external domain\n\turl = ../owner\n',
        ):
            with self.subTest(raw=raw):
                (self.root / ".gitmodules").write_bytes(raw)
                before = self.snapshot()
                result = self.inspect(operation="submodule", target="external domain")
                self.assertEqual("conflict", result["status"])
                self.assertEqual(before, self.snapshot())
        (self.root / ".gitmodules").write_bytes(b'# staged owner\n')
        git(self.root, "add", "--", ".gitmodules")
        (self.root / ".gitmodules").write_bytes(b'# unstaged owner\n')
        result = self.inspect(operation="submodule", target="external domain")
        self.assertEqual("conflict", result["status"])
        self.assertIn("INDEX_CONFLICT", self.codes(result))

    def test_source_11_partial_native_setup_is_retained_and_not_reclassified_as_success(self):
        module = self.tool()
        original = module._atomic_write
        before = self.snapshot()

        def fail_gitmodules(path, *args, **kwargs):
            if Path(path).name == ".gitmodules":
                raise OSError("injected metadata write boundary failure after real local clone")
            return original(path, *args, **kwargs)

        with patch.object(module, "_atomic_write", side_effect=fail_gitmodules):
            result = self.setup_submodule()
        self.assertEqual(("unavailable", "partial"), (result["status"], result["outcome"]))
        self.assertFalse(result["recovery"]["automatic_cleanup"])
        target = self.root / "external domain"
        self.assertTrue((target / ".git").is_file(), "No recursive rollback of owned partial checkout")
        self.assertEqual(before[1], source_bytes(self.source))
        for name in ("bc-config.yaml", ".git/config", ".git/index", ".git/HEAD"):
            self.assertEqual(before[0][name], source_bytes(self.root)[name])
        (target / "README.md").write_bytes(b"Later owner edit; never remove automatically\n")
        before_repeat = self.snapshot()
        repeated = self.setup_submodule()
        self.assertEqual("conflict", repeated["status"])
        self.assertEqual(before_repeat, self.snapshot())

    def test_source_12_target_link_and_parent_escape_are_refused_without_writes(self):
        alias = self.root / "alias"
        with directory_link(alias, self.source):
            for target in ("alias/new", "../outside", ".git/modules/data"):
                with self.subTest(target=target):
                    before = self.snapshot()
                    result = self.inspect(operation="submodule", target=target)
                    self.assertIn(result["status"], ("unavailable", "conflict"), result)
                    self.assertEqual([], result["written"])
                    self.assertEqual(before, self.snapshot())

    def test_source_12_changed_native_index_invalidates_preflight(self):
        expected = self.inspect(operation="submodule", target="external domain")["preflight"]
        (self.root / "later.txt").write_bytes(b"Later staged owner content\n")
        git(self.root, "add", "--", "later.txt")
        before = self.snapshot()
        result = self.setup_submodule(expected=expected)
        self.assertEqual("conflict", result["status"])
        self.assertIn("INPUT_CHANGED", self.codes(result))
        self.assertEqual(before, self.snapshot())

    def test_source_10_materialized_source_can_be_registered_only_as_a_separate_operation(self):
        result = self.setup_submodule()
        self.assertEqual("materialized", result["outcome"])
        selected = result["suggested_registration"]
        self.assertEqual(dict(self.declaration, root="external domain"), selected)
        self.assertEqual("registered", self.apply(selected, owned=True)["outcome"])
        self.assertEqual([selected], yaml.safe_load(self.config.read_bytes())["domainSources"])


class SourceCLITests(DomainFixture):
    def test_source_02_cli_default_is_read_only_and_uses_explicit_root_not_cwd(self):
        before = self.snapshot()
        run, result = self.cli()
        self.assertEqual((0, "ready", "proposed"), (run.returncode, result["status"], result["outcome"]))
        self.assertEqual(str(self.source), result["location"]["root"])
        self.assertEqual(before, self.snapshot())

    def test_source_04_cli_conflict_and_input_failure_have_distinct_exits(self):
        self.write_config([dict(self.declaration, readOnly=False)])
        run, result = self.cli()
        self.assertEqual((1, "conflict"), (run.returncode, result["status"]))
        self.write_config([])
        self.declaration["root"] = "../missing"
        run, result = self.cli()
        self.assertEqual((2, "unavailable"), (run.returncode, result["status"]))

    def test_source_05_cli_registration_and_existing_source_selection_are_idempotent(self):
        _, plan = self.cli()
        run, result = self.cli("--apply", "--operation", "register", "--owned-target",
                               "--expect", plan["preflight"])
        self.assertEqual((0, "registered"), (run.returncode, result["outcome"]))
        before = self.snapshot()
        run, result = self.cli(proposed=False)
        self.assertEqual((0, "no-change"), (run.returncode, result["outcome"]))
        self.assertEqual(before, self.snapshot())

    def test_source_10_cli_apply_never_implies_index_consent(self):
        _, plan = self.cli("--operation", "submodule", "--target", "external domain")
        before = self.snapshot()
        run, result = self.cli("--apply", "--operation", "submodule", "--target", "external domain",
                               "--owned-target", "--expect", plan["preflight"])
        self.assertEqual((2, "unavailable"), (run.returncode, result["status"]))
        self.assertIn("INDEX_CONSENT_REQUIRED", self.codes(result))
        self.assertEqual(before, self.snapshot())

    def test_source_09_cli_rejected_network_location_is_not_echoed(self):
        self.declaration["root"] = "https://private@example.invalid/source"
        before = self.snapshot()
        run, result = self.cli()
        self.assertEqual((2, "unavailable"), (run.returncode, result["status"]))
        self.assertIn("NETWORK_NOT_AUTHORIZED", self.codes(result))
        self.assertNotIn("private@", run.stdout + run.stderr)
        self.assertEqual(before, self.snapshot())


class SourceBoundaryTests(DomainFixture):
    """Self-review counterexamples; each preserves the original SOURCE cases."""

    def setup_submodule(self, **kwargs):
        return self.apply(operation="submodule", target="external domain", owned=True,
                          index_consent=True, **kwargs)

    def test_source_10_cli_apply_requires_explicit_operation_not_defaulted_registration(self):
        _, plan = self.cli()
        before = self.snapshot()
        run, result = self.cli("--apply", "--owned-target", "--expect", plan["preflight"])
        self.assertEqual((2, "unavailable"), (run.returncode, result["status"]))
        self.assertIn("INVALID_OPERATION", self.codes(result))
        self.assertEqual(before, self.snapshot())

    def test_source_08_invalid_owner_source_id_types_are_data_errors_not_uncaught_exceptions(self):
        for value in ([], {"bad": "id"}):
            with self.subTest(value=value):
                self.write_config([dict(self.declaration, id=value)])
                before = self.snapshot()
                result = self.tool().inspect_domain_source(self.root, self.declaration)
                self.assertEqual("unavailable", result["status"])
                self.assertIn("INVALID_METADATA", self.codes(result))
                self.assertEqual(before, self.snapshot())

    def test_source_12_case_aliased_git_root_is_not_a_local_content_source(self):
        source = dict(self.declaration, kind="local", root="../owner BC проект €/.GIT", path="config",
                      baseline=digest((self.root / ".git/config").read_bytes()))
        result = self.inspect(source)
        self.assertEqual("unavailable", result["status"])
        self.assertIn("EXCLUDED_TARGET", self.codes(result))

    def test_source_05_owner_module_index_changes_are_conflicts_not_identical_setup(self):
        self.assertEqual("materialized", self.setup_submodule()["outcome"])
        target = self.root / "external domain"
        blob = git(target, "rev-parse", "HEAD:README.md")
        git(target, "update-index", "--cacheinfo", f"100644,{blob},domain-model/правило.md")
        result = self.inspect(operation="submodule", target="external domain")
        self.assertEqual("conflict", result["status"])
        self.assertIn("INDEX_CONFLICT", self.codes(result))

    def test_source_05_missing_staged_gitmodules_is_partial_not_identical_setup(self):
        self.assertEqual("materialized", self.setup_submodule()["outcome"])
        git(self.root, "update-index", "--force-remove", "--", ".gitmodules")
        result = self.inspect(operation="submodule", target="external domain")
        self.assertEqual("conflict", result["status"])
        self.assertIn("INDEX_CONFLICT", self.codes(result))

    def sha256_source(self):
        source = self.workspace / "sha256 домен €"
        source.mkdir()
        git(source, "init", "--quiet", "--template=", "--object-format=sha256")
        (source / "domain-model").mkdir()
        (source / "domain-model/rule.md").write_bytes(b"SHA256 domain bytes\n")
        git(source, "add", "--", ".")
        git(source, "commit", "--quiet", "-m", "Exact SHA256 source")
        version = git(source, "rev-parse", "HEAD")
        self.assertEqual(64, len(version))
        return source, dict(self.declaration, root="../sha256 домен €", baseline=version)

    def test_source_06_sha256_source_and_parent_format_mismatch_stops_before_clone(self):
        _, source = self.sha256_source()
        result = self.inspect(source)
        self.assertEqual("ready", result["status"], "64-digit readable commits are supported for registration")
        before = self.snapshot()
        plan = self.inspect(source, operation="submodule", target="external domain")
        self.assertEqual("unavailable", plan["status"])
        self.assertIn("GIT_FORMAT_MISMATCH", self.codes(plan))
        self.assertEqual(before, self.snapshot())

    def test_source_06_matching_sha256_parent_runs_real_local_native_submodule(self):
        source, selected = self.sha256_source()
        root = self.workspace / "sha256 owner BC"
        root.mkdir()
        git(root, "init", "--quiet", "--template=", "--object-format=sha256")
        (root / "README.md").write_bytes(b"SHA256 project fixture\n")
        (root / "docs").mkdir()
        (root / "docs/development.md").write_bytes((self.root / "docs/development.md").read_bytes())
        (root / "bc-config.yaml").write_bytes(self.config.read_bytes())
        git(root, "add", "--", ".")
        git(root, "commit", "--quiet", "-m", "SHA256 owner baseline")
        before = source_bytes(source)
        plan = self.tool().inspect_domain_source(root, selected, operation="submodule", target="domain")
        self.assertEqual("ready", plan["status"], plan)
        result = self.tool().apply_domain_source(
            root, selected, operation="submodule", config_path="bc-config.yaml", expected=plan["preflight"],
            target="domain", owned=True, index_consent=True,
        )
        self.assertEqual("materialized", result["outcome"], result)
        self.assertEqual(selected["baseline"], git(root / "domain", "rev-parse", "HEAD"))
        self.assertIn("160000 " + selected["baseline"], git(root, "ls-files", "--stage", "--", "domain"))
        self.assertEqual(before, source_bytes(source))

    def test_source_11_recovery_records_prior_empty_target_and_exact_retained_module_hashes(self):
        target = self.root / "external domain"
        target.mkdir()
        module = self.tool()
        original = module._atomic_write

        def fail_gitmodules(path, *args, **kwargs):
            if Path(path).name == ".gitmodules":
                raise OSError("injected late metadata boundary")
            return original(path, *args, **kwargs)

        with patch.object(module, "_atomic_write", side_effect=fail_gitmodules):
            result = self.setup_submodule()
        self.assertEqual("partial", result["outcome"])
        records = {item["path"]: item for item in result["recovery"]["paths"]}
        self.assertEqual("empty-directory", records[str(target)]["prior_state"])
        metadata = self.root / ".git/modules/fixed-domain"
        self.assertEqual("absent", records[str(metadata)]["prior_state"])
        files = {item["path"]: item for item in records[str(metadata)]["files"]}
        self.assertEqual(digest((metadata / "HEAD").read_bytes()), files["HEAD"]["sha256"])
        self.assertEqual(digest((metadata / "index").read_bytes()), files["index"]["sha256"])

    def test_source_11_late_native_index_failure_reports_object_and_preserves_owner_lock(self):
        module = self.tool()
        original = module._native
        lock = self.root / ".git/index.lock"
        old_index = (self.root / ".git/index").read_bytes()
        source_before = source_bytes(self.source)

        def owner_lock_after_object(root, *args, **kwargs):
            value = original(root, *args, **kwargs)
            if args[:3] == ("hash-object", "-w", "--stdin"):
                lock.write_bytes(b"Concurrent owner lock; do not remove\n")
            return value

        with patch.object(module, "_native", side_effect=owner_lock_after_object):
            result = self.setup_submodule()
        self.assertEqual(("unavailable", "partial"), (result["status"], result["outcome"]))
        self.assertEqual(old_index, (self.root / ".git/index").read_bytes())
        self.assertEqual(source_before, source_bytes(self.source))
        self.assertEqual(b"Concurrent owner lock; do not remove\n", lock.read_bytes())
        object_id = next(item["stdout"].strip() for item in result["native"]
                         if "hash-object" in item["argv"] and "-w" in item["argv"])
        path = self.root / ".git/objects" / object_id[:2] / object_id[2:]
        records = {item["path"]: item for item in result["recovery"]["paths"]}
        self.assertIn(str(path), records, "The created parent Git object is part of exact partial state")
        self.assertEqual(digest(path.read_bytes()), records[str(path)]["sha256"])
        self.assertFalse(result["recovery"]["automatic_cleanup"])
        self.assertNotIn(str(lock), result["written"], "Observing an owner lock is not a product write")

    def test_source_10_cli_explicit_local_submodule_consent_runs_native_operation(self):
        _, plan = self.cli("--operation", "submodule", "--target", "external domain")
        run, result = self.cli("--operation", "submodule", "--target", "external domain",
                               "--apply", "--owned-target", "--index-consent", "--expect", plan["preflight"])
        self.assertEqual((0, "materialized"), (run.returncode, result["outcome"]), result)
        self.assertEqual(self.version, git(self.root / "external domain", "rev-parse", "HEAD"))


class MetadataFixture(DomainFixture):
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


class IndexIntentTests(MetadataFixture):
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


class WritableOverlapTests(MetadataFixture):
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


class GitMetadataTests(MetadataFixture):
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
                result = self.tool().inspect_domain_source(self.root, self.declaration)
                self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]), result)
                self.assertIn("BASE_UNAVAILABLE", self.codes(result))
                self.assertEqual(before, self.snapshot())
        head.write_bytes(original)

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


if __name__ == "__main__":
    unittest.main()
