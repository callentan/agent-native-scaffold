"""Source-verified deterministic local graph exports. No renderer installation or execution."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import hashlib
import html
import json
from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET

from artifact_io import ArtifactInputError, iter_markdown_lines, load_yaml_mapping
from check_artifacts import (
    _decode, _HEADING, _local_root, _output_path, _write_new, read_inventory,
)
from export_model import _derive, _model_path, _SCOPE, _Sources, check_model


_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", _NS)
_MIME = {"json": "application/json", "svg": "image/svg+xml", "html": "text/html"}
_DRIFT = {"STALE_MODEL_SOURCE", "MODEL_MISMATCH"}
_NOTICE = "Derived source documentation; not execution, approval, risk acceptance or release."
_STYLE = """
:root{color-scheme:light;background:#f5f5f5;color:#2d3142}
body{margin:32px auto;padding:0 24px;max-width:1400px;font:16px/1.6 Arial,sans-serif}
h1,h2{font-family:Georgia,serif;line-height:1.25}h1{font-size:32px}h2{font-size:25px}
h3{font-size:19px}a{color:#2e5aa8}pre,code,.technical{font-family:monospace}
pre{white-space:pre-wrap;overflow-wrap:anywhere}svg{max-width:100%;height:auto}
.figure{overflow-x:auto}.figure>svg{min-width:760px}
article,.view,.slide{border-top:1px solid #bfc0c0;padding:20px 0}
.provenance,.gap{overflow-wrap:anywhere;color:#4f5d75}.provenance{font:13px/1.7 monospace}
.slide{min-height:360px;break-after:page}.slide h2{font-size:30px}
@media print{body{margin:0;max-width:none}.figure>svg{min-width:0}.slide{min-height:0}}
""".strip()


def _text(value) -> str:
    value = str(value)
    if any(not (character in "\t\n\r" or "\x20" <= character <= "\ud7ff"
                or "\ue000" <= character <= "\ufffd" or "\U00010000" <= character <= "\U0010ffff")
           for character in value):
        raise ArtifactInputError("INVALID_RENDER_TEXT", "source text", 1, "Text contains characters not representable in XML")
    return value


def _escape(value) -> str:
    return html.escape(_text(value), quote=True)


def _identity(value: str, prefix: str = "source") -> str:
    return prefix + "-" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _json(data) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _format(value, supported) -> str:
    if not isinstance(value, str) or value not in (*supported, "pdf", "pptx"):
        raise ArtifactInputError("UNSUPPORTED_FORMAT", "format", 1, "Select an advertised local format or a separately gated PDF/PPTX request")
    return value


def _load(inputs, *, trace: bool = False) -> dict:
    allowed = {"root", "scope", "model_path"} | ({"format"} if trace else {"sources"})
    required = {"root", "scope"} | (set() if trace else {"sources"})
    if not isinstance(inputs, Mapping) or not required <= inputs.keys() or set(inputs) - allowed:
        raise ArtifactInputError("INVALID_RENDER_INPUT", "render inputs", 1, "Supply only the documented explicit root/scope/source selection fields")
    if not isinstance(inputs["scope"], str) or not _SCOPE.fullmatch(inputs["scope"]):
        raise ArtifactInputError("INVALID_SCOPE", "scope", 1, "Select an explicit project/context")
    root = _local_root(inputs["root"])
    inventory = read_inventory(root)
    if inventory.report.status in ("invalid", "input-error"):
        finding = inventory.report.findings[0]
        raise ArtifactInputError(finding.code, finding.path, finding.line, finding.message)
    empty = trace and not inventory.artifacts and inputs.get("model_path") is None
    if empty:
        reader = _Sources(inventory)
        reader.manifest()  # An invalid supplied manifest is never disguised as empty.
        model = None
        source = {"root": ".", "baseline": "sha256:" + inventory.report.baseline.snapshot_sha256}
    else:
        model, _, reader = _derive(inventory, inputs["scope"])
        source = model["source"]
    extra_raw = {}
    if inputs.get("model_path") is not None:
        report = check_model(root, inputs["scope"], inputs["model_path"])
        if report.status in ("invalid", "input-error"):
            finding = report.findings[0]
            raise ArtifactInputError(finding.code, finding.path, finding.line, finding.message)
        path = _model_path(root, inputs["model_path"])
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise ArtifactInputError("FILE_READ_ERROR", path, 1, str(error)) from error
        data, _ = load_yaml_mapping(_decode(raw, path), path)
        if data != model:
            code = "STALE_MODEL_SOURCE" if data.get("source") != source else "MODEL_MISMATCH"
            raise ArtifactInputError(code, path, 1, "Persisted model changed or differs from this source acquisition")
        extra_raw[path] = raw
        reader.reserved_paths.add(path)
    sources = inputs.get("sources", [])
    if not isinstance(sources, list):
        raise ArtifactInputError("INVALID_RENDER_INPUT", root, 1, "sources must be an explicit list, including [] for no content selection")
    seen = set()
    for pointer in sources:
        if not isinstance(pointer, Mapping) or set(pointer) != {"reference", "baseline"}:
            raise ArtifactInputError("INVALID_EVIDENCE", root, 1, "Each selection needs reference and fixed baseline")
        if not isinstance(pointer["reference"], str) or not isinstance(pointer["baseline"], str):
            raise ArtifactInputError("INVALID_EVIDENCE", root, 1, "Source reference/baseline must be strings")
        key = (pointer["reference"], pointer["baseline"])
        if key in seen:
            raise ArtifactInputError("DUPLICATE_EVIDENCE", root, 1, "Do not select the same source fragment twice")
        seen.add(key)
        reader.reserve(pointer["reference"].split("#", 1)[0])
    return {"root": root, "scope": inputs["scope"], "reader": reader, "model": model,
            "source": source, "sources": sources, "extra_raw": extra_raw, "empty": empty}


def _result(context, format, content, *, status="rendered", counts=None, gaps=(), gates=()) -> dict:
    return {
        "status": status, "format": format, "media_type": _MIME.get(format), "content": content,
        "counts": {**dict.fromkeys(("nodes", "edges", "sections", "diagrams", "messages", "slides"), 0),
                   **(counts or {})},
        "source": dict(context["source"]), "gaps": sorted(set(gaps)), "gates": list(gates),
    }


def _unavailable(context, format) -> dict:
    reasons = {
        "authorization": "No renderer/version/template/input-processing selection has been separately approved.",
        "dependency": "No approved PDF/PPTX package, SDK, service or container is selected or installed by this tool.",
        "signature-parser": "Actual binary signature and format parser checks have not run.",
        "nonzero-count": "Actual nonzero page/slide count has not been measured.",
        "source-content": "Binary source-content completeness has not been checked.",
        "human-app": "Human/native application content and readability checks have not run.",
    }
    return _result(context, format, None, status="unavailable",
                   gaps=[format + ": no approved renderer; select/authorize and lock one before real format checks"],
                   gates=[{"name": name, "status": "not-run", "reason": reason} for name, reason in reasons.items()])


def _title(artifact) -> str:
    for _, line in iter_markdown_lines(artifact.body, artifact.body_start_line):
        match = _HEADING.fullmatch(line) if line is not None else None
        if match and len(match[1]) == 1:
            return match[2] or artifact.id
    return artifact.id


def _graph(context) -> dict:
    reader = context["reader"]
    owners = reader.owners
    pending = sorted(key for key, artifact in owners.items() if artifact.scope == context["scope"])
    selected = set()
    edges = []
    while pending:
        key = pending.pop()
        if key in selected:
            continue
        selected.add(key)
        artifact = owners[key]
        locations = dict(artifact.metadata_locations)
        for index, reference in enumerate(artifact.upstream):
            target = reference.split("#", 1)[0]
            edges.append({"source": key, "target": target, "sourceRef": key, "targetRef": reference,
                          "relation": "upstream", "path": artifact.relative_path,
                          "line": locations[("upstream", index)].line})
            pending.append(target)
        for target in artifact.targets:
            target_key = target.target.split("#", 1)[0]
            edges.append({"source": key, "target": target_key, "sourceRef": key + "#" + target.criterion_anchor,
                          "targetRef": target.target, "relation": "targets", "path": artifact.relative_path,
                          "line": target.location.line, "criterionAnchor": target.criterion_anchor,
                          **({"testId": target.test_id} if target.test_id is not None else {})})
            pending.append(target_key)
    nodes = [{
        "key": key, "kind": owners[key].kind, "title": _title(owners[key]),
        "path": owners[key].relative_path, "baseline": "sha256:" + hashlib.sha256(reader.raw[owners[key].path]).hexdigest(),
        "line": owners[key].id_location.line,
        "anchors": [{"reference": key + "#" + anchor.name, "line": anchor.location.line} for anchor in owners[key].anchors],
    } for key in sorted(selected)]
    views = context["model"]["views"] if context["model"] is not None else {}
    gaps = [gap for view in views.values() for gap in view["gaps"]]
    if not nodes:
        gaps.append("empty formal inventory; requested scope existence and business results are not asserted")
    return {"status": "empty" if not nodes else "partial" if gaps else "rendered",
            "scope": context["scope"], "source": context["source"], "nodes": nodes,
            "edges": sorted(edges, key=lambda edge: (edge["sourceRef"], edge["targetRef"], edge["relation"],
                                                    edge["path"], edge["line"], edge.get("testId", ""))),
            "views": views, "gaps": sorted(set(gaps))}


def _element(parent, tag, text=None, **attributes):
    node = ET.SubElement(parent, "{" + _NS + "}" + tag,
                         {name.replace("_", "-"): _text(value) for name, value in attributes.items()})
    if text is not None:
        node.text = _text(text)
    return node


def _svg_root(slug, title, description, width, height):
    root = ET.Element("{" + _NS + "}svg", {
        "viewBox": f"0 0 {width} {height}", "role": "img",
        "aria-labelledby": slug + "-title " + slug + "-desc",
        "font-family": "Arial, sans-serif", "fill": "#2d3142",
    })
    _element(root, "title", title, id=slug + "-title")
    _element(root, "desc", description, id=slug + "-desc")
    definitions = _element(root, "defs")
    marker = _element(definitions, "marker", id=slug + "-arrow", markerWidth=8, markerHeight=8,
                      refX=7, refY=4, orient="auto")
    _element(marker, "path", d="M0 0 L8 4 L0 8 Z", fill="#4f5d75")
    _element(root, "rect", x=0, y=0, width=width, height=height, fill="#f5f5f5")
    return root


def _wrap(value, width=100):
    """Preserve every character while splitting for offline SVG layout."""
    result = []
    for paragraph in _text(value).split("\n"):
        line, used = "", 0
        for character in paragraph:
            amount = (0 if unicodedata.combining(character) else
                      2 if unicodedata.east_asian_width(character) in ("W", "F") else 1)
            if used + amount > width and line:
                result.append(line)
                line, used = "", 0
            line += character
            used += amount
        result.append(line)
    return result


def _svg_lines(parent, lines, x, y, *, size=15, step=22, **attributes):
    for line in lines:
        _element(parent, "text", line, x=x, y=y, font_size=size, **attributes)
        y += step
    return y


def _svg_string(root):
    return ET.tostring(root, encoding="unicode") + "\n"


def _html(title, body):
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
            'style-src \'unsafe-inline\'; font-src \'none\'; img-src \'none\'; base-uri \'none\'; form-action \'none\'">\n'
            f'<title>{_escape(title)}</title><style>{_STYLE}</style></head><body>\n'
            f'<header><h1>{_escape(title)}</h1><p>{_escape(_NOTICE)}</p></header>\n'
            + body + f'\n<footer><p>{_escape(_NOTICE)}</p></footer></body></html>\n')


def _graph_svg(data):
    slug = _identity(data["scope"], "trace")
    nodes, edges = data["nodes"], data["edges"]
    boxes, ports = {}, {}
    y = 120
    for node in nodes:
        key = node["key"]
        lines = [part for text in (key, node["title"], f'{node["path"]}:{node["line"]}', node["baseline"])
                 for part in _wrap(text, 76)]
        incidents = [(index, side) for index, edge in enumerate(edges)
                     for side in ("source", "target") if edge[side] == key]
        height = max(48 + 20 * len(lines), 32 + 16 * len(incidents))
        height = (height + 3) // 4 * 4
        boxes[key] = (y, height, lines)
        for rank, incident in enumerate(incidents, 1):
            ports[incident] = y + height * rank / (len(incidents) + 1)
        y += height + 32
    appendix = [_NOTICE, "Dependency direction: declaring owner -> upstream basis; criterion -> target."]
    if not nodes:
        appendix.append("empty: no formal nodes or declared relationships")
    for index, edge in enumerate(edges, 1):
        appendix.extend(_wrap(f'E{index} {edge["relation"]}: {edge["sourceRef"]} -> {edge["targetRef"]}'))
        appendix.extend(_wrap(f'{edge["path"]}:{edge["line"]}'))
    appendix.extend(part for gap in data["gaps"] for part in _wrap("gap: " + gap))
    width = max(1120, 848 + len(edges) * 28)
    root = _svg_root(slug, "Source traceability", "Actual owner relationships, isolated owners, source baselines and gaps.",
                     width, y + len(appendix) * 22 + 100)
    _svg_lines(root, ["Source traceability — " + data["status"], data["scope"], data["source"]["baseline"]],
               32, 32, size=15)
    right = 784
    routes = [(848 + index * 28, ports[(index, "source")], ports[(index, "target")])
              for index in range(len(edges))]

    def horizontal(start, end, level, current):
        # Give every real orthogonal crossing its own visible 8px bridge.
        # Keep source/target ports distinct; never merge declarations into a line.
        crossings = [lane for index, (lane, first, last) in enumerate(routes)
                     if index != current and min(start, end) + 8 < lane < max(start, end) - 8
                     and min(first, last) + 8 < level < max(first, last) - 8]
        command = ""
        direction = 1 if end > start else -1
        for lane in sorted(crossings, reverse=direction < 0):
            before, after = lane - direction * 8, lane + direction * 8
            command += (f" H{before} Q{before} {level - 8} {lane} {level - 8}"
                        f" Q{after} {level - 8} {after} {level}")
        return command + f" H{end}"

    for index, edge in enumerate(edges):
        lane, source_y, target_y = routes[index]
        direction = 1 if target_y > source_y else -1
        d = (f"M{right} {source_y}" + horizontal(right, lane - 8, source_y, index)
             + f" Q{lane} {source_y} {lane} {source_y + direction * 8} "
             + f"V{target_y - direction * 8} Q{lane} {target_y} {lane - 8} {target_y}"
             + horizontal(lane - 8, right, target_y, index))
        path = _element(root, "path", d=d, fill="none", stroke="#4f5d75", stroke_width=1.5,
                        marker_end=f"url(#{slug}-arrow)", data_edge=index,
                        data_source_ref=edge["sourceRef"], data_target_ref=edge["targetRef"])
        _element(path, "title", f'E{index + 1} {edge["relation"]}: {edge["sourceRef"]} -> {edge["targetRef"]}')
    for node in nodes:
        top, height, lines = boxes[node["key"]]
        group = _element(root, "g", data_node=node["key"], id=_identity(node["key"], "node"))
        _element(group, "rect", x=32, y=top, width=752, height=height, rx=6,
                 fill="#ffffff", stroke="#4f5d75")
        _svg_lines(group, lines, 48, top + 28, size=14, step=20)
    _svg_lines(root, appendix, 32, y + 24)
    return root


def render_traceability(view) -> dict:
    """Render explicit local sources; view is the selector documented in document-exports."""
    if not isinstance(view, Mapping):
        raise ArtifactInputError("INVALID_RENDER_INPUT", "render inputs", 1, "Supply an explicit root/scope selector mapping")
    format = _format(view.get("format", "json"), ("json", "svg", "html"))
    context = _load(view, trace=True)
    if format in ("pdf", "pptx"):
        return _unavailable(context, format)
    data = _graph(context)
    if format == "json":
        content = _json(data)
    else:
        svg = _svg_string(_graph_svg(data))
        content = (svg if format == "svg" else _html(
            "Source traceability", '<p class="provenance">' + _escape(data["source"]["baseline"])
            + '</p><div class="figure">' + svg + "</div>"))
    return _result(context, format, content, status=data["status"],
                   counts={"nodes": len(data["nodes"]), "edges": len(data["edges"])}, gaps=data["gaps"])


def write_export(result, value: str, inputs) -> Path:
    """Explicit CLI write boundary; reserve every read or declared source location."""
    context = _load(inputs, trace="sources" not in inputs)
    reader = context["reader"]
    for pointer in context["sources"]:
        reader.evidence(dict(pointer))
    if result["status"] in ("unavailable", "unsupported") or result["content"] is None:
        raise ArtifactInputError("UNSUPPORTED_FORMAT", "output", 1, "Unavailable or unsupported output cannot be written")
    format = _format(result["format"], ("json", "svg", "html"))
    if reader.reservation_errors:
        raise ArtifactInputError("REPORT_CONFLICT", "output", 1, "Malformed declared source locations prevent safe output isolation")
    protected = set(reader.raw) | reader.reserved_paths | reader.reserved_directories | set(context["extra_raw"])
    path = _output_path(value, context["root"], ("." + format,), protected=protected)
    _write_new(path, result["content"])
    return path


def _run_cli(kind, render) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--format", default="json" if kind == "traceability" else "html")
    parser.add_argument("--model-path")
    parser.add_argument("--output")
    if kind != "traceability":
        parser.add_argument("--source", action="append", default=[])
        parser.add_argument("--baseline", action="append", default=[])
    args = parser.parse_args()
    inputs = {"root": args.root, "scope": args.scope}
    if args.model_path is not None:
        inputs["model_path"] = args.model_path
    try:
        if kind == "traceability":
            result = render({**inputs, "format": args.format})
        else:
            if len(args.source) != len(args.baseline):
                raise ArtifactInputError("INVALID_RENDER_INPUT", args.root, 1, "Each --source needs its corresponding --baseline")
            inputs["sources"] = [{"reference": ref, "baseline": base} for ref, base in zip(args.source, args.baseline)]
            result = render(inputs, args.format)
        if result["status"] in ("unavailable", "unsupported"):
            print(_json({**result, "content": None}), end="")
            return 2 if result["status"] == "unavailable" else 1
        if args.output is not None:
            write_export(result, args.output, inputs)
        sys.stdout.write(result["content"])
        return 0
    except ArtifactInputError as error:
        print(_json({"status": "drift" if error.code in _DRIFT else "input-error", "findings": [{
            "code": error.code, "path": str(error.path), "line": error.line, "message": error.message,
        }]}), end="")
        return 1 if error.code in _DRIFT else 2


def main() -> int:
    return _run_cli("traceability", render_traceability)


if __name__ == "__main__":
    raise SystemExit(main())
