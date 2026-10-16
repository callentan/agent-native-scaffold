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
            text="Rule: 成员 must keep receipts.",
            fragment='{"speaker":"A","timestamp":"00:00:01.000","text":"Rule: \\u6210\\u5458 must keep receipts."}',
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


if __name__ == "__main__":
    unittest.main()
