---
name: implement-task
description: Use when an identified task is ready for scoped edits, or an implementation request may lack project or development inputs. Not for initial code generation or project scaffolding (use generate-code).
---

# Implement the current task

Start from the actual directory, the task basis, and the acceptance criteria. Documentation maintenance and coding have different prerequisites. **Never generate a project on your own initiative just to carry out a request.**

## Inputs

- Required:
  - Goal, scope, non-goals, completion conditions, and the source of authorization.
  - The actual working tree and Git status.
  - The affected model, REQs, SRs, VTs, and necessary design.
- When applicable:
  - The current task or an existing [US](../../../user-stories/README.md), if any.
  - For coding: the project, tech stack, location, and environment selected by the user, and a verified [development registration](../../../docs/development.md#project-registration).

## Steps

1. Check the workspace and read the applicable rules.
   - Check the current directory, branch, commit, index, pre-existing uncommitted changes, and the actual file tree.
   - Read the task source and its completion conditions.
   - When editing Markdown, read the [documentation rules](../../instructions/docs.instructions.md).
   - When editing any test, explicitly read the [test rules](../../instructions/tests.instructions.md).
   - When editing code, also read the [architecture](../../instructions/architecture.instructions.md), [coding](../../instructions/coding.instructions.md), and [security rules](../../instructions/security.instructions.md) in full, even if the actual paths do not match their globs. Do not rely on automatic loading alone.
2. Before writing, read the affected domain rules/contexts, REQs, SRs, and VTs.
   - Confirm the applicable acceptance criteria and the pre-implementation verification plan with [specify-feature](../specify-feature/SKILL.md).
   - If the task changes the model or requirements, first handle sources, downstream items, expectations, and baselines with the [verify-change semantic impact check](../verify-change/SKILL.md#impact). Do not mechanically implement the old task.
3. Choose a path:
   - **Documentation-only maintenance:** continue with steps 4-8, following the documentation branches.
   - **Initial code generation:** use [generate-code](../generate-code/SKILL.md). This method does not rerun an initializer over existing code. When the [project creation prerequisites](../../../docs/development.md#creation-inputs) are incomplete, do not initialize anything or install dependencies.
   - **Existing code maintenance:** continue with steps 4-8, following the code branches.
4. Confirm the prerequisites of your path.
   - Documentation-only: with an explicit path, basis, and completion conditions, continue according to the [document check guide](../../../docs/development.md#document-checks). Do not wait for a tech stack. Do not create new business artifacts.
   - Existing code:
     - Verify the user-selected project/stack/location/environment, the actual source/test layout, and the registered commands/cwd/reports.
     - When a BC configuration is adopted, check the actual source root, relative paths, pinned baseline, and read-only nature. Never write back to sources.
     - If anything is missing, mark the affected task `blocked` and the related checks `not-run`, and state who must supply what. Never unblock with a new project, a default stack, or fake commands.
5. Once the inputs are complete, study the change target.
   - Code: read the relevant implementation, calls/boundaries, native tests, and existing diff in the directory the task specifies. Establish a repeatable check or an actual reproduction.
   - Documentation: check only the specified materials, basis, and applicable document checks. No application layout is required.
6. Record the exact files to change and the acceptance criteria they map to. Then make the smallest complete change.
   - In code, locate full owner-qualified acceptance IDs through the project's existing comments/test identifiers or the task record. Do not create a dedicated traceability framework.
   - On a conflict, a write to an unexpected path, or a failed check, stop the affected action and locate the cause. Do not switch to initializer overwrites or narrow the acceptance criteria.
7. Run the applicable checks with [verify-change](../verify-change/SKILL.md) and keep the actual evidence.
   - Distinguish documentation results, behavioral VTs, old results, and current applicability.
   - Recheck the diff against the task scope.
   - Update an existing task checklist only to reflect what was actually completed. A ticked checklist item is not an acceptance result.
8. Following [record-handoff](../record-handoff/SKILL.md), use the [log form](../../../_templates/items/development-log.md#follow-up) to leave the changes, result entry points, exact gaps, blockers, and next steps.

## Guardrails

- Keep owner content, unrelated changes, and the native layout.
- Do not create an extra runtime layer, sample project, or task mirror.
- Commits, pushes, PRs, and other external side effects are handled separately under actual authorization. This method grants no permissions.

## Outputs

- Changes → the explicitly specified documents or actual project paths.
- Tests → the project's native locations.
- Verification → existing VTs and actual reports.
- Handoff → `logs/YYYY-MM-DD-<task>-<session>.md`.

## Done when

Report the corresponding task status only when:

- the agreed changes are complete;
- applicable checks have traceable records;
- unfinished items are explicit;
- the handoff lets work continue.

Blocked coding cannot be reported as complete. Completing an independent documentation task does not mean business or software acceptance has passed.

## Stop conditions

- Stop the affected operations and report the specific gaps when:
  - the directory or inputs do not match the registration;
  - behavioral facts are unconfirmed;
  - required materials are unreadable;
  - changes conflict;
  - a check failure is unexplained;
  - authorization is insufficient.
- Other independent documentation work whose inputs are complete is not blocked as a result.
