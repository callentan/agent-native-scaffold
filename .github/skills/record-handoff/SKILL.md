---
name: record-handoff
description: Use when pausing or finishing a task, handing work to another session, or resuming from incomplete logs and uncertain evidence. Not for carrying out the resumed work itself (use the method for that activity, such as implement-task).
---

# Record a handoff and resume a task

Leave a record that lets whoever takes over determine the current state and the next step without relying on old chats. The log only summarizes changes and links to authoritative records; it does not keep another copy of acceptance results.

## Inputs

- Required:
  - The current task, date, session identifier, scope, and authorization.
  - Confirmed judgments and their sources.
  - The actual Git branch, commit, and staged and uncommitted scope.
  - The models, REQs, SRs, VTs, and tasks changed or affected in this session.
  - Entry points to the actual check records, and the object/requirement/VT baselines.
  - Exact gaps, items pending re-review, work not run, and blockers.

## Steps

1. Choose the activity:
   - Pausing, finishing, or handing off a task: follow Record a handoff.
   - Taking over or resuming a task: follow Take over or resume.
2. Perform that section's actions in order.

## Record a handoff

Fill in the log form section by section, so that whoever takes over can continue without old chats.

1. Read the [log guide](../../../logs/README.md#recording).
2. In the [log form](../../../_templates/items/development-log.md#session), fill in "Session, task, and Git state".
   - Recheck Git now; do not prefill it as clean.
   - Distinguish the starting baseline, the current commit, the committed scope, pre-existing versus new uncommitted scope, and the staging state.
   - Link existing tasks directly. Fill in the form's optional task-basis section only for a maintenance request that truly has no persistent source.
3. Under "Changes in this session":
   - List the actual paths/artifact IDs, the related rules/requirements/VTs/tasks, and the basis for each change.
   - Describe any state that is unfinished or could not be preserved.
   - Cite long-term decisions from their formal sources. A progress log does not replace requirement or design text.
4. Under [Actual result entry points](../../../_templates/items/development-log.md#verification):
   - Link, by category, the VT runs, reports, or standalone document-check records that actually exist, with their baselines and access limitations.
   - When an [implementation report](../../utilities/README.md#implementation-report) exists, follow its per-target references back to the original VTs/reports. Check each one's object, requirement, and plan baselines. Collecting them does not mean re-running them or that they currently apply.
   - Without evidence, write only "not run" or "inaccessible".
   - Do not treat an old summary as a new result. Do not copy result status tables.
5. In the [gaps and impact section](../../../_templates/items/development-log.md#follow-up):
   - Write the full IDs of uncovered or dangling acceptance criteria, the affected artifacts, entry points for current applicability pending re-review, and `not-run` actions with their reasons.
   - Check the sources with [verify-change](../verify-change/SKILL.md).
   - Keep old results and their original baselines.
6. Under "Blockers and next steps":
   - Write who must supply what, the inputs and authorization prerequisites for the next step, and the Git/evidence/external state that whoever takes over must recheck.
   - Note the limitations of reports that exist only on this machine. Do not call them cross-machine evidence.
   - When applicable, follow the [minimal tool record](../../../docs/ai-tooling.md#minimal-record) to link the tool/version/purpose, object, evaluation, and [actual decision](../../../docs/governance.md#decisions). When the version, configuration, or purpose changes, keep the old baseline and note that re-evaluation is needed.

Record: the handoff in `logs/YYYY-MM-DD-<task>-<session>.md`.

<a id="resume"></a>
## Take over or resume

Rebuild the current state from the source records before continuing. Work through this checklist in order:

1. Enter from the [README](../../../README.md#resume) and [AGENTS](../../../AGENTS.md).
2. Read the current task, the [domain facts](../../../domain-model/README.md), the related [REQ](../../../stakeholder-requirements/README.md)/[SR](../../../software-requirements/README.md), the [coverage index](../../../verification/README.md#coverage-index), the actual VTs, and the [most recent related logs](../../../logs/README.md#handoff). Indexes and summaries cannot replace the target's source text.
3. Recheck whether the actual directory and the Git branch/commit/dirty scope match the record.
4. Follow the result entry points. Check the object, requirement, and VT baselines and whether the evidence is accessible.
   - Record inaccessible reports explicitly.
   - Never inherit an old "pass" as a current pass.
   - A log cannot restore unsaved edits or the original process.
5. Check for changes in rules, scope, or authorization. Use [verify-change](../verify-change/SKILL.md) to check semantic impact, omissions, items pending re-review, and `not-run` work. Keep still-unknown facts unknown.
6. Choose a next step that is **not yet done and has complete inputs**, then read the method for that activity. When development inputs are insufficient, independent documentation work may continue.
7. For an external operation that may or may not have completed, first verify its readable state or ask for confirmation. Do not retry it blindly.
   - Without authorization, do not push or create PRs.
   - Do not derive new side-effect permissions from old logs.
8. Write the findings, limitations, and next steps of this resumption into an authorized handoff record.

Record: the authorized handoff record from action 8.

## Guardrails

- Save only necessary facts and links. Do not store full chats, credentials, personal absolute paths, or sensitive output.
- Do not fabricate approvals or results in the log.

## Outputs

- Formal handoff → `logs/YYYY-MM-DD-<task>-<session>.md`, using the fields of the existing form.
- Tasks, acceptance criteria, and runs → stay in their own source files.
- When resuming: update only authorized records. Implementation itself belongs to the corresponding activity method.

## Done when

Whoever takes over can locate, from the record:

- the task;
- the current baseline;
- the actual results, or their absence;
- the affected items;
- a next step whose inputs are complete.

This does not mean that all work is done, that historical evidence has been restored, or that behavioral acceptance has passed.

## Stop conditions

- When a required task or its evidence is unreadable, the Git scope conflicts, sources contradict each other, or a change in authorization is unclear, stop the operations that depend on that item.
- Then: state the limitation and give the minimal additional input needed.
- Never get past a blocker by relying on old chats, replaying uncertain external actions, or fabricating results.
