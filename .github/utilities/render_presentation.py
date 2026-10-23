"""Render parameterized source-section slides as real, self-contained local HTML/SVG."""

from __future__ import annotations

from render_architecture import (
    _architecture_data, _counts, _provenance, _section_html, _sequence_svg, _view_lines, _views_html,
)
from render_traceability import (
    _element, _escape, _format, _html, _identity, _load, _NOTICE, _result, _run_cli,
    _svg_lines, _svg_root, _svg_string, _unavailable, _wrap,
)


def _slides(data):
    """Source structure is the backbone; pagination never substitutes a canned deck."""
    slides = []
    for section in data["sections"]:
        lines = [part for line in section["lines"] for part in _wrap(line, 100)]
        parts = [lines[index:index + 24] for index in range(0, len(lines), 24)] or [[]]
        for index, part in enumerate(parts):
            slides.append({
                **section, "lines": part, "identity": section["identity"] + "-page-" + str(index + 1),
                "title": section["title"] + (f" [part {index + 1}/{len(parts)}]" if len(parts) > 1 else ""),
                "sequence": section["sequence"] if index == len(parts) - 1 else None,
            })
    return slides


def _presentation_svg(data, slides):
    header = []
    for name, view in sorted(data["views"].items()):
        header.append((name, [part for line in _view_lines(name, view) for part in _wrap(line, 120)]))
    gaps = [part for gap in data["gaps"] for part in _wrap("gap: " + gap, 120)]
    header_height = 160 + sum(len(lines) * 22 + 24 for _, lines in header) + len(gaps) * 22
    layouts = []
    for slide in slides:
        heading = _wrap(slide["title"], 88)
        provenance = [part for line in _provenance(slide).splitlines() for part in _wrap(line, 120)]
        visual = _sequence_svg(slide["sequence"]) if slide["sequence"] is not None else None
        visual_height = float(visual.attrib["viewBox"].split()[3]) if visual is not None else 0
        height = max(720, 100 + len(heading) * 30 + (len(provenance) + len(slide["lines"])) * 22 + visual_height)
        layouts.append((slide, heading, provenance, visual, height))
    height = header_height + sum(layout[4] + 32 for layout in layouts) + 80
    root = _svg_root(_identity(data["scope"], "presentation"), "Selected source presentation",
                     "Source-defined sections as slides, source baselines, nine view gaps and supplied sequence messages.",
                     1280, height)
    _svg_lines(root, ["Selected source presentation — " + data["status"], data["scope"], data["source"]["baseline"]], 24, 32)
    y = 128
    for name, lines in header:
        group = _element(root, "g", data_view=name)
        y = _svg_lines(group, lines, 24, y) + 24
    y = _svg_lines(root, gaps, 24, y) + 32
    for slide, heading, provenance, visual, slide_height in layouts:
        group = _element(root, "g", **{"class": "slide", "data_section": slide["key"], "id": slide["identity"]})
        _element(group, "rect", x=16, y=y, width=1248, height=slide_height, fill="#ffffff", stroke="#bfc0c0")
        cursor = _svg_lines(group, heading, 40, y + 40, size=22, step=30)
        cursor = _svg_lines(group, provenance, 40, cursor + 12, size=14) + 20
        cursor = _svg_lines(group, slide["lines"], 40, cursor, size=16)
        if visual is not None:
            visual.set("x", "32")
            visual.set("y", str(cursor))
            visual.set("width", "1200")
            visual.set("height", visual.attrib["viewBox"].split()[3])
            group.append(visual)
        y += slide_height + 32
    _svg_lines(root, [_NOTICE], 24, y + 24, size=13)
    return root


def render_presentation(inputs, format) -> dict:
    """Read selected supplied sources; return derived slides, never approval/execution."""
    format = _format(format, ("html", "svg"))
    context = _load(inputs)
    if format in ("pdf", "pptx"):
        return _unavailable(context, format)
    data = _architecture_data(context)
    slides = _slides(data)
    if format == "html":
        titles = list(dict.fromkeys(section["source_title"] for section in data["sections"]))
        title = " / ".join(titles) if titles else "Empty presentation selection"
        content = _html(title, '<p class="provenance">' + _escape(data["source"]["baseline"]) + "</p>"
                        + _views_html(data) + "".join(_section_html(slide, slide=True) for slide in slides))
    else:
        content = _svg_string(_presentation_svg(data, slides))
    return _result(context, format, content, status=data["status"],
                   counts={**_counts(data), "slides": len(slides)}, gaps=data["gaps"])


def main() -> int:
    return _run_cli("presentation", render_presentation)


if __name__ == "__main__":
    raise SystemExit(main())
