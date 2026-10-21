# Verification, coverage, and results entry point

This directory holds verification plans, target references, gaps, and entry points to actual run records; it does not hold test code. When a verification artifact is needed, use the [VT form](../_templates/items/verification-test.md) and save it as `verification/VT-NNN-<slug>.md`. There are no formal acceptance criteria or VTs yet; an empty table does not mean that coverage is complete or that anything has passed.

<a id="layers"></a>
## Distinguish verification layers first

| Layer | What it verifies | Target reference example (all placeholders) |
|---|---|---|
| Business acceptance | Users' business goals, rules, and business-observable outcomes | `REQ-NNN-AC-01`, pointing to the stable anchor in the REQ |
| Software behavior | Specified software behavior, boundaries, errors, and side effects | `SR-NNN-AC-01`, pointing to the stable anchor in the SR |
| Applicable design verification | Sourced structural, collaboration, or design constraints | For example `ABB-NNN-VC-01`, pointing to the constraint owner |
| Standalone maintenance or document check | Explicit completion conditions of the current request or issue | For example `TASK-NNN-AC-01`, pointing to a fixed subsection or record in the actual task source |

A passing software check does not automatically imply that business acceptance has passed. A document check only shows that the structure or content of documents conforms to the conventions within the checked scope; it does not count as executing business or software behavior. One VT can cover several targets in the same layer, and several VTs can cover one target, but every target needs its own standalone criterion; different layers should preferably get separate VTs.

<a id="domain-scenarios"></a>
## Optional domain scenarios and target declarations

The [validation scenario form (TS)](../_templates/items/validation-scenario.md) goes in `verification/TS-NNN-<slug>.md` and can plan within-context, cross-context, REQ business acceptance, or QAS scenarios; it is not application test code. A standalone business criterion can be owned by a UC, REQ, INV, or QAS; the scenario references its specific AC anchor, and rules are still referenced in the original domain text. A scenario without sufficient sources stays a draft/question and does not produce definite behavior.

New TS and [VT forms](../_templates/items/verification-test.md) adopt the [existing metadata contract](../.github/contracts/README.md):

- The frontmatter exclusively holds identity, scope, content state, `upstream`, and `targets`; the body holds the per-target judgment method, plan, actual results, and current applicability. Old VTs are not migrated or renumbered automatically; reading old materials does not require installing the parser.
- Each target gives the full `scope/id#anchor` and the current file's `criterionAnchor`; the optional `testId` takes only a real test identifier. A target is not a generic file title, and `AC-01` alone is not enough.
- Each target has its own criterion block in the body with an explicit anchor. When adding a target, add a block at the same time that states the preconditions, steps/observation points, expected outcome, forbidden side effects, and open conditions. The body may include navigation to source items, but do not hand-maintain another target mapping or an overall pass status.
- Check that the target file, owner, scope, and AC/VC anchor actually match. The parser checks only local criterion anchors; when execution is authorized, you can use the [coverage tool](../.github/utilities/README.md#traceability) to cross-check against the full inventory. It establishes only a structural lower bound for layered/standalone criteria and does not prove semantic sufficiency. When different contexts use the same number, look items up by their full identity.

The following only illustrates one entry in `targets`; adopt it only after replacing all placeholders and creating the actual `criterion-01` anchor in the current body:

```yaml
- target: PROJECT/CTX-NNN/UC-NNN#uc-nnn-ac-01
  criterionAnchor: criterion-01
```

Scenario Markdown holds sources, criteria, and step observation points. When a `.feature` file exists, link to its single Gherkin text and baseline instead of copying it; when there is only a proposed path, mark it in plain text as "proposed, not created", without creating a broken file link or implying that a runner exists. A business scenario without an application/runner stays `not-run`, and a QAS that lacks a measurement criterion cannot be recorded as verified.

For actual runs, choose one record, in either the TS or the VT, as the owner; if the VT holds it, the TS only links to its run block and does not duplicate the result. Record the run result, the specific reason for not running, and the original baseline separately for each target; record current applicability separately, and never record document use or a schema/parser check as business execution.

<a id="feature-companion"></a>
## Gherkin companion and BC verification plan

For the planning activity, see [specify-feature / plan-verification](../.github/skills/specify-feature/SKILL.md#plan-verification). Start from the actual UC/INV/REQ/QAS, SR, or design criteria; there is no need to create a US/ABB first. Once the required inputs are complete, VTs and architecture design can proceed independently.

When behavior suits Gherkin, use the [blank feature](../_templates/items/verification-test.feature), with the same name and directory as its owning VT. Keep the normal, rejection/negative, boundary, and error paths known from sources; do not prefill actors, response metrics, failure policies, or safety-critical tags that have no source. For a non-behavioral QAS or a missing measure, keep only the specification/gap and do not force an executable scenario.

- The `.feature` file is the sole owner of the Given/When/Then scenario text. The Markdown holds target metadata, standalone criteria, file and baseline navigation, preconditions, and evidence, and does not keep a second copy of the Gherkin.
- `targets[].testId` only locates a scenario/native test that actually exists, and `criterionAnchor` corresponds to a standalone criterion in the current Markdown. File/scenario names are textual locators; while no runner is configured, they cannot be treated as executable selectors or used to claim automation.
- Before adding a scenario, check the original acceptance criteria and the full coverage, judging every target individually. When running, record the actual baselines of the `.feature` file, step implementations, object, requirements, and VT together; do not let the companion and the plan drift apart.
- The presence of a file, an Approved tag, or a test file name is neither a pass nor a certification. Without an application, step implementations, a runner, an authorized command/cwd, or a report, behavior verification stays `not-run` and the exact missing items are listed. If you actually performed a text/syntax/mapping check, report only that layer; do not claim that the Gherkin ran successfully.

<a id="coverage-check"></a>
## Start checking from all acceptance criteria

1. **Determine the scope and baselines first.** Read the current task, the in-scope REQs and SRs, the necessary UC/INV/QAS and design, and the standalone maintenance completion conditions; record the scope basis and the version of each artifact. For a maintenance request that has no persistent task source yet, keep the necessary summary and fixed identifiers in the existing task or in the [task basis section of the log](../logs/README.md#task-basis); there is no need to invent a stakeholder requirement.
2. **Inventory acceptance criteria first, then look for VTs.** List the owning artifact, full ID, and original-text link of every in-scope acceptance criterion, including those without a VT yet. Do not derive the requirement list backwards from the list of existing VTs; implementation checkboxes in a US do not replace the original acceptance criteria either.
3. **Find coverage item by item.** Search the target fields of VTs and check whether the layer, the specific target, the per-target expected outcome, the method, and the preconditions are sufficient. Record a missing VT, a missing criterion, an omitted boundary, or an item to be confirmed as a gap; the existence of a file does not mean coverage.
4. **Cross-check every VT target.** Read the existing VTs and confirm one by one that the target file and anchor exist, that the ID includes its owner and is consistent, and that the reference points to the correct layer and specific item rather than to another item with the same number or a generic title. Note out-of-scope targets separately; dangling and incorrect references must not be silently ignored.
5. **Check the source of relationships.** An SR maintains its upstream basis, and VTs/validation scenarios maintain their own target acceptance references; for artifacts that adopt metadata, the frontmatter is the source of relationships, and body criteria are located via `criterionAnchor`. Reverse lookups are done by searching these fields; do not hand-maintain two opposite mappings at both ends of a relationship.
6. **Record gaps and the checked baselines.** Keep source links and discrepancies in the index below. Do not delete real acceptance criteria, fabricate facts, or narrow the scope on your own to eliminate gaps; when deferral, withdrawal, or exclusion is genuinely needed, keep the basis and the accountable owner's confirmation.

When your execution authorization covers the maintenance tools, use `check_traceability.trace_report(root, delivery_ids)` or the [actual CLI](../.github/utilities/README.md#traceability). `delivery_ids` must come from the complete inventory above, including acceptance criteria without a VT; an empty, invalid, duplicate, or unknown selection is an input error and is not narrowed down to the known part. The report keeps the owner, source line, target, and actual byte baseline; counts are numbers of formal files, not numbers of business passes. The VT layer still belongs in the `plan` table, and the TS layer in the scenario type under `basis`; no metadata layer field is added.

<a id="coverage-index"></a>
## Acceptance source index (to be inventoried)

This is a navigation and discrepancy record, not another requirements, mapping, or results database. The acceptance text is authoritative in its owner, and VT target relationships are authoritative in the VT; VT links in the index are only the sources found in this check and must be rechecked later.

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

Do not add a copy of the acceptance text or a `pass`/`fail` status table. **Complete traceability, actual execution, and successful execution are three different conclusions**, each requiring its own basis.

<a id="execution"></a>
## Run records and applicability

Before running, determine the targets and per-target criteria, and record the planned object baseline, the requirement or task baseline, and the VT plan baseline. Command-based checks use only confirmed real tools, environments, and working directories; application commands are based on the [development guide](../docs/development.md#project-registration) and the actual project, and are not run while they are not configured.

A standalone document check does not require an application, but you must still confirm the tool source, actual working directory, checked object, and criteria, and record them according to the [document check notes](../docs/development.md#document-checks). For manual checks, write down the actions and observations; do not invent shell commands.

An actual run record contains at least: the time, the actual object and uncommitted scope, the requirement and VT baselines at the time, the environment, the working directory, the actual command or manual steps, the raw report location, and per-target observations and results. When applicable, record the exit code and the discovered/executed/skipped counts; zero discovered, all skipped, or not run cannot be recorded as the target being verified.

- Every target defaults to `not-run`, with the specific reason it was not run; only after an actual run can `pass` or `fail` be recorded according to the criterion, and skipped items are recorded as `skipped` with a reason.
- **Keep actual results separate from current applicability.** A result is bound to the object, requirements, and VT at the time; current applicability is recorded separately as `unverified` / `applicable` / `not-applicable` together with its basis. `applicable` does not mean success, and `not-applicable` does not erase the historical run.
- A new check appends a new record and a new baseline; it does not overwrite old runs. Re-reviewing applicability also keeps the date and rationale; an old success cannot be turned into a current success or into a historical failure.
- When there is no application, application builds and tests are not applicable to the current documentation task; already planned business or software behavior VTs remain `not-run` and cannot be replaced by document checks.
- A raw report should have a real, accessible source. Clearly mark the access limitations of a report that is available only on the local machine; do not record personal absolute paths, credentials, or sensitive raw output, and do not claim that it is cross-machine evidence.

<a id="implementation-summary"></a>
## Generate a reference summary from existing runs

When collection is authorized, select the exact test object and the actual VT file/owned run anchors through the [implementation report interface](../.github/utilities/README.md#implementation-report); the [fields and limited syntax](../.github/contracts/README.md#implementation-report) reuse the baselines, run information, per-criterion results, and separate applicability columns of the forms above, without a separate JSON/YAML execution-input ledger. When there are several runs, select one explicitly; do not pick the latest or splice together fields from different runs.

The collector first keeps all owner acceptance criteria of the selected BC, then reads the records target by target; a target without evidence remains not-run, with empty evidenceRefs and a reason. Each pass/fail requires a corresponding observation, a readable raw report, and verified object/requirement/VT baselines; zero discovered, all skipped, a test name, Approved, or a view being available does not constitute execution. Manual records describe the real steps; do not fabricate automated/manual counts.

This is a **reference summary of source results**; it does not mean that the collector reran business tests, and it certifies neither the recorder nor an approval. Actual results and current applicability are still read from the VT/raw reports; the report is only a reproducible output that the model may reference explicitly, and it does not transfer ownership of results to the model, logs, or the coverage index.

<a id="optional-reviews"></a>
## Optional review and tool usage records

Adopt the [review form](../_templates/items/review-record.md) or the [tool qualification and usage form](../_templates/items/tool-qualification.md) only when a standalone record is needed; they go in `verification/REVIEW-NNN-<slug>.md` and `verification/TQ-NNN-<slug>.md` respectively, and existing project locations stay unchanged. Use the [governance field ownership](../docs/governance.md#ownership) to distinguish criteria, findings, raw execution evidence, and named decisions; for tool scope/version/configuration and re-evaluation, see the [tooling notes](../docs/ai-tooling.md).

Reviews still use [verify-change](../.github/skills/verify-change/SKILL.md#domain-review) and are read-only by default; write a record only when the current authorization allows saving it. When you find missing tests, conflicting evidence, or failed criteria, reference the original owner and list follow-ups; do not rewrite VT results, quietly narrow coverage, or claim a pass because a form is complete. Synthetic decisions only demonstrate fields/navigation, and a declared confirmation does not certify an actual person or permission; agent self-review is not human participation in acceptance.

<a id="change-impact"></a>
## When domain rules, boundaries, or requirements change

1. Record the changed rule/context/acceptance IDs, the source, the old and new baselines, and the confirmation status. First clarify any business intent that affects behavior but is still unclear.
2. Follow the references, combined with a semantic review, to check the dependent UC, INV, REQ, QAS, SR, ABB/ADR, SEQ/SWAS, scenarios/VTs, companions, and tasks, and list the affected items and the items pending re-review; for boundary/interface changes, also check CAPs, context maps, Published Interfaces, partners, and any tactical materials in use. **A referencing file can be affected even if it did not copy the numeric rule**; valid links alone do not prove that the semantics are unchanged.
3. Update the behavior boundaries, acceptance scenarios, design constraints, VT expectations, and index gaps that are actually affected. Do not change unaffected rules without reason; a judgment of no impact needs a basis.
4. Keep old results and their original baselines, and mark their applicability to the current content as `unverified`. Rerun the relevant checks against the new baseline and append the results; when the object or environment is not available, keep `not-run` with the reason.
5. In the [handoff record](../logs/README.md#handoff), state the changes, gaps, items pending re-review, and items not run. Always keep document consistency re-checks separate from business/software behavior execution.

When execution is authorized, `impact_report(root, base_sha, task_ids=())` in the [impact tool](../.github/utilities/README.md#impact-candidates) can derive candidates from an explicit full commit and the current files. It traces the old and new canonical upstream/targets, keeps the chains and actual reasons for deleted/removed references, and does not ignore consumers just because a value appears only in the rule. Ordinary lightweight links, implicit business meaning, severity, and the applicability of old results are still checked with the method above; the tool does not run checks or modify rules or historical results.
