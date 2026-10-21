"""ENH-16 / EXTRACT-05..09,15: independently hand-derived scores and origins."""

from __future__ import annotations

import copy
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from artifact_io import ArtifactInputError
from tests.helpers import WORKTREE, source_bytes, temporary_workspace


def candidate(path, **changes):
    # A deliberately supplied candidate record, not a calibrated/confirmed fact.
    result = {
        "candidate_id": "candidate-0001",
        "kind": "rule",
        "nature": "observed",
        "text": "Rule: Members must keep receipts.",
        "fragment": "Rule: Members must keep receipts.",
        "source": {"path": str(path), "kind": "text",
                   "baseline": "sha256:" + "1" * 64, "byte_count": 32},
        "location": {"line": 3, "paragraph": 2},
        "uncertainty": [],
        "extraction_reason": "Explicit source label; no business confirmation.",
        "clarification": "Ask the actual owner to reconcile contrary sources.",
    }
    result.update(changes)
    return result


class CandidateScoringTests(unittest.TestCase):
    def setUp(self):
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / "explicitly supplied source.txt"

    def tool(self):
        self.assertIsNotNone(importlib.util.find_spec("score_candidates"),
                             "ENH-16 transparent scoring is not implemented")
        return importlib.import_module("score_candidates")

    def score(self, items):
        return self.tool().score_candidates(items)

    def error(self, items, code):
        with self.assertRaises(ArtifactInputError) as caught:
            self.score(items)
        self.assertEqual(code, caught.exception.code, str(caught.exception))

    def cli(self, *args):
        script = WORKTREE / ".github/utilities/score_candidates.py"
        self.assertTrue(script.is_file(), "ENH-16 scoring CLI is missing")
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(script), "--root", str(self.root), *args],
            cwd=self.root, shell=False, capture_output=True, text=True, encoding="utf-8",
        )

    def test_extract_08_exact_observed_score_is_transparent_and_deterministic(self):
        items = [candidate(self.path)]
        original = copy.deepcopy(items)
        first = self.score(items)
        second = self.score(items)
        self.assertEqual(first, second)
        self.assertEqual(original, items)
        score = first[0]["score"]
        self.assertEqual(100, score["value"])
        self.assertEqual({"minimum": 0, "maximum": 100}, score["scale"])
        self.assertEqual([("evidence", 30), ("locator", 25), ("completeness", 25),
                          ("uncertainty", 20)],
                         [(f["factor"], f["value"]) for f in score["factors"]])
        self.assertTrue(all(f["reason"] for f in score["factors"]))
        self.assertIn("not a probability", score["meaning"])
        self.assertNotIn("accepted", score)
        self.assertEqual({}, source_bytes(self.root))

    def test_extract_08_uncertain_and_inferred_scores_follow_literal_factors(self):
        uncertain = candidate(self.path, text="Rule: Maybe members should keep receipts.",
                              fragment="Rule: Maybe members should keep receipts.",
                              nature="uncertain", uncertainty=["proposal language: maybe", "proposal language: should"])
        inferred = candidate(self.path, text="Members must keep receipts.",
                             fragment="Members must keep receipts.", nature="inferred")
        values = self.score([uncertain, inferred])
        self.assertEqual([80, 75], [item["score"]["value"] for item in values])
        self.assertEqual([0, 10], [item["score"]["factors"][3]["value"] for item in values])
        self.assertEqual([25, 10], [item["score"]["factors"][2]["value"] for item in values])

    def test_extract_08_short_evidence_is_not_given_completeness_credit(self):
        item = candidate(self.path, text="Rule: X", fragment="Rule: X")
        self.assertEqual(90, self.score([item])[0]["score"]["value"])

    def test_extract_05_repeats_and_contrary_sources_keep_all_provenance(self):
        a = candidate(self.path)
        b = candidate(self.root / "contrary source.txt",
                      text="Rule: Members must not keep receipts.",
                      fragment="Rule: Members must not keep receipts.")
        c = candidate(self.path, location={"line": 5, "paragraph": 3}, candidate_id="candidate-0002")
        items = [a, b, c]
        scored = self.score(items)
        self.assertEqual(3, len(scored))
        self.assertEqual(items, [{k: v for k, v in item.items() if k != "score"} for item in scored])
        self.assertEqual([100, 100, 100], [item["score"]["value"] for item in scored])
        self.assertEqual([str(self.path), str(self.root / "contrary source.txt"), str(self.path)],
                         [item["source"]["path"] for item in scored])

    def test_extract_08_empty_input_returns_empty_not_a_business_pass(self):
        self.assertEqual([], self.score([]))

    def test_extract_09_candidate_collection_bound_prevents_unbounded_score_expansion(self):
        self.error([candidate(self.path)] * 10_001, "CANDIDATE_LIMIT_EXCEEDED")

    def test_extract_09_missing_or_invalid_identity_is_not_zero_with_no_error(self):
        cases = []
        for field in ("path", "baseline", "kind", "byte_count"):
            item = candidate(self.path)
            del item["source"][field]
            cases.append(item)
        for field, value in (("path", "unknown"), ("baseline", "unknown"),
                             ("byte_count", -1), ("byte_count", 0), ("byte_count", True), ("kind", "audio"),
                             ("path", "https://example.invalid/a.txt"),
                             ("path", str(self.root / "child" / ".." / "source.txt")),
                             ("path", str(self.root / "source.txt") + ":hidden"),
                             ("path", str(self.root / "bad\ud800.txt"))):
            item = candidate(self.path)
            item["source"][field] = value
            cases.append(item)
        for item in cases:
            with self.subTest(item=item):
                self.error([item], "INVALID_SOURCE_IDENTITY")

    def test_extract_09_unsupported_kind_and_value_are_typed(self):
        self.error([candidate(self.path, kind="confirmed-rule")], "INVALID_CANDIDATE_KIND")
        for change in ({"nature": "confirmed"}, {"text": ""}, {"fragment": ""},
                       {"candidate_id": "REQ-001"}, {"uncertainty": "unknown"},
                       {"extraction_reason": ""}, {"clarification": ""},
                       {"score": float("nan")}, {"confirmation": {"by": "fake"}}):
            with self.subTest(change=change):
                self.error([candidate(self.path, **change)], "INVALID_CANDIDATE")
        self.error({"not": "a list"}, "INVALID_CANDIDATE")
        self.error([None], "INVALID_CANDIDATE")

    def test_extract_09_missing_source_is_not_invented(self):
        item = candidate(self.path)
        del item["source"]
        self.error([item], "INVALID_SOURCE_IDENTITY")

    def test_extract_09_bad_locator_and_inconsistent_evidence_are_errors(self):
        for location in (None, {}, {"line": 0, "paragraph": 1}, {"line": True, "paragraph": 1},
                         {"line": 1, "paragraph": -1}, {"line": 1, "paragraph": 1, "page": 99}):
            with self.subTest(location=location):
                self.error([candidate(self.path, location=location)], "INVALID_CANDIDATE_LOCATION")
        self.error([candidate(self.path, text="Rule: Invented text not in evidence.")],
                   "INVALID_CANDIDATE")

    def test_extract_09_escaped_control_and_surrogate_values_are_typed_cli_errors(self):
        path = self.root / "candidates.json"
        for value in ("\ud800", "\x00"):
            with self.subTest(value=repr(value)):
                item = candidate(self.path, text=value, fragment=value, kind="statement", nature="inferred")
                path.write_text(json.dumps([item]), encoding="utf-8")
                result = self.cli("--input", path.name)
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertEqual("INVALID_CANDIDATE", json.loads(result.stdout)["error"]["code"])
                self.assertEqual("", result.stderr)

    def test_extract_09_uncertainty_and_nature_cannot_contradict_evidence_markers(self):
        self.error([candidate(self.path, uncertainty=["maybe"])], "INVALID_CANDIDATE")
        self.error([candidate(self.path, nature="uncertain")], "INVALID_CANDIDATE")
        self.error([candidate(self.path, text="Rule: Maybe receipts are needed.",
                              fragment="Rule: Maybe receipts are needed.")], "INVALID_CANDIDATE")

    def test_extract_08_real_extracted_markdown_transcript_and_docx_are_scoreable(self):
        self.assertIsNotNone(importlib.util.find_spec("extract_source"), "ENH-16 extractor missing")
        from extract_source import extract_candidates
        from tests.test_source_extraction import docx_bytes
        inputs = (
            ("source.md", "markdown", b"Rule: Members must keep receipts.\n"),
            ("source.txt", "transcript",
             b'{"speaker":"A","timestamp":"00:00:01.000","text":"Rule: Members must keep receipts."}\n'),
            ("source.docx", "docx", docx_bytes()),
        )
        for name, kind, raw in inputs:
            with self.subTest(kind=kind):
                path = self.root / name
                path.write_bytes(raw)
                report = extract_candidates(path, kind)
                result = self.score(report["candidates"])
                self.assertEqual(report["candidate_count"], len(result))
                self.assertEqual(100, result[0]["score"]["value"])
                self.assertEqual(report["source"], result[0]["source"])

    def test_extract_08_transcript_with_json_escapes_is_not_a_missing_evidence_false_positive(self):
        item = candidate(
            self.root / "transcript.txt",
            source={"path": str(self.root / "transcript.txt"), "kind": "transcript",
                    "baseline": "sha256:" + "2" * 64, "byte_count": 200},
            text="Rule: члены € must keep receipts.",
            fragment='{"speaker":"A","timestamp":"00:00:01.000","text":"Rule: \\u0447\\u043b\\u0435\\u043d\\u044b \\u20ac must keep receipts."}',
            location={"line": 1, "turn": 1, "speaker": "A", "timestamp": "00:00:01.000"},
        )
        self.assertEqual(100, self.score([item])[0]["score"]["value"])

    def test_extract_08_real_markdown_inline_comment_keeps_raw_fragment_and_scores_visible_text(self):
        self.assertIsNotNone(importlib.util.find_spec("extract_source"), "ENH-16 extractor missing")
        from extract_source import extract_candidates
        path = self.root / "inline-comment.md"
        raw = "Rule: Members <!-- proposal: should? --> must keep receipts.\n"
        path.write_text(raw, encoding="utf-8")
        report = extract_candidates(path, "markdown")
        item = report["candidates"][0]
        self.assertEqual(raw.rstrip("\n"), item["fragment"])
        self.assertEqual("Rule: Members  must keep receipts.", item["text"])
        self.assertEqual("observed", item["nature"])
        self.assertEqual(100, self.score([item])[0]["score"]["value"])

    def test_extract_15_cli_scores_extraction_envelope_and_preserves_source_identity(self):
        self.assertIsNotNone(importlib.util.find_spec("extract_source"), "ENH-16 extractor missing")
        from extract_source import extract_candidates
        self.path.write_bytes(b"Rule: Members must keep receipts.\n")
        report = extract_candidates(self.path, "text")
        input_path = self.root / "candidate input.json"
        input_path.write_text(json.dumps(report), encoding="utf-8")
        before = source_bytes(self.root)
        output = self.root / "scored output.json"
        result = self.cli("--input", str(input_path), "--output", str(output))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(report["source"], payload["source"])
        self.assertEqual(100, payload["candidates"][0]["score"]["value"])
        self.assertEqual(payload, json.loads(output.read_bytes()))
        self.assertEqual(before, {k: v for k, v in source_bytes(self.root).items()
                                  if k != output.name})

    def test_extract_15_cli_list_input_default_stdout_is_read_only(self):
        path = self.root / "candidates.json"
        path.write_text(json.dumps([candidate(self.path)]), encoding="utf-8")
        before = source_bytes(self.root)
        result = self.cli("--input", path.name)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(100, json.loads(result.stdout)[0]["score"]["value"])
        self.assertEqual(before, source_bytes(self.root))

    def test_extract_15_cli_conflicting_output_outside_and_missing_parent_do_not_write(self):
        input_path = self.root / "candidates.json"
        input_path.write_text(json.dumps([candidate(self.path)]), encoding="utf-8")
        for destination, code in ((str(input_path), "REPORT_CONFLICT"),
                                  ("../outside.json", "OUTSIDE_ROOT"),
                                  ("missing/new.json", "REPORT_WRITE_ERROR")):
            with self.subTest(destination=destination):
                before = source_bytes(self.root)
                result = self.cli("--input", str(input_path), "--output", destination)
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertEqual(code, json.loads(result.stdout)["error"]["code"])
                self.assertEqual(before, source_bytes(self.root))

    def test_extract_09_cli_invalid_json_duplicate_keys_and_values_are_errors(self):
        path = self.root / "bad.json"
        for raw in ('{"candidates":[],"candidates":[]}', "not JSON", "[NaN]", "[{}]"):
            with self.subTest(raw=raw):
                path.write_text(raw, encoding="utf-8")
                result = self.cli("--input", path.name)
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertEqual("input-error", json.loads(result.stdout)["status"])
                self.assertEqual("", result.stderr)


    # T16-I1/I2/I3: real source units and intrinsic consistency, not origin authentication.
    def extract(self, text, kind="text", name=None):
        from extract_source import extract_candidates
        from tests.test_source_extraction import W, docx_bytes
        path = self.root / (name or {"text": "unit.txt", "markdown": "unit.md",
                                    "transcript": "turns.txt", "docx": "unit.docx"}[kind])
        if kind == "docx":
            document = (f'<w:document xmlns:w="{W}"><w:body><w:p><w:r><w:t>'
                        + text + '</w:t></w:r></w:p></w:body></w:document>')
            raw = docx_bytes(document=document)
        else:
            raw = text.encode("utf-8")
        path.write_bytes(raw)
        return extract_candidates(path, kind)

    def envelope_cli(self, report, code=None):
        sequence = getattr(self, "_input_sequence", 0) + 1
        self._input_sequence = sequence
        source = self.root / f"envelope-{sequence}.json"
        output = self.root / f"scored-{sequence}.json"
        source.write_text(json.dumps(report, ensure_ascii=True), encoding="utf-8")
        before = source_bytes(self.root)
        result = self.cli("--input", source.name, "--output", output.name)
        self.assertEqual(0 if code is None else 2, result.returncode,
                         (result.stdout + result.stderr)[:400])
        self.assertEqual("", result.stderr[:400])
        payload = json.loads(result.stdout)
        if code is None:
            self.assertEqual(payload, json.loads(output.read_bytes()))
            self.assertEqual(before, {k: v for k, v in source_bytes(self.root).items()
                                      if k != output.name})
        else:
            self.assertEqual("input-error", payload["status"])
            self.assertEqual(code, payload["error"]["code"])
            self.assertNotIn("candidates", payload)
            self.assertFalse(output.exists(), "An invalid whole input must not create scored output")
            self.assertEqual(before, source_bytes(self.root))
        return payload

    def test_fix1_i1_omitted_proposal_and_restrictive_suffix_are_not_complete_units(self):
        cases = (
            ("Maybe Rule: Members must keep receipts.", "Rule: Members must keep receipts."),
            ("Rule: Members must keep receipts only while active.",
             "Rule: Members must keep receipts"),
        )
        for kind in ("text", "markdown", "docx"):
            for fragment, shortened in cases:
                with self.subTest(kind=kind, fragment=fragment):
                    report = self.extract(fragment, kind)
                    altered = copy.deepcopy(report["candidates"][0])
                    altered.update(text=shortened, kind="rule", nature="observed", uncertainty=[])
                    self.error([altered], "INVALID_CANDIDATE")

    def test_fix1_i1_normalization_is_only_outer_whitespace_not_case_or_interior_edits(self):
        report = self.extract(" \tRule: Members  must keep receipts. \t")
        self.assertEqual(100, self.score(report["candidates"])[0]["score"]["value"])
        for text in ("Rule: Members must keep receipts.", "Rule: members  must keep receipts.",
                     "Rule: Members  must keep receipts"):
            with self.subTest(text=text):
                altered = copy.deepcopy(report["candidates"][0])
                altered["text"] = text
                self.error([altered], "INVALID_CANDIDATE")

    def test_fix1_i1_full_normalized_classification_and_all_markers_must_agree(self):
        item = self.extract("Rule: Maybe members should keep receipts.")["candidates"][0]
        self.assertEqual(["proposal language: maybe", "proposal language: should"], item["uncertainty"])
        for uncertainty in (["proposal language: maybe"], ["proposal language: should"],
                            ["proposal language: should", "proposal language: maybe"]):
            with self.subTest(uncertainty=uncertainty):
                changed = copy.deepcopy(item)
                changed["uncertainty"] = uncertainty
                self.error([changed], "INVALID_CANDIDATE")
        direct = self.extract("Rule: Members must keep receipts.")["candidates"][0]
        direct.update(nature="uncertain", uncertainty=["caller-chosen override"])
        self.error([direct], "INVALID_CANDIDATE")

    def test_fix1_i3_actual_multiline_comment_roundtrip_keeps_fragment_context_and_location(self):
        raw = "<!--\r\n    --> Rule: Members <!--x--> must keep receipts.\r\n"
        report = self.extract(raw, "markdown")
        self.assertEqual((2, 1), (report["unit_count"], report["candidate_count"]))
        item = report["candidates"][0]
        self.assertEqual("    --> Rule: Members <!--x--> must keep receipts.", item["fragment"])
        self.assertEqual("Rule: Members  must keep receipts.", item["text"])
        self.assertEqual({"line": 2, "paragraph": 1}, item["location"])
        try:
            scored = self.score(report["candidates"])
        except ArtifactInputError as error:
            self.fail(f"T16-I3 extractor rejected by its scorer: {error.code}")
        self.assertEqual(100, scored[0]["score"]["value"])
        self.assertEqual({"in_comment": True}, item.get("markdown_context"))
        self.assertEqual(item, {k: v for k, v in scored[0].items() if k != "score"})
        self.assertEqual(100, self.envelope_cli(report)["candidates"][0]["score"]["value"])

    def test_fix1_i1_i3_comment_context_does_not_allow_dropping_visible_maybe(self):
        report = self.extract("<!--\n    --> Maybe Rule: Members <!--x--> must keep receipts.", "markdown")
        item = report["candidates"][0]
        self.assertEqual("Maybe Rule: Members  must keep receipts.", item["text"])
        self.assertEqual("uncertain", item["nature"])
        try:
            result = self.score([item])
        except ArtifactInputError as error:
            self.fail(f"Supported complete uncertain Markdown unit rejected: {error.code}")
        self.assertEqual(65, result[0]["score"]["value"])
        changed = copy.deepcopy(item)
        changed.update(text="Rule: Members  must keep receipts.", nature="observed", uncertainty=[])
        self.error([changed], "INVALID_CANDIDATE")

    def test_fix1_i3_context_is_structural_not_a_duplicated_visible_text_override(self):
        report = self.extract("Rule: Maybe members must keep receipts.", "markdown")
        for context in ({"in_comment": 1}, {"in_comment": "yes"}, {},
                        {"in_comment": False, "visible_text": "Rule: Members must keep receipts."}):
            with self.subTest(context=context):
                item = copy.deepcopy(report["candidates"][0])
                item["markdown_context"] = context
                self.error([item], "INVALID_CANDIDATE")
        item = copy.deepcopy(report["candidates"][0])
        item["markdown_context"] = {"in_comment": True}
        self.error([item], "INVALID_CANDIDATE")

    def test_fix1_i3_shared_scanner_keeps_inline_literals_and_fences_out_of_comment_state(self):
        raw = ("```\n<!--\n```\n\nRule: Literal `<!--` must stay.\n\n"
               "<!--\n    --> Rule: Members <!--x--> must keep receipts.\n"
               "    Rule: indented code is not a candidate.\n")
        report = self.extract(raw, "markdown")
        self.assertEqual(["Rule: Literal `<!--` must stay.", "Rule: Members  must keep receipts."],
                         [i["text"] for i in report["candidates"]])
        try:
            values = self.score(report["candidates"])
        except ArtifactInputError as error:
            self.fail(f"Shared Markdown context lost at score boundary: {error.code}")
        self.assertEqual([100, 100], [i["score"]["value"] for i in values])
        self.assertEqual([False, True], [i["markdown_context"]["in_comment"] for i in report["candidates"]])

    def test_fix1_i2_zero_units_and_line_outside_envelope_fail_without_output(self):
        original = self.extract("Rule: Members must keep receipts.\n")
        no_units = copy.deepcopy(original)
        no_units["unit_count"] = 0
        outside = copy.deepcopy(original)
        outside["candidates"][0]["location"]["line"] = 2
        for report, code in ((no_units, "INVALID_CANDIDATE"), (outside, "INVALID_CANDIDATE_LOCATION")):
            with self.subTest(code=code):
                self.envelope_cli(report, code)

    def test_fix1_i2_plain_groups_and_source_order_obey_complete_envelope_semantics(self):
        original = self.extract("Rule: First statement must stay.\n\nRule: Second statement must stay.\n")
        for mutation in ("same-group-across-blank-gap", "duplicate-line", "backwards"):
            with self.subTest(mutation=mutation):
                altered = copy.deepcopy(original)
                if mutation == "same-group-across-blank-gap":
                    altered["candidates"][1]["location"]["paragraph"] = 1
                elif mutation == "duplicate-line":
                    altered["candidates"][1]["location"] = {"line": 1, "paragraph": 1}
                else:
                    altered["candidates"].reverse()
                self.envelope_cli(altered, "INVALID_CANDIDATE_LOCATION")

    def test_fix1_i2_markdown_sparse_groups_are_valid_but_impossible_groups_are_not(self):
        report = self.extract("# Header\n\n<!-- omitted group -->\n\nRule: Keep all sources.\n\n"
                              "# Another header\n\nCapability: Members can view receipts.\n", "markdown")
        self.assertEqual([{"line": 5, "paragraph": 3}, {"line": 9, "paragraph": 5}],
                         [i["location"] for i in report["candidates"]])
        self.assertEqual([100, 100], [i["score"]["value"] for i in self.envelope_cli(report)["candidates"]])
        impossible = copy.deepcopy(report)
        impossible["candidates"][1]["location"]["paragraph"] = 2
        self.envelope_cli(impossible, "INVALID_CANDIDATE_LOCATION")

    def test_fix1_i2_transcript_turns_are_sequential_not_inferred_from_timestamps(self):
        raw = ('\n{"speaker":"A","timestamp":"00:00:02.000","text":"Rule: Keep all sources."}\n'
               '\n{"speaker":"B","timestamp":"00:00:01.000","text":"Rule: Keep contrary sources."}\n')
        report = self.extract(raw, "transcript")
        self.assertEqual(4, report["unit_count"])
        self.assertEqual([2, 4], [i["location"]["line"] for i in report["candidates"]])
        self.assertEqual([1, 2], [i["location"]["turn"] for i in report["candidates"]])
        self.envelope_cli(report)
        for mutation in ("first-turn-not-one", "turn-outside-line", "line-outside-units"):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(report)
                if mutation == "first-turn-not-one":
                    changed["candidates"][0]["location"]["turn"] = 2
                elif mutation == "turn-outside-line":
                    changed["candidates"][0]["location"]["turn"] = 3
                else:
                    changed["candidates"][1]["location"]["line"] = 5
                self.envelope_cli(changed, "INVALID_CANDIDATE_LOCATION")

    def test_fix1_i2_docx_paragraph_bounds_and_related_coordinates_are_intrinsic(self):
        from extract_source import extract_candidates
        from tests.test_source_extraction import docx_bytes
        path = self.root / "paragraph-table.docx"
        path.write_bytes(docx_bytes())
        original = extract_candidates(path, "docx")
        self.assertEqual((4, 3), (original["unit_count"], original["candidate_count"]))
        mutations = (("paragraph", 5), ("block", 99), ("table", 99),
                     ("row", 99), ("cell", 99), ("cell_paragraph", 99))
        for field, value in mutations:
            with self.subTest(field=field):
                altered = copy.deepcopy(original)
                altered["candidates"][1]["location"][field] = value
                self.envelope_cli(altered, "INVALID_CANDIDATE_LOCATION")
        repeated = copy.deepcopy(original)
        repeated["candidates"].append(copy.deepcopy(repeated["candidates"][1]))
        repeated["candidate_count"] += 1
        self.envelope_cli(repeated, "INVALID_CANDIDATE_LOCATION")

    def test_fix1_i2_list_checks_knowable_bounds_but_preserves_partial_and_repeat_origins(self):
        from extract_source import extract_candidates
        from tests.test_source_extraction import docx_bytes
        bad_text = candidate(self.path, location={"line": 2, "paragraph": 2})
        with self.subTest(kind="text"):
            self.error([bad_text], "INVALID_CANDIDATE_LOCATION")
        turn = self.extract('{"speaker":"A","timestamp":"00:00:01.000","text":"Rule: Keep all sources."}',
                            "transcript")["candidates"][0]
        turn["location"]["turn"] = 2
        with self.subTest(kind="transcript"):
            self.error([turn], "INVALID_CANDIDATE_LOCATION")
        path = self.root / "partial.docx"
        path.write_bytes(docx_bytes())
        item = extract_candidates(path, "docx")["candidates"][1]
        for field, value in (("block", 3), ("table", 3), ("row", 2),
                             ("cell", 2), ("cell_paragraph", 2)):
            with self.subTest(field=field):
                changed = copy.deepcopy(item)
                changed["location"][field] = value
                self.error([changed], "INVALID_CANDIDATE_LOCATION")
        tool = self.tool()
        with patch.object(Path, "open", side_effect=AssertionError("Do not reopen/authenticate origins")):
            values = tool.score_candidates([item, copy.deepcopy(item), candidate(self.path)])
        self.assertEqual(3, len(values))
        self.assertEqual([100, 100, 100], [i["score"]["value"] for i in values])

    def test_fix1_i2_docx_known_block_table_and_cell_offsets_must_not_contradict(self):
        from extract_source import extract_candidates
        from tests.test_source_extraction import W, docx_bytes
        path = self.root / "known-blocks.docx"
        path.write_bytes(docx_bytes())
        changed = extract_candidates(path, "docx")
        for item in changed["candidates"][1:]:
            item["location"]["table"] = 2  # Block 1 is a known paragraph, not a hidden first table.
        with self.subTest(contradiction="table-index-cannot-use-known-plain-block"):
            self.envelope_cli(changed, "INVALID_CANDIDATE_LOCATION")
        document = (f'<w:document xmlns:w="{W}"><w:body><w:tbl><w:tr><w:tc>'
                    '<w:p><w:r><w:t>Rule: First statement must stay.</w:t></w:r></w:p><w:p/>'
                    '<w:p><w:r><w:t>Rule: Second statement must stay.</w:t></w:r></w:p>'
                    '</w:tc></w:tr></w:tbl></w:body></w:document>')
        path.write_bytes(docx_bytes(document=document))
        report = extract_candidates(path, "docx")
        self.assertEqual([1, 3], [i["location"]["paragraph"] for i in report["candidates"]])
        self.envelope_cli(report)
        report["candidates"][1]["location"]["cell_paragraph"] = 2
        with self.subTest(contradiction="same-cell-global-and-local-paragraph-offset"):
            self.envelope_cli(report, "INVALID_CANDIDATE_LOCATION")

    def test_fix1_i2_docx_known_first_and_adjacent_block_anchors_cannot_hide_paragraphs(self):
        from extract_source import extract_candidates
        from tests.test_source_extraction import W, docx_bytes
        first = self.extract("Rule: Keep all sources.", "docx")
        first["candidates"][0]["location"]["paragraph"] = 2
        with self.subTest(contradiction="first-plain-block"):
            self.error(first["candidates"], "INVALID_CANDIDATE_LOCATION")
        cell = "<w:tc><w:p><w:r><w:t>Rule: Keep all sources.</w:t></w:r></w:p></w:tc>"
        document = (f'<w:document xmlns:w="{W}"><w:body><w:tbl><w:tr>'
                    + cell + "</w:tr></w:tbl></w:body></w:document>")
        path = self.root / "first-table.docx"
        path.write_bytes(docx_bytes(document=document))
        first_table = extract_candidates(path, "docx")
        first_table["candidates"][0]["location"]["paragraph"] = 2
        with self.subTest(contradiction="first-table-first-cell"):
            self.error(first_table["candidates"], "INVALID_CANDIDATE_LOCATION")
        path.write_bytes(docx_bytes())
        adjacent = extract_candidates(path, "docx")
        adjacent["unit_count"] += 1
        for item in adjacent["candidates"][1:]:
            item["location"]["paragraph"] += 1
        with self.subTest(contradiction="no-hidden-paragraph-between-known-adjacent-blocks"):
            self.envelope_cli(adjacent, "INVALID_CANDIDATE_LOCATION")
        # No envelope/source is supplied for this list record. A preceding unknown
        # table could account for the offset; do not invent a total or reopen it.
        supplied = candidate(
            self.root / "unprovided.docx",
            source={"path": str(self.root / "unprovided.docx"), "kind": "docx",
                    "baseline": "sha256:" + "3" * 64, "byte_count": 1000},
            location={"part": "word/document.xml", "block": 2, "paragraph": 10},
        )
        self.assertEqual(100, self.score([supplied])[0]["score"]["value"])
        empty = "<w:tc><w:p/></w:tc>"
        document = (f'<w:document xmlns:w="{W}"><w:body><w:tbl><w:tr>'
                    + empty + cell + "</w:tr><w:tr>" + cell + empty
                    + "</w:tr></w:tbl></w:body></w:document>")
        path.write_bytes(docx_bytes(document=document))
        trailing = extract_candidates(path, "docx")
        self.assertEqual((4, 2), (trailing["unit_count"], trailing["candidate_count"]))
        self.assertEqual([2, 3], [i["location"]["paragraph"] for i in trailing["candidates"]])
        self.envelope_cli(trailing)
        trailing["unit_count"] = 3
        with self.subTest(contradiction="known-width-implies-trailing-empty-cell-paragraph"):
            self.envelope_cli(trailing, "INVALID_CANDIDATE_LOCATION")

    def test_fix1_i2_empty_lines_and_docx_paragraph_gaps_are_not_candidate_count(self):
        from extract_source import extract_candidates
        from tests.test_source_extraction import W, docx_bytes
        plain = self.extract("\n\nRule: Keep all sources.\n\n\n")
        self.assertEqual((5, 1), (plain["unit_count"], plain["candidate_count"]))
        self.assertEqual({"line": 3, "paragraph": 1}, plain["candidates"][0]["location"])
        self.envelope_cli(plain)
        document = (f'<w:document xmlns:w="{W}"><w:body><w:p/>'
                    '<w:p><w:r><w:t>Rule: Keep all sources.</w:t></w:r></w:p><w:p/>'
                    '<w:tbl><w:tr><w:tc><w:p/></w:tc><w:tc><w:p/>'
                    '<w:p><w:r><w:t>Capability: Members can view receipts.</w:t></w:r></w:p></w:tc></w:tr>'
                    '<w:tr><w:tc><w:p/></w:tc><w:tc><w:p><w:r><w:t>Rule: Keep contrary sources.</w:t>'
                    '</w:r></w:p></w:tc></w:tr></w:tbl><w:p/></w:body></w:document>')
        path = self.root / "empty-paragraphs.docx"
        path.write_bytes(docx_bytes(document=document))
        report = extract_candidates(path, "docx")
        self.assertEqual((9, 3), (report["unit_count"], report["candidate_count"]))
        self.assertEqual([2, 6, 8], [i["location"]["paragraph"] for i in report["candidates"]])
        self.assertEqual([100, 100, 100],
                         [i["score"]["value"] for i in self.envelope_cli(report)["candidates"]])

    def test_fix1_i2_later_invalid_unit_rejects_whole_input_not_a_scored_prefix(self):
        report = self.extract("Rule: First statement must stay.\nRule: Second statement must stay.\n")
        report["candidates"][1]["location"]["line"] = 3
        self.envelope_cli(report, "INVALID_CANDIDATE_LOCATION")


if __name__ == "__main__":
    unittest.main()
