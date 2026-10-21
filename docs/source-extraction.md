# Local source candidates and transparent scoring

These optional tools read local files explicitly selected for this run and return candidates; they do not write formal domain facts.
Users check read authorization first; a readable file does not mean permission to process real private documents or send material.
The [reverse-engineering method](../.github/skills/reverse-engineer-domain/SKILL.md) remains responsible for returning to the sources,
comparing contradictory statements, requesting clarification, and any later authorized drafting. Scoring cannot confirm business rules, authenticate speakers, or approve candidates.

The tools use the [existing maintenance environment](development.md#maintenance-tools) and require no new media packages.
The [optional media manifest](../.github/utilities/requirements-media.txt) currently contains only notes;
no DOCX package, audio service, model, or SDK has been selected, so do not install guessed dependencies based on it.

<a id="interfaces"></a>
## API and source identity

Import the following narrow interfaces from `.github/utilities/`; they do not scan the repository, execute content, or follow links:

```python
extract_candidates(source: str | os.PathLike[str], kind: str) -> dict
score_candidates(items: list[dict]) -> list[dict]
```

`source` must be an explicit absolute path to a local regular file. URLs, UNC paths, ambiguous drive-relative
paths, and alternate streams are rejected; paths resolve links the host's normal way (for example macOS `/tmp`); this is not an OS sandbox,
and it does not guarantee protection against malicious concurrent replacement by other processes. The source identity is **the bytes actually read in this run**, not an inferred Git commit or formal artifact identity.
The API does not write files or change the cwd.

Extraction returns an envelope whose `candidates` field is the candidate list; the envelope is kept so that even empty input has a
real read identity. Its fixed fields are listed below; they do not belong to the formal artifact schema and add no formal kind:

| Field | Meaning |
|---|---|
| `status` | `extracted` or `empty`; not a business pass/approval |
| `source` | `path`: the actual absolute local path; `kind`: the explicit format choice; `baseline`: `sha256:` followed by the 64-character lowercase hexadecimal digest of the raw bytes; `byte_count`: the actual number of bytes read |
| `unit_count` | For text/Markdown/transcripts, the number of raw physical lines per Python `str.splitlines()`; for DOCX, the number of all paragraphs in the supported layout, including empty paragraphs and cell paragraphs |
| `candidate_count` | The actual list length, not an acceptance count |
| `candidates` | Candidates kept in original file order; not deduplicated by text or reordered by time |

Each candidate has the following fixed fields:

| Field | Meaning |
|---|---|
| `candidate_id` | A local sequence number for this run starting at `candidate-0001`; different sources may reuse numbers, so it must not be treated as a REQ/RULE or canonical ID |
| `kind` | The candidate type: `rule`, `capability`, `use-case`, `term`, or `statement` |
| `nature` | `observed`: explicit label; `inferred`: lexical classification of unlabeled text; `uncertain`: proposal/tentative wording. None of them means the fact is confirmed |
| `text` | The **complete** normalized text of the selected source unit; it must not select only a substring or drop qualifiers; normalization is specified below |
| `fragment` | The raw line, raw transcript JSON line, or DOCX paragraph text; it does not pose as a missing raw interview or XML line number |
| `source`, `location` | The same actual byte identity, and the 1-based format coordinates described below |
| `uncertainty` | The detected proposal words and the reason; empty when a direct statement contains none of these words, which does not mean it agrees with other sources |
| `extraction_reason` | The classification basis: explicit label or lexical inference |
| `clarification` | Asks the actual owner to confirm the scope and check contradictory sources; does not invent a named approver or decision number |
| `markdown_context` | Newly extracted Markdown candidates carry `{"in_comment": false}` or `true`, indicating whether the raw line was already inside an HTML comment before entering the scanner; it is not extra visible content or an authentication result. Other formats do not allow this field |

Supported explicit labels are `Rule:`, `Capability:`, `Use case:` / `Use-case:`, and
`Term:`; matching is case-insensitive.
Unlabeled text is inferred as a rule only from `must/shall/never/required/cannot`,
and as a capability only from `can/allows/supports`; everything else is a statement.
This is not a complete natural-language recognizer and cannot prove necessity or that the domain type is correct.
`maybe/should/proposed/perhaps/unconfirmed` are kept as uncertainty markers,
overriding the ordinary observed/inferred classification. Contradictory sources may both lack proposal words; both must still be kept and compared by the method;
the tool does not automatically detect all business contradictions or choose a prevailing rule, and has no supersedes/confirmed status.

<a id="formats"></a>
## Local formats and exact locations

| `kind` / extension | Reading and candidate unit | `location` |
|---|---|---|
| `text` / `.txt` | UTF-8; one candidate per non-empty line; command-like text is just text | `line`, `paragraph` |
| `markdown` / `.md` | UTF-8; reuses the existing Markdown line scanner to skip code/comments and ATX headings; visible non-empty lines become candidates; frontmatter and formal identity are not parsed separately | `line`, `paragraph` |
| `transcript` / `.txt` | Strict JSON Lines as defined below; each non-empty line is one complete turn | `line`, `turn`, `speaker`, `timestamp` |
| `docx` / `.docx` | The bounded OOXML subset defined below; one candidate per non-empty paragraph, including table cells | `part`, `block`, `paragraph`; cells also have `table`, `row`, `cell`, `cell_paragraph` |

UTF-8 may have a BOM; Unicode, paths with spaces, and CRLF are supported. The byte digest keeps the BOM/line endings as they are;
text lines in `fragment` exclude the line terminator. A text paragraph is a group of consecutive non-empty raw lines separated by blank lines **before filtering**,
so groups containing Markdown headings, comments, and fences still count; they do not pretend to be renderer-semantic paragraphs.
Markdown `text` may strip HTML comments while `fragment` keeps the raw line; scoring uses the same state machine and the
explicit pre-line comment context to check the complete visible unit. The tool is not a complete Markdown renderer
and does not automatically turn tables, headings, or frontmatter into formal artifacts.

### Complete source-unit normalization and Markdown context

- plain text, DOCX: only a leading/trailing `strip()` of the whole `fragment`; no truncation, collapsing of internal whitespace,
  or changes to case or punctuation, and no removal of restrictive suffixes. A DOCX paragraph may contain tabs/line breaks and is still one complete unit.
- transcript: strictly parse the whole raw JSON line and take the complete `text.strip()`; also check the supplied
  speaker/time, and never take an arbitrary substring of it.
- Markdown: the same shared scanner reads the whole raw line and applies the comment/code/fence rules to get the complete visible line;
  after excluding headings, code, and empty visible lines, only a leading/trailing `strip()` is applied. Extraction keeps the actual whole-file
  `markdown_context.in_comment`; scoring enters the **same** scanner in that declared state,
  without writing a second Markdown parser for standalone fragments and without accepting caller-supplied duplicated visible text.

For example, given the two raw lines `<!--` and `    --> Rule: Members <!--x--> must keep receipts.`,
the second line keeps its raw fragment, raw line/group, and `{"in_comment": true}`;
its complete text is `Rule: Members  must keep receipts.`. The four leading spaces of the standalone fragment
are not mistaken for code, and a visible Maybe or restrictive suffix cannot be removed to raise the score.

`markdown_context` allows only a single genuine bool `in_comment`; visible-text overrides,
unknown keys, and numeric stand-ins for bools are not allowed; line 1 cannot inherit a comment from a previous line. For compatibility with older
Markdown candidates that lack this field, the declared default entry state is non-comment; omitted context cannot be guessed.
This state is a limited **source-context declaration**, not a fact re-authenticated from the original file.
The tool does not open the original or authenticate the original hash, the speaker, or unsupplied prefixes; it only proves that the given fragment/context/
complete text/classification are internally consistent. Do not advertise this limitation as a guarantee of authenticity or approval.

`kind`, `nature`, and all `uncertainty` markers must match the result of reclassifying the complete normalized unit,
including the order and repetition of markers. Truncating text, removing `maybe`/`should`/`unconfirmed`, or manually overriding
nature/markers to disguise a different candidate is not allowed. Separate business judgments by the owner are still recorded through the shared method, and the tool's observations are not modified
in place of clarification; raw fragments and coordinates are not rewritten by normalization.

### Explicit transcript format

Each non-empty physical line must be a JSON object with exactly three non-empty string fields and no duplicate/extra keys:

```json
{"speaker":"A","timestamp":"00:00:02.125","text":"Rule: Members must keep receipts."}
{"speaker":"B","timestamp":"00:00:01.000","text":"Maybe that policy should change."}
```

Timestamps are fixed as `HH:MM:SS.mmm` (two-digit hours, minutes/seconds 00–59, three-digit milliseconds).
Input order, speakers, and time strings are preserved; names are not authenticated, real clock times are not validated, and chronological order is not inferred.
`text` is the JSON-decoded text and `fragment` is the raw JSON line; escaping does not change the source baseline.
Blank lines add no turn; invalid JSON, non-finite numbers, missing fields, empty text, invalid Unicode/control characters,
or any bad turn fails the entire read, and no first-half "success" is returned.

### Bounded stdlib DOCX

The implementation uses the already selected Python standard library `zipfile` and XML; it calls no converter and adds no parser package.
It actually reads the DOCX ZIP container and does not treat renamed text files as documents.
Currently only three required OPC parts are accepted:
`[Content_Types].xml`, `_rels/.rels`, and `word/document.xml`,
plus optional empty `word/` and `_rels/` directory entries. The content type must be a macro-free DOCX document;
the root relationship must be the fixed internal main-document relationship, which is only validated and never followed to read another location.

Supported: transitional WordprocessingML `document/body`, plain `p/r/t`,
`tab/br/cr` within runs, a trailing empty `sectPr`, and rectangular `tbl/tr/tc` tables.
Tables may have an empty `tblPr`, a simple `tblGrid/gridCol`, and a `tcPr` containing only `tcW`.
With a grid, all rows are checked against the grid's column count; without a grid, all rows are checked against the first row's actual cell count;
any later row that is wider or narrower is explicitly rejected and must not be treated as a supported rectangular subset.
Run concatenation order, XML-decoded text, tabs, and line breaks are preserved; no spaces, pages, or audio times are added.
`block` is the position within the body; `paragraph` counts all paragraphs in document order;
`cell_paragraph` is the paragraph position within that cell; other coordinates count in document/table order.
Coordinates are not page numbers or XML line numbers, and the source baseline is still the byte digest of the entire actual ZIP.

**Unsupported layouts are explicitly rejected, with no partial success:** extra parts (including common styles/settings,
properties, headers/footers, footnotes, images, macros, and additional relationships),
Strict OOXML, non-UTF-8 XML, merged/nested tables, style properties, fields, hyperlinks, revisions,
content controls, embedded objects, and other body layouts. Ordinary office documents may contain these, so this narrow adapter does not
justify claiming that arbitrary DOCX files are fully extracted; the needed format extensions and input authorization must be decided separately.

Nothing is unpacked to disk, external entities are not resolved, relationship targets are not accessed, and document content is not executed.
ZIP traversal/absolute paths/backslashes/NUL/duplicate names/type aliases, encrypted ZIPs, DTD/entity
declarations, corrupt XML/CRC, missing required parts, and unsupported compression/layouts are rejected. Non-body content such as XML comments does not become a business candidate;
it still falls within the identity of the entire input bytes.

| Resource boundary | Fixed limit |
|---|---|
| Single source or CLI scoring JSON | 4 MiB of raw input; exceeding it fails, never truncating to a success |
| Text/Markdown/transcript lines | 10,000 (including empty/excluded lines), checked before candidate expansion |
| Single scoring run | 10,000 candidates; both the API and the CLI reject larger sets |
| ZIP entries | 64, including directory entries |
| Single ZIP part / total uncompressed bytes | 1 MiB / 8 MiB |
| ZIP expansion ratio | Each part at most `100 × max(compressed_size, 1)` |
| Each XML part | Depth at most 32 and at most 10,000 elements, checked during parsing |

<a id="scoring"></a>
## Transparent scoring

`score_candidates` accepts a concrete list of unscored candidates. Across the whole input, it first validates the complete source identity, location,
complete normalized unit, and kind/nature/uncertainty consistency, and computes scores only after everything is valid.
Missing sources, invalid enums, negative numbers, bools posing as counts, invalid Unicode, missing locations, or unknown fields are errors;
they are never silently scored as 0. An empty source may have an empty envelope but cannot supply non-empty candidates.
Source paths must be absolute local declarations without `.` / `..` segments or alternate streams.

Scoring returns deep-copied candidates with an added `score`; it does not change the input, deduplicate, or reopen the raw source to recompute,
and does not authenticate the source hash or speakers; externally supplied provenance is checked only for shape/consistency.
Cross-source contradictions or duplicates earn no automatic bonus, and all are kept with their provenance.

### Consistency of units, counts, and locations

When the scoring CLI reads an envelope, it checks the following before producing any score or creating output:

| Format or relation | Constraints that can be checked from the input itself |
|---|---|
| Generic envelope | `candidate_count` equals the list length and is not greater than `unit_count`; the status/count/source declarations are consistent, and counts are genuine non-negative integers. Candidate positions must not exceed the corresponding declared unit total |
| text / Markdown | `line <= unit_count`; a paragraph is a group of consecutive non-empty **raw** lines, so `2 × paragraph - 1 <= line`. The physical line count must not exceed the given text byte count; the group count is not taken as the line count |
| Complete text envelope | Source lines are unique and increasing, and the first non-empty group is 1; adjacent candidate lines are in the same group, and a blank-line gap between line numbers increases the group by exactly 1 |
| Markdown envelope | Source lines are unique and increasing, groups never go backwards, and moving to another group requires at least a corresponding blank-line separation. Headings/code/comments may make candidates skip raw groups, so the first visible group is not forced to be 1 |
| transcript envelope | Lines are unique, increasing, and bounded by the total; turns must run consecutively from 1 to candidate_count, and a turn is not greater than its original line. Blank lines produce no turn, and timestamps are not reordered by value |
| DOCX envelope | `paragraph <= unit_count`; global paragraphs are unique and increasing, and body blocks never go backwards; an ordinary block has only one paragraph, and table indices are compatible with the known body blocks |
| DOCX related coordinates | block is not greater than the global paragraph, and table is not greater than block; row/cell/cell_paragraph must fit before the given global paragraph. The known minimum rectangle width, the local/global paragraph offsets within the same cell, the knowable starts of adjacent blocks, and trailing empty cell paragraphs must not contradict each other |

Blank lines and empty DOCX paragraphs/cells are real units, so `candidate_count` may be smaller than
`unit_count`, and the last candidate need not occupy the last unit; missing candidates are not filled in automatically.
Table position checks use only the minimum row width/offsets determinable from the given coordinates and do not claim to know all unsupplied empty cells or OOXML.

**The bare list API has no envelope totals or complete-read declaration.** It checks only the relationships knowable from a single record
(for example the required lower bounds of group/line, turn/line, and DOCX block/table/paragraph, and the first-block constraint);
it does not invent a unit_count and does not force partial/repeated/cross-source sets to be sorted, deduplicated, or treated as a complete original file.
This does not reopen the source to verify positions; the authenticity of the raw bytes cannot be established from the declarations themselves.
Any inconsistency fails the entire call with the existing typed input error; no scored prefix is returned,
and the CLI does not write a partial "success" report.

| factor | Points and public rationale |
|---|---|
| `evidence` | 30: the complete normalized unit and classification are consistent with the given fragment/context; not proof of independent source authenticity |
| `locator` | 25: the format's required positive-integer coordinates and any supplied speaker/time are complete |
| `completeness` | 15 for an explicit type label, plus 10 for stripped text of at least 16 characters; not business-semantic completeness |
| `uncertainty` | observed 20, inferred 10, uncertain 0 |

The total is the sum of the four factors, an integer from 0 to 100; `score.scale`, the per-factor `factors[].value/reason`, and
`meaning` are all returned. A long direct statement with an explicit label can score 100, a long uncertain statement 80,
and a long unlabeled inferred statement 75; two contradictory statements may also receive the same score.
This is a deterministic heuristic of evidence quality, **not a calibrated probability, model confidence, business decision, or automatic acceptance threshold**.
A high score does not remove conflicts, unknown context, or the accountable-owner confirmation gate.

<a id="cli"></a>
## CLI, output, and errors

The cwd for the following commands is the root of the selected documentation repository; the path examples must be replaced with the actual files for this run.
The API is read-only; by default the CLI only outputs UTF-8 JSON. `--root` is required and bounds the CLI inputs and the scope of new outputs;
relative paths are all relative to that root, and no other workspace files are read automatically.

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\extract_source.py --root . --source "sources\notes.md" --kind markdown
.venv\Scripts\python.exe -B -X utf8 .github\utilities\extract_source.py --root . --source "sources\notes.md" --kind markdown --output "reports\notes-candidates.json"
.venv\Scripts\python.exe -B -X utf8 .github\utilities\score_candidates.py --root . --input "reports\notes-candidates.json" --output "reports\notes-scored.json"
```

The scoring CLI can read a complete extraction envelope (keeping the source and read counts) or an explicitly merged candidate JSON list
(keeping each candidate's own source); it never searches for or merges sources automatically. Its JSON parsing likewise rejects duplicate keys/non-finite numbers.
Saving requires an explicitly specified, non-existent `.json` whose parent directory already exists and which resolves inside the root
without taking over a declared source or input; exclusive create, no overwrite, no mkdir, no auto-repair.
Existing files/sources/directories, out-of-bounds paths, stream paths, and missing parent directories are rejected. Partial I/O failures are not guaranteed to roll back;
the explicit error and any partial output from this run are kept, and this must not be used as grounds to overwrite owner content and retry.

| Result / code | Meaning and exit |
|---|---|
| `extracted` / `empty` or a valid scoring list | Exit 0; only this offline processing completed; empty input keeps its real identity and is not a business pass |
| `FILE_NOT_FOUND` / `FILE_READ_ERROR` / `INVALID_PATH` / `OUTSIDE_ROOT` | Local read/path error; exit 2 |
| `INVALID_ENCODING` / `INVALID_SOURCE_FORMAT` / `INVALID_TRANSCRIPT` | Input format/encoding error; exit 2, with no fake empty success |
| `INVALID_DOCX` / `INVALID_DOCX_XML` / `UNSUPPORTED_DOCX` / `UNSAFE_DOCX` / `SOURCE_ENCRYPTED` | Rejected by the actual container, layout, or security boundary; exit 2 |
| `SOURCE_LIMIT_EXCEEDED` / `CANDIDATE_LIMIT_EXCEEDED` | A public resource limit was exceeded; exit 2 |
| `INVALID_CANDIDATE` / `INVALID_CANDIDATE_KIND` / `INVALID_CANDIDATE_LOCATION` / `INVALID_SOURCE_IDENTITY` | Invalid scoring input; exit 2 |
| `REPORT_CONFLICT` / `REPORT_WRITE_ERROR` | Output conflict/write failure; exit 2; the original input is kept |
| `SOURCE_ADAPTER_UNAVAILABLE` | No currently supported format/adapter, including compound/encrypted Office containers and the audio adapter; exit 2 |

The API raises the existing `ArtifactInputError`, keeping `code/path/line/message` and the underlying exception chain.
CLI errors go to stdout as `{"status":"input-error","error":{...}}`;
argument syntax errors are reported by argparse on stderr with exit 2. There is no exit 1 that judges candidates as accepted/rejected.
Unknown kinds are not guessed from the extension, and read/parse failures are not downgraded to empty.

<a id="audio"></a>
## Audio gate: only an honest refusal entry point

```python
transcribe_audio(
    source, *, service=None, model=None, data_scope=None,
    operation=None, output=None, authorized=False,
) -> NoReturn
```

No audio service, model, SDK, adapter, or data-sending scope is currently selected or approved.
For `transcribe_audio.py --source <explicit input for this run>`, neither the CLI nor the API reads audio/secrets,
discovers environment providers, installs packages, sends data, writes output, or returns a fake empty transcript:

- Without separate authorization: `AUDIO_AUTHORIZATION_REQUIRED`, listing the missing inputs.
- Declared as authorized but missing service/model/data_scope/operation/output: `AUDIO_INPUT_REQUIRED`.
- All future fields supplied and operation is `transcribe`: still `SOURCE_ADAPTER_UNAVAILABLE`.
  Passing a service name or `--authorized` **cannot** select, install, or enable an adapter.

A future real call additionally requires explicit input/service/model/pinned SDK version, operation, allowed data scope/destination,
an exact new output, and authorization, before a concrete adapter and real failure propagation are implemented. No transcription service success or failure has been verified;
the local refusal contract does not replace actual audio acceptance and does not close the related enhancement conditions.
