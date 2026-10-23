---
name: update-template
description: Use when a template version changes, a project has owner edits against an old template, or explicitly selected BCs need proposals for versioned source scenarios. Not for first-time onboarding of project materials (use project-onboarding).
---

# Compare template versions and make multi-target proposals

Read the old baseline, the current owner content, and the new candidate separately. **A difference is a proposal, not an applied result or an authorization to propagate.** Humans and agents share this method; it does not depend on prompts or maintainer workflows.

## Inputs

- Required:
  - The task, its allowed file scope, read/write permissions, and completion conditions.
  - The actual template source in the [project registration](../../../README.md#project).
  - The local roots, readable files, and versions of the actual old baseline, local project, and new candidate.
  - Local uncommitted changes, intentional deletions, business data, and original rule locations.
  - The [maintenance tool environment](../../../docs/development.md#maintenance-tools) and this run's output location.
- When applicable:
  - For multi-target runs, as defined in the [registration contract](../../../docs/template-updates.md#registration): the source scenario, allowed files, target repositories/contexts, local checkouts, exact versions, and the targets explicitly selected for this run.
- Never substitute HEAD, a branch, an empty directory, or the first target for a missing input.

## Steps

1. Read [AGENTS](../../../AGENTS.md), the task, and the actual materials first. Check the working directory, branch, commit, index/working files, and existing changes.
2. Following the [tool contract](../../../docs/template-updates.md#api), check the three roots and the actual raw bytes.
   - When an exact Git/content version is given, verify it.
   - Never label a dirty file as HEAD without verification.
   - The default mode and the API do not write. Only an explicit new report may be written, and only outside all protected sources. Never overwrite an existing report.
3. Run the same Python core (see Command example) to obtain `changes/conflicts/preserved`. For each item, read the path, the old/local/candidate versions with their digests (or explicit absence), the operation, and the reason.
   - Do not normalize binaries, BOMs, line endings, or intentional local deletions.
   - Do not auto-merge, pick ours/theirs, or resurrect content the owner deleted.
4. Check multi-target runs in this order: source scenario → explicit BC → allowed files → per-target result.
   - Read only existing local sources. Do not copy the model or the whole repository.
   - A target that is unavailable or in conflict does not hide the other results.
   - Never use a few successes to claim that the whole batch has propagated.
5. Apply the stop points in Result handling per affected target.
6. If native Git/platform operations follow later, obtain separate current authorization for the **specific target, version, and action**. Before acting, re-read the source version and the exact proposal.
7. Use [verify-change](../verify-change/SKILL.md) to check actual results and source protection. Use [record-handoff](../record-handoff/SKILL.md) to link proposals and gaps.
   - Record only the necessary identities, digests, and diagnostics.
   - Do not copy local business text, secrets, or full chats.

## Command example

Run from the repository root with this run's actual project interpreter. This is a Windows example; on other hosts, substitute the actual interpreter (for example, `.venv/bin/python`) and use `/` separators.

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --registration "<local-registration.yaml>" --target "<explicit-target-id>"
```

- Replace every angle-bracket placeholder with an actual input.
- `--target` may be repeated.
- For the three-root mode, exact versions, the 16 decision classes, and new-output rules, see the [update guide](../../../docs/template-updates.md). This method does not duplicate the algorithm.

## Result handling

Apply each row to the affected target.

| Observation | Output and next step for this run |
|---|---|
| `no-change` / 0 | Already aligned, or only owner changes are preserved. Not a successful apply or propagation. |
| `proposed` / 0 | Reviewable add/modify/delete proposals. The target has not been modified yet. |
| `conflict` / 1 | Keep the conflicts and all identities. Stop merging into that target until the owner decides. |
| `input-error` / 2, or per-target `unavailable` | Keep the missing-root/version/read/registration/scope problems. Stop that target and recompute once the inputs are supplied. |
| Unclear permissions/scope, or a non-empty target/output not authorized for modification | Stop writing. Do not skip conflicts and then report completion. Do not build a separate application or executor to unblock. |

## Guardrails

- Never write back to read-only sources.
- Do not overwrite the whole repository or move the business layout.
- Do not treat a historical distribution manifest as the file scope of the current version.
- The configuration, a proposal, the word `apply`, and this method do not approve clone/fetch, file changes, commit/push, PRs, or merges. This tool has none of these operations.
- Do not misread inputs: a missing old baseline does not mean "the template never had the file"; an unreadable file is not a deleted file; a local-only file is not an outdated template.
- A report exiting 0, a file existing, or workflow YAML parsing successfully does not prove that business acceptance, manual approval, client discovery, or an external fan-out has run.

## Outputs

- Per-target results → stdout by default, with nothing written; or one explicit new report outside all protected sources.
- Links to proposals and gaps → the handoff record (record-handoff).
- Targets → not modified by this run (see Guardrails).

## Done when

- Every selected target has its own result from Result handling, and no unavailable or conflicting target hides the others.
- Actual results and source protection have been checked with verify-change.
- Proposals and gaps are linked through record-handoff.

## Stop conditions

- Stop the affected target at each stop point in Result handling: `conflict`, `input-error` / `unavailable`, and unclear permissions/scope or an unauthorized non-empty target/output.
- Stop any native Git/platform operation that lacks separate current authorization for its specific target, version, and action (Step 6).
- Then: handle the target as its Result handling row says; the other targets' results stay visible.
