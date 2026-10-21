---
name: project-onboarding
description: Use when joining an existing repository, adopting this skeleton, or starting with incomplete project information.
---

# Project onboarding

First separate existing content, confirmed inputs, and open items. Humans can follow this method directly; it needs neither an agent service nor an existing application.

## Inputs

- The current task's goal, scope, completion conditions, and authorization; project materials the user has confirmed, with their sources.
- The current directory, Git status, and existing README, AGENTS, rules, and material locations; the adopted template source (if confirmed).

## Steps

1. Check the actual working directory, branch, commit, index (staging area), and uncommitted scope; read the [project registration](../../../README.md#project) and the existing rules. Distinguish existing content from content proposed for this merge, and keep owner markers, rule locations, and unrelated changes. Compare differences item by item; do not overwrite the whole repository or move code.
2. Enter only confirmed names, stage, scope summary, and source version in the project registration. Do not guess an unknown stage, and keep the original placeholder when a version has no basis. Details of goals, users, scope, and constraints belong in the [product description](../../../stakeholder-requirements/README.md#product); do not keep a second copy in the README.
3. Record each gap under the stage it affects: questions that affect current materials or business decisions go into the open-items section of the product description, with the blocked scope noted; inputs that only affect later coding stay in the [development registration](../../../docs/development.md#project-registration) and its [gaps section](../../../docs/development.md#troubleshooting). Documentation-only tasks may continue; never fabricate information to make something look "done".
4. When business matters are involved, check facts against the [domain sources](../../../domain-model/README.md#sources), then use [define-requirements](../define-requirements/SKILL.md); when an optional local domain source is needed, also read [the difference between registration and materialization](../../../docs/domain-sources.md#operations). For technical or documentation maintenance, state that business modeling is not applicable. Onboarding itself does not initialize code, install dependencies, or choose a tech stack. Move on to implementation separately, and only after the user has chosen the project, tech stack, and location, has granted authorization, and the [actual development inputs](../../../docs/development.md#creation-inputs) are complete.
5. Check this session's registrations and links, and state which fields remain unconfirmed. Use the [log form](../../../_templates/items/development-log.md#session) to record the task and Git scope, and leave a usable handoff under "Changes in this session", "Actual result entry points", and "Blockers and next steps". Close out with [record-handoff](../record-handoff/SKILL.md); a full chat transcript does not replace the record.

## Outputs and completion

Formal content goes, as needed, into the root `README.md`, `stakeholder-requirements/README.md`, `docs/development.md`, and `logs/YYYY-MM-DD-<task>-<session>.md`; existing projects keep their actual material locations. For log fields, see the [log guide](../../../logs/README.md#recording).

Onboarding is complete when known information has sources, existing content is preserved, gaps for the current and later stages are kept separate, and the next step is clear. This does not mean the development environment is configured or business acceptance has passed.

## Stop conditions

When materials are unreadable, behavioral facts conflict, a merge conflicts, or authorization is insufficient, keep the current state, list the specific paths, the problems, and who must confirm what, and stop the affected writes. A missing tech stack blocks only the coding work that needs it, not documentation maintenance whose inputs are complete.
