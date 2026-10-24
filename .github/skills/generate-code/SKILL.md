---
name: generate-code
description: Use when initial code generation or project scaffolding is requested for an identified task, including when the project, stack, target paths, or execution inputs may be missing. Not for maintaining existing code or independent documentation fixes (use implement-task).
---

# Generate initial code safely

This is a file-based method shared by humans and agents, not a generator program; it handles only authorized initial generation. **Write nothing to a target until it has passed every preflight check below.**

## Inputs

- Required:
  - The actual task, confirmed scope and non-goals, behavior sources, all acceptance criteria, and planned VTs, each with its baseline.
  - Selected by the user: the application/project, language/stack and versions, target location, and creation authorization.
  - From the [development registration](../../../docs/development.md#project-registration): the actual layout, environment/dependency sources, commands, and each command's cwd and report location.
  - Directories authorized for reading, directories/files to be written, and content that must be preserved.
- When applicable:
  - US/ABB, only when the task actually needs them.
  - When a [BC configuration](../../../architecture/README.md#bc-configuration) is adopted: its actual source roots, paths, pinned objects, and read-only nature.

## Steps

1. Confirm the route:
   - Authorized initial generation: continue with this method.
   - Existing code maintenance: use [implement-task](../implement-task/SKILL.md).
   - Independent documentation fix: follow the documentation path of implement-task.
2. Complete the preflight gate.
3. Prepare the proposed-files statement.
4. Write and verify.
5. Report the result as described in Done when.

<a id="preflight"></a>
## Preflight gate

This is a hard gate: complete every check here before any write.

1. Check the directory, Git branch, full commit, index, and pre-existing changes.
2. Read the task and its actual sources, and check the acceptance criteria and plan with [specify-feature](../specify-feature/SKILL.md#plan-verification). Unconfirmed rules, unreadable sources, and conflicts support only questions or candidates; never generate definite business behavior from them.
3. Verify each [project creation input](../../../docs/development.md#creation-inputs) and the authorization to run each command.
   - New project with no source code yet: state explicitly that none exists; verify the intended native layout and the files the tools can produce.
   - Existing project: keep its actual layout.
   - If the project, stack/version, path, environment, actual commands/cwd/reports, or creation permission is missing, record `blocked` with the exact gaps and keep related behavioral VTs `not-run`.
   - Never unblock by borrowing the maintenance tools' Python stack, a sample application, or fake commands.
4. Explicitly read the [architecture](../../instructions/architecture.instructions.md), [coding](../../instructions/coding.instructions.md), [security](../../instructions/security.instructions.md), and applicable [test rules](../../instructions/tests.instructions.md) in full. Rule globs do not cover every actual code location, and they do not authorize execution.
5. For every path to be written, resolve its actual root, parent directory, and link targets. Check the allowed scope and all existing content.
   - Stop the write to a path when its directory does not match, when it is out of scope or unreadable, or when it is a conflicting non-empty target. List the exact path.
   - Send task changes to existing files to the maintenance path ([implement-task](../implement-task/SKILL.md)). Do not use an initializer in place of review.
   - Keep the original bytes or a retrievable snapshot.

Record: `blocked` with the exact gaps, and the exact path of every stopped write.

<a id="proposed-files"></a>
## Proposed files

Before writing, state what will be generated. Record these fields for each proposed file:

| Field | What to record |
|---|---|
| Path and action | Resolved exact target, owning project, existing content/conflicts, and the allowed creation scope |
| Source and responsibility | Actual source text, pinned baseline, and the behavior the file is and is not responsible for; gaps must not turn into default implementations |
| Acceptance and trace marker | Full owner-qualified IDs/anchors, and how they are located in native project comments, test identifiers, or task records |
| Native generation/check scope | Actual tools and arguments, explicit cwd, files the tools may write as a side effect, environment/dependencies, report location, and current authorization |

1. Show the statement to the requester or save it in an authorized task record; it is not automatically approval.
2. If you cannot list a tool's outputs, side effects, or commands, stop any generation that depends on that tool.
3. Do not add bootstrap steps, dependency choices, authentication/deployment configuration, or test projects that were not shown.
4. A maintenance task without formal artifacts may cite the actual task conditions. Do not invent IDs.

Record: the proposed-files statement.

<a id="generation"></a>
## Writing and verification

Write only what passed preflight, then check what was actually produced.

1. Generate only for authorized targets that passed preflight without conflicts, and recheck the existing content right before writing. If a tool produces out-of-scope output or a new conflict, stop further actions, describe the actual changes, and ask how to proceed. Do not clean up owner files yourself.
2. Check the actual diff, sources, and trace markers against the proposed-files statement. Report omitted, skipped, and unauthorized extra files separately; do not call partial generation complete. For a missing business policy, keep an explicit blocker, and do not generate default behavior that merely "looks usable".
3. Following [verify-change](../verify-change/SKILL.md), run only registered and authorized native checks, and check the discovered/executed/skipped counts and per-item reports. File existence, a successful compile, a test name, or a zero exit code alone cannot prove behavioral acceptance. Tests that were not run stay `not-run`; do not fabricate results or auto-generate tests to pass them off as execution.
4. Following [record-handoff](../record-handoff/SKILL.md), link the actual files, the checks and their baselines, preserved content, conflicts, and remaining inputs.

## Guardrails

- Without explicit authorization, do not overwrite, append, delete, or rename.
- Leave user content, read-only domain sources, and unrelated paths unchanged.
- Commits, installs, remote operations, and releases are handled separately under current authorization. This method does not grant these permissions.

## Outputs

- Generated files → only authorized targets that passed preflight without conflicts.
- Proposed-files statement → shown to the requester or saved in an authorized task record.
- Native check evidence → the registered report locations.
- Links to files, checks, baselines, preserved content, conflicts, and remaining inputs → the handoff record (record-handoff).

## Done when

Report the generation result for a scope only when the authorized files are fully written, the diff and sources have been checked, the required native checks have actual evidence, and the remaining gaps are clear.

Report blocked or partial generation, documentation derivation, source generation, actual runs, and acceptance success separately. **Skipping conflicts does not mean generation is complete.** Never cover a missing source, a path conflict, or insufficient execution prerequisites with "done".

## Stop conditions

- Stop and record `blocked` when a creation input or permission is missing (Preflight gate 3).
- Stop the write to a path whose directory does not match, that is out of scope or unreadable, or that is a conflicting non-empty target (Preflight gate 5).
- Stop generation that depends on a tool whose outputs, side effects, or commands you cannot list (Proposed files 2).
- Stop further actions when a tool produces out-of-scope output or a new conflict, and ask how to proceed (Writing and verification 1).
- Then: keep the exact gaps and paths visible.
- Do not stop unrelated documentation tasks because application inputs are missing.
