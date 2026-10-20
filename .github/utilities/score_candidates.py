"""Deterministic evidence-quality scores, not probabilities or acceptance."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re

from artifact_io import ArtifactInputError, iter_markdown_source_lines
from extract_source import (
    CANDIDATE_KINDS, SOURCE_KINDS, TIMESTAMP, _LABEL, _classify, _decode, _json_value,
    _local_path, _markdown_text, _print_error, _read_bytes, _transcript_turn, _valid_text, _write_output,
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
        if valid:
            valid = 2 * value["paragraph"] - 1 <= value["line"]
    elif valid and kind == "transcript":
        valid = (set(value) == {"line", "turn", "speaker", "timestamp"}
                 and _positive(value["line"]) and _positive(value["turn"])
                 and _valid_text(value["speaker"])
                 and isinstance(value["timestamp"], str) and TIMESTAMP.fullmatch(value["timestamp"]) is not None)
        if valid:
            valid = value["turn"] <= value["line"]
    elif valid and kind == "docx":
        fields = {"part", "block", "paragraph"}
        if set(value) & {"table", "row", "cell", "cell_paragraph"}:
            fields |= {"table", "row", "cell", "cell_paragraph"}
        valid = (set(value) == fields and value["part"] == "word/document.xml"
                 and all(_positive(v) for k, v in value.items() if k != "part"))
        if valid:
            valid = value["block"] <= value["paragraph"]
            if "table" in value:
                minimum = (value["block"] - 1 + (value["row"] - 1) * value["cell"]
                           + value["cell"] - 1 + value["cell_paragraph"])
                valid = valid and value["table"] <= value["block"] and value["paragraph"] >= minimum
                if value["block"] == value["row"] == value["cell"] == 1:
                    valid = valid and value["paragraph"] == value["cell_paragraph"]
            elif value["block"] == 1:
                valid = valid and value["paragraph"] == 1
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
    fields = _FIELDS | {"markdown_context"} if "markdown_context" in item else _FIELDS
    context = item.get("markdown_context", {"in_comment": False})
    valid = (
        set(item) == fields
        and isinstance(item.get("candidate_id"), str)
        and re.fullmatch(r"candidate-[0-9]{4,}", item["candidate_id"]) is not None
        and item.get("nature") in ("observed", "inferred", "uncertain")
        and all(_valid_text(item.get(k))
                for k in ("text", "fragment", "extraction_reason", "clarification"))
        and isinstance(item.get("uncertainty"), list)
        and all(_valid_text(reason) for reason in item["uncertainty"])
    )
    source_kind = item["source"]["kind"]
    if valid and "markdown_context" in item:
        valid = (source_kind == "markdown" and isinstance(context, dict)
                 and set(context) == {"in_comment"} and type(context["in_comment"]) is bool
                 and (not context["in_comment"] or item["location"]["line"] > 1))
    if valid and source_kind != "docx":
        valid = len(item["fragment"].splitlines()) == 1
    normalized = None
    if valid and item["source"]["kind"] == "transcript":
        turn = _transcript_turn(item["fragment"], Path(item["source"]["path"]), item["location"]["line"])
        normalized = turn["text"].strip()
        valid = all(turn[k] == item["location"][k] for k in ("speaker", "timestamp"))
    elif valid:
        if source_kind == "markdown":
            _, visible, _ = next(iter_markdown_source_lines(
                item["fragment"], initial_in_comment=context["in_comment"]))
            normalized = _markdown_text(visible)
        else:
            normalized = item["fragment"].strip()
    if valid:
        valid = normalized is not None and item["text"] == normalized
    if valid:
        kind, nature, markers, _ = _classify(normalized)
        valid = (kind == item["kind"] and nature == item["nature"] and markers == item["uncertainty"])
    if not valid:
        raise ArtifactInputError("INVALID_CANDIDATE", item["source"]["path"], 1,
                                 "Candidate values/evidence/nature are missing, inconsistent or unsupported")


def _validate_items(items) -> None:
    if not isinstance(items, list):
        raise ArtifactInputError("INVALID_CANDIDATE", "candidates", 1, "Expected a list of candidate records")
    if len(items) > MAX_CANDIDATES:
        raise ArtifactInputError("CANDIDATE_LIMIT_EXCEEDED", "candidates", 1, "At most 10,000 candidates may be scored")
    for item in items:
        _validate(item)


def _score_validated(items: list[dict]) -> list[dict]:
    scored = []
    for item in items:
        explicit = _LABEL.match(item["text"]) is not None
        long_enough = len(item["text"].strip()) >= 16
        uncertainty = {"observed": 20, "inferred": 10, "uncertain": 0}[item["nature"]]
        factors = [
            {"factor": "evidence", "value": 30,
             "reason": "The complete normalized source unit and classification agree; supplied provenance/context is not authenticated."},
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


def score_candidates(items: list[dict]) -> list[dict]:
    """Validate the whole list before scores; no envelope total/order is invented."""
    _validate_items(items)
    return _score_validated(items)


def _location_error(item: dict, message: str) -> None:
    raise ArtifactInputError("INVALID_CANDIDATE_LOCATION", item["source"]["path"], 1, message)


def _docx_envelope_locations(items: list[dict], unit_count: int) -> None:
    blocks = {}
    widths = {}
    by_block = {}
    for item in items:
        loc = item["location"]
        table = loc.get("table")
        block = loc["block"]
        if block in blocks and blocks[block] != table:
            _location_error(item, "One body block cannot be both a paragraph and a table")
        blocks[block] = table
        by_block.setdefault(block, []).append(item)
        if table is not None:
            widths[table] = max(widths.get(table, 0), loc["cell"])
    last_number = last_block = known_plain = 0
    for block, table in sorted(blocks.items()):
        if table is None:
            known_plain += 1
        else:
            if not last_number < table <= last_number + block - last_block - known_plain:
                _location_error(items[0], "Table indexes contradict the known body blocks")
            last_number, last_block, known_plain = table, block, 0
    previous = None
    table_previous = {}
    for item in items:
        loc = item["location"]
        if previous is not None:
            block_delta = loc["block"] - previous["block"]
            paragraph_delta = loc["paragraph"] - previous["paragraph"]
            if block_delta < 0 or paragraph_delta <= 0 or paragraph_delta < block_delta:
                _location_error(item, "DOCX paragraphs/body blocks must follow source order")
            if block_delta == 0 and ("table" not in loc or "table" not in previous):
                _location_error(item, "A plain body paragraph has only one candidate unit")
        if "table" in loc:
            width = widths[loc["table"]]
            minimum = (loc["block"] - 1 + (loc["row"] - 1) * width
                       + loc["cell"] - 1 + loc["cell_paragraph"])
            if loc["paragraph"] < minimum:
                _location_error(item, "Paragraph offset cannot contain the known preceding rows/cells")
            prior = table_previous.get(loc["table"])
            if prior is not None:
                here_cell = (loc["row"], loc["cell"])
                prior_cell = (prior["row"], prior["cell"])
                delta = loc["paragraph"] - prior["paragraph"]
                if here_cell == prior_cell:
                    if delta != loc["cell_paragraph"] - prior["cell_paragraph"]:
                        _location_error(item, "Same-cell local/global paragraph offsets disagree")
                elif here_cell < prior_cell:
                    _location_error(item, "Table rows/cells must follow source order")
                else:
                    between = (loc["cell"] - prior["cell"] - 1 if loc["row"] == prior["row"]
                               else width - prior["cell"] + (loc["row"] - prior["row"] - 1) * width
                               + loc["cell"] - 1)
                    if delta < between + loc["cell_paragraph"]:
                        _location_error(item, "Not enough paragraphs for intervening rows/cells")
            table_previous[loc["table"]] = loc
        previous = loc
    previous_block = previous_end = 0
    for block, table in sorted(blocks.items()):
        minimum_start = previous_end + block - previous_block - 1
        start = None
        end = 0
        for item in by_block[block]:
            loc = item["location"]
            if table is None:
                anchor, within, tail = loc["paragraph"] - 1, 1, 0
            else:
                within = (loc["row"] - 1) * widths[table] + loc["cell"] - 1 + loc["cell_paragraph"]
                tail = widths[table] - loc["cell"]
                anchor = loc["paragraph"] - loc["cell_paragraph"] if loc["row"] == loc["cell"] == 1 else None
            if loc["paragraph"] < minimum_start + within:
                _location_error(item, "Paragraphs cannot fit between the known body blocks")
            if anchor is not None:
                if start is not None and start != anchor:
                    _location_error(item, "Known paragraph anchors disagree within a body block")
                start = anchor
            end = max(end, loc["paragraph"] + tail)
        if end > unit_count:
            _location_error(by_block[block][-1], "Known table width requires paragraph units beyond unit_count")
        if start is not None:
            if (start < minimum_start
                    or block == previous_block + 1
                    and (previous_block == 0 or blocks[previous_block] is None) and start != previous_end):
                _location_error(by_block[block][0], "Known adjacent block anchors cannot hide extra paragraphs")
        previous_block, previous_end = block, end


def _envelope_locations(payload: dict) -> None:
    items = payload["candidates"]
    kind = payload["source"]["kind"]
    units = payload["unit_count"]
    if kind != "docx" and units > payload["source"]["byte_count"]:
        raise ArtifactInputError("INVALID_CANDIDATE", "candidates", 1, "Physical lines cannot exceed supplied text bytes")
    previous = None
    for ordinal, item in enumerate(items, 1):
        loc = item["location"]
        position = loc["paragraph"] if kind == "docx" else loc["line"]
        if position > units:
            _location_error(item, "Candidate source position exceeds the envelope unit_count")
        if kind == "transcript" and loc["turn"] != ordinal:
            _location_error(item, "A complete transcript envelope has consecutive turns starting at one")
        if kind != "docx":
            if previous is not None:
                delta = loc["line"] - previous["line"]
                if delta <= 0:
                    _location_error(item, "Envelope source lines must be unique and increasing")
                if kind == "text" and loc["paragraph"] != previous["paragraph"] + (delta > 1):
                    _location_error(item, "Plain-text groups must agree with contiguous lines or blank gaps")
                if kind == "markdown":
                    groups = loc["paragraph"] - previous["paragraph"]
                    if groups < 0 or 2 * groups > delta:
                        _location_error(item, "Markdown raw groups cannot move backwards or omit required blank separators")
            elif kind == "text" and loc["paragraph"] != 1:
                _location_error(item, "The first nonempty plain-text group must be one")
        previous = loc
    if kind == "docx":
        _docx_envelope_locations(items, units)


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
            or payload["candidate_count"] > payload["unit_count"]
            or payload["status"] != ("extracted" if payload["candidates"] else "empty")):
        raise ArtifactInputError("INVALID_CANDIDATE", "candidates", 1, "Extraction status/counts are inconsistent")
    items = payload["candidates"]
    _validate_items(items)
    if any(item["source"] != payload["source"] for item in items):
        raise ArtifactInputError("INVALID_SOURCE_IDENTITY", "candidates", 1, "Envelope and candidate source identities differ")
    _envelope_locations(payload)
    return {**payload, "candidates": _score_validated(items)}


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
