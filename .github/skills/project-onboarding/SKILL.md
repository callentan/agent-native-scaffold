---
name: project-onboarding
description: Use when joining an existing repository, adopting this skeleton, or starting with incomplete project information. Not for comparing old, local, and new template versions (use update-template).
---

# Onboard a project

First separate existing content, confirmed inputs, and open items. Humans can follow this method directly; it needs neither an agent service nor an existing application.

## Inputs

- Required:
  - The current task's goal, scope, completion conditions, and authorization.
  - Project materials the user has confirmed, with their sources.
  - The current directory, Git status, and existing README, AGENTS, rules, and material locations.
- When applicable:
  - The adopted template source, if confirmed.

## Steps

1. Check the actual working directory, branch, commit, index (staging area), and uncommitted scope. Read the [project registration](../../../README.md#project) and the existing rules.
   - Distinguish existing content from content proposed for this merge.
   - Compare differences item by item.
2. Enter only confirmed names, stage, scope summary, and source version in the project registration.
   - Do not guess an unknown stage.
   - When a version has no basis, keep the original placeholder.
   - Details of goals, users, scope, and constraints belong in the [product description](../../../stakeholder-requirements/README.md#product). Do not keep a second copy in the README.
3. Record each gap under the stage it affects.
   - Questions that affect current materials or business decisions → the open-items section of the product description, with the blocked scope noted.
   - Inputs that only affect later coding → the [development registration](../../../docs/development.md#project-registration) and its [gaps section](../../../docs/development.md#troubleshooting).
   - Documentation-only tasks may continue.
4. Decide whether business modeling applies.
   - When business matters are involved, check facts against the [domain sources](../../../domain-model/README.md#sources), then use [define-requirements](../define-requirements/SKILL.md).
   - When an optional local domain source is needed, also read [the difference between registration and materialization](../../../docs/domain-sources.md#operations).
   - For technical or documentation maintenance, state that business modeling is not applicable.
5. Check this session's registrations and links, and state which fields remain unconfirmed.
6. Close out with [record-handoff](../record-handoff/SKILL.md).
   - Use the [log form](../../../_templates/items/development-log.md#session) to record the task and Git scope.
   - Leave a usable handoff under "Changes in this session", "Actual result entry points", and "Blockers and next steps".
   - A full chat transcript does not replace the record.

## Guardrails

- Keep owner markers, rule locations, and unrelated changes. Do not overwrite the whole repository or move code.
- Never fabricate information to make something look "done".
- Onboarding itself does not initialize code, install dependencies, or choose a tech stack.
- Move on to implementation separately, and only after the user has chosen the project, tech stack, and location; granted authorization; and the [actual development inputs](../../../docs/development.md#creation-inputs) are complete.

## Outputs

Formal content goes, as needed, to:

- Confirmed project registration → the root `README.md`.
- Product details and current-stage open items → `stakeholder-requirements/README.md`.
- Coding-stage inputs and gaps → `docs/development.md`.
- Handoff → `logs/YYYY-MM-DD-<task>-<session>.md`. For log fields, see the [log guide](../../../logs/README.md#recording).

Existing projects keep their actual material locations.

## Done when

- Known information has sources.
- Existing content is preserved.
- Gaps for the current and later stages are kept separate.
- The next step is clear.

This does not mean the development environment is configured or business acceptance has passed.

## Stop conditions

- Stop the affected writes when materials are unreadable, behavioral facts conflict, a merge has conflicts, or authorization is insufficient.
- Then: keep the current state, and list the specific paths, the problems, and who must confirm what.
- A missing tech stack blocks only the coding work that needs it, not documentation maintenance whose inputs are complete.
