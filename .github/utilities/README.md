# Local maintenance tools

This directory provides parsing, formal-artifact checks, coverage and impact candidates, a deterministic reference model, read-only implementation-report collection, three-way and explicit multi-target update proposals, explicit local source preflight and onboarding, local document/transcript candidates with transparent scoring, and sourced local exports of relationship graphs, architecture views, and presentations. The optional hook adapter and installer entry points are described in a later section. These tools are not an application, a unified CLI framework, a general-purpose executor, or a global library. Schema fields and complete examples are maintained only in the [contract notes](../contracts/README.md); these mechanical tools do not prove business execution or approval.

## Tool environment

The tools require Python 3.11+ and target Windows, Linux, and macOS. The environment and command registration are in the [maintenance tools section of the development guide](../../docs/development.md#maintenance-tools), kept separate from downstream business applications; maker-repository regression tests and run history are not prerequisites for downstream use. Locations are determined by explicit arguments and project-relative resources; no specific drive letter or directory is required. The checkers serve only DDD artifacts, references, coverage, and derived results; they are not a file-system audit or a sandbox.

- [requirements.txt](requirements.txt) lists only the approved PyYAML 6.0.2 and jsonschema 4.23.0; these are the locked and tested versions. At run time, the tools only require both to be importable.
- [requirements.lock](requirements.lock) keeps the six versions actually resolved in a Python 3.13 environment, plus a conditional `typing-extensions==4.16.0` entry that Python `<3.13` needs and that was verified by an actual install on 3.11; 3.11 selects seven entries and 3.13 still selects the original six. The condition comes from the package metadata of `referencing` and does not upgrade the original pins. pip is an environment installation tool, not a runtime dependency of the tools; no hashes were guessed.
- On Windows, from the repository root, run `python -m venv .venv`, restore the locked environment with `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.lock`, and then run `.venv\Scripts\python.exe -m pip check`.
- No environment activation or global pip is needed; there are no media packages, extra DOCX/PDF packages, binary-format renderers, cloud SDKs, or application dependencies. The narrow DOCX adapter uses stdlib ZIP/XML; the [optional media manifest](requirements-media.txt) selects no packages. Local JSON/SVG/HTML output uses the stdlib, and the [rendering manifest](requirements-rendering.txt) selects no PDF/PPTX engine. Other hosts use their actual `.venv/bin/python`; users must verify the local interpreter and the installed dependencies.

<a id="interaction-ledger"></a>
## Explicit interaction ledger and usage summary

`append_record(log_path, InteractionRecord, *, attest_local_storage=True)` in `log_interaction.py` accepts only values that the caller supplies explicitly; `summarize_usage(log_path)` in `summarize_usage.py` returns the source SHA-256, record and unknown counts, and known-usage groups in deterministic order. Explicit summary output uses `write_summary(log_path, output_path, *, attest_local_storage=True)`. Neither reads full prompts/chats, the environment, a personal `models.json`, credentials, billing, application output, or vendor services, and neither executes any field text. When there is no usage, the value, unit, and currency are all left empty; unknown is not zero. The summary sums exact decimals only across records with an identical tool, version, unit, and currency; it does not estimate prices or draw cost or savings conclusions.

The fixed CSV v1 columns are:

```text
schema_version,record_id,recorded_at,tool_name,tool_version,task_ref,object_ref,object_baseline,operation_summary,decision_ref,usage_value,usage_unit,usage_currency,evidence_ref
```

Field meanings, the minimal data boundary, and limitations are in the [AI tooling guide](../../docs/ai-tooling.md#interaction-ledger). [`_templates/reports/ai-interaction-log.csv`](../../_templates/reports/ai-interaction-log.csv) is a blank header to copy, not an active ledger; first copy it yourself to a new `.csv` in an existing local directory, and never write to the template directly as a ledger. The API/CLI require an explicit absolute path to an existing regular file with an existing v1 header; they do not create parent directories or repair bad records. Every row must carry a timezone-qualified time `YYYY-MM-DDTHH:MM:SS[.fraction](Z|±HH:MM)`; the original literal text of the time and usage is preserved, and usage values accept only finite, non-negative plain decimals, not exponent notation. The summary is at most 512 characters; callers must not put complete interactions or sensitive data into it.

Cross-platform read/write boundaries:

- Every write path requires caller attestation: `attest_local_storage=True` in the API or `--attest-local-storage` on the CLI. Without it, the request is rejected with `WRITE_ATTESTATION_REQUIRED` and no lock or output is created. The attestation is the user's declaration that the selected directory is single-machine local storage, not a network or cloud-synced location; it is not OS or vendor verification or a durability guarantee, and the tools do not inspect fixed drives, the registry, or vendors.
- Appends use an adjacent `.lock` file to serialize tool processes on the same machine; Windows uses `msvcrt` and Linux/macOS use `fcntl`, and the lock sidecar file is kept. Before writing inside the lock, an append verifies that the ledger bytes are unchanged; this is the only change detection. The default summary without output reads once, takes no lock, and creates no file; corrupt or partial lines are not counted. The cross-module public interfaces are `read_ledger`, `file_lock`, `validate_existing_log`, `validate_new_output`, `require_write_attestation`, and `emit_error`.
- Explicit `write_summary`/CLI `--output` requires attestation, uses the source lock and standard-library exclusive creation, and never overwrites an existing file or creates a missing parent directory. It preserves read/write consistency and recovery information for partial failures, but it does not bind native directory handles or guarantee isolation against malicious concurrent path replacement; it does not automatically delete or rebuild output.
- A OneDrive-synced directory has no cross-host coordination guarantee even when it is mapped to a fixed drive, so callers should not attest to it. CSV is a data-interchange format, not a spreadsheet-safe format; references and cell contents are not executed.

CLI examples (replace angle-bracket values with the values supplied for this call; paths must be absolute and may contain spaces inside the quotes):

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\log_interaction.py --log "<absolute-local-ledger.csv>" --record-id "<id>" --time "2026-10-18T12:34:56Z" --tool "<caller-supplied-name>" --tool-version "<caller-supplied-version>" --task-ref "<task-reference>" --object-ref "<object-reference>" --object-baseline "<object-baseline>" --summary "<brief factual summary>" --attest-local-storage [--decision-ref "<pointer>"] [--usage-value "<decimal>" --usage-unit "<unit>" [--usage-currency "<currency>"]] [--evidence-ref "<pointer>"]
.venv\Scripts\python.exe -B -X utf8 .github\utilities\summarize_usage.py --log "<absolute-local-ledger.csv>"
.venv\Scripts\python.exe -B -X utf8 .github\utilities\summarize_usage.py --log "<absolute-local-ledger.csv>" --output "<absolute-new-summary.json>" --attest-local-storage
```

CLI exit 0 means the append, identical replay, or summary request completed; exit 1 means a record-input error or a record ID conflict; exit 2 means a path, log, lock, output, or recovery error. The default summary does not print the source path and refers to the source bytes only by hash. The tools describe only reproducible local behavior; they cannot verify the real tool, service provider, billing, human decisions, or qualification.

<a id="document-exports"></a>
## Sourced relationship graphs, architecture, and presentations

`render_traceability(view)` reads an explicit root/scope and produces JSON/SVG/HTML showing the
actual dependency direction, complete owner/anchor, isolated nodes, cycles, and source gaps. `render_architecture(inputs, format)`
and the required `render_presentation(inputs, format)` read explicit source pointers and fixed baselines and
output HTML/SVG driven by source sections; a limited SEQ subset actually draws participants, messages, and branches.
Copied code is not presented as a visualization, and transport is not inferred from arrows.

The [single contract for inputs, returns, limited syntax, CLI, errors, and writes](../../docs/document-exports.md)
describes the specific fields. These tools reuse the real inventory, the nine views, `check_model`, and the source and report adapters;
they do not accept an arbitrary schema-valid model as fact. An empty trace produces no demo; missing sources keep the nine-view gaps;
drift, wrong sources, or unsupported SEQ produce explicit diagnostics.
The parser's `section_fences(artifact, anchor)` only projects the closed fences owned by an already parsed Artifact and shares the original comment/literal state machine with the model;
it adds no new file parser or authorization boundary.

The API and the default CLI do not write. The only file written is an explicit new output, created exclusively. Its parent directory must exist,
and the output is rejected if it conflicts with a source or history path, a declared-but-missing location or its ancestor/child paths, or a case/alias conflict. There are no CDNs, remote fonts,
scripts, source commands, or automatic downloads. PDF/PPTX have only an unavailable/not-run rejection contract,
which is not success in that format; the actual engine, dependencies, signature/parser, non-zero pages/slides, source content, and human/App
gates still require separate authorization and execution. A local export is not SWAS approval or complete equivalent acceptance.

<a id="source-candidates"></a>
## Local source candidates and scoring

`extract_source.extract_candidates(source, kind)` reads only an explicit absolute local file and returns the actual
byte identity/read count and a `candidates` list; it supports Markdown/plain text, strict JSONL transcripts, and
bounded stdlib DOCX. `score_candidates.score_candidates(items)` keeps duplicate and contradictory sources and returns
public 0–100 factors with reasons; these are not probabilities or acceptance thresholds. The single description of types, locations, input limits, CLI, and errors
is the [source-candidate contract](../../docs/source-extraction.md); it is not added to the formal-artifact schema.

The complete normalized source unit and its classification must agree; qualifiers cannot be dropped by matching a substring. Markdown candidates use the
preceding-comment context produced by the same scanner. This context is not a caller override of the visible body, and it is not source authentication.
The envelope also checks the declared total unit count, format-specific coordinates/order, and empty-unit relations, and scoring happens only when all are valid;
a bare list does not invent a total or drop duplicate sources. A DOCX table without a grid keeps the rectangular limit based on the first-row width.

The API and the default CLI do not write. Explicit output only creates a new JSON file exclusively, inside the root, and never creates directories or
overwrites declared inputs. `transcribe_audio` currently has only a rejection entry point (authorization/missing items/unavailable); it does not read audio or environment secrets,
install SDKs, or call services. Candidates still go back to the [shared reverse-engineering method](../skills/reverse-engineer-domain/SKILL.md)
for checking and clarification; the tools cannot record them as confirmed facts.

<a id="native-hooks"></a>
## Optional native hooks and same-source CI

The [hook guide](../hooks/README.md) defines the installation proposal, explicit apply, per-path recovery, index semantics, and
the `Reviewed-by` text policy for managed paths. By default `install_hooks.py` does not write; it rejects existing hooks,
configuration conflicts, and shared worktree metadata, and it never modifies Git configuration or commits/pushes automatically.
When installation I/O fails, it keeps and itemizes everything this run fully or partially created; it does not guess at or delete owner content added later.

`hook_checks.py pre-commit --root <checkout-root>` can also be called directly with the selected project Python;
it uses the actual index and raw blobs rather than working files, and accepts an exact `--base` and a new `--report`.
Both Python hook entry points and the downstream documentation workflow reuse this module. The adapter handles only snapshots/context and
format policy; artifact, Markdown, owner AC/VC, and coverage rules still belong to the three existing modules.
Before reading the index or artifacts, the entry point only confirms Python 3.11+ and that PyYAML and jsonschema are importable;
a venv, conda, or system interpreter all work, and it does not check pinned versions, `pyvenv.cfg`, or the prefix.
The selected path/prefix passed by the launcher is only recorded in the report and is never a reason for rejection; the entry point never switches interpreters on its own.
The private `_base_root` of `read_inventory` only lets a temporary snapshot obtain historical raw objects from the original Git root;
`_trace_inventory` reuses the same already obtained inventory and still reverse-checks targets when there are zero owners. The working-tree/non-empty-delivery selection contract of the public local
`run_check` and `trace_report` is unchanged.

These entry points must be distributed together with `artifact_io.py`, `check_artifacts.py`, `check_traceability.py`,
`artifact.schema.json`, and the dependency manifests. The maker repository's test runner/workflows, test data,
research, and history records do not become downstream dependencies. Native Git failures and the JSON exit codes 0/1/2 are each preserved;
an empty inventory is not a business pass, local format checks do not authenticate the reviewer, and the presence of the workflow YAML does not mean hosted CI has run.

## Parser interface

Later scripts in the same directory import this module directly. It provides no command-line entry point that would fake success. Callers explicitly supply the real root directory and files for each call rather than relying on changing the cwd, automatic scanning, or business command registration.

```python
parse_artifact(path: str | os.PathLike[str], root: str | os.PathLike[str]) -> Artifact

parse_artifacts(
    paths: Iterable[str | os.PathLike[str]],
    root: str | os.PathLike[str],
) -> tuple[Artifact, ...]
```

A relative `path` is resolved against the explicit `root`; the root must be an actual directory, and each input must be a readable regular file inside the resolved root. A path that escapes the root after symlink or junction resolution fails; a missing file, wrong type, garbled text, or failed read is not an empty artifact. UTF-8 with or without BOM, LF/CRLF, and paths containing non-ASCII characters and spaces are all covered by real-file tests. There is no guarantee against another process maliciously replacing a path between the check and the open; this is not an operating-system sandbox.

`parse_artifacts` processes only the explicitly given collection and keeps the input order; for a duplicate scope/id, it reports the locations of both the second and the first occurrence. The same ID in different scopes is valid. An empty collection returns an empty tuple but still validates the root; this does not mean business coverage is complete. Parsing a single file never scans other files for deduplication.

All returned records are `frozen=True, slots=True` dataclasses, and collections are tuples:

| Type | Available fields |
|---|---|
| `Artifact` | `schema_version`, `id`, `kind`, `scope`, `content_state`, `upstream`, `targets`, `confirmation`, `path`, `relative_path`, `location`, `id_location`, `body_start_line`, `source`, `body`, `anchors`, `acceptances`, `metadata_locations`; derived properties `key` and `acceptance_ids` |
| `SourceLocation` | `path: Path` (actual absolute path), `line: int` (1-based) |
| `Target` | `target`, `criterion_anchor`, `test_id: str \| None`, `location`, `criterion_location` |
| `Confirmation` | `by`, `reference`, `baseline`, `location`; presence does not mean the approver has been verified |
| `Anchor` | `name`, `location` |
| `Acceptance` | Full heading `id`, `owner` (scope/id), `anchor`, heading `location`, `anchor_location`; derived property `reference` (scope/id#anchor) |

`source` is the original text with the UTF-8 BOM removed, and `body` starts after the closing frontmatter delimiter line; both keep the original LF/CRLF and are never reflowed or written back. `body_start_line` and the target and acceptance locations let later checks locate findings; `relative_path` is the resolved root-relative path using `/`. Callers must read raw bytes separately; the decoded `source` cannot substitute for a byte digest of the original file.

`metadata_locations` is a tuple of `(field-path tuple, SourceLocation)` pairs from the same YAML parse, for example `("scope",)` or `("targets", 0, "target")`; it is not a second field parser. The shared `iter_markdown_lines(body, start=1)` keeps line numbers, removes HTML comments, and returns `None` for code lines, so the parser and the checkers treat literal content the same way. `iter_markdown_fences(body, start=1)` returns genuinely closed `MarkdownFence(start_line, end_line, info, body)` values from the **same** state machine; fence examples inside comments or enclosing code do not become new code blocks. Owner acceptance criteria still come only from the original parser's explicit anchors and owned ID headings.

Source candidates can use `iter_markdown_source_lines(body, start=1, *, initial_in_comment=False)` to obtain
`(line, visible_or_None, incoming_comment_bool)`; the keyword-only initial state exists only to replay a complete source unit
and still delegates to the same state machine. The original line/fence interfaces and formal identity behavior are unchanged, and an unsupplied source prefix is not authenticated.

## Input errors

The stable attributes of `ArtifactInputError(ValueError)` are `code`, `path`, `line`, and `message`. Its string contains all four; YAML, decoding, file-read, and schema failures keep the original exception chain. If a path cannot be established yet, `path` holds a readable form of the input; errors before the file is read use line 1, and empty metadata uses line 2.

| code | Condition |
|---|---|
| `INVALID_ROOT` | Root of the wrong type, empty, missing, unreadable, or not a directory; in both APIs `path` is the string representation of the invalid root and the line is 1; an empty selection cannot bypass this |
| `INVALID_PATH` | Invalid input type/path, an ambiguous drive-relative path, a directory, or another non-regular file; a single path passed to the collection interface by mistake |
| `OUTSIDE_ROOT` | A normalized path, symlink, or junction target escapes the explicit root |
| `FILE_NOT_FOUND` | The file inside the root does not exist |
| `FILE_READ_ERROR` | stat/read failed; keeps the specific OS error and never defaults to an empty body |
| `INVALID_ENCODING` | UTF-8 decoding failed; the line number is computed on the decoder's original input, so failures with a BOM are not offset either |
| `MISSING_FRONTMATTER` / `UNTERMINATED_FRONTMATTER` | The file does not start with `---`, or the closing `---` is missing |
| `INVALID_YAML` | YAML syntax error, non-string mapping key, unsafe/unknown tag, circular alias, or exceeding the parser nesting limit |
| `DUPLICATE_YAML_KEY` | A duplicate key at any depth, including a duplicate `<<` and overrides after a merge; the raw node graph is checked first so that normalization cannot swallow duplicate keys |
| `INVALID_METADATA` | Not a mapping, missing fields, malformed scope/id/relations/confirmation, unknown fields, or duplicate relation records |
| `UNSUPPORTED_SCHEMA_VERSION` | Not a genuine integer 1; no fallback parsing |
| `INVALID_KIND` / `INVALID_CONTENT_STATE` | Not in the fixed contract enumeration |
| `MISSING_ACCEPTANCE_ANCHOR` / `DUPLICATE_ANCHOR` | An owner acceptance heading lacks its matching explicit anchor, or a body anchor is not unique |
| `MISSING_CRITERION_ANCHOR` | A target's criterion anchor is not in the current body |
| `DUPLICATE_ARTIFACT_ID` | The same scope/id appears twice within the explicit collection; neither merged nor dropped |
| `CONTRACT_ERROR` | The local artifact schema cannot be read/parsed/validated, or contains a non-local or unresolvable `$ref` |

Parsing uses SafeLoader; it does not construct Python objects or execute YAML/Markdown/referenced commands. Valid, non-circular YAML aliases that do not introduce duplicate keys are parsed; a malformed `upstream` or `targets` value that is present is reported as an error first and is not replaced by an empty tuple. The schema cache is limited to the current process; after changing the local contract, reload it in a new process rather than reusing the old cache.

<a id="artifact-checker"></a>
## Formal artifact checker

```python
run_check(root: str | os.PathLike[str], base_sha: str | None = None) -> CheckReport
```

Import it from `check_artifacts` in the same directory. The API does not write files, change the cwd, or execute commands found in sources; `root` must be an explicit local directory. By default the CLI only prints UTF-8 JSON to stdout:

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_artifacts.py --root .
```

In this example the cwd is the repository root and `.` is the currently selected documentation root; other hosts substitute their actual project interpreter. You can additionally pass `--base <full commit>` or `--report <explicit new JSON file path>`. Angle-bracket arguments must be replaced with the real values for this run. No shell wrapper, hooks, or CI are needed; `-B` avoids writing Python bytecode at run time.

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
- The leading frontmatter contains a field signal from `schemaVersion/id/kind/scope/contentState/upstream/targets/confirmation`, or the opening delimiter is missing but such a metadata prefix is still present. A recognizable but invalid `---` on the first line (for example with an extra leading space) also keeps the metadata candidate that immediately follows it; once ordinary body text or code is encountered, the search for a metadata prefix stops. This step only selects files; delimiter validity and the actual fields, types, duplicate keys, version, and confirmation shape are all left to the existing parser.
- An H1 outside code/comments starts with the same kind of formal ID. Exact-base mode also keeps current paths that were historically recognized as formal, so a change cannot be hidden by deleting all metadata.

A formal file with damaged fields or no frontmatter still reports an input error; it is never migrated or rewritten automatically. An ordinary README, note, or old lightweight body with no identity/metadata signal is treated only as a guide; the checker cannot recreate an identity that has been completely deleted. A file with any name (including a README) is still checked as long as it keeps formal metadata.

Each entry in `excluded` is `{path, reason}`; a directory with a trailing `/` stands for its whole subtree. All entries are relative to **this run's root** and never match ancestors of the root, so an independent test root located under the tools' `.venv` can still be scanned.

| reason | Exact exclusion rule |
|---|---|
| `TEMPLATE` | `_templates/` and `.github/pull_request_template.md` under the root |
| `NATIVE_METADATA` | `.github/skills/`, `instructions/`, `agents/`, `prompts/`, `workflows/`, and `.github/copilot-instructions.md` under the root |
| `MAKER_DATA` | `docs/design/`, `docs/plan/`, and `docs/research/` under the root |
| `TEST_FIXTURE` | `tests`, `test`, or `fixtures` directory segments in the relative path |
| `TOOL_DATA` | `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.tox`, or `.nox` segments in the relative path |
| `DIRECTORY_ALIAS` | Directory symlink/junction aliases that point inside the root; the actual directory is scanned only once, avoiding duplicates and cycles |
| `NON_MARKDOWN` / `LIGHTWEIGHT_GUIDE` | Non-Markdown files / Markdown that was read but has no formal signal |

A directory link that escapes the root is an error, not an exclusion; formal inputs do not accept symlinked files. A template or guide inside the root that is explicitly referenced may be read as a link target without becoming part of the formal inventory; Git, environment, and dependency data are never read as link targets. An unenumerable directory, an unreadable file, or garbled text is never treated as empty. UNC/URL roots and UNC local references are rejected before file parsing; network addresses are never accessed. Path resolution is not an OS sandbox and does not guarantee protection against concurrent malicious replacement.

<a id="checker-format"></a>
### Checked Markdown and placeholder syntax

- A formal body needs one non-empty ATX H1 (`# Title`) and must not have a second H1. The parser's checks for metadata, unique scope/id, explicit anchors, and owner AC/VC structure still apply; the same ID in different scopes is valid.
- Supported: single-line inline links/images, angle-bracket destinations, optional single- or double-quoted titles, reference definitions, and full/collapsed reference links; defined shortcut references are resolved too. Paths with spaces use `%20` or `<path with spaces.md>`, and a destination may contain one level of parentheses.
- Local files must exist inside the root. A fragment matches a parser-style standalone `<a id="ascii-anchor"></a>` or an ATX heading slug: lowercased, keeping Unicode letters/digits, spaces, `_`, and `-`, with spaces turned into `-` and suffixes such as `-1` added for repeated headings. Heading slugs serve navigation only and do not replace the explicit anchors of owner acceptance criteria. A fragment on a non-Markdown target returns `UNSUPPORTED_FRAGMENT`.
- Backtick/tilde fenced code, code lines starting with four spaces or a tab, single-line inline code, and HTML comments are ignored. External URIs are not fetched; an undefined explicit `[label][reference]` is an error. Setext headings, multi-line links, complex nesting, raw HTML `href`, and renderer-specific anchors are outside this checked syntax; this is not a complete CommonMark/GFM renderer.
- An actual body comment that starts before a fence is still treated as a comment; a fence's info string and content do not change the body's comment state. The info string of a backtick fence must not contain backticks, and comment-like text in it is not removed before judging validity. After the fence closes, scanning for real links and owner acceptance criteria resumes, using the original line numbers.
- Explicit residual markers are the standalone tokens `TODO/TBD/PROJECT` (`TBD` is the standard fill-in placeholder), a standalone `NNN` (including in lowercase anchors), `<slug>`/`<project>`/`<context>`/`<id>`, and `{{field}}`. Metadata placeholders are checked in the identity/relation/confirmation fields that the parser has already read, and YAML comments are not treated as values; examples in body code and comments are not placeholders. The ordinary word `project` is not a placeholder.
- Facts with specific context, such as `open`, `to be confirmed`, or `not-run`, may remain; the checker does not fill in business decisions. The absence of these mechanical violations does not mean semantic completeness, trustworthy approval, or successful behavior execution.

<a id="checker-baseline"></a>
### Exact baseline and current-file comparison

Without a base, only the current root is read and Git is not needed. With a base, the root must be exactly the top level of the selected checkout (linked worktrees are supported); borrowing an ancestor repository is rejected. The base accepts only an actually readable full 40/64-hex-digit **commit object**; branches, short hashes, tag or blob objects, and nonexistent objects are rejected, with no fallback.

**In both modes, the verification target is always the complete formal inventory of the current working files.** The base only adds a historical comparison; it does not skip unchanged artifacts and is not an index (staging-area) hook check; unstaged and untracked formal files are included as well. Historical Markdown is read and recognized only from raw Git blobs, and old metadata is not required to satisfy new rules.

Git reads use argument lists, an explicit cwd, `shell=False`, and raw `ls-tree/cat-file`; they never invoke diff/textconv, clean/smudge filters, hooks, or source commands. Inherited repository/index/Git-configuration environment variables are cleared, replace refs and lazy fetch are not used, and the tool never looks for main/master or a newer HEAD. Failures keep their diagnostics and return an input error.

Each Git call sets `GIT_CEILING_DIRECTORIES` to the parent of the selected root; missing or incomplete metadata returns
`BASE_UNAVAILABLE` instead of borrowing an ancestor repository; the host Git's `GIT_EXEC_PATH` is kept. The repository's own configuration takes effect under native Git
rules, and the tools do not parse it separately. The [Git invocation environment](../../docs/domain-sources.md#git-config-boundary)
describes its scope; ordinary local content inputs without Git do not require creating a repository.

<a id="checker-output"></a>
### JSON fields, counts, and stable codes

The report and internal records are narrow-purpose immutable dataclasses; `report.to_dict()` is directly JSON-serializable, with tuples encoded as arrays and missing values as `null`:

| Field | Actual representation |
|---|---|
| `status`, `findings`, `checked_count`, `baseline`, `excluded`, `attempted_count` | Top-level fields; `checked_count` is the number of formal files successfully parsed and body-checked, including files with violations; `attempted_count` additionally counts recognized formal candidates that failed to parse or could not be read. If a directory cannot be read, candidates may not be listed yet; the status is still an error |
| `findings[]` | `{code, path, line, owner, target, message, related}`; `path` is the actual absolute path or the string of an invalid input, and `line` is 1-based; `owner` is `scope/id` once parsed, otherwise `null`. Link findings locate the referencing line and the original target; for duplicate IDs, `related={path,line}` stores the first occurrence and the primary location is the second |
| `baseline` | `null` when the root/base fails before reading; otherwise contains `root`, `target="working-tree"`, `base_sha`, `base_tree`, `comparison_complete`, `snapshot_sha256`, `files`, `base_files`, `changes` |
| `baseline.files[]` | `{path, sha256, size, role, owner}`; the root-relative path and the SHA-256/size of the raw bytes actually read (BOM/newline differences preserved), `role=formal/guide/reference`. Includes guides read for selection and local references; it is not a digest of the whole repository or of the tool source/schema |
| `baseline.base_files[]` | `{path, blob, sha256, size, formal}`; the Git blob ID, raw-byte digest, and selection signal of eligible historical Markdown; historical schema is not parsed |
| `baseline.changes[]` | `{path, status, base_blob, before_sha256, after_sha256}` over the union of formal paths; `status=added/modified/deleted`, with `null` when a side does not exist; not a whole-repository diff |
| `baseline.comparison_complete` | `null` without a base; `false` when the base comparison hit a read/path problem, in which case only known comparisons are listed and a missing read is never presented as a deletion; `true` for a normal read. This does not mean the metadata/documents are valid |
| `baseline.snapshot_sha256` | SHA-256 of the path-sorted `files` array encoded with `json.dumps(sort_keys=True, separators=(",", ":"))`; identifies the actual read set of this run and never labels a dirty working tree as plain HEAD |

Each input is read only once per check, and later references share the same bytes. The read set is not a file-system transaction; record the tool version used for the call, re-check after later file or tool changes, and do not treat the digest as proof of approval.

`read_inventory(root, base_sha=None) -> Inventory` is reused by tools in the same directory. It performs the same single complete discovery, parse, and check as `run_check`. The `report` of an `Inventory` is exactly the `CheckReport` above, and it additionally keeps immutable tuples: `artifacts`, `raw_files` (actual paths and the bytes read), and `base_raw_files` (historical relative paths and raw blob bytes). Consumers do not re-read Markdown to reconstruct the same snapshot. Historical parsing uses the original parser's byte entry point; standalone YAML/JSON sources use `load_yaml_mapping(text, path)`, which is still the same SafeLoader with duplicate-key/alias checks and 1-based locations, with no separate frontmatter or owner parser.

| Stable code | Classification |
|---|---|
| All parser input errors above (including `DUPLICATE_ARTIFACT_ID`) | `input-error`; never swallowed or turned into an empty object |
| `MISSING_TITLE`, `EMPTY_TITLE`, `MULTIPLE_TITLES` | `invalid`; H1 structure |
| `INCOMPLETE_ARTIFACT` | `invalid`; explicit residual placeholder |
| `BROKEN_LINK`, `BROKEN_ANCHOR`, `UNRESOLVED_REFERENCE`, `UNSUPPORTED_FRAGMENT`, `INVALID_LINK` | `invalid`; local link or supported scope |
| `DIRECTORY_READ_ERROR`, `EXCLUDED_TARGET` | `input-error`; read or boundary failure; other path and decoding codes reuse the parser codes |
| `INVALID_BASE`, `BASE_UNAVAILABLE` | `input-error`; base shape, or failure to read the exact object |
| `REPORT_CONFLICT`, `REPORT_WRITE_ERROR` | `input-error`; output conflict or write failure |

Explicit output from every tool follows one shared rule in `check_artifacts._output_path` / `_write_new`: a new local file with a matching suffix whose parent directory already exists; no overwriting and no directory creation; no `:` in the file name (Windows alternate data streams); no writes into `.git`; and no overlap with sources that were read or declared. Paths are resolved the host's normal way, with `..` first normalized literally. `--report` can only explicitly create a new local `.json` file; a relative path is resolved against the root, and an absolute path is used as authorized for this run. Exclusive create is used and a failure exits 2; if writing fails after the new file was created, an incomplete new report may remain and must not be taken as evidence of success. The CLI's `report_output={path,written}` is independent of the protected input read set, and the default mode/API never produces this file. CLI argument usage errors are printed to stderr by argparse with exit 2; other defined errors are returned in the JSON.

<a id="traceability"></a>
## Complete delivery coverage

```python
trace_report(root, delivery_ids) -> CheckReport
```

Import it from `check_traceability` in the same directory. `delivery_ids` is the **complete set of delivery acceptance criteria** given by the caller; each item must be the `scope/id#anchor` of an actual owner, not a file title, a short ID, or a list inferred backwards from VTs. An empty collection, a single string, or invalid, duplicate, or unknown items are all input errors. The complete formal inventory is read first, and AC/VC are then extracted from their owners; other artifacts may serve as reference context but never automatically become part of "this delivery".

Every actual `targets` entry is reverse-checked, including targets outside the delivery set. A VT or TS counts toward coverage only when its real owner acceptance criterion, compatible layer, and independent criterion all meet the mechanical requirements. The layer comes from the `Verification layer` table row in the VT's `plan` section, or from `Business scope and scenario type` in the TS's `basis` section; it is never inferred from the file name, and frontmatter is not extended. A VT accepts the four explicit layers of the form (`Business acceptance`, `Software behavior`, `Applicable design verification`, `Standalone maintenance or document check`); a TS accepts an explicit business declaration of `Within context`, `Cross-context`, `REQ business acceptance`, or `QAS`. A missing, multi-valued, or unknown declaration must be reported.

| owner kind | Target layer |
|---|---|
| stakeholder-requirement, use-case, invariant, quality-attribute-scenario, domain-model | business |
| software-requirement | software |
| architecture-building-block, architecture-decision, architecture-specification, sequence-diagram, published-interface | design |
| development-log, backlog-item, user-story, tool-qualification, review-record | maintenance |
| Other kinds | No layer is guessed; reports `UNKNOWN_TARGET_LAYER` |

Criteria are read from the existing forms: under each `criterionAnchor`, a VT needs actual table values in the three rows `Expected outcome and independent pass criterion for this target`, `Corresponding method/steps or actual test identifier`, and `Preconditions, forbidden side effects, and open items`; a TS needs its four form bullets `Preconditions and inputs for this target`, `Actions, observations, and independent pass criterion for this target`, `Corresponding steps or actual test identifier`, and `Source navigation, open conditions, and forbidden side effects`. An anchor/heading alone, code/comments, placeholders, or a generic "all passed" do not satisfy the requirement. Different targets that share an anchor or have identical criterion content are reported as `SHARED_CRITERION`. This is an explainable structural minimum, not proof of natural-language semantics. Human review is still needed to judge whether the actual expectation suffices for the original acceptance criterion.

The returned fields, the formal-file `checked_count/attempted_count`, and the read-set `baseline` reuse the contract above; they are neither a coverage denominator nor a count of test runs. Parser/inventory input errors take precedence; a parse failure is never turned into "uncovered" or success. Additional codes:

| code | Status |
|---|---|
| `INVALID_DELIVERY`, `EMPTY_DELIVERY`, `INVALID_DELIVERY_ID`, `DUPLICATE_DELIVERY_ID`, `UNKNOWN_DELIVERY_ID` | `input-error` / 2 |
| `DANGLING_TARGET`, `TARGET_NOT_ACCEPTANCE`, `INVALID_TARGET_SOURCE` | `invalid` / 1; keeps the actual referencing location/target |
| `UNKNOWN_VALIDATION_LAYER`, `UNKNOWN_TARGET_LAYER`, `LAYER_MISMATCH` | `invalid` / 1 |
| `INSUFFICIENT_CRITERION`, `SHARED_CRITERION` | `invalid` / 1; locates the criterion declaration |
| `UNCOVERED_ACCEPTANCE` | `invalid` / 1; locates the actual acceptance owner, path, heading line, and full target |

The command is `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_traceability.py --root <documentation-root> --delivery <full-acceptance-reference>`; repeat `--delivery` once per delivery ID. stdout is the `CheckReport` JSON, and the CLI also keeps the actual `delivery_ids`; you can add `--report <new .json>`, which follows the protected-output contract. No arguments or wrong usage exits 2; a complete structure with no findings exits 0. This does not mean that any VT was run.

<a id="impact-candidates"></a>
## Impact candidates against an exact baseline

```python
impact_report(root, base_sha, task_ids=()) -> dict
```

It is also part of `check_traceability`. It uses an explicit full commit and the current working files, does not pick HEAD or a branch, and does not look only at staged content. The base is mandatory in the public API: explicitly passing `None` also returns `INVALID_BASE` / input-error / 2, rather than falling back through the shared inventory's optional-base semantics to a clean empty comparison. It returns the fields of `CheckReport.to_dict()` plus:

- `changed_sources`: changed formal paths, added/modified/deleted, the old blob, and the before/after SHA256; `before/after` hold the parseable `{key, path, sha256}` and are null when that side does not exist.
- `candidates`: transitive dependency candidates sorted by key, keeping `before/after` of the same shape, `requested_task`, and `reasons`. Each reason has the actual `source/consumer/reference/relation/path/line/snapshot`; `relation` is upstream or target, and `snapshot` is base/current.
- `task_ids`: keys of existing formal tasks explicitly specified by the caller (not an acceptance set); an empty list is allowed, and invalid, duplicate, or unknown items report `INVALID_TASK* / DUPLICATE_TASK_ID / UNKNOWN_TASK_ID` respectively. Tasks that were not supplied are never invented.

Changed owners are the seeds listed in `changed_sources`, and the other reachable owners are candidates; the dependency graph merges the old and new sides, so deleting a source or removing a reference does not erase the historical chain, and cycles are visited only once. A change to only a numeric value in a rule file can also reach REQ/SR, VT, and tasks through canonical references. An unparseable historical formal file reports `HISTORICAL_INPUT_ERROR` / 2 and keeps the known candidates without pretending to be a complete comparison. Compared with the raw historical byte comparison of `run_check`, this interface additionally parses historical identities.

The CLI uses `--base <full commit>` instead of `--delivery` and accepts repeated `--task <scope/id>`; the two modes are mutually exclusive. The report can still be written explicitly to a new `.json`. Candidates are not a final conclusion on severity, approval, or business impact; non-canonical lightweight links, semantically implied dependencies, and unknown sources outside the scope must still be added following the [shared impact method](../skills/verify-change/SKILL.md#impact). The tool does not change rules, run VTs, or rewrite old results.

<a id="model-export"></a>
## Nine-view reference model and drift check

```python
export_view(root, scope) -> dict
check_model(root, scope, model_path) -> CheckReport
```

Import them from `export_model` in the same directory. Neither API writes files. The primary input reuses the complete inventory and the actual read set; the selected scope must exist in real formal artifacts, and same-numbered IDs from different scopes are not mixed. All formal sources must be valid, and canonical upstream/targets must locate a real owner/anchor. An invalid root/scope/contract/formal inventory cannot be masked by nine empty views. The export API raises `ArtifactInputError` with code/path/line; the check API and the CLI map it to an input error / 2.

The [optional model-sources contract](../contracts/README.md#model-sources) selects each scope's existing Markdown or YAML/JSON summaries. A missing manifest, a missing scope registration, and a missing view each produce a specific gap; the primary index remains usable. An invalid manifest gives `INVALID_SOURCE_MANIFEST` / 2. A single optional source that is missing, unreadable, or has a format or baseline problem makes that view `unverified` with its refs cleared; readable but incomplete fields or entries give `partial`; a complete source gives `available`. The nine original keys are never omitted; values, body text, and results still belong to the source, and approval is never inferred from a state. An optional-failure gap carries the selected path, the actual failing source, and the code; personal absolute paths and raw sensitive exception content are never output.

Direct quality checks cover both the actual QAS and the utility-tree source (an existing file with a top-level `tree` mapping/list can be selected explicitly); a missing source gives unverified, and only missing fields/entries in a known source give partial. Direct verification reads the owned child run blocks and the four-column result table of the current VT form, records missing items/conflicts per run, and keeps the original anchors; automated/manual counts are never derived from totals, and content from adjacent runs or criteria is never stitched together. SEQ completeness reads the real diagram code subject to the shared comment/fence state, without rescanning raw literal examples. The contract notes remain authoritative for the specific source shapes.

The primary `source.root` is always the portable `.`. Each artifact baseline is the `sha256:` of the raw bytes actually read (including BOM/newlines), and upstream/targets, artifacts, views, refs, and gaps are sorted deterministically. The primary `source.baseline` is the `sha256:` of the following object, encoded with `json.dumps(sort_keys=True, separators=(",", ":"))` and UTF-8: `scope`, the Task6 `files` read-set records sorted by path, `manifest: absent/present`, the sorted optional failures `(selected path, code)`, and the raw digests of the contracts used for artifact/model/model-sources; when the implementation-report adapter is used, it also includes the bc-config/implementation-report contracts. The read set includes guides used for selection, the manifest, actual optional YAML/JSON, and evidence files, not only formal Markdown. There are no timestamps or random data; the tool version is saved separately with the check record.

Canonical references also keep the evidence baseline of their actual owner file, so cross-scope consumers can trace back to the source. Mentions in code, table headers, or ordinary AC text never automatically become source fields or owner acceptance criteria. Each file is read only once per derivation; this is not a file-system transaction, so do not modify sources during derivation.

`check_model` reads an explicit local `.json/.yaml/.yml` (which may be a separately authorized model file outside the root), validates it, and recomputes; a changed primary source identity is `STALE_MODEL_SOURCE` / 1, and a hand-edited structure with the same source is `MODEL_MISMATCH` / 1. An invalid persisted model/schemaVersion/scope is an input error / 2. It does not repair an old model, and a derived model cannot serve as a source or as source evidence; manifest self-references are rejected.

An implementation report must be selected separately and explicitly among the `verification` sources of the existing manifest. A dedicated adapter checks the v1 schema, scope, and report baseline, and rebuilds the report read-only from its exact object/owned VT references; a hand-edited report that cannot be rebuilt is `REPORT_MISMATCH`, and a missing or drifted raw report only leaves a gap in that optional view; a schema-valid pass claim alone is not accepted. The model's `implementationReports` and the verification view store only the report's `reference + baseline`, without copying entries/execution/applicability. The other eight views and the existing sources are not replaced by the report; when no report is selected, the `implementationReports` list stays empty. `available` only means the reference can be checked; it does not imply that execution passed.

| CLI arguments (all require `--root` and `--scope`) | Output and exit |
|---|---|
| No output argument | Validates/derives to JSON stdout without creating files; exits 0 when the primary input can be derived, even with optional gaps |
| `--check <existing model>` | JSON CheckReport; 0 for no drift, 1 when drift is found, 2 for input errors |
| `--output <new model>` | Explicitly exclusive-creates a local `.json/.yaml/.yml`; stdout is still the schema-valid model; the parent directory must exist |

`--check` and `--output` are mutually exclusive. The output path reuses the Task6 local/conflict constraints: no existing source, model, report, empty file, or directory is overwritten; nested source/evidence locations declared in the manifest or in a selected YAML/JSON source cannot be taken by the model even if they are missing. The tool first registers every `reference` and `path + baseline` location in the whole parsed document and only then dereferences them one by one; a failure on an earlier item does not skip protection of later declarations. Registration grants no read permission and never marks unread data as usable.

When a declared location is itself invalid and cannot be registered safely, the default read-only derivation can still report an optional gap, but explicitly creating output returns `REPORT_CONFLICT` rather than pretending that input/output isolation has been established. A normal new output path can be exported and then checked as is; it does not automatically become its own source. `REPORT_CONFLICT / REPORT_WRITE_ERROR` exit 2; a primary-input failure creates no output, and a failure during writing may leave an incomplete new file. There is no network access, fetch, filters/textconv, hook, or source-command execution, and manifest baselines are never revised automatically.

An explicit domain `root/path` in an implementation report is likewise registered before verification, protecting that location and its child paths without requiring the baseline to exist or be valid. When a `domainSources` location declaration is incomplete or cannot be resolved safely, the default read can still report an optional gap, but explicit output must return `REPORT_CONFLICT`; a resolvable location still protects all of its child paths. Registration does not mean that this data is readable, valid, or authorized for writing.

<a id="implementation-report"></a>
## Collecting implementation summaries from existing VTs

```python
build_report(root, object_sha, evidence_files, *, scope=None) -> dict
```

Import it from `collect_implementation_report` in the same directory. The API is read-only and returns the existing [implementation-report v1](../contracts/README.md#implementation-report), with no root-level execution/views. The complete fields and the supported **VT selection, original form fields/baselines, comment markers, and applicability syntax** are all described in that contract; there is no separate input manifest or copied result ledger. The [blank report form](../../_templates/reports/implementation-report.yaml) only guides the output structure; it is not an actual result.

- The primary BC configuration, all owner acceptance criteria, and code/test locations come from the given full local commit, not from HEAD, the index, or a snapshot of current files. With multiple configured contexts the scope must be explicit; collection fails when there is no actual scope or acceptance criterion.
- The currently supplied VT may have records appended after the object; only owned child runs of the original owner at the same path are accepted, and a file with multiple runs requires an anchor. The original record bytes, the test object, the requirement baseline, the VT plan, and the raw report are each verified; new evidence is never labeled as part of the old object's bytes.
- Each target is handled independently. A target without a selected run is not-run with empty evidenceRefs and a reason; fail/skipped and their reasons are kept. The existence of a raw report, a located test text, Approved, a count of zero, all-skipped, or an available view cannot substitute for execution.
- Source runs, reports, dates, observations, and commands are **collected data**, not results of the collector's own run. The collector does not execute source commands or run applications/tests, and it cannot authenticate people or prove that external events happened. Manual records use concrete steps; auto/manual counts are never invented.
- Domain inputs are read and compared using the configured root/path and fixed baseline, and are never written back. The report's object root is `.`; no personal absolute paths, raw sensitive body text, or business summaries are copied.

| CLI arguments | Behavior and exit |
|---|---|
| `--root <checkout> --object <full commit>` | stdout is the per-target report and no file is written; repeat `--evidence <VT-relative-path[#run-anchor]>`, and add `--scope <project/context>` for multiple BCs |
| Add `--output <explicit new .json/.yaml/.yml>` | Exclusive create; the parent directory must exist; no report directory is created and source selection is unchanged. An existing source path, or a registered/referenced one even if missing, can never become the output |
| Successful collection with no fail | Exit 0, which may include all targets not-run or skipped. It only means that the collection completed, not that targets passed |
| A target was collected as fail | Still outputs the complete per-target report and exits 1; never changed into success |
| Input/source/output error | JSON `status: input-error` with findings carrying code/path/line/message, exit 2; no forged empty success |

Main diagnostics include `INVALID_BASE / BASE_UNAVAILABLE / OBJECT_PATH_MISSING / BASE_MISMATCH / PLAN_MISMATCH / OBJECT_MISMATCH` (object/source), `AMBIGUOUS_SCOPE / INVALID_SCOPE / UNKNOWN_SCOPE / EMPTY_ACCEPTANCE` (scope), `INVALID_EVIDENCE_OWNER / SCOPE_MISMATCH / REQUIREMENT_MISMATCH` (owner), `DUPLICATE_EVIDENCE / AMBIGUOUS_RUN / UNKNOWN_RUN / AMBIGUOUS_RESULT / INVALID_RUN` (selection/records), `INVALID_EXECUTION / INVALID_OBSERVATION / INVALID_EVIDENCE / MISSING_TEST_REFERENCE / INVALID_MARKER` (actual location/evidence), and `INVALID_APPLICABILITY / AMBIGUOUS_APPLICABILITY` (independent re-review). Shared file/schema diagnostics are kept; `REPORT_CONFLICT / REPORT_WRITE_ERROR` never silently overwrite an old report.

The report can be rebuilt but is not a source transaction: each file is read only once per collection, so do not modify sources during collection. An interrupted report write may leave an incomplete new file, which the next run still refuses to overwrite. A domain source's `readOnly: false` does not authorize writes either; no hooks, filters, replace-refs, fetch, or any command from the configuration are executed.

<a id="template-update"></a>
## Read-only template and explicit BC scenario proposals

`plan_template_update.plan_update(base, local, candidate) -> UpdatePlan` compares three real roots
and returns `changes/conflicts/preserved/sources` without writing sources or output. A narrow `TreeSource(root, version, files)`
can supply an exact local Git/content identity and a consistent file scope; a missing old baseline, a read failure, or a wrong version fails immediately.
`plan_batch(registration, target_ids) -> BatchPlan` maps `.feature` files only for explicitly registered/selected BCs,
keeping the source scenarios, repository/context/version, allowed files, and an independent result per target; it does not propagate the model or the whole repository.

The [complete contract for inputs, digest recipes, the 16 decision classes, registration, states, and output](../../docs/template-updates.md)
is maintained only in the update guide; the [shared method](../skills/update-template/SKILL.md) handles judgment and stop points.
The CLI defaults to stdout; three-root mode is `--base <old-root> --local <local-root> --candidate <candidate-root>`;
batch mode is `--registration <local-registration> --target <explicit-ID>` (repeat per target).
`no-change/proposed` exits 0, `conflict` exits 1, and any `unavailable` or input/output error exits 2.
A clean proposal may contain additions, modifications, and deletions; it is not a successful apply. An explicit `--output <new .json>` must be outside all input/
registration locations; it creates no parent directory, never overwrites history, and cannot take a missing or unselected target root.

Input parsing, safe YAML, and the restricted raw Git helpers reuse `artifact_io.py` and `check_artifacts.py`;
these modules and the existing locked dependencies are enough for the tool, with no dependency on maintainer tests, maker materials, workflows, or new dependencies.
There is no `--apply`, clone/fetch, commit/push, PR, external-source write-back, or background sync.
Owner business data, original rules, and deliberate deletions are preserved; raw bytes and source drift are checked against the complete contract.

<a id="domain-sources"></a>
## Optional local domain-source preflight and explicit onboarding

`setup_domain_source.inspect_domain_source(root, source_config) -> dict` is read-only by default;
it checks the real root/path/fixed baseline against the six source fields of the original BC and returns `ready / conflict / unavailable`
with 0/1/2, plus the exact paths, ownership declarations, targets, and proposed operations. Sources, the index, config, refs, and objects are not written,
and there is no fallback to HEAD or a remote. Network addresses are rejected before Git or credential tools are called, and the original URL is not echoed.

`apply_domain_source` writes only when the operation, the existing configuration, the exact preflight, and the target ownership declaration are all given explicitly;
register only appends a source entry to the BC and does not materialize or stage anything. The optional local submodule does not edit the
BC configuration and requires a separately given exact target plus separate consent for the index change; raw blob writes bypass checkout/filters/hooks,
native metadata and gitlink changes are disclosed item by item, and no commit/push is included. A non-empty target, alias, conflict, or drift is never skipped as success.

The BC token identifies only the raw configuration bytes actually used for parsing/planning; a change detected by a later read during inspection is also rejected.
A new native target never revives a `.gitmodules` from HEAD whose deletion the owner has staged, and the target itself cannot
occupy a metadata file. The shared Git reader and the native helper use the same clean Git environment, with the selected root
as the discovery ceiling; they neither borrow an ancestor repository nor parse repository configuration separately.

The complete API/CLI, the editable configuration layout, native commands, and recovery boundaries for retained partial state are in the
[domain-source guide](../../docs/domain-sources.md); the fields still belong to the [original contract](../contracts/README.md#bc-configuration).
The tool reuses the single safe YAML/schema reader of `artifact_io.py`, the path/Git boundaries of `check_artifacts.py`,
and the fixed-commit/raw-domain-byte comparison of `source_baseline.py`; the implementation-report collector shares that comparison,
so no second baseline parser or source model is maintained. Core dependencies are unchanged, and nothing extra is installed.

## Scope of use

Downstream use depends only on the modules provided in this directory (including the shared `vt_records.py` and `source_baseline.py`), the sibling dependency manifests, and the adjacent contracts; it does not require downloading maker specifications, run logs, or maintainer regression tests. The local architecture/presentation tools also reuse the narrow output and safe-encoding helpers of `render_traceability.py`; the complete usage guide is the [export contract](../../docs/document-exports.md). Formal artifact checks, coverage, impact candidates, the model, implementation summaries, update proposals, source onboarding, and document exports each have the boundaries described above and do not substitute for one another; all links and semantics of ordinary guides still need review. None of the tools runs `.feature` files, applications, or business VTs, and none authenticates approvers.
