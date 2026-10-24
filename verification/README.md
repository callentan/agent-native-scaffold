# Verification, coverage, and results entry point

This directory holds verification plans, target references, gaps, and run-record entry points; it does not hold test code. Use the [VT form](../_templates/items/verification-test.md) for a verification artifact and save it as `verification/VT-NNN-<slug>.md`. There are no formal acceptance criteria or VTs yet; an empty table does not mean coverage is complete or anything has passed.

<a id="layers"></a>
## Distinguish verification layers first

| Layer | What it verifies | Target reference example (all placeholders) |
|---|---|---|
| Business acceptance | Users' business goals, rules, and business-observable outcomes | `REQ-NNN-AC-01`, pointing to the stable anchor in the REQ |
| Software behavior | Specified software behavior, boundaries, errors, and side effects | `SR-NNN-AC-01`, pointing to the stable anchor in the SR |
| Applicable design verification | Sourced structural, collaboration, or design constraints | For example `ABB-NNN-VC-01`, pointing to the constraint owner |
| Standalone maintenance or document check | Explicit completion conditions of the current request or issue | For example `TASK-NNN-AC-01`, pointing to a fixed subsection or record in the actual task source |

A passing software check does not automatically imply that business acceptance has passed. A document check only shows that the structure or content of documents conforms to the conventions within the checked scope; it is not execution of business or software behavior. One VT can cover several targets in the same layer, and several VTs can cover one target, but every target needs its own standalone criterion; different layers should preferably get separate VTs.

<a id="domain-scenarios"></a>
## Optional domain scenarios and target declarations

The [validation scenario form (TS)](../_templates/items/validation-scenario.md), saved as `verification/TS-NNN-<slug>.md`, can plan within-context, cross-context, REQ business acceptance, or QAS scenarios; it is not application test code. A standalone business criterion can be owned by a UC, REQ, INV, or QAS; the scenario references its specific AC anchor, and rules stay referenced in the original domain text. A scenario without sufficient sources stays a draft/question and produces no definite behavior.

New TS and [VT forms](../_templates/items/verification-test.md) adopt the [existing metadata contract](../.github/contracts/README.md):

- The frontmatter holds only identity, scope, content state, `upstream`, and `targets`; the body holds the per-target judgment method, plan, actual results, and current applicability. Old VTs are not migrated or renumbered automatically, and reading them does not require installing the parser.
- Each target gives the full `scope/id#anchor` and the current file's `criterionAnchor`; the optional `testId` takes only a real test identifier. A target is not a generic file title; `AC-01` alone is not enough, and when different contexts reuse a number, look items up by full identity.
- Each target has its own criterion block in the body with an explicit anchor, stating the preconditions, steps/observation points, expected outcome, forbidden side effects, and open conditions; add the block together with the target. The body may navigate to source items, but do not hand-maintain another target mapping or an overall pass status.
- Check that the target file, owner, scope, and AC/VC anchor actually match. The parser checks only local criterion anchors. When execution is authorized, the [coverage tool](../.github/utilities/README.md#traceability) can cross-check the full inventory, but it gives only a structural lower bound for layered/standalone criteria and does not prove semantic sufficiency.

This only illustrates one `targets` entry; adopt it only after replacing all placeholders and creating the actual `criterion-01` anchor in the body:

```yaml
- target: PROJECT/CTX-NNN/UC-NNN#uc-nnn-ac-01
  criterionAnchor: criterion-01
```

Scenario Markdown holds sources, criteria, and step observation points. When a `.feature` file exists, link to its single Gherkin text and baseline instead of copying it; for a proposed path only, write "proposed, not created" in plain text, with no broken file link and no implication that a runner exists. A QAS that lacks a measurement criterion cannot be recorded as verified.

For actual runs, choose one owner record, the TS or the VT; if the VT holds it, the TS only links to its run block and does not duplicate the result. Record each target's run result, reason for not running, and original baseline separately; never record document use or a schema/parser check as business execution.

<a id="feature-companion"></a>
## Gherkin companion and BC verification plan

For planning, see [specify-feature / plan-verification](../.github/skills/specify-feature/SKILL.md#plan-verification). Start from the actual UC/INV/REQ/QAS, SR, or design criteria; no US/ABB is needed first. Once the required inputs are complete, VTs and architecture design can proceed independently.

When behavior suits Gherkin, use the [blank feature](../_templates/items/verification-test.feature), with the same name and directory as its owning VT. Keep the normal, rejection/negative, boundary, and error paths known from sources; do not prefill actors, response metrics, failure policies, or safety-critical tags without a source. For a non-behavioral QAS or missing measure, keep only the specification/gap; do not force an executable scenario.

- The `.feature` file is the sole owner of the Given/When/Then text; the Markdown holds target metadata, standalone criteria, file and baseline navigation, preconditions, and evidence, and no second Gherkin copy.
- `targets[].testId` only locates a scenario/native test that actually exists; `criterionAnchor` corresponds to a standalone criterion in the current Markdown. File/scenario names are textual locators; while no runner is configured, they are not executable selectors and cannot claim automation.
- Before adding a scenario, check the original ACs and coverage for each target. When running, record the actual baselines of the `.feature` file, step implementations, object, requirements, and VT together so the companion and plan do not drift apart.
- A file, an Approved tag, or a test file name is neither a pass nor a certification. Without an application, step implementations, a runner, an authorized command/cwd, or a report, behavior verification stays `not-run` and the exact missing items are listed. If only a text/syntax/mapping check was performed, report only that layer and do not claim the Gherkin ran.

<a id="coverage-check"></a>
## Start checking from all acceptance criteria

1. **Determine the scope and baselines first.** Read the current task, in-scope REQs and SRs, necessary UC/INV/QAS and design, and standalone completion conditions; record the scope basis and each artifact's version. For a maintenance request with no persistent task source, keep the summary and fixed identifiers in the existing task or in the [task basis section of the log](../logs/README.md#task-basis); do not invent a stakeholder requirement.
2. **Inventory acceptance criteria first, then look for VTs.** List the owning artifact, full ID, and original-text link of every in-scope AC, including those without a VT. Do not derive the list backwards from existing VTs; implementation checkboxes in a US do not replace the original ACs.
3. **Find coverage item by item.** Search VT target fields and check whether the layer, specific target, per-target expected outcome, method, and preconditions are sufficient. Record a missing VT, missing criterion, omitted boundary, or item to confirm as a gap; a file's existence does not mean coverage.
4. **Cross-check every VT target.** Confirm one by one that the target file and anchor exist, that the ID includes its owner and is consistent, and that the reference points to the correct layer and specific item, not one with the same number or a generic title. Note out-of-scope targets separately; never silently ignore dangling or incorrect references.
5. **Check the source of relationships.** An SR maintains its upstream basis; VTs and validation scenarios maintain their own target AC references. For metadata artifacts, the frontmatter is the source and body criteria are located via `criterionAnchor`. Do reverse lookups by searching these fields; do not hand-maintain two opposite mappings.
6. **Record gaps and checked baselines** in the index below. Do not delete real ACs, fabricate facts, or narrow scope on your own to eliminate gaps; when deferral, withdrawal, or exclusion is genuinely needed, keep its basis and the accountable owner's confirmation.

When execution authorization covers the maintenance tools, use `check_traceability.trace_report(root, delivery_ids)` or the [actual CLI](../.github/utilities/README.md#traceability). `delivery_ids` must come from the complete inventory above, including ACs without a VT; an empty, invalid, duplicate, or unknown selection is an input error and is never narrowed to the known part. The report keeps the owner, source line, target, and byte baseline; its counts are numbers of formal files, not business passes. The VT layer stays in the `plan` table and the TS layer in the scenario type under `basis`; no metadata layer field is added.

<a id="coverage-index"></a>
## Acceptance source index (to be inventoried)

This is a navigation and discrepancy record, not a requirements, mapping, or results database. The acceptance text is authoritative in its owner, and VT target relationships in the VT; VT links here are only the sources found in this check and must be rechecked later.

| Check context | Content |
|---|---|
| Task, delivery scope, and basis for exclusions | TBD |
| Check date and recorder | TBD |
| Object baseline (commit, branch, and uncommitted scope) | TBD |
| REQ/SR, design, or task basis baseline | TBD |
| VT baseline and search scope of this check | TBD |

Register each inventoried acceptance criterion individually; criteria without a VT must also keep a row.

| Original-text link to the owning artifact and full acceptance ID | VT source links found (state if none) | Gaps, reference discrepancies, or items to check |
|---|---|---|
| To be inventoried; no formal entries yet | To be checked | TBD; do not use this to claim complete coverage |

Do not add a copy of the acceptance text or a `pass`/`fail` status table. **Complete traceability, actual execution, and successful execution are three different conclusions**, each needing its own basis.

<a id="execution"></a>
## Run records and applicability

Before running, determine the targets and per-target criteria, and record the planned object baseline, requirement or task baseline, and VT plan baseline. Command-based checks use only confirmed real tools, environments, and working directories; application commands follow the [development guide](../docs/development.md#project-registration) and the actual project, and do not run until configured.

A standalone document check needs no application, but you must still confirm the tool source, actual working directory, checked object, and criteria, and record them per the [document check notes](../docs/development.md#document-checks). For manual checks, write down the actions and observations; do not invent shell commands.

An actual run record contains at least: the time, actual object and uncommitted scope, requirement and VT baselines at the time, environment, working directory, actual command or manual steps, raw report location, and per-target observations and results. When applicable, record the exit code and the discovered/executed/skipped counts. Zero discovered, all skipped, or not run cannot be recorded as the target being verified.

- Every target defaults to `not-run` with the specific reason; `pass` or `fail` is recorded only after an actual run, per the criterion; skipped items are recorded as `skipped` with a reason.
- **Keep actual results separate from current applicability.** A result is bound to the object, requirements, and VT at the time; applicability is recorded separately as `unverified` / `applicable` / `not-applicable` with its basis. `applicable` does not mean success, and `not-applicable` does not erase the historical run.
- A new check appends a new record and baseline; old runs are not overwritten. Re-reviewed applicability keeps its date and rationale; an old success cannot become a current success or a historical failure.
- With no application, application builds and tests do not apply to the current documentation task; already planned business or software behavior VTs remain `not-run` and cannot be replaced by document checks.
- A raw report needs a real, accessible source; mark the access limits of a report available only on the local machine. Do not record personal absolute paths, credentials, or sensitive raw output, and do not claim it is cross-machine evidence.

<a id="implementation-summary"></a>
## Generate a reference summary from existing runs

When collection is authorized, select the exact test object and the actual VT file and owned run anchors through the [implementation report interface](../.github/utilities/README.md#implementation-report). The [fields and limited syntax](../.github/contracts/README.md#implementation-report) reuse the baselines, run information, per-criterion results, and separate applicability columns above, with no separate JSON/YAML execution-input ledger. With several runs, select one explicitly; do not pick the latest or splice fields across runs.

The collector first keeps all owner ACs of the selected BC, then reads records target by target; a target without evidence stays not-run, with empty evidenceRefs and a reason. Each pass/fail requires a matching observation, a readable raw report, and verified object/requirement/VT baselines; zero discovered, all skipped, a test name, Approved, or an available view is not execution. Manual records describe the real steps; do not fabricate automated/manual counts.

This is a **reference summary of source results**: it does not mean the collector reran business tests, and it certifies neither the recorder nor an approval. Actual results and current applicability are still read from the VT and raw reports; the report is a reproducible output the model may reference explicitly, and it does not transfer result ownership to the model, logs, or the coverage index.

<a id="optional-reviews"></a>
## Optional review and tool usage records

Adopt the [review form](../_templates/items/review-record.md) or the [tool qualification and usage form](../_templates/items/tool-qualification.md) only when a standalone record is needed, saved as `verification/REVIEW-NNN-<slug>.md` or `verification/TQ-NNN-<slug>.md`; existing project locations stay unchanged. Use [governance field ownership](../docs/governance.md#ownership) to distinguish criteria, findings, raw execution evidence, and named decisions; for tool scope, version, configuration, and re-evaluation, see the [tooling notes](../docs/ai-tooling.md).

Reviews still follow [verify-change](../.github/skills/verify-change/SKILL.md#domain-review) and are read-only by default; write a record only when current authorization allows saving it. For missing tests, conflicting evidence, or failed criteria, reference the original owner and list follow-ups; do not rewrite VT results, quietly narrow coverage, or claim a pass because a form is complete. Synthetic decisions only demonstrate fields and navigation; a declared confirmation does not certify a person or permission, and agent self-review is not human participation in acceptance.

<a id="change-impact"></a>
## When domain rules, boundaries, or requirements change

1. Record the changed rule, context, or AC IDs, the source, old and new baselines, and confirmation status. First clarify any business intent that affects behavior but is still unclear.
2. Follow the references with a semantic review to check dependent UC, INV, REQ, QAS, SR, ABB/ADR, SEQ/SWAS, scenarios/VTs, companions, and tasks; list affected items and items pending re-review. For boundary or interface changes, also check CAPs, context maps, Published Interfaces, partners, and tactical materials in use. **A referencing file can be affected even if it did not copy the numeric rule**; valid links alone do not prove the semantics are unchanged.
3. Update only the affected behavior boundaries, acceptance scenarios, design constraints, VT expectations, and index gaps. Do not change unaffected rules without reason; a no-impact judgment needs a basis.
4. Keep old results and their original baselines, marking their applicability to current content as `unverified`. Rerun relevant checks against the new baseline and append results; if the object or environment is unavailable, keep `not-run` with the reason.
5. In the [handoff record](../logs/README.md#handoff), state the changes, gaps, items pending re-review, and items not run.

When execution is authorized, `impact_report(root, base_sha, task_ids=())` in the [impact tool](../.github/utilities/README.md#impact-candidates) derives candidates from an explicit full commit and the current files. It traces old and new canonical upstream/targets, keeps chains and actual reasons for deleted or removed references, and does not ignore consumers just because a value appears only in the rule. Lightweight links, implicit business meaning, severity, and applicability of old results are still checked with the method above; the tool does not run checks or modify rules or historical results.
