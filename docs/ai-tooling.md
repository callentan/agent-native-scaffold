# AI tool use and bounded evaluation

This page applies when a project keeps a basis for its use of AI or other assistive tools; a qualification file is not required for every small maintenance task. It does not specify models, vendors, tech stacks, or authorized uses; a tool name, paid edition, role, or passing parser is not a qualification decision.

<a id="adoption"></a>
## Adoption and recording boundaries

When a standalone evaluation record is needed, use the [tool qualification and use form](../_templates/items/tool-qualification.md) at its default location `verification/TQ-NNN-<slug>.md`. When an independent review or waiver is needed, use the [existing review form and decision guidance](governance.md#decisions), not a new role pipeline. Check material with [verify-change](../.github/skills/verify-change/SKILL.md), change documents with [implement-task](../.github/skills/implement-task/SKILL.md), and hand off with [record-handoff](../.github/skills/record-handoff/SKILL.md); complete methods live only in those files.

Distinguish four things:

| Information | Required basis |
|---|---|
| Proposed use | The current task, object, input categories, allowed/excluded scope, and known issues; this is not authorization |
| Evaluated limited behavior | The actual tool/version, configuration, environment, evaluation inputs/criteria, run steps, and the baseline of the raw observations/report |
| Declared authorization to use | A locatable named decision, the basis of accountability/authority, the allowed scope, limitations, and the decided baseline; the text still does not authenticate identity |
| Current applicability | A comparison of the current object/use/version/configuration with the original evaluation and original decision, and any need for re-evaluation; it is not inherited automatically from historical results |

Tools may give wrong explanations or unstable output, so the evaluation should cover the normal, missing-input, conflict, refusal, and forbidden-side-effect boundaries the task actually relies on. Record only inputs, methods, and observations actually run. Without an environment, evaluation evidence, or a decision maker, keep the record as a draft with precise gaps; do not record a demo, a model's self-assessment, or a completed form as qualified. Collect evidence separately for documentation tool checks, business execution, and human decisions.

<a id="minimal-record"></a>
## Minimal necessary record

Enough pointers for a handoff in the existing task, log, or tool record suffice; do not duplicate ownership of original results.

| Element | What to keep |
|---|---|
| Task and time | Actual request/task entry point, date or time of this use, record scope |
| Object and source | Real file/section or owner-qualified ID, object and input baselines, accessibility |
| Tool and configuration | Actual tool name/version, model identifier where available, behavior-affecting configuration/method baseline, environment; write Unknown for an unexposed service version, do not guess |
| Use and data boundaries | Current use, allowed input categories, in/out of scope, forbidden side effects; only necessary metadata |
| Evaluation and result | Actual criteria/steps, check scope/count when applicable, entry points to the VT/raw report and their baselines; write `not-run` for anything not run |
| Decision and accountability | Original text of the actual decision, named role/person declaration, authorization scope and baseline; list a gap if any is missing |
| Follow-up needs | Limitations, open inputs, current applicability, conditions calling for further evaluation or decisions |

Full prompts/chats, access tokens, credentials, patient data, and production data are not required; do not copy sensitive interactions to document tool use. If an input is genuinely needed as evaluation evidence, check data authorization first, then use minimal necessary, de-identified, or self-owned synthetic material, stated as not representing real business samples. For usage/cost, cite only measurement definitions and bills actually provided; do not estimate missing values from text length, tool-call count, or model names.

<a id="interaction-ledger"></a>
## Optional minimal interaction ledger

Maintainers can use the [local ledger tool](../.github/utilities/README.md#interaction-ledger) to record explicitly provided minimal metadata; the blank form is [`_templates/reports/ai-interaction-log.csv`](../_templates/reports/ai-interaction-log.csv). It is not a required session archive, application service, or qualification system. Each append must give the path of an existing local CSV and the record fields explicitly. The tool searches no environment, personal configuration, session files, bills, or logs, makes no network access, and executes no commands or references found in fields.

A record stores only: version 1, a stable record ID, an ISO 8601 time with time zone, tool name/version, task and object references/baselines, an operation summary of at most 512 characters, optional decision/evidence references, and optional explicit usage values, units, and currency. References are plain text, not opened, parsed, or authenticated; a missing reference is empty in the CSV and summarized as unknown. The decision field stores only a source pointer; there is no decision outcome or approval field, and text such as "Approved" is not proof of approval or qualification. The ledger reflects only caller-provided data and authenticates no tool identity, actual use, sources, or authorization.

Usage values use non-negative, finite, plain decimal notation (negative numbers, NaN, Infinity, and exponent notation are rejected); original characters and decimal places are kept verbatim. Units are not inferred, and unknown usage stays empty rather than `0`. The summary computes exact decimal sums only over known records whose tool, version, unit, and currency match exactly, and lists unknown counts separately in stable order. Different units or currencies are not combined, and no "cost", "savings", or qualification conclusion is generated. Currency codes are caller-provided labels, not checked against a lookup table. Treat the ledger and CSV only as data: CSV quoting does not prevent spreadsheet formula interpretation, so do not open untrusted cells as executable formulas.

Before appending, the tool validates the fixed header, the version, and all existing rows. A malformed CSV, duplicate IDs among existing rows, conflicting IDs, and invalid times or usage are rejected explicitly; history is never rebuilt, truncated, or skipped. The same ID with exactly the same values is a no-change replay. Every write (appends and explicit summary files) requires the caller to pass `attest_local_storage=True` explicitly, or `--attest-local-storage` on the CLI; otherwise it is rejected with `WRITE_ATTESTATION_REQUIRED`, and no lock or output is created. The attestation only declares that the path is single-machine local storage that is neither network nor cloud-synced; it does not authenticate the caller, the actual OS disk type, or the storage vendor, and it is not a durability guarantee. Do not make this declaration for synced locations such as OneDrive. Windows drive letters and fixed-disk types do not decide availability, and the tool does not probe the environment, registry, or vendor to guess sync status.

By default, a summary without output reads the ledger once, takes no lock, and creates no `.lock` or other files; a source with corrupted formatting or a partial line returns a CSV input error rather than counting as complete. An explicit `--output` is a write: it requires the attestation above, reads the source once under the source lock, and creates the output by exclusive create without overwriting. A partial write or failure after creation returns recovery information, with no automatic deletion, rollback, or broad cleanup. The tool does not defend against malicious concurrent path replacement and does not claim an OS sandbox.

Reads and writes support local regular files the caller explicitly chooses on Windows, Linux, and macOS; the directory need not be inside a repository or virtual environment or on a fixed drive letter. Cross-host coordination for network or cloud-synced locations is out of scope; do not make a local-storage attestation for them. Appends use an adjacent `.lock` file and an exclusive local inter-process lock (`msvcrt` on Windows, `fcntl` on Linux/macOS); the lock sidecar is kept. External edits that do not honor the lock can still happen. Before writing under the lock, an append checks that ledger bytes are unchanged; if they changed, it returns `OWNER_BYTES_CHANGED` without writing. This is not a promise of isolation on arbitrary file systems or against malicious processes.

On an I/O failure during an append or a new summary output, the tool does not automatically delete or roll back unknown owner bytes; the error reports a recovery flag and expected/observed byte counts. On `recovery_required`, keep the file and manually inspect the last line or partial new output before deciding whether to recover or retry. An explicit `--output` only creates a new `.json` whose parent directory already exists, and never overwrites existing outputs, logs, or templates. The tool fails explicitly when target OS/file-system semantics are unsupported.

Without actual bills, vendor data, or authorized usage statistics, do not report real charges, usage, savings, or service effectiveness. The tool has no vendor pricing interface and does not replace VT run evidence, named review decisions, tool qualification, approval, or handoff. Follow referenced pointers to the original owner records.

<a id="requalification"></a>
## Changes to version, use, or baseline

When the tool or model version, behavior-affecting configuration or method, environment, data category, usage scenario, object or requirement baseline, or accountability policy changes, the original evaluation holds only for its original scope. Keep old records, decisions, and raw reports; add the new evaluation as a separate record or file linking the original baseline, and do not rewrite old results.

First state which behaviors and authorizations may no longer apply, and list the evaluations to redo, accountable owners, and open inputs; do not inherit the old qualification until required evidence is obtained. An unknown service version cannot be assumed to match the last one. Handle re-evaluation and decisions per the project's real accountability arrangements; do not derive a mandatory approval order from this page.

<a id="limits"></a>
## What records cannot prove

`confirmation` only stores this record's declaration per the [existing contract](../.github/contracts/README.md); it cannot authenticate the reviewer, actual tool permissions, or risk acceptance. Successful synthetic samples do not mean all inputs are reliable. An independent human review requires actual people and records; an Agent self-review cannot replace it.

An authorization record and actual execution permission are different things. Roles, trailers, text rules, or read-only fields do not configure ACLs, sandboxes, network policies, clients, or CI gates. Source access, execution, write-back, installation, external transfer, and release each still need their own authorization; for missing items, see [governance boundaries](governance.md#limits).
