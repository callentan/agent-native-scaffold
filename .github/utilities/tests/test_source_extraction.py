"""ENH-16 / EXTRACT-01..16: self-owned files, real OOXML, no service calls."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import random
import stat
import struct
import subprocess
import sys
import unittest
from unittest.mock import patch
import warnings
import zipfile

from artifact_io import ArtifactInputError
from tests.helpers import WORKTREE, source_bytes, temporary_workspace


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '</Types>'
)
RELATIONSHIPS = (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    'Target="word/document.xml"/></Relationships>'
)
DOCUMENT = (
    f'<w:document xmlns:w="{W}"><w:body>'
    '<w:p><w:r><w:t>Rule: A member must borrow at most two items.</w:t></w:r></w:p>'
    '<w:tbl><w:tblPr/><w:tblGrid><w:gridCol w:w="3000"/><w:gridCol w:w="3000"/></w:tblGrid>'
    '<w:tr><w:tc><w:tcPr><w:tcW w:w="3000" w:type="dxa"/></w:tcPr>'
    '<w:p><w:r><w:t>Capability: Members can view loans.</w:t></w:r></w:p></w:tc>'
    '<w:tc><w:p><w:r><w:t>Maybe the limit should change.</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
    '<w:p/><w:sectPr/></w:body></w:document>'
)


def docx_bytes(document=DOCUMENT, *, extra=(), content_types=CONTENT_TYPES,
               relationships=RELATIONSHIPS, compression=zipfile.ZIP_STORED):
    """A self-owned actual OPC/OOXML ZIP, never a renamed text file."""
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=compression) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", relationships)
        archive.writestr("word/document.xml", document)
        for name, raw in extra:
            if isinstance(name, str):
                # ZipInfo normalizes Windows separators at construction. Keep
                # the actual adversarial spelling in both ZIP headers.
                spelling = name
                name = zipfile.ZipInfo(spelling)
                name.filename = name.orig_filename = spelling
                name.compress_type = compression
            archive.writestr(name, raw)
    return output.getvalue()


def sha(raw):
    # Independent byte oracle, not a production helper.
    return "sha256:" + hashlib.sha256(raw).hexdigest()


class SourceFixture(unittest.TestCase):
    def setUp(self):
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "source 输入 with spaces"
        self.root.mkdir()

    def tool(self, name="extract_source"):
        self.assertIsNotNone(importlib.util.find_spec(name),
                             f"ENH-16 {name} is not implemented")
        return importlib.import_module(name)

    def write(self, text, name="notes.txt"):
        path = self.root / name
        path.write_bytes(text if isinstance(text, (bytes, bytearray)) else text.encode("utf-8"))
        return path

    def extract(self, path, kind="text"):
        return self.tool().extract_candidates(path, kind)

    def error(self, path, kind, code):
        with self.assertRaises(ArtifactInputError) as caught:
            self.extract(path, kind)
        self.assertEqual(code, caught.exception.code, str(caught.exception))
        return caught.exception

    def cli(self, module="extract_source", *args):
        script = WORKTREE / ".github" / "utilities" / (module + ".py")
        self.assertTrue(script.is_file(), f"ENH-16 {module} CLI is missing")
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(script), *args],
            cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8",
        )

    def cli_error(self, result, code):
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("input-error", payload["status"])
        self.assertEqual(code, payload["error"]["code"])
        return payload


class TextExtractionTests(SourceFixture):
    def test_extract_01_markdown_exact_line_paragraph_and_bytes(self):
        raw = (b"# Loan notes\n\nRule: A member must borrow at most two items.\n"
               b"Capability: Members can view loans.\n")
        path = self.write(raw, "loan notes.md")
        before = source_bytes(self.root)
        report = self.extract(path, "markdown")
        identity = {"path": str(path.resolve()), "kind": "markdown",
                    "baseline": sha(raw), "byte_count": len(raw)}
        self.assertEqual(identity, report["source"])
        self.assertEqual(("extracted", 4, 2),
                         (report["status"], report["unit_count"], report["candidate_count"]))
        first, second = report["candidates"]
        self.assertEqual(("candidate-0001", "rule", "observed"),
                         (first["candidate_id"], first["kind"], first["nature"]))
        self.assertEqual("Rule: A member must borrow at most two items.", first["text"])
        self.assertEqual(first["text"], first["fragment"])
        self.assertEqual({"line": 3, "paragraph": 2}, first["location"])
        self.assertEqual({"line": 4, "paragraph": 2}, second["location"])
        self.assertEqual("capability", second["kind"])
        self.assertEqual(identity, second["source"])
        self.assertTrue(first["clarification"])
        self.assertNotIn("contentState", first)
        self.assertNotIn("confirmation", first)
        self.assertEqual(before, source_bytes(self.root))

    def test_extract_01_unlabelled_statements_are_inferences_not_invented_rules(self):
        path = self.write("Members must retain receipts.\nA member can view loans.\nLoose note.\n")
        items = self.extract(path)["candidates"]
        self.assertEqual(["rule", "capability", "statement"], [i["kind"] for i in items])
        self.assertEqual(["inferred"] * 3, [i["nature"] for i in items])
        self.assertTrue(all(i["extraction_reason"] for i in items))
        self.assertEqual("Loose note.", items[2]["text"])

    def test_extract_01_labels_include_terms_and_use_cases_without_owner_ids(self):
        items = self.extract(self.write("Term: Loan means an outstanding borrowing.\n"
                                       "Use case: A member requests a loan.\n"))["candidates"]
        self.assertEqual(["term", "use-case"], [i["kind"] for i in items])
        self.assertEqual(["observed", "observed"], [i["nature"] for i in items])
        self.assertEqual(["candidate-0001", "candidate-0002"],
                         [i["candidate_id"] for i in items])

    def test_extract_02_readable_empty_and_whitespace_keep_identity(self):
        for raw in (b"", b" \t\r\n\r\n"):
            with self.subTest(raw=raw):
                path = self.write(raw)
                report = self.extract(path)
                self.assertEqual("empty", report["status"])
                self.assertEqual([], report["candidates"])
                self.assertEqual(0, report["candidate_count"])
                self.assertEqual(sha(raw), report["source"]["baseline"])
                self.assertEqual(len(raw), report["source"]["byte_count"])
                self.assertEqual(str(path.resolve()), report["source"]["path"])
                self.assertEqual(0 if not raw else 2, report["unit_count"])

    def test_extract_03_missing_directory_and_relative_api_inputs_are_errors(self):
        self.error(self.root / "absent.txt", "text", "FILE_NOT_FOUND")
        self.error(self.root, "text", "INVALID_PATH")
        self.error("notes.txt", "text", "INVALID_PATH")

    def test_extract_03_read_failure_is_typed_not_empty_injected_io_boundary(self):
        path = self.write("Rule: Keep this source.\n")
        tool = self.tool()
        with patch.object(Path, "open", side_effect=PermissionError("controlled read denial")):
            with self.assertRaises(ArtifactInputError) as caught:
                tool.extract_candidates(path, "text")
        self.assertEqual("FILE_READ_ERROR", caught.exception.code)
        self.assertIsInstance(caught.exception.__cause__, PermissionError)

    def test_extract_03_wrong_extension_binary_and_encoding_are_errors(self):
        self.error(self.write("Rule: valid text", "notes.docx"), "text", "INVALID_SOURCE_FORMAT")
        self.error(self.write(b"Rule:\x00binary"), "text", "INVALID_SOURCE_FORMAT")
        self.error(self.write(b"\xef\xbb\xbfok\r\n\xff"), "text", "INVALID_ENCODING")

    def test_extract_03_unknown_adapter_does_not_guess_from_extension(self):
        path = self.write("Rule: Keep original.")
        self.error(path, "pdf", "SOURCE_ADAPTER_UNAVAILABLE")
        self.error(path, None, "SOURCE_ADAPTER_UNAVAILABLE")

    def test_extract_03_network_and_drive_relative_are_refused_before_io(self):
        tool = self.tool()
        for value in ("https://example.invalid/source.txt", "//host/share/source.txt",
                      "\\\\host\\share\\source.txt", "C:relative.txt"):
            with self.subTest(value=value), patch.object(Path, "open",
                                                       side_effect=AssertionError("must not read")):
                with self.assertRaises(ArtifactInputError) as caught:
                    tool.extract_candidates(value, "text")
                self.assertEqual("INVALID_PATH", caught.exception.code)

    def test_extract_04_transcript_preserves_supplied_speaker_time_turn_and_literal(self):
        raw = ('{"speaker":"李 A","timestamp":"00:00:02.125","text":"Rule: Borrow at most two items."}\r\n'
               '\r\n{"speaker":"B","timestamp":"00:00:01.000","text":"Maybe three instead."}\r\n')
        path = self.write(("\ufeff" + raw).encode("utf-8"), "meeting.txt")
        report = self.extract(path, "transcript")
        self.assertEqual(3, report["unit_count"])
        first, second = report["candidates"]
        self.assertEqual({"line": 1, "turn": 1, "speaker": "李 A", "timestamp": "00:00:02.125"},
                         first["location"])
        self.assertEqual({"line": 3, "turn": 2, "speaker": "B", "timestamp": "00:00:01.000"},
                         second["location"])
        self.assertEqual(raw.splitlines()[0], first["fragment"])
        self.assertEqual("Rule: Borrow at most two items.", first["text"])
        self.assertEqual("uncertain", second["nature"])
        self.assertEqual(sha(path.read_bytes()), report["source"]["baseline"])

    def test_extract_04_bad_transcript_is_not_partially_successful(self):
        valid = '{"speaker":"A","timestamp":"00:00:01.000","text":"Rule: Keep original."}\n'
        bad = (
            "A: no timestamp",
            '{"speaker":"A","text":"missing time"}',
            '{"speaker":"","timestamp":"00:00:01.000","text":"x"}',
            '{"speaker":"A","timestamp":"00:61:01.000","text":"x"}',
            '{"speaker":"A","timestamp":"1:01","text":"x"}',
            '{"speaker":"A","timestamp":"00:00:01.000","text":""}',
            '{"speaker":"A","speaker":"B","timestamp":"00:00:01.000","text":"x"}',
            '{"speaker":"A","timestamp":"00:00:01.000","text":"x","confirmed":true}',
            '{"speaker":"A","timestamp":"00:00:01.000","text":"\\ud800"}',
            '{"speaker":"A","timestamp":"00:00:01.000","text":"\\u0000"}',
            '[]',
        )
        for line in bad:
            with self.subTest(line=line):
                error = self.error(self.write(valid + line), "transcript", "INVALID_TRANSCRIPT")
                self.assertEqual(2, error.line)

    def test_extract_05_repeated_lines_keep_both_actual_locations(self):
        path = self.write("Rule: Keep all origins.\n\nRule: Keep all origins.\n")
        items = self.extract(path)["candidates"]
        self.assertEqual(2, len(items))
        self.assertEqual([{"line": 1, "paragraph": 1}, {"line": 3, "paragraph": 2}],
                         [item["location"] for item in items])
        self.assertEqual(items[0]["text"], items[1]["text"])
        self.assertNotEqual(items[0]["candidate_id"], items[1]["candidate_id"])

    def test_extract_06_contrary_sources_do_not_supersede_or_confirm_each_other(self):
        a = self.write("Rule: Inactive members may borrow two items.\n", "a.txt")
        b = self.write("Rule: Inactive members must not borrow items.\n", "b.txt")
        items = self.extract(a)["candidates"] + self.extract(b)["candidates"]
        self.assertEqual([str(a.resolve()), str(b.resolve())], [i["source"]["path"] for i in items])
        self.assertEqual(["Rule: Inactive members may borrow two items.",
                          "Rule: Inactive members must not borrow items."], [i["text"] for i in items])
        for item in items:
            self.assertNotIn("confirmed", item.values())
            self.assertIn("contrary", item["clarification"])
            self.assertIn("owner", item["clarification"])

    def test_extract_07_explicit_uncertainty_is_preserved_not_probabilistic(self):
        items = self.extract(self.write("Rule: Maybe members should borrow three items.\n"
                                       "规则：额度待确认。\n"
                                       "Capability: Export is proposed.\n"))["candidates"]
        self.assertEqual(["uncertain"] * 3, [i["nature"] for i in items])
        self.assertEqual(["rule", "rule", "capability"], [i["kind"] for i in items])
        for item in items:
            self.assertTrue(item["uncertainty"])
            self.assertNotIn("confidence", item)

    def test_extract_16_bom_crlf_unicode_spaces_and_executable_text_are_literal(self):
        raw = ('\ufeff规则：必须保留来源。\r\n\r\n'
               '$(New-Item NEVER-CREATE); python -c "raise SystemExit(7)"\r\n').encode("utf-8")
        path = self.write(raw, "来源 unicode 空格.txt")
        before = source_bytes(self.root)
        items = self.extract(path)["candidates"]
        self.assertEqual("规则：必须保留来源。", items[0]["fragment"])
        self.assertEqual({"line": 3, "paragraph": 2}, items[1]["location"])
        self.assertEqual("statement", items[1]["kind"])
        self.assertEqual(sha(raw), items[0]["source"]["baseline"])
        self.assertEqual(before, source_bytes(self.root))

    def test_extract_16_markdown_literals_comments_and_code_are_not_statements(self):
        path = self.write("# Heading\n\n<!-- Rule: hidden -->\n\n```python\n"
                          "Rule: code sample\n```\n\nRule: Keep actual text.\n", "literal.md")
        report = self.extract(path, "markdown")
        self.assertEqual(1, report["candidate_count"])
        self.assertEqual({"line": 9, "paragraph": 4}, report["candidates"][0]["location"])
        self.assertEqual("Rule: Keep actual text.", report["candidates"][0]["fragment"])

    def test_extract_12_plain_source_size_bound_is_explicit(self):
        self.error(self.write(b"x" * (4 * 1024 * 1024 + 1)), "text", "SOURCE_LIMIT_EXCEEDED")
        self.error(self.write("Rule: Keep all sources.\n" * 10_001), "text", "SOURCE_LIMIT_EXCEEDED")


class DocxExtractionTests(SourceFixture):
    def document(self, **kwargs):
        return self.write(docx_bytes(**kwargs), "source actual.docx")

    def test_extract_10_actual_zip_paragraph_table_and_uncertainty_have_exact_positions(self):
        path = self.document()
        before = source_bytes(self.root)
        report = self.extract(path, "docx")
        self.assertEqual((4, 3), (report["unit_count"], report["candidate_count"]))
        first, second, third = report["candidates"]
        self.assertEqual({"part": "word/document.xml", "block": 1, "paragraph": 1},
                         first["location"])
        self.assertEqual({"part": "word/document.xml", "block": 2, "paragraph": 2,
                          "table": 1, "row": 1, "cell": 1, "cell_paragraph": 1},
                         second["location"])
        self.assertEqual({"part": "word/document.xml", "block": 2, "paragraph": 3,
                          "table": 1, "row": 1, "cell": 2, "cell_paragraph": 1},
                         third["location"])
        self.assertEqual("Capability: Members can view loans.", second["fragment"])
        self.assertEqual("uncertain", third["nature"])
        self.assertEqual(sha(path.read_bytes()), first["source"]["baseline"])
        self.assertEqual(before, source_bytes(self.root))

    def test_extract_10_runs_tabs_breaks_and_xml_escaping_preserve_paragraph_text(self):
        document = (f'<w:document xmlns:w="{W}"><w:body><w:p><w:r>'
                    '<w:t xml:space="preserve">Rule: A &amp; B </w:t></w:r><w:r>'
                    '<w:t>must keep</w:t><w:tab/><w:t>sources.</w:t><w:br/>'
                    '<w:t>Always.</w:t></w:r></w:p></w:body></w:document>')
        item = self.extract(self.document(document=document), "docx")["candidates"][0]
        self.assertEqual("Rule: A & B must keep\tsources.\nAlways.", item["fragment"])
        self.assertEqual(item["fragment"], item["text"])

    def test_extract_10_empty_docx_is_explicit_empty_with_real_container_identity(self):
        path = self.document(document=f'<w:document xmlns:w="{W}"><w:body><w:p/></w:body></w:document>')
        report = self.extract(path, "docx")
        self.assertEqual(("empty", 1, 0),
                         (report["status"], report["unit_count"], report["candidate_count"]))
        self.assertEqual(sha(path.read_bytes()), report["source"]["baseline"])

    def test_extract_11_renamed_text_corruption_and_missing_main_part_are_errors(self):
        self.error(self.write(b"Rule: not a ZIP", "wrong.docx"), "docx", "INVALID_DOCX")
        self.error(self.write(docx_bytes()[:-24], "truncated.docx"), "docx", "INVALID_DOCX")
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        self.error(self.write(output.getvalue(), "missing.docx"), "docx", "INVALID_DOCX")

    def test_extract_11_invalid_xml_and_wrong_content_type_do_not_return_partial_results(self):
        self.error(self.document(document=DOCUMENT[:-10]), "docx", "INVALID_DOCX_XML")
        self.error(self.document(content_types=CONTENT_TYPES.replace(
            "wordprocessingml.document.main+xml", "wordprocessingml.template.main+xml")),
            "docx", "UNSUPPORTED_DOCX")
        self.error(self.document(document=f'<w:notDocument xmlns:w="{W}"/>'), "docx", "INVALID_DOCX")

    def test_extract_11_encrypted_zip_flag_is_refused_without_password_discovery(self):
        raw = bytearray(docx_bytes())
        for signature, flag_offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
            offset = 0
            while (offset := raw.find(signature, offset)) != -1:
                struct.pack_into("<H", raw, offset + flag_offset, 1)
                offset += 4
        self.error(self.write(raw, "encrypted.docx"), "docx", "SOURCE_ENCRYPTED")

    def test_extract_11_unsupported_compression_is_refused(self):
        self.error(self.document(compression=zipfile.ZIP_BZIP2), "docx", "UNSUPPORTED_DOCX")

    def test_extract_11_unsupported_body_features_and_merged_cells_are_explicit(self):
        variants = (
            DOCUMENT.replace("<w:p/>", "<w:altChunk/>"),
            DOCUMENT.replace("<w:p/>", "<w:p><w:hyperlink/></w:p>"),
            DOCUMENT.replace("<w:p/>", "<w:p><w:r><w:drawing/></w:r></w:p>"),
            DOCUMENT.replace("<w:tcPr>", '<w:tcPr><w:gridSpan w:val="2"/>', 1),
            DOCUMENT.replace("<w:p/>", "<w:sdt/>"),
        )
        for document in variants:
            with self.subTest(document=document):
                self.error(self.document(document=document), "docx", "UNSUPPORTED_DOCX")

    def test_extract_12_traversal_absolute_backslash_and_alias_members_are_unsafe(self):
        for name in ("../escape.txt", "/escape.txt", "word/../../escape.txt",
                     "word\\escape.txt", "C:/escape.txt", "word/./document.xml"):
            with self.subTest(name=name):
                path = self.document(extra=((name, b"must not extract"),))
                before = source_bytes(self.workspace)
                self.error(path, "docx", "UNSAFE_DOCX")
                self.assertEqual(before, source_bytes(self.workspace))

    def test_extract_12_duplicate_members_and_symlinks_are_unsafe(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self.error(self.document(extra=(("word/document.xml", DOCUMENT),)),
                       "docx", "UNSAFE_DOCX")
        alias = zipfile.ZipInfo("alias")
        alias.create_system = 3
        alias.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.error(self.document(extra=((alias, b"../outside"),)), "docx", "UNSAFE_DOCX")

    def test_extract_12_nul_truncated_zip_name_is_not_a_safe_alias(self):
        raw = docx_bytes(extra=(("word/x.xml", b"do not silently truncate"),))
        raw = raw.replace(b"word/x.xml", b"word/\x00.xml")
        self.error(self.write(raw, "nul-name.docx"), "docx", "UNSAFE_DOCX")

    def test_extract_12_entity_and_external_relationships_are_never_resolved(self):
        dtd = '<!DOCTYPE x [<!ENTITY x SYSTEM "file:///never-read">]>'
        self.error(self.document(document=dtd + DOCUMENT), "docx", "UNSAFE_DOCX")
        self.error(self.document(relationships=RELATIONSHIPS.replace(
            'Target="word/document.xml"', 'TargetMode="External" Target="https://example.invalid/x"')),
            "docx", "UNSAFE_DOCX")
        self.error(self.document(extra=(("word/_rels/document.xml.rels", RELATIONSHIPS),)),
                   "docx", "UNSUPPORTED_DOCX")

    def test_extract_12_unrecognized_parts_macros_and_additional_story_text_are_not_skipped(self):
        for name in ("word/vbaProject.bin", "word/header1.xml", "word/footnotes.xml", "unknown.xml"):
            with self.subTest(name=name):
                self.error(self.document(extra=((name, b"not silently discarded"),)),
                           "docx", "UNSUPPORTED_DOCX")

    def test_extract_12_crc_failure_is_not_an_empty_document(self):
        raw = docx_bytes()
        broken = raw.replace(b"A member must borrow", b"B member must borrow", 1)
        self.assertNotEqual(raw, broken)
        self.error(self.write(broken, "bad-crc.docx"), "docx", "INVALID_DOCX")

    def test_extract_12_member_count_part_size_and_compression_ratio_are_bounded(self):
        fixtures = (
            docx_bytes(extra=tuple((f"part-{n}.xml", b"") for n in range(65))),
            docx_bytes(document="x" * (1024 * 1024 + 1)),
            docx_bytes(document=" " * 100_000, compression=zipfile.ZIP_DEFLATED),
        )
        for raw in fixtures:
            with self.subTest(size=len(raw)):
                self.error(self.write(raw, "bounded.docx"), "docx", "SOURCE_LIMIT_EXCEEDED")

    def test_extract_12_total_expansion_bound_uses_actual_container_not_mock_sizes(self):
        # Nine 1,024,000-byte members: >8 MiB total, <4 MiB compressed ZIP.
        # Repeated 16 KiB noise stays below 100:1; each member is <1 MiB.
        chunk = random.Random(16).randbytes(16_000)
        raw = docx_bytes(extra=tuple((f"extra-{n}.xml", chunk * 64) for n in range(9)),
                         compression=zipfile.ZIP_DEFLATED)
        self.assertLess(len(raw), 4 * 1024 * 1024)
        self.error(self.write(raw, "total.docx"), "docx", "SOURCE_LIMIT_EXCEEDED")

    def test_extract_12_xml_depth_and_node_count_are_bounded(self):
        deep = "<x>" * 34 + "</x>" * 34
        many = "<x>" + "<y/>" * 10_001 + "</x>"
        for xml in (deep, many):
            with self.subTest(xml_length=len(xml)):
                self.error(self.document(document=xml), "docx", "SOURCE_LIMIT_EXCEEDED")

    def test_extract_11_package_attributes_and_non_element_text_are_not_silently_skipped(self):
        variants = (
            {"content_types": CONTENT_TYPES.replace("<Types xmlns=", '<Types unknown="x" xmlns=')},
            {"content_types": CONTENT_TYPES.replace("<Default Extension=", '<Default unknown="x" Extension=', 1)},
            {"content_types": CONTENT_TYPES.replace("</Types>", "Unsupported loose text</Types>")},
            {"relationships": RELATIONSHIPS.replace("<Relationships xmlns=",
                                                   '<Relationships unknown="x" xmlns=')},
        )
        for changes in variants:
            with self.subTest(changes=changes):
                self.error(self.document(**changes), "docx", "UNSUPPORTED_DOCX")

    def test_extract_10_xml_formatting_whitespace_does_not_change_paragraph_locations(self):
        path = self.document(document=DOCUMENT.replace("<w:sectPr/>", "<w:sectPr>\n  </w:sectPr>"))
        report = self.extract(path, "docx")
        self.assertEqual((4, 3), (report["unit_count"], report["candidate_count"]))
        self.assertEqual({"part": "word/document.xml", "block": 1, "paragraph": 1},
                         report["candidates"][0]["location"])

    def test_extract_12_directory_type_cannot_impersonate_a_main_xml_file(self):
        raw = docx_bytes()
        data = bytearray(raw)
        offset = data.find(b"PK\x01\x02")
        while offset != -1:
            name_length = struct.unpack_from("<H", data, offset + 28)[0]
            name = bytes(data[offset + 46:offset + 46 + name_length])
            if name == b"word/document.xml":
                struct.pack_into("<I", data, offset + 38, (stat.S_IFDIR | 0o755) << 16)
                break
            offset = data.find(b"PK\x01\x02", offset + 4)
        self.error(self.write(data, "directory-alias.docx"), "docx", "UNSAFE_DOCX")


class SourceCliTests(SourceFixture):
    def test_extract_15_default_stdout_is_read_only_with_actual_selected_root(self):
        path = self.write("Rule: Keep the input file.\n", "a spaced 来源.txt")
        before = source_bytes(self.workspace)
        result = self.cli("extract_source", "--root", str(self.root),
                          "--source", path.name, "--kind", "text")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stderr)
        self.assertEqual(str(path.resolve()), json.loads(result.stdout)["source"]["path"])
        self.assertEqual(before, source_bytes(self.workspace))

    def test_extract_15_explicit_new_output_is_json_and_does_not_change_readonly_source(self):
        path = self.write("Rule: Keep the input file.\n")
        path.chmod(stat.S_IREAD)
        self.addCleanup(path.chmod, stat.S_IREAD | stat.S_IWRITE)
        raw = path.read_bytes()
        output = self.root / "candidate output.json"
        result = self.cli("extract_source", "--root", str(self.root),
                          "--source", path.name, "--kind", "text", "--output", str(output))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout), json.loads(output.read_bytes()))
        self.assertEqual(raw, path.read_bytes())
        self.assertEqual({"notes.txt", "candidate output.json"}, set(source_bytes(self.root)))

    def test_extract_15_existing_source_output_and_outside_output_remain_unchanged(self):
        path = self.write("Rule: Never replace this source.\n")
        output = self.write(b"owner output", "existing.json")
        for destination, code in ((str(output), "REPORT_CONFLICT"),
                                  (str(path), "REPORT_CONFLICT"),
                                  (str(self.workspace / "outside.json"), "OUTSIDE_ROOT")):
            with self.subTest(destination=destination):
                before = source_bytes(self.workspace)
                result = self.cli("extract_source", "--root", str(self.root),
                                  "--source", path.name, "--kind", "text", "--output", destination)
                self.cli_error(result, code)
                self.assertEqual(before, source_bytes(self.workspace))

    def test_extract_15_missing_output_parent_and_outside_source_are_errors(self):
        path = self.write("Rule: Keep original.\n")
        before = source_bytes(self.workspace)
        result = self.cli("extract_source", "--root", str(self.root), "--source", path.name,
                          "--kind", "text", "--output", "missing/output.json")
        self.cli_error(result, "REPORT_WRITE_ERROR")
        outside = self.workspace / "outside.txt"
        outside.write_text("Not selected.", encoding="utf-8")
        result = self.cli("extract_source", "--root", str(self.root),
                          "--source", str(outside), "--kind", "text")
        self.cli_error(result, "OUTSIDE_ROOT")
        self.assertEqual(before, {k: v for k, v in source_bytes(self.workspace).items()
                                  if k != "outside.txt"})

    def test_extract_03_cli_unsupported_and_invalid_inputs_exit_two_not_empty_zero(self):
        path = self.write(b"\xff")
        result = self.cli("extract_source", "--root", str(self.root),
                          "--source", path.name, "--kind", "text")
        self.cli_error(result, "INVALID_ENCODING")
        result = self.cli("extract_source", "--root", str(self.root),
                          "--source", path.name, "--kind", "audio")
        self.cli_error(result, "SOURCE_ADAPTER_UNAVAILABLE")

    def test_extract_15_alternate_stream_is_not_an_exclusive_new_output_file(self):
        path = self.write("Rule: Keep owner source bytes.\n")
        before = source_bytes(self.workspace)
        result = self.cli("extract_source", "--root", str(self.root),
                          "--source", path.name, "--kind", "text",
                          "--output", path.name + ":hidden.json")
        self.cli_error(result, "REPORT_CONFLICT")
        self.assertEqual(before, source_bytes(self.workspace))


class AudioRefusalTests(SourceFixture):
    def test_extract_13_unapproved_audio_is_refused_before_source_or_secret_reads(self):
        tool = self.tool("transcribe_audio")
        before = source_bytes(self.workspace)
        with patch.object(Path, "open", side_effect=AssertionError("no audio or secret reads")):
            with self.assertRaises(ArtifactInputError) as caught:
                tool.transcribe_audio(self.root / "not-provided.wav")
        self.assertEqual("AUDIO_AUTHORIZATION_REQUIRED", caught.exception.code)
        self.assertIn("service", caught.exception.message)
        self.assertIn("model", caught.exception.message)
        self.assertIn("data_scope", caught.exception.message)
        self.assertEqual(before, source_bytes(self.workspace))

    def test_extract_13_authorized_flag_with_missing_inputs_is_still_blocked(self):
        tool = self.tool("transcribe_audio")
        with self.assertRaises(ArtifactInputError) as caught:
            tool.transcribe_audio(self.root / "not-provided.wav", authorized=True)
        self.assertEqual("AUDIO_INPUT_REQUIRED", caught.exception.code)
        self.assertIn("output", caught.exception.message)

    def test_extract_14_supplied_future_fields_do_not_imply_adapter_or_service_success(self):
        # This exercises unavailable-adapter refusal, NOT a real service failure.
        tool = self.tool("transcribe_audio")
        output = self.root / "uncreated-transcript.txt"
        before = source_bytes(self.workspace)
        with patch.object(Path, "open", side_effect=AssertionError("no implicit adapter invocation")):
            with self.assertRaises(ArtifactInputError) as caught:
                tool.transcribe_audio(
                    self.root / "not-provided.wav", service="future-unselected-service",
                    model="future-unselected-model", data_scope="self-owned-fixture-only",
                    operation="transcribe", output=output, authorized=True,
                )
        self.assertEqual("SOURCE_ADAPTER_UNAVAILABLE", caught.exception.code)
        self.assertFalse(output.exists())
        self.assertEqual(before, source_bytes(self.workspace))

    def test_extract_13_audio_cli_is_machine_readable_refusal_and_preserves_existing_output(self):
        output = self.write(b"owner transcript", "existing.txt")
        before = source_bytes(self.workspace)
        result = self.cli("transcribe_audio", "--source", str(self.root / "not-provided.wav"),
                          "--output", str(output))
        self.cli_error(result, "AUDIO_AUTHORIZATION_REQUIRED")
        self.assertEqual(before, source_bytes(self.workspace))

    def test_extract_14_audio_cli_never_fakes_transcription_with_complete_future_inputs(self):
        result = self.cli(
            "transcribe_audio", "--source", str(self.root / "not-provided.wav"),
            "--service", "future-unselected", "--model", "future-unselected",
            "--data-scope", "self-owned-fixture-only", "--operation", "transcribe",
            "--output", str(self.root / "absent.txt"), "--authorized",
        )
        self.cli_error(result, "SOURCE_ADAPTER_UNAVAILABLE")
        self.assertEqual({}, source_bytes(self.workspace))


if __name__ == "__main__":
    unittest.main()
