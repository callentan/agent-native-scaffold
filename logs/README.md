# Development logs and handoff

A log holds the changes made in one task or session and the clues needed to take it over; it keeps no second copy of acceptance results. Use the [development log form](../_templates/items/development-log.md) and create `logs/YYYY-MM-DD-<task>-<session>.md` as needed; currently only this guide exists, with no real session record.

<a id="task-basis"></a>
## Task basis

Prefer referencing an existing US, issue, or explicit request, and state its goal, scope, and completion conditions. A standalone maintenance request with no persistent location may keep its summary, source, and stable acceptance identifiers in the optional task basis section, e.g. the placeholder `TASK-NNN-AC-01` with anchor `task-nnn-ac-01`. Fill that section in only when it truly is the task basis; do not copy existing requirements or disguise maintenance conditions as a REQ/SR.

<a id="recording"></a>
## What to record

- Date, session identifier, related task, and the necessary recorder information.
- Branch, object baseline, committed changes, and uncommitted scope; distinguish this session's changes from pre-existing ones, and never write "clean" without checking.
- Actual changes and links to the related artifacts, the sources of important judgments, and items that are still not confirmed.
- Links to actual check records and raw results, including entry points to the object and basis baselines; acceptance results are read from the VT/raw reports, and the log does not keep a separate result status table.
- When applicable, the [minimal tool/task/object/time/decision pointers](../docs/ai-tooling.md#minimal-record); evaluations and [reviews/waivers](../docs/governance.md#decisions) keep their own original records and baselines, and a log, a role, or a trailer is no substitute for approval.
- Coverage gaps, affected items, items pending re-review, operations not run and why, blockers, next steps, and conditions for re-verification.

When there is a new result, append its entry point; do not overwrite records tied to old baselines. Do not save complete chats, credentials, personal absolute paths, production data, or large blocks of sensitive output. Raw reports use a suitable existing location in the project or an authorized report entry point; for a report that is accessible only on the local machine, note the limitation and the actions needed to take over, and do not present it as cross-machine evidence.

After a tool/purpose/object change, check current applicability through the [re-evaluation entry point](../docs/ai-tooling.md#requalification); unknown decisions or evidence are still listed as gaps. Small maintenance tasks without applicable governance requirements need no new qualification or approval chain; this guide provides no interaction ledger tool and does not require archiving complete conversations.

<a id="handoff"></a>
## Take over in a new session

1. Read the [README](../README.md#resume), [AGENTS](../AGENTS.md), the current task, the relevant facts, and the [verification index](../verification/README.md#coverage-index), then read the most recent related logs.
2. Recheck the Git status and baselines, and check whether the changes, gaps, and results in the log still apply; do not simply inherit old success conclusions.
3. Follow the records to find the affected requirements, rules, designs, and VTs, and determine which are pending re-review, which were never run, and which reports are currently inaccessible.
4. Confirm whether the goal, unknown facts, or authorization have changed, then continue with the next step whose inputs are complete. A log does not guarantee that the original process, unsaved edits, or external system state can be restored.

When a check fails, materials are unreadable, or changes conflict, keep the current state and explain. Ordinary progress goes in the log; long-term architecture trade-offs go in an [ADR](../architecture/README.md#decisions) as needed.
