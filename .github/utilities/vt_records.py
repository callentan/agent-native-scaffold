"""Shared readers for the existing VT form; no execution or source mutation."""

from __future__ import annotations

import re

from artifact_io import Artifact, ArtifactInputError, iter_markdown_lines
from check_artifacts import _HEADING, _INLINE_LINK
from check_traceability import section_lines


def owned_runs(source: Artifact) -> tuple[str, ...]:
    """Only child runs inside the source-owned H2; closing H2/H1 cannot qualify."""
    start = next((a.location.line for a in source.anchors if a.name == "runs"), None)
    if start is None:
        return ()
    anchors = {a.location.line: a.name for a in source.anchors}
    pattern = re.compile(re.escape(source.id.lower()) + r"-run-[0-9]+")
    pending, inside, runs = "runs", False, []
    for number, line in iter_markdown_lines(source.body, source.body_start_line):
        if number <= start:
            continue
        if line is None:
            pending = None
            continue
        if number in anchors:
            pending = anchors[number]
            continue
        heading = _HEADING.fullmatch(line)
        if heading:
            if not inside:
                if pending != "runs" or len(heading[1]) != 2:
                    return ()
                inside = True
            elif len(heading[1]) <= 2:
                break
            elif pending is not None and pattern.fullmatch(pending):
                runs.append(pending)
            pending = None
        elif line.strip():
            pending = None
    return tuple(runs)


def result_rows(source: Artifact, anchor: str,
                lines: tuple[tuple[int, str], ...] | None = None) -> tuple[dict, list[str]]:
    """Keep each real four-column observation/reason/line, not only its status."""
    lines = section_lines(source, anchor) if lines is None else lines
    expected = {target.criterion_anchor for target in source.targets}
    results, gaps = {}, []
    prefix = f"{source.relative_path}#{anchor}"
    labels = ("判据链接（目标由 frontmatter 定位）", "实际观察及原始报告定位",
              "实际结果", "未执行/跳过原因或失败差异")
    header, tables, previous = None, 0, 0
    for number, line in lines:
        if number != previous + 1:
            header = None
        previous = number
        if not line.strip().startswith("|"):
            header = None
            continue
        cells = [cell.strip().replace(r"\|", "|") for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if all(label in cells for label in labels):
            tables += 1
            if len(cells) != len(labels) or len(set(cells)) != len(labels):
                gaps.append(f"{prefix}: ambiguous verificationSummary.result table header")
                header = None
            else:
                header = {label: cells.index(label) for label in labels}
            continue
        if header is None or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if len(cells) != len(labels):
            gaps.append(f"{prefix}:{number}: malformed verificationSummary.result row")
            continue
        link = _INLINE_LINK.fullmatch(cells[header[labels[0]]])
        criterion = link[1].strip("<>").removeprefix("#") if link and link[1].strip("<>").startswith("#") else None
        status, observation, reason = (cells[header[label]] for label in (labels[2], labels[1], labels[3]))
        if criterion not in expected:
            gaps.append(f"{prefix}:{number}: unknown local criterion in verificationSummary.result")
        elif criterion in results:
            gaps.append(f"{prefix}:{number}: ambiguous verificationSummary.result for {criterion}")
        elif (status not in ("not-run", "pass", "fail", "skipped") or not observation
              or status in ("not-run", "skipped") and not reason):
            gaps.append(f"{prefix}:{number}: incomplete verificationSummary.result for {criterion}")
        else:
            results[criterion] = {"status": status, "observation": observation, "reason": reason, "line": number}
    if tables != 1:
        gaps.append(f"{prefix}: missing or ambiguous verificationSummary.result table")
    for criterion in sorted(expected - results.keys()):
        gaps.append(f"{prefix}: missing verificationSummary.result for {criterion}")
    if not expected:
        gaps.append(f"{prefix}: missing declared criterion targets for verificationSummary.result")
    return results, gaps


def plan_bytes(source: Artifact, raw: bytes) -> bytes:
    """Exclude ONLY genuine runs/applicability H2 subtrees; preserve other bytes.

    Pending explicit anchors belong to their next real heading, including the
    peer heading that terminates an excluded section. Literal text cannot lend a
    heading to an anchor. Declared criteria cannot belong to omitted subtrees.
    No normalization of frontmatter, whitespace or CRLF.
    """
    anchors = {a.location.line: a.name for a in source.anchors}
    pending, active = None, None
    omitted: list[tuple[int, int]] = []
    raw_lines = raw.decode("utf-8").splitlines(keepends=True)
    for number, line in iter_markdown_lines(source.body, source.body_start_line):
        if line is None:
            pending = None
            continue
        if number in anchors:
            pending = (anchors[number], number)
            continue
        heading = _HEADING.fullmatch(line)
        if heading:
            level = len(heading[1])
            if active is not None and level <= 2:
                omitted.append((active, pending[1] if pending else number))
                active = None
            if level == 2 and pending and pending[0] in ("runs", "applicability"):
                active = pending[1]
            pending = None
        elif line.strip():
            pending = None
    if active is not None:
        omitted.append((active, len(raw_lines) + 1))
    declared = {target.criterion_anchor for target in source.targets}
    for number, name in anchors.items():
        if name in declared and any(start <= number < end for start, end in omitted):
            raise ArtifactInputError("INVALID_CRITERION", source.path, number,
                                     f"Declared criterion {name} belongs to an omitted runs/applicability subtree")
    return b"".join(line.encode("utf-8") for number, line in enumerate(raw_lines, 1)
                    if not any(start <= number < end for start, end in omitted))
