"""Source-owned SWAS/SEQ local HTML/SVG, preserving nine-view gaps and boundaries."""

from __future__ import annotations

import json
import re

from artifact_io import (
    ArtifactInputError, _ANCHOR, _markdown_tokens, section_fences,
)
from check_artifacts import _HEADING
from check_traceability import section_lines
from export_model import _SUMMARY
from render_traceability import (
    _element, _escape, _format, _html, _identity, _load, _NOTICE, _result,
    _run_cli, _svg_lines, _svg_root, _svg_string, _title, _unavailable, _wrap,
)


_IDENTIFIER = r"[A-Za-z_][A-Za-z0-9_]*"
_PARTICIPANT = re.compile(r"(participant|actor)[ \t]+(" + _IDENTIFIER + r")(?:[ \t]+as[ \t]+(.+))?")
_MESSAGE = re.compile(r"(" + _IDENTIFIER + r")[ \t]*(-->>|->>)[ \t]*(" + _IDENTIFIER + r")[ \t]*:[ \t]*(\S.*)")


def _sections(artifact, fragment=""):
    """Display source sections, not a second Markdown/identity parser."""
    if fragment:
        entry = next(anchor for anchor in artifact.anchors if anchor.name == fragment)
        lines = list(section_lines(artifact, fragment))
        heading = next(((number, _HEADING.fullmatch(line)) for number, line in lines if _HEADING.fullmatch(line)), None)
        if heading:
            lines = [(number, line) for number, line in lines if number != heading[0]]
        if not (artifact.kind == "sequence-diagram" and fragment == "diagram"):
            raw_lines = artifact.source.splitlines()
            for block in section_fences(artifact, fragment):
                lines.extend((number, raw_lines[number - 1]) for number in range(block.start_line, block.end_line + 1))
        return [{"key": fragment, "title": heading[1][2] if heading else fragment,
                 "line": entry.location.line, "lines": [line for _, line in sorted(lines)]}]
    sections = []
    current, waiting_heading = None, False
    raw_lines = artifact.source.splitlines()
    # The *same* Markdown state machine owns all prose/code/comment boundaries.
    # Literal tokens keep their actual position instead of being appended later.
    for number, kind, line in _markdown_tokens(artifact.body, artifact.body_start_line):
        if kind == "text":
            anchor = _ANCHOR.fullmatch(line)
            if anchor:
                current = {"key": anchor[2], "title": anchor[2], "line": number, "lines": []}
                sections.append(current)
                waiting_heading = True
                continue
            heading = _HEADING.fullmatch(line)
            if heading and len(heading[1]) == 1:
                continue
            if heading:
                if current is None or not waiting_heading:
                    current = {"key": "section-" + str(number), "line": number, "lines": []}
                    sections.append(current)
                current["title"] = heading[2] or ""
                waiting_heading = False
                continue
        else:
            line = raw_lines[number - 1]
        if line.strip() or current:
            if current is None:
                current = {"key": "body", "title": _title(artifact), "line": number, "lines": []}
                sections.append(current)
            if not (kind != "text" and artifact.kind == "sequence-diagram" and current["key"] == "diagram"):
                current["lines"].append(line)
            if line.strip():
                waiting_heading = False
    return sections


def _sequence(artifact, namespace):
    blocks = [block for block in section_fences(artifact, "diagram") if block.info.split()[:1] == ["mermaid"]]
    result = {"status": "unsupported", "participants": [], "events": [], "messages": 0,
              "gaps": [], "slug": _identity(namespace, "sequence"), "source": artifact.key}

    def unsupported(line, reason):
        result["gaps"] = [f"{artifact.relative_path}:{line}: unsupported SEQ: {reason}"]
        # Never draw a supported-looking prefix of an unsupported source diagram.
        result.update(participants=[], events=[], messages=0)
        return result

    if len(blocks) != 1:
        return unsupported(artifact.body_start_line, "expected one closed, source-owned Mermaid diagram fence")
    block = blocks[0]
    if block.info != "mermaid":
        return unsupported(block.start_line, "extra Mermaid fence options are outside the finite subset")
    statements = [(block.start_line + offset, line.strip()) for offset, line in enumerate(block.body.splitlines(), 1)
                  if line.strip()]
    if not statements or statements[0][1] != "sequenceDiagram":
        return unsupported(block.start_line + 1, "expected sequenceDiagram")
    participants, events, known = [], [], set()
    fragment, region_count = None, 0
    message_count = 0
    for number, line in statements[1:]:
        if line.startswith("%%") and not line.startswith("%%{"):
            continue
        match = _PARTICIPANT.fullmatch(line)
        if match:
            if message_count or match[2] in known or fragment is not None:
                return unsupported(number, "participants must be distinct declarations before messages/fragments")
            known.add(match[2])
            participants.append({"id": match[2], "label": match[3] or match[2], "kind": match[1], "line": number})
            continue
        match = _MESSAGE.fullmatch(line)
        if match:
            if match[1] not in known or match[3] not in known:
                return unsupported(number, "both participants must be explicitly declared")
            events.append({"kind": "message", "from": match[1], "to": match[3], "arrow": match[2],
                           "label": match[4], "index": message_count, "line": number})
            message_count += 1
            region_count += 1
            continue
        match = re.fullmatch(r"(alt|opt|loop)[ \t]+(\S.*)", line)
        if match:
            if fragment is not None:
                return unsupported(number, "nested combined fragments are outside the finite subset")
            fragment, region_count = match[1], 0
            events.append({"kind": "start", "operator": match[1], "label": match[2], "line": number})
        elif line.startswith("else "):
            if fragment != "alt" or not region_count or not line[5:].strip():
                return unsupported(number, "else needs an alt and a nonempty preceding message region")
            region_count = 0
            events.append({"kind": "else", "label": line[5:].strip(), "line": number})
        elif line == "end":
            if fragment is None or not region_count:
                return unsupported(number, "end needs a nonempty, open fragment")
            events.append({"kind": "end", "line": number})
            fragment = None
        else:
            return unsupported(number, "statement is outside the advertised participant/message/fragment subset")
    if fragment is not None or not message_count:
        return unsupported(block.end_line, "unclosed fragment or zero source messages")
    gaps = [f"{artifact.relative_path}: missing source context in {anchor}"
            for anchor in ("basis", "participants", "paths") if not section_lines(artifact, anchor)]
    result.update(status="partial" if gaps else "rendered", participants=participants,
                  events=events, messages=message_count, gaps=gaps)
    return result


def _source_sections(context, pointer):
    reader = context["reader"]
    reader.evidence(dict(pointer))
    relative, _, fragment = pointer["reference"].partition("#")
    path, raw = reader.read(relative)
    artifact = reader.artifacts.get(path)
    if artifact is not None:
        sections = _sections(artifact, fragment)
        for section in sections:
            section.update(source_id=artifact.key, source_title=_title(artifact),
                           path=relative, baseline=pointer["baseline"], reference=pointer["reference"],
                           identity=_identity(pointer["reference"] + "#" + section["key"], "section"),
                           sequence=None)
        if artifact.kind == "sequence-diagram":
            diagram = next((section for section in sections if section["key"] == "diagram"), None)
            if diagram is not None:
                diagram["sequence"] = _sequence(artifact, pointer["reference"])
            elif not fragment:
                # Missing diagram remains visible even if no H2 could be extracted.
                sections.append({
                    "key": "diagram", "title": "Missing source diagram", "line": artifact.body_start_line,
                    "lines": [], "source_id": artifact.key, "source_title": _title(artifact),
                    "path": relative, "baseline": pointer["baseline"], "reference": pointer["reference"],
                    "identity": _identity(pointer["reference"] + "#missing-diagram", "section"),
                    "sequence": _sequence(artifact, pointer["reference"]),
                })
        return sections
    if path.suffix.lower() not in (".yaml", ".yml", ".json"):
        raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", path, 1, "Select a formal Markdown artifact or verified view source")
    verified = {(entry["reference"], entry["baseline"])
                for view in context["model"]["views"].values() for entry in view["evidenceRefs"]}
    if (pointer["reference"], pointer["baseline"]) not in verified:
        raise ArtifactInputError(
            "INVALID_OPTIONAL_SOURCE", path, 1,
            "The exact structured source fragment and baseline must be selected by the verified nine-view model",
        )
    data = reader.document(path, raw)
    if "object" in data and "entries" in data:
        # Use the existing reconstruction adapter rather than making schema-valid result claims.
        from export_model import _implementation_source
        _implementation_source(reader, path, pointer["baseline"], data, context["scope"])
        selected = [("implementation report reference",
                     ["Owned VT execution/applicability stays with the original records.",
                      relative + " @ " + pointer["baseline"]])]
    else:
        names = [name for name in data if name in _SUMMARY.values() or name == "tree"]
        if fragment:
            names = [name for name in names if name == fragment]
        if not names:
            raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", path, 1, "No selected, supported source-owned summary field")
        selected = []
        for name in names:
            try:
                lines = json.dumps(data[name], ensure_ascii=False, sort_keys=True, indent=2).splitlines()
            except (TypeError, ValueError) as error:
                raise ArtifactInputError(
                    "INVALID_OPTIONAL_SOURCE", path, 1,
                    f"Selected structured view {name!r} contains YAML-native values unsupported by the JSON projection ({type(error).__name__})",
                ) from error
            selected.append((name, lines))
    return [{
        "key": name, "title": name, "line": 1, "lines": lines,
        "source_id": "file:" + relative, "source_title": relative,
        "path": relative, "baseline": pointer["baseline"], "reference": pointer["reference"],
        "identity": _identity(pointer["reference"] + "#" + name, "section"), "sequence": None,
    } for name, lines in selected]


def _architecture_data(context):
    sections = [section for pointer in context["sources"] for section in _source_sections(context, pointer)]
    views = context["model"]["views"]
    gaps = [gap for view in views.values() for gap in view["gaps"]]
    if not any(section["key"] == "deployment" and any(line.strip() for line in section["lines"]) for section in sections):
        gaps.append("deployment source is absent from the selected explicit deployment sections; topology is not inferred")
    if not sections:
        gaps.append("empty content selection; no source-defined document sections or slides")
    sequences = [section["sequence"] for section in sections if section["sequence"] is not None]
    for sequence in sequences:
        gaps.extend(sequence["gaps"])
    status = ("unsupported" if any(sequence["status"] == "unsupported" for sequence in sequences) else
              "empty" if not sections else "partial" if gaps else "rendered")
    return {"scope": context["scope"], "source": context["source"], "sections": sections, "views": views,
            "gaps": sorted(set(gaps)), "status": status, "sequences": sequences}


def _counts(data):
    return {"sections": len(data["sections"]), "diagrams": sum(s["status"] != "unsupported" for s in data["sequences"]),
            "messages": sum(s["messages"] for s in data["sequences"])}


def _view_lines(name, view):
    lines = [name + " — " + view["state"]]
    lines.extend("artifact: " + reference for reference in view["artifactRefs"])
    lines.extend("evidence: " + pointer["reference"] + " @ " + pointer["baseline"] for pointer in view["evidenceRefs"])
    lines.extend("gap: " + gap for gap in view["gaps"])
    return lines


def _views_html(data):
    result = ['<aside><h2>Source completeness, not results</h2><p>'
              'Business / logical / runtime navigation: requirements / architecture / sequences. '
              'Deployment requires its own selected source section.</p></aside>']
    for name, view in sorted(data["views"].items()):
        lines = _view_lines(name, view)
        result.append(f'<section class="view" data-view="{_escape(name)}" data-state="{_escape(view["state"])}">'
                      f'<h3>{_escape(lines[0])}</h3><pre>{_escape(chr(10).join(lines[1:]))}</pre></section>')
    result.append('<aside><h2>Source gaps and limits</h2><ul>'
                  + "".join('<li class="gap">' + _escape(gap) + "</li>" for gap in data["gaps"]) + "</ul></aside>")
    return "\n".join(result)


def _provenance(section):
    return (section["source_id"] + " — " + section["source_title"] + "\n"
            + section["path"] + ":" + str(section["line"]) + "\n"
            + section["reference"] + " @ " + section["baseline"])


def _sequence_svg(sequence):
    if sequence["status"] == "unsupported":
        return None
    participants, events = sequence["participants"], sequence["events"]
    slug = sequence["slug"]
    width = max(1040, 240 * len(participants) + 160)
    centers = {item["id"]: 160 + index * (width - 320) / max(1, len(participants) - 1)
               for index, item in enumerate(participants)}
    label_rows = max(len(_wrap(item["label"], 22)) for item in participants)
    actor_height = 36 + label_rows * 20
    y = actor_height + 120
    positions = []
    fragment = None
    frames = []
    for event in events:
        if event["kind"] == "start":
            fragment = (y, event["operator"])
            y += 56 + max(0, len(_wrap(event["label"], 80)) - 1) * 20
        elif event["kind"] == "else":
            y += 48 + max(0, len(_wrap(event["label"], 80)) - 1) * 20
        elif event["kind"] == "end":
            y += 24
            frames.append((fragment[0] - 24, y, fragment[1]))
            fragment = None
        else:
            # All source text remains visible; self-loops reserve another row.
            y += len(_wrap(event["label"], 70)) * 20 + 28
            if event["from"] == event["to"]:
                y += 28
        positions.append(y)
    root = _svg_root(slug, sequence["source"], "Source-declared participants, ordered messages and explicit branch boundaries.",
                     width, y + 80)
    _svg_lines(root, [sequence["source"], "Arrow glyphs are preserved; transport guarantees are not inferred."], 24, 28, size=14)
    for top, bottom, operator in frames:
        _element(root, "rect", x=48, y=top, width=width - 96, height=bottom - top,
                 fill="#ececec", stroke="#7a8399", rx=4)
        _element(root, "text", operator, x=60, y=top + 18, font_size=13)
    for participant in participants:
        center = centers[participant["id"]]
        _element(root, "line", x1=center, y1=80 + actor_height, x2=center, y2=y + 36,
                 stroke="#bfc0c0", stroke_dasharray="4 4")
    for event, position in zip(events, positions):
        if event["kind"] in ("start", "else"):
            if event["kind"] == "else":
                _element(root, "line", x1=48, x2=width - 48, y1=position - 40, y2=position - 40,
                         stroke="#7a8399", stroke_dasharray="4 4")
            group = _element(root, "g", data_branch=event["label"])
            _svg_lines(group, _wrap(event["label"], 80), 68, position - 16 - 20 * (len(_wrap(event["label"], 80)) - 1),
                       size=14, step=20)
        if event["kind"] != "message":
            continue
        left, right = centers[event["from"]], centers[event["to"]]
        arrow_y = position - (28 if left == right else 0)
        labels = _wrap(event["label"], 70)
        label_x = min(left, right) + 16 if left != right else left + 80
        label_width = max(20, max(len(line) for line in labels) * 9)
        if left == right:
            label_x = min(label_x, width - label_width - 24)
        else:
            label_x = min(label_x, width - label_width - 24)
        mask_y = arrow_y - len(labels) * 20 - 14
        _element(root, "rect", x=label_x - 4, y=mask_y, width=label_width + 8,
                 height=len(labels) * 20, fill="#f5f5f5")
        _svg_lines(root, labels, label_x, mask_y + 15, size=14, step=20)
        attributes = {"stroke": "#4f5d75", "stroke_width": 1.5, "fill": "none",
                      "marker_end": f"url(#{slug}-arrow)", "data_message": event["index"],
                      "data_from": event["from"], "data_to": event["to"], "data_arrow": event["arrow"]}
        if event["arrow"] == "-->>":
            attributes["stroke_dasharray"] = "5 4"
        if left == right:
            _element(root, "path", d=f"M{left} {arrow_y} H{left + 48} Q{left + 56} {arrow_y} {left + 56} {arrow_y + 8} "
                     f"V{arrow_y + 20} Q{left + 56} {arrow_y + 28} {left + 48} {arrow_y + 28} H{left}",
                     **attributes)
        else:
            _element(root, "line", x1=left, y1=arrow_y, x2=right, y2=arrow_y, **attributes)
    for participant in participants:
        group = _element(root, "g", data_participant=participant["id"])
        center = centers[participant["id"]]
        _element(group, "rect", x=center - 112, y=80, width=224, height=actor_height, rx=6,
                 fill="#ffffff", stroke="#4f5d75")
        _svg_lines(group, _wrap(participant["label"], 22), center - 96, 104, size=15, step=20)
        _element(group, "text", participant["kind"] + " " + participant["id"],
                 x=center - 96, y=80 + actor_height - 12, font_size=12)
    return root


def _section_html(section, *, slide=False):
    tag = "section" if slide else "article"
    attributes = ('class="slide" ' if slide else "") + f'data-section="{_escape(section["key"])}"'
    body = (f'<{tag} {attributes} id="{section["identity"]}">'
            f'<h2>{_escape(section["title"])}</h2>'
            f'<pre class="provenance">{_escape(_provenance(section))}</pre>'
            f'<pre>{_escape(chr(10).join(section["lines"]))}</pre>')
    if section["sequence"] is not None:
        visual = _sequence_svg(section["sequence"])
        body += ('<div class="figure">' + _svg_string(visual) + "</div>" if visual is not None else
                 "<p>Unsupported source sequence; no visual prefix is substituted.</p>")
    return body + f"</{tag}>"


def _architecture_svg(data):
    blocks = [("notice", "", [_NOTICE], None)]
    for name, view in sorted(data["views"].items()):
        blocks.append(("view", name, [part for line in _view_lines(name, view) for part in _wrap(line, 120)], None))
    for gap in data["gaps"]:
        blocks.append(("gap", "", _wrap("gap: " + gap, 120), None))
    for section in data["sections"]:
        lines = [section["title"], *_provenance(section).splitlines(), *section["lines"]]
        visual = _sequence_svg(section["sequence"]) if section["sequence"] is not None else None
        blocks.append(("section", section["key"], [part for line in lines for part in _wrap(line, 120)], visual))
    height = 140 + sum(len(lines) * 22 + 40 + (float(visual.attrib["viewBox"].split()[3]) if visual is not None else 0)
                       for _, _, lines, visual in blocks)
    root = _svg_root(_identity(data["scope"], "architecture"), "Architecture source document",
                     "Selected source sections, nine view completeness states and source-owned sequence diagrams.", 1280, height)
    _svg_lines(root, ["Architecture source document — " + data["status"], data["scope"], data["source"]["baseline"]], 24, 32)
    y = 128
    for kind, key, lines, visual in blocks:
        group = _element(root, "g", **({"data_view": key} if kind == "view" else
                                      {"data_section": key} if kind == "section" else {}))
        y = _svg_lines(group, lines, 24, y)
        if visual is not None:
            visual.set("x", "24")
            visual.set("y", str(y))
            visual.set("width", "1200")
            visual.set("height", visual.attrib["viewBox"].split()[3])
            group.append(visual)
            y += float(visual.attrib["height"])
        y += 40
    return root


def render_architecture(inputs, format) -> dict:
    """Read explicit local source pointers and return real HTML/SVG or gated refusal."""
    format = _format(format, ("html", "svg"))
    context = _load(inputs)
    if format in ("pdf", "pptx"):
        return _unavailable(context, format)
    data = _architecture_data(context)
    if format == "html":
        content = _html("Architecture sources — " + data["scope"],
                        '<p class="provenance">' + _escape(data["source"]["baseline"]) + "</p>"
                        + _views_html(data) + "".join(_section_html(section) for section in data["sections"]))
    else:
        content = _svg_string(_architecture_svg(data))
    return _result(context, format, content, status=data["status"], counts=_counts(data), gaps=data["gaps"])


def main() -> int:
    return _run_cli("architecture", render_architecture)


if __name__ == "__main__":
    raise SystemExit(main())
