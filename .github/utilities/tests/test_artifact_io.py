"""ENH-02 / ENH-06 Task 2: real file parsing, identity and input failures."""

from __future__ import annotations

import os
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from artifact_io import ArtifactInputError, parse_artifact, parse_artifacts
from tests.helpers import (
    KINDS, directory_link, metadata, temporary_workspace, write_artifact, write_metadata,
)


class ArtifactIOTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "root with spaces"
        self.root.mkdir()

    def assert_input_error(
        self, path: Path | str, code: str, *, line: int | None = None,
        root: object = None,
    ) -> ArtifactInputError:
        with self.assertRaises(ArtifactInputError) as caught:
            parse_artifact(path, self.root if root is None else root)
        error = caught.exception
        self.assertEqual(error.code, code)
        self.assertGreaterEqual(error.line, 1)
        if line is not None:
            self.assertEqual(error.line, line)
        self.assertTrue(error.message.strip())
        self.assertIn(code, str(error))
        self.assertIn(str(error.path), str(error))
        return error

    def test_read_retains_identity_source_body_and_absolute_location(self) -> None:
        body = '# REQ-001：本地来源\n\n<a id="req-001-ac-01"></a>\n### REQ-001-AC-01：判据\n'
        path = write_metadata(self.root, metadata(), body, "资料 with spaces/REQ-001.md")
        original = path.read_bytes()
        before = Path.cwd()
        artifact = parse_artifact(Path("资料 with spaces/REQ-001.md"), self.root)
        self.assertEqual(artifact.key, "sample/CTX-001/REQ-001")
        self.assertEqual(artifact.id, "REQ-001")
        self.assertEqual(artifact.scope, "sample/CTX-001")
        self.assertEqual(artifact.content_state, "draft")
        self.assertEqual(artifact.path, path.resolve())
        self.assertEqual(artifact.relative_path, "资料 with spaces/REQ-001.md")
        self.assertEqual(artifact.location.path, path.resolve())
        self.assertEqual(artifact.location.line, 1)
        self.assertEqual(artifact.body_start_line, 8)
        self.assertEqual(artifact.source, original.decode("utf-8"))
        self.assertEqual(artifact.body, body)
        self.assertEqual(artifact.upstream, ())
        self.assertEqual(artifact.targets, ())
        self.assertEqual(artifact.confirmation, None)
        self.assertEqual(Path.cwd(), before)
        self.assertEqual(path.read_bytes(), original)

    def test_only_owner_headings_with_stable_anchors_are_acceptances(self) -> None:
        body = (
            "# REQ-001：Owner\n"
            "Referenced REQ-998-AC-01 and [REQ-999-AC-01](elsewhere.md#req-999-ac-01).\n\n"
            '<a id="req-001-ac-01"></a>\n'
            "### REQ-001-AC-01：First\n\n"
            "```markdown\n"
            '<a id="req-001-ac-88"></a>\n'
            "### REQ-001-AC-88：not an item\n"
            "```\n"
            "~~~~ markdown\n"
            '<a id="req-001-ac-89"></a>\n'
            "### REQ-001-AC-89：also code\n"
            "~~~\n"
            "~~~~\n"
            "<!--\n"
            '<a id="req-001-ac-90"></a>\n'
            "### REQ-001-AC-90：comment\n"
            "-->\n\n"
            '<a id="req-001-ac-02"></a>\n'
            "### REQ-001-AC-02: Second\n\n"
            '<a id="req-999-ac-03"></a>\n'
            "### REQ-999-AC-03：other owner\n"
        )
        path = write_metadata(self.root, metadata(), body)
        artifact = parse_artifact(path, self.root)
        self.assertEqual(artifact.acceptance_ids, (
            "sample/CTX-001/REQ-001#req-001-ac-01",
            "sample/CTX-001/REQ-001#req-001-ac-02",
        ))
        self.assertEqual(tuple(item.id for item in artifact.acceptances),
                         ("REQ-001-AC-01", "REQ-001-AC-02"))
        self.assertEqual(tuple(item.location.line for item in artifact.acceptances), (12, 29))
        self.assertEqual(tuple(item.anchor_location.line for item in artifact.acceptances), (11, 28))
        self.assertEqual(artifact.acceptances[1].anchor, "req-001-ac-02")
        self.assertEqual(artifact.acceptances[0].location.path, path.resolve())

    def test_design_verification_item_retains_full_owner(self) -> None:
        path = write_artifact(
            self.root, id="ABB-001", kind="architecture-building-block",
            acceptance_ids=("ABB-001-VC-01",),
        )
        self.assertEqual(parse_artifact(path, self.root).acceptance_ids,
                         ("sample/CTX-001/ABB-001#abb-001-vc-01",))

    def test_targets_keep_owner_anchor_criterion_and_optional_test_id(self) -> None:
        data = metadata(id="VT-001", kind="verification-test", upstream=[
            "sample/CTX-001/SR-001", "sample/CTX-002/SR-001#sr-001-ac-02",
        ], targets=[
            {"target": "sample/CTX-001/SR-001#sr-001-ac-01",
             "criterionAnchor": "criterion-01", "testId": "native.suite::test_reject"},
            {"target": "sample/CTX-002/SR-001#sr-001-ac-01",
             "criterionAnchor": "criterion-02"},
        ])
        path = write_metadata(self.root, data, (
            '# VT-001\n<a id="criterion-01"></a>\n## First criterion\n'
            '<a id="criterion-02"></a>\n## Second criterion\n'
        ))
        artifact = parse_artifact(path, self.root)
        self.assertEqual(artifact.upstream, (
            "sample/CTX-001/SR-001", "sample/CTX-002/SR-001#sr-001-ac-02",
        ))
        first, second = artifact.targets
        self.assertEqual(first.target, "sample/CTX-001/SR-001#sr-001-ac-01")
        self.assertEqual(first.criterion_anchor, "criterion-01")
        self.assertEqual(first.test_id, "native.suite::test_reject")
        self.assertEqual(second.target, "sample/CTX-002/SR-001#sr-001-ac-01")
        self.assertIsNone(second.test_id)
        self.assertEqual(first.location.path, path.resolve())
        self.assertGreater(first.location.line, 1)

    def test_confirmed_declaration_is_preserved_without_authenticating_person(self) -> None:
        path = write_metadata(self.root, metadata(contentState="confirmed", confirmation={
            "by": "Named source", "reference": "records/review.md#decision",
            "baseline": "frozen-review-01",
        }))
        declaration = parse_artifact(path, self.root).confirmation
        self.assertEqual(declaration.by, "Named source")
        self.assertEqual(declaration.reference, "records/review.md#decision")
        self.assertEqual(declaration.baseline, "frozen-review-01")
        self.assertEqual(declaration.location.path, path.resolve())

    def test_returned_records_are_immutable(self) -> None:
        path = write_artifact(self.root, acceptance_ids=("REQ-001-AC-01",))
        artifact = parse_artifact(path, self.root)
        with self.assertRaises(FrozenInstanceError):
            artifact.scope = "changed/CTX-001"
        with self.assertRaises(FrozenInstanceError):
            artifact.acceptances[0].anchor = "changed"
        with self.assertRaises(FrozenInstanceError):
            artifact.location.line = 500
        self.assertIsInstance(artifact.acceptances, tuple)

    def test_utf8_bom_and_crlf_are_preserved_without_bom_in_decoded_source(self) -> None:
        for newline in ("\n", "\r\n"):
            for bom in (False, True):
                with self.subTest(newline=repr(newline), bom=bom):
                    path = write_metadata(
                        self.root, metadata(), "# REQ-001：中文\n",
                        newline=newline, bom=bom,
                    )
                    artifact = parse_artifact(path, self.root)
                    self.assertEqual(artifact.body, f"# REQ-001：中文{newline}")
                    self.assertEqual(artifact.source, path.read_bytes().decode("utf-8-sig"))
                    self.assertEqual(artifact.body_start_line, 8)

    def test_different_scopes_can_use_same_id(self) -> None:
        first = write_artifact(self.root, scope="sample/CTX-001", relative_path="one/REQ-001.md")
        second = write_artifact(self.root, scope="sample/CTX-002", relative_path="two/REQ-001.md")
        result = parse_artifacts((first, second), self.root)
        self.assertIsInstance(result, tuple)
        self.assertEqual(tuple(artifact.key for artifact in result),
                         ("sample/CTX-001/REQ-001", "sample/CTX-002/REQ-001"))

    def test_collection_rejects_same_scope_duplicate_with_both_locations(self) -> None:
        first = write_artifact(self.root, relative_path="one/REQ-001.md")
        second = write_artifact(self.root, relative_path="two/REQ-001.md")
        with self.assertRaises(ArtifactInputError) as caught:
            parse_artifacts((first, second), self.root)
        self.assertEqual(caught.exception.code, "DUPLICATE_ARTIFACT_ID")
        self.assertEqual(caught.exception.path, second.resolve())
        self.assertEqual(caught.exception.line, 3)
        self.assertIn(str(first.resolve()), caught.exception.message)
        self.assertIn("sample/CTX-001/REQ-001", caught.exception.message)

    def test_collection_parses_only_explicit_inputs_and_propagates_errors(self) -> None:
        good = write_artifact(self.root)
        bad = self.root / "not-selected.md"
        bad.write_text("not valid metadata", encoding="utf-8")
        self.assertEqual(len(parse_artifacts((good,), self.root)), 1)
        self.assertEqual(parse_artifacts((), self.root), ())
        with self.assertRaises(ArtifactInputError) as caught:
            parse_artifacts((good, bad), self.root)
        self.assertEqual(caught.exception.code, "MISSING_FRONTMATTER")

    def test_rejects_unknown_schema_version(self) -> None:
        self.assert_input_error(write_artifact(self.root, schema_version=9),
                                "UNSUPPORTED_SCHEMA_VERSION", line=2)

    def test_rejects_boolean_string_float_and_null_schema_versions(self) -> None:
        for value in (True, False, "1", 1.0, None):
            with self.subTest(value=repr(value)):
                self.assert_input_error(write_metadata(self.root, metadata(schemaVersion=value)),
                                        "UNSUPPORTED_SCHEMA_VERSION", line=2)

    def test_rejects_unknown_kind_and_content_state(self) -> None:
        for field, value, code, line in (
            ("kind", "custom-plugin", "INVALID_KIND", 4),
            ("kind", 32, "INVALID_KIND", 4),
            ("contentState", "approved", "INVALID_CONTENT_STATE", 6),
            ("contentState", None, "INVALID_CONTENT_STATE", 6),
        ):
            with self.subTest(field=field, value=value):
                self.assert_input_error(write_metadata(self.root, metadata(**{field: value})),
                                        code, line=line)

    def test_rejects_each_missing_required_field(self) -> None:
        for field in ("schemaVersion", "id", "kind", "scope", "contentState"):
            with self.subTest(field=field):
                data = metadata()
                del data[field]
                error = self.assert_input_error(write_metadata(self.root, data), "INVALID_METADATA")
                self.assertIn(field, error.message)

    def test_rejects_invalid_identity_and_scope(self) -> None:
        for field, value in (
            ("id", ""), ("id", "../REQ-001"), ("id", "REQ-001\n"),
            ("id", "REQ 001"), ("scope", "CTX-001"), ("scope", "../CTX-001"),
            ("scope", "sample/CTX-001/extra"), ("scope", None),
        ):
            with self.subTest(field=field, value=value):
                self.assert_input_error(write_metadata(self.root, metadata(**{field: value})),
                                        "INVALID_METADATA")

    def test_rejects_provided_malformed_upstream_instead_of_defaulting(self) -> None:
        for value in (None, "", {}, 12, [None], ["REQ-001#req-001-ac-01"],
                      ["sample/CTX-001/REQ-001", "sample/CTX-001/REQ-001"]):
            with self.subTest(value=value):
                self.assert_input_error(write_metadata(self.root, metadata(upstream=value)),
                                        "INVALID_METADATA")

    def test_rejects_provided_malformed_targets_instead_of_defaulting(self) -> None:
        for value in (None, {}, "", 1, [None], ["sample/CTX-001/REQ-001#req-001-ac-01"]):
            with self.subTest(value=value):
                self.assert_input_error(write_metadata(self.root, metadata(targets=value)),
                                        "INVALID_METADATA")

    def test_rejects_target_without_canonical_owner_or_anchor(self) -> None:
        for ref in (
            "AC-01", "SR-001#sr-001-ac-01", "sample/CTX-001/SR-001",
            "sample/../SR-001#sr-001-ac-01", "sample/CTX-001/SR-001#",
            "https://example.invalid/SR-001#sr-001-ac-01",
            "sample/CTX-001/SR-001#sr-001-ac-01\n",
        ):
            with self.subTest(ref=ref):
                data = metadata(targets=[{"target": ref, "criterionAnchor": "criterion"}])
                self.assert_input_error(write_metadata(self.root, data), "INVALID_METADATA")

    def test_rejects_duplicate_target_records(self) -> None:
        target = {"target": "sample/CTX-001/SR-001#sr-001-ac-01", "criterionAnchor": "criterion"}
        self.assert_input_error(write_metadata(self.root, metadata(targets=[target, dict(target)])),
                                "INVALID_METADATA")

    def test_rejects_missing_local_criterion_anchor_even_if_it_occurs_in_code(self) -> None:
        data = metadata(targets=[{
            "target": "sample/CTX-001/SR-001#sr-001-ac-01", "criterionAnchor": "criterion",
        }])
        path = write_metadata(self.root, data, '```md\n<a id="criterion"></a>\n```\n')
        error = self.assert_input_error(path, "MISSING_CRITERION_ANCHOR", line=9)
        self.assertIn("criterion", error.message)

    def test_rejects_missing_or_wrong_acceptance_anchor(self) -> None:
        for body in ("### REQ-001-AC-01：missing\n",
                     '<a id="req-999-ac-01"></a>\n### REQ-001-AC-01：wrong owner\n'):
            with self.subTest(body=body):
                self.assert_input_error(write_metadata(self.root, metadata(), body),
                                        "MISSING_ACCEPTANCE_ANCHOR")

    def test_rejects_duplicate_body_anchor(self) -> None:
        body = '<a id="criterion"></a>\n## First\n<a id="criterion"></a>\n## Second\n'
        self.assert_input_error(write_metadata(self.root, metadata(), body),
                                "DUPLICATE_ANCHOR", line=10)

    def test_rejects_missing_or_blank_confirmation_fields(self) -> None:
        for declaration in (None, {}, {"by": "  ", "reference": "review.md", "baseline": "v1"},
                            {"by": "Person", "reference": "\t", "baseline": "v1"},
                            {"by": "Person", "reference": "review.md", "baseline": ""},
                            {"by": 12, "reference": "review.md", "baseline": "v1"}):
            with self.subTest(declaration=declaration):
                self.assert_input_error(write_metadata(self.root, metadata(
                    contentState="confirmed", confirmation=declaration)), "INVALID_METADATA")
        self.assert_input_error(write_metadata(self.root, metadata(contentState="confirmed")),
                                "INVALID_METADATA")

    def test_rejects_duplicate_yaml_keys_at_top_and_nested_depths(self) -> None:
        for suffix, line in (
            ("scope: other/CTX-002\n", 7),
            ("confirmation:\n  by: Person\n  reference: review.md\n  baseline: v1\n  by: Other\n", 11),
            ("targets:\n  - target: sample/CTX-001/SR-001#sr-001-ac-01\n"
             "    criterionAnchor: a\n    criterionAnchor: b\n", 10),
        ):
            with self.subTest(suffix=suffix):
                path = self.root / "duplicate.md"
                path.write_text(
                    "---\nschemaVersion: 1\nid: REQ-001\nkind: stakeholder-requirement\n"
                    "scope: sample/CTX-001\ncontentState: draft\n" + suffix + "---\n",
                    encoding="utf-8",
                )
                error = self.assert_input_error(path, "DUPLICATE_YAML_KEY", line=line)
                self.assertIn("duplicate", error.message.lower())

    def test_rejects_unsafe_and_unknown_yaml_tags_without_execution(self) -> None:
        marker = self.root / "must-not-exist"
        for tag in (
            "!!python/object/apply:os.system ['echo must-not-run']",
            "!external 'anything'", f"!!python/object/apply:pathlib.Path.touch ['{marker.as_posix()}']",
        ):
            with self.subTest(tag=tag):
                path = self.root / "unsafe.md"
                path.write_text("---\nschemaVersion: " + tag + "\n---\n", encoding="utf-8")
                self.assert_input_error(path, "INVALID_YAML", line=2)
                self.assertFalse(marker.exists())

    def test_rejects_malformed_yaml_with_original_location_and_cause(self) -> None:
        path = self.root / "broken.md"
        path.write_text("---\nschemaVersion: 1\nid: [unfinished\n---\n", encoding="utf-8")
        error = self.assert_input_error(path, "INVALID_YAML", line=4)
        self.assertIsNotNone(error.__cause__)
        self.assertIn("expected", error.message)

    def test_invalid_values_for_safe_yaml_tags_still_raise_located_input_errors(self) -> None:
        for value in ("!!int not-an-integer", "!!bool maybe", "!!timestamp 2026-99-99",
                      "!!map scalar", "!!int ''", "!!timestamp not-a-date",
                      "!!float not-a-number"):
            with self.subTest(value=value):
                path = self.root / "malformed-safe-tag.md"
                path.write_text("---\nschemaVersion: " + value + "\n---\n", encoding="utf-8")
                error = self.assert_input_error(path, "INVALID_YAML", line=2)
                self.assertIsNotNone(error.__cause__)

    def test_rejects_recursive_alias_and_duplicate_merge_override(self) -> None:
        for contents, code in (
            ("---\nschemaVersion: 1\nextra: &cycle [*cycle]\n---\n", "INVALID_YAML"),
            ("---\nschemaVersion: 1\nid: REQ-001\nkind: stakeholder-requirement\n"
             "scope: sample/CTX-001\ncontentState: draft\n"
             "confirmation:\n  <<: {by: First, reference: review.md, baseline: v1}\n"
             "  by: Second\n---\n", "DUPLICATE_YAML_KEY"),
        ):
            with self.subTest(code=code):
                path = self.root / "aliases.md"
                path.write_text(contents, encoding="utf-8")
                self.assert_input_error(path, code)

    def test_rejects_repeated_merge_keys_even_when_merged_fields_do_not_overlap(self) -> None:
        path = self.root / "duplicate-merge.md"
        for declaration, line in (
            ("confirmation:\n  <<: {by: Person}\n"
             "  <<: {reference: review.md, baseline: v1}\n", 9),
            ("confirmation:\n  <<:\n    <<: {by: Person}\n"
             "    <<: {reference: review.md, baseline: v1}\n", 10),
        ):
            with self.subTest(declaration=declaration):
                path.write_text(
                    "---\nschemaVersion: 1\nid: REQ-001\nkind: stakeholder-requirement\n"
                    "scope: sample/CTX-001\ncontentState: confirmed\n" + declaration
                    + "---\n# REQ-001\n", encoding="utf-8",
                )
                self.assert_input_error(path, "DUPLICATE_YAML_KEY", line=line)

    def test_rejects_nonmapping_empty_multidocument_and_nonstring_yaml_keys(self) -> None:
        for contents, code in (
            ("---\n---\n# Empty\n", "INVALID_METADATA"),
            ("---\n- a\n- b\n---\n", "INVALID_METADATA"),
            ("---\ntrue\n---\n", "INVALID_METADATA"),
            ("---\n1: value\n---\n", "INVALID_YAML"),
            ("---\nschemaVersion: 1\n...\nid: REQ-001\n---\n", "INVALID_YAML"),
        ):
            with self.subTest(contents=contents):
                path = self.root / "mapping.md"
                path.write_text(contents, encoding="utf-8")
                self.assert_input_error(path, code)

    def test_rejects_missing_and_unterminated_frontmatter(self) -> None:
        for contents, code in (
            ("# Plain Markdown\n", "MISSING_FRONTMATTER"),
            ("", "MISSING_FRONTMATTER"),
            ("---\nschemaVersion: 1\n", "UNTERMINATED_FRONTMATTER"),
        ):
            with self.subTest(contents=contents):
                path = self.root / "frontmatter.md"
                path.write_text(contents, encoding="utf-8")
                self.assert_input_error(path, code, line=1)

    def test_rejects_invalid_utf8_with_original_line_and_cause(self) -> None:
        path = self.root / "encoding.md"
        path.write_bytes(b"---\nschemaVersion: 1\nid: \xff\n---\n")
        error = self.assert_input_error(path, "INVALID_ENCODING", line=3)
        self.assertIsInstance(error.__cause__, UnicodeDecodeError)
        self.assertIn("decode", error.message)

    def test_invalid_utf8_bom_error_line_uses_decoder_input_offset(self) -> None:
        path = self.root / "bom-encoding.md"
        path.write_bytes(b"\xef\xbb\xbf---\n\xff\n")
        error = self.assert_input_error(path, "INVALID_ENCODING", line=2)
        self.assertIsInstance(error.__cause__, UnicodeDecodeError)

    def test_rejects_nonexistent_and_nondirectory_roots(self) -> None:
        path = write_artifact(self.root)
        for root in (self.workspace / "absent", path, 9, True, b"bytes-root"):
            with self.subTest(root=root):
                self.assert_input_error(path, "INVALID_ROOT", root=root, line=1)

    def test_invalid_root_errors_identify_root_in_both_apis(self) -> None:
        artifact_path = write_artifact(self.root)
        root_file = self.workspace / "not a root directory.txt"
        root_file.write_text("A real file, not a root directory.\n", encoding="utf-8")
        for invalid_root in (self.workspace / "missing root", root_file, None, 9):
            for api, selected in (
                (parse_artifact, artifact_path),
                (parse_artifacts, (artifact_path,)),
                (parse_artifacts, ()),
            ):
                with self.subTest(root=invalid_root, api=api.__name__, selected=selected):
                    with self.assertRaises(ArtifactInputError) as caught:
                        api(selected, invalid_root)
                    error = caught.exception
                    self.assertEqual(
                        (error.code, error.path, error.line),
                        ("INVALID_ROOT", str(invalid_root), 1),
                    )

    def test_rejects_null_root_even_for_empty_collection(self) -> None:
        with self.assertRaises(ArtifactInputError) as caught:
            parse_artifacts((), None)
        self.assertEqual(caught.exception.code, "INVALID_ROOT")

    def test_rejects_invalid_path_types_and_missing_file(self) -> None:
        for path in (None, 7, True, b"bytes-path"):
            with self.subTest(path=path):
                self.assert_input_error(path, "INVALID_PATH", line=1)
        self.assert_input_error(self.root / "missing.md", "FILE_NOT_FOUND", line=1)

    def test_rejects_directory_instead_of_file(self) -> None:
        self.assert_input_error(self.root, "INVALID_PATH", line=1)

    def test_rejects_relative_traversal_and_absolute_outside_root(self) -> None:
        outside = self.workspace / "root with spaces-shadow"
        outside.mkdir()
        path = write_artifact(outside)
        for requested in (path, Path("../root with spaces-shadow/REQ-001.md")):
            with self.subTest(requested=requested):
                self.assert_input_error(requested, "OUTSIDE_ROOT", line=1)

    def test_rejects_outside_root_directory_link_target(self) -> None:
        outside = self.workspace / "outside"
        outside.mkdir()
        write_artifact(outside)
        with directory_link(self.root / "external-link", outside) as link:
            error = self.assert_input_error(link / "REQ-001.md", "OUTSIDE_ROOT", line=1)
            self.assertIn(str(outside.resolve()), error.message)

    def test_allows_internal_directory_link_and_returns_real_path(self) -> None:
        internal = self.root / "actual"
        internal.mkdir()
        original = write_artifact(internal)
        with directory_link(self.root / "internal-link", internal) as link:
            artifact = parse_artifact(link / "REQ-001.md", self.root)
            self.assertEqual(artifact.path, original.resolve())
            self.assertEqual(artifact.relative_path, "actual/REQ-001.md")

    def test_read_failure_is_not_an_empty_artifact(self) -> None:
        path = write_artifact(self.root)
        if os.name == "nt":
            import msvcrt
            with path.open("r+b") as locked:
                msvcrt.locking(locked.fileno(), msvcrt.LK_NBLCK, 1)
                try:
                    error = self.assert_input_error(path, "FILE_READ_ERROR", line=1)
                finally:
                    locked.seek(0)
                    msvcrt.locking(locked.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            previous = path.stat().st_mode
            path.chmod(0)
            try:
                if os.access(path, os.R_OK):
                    self.skipTest("Host privilege bypasses chmod; unreadable-file behavior not tested")
                error = self.assert_input_error(path, "FILE_READ_ERROR", line=1)
            finally:
                path.chmod(previous)
        self.assertIsInstance(error.__cause__, OSError)
        self.assertTrue(error.__cause__.strerror)


def _kind_case(kind: str):
    def test(self: ArtifactIOTests) -> None:
        path = write_artifact(self.root, kind=kind)
        artifact = parse_artifact(path, self.root)
        self.assertEqual(artifact.kind, kind)
        self.assertEqual(artifact.key, "sample/CTX-001/REQ-001")
        self.assertEqual(artifact.body, "# REQ-001：本地夹具\n\n")
    return test


for _kind in KINDS:
    setattr(ArtifactIOTests, "test_parses_kind_" + _kind.replace("-", "_"), _kind_case(_kind))
