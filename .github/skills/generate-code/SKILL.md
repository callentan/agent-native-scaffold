---
name: generate-code
description: Use when initial code generation or project scaffolding is requested for an identified task, including when project, stack, target paths or execution inputs may be missing.
---

# Safe initial code generation

This is a file-based method shared by humans and agents, not a generator program. It handles only authorized initial generation; existing code maintenance uses [implement-task](../implement-task/SKILL.md), and independent documentation fixes also follow its documentation path. Do not stop unrelated documentation tasks because application inputs are missing.

## Inputs

- The actual task, confirmed scope/non-goals, behavior sources and all acceptance criteria, planned VTs, and their respective baselines; US/ABB only when the task actually needs them.
- The application/project, language/stack and versions, target location, and creation authorization selected by the user; the actual layout, environment/dependency sources, commands, and each command's cwd and report location from the [development registration](../../../docs/development.md#project-registration).
- Directories authorized for reading, directories/files to be written, and content that must be preserved; when a [BC configuration](../../../architecture/README.md#bc-configuration) is adopted, its actual source roots, paths, pinned objects, and read-only nature.

<a id="preflight"></a>
## Pre-generation checks

1. Check the directory, Git branch/full commit, index, and pre-existing changes. Read the task and the actual sources, and check the acceptance criteria/plan with [specify-feature](../specify-feature/SKILL.md#plan-verification). Unconfirmed rules, unreadable sources, or conflicts support only questions/candidates; never generate definite business behavior from them.
2. Verify each [project creation input](../../../docs/development.md#creation-inputs) and the authorization to run each command. When a new project has no source code yet, state explicitly that it does not exist, and verify the intended native layout and the files the tools can produce; existing projects keep their actual layout. If the project, stack/version, path, environment, actual commands/cwd/reports, or creation permission is missing, record `blocked` with the exact gaps and keep the related behavioral VTs `not-run`; never unblock by borrowing the maintenance tools' Python stack, a sample application, or fake commands.
3. Explicitly read the [architecture](../../instructions/architecture.instructions.md), [coding](../../instructions/coding.instructions.md), [security](../../instructions/security.instructions.md), and applicable [test rules](../../instructions/tests.instructions.md) in full. Rule globs do not cover every actual code location, and they do not authorize execution.
4. Resolve the actual root, parent directory, and link targets of every path to be written, and check the allowed scope and all existing content. A mismatched directory, an out-of-scope or unreadable path, or a conflict with a non-empty target stops that write; list the exact path. Without explicit authorization, do not overwrite, append, delete, or rename. Task changes to existing files go to the maintenance path; do not use an initializer in place of review. Keep the original bytes or a retrievable snapshot; **skipping conflicts does not mean generation is complete**.

<a id="proposed-files"></a>
## Proposed files

Before writing, show the requester the following information or save it in an authorized task record; it is not automatically treated as approval:

| Each proposed file | What to record |
|---|---|
| Path and action | Resolved exact target, owning project, existing content/conflicts, and the allowed creation scope |
| Source and responsibility | Actual source text, pinned baseline, and the behavior the file is and is not responsible for; gaps must not turn into default implementations |
| Acceptance and trace marker | Full owner-qualified IDs/anchors, and how they are located in native project comments, test identifiers, or task records |
| Native generation/check scope | Actual tools and arguments, explicit cwd, files the tools may write as a side effect, environment/dependencies, report location, and current authorization |

When there is not enough information to list the outputs, side effects, or commands, stop any generation that depends on that tool; do not add bootstrap steps, dependency choices, authentication/deployment configuration, or test projects that were not shown. Maintenance tasks without formal artifacts may cite the actual task conditions; do not invent IDs.

<a id="generation"></a>
## Writing and verification

1. Generate only for targets that passed preflight without conflicts and are authorized. Recheck the existing content right before writing, and leave user content, read-only domain sources, and unrelated paths unchanged. If a tool produces out-of-scope output or a new conflict, stop further actions, describe the actual changes, and ask how to proceed; do not clean up owner files yourself.
2. Check the actual diff, sources, and trace markers against the proposed-files statement. Report omitted, skipped, and unauthorized extra files separately, and do not call partial generation complete. Keep an explicit blocker for a missing business policy; do not generate default behavior that merely "looks usable".
3. Following [verify-change](../verify-change/SKILL.md), run only registered and authorized native checks, and check the discovered/executed/skipped counts and the per-item reports. File existence, a successful compile, a test name, or a zero exit code alone cannot prove behavioral acceptance. Tests that were not run stay `not-run`; do not fabricate results or auto-generate tests to pass them off as execution.
4. Following [record-handoff](../record-handoff/SKILL.md), link the actual files, the checks and their baselines, preserved content, conflicts, and remaining inputs. Commits, installs, remote operations, and releases are handled separately under current authorization; this method does not grant these permissions.

## Completion and stop points

Report the generation result for a scope only when the authorized files are fully written, the diff and sources have been checked, the required native checks have actual evidence, and the remaining gaps are clear. Report blocked/partial generation, documentation derivation, source generation, actual runs, and acceptance success separately; never cover a missing source, a path conflict, or insufficient execution prerequisites with "done".
