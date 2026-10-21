# Six-repository functional enhancement: plan handoff

This is a planning record for the maker repository; it does not go into the downstream skeleton candidate.

<a id="session"></a>
## Session, task, and Git state

| Field | Record |
|---|---|
| Date and session | 2026-10-14; `1ff56941-bf56-4aa4-b769-fd4720915e1f` |
| Task source | User request "generate a plan for this enhancement"; the preceding question was what still needs to be implemented to align with the six `ddd-*` repositories |
| Scope of this session | Write the enhancement specification and phased plan, and connect them to the existing plans and decisions; do not implement tools or business projects |
| Direction chosen by the user | Functional equivalence, single repository, tech-stack neutral, no backward compatibility with old formats required; in-project Python tools and a PowerShell 7 Windows entry point, no custom CLI/executor |
| Branch/starting baseline | `callentan-repository-skeleton`; `453189135af07f8ba5ab65dd4dd58879b8741c17` |
| Pre-existing uncommitted content | Table-separator formatting in two places in README; kept as is and not mixed into the planning commit |
| Objects of this session | Two new planning documents, navigation and status in the roadmap/decisions, and this log; the creating commit is located through Git file history, and its own hash is not pre-filled |

<a id="changes"></a>
## Changes and fact ownership

The [enhancement specification](../docs/design/ddd-functional-alignment.md) owns ENH-01 through ENH-14, the user's choices, and the design conventions; the [enhancement plan](../docs/plan/2026-10-14-ddd-functional-alignment.md) owns future file responsibilities, dependencies, steps, test cases, and implementation gates. The specification and plan are planning bases, not a confirmed downstream product model.

The six full reference commits come from the existing source registration; this round did not re-audit the full contents of the six repositories. Task 1 is precisely the prerequisite for filling in per-file capability evidence, so no claim is made that an exhaustive matrix already exists. Source code and forms are not reused directly, and internal evidence does not go into the candidate.

<a id="verification"></a>
## Results and items not run

This round performed only a planning self-review and document checks. The self-review covered task coverage for each ENH, actual file responsibilities, dependencies, tool-interface consistency, not-yet-implemented status, and authorization gates. The actual document-check results take this session's tool output as their source and cannot be treated as tests of the enhancement tools.

The self-review found and corrected three plan-interface problems: the tool environment must be prepared before the RED tests; Tasks 4/5 share method entry points and therefore cannot overwrite them in parallel; and maintainer tests/propagation workflows are not distributed, so downstream CI cannot depend on them. The imports/APIs in the five test examples are aligned with the interfaces and test helpers defined in each task.

The local planning check `validate-ddd-plan.py` used the current repository as its explicit root and read the five documents from this session; the result is saved in `ddd-plan-check.json`. It checks only navigation, the 14 task/ENH mappings, and Python example syntax; it does not run the examples, parsers, or enhancement acceptance. The raw output is in this session's history and the artifacts are available only on this machine, so no fake repository report link is constructed.

None of the planned Python/PowerShell code, schemas, forms, methods, CI, hooks, or propagation scripts has been created; enhancement unit/integration/behavior tests are `not-run`. This round did not install dependencies, initialize an application, change source materials, or perform remote operations, and it did not declare functional equivalence with the six repositories.

<a id="handoff"></a>
## Next steps and blocking boundaries

The next step, once the user approves execution, is to freeze the six-repository capability matrix in Task 1 and then review the Task 2 contract; source verification must not be bypassed by starting directly with parsers/generators. As long as a pinned source is unreadable, the affected equivalence judgments stay blocked, and historical summaries are not expanded into facts about the original repositories.

The concrete trial project/stack/location and real commands for business code generation have not been selected; Task 13 confirms them first at execution time and does not infer them from the Python used by the maintenance tools. Hook installation, real CI/required checks, cross-repository updates/PRs, and release require separate operational authorization; the plan is not authorization.

The real App core results from the original P3 can serve as the baseline for the original version, but the manual path and the remaining client entry points are still untested; once the new workflows and tools change, new results are needed and the old pass cannot be carried over. On takeover, check Git, the pre-existing README formatting, and the history of the planning files; local artifacts are not claimed to be available as cross-machine evidence.

<a id="python-first-revision"></a>
## 2026-10-15: Script strategy revision

After reviewing the responsibilities of the original repositories' validators, hooks, and pipelines, the user confirmed that "adopting a similar strategy means using Python scripts for basically everything." Starting from planning commit `3f3d7c5575d860b9e25c38ae1186decb579342bc`, this session revised the specification, plan, roadmap, decisions, and this record. The PowerShell entry point above is the historical 2026-10-14 approach; the [specification's tool boundary](../docs/design/ddd-functional-alignment.md#method-tool-boundaries) is now authoritative.

The `.ps1` files and wrapper-layer tests that the plan required as deliverables were removed; project Python is now called directly, with checks for arguments, cwd, paths containing spaces, and real exit codes. Hooks/CI reuse the same logic; native YAML and thin launch adapters that are genuinely needed are kept. Method judgments are not rewritten as an executor, and new automation is not passed off as the corresponding feature of the original repositories.

This session again changed only planning documents; it did not create enhancement scripts, installation packages, hooks, or a business application. The two pre-existing README formatting changes were kept and not mixed into the planning revision. Document navigation, ENH task coverage, and example syntax were checked with the local planning check; the result does not represent enhancement tests, and old reports are not rewritten as a pass for this session.

This session's check output is saved separately in `ddd-plan-python-first-check.json`: the five documents, 24 relative links, the syntax of five Python examples, and the 14 task/ENH mappings had no errors, and `git diff --check` exited 0. The remaining PowerShell mentions were reread and confirmed to be only historical records, explicit statements of non-dependence, or references to the user's available terminal; no wrapper script remains a required deliverable. The raw results are still only local session evidence.
