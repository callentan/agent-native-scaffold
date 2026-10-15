"""ENH-07 / Task6 CHECK-01..13: real files, exact Git objects and CLI behavior.

CHECK-14 belongs to the execution-receipt harness, not a test of its own existence.
Expected identities, counts, locations and outcomes below come from the fixtures,
not the checker. Git stdout is never mocked.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from artifact_io import parse_artifact
from check_artifacts import run_check
from tests.helpers import (
    WORKTREE, directory_link, git, metadata, seed_git_repo, temporary_workspace,
    write_artifact, write_metadata,
)


SCRIPT = WORKTREE / ".github" / "utilities" / "check_artifacts.py"


def source_bytes(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


class ArtifactCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "正式资料 Ω with spaces"
        self.root.mkdir()

    def finding(self, report, code: str):
        matches = [item for item in report.findings if item.code == code]
        self.assertTrue(matches, (code, report))
        return matches[0]

    def cli(self, *arguments: str, cwd: Path | None = None, env: dict | None = None):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(SCRIPT),
             "--root", str(self.root), *arguments],
            cwd=cwd or self.workspace, env=env, shell=False,
            capture_output=True, text=True, encoding="utf-8",
        )

    def commit_files(self) -> str:
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Local artifact baseline")
        return git(self.root, "rev-parse", "HEAD")

    def test_clean_reports_exact_owners_and_raw_bom_crlf_bytes_without_writes(self) -> None:
        # Break caught: treating a real selection as empty, or hashing decoded text.
        first = write_metadata(
            self.root, metadata(), '# REQ-001：范围\n<a id="req-001-ac-01"></a>\n'
            '### REQ-001-AC-01：可观察条件\n',
            "需求 空格/REQ-001.md", newline="\r\n", bom=True,
        )
        write_artifact(self.root, id="SR-001", kind="software-requirement")
        original = source_bytes(self.root)
        cwd = Path.cwd()
        report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertEqual(2, report.checked_count)
        self.assertEqual(2, report.attempted_count)
        self.assertEqual((), report.findings)
        self.assertEqual(
            [("SR-001.md", "sample/CTX-001/SR-001"),
             ("需求 空格/REQ-001.md", "sample/CTX-001/REQ-001")],
            [(item.path, item.owner) for item in report.baseline.files if item.role == "formal"],
        )
        record = next(item for item in report.baseline.files if item.path == "需求 空格/REQ-001.md")
        self.assertEqual(hashlib.sha256(first.read_bytes()).hexdigest(), record.sha256)
        self.assertEqual(len(first.read_bytes()), record.size)
        self.assertEqual("working-tree", report.baseline.target)
        self.assertIsNone(report.baseline.base_sha)
        self.assertEqual(report, run_check(self.root))
        self.assertEqual(original, source_bytes(self.root))
        self.assertEqual(cwd, Path.cwd())

    def test_duplicate_identity_keeps_first_and_second_source_locations(self) -> None:
        first = write_artifact(self.root, relative_path="a/REQ-001.md")
        second = write_artifact(self.root, relative_path="b/REQ-001.md")
        report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.assertEqual(2, report.checked_count)
        item = self.finding(report, "DUPLICATE_ARTIFACT_ID")
        self.assertEqual(str(second.resolve()), item.path)
        self.assertEqual(3, item.line)
        self.assertEqual("sample/CTX-001/REQ-001", item.owner)
        self.assertEqual(first.resolve(), item.related.path)
        self.assertEqual(3, item.related.line)

    def test_same_id_in_different_scopes_is_not_duplicate(self) -> None:
        write_artifact(self.root, scope="sample/CTX-001", relative_path="a/REQ-001.md")
        write_artifact(self.root, scope="sample/CTX-002", relative_path="b/REQ-001.md")
        report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertEqual(2, report.checked_count)

    def test_formal_filename_cannot_hide_removed_frontmatter(self) -> None:
        path = self.root / "REQ-001-purpose.md"
        path.write_text("# Requirement\n", encoding="utf-8")
        report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.assertEqual(1, report.attempted_count)
        self.assertEqual(0, report.checked_count)
        self.assertEqual(1, self.finding(report, "MISSING_FRONTMATTER").line)

    def test_missing_each_required_field_is_input_error_not_exclusion(self) -> None:
        for field in ("schemaVersion", "id", "kind", "scope", "contentState"):
            with self.subTest(field=field):
                data = metadata()
                del data[field]
                write_metadata(self.root, data)
                report = run_check(self.root)
                self.assertEqual("input-error", report.status)
                self.assertEqual(1, report.attempted_count)
                self.assertEqual(0, report.checked_count)
                self.finding(report, "INVALID_METADATA")

    def test_formal_metadata_discovers_readme_and_arbitrary_filename(self) -> None:
        write_artifact(self.root, relative_path="README.md")
        write_artifact(self.root, id="UC-002", kind="use-case", relative_path="ordinary-name.md")
        report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertEqual(2, report.checked_count)

    def test_malformed_metadata_in_non_id_filename_is_still_attempted(self) -> None:
        path = self.root / "ordinary-name.md"
        for source, code in (
            ("---\nschemaVersion: [\n---\n# Broken\n", "INVALID_YAML"),
            ("---\nschemaVersion 1\nkind: use-case\n---\n# Broken\n", "INVALID_YAML"),
            ("---\nschemaVersion: 1\nid: UC-001\n", "UNTERMINATED_FRONTMATTER"),
        ):
            with self.subTest(source=source):
                path.write_text(source, encoding="utf-8")
                report = run_check(self.root)
                self.assertEqual("input-error", report.status)
                self.assertEqual(1, report.attempted_count)
                self.finding(report, code)

    def test_removed_opening_delimiter_does_not_hide_formal_metadata(self) -> None:
        path = write_artifact(self.root, relative_path="ordinary.md")
        path.write_bytes(path.read_bytes().removeprefix(b"---\n"))
        report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.assertEqual(1, report.attempted_count)
        self.finding(report, "MISSING_FRONTMATTER")

    def test_fix1_indented_opening_stays_attempted_in_full_api_and_cli(self) -> None:
        # Finding 1: neither filename nor H1 provides a fallback formal ID.
        path = write_metadata(self.root, metadata(), "# Requirement\n", "ordinary.md")
        path.write_bytes(b" " + path.read_bytes())
        for companion, attempted, checked in ((False, 1, 0), (True, 2, 1)):
            if companion:
                write_artifact(self.root, id="SR-002", kind="software-requirement")
            before = source_bytes(self.root)
            report = run_check(self.root)
            result = self.cli()  # Execute the actual script even when the API assertion fails.
            for interface, payload, exit_code in (
                ("api", report.to_dict(), None),
                ("cli", json.loads(result.stdout), result.returncode),
            ):
                with self.subTest(companion=companion, interface=interface):
                    if exit_code is not None:
                        self.assertEqual(2, exit_code, result.stdout + result.stderr)
                    self.assertEqual("input-error", payload["status"])
                    self.assertEqual(attempted, payload["attempted_count"])
                    self.assertEqual(checked, payload["checked_count"])
                    self.assertNotIn("ordinary.md", [item["path"] for item in payload["excluded"]])
                    self.assertEqual(
                        [("MISSING_FRONTMATTER", str(path.resolve()), 1)],
                        [(item["code"], item["path"], item["line"]) for item in payload["findings"]],
                    )
            self.assertEqual(before, source_bytes(self.root))

    def test_fix1_malformed_opening_selection_does_not_search_prose_or_literals(self) -> None:
        fields = (
            "schemaVersion: 1\nid: REQ-001\nkind: stakeholder-requirement\n"
            "scope: sample/CTX-001\ncontentState: draft\n"
        )
        for source in (
            " ---\nOrdinary explanatory prose.\n" + fields + "# Guide\n",
            " ---\n# Guide\n" + fields,
            " ---\n```yaml\n" + fields + "```\n# Guide\n",
            " ---\n~~~yaml\n" + fields + "~~~\n# Guide\n",
            " ---\n<!--\n" + fields + "-->\n# Guide\n",
            "Ordinary prose before the delimiter.\n ---\n" + fields + "# Guide\n",
            "    ---\n" + "".join("    " + line + "\n" for line in fields.splitlines()) + "# Guide\n",
            "\t---\n" + "".join("\t" + line + "\n" for line in fields.splitlines()) + "# Guide\n",
        ):
            with self.subTest(source=source):
                path = self.root / "ordinary.md"
                path.write_text(source, encoding="utf-8")
                before = path.read_bytes()
                report = run_check(self.root)
                self.assertEqual("empty", report.status)
                self.assertEqual((0, 0), (report.attempted_count, report.checked_count))
                self.assertEqual((), report.findings)
                self.assertIn(("ordinary.md", "LIGHTWEIGHT_GUIDE"),
                              [(item.path, item.reason) for item in report.excluded])
                self.assertEqual(before, path.read_bytes())

    def test_fix1_tilde_info_comment_keeps_broken_link_in_api_and_cli(self) -> None:
        # Finding 2, verbatim body: the real missing link is on source line 12.
        path = write_metadata(
            self.root, metadata(),
            "# Requirement\n~~~ text <!--\nexample\n~~~\n[broken](missing.md)\n"
            '<a id="req-001-ac-01"></a>\n### REQ-001-AC-01: Observable condition\n',
        )
        before = path.read_bytes()
        report = run_check(self.root)
        result = self.cli()
        for interface, payload, exit_code in (
            ("api", report.to_dict(), None),
            ("cli", json.loads(result.stdout), result.returncode),
        ):
            with self.subTest(interface=interface):
                if exit_code is not None:
                    self.assertEqual(1, exit_code, result.stdout + result.stderr)
                self.assertEqual("invalid", payload["status"])
                self.assertEqual((1, 1), (payload["attempted_count"], payload["checked_count"]))
                self.assertEqual(
                    [("BROKEN_LINK", str(path.resolve()), 12, "sample/CTX-001/REQ-001", "missing.md")],
                    [(item["code"], item["path"], item["line"], item["owner"], item["target"])
                     for item in payload["findings"]],
                )
        self.assertEqual(before, path.read_bytes())

    def test_fix1_supported_fences_keep_info_and_content_comments_literal(self) -> None:
        for opener, short_close, closer in (
            ("~~~ text <!--", "~~", "~~~"),
            ("``` text <!--", "``", "```"),
            ("   ~~~~ text <!--", "~~~", "  ~~~~~"),
            ("  ```` text <!--", "```", "   `````"),
            ("~~~ text `literal` <!--", "~~", "~~~~"),
            ("~~~ text <!-- closed -->", "~~", "~~~"),
            ("<!-- note -->~~~ text <!--", "~~", "~~~"),
        ):
            path = write_metadata(
                self.root, metadata(),
                f"# Requirement\n{opener}\n[hidden](hidden.md) <!--\n"
                '<a id="req-001-ac-99"></a>\n### REQ-001-AC-99: Literal only\n'
                f"{short_close}\n{closer}\n[broken](missing.md)\n"
                '<a id="req-001-ac-01"></a>\n### REQ-001-AC-01: Observable condition\n',
            )
            before = path.read_bytes()
            report = run_check(self.root)
            result = self.cli()
            for interface, payload, exit_code in (
                ("api", report.to_dict(), None),
                ("cli", json.loads(result.stdout), result.returncode),
            ):
                with self.subTest(opener=opener, interface=interface):
                    if exit_code is not None:
                        self.assertEqual(1, exit_code, result.stdout + result.stderr)
                    self.assertEqual("invalid", payload["status"])
                    self.assertEqual([("BROKEN_LINK", 15, "missing.md")],
                                     [(item["code"], item["line"], item["target"])
                                      for item in payload["findings"]])
            self.assertEqual(before, path.read_bytes())

    def test_fix1_fence_text_inside_document_comment_does_not_open_code(self) -> None:
        path = write_metadata(
            self.root, metadata(),
            "# Requirement\n<!-- document comment\n~~~ text <!--\n[hidden](hidden.md)\n"
            '<a id="req-001-ac-99"></a>\n### REQ-001-AC-99: Hidden\n-->\n'
            '[broken](missing.md)\n<a id="req-001-ac-01"></a>\n'
            "### REQ-001-AC-01: Observable condition\n",
        )
        before = path.read_bytes()
        report = run_check(self.root)
        result = self.cli()
        self.assertEqual("invalid", report.status)
        self.assertEqual([("BROKEN_LINK", 15, "missing.md")],
                         [(item.code, item.line, item.target) for item in report.findings])
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual("invalid", json.loads(result.stdout)["status"])
        self.assertEqual(before, path.read_bytes())

    def test_formal_h1_with_colon_does_not_hide_removed_metadata(self) -> None:
        (self.root / "ordinary.md").write_text("# REQ-001：Actual owner\n", encoding="utf-8")
        report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.finding(report, "MISSING_FRONTMATTER")

    def test_bad_metadata_uses_existing_parser_error_codes_and_lines(self) -> None:
        good = write_artifact(self.root).read_text(encoding="utf-8")
        path = self.root / "REQ-001.md"
        for source, code, line in (
            (good.replace("kind: stakeholder-requirement", "kind: plugin-kind"), "INVALID_KIND", 4),
            (good.replace("schemaVersion: 1", "schemaVersion: true"), "UNSUPPORTED_SCHEMA_VERSION", 2),
            (good.replace("id: REQ-001", "id: REQ-001\nid: REQ-002"), "DUPLICATE_YAML_KEY", 4),
            (good.replace("id: REQ-001", "id: !!python/object:os.system {}"), "INVALID_YAML", 3),
        ):
            with self.subTest(code=code):
                path.write_text(source, encoding="utf-8")
                report = run_check(self.root)
                self.assertEqual("input-error", report.status)
                self.assertEqual(line, self.finding(report, code).line)

    def test_missing_h1_is_document_violation(self) -> None:
        write_metadata(self.root, metadata(), "## Not a title\nBody.\n")
        report = run_check(self.root)
        self.assertEqual("invalid", report.status)
        self.assertEqual(1, report.checked_count)
        self.assertEqual(8, self.finding(report, "MISSING_TITLE").line)

    def test_empty_h1_is_document_violation(self) -> None:
        write_metadata(self.root, metadata(), "#   \nBody.\n")
        report = run_check(self.root)
        self.assertEqual("invalid", report.status)
        self.assertEqual(8, self.finding(report, "EMPTY_TITLE").line)

    def test_two_h1_titles_report_second_title(self) -> None:
        write_metadata(self.root, metadata(), "# One\n# Two\n")
        report = run_check(self.root)
        self.assertEqual("invalid", report.status)
        self.assertEqual(9, self.finding(report, "MULTIPLE_TITLES").line)

    def test_literal_h1_does_not_satisfy_title_requirement(self) -> None:
        write_metadata(self.root, metadata(), "```md\n# Literal\n```\n<!-- # Comment -->\n")
        self.assertEqual("invalid", run_check(self.root).status)
        self.finding(run_check(self.root), "MISSING_TITLE")

    def test_identity_and_required_content_placeholders_have_exact_locations(self) -> None:
        for data, body, line, target in (
            (metadata(id="REQ-NNN"), "# Requirement\n", 3, "REQ-NNN"),
            (metadata(scope="PROJECT/CTX-NNN"), "# Requirement\n", 5, "PROJECT/CTX-NNN"),
            (metadata(), "# Requirement\n- 判据：待填写实际条件。\n", 9, "待填写"),
            (metadata(), "# Requirement\n| Threshold | TBD |\n", 9, "TBD"),
            (metadata(), "# Requirement\nTODO\n", 9, "TODO"),
            (metadata(), "# Requirement\n<slug>\n", 9, "<slug>"),
        ):
            with self.subTest(target=target):
                write_metadata(self.root, data, body)
                report = run_check(self.root)
                self.assertEqual("invalid", report.status)
                item = self.finding(report, "INCOMPLETE_ARTIFACT")
                self.assertEqual(line, item.line)
                self.assertIn(target, item.target)

    def test_unknown_business_facts_are_retained_not_invented_or_blanket_rejected(self) -> None:
        path = write_metadata(
            self.root, metadata(),
            "# Requirement\n并发规则未决，需业务责任人提供来源；本稿不作假设。\n"
            "确认日期待确认；当前执行为 not-run，没有应用。\n",
        )
        before = path.read_bytes()
        self.assertEqual("clean", run_check(self.root).status)
        self.assertEqual(before, path.read_bytes())

    def test_ordinary_lowercase_project_word_is_not_a_template_value(self) -> None:
        write_metadata(self.root, metadata(), "# Project scope\nThis project has no application.\n")
        self.assertEqual("clean", run_check(self.root).status)

    def test_code_comments_and_yaml_comments_are_not_placeholder_or_link_inputs(self) -> None:
        path = write_metadata(
            self.root, metadata(),
            "# Requirement\n`TODO [literal](missing.md)` and ``REQ-NNN``.\n"
            "```markdown\n# REQ-NNN\n[absent](missing.md)\n"
            '<a id="req-001-ac-99"></a>\n### REQ-001-AC-99\n```\n'
            "~~~~\n待填写\n~~~~\n"
            "<!-- TBD [also absent](other.md)\n# Hidden\n-->\n"
            "    [indented code](unreadable.md)\n",
        )
        path.write_bytes(path.read_bytes().replace(
            b"schemaVersion: 1\n", b"schemaVersion: 1 # TODO REQ-NNN\n",
        ))
        report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertEqual(1, report.checked_count)
        self.assertEqual((), parse_artifact(path, self.root).acceptances)

    def test_comment_opener_in_inline_code_cannot_hide_later_links(self) -> None:
        write_metadata(self.root, metadata(),
                       "# Requirement\nA literal `<!--` is not a comment opener.\n"
                       "[missing](missing.md)\n")
        report = run_check(self.root)
        self.assertEqual("invalid", report.status)
        self.assertEqual(10, self.finding(report, "BROKEN_LINK").line)

    def test_missing_relative_file_keeps_owner_line_and_target(self) -> None:
        path = write_metadata(self.root, metadata(), "# Requirement\n[details](missing.md)\n")
        report = run_check(self.root)
        self.assertEqual("invalid", report.status)
        item = self.finding(report, "BROKEN_LINK")
        self.assertEqual(str(path.resolve()), item.path)
        self.assertEqual(9, item.line)
        self.assertEqual("sample/CTX-001/REQ-001", item.owner)
        self.assertEqual("missing.md", item.target)

    def test_missing_fragment_reports_actual_fragment(self) -> None:
        write_metadata(self.root, metadata(), "# Requirement\n[details](#absent)\n")
        report = run_check(self.root)
        self.assertEqual("invalid", report.status)
        item = self.finding(report, "BROKEN_ANCHOR")
        self.assertEqual(9, item.line)
        self.assertEqual("#absent", item.target)

    def test_links_use_explicit_and_heading_anchors_with_spaces_and_unicode(self) -> None:
        guide = self.root / "指南 space.md"
        guide.write_text(
            '# Guide\n<a id="exact"></a>\n## 章节 One\n## Repeated\n## Repeated\n',
            encoding="utf-8",
        )
        write_metadata(self.root, metadata(),
                       '# Requirement\n[one](<指南 space.md#exact>)\n'
                       '[two](指南%20space.md#章节-one "title")\n'
                       '[three](指南%20space.md#repeated-1)\n')
        report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertEqual(1, report.checked_count)
        record = next(item for item in report.baseline.files if item.path == "指南 space.md")
        self.assertEqual(hashlib.sha256(guide.read_bytes()).hexdigest(), record.sha256)

    def test_fragment_inside_code_or_comment_does_not_resolve(self) -> None:
        (self.root / "guide.md").write_text(
            '# Guide\n```\n<a id="absent"></a>\n```\n<!-- <a id="also-absent"></a> -->\n',
            encoding="utf-8",
        )
        write_metadata(self.root, metadata(), "# Requirement\n[x](guide.md#absent)\n")
        self.finding(run_check(self.root), "BROKEN_ANCHOR")

    def test_reference_links_check_used_definition_at_use_location(self) -> None:
        (self.root / "guide.md").write_text('# Guide\n<a id="exists"></a>\n', encoding="utf-8")
        write_metadata(
            self.root, metadata(),
            "# Requirement\n[ok][source]\n[bad][missing]\n"
            '[source]: guide.md#exists "title"\n[missing]: guide.md#absent\n',
        )
        report = run_check(self.root)
        self.assertEqual("invalid", report.status)
        self.assertEqual(1, len(report.findings))
        self.assertEqual(10, report.findings[0].line)
        self.assertEqual("guide.md#absent", report.findings[0].target)

    def test_undefined_explicit_reference_is_not_silently_ignored(self) -> None:
        write_metadata(self.root, metadata(), "# Requirement\n[label][not-defined]\n")
        report = run_check(self.root)
        self.assertEqual("invalid", report.status)
        self.finding(report, "UNRESOLVED_REFERENCE")

    def test_external_links_are_not_network_reads_or_formal_targets(self) -> None:
        write_metadata(self.root, metadata(),
                       "# Requirement\n[web](https://example.invalid/not-read#anchor)\n"
                       "[mail](mailto:fixture@example.invalid)\n")
        report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertEqual(["REQ-001.md"], [item.path for item in report.baseline.files])

    def test_local_nonmarkdown_reference_is_hashed_but_fragment_is_unsupported(self) -> None:
        (self.root / "case.feature").write_text("Feature: Local text\n", encoding="utf-8")
        path = write_metadata(self.root, metadata(), "# Requirement\n[case](case.feature)\n")
        report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertIn("case.feature", {item.path for item in report.baseline.files})
        path.write_bytes(path.read_bytes().replace(b"case.feature)", b"case.feature#scenario)"))
        self.finding(run_check(self.root), "UNSUPPORTED_FRAGMENT")

    def test_traversal_reference_is_input_error_without_reading_outside(self) -> None:
        outside = self.workspace / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        write_metadata(self.root, metadata(), "# Requirement\n[x](../outside.md)\n")
        report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        item = self.finding(report, "OUTSIDE_ROOT")
        self.assertEqual(9, item.line)
        self.assertEqual("../outside.md", item.target)
        self.assertNotIn("outside.md", {item.path for item in report.baseline.files})

    def test_invalid_roots_are_not_empty_selections(self) -> None:
        file = self.root / "not-a-directory"
        file.write_bytes(b"owner data")
        for root in (None, "", 42, self.root / "missing", file):
            with self.subTest(root=root):
                report = run_check(root)
                self.assertEqual("input-error", report.status)
                item = self.finding(report, "INVALID_ROOT")
                self.assertEqual(str(root), item.path)
                self.assertEqual(1, item.line)

    def test_unc_root_is_rejected_before_any_network_path_resolution(self) -> None:
        # Deny the unsafe boundary locally: the regression never contacts a server.
        def forbidden(*arguments, **keywords):
            self.fail("The checker attempted filesystem resolution for a UNC root")
        with patch("check_artifacts._resolve_root", forbidden):
            report = run_check(r"\\unread-host.invalid\share")
        self.assertEqual("input-error", report.status)
        self.finding(report, "INVALID_ROOT")

    def test_unc_reference_is_rejected_before_any_network_path_resolution(self) -> None:
        write_metadata(self.root, metadata(), "# Requirement\n[x](<\\\\unread-host.invalid\\share\\source.md>)\n")
        from check_artifacts import _resolve_file
        def local_only(path, root):
            if "unread-host.invalid" in str(path):
                self.fail("The checker attempted filesystem resolution for a UNC reference")
            return _resolve_file(path, root)
        with patch("check_artifacts._resolve_file", local_only):
            report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.finding(report, "OUTSIDE_ROOT")

    def test_invalid_encoding_is_input_error_and_retains_byte_hash(self) -> None:
        path = self.root / "REQ-001.md"
        path.write_bytes(b"---\n\xff\n")
        report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.assertEqual(2, self.finding(report, "INVALID_ENCODING").line)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), report.baseline.files[0].sha256)

    def test_unreadable_formal_file_is_not_silently_skipped(self) -> None:
        path = write_artifact(self.root)
        if os.name == "nt":
            import msvcrt
            with path.open("r+b") as locked:
                msvcrt.locking(locked.fileno(), msvcrt.LK_NBLCK, 1)
                try:
                    report = run_check(self.root)
                finally:
                    locked.seek(0)
                    msvcrt.locking(locked.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            # No permission changes: inject just the unavailable OS read boundary.
            read_bytes = Path.read_bytes
            def denied(current):
                if current == path:
                    raise PermissionError("Fixture input unavailable")
                return read_bytes(current)
            with patch.object(Path, "read_bytes", denied):
                report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.finding(report, "FILE_READ_ERROR")

    def test_directory_enumeration_error_propagates_instead_of_empty(self) -> None:
        # Real directory plus one injected OS failure; no ACL modification is authorized.
        blocked = self.root / "blocked"
        blocked.mkdir()
        write_artifact(blocked)
        scandir = os.scandir
        def denied(path):
            if Path(path) == blocked:
                raise PermissionError("Fixture directory unavailable")
            return scandir(path)
        with patch("os.scandir", denied):
            report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.finding(report, "DIRECTORY_READ_ERROR")

    def test_directory_link_escape_is_rejected_without_following_it(self) -> None:
        outside = self.workspace / "outside"
        outside.mkdir()
        write_artifact(outside)
        with directory_link(self.root / "escape", outside):
            report = run_check(self.root)
        self.assertEqual("input-error", report.status)
        self.finding(report, "OUTSIDE_ROOT")
        self.assertEqual(0, report.checked_count)

    def test_internal_directory_alias_is_explicitly_excluded_not_double_counted(self) -> None:
        actual = self.root / "actual"
        actual.mkdir()
        write_artifact(actual)
        with directory_link(self.root / "alias", actual):
            report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertEqual(1, report.checked_count)
        self.assertIn(("alias/", "DIRECTORY_ALIAS"),
                      [(item.path, item.reason) for item in report.excluded])

    def test_empty_skeleton_has_precise_template_native_and_maker_exclusions(self) -> None:
        for path in (
            "_templates/items/REQ-NNN.md", ".venv/REQ-001.md", ".git/REQ-001.md",
            "node_modules/REQ-001.md", "docs/research/REQ-001.md",
            ".github/utilities/tests/fixtures/REQ-001.md",
            ".github/skills/example/SKILL.md", ".github/prompts/example.prompt.md",
            ".github/instructions/example.instructions.md", ".github/agents/example.agent.md",
        ):
            write_artifact(self.root, relative_path=path)
        (self.root / "README.md").write_text("# Guide\n待填写\n", encoding="utf-8")
        (self.root / "source.py").write_text("# REQ-001 / TODO\n", encoding="utf-8")
        report = run_check(self.root)
        self.assertEqual("empty", report.status)
        self.assertEqual(0, report.checked_count)
        self.assertEqual(0, report.attempted_count)
        self.assertEqual((), report.findings)
        reasons = {(item.path, item.reason) for item in report.excluded}
        self.assertIn(("_templates/", "TEMPLATE"), reasons)
        self.assertIn((".venv/", "TOOL_DATA"), reasons)
        self.assertIn((".git/", "TOOL_DATA"), reasons)
        self.assertIn(("docs/research/", "MAKER_DATA"), reasons)
        self.assertIn((".github/skills/", "NATIVE_METADATA"), reasons)
        self.assertIn((".github/utilities/tests/", "TEST_FIXTURE"), reasons)
        self.assertIn(("README.md", "LIGHTWEIGHT_GUIDE"), reasons)

    def test_literal_id_mentions_do_not_make_ordinary_guide_formal(self) -> None:
        (self.root / "guide.md").write_text(
            "# Guide\n```markdown\n# REQ-001\nid: REQ-001\n```\n"
            "<!--\nschemaVersion: 1\n-->\n", encoding="utf-8",
        )
        self.assertEqual("empty", run_check(self.root).status)

    def test_exclusions_do_not_match_the_explicit_roots_venv_ancestor(self) -> None:
        write_artifact(self.root, relative_path=".notes/REQ-001.md")
        report = run_check(self.root)
        self.assertEqual("clean", report.status)
        self.assertEqual(1, report.checked_count)

    def test_nonexistent_full_git_base_is_input_error(self) -> None:
        seed_git_repo(self.root)
        report = run_check(self.root, base_sha="0" * 40)
        self.assertEqual("input-error", report.status)
        self.finding(report, "BASE_UNAVAILABLE")

    def test_symbolic_abbreviated_and_malformed_base_are_rejected(self) -> None:
        baseline = seed_git_repo(self.root)
        for base in ("HEAD", "main", baseline[:12], "", "g" * 40, "0" * 41):
            with self.subTest(base=base):
                report = run_check(self.root, base_sha=base)
                self.assertEqual("input-error", report.status)
                self.finding(report, "INVALID_BASE")

    def test_exact_blob_id_is_not_a_commit_base(self) -> None:
        seed_git_repo(self.root)
        blob = git(self.root, "rev-parse", "HEAD:README.md")
        report = run_check(self.root, base_sha=blob)
        self.assertEqual("input-error", report.status)
        self.finding(report, "BASE_UNAVAILABLE")

    def test_base_mode_does_not_use_an_implicit_parent_checkout(self) -> None:
        # This fixture lives below the real checkout, but is not itself a repository.
        base = git(WORKTREE, "rev-parse", "HEAD")
        report = run_check(self.root, base_sha=base)
        self.assertEqual("input-error", report.status)
        self.finding(report, "BASE_UNAVAILABLE")

    def test_base_compares_full_current_files_including_unstaged_untracked_and_deleted(self) -> None:
        seed_git_repo(self.root)
        unchanged = write_artifact(self.root, relative_path="keep/REQ-001.md")
        modified = write_artifact(self.root, id="SR-001", kind="software-requirement")
        deleted = write_artifact(self.root, id="UC-001", kind="use-case")
        base = self.commit_files()
        old_raw = modified.read_bytes()
        old_blob = git(self.root, "rev-parse", f"{base}:SR-001.md")
        modified.write_bytes(old_raw + b"\nStaged body.\n")
        git(self.root, "add", "--", "SR-001.md")
        modified.write_bytes(old_raw + b"\nCurrent unstaged body.\n")
        deleted.unlink()
        added = write_artifact(self.root, id="INV-001", kind="invariant")
        before = source_bytes(self.root)
        report = run_check(self.root, base_sha=base)
        self.assertEqual("clean", report.status)
        self.assertEqual(3, report.checked_count)
        self.assertEqual(base, report.baseline.base_sha)
        self.assertEqual(git(self.root, "rev-parse", f"{base}^{{tree}}"), report.baseline.base_tree)
        self.assertEqual("working-tree", report.baseline.target)
        self.assertEqual(
            [("INV-001.md", "added"), ("SR-001.md", "modified"), ("UC-001.md", "deleted")],
            [(item.path, item.status) for item in report.baseline.changes],
        )
        change = report.baseline.changes[1]
        self.assertEqual(old_blob, change.base_blob)
        self.assertEqual(hashlib.sha256(old_raw).hexdigest(), change.before_sha256)
        self.assertEqual(hashlib.sha256(modified.read_bytes()).hexdigest(), change.after_sha256)
        self.assertEqual(
            {added.name, modified.name, "keep/" + unchanged.name},
            {item.path for item in report.baseline.files if item.role == "formal"},
        )
        self.assertEqual(before, source_bytes(self.root))

    def test_base_does_not_require_old_metadata_to_meet_new_rules(self) -> None:
        seed_git_repo(self.root)
        path = self.root / "REQ-001.md"
        path.write_text("# Legacy file without metadata\n", encoding="utf-8")
        base = self.commit_files()
        write_artifact(self.root)
        report = run_check(self.root, base_sha=base)
        self.assertEqual("clean", report.status)
        self.assertEqual([("REQ-001.md", "modified")],
                         [(item.path, item.status) for item in report.baseline.changes])

    def test_unreadable_current_file_is_not_misreported_as_a_deletion(self) -> None:
        seed_git_repo(self.root)
        path = write_artifact(self.root)
        base = self.commit_files()
        read_bytes = Path.read_bytes
        def denied(current):
            if current == path:
                raise PermissionError("Unavailable current input, not a deletion")
            return read_bytes(current)
        with patch.object(Path, "read_bytes", denied):
            report = run_check(self.root, base_sha=base)
        self.assertEqual("input-error", report.status)
        self.assertEqual((), report.baseline.changes)
        self.assertFalse(report.baseline.comparison_complete)

    def test_exact_sha256_commit_is_supported_when_provided(self) -> None:
        git(self.root, "init", "--quiet", "--template=", "--object-format=sha256")
        write_artifact(self.root)
        base = self.commit_files()
        self.assertEqual(64, len(base))
        report = run_check(self.root, base_sha=base.upper())
        self.assertEqual("clean", report.status)
        self.assertEqual(base, report.baseline.base_sha)
        self.assertTrue(report.to_dict()["baseline"].get("comparison_complete"))

    def test_base_keeps_prior_formal_path_when_all_metadata_was_removed(self) -> None:
        seed_git_repo(self.root)
        path = write_artifact(self.root, relative_path="ordinary.md")
        base = self.commit_files()
        path.write_text("# Erased metadata\n", encoding="utf-8")
        report = run_check(self.root, base_sha=base)
        self.assertEqual("input-error", report.status)
        self.finding(report, "MISSING_FRONTMATTER")
        self.assertEqual([("ordinary.md", "modified")],
                         [(item.path, item.status) for item in report.baseline.changes])

    def test_base_keeps_validation_of_unchanged_broken_links(self) -> None:
        seed_git_repo(self.root)
        write_metadata(self.root, metadata(), "# Requirement\n[x](missing.md)\n")
        base = self.commit_files()
        write_artifact(self.root, id="UC-001", kind="use-case")
        report = run_check(self.root, base_sha=base)
        self.assertEqual("invalid", report.status)
        self.assertEqual(2, report.checked_count)
        self.finding(report, "BROKEN_LINK")

    def test_base_keeps_unchanged_duplicate_inventory(self) -> None:
        seed_git_repo(self.root)
        write_artifact(self.root, relative_path="a/REQ-001.md")
        write_artifact(self.root, relative_path="b/REQ-001.md")
        base = self.commit_files()
        write_artifact(self.root, id="UC-001", kind="use-case")
        report = run_check(self.root, base_sha=base)
        self.assertEqual("input-error", report.status)
        self.assertEqual(3, report.checked_count)
        self.finding(report, "DUPLICATE_ARTIFACT_ID")

    def test_git_replace_does_not_change_selected_commit_contents(self) -> None:
        seed_git_repo(self.root)
        path = write_artifact(self.root)
        original = path.read_bytes()
        base = self.commit_files()
        path.write_bytes(original + b"\nNew commit content.\n")
        newer = self.commit_files()
        git(self.root, "replace", base, newer)
        report = run_check(self.root, base_sha=base)
        self.assertEqual("clean", report.status)
        self.assertEqual(base, report.baseline.base_sha)
        self.assertEqual(hashlib.sha256(original).hexdigest(),
                         report.baseline.changes[0].before_sha256)

    def test_git_reads_do_not_execute_attributes_filters_or_diff_commands(self) -> None:
        seed_git_repo(self.root)
        path = write_artifact(self.root)
        base = self.commit_files()
        (self.root / ".gitattributes").write_text("*.md filter=trap diff=trap\n", encoding="utf-8")
        marker = self.root / "must-not-run"
        command = f'"{sys.executable}" -c "open(\'must-not-run\', \'w\').write(\'executed\')"'
        git(self.root, "config", "filter.trap.clean", command)
        git(self.root, "config", "filter.trap.smudge", command)
        git(self.root, "config", "diff.trap.textconv", command)
        path.write_bytes(path.read_bytes() + b"\nCurrent change.\n")
        report = run_check(self.root, base_sha=base)
        self.assertEqual("clean", report.status)
        self.assertEqual("modified", report.baseline.changes[0].status)
        self.assertFalse(marker.exists())

    def test_cli_current_interpreter_propagates_clean_invalid_input_and_empty(self) -> None:
        for body, status, exit_code in (
            ("# Requirement\n", "clean", 0),
            ("# Requirement\n[x](missing.md)\n", "invalid", 1),
            ("# Requirement\n", "input-error", 2),
        ):
            with self.subTest(status=status):
                path = write_metadata(self.root, metadata(), body)
                if status == "input-error":
                    path.write_text("# REQ-001 missing metadata\n", encoding="utf-8")
                before = source_bytes(self.root)
                result = self.cli()
                self.assertEqual(exit_code, result.returncode, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(status, payload["status"])
                self.assertEqual(before, source_bytes(self.root))
        path.unlink()
        result = self.cli()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("empty", json.loads(result.stdout)["status"])

    def test_cli_unavailable_base_propagates_exit_two(self) -> None:
        seed_git_repo(self.root)
        result = self.cli("--base", "0" * 40)
        self.assertEqual(2, result.returncode)
        self.assertIn("BASE_UNAVAILABLE", {item["code"] for item in json.loads(result.stdout)["findings"]})

    def test_cli_ignores_inherited_git_directory_and_index(self) -> None:
        seed_git_repo(self.root)
        write_artifact(self.root)
        base = self.commit_files()
        outside = self.workspace / "other repository"
        seed_git_repo(outside)
        env = dict(os.environ, GIT_DIR=str(outside / ".git"), GIT_WORK_TREE=str(outside),
                   GIT_INDEX_FILE=str(outside / ".git" / "index"))
        result = self.cli("--base", base, env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("clean", payload["status"])
        self.assertEqual(base, payload["baseline"]["base_sha"])

    def test_cli_creates_only_explicit_new_json_report(self) -> None:
        write_artifact(self.root)
        before = source_bytes(self.root)
        output = self.workspace / "报告 new.json"
        result = self.cli("--report", str(output))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(output.is_file(), "Explicit report was not created")
        self.assertEqual(json.loads(result.stdout), json.loads(output.read_text(encoding="utf-8")))
        self.assertEqual({"path": str(output.resolve()), "written": True},
                         json.loads(result.stdout)["report_output"])
        self.assertEqual(before, source_bytes(self.root))

    def test_cli_relative_report_is_relative_to_root_not_cwd(self) -> None:
        write_artifact(self.root)
        result = self.cli("--report", "report.json", cwd=self.workspace)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue((self.root / "report.json").is_file())
        self.assertFalse((self.workspace / "report.json").exists())
        self.assertNotIn("report.json", {
            item["path"] for item in json.loads(result.stdout)["baseline"]["files"]
        })

    def test_cli_never_overwrites_source_or_existing_historical_report(self) -> None:
        source = write_artifact(self.root)
        history = self.workspace / "historical.json"
        history.write_bytes(b'{"previous": "preserve exactly"}\r\n')
        for output in (source, history):
            with self.subTest(output=output):
                before = output.read_bytes()
                result = self.cli("--report", str(output))
                self.assertEqual(2, result.returncode, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual("input-error", payload["status"])
                self.assertIn("REPORT_CONFLICT", {item["code"] for item in payload["findings"]})
                self.assertEqual(before, output.read_bytes())

    def test_cli_report_write_failure_is_not_reported_as_success(self) -> None:
        write_artifact(self.root)
        output = self.workspace / "missing directory" / "report.json"
        result = self.cli("--report", str(output))
        self.assertEqual(2, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("REPORT_WRITE_ERROR", {item["code"] for item in payload["findings"]})
        self.assertFalse(output.exists())

    def test_cli_new_markdown_report_cannot_become_source_input(self) -> None:
        write_artifact(self.root)
        output = self.root / "new-source.md"
        result = self.cli("--report", str(output))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
