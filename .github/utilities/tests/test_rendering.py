"""Task17 / ENH-17: independently specified RENDER-01..16, not renderer examples."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import importlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import yaml

from artifact_io import ArtifactInputError, parse_artifact
from export_model import export_view
from tests.helpers import (
    WORKTREE, directory_link, git, metadata, seed_git_repo, seed_implementation_fixture, source_bytes,
    temporary_workspace, write_metadata,
)


SCOPE = "render/CTX-A"
OTHER = "render/CTX-B"
VIEWS = ("architecture", "governance", "quality", "release", "requirements",
         "risk", "sequences", "stories", "verification")
SVG = "{http://www.w3.org/2000/svg}"
SEQUENCE = """sequenceDiagram
participant Caller as Source Author
actor Ledger as Candidate Keeper
Caller->>Ledger: propose candidate
alt accepted
Ledger-->>Caller: accepted candidate
else refused
Ledger-->>Caller: refusal preserves owner
end
Ledger-->>Caller: error surfaced unchanged
"""


def baseline(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class Document(HTMLParser):
    """Independent HTML tree observations, not regex signature acceptance."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


class RenderingTests(unittest.TestCase):
    def setUp(self):
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "导出 sources with spaces"
        self.root.mkdir()

    def tool(self, name):
        # Missing behavior is an assertion RED, not an import/collection error.
        self.assertIsNotNone(importlib.util.find_spec(name), f"Task17 {name} is not implemented")
        return importlib.import_module(name)

    def artifact(self, identifier, kind, body, *, upstream=(), targets=(), scope=SCOPE, path=None):
        return write_metadata(self.root, metadata(
            id=identifier, kind=kind, scope=scope, upstream=list(upstream), targets=list(targets)),
            body, path or identifier + ".md")

    def graph(self):
        # Hand-owned graph: five owners, four directed declarations, one isolate,
        # A/REQ -> A/SR -> A/REQ cycle; B/REQ must never be merged with A/REQ.
        self.artifact("REQ-001", "stakeholder-requirement",
                      '# REQ-001 Source proposal\n<a id="req-001-ac-01"></a>\n'
                      '### REQ-001-AC-01 Candidate rule\nKeep source ownership.\n',
                      upstream=[SCOPE + "/SR-001#sr-001-ac-01"], path="requirements/REQ-001.md")
        self.artifact("REQ-001", "stakeholder-requirement",
                      '# REQ-001 Foreign candidate\n<a id="req-001-ac-01"></a>\n'
                      '### REQ-001-AC-01 Different owner\nDo not join short IDs.\n',
                      scope=OTHER, path="foreign/REQ-001.md")
        self.artifact("SR-001", "software-requirement",
                      '# SR-001 Preserve bytes\n<a id="sr-001-ac-01"></a>\n'
                      '### SR-001-AC-01 Keep bytes\nA refusal leaves the source intact.\n',
                      upstream=[SCOPE + "/REQ-001#req-001-ac-01", OTHER + "/REQ-001#req-001-ac-01"],
                      path="software/SR-001.md")
        self.artifact("VT-001", "verification-test",
                      '# VT-001 Plan only\n<a id="criterion"></a>\n## Unexecuted criterion\n'
                      'Compare refusal bytes; no execution is asserted.\n',
                      targets=[{"target": SCOPE + "/SR-001#sr-001-ac-01",
                                "criterionAnchor": "criterion", "testId": "test_owned_refusal"}])
        self.artifact("CAP-001", "capability",
                      '# CAP-001 Isolated scope\n<a id="ownership"></a>\n## Ownership\n'
                      'This owner has no declared relationships.\n')

    def manifest(self, selections):
        path = self.root / "model-sources.yaml"
        path.write_text(yaml.safe_dump({"schemaVersion": 1, "scopes": {SCOPE: selections}},
                                       allow_unicode=True, sort_keys=False), encoding="utf-8")
        return path

    def pointer(self, path, fragment=""):
        return {"reference": path.relative_to(self.root).as_posix() + fragment, "baseline": baseline(path)}

    def architecture(self, title="Workbench Alpha", *, sequence=SEQUENCE, deployment=False):
        self.graph()
        body = (
            f'# SWAS-001 {title}\n<a id="basis"></a>\n## Selected basis\n'
            f'{title} is a candidate source, not an approval.\n'
            '<a id="business"></a>\n## Owned business\nThe source author owns candidate meaning.\n'
            '<a id="logical"></a>\n## Logical boundary\nA keeper preserves refusal bytes.\n'
            '<a id="runtime"></a>\n## Runtime boundary\nErrors are surfaced without source mutation.\n'
        )
        if deployment:
            body += ('<a id="deployment"></a>\n## Supplied deployment\n'
                     'Only the supplied offline workstation is in this source.\n')
        spec = self.artifact("SWAS-001", "architecture-specification", body,
                             path="architecture/规格 空格.md")
        sources = [self.pointer(spec)]
        selections = {"requirements": [{"path": "software/SR-001.md",
                                        "baseline": baseline(self.root / "software/SR-001.md")}]}
        if sequence is not None:
            self.artifact("UC-001", "use-case",
                          '# UC-001 Source interaction\n<a id="main"></a>\n## Main path\n'
                          'Author proposes a candidate; keeper owns its refusal.\n')
            abb = self.artifact("ABB-001", "architecture-building-block",
                               '# ABB-001 Keeper candidate\n<a id="structure"></a>\n## Source structure\n'
                               'Own candidate bytes.\n<a id="interfaces"></a>\n## Supplied interface\n'
                               'Conceptual exchange only.\n<a id="runtime"></a>\n## Runtime\n'
                               '| Field | Source |\n|---|---|\n| language | not selected by owner |\n'
                               '| framework | no framework selected |\n')
            seq = self.artifact("SEQ-001", "sequence-diagram",
                               '# SEQ-001 Candidate exchange\n<a id="basis"></a>\n## Source basis\n'
                               'Conceptual candidate exchange, no transport guarantees.\n'
                               '<a id="participants"></a>\n## Source roles\n'
                               '| Field | Value |\n|---|---|\n| externalPartners | none in this source |\n'
                               'Source Author proposes; Candidate Keeper preserves the owner.\n'
                               '<a id="paths"></a>\n## Source boundaries\n'
                               '| Field | Value |\n|---|---|\n| hasAsync | false |\n'
                               'success returns the candidate; refusal preserves owner; error leaves bytes unchanged.\n'
                               '<a id="diagram"></a>\n## Supplied sequence\n```mermaid\n' + sequence + '```\n'
                               '<a id="limitations"></a>\n## Known gaps\nNo runtime test has executed.\n',
                               upstream=[SCOPE + "/UC-001#main", SCOPE + "/ABB-001#structure"],
                               path="architecture/SEQ-001.md")
            sources.append(self.pointer(seq))
            selections["architecture"] = [{"path": abb.relative_to(self.root).as_posix(), "baseline": baseline(abb)}]
            selections["sequences"] = [{"path": seq.relative_to(self.root).as_posix(), "baseline": baseline(seq)}]
        self.manifest(selections)
        return {"root": self.root, "scope": SCOPE, "sources": sources}

    def trace(self, format="json", **extra):
        return self.tool("render_traceability").render_traceability(
            {"root": self.root, "scope": SCOPE, "format": format, **extra})

    def render(self, name, inputs, format="html"):
        return getattr(self.tool(name), name)(inputs, format)

    def cli(self, name, *arguments):
        script = WORKTREE / ".github/utilities" / (name + ".py")
        self.assertTrue(script.is_file(), f"Task17 {name} CLI is not implemented")
        return subprocess.run([sys.executable, "-B", "-X", "utf8", str(script),
                               "--root", str(self.root), "--scope", SCOPE, *arguments],
                              cwd=self.workspace, shell=False, capture_output=True,
                              text=True, encoding="utf-8")

    def assert_error(self, code, action):
        with self.assertRaises(ArtifactInputError) as caught:
            action()
        self.assertEqual(code, caught.exception.code)
        self.assertGreaterEqual(caught.exception.line, 1)

    def assert_local_html(self, content):
        self.assertTrue(content.lower().startswith("<!doctype html>"))
        document = Document(content)
        tags = [tag for tag, _ in document.tags]
        self.assertIn("html", tags)
        self.assertIn("head", tags)
        self.assertIn("body", tags)
        self.assertNotIn("script", tags)
        self.assertNotIn("iframe", tags)
        self.assertNotIn("link", tags)
        for _, attrs in document.tags:
            self.assertFalse(any(key.lower().startswith("on") for key in attrs))
            for name in ("href", "src", "xlink:href"):
                if name in attrs:
                    self.assertTrue(attrs[name].startswith("#"), attrs)
        self.assertNotIn("@import", content)
        return document

    def svg(self, content):
        root = ET.fromstring(content)
        self.assertEqual(SVG + "svg", root.tag)
        self.assertEqual("img", root.attrib["role"])
        self.assertEqual(SVG + "title", list(root)[0].tag)
        ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
        self.assertEqual(len(ids), len(set(ids)), "SVG IDs must not collide")
        for name in root.attrib["aria-labelledby"].split():
            self.assertIn(name, ids)
        self.assertGreater(float(root.attrib["viewBox"].split()[2]), 0)
        self.assertGreater(float(root.attrib["viewBox"].split()[3]), 0)
        return root

    # RENDER-01: a valid empty inventory differs from invalid root/model/scope.
    def test_empty_inventory_is_explicit_without_demo(self):
        result = self.trace()
        data = json.loads(result["content"])
        self.assertEqual(("empty", [], []), (result["status"], data["nodes"], data["edges"]))
        self.assertEqual(0, result["counts"]["nodes"])
        self.assertIn("empty", " ".join(result["gaps"]).lower())

    def test_empty_trace_svg_is_real_and_has_zero_nodes(self):
        result = self.trace("svg")
        root = self.svg(result["content"])
        self.assertEqual([], [n for n in root.iter() if "data-node" in n.attrib])
        self.assertIn("empty", "".join(root.itertext()).lower())

    def test_empty_inventory_does_not_make_architecture_scope_valid(self):
        self.assert_error("UNKNOWN_SCOPE", lambda: self.render(
            "render_architecture", {"root": self.root, "scope": SCOPE, "sources": []}))

    # RENDER-02/03: literal independent identities and direction, including cycle.
    def test_exact_owners_edges_directions_and_isolate(self):
        self.graph()
        result = self.trace()
        data = json.loads(result["content"])
        self.assertEqual([
            SCOPE + "/CAP-001", SCOPE + "/REQ-001", SCOPE + "/SR-001", SCOPE + "/VT-001",
            OTHER + "/REQ-001",
        ], [node["key"] for node in data["nodes"]])
        self.assertEqual({
            (SCOPE + "/REQ-001", SCOPE + "/SR-001", "upstream", SCOPE + "/REQ-001",
             SCOPE + "/SR-001#sr-001-ac-01"),
            (SCOPE + "/SR-001", SCOPE + "/REQ-001", "upstream", SCOPE + "/SR-001",
             SCOPE + "/REQ-001#req-001-ac-01"),
            (SCOPE + "/SR-001", OTHER + "/REQ-001", "upstream", SCOPE + "/SR-001",
             OTHER + "/REQ-001#req-001-ac-01"),
            (SCOPE + "/VT-001", SCOPE + "/SR-001", "targets", SCOPE + "/VT-001#criterion",
             SCOPE + "/SR-001#sr-001-ac-01"),
        }, {(e["source"], e["target"], e["relation"], e["sourceRef"], e["targetRef"]) for e in data["edges"]})
        # Four actual declarations, NOT five: two-node cycle does not add an edge.
        self.assertEqual((5, 4), (result["counts"]["nodes"], result["counts"]["edges"]))
        for node in data["nodes"]:
            self.assertEqual(baseline(self.root / node["path"]), node["baseline"])
            self.assertGreater(node["line"], 0)
        target = next(e for e in data["edges"] if e["relation"] == "targets")
        self.assertEqual("test_owned_refusal", target["testId"])
        self.assertGreater(target["line"], 0)

    def test_second_scope_selection_excludes_unrelated_owners(self):
        self.graph()
        result = self.tool("render_traceability").render_traceability({"root": self.root, "scope": OTHER})
        self.assertEqual([OTHER + "/REQ-001"], [n["key"] for n in json.loads(result["content"])["nodes"]])

    def test_svg_draws_each_declared_edge_and_isolated_owner(self):
        self.graph()
        root = self.svg(self.trace("svg")["content"])
        nodes = [n for n in root.iter() if "data-node" in n.attrib]
        edges = [n for n in root.iter() if "data-edge" in n.attrib]
        self.assertEqual(5, len(nodes))
        self.assertEqual(4, len(edges))
        self.assertEqual({SCOPE + "/REQ-001", OTHER + "/REQ-001"},
                         {n.attrib["data-node"] for n in nodes if n.attrib["data-node"].endswith("/REQ-001")})
        for edge in edges:
            self.assertIn("marker-end", edge.attrib)
            self.assertIn("data-source-ref", edge.attrib)
            self.assertIn("data-target-ref", edge.attrib)

    def test_html_graph_is_self_contained_with_real_source_navigation(self):
        self.graph()
        result = self.trace("html")
        document = self.assert_local_html(result["content"])
        self.assertEqual(5, sum("data-node" in attrs for _, attrs in document.tags))
        self.assertEqual(4, sum("data-edge" in attrs for _, attrs in document.tags))
        self.assertIn("foreign/REQ-001.md", "".join(document.text))
        self.assertNotIn(str(self.root), result["content"])

    # RENDER-04: errors cannot be turned into plausible partial models.
    def test_invalid_root_is_typed_not_empty(self):
        self.assert_error("INVALID_ROOT", lambda: self.tool("render_traceability").render_traceability(
            {"root": self.root / "absent", "scope": SCOPE}))

    def test_unknown_nonempty_scope_is_typed(self):
        self.graph()
        self.assert_error("UNKNOWN_SCOPE", lambda: self.trace(scope="render/absent"))

    def test_invalid_relation_does_not_render(self):
        self.graph()
        path = self.root / "software/SR-001.md"
        path.write_text(path.read_text().replace("CTX-B/REQ-001", "CTX-B/REQ-999"), encoding="utf-8")
        self.assert_error("DANGLING_REFERENCE", self.trace)

    def test_invalid_artifact_version_is_not_optional_gap(self):
        self.graph()
        path = self.root / "CAP-001.md"
        path.write_text(path.read_text().replace("schemaVersion: 1", "schemaVersion: 2"), encoding="utf-8")
        self.assert_error("UNSUPPORTED_SCHEMA_VERSION", self.trace)

    def test_rejects_detached_model_as_input_authority(self):
        self.graph()
        self.assert_error("INVALID_RENDER_INPUT", lambda: self.tool("render_traceability").render_traceability(
            export_view(self.root, SCOPE)))

    def test_persisted_model_is_recomputed_before_render(self):
        self.graph()
        model = self.workspace / "old model.yaml"
        model.write_text(yaml.safe_dump(export_view(self.root, SCOPE)), encoding="utf-8")
        before = source_bytes(self.root)
        result = self.trace(model_path=model)
        self.assertEqual(5, result["counts"]["nodes"])
        self.assertEqual(before, source_bytes(self.root))

    def test_manual_persisted_view_is_drift_even_when_schema_valid(self):
        self.graph()
        data = export_view(self.root, SCOPE)
        data["views"]["risk"]["gaps"].append("manual unsupported risk assertion")
        model = self.workspace / "manual.yaml"
        model.write_text(yaml.safe_dump(data), encoding="utf-8")
        self.assert_error("MODEL_MISMATCH", lambda: self.trace(model_path=model))

    def test_stale_persisted_source_is_drift(self):
        self.graph()
        model = self.workspace / "old.json"
        model.write_text(json.dumps(export_view(self.root, SCOPE)), encoding="utf-8")
        path = self.root / "CAP-001.md"
        path.write_bytes(path.read_bytes() + b"\nAdditional candidate detail.\n")
        self.assert_error("STALE_MODEL_SOURCE", lambda: self.trace(model_path=model))

    def test_invalid_persisted_model_version_has_no_content(self):
        self.graph()
        model = self.workspace / "bad.json"
        model.write_text('{"schemaVersion": 2}', encoding="utf-8")
        self.assert_error("UNSUPPORTED_SCHEMA_VERSION", lambda: self.trace(model_path=model))

    def test_unknown_view_manifest_is_input_error(self):
        self.graph()
        self.manifest({"invented": [{"path": "CAP-001.md", "baseline": baseline(self.root / "CAP-001.md")}]})
        self.assert_error("INVALID_SOURCE_MANIFEST", self.trace)

    def test_bad_explicit_source_baseline_is_error_not_partial(self):
        inputs = self.architecture(sequence=None)
        inputs["sources"][0]["baseline"] = "sha256:" + "0" * 64
        self.assert_error("BASE_MISMATCH", lambda: self.render("render_architecture", inputs))

    def test_missing_explicit_source_is_error_not_optional_view_gap(self):
        inputs = self.architecture(sequence=None)
        inputs["sources"][0]["reference"] = "missing/SWAS-001.md"
        self.assert_error("FILE_NOT_FOUND", lambda: self.render("render_architecture", inputs))

    def test_source_fragment_must_exist(self):
        inputs = self.architecture(sequence=None)
        inputs["sources"][0]["reference"] += "#not-present"
        self.assert_error("BROKEN_ANCHOR", lambda: self.render("render_architecture", inputs))

    def test_structured_source_needs_existing_view_validation(self):
        inputs = self.architecture(sequence=None)
        path = self.root / "arbitrary.yaml"
        path.write_text("secretTopology: [invented]\n", encoding="utf-8")
        inputs["sources"] = [self.pointer(path)]
        self.assert_error("INVALID_OPTIONAL_SOURCE", lambda: self.render("render_architecture", inputs))

    # RENDER-05/08: partial SWAS must show actual nine views, never risk/stack defaults.
    def test_partial_architecture_keeps_nine_views_and_missing_sources(self):
        inputs = self.architecture(sequence=None)
        result = self.render("render_architecture", inputs)
        document = self.assert_local_html(result["content"])
        self.assertEqual(set(VIEWS), {a["data-view"] for _, a in document.tags if "data-view" in a})
        self.assertEqual("partial", result["status"])
        self.assertTrue(any("deployment" in gap for gap in result["gaps"]))
        self.assertTrue(any("risk" in gap for gap in result["gaps"]))
        self.assertIn("Owned business", "".join(document.text))
        self.assertIn("architecture/规格 空格.md", "".join(document.text))
        self.assertNotIn("Kubernetes", result["content"])
        self.assertNotIn("risk accepted", result["content"].lower())
        self.assertNotIn("safetyClass: A", result["content"])

    def test_supplied_deployment_is_preserved_not_inferred(self):
        inputs = self.architecture(sequence=None, deployment=True)
        result = self.render("render_architecture", inputs)
        self.assertIn("supplied offline workstation", result["content"])
        self.assertFalse(any("deployment source is absent" in gap for gap in result["gaps"]))

    def test_architecture_svg_contains_actual_sections_and_view_states(self):
        inputs = self.architecture(sequence=None)
        result = self.render("render_architecture", inputs, "svg")
        root = self.svg(result["content"])
        self.assertEqual(set(VIEWS), {n.attrib["data-view"] for n in root.iter() if "data-view" in n.attrib})
        self.assertEqual({"basis", "business", "logical", "runtime"},
                         {n.attrib["data-section"] for n in root.iter() if "data-section" in n.attrib})
        self.assertIn("Errors are surfaced without source mutation.", "".join(root.itertext()))

    def test_source_fragment_selects_only_owned_section(self):
        inputs = self.architecture(sequence=None)
        inputs["sources"][0]["reference"] += "#business"
        result = self.render("render_architecture", inputs)
        document = Document(result["content"])
        self.assertEqual(["business"], [a["data-section"] for _, a in document.tags if "data-section" in a])
        self.assertNotIn("Errors are surfaced without source mutation.", result["content"])

    # RENDER-06/07: draw finite syntax from the owned closed fence, with direction.
    def test_sequence_draws_exact_participants_messages_and_branches(self):
        inputs = self.architecture()
        result = self.render("render_architecture", inputs)
        document = Document(result["content"])
        self.assertEqual(("partial", 1, 4),
                         (result["status"], result["counts"]["diagrams"], result["counts"]["messages"]))
        self.assertEqual(["Caller", "Ledger"], [a["data-participant"] for _, a in document.tags if "data-participant" in a])
        self.assertEqual([
            ("Caller", "Ledger", "->>"), ("Ledger", "Caller", "-->>"),
            ("Ledger", "Caller", "-->>"), ("Ledger", "Caller", "-->>"),
        ], [(a["data-from"], a["data-to"], a["data-arrow"])
            for _, a in document.tags if "data-message" in a])
        self.assertEqual(["accepted", "refused"], [a["data-branch"] for _, a in document.tags if "data-branch" in a])
        self.assertIn("Source Author", "".join(document.text))
        self.assertIn("error leaves bytes unchanged", "".join(document.text))
        self.assertNotIn("broker", result["content"].lower())

    def test_sequence_svg_has_drawn_arrows_not_only_copied_code(self):
        inputs = self.architecture()
        result = self.render("render_architecture", inputs, "svg")
        root = self.svg(result["content"])
        arrows = [n for n in root.iter() if "data-message" in n.attrib]
        self.assertEqual(4, len(arrows))
        self.assertTrue(all(n.tag in (SVG + "path", SVG + "line") for n in arrows))
        self.assertTrue(all("marker-end" in n.attrib for n in arrows))
        self.assertEqual(3, sum("stroke-dasharray" in n.attrib for n in arrows))

    def test_self_message_is_drawn_as_directional_loop(self):
        inputs = self.architecture(sequence="sequenceDiagram\nparticipant Caller\nCaller->>Caller: retain candidate\n")
        root = self.svg(self.render("render_architecture", inputs, "svg")["content"])
        arrow = next(n for n in root.iter() if "data-message" in n.attrib)
        self.assertEqual((SVG + "path", "Caller", "Caller"),
                         (arrow.tag, arrow.attrib["data-from"], arrow.attrib["data-to"]))
        self.assertIn("Q", arrow.attrib["d"])

    def test_comments_and_outer_literals_cannot_create_visual_messages(self):
        inputs = self.architecture(sequence=None)
        source = self.artifact("SEQ-002", "sequence-diagram",
                              '# SEQ-002 Literal examples\n<a id="diagram"></a>\n## Examples\n'
                              '<!--\n```mermaid\n' + SEQUENCE + '```\n-->\n'
                              '````markdown\n```mermaid\n' + SEQUENCE + '```\n````\n')
        inputs["sources"].append(self.pointer(source))
        result = self.render("render_architecture", inputs)
        self.assertEqual(("unsupported", 0, 0),
                         (result["status"], result["counts"]["diagrams"], result["counts"]["messages"]))

    def test_unclosed_mermaid_is_not_rendered(self):
        inputs = self.architecture(sequence=None)
        source = self.artifact("SEQ-002", "sequence-diagram",
                              '# SEQ-002 Unclosed\n<a id="diagram"></a>\n## Source\n```mermaid\n' + SEQUENCE)
        inputs["sources"].append(self.pointer(source))
        result = self.render("render_architecture", inputs)
        self.assertEqual(("unsupported", 0), (result["status"], result["counts"]["messages"]))

    def test_sequence_in_sibling_section_does_not_fill_diagram(self):
        inputs = self.architecture(sequence=None)
        source = self.artifact("SEQ-002", "sequence-diagram",
                              '# SEQ-002 Wrong section\n<a id="diagram"></a>\n## Source\n'
                              'No actual diagram supplied.\n## Sibling example\n```mermaid\n' + SEQUENCE + '```\n')
        inputs["sources"].append(self.pointer(source))
        result = self.render("render_architecture", inputs)
        self.assertEqual(("unsupported", 0), (result["status"], result["counts"]["messages"]))

    def test_shared_section_fences_respect_owner_and_literal_boundaries(self):
        self.graph()
        source = self.artifact("SEQ-002", "sequence-diagram",
                              '# SEQ-002 Owned\n<a id="diagram"></a>\n## Actual\n'
                              '```mermaid\n' + SEQUENCE + '```\n## Sibling\n'
                              '```mermaid\nsequenceDiagram\nX->>Y: not owned\n```\n')
        artifact = parse_artifact(source, self.root)
        module = importlib.import_module("artifact_io")
        self.assertTrue(hasattr(module, "section_fences"), "Shared owned section fence reader is missing")
        blocks = module.section_fences(artifact, "diagram")
        self.assertEqual([SEQUENCE.rstrip("\n")], [block.body for block in blocks])

    def test_unsupported_statement_does_not_silently_drop_message(self):
        inputs = self.architecture(sequence=SEQUENCE + "Note over Caller: unsupported note\n")
        result = self.render("render_architecture", inputs)
        self.assertEqual(("unsupported", 0), (result["status"], result["counts"]["messages"]))
        self.assertIn("unsupported", " ".join(result["gaps"]).lower())

    def test_undeclared_participant_and_incomplete_fragment_are_explicit(self):
        for sequence in ("sequenceDiagram\nCaller->>Other: not declared\n",
                         "sequenceDiagram\nparticipant Caller\nparticipant Ledger\nalt pending\nCaller->>Ledger: propose\n"):
            with self.subTest(sequence=sequence):
                source = self.artifact("SEQ-002", "sequence-diagram",
                                      '# SEQ-002 Invalid subset\n<a id="diagram"></a>\n## Actual\n'
                                      '```mermaid\n' + sequence + '```\n')
                if not (self.root / "CAP-001.md").exists():
                    self.graph()
                result = self.render("render_architecture",
                                     {"root": self.root, "scope": SCOPE, "sources": [self.pointer(source)]})
                self.assertEqual(("unsupported", 0), (result["status"], result["counts"]["messages"]))

    def test_nested_fragment_and_init_directive_are_not_executed(self):
        self.graph()
        for addition in ("%%{init: {'theme':'remote'}}%%\n",
                         "alt inner\nCaller->>Ledger: nested\nend\n"):
            with self.subTest(addition=addition):
                sequence = ("sequenceDiagram\nparticipant Caller\nparticipant Ledger\n"
                            "alt outer\nCaller->>Ledger: proposal\n" + addition + "end\n")
                source = self.artifact("SEQ-002", "sequence-diagram",
                                      '# SEQ-002 Limited\n<a id="diagram"></a>\n## Actual\n'
                                      '```mermaid\n' + sequence + '```\n')
                result = self.render("render_architecture",
                                     {"root": self.root, "scope": SCOPE, "sources": [self.pointer(source)]})
                self.assertEqual("unsupported", result["status"])

    def test_opt_loop_and_comment_preserve_source_order(self):
        sequence = ("sequenceDiagram\nparticipant Caller\nparticipant Ledger\n"
                    "%% Source-owned comment\nopt proposed\nCaller->>Ledger: first\nend\n"
                    "loop supplied iteration\nLedger-->>Caller: second\nend\n")
        inputs = self.architecture(sequence=sequence)
        result = self.render("render_architecture", inputs)
        document = Document(result["content"])
        self.assertEqual(["0", "1"], [a["data-message"] for _, a in document.tags if "data-message" in a])
        self.assertEqual(2, result["counts"]["messages"])

    # RENDER-09/11: actual source structure, not a filename-only hardcoded deck.
    def test_presentation_uses_selected_sections_content_and_source_ids(self):
        inputs = self.architecture(sequence=None)
        result = self.render("render_presentation", inputs)
        document = self.assert_local_html(result["content"])
        self.assertEqual(["basis", "business", "logical", "runtime"],
                         [a["data-section"] for _, a in document.tags if "data-section" in a])
        self.assertEqual(4, result["counts"]["sections"])
        self.assertEqual(4, sum(a.get("class") == "slide" for _, a in document.tags))
        self.assertIn(SCOPE + "/SWAS-001", "".join(document.text))
        self.assertIn("Workbench Alpha", "".join(document.text))

    def test_distinct_presentation_source_changes_sections_not_only_filename(self):
        inputs = self.architecture(sequence=None)
        first = self.render("render_presentation", inputs)
        different = self.artifact("SWAS-002", "architecture-specification",
                                  '# SWAS-002 Beta review notes\n<a id="tradeoffs"></a>\n'
                                  '## Candidate tradeoffs\nNo topology has been selected for Beta.\n'
                                  '<a id="questions"></a>\n## Open questions\nWho owns the offline boundary?\n',
                                  path="architecture/Beta notes.md")
        inputs["sources"] = [self.pointer(different)]
        second = self.render("render_presentation", inputs)
        document = Document(second["content"])
        self.assertEqual(["tradeoffs", "questions"], [a["data-section"] for _, a in document.tags if "data-section" in a])
        self.assertIn("Beta review notes", "".join(document.text))
        self.assertIn("Who owns the offline boundary?", "".join(document.text))
        self.assertNotIn("Workbench Alpha", second["content"])
        self.assertNotEqual(first["content"], second["content"])

    def test_presentation_svg_has_real_nonzero_slides_and_content(self):
        inputs = self.architecture(sequence=None)
        result = self.render("render_presentation", inputs, "svg")
        root = self.svg(result["content"])
        self.assertEqual(4, sum(n.attrib.get("class") == "slide" for n in root.iter()))
        self.assertIn("keeper preserves refusal bytes", "".join(root.itertext()))
        self.assertEqual(4, result["counts"]["slides"])

    def test_presentation_keeps_actual_sequence_visualization(self):
        inputs = self.architecture()
        result = self.render("render_presentation", inputs)
        document = Document(result["content"])
        self.assertEqual(4, sum("data-message" in a for _, a in document.tags))
        self.assertEqual(4, result["counts"]["messages"])

    def test_repeated_all_local_formats_are_byte_deterministic(self):
        inputs = self.architecture()
        before = source_bytes(self.root)
        for name, formats in (("render_traceability", ("json", "svg", "html")),
                              ("render_architecture", ("svg", "html")),
                              ("render_presentation", ("svg", "html"))):
            for format in formats:
                with self.subTest(name=name, format=format):
                    first = self.trace(format) if name == "render_traceability" else self.render(name, inputs, format)
                    second = self.trace(format) if name == "render_traceability" else self.render(name, inputs, format)
                    self.assertEqual(first, second)
                    self.assertNotIn(str(self.workspace), first["content"])
        self.assertEqual(before, source_bytes(self.root))

    # RENDER-10/13: hostile text stays text in DOM and XML, never a resource.
    def test_untrusted_source_text_is_encoded_in_html_and_svg(self):
        inputs = self.architecture(sequence=None)
        source = self.artifact("SWAS-002", "architecture-specification",
                              '# SWAS-002 Unsafe-looking candidate\n<a id="text"></a>\n## Source text\n'
                              '<script>alert("candidate")</script>\n'
                              '<img src="https://example.invalid/no-fetch" onerror="bad()">\n'
                              '[source text](javascript:alert(1)) & "quotes" <tag>\n',
                              path="architecture/untrusted.md")
        inputs["sources"] = [self.pointer(source)]
        for name in ("render_architecture", "render_presentation"):
            document = self.assert_local_html(self.render(name, inputs)["content"])
            text = "".join(document.text)
            self.assertIn('<script>alert("candidate")</script>', text)
            root = self.svg(self.render(name, inputs, "svg")["content"])
            self.assertEqual([], root.findall(".//" + SVG + "script"))
            self.assertIn("[source text](javascript:alert(1))", "".join(root.itertext()))

    def test_unsafe_sequence_label_is_text_not_executable_svg(self):
        inputs = self.architecture(sequence=(
            'sequenceDiagram\nparticipant Caller as <script>candidate</script>\n'
            'participant Ledger as "Keeper & owner"\n'
            'Caller->>Ledger: <img src=x onerror=bad()> & "candidate"\n'))
        result = self.render("render_architecture", inputs, "svg")
        root = self.svg(result["content"])
        self.assertIn("<script>candidate</script>", "".join(root.itertext()))
        self.assertEqual([], root.findall(".//" + SVG + "image"))
        self.assertEqual(1, result["counts"]["messages"])

    def test_svg_long_unicode_content_is_not_truncated_or_zero_height(self):
        inputs = self.architecture(sequence=None)
        text = "来源甲 & candidate boundary " * 70 + "FINAL-SOURCE-TOKEN"
        source = self.artifact("SWAS-002", "architecture-specification",
                              '# SWAS-002 Long candidate\n<a id="long"></a>\n## Supplied long content\n' + text + "\n")
        inputs["sources"] = [self.pointer(source)]
        for name in ("render_architecture", "render_presentation"):
            root = self.svg(self.render(name, inputs, "svg")["content"])
            self.assertIn("FINAL-SOURCE-TOKEN", "".join(root.itertext()))
            height = float(root.attrib["viewBox"].split()[3])
            for node in root.iter():
                if node.tag == SVG + "text" and "y" in node.attrib:
                    self.assertLess(float(node.attrib["y"]), height)

    # RENDER-12/16: explicit new output, real files and aliases; no author overwrite.
    def test_default_cli_is_read_only_actual_json(self):
        self.graph()
        before = source_bytes(self.root)
        result = self.cli("render_traceability")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(5, len(json.loads(result.stdout)["nodes"]))
        self.assertEqual(before, source_bytes(self.root))

    def test_new_unicode_space_output_matches_actual_format_and_stdout(self):
        self.graph()
        output = self.workspace / "新 导出.svg"
        result = self.cli("render_traceability", "--format", "svg", "--output", str(output))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.svg(output.read_text(encoding="utf-8"))
        self.assertEqual(output.read_text(encoding="utf-8"), result.stdout)

    def test_existing_nonempty_empty_and_directory_outputs_are_conflicts(self):
        self.graph()
        for name, value in (("owner.svg", b"owner bytes"), ("empty.svg", b""), ("folder.svg", None)):
            output = self.root / name
            output.mkdir() if value is None else output.write_bytes(value)
            before = source_bytes(self.root)
            result = self.cli("render_traceability", "--format", "svg", "--output", str(output))
            self.assertEqual(2, result.returncode)
            self.assertEqual("REPORT_CONFLICT", json.loads(result.stdout)["findings"][0]["code"])
            self.assertEqual(before, source_bytes(self.root))

    def test_explicit_output_cannot_write_into_local_git_history(self):
        self.graph()
        seed_git_repo(self.root)
        git_dir = self.root / ".git"
        before = {path.relative_to(git_dir).as_posix(): path.read_bytes()
                  for path in git_dir.rglob("*") if path.is_file()}
        output = git_dir / "task17.svg"
        result = self.cli("render_traceability", "--format", "svg", "--output", str(output))
        self.assertEqual(2, result.returncode)
        self.assertEqual("REPORT_CONFLICT", json.loads(result.stdout)["findings"][0]["code"])
        self.assertFalse(output.exists())
        after = {path.relative_to(git_dir).as_posix(): path.read_bytes()
                 for path in git_dir.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_output_cannot_occupy_declared_missing_source_or_ancestor(self):
        self.graph()
        optional = self.root / "sources.yaml"
        optional.write_text(yaml.safe_dump({"riskSummary": {
            "riskVersion": "candidate-v1", "entries": [],
            "evidenceRefs": [{"reference": "Reserved.svg/missing.txt", "baseline": "sha256:" + "1" * 64}],
        }}), encoding="utf-8")
        self.manifest({"risk": [{"path": "sources.yaml", "baseline": baseline(optional)}],
                       "release": [{"path": "Future.svg", "baseline": "sha256:" + "2" * 64}]})
        for output in ("Reserved.svg", "Reserved.svg/missing.txt", "future.svg"):
            with self.subTest(output=output):
                before = source_bytes(self.root)
                result = self.cli("render_traceability", "--format", "svg", "--output", str(self.root / output))
                self.assertEqual(2, result.returncode)
                self.assertEqual("REPORT_CONFLICT", json.loads(result.stdout)["findings"][0]["code"])
                self.assertEqual(before, source_bytes(self.root))

    def test_output_alias_and_canceled_traversal_do_not_escape_protection(self):
        self.graph()
        target = self.workspace / "alias-target"
        target.mkdir()
        alias = self.workspace / "alias"
        with directory_link(alias, target):
            for output in (alias / "new.svg", alias / ".." / "escaped.svg"):
                result = self.cli("render_traceability", "--format", "svg", "--output", str(output))
                self.assertEqual(2, result.returncode)
                self.assertEqual("REPORT_CONFLICT", json.loads(result.stdout)["findings"][0]["code"])
                self.assertFalse((target / "new.svg").exists())
                self.assertFalse((self.workspace / "escaped.svg").exists())

    def test_missing_output_parent_is_not_created(self):
        self.graph()
        output = self.workspace / "not-created" / "out.svg"
        result = self.cli("render_traceability", "--format", "svg", "--output", str(output))
        self.assertEqual(2, result.returncode)
        self.assertEqual("REPORT_WRITE_ERROR", json.loads(result.stdout)["findings"][0]["code"])
        self.assertFalse(output.parent.exists())

    def test_output_suffix_cannot_claim_foreign_format(self):
        self.graph()
        output = self.workspace / "false.pdf"
        result = self.cli("render_traceability", "--format", "html", "--output", str(output))
        self.assertEqual(2, result.returncode)
        self.assertFalse(output.exists())

    def test_unknown_format_propagates_explicit_error(self):
        self.graph()
        self.assert_error("UNSUPPORTED_FORMAT", lambda: self.trace("jpeg"))
        result = self.cli("render_traceability", "--format", "unknown")
        self.assertEqual(2, result.returncode)
        self.assertEqual("UNSUPPORTED_FORMAT", json.loads(result.stdout)["findings"][0]["code"])

    def test_source_selection_and_baseline_cli_counts_must_match(self):
        self.graph()
        result = self.cli("render_architecture", "--source", "VT-001.md")
        self.assertEqual(2, result.returncode)
        self.assertEqual("INVALID_RENDER_INPUT", json.loads(result.stdout)["findings"][0]["code"])

    def test_cli_architecture_and_presentation_use_selected_source(self):
        inputs = self.architecture(sequence=None)
        pointer = inputs["sources"][0]
        for name in ("render_architecture", "render_presentation"):
            result = self.cli(name, "--format", "html", "--source", pointer["reference"],
                              "--baseline", pointer["baseline"])
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Workbench Alpha", "".join(self.assert_local_html(result.stdout).text))

    def test_cli_stale_model_returns_drift_exit_one_without_output(self):
        self.graph()
        model = self.workspace / "stale.json"
        model.write_text(json.dumps(export_view(self.root, SCOPE)), encoding="utf-8")
        (self.root / "CAP-001.md").write_bytes((self.root / "CAP-001.md").read_bytes() + b"\nChanged detail.\n")
        output = self.workspace / "no-drift.svg"
        result = self.cli("render_traceability", "--format", "svg", "--model-path", str(model), "--output", str(output))
        self.assertEqual(1, result.returncode)
        self.assertEqual("STALE_MODEL_SOURCE", json.loads(result.stdout)["findings"][0]["code"])
        self.assertFalse(output.exists())

    def test_cli_unsupported_sequence_exit_one_has_diagnostics(self):
        inputs = self.architecture(sequence=SEQUENCE + "autonumber\n")
        pointer = inputs["sources"][1]
        result = self.cli("render_architecture", "--format", "html", "--source", pointer["reference"],
                          "--baseline", pointer["baseline"])
        self.assertEqual(1, result.returncode)
        self.assertEqual("unsupported", json.loads(result.stdout)["status"])

    def test_write_io_error_is_typed_not_success(self):
        self.graph()
        module = self.tool("render_traceability")
        output = self.workspace / "io.svg"
        # Injection only at an unsafe-to-reproduce OS open failure; real derivation.
        original = Path.open

        def fail_selected(path, *args, **kwargs):
            if path == output:
                raise OSError("injected local disk failure")
            return original(path, *args, **kwargs)

        with patch.object(Path, "open", fail_selected):
            self.assert_error("REPORT_WRITE_ERROR", lambda: module.write_export(
                self.trace("svg"), str(output), {"root": self.root, "scope": SCOPE}))
        self.assertFalse(output.exists())

    # RENDER-14/15: finite refusal tests, NOT future renderer/page/slide evidence.
    def test_unavailable_pdf_pptx_have_no_fake_content_or_passed_format_gates(self):
        inputs = self.architecture(sequence=None)
        for name in ("render_traceability", "render_architecture", "render_presentation"):
            for format in ("pdf", "pptx"):
                with self.subTest(name=name, format=format):
                    result = self.trace(format) if name == "render_traceability" else self.render(name, inputs, format)
                    self.assertEqual(("unavailable", None, None), (result["status"], result["content"], result["media_type"]))
                    self.assertEqual({"authorization", "dependency", "signature-parser", "nonzero-count",
                                      "source-content", "human-app"}, {g["name"] for g in result["gates"]})
                    self.assertTrue(all(g["status"] == "not-run" for g in result["gates"]))

    def test_unavailable_cli_does_not_create_requested_binary(self):
        inputs = self.architecture(sequence=None)
        pointer = inputs["sources"][0]
        before = source_bytes(self.root)
        for name in ("render_traceability", "render_architecture", "render_presentation"):
            for format in ("pdf", "pptx"):
                output = self.workspace / (name + "." + format)
                args = [] if name == "render_traceability" else [
                    "--source", pointer["reference"], "--baseline", pointer["baseline"]]
                result = self.cli(name, "--format", format, "--output", str(output), *args)
                self.assertEqual(2, result.returncode)
                self.assertEqual("unavailable", json.loads(result.stdout)["status"])
                self.assertFalse(output.exists())
        self.assertEqual(before, source_bytes(self.root))

    def test_trace_source_read_failure_is_not_silent_empty(self):
        self.graph()
        module = self.tool("render_traceability")
        source = self.root / "CAP-001.md"
        original = Path.read_bytes

        def fail_selected(path):
            if path == source:
                raise PermissionError("injected unreadable source")
            return original(path)

        with patch.object(Path, "read_bytes", fail_selected):
            self.assert_error("FILE_READ_ERROR", lambda: module.render_traceability(
                {"root": self.root, "scope": SCOPE}))

    def test_source_mutation_detected_by_rechecking_acquired_bytes(self):
        inputs = self.architecture(sequence=None)
        module = self.tool("render_architecture")
        source = self.root / "architecture/规格 空格.md"
        original = Path.read_bytes
        count = 0

        def changing(path):
            nonlocal count
            raw = original(path)
            if path == source:
                count += 1
                if count > 1:
                    return raw + b"\nchanged during read\n"
            return raw

        with patch.object(Path, "read_bytes", changing):
            self.assert_error("INPUT_CHANGED", lambda: module.render_architecture(inputs, "html"))

    # Self-review regressions: preserve actual source order and finite boundaries.
    def test_source_literal_stays_between_its_original_surrounding_prose(self):
        inputs = self.architecture(sequence=None)
        source = self.artifact("SWAS-002", "architecture-specification",
                              '# SWAS-002 Source ordering\n<a id="ordered"></a>\n## Actual order\n'
                              'BEFORE-SOURCE-TOKEN\n```text\nMIDDLE-LITERAL-TOKEN\n```\nAFTER-SOURCE-TOKEN\n')
        inputs["sources"] = [self.pointer(source)]
        for name in ("render_architecture", "render_presentation"):
            document = Document(self.render(name, inputs)["content"])
            text = "".join(document.text)
            self.assertLess(text.index("BEFORE-SOURCE-TOKEN"), text.index("MIDDLE-LITERAL-TOKEN"))
            self.assertLess(text.index("MIDDLE-LITERAL-TOKEN"), text.index("AFTER-SOURCE-TOKEN"))

    def test_only_literal_source_body_is_not_dropped(self):
        inputs = self.architecture(sequence=None)
        source = self.artifact("SWAS-002", "architecture-specification",
                              '# SWAS-002 Literal body\n```text\nONLY-LITERAL-CONTENT\n```\n')
        inputs["sources"] = [self.pointer(source)]
        for name in ("render_architecture", "render_presentation"):
            result = self.render(name, inputs)
            self.assertEqual(1, result["counts"]["sections"])
            self.assertIn("ONLY-LITERAL-CONTENT", result["content"])

    def test_all_svg_formats_visibly_disclaim_execution_and_approval(self):
        inputs = self.architecture()
        for name in ("render_traceability", "render_architecture", "render_presentation"):
            result = self.trace("svg") if name == "render_traceability" else self.render(name, inputs, "svg")
            root = self.svg(result["content"])
            self.assertIn("not execution, approval", "".join(root.itertext()))

    def test_non_mapping_trace_selector_is_typed_input_error(self):
        for value in (None, [], "model.yaml"):
            self.assert_error("INVALID_RENDER_INPUT", lambda value=value: self.tool(
                "render_traceability").render_traceability(value))

    def test_empty_trace_has_real_single_prefixed_snapshot_digest(self):
        source = self.trace()["source"]
        self.assertRegex(source["baseline"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(".", source["root"])

    def test_duplicate_sources_do_not_double_the_source_content(self):
        inputs = self.architecture(sequence=None)
        inputs["sources"].append(dict(inputs["sources"][0]))
        self.assert_error("DUPLICATE_EVIDENCE", lambda: self.render("render_presentation", inputs))

    def test_explicit_empty_presentation_selection_has_zero_slides(self):
        self.graph()
        result = self.render("render_presentation", {"root": self.root, "scope": SCOPE, "sources": []})
        self.assertEqual(("empty", 0, 0), (result["status"], result["counts"]["sections"], result["counts"]["slides"]))
        self.assertIn("empty", " ".join(result["gaps"]))

    def test_exact_local_git_source_baseline_is_checked_without_checkout(self):
        inputs = self.architecture(sequence=None)
        seed_git_repo(self.root)
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Self-owned render source fixture")
        exact = git(self.root, "rev-parse", "HEAD")
        inputs["sources"][0]["baseline"] = exact
        before = source_bytes(self.root)
        result = self.render("render_architecture", inputs)
        self.assertIn(exact, result["content"])
        self.assertEqual(before, source_bytes(self.root))
        source = self.root / "architecture/规格 空格.md"
        source.write_bytes(source.read_bytes() + b"\nChanged candidate content.\n")
        self.assert_error("BASE_MISMATCH", lambda: self.render("render_architecture", inputs))

    def test_verified_source_summary_keeps_actual_parameterized_fields(self):
        self.graph()
        source = self.root / "supplied-summary.yaml"
        source.write_text(yaml.safe_dump({"srSummary": {
            "srVersion": "self-owned-candidate-7",
            "entries": [{"reqId": SCOPE + "/REQ-001#req-001-ac-01",
                         "srIds": [SCOPE + "/SR-001#sr-001-ac-01"],
                         "notes": "Owner has not selected runtime infrastructure"}],
        }}, allow_unicode=True), encoding="utf-8")
        self.manifest({"requirements": [{"path": "supplied-summary.yaml", "baseline": baseline(source)}]})
        inputs = {"root": self.root, "scope": SCOPE, "sources": [self.pointer(source, "#srSummary")]}
        result = self.render("render_presentation", inputs)
        document = Document(result["content"])
        self.assertIn("self-owned-candidate-7", "".join(document.text))
        self.assertIn("Owner has not selected runtime infrastructure", "".join(document.text))
        self.assertEqual(["srSummary"], [a["data-section"] for _, a in document.tags if "data-section" in a])

    def test_report_source_uses_real_reconstruction_not_execution_status_copy(self):
        from collect_implementation_report import build_report
        exact = seed_implementation_fixture(self.root)
        report = build_report(self.root, exact, [], scope="sample/CTX-001")
        source = self.root / "implementation-report.json"
        source.write_text(json.dumps(report), encoding="utf-8")
        (self.root / "model-sources.yaml").write_text(yaml.safe_dump({
            "schemaVersion": 1, "scopes": {"sample/CTX-001": {
                "verification": [{"path": source.name, "baseline": baseline(source)}]}}}), encoding="utf-8")
        inputs = {"root": self.root, "scope": "sample/CTX-001", "sources": [self.pointer(source)]}
        before = source_bytes(self.root)
        result = self.render("render_architecture", inputs)
        text = "".join(Document(result["content"]).text)
        self.assertEqual(1, result["counts"]["sections"])
        self.assertIn("original records", text)
        self.assertNotIn('"execution"', text)
        self.assertNotIn('"applicability"', text)
        self.assertEqual(before, source_bytes(self.root))
        report["entries"][0]["execution"] = {"status": "pass", "evidenceRefs": []}
        source.write_text(json.dumps(report), encoding="utf-8")
        (self.root / "model-sources.yaml").write_text(yaml.safe_dump({
            "schemaVersion": 1, "scopes": {"sample/CTX-001": {
                "verification": [{"path": source.name, "baseline": baseline(source)}]}}}), encoding="utf-8")
        inputs["sources"] = [self.pointer(source)]
        self.assert_error("INVALID_OPTIONAL_SOURCE", lambda: self.render("render_architecture", inputs))

    def test_empty_message_other_arrows_and_extra_fence_options_are_unsupported(self):
        self.graph()
        for content, info in (
            ("sequenceDiagram\nparticipant A\nparticipant B\nA->>B: \n", "mermaid"),
            ("sequenceDiagram\nparticipant A\nparticipant B\nA-)B: event\n", "mermaid"),
            ("sequenceDiagram\nparticipant A\nparticipant B\nA->>B: event\n", "mermaid unsafe-option"),
        ):
            source = self.artifact("SEQ-002", "sequence-diagram",
                                  '# SEQ-002 Finite subset\n<a id="diagram"></a>\n## Actual\n```'
                                  + info + "\n" + content + '```\n')
            result = self.render("render_architecture", {"root": self.root, "scope": SCOPE,
                                                         "sources": [self.pointer(source)]})
            self.assertEqual(("unsupported", 0), (result["status"], result["counts"]["messages"]))

    def test_multiple_source_owned_sequence_fences_are_explicitly_unsupported(self):
        self.graph()
        source = self.artifact("SEQ-002", "sequence-diagram",
                              '# SEQ-002 Two diagrams\n<a id="diagram"></a>\n## Actual\n'
                              '```mermaid\n' + SEQUENCE + '```\n```mermaid\n' + SEQUENCE + '```\n')
        result = self.render("render_architecture", {"root": self.root, "scope": SCOPE,
                                                     "sources": [self.pointer(source)]})
        self.assertEqual(("unsupported", 0), (result["status"], result["counts"]["diagrams"]))

    def test_xml_illegal_source_text_is_error_not_invalid_document_success(self):
        inputs = self.architecture(sequence=None)
        source = self.root / "architecture/规格 空格.md"
        source.write_bytes(source.read_bytes() + b"\nInvalid XML scalar: \x01\n")
        inputs["sources"] = [self.pointer(source)]
        for name in ("render_architecture", "render_presentation"):
            self.assert_error("INVALID_RENDER_TEXT", lambda name=name: self.render(name, inputs, "svg"))

    def test_output_declarations_with_invalid_locations_refuse_new_files(self):
        self.graph()
        optional = self.root / "sources.yaml"
        optional.write_text(yaml.safe_dump({"riskSummary": {
            "riskVersion": "candidate", "entries": [],
            "evidenceRefs": [{"reference": "../not-a-permitted-input", "baseline": "sha256:" + "1" * 64}],
        }}), encoding="utf-8")
        self.manifest({"risk": [{"path": "sources.yaml", "baseline": baseline(optional)}]})
        output = self.workspace / "no-isolation.svg"
        result = self.cli("render_traceability", "--format", "svg", "--output", str(output))
        self.assertEqual(2, result.returncode)
        self.assertEqual("REPORT_CONFLICT", json.loads(result.stdout)["findings"][0]["code"])
        self.assertFalse(output.exists())

    def test_rounded_graph_routes_do_not_cross_other_straight_segments(self):
        self.graph()
        root = self.svg(self.trace("svg")["content"])
        segments = []
        for node in root.iter():
            if "data-edge" not in node.attrib:
                continue
            tokens = iter(re.findall(r"[MHVQ]|-?\d+(?:\.\d+)?", node.attrib["d"]))
            x = y = 0.0
            for command in tokens:
                if command == "M":
                    x, y = float(next(tokens)), float(next(tokens))
                elif command == "H":
                    end = float(next(tokens))
                    segments.append((node.attrib["data-edge"], x, y, end, y))
                    x = end
                elif command == "V":
                    end = float(next(tokens))
                    segments.append((node.attrib["data-edge"], x, y, x, end))
                    y = end
                elif command == "Q":
                    next(tokens), next(tokens)  # Control point, not a straight segment.
                    x, y = float(next(tokens)), float(next(tokens))
                else:
                    self.fail("unexpected local graph path command")
        for owner, x1, y1, x2, y2 in segments:
            if y1 != y2:
                continue
            for other, vx1, vy1, vx2, vy2 in segments:
                if owner == other or vx1 != vx2:
                    continue
                self.assertFalse(min(x1, x2) < vx1 < max(x1, x2) and min(vy1, vy2) < y1 < max(vy1, vy2),
                                 "A real graph connector crosses another without a visible bridge")


if __name__ == "__main__":
    unittest.main()
