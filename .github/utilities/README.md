# Local maintenance tools

This directory provides parsing, formal-artifact checks, coverage and impact candidates, a deterministic reference model, read-only implementation-report collection, three-way and explicit multi-target update proposals, explicit local source preflight and onboarding, local document/transcript candidates with transparent scoring, and sourced local exports of relationship graphs, architecture views, and presentations. The optional hook adapter and installer entry points are described in a later section. These tools are not an application, a unified CLI framework, a general-purpose executor, or a global library. Schema fields and complete examples are maintained only in the [contract notes](../contracts/README.md); these mechanical tools do not prove business execution or approval.

## Tool environment

The tools require Python 3.11+ and target Windows, Linux, and macOS. The environment and command registration are in the [maintenance tools section of the development guide](../../docs/development.md#maintenance-tools), separate from downstream business applications; maker-repository regression tests and run history are not prerequisites for downstream use. Locations come from explicit arguments and project-relative resources; no drive letter or directory is required. The checkers serve only DDD artifacts, references, coverage, and derived results; they are not a file-system audit or a sandbox.

- [requirements.txt](requirements.txt) lists only the approved PyYAML 6.0.2 and jsonschema 4.23.0 (locked and tested); at run time the tools only require both to be importable.
- [requirements.lock](requirements.lock) keeps the six versions resolved in a Python 3.13 environment. It adds a conditional `typing-extensions==4.16.0` entry for Python `<3.13` (verified by an actual install on 3.11): 3.11 selects seven entries, 3.13 still selects six. The condition comes from `referencing` package metadata and does not upgrade the original pins. pip is an environment installation tool, not a runtime dependency; no hashes were guessed.
- On Windows, from the repository root, run `python -m venv .venv`, restore the locked environment with `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.lock`, and then run `.venv\Scripts\python.exe -m pip check`.
- No activation or global pip is needed. There are no media packages, extra DOCX/PDF packages, binary-format renderers, cloud SDKs, or application dependencies: the DOCX adapter uses stdlib ZIP/XML, the [optional media manifest](requirements-media.txt) selects no packages, local JSON/SVG/HTML use the stdlib, and the [rendering manifest](requirements-rendering.txt) selects no PDF/PPTX engine. Other hosts use their actual `.venv/bin/python`; users must verify the local interpreter and installed dependencies.

<a id="interaction-ledger"></a>
## Explicit interaction ledger and usage summary

`append_record(log_path, InteractionRecord, *, attest_local_storage=True)` in `log_interaction.py` accepts only values the caller supplies explicitly. `summarize_usage(log_path)` in `summarize_usage.py` returns the source SHA-256, record and unknown counts, and known-usage groups in deterministic order; explicit output uses `write_summary(log_path, output_path, *, attest_local_storage=True)`. Neither reads full prompts/chats, the environment, a personal `models.json`, credentials, billing, application output, or vendor services, and neither executes field text. Without usage, value, unit, and currency stay empty; unknown is not zero. The summary sums exact decimals only across records with identical tool, version, unit, and currency, and does not estimate prices or draw cost or savings conclusions.

The fixed CSV v1 columns are:

```text
schema_version,record_id,recorded_at,tool_name,tool_version,task_ref,object_ref,object_baseline,operation_summary,decision_ref,usage_value,usage_unit,usage_currency,evidence_ref
```

Field meanings, the minimal data boundary, and limitations are in the [AI tooling guide](../../docs/ai-tooling.md#interaction-ledger). [`_templates/reports/ai-interaction-log.csv`](../../_templates/reports/ai-interaction-log.csv) is a blank header to copy, not an active ledger: copy it to a new `.csv` in an existing local directory first; never write to the template. The API/CLI require an explicit absolute path to an existing regular file with a v1 header; they do not create parent directories or repair bad records. Every row needs a timezone-qualified time `YYYY-MM-DDTHH:MM:SS[.fraction](Z|±HH:MM)`; the original literal time and usage text is preserved. Usage accepts only finite, non-negative plain decimals, not exponent notation. The summary is at most 512 characters and must not contain complete interactions or sensitive data.

Cross-platform read/write boundaries:

- Every write path requires caller attestation (`attest_local_storage=True` in the API, `--attest-local-storage` on the CLI); without it the request is rejected with `WRITE_ATTESTATION_REQUIRED`, and no lock or output is created. Attestation is the user's declaration that the directory is single-machine local storage, not network or cloud-synced. It is not OS or vendor verification or a durability guarantee; the tools do not inspect drives, the registry, or vendors.
- Appends use an adjacent `.lock` sidecar (kept) to serialize same-machine processes (`msvcrt` on Windows, `fcntl` on Linux/macOS). Before writing inside the lock, an append verifies the ledger bytes are unchanged; that is the only change detection. The default summary reads once, takes no lock, creates no file, and does not count corrupt or partial lines. Cross-module public interfaces: `read_ledger`, `file_lock`, `validate_existing_log`, `validate_new_output`, `require_write_attestation`, `emit_error`.
- Explicit `write_summary`/`--output` requires attestation, uses the source lock and stdlib exclusive creation, never overwrites, and never creates a missing parent directory. It keeps read/write consistency and partial-failure recovery information, but does not bind native directory handles, guard against malicious concurrent path replacement, or delete or rebuild output.
- A OneDrive-synced directory has no cross-host coordination guarantee, even when mapped to a fixed drive, so callers should not attest to it. CSV is a data-interchange format, not spreadsheet-safe; references and cell contents are not executed.

CLI examples (replace angle-bracket values with this call's values; paths must be absolute and may contain spaces inside quotes):

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\log_interaction.py --log "<absolute-local-ledger.csv>" --record-id "<id>" --time "2026-10-18T12:34:56Z" --tool "<caller-supplied-name>" --tool-version "<caller-supplied-version>" --task-ref "<task-reference>" --object-ref "<object-reference>" --object-baseline "<object-baseline>" --summary "<brief factual summary>" --attest-local-storage [--decision-ref "<pointer>"] [--usage-value "<decimal>" --usage-unit "<unit>" [--usage-currency "<currency>"]] [--evidence-ref "<pointer>"]
.venv\Scripts\python.exe -B -X utf8 .github\utilities\summarize_usage.py --log "<absolute-local-ledger.csv>"
.venv\Scripts\python.exe -B -X utf8 .github\utilities\summarize_usage.py --log "<absolute-local-ledger.csv>" --output "<absolute-new-summary.json>" --attest-local-storage
```

CLI exit 0 means the append, identical replay, or summary completed; exit 1 means a record-input error or ID conflict; exit 2 means a path, log, lock, output, or recovery error. The default summary prints no source path, only its hash. The tools describe only reproducible local behavior and cannot verify the real tool, provider, billing, human decisions, or qualification.

<a id="document-exports"></a>
## Sourced relationship graphs, architecture, and presentations

`render_traceability(view)` reads an explicit root/scope and produces JSON/SVG/HTML showing the
actual dependency direction, complete owner/anchor, isolated nodes, cycles, and source gaps. `render_architecture(inputs, format)`
and the required `render_presentation(inputs, format)` read explicit source pointers and fixed baselines and
output HTML/SVG driven by source sections; a limited SEQ subset actually draws participants, messages, and branches.
Copied code is not presented as a visualization, and transport is not inferred from arrows.

The [single contract for inputs, returns, limited syntax, CLI, errors, and writes](../../docs/document-exports.md) describes the fields. These tools reuse the real inventory, nine views, `check_model`, and source and report adapters; they do not accept an arbitrary schema-valid model as fact. An empty trace produces no demo; missing sources keep nine-view gaps; drift, wrong sources, or unsupported SEQ give explicit diagnostics. `section_fences(artifact, anchor)` projects only the closed fences of an already parsed Artifact, sharing the original comment/literal state machine with the model; it adds no file parser or authorization boundary.

The API and default CLI do not write; the only file written is an explicit new output, created exclusively, whose parent directory must exist. It is rejected on a conflict with a source or history path, a declared-but-missing location or its ancestor/child paths, or a case/alias conflict. There are no CDNs, remote fonts, scripts, source commands, or automatic downloads. PDF/PPTX have only an unavailable/not-run rejection contract, which is not success in that format; the actual engine, dependencies, signature/parser, non-zero pages/slides, source content, and human/App gates still need separate authorization and execution. A local export is not SWAS approval or complete equivalent acceptance.

<a id="source-candidates"></a>
## Local source candidates and scoring

`extract_source.extract_candidates(source, kind)` reads only an explicit absolute local file and returns the actual byte identity/read count and a `candidates` list; it supports Markdown/plain text, strict JSONL transcripts, and bounded stdlib DOCX. `score_candidates.score_candidates(items)` keeps duplicate and contradictory sources and returns public 0–100 factors with reasons, which are not probabilities or acceptance thresholds. Types, locations, input limits, CLI, and errors are in the [source-candidate contract](../../docs/source-extraction.md), not the formal-artifact schema.

The normalized source unit and its classification must agree; qualifiers cannot be dropped by substring matching. Markdown candidates use the same scanner's preceding-comment context, which is neither a caller override of the visible body nor source authentication. The envelope also checks the declared total unit count, format-specific coordinates/order, and empty-unit relations; scoring happens only when all are valid, and a bare list neither invents a total nor drops duplicate sources. A DOCX table without a grid keeps the rectangular limit from its first-row width.

The API and default CLI do not write. Explicit output only creates a new JSON file exclusively, inside the root; it never creates directories or overwrites declared inputs. `transcribe_audio` currently has only a rejection entry point (authorization/missing items/unavailable); it reads no audio or environment secrets, installs no SDKs, and calls no services. Candidates still go back to the [shared reverse-engineering method](../skills/reverse-engineer-domain/SKILL.md) for checking and clarification; the tools cannot record them as confirmed facts.

<a id="native-hooks"></a>
## Optional native hooks and same-source CI

The [hook guide](../hooks/README.md) defines the installation proposal, explicit apply, per-path recovery, index semantics, and `Reviewed-by` text policy for managed paths. By default `install_hooks.py` does not write; it rejects existing hooks, configuration conflicts, and shared worktree metadata. It never modifies Git configuration or commits/pushes automatically. When installation I/O fails, it keeps and itemizes everything this run fully or partially created, and does not guess at or delete owner content added later.

`hook_checks.py pre-commit --root <checkout-root>` can also be called directly with the selected project Python. It uses the actual index and raw blobs, not working files, and accepts an exact `--base` and a new `--report`. Both Python hook entry points and the downstream documentation workflow reuse this module, which handles only snapshots/context and format policy; artifact, Markdown, owner AC/VC, and coverage rules stay in the three existing modules.
Before reading the index or artifacts, the entry point only confirms Python 3.11+ and that PyYAML and jsonschema are importable. A venv, conda, or system interpreter all work; pinned versions, `pyvenv.cfg`, and the prefix are not checked. The launcher-selected path/prefix is only recorded in the report, never a rejection reason, and the entry point never switches interpreters on its own.
The private `_base_root` of `read_inventory` only lets a temporary snapshot read historical raw objects from the original Git root. `_trace_inventory` reuses the same inventory and still reverse-checks targets when there are zero owners. The working-tree/non-empty-delivery selection contract of public `run_check` and `trace_report` is unchanged.

These entry points must ship with `artifact_io.py`, `check_artifacts.py`, `check_traceability.py`, `artifact.schema.json`, and the dependency manifests. Maker-repository test runner/workflows, test data, research, and history records are not downstream dependencies. Native Git failures and JSON exit codes 0/1/2 are each preserved. An empty inventory is not a business pass, local format checks do not authenticate the reviewer, and workflow YAML presence does not mean hosted CI has run.

## Parser interface

Later scripts in this directory import this module directly; it has no command-line entry point that could fake success. Callers supply the real root and files explicitly on each call, rather than relying on cwd changes, automatic scanning, or business command registration.

```python
parse_artifact(path: str | os.PathLike[str], root: str | os.PathLike[str]) -> Artifact

parse_artifacts(
    paths: Iterable[str | os.PathLike[str]],
    root: str | os.PathLike[str],
) -> tuple[Artifact, ...]
```

A relative `path` resolves against the explicit `root`, which must be an actual directory; each input must be a readable regular file inside it. A path escaping the root through a symlink or junction fails. A missing file, wrong type, garbled text, or failed read is never an empty artifact. UTF-8 with or without BOM, LF/CRLF, non-ASCII paths, and spaces are covered by real-file tests. There is no guarantee against another process maliciously replacing a path between check and open; this is not an operating-system sandbox.

`parse_artifacts` processes only the given collection, keeps input order, and for a duplicate scope/id reports both the second and the first occurrence. The same ID in different scopes is valid. An empty collection returns an empty tuple after validating the root; this does not mean business coverage is complete. Parsing one file never scans others for deduplication.

Returned records are `frozen=True, slots=True` dataclasses; collections are tuples:

| Type | Available fields |
|---|---|
| `Artifact` | `schema_version`, `id`, `kind`, `scope`, `content_state`, `upstream`, `targets`, `confirmation`, `path`, `relative_path`, `location`, `id_location`, `body_start_line`, `source`, `body`, `anchors`, `acceptances`, `metadata_locations`; derived properties `key` and `acceptance_ids` |
| `SourceLocation` | `path: Path` (actual absolute path), `line: int` (1-based) |
| `Target` | `target`, `criterion_anchor`, `test_id: str \| None`, `location`, `criterion_location` |
| `Confirmation` | `by`, `reference`, `baseline`, `location`; presence does not mean the approver has been verified |
| `Anchor` | `name`, `location` |
| `Acceptance` | Full heading `id`, `owner` (scope/id), `anchor`, heading `location`, `anchor_location`; derived property `reference` (scope/id#anchor) |

`source` is the original text minus the UTF-8 BOM; `body` starts after the closing frontmatter delimiter line. Both keep the original LF/CRLF and are never reflowed or written back. `body_start_line` and the target and acceptance locations let later checks locate findings; `relative_path` is the resolved root-relative path using `/`. Callers must read raw bytes separately; the decoded `source` cannot substitute for a byte digest of the original file.

`metadata_locations` is a tuple of `(field-path tuple, SourceLocation)` pairs from the same YAML parse, for example `("scope",)` or `("targets", 0, "target")`; it is not a second field parser. `iter_markdown_lines(body, start=1)` keeps line numbers, removes HTML comments, and returns `None` for code lines, so the parser and checkers treat literal content alike. `iter_markdown_fences(body, start=1)` returns genuinely closed `MarkdownFence(start_line, end_line, info, body)` values from the **same** state machine; fence examples inside comments or enclosing code do not become code blocks. Owner acceptance criteria still come only from the original parser's explicit anchors and owned ID headings.

Source candidates can use `iter_markdown_source_lines(body, start=1, *, initial_in_comment=False)` to obtain `(line, visible_or_None, incoming_comment_bool)`. The keyword-only initial state exists only to replay a complete source unit and still delegates to the same state machine. Original line/fence interfaces and formal identity behavior are unchanged; an unsupplied source prefix is not authenticated.

## Input errors

`ArtifactInputError(ValueError)` has stable attributes `code`, `path`, `line`, and `message`; its string contains all four. YAML, decoding, file-read, and schema failures keep the original exception chain. If a path cannot be established yet, `path` holds a readable form of the input. Errors before the file is read use line 1; empty metadata uses line 2.

| code | Condition |
|---|---|
| `INVALID_ROOT` | Root of wrong type, empty, missing, unreadable, or not a directory; `path` is the invalid root's string form and line is 1 in both APIs; an empty selection cannot bypass this |
| `INVALID_PATH` | Invalid input type or path, ambiguous drive-relative path, directory, or other non-regular file; a single path passed to the collection interface by mistake |
| `OUTSIDE_ROOT` | A normalized path, symlink, or junction target escapes the explicit root |
| `FILE_NOT_FOUND` | The file inside the root does not exist |
| `FILE_READ_ERROR` | stat/read failed; keeps the specific OS error and never defaults to an empty body |
| `INVALID_ENCODING` | UTF-8 decoding failed; the line is computed on the decoder's original input, so BOM failures are not offset |
| `MISSING_FRONTMATTER` / `UNTERMINATED_FRONTMATTER` | The file does not start with `---`, or the closing `---` is missing |
| `INVALID_YAML` | YAML syntax error, non-string mapping key, unsafe/unknown tag, circular alias, or nesting limit exceeded |
| `DUPLICATE_YAML_KEY` | A duplicate key at any depth, including a duplicate `<<` and overrides after a merge; the raw node graph is checked first so normalization cannot hide duplicates |
| `INVALID_METADATA` | Not a mapping, missing fields, malformed scope/id/relations/confirmation, unknown fields, or duplicate relation records |
| `UNSUPPORTED_SCHEMA_VERSION` | Not a genuine integer 1; no fallback parsing |
| `INVALID_KIND` / `INVALID_CONTENT_STATE` | Not in the fixed contract enumeration |
| `MISSING_ACCEPTANCE_ANCHOR` / `DUPLICATE_ANCHOR` | An owner acceptance heading lacks its explicit matching anchor, or a body anchor is not unique |
| `MISSING_CRITERION_ANCHOR` | A target's criterion anchor is not in the current body |
| `DUPLICATE_ARTIFACT_ID` | The same scope/id appears twice in the explicit collection; neither merged nor dropped |
| `CONTRACT_ERROR` | The local artifact schema cannot be read, parsed, or validated, or has a non-local or unresolvable `$ref` |

Parsing uses SafeLoader; it does not construct Python objects or execute YAML, Markdown, or referenced commands. Valid, non-circular aliases without duplicate keys are parsed. A present but malformed `upstream` or `targets` value is reported as an error first, never replaced by an empty tuple. The schema cache is per process; after changing the local contract, reload it in a new process.

<a id="artifact-checker"></a>
## Formal artifact checker

```python
run_check(root: str | os.PathLike[str], base_sha: str | None = None) -> CheckReport
```

Import it from `check_artifacts` in this directory. The API writes no files, changes no cwd, and executes no commands found in sources; `root` must be an explicit local directory. By default the CLI only prints UTF-8 JSON to stdout:

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_artifacts.py --root .
```

In this example the cwd is the repository root and `.` is the currently selected documentation root; other hosts substitute their actual project interpreter. You can also pass `--base <full commit>` or `--report <explicit new JSON file path>`. Replace angle-bracket arguments with this run's real values. No shell wrapper, hooks, or CI are needed; `-B` avoids writing bytecode.

| status | Exit code | Meaning |
|---|---|---|
| `clean` | 0 | At least one formal artifact was checked and no finding within this tool's scope was produced |
| `empty` | 0 | No formal input was found, `checked_count=0`; not a requirement, business, or application pass |
| `invalid` | 1 | There are heading, placeholder, or local Markdown link violations |
| `input-error` | 2 | Input, parser, path, baseline, or report-output failure; takes precedence over `invalid`, and other findings already obtained are kept |

<a id="checker-discovery"></a>
### Discovery scope and exclusions

Files are checked recursively in stable relative-path order for `.md` (case-insensitive extension). Any of the following signals makes a file a formal input:

- The file name starts with an uppercase hyphenated ID, for example `REQ-001.md`, `SR-SYN-001-title.md`, or `REQ-NNN.md`; the pattern is `^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+`, followed by a separator or the end of the file name.
- The leading frontmatter contains a field signal from `schemaVersion/id/kind/scope/contentState/upstream/targets/confirmation`, or the opening delimiter is missing but such a metadata prefix is present. A recognizable but invalid `---` on the first line (for example with an extra leading space) keeps the metadata candidate that follows it; ordinary body text or code ends the prefix search. This step only selects files; delimiter validity, fields, types, duplicate keys, version, and confirmation shape are left to the parser.
- An H1 outside code/comments starts with the same kind of formal ID. Exact-base mode also keeps current paths that were historically recognized as formal, so a change cannot be hidden by deleting all metadata.

A formal file with damaged fields or no frontmatter still reports an input error; it is never migrated or rewritten automatically. An ordinary README, note, or old lightweight body with no identity or metadata signal is only a guide; the checker cannot recreate a fully deleted identity. A file with any name (including a README) is still checked while it keeps formal metadata.

Each `excluded` entry is `{path, reason}`; a trailing `/` covers the whole subtree. Entries are relative to **this run's root** and never match its ancestors, so a test root under the tools' `.venv` can still be scanned.

| reason | Exact exclusion rule |
|---|---|
| `TEMPLATE` | `_templates/` and `.github/pull_request_template.md` under the root |
| `NATIVE_METADATA` | `.github/skills/`, `instructions/`, `agents/`, `prompts/`, `workflows/`, and `.github/copilot-instructions.md` under the root |
| `MAKER_DATA` | `docs/design/`, `docs/plan/`, and `docs/research/` under the root |
| `TEST_FIXTURE` | `tests`, `test`, or `fixtures` directory segments in the relative path |
| `TOOL_DATA` | `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.tox`, or `.nox` segments in the relative path |
| `DIRECTORY_ALIAS` | Directory symlink/junction aliases that point inside the root; the actual directory is scanned only once, avoiding duplicates and cycles |
| `NON_MARKDOWN` / `LIGHTWEIGHT_GUIDE` | Non-Markdown files / Markdown that was read but has no formal signal |

A directory link that escapes the root is an error, not an exclusion; formal inputs do not accept symlinked files. An explicitly referenced template or guide inside the root may be read as a link target without joining the formal inventory; Git, environment, and dependency data are never read as link targets. An unenumerable directory, unreadable file, or garbled text is never treated as empty. UNC/URL roots and UNC local references are rejected before parsing; network addresses are never accessed.

<a id="checker-format"></a>
### Checked Markdown and placeholder syntax

- A formal body needs one non-empty ATX H1 (`# Title`) and no second H1. Parser checks for metadata, unique scope/id, explicit anchors, and owner AC/VC structure still apply; the same ID in different scopes is valid.
- Supported: single-line inline links/images, angle-bracket destinations, optional single- or double-quoted titles, reference definitions, full/collapsed reference links, and defined shortcut references. Paths with spaces use `%20` or `<path with spaces.md>`; a destination may contain one level of parentheses.
- Local files must exist inside the root. A fragment matches a parser-style standalone `<a id="ascii-anchor"></a>` or an ATX heading slug (lowercased; Unicode letters/digits, spaces, `_`, and `-` kept; spaces become `-`; repeated headings get suffixes such as `-1`). Heading slugs serve navigation only and do not replace explicit owner acceptance anchors. A fragment on a non-Markdown target returns `UNSUPPORTED_FRAGMENT`.
- Backtick/tilde fenced code, code lines indented four spaces or a tab, single-line inline code, and HTML comments are ignored. External URIs are not fetched; an undefined explicit `[label][reference]` is an error. Setext headings, multi-line links, complex nesting, raw HTML `href`, and renderer-specific anchors are outside the checked syntax; this is not a complete CommonMark/GFM renderer.
- A body comment that starts before a fence is still a comment; a fence's info string and content do not change the body's comment state. A backtick fence's info string must not contain backticks, and comment-like text in it is not removed before judging validity. After the fence closes, scanning for real links and owner acceptance criteria resumes with the original line numbers.
- Residual markers are the standalone tokens `TODO/TBD/PROJECT` (`TBD` is the standard fill-in placeholder), a standalone `NNN` (including in lowercase anchors), `<slug>`/`<project>`/`<context>`/`<id>`, and `{{field}}`. Metadata placeholders are checked only in the identity/relation/confirmation fields the parser has read; YAML comments are not values, and examples in body code and comments are not placeholders. The ordinary word `project` is not a placeholder.
- Facts with specific context, such as `open`, `to be confirmed`, or `not-run`, may remain; the checker does not fill in business decisions. The absence of mechanical violations does not mean semantic completeness, trustworthy approval, or successful behavior execution.

<a id="checker-baseline"></a>
### Exact baseline and current-file comparison

Without a base, only the current root is read and Git is not needed. With a base, the root must be exactly the top level of the selected checkout (linked worktrees are supported); borrowing an ancestor repository is rejected. The base accepts only a readable full 40/64-hex-digit **commit object**; branches, short hashes, tag or blob objects, and nonexistent objects are rejected, with no fallback.

**In both modes, the verification target is always the complete formal inventory of the current working files**, including unstaged and untracked formal files. The base only adds a historical comparison; it does not skip unchanged artifacts and is not an index (staging-area) hook check. Historical Markdown is read and recognized only from raw Git blobs, and old metadata need not satisfy new rules.

Git reads use argument lists, an explicit cwd, `shell=False`, and raw `ls-tree/cat-file`; they never invoke diff/textconv, clean/smudge filters, hooks, or source commands. Inherited repository, index, and Git-configuration environment variables are cleared; replace refs and lazy fetch are not used; the tool never looks for main/master or a newer HEAD. Failures keep their diagnostics and return an input error.

Each Git call sets `GIT_CEILING_DIRECTORIES` to the parent of the selected root; missing or incomplete metadata returns `BASE_UNAVAILABLE` instead of borrowing an ancestor repository. The host Git's `GIT_EXEC_PATH` is kept. The repository's own configuration takes effect under native Git rules and is not parsed separately. The [Git invocation environment](../../docs/domain-sources.md#git-config-boundary) describes its scope; ordinary local content inputs without Git need no repository.

<a id="checker-output"></a>
### JSON fields, counts, and stable codes

Report and internal records are immutable dataclasses; `report.to_dict()` is directly JSON-serializable (tuples become arrays, missing values `null`):

| Field | Actual representation |
|---|---|
| `status`, `findings`, `checked_count`, `baseline`, `excluded`, `attempted_count` | Top-level fields; `checked_count` is the number of formal files successfully parsed and body-checked, including files with violations; `attempted_count` also counts recognized formal candidates that failed to parse or be read. If a directory cannot be read, candidates may not be listed yet; the status is still an error |
| `findings[]` | `{code, path, line, owner, target, message, related}`; `path` is the actual absolute path or the string of an invalid input; `line` is 1-based; `owner` is `scope/id` once parsed, else `null`. Link findings locate the referencing line and the original target; for duplicate IDs, `related={path,line}` is the first occurrence and the primary location is the second |
| `baseline` | `null` when the root/base fails before reading; otherwise contains `root`, `target="working-tree"`, `base_sha`, `base_tree`, `comparison_complete`, `snapshot_sha256`, `files`, `base_files`, `changes` |
| `baseline.files[]` | `{path, sha256, size, role, owner}`; root-relative path and SHA-256/size of the raw bytes actually read (BOM/newline differences preserved); `role=formal/guide/reference`. Includes guides read for selection and local references. Not a digest of the whole repository or of the tool source/schema |
| `baseline.base_files[]` | `{path, blob, sha256, size, formal}`; Git blob ID, raw-byte digest, and selection signal of eligible historical Markdown; historical schema not parsed |
| `baseline.changes[]` | `{path, status, base_blob, before_sha256, after_sha256}` over the union of formal paths; `status=added/modified/deleted`, with `null` when a side does not exist; not a whole-repository diff |
| `baseline.comparison_complete` | `null` without a base; `false` when the base comparison hit a read/path problem (only known comparisons are listed; a missing read is never presented as a deletion); `true` for a normal read. Does not mean the metadata/documents are valid |
| `baseline.snapshot_sha256` | SHA-256 of the path-sorted `files` array encoded with `json.dumps(sort_keys=True, separators=(",", ":"))`; identifies this run's read set and never labels a dirty working tree as plain HEAD |

Each input is read once per check; later references share those bytes. The read set is not a file-system transaction: record the tool version, re-check after later file or tool changes, and do not treat the digest as proof of approval.

`read_inventory(root, base_sha=None) -> Inventory` is reused by tools in this directory and performs the same single discovery, parse, and check as `run_check`. `Inventory.report` is exactly the `CheckReport` above, plus immutable tuples `artifacts`, `raw_files` (actual paths and bytes read), and `base_raw_files` (historical paths and raw blob bytes), so consumers never re-read Markdown. Historical parsing uses the original parser's byte entry point. Standalone YAML/JSON uses `load_yaml_mapping(text, path)`: the same SafeLoader, duplicate-key/alias checks, and 1-based locations, with no separate frontmatter or owner parser.

| Stable code | Classification |
|---|---|
| All parser input errors above (including `DUPLICATE_ARTIFACT_ID`) | `input-error`; never swallowed or turned into an empty object |
| `MISSING_TITLE`, `EMPTY_TITLE`, `MULTIPLE_TITLES` | `invalid`; H1 structure |
| `INCOMPLETE_ARTIFACT` | `invalid`; explicit residual placeholder |
| `BROKEN_LINK`, `BROKEN_ANCHOR`, `UNRESOLVED_REFERENCE`, `UNSUPPORTED_FRAGMENT`, `INVALID_LINK` | `invalid`; local link or supported scope |
| `DIRECTORY_READ_ERROR`, `EXCLUDED_TARGET` | `input-error`; read or boundary failure; other path and decoding codes reuse the parser codes |
| `INVALID_BASE`, `BASE_UNAVAILABLE` | `input-error`; base shape, or failure to read the exact object |
| `REPORT_CONFLICT`, `REPORT_WRITE_ERROR` | `input-error`; output conflict or write failure |

Every tool's explicit output follows one rule in `check_artifacts._output_path` / `_write_new`: a new local file with a matching suffix in an existing parent directory; no overwrite or directory creation; no `:` in the file name (Windows alternate data streams); no writes into `.git`; no overlap with read or declared sources. Paths resolve the host's normal way, with `..` normalized literally. `--report` creates only a new local `.json` file; a relative path resolves against the root, and an absolute path is used as authorized for this run. Exclusive create failures exit 2; a write that fails after creation may leave an incomplete report, which is not evidence of success. `report_output={path,written}` is independent of the protected input read set, and the default mode and API never produce this file. argparse usage errors go to stderr with exit 2; other defined errors are returned in the JSON.

<a id="traceability"></a>
## Complete delivery coverage

```python
trace_report(root, delivery_ids) -> CheckReport
```

Import it from `check_traceability` in this directory. `delivery_ids` is the **complete set of delivery acceptance criteria** given by the caller; each item must be the `scope/id#anchor` of an actual owner, not a file title, a short ID, or a list inferred backwards from VTs. An empty collection, a single string, or invalid, duplicate, or unknown items are all input errors. The complete formal inventory is read first and AC/VC are extracted from their owners; other artifacts may serve as reference context but never automatically become part of "this delivery".

Every actual `targets` entry is reverse-checked, including targets outside the delivery set. A VT or TS counts toward coverage only when its real owner acceptance criterion, compatible layer, and independent criterion all meet the mechanical requirements. The layer comes from the `Verification layer` table row in the VT's `plan` section, or from `Business scope and scenario type` in the TS's `basis` section; it is never inferred from the file name, and frontmatter is not extended. A VT accepts the four explicit form layers (`Business acceptance`, `Software behavior`, `Applicable design verification`, `Standalone maintenance or document check`); a TS accepts an explicit business declaration of `Within context`, `Cross-context`, `REQ business acceptance`, or `QAS`. A missing, multi-valued, or unknown declaration must be reported.

| owner kind | Target layer |
|---|---|
| stakeholder-requirement, use-case, invariant, quality-attribute-scenario, domain-model | business |
| software-requirement | software |
| architecture-building-block, architecture-decision, architecture-specification, sequence-diagram, published-interface | design |
| development-log, backlog-item, user-story, tool-qualification, review-record | maintenance |
| Other kinds | No layer is guessed; reports `UNKNOWN_TARGET_LAYER` |

Criteria come from the existing forms. Under each `criterionAnchor`, a VT needs actual table values in three rows: `Expected outcome and independent pass criterion for this target`, `Corresponding method/steps or actual test identifier`, and `Preconditions, forbidden side effects, and open items`. A TS needs its four form bullets: `Preconditions and inputs for this target`, `Actions, observations, and independent pass criterion for this target`, `Corresponding steps or actual test identifier`, and `Source navigation, open conditions, and forbidden side effects`. An anchor or heading alone, code/comments, placeholders, or a generic "all passed" do not satisfy this. Targets that share an anchor or have identical criterion content are reported as `SHARED_CRITERION`. This is an explainable structural minimum, not proof of natural-language semantics; human review is still needed to judge whether the actual expectation suffices for the original acceptance criterion.

Returned fields, formal-file `checked_count/attempted_count`, and the read-set `baseline` reuse the contract above; they are neither a coverage denominator nor a count of test runs. Parser/inventory input errors take precedence; a parse failure never becomes "uncovered" or success. Additional codes:

| code | Status |
|---|---|
| `INVALID_DELIVERY`, `EMPTY_DELIVERY`, `INVALID_DELIVERY_ID`, `DUPLICATE_DELIVERY_ID`, `UNKNOWN_DELIVERY_ID` | `input-error` / 2 |
| `DANGLING_TARGET`, `TARGET_NOT_ACCEPTANCE`, `INVALID_TARGET_SOURCE` | `invalid` / 1; keeps the actual referencing location/target |
| `UNKNOWN_VALIDATION_LAYER`, `UNKNOWN_TARGET_LAYER`, `LAYER_MISMATCH` | `invalid` / 1 |
| `INSUFFICIENT_CRITERION`, `SHARED_CRITERION` | `invalid` / 1; locates the criterion declaration |
| `UNCOVERED_ACCEPTANCE` | `invalid` / 1; locates the actual acceptance owner, path, heading line, and full target |

The command is `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_traceability.py --root <documentation-root> --delivery <full-acceptance-reference>`; repeat `--delivery` once per delivery ID. stdout is the `CheckReport` JSON, which also keeps the actual `delivery_ids`; `--report <new .json>` follows the protected-output contract. No arguments or wrong usage exits 2; a complete structure with no findings exits 0. This does not mean any VT was run.

<a id="impact-candidates"></a>
## Impact candidates against an exact baseline

```python
impact_report(root, base_sha, task_ids=()) -> dict
```

Also part of `check_traceability`. It uses an explicit full commit and the current working files; it does not pick HEAD or a branch, nor look only at staged content. The base is mandatory in the public API: passing `None` returns `INVALID_BASE` / input-error / 2 rather than falling back to the shared optional-base semantics and a clean empty comparison. It returns the `CheckReport.to_dict()` fields plus:

- `changed_sources`: changed formal paths with added/modified/deleted status, the old blob, and before/after SHA256; `before/after` hold the parseable `{key, path, sha256}` and are null when that side does not exist.
- `candidates`: transitive dependency candidates sorted by key, keeping the same `before/after` shape, `requested_task`, and `reasons`. Each reason has the actual `source/consumer/reference/relation/path/line/snapshot`; `relation` is upstream or target; `snapshot` is base or current.
- `task_ids`: keys of existing formal tasks explicitly specified by the caller (not an acceptance set); an empty list is allowed; invalid, duplicate, or unknown items report `INVALID_TASK* / DUPLICATE_TASK_ID / UNKNOWN_TASK_ID` respectively. Unsupplied tasks are never invented.

Changed owners are the seeds in `changed_sources`; other reachable owners are candidates. The dependency graph merges old and new sides, so deleting a source or removing a reference does not erase the historical chain, and cycles are visited once. A numeric-only change in a rule file can also reach REQ/SR, VT, and tasks through canonical references. An unparseable historical formal file reports `HISTORICAL_INPUT_ERROR` / 2 and keeps known candidates without pretending to be a complete comparison. Unlike the raw historical byte comparison of `run_check`, this interface also parses historical identities.

The CLI uses `--base <full commit>` instead of `--delivery` and accepts repeated `--task <scope/id>`; the two modes are mutually exclusive. The report can still be written explicitly to a new `.json`. Candidates are not a final conclusion on severity, approval, or business impact. Non-canonical lightweight links, semantically implied dependencies, and unknown sources outside scope must still be added per the [shared impact method](../skills/verify-change/SKILL.md#impact). The tool does not change rules, run VTs, or rewrite old results.

<a id="model-export"></a>
## Nine-view reference model and drift check

```python
export_view(root, scope) -> dict
check_model(root, scope, model_path) -> CheckReport
```

Import them from `export_model` in this directory; neither API writes files. The primary input reuses the complete inventory and actual read set. The selected scope must exist in real formal artifacts, and same-numbered IDs from different scopes are never mixed. All formal sources must be valid, and canonical upstream/targets must locate a real owner/anchor; an invalid root, scope, contract, or inventory cannot be masked by nine empty views. The export API raises `ArtifactInputError` (code/path/line); the check API and CLI map it to input error / 2.

The [optional model-sources contract](../contracts/README.md#model-sources) selects each scope's Markdown or YAML/JSON summaries. A missing manifest, scope registration, or view each produces a specific gap; the primary index stays usable. An invalid manifest gives `INVALID_SOURCE_MANIFEST` / 2. A single optional source that is missing, unreadable, or has a format or baseline problem makes its view `unverified` with refs cleared; readable but incomplete fields or entries give `partial`; a complete source gives `available`. The nine original keys are never omitted, and values, body text, and results still belong to the source; approval is never inferred from a state. An optional-failure gap carries the selected path, the actual failing source, and the code; personal absolute paths and raw sensitive exception content are never output.

Direct quality checks cover the actual QAS and the utility-tree source (an existing file with a top-level `tree` mapping/list can be selected explicitly); a missing source gives unverified, and only missing fields/entries in a known source give partial. Direct verification reads owned child run blocks and the four-column result table of the current VT form, records missing items/conflicts per run, and keeps original anchors. Automated/manual counts are never derived from totals, and content from adjacent runs or criteria is never stitched together. SEQ completeness reads the real diagram code under the shared comment/fence state, without rescanning raw literal examples. Contract notes remain authoritative for source shapes.

The primary `source.root` is always the portable `.`. Each artifact baseline is the `sha256:` of the raw bytes actually read (including BOM/newlines); upstream/targets, artifacts, views, refs, and gaps are sorted deterministically. The primary `source.baseline` is the `sha256:` of this object, encoded as UTF-8 with `json.dumps(sort_keys=True, separators=(",", ":"))`: `scope`, the Task6 `files` read-set records sorted by path, `manifest: absent/present`, the sorted optional failures `(selected path, code)`, and the raw digests of the artifact/model/model-sources contracts used; with the implementation-report adapter, also the bc-config/implementation-report contracts. The read set includes selection guides, the manifest, actual optional YAML/JSON, and evidence files, not only formal Markdown. There are no timestamps or random data; the tool version is saved separately with the check record.

Canonical references also keep the evidence baseline of their actual owner file, so cross-scope consumers can trace back to the source. Mentions in code, table headers, or ordinary AC text never become source fields or owner acceptance criteria. Each file is read once per derivation; this is not a file-system transaction, so do not modify sources during derivation.

`check_model` reads an explicit local `.json/.yaml/.yml` (possibly a separately authorized model file outside the root), validates it, and recomputes. A changed primary source identity is `STALE_MODEL_SOURCE` / 1; a hand-edited structure with the same source is `MODEL_MISMATCH` / 1. An invalid persisted model, schemaVersion, or scope is an input error / 2. It does not repair an old model; a derived model cannot serve as a source or source evidence, and manifest self-references are rejected.

An implementation report must be selected separately and explicitly among the manifest's `verification` sources. A dedicated adapter checks the v1 schema, scope, and report baseline and rebuilds the report read-only from its exact object/owned VT references. A hand-edited report that cannot be rebuilt is `REPORT_MISMATCH`; a missing or drifted raw report only leaves a gap in that optional view; a schema-valid pass claim alone is not accepted. The model's `implementationReports` and the verification view store only `reference + baseline`, not entries, execution, or applicability. The other eight views and existing sources are not replaced; with no report selected, `implementationReports` stays empty. `available` only means the reference can be checked, not that execution passed.

| CLI arguments (all require `--root` and `--scope`) | Output and exit |
|---|---|
| No output argument | Validates and derives to JSON stdout without creating files; exits 0 when the primary input is derivable, even with optional gaps |
| `--check <existing model>` | JSON CheckReport; 0 for no drift, 1 when drift is found, 2 for input errors |
| `--output <new model>` | Explicitly exclusive-creates a local `.json/.yaml/.yml`; stdout is still the schema-valid model; parent directory must exist |

`--check` and `--output` are mutually exclusive. Output reuses the Task6 local/conflict constraints: no existing source, model, report, empty file, or directory is overwritten, and nested source/evidence locations declared in the manifest or a selected YAML/JSON source cannot be taken by the model even if missing. Every `reference` and `path + baseline` location in the whole parsed document is registered before any is dereferenced; a failure on an earlier item does not skip protection of later declarations. Registration grants no read permission and never makes unread data usable.

A declared location that is invalid and cannot be registered safely still lets the default read-only derivation report an optional gap, but explicit output returns `REPORT_CONFLICT` rather than implying isolation. The same applies to an incomplete or unresolvable `domainSources` declaration; a resolvable location still protects all its child paths. An explicit implementation-report domain `root/path` is registered before verification, protecting it and its child paths without requiring the baseline to exist or be valid. Registration does not mean the data is readable, valid, or authorized for writing. A normal new output can be exported and then checked; it does not automatically become its own source. `REPORT_CONFLICT / REPORT_WRITE_ERROR` exit 2; a primary-input failure creates no output, and a write failure may leave an incomplete new file. There is no network access, fetch, filters/textconv, hook, or source-command execution, and manifest baselines are never revised automatically.

<a id="implementation-report"></a>
## Collecting implementation summaries from existing VTs

```python
build_report(root, object_sha, evidence_files, *, scope=None) -> dict
```

Import it from `collect_implementation_report` in this directory. The API is read-only and returns the existing [implementation-report v1](../contracts/README.md#implementation-report), with no root-level execution or views. The contract defines the complete fields and the supported **VT selection, original form fields/baselines, comment markers, and applicability syntax**; there is no separate input manifest or copied result ledger. The [blank report form](../../_templates/reports/implementation-report.yaml) only guides structure; it is not an actual result.

- Primary BC configuration, owner acceptance criteria, and code/test locations come from the given full local commit, not HEAD, the index, or current files. With multiple configured contexts the scope must be explicit; collection fails with no actual scope or acceptance criterion.
- The supplied VT may have records appended after the object; only owned child runs of the original owner at the same path are accepted, and a file with multiple runs requires an anchor. The original record bytes, test object, requirement baseline, VT plan, and raw report are each verified; new evidence is never labeled as part of the old object's bytes.
- Each target is handled independently. A target without a selected run is not-run, with empty evidenceRefs and a reason; fail/skipped and their reasons are kept. A raw report, a located test text, Approved, a zero count, all-skipped, or an available view cannot substitute for execution.
- Source runs, reports, dates, observations, and commands are **collected data**, not results of the collector's own run. The collector executes no source commands or applications/tests, cannot authenticate people, and cannot prove external events happened. Manual records use concrete steps; auto/manual counts are never invented.
- Domain inputs are read and compared using the configured root/path and fixed baseline, never written back. The object root is `.`; no personal absolute paths, raw sensitive body text, or business summaries are copied.

| CLI arguments | Behavior and exit |
|---|---|
| `--root <checkout> --object <full commit>` | stdout is the per-target report and no file is written; repeat `--evidence <VT-relative-path[#run-anchor]>`, and add `--scope <project/context>` for multiple BCs |
| Add `--output <explicit new .json/.yaml/.yml>` | Exclusive create; parent directory must exist; no report directory is created and source selection is unchanged. An existing source path, or a registered or referenced one even if missing, can never become the output |
| Successful collection with no fail | Exit 0; may include targets that are not-run or skipped. Means only that collection completed, not that targets passed |
| A target was collected as fail | Still outputs the complete per-target report and exits 1; never changed into success |
| Input/source/output error | JSON `status: input-error` with findings carrying code/path/line/message, exit 2; no forged empty success |

Diagnostics include `INVALID_BASE / BASE_UNAVAILABLE / OBJECT_PATH_MISSING / BASE_MISMATCH / PLAN_MISMATCH / OBJECT_MISMATCH` (object/source), `AMBIGUOUS_SCOPE / INVALID_SCOPE / UNKNOWN_SCOPE / EMPTY_ACCEPTANCE` (scope), `INVALID_EVIDENCE_OWNER / SCOPE_MISMATCH / REQUIREMENT_MISMATCH` (owner), `DUPLICATE_EVIDENCE / AMBIGUOUS_RUN / UNKNOWN_RUN / AMBIGUOUS_RESULT / INVALID_RUN` (selection/records), `INVALID_EXECUTION / INVALID_OBSERVATION / INVALID_EVIDENCE / MISSING_TEST_REFERENCE / INVALID_MARKER` (actual location/evidence), and `INVALID_APPLICABILITY / AMBIGUOUS_APPLICABILITY` (independent re-review). Shared file/schema diagnostics are kept; `REPORT_CONFLICT / REPORT_WRITE_ERROR` never silently overwrite an old report.

The report can be rebuilt but is not a source transaction: each file is read once per collection, so do not modify sources during collection. An interrupted write may leave an incomplete new file, which the next run still refuses to overwrite. A domain source's `readOnly: false` does not authorize writes; no hooks, filters, replace-refs, fetch, or configuration commands run.

<a id="template-update"></a>
## Read-only template and explicit BC scenario proposals

`plan_template_update.plan_update(base, local, candidate) -> UpdatePlan` compares three real roots and returns `changes/conflicts/preserved/sources`, writing no sources or output. A narrow `TreeSource(root, version, files)` supplies an exact local Git/content identity and a consistent file scope; a missing old baseline, read failure, or wrong version fails immediately. `plan_batch(registration, target_ids) -> BatchPlan` maps `.feature` files only for explicitly registered or selected BCs, keeping source scenarios, repository/context/version, allowed files, and an independent result per target; it does not propagate the model or the whole repository.

The [complete contract for inputs, digest recipes, the 16 decision classes, registration, states, and output](../../docs/template-updates.md) is maintained only in the update guide; the [shared method](../skills/update-template/SKILL.md) handles judgment and stop points. The CLI defaults to stdout. Three-root mode: `--base <old-root> --local <local-root> --candidate <candidate-root>`; batch mode: `--registration <local-registration> --target <explicit-ID>` (repeat per target). `no-change/proposed` exits 0, `conflict` exits 1, and `unavailable` or any input/output error exits 2. A clean proposal may contain additions, modifications, and deletions; it is not a successful apply. An explicit `--output <new .json>` must lie outside all input and registration locations; it creates no parent directory, never overwrites history, and cannot take a missing or unselected target root.

Input parsing, safe YAML, and restricted raw Git helpers reuse `artifact_io.py` and `check_artifacts.py`; the existing locked dependencies suffice, with no maintainer tests, maker materials, workflows, or new dependencies. There is no `--apply`, clone/fetch, commit/push, PR, external-source write-back, or background sync. Owner business data, original rules, and deliberate deletions are preserved; raw bytes and source drift are checked against the full contract.

<a id="domain-sources"></a>
## Optional local domain-source preflight and explicit onboarding

`setup_domain_source.inspect_domain_source(root, source_config) -> dict` is read-only by default. It checks the real root/path/fixed baseline against the six source fields of the original BC and returns `ready / conflict / unavailable` with 0/1/2, plus exact paths, ownership declarations, targets, and proposed operations. Sources, index, config, refs, and objects are not written; there is no fallback to HEAD or a remote. Network addresses are rejected before Git or credential tools are called, and the original URL is not echoed.

`apply_domain_source` writes only when the operation, existing configuration, exact preflight, and target ownership declaration are all given explicitly. Register only appends a source entry to the BC and does not materialize or stage anything. The optional local submodule does not edit the BC configuration; it requires a separately given exact target plus separate consent for the index change. Raw blob writes bypass checkout/filters/hooks, native metadata and gitlink changes are disclosed item by item, and no commit or push is included. A non-empty target, alias, conflict, or drift is never skipped as success.

The BC token identifies only the raw configuration bytes actually used for parsing/planning; a change detected by a later read during inspection is also rejected. A new native target never revives a `.gitmodules` from HEAD whose deletion the owner has staged, and the target cannot occupy a metadata file. The shared Git reader and native helper use the same clean Git environment and selected-root discovery ceiling described in the [checker baseline](#checker-baseline).

The complete API/CLI, editable configuration layout, native commands, and recovery boundaries for retained partial state are in the [domain-source guide](../../docs/domain-sources.md); the fields still belong to the [original contract](../contracts/README.md#bc-configuration). The tool reuses the safe YAML/schema reader of `artifact_io.py`, the path/Git boundaries of `check_artifacts.py`, and the fixed-commit/raw-byte comparison of `source_baseline.py`, which the implementation-report collector also shares; no second baseline parser or source model is maintained. Core dependencies are unchanged and nothing extra is installed.

## Scope of use

Downstream use needs only the modules in this directory (including the shared `vt_records.py` and `source_baseline.py`), the sibling dependency manifests, and the adjacent contracts, not maker specifications, run logs, or maintainer regression tests. The local architecture/presentation tools also reuse the output and safe-encoding helpers of `render_traceability.py`; the complete usage guide is the [export contract](../../docs/document-exports.md). Each capability above keeps its own boundaries and does not substitute for the others; links and semantics of ordinary guides still need review. No tool runs `.feature` files, applications, or business VTs, and none authenticates approvers.
