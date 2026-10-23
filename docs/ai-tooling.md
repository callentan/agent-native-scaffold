# AI tool use and bounded evaluation

This page applies when a project decides to keep a basis for its use of AI or other assistive tools; it does not require a qualification file for every small maintenance task. It does not specify models, vendors, tech stacks, or authorized uses; a tool name, paid edition, role, or passing parser is not a qualification decision.

<a id="adoption"></a>
## Adoption and recording boundaries

When a standalone evaluation record is needed, use the [tool qualification and use form](../_templates/items/tool-qualification.md); its default location is `verification/TQ-NNN-<slug>.md`. When an independent review or a waiver is needed, use the [existing review form and decision guidance](governance.md#decisions) rather than a new role pipeline. Check material with [verify-change](../.github/skills/verify-change/SKILL.md), change documents with [implement-task](../.github/skills/implement-task/SKILL.md), and hand off with [record-handoff](../.github/skills/record-handoff/SKILL.md); the complete methods are maintained only in those files.

Distinguish four things:

| Information | Required basis |
|---|---|
| Proposed use | The current task, object, input categories, allowed/excluded scope, and known issues; this is not authorization |
| Evaluated limited behavior | The actual tool/version, configuration, environment, evaluation inputs/criteria, run steps, and the baseline of the raw observations/report |
| Declared authorization to use | A locatable named decision, the basis of accountability/authority, the allowed scope, limitations, and the decided baseline; the text still does not authenticate identity |
| Current applicability | A comparison of the current object/use/version/configuration with the original evaluation and original decision, and any need for re-evaluation; it is not inherited automatically from historical results |

Tools may give wrong explanations or unstable output, so the evaluation should cover the normal, missing-input, conflict, refusal, and forbidden-side-effect boundaries that this task actually relies on. Record only the inputs, methods, and observations that were actually run. Without an environment, evaluation evidence, or a decision maker, keep the record as a draft with the precise gaps; do not record a demo, a model's self-assessment, or a completed form as qualified. Collect evidence separately for documentation tool checks, business execution, and human decisions.

<a id="minimal-record"></a>
## Minimal necessary record

Keeping enough pointers for a handoff in the existing task/log or tool record is sufficient; do not duplicate ownership of the original results.

| Element | What to keep |
|---|---|
| Task and time | The actual request/task entry point, the date or time of this use, and the scope of the record |
| Object and source | The real file/section or owner-qualified ID, the object and input baselines, and accessibility |
| Tool and configuration | The actual tool name/version, the model identifier where available, the behavior-affecting configuration/method baseline, and the environment; write Unknown for a service version that is not exposed instead of guessing |
| Use and data boundaries | The current use, allowed input categories, what is in and out of scope, and forbidden side effects; record only the necessary metadata |
| Evaluation and result | The actual criteria/steps, the check scope/count (when applicable), and entry points to the VT/raw report and their baselines; write `not-run` for anything not run |
| Decision and accountability | The original text of the actual decision, the named role/person declaration, and the authorization scope and baseline; list a gap if any of these is missing |
| Follow-up needs | Limitations, open inputs, current applicability, and the conditions that call for further evaluation/decisions |

Saving full prompts/chats, access tokens, credentials, patient data, or production data is not required; do not copy sensitive interactions just to document tool use. If a specific input is genuinely needed as evaluation evidence, first check the data authorization, then use minimal necessary, de-identified, or self-owned synthetic material, and state that it does not represent real business samples. For usage/cost, cite only the measurement definitions and bills actually provided; do not estimate missing values from text length, number of tool calls, or model names.

<a id="interaction-ledger"></a>
## Optional minimal interaction ledger

Maintainers can use the [local ledger tool](../.github/utilities/README.md#interaction-ledger) to record minimal metadata that was explicitly provided; the blank form is [`_templates/reports/ai-interaction-log.csv`](../_templates/reports/ai-interaction-log.csv). It is not a required session archive, application service, or qualification system. Every append must explicitly give the path of an existing local CSV and the record fields; the tool does not search the environment, personal configuration, session files, bills, or logs, does not access the network, and does not execute commands or references found in fields.

A record stores only: version 1, a stable record ID, an ISO 8601 time with time zone, the tool name/version, task and object references/baselines, an operation summary of at most 512 characters, optional decision/evidence references, and optional explicit usage values, units, and currency. References are stored as plain text and are not automatically opened, parsed, or authenticated; a missing reference is empty in the CSV and summarized as unknown. The decision field stores only a source pointer; there is no decision outcome/approval field, and writing text such as "Approved" is not proof of approval or qualification. The ledger reflects only the data the caller provides and does not authenticate tool identity, actual use, sources, or authorization.

Usage values use non-negative, finite, plain decimal notation (negative numbers, NaN, Infinity, and exponent notation are rejected), and the original characters and decimal places are kept verbatim; units are not inferred, and unknown usage stays empty rather than `0`. The summary computes exact decimal sums only over known records whose tool, version, unit, and currency match exactly, and lists unknown counts separately in a stable order; different units/currencies are not combined, and no "cost", "savings", or qualification conclusion is generated. Currency codes are caller-provided labels; the tool does not validate them against a lookup table. Treat the ledger and the CSV only as data; CSV quoting does not prevent spreadsheet formula interpretation, so do not open untrusted cells as executable formulas.

Before appending, the tool validates the fixed header, the version, and all existing rows. A malformed CSV, duplicate IDs among existing rows, conflicting IDs, and invalid times/usage are all rejected explicitly; history is never rebuilt, truncated, or skipped. The same ID with exactly the same values is a no-change replay. Every write operation (appends and explicit summary files) requires the caller to pass `attest_local_storage=True` explicitly, or `--attest-local-storage` on the CLI; by default the operation is rejected with `WRITE_ATTESTATION_REQUIRED` and no lock/output is created. This value is only the caller's declaration that the selected path is on single-machine local storage that is neither network nor cloud-synced storage; it does not authenticate the caller's identity, the actual OS disk type, or the storage vendor, and it is not a durability guarantee. Do not make this declaration for synced locations such as OneDrive. Availability is not decided by Windows drive letter or fixed-disk type, and the tool does not probe the environment/registry/vendor to guess sync status.

By default, a summary without output reads the ledger once, takes no lock, and creates no `.lock` or other files; a source with corrupted formatting or a partial line returns a CSV input error instead of counting the partial line as complete. An explicit `--output` is a write operation: it requires the caller's attestation above, reads the source once under the source lock, and creates the output with the standard library's exclusive create, without overwriting existing content. A partial write or a failure after creation returns recovery information, without automatic deletion, rollback, or broad cleanup. The tool does not defend against malicious concurrent path replacement and does not claim to provide an OS sandbox.

Reads and writes support local regular files explicitly chosen by the caller on Windows, Linux, and macOS; the directory need not be inside a repository or virtual environment or on a fixed drive letter. Cross-host coordination for network or cloud-synced locations is out of scope, and callers should not make a local-storage attestation for them. Appends use an adjacent `.lock` file; an exclusive inter-process lock on the local machine is implemented with `msvcrt` on Windows and `fcntl` on Linux/macOS, and the lock sidecar is kept. External edits that do not honor the lock can still happen. Before writing under the lock, an append checks that the ledger bytes are unchanged; if they changed, it returns `OWNER_BYTES_CHANGED` without writing. This cannot be taken as a promise of isolation on arbitrary file systems or against malicious processes.

When an I/O failure occurs during an append or a new summary output, the tool does not automatically delete or roll back unknown owner bytes; the error reports a recovery flag and the expected/observed byte counts. On `recovery_required`, keep the file and manually inspect the last line/partial new output before deciding whether to recover or retry. An explicit `--output` only allows creating a new `.json` file whose parent directory already exists, and does not overwrite existing outputs, logs, or templates. The tool fails explicitly when the target OS/file-system semantics are not supported.

Without actual bills, vendor data, or authorized usage statistics, do not report real charges/usage, savings, or service effectiveness. This tool has no vendor pricing interface and does not replace VT run evidence, named review decisions, tool qualification, approval, or handoff. Referenced pointers must still be followed to the original owner records.

<a id="requalification"></a>
## Changes to version, use, or baseline

When the tool or model version, behavior-affecting configuration/method, environment, data category, usage scenario, object/requirement baseline, or accountability policy changes, the original evaluation holds only for its original scope. Keep the old records, decisions, and raw reports; add the new evaluation as a separate record or new file that links the original baseline, and do not rewrite old results.

First state which behaviors and authorizations may no longer apply, and list the evaluations to redo, the accountable owners, and the open inputs; do not inherit the old qualification until the required evidence has been obtained. An unknown service version also cannot be assumed to match the last one. Handle the specific re-evaluation and decisions according to the project's real accountability arrangements; do not derive a mandatory approval order from this page.

<a id="limits"></a>
## What records cannot prove

`confirmation` only stores this record's confirmation declaration per the [existing contract](../.github/contracts/README.md); it cannot authenticate the reviewer, actual tool permissions, or risk acceptance. Successful synthetic samples in a tool evaluation do not mean that all inputs are reliable; an independent human review requires actual people and records, and an Agent self-review cannot replace it.

An authorization record and actual execution permission are two different things. Roles, trailers, text rules, or read-only fields do not configure ACLs, sandboxes, network policies, clients, or CI gates. Source access, execution, write-back, installation, external transfer, and release each still need their own authorization; for handling missing items, see [governance boundaries](governance.md#limits).
