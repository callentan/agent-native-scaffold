"""Deterministic evidence-quality scores, not probabilities or acceptance."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re

from artifact_io import ArtifactInputError, iter_markdown_lines
from extract_source import (
    CANDIDATE_KINDS, SOURCE_KINDS, TIMESTAMP, _LABEL, _classify, _decode, _json_value,
    _local_path, _print_error, _read_bytes, _transcript_turn, _valid_text, _write_output,
)


_FIELDS = frozenset(("candidate_id", "kind", "nature", "text", "fragment", "source",
                     "location", "uncertainty", "extraction_reason", "clarification"))
MAX_CANDIDATES = 10_000


def _positive(value) -> bool:
    return type(value) is int and value > 0


def _source(value) -> None:
    if (not isinstance(value, dict) or set(value) != {"path", "kind", "baseline", "byte_count"}
            or not _valid_text(value.get("path")) or any(ord(c) < 32 for c in value["path"])
            or value["path"].startswith(("//", "\\\\"))
            or "://" in value["path"] or not Path(value["path"]).is_absolute()
            or any(part in (".", "..") for part in re.split(r"[/\\]", value["path"]))
            or ":" in Path(value["path"]).as_posix()[len(Path(value["path"]).anchor):]
            or not isinstance(value.get("kind"), str) or value["kind"] not in SOURCE_KINDS
            or not isinstance(value.get("baseline"), str)
            or re.fullmatch(r"sha256:[0-9a-f]{64}", value["baseline"]) is None
            or type(value.get("byte_count")) is not int or value["byte_count"] < 0):
        raise ArtifactInputError("INVALID_SOURCE_IDENTITY", "candidates", 1,
                                 "Each candidate needs an absolute local path, supported kind, SHA256 and byte count")


def _location(item: dict) -> None:
    value = item.get("location")
    kind = item["source"]["kind"]
    valid = isinstance(value, dict)
    if valid and kind in ("markdown", "text"):
        valid = set(value) == {"line", "paragraph"} and all(_positive(v) for v in value.values())
    elif valid and kind == "transcript":
        valid = (set(value) == {"line", "turn", "speaker", "timestamp"}
                 and _positive(value["line"]) and _positive(value["turn"])
                 and _valid_text(value["speaker"])
                 and isinstance(value["timestamp"], str) and TIMESTAMP.fullmatch(value["timestamp"]) is not None)
    elif valid and kind == "docx":
        fields = {"part", "block", "paragraph"}
        if set(value) & {"table", "row", "cell", "cell_paragraph"}:
            fields |= {"table", "row", "cell", "cell_paragraph"}
        valid = (set(value) == fields and value["part"] == "word/document.xml"
                 and all(_positive(v) for k, v in value.items() if k != "part"))
    if not valid:
        raise ArtifactInputError("INVALID_CANDIDATE_LOCATION", item["source"]["path"], 1,
                                 "Expected exact positive line/paragraph, turn/time or DOCX paragraph/cell coordinates")


def _validate(item) -> None:
    if not isinstance(item, dict):
        raise ArtifactInputError("INVALID_CANDIDATE", "candidates", 1, "Expected candidate records")
    _source(item.get("source"))
    if item["source"]["byte_count"] == 0:
        raise ArtifactInputError("INVALID_SOURCE_IDENTITY", "candidates", 1,
                                 "A zero-byte source cannot supply a nonempty candidate")
    if not isinstance(item.get("kind"), str) or item["kind"] not in CANDIDATE_KINDS:
        raise ArtifactInputError("INVALID_CANDIDATE_KIND", item["source"]["path"], 1, "Unsupported candidate kind")
    _location(item)
    valid = (
        set(item) == _FIELDS
        and isinstance(item.get("candidate_id"), str)
        and re.fullmatch(r"candidate-[0-9]{4,}", item["candidate_id"]) is not None
        and item.get("nature") in ("observed", "inferred", "uncertain")
        and all(_valid_text(item.get(k))
                for k in ("text", "fragment", "extraction_reason", "clarification"))
        and isinstance(item.get("uncertainty"), list)
        and all(_valid_text(reason) for reason in item["uncertainty"])
    )
    if valid:
        kind, nature, markers, _ = _classify(item["text"])
        valid = (kind == item["kind"]
                 and bool(item["uncertainty"]) == (item["nature"] == "uncertain")
                 and (not markers or item["nature"] == "uncertain")
                 and (item["nature"] == "uncertain" or item["nature"] == nature))
    if valid and item["source"]["kind"] == "transcript":
        turn = _transcript_turn(item["fragment"], Path(item["source"]["path"]), item["location"]["line"])
        valid = (turn["text"].strip() == item["text"]
                 and all(turn[k] == item["location"][k] for k in ("speaker", "timestamp")))
    elif valid:
        valid = item["text"] in item["fragment"]
        if not valid and item["source"]["kind"] == "markdown":
            valid = any(item["text"] in visible for _, visible in iter_markdown_lines(item["fragment"])
                        if visible is not None)
    if not valid:
        raise ArtifactInputError("INVALID_CANDIDATE", item["source"]["path"], 1,
                                 "Candidate values/evidence/nature are missing, inconsistent or unsupported")


def score_candidates(items: list[dict]) -> list[dict]:
    """Copy and score a concrete list, preserving duplicates and contrary evidence."""
    if not isinstance(items, list):
        raise ArtifactInputError("INVALID_CANDIDATE", "candidates", 1, "Expected a list of candidate records")
    if len(items) > MAX_CANDIDATES:
        raise ArtifactInputError("CANDIDATE_LIMIT_EXCEEDED", "candidates", 1, "At most 10,000 candidates may be scored")
    scored = []
    for item in items:
        _validate(item)
        explicit = _LABEL.match(item["text"]) is not None
        long_enough = len(item["text"].strip()) >= 16
        uncertainty = {"observed": 20, "inferred": 10, "uncertain": 0}[item["nature"]]
        factors = [
            {"factor": "evidence", "value": 30,
             "reason": "Nonempty text matches the literal/Markdown-visible fragment or decoded transcript; provenance syntax is valid, not authenticated."},
            {"factor": "locator", "value": 25,
             "reason": "Complete positive source-format coordinates are supplied; no source is reopened or speaker authenticated."},
            {"factor": "completeness", "value": (15 if explicit else 0) + (10 if long_enough else 0),
             "reason": f"Explicit type label: {15 if explicit else 0}/15; at least 16 stripped characters: {10 if long_enough else 0}/10. Not semantic completeness."},
            {"factor": "uncertainty", "value": uncertainty,
             "reason": f"Declared {item['nature']}: {uncertainty}/20; uncertainty does not resolve a business conflict."},
        ]
        result = copy.deepcopy(item)
        result["score"] = {
            "value": sum(f["value"] for f in factors),
            "scale": {"minimum": 0, "maximum": 100},
            "factors": factors,
            "meaning": "Deterministic evidence-quality heuristic, not a probability, model confidence or acceptance threshold.",
        }
        scored.append(result)
    return scored


def _score_payload(payload):
    if isinstance(payload, list):
        return score_candidates(payload)
    if not isinstance(payload, dict) or set(payload) != {
            "status", "source", "unit_count", "candidate_count", "candidates"}:
        raise ArtifactInputError("INVALID_CANDIDATE", "candidates", 1, "Expected a list or an extraction envelope")
    _source(payload["source"])
    if (not isinstance(payload["candidates"], list)
            or type(payload["candidate_count"]) is not int
            or payload["candidate_count"] != len(payload["candidates"])
            or type(payload["unit_count"]) is not int or payload["unit_count"] < 0
            or payload["status"] != ("extracted" if payload["candidates"] else "empty")):
        raise ArtifactInputError("INVALID_CANDIDATE", "candidates", 1, "Extraction status/counts are inconsistent")
    items = score_candidates(payload["candidates"])
    if any(item["source"] != payload["source"] for item in items):
        raise ArtifactInputError("INVALID_SOURCE_IDENTITY", "candidates", 1, "Envelope and candidate source identities differ")
    return {**payload, "candidates": items}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        path = _local_path(args.input, root=args.root)
        if path.suffix.lower() != ".json":
            raise ArtifactInputError("INVALID_SOURCE_FORMAT", path, 1, "Scoring input must be JSON")
        payload = _score_payload(_json_value(_decode(_read_bytes(path), path), path, "INVALID_CANDIDATE"))
        if args.output is not None:
            items = payload if isinstance(payload, list) else payload["candidates"]
            protected = [path, *(Path(item["source"]["path"]) for item in items)]
            if isinstance(payload, dict):
                protected.append(Path(payload["source"]["path"]))
            _write_output(payload, args.output, args.root, protected)
        print(json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=2))
        return 0
    except ArtifactInputError as error:
        return _print_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
