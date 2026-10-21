# Maintenance-tool data contracts v1

This directory defines the input contracts for artifact metadata, the optional BC configuration, the derived model, and implementation reports. They are this repository's functionally equivalent design, **not a compatibility claim for the fields, file formats, or automatic import of the original six repositories**. This page and the schemas in this directory fully describe the fields and examples, so the internal maker specifications are not needed; tool invocation and error codes are in the [tool notes](../utilities/README.md).

The v1 semantics of the original four schemas remain unchanged; the optional source manifest has its own fifth schema. All of them are JSON Schema Draft 2020-12, require `schemaVersion: 1`, and reject unknown fields. `$ref` uses only JSON Pointers within the same file; the `$schema` URI only identifies the dialect, requires no network download, and does not depend on the maker repository's tests or history.

The optional [template-update registration](../../docs/template-updates.md#registration) has its own narrow path/version/file contract and [blank data form](../../_templates/config/template-updates.yaml); it reuses the safe YAML reader and adds no business/result schema, command manifest, or authorization field. The five schemas above and their original v1 semantics are unchanged.

## Shared representations

| Representation | Convention |
|---|---|
| `id` / `projectId` / context `id` | Starts with an ASCII letter or digit, followed by letters, digits, dots, underscores, or hyphens; no path separators or whitespace |
| `scope` | Exactly two segments, `project/context`; never guessed from directory names or the current application |
| Artifact `key` | `scope/id`, for example `sample/CTX-001/SR-001` |
| Canonical reference | `scope/id#anchor`; artifact references in targets, views, and reports must include an anchor. `upstream` also allows a full artifact key without an anchor |
| Anchor | Starts with an ASCII letter, followed by letters, digits, dots, underscores, colons, or hyphens; no `#` or whitespace |
| `path` | Repository-relative path using `/`; non-ASCII characters and spaces are allowed; absolute paths, backslashes, empty segments, and `.` / `..` intermediate segments are not allowed. A lone `.` may denote the source root |
| File `reference` | Repository-relative file path with an optional `#anchor`; not an executable command or a network download instruction |
| Fixed object `baseline` | A full lowercase Git object ID (40 / 64 hex digits), or `sha256:` followed by a 64-digit content digest; `HEAD`, branch names, and abbreviations are not accepted. Git-type domain sources must use a full Git object ID |
| Evidence/confirmation `baseline` | A non-empty object or report baseline pointer containing non-whitespace characters; the schema does not authenticate it. It is defined separately from the fixed-object format of the primary input, and missing optional evidence cannot substitute for a primary-input error |
| Three kinds of state | The content declaration is `draft / confirmed / retired`; task progress remains maintained by the task owner as `todo / in-progress / blocked / review-ready / done`; execution results are recorded separately as `not-run / pass / fail / skipped`; none of them converts into another |

Integers in JSON Schema follow JSON numeric semantics; booleans and strings are not integers. The Markdown parser further requires the YAML-decoded `schemaVersion` to be a genuine Python `int` equal to 1, and rejects `true`, `"1"`, and `1.0` without coercion.

Everything below is a **structural example**, not a confirmed artifact, configuration, or execution record. Example baselines only show the fixed-object format; when adopting them, replace them with real objects readable in your project. These examples do not prove that any scope, source, report, or acceptance criterion exists.

## 1. Artifact frontmatter

[artifact.schema.json](artifact.schema.json) owns only machine metadata; the Markdown body still owns business meaning and criteria.

| Field | Requirement and meaning |
|---|---|
| `schemaVersion`, `id`, `kind`, `scope`, `contentState` | All required. The only formal enumeration of `kind` is `$defs.kind` in the schema, a closed set of 32 items; there are no custom plug-in kinds |
| `upstream` | Optional; a deduplicated list of full source references. The parser returns an empty tuple only when the field is truly omitted; `null`, objects, strings, or invalid elements are errors |
| `targets` | Optional; a deduplicated list of structured records. Each record requires `target` and `criterionAnchor`, with an optional non-empty `testId`; when present, the owner, anchor, and test identifier must never be dropped |
| `confirmation` | Required for `confirmed`; if provided, non-empty `by`, `reference`, and `baseline` are required. Only the shape of the declaration is validated; it cannot authenticate the person, permissions, or approval |

A target record looks like `{"target": "sample/CTX-001/SR-001#sr-001-ac-01", "criterionAnchor": "criterion-01", "testId": "native::test_reject"}`. `criterionAnchor` must be a real explicit anchor in the current document body, not inside a code fence, a comment, or link text. Identical target records are rejected; the same target referenced by different tests/criteria may be kept. Cross-file existence, layer, and coverage of targets are outside this parser's checks.

````markdown
---
schemaVersion: 1
id: REQ-001
kind: stakeholder-requirement
scope: sample/CTX-001
contentState: draft
upstream: []
targets: []
---
# REQ-001: Structural example

<a id="req-001-ac-01"></a>
### REQ-001-AC-01: First item

This is an example of an independent criterion of this artifact, not a pass record.

<a id="req-001-ac-02"></a>
### REQ-001-AC-02: Second item

Body text that references other IDs is not an additional acceptance criterion.
````

The parser recognizes the existing repository pattern: an `<a id="..."></a>` on its own line (single or double quotes both work), immediately followed by the owning artifact's ATX heading `### REQ-001-AC-01: ...`; blank lines in between are allowed. The anchor must be the lowercase form of the full heading ID. Both `AC` and design-verification `VC` are supported; IDs anywhere in the text, links, other owners' headings, comments, indented code, and backtick/tilde code fences never become part of the acceptance inventory. It is not a general Markdown renderer and does not derive implicit heading anchors.

For the example above, `acceptance_ids` returns `sample/CTX-001/REQ-001#req-001-ac-01` and `sample/CTX-001/REQ-001#req-001-ac-02`, not `AC-01`. Each `Acceptance` also keeps the full heading ID, the owner, the anchor, and the original file line numbers of the heading and the anchor. A missing matching anchor or a duplicate anchor is an error.

Existing documentation is not moved, renumbered, or overwritten. Add frontmatter explicitly only after the scope is confirmed; the parser does not batch-convert old documents or forms. Ordinary documentation without frontmatter can still be read directly, but passing it explicitly to this parser yields `MISSING_FRONTMATTER`; no default artifact is silently generated.

<a id="bc-configuration"></a>
## 2. Optional BC configuration

[bc-config.schema.json](bc-config.schema.json) is data configuration, not a shell manifest.

| Field | Meaning |
|---|---|
| `schemaVersion`, `projectId` | Data version and project identity |
| `boundedContexts` | Non-empty list; each entry has only an explicit `id`; the scope is formed from the project and this ID, so no separate scope that could drift is stored |
| `domainSources` | List; each entry requires `id`, `kind: local / git`, `root`, `path`, `baseline`, and `readOnly` |
| `developmentRegistration` | Repository-relative path and required anchor pointing to the existing development registration; commands, credentials, and environment variables are not copied |

`root` keeps the explicit source root: a local directory, a selected clone root, or a Git repository location; `path` separately stores the relative location inside that repository. `id` is a short identifier that later onboarding uses to reference the source stably. The schema does not connect to Git, access remotes, or create submodules, and `readOnly: false` grants no write permission. The actual path, object type/readability, source ID conflicts, and whether the registration matches still require a later source-onboarding check.

Use [local domain-source onboarding](../../docs/domain-sources.md) to check these original fields read-only first; it adds no schema
or execution manifest. Registering an existing source only edits the explicit BC source list and never overwrites the domain directory.
The optional submodule is a separate local materialization operation that additionally requires consent for the target and the index, and completing it does not
register the BC automatically. Network sources stay unavailable/proposal-only; the exact commit/raw-file digest, the root/path separation, and the
readOnly semantics are the same as for the collector below, and no clone, staging, commit, or write-back permission is derived from the configuration.

```yaml
schemaVersion: 1
projectId: sample
boundedContexts:
  - id: CTX-001
domainSources:
  - id: owned-domain
    kind: local
    root: .
    path: domain-model
    baseline: 0123456789abcdef0123456789abcdef01234567
    readOnly: true
developmentRegistration: docs/development.md#project-registration
```

## 3. Derived model

[model.schema.json](model.schema.json) stores only references; it does not copy business body text, confirmation declarations, or actual results.

| Field | Meaning |
|---|---|
| `schemaVersion`, `scope` | Version and selected scope |
| `source` | `root` and fixed-object `baseline` of the required primary input; cannot be downgraded to "optional source unverified" |
| `artifacts` | Each entry requires `key`, a repository-relative `path`, an object `baseline`, `upstream`, and `targets`; the last two use the same reference shape as frontmatter |
| `implementationReports` | List of `reference + baseline` evidence pointers |
| `views` | Must have exactly the nine keys `requirements`, `stories`, `architecture`, `sequences`, `verification`, `quality`, `governance`, `risk`, and `release`; each requires `state`, `artifactRefs`, `evidenceRefs`, and `gaps` |

`unverified` must have empty references and a specific non-empty gap; `partial` must have at least one known artifact/evidence reference plus a specific gap; `available` has no gap and keeps at least one source reference (a known empty source is also located with an evidence reference). These states do not mean business acceptance, approval, or release. Missing required fields, invalid references, or a malformed primary-object baseline are invalid input data; the schema does not turn them into nine empty views.

```yaml
schemaVersion: 1
scope: sample/CTX-001
source:
  root: .
  baseline: 0123456789abcdef0123456789abcdef01234567
artifacts: []
implementationReports: []
views:
  requirements:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["srSummary source is absent"]
  stories:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["SR to US bridge is unavailable"]
  architecture:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["ABB and ADR sources are absent"]
  sequences:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["runtime sequence source is unavailable"]
  verification:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["verification evidence source is unavailable"]
  quality:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["QAS and utility-tree sources are absent"]
  governance:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["governance source is unavailable"]
  risk:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["risk source is unavailable"]
  release:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["release source is unavailable"]
```

This schema validates only the shape of view data; it does not look up actual sources, derive fields, or verify scope/baseline consistency or hand edits. Callers must still check the real sources and evidence; schema-valid does not mean that the model was generated by the exporter or verified by a run.

<a id="implementation-report"></a>
## 4. Implementation report

[implementation-report.schema.json](implementation-report.schema.json) keeps the object, sources, execution records, and applicability separate.

| Field | Meaning |
|---|---|
| `schemaVersion`, `scope`, `object` | Version and scope; `object` requires the source root `root` and the fixed-object `baseline` |
| `bcConfig`, `domainSources` | `reference + baseline` of the BC configuration; each domain source stores `root + path + baseline` |
| `artifactRefs` | Full canonical references to SR/US/ABB/VT and so on; ID prefixes are not an additional kind enumeration |
| `entries[].target` | The full acceptance reference that this record covers |
| `entries[].codeRefs` | Repository-relative `path`, fixed-object `baseline`, optional `symbol` |
| `entries[].testRefs` | Repository-relative `path`, fixed-object `baseline`, non-empty `testId`; application test directories and languages are not restricted |
| `entries[].execution` | `status` and `evidenceRefs`; pass/fail must have non-empty evidence references, and not-run/skipped must have a specific `reason` |
| `entries[].applicability` | A separate `state: unverified / applicable / not-applicable` and a specific `reason`; current applicability is never generated automatically from a historical pass |

```yaml
schemaVersion: 1
scope: sample/CTX-001
object:
  root: .
  baseline: 0123456789abcdef0123456789abcdef01234567
bcConfig:
  reference: bc-config.yaml
  baseline: 0123456789abcdef0123456789abcdef01234567
domainSources:
  - root: .
    path: domain-model
    baseline: 0123456789abcdef0123456789abcdef01234567
artifactRefs:
  - sample/CTX-001/SR-001#sr-001-ac-01
  - sample/CTX-001/VT-001#criterion-01
entries:
  - target: sample/CTX-001/SR-001#sr-001-ac-01
    codeRefs: []
    testRefs: []
    execution:
      status: not-run
      evidenceRefs: []
      reason: Application environment is not configured
    applicability:
      state: unverified
      reason: No execution evidence is available
```

There is no global "passed" field; empty entries or empty evidence cannot establish a pass. Even when the data structure of a pass is valid, you must still go back to the evidence to check the actual object, each target, the execution counts, and the results; the schema does not authenticate the report, run tests, or write back to read-only sources. Changing fields of this version requires an explicit version/contract change; unknown fields are never silently tolerated.

### 4.1 Collection scope and exact object

`collect_implementation_report.build_report(root, object_sha, evidence_files, *, scope=None)` reads existing VTs and introduces no separate execution-input ledger. `root` must be an explicit local Git checkout root, and `object_sha` must be a readable full commit ID; None, branches, short hashes, tag/tree/blob objects, and unavailable objects are rejected, with no fallback to HEAD/index and no fetch. The report's `object.root` is `.`.

The primary `bc-config.yaml`, formal artifacts, and code/test text are read from regular blobs of that commit; current working files, the index, or another HEAD never replace them. The scope is selected from the configured project/context: it may be omitted when there is only one BC; with several, `scope` / `--scope` must be passed explicitly, and the first one is never picked. All owner AC/VC of the scope are inventoried first, including items without a VT, and evidence is collected afterwards; no actual scope or no acceptance criteria is an input error. Upstream items from other scopes serve only as sources and never automatically add delivery items.

The configured `developmentRegistration` must point to a real file/anchor in that object. A domain `root` is an explicit local directory relative to this checkout (`../domain-source` can select an authorized standalone local source); environment variables are not expanded, and URLs, UNC paths, or personal absolute paths are not accepted; `path` is interpreted only relative to that source root. A SHA256 baseline applies to the raw bytes of one file; a full Git commit applies to a file or directory at the same path and must match the actual local file set/bytes. Directory comparison does not follow links or initialize gitlinks, and Git sources accept only commits. `readOnly` keeps the original configuration declaration, and false does not grant write permission either; the collector never changes sources, the index, config, or permissions. Domain files that overlap the primary object must also match the bytes inside the object.

### 4.2 VT files and run selection

`evidence_files` is a list of strings whose elements are root-relative `verification/VT-001.md` or `verification/VT-001.md#vt-001-run-01`, not JSON/YAML containing copied states. Each file must be a VT at the same path and with the same owner/scope as in that object. Runs may be appended after the test object; the current file and the raw reports are referenced by their own actual byte digests and are never labeled as new bytes in the test object.

No argument (CLI) or an empty list (API) means that no run is selected; the current VTs are not scanned implicitly to fill in results. A missing or out-of-root path, a duplicate selection, and an unknown anchor are all input errors. A file without a fragment selects its run only when it has exactly one owned run; zero runs keep each target not-run, and multiple runs require selecting an anchor. If different selected runs involve the same target, this is reported as ambiguous whether the results are identical, conflicting, or based on different baselines; the newest/last/most favorable result is never adopted, and fields are never stitched together across runs.

Only `vt-…-run-NN` subheadings inside this VT's `runs` H2 that belong to this owner are read, reusing the strict section boundaries and the comment/fence exclusions. Same-level or higher H2/H1 headings, example code, comments, file names, and Approved are not runs. Each selected run must have the original form's four-column per-criterion result table, with exactly one row for every declared criterion; the execution table does not need to be copied before the parent heading.

Collection supports the following **limited value syntax for the original form fields**; existing records that do not conform are reported explicitly as input errors and are never migrated automatically or interpreted by guessing at natural language:

| Original field | Supported values |
|---|---|
| Date, executor, and mode | `YYYY-MM-DD; recorder=<named recorder>; mode=command` or `mode=manual`; only a locating declaration, not identity authentication |
| Actual object baseline | The full commit ID requested for this collection |
| Requirement/design/task basis baseline at the time | `scope/OWNER@baseline`, with multiple owners separated by `;`; must cover exactly the target owners of this VT |
| VT baseline at the time | A full local commit of this VT, or the `sha256:` of the raw file within the object; not a digest taken after the current new run was added |
| Actual environment and tool versions | An actual named environment description; must not be a placeholder such as `Not configured`, `Not provided`, `Not run`, `TBD`, or `Unknown` |
| Actual working directory | In command mode, a relative directory that exists in the object, or `.`; manual mode may describe a non-command check |
| Actual command or manual steps/test identifier | The actual command text or concrete manual operations; read-only and never executed. Targets executed in command mode must give their real testId |
| Exit code and discovered/executed/skipped counts (when applicable) | command: `exit=0; discovered=2; executed=2; skipped=0`. executed excludes skipped, and discovered must equal the sum of the two; auto/manual splits are not derived from these totals. Manual mode does not require this row or invented counts |
| Raw report and exact location | `[description](path-relative-to-this-VT#optional-anchor) @ baseline`; multiple entries separated by `;`. May be `not-run` only when the run was not run or was skipped |
| Report accessibility and limitations | A description of the actual access scope and limitations |

Two-column table values use the existing reader and currently cannot contain `|` (including in escaped form); a `;`-separated owner/report list cannot contain another semicolon within a single item. A Markdown link with spaces in its path uses `[description](<../reports/raw report.txt>)`. This is a limited input syntax, not a general importer for arbitrary Markdown or local runner reports.

A baseline is a raw `sha256:` or a full local Git commit (raw reports also accept a blob). If a requirement baseline is not object_sha, **identical whole-file bytes** must be verified per owner; the VT baseline must verify identical plan content. The VT plan projection excludes only the real `runs` and `applicability` H2 sections (including their child blocks); all other frontmatter/body/newline bytes must match. No declared `criterionAnchor` may lie inside an excluded subtree, even if that criterion is not-run this time; the comparison explicitly returns `INVALID_CRITERION` rather than letting the criterion be discarded together with the run records. The currently supplied VT is compared with the object's plan as well; changing targets, criteria, methods, or non-excluded content cannot reuse old results by appending a run.

A pass/fail row must have an independent, specific observation with a link to its raw report; that link must correspond to a path/fragment/baseline already verified in this run's report field. The report must be readable and non-empty; a Markdown fragment must be a real explicit anchor, a JSON/YAML fragment must be a top-level key, and other files do not support fragments. A fail also keeps the reason for the difference. In command mode, zero discovered, zero actually executed, all skipped, no corresponding testId, or mere success wording cannot form a pass/fail. Mixed pass/fail keeps each result and is never merged into a global pass. A self-contradictory record with only passes but a non-zero command exit is rejected. Manual mode uses actual concrete steps and per-item observations, and requires no command or fabricated counts.

In command mode, `executed` must also be at least the **number of distinct testIds** to which the pass/fail rows actually belong; otherwise it is `INVALID_EXECUTION`. One located test covering several independent criteria counts only once; an executed count higher than the number of mapped tests may be kept. skipped/not-run rows do not consume this execution minimum, and manual mode does not apply command run counts; counts cannot be derived from test names appearing in the command text.

When no run is selected for a target, the target still appears in entries, with execution not-run, empty evidenceRefs, and an explicit reason. A selected not-run/skipped keeps its reason and the reference to the original record, and is never filled in with another target's success. The collection result only states that **source declarations** satisfying these structural/baseline conditions were read; it cannot prove that external events actually happened, let alone authenticate human approval.

### 4.3 Code/test text location and applicability

Supported markers are whole-line comments in ordinary UTF-8 source files, `# implements: scope/OWNER#ac symbol=name` and `# verifies: scope/OWNER#ac testId=test_name`; the `//` comment prefix is supported as well. The next non-empty text that is not a line comment must contain the given identifier followed by `(`; the identifier is limited to a single identifier starting with an ASCII letter or underscore. This narrow rule is text location, not language parsing, runner discovery, or test execution; unsupported markers are reported explicitly as errors. Markdown, JSON/YAML, forms, and dependency directories are not code-marker inputs. Paths come from actual Git blobs; code/test directories or file names are never guessed.

A marker must reference an actual, full owner acceptance criterion; the same short ID in another scope does not satisfy this target. When the VT has declared a `testId`, it must match the actual marker and location. The report stores only the path, the object baseline, and the explicit symbol/testId; without a marker the reference is empty, and implementation is never inferred from file names.

Default applicability is unverified. Independent re-review uses the VT's original `applicability` table: the `Original run/result and target link` value is `[Run](#vt-001-run-01) [Criterion](#allow)`; `Current object, requirement, and VT baselines` is `object=<full-commit>; requirement=scope/OWNER@baseline; vt=baseline`. `Review date and recorder` uses `YYYY-MM-DD; recorder=<recorder>`, `Applicability` uses `unverified` / `applicable` / `not-applicable`, and the rationale must be specific. Only a row whose run, criterion, object, and verified requirement/plan baselines all match can support the corresponding state; multiple matching re-review rows are reported as ambiguous, and historical re-reviews of other objects are not carried over. Applicability is independent of execution results; a pass or the same commit never automatically produces applicable.

### 4.4 Read-only output and model bridge

The API and the default CLI do not write files. The CLI uses `--root` and `--object` explicitly and accepts repeated `--evidence`; only `--output` creates the specified new `.json/.yaml/.yml`, and the parent directory must already exist. Overwriting any existing location is refused, and the output must not take the object files, BC/domain/VT/raw-report locations, or declared optional-source locations, even if such a location is currently missing. The domain `root + path` declared by the report protects that location and its child paths before baseline validation, without requiring the baseline to exist or be valid. When a `domainSources` location declaration is incomplete or cannot be resolved safely, or the container is invalid, the read-only view can still keep an optional gap, but every explicit output must be refused; a read gap can never turn into write permission. When the location resolves completely and only the baseline is missing, output to a disjoint new location is still possible, without forging a valid source. Exit 0 means successful collection (possibly all not-run), 1 means a per-item fail was collected, and 2 means an input/output error; the CLI's exit is never treated as the exit of the source VT.

A report can be **selected separately and explicitly** in the `verification` list of the existing `model-sources.yaml`; there is no new selection manifest. After the adapter validates the report's schema, scope, source-reference baselines, and rebuildability, the model's `implementationReports` and verification view store only the report file and its baseline, without copying entries, states, observations, or applicability. The other eight views and the existing verification sources are still read according to the existing selection; the nine-view missing-source/gap semantics are unchanged. The report has no views, and governance/risk/SEQ/QAS/release references are never disguised as execution evidenceRefs. Building a report never changes the source manifest automatically.

<a id="model-sources"></a>
## 5. Optional model-source manifest

[model-sources.schema.json](model-sources.schema.json) and the [blank source form](../../_templates/config/model-sources.yaml) only register source selections. When adopted, the manifest lives at `model-sources.yaml` in the selected documentation root; no second BC/model/execution manifest is added. The original four contracts, the 32 kinds, and the nine views are unchanged.

The manifest has only `schemaVersion: 1` and `scopes`. The latter is a map keyed by explicit `project/context`; each scope's value is a map of the needed views among the nine, and each view maps to a non-empty list of `{path, baseline}`. `scopes: {}` is a valid empty map and does not mean that a real project has been registered; a scope value of `{}` means that no view source has been selected yet. Duplicate YAML keys, duplicate paths within one view, or conflicting baselines for the same path are configuration errors and are never merged by overriding.

`path` is the relative path of an actual file inside the root; it allows non-ASCII characters and spaces, and rejects network/absolute paths, parent traversal, anchors, backslashes, control characters, and leading/trailing whitespace; a resolved symlink/junction cannot escape the root either. `baseline` is the `sha256:` digest of the raw file bytes, or a full lowercase local Git commit/blob ID. A commit must locate a regular blob at the same path from the explicit checkout root, and a blob must match the bytes currently read exactly; branches, HEAD, short hashes, tag/tree, textconv, or network access cannot substitute. The manifest is not a permission; it contains no root/URL, commands, credentials, body text, results, approvals, or write-back switches.

The structure looks like this; the paths and digests must be replaced with actual local inputs and do not refer to existing documentation:

```yaml
schemaVersion: 1
scopes:
  sample/CTX-001:
    requirements:
      - path: software-requirements/SR-001.md
        baseline: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  sample/CTX-002:
    sequences:
      - path: sources/sequences.yaml
        baseline: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

Errors in the primary root, scope, schema, formal inventory, or primary baseline always fail; supplying an invalid manifest also fails and cannot be downgraded to "missing optional source". An optional file in a valid manifest that is missing, unreadable, or malformed, or whose baseline cannot be verified, only makes the selected view `unverified`, with empty refs and a specific source gap listed. A valid but incomplete source gives `partial`; a complete source gives `available`. These states describe only the sources and are never interpreted as a pass or approval.

No manifest supplied, a manifest without the selected scope, and a scope without a given view each produce an explicit gap. As long as the primary inventory contains the scope, a missing manifest registration does not block the primary artifact index; a nonexistent primary scope is still an input error and cannot be invented through the manifest. Sources can be existing formal Markdown artifacts or existing YAML/JSON summaries as specified in the next section; there is no need to copy model body text for the export. A persisted derived model can never serve as a source again.

### 5.1 Two read shapes for existing sources

Prefer the original artifacts; do not make a new copy of the business model for the tools. Formal Markdown reuses the artifact parser and the original explicit anchors: the source version uses a raw-byte baseline, the content declaration stays in the metadata, and meaning and results stay in the body. Views keep the actual owner's anchors, the related `upstream` / `targets` navigation, and file baselines. When the selected artifacts and their dependencies lack a category/section that the view needs, the view is `partial`; fields are never filled in from file names.

| view | Required Markdown sources and sections (structure is checked; content is not authenticated) |
|---|---|
| requirements | REQ, SR, UC; owner AC of REQ/SR, explicit body anchors of UC |
| stories | US `task` and `checklist`, plus SR sources |
| architecture | ABB `structure`, `interfaces`, and `runtime`, plus ADR `decision` |
| sequences | SEQ `basis`, `participants`, `paths`, and `diagram`, plus UC and ABB sources; read the source for timing, partner, and async meaning |
| verification | VT `plan`, `targets`, `runs` and their actual owned child run blocks, plus REQ/SR; the plan structure does not prove that an actual run exists |
| quality | QAS `scenario` and `measurement`, the actual utility-tree source, plus REQ and actual TS/VT targets; a missing QAS or tree source gives unverified, and neither the tree nor the scenario body is copied |
| governance | review-record `decision`; the meaning of approvals/waivers still belongs to the original record |
| risk | risk-control `analysis`, `control`, and `residual`, plus REQ/VT sources; risk levels are not computed |
| release | development-log `release` and `change-control`; lifecycle/classification/version still belong to the original release record |

A section alone or a generic body paragraph is not enough to locate the original summary fields. Direct Markdown also checks the following **table values in the original owner** (two-column tables); when one is absent, a field-level `partial` gap is kept, and nothing is inferred from code arrows, metadata states, file names, or common values. The version is located by the actual object baseline, and IDs/relations still come from the parser; these are not new frontmatter fields and do not require copying a model for the export.

| Source location | Values that must be locatable (`/` separates accepted original labels) |
|---|---|
| US `task` | `Task progress/status`; contentState never substitutes for task progress |
| ABB `runtime` | `language/Implementation language`, `framework/Framework`; if not yet selected, the item is missing and no default stack is chosen |
| SEQ `paths` | An explicit `true/false` declaration of `hasAsync/Asynchronous interaction`; never inferred from Mermaid arrows |
| SEQ `participants` | An existing integration-partner upstream; without one, an explicit source statement for `externalPartners/External partners` is needed, including when it is known that there are no partners |
| This owner's `vt-…-run-NN` child blocks under VT `runs` | The date, notes, the three run baselines, and explicit auto/manual counts are read in each child block; actual results come from that block's multi-column per-criterion table, and there is no need to copy them again before the `runs` heading |
| QAS `scenario` | All six values of the existing six-element table; the original field labels `stimulusSource/stimulus/environment/object/response/responseMeasure` are accepted as well |
| review-record `decision` | `status/Review conclusion`, `notes/Limitations and notes`; reading the declaration does not authenticate approval |
| risk-control `analysis` / `residual` | `preMitigationLevel/Pre-mitigation risk`, `residualRiskLevel/Residual risk`; risk is neither computed nor accepted |
| development-log `release` | The five original field values `lifecycle/safetyClass/currentVersion/lastReleaseDate/nextPlannedRelease`; change control is still located through its own separate original section |

Duplicate or missing values for the same field, an explicitly unknown value or placeholder (such as `Unknown`, `Not provided`, `Not run`, or `TBD`), a missing original section, and a missing required relation are each a specific gap. Counts are non-negative decimals, booleans accept only `true/false`, and a known zero or false is not treated as missing. Header and separator rows alone are not content; a SEQ diagram must be a genuinely closed Mermaid code fence inside its `diagram` section, with a sequence header and messages. HTML comments, examples inside an enclosing literal fence, unclosed fences, or ordinary notes cannot fill the gap; the body and the diagram reuse the same comment/fence state machine, and raw text is never rescanned to guess at a diagram. Existing documents in unsupported shapes keep specific gaps and are not migrated automatically.

Direct quality can select the original QAS Markdown and an existing utility-tree YAML/JSON side by side in the same manifest view. The tree file's top-level `tree` is a mapping/list, the data still belongs to that file, and the export keeps only `file#tree + baseline`, without adding a kind or copying tree nodes. An empty `tree` is an entry gap in a known source (partial); no QAS, no tree source, or a tree that is unreadable, malformed, or has an unverifiable baseline gives unverified, empty refs, and a specific missing-source reason. Only after both QAS and the tree can be verified does a missing response measure or a partial set of scenarios give partial. An existing `quality.utilityTree` evidence pointer can also be referenced directly; no new model needs to be built for the tools.

Ordinary business nodes in the tree may contain `root` and `path`; these keys by themselves do not declare domain file locations, and they neither restrict nor rename the mapping/list/text values in them. The special handling that protects a location even without a baseline belongs to the context of actual `domainSources` entries; outside that context, the existing source-reference handling of complete `root/path/baseline`, `reference`, or `path + baseline` still applies, and no path is inferred from the two business keys.

Direct VT looks for this owner's `vt-…-run-NN` anchors inside the real `runs` level-2 section and associates each anchor with the real heading that immediately follows it (blank lines/comments allowed). Only lower-level headings inside that H2 are owned runs; an anchor before the same-level H2 or higher H1 that ends the section is not a child block, and notes, code, or another anchor cannot borrow a later heading. Child blocks are still isolated by strict anchor boundaries. It reads the original form's `Date, executor, and mode` and `Report accessibility and limitations`, the three baselines (actual object, requirement basis at the time, and VT), and the four columns `Criterion link (target located by frontmatter)` / `Actual observation and raw report location` / `Actual result` / `Not-run/skip reason or failure difference`. Every declared criterion needs its own result row; duplicate rows, missing rows, invalid states, or unknown criteria produce gaps with source locations. Results are not copied into the model.

Auto/manual counts can come only from explicit `automatedCount/Automated check count` and `manualCount/Manual check count` rows in that run block, or from these two items stated explicitly in the original `Exit code and discovered/executed/skipped counts (when applicable)` value (for example `Automated check count 0; Manual check count 2`). They cannot be derived from the total discovered/executed counts, the number of result rows, or file names. Multiple runs each keep their own source anchors/baselines; complementary missing fields cannot be stitched into a complete run, and when the object/requirement/VT baselines are the same but the results conflict, both references are kept and marked with a partial conflict gap. Complete historical records with different baselines can be located separately; the newest is not selected, and they are not merged into a global result.

Existing YAML/JSON summaries can be selected directly as sources. The file's top level contains the objects listed in the table below; one file may hold several known summaries, but it is **not a model derived by this tool**. Field values are still maintained by the source, and the export stores only `file#summary-key + baseline` plus the actual references below; status/result/measures/safety classification are not copied into the model. JSON is read as its compatible subset by the same safe YAML data reader, which rejects duplicate keys, dangerous tags, and circular aliases.

In the table below, `ref` is a canonical reference to an existing owner/explicit anchor, not a short ID. `evidence` is the `{reference, baseline}` of an actual local file, and its baseline must likewise be verifiable by raw bytes or an exact local Git object; a Markdown fragment is a real anchor, a YAML/JSON fragment is a real top-level key, and other files allow only references without a fragment. Actual relations in arrays are never completed from a suffix/title. Each object may additionally give `evidenceRefs: [evidence]` to locate its existing original records; this is not an execution authorization.

| view / top-level key | Required source fields (source data, not manifest fields) |
|---|---|
| requirements / `srSummary` | `srVersion: text`, `entries: [{reqId: ref, srIds: [ref], ucId: ref, status: text, notes: text}]` |
| stories / `storySummary` | `storyVersion: text`, `entries: [{srId: ref, usIds: [ref], status: text}]` |
| architecture / `abbSummary` | `abbVersion/language/framework: text`, `blocks: [{abbId: ref, adrRef: ref}]`, `integrations: [ref]` |
| sequences / `sequenceSummary` | `seqVersion: text`, `entries: [{seqId: ref, ucId: ref, title: text, hasAsync: boolean, externalPartners: [ref], status: text}]`; ABB/partners are also located through the SEQ's original `upstream` |
| verification / `verificationSummary` | `vtVersion/lastRunDate: text`, `entries: [{usId: ref, vtIds: [ref], result: text, automatedCount: nonnegative integer, manualCount: nonnegative integer, notes: text}]` |
| quality / `quality` | `qasRefs: [ref]`, `utilityTree: evidence`, `testScenarios: [ref or evidence]`; no new `qasSummary` is created; when a feature has no artifact identity, file evidence is used and no canonical ID is invented |
| governance / `governanceSummary` | `govVersion: text`, `entries: [{govId: ref, status: text, ref: evidence, notes: text}]`; existing `reqIds/waiverRefs: [ref]` are kept as well |
| risk / `riskSummary` | `riskVersion: text`, `entries: [{riskId: ref, title: text, preMitigationLevel: text, rcIds: [ref], residualRiskLevel: text, reqIds: [ref], vtCoverage: [ref], status: text}]` |
| release / `releaseStatus` | `lifecycle/safetyClass/currentVersion/lastReleaseDate/nextPlannedRelease: text`, `changeControlRef: evidence`; existing `releaseRef: ref` and `bcRefs: [ref]` are kept as well |

A missing whole summary object or a wrong field type is an optional-source format error: `unverified` with empty refs. When the source is supplied but a specific field is missing, null, or empty text, or a required relation entry is missing, the result is `partial`, and the gap carries the source file and the full field path, for example `sequenceSummary.entries[0].externalPartners`; known refs and source pointers are kept. QAS and the utility tree are required source components of quality; a missing one is handled as unverified first and cannot be downgraded to an ordinary field-level partial. An explicitly empty `entries/blocks` denotes a verifiable empty summary; an empty `srIds/usIds/vtIds/testScenarios` list reports a missing relation, while an explicitly empty `externalPartners/integrations/rcIds/reqIds/vtCoverage` list never implies nonexistent objects. `false` and a count of `0` are valid source values, but string booleans and boolean counts are not valid types. When a referenced owner/anchor, file, or baseline cannot be verified, the result is `unverified`, and references that cannot be confirmed are not kept.

When a view has several sources, any source that cannot be verified makes that view `unverified` and clears its refs; if all can be verified but there are structural gaps, the view is `partial`. Other views are not affected. Each state describes only the structure/locatability of the selected sources; the complete text, numeric/async meaning, authenticity of approvals, and applicability of results must still be judged against the original owner.

### 5.2 Explicitly referencing implementation reports

Verification sources can also select a [v1 implementation report](#implementation-report). It still uses the same `{path, baseline}` selection item; the baseline must match the bytes of the generated report, and no execution entries are copied into the manifest. The adapter rebuilds the report read-only to check its original object/owned VT references; when the report's object is unreadable, the report was hand-edited, the scope mismatches, or the original records have drifted, that optional view is unverified and its report references are cleared. Invalid input in the primary inventory still fails.

Existing verification sources can be selected alongside the report; the model only adds file/baseline pointers and does not copy entries, result, or applicability into the view, and the canonical/evidence/baseline of the other sources keep their original semantics. A report being `available` is not a pass; when no report is selected explicitly, `implementationReports` stays an empty array. Building a report never modifies the manifest or the source model.
