---
name: record-handoff
description: Use when pausing or finishing a task, handing work to another session, or resuming from incomplete logs and uncertain evidence.
---

# Record handoffs and resume tasks

Make it possible for whoever takes over to determine the current state and the next step without relying on old chats. The log only summarizes changes and links authoritative records; it does not maintain another copy of acceptance results.

## Inputs

- The current task, date, session identifier, scope, and authorization; confirmed judgments and their sources.
- The actual Git branch, commit, and staged and uncommitted scope; the models, REQs, SRs, VTs, and tasks changed or affected in this session.
- Entry points to the actual check records and the object/requirement/VT baselines; exact gaps, items pending re-review, work not run, and blockers.

## Recording order

1. Read the [log guide](../../../logs/README.md#recording), and use the [log form](../../../_templates/items/development-log.md#session) to fill in "Session, task, and Git state". Recheck Git instead of prefilling it as clean; distinguish the starting baseline, the current commit, the committed scope, pre-existing versus new uncommitted scope, and the staging state. Link existing tasks directly; fill in the form's optional task-basis section only for maintenance requests that truly have no persistent source.
2. Under "Changes in this session", list the actual paths/artifact IDs, the related rules/requirements/VTs/tasks, and the basis for each change, and describe any state that is unfinished or could not be preserved. Cite long-term decisions from their formal sources; a progress log does not replace requirement or design text.
3. Under [Actual result entry points](../../../_templates/items/development-log.md#verification), link, by category, the VT runs, reports, or standalone document-check records that actually exist, with their baselines and access limitations. When an [implementation report](../../utilities/README.md#implementation-report) exists, follow its per-target references back to the original VTs/reports and check each one's object, requirement, and plan baselines; collecting them does not mean re-running them or that they currently apply. Without evidence, write only "not run" or "inaccessible"; do not treat an old summary as a new result, and do not copy result status tables.
4. In the [gaps and impact section](../../../_templates/items/development-log.md#follow-up), write the full IDs of uncovered/dangling acceptance criteria, the affected artifacts, entry points for current applicability pending re-review, and `not-run` actions with their reasons; check the sources with [verify-change](../verify-change/SKILL.md). Keep old results and their original baselines.
5. Under "Blockers and next steps", write who must supply what, the inputs and authorization prerequisites for the next step, and the Git/evidence/external state that whoever takes over must recheck. Save only necessary facts and links; do not store full chats, credentials, personal absolute paths, or sensitive output. Note the limitations of reports that exist only on this machine, and do not call them cross-machine evidence. When applicable, follow the [minimal tool record](../../../docs/ai-tooling.md#minimal-record) to link the tool/version/purpose, object, evaluation, and [actual decision](../../../docs/governance.md#decisions); do not fabricate approvals or results in the log. When the version/configuration/purpose changes, keep the old baseline and note that re-evaluation is needed.

<a id="resume"></a>
## Takeover order

1. Enter from the [README](../../../README.md#resume) and [AGENTS](../../../AGENTS.md), then read the current task, the [domain facts](../../../domain-model/README.md), the related [REQ](../../../stakeholder-requirements/README.md)/[SR](../../../software-requirements/README.md), the [coverage index](../../../verification/README.md#coverage-index), the actual VTs, and the [most recent related logs](../../../logs/README.md#handoff). Indexes and summaries cannot replace the target's source text.
2. Recheck whether the actual directory and the Git branch/commit/dirty scope match the record; follow the result entry points to check the object, requirement, and VT baselines and whether the evidence is accessible. Record inaccessible reports explicitly; an old "pass" cannot be inherited as a current pass, and a log cannot restore unsaved edits or the original process.
3. Check for changes in rules, scope, or authorization, and use [verify-change](../verify-change/SKILL.md) to check semantic impact, omissions, items pending re-review, and `not-run` work. Keep still-unknown facts unknown. First choose a next step that is **not yet done and has complete inputs**, then read the method for that activity; when development inputs are insufficient, independent documentation work may continue.
4. For external operations that may or may not have completed, first verify their readable state or ask for confirmation; do not retry blindly. Without authorization, do not push or create PRs, and do not derive new side-effect permissions from old logs. Write the findings, limitations, and next steps of this resumption into an authorized handoff record.

## Outputs and completion

Formal handoffs go into `logs/YYYY-MM-DD-<task>-<session>.md`, using the fields of the existing form; tasks, acceptance criteria, and runs are still maintained in their own source files. When resuming, update only authorized records; the actual implementation is the responsibility of the corresponding activity method.

The handoff is complete when whoever takes over can locate, from the record, the task, the current baseline, the actual results or their absence, the affected items, and a next step whose inputs are complete. This does not mean that all work is done, that historical evidence has been restored, or that behavioral acceptance has passed.

## Stop conditions

When a required task or evidence is unreadable, the Git scope conflicts, sources contradict each other, or a change in authorization is unclear, stop the operations that depend on it, state the limitation, and give the minimal additional input needed. Never get past a blocker by relying on old chats, replaying uncertain external actions, or fabricating results.
