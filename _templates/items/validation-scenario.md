---
schemaVersion: 1
id: TS-NNN
kind: validation-scenario
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets:
  - target: PROJECT/CTX-NNN/UC-NNN#uc-nnn-ac-01
    criterionAnchor: criterion-01
---
# TS-NNN: TBD business validation scenario

> Optional scenario plan; not run yet. Read the [domain scenario guide](../../verification/README.md#domain-scenarios) and the [metadata conventions](../../domain-model/README.md#artifact-metadata) first. Copy it to `verification/TS-NNN-<slug>.md` as needed; confirm and replace `PROJECT/CTX-NNN`, the ID, targets, and anchors, check the target owners, the actual location, and the relative links, keep existing records, and then delete this notice. Copying the blank form or parsing it successfully does not mean the business passed.

<a id="basis"></a>
## Basis and plan baseline

| Plan information | Content |
|---|---|
| Business scope and scenario type | TBD: Within context / Cross-context / REQ business acceptance / QAS; do not confuse it with a software run |
| Known facts and locatable sources, dates, or versions | TBD |
| Derived candidates and source limitations | TBD; unconfirmed policies do not enter definite expectations |
| Object, requirement, and scenario plan baselines | TBD; locate each separately, not just the current HEAD |
| Plan recorder and required confirmation basis | TBD |

Declare parseable bases such as UC, RULE, INV, REQ, and QAS in `upstream`; declare the specific UC/REQ/INV/QAS entries being verified in `targets`. A single generic file title cannot stand in for multiple targets.

<a id="targets"></a>
## Criteria by target

Each `targets` entry uses `criterionAnchor` to point at an independent criterion block in this file. When you add a target, add a criterion block; different targets cannot share one "all passed" sentence. The source entry's text still belongs to its original owner.

<a id="criterion-01"></a>
### Criterion 01

- Preconditions and inputs for this target: TBD.
- Actions, observations, and independent pass criterion for this target: TBD.
- Corresponding steps or actual test identifier: TBD; if none exists, say so; do not guess the runner.
- Source navigation, open conditions, and forbidden side effects: TBD.

<a id="scenario"></a>
## Scenario preparation and steps

| Scenario information | Content |
|---|---|
| Participants, facts used, and their owners | TBD |
| Initial state, input preparation, and cleanup constraints | TBD |
| Step order and observation points for each criterion | TBD |
| Coverage and gaps for normal, boundary, and rejection cases | TBD |
| `.feature` reference and its baseline (when applicable) | Not provided yet; a proposed path may be recorded but not written as a link to an existing file |
| Source of the actual environment, runner, command, and cwd | Not configured; fill in only from the real development registration |
| Raw output location and access limitations | Not configured |

When a `.feature` file exists, only reference its single Gherkin body; do not copy that body into this file. Without an application or runner, the scenario remains a plan; when a QAS lacks a measurement criterion, keep the gap and do not produce a fictitious pass criterion.

<a id="runs"></a>
## Actual runs (separate from the plan)

This block is a pending-run record, not a run that has happened. If a VT holds the actual result, only link its run block here; do not copy the result again. For repeat runs, append records and keep the old baselines.

<a id="ts-nnn-run-01"></a>
### TS-NNN-RUN-01: Pending run

| Actual run information | Content |
|---|---|
| Date, executor, and actual object baseline | Not run |
| Requirement and scenario plan baselines at the time | Not run; pin the actual versions when run |
| Actual environment, cwd, command, or manual operations | Not run |
| Discovered/executed/skipped counts and exit code (if applicable) | Not run; do not prefill zero |
| Raw report or the single VT run record | None; not run yet |

| Local criterion (target located by frontmatter) | Actual observation | Actual result | Not-run/skip reason or failure difference |
|---|---|---|---|
| [Criterion 01](#criterion-01) | Not run | not-run | No confirmed run object, method, or environment yet |

<a id="applicability"></a>
## Current applicability

| Review date | Original run/criterion navigation and original baseline | Current requirement and object baselines | Applicability and basis |
|---|---|---|---|
| TBD | No run record yet | TBD | unverified; no reusable result |

Applicability is independent of the result; after a rule change, keep the original record and do not turn a historical `pass` into a pass against the new baseline.

<a id="questions"></a>
## Open items and next steps

- Uncovered targets and missing preconditions or criteria: TBD.
- Rules, measures, objects, or run authorization needed and who must provide them; link a BL when necessary: TBD.
- Business runs that the completed document checks cannot replace: TBD; keep them `not-run` with the specific reason.
