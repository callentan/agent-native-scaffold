# Sourced local document exports

These tools only generate rebuildable derived documents; they do not take over the domain,
architecture decisions, VT results, or approvals.
Use Python 3.11+ and the [existing maintenance environment](development.md#maintenance-tools);
local JSON, SVG, and HTML use only the stdlib, with no browser, CDN, remote fonts, or source commands.
The [rendering manifest](../.github/utilities/requirements-rendering.txt) does not select a PDF/PPTX engine.

<a id="inputs"></a>
## Inputs and return values

Import the three bound functions from the modules of the same name; the API does not write files
or change the cwd:

```python
render_traceability(view)
render_architecture(inputs, format)
render_presentation(inputs, format)
```

`view` is a plain Python mapping with only the required `root` and `scope`, plus optional `format`
(default `json`) and `model_path`. `inputs` has the same explicit `root`, `scope`, and optional
`model_path`, plus a required `sources` list. It is not another file manifest.
Each source reuses the existing evidence pointer: `{"reference": "architecture/SWAS-001.md",
"baseline": "sha256:<actual raw-byte digest>"}`; the reference may carry a real explicit anchor,
and the baseline may also be a readable full local Git commit/blob. Unknown fields, duplicate
selections, and invalid versions, paths, references, or mismatched baselines are not empty data.

Every call reads the real inventory of the explicit root and reuses the parser, the nine-view
derivation, source selection, and baseline checks. `model_path` is only an existing model to be
checked: it is recomputed with `check_model`, and `STALE_MODEL_SOURCE` / `MODEL_MISMATCH` block
rendering; schema-valid YAML is not trusted. A model dict detached from the root is not accepted
as a verified fact. There is no public "arbitrary data is verified" projection shortcut, and
sources, execution, or approval are not inferred from file names, extensions, the cwd, or `available`.

Markdown sources for architecture/presentation must be real formal artifacts in the inventory;
the source ID, path, raw baseline, line numbers, and actual sections are kept. JSON/YAML sources
must be sources that the nine views have already checked, and each input `(reference, baseline)`
must exactly match one entry in the current nine-view `evidenceRefs`; another fragment of the same
file, or a whole-file reference, cannot gain authorization through a selected fragment.
An arbitrary mapping is not treated as a SWAS. Implementation reports are checked only through the
existing report adapter, with navigation kept; their execution/applicability entries are not
reinterpreted as results of this run. References grant no execution or write-back permission.
Structured projections serialize only JSON-representable values; native values such as `date` or
YAML `!!binary` are not implicitly converted to strings: they return `INVALID_OPTIONAL_SOURCE`
and keep the explicit source error.

Each function returns a plain dict that always has:

| Field | Meaning |
|---|---|
| `status` | `rendered`, `partial`, `empty`, `unsupported`, or `unavailable`; none of these is a business result |
| `format` / `media_type` | The actual format and MIME type; MIME is null when unavailable |
| `content` | The complete UTF-8 text content; null when unavailable, and no fake binary is returned |
| `counts` | The actual numbers of `nodes/edges/sections/diagrams/messages/slides`; 0 for any kind that is absent |
| `source` | The real derived source identity of the selected scope; an empty trace uses the actual snapshot identity of the inventory |
| `gaps` | Actual source, completeness, and limited-syntax gaps; risk/approval is not computed from them |
| `gates` | Empty for local formats; for PDF/PPTX, lists the authorization, dependency, parsing, page/slide count, and content checks that have not been run |

Input/source/format/I/O errors raise the existing `ArtifactInputError(code, path, line, message)`.
The API does not swallow errors, install anything, or send data. Each file in the read set is read
only once; this is not a file-system transaction or an OS sandbox, so do not modify sources during rendering.

<a id="traceability"></a>
## Relationship graph

trace supports `json`, `svg`, and `html`. The JSON content is the actual relation projection,
containing `status`, `scope`, `source`, `nodes`, `edges`, nine `views`, and `gaps`.
A node `key` is the full `scope/id` and keeps the path, baseline, identity line, and full anchor reference.
An edge keeps the `source/target` node keys, `sourceRef/targetRef`, `relation`, and the original
declaration path/line; targets additionally keep criterion/testId.

- `upstream` is **declarer → the source it depends on**, not a reversed message flow;
  targets is **the verifying/declaring artifact's criterion → the verified target**.
- All owners in the selected scope are kept, including isolated nodes; the cross-scope dependency
  closure is included along actual relations, and identical short IDs are not merged. Cycles are
  traversed only once, and no edge is lost.
- When there are no formal artifacts and the inventory is valid, trace is explicitly `empty`, with
  0 nodes and 0 edges. In that case the scope only records the request and does not confirm that
  it exists; this is not a successfully exported business model. An empty inventory cannot satisfy
  an explicit `model_path` check or the primary-scope requirement of architecture/presentation.
- JSON, SVG, and HTML all carry the actual source/gaps; arrows in the graph do not imply a transport.

<a id="architecture"></a>
## Architecture, SEQ, and presentation

architecture supports `html` and `svg`. The output keeps the nine views' original
`state/artifactRefs/evidenceRefs/gaps` and the actual sections of the selected business, logical,
runtime, and deployment sources. Business/logical/runtime navigation leads back to
requirements/architecture/sequences respectively. Only an actually selected `deployment` section
provides deployment content; otherwise the source is explicitly reported as missing, and no
deployment topology is inferred from ABBs. SWAS `perspectives` are still shown as written; the tool
does not fill in language, containers, classification, risk acceptance, lifecycle, or release on the
author's behalf. When ABB/risk/deployment input is missing, a document with gaps can still be output,
but it is not called a complete SWAS.

Within the SEQ section with the explicit `diagram` anchor, only **one closed** Mermaid fence
recognized by the shared scanner is accepted, with no additional fence options; multiple diagrams
are explicitly unsupported and are not concatenated. The limited subset is:

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

An unsupported diagram is never drawn as a "complete" sequence; the document keeps the source and the
specific line/syntax gaps, status is `unsupported`, and the CLI exits 1. Comments, outer literals,
adjacent sections, and unclosed fences cannot be borrowed to produce messages. Success/rejection/error
boundaries come from the original `paths` section and the actual diagram; the tool does not fill them in.
There is no promise of full Mermaid compatibility.

presentation is a required parameterized capability that supports `html` and `svg`; it is not a fixed
management deck. The real sections of each selected source produce corresponding slides; long
paragraphs are paginated without deleting text, sources, or gaps. The source-status navigation of all
nine views and the actual SEQ drawings are kept. Two different source sets must produce their own
titles, sections, content, and source IDs, without sharing a hard-coded business narrative.
The SVG is a single parsable vertical multi-page canvas and the HTML is a printable continuous slide
document; neither counts as acceptance of PPTX, PDF, or a native presentation application.

The visual convention is a static, offline, light-colored document that uses system
serif/sans/monospace fallbacks and does not establish a brand profile. Complete identity and content
take priority: long graphs/documents scroll, and cycles or isolated owners are not cut off.
SVG uses accessible title/desc, complete content text, and the actual direction; it requests no external resources.
Source HTML, scripts, URLs, and commands appear only as safely encoded text, and output links are only internal navigation.

<a id="cli"></a>
## CLI, writes, and error boundaries

With the repository root as the cwd, run each script with the actual project interpreter (Windows example):

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_traceability.py --root . --scope sample/CTX-001 --format svg
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_architecture.py --root . --scope sample/CTX-001 --format html --source architecture/SWAS-001.md --baseline sha256:<actual-digest>
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_presentation.py --root . --scope sample/CTX-001 --format html --source architecture/SWAS-001.md --baseline sha256:<actual-digest>
```

Replace the example scope/sources/baselines; each `--source` has a `--baseline` in the matching position.
The architecture/presentation CLI without a source explicitly passes an empty selection and outputs
only source/gap navigation, without fabricating content.
You can pass `--model-path` to check an existing model. By default only the actual text is written to stdout;
on failure or unavailability, stdout carries a structured JSON diagnostic. There is no default write or directory creation.

`--output` accepts only a new local file explicitly given for this run; its suffix must match
`--format`, its parent directory must already exist, and it is created with exclusive create. It must
not occupy any existing file (including an empty file) or directory, source/report/history,
manifest/resolved reference, or unselected/missing declared location, or any ancestor/descendant path
of these; the path must not enter `.git` metadata/history even if the target file does not exist yet,
and the file name must not contain `:`. Links in the path are resolved in the host's normal way before
comparison with the locations above, and the path must also stay isolated after case folding/normalization.
When invalid declarations make isolation impossible to establish, the write is refused. A failed write
may leave a partial new file, which is not automatically cleaned up, overwritten, or moved to another
path; the next run still refuses to overwrite it.

| Situation | CLI exit |
|---|---|
| Real local format `rendered/partial/empty` | 0; having content does not mean a business pass |
| Persisted model drift, or the selected SEQ is unsupported | 1 |
| Input, source, format, or I/O error, or PDF/PPTX unavailable | 2 |

<a id="format-gates"></a>
## Separate format gates not yet run

PDF and PPTX requests return `unavailable` with `content: null`; no corresponding output is created,
and global packages are not probed to infer authorization. No engine, version, template, package,
container, or service has been selected/approved yet. In the future, separate authorization must be
obtained for selection, installation, and input processing, and the actual dependencies must be locked
before real signature, parser, non-zero page/slide count, complete source content, and human/App checks
are run. A file name alone, a `%PDF`/`PK` prefix, or a zero-page file does not qualify.
Limited refusal regression is not evidence of success for these formats.
Local HTML/SVG does not close the full ENH-17 or overall parity.
