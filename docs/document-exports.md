# Sourced local document exports

These tools only generate rebuildable derived documents; they do not take over the domain, architecture decisions, VT results, or approvals.
Use Python 3.11+ and the [maintenance environment](development.md#maintenance-tools). Local JSON, SVG, and HTML use only the stdlib: no browser, CDN, remote fonts, or commands from sources.
The [rendering manifest](../.github/utilities/requirements-rendering.txt) does not select a PDF/PPTX engine.

<a id="inputs"></a>
## Inputs and return values

Import each function from the same-named module; the API writes no files and does not change the cwd:

```python
render_traceability(view)
render_architecture(inputs, format)
render_presentation(inputs, format)
```

`view` is a plain mapping with required `root` and `scope`, plus optional `format` (default `json`) and `model_path`. `inputs` has the same explicit `root`, `scope`, and optional `model_path`, plus a required `sources` list; it is not another file manifest.
Each source reuses the existing evidence pointer `{"reference": "architecture/SWAS-001.md", "baseline": "sha256:<actual raw-byte digest>"}`; the reference may carry a real explicit anchor, and the baseline may be a readable full local Git commit/blob. Unknown fields, duplicate selections, and invalid versions, paths, references, or mismatched baselines are errors, not empty data.

Every call reads the real inventory of the explicit root and reuses the parser, nine-view derivation, source selection, and baseline checks. `model_path` is only an existing model to check: it is recomputed with `check_model`, and `STALE_MODEL_SOURCE` / `MODEL_MISMATCH` block rendering; schema-valid YAML is not trusted. A model dict detached from the root is not accepted as a verified fact. There is no public "arbitrary data is verified" shortcut; sources, execution, or approval are never inferred from file names, extensions, the cwd, or `available`.

Markdown sources for architecture/presentation must be real formal artifacts in the inventory; source ID, path, raw baseline, line numbers, and actual sections are kept. JSON/YAML sources must already be checked by the nine views, and each input `(reference, baseline)` must exactly match one entry in the current nine-view `evidenceRefs`; another fragment of the same file or a whole-file reference cannot gain authorization through a selected fragment. An arbitrary mapping is not treated as a SWAS. Implementation reports are checked only through the existing report adapter, with navigation kept; their execution/applicability entries are not reinterpreted as results of this run. References grant no execution or write-back permission. Projections serialize only JSON-representable values; native values such as `date` or YAML `!!binary` are not converted to strings implicitly: they return `INVALID_OPTIONAL_SOURCE` and keep the explicit source error.

Each function returns a plain dict that always has:

| Field | Meaning |
|---|---|
| `status` | `rendered`, `partial`, `empty`, `unsupported`, or `unavailable`; none of these is a business result |
| `format` / `media_type` | The actual format and MIME type; MIME is null when unavailable |
| `content` | Complete UTF-8 text; null when unavailable (no fake binary) |
| `counts` | Actual `nodes/edges/sections/diagrams/messages/slides`; 0 for absent kinds |
| `source` | Real derived source identity of the selected scope; an empty trace uses the actual inventory snapshot identity |
| `gaps` | Actual source, completeness, and limited-syntax gaps; risk/approval is not computed from them |
| `gates` | Empty for local formats; for PDF/PPTX, lists authorization, dependency, parsing, page/slide count, and content checks not yet run |

Input, source, format, and I/O errors raise the existing `ArtifactInputError(code, path, line, message)`. The API does not swallow errors, install anything, or send data. Each file is read only once; this is not a file-system transaction or an OS sandbox, so do not modify sources during rendering.

<a id="traceability"></a>
## Relationship graph

trace supports `json`, `svg`, and `html`. The JSON is the actual relation projection with `status`, `scope`, `source`, `nodes`, `edges`, nine `views`, and `gaps`.
A node `key` is the full `scope/id` and keeps path, baseline, identity line, and full anchor reference. An edge keeps `source/target` node keys, `sourceRef/targetRef`, `relation`, and the original declaration path/line; targets also keep criterion/testId.

- `upstream` points **from the declarer to the source it depends on**, not a reversed message flow; `targets` points **from the verifying or declaring criterion to the verified target**.
- All owners in the selected scope are kept, including isolated nodes; cross-scope dependency closure follows actual relations; identical short IDs are not merged; cycles are traversed once with no edge lost.
- With no formal artifacts and a valid inventory, trace is explicitly `empty` (0 nodes, 0 edges). The scope only records the request and does not confirm that it exists; this is not a successfully exported business model. An empty inventory cannot satisfy an explicit `model_path` check or the primary-scope requirement of architecture/presentation.
- JSON, SVG, and HTML all carry the actual source/gaps; arrows do not imply a transport.

<a id="architecture"></a>
## Architecture, SEQ, and presentation

architecture supports `html` and `svg`. The output keeps the nine views' original `state/artifactRefs/evidenceRefs/gaps` and the actual sections of the selected business, logical, runtime, and deployment sources. Business/logical/runtime navigation leads back to requirements/architecture/sequences respectively. Only an actually selected `deployment` section provides deployment content; otherwise the source is explicitly reported as missing, and no deployment topology is inferred from ABBs. SWAS `perspectives` are shown as written; the tool does not fill in language, containers, classification, risk acceptance, lifecycle, or release on the author's behalf. With ABB/risk/deployment input missing, a document with gaps can be output but is not called a complete SWAS.

In the SEQ section with the explicit `diagram` anchor, only **one closed** Mermaid fence recognized by the shared scanner is accepted, with no extra fence options; multiple diagrams are explicitly unsupported and not concatenated. The subset is:

- `sequenceDiagram`; `participant ID [as Label]` and `actor ID [as Label]`, where ID consists of
  ASCII letters, digits, and underscores and starts with a letter or underscore.
- `ID->>ID: Text` and `ID-->>ID: Text` with both ends explicitly declared, including self-messages.
  The original arrow tokens and solid/dashed lines are kept and are not reinterpreted as
  synchronous/asynchronous transport guarantees.
- Non-nested `alt Text` / `else Text` / `end`, as well as `opt Text` and `loop Text` / `end`;
  each region has at least one source message, and all branches, labels, and messages keep the source order.
- Blank lines and plain full-line `%%` comments are not drawn; init directives, implicit participants,
  activations, notes, nested fragments, other arrows/statements, empty messages, unclosed fragments,
  or zero messages are all explicitly unsupported.

An unsupported diagram is never drawn as a "complete" sequence: the document keeps the source and specific line/syntax gaps, status is `unsupported`, and the CLI exits 1. Comments, literal text outside the fence, adjacent sections, and unclosed fences cannot produce messages. Success/rejection/error boundaries come from the original `paths` section and the actual diagram; the tool does not fill them in. No full Mermaid compatibility is promised.

presentation is a required parameterized capability supporting `html` and `svg`; it is not a fixed management deck. The real sections of each selected source produce corresponding slides; long paragraphs are paginated without deleting text, sources, or gaps. Source-status navigation for all nine views and the actual SEQ drawings are kept. Two source sets produce their own titles, sections, content, and source IDs, with no shared hard-coded business narrative. The SVG is a single parsable vertical multi-page canvas and the HTML a printable continuous slide document; neither counts as acceptance of PPTX, PDF, or a native presentation application.

The visual convention is a static, offline, light-colored document with system serif/sans/monospace fallbacks and no brand profile. Complete identity and content take priority: long graphs and documents scroll, and cycles or isolated owners are not cut off. SVG uses accessible title/desc, complete content text, and the actual direction; it requests no external resources. Source HTML, scripts, URLs, and commands appear only as safely encoded text; output links are internal navigation only.

<a id="cli"></a>
## CLI, writes, and error boundaries

With the repository root as the cwd, run each script with the actual project interpreter (Windows example):

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_traceability.py --root . --scope sample/CTX-001 --format svg
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_architecture.py --root . --scope sample/CTX-001 --format html --source architecture/SWAS-001.md --baseline sha256:<actual-digest>
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_presentation.py --root . --scope sample/CTX-001 --format html --source architecture/SWAS-001.md --baseline sha256:<actual-digest>
```

Replace the example scope, sources, and baselines; each `--source` takes a matching `--baseline`. Architecture/presentation without a source passes an explicit empty selection and outputs only source/gap navigation, with no fabricated content.
Pass `--model-path` to check an existing model. By default only the actual text goes to stdout; on failure or unavailability, stdout carries a structured JSON diagnostic. No default write or directory creation.

`--output` accepts only a new local file explicitly given for this run: its suffix must match `--format`, its parent directory must already exist, and it is created with exclusive create. It must not occupy any existing file (including an empty one) or directory, source/report/history, manifest/resolved reference, or unselected/missing declared location, or any ancestor or descendant of these. It must not enter `.git` metadata/history even if the target does not yet exist, and its file name must not contain `:`. Links are resolved in the host's normal way before comparison, and the path must stay isolated after case folding and normalization. If invalid declarations make isolation impossible to establish, the write is refused. A failed write may leave a partial new file; it is not cleaned up, overwritten, or moved, and the next run still refuses to overwrite it.

| Situation | CLI exit |
|---|---|
| Real local format `rendered/partial/empty` | 0; having content does not mean a business pass |
| Persisted model drift, or the selected SEQ is unsupported | 1 |
| Input, source, format, or I/O error, or PDF/PPTX unavailable | 2 |

<a id="format-gates"></a>
## Separate format gates not yet run

PDF and PPTX requests return `unavailable` with `content: null`; no output is created, and global packages are not probed to infer authorization. No engine, version, template, package, container, or service has been selected or approved. Future work needs separate authorization for selection, installation, and input processing, and dependencies must be locked before the real signature, parser, non-zero page/slide count, complete source content, and human/App checks run. A file name alone, a `%PDF`/`PK` prefix, or a zero-page file does not qualify. The limited refusal regression is not evidence of success for these formats. Local HTML/SVG does not close the full ENH-17 or overall parity.
