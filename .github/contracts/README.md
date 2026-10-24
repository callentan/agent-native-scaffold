# Maintenance-tool data contracts v1

This directory defines the input contracts for artifact metadata, the optional BC configuration, the derived model, and implementation reports. They are this repository's functionally equivalent design, **not a compatibility claim for the fields, file formats, or automatic import of the original six repositories**. This page and the schemas fully describe the fields and examples; internal maker specifications are not needed. Tool invocation and error codes are in the [tool notes](../utilities/README.md).

The original four schemas keep their v1 semantics; the optional source manifest has its own fifth schema. All are JSON Schema Draft 2020-12, require `schemaVersion: 1`, and reject unknown fields. `$ref` uses only JSON Pointers within the same file; the `$schema` URI only identifies the dialect, needs no network download, and does not depend on maker repository tests or history.

The optional [template-update registration](../../docs/template-updates.md#registration) has its own narrow path, version, and file contract and a [blank data form](../../_templates/config/template-updates.yaml). It reuses the safe YAML reader and adds no business/result schema, command manifest, or authorization field. The five schemas and their v1 semantics are unchanged.

## Shared representations

| Representation | Convention |
|---|---|
| `id` / `projectId` / context `id` | Starts with an ASCII letter or digit, followed by letters, digits, dots, underscores, or hyphens; no path separators or whitespace |
| `scope` | Exactly two segments, `project/context`; never guessed from directory names or the current application |
| Artifact `key` | `scope/id`, for example `sample/CTX-001/SR-001` |
| Canonical reference | `scope/id#anchor`; artifact references in targets, views, and reports must include an anchor. `upstream` also allows a full artifact key without an anchor |
| Anchor | Starts with an ASCII letter, followed by letters, digits, dots, underscores, colons, or hyphens; no `#` or whitespace |
| `path` | Repository-relative, `/`-separated; non-ASCII characters and spaces allowed; absolute paths, backslashes, empty segments, and `.` / `..` intermediate segments not allowed; a lone `.` may denote the source root |
| File `reference` | Repository-relative file path with an optional `#anchor`; not an executable command or a network download instruction |
| Fixed object `baseline` | A full lowercase Git object ID (40 / 64 hex digits), or `sha256:` followed by a 64-digit content digest; `HEAD`, branch names, and abbreviations are not accepted. Git-type domain sources must use a full Git object ID |
| Evidence/confirmation `baseline` | A non-empty object or report baseline pointer with non-whitespace characters; the schema does not authenticate it. Defined separately from the primary input's fixed-object format; missing optional evidence cannot substitute for a primary-input error |
| Three kinds of state | Content declaration `draft / confirmed / retired`; task progress (kept by the task owner) `todo / in-progress / blocked / review-ready / done`; execution results `not-run / pass / fail / skipped`; none converts into another |

Integers follow JSON numeric semantics; booleans and strings are not integers. The Markdown parser also requires the YAML-decoded `schemaVersion` to be a genuine Python `int` equal to 1, rejecting `true`, `"1"`, and `1.0` without coercion.

Everything below is a **structural example**, not a confirmed artifact, configuration, or execution record. Example baselines only show the fixed-object format; replace them with real objects your project can read when adopting. Examples do not prove that any scope, source, report, or acceptance criterion exists.

## 1. Artifact frontmatter

[artifact.schema.json](artifact.schema.json) owns only machine metadata; the Markdown body owns business meaning and criteria.

| Field | Requirement and meaning |
|---|---|
| `schemaVersion`, `id`, `kind`, `scope`, `contentState` | All required. The only formal `kind` enumeration is `$defs.kind` in the schema, a closed set of 32 items; there are no custom plug-in kinds |
| `upstream` | Optional; deduplicated list of full source references. Empty tuple only when truly omitted; `null`, objects, strings, or invalid elements are errors |
| `targets` | Optional; deduplicated list of structured records. Each requires `target` and `criterionAnchor`, with an optional non-empty `testId`; owner, anchor, and test identifier must never be dropped |
| `confirmation` | Required for `confirmed`; if provided, non-empty `by`, `reference`, and `baseline` are required. Only the declaration's shape is validated; it cannot authenticate the person, permissions, or approval |

A target record looks like `{"target": "sample/CTX-001/SR-001#sr-001-ac-01", "criterionAnchor": "criterion-01", "testId": "native::test_reject"}`. `criterionAnchor` must be a real explicit anchor in the current document body, not inside a code fence, comment, or link text. Identical target records are rejected; the same target with different tests/criteria may be kept. Cross-file existence, layer, and coverage of targets are outside this parser's checks.

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

The parser recognizes the repository pattern: an `<a id="..."></a>` on its own line (single or double quotes both work), immediately followed by the owner's ATX heading `### REQ-001-AC-01: ...`; blank lines in between are allowed. The anchor is the lowercase form of the full heading ID. Both `AC` and design-verification `VC` are supported; IDs in text, links, other owners' headings, comments, indented code, or backtick/tilde fences never enter the acceptance inventory. It is not a general Markdown renderer and does not derive implicit heading anchors.

For the example above, `acceptance_ids` returns `sample/CTX-001/REQ-001#req-001-ac-01` and `sample/CTX-001/REQ-001#req-001-ac-02`, not `AC-01`. Each `Acceptance` also keeps the full heading ID, owner, anchor, and original line numbers of the heading and anchor. A missing or duplicate anchor is an error.

Existing documentation is not moved, renumbered, or overwritten. Add frontmatter explicitly only after the scope is confirmed; the parser does not batch-convert old documents or forms. Ordinary documentation without frontmatter can be read directly, but Passing it explicitly yields `MISSING_FRONTMATTER`; no default artifact is silently generated.

<a id="bc-configuration"></a>
## 2. Optional BC configuration

[bc-config.schema.json](bc-config.schema.json) is data configuration, not a shell manifest.

| Field | Meaning |
|---|---|
| `schemaVersion`, `projectId` | Data version and project identity |
| `boundedContexts` | Non-empty list; each entry has only an explicit `id`; the scope is formed from the project and this ID, so no separate scope is stored to drift |
| `domainSources` | List; each entry requires `id`, `kind: local / git`, `root`, `path`, `baseline`, and `readOnly` |
| `developmentRegistration` | Repository-relative path and required anchor to the existing development registration; commands, credentials, and environment variables are not copied |

`root` keeps the explicit source root (a local directory, a selected clone root, or a Git repository location); `path` separately stores the relative location inside it. `id` is the short identifier later onboarding uses to reference the source. The schema does not connect to Git, access remotes, or create submodules, and `readOnly: false` grants no write permission. Actual path, object type/readability, source ID conflicts, and registration matching still require a later source-onboarding check.

Check these original fields read-only first with [local domain-source onboarding](../../docs/domain-sources.md); it adds no schema or execution manifest. Registering an existing source only edits the explicit BC source list and never overwrites the domain directory. The optional submodule is a separate local materialization operation that requires consent for the target and the index; completing it does not register the BC automatically. Network sources remain unavailable or proposal-only; their exact commit/raw-file digest, root/path separation, and readOnly semantics match the collector below, and no clone, staging, commit, or write-back permission derives from the configuration.

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

`unverified` has empty references and a specific non-empty gap; `partial` has at least one known artifact/evidence reference plus a specific gap; `available` has no gap and keeps at least one source reference (a known empty source is also located through an evidence reference). These states do not mean business acceptance, approval, or release. Missing required fields, invalid references, or a malformed primary-object baseline are invalid input data, not nine empty views.

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

This schema validates only the shape of view data; it does not look up sources, derive fields, verify scope/baseline consistency, or detect hand edits. Callers must still check real sources and evidence; schema-valid does not mean exporter-generated or run-verified.

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

There is no global "passed" field; empty entries or empty evidence cannot establish a pass. Even a structurally valid pass must still be checked against the actual object, each target, the execution counts, and the results; the schema does not authenticate the report, run tests, or write back to read-only sources. Changing this version's fields requires an explicit version/contract change; unknown fields are never silently tolerated.

### 4.1 Collection scope and exact object

`collect_implementation_report.build_report(root, object_sha, evidence_files, *, scope=None)` reads existing VTs and introduces no separate execution-input ledger. `root` must be an explicit local Git checkout root, and `object_sha` a readable full commit ID; None, branches, short hashes, tag/tree/blob objects, and unavailable objects are rejected, with no fallback to HEAD/index and no fetch. The report's `object.root` is `.`.

The primary `bc-config.yaml`, formal artifacts, and code/test text are read from regular blobs of that commit; current working files, the index, or another HEAD never replace them. The scope comes from the configured project/context. It may be omitted with one BC; with several, `scope` / `--scope` must be passed explicitly, and the first is never picked. All owner AC/VC of the scope are inventoried first, including items without a VT, and evidence is collected afterwards. A scope that does not exist or has no acceptance criteria is an input error. Upstream items from other scopes serve only as sources and never add delivery items.

The configured `developmentRegistration` must point to a real file/anchor in that object. A domain `root` is an explicit local directory relative to this checkout (`../domain-source` can select an authorized standalone source); environment variables are not expanded, and URLs, UNC paths, or personal absolute paths are not accepted. `path` is interpreted only relative to that root. A SHA256 baseline applies to the raw bytes of one file; a full Git commit applies to a file or directory at the same path and must match the actual local file set/bytes. Directory comparison does not follow links or initialize gitlinks, and Git sources accept only commits. `readOnly` keeps the original declaration; false grants no write permission either, and the collector never changes sources, the index, config, or permissions. Domain files overlapping the primary object must also match the bytes inside it.

### 4.2 VT files and run selection

`evidence_files` is a list of strings, each a root-relative `verification/VT-001.md` or `verification/VT-001.md#vt-001-run-01`, not a JSON or YAML document with copied states. Each file must be a VT at the same path with the same owner/scope as in that object. Runs may be appended after the test object; the current file and raw reports are referenced by their own byte digests, never recorded as new bytes of the test object.

No argument (CLI) or empty list (API) means no run is selected; current VTs are never scanned implicitly to fill in results. A missing or out-of-root path, duplicate selection, or unknown anchor is an input error. A file without a fragment selects its run only when it has exactly one owned run; zero runs keep each target not-run, and multiple runs require an anchor. If selected runs involve the same target, it is reported as ambiguous (identical, conflicting, or different baselines); the newest, last, or most favorable result is never adopted, and fields are never stitched across runs.

Only `vt-…-run-NN` subheadings inside this VT's `runs` H2 that belong to this owner are read, under the strict section boundaries and comment/fence exclusions. Same-level or higher H2/H1 headings, example code, comments, file names, and Approved are not runs. Each selected run needs the original form's four-column per-criterion result table, with exactly one row per declared criterion; the execution table need not be copied before the parent heading.

Collection accepts this **limited value syntax for the original form fields**; non-conforming records are input errors, never migrated automatically or interpreted by guessing at natural language:

| Original field | Supported values |
|---|---|
| Date, executor, and mode | `YYYY-MM-DD; recorder=<named recorder>; mode=command` or `mode=manual`; only a locating declaration, not identity authentication |
| Actual object baseline | The full commit ID requested for this collection |
| Requirement/design/task basis baseline at the time | `scope/OWNER@baseline`, with multiple owners separated by `;`; must cover exactly the target owners of this VT |
| VT baseline at the time | A full local commit of this VT, or the `sha256:` of the raw file within the object; not a digest taken after the current new run was added |
| Actual environment and tool versions | An actual named environment description; must not be a placeholder such as `Not configured`, `Not provided`, `Not run`, `TBD`, or `Unknown` |
| Actual working directory | In command mode, a relative directory that exists in the object, or `.`; manual mode may describe a non-command check |
| Actual command or manual steps/test identifier | Actual command text or concrete manual operations; read only, never executed. Command-mode targets must give their real testId |
| Exit code and discovered/executed/skipped counts (when applicable) | command: `exit=0; discovered=2; executed=2; skipped=0`. executed excludes skipped; discovered must equal executed + skipped. Auto/manual splits are not derived from these totals. Manual mode requires neither this row nor invented counts |
| Raw report and exact location | `[description](path-relative-to-this-VT#optional-anchor) @ baseline`; multiple entries separated by `;`. May be `not-run` only when the run was not run or was skipped |
| Report accessibility and limitations | A description of the actual access scope and limitations |

Two-column table values use the existing reader and cannot contain `|` (even escaped); a `;`-separated list cannot contain another semicolon within one item. A link with spaces in its path uses `[description](<../reports/raw report.txt>)`. This is limited input syntax, not a general importer for Markdown or local runner reports.

A baseline is a raw `sha256:` or a full local Git commit (raw reports also accept a blob). If a requirement baseline is not object_sha, **identical whole-file bytes** must be verified per owner; the VT baseline must verify identical plan content. The VT plan projection excludes only the real `runs` and `applicability` H2 sections (with their child blocks); all other frontmatter/body/newline bytes must match. No declared `criterionAnchor` may lie inside an excluded subtree, even if not-run this time; the comparison returns `INVALID_CRITERION` rather than discarding the criterion with its run records. The supplied VT is also compared with the object's plan; changing targets, criteria, methods, or non-excluded content cannot reuse old results by appending a run.

A pass/fail row needs an independent, specific observation and a link to its raw report; the link must match a path/fragment/baseline already verified in this run's report field. The report must be readable and non-empty; a Markdown fragment must be a real explicit anchor, a JSON/YAML fragment a top-level key, and other files support no fragments. A fail keeps the reason for the difference. In command mode, zero discovered, zero executed, all skipped, no matching testId, or mere success wording cannot form a pass/fail. Mixed results keep each row and are never merged into a global pass. A record with only passes but a non-zero command exit is rejected. Manual mode uses concrete steps and per-item observations and requires no command or fabricated counts.

In command mode, `executed` must be at least the **number of distinct testIds** of the pass/fail rows; otherwise it is `INVALID_EXECUTION`. One test covering several independent criteria counts once; an executed count above the mapped test count may be kept. skipped/not-run rows do not consume this minimum, manual mode does not apply command run counts, and counts cannot be derived from test names in the command text.

When no run is selected for a target, the target still appears in entries with execution not-run, empty evidenceRefs, and an explicit reason. A selected not-run/skipped keeps its reason and original-record reference, and is never filled with another target's success. The result states only that **source declarations** meeting these structural and baseline conditions were read; it cannot prove external events happened or authenticate human approval.

### 4.3 Code/test text location and applicability

Supported markers are whole-line comments in ordinary UTF-8 source files: `# implements: scope/OWNER#ac symbol=name` and `# verifies: scope/OWNER#ac testId=test_name` (the `//` prefix works too). The next non-empty text that is not a line comment must contain the given identifier followed by `(`; the identifier is a single identifier starting with an ASCII letter or underscore. This is text location, not language parsing, runner discovery, or test execution; unsupported markers are reported as errors. Markdown, JSON/YAML, forms, and dependency directories are not marker inputs. Paths come from actual Git blobs; code/test directories or file names are never guessed.

A marker must reference an actual owner acceptance criterion by full reference; the same short ID in another scope does not satisfy it. A declared VT `testId` must match the actual marker and location. The report stores only the path, object baseline, and explicit symbol/testId; without a marker the reference is empty, and implementation is never inferred from file names.

Default applicability is unverified. Independent re-review uses the VT's original `applicability` table: `Original run/result and target link` is `[Run](#vt-001-run-01) [Criterion](#allow)`; `Current object, requirement, and VT baselines` is `object=<full-commit>; requirement=scope/OWNER@baseline; vt=baseline`; `Review date and recorder` is `YYYY-MM-DD; recorder=<recorder>`; `Applicability` is `unverified` / `applicable` / `not-applicable`, with a specific rationale. Only a row whose run, criterion, object, and verified requirement/plan baselines all match can support its state; multiple matching rows are ambiguous, and re-reviews of other objects are not carried over. Applicability is independent of execution results; a pass or the same commit never automatically yields applicable.

### 4.4 Read-only output and model bridge

The API and default CLI do not write files. The CLI uses `--root` and `--object` explicitly and accepts repeated `--evidence`; only `--output` creates a new `.json/.yaml/.yml`, and its parent directory must already exist. Overwriting any existing location is refused, and output must not target object files, BC/domain/VT/raw-report locations, or declared optional-source locations, even if currently missing. The report's declared domain `root + path` protects that location and its children before baseline validation, without requiring the baseline to exist or be valid. If a `domainSources` location is incomplete, cannot be resolved safely, or the container is invalid, the read-only view can keep an optional gap, but every explicit output is refused; a read gap never becomes write permission. If the location resolves completely and only the baseline is missing, a disjoint new output location is still possible, without forging a valid source. Exit 0 = successful collection (possibly all not-run); 1 = a per-item fail was collected; 2 = input/output error. The CLI exit is never treated as the source VT's exit.

A report can be **selected separately and explicitly** in the `verification` list of the existing `model-sources.yaml`; there is no new selection manifest. After the adapter validates the report's schema, scope, source-reference baselines, and rebuildability, the model's `implementationReports` and verification view store only the report file and its baseline, not entries, states, observations, or applicability. The other eight views and existing verification sources are still read per the existing selection; nine-view gap semantics are unchanged. The report has no views, and governance/risk/SEQ/QAS/release references are never disguised as execution evidenceRefs.

<a id="model-sources"></a>
## 5. Optional model-source manifest

[model-sources.schema.json](model-sources.schema.json) and the [blank source form](../../_templates/config/model-sources.yaml) only register source selections. When adopted, the manifest is `model-sources.yaml` in the selected documentation root; no second BC/model/execution manifest is added. The original four contracts, 32 kinds, and nine views are unchanged.

The manifest has only `schemaVersion: 1` and `scopes`. `scopes` maps explicit `project/context` keys to a map of needed views among the nine; each view maps to a non-empty list of `{path, baseline}`. `scopes: {}` is a valid empty map and does not mean a real project is registered; a scope value of `{}` means no view source is selected yet. Duplicate YAML keys, duplicate paths within one view, or conflicting baselines for one path are configuration errors, never merged by overriding.

`path` is the relative path of an actual file inside the root; non-ASCII characters and spaces are allowed, while network/absolute paths, parent traversal, anchors, backslashes, control characters, and leading/trailing whitespace are rejected. A resolved symlink/junction cannot escape the root. `baseline` is the `sha256:` digest of the raw file bytes, or a full lowercase local Git commit/blob ID. A commit baseline must locate a regular blob at the same path in the explicit checkout root, and the blob must match the bytes read exactly; branches, HEAD, short hashes, tag/tree, textconv, or network access cannot substitute. The manifest is not a permission; it contains no root/URL, commands, credentials, body text, results, approvals, or write-back switches.

Replace the paths and digests with actual local inputs; the example does not refer to existing documentation:

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

Errors in the primary root, scope, schema, formal inventory, or primary baseline always fail; an invalid manifest also fails and cannot be downgraded to "missing optional source". An optional file in a valid manifest that is missing, unreadable, malformed, or has an unverifiable baseline makes only the selected view `unverified`, with empty refs and a specific source gap. A valid but incomplete source gives `partial`; a complete source gives `available`. These states describe only the sources and are never a pass or approval.

No manifest, a manifest without the selected scope, and a scope without a given view each produce an explicit gap. If the primary inventory contains the scope, a missing registration does not block the primary artifact index; a nonexistent primary scope is still an input error and cannot be invented through the manifest. Sources are existing formal Markdown artifacts or YAML/JSON summaries (next section); model body text need not be copied. A persisted derived model can never be a source.

### 5.1 Two read shapes for existing sources

Prefer the original artifacts; do not copy the business model for the tools. Formal Markdown reuses the artifact parser and original explicit anchors: the source version uses a raw-byte baseline, the content declaration stays in metadata, and meaning and results stay in the body. Views keep the owner's anchors, related `upstream` / `targets` navigation, and file baselines. When selected artifacts and their dependencies lack a category or section a view needs, the view is `partial`; fields are never filled from file names.

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

A section alone or a generic body paragraph does not locate the original summary fields. Direct Markdown also checks the following **table values in the original owner** (two-column tables); when one is absent, a field-level `partial` gap is kept, and nothing is inferred from code arrows, metadata states, file names, or common values. The version is located by the actual object baseline; IDs and relations still come from the parser. These values are not new frontmatter fields and need no model copy.

| Source location | Values that must be locatable (`/` separates accepted original labels) |
|---|---|
| US `task` | `Task progress/status`; contentState never substitutes for task progress |
| ABB `runtime` | `language/Implementation language`, `framework/Framework`; if not yet selected, the item is missing and no default stack is chosen |
| SEQ `paths` | An explicit `true/false` declaration of `hasAsync/Asynchronous interaction`; never inferred from Mermaid arrows |
| SEQ `participants` | An existing integration-partner upstream; without one, an explicit source statement for `externalPartners/External partners` is needed, including when it is known that there are no partners |
| This owner's `vt-…-run-NN` child blocks under VT `runs` | Date, notes, the three run baselines, and explicit auto/manual counts are read from each child block; actual results come from its multi-column per-criterion table, with no copy needed before the `runs` heading |
| QAS `scenario` | All six values of the existing six-element table; the original field labels `stimulusSource/stimulus/environment/object/response/responseMeasure` are accepted as well |
| review-record `decision` | `status/Review conclusion`, `notes/Limitations and notes`; reading the declaration does not authenticate approval |
| risk-control `analysis` / `residual` | `preMitigationLevel/Pre-mitigation risk`, `residualRiskLevel/Residual risk`; risk is neither computed nor accepted |
| development-log `release` | The five original field values `lifecycle/safetyClass/currentVersion/lastReleaseDate/nextPlannedRelease`; change control is still located through its own separate original section |

Duplicate or missing values for one field, an explicit unknown value or placeholder (such as `Unknown`, `Not provided`, `Not run`, or `TBD`), a missing original section, and a missing required relation are each a specific gap. Counts are non-negative decimal integers; booleans accept only `true/false`; a known zero or false is not missing. Header and separator rows alone are not content. A SEQ diagram must be a genuinely closed Mermaid code fence inside its `diagram` section, with a sequence header and messages. HTML comments, examples inside an enclosing literal fence, unclosed fences, or ordinary notes cannot fill a gap; the body and diagram reuse the same comment/fence state machine, and raw text is never rescanned to guess a diagram. Unsupported shapes keep specific gaps and are not migrated automatically.

Quality can select the original QAS Markdown and an existing utility-tree YAML/JSON side by side in the same manifest view. The tree file's top-level `tree` is a mapping/list; the data stays in that file, and the export keeps only `file#tree + baseline`, adding no kind and copying no tree nodes. An empty `tree` is an entry gap in a known source (partial). No QAS, no tree source, or an unreadable, malformed, or unverifiable tree gives unverified, empty refs, and a specific missing-source reason. Only after both QAS and tree are verifiable can a missing response measure or partial scenario set give partial. An existing `quality.utilityTree` evidence pointer can also be referenced directly.

Business nodes in the tree may contain `root` and `path`; these keys alone do not declare domain file locations and neither restrict nor rename the values in them. The location protection that applies without a baseline belongs only to actual `domainSources` entries; elsewhere, the existing handling of complete `root/path/baseline`, `reference`, or `path + baseline` applies, and no path is inferred from these two business keys.

Direct VT pairs each `vt-…-run-NN` anchor inside the real `runs` H2 with the heading that immediately follows it (blank lines/comments allowed). Only lower-level headings inside that H2 are owned runs; an anchor before the same-level H2 or higher H1 that ends the section borrows no heading, and notes, code, or another anchor cannot borrow a later one. Child blocks stay isolated by strict anchor boundaries. It reads the original form's `Date, executor, and mode` and `Report accessibility and limitations`, the three baselines (actual object, requirement basis at the time, and VT), and four columns: `Criterion link (target located by frontmatter)` / `Actual observation and raw report location` / `Actual result` / `Not-run/skip reason or failure difference`. Every declared criterion needs its own result row; duplicate, missing, or invalid-state rows, and unknown criteria, produce gaps with source locations. Results are not copied into the model.

Auto/manual counts come only from explicit `automatedCount/Automated check count` and `manualCount/Manual check count` rows in that run block, or from the two items stated in the original `Exit code and discovered/executed/skipped counts (when applicable)` value (for example `Automated check count 0; Manual check count 2`). They cannot be derived from total discovered/executed counts, result-row counts, or file names. Each run keeps its own source anchors/baselines; complementary missing fields cannot be stitched into one complete run. Same object/requirement/VT baselines with conflicting results keep both references, marked with a partial conflict gap. Complete historical records with different baselines are located separately; the newest is not selected and nothing is merged into a global result.

Existing YAML/JSON summaries can be selected directly as sources. Their top level holds the objects in the table below; one file may hold several known summaries, but it is **not a model derived by this tool**. Values stay maintained by the source; the export stores only `file#summary-key + baseline` plus the references below, and copies no status, result, measure, or safety classification. JSON is read as a compatible YAML subset by the same safe reader, which rejects duplicate keys, dangerous tags, and circular aliases.

In the table, `ref` is a canonical reference to an existing owner/explicit anchor, not a short ID. `evidence` is the `{reference, baseline}` of an actual local file, verifiable by raw bytes or an exact local Git object; a Markdown fragment is a real anchor, a YAML/JSON fragment a real top-level key, and other files take no fragment. Array relations are never completed from a suffix or title. Each object may add `evidenceRefs: [evidence]` to locate its original records; this is not an execution authorization.

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

A missing whole summary object or a wrong field type is an optional-source format error: `unverified` with empty refs. A supplied source with a missing, null, or empty field, or a missing required relation entry, is `partial`; the gap carries the source file and full field path (for example `sequenceSummary.entries[0].externalPartners`), and known refs and source pointers are kept. QAS and the utility tree are required components of quality; a missing one is handled as unverified first and cannot be downgraded to an ordinary field-level partial. An explicitly empty `entries/blocks` is a verifiable empty summary; an empty `srIds/usIds/vtIds/testScenarios` list reports a missing relation, while an explicitly empty `externalPartners/integrations/rcIds/reqIds/vtCoverage` list never implies nonexistent objects. `false` and `0` are valid source values; string booleans and boolean counts are not valid types. A referenced owner/anchor, file, or baseline that cannot be verified makes the result `unverified`, and unconfirmable references are not kept.

When a view has several sources, any unverifiable source makes it `unverified` and clears its refs; if all are verifiable but have structural gaps, it is `partial`. Other views are not affected. Each state describes only the structure and locatability of the selected sources; full text, numeric/async meaning, approval authenticity, and result applicability must still be judged against the original owner.

### 5.2 Explicitly referencing implementation reports

Verification sources can also select a [v1 implementation report](#implementation-report) with the same `{path, baseline}` item; the baseline must match the generated report's bytes, and no execution entries are copied into the manifest. The adapter rebuilds the report read-only to check its object and owned VT references. If the object is unreadable, the report was hand-edited, the scope mismatches, or the original records have drifted, that optional view is unverified and its report references are cleared.

Existing verification sources can be selected alongside the report; the model adds only file/baseline pointers, copying no entries, results, or applicability, and other sources keep their original semantics. A report being `available` is not a pass; with no report selected, `implementationReports` stays an empty array. Building a report never modifies the manifest or the source model.
