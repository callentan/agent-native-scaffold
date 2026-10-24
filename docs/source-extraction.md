# Local source candidates and transparent scoring

These optional tools read only local files explicitly selected for this run and return candidates; they do not write formal domain facts.
Users check read authorization first; a readable file is not permission to process real private documents or send material.
The [reverse-engineering method](../.github/skills/reverse-engineer-domain/SKILL.md) remains responsible for returning to the sources,
comparing contradictory statements, requesting clarification, and later authorized drafting. Scoring cannot confirm business rules, authenticate speakers, or approve candidates.

The tools use the [maintenance environment](development.md#maintenance-tools) and need no new media packages.
The [media manifest](../.github/utilities/requirements-media.txt) contains only notes; no DOCX package, audio service, model, or SDK is selected, so do not install guessed dependencies.

<a id="interfaces"></a>
## API and source identity

Import these narrow interfaces from `.github/utilities/`; they do not scan the repository, execute content, or follow links:

```python
extract_candidates(source: str | os.PathLike[str], kind: str) -> dict
score_candidates(items: list[dict]) -> list[dict]
```

`source` must be an explicit absolute path to a local regular file. URLs, UNC paths, ambiguous drive-relative paths, and alternate streams are rejected. Links in paths resolve as the host normally resolves them (for example, macOS `/tmp`); this is not an OS sandbox and gives no protection against malicious concurrent replacement. The source identity is **the bytes actually read in this run**, not an inferred Git commit or formal artifact identity. The API does not write files or change the cwd.

Extraction returns an envelope whose `candidates` field is the candidate list; it keeps a real read identity even for empty input. These fixed fields are outside the formal artifact schema and add no formal kind:

| Field | Meaning |
|---|---|
| `status` | `extracted` or `empty`; not a business pass/approval |
| `source` | `path`: actual absolute local path; `kind`: explicit format choice; `baseline`: `sha256:` plus the 64-character lowercase hex digest of the raw bytes; `byte_count`: actual bytes read |
| `unit_count` | Text/Markdown/transcripts: raw physical lines per Python `str.splitlines()`; DOCX: all paragraphs in the supported layout, including empty and cell paragraphs |
| `candidate_count` | The actual list length, not an acceptance count |
| `candidates` | Original file order; not deduplicated by text or reordered by time |

Each candidate has these fixed fields:

| Field | Meaning |
|---|---|
| `candidate_id` | Local sequence number for this run, from `candidate-0001`; sources may reuse numbers, so it is not a REQ/RULE or canonical ID |
| `kind` | Candidate type: `rule`, `capability`, `use-case`, `term`, or `statement` |
| `nature` | `observed`: explicit label; `inferred`: lexical classification of unlabeled text; `uncertain`: proposal/tentative wording. None of them means the fact is confirmed |
| `text` | The **complete** normalized text of the selected unit; never a substring or without qualifiers (see normalization) |
| `fragment` | Raw line, raw transcript JSON line, or DOCX paragraph text; not a stand-in for a missing raw interview or XML line number |
| `source`, `location` | Same actual byte identity; 1-based format coordinates (below) |
| `uncertainty` | Detected proposal words and reason; empty when none are found, which does not mean agreement with other sources |
| `extraction_reason` | The classification basis: explicit label or lexical inference |
| `clarification` | Asks the actual owner to confirm scope and check contradictory sources; invents no approver or decision number |
| `markdown_context` | Newly extracted Markdown candidates carry `{"in_comment": false}` or `true`: whether the raw line was already inside an HTML comment before the scanner. Not visible content or an authentication result; other formats must not carry this field |

Supported explicit labels are `Rule:`, `Capability:`, `Use case:` / `Use-case:`, and
`Term:`; matching is case-insensitive.
Unlabeled text is inferred as a rule only from `must/shall/never/required/cannot`,
and as a capability only from `can/allows/supports`; everything else is a statement.
This is not a complete natural-language recognizer and cannot prove necessity or that the domain type is correct.
`maybe/should/proposed/perhaps/unconfirmed` are uncertainty markers that override observed/inferred.
Contradictory sources may both lack these words; both are still kept and compared by the method.
The tool does not automatically detect all business contradictions, choose a prevailing rule, or record a supersedes/confirmed status.

<a id="formats"></a>
## Local formats and exact locations

| `kind` / extension | Reading and candidate unit | `location` |
|---|---|---|
| `text` / `.txt` | UTF-8; one candidate per non-empty line; command-like text is just text | `line`, `paragraph` |
| `markdown` / `.md` | UTF-8; reuses the existing Markdown line scanner to skip code, comments, and ATX headings; visible non-empty lines become candidates; frontmatter and formal identity are not parsed separately | `line`, `paragraph` |
| `transcript` / `.txt` | Strict JSON Lines as defined below; each non-empty line is one complete turn | `line`, `turn`, `speaker`, `timestamp` |
| `docx` / `.docx` | The bounded OOXML subset defined below; one candidate per non-empty paragraph, including table cells | `part`, `block`, `paragraph`; cells also have `table`, `row`, `cell`, `cell_paragraph` |

UTF-8 may have a BOM; Unicode, paths with spaces, and CRLF are supported. The byte digest keeps BOM and line endings;
text in `fragment` excludes the line terminator. A text paragraph is a group of consecutive non-empty raw lines separated by blank lines **before filtering**,
so groups containing headings, comments, or fences still count; these are not renderer-level paragraphs.
Markdown `text` may strip HTML comments while `fragment` keeps the raw line; scoring uses the same state machine and explicit pre-line comment context to check the complete visible unit. The tool is not a complete Markdown renderer and does not automatically turn tables, headings, or frontmatter into formal artifacts.

### Complete source-unit normalization and Markdown context

- plain text, DOCX: only a leading/trailing `strip()` of the whole `fragment`; no truncation, whitespace collapsing, case or punctuation changes, or removal of restrictive suffixes. A DOCX paragraph may contain tabs or line breaks and is still one complete unit.
- transcript: strictly parse the whole raw JSON line and take the complete `text.strip()`; also check the supplied speaker/time; never take an arbitrary substring.
- Markdown: the shared scanner reads the whole raw line and applies the comment/code/fence rules; after excluding headings, code, and empty visible lines, only a leading/trailing `strip()` is applied. Extraction keeps the whole-file `markdown_context.in_comment`; scoring enters the **same** scanner in that declared state, with no second parser for standalone fragments and no caller-supplied duplicate visible text.

For example, given the raw lines `<!--` and `    --> Rule: Members <!--x--> must keep receipts.`, the second line keeps its raw fragment, raw line/group, and `{"in_comment": true}`;
its complete text is `Rule: Members  must keep receipts.`. The four leading spaces of the standalone fragment are not mistaken for code,
and a visible Maybe or restrictive suffix cannot be removed to raise the score.

`markdown_context` allows only a single genuine bool `in_comment`; visible-text overrides, unknown keys, and numeric stand-ins for bools are not allowed; line 1 cannot inherit a comment from a previous line.
Older Markdown candidates that lack this field default to the non-comment entry state; omitted context cannot be guessed.
This is a limited **source-context declaration**, not a fact re-authenticated from the original file. The tool does not open the original or authenticate its hash, the speaker, or unsupplied prefixes; it only proves that the fragment, context, complete text, and classification are internally consistent. Do not present this check as a guarantee of authenticity or approval.

`kind`, `nature`, and all `uncertainty` markers must match the reclassification of the complete normalized unit, including the order and repetition of markers.
Truncating text, removing `maybe`/`should`/`unconfirmed`, or overriding nature/markers to disguise a different candidate is not allowed.
Owner business judgments are still recorded through the shared method; tool observations are not edited in place of clarification; raw fragments and coordinates are not rewritten by normalization.

### Explicit transcript format

Each non-empty physical line must be a JSON object with exactly three non-empty string fields and no duplicate/extra keys:

```json
{"speaker":"A","timestamp":"00:00:02.125","text":"Rule: Members must keep receipts."}
{"speaker":"B","timestamp":"00:00:01.000","text":"Maybe that policy should change."}
```

Timestamps are fixed as `HH:MM:SS.mmm` (two-digit hours, minutes/seconds 00–59, three-digit milliseconds).
Input order, speakers, and time strings are preserved; names are not authenticated, real clock times are not validated, and chronological order is not inferred.
`text` is the JSON-decoded text and `fragment` is the raw JSON line; escaping does not change the source baseline.
Blank lines add no turn; invalid JSON, non-finite numbers, missing fields, empty text, invalid Unicode/control characters, or any bad turn fails the entire read with no partial success.

### Bounded stdlib DOCX

The implementation uses the selected standard library `zipfile` and XML, calls no converter, and adds no parser package. It reads the actual ZIP container; renamed text files are not treated as documents.
Currently only three required OPC parts are accepted:
`[Content_Types].xml`, `_rels/.rels`, and `word/document.xml`,
plus optional empty `word/` and `_rels/` directory entries. The content type must be a macro-free DOCX document;
the root relationship must be the fixed internal main-document relationship, which is validated and never followed.

Supported: transitional WordprocessingML `document/body`, plain `p/r/t`, `tab/br/cr` within runs, a trailing empty `sectPr`, and rectangular `tbl/tr/tc` tables.
Tables may have an empty `tblPr`, a simple `tblGrid/gridCol`, and a `tcPr` containing only `tcW`.
With a grid, all rows are checked against its column count; without one, against the first row's actual cell count; any wider or narrower later row is explicitly rejected and is not a supported rectangular subset.
Run concatenation order, XML-decoded text, tabs, and line breaks are preserved; no spaces, pages, or audio times are added.
`block` is the position within the body; `paragraph` counts all paragraphs in document order; `cell_paragraph` is the position within that cell; other coordinates count in document/table order.
Coordinates are not page numbers or XML line numbers; the source baseline is still the byte digest of the entire ZIP.

**Unsupported layouts are explicitly rejected, with no partial success:** extra parts (including common styles/settings,
properties, headers/footers, footnotes, images, macros, and additional relationships), Strict OOXML, non-UTF-8 XML, merged/nested tables, style properties, fields, hyperlinks, revisions,
content controls, embedded objects, and other body layouts. Ordinary office documents may contain these; this narrow adapter does not justify claiming that arbitrary DOCX files are fully extracted.
Format extensions and input authorization must be decided separately.

Nothing is unpacked to disk, external entities are not resolved, relationship targets are not accessed, and document content is not executed.
Rejected: ZIP traversal/absolute paths/backslashes/NUL/duplicate names/type aliases, encrypted ZIPs, DTD/entity declarations, corrupt XML/CRC, missing required parts, and unsupported compression/layouts. Non-body content such as XML comments does not become a business candidate, but is still covered by the identity of the entire input bytes.

| Resource boundary | Fixed limit |
|---|---|
| Single source or CLI scoring JSON | 4 MiB raw input; exceeding it fails, never truncates to a success |
| Text/Markdown/transcript lines | 10,000 (including empty/excluded lines), checked before candidate expansion |
| Single scoring run | 10,000 candidates; API and CLI reject larger sets |
| ZIP entries | 64, including directory entries |
| Single ZIP part / total uncompressed bytes | 1 MiB / 8 MiB |
| ZIP expansion ratio | Each part at most `100 × max(compressed_size, 1)` |
| Each XML part | Depth at most 32 and at most 10,000 elements, checked during parsing |

<a id="scoring"></a>
## Transparent scoring

`score_candidates` accepts a concrete list of unscored candidates; it validates the whole input first (source identity, location, complete normalized unit, kind/nature/uncertainty consistency) and scores only after everything is valid.
Missing sources, invalid enums, negative numbers, bools posing as counts, invalid Unicode, missing locations, or unknown fields are errors, never silently scored as 0.
An empty source may have an empty envelope but cannot supply non-empty candidates.
Source paths must be absolute local declarations without `.` / `..` segments or alternate streams.

Scoring returns deep-copied candidates with an added `score`; it does not change the input, deduplicate, reopen the raw source, or authenticate the source hash or speakers; supplied provenance is checked only for shape and consistency.
Cross-source contradictions or duplicates earn no automatic bonus and are all kept with their provenance.

### Consistency of units, counts, and locations

When the scoring CLI reads an envelope, it checks the following before producing any score or creating output:

| Format or relation | Constraints that can be checked from the input itself |
|---|---|
| Generic envelope | `candidate_count` equals the list length and is not greater than `unit_count`; status, count, and source declarations are consistent; counts are genuine non-negative integers. Candidate positions must not exceed the declared unit total |
| text / Markdown | `line <= unit_count`; a paragraph is a group of consecutive non-empty **raw** lines, so `2 × paragraph - 1 <= line`. The physical line count must not exceed the text byte count; the group count is not the line count |
| Complete text envelope | Source lines unique and increasing; first non-empty group is 1; adjacent candidate lines share a group, and a blank-line gap between line numbers raises the group by exactly 1 |
| Markdown envelope | Source lines unique and increasing; groups never go backwards; moving to another group requires at least a corresponding blank-line separation. Headings/code/comments may skip raw groups, so the first visible group need not be 1 |
| transcript envelope | Lines unique, increasing, and bounded by the total; turns run consecutively from 1 to candidate_count, each not greater than its line. Blank lines produce no turn; timestamps are not reordered by value |
| DOCX envelope | `paragraph <= unit_count`; global paragraphs unique and increasing; body blocks never go backwards; an ordinary block has one paragraph; table indices fit the known body blocks |
| DOCX related coordinates | block <= global paragraph; table <= block; row/cell/cell_paragraph must fit before the given global paragraph. Minimum rectangle width, local/global offsets within a cell, knowable adjacent-block starts, and trailing empty cell paragraphs must not contradict each other |

Blank lines and empty DOCX paragraphs/cells are real units, so `candidate_count` may be smaller than `unit_count`, and the last candidate need not occupy the last unit; missing candidates are not filled in.
Table checks use only the minimum row width and offsets determinable from the coordinates; they do not claim to know unsupplied empty cells or OOXML.

**The bare list API has no envelope totals or complete-read declaration.** It checks only relationships knowable from a single record (for example, the lower bounds of group/line, turn/line, and DOCX block/table/paragraph, and the first-block constraint); it invents no unit_count and does not force partial, repeated, or cross-source sets to be sorted, deduplicated, or treated as a complete original file.
Like scoring, it does not reopen the source; raw-byte authenticity cannot be established from the declarations.
Any inconsistency fails the entire call with the existing typed input error; no scored prefix is returned, and the CLI writes no partial "success" report.

| factor | Points and public rationale |
|---|---|
| `evidence` | 30: complete normalized unit and classification consistent with the given fragment/context; not proof of independent source authenticity |
| `locator` | 25: the format's required positive-integer coordinates and any supplied speaker/time are complete |
| `completeness` | 15 for an explicit type label, plus 10 for stripped text of at least 16 characters; not business-semantic completeness |
| `uncertainty` | observed 20, inferred 10, uncertain 0 |

The total is the sum of the four factors, an integer from 0 to 100; `score.scale`, per-factor `factors[].value/reason`, and `meaning` are all returned.
A long direct statement with an explicit label can score 100, a long uncertain statement 80, and a long unlabeled inferred statement 75; contradictory statements may tie.
This is a deterministic evidence-quality heuristic, **not a calibrated probability, model confidence, business decision, or automatic acceptance threshold**.
A high score does not remove conflicts, unknown context, or the accountable-owner confirmation gate.

<a id="cli"></a>
## CLI, output, and errors

Run from the selected documentation repository root, with this run's actual files in place of the path examples.
By default the CLI only outputs UTF-8 JSON. `--root` is required and bounds CLI inputs and the scope of new outputs; relative paths are relative to that root, and no other workspace files are read automatically.

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\extract_source.py --root . --source "sources\notes.md" --kind markdown
.venv\Scripts\python.exe -B -X utf8 .github\utilities\extract_source.py --root . --source "sources\notes.md" --kind markdown --output "reports\notes-candidates.json"
.venv\Scripts\python.exe -B -X utf8 .github\utilities\score_candidates.py --root . --input "reports\notes-candidates.json" --output "reports\notes-scored.json"
```

The scoring CLI reads a complete extraction envelope (keeping source and read counts) or an explicitly merged candidate JSON list (keeping each candidate's own source); it never searches for or merges sources automatically. Its JSON parsing also rejects duplicate keys and non-finite numbers.
Saving requires an explicit non-existent `.json` whose parent directory already exists, resolves inside the root, and does not take over a declared source or input; exclusive create, no overwrite, no mkdir, no auto-repair.
Existing files/sources/directories, out-of-bounds paths, stream paths, and missing parent directories are rejected. Partial I/O failures may not roll back; the explicit error and any partial output are kept, and they may not justify overwriting owner content and retrying.

| Result / code | Meaning and exit |
|---|---|
| `extracted` / `empty` or a valid scoring list | Exit 0; only offline processing completed; empty input keeps its real identity, not a business pass |
| `FILE_NOT_FOUND` / `FILE_READ_ERROR` / `INVALID_PATH` / `OUTSIDE_ROOT` | Local read/path error; exit 2 |
| `INVALID_ENCODING` / `INVALID_SOURCE_FORMAT` / `INVALID_TRANSCRIPT` | Input format/encoding error; exit 2, with no fake empty success |
| `INVALID_DOCX` / `INVALID_DOCX_XML` / `UNSUPPORTED_DOCX` / `UNSAFE_DOCX` / `SOURCE_ENCRYPTED` | Rejected by the actual container, layout, or security boundary; exit 2 |
| `SOURCE_LIMIT_EXCEEDED` / `CANDIDATE_LIMIT_EXCEEDED` | A public resource limit was exceeded; exit 2 |
| `INVALID_CANDIDATE` / `INVALID_CANDIDATE_KIND` / `INVALID_CANDIDATE_LOCATION` / `INVALID_SOURCE_IDENTITY` | Invalid scoring input; exit 2 |
| `REPORT_CONFLICT` / `REPORT_WRITE_ERROR` | Output conflict/write failure; exit 2; the original input is kept |
| `SOURCE_ADAPTER_UNAVAILABLE` | No currently supported format/adapter, including compound/encrypted Office containers and the audio adapter; exit 2 |

The API raises the existing `ArtifactInputError`, keeping `code/path/line/message` and the underlying exception chain.
CLI errors go to stdout as `{"status":"input-error","error":{...}}`; argument syntax errors are reported by argparse on stderr with exit 2. There is no exit 1 that judges candidates as accepted/rejected.
Unknown kinds are not guessed from the extension, and read/parse failures are not downgraded to empty.

<a id="audio"></a>
## Audio gate: refusal-only entry point

```python
transcribe_audio(
    source, *, service=None, model=None, data_scope=None,
    operation=None, output=None, authorized=False,
) -> NoReturn
```

No audio service, model, SDK, adapter, or data-sending scope is currently selected or approved.
For `transcribe_audio.py --source <explicit input for this run>`, neither the CLI nor the API reads audio or secrets, discovers environment providers, installs packages, sends data, writes output, or returns a fake empty transcript:

- Without separate authorization: `AUDIO_AUTHORIZATION_REQUIRED`, listing the missing inputs.
- Declared as authorized but missing service/model/data_scope/operation/output: `AUDIO_INPUT_REQUIRED`.
- All future fields supplied and operation is `transcribe`: still `SOURCE_ADAPTER_UNAVAILABLE`. Passing a service name or `--authorized` **cannot** select, install, or enable an adapter.

A future real call requires explicit input, service, model, pinned SDK version, operation, allowed data scope and destination, an exact new output, and authorization, all settled before a concrete adapter and real failure propagation are implemented.
No transcription service success or failure has been verified; the local refusal contract does not replace actual audio acceptance or close the related enhancement conditions.
