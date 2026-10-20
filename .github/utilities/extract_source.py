"""Extract local source-located candidates, never confirmed domain artifacts."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import xml.etree.ElementTree as ET
import zipfile
import zlib

from artifact_io import ArtifactInputError, PathInput, _resolve_file, iter_markdown_source_lines
from check_artifacts import _checked_location, _local_root, _output_path, _write_new


SOURCE_KINDS = {"markdown": (".md",), "text": (".txt",), "transcript": (".txt",),
                "docx": (".docx",)}
CANDIDATE_KINDS = frozenset(("rule", "capability", "use-case", "term", "statement"))
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_SOURCE_UNITS = 10_000
MAX_DOCX_MEMBERS = 64
MAX_DOCX_PART_BYTES = 1024 * 1024
MAX_DOCX_TOTAL_BYTES = 8 * 1024 * 1024
MAX_DOCX_RATIO = 100
MAX_XML_DEPTH = 32
MAX_XML_NODES = 10_000
TIMESTAMP = re.compile(r"[0-9]{2}:[0-5][0-9]:[0-5][0-9]\.[0-9]{3}")
_LABEL = re.compile(r"^(rule|capability|use[ -]case|term|规则|能力|用例|术语)\s*[:：]", re.I)
_LABEL_KINDS = {"rule": "rule", "规则": "rule", "capability": "capability", "能力": "capability",
                "use case": "use-case", "use-case": "use-case", "用例": "use-case",
                "term": "term", "术语": "term"}
_UNCERTAIN = re.compile(r"\b(maybe|should|proposed|perhaps|unconfirmed)\b|待确认|可能|建议", re.I)
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
_OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
_MAIN_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
_PARTS = frozenset(("[Content_Types].xml", "_rels/.rels", "word/document.xml"))
_CLARIFICATION = (
    "Confirm the scope and reconcile contrary sources with the actual owner; "
    "this candidate records no acceptance."
)


def _valid_text(value) -> bool:
    return (isinstance(value, str) and bool(value.strip())
            and not any((ord(c) < 32 and c not in "\t\r\n")
                        or 0xD800 <= ord(c) <= 0xDFFF for c in value))


def _local_path(value: PathInput, *, root: PathInput | None = None) -> Path:
    """Select one ordinary local file; reject aliases before their resolution."""
    try:
        text = os.fspath(value)
        if (not _valid_text(text) or any(ord(c) < 32 for c in text)
                or text.startswith(("//", "\\\\")) or "://" in text):
            raise ArtifactInputError("INVALID_PATH", "source", 1, "Select an explicit local file")
        requested = Path(text)
        if ":" in requested.as_posix()[len(requested.anchor):]:
            raise ArtifactInputError("INVALID_PATH", "source", 1, "Alternate streams/device paths are not local source files")
        if requested.anchor and not requested.is_absolute() or root is None and not requested.is_absolute():
            raise ArtifactInputError("INVALID_PATH", text, 1, "API paths must be absolute; CLI paths use --root")
        parent = _local_root(_checked_location(root)) if root is not None else None
        selected = parent / requested if parent is not None else requested
        if parent is not None and not Path(os.path.abspath(selected)).is_relative_to(parent):
            raise ArtifactInputError("OUTSIDE_ROOT", text, 1, "Selected file is outside --root")
        try:
            actual = _checked_location(selected)
        except ArtifactInputError as error:
            if isinstance(error.__cause__, FileNotFoundError):
                raise ArtifactInputError("FILE_NOT_FOUND", selected, 1, "Selected file does not exist") from error
            raise ArtifactInputError("INVALID_PATH", selected, 1, "Unsafe or unreadable local path") from error
        return _resolve_file(actual, parent if parent is not None else actual.parent)
    except (OSError, TypeError, ValueError) as error:
        if isinstance(error, ArtifactInputError):
            raise
        raise ArtifactInputError("INVALID_PATH", "source", 1, "Invalid local file path") from error


def _read_bytes(path: Path) -> bytes:
    try:
        with path.open("rb") as source:
            raw = source.read(MAX_SOURCE_BYTES + 1)
    except OSError as error:
        raise ArtifactInputError("FILE_READ_ERROR", path, 1, "Cannot read the selected file") from error
    if len(raw) > MAX_SOURCE_BYTES:
        raise ArtifactInputError("SOURCE_LIMIT_EXCEEDED", path, 1, "Source exceeds 4 MiB")
    return raw


def _decode(raw: bytes, path: Path) -> str:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as error:
        raise ArtifactInputError("INVALID_ENCODING", path, 1, "Expected UTF-8, with optional BOM") from error
    if any(ord(c) < 32 and c not in "\t\r\n" for c in text):
        raise ArtifactInputError("INVALID_SOURCE_FORMAT", path, 1, "Control/binary content is not supported text")
    return text


def _json_value(text: str, path: Path, code: str, line: int = 1):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("Nonfinite JSON number")

    try:
        return json.loads(text, object_pairs_hook=unique, parse_constant=invalid_constant)
    except (ValueError, RecursionError) as error:
        raise ArtifactInputError(code, path, line, "Expected unambiguous finite JSON") from error


def _transcript_turn(fragment: str, path: Path, line: int) -> dict:
    turn = _json_value(fragment, path, "INVALID_TRANSCRIPT", line)
    if (not isinstance(turn, dict) or set(turn) != {"speaker", "timestamp", "text"}
            or any(not _valid_text(turn[k]) for k in turn)
            or TIMESTAMP.fullmatch(turn["timestamp"]) is None):
        raise ArtifactInputError(
            "INVALID_TRANSCRIPT", path, line,
            "Each nonblank JSON line requires speaker, HH:MM:SS.mmm timestamp and nonempty text only",
        )
    return turn


def _classify(text: str) -> tuple[str, str, list[str], str]:
    label = _LABEL.match(text)
    if label:
        kind = _LABEL_KINDS[label.group(1).lower()]
        nature = "observed"
        reason = "Explicit source label; the classification records a statement, not business confirmation."
    else:
        kind = ("rule" if re.search(r"(?<![\w-])(must|shall|never|required|cannot)(?![\w-])|必须|不得|禁止", text, re.I)
                else "capability" if re.search(r"\b(can|allows|supports)\b|能够|支持", text, re.I)
                else "statement")
        nature = "inferred"
        reason = "Unlabelled text: lexical candidate classification is an inference, not a domain decision."
    uncertainty = ["proposal language: " + match.group(0).lower() for match in _UNCERTAIN.finditer(text)]
    if uncertainty:
        nature = "uncertain"
    return kind, nature, uncertainty, reason


def _markdown_text(visible: str | None) -> str | None:
    """Select a complete visible line, not an arbitrary excerpt within it."""
    if visible is None or not visible.strip() or re.match(r" {0,3}#{1,6}(?:\s|$)", visible):
        return None
    return visible.strip()


def _text_units(text: str, kind: str, path: Path) -> tuple[int, list[tuple[str, str, dict, dict | None]]]:
    lines = text.splitlines()
    if len(lines) > MAX_SOURCE_UNITS:
        raise ArtifactInputError("SOURCE_LIMIT_EXCEEDED", path, 1, "Text/transcript exceeds 10,000 physical lines")
    units = []
    if kind == "transcript":
        turn_number = 0
        for number, raw in enumerate(lines, 1):
            if not raw.strip():
                continue
            turn = _transcript_turn(raw, path, number)
            turn_number += 1
            units.append((turn["text"].strip(), raw, {
                "line": number, "turn": turn_number, "speaker": turn["speaker"],
                "timestamp": turn["timestamp"],
            }, None))
    else:
        visible = {n: (line, before) for n, line, before in iter_markdown_source_lines(text)} if kind == "markdown" else None
        paragraph = 0
        in_paragraph = False
        for number, raw in enumerate(lines, 1):
            if not raw.strip():
                in_paragraph = False
                continue
            if not in_paragraph:
                paragraph += 1
                in_paragraph = True
            context = None
            if visible is not None:
                line, before = visible[number]
                content = _markdown_text(line)
                context = {"in_comment": before}
            else:
                content = raw.strip()
            if not content:
                continue
            units.append((content, raw, {"line": number, "paragraph": paragraph}, context))
    return len(lines), units


def _xml(raw: bytes, path: Path) -> ET.Element:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as error:
        raise ArtifactInputError("INVALID_DOCX_XML", path, 1, "Only UTF-8 OOXML parts are supported") from error
    if re.search(r"<!\s*(DOCTYPE|ENTITY)\b", text, re.I):
        raise ArtifactInputError("UNSAFE_DOCX", path, 1, "DTD/entity declarations are forbidden")
    declaration = re.search(r"<\?xml\s[^?]*encoding\s*=\s*['\"]([^'\"]+)", text, re.I)
    if declaration and declaration.group(1).lower() not in ("utf-8", "utf8"):
        raise ArtifactInputError("INVALID_DOCX_XML", path, 1, "OOXML encoding must be UTF-8")
    parser = ET.XMLPullParser(events=("start", "end"))
    root = None
    depth = nodes = 0
    try:
        for offset in range(0, len(text), 4096):
            parser.feed(text[offset:offset + 4096])
            for event, element in parser.read_events():
                if event == "start":
                    depth += 1
                    nodes += 1
                    if root is None:
                        root = element
                    if depth > MAX_XML_DEPTH or nodes > MAX_XML_NODES:
                        raise ArtifactInputError("SOURCE_LIMIT_EXCEEDED", path, 1, "OOXML depth/node bound exceeded")
                else:
                    depth -= 1
        parser.close()
    except ET.ParseError as error:
        raise ArtifactInputError("INVALID_DOCX_XML", path, 1, "Malformed OOXML part") from error
    if root is None:
        raise ArtifactInputError("INVALID_DOCX_XML", path, 1, "Empty XML is not an OOXML part")
    return root


def _unsupported(path: Path, detail: str) -> None:
    raise ArtifactInputError("UNSUPPORTED_DOCX", path, 1, detail)


def _package(parts: dict[str, bytes], path: Path) -> ET.Element:
    types = _xml(parts["[Content_Types].xml"], path)
    rels = _xml(parts["_rels/.rels"], path)
    document = _xml(parts["word/document.xml"], path)
    if types.tag != _CT + "Types" or rels.tag != _REL + "Relationships" or document.tag != _W + "document":
        raise ArtifactInputError("INVALID_DOCX", path, 1, "Expected OPC types/relationships and Word document roots")
    _plain_container(types, path)
    _plain_container(rels, path)
    seen = set()
    main = False
    for entry in types:
        if (list(entry) or entry.text and entry.text.strip()
                or entry.tag not in (_CT + "Default", _CT + "Override")):
            _unsupported(path, "Unsupported content-type declaration")
        if entry.tag == _CT + "Override":
            if set(entry.attrib) != {"PartName", "ContentType"}:
                _unsupported(path, "Unsupported content-type attributes")
            key = entry.get("PartName")
            if key != "/word/document.xml" or entry.get("ContentType") != _MAIN_TYPE:
                _unsupported(path, "Only a non-macro DOCX document main part is supported")
            main = True
        else:
            if set(entry.attrib) != {"Extension", "ContentType"}:
                _unsupported(path, "Unsupported content-type attributes")
            key = entry.get("Extension")
            expected = {"xml": "application/xml",
                        "rels": "application/vnd.openxmlformats-package.relationships+xml"}
            if key not in expected or entry.get("ContentType") != expected[key]:
                _unsupported(path, "Unsupported package default type")
        if key in seen:
            raise ArtifactInputError("INVALID_DOCX", path, 1, "Duplicate content type")
        seen.add(key)
    if not main:
        raise ArtifactInputError("INVALID_DOCX", path, 1, "Missing document content type")
    for relation in rels:
        if relation.get("TargetMode", "Internal") != "Internal":
            raise ArtifactInputError("UNSAFE_DOCX", path, 1, "External relationships are forbidden")
    if (len(rels) != 1 or rels[0].tag != _REL + "Relationship"
            or rels[0].get("Type") != _OFFICE_REL or rels[0].get("Target") != "word/document.xml"
            or not rels[0].get("Id") or list(rels[0])
            or rels[0].text and rels[0].text.strip()
            or set(rels[0].attrib) - {"Id", "Type", "Target", "TargetMode"}):
        _unsupported(path, "Only the fixed internal main-document relationship is supported; no relationship is followed")
    return document


def _container(raw: bytes, path: Path) -> ET.Element:
    if raw.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        raise ArtifactInputError("SOURCE_ADAPTER_UNAVAILABLE", path, 1, "Compound/encrypted Office containers are unavailable")
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_DOCX_MEMBERS:
                raise ArtifactInputError("SOURCE_LIMIT_EXCEEDED", path, 1, "DOCX exceeds 64 ZIP entries")
            seen = set()
            total = 0
            for entry in entries:
                name = entry.orig_filename
                segments = name.rstrip("/").split("/")
                mode = stat.S_IFMT(entry.external_attr >> 16)
                if (name != entry.filename or name.startswith(("/", "\\"))
                        or "\\" in name or ":" in name or "\x00" in name
                        or any(s in ("", ".", "..") for s in segments) or name in seen
                        or mode not in (0, stat.S_IFREG, stat.S_IFDIR)
                        or mode == stat.S_IFDIR and not entry.is_dir()
                        or mode == stat.S_IFREG and entry.is_dir()):
                    raise ArtifactInputError("UNSAFE_DOCX", path, 1, "Unsafe/duplicate/alias ZIP member")
                seen.add(name)
                if entry.flag_bits & 1:
                    raise ArtifactInputError("SOURCE_ENCRYPTED", path, 1, "Encrypted ZIP members are not supported")
                if entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    _unsupported(path, "Only stored/deflated DOCX members are supported")
                total += entry.file_size
                if (entry.file_size > MAX_DOCX_PART_BYTES or total > MAX_DOCX_TOTAL_BYTES
                        or entry.file_size > MAX_DOCX_RATIO * max(entry.compress_size, 1)):
                    raise ArtifactInputError("SOURCE_LIMIT_EXCEEDED", path, 1, "DOCX part/total/expansion bound exceeded")
            files = {entry.filename for entry in entries if not entry.is_dir()}
            if not _PARTS.issubset(files):
                raise ArtifactInputError("INVALID_DOCX", path, 1, "Missing required OPC/DOCX parts")
            if files != _PARTS or any(e.is_dir() and e.filename not in ("word/", "_rels/") for e in entries):
                _unsupported(path, "Additional parts (including headers, media, macros and relationships) are unsupported")
            parts = {}
            for entry in entries:
                with archive.open(entry) as source:
                    content = source.read(MAX_DOCX_PART_BYTES + 1)
                if len(content) != entry.file_size or len(content) > MAX_DOCX_PART_BYTES:
                    raise ArtifactInputError("INVALID_DOCX", path, 1, "ZIP member size is inconsistent")
                if entry.is_dir():
                    if content:
                        _unsupported(path, "Directory entries must be empty")
                else:
                    parts[entry.filename] = content
            return _package(parts, path)
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError, RuntimeError,
            NotImplementedError, ValueError, zlib.error) as error:
        if isinstance(error, ArtifactInputError):
            raise
        raise ArtifactInputError("INVALID_DOCX", path, 1, "Corrupt or unreadable DOCX ZIP container") from error


def _plain_container(element: ET.Element, path: Path) -> None:
    if element.attrib or element.text and element.text.strip():
        _unsupported(path, "Unsupported element attributes or non-run text")
    if any(child.tail and child.tail.strip() for child in element):
        _unsupported(path, "Unsupported text outside Word runs")


def _paragraph(element: ET.Element, path: Path) -> str:
    _plain_container(element, path)
    fragments = []
    for run in element:
        if run.tag != _W + "r":
            _unsupported(path, "Only plain runs are supported: no fields, revisions, links, drawings or styles")
        _plain_container(run, path)
        for leaf in run:
            if list(leaf):
                _unsupported(path, "Nested run content is unsupported")
            if leaf.tag == _W + "t":
                if (set(leaf.attrib) - {"{http://www.w3.org/XML/1998/namespace}space"}
                        or leaf.get("{http://www.w3.org/XML/1998/namespace}space", "default")
                        not in ("default", "preserve")):
                    _unsupported(path, "Unsupported text attributes")
                fragments.append(leaf.text or "")
            elif leaf.tag in (_W + "tab", _W + "br", _W + "cr") and not leaf.attrib and not leaf.text:
                fragments.append("\t" if leaf.tag == _W + "tab" else "\n")
            else:
                _unsupported(path, "Unsupported run content")
    return "".join(fragments)


def _docx_units(raw: bytes, path: Path) -> tuple[int, list[tuple[str, str, dict, dict | None]]]:
    document = _container(raw, path)
    _plain_container(document, path)
    if len(document) != 1 or document[0].tag != _W + "body":
        _unsupported(path, "Expected exactly one Word body")
    body = document[0]
    _plain_container(body, path)
    units = []
    paragraph = table = 0

    def append(element, location):
        nonlocal paragraph
        paragraph += 1
        fragment = _paragraph(element, path)
        if fragment.strip():
            units.append((fragment.strip(), fragment, {
                "part": "word/document.xml", **location, "paragraph": paragraph,
            }, None))

    for block, element in enumerate(body, 1):
        if element.tag == _W + "p":
            append(element, {"block": block})
        elif (element.tag == _W + "sectPr" and not list(element) and not element.attrib
              and not (element.text and element.text.strip())):
            if block != len(body):
                _unsupported(path, "Section properties must be last")
        elif element.tag == _W + "tbl":
            table += 1
            _plain_container(element, path)
            rows = []
            grid = None
            properties = False
            for child in element:
                if child.tag == _W + "tblPr" and not properties and not rows and grid is None:
                    _plain_container(child, path)
                    if list(child):
                        _unsupported(path, "Only empty table properties are supported")
                    properties = True
                elif child.tag == _W + "tblGrid" and grid is None and not rows:
                    _plain_container(child, path)
                    if any(c.tag != _W + "gridCol" or list(c) or c.text
                           or set(c.attrib) - {_W + "w"} for c in child):
                        _unsupported(path, "Unsupported table grid")
                    grid = len(child)
                elif child.tag == _W + "tr":
                    rows.append(child)
                else:
                    _unsupported(path, "Only simple tables are supported")
            if not rows:
                raise ArtifactInputError("INVALID_DOCX", path, 1, "A table must contain rows")
            width = grid if grid is not None else len(rows[0])
            for row_number, row in enumerate(rows, 1):
                _plain_container(row, path)
                if not len(row) or len(row) != width:
                    _unsupported(path, "Nonrectangular or merged tables are unsupported")
                for cell_number, cell in enumerate(row, 1):
                    if cell.tag != _W + "tc":
                        _unsupported(path, "Unsupported row content")
                    _plain_container(cell, path)
                    children = list(cell)
                    if children and children[0].tag == _W + "tcPr":
                        props = children.pop(0)
                        _plain_container(props, path)
                        if any(p.tag != _W + "tcW" or list(p) or p.text
                               or set(p.attrib) - {_W + "w", _W + "type"} for p in props):
                            _unsupported(path, "Merged/styled cells are unsupported")
                    if not children or any(p.tag != _W + "p" for p in children):
                        _unsupported(path, "Cells require plain paragraphs; nested tables are unsupported")
                    for cell_paragraph, p in enumerate(children, 1):
                        append(p, {"block": block, "table": table, "row": row_number,
                                   "cell": cell_number, "cell_paragraph": cell_paragraph})
        else:
            _unsupported(path, "Unsupported body layout; no partial extraction is returned")
    return paragraph, units


def extract_candidates(source: PathInput, kind: str) -> dict:
    """Return an identity/count envelope with a list of provisional candidates."""
    if not isinstance(kind, str) or kind not in SOURCE_KINDS:
        raise ArtifactInputError("SOURCE_ADAPTER_UNAVAILABLE", "source", 1,
                                 "Supported local selectors: markdown, text, transcript, docx")
    path = _local_path(source)
    if path.suffix.lower() not in SOURCE_KINDS[kind]:
        raise ArtifactInputError("INVALID_SOURCE_FORMAT", path, 1, "Extension does not match the explicit selector")
    raw = _read_bytes(path)
    identity = {"path": str(path), "kind": kind, "baseline": "sha256:" + hashlib.sha256(raw).hexdigest(),
                "byte_count": len(raw)}
    count, units = _docx_units(raw, path) if kind == "docx" else _text_units(_decode(raw, path), kind, path)
    candidates = []
    for text, fragment, location, context in units:
        candidate_kind, nature, uncertainty, reason = _classify(text)
        candidates.append({
            "candidate_id": f"candidate-{len(candidates) + 1:04d}",
            "kind": candidate_kind, "nature": nature, "text": text, "fragment": fragment,
            "source": dict(identity), "location": location, "uncertainty": uncertainty,
            "extraction_reason": reason, "clarification": _CLARIFICATION,
        })
        if context is not None:
            candidates[-1]["markdown_context"] = context
    return {"status": "extracted" if candidates else "empty", "source": identity,
            "unit_count": count, "candidate_count": len(candidates), "candidates": candidates}


def _write_output(payload, output: str, root: PathInput, protected=()) -> None:
    """Shared new-output rule, additionally confined to --root and away from its inputs."""
    actual_root = _local_root(_checked_location(root))
    path = _output_path(output, actual_root, (".json",), within=actual_root, protected=protected)
    _write_new(path, json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=2) + "\n")


def _print_error(error: ArtifactInputError) -> int:
    print(json.dumps({"status": "input-error", "error": {
        "code": error.code, "path": str(error.path), "line": error.line, "message": error.message,
    }}, ensure_ascii=True, indent=2))
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        source = _local_path(args.source, root=args.root)
        payload = extract_candidates(source, args.kind)
        if args.output is not None:
            _write_output(payload, args.output, args.root, (source,))
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except ArtifactInputError as error:
        return _print_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
