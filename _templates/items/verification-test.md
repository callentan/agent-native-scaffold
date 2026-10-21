---
schemaVersion: 1
id: VT-NNN
kind: verification-test
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets:
  - target: PROJECT/CTX-NNN/REQ-NNN#req-nnn-ac-01
    criterionAnchor: criterion-01
---
# VT-NNN: TBD

> Blank verification plan and record form; it is not test-run evidence. Read the [verification guide](../../verification/README.md) and the [target declaration conventions](../../verification/README.md#domain-scenarios) first, then copy it to `verification/VT-NNN-<slug>.md` as needed. Confirm and replace `PROJECT/CTX-NNN`, placeholder IDs, targets, and anchors; keep existing records and check the relative links from the actual location, then delete this notice. Inventory every in-scope acceptance criterion before filling in targets; do not judge coverage only from existing VTs.

<a id="plan"></a>
## Plan and layer

| Field | Content |
|---|---|
| Verification layer | To be selected: Business acceptance / Software behavior / Applicable design verification / Standalone maintenance or document check |
| Task basis, scope, and non-goals | TBD |
| Plan date, recorder, and source notes | TBD; content state and confirmation statements belong in the frontmatter |
| Object baseline planned for verification | TBD: object, branch, commit; if there is uncommitted content, describe its scope and a locatable snapshot |
| Requirement/design/task completion-condition baseline | TBD: source file or record and its version; an ID alone is not enough |
| VT plan baseline | TBD: commit or locatable revision range of this plan |

<a id="targets"></a>
## Targets and criteria by item

The frontmatter `targets` list is the only declaration of target relationships; each entry contains a full `scope/id#anchor` and this file's `criterionAnchor`. The body expands each criterion anchor one by one; do not write only `AC-01`, a requirement file title, or a generic "verify everything". When business inputs are used, targets may point at specific UC/REQ/INV/QAS entries, but do not mix up verification layers.

<a id="criterion-01"></a>
### Criterion 01

| Criterion information for this target | Content |
|---|---|
| Reading navigation to the source item | TBD: actual relative link; the frontmatter remains authoritative for the target declaration |
| Expected outcome and independent pass criterion for this target | TBD: how to observe and judge this item |
| Corresponding method/steps or actual test identifier | TBD; if none exists, do not guess |
| Preconditions, forbidden side effects, and open items | TBD |

When you add a target, add a separate criterion block and anchor. Cite the original acceptance text and add only how this method judges that the target is met; do not write a second set of requirements or mappings. Prefer separate VTs for different layers; a document check cannot be recorded as a business or software behavior run.

Relative links in a formal VT take the form below; use them only after replacing them with artifacts that actually exist:

```markdown
[REQ-NNN-AC-01](../stakeholder-requirements/REQ-NNN-<slug>.md#req-nnn-ac-01)
[SR-NNN-AC-01](../software-requirements/SR-NNN-<slug>.md#sr-nnn-ac-01)
```

<a id="method"></a>
## Method and run preconditions

| Method information | Content |
|---|---|
| Method, step order, and target mapping | TBD; for manual checks, describe the specific operations and observations |
| Test identifier/code location (if applicable) | TBD; do not presume that tests exist |
| Existing validation scenario or `.feature` and its baseline (if applicable) | Not provided; if one exists, link its single body text and do not copy Gherkin into this table |
| Inputs, preparation, necessary cleanup, and limitations | TBD |
| Required environment, dependencies, and versions | Not configured; fill in from the real object |
| Corresponding development registration and command source | Not configured; fill in the actual source once configured |
| Planned command and working directory | Not configured; enter only confirmed real commands and a repository-relative cwd |
| Planned report/output location | Not configured; record only locations the actual tool supports |

For non-command checks, state why commands do not apply; do not invent commands. While inputs are incomplete, keep `not-run` and record the specific missing items. When there is no application, application build/test does not apply to documentation tasks; a planned behavior VT does not thereby become passed or get deleted.

<a id="feature"></a>
## Gherkin companion (as needed)

When behavior scenarios apply, copy the [blank feature form](verification-test.feature) to a `.feature` file with the same name in the same directory as this VT, and fill it in following the [companion guide](../../verification/README.md#feature-companion). After deleting this section's notes, keep only the actual file/baseline navigation in the method table; the `.feature` file exclusively owns the Given/When/Then scenario text, and the Markdown does not maintain a second copy of the scenario.

`targets[].testId` may point at a scenario or native test identifier that actually exists; a source file name or scenario name only proves a text location and is not a test the runner can discover. Each target still owns an independent criterion through `criterionAnchor`. Safety/risk tags may come only from named sources already provided; the blank form presets none. Without an application, step implementations, a runner, a command/cwd, or a report, the behavior result is `not-run`; report only the text, syntax, or mapping checks actually performed.

<a id="runs"></a>
## Actual run records

Below is a record block to be filled in; every target defaults to `not-run`, and it is not a run that has happened. After an actual run, fill in the observations made at that time; for a repeat check, append a new block with a new run anchor and keep the old results and their original baselines. Do not copy the planned command here to pretend it has been run.

<a id="vt-nnn-run-01"></a>
### VT-NNN-RUN-01: Pending run

| Actual run information | Content |
|---|---|
| Date, executor, and mode | Not run; TBD |
| Actual object baseline | Not run; when run, record the object, branch, commit, and the actual uncommitted scope/snapshot |
| Requirement/design/task basis baseline at the time | Not run; TBD: source and version |
| VT baseline at the time | Not run; TBD: plan version used for this run |
| Actual environment and tool versions | Not run; fill in from the actual setup once configured |
| Actual working directory | Not run; for command checks, enter the confirmed repository-relative cwd |
| Actual command or manual steps/test identifier | Not run; do not enter a guessed command |
| Exit code and discovered/executed/skipped counts (when applicable) | Not run; do not prefill zero or success |
| Raw report and exact location | Not run, so no report; after the run, enter a real relative link or an authorized report entry point |
| Report accessibility and limitations | TBD; material available only on this machine cannot be claimed as accessible from other machines |

Record the actual result for each item; a zero exit code or an overall summary cannot replace the judgment for each target.

| Criterion link (target located by frontmatter) | Actual observation and raw report location | Actual result | Not-run/skip reason or failure difference |
|---|---|---|---|
| [Criterion 01](#criterion-01) | Not run | not-run | Not run yet; the specific reason is TBD |

The result can be `not-run`, `pass`, `fail`, or `skipped` and must have a matching observation; zero discovered tests or all tests skipped cannot be reported as the target being verified. Do not maintain this result table again in logs or the coverage index.

<a id="applicability"></a>
## Current applicability review (separate from actual results)

Append a row each time applicability is reviewed and keep historical conclusions; the latest review row for the same run and target states its applicability to the current baseline. After a baseline or rule changes, first record `unverified`; do not simply carry over an old success, and do not change a historical success into a failure.

| Review date and recorder | Original run/result and target link | Current object, requirement, and VT baselines | Applicability | Rationale, impact, and items to recheck |
|---|---|---|---|---|
| TBD | TBD | TBD | unverified | Not run yet; no reusable result |

Applicability is `unverified`, `applicable`, or `not-applicable` and needs a stated basis; it does not replace the actual run status. After an affected check is rerun, append a new record with the new baseline and raw report; do not overwrite the original record.

<a id="gaps"></a>
## Gaps and next steps

- Uncovered targets, wrong references, or missing preconditions: TBD.
- Unconfirmed facts, blockers, and who must provide what: TBD.
- Specific checks pending re-review or not run, and next steps: TBD.

Do not close gaps by deleting real acceptance criteria, fabricating targets, or lowering criteria. While business/software behavior has not been run, keep its not-run status even if the document consistency check is complete.
