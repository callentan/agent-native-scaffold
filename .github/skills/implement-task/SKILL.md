---
name: implement-task
description: Use when an identified task is ready for scoped edits, or an implementation request may lack project or development inputs.
---

# Implement the current task

Start from the actual directory, the task basis, and the acceptance criteria. Documentation maintenance and coding have different prerequisites; never generate a project on your own initiative just to carry out a request.

## Inputs

- Goal, scope, non-goals, completion conditions, and the source of authorization; the current task or an existing [US](../../../user-stories/README.md) (if any).
- The actual working tree and Git status; the affected model, REQs, SRs, VTs, and necessary design.
- For coding, also the project, tech stack, location, and environment selected by the user, and a verified [development registration](../../../docs/development.md#project-registration).

## Steps

1. Check the current directory, branch, commit, index, pre-existing uncommitted changes, and the actual file tree; read the task source and its completion conditions. When editing Markdown, read the [documentation rules](../../instructions/docs.instructions.md); when editing any test, explicitly read the [test rules](../../instructions/tests.instructions.md). When editing code, also read the [architecture](../../instructions/architecture.instructions.md), [coding](../../instructions/coding.instructions.md), and [security rules](../../instructions/security.instructions.md) in full, even if the actual paths do not match their globs; do not rely on automatic loading alone.
2. Before writing, read the affected domain rules/contexts, REQs, SRs, and VTs, and confirm the applicable acceptance criteria and the pre-implementation verification plan with [specify-feature](../specify-feature/SKILL.md). If the task changes the model or requirements, first handle sources, downstream items, expectations, and baselines with the [verify-change semantic impact check](../verify-change/SKILL.md#impact); do not mechanically implement the old task.
3. Choose a path:
   - **Documentation-only maintenance:** with an explicit path, basis, and completion conditions, continue according to the [document check guide](../../../docs/development.md#document-checks); do not wait for a tech stack, and do not create new business artifacts.
   - **Initial code generation:** use [generate-code](../generate-code/SKILL.md); this method does not rerun an initializer over existing code. When the [project creation prerequisites](../../../docs/development.md#creation-inputs) are incomplete, do not initialize anything or install dependencies.
   - **Existing code maintenance:** verify the user-selected project/stack/location/environment, the actual source/test layout, and the registered commands/cwd/reports. When a BC configuration is adopted, check the actual source root, relative paths, pinned baseline, and read-only nature, and never write back to sources. If anything is missing, mark the affected task `blocked` and the related checks `not-run`, and state who must supply what; never unblock with a new project, a default stack, or fake commands.
4. Once the inputs are complete, code maintenance reads the relevant implementation, calls/boundaries, native tests, and existing diff in the directory the task specifies, and establishes a repeatable check or an actual reproduction; documentation maintenance checks only the specified materials, basis, and applicable document checks, and does not require an application layout. Record the exact files to change and the acceptance criteria they map to, then make the smallest complete change. In code, locate full owner-qualified acceptance IDs through the project's existing comments/test identifiers or the task record; do not create a dedicated traceability framework. Keep owner content, unrelated changes, and the native layout. On a conflict, a write to an unexpected path, or a failed check, stop the affected action and locate the cause; do not switch to initializer overwrites or narrow the acceptance criteria.
5. Run the applicable checks with [verify-change](../verify-change/SKILL.md) and keep the actual evidence, distinguishing documentation results, behavioral VTs, old results, and current applicability. Recheck the diff against the task scope, and update an existing task checklist only to reflect what was actually completed; a ticked checklist item is not an acceptance result.
6. Following [record-handoff](../record-handoff/SKILL.md), use the [log form](../../../_templates/items/development-log.md#follow-up) to leave the changes, result entry points, exact gaps, blockers, and next steps. Commits, pushes, PRs, and other external side effects are handled separately under actual authorization; this method grants no permissions.

## Outputs and completion

Changes go into the explicitly specified documents or actual project paths, and tests stay in the project's native locations. Verification relies on existing VTs and actual reports, and the handoff goes into `logs/YYYY-MM-DD-<task>-<session>.md`. Do not create an extra runtime layer, sample project, or task mirror.

Report the corresponding task status only when the agreed changes are complete, applicable checks have traceable records, unfinished items are explicit, and the handoff lets work continue. Blocked coding cannot be reported as complete; completing an independent documentation task does not mean business or software acceptance has passed.

## Stop conditions

When the directory or inputs do not match the registration, behavioral facts are unconfirmed, required materials are unreadable, changes conflict, a check failure is unexplained, or authorization is insufficient, stop the affected operations and report the specific gaps. Other independent documentation work whose inputs are complete is not blocked as a result.
