# Development workflow, logging, and handoff conventions

**This file defines the working conventions of the repo template; it is not a protocol for a home-grown executor. The corresponding P1 forms and P2 shared methods have been produced; for the limited exercise results of 2026-10-14 and the unfinished items, see the [actual acceptance record](../plan/roadmap.md#actual-acceptance).**

## 1. Choose the process each task needs

The usual order is "domain and business requirements → necessary software requirements and delivery slices → implementation → verification → recording and delivery". Directories use the reference projects' naming, but not every change has to create a whole new REQ/SR/US/ABB/VT chain, and there is no requirement to call a series of different agents first.

DDD provides the business model and boundaries, and the V-model maps requirements at different levels to their verification; forms define artifact structure, skills define the shared methods, and prompts start the current activity. A lightweight process can reuse existing artifacts but must not lose the current task's business basis, acceptance source, or unverified status.

| Activity | Input | Output and exit condition |
|---|---|---|
| Project start | Goals and constraints provided by the user, and the current repository state | Shared terms, concept relationships, rules, and context boundaries filled in per the blueprint; stakeholder requirements, open items, and a development environment guide |
| Feature planning | Related model and business requirements, existing code and architecture | SR, testable acceptance criteria, and the corresponding verification plan; US and design artifacts arranged as needed, with gaps listed explicitly |
| Development or fix | Confirmed task, related specifications, actual workspace | Code and test changes, without bundling unrelated rework |
| Verification and review | List of acceptance criteria for the current delivery, the current changes, the verification plan, and applicable commands | Coverage and reference checks, actual results, baseline applicability, explanations of what was not run, and questions awaiting review |
| Handoff or delivery | Current Git status, task, and verification results | Development log and delivery summary; a PR awaiting review when needed |

One general-purpose agent can carry all of these activities. Planner, implementer, and reviewer are only selectable working modes; they do not imply automatic dispatching or an independent approver identity.

Humans read the same skill, forms, and project materials from the README activity navigation, and agents enter the same method from AGENTS; inputs, outputs, and completion and stop conditions are the same, with no separate human-only facts or rules. Manual work does not require running an agent, a dedicated prompt command, or a model service.

The skeleton initially contains no business project. Browsing, setting up project materials, planning, and documentation maintenance can proceed independently; coding steps begin only when the user decides to create or modify a concrete project. The coding conventions below are for downstream use and do not require the first-release skeleton to ship an application exercise.

## 2. What to know before starting

An agent first reads `AGENTS.md`, then locates the current US or issue, the related domain facts and REQ/SR, the development guide, and the most recent related logs. Read only the materials relevant to the task; do not inject the whole research directory into the context by default.

A task must state at least its goal, scope, existing basis, and completion conditions. When delivering a feature, maintain the implementation checklist in the US file under `user-stories/`; standalone maintenance or defect tasks can keep using an issue/PR, without forcing a user story and without setting up a separate task directory with the same content. A task record should include:

| Content | Notes |
|---|---|
| Goals and non-goals | What this task will accomplish, and which work is out of scope |
| Input links | Related REQ/SR/US, defects, or discussion records |
| Change scope | Related directories or modules, and what must not be modified |
| Acceptance criteria | Observable behavior and the checks that must be run |
| Status and owner | Progress readable by humans and agents; not used as a concurrency lock |
| Record links | Verification results, development log, and any necessary PR or review records |

Minor fixes can express this content in the user request or PR description, without creating a duplicate task document. When business facts that affect behavior are missing, ask specific questions first; do not fill in an empty template field and mark it "confirmed" just because the field exists.

Before writing, check the branch, the working directory, and existing changes. On a conflict with someone else's changes, keep both sides' content and stop the affected operation; do not overwrite an existing project by reinitializing the template.

Before coding, also confirm the target project location within `src/`, the tech stack, the existing layout, and the real development workflow, and register the relative path, commands, and working directory per subproject in `docs/development.md`. If the user has not chosen yet, record the missing items and do not run a project generator on your own; an unselected tech stack does not block pure documentation tasks.

## 3. Artifact responsibilities and content ownership

The PRD's product goals and scope go in the entry point and the business requirements of `stakeholder-requirements/`; domain concepts, rules, and contexts go in `domain-model/`, with the minimum filling requirements in [blueprint section 3.1](repository-blueprint.md). Business acceptance belongs to REQ, software behavior and software acceptance to SR, delivery scope and implementation progress to US, necessary design to `architecture/`, and verification methods and result references to `verification/`. Do not simply treat a whole PRD as a single REQ, and do not cram all spec content into SR.

US references requirements through links and does not copy software requirements that would then change independently; VT directly references the REQ/SR acceptance criteria it verifies and, when needed, links design constraints or the completion conditions of a standalone maintenance task. US is not a mandatory layer between requirements and VT. `verification/` stores verification documents and is not a test code directory; the skeleton does not pre-create `src/tests/`, and actual project and test paths follow the downstream tech stack or the existing project.

Small changes reuse existing artifacts; new business decisions are first recorded as proposals. When architecture decision history is needed, write an ADR in `architecture/decisions/`; ordinary progress goes in the log, and not every change has to produce an ADR. Take document forms from `_templates/items/` and, once filled in, place them in the corresponding artifact directory.

Filling hints and examples in template files are not business facts. Nor are the reference projects an implicit source of requirements for the current task.

### 3.1 Minimum traceability and coverage check

| Requirement or design | Corresponding verification question | Minimum linkage |
|---|---|---|
| Stakeholder requirement (REQ) | Does it satisfy the users' business goals and rules? | REQ references the related model rules/contexts; business acceptance criteria link to business-acceptance VTs |
| Software requirement (SR) | Do software behavior, boundaries, and error handling meet the specification? | SR references its upstream REQ or explicit task basis; software acceptance criteria link to behavior-verification VTs |
| Necessary design (ABB) or design constraint | Do the boundaries, collaborations, and constraints that the design is responsible for hold? | The design references requirements and business boundaries; constraints that need verification link to appropriate integration, component, or design checks, without mandating an extra layer |

A VT states its verification layer, target acceptance criteria, method, and expected results. One acceptance criterion can be covered by several VTs, and one VT can cover several acceptance criteria, but each target and its pass criterion must be listed item by item; passing software checks does not automatically imply that business acceptance passes. Decide the applicable verification method during planning, rather than working backwards to requirements after the code is done.

SR stores its upstream relationships and VT stores its target relationships; each reference uses the owning artifact, a stable acceptance identifier, and a locatable link, never a bare `AC-1` of unknown ownership. Reverse lookups are done through references and search, without manually copying relationships in both directions. Update references when an artifact is renamed; when an acceptance criterion is withdrawn, keep the basis for the change and do not reuse the old identifier to hide history.

A coverage check first lists all acceptance criteria in the current delivery scope and then looks for the corresponding VTs; do not merely scan the existing VTs to infer that "all requirements are covered". Check each item for a missing verification method, a VT pointing to a nonexistent or wrong acceptance criterion, stale references, and result baseline mismatches. Record gaps, impact, and pending items explicitly; deferral or not applicable needs a rationale and confirmation by the accountable owner, and an agent must not eliminate gaps by narrowing the scope or fabricating requirements.

`verification/README.md` provides a coverage index searchable by acceptance criterion, including gaps and the checked baseline; relationships and results are still read from their sources. Complete mapping, actual execution, and passing execution are different facts; without a run result keep `not-run`, and do not substitute "a VT exists" for verification. A maintenance task with no current stakeholder requirement can directly reference the recorded user request or the issue's completion conditions, without forcing a new REQ, SR, or US.

### 3.2 Change impact and old results

1. Record the changed model rules, context responsibilities, requirements, or acceptance criteria, keeping the original baseline, the new content, and the basis for the change; clarify unknown business intent first.
2. Follow the actual references, together with the content, to check the affected REQs, SRs, designs, VTs, and tasks. List the items that need updating or re-review; when you judge there is no impact, state the basis, and do not conclude that the meaning is unchanged just because the links still resolve.
3. Update the descriptions, acceptance criteria, VT expectations, and coverage index that need changes, keeping gaps and items to be confirmed. Old results stay on their original baseline, and their applicability to the current change is marked `unverified` (pending re-review); do not rewrite a historical success as a failure, and do not automatically carry it over as a current success.
4. Rerun the applicable checks on the affected content and record the new baseline. A passing document-consistency check proves only that the documentation conventions are consistent; when the application or environment needed for behavior verification is unavailable, keep the verification not run, and do not substitute document checks for it. The handoff record must point out the items not yet re-reviewed and the items not run.

## 4. Implementation and verification

Use the project's native build, run, and test tools. Skills explain when and why to perform these steps; actual commands and working directories are based on `docs/development.md` and the real project configuration, not on calling a home-grown `ans run`.

Feature changes must cover the corresponding acceptance criteria; defect fixes first reproduce the original symptom and then verify the fix. Documentation changes use checks suited to the content; do not run unrelated business tests just to make the process look complete.

The first-release skeleton is accepted only on its files, entry points, documentation workflow, and handoff, and does not choose a sample tech stack. When there is no application, record the application build and tests as not applicable and give the reason; when a project exists but the checks cannot run, record `not-run`; neither may be written up as a passed application verification.

A verification record states at least:

| Item | Requirement |
|---|---|
| Verification object | Branch, commit, or the actual scope of uncommitted changes; old results must not be applied to new code |
| Acceptance basis | Acceptance criteria of the corresponding REQ/SR, design constraint, or standalone maintenance task, and the applicable VTs; identically numbered criteria must include their owning file |
| Run method | Actual command, working directory, and necessary environment information |
| Actual result | Success, failure, skipped, or not run; when applicable, record the exit code and test counts |
| Raw evidence | Location of the test report, CI run, or necessary output; do not leave only a line saying "tests passed" |
| Result applicability | The requirement, VT, and workspace baselines the result corresponds to; whether it is pending re-review after a change, recorded separately from historical run results |
| Remaining issues | Uncovered behavior, external dependencies, baseline failures, and reasons for blockers |

Having test files, a command exiting with zero, and passing acceptance are different facts. When zero required tests are discovered, all are skipped, or they were not run, do not write "verified". After code, tests, or acceptance criteria change, rerun the affected checks; do not delete tests or lower the standard to make a task appear complete.

A log is a summary of results, not tamper-proof evidence. CI, project tests, and human review provide the actual basis; this template does not build a separate "trusted verifier" product.

## 5. Development logs and handoff

A separate file per task or work session is recommended, for example `logs/2026-10-13-US-001-session-a.md`; maintenance tasks can use their issue or PR identifier. This avoids all agents editing one global log at the same time. The US or issue links the related logs, progress is tracked from the corresponding task record, and logs keep the observations made at the time. `logs/` is our own additional directory and does not claim to reuse a same-named log path from the reference repositories.

Minimum log structure:

- Related task, date, and session identifier; record the agent used when needed.
- Working branch, baseline version, and where committed and uncommitted changes are.
- Changes completed in this session, and the basis for important judgments.
- Checks actually run, their results, and links to raw reports.
- Current blockers, traceability gaps, affected artifacts, items pending re-review or not run, next steps, and the conditions that need rechecking.

Do not store full chats, hidden reasoning, access tokens, production data, or large chunks of machine output. Raw reports that must be kept use the project's existing output locations or authorized CI artifacts; local temporary files must not be described as handoff material that other machines can access directly.

Update the log at important milestones, pauses, and deliveries; an entry is not required for every file change. User-facing change notes that are maintained over time can go in a separate changelog, kept apart from the running development log.

## 6. Continuing in another session or agent

1. Read the common entry point, the current task, the related model and REQ/SR/VT, the coverage index, and the latest log; the task does not have to be a US.
2. Check whether the Git status, artifact references, known gaps, result baselines, and the log are consistent, and distinguish completed mapping, document checks, and software behavior verification.
3. Confirm whether open questions have been resolved, and whether the user has changed the goal or the authorized scope.
4. State explicitly which patches, reports, or materials cannot be accessed; do not pretend they have been recovered.
5. Continue from a step that is not yet complete and whose inputs are available, and re-verify as needed.

Logs provide takeover clues; they do not guarantee restoring the previous process, tool session, unsaved edits, or external system state. If a "PR created" entry in the log cannot be confirmed, query the existing platform before acting, to avoid a duplicate submission.

Parallel work by several people relies on branches, worktrees, and normal Git collaboration; this template provides no task claiming, leases, or cross-machine state synchronization.

## 7. Completion, review, and permissions

Tasks can use simple statuses such as `todo`, `in-progress`, `blocked`, `review-ready`, and `done`, but these are work records, not a program-enforced state machine. `done` means only that the agreed delivery for this task is complete; it does not automatically mean merged or released.

On completion, give a change summary, the verification results, the remaining limitations, and the log location. Whether to push or create a PR is decided by user authorization and the existing client capabilities; it is not a side effect of copying the template or reading a prompt.

An agent writing `Approved` in a file, selecting the reviewer mode, or reviewing its own work cannot replace the decision of an authorized person. When a formal merge gate is needed, maintainers configure reviews, required checks, and permissions on the hosting platform. Statements in the template do not enable these settings automatically.

Likewise, tool scope, isolation, budgets, and cancellation are controlled by the client and the host environment. This template does not guarantee that Markdown rules can prevent every unauthorized action, and it does not build its own credential storage or release service.

## 8. When to stop

When business facts contradict each other, required materials are unreadable, verification fails, authorization is insufficient, existing changes conflict, or the outcome of an external operation is unclear, report the specific problem and preserve the work. Retry only operations that have a clear reason to be retried; do not loop indefinitely, and do not silently lower the requirements.

Without a test environment you may deliver unverified changes for discussion, but they must be marked `not-run` or blocked; do not describe "the files are written" as verified behavior. An empty template with no tech stack chosen also cannot report a successful application build.
