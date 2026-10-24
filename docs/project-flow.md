# Project flow from zero to one

This page is a derived view of the existing method documents. It is not a formal artifact, does not authorize any step, and records no results. The `SKILL.md` file for each step is authoritative.

<a id="overview"></a>
## Overview

```mermaid
flowchart TD
    Start(["New project or task"]) --> Onboard

    subgraph P0 ["0. Onboard"]
        Onboard["project-onboarding<br/>Confirm registration, record gaps, decide whether business modeling applies"]
    end

    Onboard --> Biz{"Business matters involved?"}
    Biz -- No --> Specify
    Biz -- Yes --> Mine{"Existing documents or code to mine?"}
    Mine -- Yes --> Extract["reverse-engineer-domain<br/>Candidates only, not confirmed facts"]
    Mine -- No --> Define
    Extract --> Define

    subgraph P1 ["1. Model and clarify"]
        Define["define-requirements<br/>Product description, domain model, and REQs, confirmed round by round"]
    end

    Define --> Specify

    subgraph P2 ["2. Specify"]
        Specify["specify-feature<br/>Software requirements, architecture decisions, and pre-implementation verification plan"]
    end

    Specify --> Ready{"Sources sufficient and acceptance plan confirmed?"}
    Ready -- No --> Define
    Ready -- Yes --> Kind{"What is being changed?"}

    Kind -- Documentation only --> Implement
    Kind -- Existing code --> Implement
    Kind -- New application code --> Gate{"Creation inputs complete and creation authorized?"}

    Gate -- No --> Blocked["Record blocked with exact gaps<br/>Behavioral VTs stay not-run"]
    Gate -- Yes --> Generate

    subgraph P3 ["3. Create and maintain"]
        Generate["generate-code<br/>Preflight gate, proposed files, write, verify"]
        Implement["implement-task<br/>Check prerequisites, make the smallest complete change, map to acceptance"]
    end

    Generate --> Verify
    Implement --> Verify

    subgraph P4 ["4. Verify and hand off"]
        Verify["verify-change<br/>Coverage, semantic impact, runs and records"]
        Verify --> Done{"Acceptance and evidence satisfied for this scope?"}
        Done -- No, code or document gap --> Implement
        Done -- No, requirement or plan gap --> Specify
        Done -- Yes --> Handoff
        Blocked --> Handoff["record-handoff<br/>Development log: changes, result entry points, blockers, next steps"]
    end

    Handoff --> End(["Next task or session"])
```

<a id="stages"></a>
## Stages

| Stage | Method | Entry condition | Output | Stop or blocked condition |
| --- | --- | --- | --- | --- |
| 0. Onboard | [project-onboarding](../.github/skills/project-onboarding/SKILL.md) | Goal, scope, and authorization of the task; confirmed project materials | Confirmed registration fields, recorded gaps, applicability of business modeling | Unconfirmed fields stay unconfirmed; no guessed stage |
| 1. Model and clarify | [define-requirements](../.github/skills/define-requirements/SKILL.md) | Business matters apply | [Product description](../stakeholder-requirements/README.md#product), [domain model](../domain-model/README.md), REQs | Respondents or sources missing; open questions remain open |
| 1a. Mine existing material (optional) | [reverse-engineer-domain](../.github/skills/reverse-engineer-domain/SKILL.md) | Existing documents or code the user has authorized | Candidates with their sources | Candidates are never confirmed automatically |
| 2. Specify | [specify-feature](../.github/skills/specify-feature/SKILL.md) | Sources and requirements sufficient | [Software requirements](../software-requirements/README.md), [architecture](../architecture/README.md), [verification plan](../verification/README.md) | Insufficient sources send the work back to stage 1 |
| 3a. Create (gated) | [generate-code](../.github/skills/generate-code/SKILL.md) | Project, stack, location, commands, and creation permission all confirmed ([creation inputs](development.md#creation-inputs)) | Initial files that passed the preflight gate | Any missing input or conflicting non-empty target stops the write |
| 3b. Maintain | [implement-task](../.github/skills/implement-task/SKILL.md) | Task, acceptance criteria, and the actual directory | Smallest complete change, mapped to acceptance criteria | Missing prerequisites mark the task `blocked` |
| 4. Verify | [verify-change](../.github/skills/verify-change/SKILL.md) | Changes made and actual results available | Coverage and impact conclusions, run records kept separate | Unrun checks stay `not-run`; no pass is inferred |
| 5. Hand off | [record-handoff](../.github/skills/record-handoff/SKILL.md) | Any stopping point, including blocked work | [Development log](../_templates/items/development-log.md) and [logs directory](../logs/README.md) | Takeover rechecks the Git state and evidence first |

<a id="gates"></a>
## Gates

- **Creation gate.** Code is created only after the user has chosen the project, stack, and location, authorized creation, and supplied the commands and working directories. Missing inputs make the task `blocked`; documentation work can continue. See [creation inputs](development.md#creation-inputs) and [project registration](development.md#project-registration).
- **Preflight gate.** [generate-code](../.github/skills/generate-code/SKILL.md) checks the directory, Git state, applicable rules, and every write path before writing anything.
- **Evidence gate.** [verify-change](../.github/skills/verify-change/SKILL.md) keeps coverage, impact, and run results separate. A `not-run` item is never recorded as a pass.

<a id="notes"></a>
## Notes

- Documentation-only work skips stage 3a and follows the documentation branch of [implement-task](../.github/skills/implement-task/SKILL.md).
- Business modeling is applicable only when business matters are involved. Technical and documentation maintenance state that it does not apply.
- A new session or a takeover starts from [record-handoff](../.github/skills/record-handoff/SKILL.md#resume), not from chat history.
