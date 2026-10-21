---
name: update-template
description: Use when a template version changes, a project has owner edits against an old template, or explicitly selected BCs need proposals for versioned source scenarios.
---

# Template updates and multi-target proposals

Read the old baseline, the current owner content, and the new candidate separately; **a difference is a proposal, not an applied result or an authorization to propagate**. Humans and agents share this method; it does not depend on prompts or maintainer workflows.

## Inputs

- This task, the allowed file scope, read/write permissions, and completion conditions; the actual template source in the [project registration](../../../README.md#project).
- The local roots, readable files, and versions of the actual old baseline, local project, and new candidate; local uncommitted changes, intentional deletions, business data, and original rule locations.
- Multi-target runs also need, as defined in the [registration contract](../../../docs/template-updates.md#registration), the source scenario, allowed files, target repositories/contexts, local checkouts, exact versions, and the targets explicitly selected for this run.
- The [maintenance tool environment](../../../docs/development.md#maintenance-tools) and this run's output location; never substitute HEAD, a branch, an empty directory, or the first target for a missing input.

## Steps

1. First read [AGENTS](../../../AGENTS.md), the task, and the actual materials; check the working directory, branch, commit, index/working files, and existing changes. Never write back to read-only sources; do not overwrite the whole repository or move the business layout, and do not treat a historical distribution manifest as the file scope of the current version.
2. Following the [tool contract](../../../docs/template-updates.md#api), check the three roots and the actual raw bytes. When an exact Git/content version is given, verify it; a dirty file must never be labeled as HEAD without verification. The default mode and the API do not write; only an explicit new report may be written, and only outside all protected sources; existing reports are never overwritten.
3. Run the same Python core to obtain `changes/conflicts/preserved`, and read each item's path, the old/local/candidate versions with their digests (or explicit absence), the operation, and the reason. Do not normalize binaries, BOMs, line endings, or intentional local deletions; do not auto-merge, pick ours/theirs, or resurrect content the owner deleted.
4. Check multi-target runs as "source scenario → explicit BC → allowed files → per-target result"; read only existing local sources, and do not copy the model or the whole repository. A target that is unavailable or in conflict does not hide the other results, and a few successes cannot be used to claim that the whole batch has propagated.
5. Apply the stop points in the table below per affected target. If native Git/platform operations follow later, obtain separate current authorization for the **specific target, version, and action**, and first re-read the source version and the exact proposal. Neither the configuration, a proposal, the word `apply`, nor this method approves clone/fetch, file changes, commit/push, PRs, or merges; this tool has none of these operations.
6. Use [verify-change](../verify-change/SKILL.md) to check actual results and source protection, and [record-handoff](../record-handoff/SKILL.md) to link proposals and gaps. Record only the necessary identities, digests, and diagnostics; do not copy local business text, secrets, or full chats.

## Quick reference and stop points

| Observation | Output and next step for this run |
|---|---|
| `no-change` / 0 | Already aligned, or only owner changes are preserved; not a successful apply or propagation |
| `proposed` / 0 | Reviewable add/modify/delete proposals; the target has not been modified yet |
| `conflict` / 1 | Keep the conflicts and all identities; stop merging into that target until the owner decides |
| `input-error` / 2, or per-target `unavailable` | Keep the missing-root/version/read/registration/scope problems; stop that target and recompute once the inputs are supplied |
| Unclear permissions/scope, or a non-empty target/output not authorized for modification | Stop writing; do not skip conflicts and then report completion, and do not build a separate application or executor to unblock |

For example, from the repository root with this run's actual project interpreter (Windows example; on other hosts substitute the actual interpreter, such as `.venv/bin/python`, and `/` separators):

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --registration "<local-registration.yaml>" --target "<explicit-target-id>"
```

Replace every angle-bracket placeholder with an actual input; `--target` may be repeated. For the three-root mode, exact versions, the 16 decision classes, and new-output rules, see the [update guide](../../../docs/template-updates.md); this method does not duplicate the algorithm.

## Common mistakes

A missing old baseline does not mean "the template never had the file"; unreadable is not deleted; a local-only file is not an outdated template. A report exiting 0, a file existing, or workflow YAML parsing successfully does not prove that business acceptance, manual approval, client discovery, or an external fan-out has run.
