# Six-repository enhancement execution: sources, contracts, and domain forms

This file is a maker-side record and is not part of the downstream template candidate.

<a id="session"></a>
## Session, task, and Git state

| Field | Actual record |
|---|---|
| Date/session | 2026-10-15; `1ff56941-bf56-4aa4-b769-fd4720915e1f` |
| Task | User request: "First commit the current changes. Then start executing the optimizations according to the enhancement plan"; basis: the [enhancement plan](../docs/plan/2026-10-14-ddd-functional-alignment.md) and the [specification](../docs/design/ddd-functional-alignment.md) |
| Branch/start | `callentan-repository-skeleton`; planning version `f9aab56` |
| Commit current changes first | The two pending README formatting edits were committed as `1a6f594` under the new authorization; the Git state was clean afterwards, and nothing remained uncommitted |
| Scope of this session | Inventory the pinned source of the six repositories, build the capability matrix, and complete the scope, then proceed in dependency order; no release, no push, no execution of upstream programs |
| Object location | The actual commits of this log and the matrix are located through Git file history; later implementations are recorded separately, and completion is not pre-filled |

<a id="changes"></a>
## Changes in this session

As agreed, the six full SHAs were fetched read-only with native Git; no submodule was updated, no hook was run, and no reference repository was modified. The browser was once redirected to a sign-in page, but Git credentials were available; source-reading problems were not treated as "no requirement".

Three independent inventory reports cover 252 entries/195 blobs; the merged result is in the [capability matrix](../docs/research/ddd-capability-matrix.md). For directories and gitlinks only metadata was read, and 10 upstream roadmap files are marked as proposals; the remaining 185 files were read in full. The 44 groups of current capabilities overlap and are not a count of delivered features.

The original plan omitted QAS/tactical material, SEQ/Gherkin/SWAS, interface/glossary evolution, source onboarding/adaptation, diagrams/export, and ledgers. The user confirmed full inclusion, with media/PDF/platform dependencies and their execution authorized separately; tasks/ENH-15–18 were added, and the responsibilities of the original tasks and the applicability boundary between the first version and the enhancement were updated. Python-first is unchanged; the old sources' implicit commit/push, read/write contradictions, and empty successes are not features to copy.

<a id="verification"></a>
## Actual result entry points

| Object | Source record | Limitations |
|---|---|---|
| Six-repository source classification and capabilities | [Capability matrix](../docs/research/ddd-capability-matrix.md), [source register supplement](../docs/research/source-register.md#six-repo-source-inventory) | What was checked is the pinned source/carriers, not runs of the upstream programs/platforms |
| Raw snapshots and integrity | Six manifests/Git objects under the local `ddd-alignment-execution/references`; `source-audit.json` | Local only; cannot serve as a cross-machine CI link; the original Git URLs/commits/paths are sufficient to re-fetch read-only |
| Grouped reading | BC/DOMAIN/FRAMEWORK inventory/capabilities in the same directory | Source attributes and our plan recommendations are handled separately; recommendations are not treated as implemented |

An independent check covered every entry, object ID, commit, and source hash, the capability references, and the source line bounds; four report references that ran past the end of a file were corrected to the actual length, and a second check found no errors. No source was changed to fit the reports, and no claim is made that directories/gitlinks were read in full.

The source-gate review clarified the Task 1 scope mapping, the single 32-kind enumeration, the source-field references of the nine views, and the required equivalence criteria for DOCX and presentation export. A second review confirmed these were addressed and pointed out a contradiction between the wording on primary-input errors and on missing optional views. It is now explicit: root/schema/scope/primary-artifact baseline errors fail, while a single missing/unreadable/invalid optional summary yields unverified+gap; errors are not swallowed, and an empty view is not treated as a complete model. The enhancement implementation must still verify these contracts with real tests.

<a id="follow-up"></a>
## Impact and items not run

The plan, specification, blueprint, and P0 applicability scope need revision against the complete sources; the original first-version/P3 records are not voided. The various consumer gitlinks, external ADR/risk/ADO instances, media services, PDF/PPTX engines, and real CI/permissions/approvals were not run; success cannot be inferred from the source inventory.

When Task 1 ended, no enhancement tooling environment had been created, no dependencies installed, and no application initialized. The user chose Python for the core tooling environment; Task 2 then created the manifest first and then the local `.venv`, with actual results recorded separately below. The tooling stack is not treated as the business language; business/platform/media acceptance remains subject to separate authorization.

<a id="handoff"></a>
## Next steps

After the consistency review of the source matrix/scope, move to Task 2: four data contracts, typed parsers, and real-file tests that make input errors, duplicate YAML keys, unknown versions/statuses, scope/IDs, paths, and confirmation claims explicit. See the tests' expected failures before implementing; restore dependencies only after the manifest is ready.

Whoever takes over first checks Git and the actual commits after this log, the plan ledger, and source accessibility; do not re-fetch or redo completed source groups, and do not read the old "planning only" state as meaning the work is currently unauthorized. No new authorization was granted for release, PRs, business projects, or sending data externally.

<a id="task2"></a>
## Task 2: metadata contracts, parser, and maintenance tooling environment

This section appends the actual Task 2 results without rewriting the Task 1 state recorded above. The basis is [enhancement plan Task 2](../docs/plan/2026-10-14-ddd-functional-alignment.md) and the authorized `ddd-alignment-execution/task2-brief.md`; the scope covers only the 17 repository files listed for this task. The starting point was a clean working tree on branch `callentan-repository-skeleton` at full commit `81ffd45b3b9b7643d643a9162b533af92613c553`. The earlier README formatting commit was not repeated.

Added [four data contracts](../.github/contracts/README.md), an [immutable parser and explicit collection interface](../.github/utilities/README.md), separate schema/parser tests, and real-file/Git helpers. `.gitignore` adds only the project `.venv` and Python bytecode; the [development registration](../docs/development.md#maintenance-tools) separates the maintenance environment from the not-yet-configured business application. The existing skills, forms, business material, source code, hooks, workflows, and remotes were not modified.

| Actual record entry point | Object and basis | Accessibility and limitations |
|---|---|---|
| Authorized report of this session: `files/ddd-alignment-execution/task2-report.md` | The Task 2 starting point and the Git commit of this section's batch of files; full SHAs, RED/GREEN commands, raw output summaries, versions, and self-review fixes are all in the report | Local artifact of session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; not part of the repository or the distribution candidate; not cross-machine CI evidence |
| [Parser behavior tests](../.github/utilities/tests/test_artifact_io.py) and [schema tests for the four types](../.github/utilities/tests/test_contracts.py) | Each of the 32 kinds has parser/schema positive cases; the nine views' data, complete references, primary-input errors, and evidence constraints are checked separately | Can be re-run with the registered environment; test source is not a result; this run is located in the report in the row above |
| [Actual dependency lock](../.github/utilities/requirements.lock) and [maintenance commands](../docs/development.md#maintenance-tools) | Manifest created first, then `.venv`; Python 3.13.15, six actual dependency versions, `pip check` reports no conflicts | Current Windows environment; no claim that other Python versions/OSes were actually verified |

Verification first saw the initial missing-module error, then produced a behavioral RED with a deliberately non-validating readable-file implementation: 6 parser methods yielded 12 failures and 4 schema methods yielded 14 failures; these numbers include subtests and are not additional discovered methods. After implementation, the first run passed 140 tests; self-review then added and reproduced a BOM line-number offset, merge normalization swallowing nested duplicate `<<`, and invalid safe-tag values leaking built-in exceptions. After fixing each one, the full suite reported **143 methods discovered/run, 0 skipped, 0 failures/errors** (parser 73, schema/Git data 70). 5 Python files passed the syntax check, and 4 contract-document examples were actually parsed/validated. Read the full commands and key failure details from the report.

The Windows tests for external/internal directory junctions and real file byte locks were all run; no skip was used to hide boundary coverage. `ArtifactInputError` keeps the code, file, 1-based line number, error message, and original exception chain; same-scope duplicate detection applies only to explicit collections and does not scan or rewrite the whole repository.

### Task 2 limitations and next steps

- Task 2 completed the input contracts and parser for ENH-02 and ENH-06; the six-repository enhancement as a whole is not complete. Real source reading/derivation for the nine views, cross-file existence/hierarchy/coverage, primary-baseline authenticity, and manual-edit detection remain for Task 7/8 and are currently `not-run`; no exporter was added just to "pass".
- Business application, media/PDF, external source onboarding, hooks/CI, propagation, release, PRs, and remote writes were not run; the corresponding separate authorization gates remain unchanged. A schema-valid confirmation or pass claim does not certify the person or the authenticity of the evidence.
- Markdown reading is limited to the documented explicit-anchor + owner ATX heading pattern; there is no general Markdown rendering, implicit anchor inference, or automatic legacy-format conversion. The Windows junction results do not generalize to all link types on other hosts, and the path checks are not an OS sandbox against concurrent malicious replacement.
- No known gap blocks Task 2. The parent session dispatches later tasks only after a scope review against the actual commit and report; this executor did not start Task 3 or any nested agent/reviewer. Whoever takes over re-checks Git and the accessibility of the local report and must not simply inherit this summary's pass conclusion.

<a id="task2-review-1"></a>
## Task 2: scope-review feedback fixes, round 1

The feedback of 2026-10-15 12:44 requested three fixes: root error location, distribution documents depending on excluded material, and a contradiction in the plan's current status. At the start, the branch was verified to still be `callentan-repository-skeleton`, HEAD was `4b833dfad154e71e982e7e107d6cb9ae0cdc0464`, and the working tree and index were clean. The feedback also reported that the parent session had independently run 143 tests with 0 skipped on that object; that is the parent session's run and is not presented as new evidence from this round.

This round modified only 7 existing files: `.github/utilities/artifact_io.py`, `.github/utilities/tests/test_artifact_io.py`, `.github/contracts/README.md`, `.github/utilities/README.md`, `docs/development.md`, `docs/plan/2026-10-14-ddd-functional-alignment.md`, `logs/2026-10-15-ddd-alignment.md`. A full record was also appended to the original session's `files/ddd-alignment-execution/task2-report.md`; the report remains a local artifact and is not committed.

- `parse_artifact` changes only one line, setting the root error context to `str(root)`, consistent with the collection API. A new real-file regression asserts `code/path/line` for both APIs, covering a missing root, an actual file used as the root, null, a wrong type, and an empty selection.
- The distribution documents drop links to the internal specification/plan/maker log and commands that depend on the excluded tests; contract fields and examples remain self-contained. Maintainer tests and historical navigation are consolidated in the [maker-repository check conventions](../docs/plan/2026-10-14-ddd-functional-alignment.md#maintainer-checks) and this log; no new checker or document file was added.
- The plan's header, footer, and related status sentences now say Task 1 is complete, the Task 2 implementation is in scope review, and later tasks are `not-run`. The original P3, the source inventory, and the 143-test result at the initial `4b833df` keep their baselines; a verbatim comparison against this round's baseline shows no change to the Task 3–18 content or the ENH coverage table.

All commands in this round used the repository root as cwd and reused the existing `.venv`; no dependencies were installed or restored. Targeted regression command:

```text
.venv\Scripts\python.exe -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_artifact_io.py -v -k test_invalid_root_errors_identify_root_in_both_apis
```

The new test was run first: 1 method with 12 subtests, of which the 4 single-file API subtests failed; in each failure `INVALID_ROOT.path` pointed to `REQ-001.md` instead of the invalid root, while the code and line number were still `INVALID_ROOT` / 1. The original output was `Ran 1 test in 0.009s; FAILED (failures=4)`, exit 1. After the one-line fix, the same command gave `Ran 1 test in 0.007s; OK`, exit 0, with no assertion weakened.

The distribution-dependency diagnostic ran bounded inline Python with the existing interpreter: it read the 3 distribution documents, checked their actual relative links against the excluded paths, and also checked whether they required `unittest discover`. Originally, 5 of 19 local links pointed to excluded material and 2 downstream commands depended on the excluded tests, 7 findings in total, exit 1; after the change: `3 documents, 16 local links, 0 findings`, exit 0. The diagnostic is not distributed as a new tool; the full code and output were appended to the original Task 2 report.

Full suite and syntax checks actually run:

```text
.venv\Scripts\python.exe -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_*.py -v
.venv\Scripts\python.exe -X utf8 -m compileall -q .github\utilities
git --no-pager diff --check
```

The full run output `Ran 144 tests in 5.440s; OK`: 144 methods discovered/run, 0 skipped, 0 failures/errors; the syntax and diff checks exited 0. An independent recount gave parser 74, schema/Git data 70, and 327 parameterized subtests (subtests are not added to the method count), likewise with 0 skipped/failures/errors. All 39 relative links and anchors in the 5 scoped Markdown files are valid; the 3 distribution documents have no dependency on excluded targets; the 4 retained contract examples actually parse/validate. The full diagnostic code, output, and committed object were appended to the original report; the old 143-test result does not substitute for current evidence.

This round did not modify schemas, dependencies, shared skills/forms, or later tools, and involved no subagents/reviewers, installs, hooks, workflows, pushes, PRs, or other remote operations. After committing, work stopped at Task 2 to await the parent session's check of this round's actual diff and evidence; "fixes implemented" does not mean the review is closed or the enhancement fully delivered.

### Parent-session scope check completed

On fix commit `322cd9082c0f99a4583cf54b04590075c5e1b42f`, the one-line parser fix, the new real invalid-root regression covering both APIs, and the scope revisions to the distribution documents/plan were read back; all three feedback items were addressed, with no schema extension and no new runtime functionality.

Using the existing project `.venv` and an explicit repository cwd, the parent session independently ran the full tooling test suite: `Ran 144 tests in 5.054s; OK`, exit 0, 0 skipped. The raw command/output and commit are in the local `ddd-alignment-execution/task2-final-tests.json`; this is not a restatement of the implementer's result. The Task 2 scope review is now closed, and the next step is Task 3; this does not close later acceptance of model export, traceability, App/manual work, or business execution.

<a id="task3"></a>
## Task3: optional domain forms and actual document use

### Session, scope, and object

| Item | Record |
|---|---|
| Date and executor | 2026-10-15; Task3 implementer, single-session execution and self-review, no nested agent |
| Task basis | User-approved [Task3](../docs/plan/2026-10-14-ddd-functional-alignment.md#task3), plus the Task3 brief and case input fixed by the parent session; not a new business requirement |
| Branch and starting baseline | `callentan-repository-skeleton`; `6f8a0f9667f7b4d81840a7d4d6a994ceff45934b`; the full SHA and its ancestry relative to the Task2 fixes were verified |
| Pre-existing changes | The index and working tree were both clean at the start; there were no earlier changes to commit on anyone's behalf |
| Objects in this session | The 24 distribution files described below, the Task3 plan status, and this log; committed together in one scoped commit; read the full commit ID from Git and the session report |
| Non-goals | No changes to the parser/schema, shared skills/agents/prompts, or application/test layout; no dependency installs, no execution of reference sources, hooks/CI, media/platform operations, or remote operations; Task4+ not started |

### Actual changes

- Added 18 independently written domain/QAS/tactical forms; see the [domain artifact navigation](../domain-model/README.md#optional-forms) for the full list and formal locations. Every blank form keeps draft status and an identity to be confirmed by the project.
- Wired them into the [domain guide](../domain-model/README.md#artifact-metadata), the [REQ/QAS guide](../stakeholder-requirements/README.md#domain-inputs), the [scenario/VT guide](../verification/README.md#domain-scenarios), and the [root form navigation](../README.md#forms). The existing lightweight body text, stable anchors, and project facts were not replaced.
- The [REQ form](../_templates/items/stakeholder-requirement.md) and the [VT form](../_templates/items/verification-test.md) adopt the existing frontmatter, and the duplicate content-status field was removed; VT target relations belong to metadata, the body keeps an independent criterion per criterionAnchor, and historical runs are kept separate from current applicability.
- No other field guidance was modified. Maker material, exercise instances, one-off check scripts, and reports did not enter the distribution files or become their dependencies.

### Result entry points and accessibility

The raw results are under `files/ddd-alignment-execution/` of parent session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; the locations below are within that authorized entry point and are not repository commands or cross-machine reports. Whoever takes over must obtain that directory or re-run bounded checks.

| Check layer | Actual record location | Object and limitations |
|---|---|---|
| Parser/schema and actual copied use of the forms | `task3-artifacts/run-03/results.json`, `template-provenance.json`; the actual instances are in the sibling `used-copy/` | 27 draft artifacts cover all 18 new kinds; 10 owner-qualified acceptance criteria and 10 target references; same-scope duplicate IDs rejected. Not a general coverage map or business execution |
| Local document links and preservation | The same `results.json`, `lightweight-before.txt`, and `lightweight-copy/domain-model/README.md` | Local links checked in the 24 changed distribution files, the 57 copied Markdown dependencies, and the positive/duplicate-ID copies; lightweight body text and owner markers preserved byte for byte |
| Document operation for a rule change | `task3-artifacts/run-03/allowance-change-plan.md` | Impact plan for UC/INV/REQ/SR/TS/VT that keeps the original files and unknowns; nothing was actually migrated and no business execution took place |
| Actual maintenance-tool regression in this session | Commands and terminal excerpts in `task3-report.md` | One fresh run of the existing full suite on the current working tree: 144 tests, 0 skipped, exit 0; the historical Task2 pass was not reused |
| Self-review and commit handoff | `task3-report.md` | Exact changed files, copy paths, operations/results, commit ID, and semantic limitations; self-review by the same executor, which does not represent parent-session or human approval |

Records of two check-script problems were kept: `run-01` reported false differences because it compared normalized line endings with the CRLF that the parser preserves; after comparing raw bytes, `run-02` completed. Extending the check to duplicate-ID negative cases then showed that relative links were not relocated after the files moved into `negative/`; after the construction of that temporary copy was corrected, `run-03` completed all bounded checks. Both fixes touched only the session check scripts, not the parser, schema, or distribution forms, and the old outputs were kept.

### Gaps, impact, and stopping point

- The self-use exercise explicitly keeps gaps in qualification lapse, concurrency, QAS measures, tactical boundaries/identity/events, interface versions, and failure policy. All business/software behavior records remain `not-run`; no application, runner, or approval can serve as a basis for execution.
- All 18 kinds have parser/schema positive cases from actually filled-in forms; semantic review is limited to the fixed document cases that were actually worked through. Design correctness of other tactical patterns, real application behavior, performance, and cross-platform support were not verified.
- The current parser does not check complete cross-file coverage or the authenticity of approvals; this session only made a bounded check of explicitly selected fixture relations and delivered no later checker/exporter.
- Task3 implementation and self-review are finished and await the independent scope review by the parent session/user; whoever takes over must re-check this session's commit, the working tree, and the accessibility of the local evidence. This execution stops at Task3; it does not mark Task4+ or unfinished original P3 items as complete, and it does not push or create a PR.

### Task3 independent scope review and next-stage baseline

The independent review of `0aef102257de02cd4cee40ac1ee4af46d14e2251` found no defects in the form/identity/source boundaries; it only found that the plan's footer still said "next step: Task 3". The footer has now been aligned with the header and the task subsection: Task3's scope for this session is complete and the next step is Task4; the delivered forms are not redone. The parent session actually re-ran `144 tests in 4.870s; OK` on that commit, 0 skipped, exit 0; the result is in the local `task3-parent-tests.json`.

Another independent consumer used only the current six shared methods and the new forms to process five fixed input scenarios, actually filled in three drafts (UC, QAS, and Published Interface), and the parser parsed them successfully; the repository was not changed. Incomplete sources, the rule conflict between 2 and 3, the homonym for active, the missing QAS metric, and the interface/approval/coverage gaps were all kept; it did not fabricate missing files, line numbers, actors, metrics, or acceptance IDs. The report is at `task4-baseline-use/task4-baseline-report.md`; it is both a bounded consumer observation of Task3 and the pre-enhancement baseline for Task4, not human participation or an App-native test.

That baseline already shows correct control behavior, so no RED or reliability gain can be invented for the new methods. The functional gap that can be confirmed is that a separate reverse-extraction activity is not yet provided and Task4 has not yet been implemented; the new domain methods must be observed again on the same input with their coverage stated explicitly.

<a id="task4"></a>
## Task4: domain methods, reverse-engineering candidates, and thin entry points

This section appends the actual Task4 results and keeps the previous section as the historical pre-implementation observation. **Task4 is now implemented and awaits independent review; this execution stops at Task4, and Task5–18 are `not-run`.**

### Session, task, and Git objects

| Item | Actual record |
|---|---|
| Date and executor | 2026-10-15; Task4 implementer, single-session implementation and self-use, no nested agent or independent reviewer |
| Basis and scope | User-approved [Task4](../docs/plan/2026-10-14-ddd-functional-alignment.md#task4) and the local session brief; implements only methods/entry points and status records, without re-fetching sources or redoing the baseline |
| Branch and starting object | `callentan-repository-skeleton`; `6f617e101b88e85bbeecfb3347187f24d0f90891`, full SHA verified |
| Pre-existing uncommitted content | The working tree and index were both clean at the start; no need to redo "commit the current changes first" |
| Object definition for this session | 18 distribution documents plus the plan's current status and this log's appended section, 20 repository files in total; the Git commit containing this section and the session report record the full commit ID |
| Authorization boundary | Permitted: the scoped files of this session, explicit self-use/document checks, one run of the existing regression suite, and a local commit with a co-author trailer; no push, PR, install, network access, running of applications/source programs, hooks/CI, or later tasks |

### Actual changes and judgments

- Added [reverse-engineer-domain](../.github/skills/reverse-engineer-domain/SKILL.md), which records candidates, the original basis, epistemic category, conflicts, confirmation needs, and impact from actual files, external records, or supplied excerpts. Missing original files/line numbers are not fabricated; implementation defaults do not become business approval, and metrics/actors/policies that were not provided remain unknown.
- Focused [define-requirements](../.github/skills/define-requirements/SKILL.md) on interviews, knowledge crunching, glossary, interfaces, incoming ADRs, and the optional Intended Use; extended [verify-change](../.github/skills/verify-change/SKILL.md) with domain/BL review, queries, and impact. Kept complete acceptance first, exact target reverse lookup, old and new baselines, and the read-only/execution branches, following the actual Task3 metadata and form contracts.
- Added ten [thin prompts](../docs/agent-support.md#entry-points), each containing only the current input and a link to one actual method section; only the planner/plan-feature selection routing and the README/AGENTS/agent-support navigation were adjusted. The current actual count is seven methods, fifteen prompts, and three modes, not the nine methods of the final plan.
- The four original methods not involved, the other modes, copilot-instructions, forms, parser/schema, dependencies, tests, and blank project facts were not changed; no integration issue requiring changes to record-handoff or copilot-instructions was found. No links to future methods or governance/architecture forms were added.

### Actual result entry points

All locations below are in the authorized `files/ddd-alignment-execution/` of parent session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; they are accessible only on the local machine and are not part of the distribution candidate, so they cannot serve as cross-machine CI links. Whoever takes over must obtain that directory or re-run bounded checks.

| Layer | Actual record location | Object and limitations |
|---|---|---|
| Independent pre-implementation baseline | `task4-baseline-use/task4-baseline-report.md` and seven original outputs | The original six methods already showed correct control behavior; this round only read them and checked hashes, without re-running or manufacturing failures |
| Self-use of the three methods on the same cases | `task4-after-use/case-interview.md`, `case-reverse.md`, `case-glossary.md`, `case-interface.md`, `case-review.md` | Five bounded cases by the same implementer; the specific choices, source locations, conflicts, who must supply what, and forbidden side effects are recorded separately; not an independent review or human participation |
| Form use and additional stop points | UC/QAS/PI drafts in `task4-after-use` and `supplemental-stops.md` | Three actual form uses; fixture identities are not production facts; ADR/Intended Use cover only stops for missing inputs, and queries cover only the current domain directory |
| Document/structure checks | Actual stdout of `task4-checks.py` and `task4-report.md` | Bounded checks of closure/relative links/anchors, YAML, scope, and baseline preservation; no new checker/exporter delivered, and the parser is not treated as a complete traceability engine |
| Maintenance-tool regression | Actual commands and output excerpts in `task4-report.md` | Current project `.venv`, explicit repository cwd, one fresh run of the original 144 tests; not a test of method semantics, business/software behavior, or the App |

The actual regression output was `Ran 144 tests in 4.654s; OK`: all 144 tests ran, 0 skipped, 0 failures/errors, exit 0; no test was changed and the Task3 pass was not reused. The hashes of the original inputs and baseline outputs were preserved. The existing native six-method/P3 records are not upgraded to "seven methods tested"; the new and revised methods are recorded only as explicit-file self-use.

### Gaps, impact, and stopping point

- CASE-REVIEW did not give the owner/ID/path of the actually missing software acceptance, so the review could only point precisely back to the input's section/line and request the original text; no target was invented, and coverage was not reported as complete. An "Approved" without a decision/baseline is still not accepted.
- Gaps remain in the original paths/line numbers, the choice between 2 and 3, actors, QAS measures, contract version/error policy, and the complete consumer list. The new records are candidates or proposals; the existing correct baseline was not described as a discipline failure, and no reliability improvement is claimed.
- Real incoming revisions of the new ADR/Intended Use, broad model/client behavior, the App's native entry points, and manual T17 were not verified; no risk classification was fabricated, and no medical/QMS precondition was imposed on the borrowed cases.
- Independent review is done separately by the parent session/user; this executor did not certify approval. Later tools/adapters, applications, media/PDF/platforms, hooks/CI, pushes, and PRs were not run; the separate authorization gates and full enhancement acceptance are unchanged.
- Whoever takes over first checks this session's full commit, the working tree, the plan's complete current status, and the readability of the local report; review only Task4, and do not automatically start Task5 or any other task from this partial result.

### Task4 parent-session scope review

The independent code/document scope review of `f8df3924da01d807091236651f22f047edff19ca` found no major issues; the parent session also actually ran the original tooling suite on that object: `144 tests in 2.906s; OK`, 0 skipped, exit 0. The new methods are Markdown activity instructions; this regression is not treated as a pass of method behavior or of App-native support.

An independent post-change consumer actually read the three complete methods and produced source/conflict/gap judgments for the five cases plus UC/QAS/PI drafts; the parent session re-parsed the three actual drafts, and their identities, kinds, draft status, and acceptance counts matched that synthetic input. This supports only bounded post-change use; it does not show that all workflows are correct or that performance improved.

That consumer also produced a so-called "no-new-method baseline" within the post-change task; it is not an independent pre-change observation, and its failure narrative is not used as RED, a control, or evidence of improvement. The only valid pre-change baseline remains the correct control record in `task4-baseline-use`, which had kept the unknowns/conflicts. The original report is kept as is; this record states the methodological limitation without rewriting the old observation.

Because of an ambiguous relative output path, the consumer also wrote ten temporary files to an untracked `execution` directory in the repository; the parent session kept all the original bytes and moved them into the local session's `task4-independent-observation`. After the empty directory was cleaned up, Git showed none of these untracked files, and no source file was modified or committed. The byte relocation and the note on the invalid control are in `task4-observation-relocation.json`; the first path cleanup failed because of a directory attribute, and the directory was deleted specifically only after it was explicitly verified to be empty.

The consumer reported that this session's callable skill list did not include the new methods, so it completed the work by reading the files explicitly. There was no independent client loading trace this time, so native discovery remains unverified, and this cannot be extended to a claim that no client supports it. The Task4 scope review is closed; the next step is the BC method in Task5; the media/platform/business/manual acceptance gates are unchanged.

<a id="task5"></a>
## Task5: BC forms, methods, and safe initial-generation contract

This section appends the actual Task5 record and keeps the historical observations of the earlier stages above. **Task5 is now implemented and awaits independent review; this execution stops at Task5, and Task6–18 are `not-run`.**

### Session, task, and Git state

| Item | Actual record |
|---|---|
| Date and executor | 2026-10-15; Task5 implementer, single-session implementation and self-use, no subagent/reviewer |
| Basis and authorization | User-approved [Task5](../docs/plan/2026-10-14-ddd-functional-alignment.md#task5), the local task5-brief, and the ten fixed cases; only documents/methods/rules, bounded checks, one run of the existing regression suite, and a local commit with a co-author trailer |
| Starting branch/full object | `callentan-repository-skeleton`; `d7693a8e481dd84effc155378ae16c255c04d9b7` |
| Pre-existing uncommitted content | The working tree/index were clean at the start; no need to repeat "commit the old changes first" |
| Scope and objects of this session | 31 distribution files plus this plan's status and this log's appended section, 33 files in total; the commit for this batch is located through Git file history; read the full SHA/post-commit state from the local task5-report |
| Unchanged boundaries | No changes to the parser/schema/dependencies/tests, the Task3 domain forms, the other four methods, or the reviewer; no business application generated, no later tools run, no network/installs, no hooks/CI configured, no push or PR |

### Actual changes

- [SR](../_templates/items/software-requirement.md), [US](../_templates/items/user-story.md), [ABB](../_templates/items/architecture-building-block.md), and [ADR](../_templates/items/architecture-decision.md) adopt the existing metadata, and the duplicate content-status/relation tables were removed; VT only gained the [companion](../verification/README.md#feature-companion) hookup, and its original run/applicability and full target inventory are kept.
- Added [SEQ/SWAS and BC configuration field guidance](../architecture/README.md) and a blank feature; the nine views only reference sources and do not manufacture model exports, infrastructure, quality measures, risk classifications, or approvals.
- [specify-feature](../.github/skills/specify-feature/SKILL.md) provides focused subsections for SR, optional slices, necessary architecture, VT/feature, and SEQ/SWAS; [generate-code](../.github/skills/generate-code/SKILL.md) separately handles initial inputs/paths/non-empty conflicts/the planned-generation statement. Maintenance of existing work still uses implement-task, and the documentation path does not depend on application inputs.
- Added three bounded code rules and six thin prompts; planner/implementer only received the relevant routing, and the reviewer still follows verify's original entry point. The original fifteen prompts needed no surgical revision; the new branches are reachable through the shared methods. The actual current count is **8 methods, 21 prompts, 3 modes**, without Task11's update-template.
- The distributed content does not depend on the maker design/plan/research, actual logs, tests, or local session outputs; only the shared log guidance/blank form continue to be distributed. The historical P3 observation of six methods/five prompts/two rules is kept and cannot be upgraded into "native discovery of the new entry points tested".

### Actual evidence entry points

All auxiliary files from this round are inside the absolute, authorized artifact root of parent session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; there is no repository-relative execution output directory. The table below gives only locations within that local entry point; they are not cross-machine evidence or new distributed tools.

| Record entry point | Actual object and limitations |
|---|---|
| `files/ddd-alignment-execution/task5-report.md` | The full report for this session: exact commands/cwd/paths, scope, real checks, commit, and limitations; actual Git was re-checked after the commit |
| `task5-baseline-use/task5-baseline-report.md` | The only real pre-change baseline; read-only this time; the control was already correct, so no RED or reliability gain is fabricated |
| `task5-after-use/start-state.json`, `copy-provenance.json` | 94 tracked files at the start and digests of the four fixed inputs; 90 actual distribution copies and pre-copy byte digests of 11 forms |
| `task5-after-use/BC-USE-01.md` to `BC-USE-10.md` | Bounded operations/stop points by the same implementer on the same ten cases; the original gaps in identity, project, approval, and old reports are kept; not an independent review |
| `task5-after-use/consumer-copy`, `use-check-01.json` | Nine actually filled-in Markdown forms parsed by the original parser, five owner-qualified synthetic acceptance criteria, and three targets; BC uses real local input digests, and the nine views are validated with the existing schema; the feature is only text/mapping |
| `task5-after-use/tool-tests.json` | Current `.venv`, explicit repository cwd, the original suite run only once: `144 tests in 4.977s; OK`, 0 skipped/failures/errors, exit 0 |

The first round of bounded document checks covered 90 distribution files, including 80 Markdown files, 63 YAML frontmatter blocks, and 512 local links; the 92 Markdown files/568 local links of the actual consumer copy can also be located, and six existing external links were not visited. The final status/log check keeps a separate final receipt; these counts are not used to prove business semantics or native client runs.

The original owner fixture was still 225 bytes after the pre-check and the checks, SHA-256 `2b060d2f641e7a1f02ccaf35c676f402aa49726ba06cef4a8b5b6921eda84466`. Another synthetic Markdown fix strictly replaced only one link and kept the surrounding bytes; the original BC-USE-04 lacks an actual target and was not presented as unblocked by that supplementary case. A VT with a wrong owner parses, but its target does not exist; a BC `HEAD` baseline was rejected by the actual schema; the blank configuration still carries explicit placeholders rather than a valid project registration.

No Git repository or commit was created for the Task5 consumer copy. Internally, the original 144-test suite uses its existing helpers to build and clean up local Git/file fixtures in a controlled temporary directory; that is the original suite's internal behavior, not a new business project or a Task5 generation activity. No helper was modified, no hook installed, and no remote connected.

### Gaps and next steps

- Synthetic identities are used only for local structure cases and do not fill in the owners/IDs/source files/baselines that the original ten cases did not give. Without actual UC/INV/CAP/QAS, participants/errors/side effects/concurrency/failure policies, or confirmation, the related requirements/US/architecture remain candidates or blocked.
- The bounded inventory explicitly keeps two uncovered targets, `task5-synthetic/CTX-BORROW/SR-SYN-001#sr-syn-001-ac-02` and `task5-synthetic/CTX-BORROW/ABB-SYN-008#abb-syn-008-vc-01`; metadata/schema and link checks do not mean these acceptance criteria pass.
- The new SEQ is a partial description in a known conceptual direction; SWAS lacks real ABB/deployment/risk/release sources; of the nine views only requirements is partial, and the rest are unverified. There is no Gherkin parser/runner, Mermaid/PDF/presentation rendering, or execution of application behavior; all corresponding results are `not-run`.
- Task13 forward application generation/native runner requires a separately chosen actual project/stack/paths, commands/cwd/reports, and authorization; this session does not require creating an application just to claim success. The later checker/exporter, source onboarding, hooks/CI, and platform/manual acceptance were not started.
- Next, the parent session independently reviews this session's 33 files, the full report, the actual copies of the ten cases, and the complete current status; whoever takes over first checks the full commit, the working tree, and the accessibility of the local evidence. Task5 has not yet received an independent review conclusion, so work does not automatically move on to Task6.

<a id="task5-review"></a>
## Task5 review addendum

On 2026-10-15, parent session `1ff56941-bf56-4aa4-b769-fd4720915e1f` closed this documentation-contract gate under the existing enhancement execution authorization. The branch was verified to still be `callentan-repository-skeleton`, HEAD `5d39f407630d557b8b0bd51fa12efdde0b5bfef8`; after the independent consumer observation, status showed only the branch line, with no staged, unstaged, or untracked files. This addendum only appends to this log and syncs the current status of the specification, plan, and roadmap; it does not change the Task5 implementation or the old records.

The independent scope review of Task5 returned no major issues. The raw record of the parent session's run on the implementation object above is the local session's `files/ddd-alignment-execution/task5-parent-tests.json`: current project interpreter, explicit repository cwd, the original 144 tooling tests, 0 skipped, exit 0, actual duration 2.564 seconds. This is a tooling regression on an unchanged parser/schema, not a result for new business behavior.

The independent post-change consumer's record is at `task5-independent-use/task5-independent-report.md` in the same entry point. It actually read only the ten fixed cases, the current methods/rules/forms, and the owner fixture, and for each case distinguished what can be drafted, missing identity, non-empty conflicts, missing run inputs, historical applicability, and the corresponding stop points; it did not fabricate a separate pre-change baseline, did not run the parser, an application, or a renderer, and did not modify the repository. In its observation the fixture was still 225 bytes, with the same digest as the original value in the previous section. That report supports only this session's explicit-file use and manual structure check; it does not prove native discovery, a human control comparison, or a general reliability gain. The full report and raw tooling records above are accessible only on the local machine; on another machine they must be re-obtained, or the corresponding checks re-run.

The two synthetic uncovered targets from the previous section remain; real application generation, the Gherkin runner, client/manual work, PDF/platforms, and approval have not been accepted. The next step is to implement, per [Task 6](../docs/plan/2026-10-14-ddd-functional-alignment.md), a Python artifact checker with explicit inputs, locations, baselines, and exit codes; this does not mean creating an application or installing later optional dependencies. Whoever takes over must still re-check the current Git state, task status, and evidence accessibility.

<a id="task6"></a>
## Task6: formal artifact checker

### Session, scope, and Git

This section appends the actual implementation and execution record of Task6 / ENH-07 and keeps the original results of the earlier tasks. The task source is the [existing Task6 plan](../docs/plan/2026-10-14-ddd-functional-alignment.md#task6) plus the bounded authorization of this session from the user's request "First commit the current changes. Then start executing the optimizations according to the enhancement plan"; no new business REQ/SR was created. The status is **implemented, awaiting independent review**; the implementer does not close the review gate on its own.

- Starting full object `fea6e3f7f5749f223528a0311734e062e392a1b3`, branch `callentan-repository-skeleton`; verified to be the original App-managed isolated worktree with no superproject, 108 original tracked source files, and a clean working tree/index. The preceding commits were already done, so no empty "commit first" was made and the main checkout was not modified.
- This session modified only 12 in-scope files: the new checker and its tests, minimal line handling and field location in the shared parser, the utilities README, the development guide, the docs/tests instructions, the coupled tool notes in verify-change, plus the specification, plan, roadmap, and this log. The four schemas, the 32 kinds, dependencies, existing tests/helpers, applications, and other tools/entry points stay as they were.
- The full report is this session's `files/ddd-alignment-execution/task6-report.md`; the actual SHA of the commit for this batch is located through Git file history and the report. The Git/staging scope before and after the commit is recorded separately; an object that was uncommitted during testing is not recorded as HEAD alone.

### Actual changes and judgment boundaries

Added `run_check(root, base_sha=None)` and a standalone CLI in [check_artifacts.py](../.github/utilities/check_artifacts.py); the [usage contract](../.github/utilities/README.md#artifact-checker) registers the discovery rules, supported Markdown, placeholders, JSON, error codes, counts, and output protection. It keeps using `Artifact`, `ArtifactInputError`, canonical keys, owner acceptance, and source locations; there is no second YAML/frontmatter/acceptance parser or configuration framework.

File-name/metadata signals under the explicit root determine the formal inventory, with exact exclusions for template/native/maker/test/Git/environment directories; an ordinary lightweight guide does not pass as a formal artifact, and a `.venv` in an ancestor of root does not wrongly exclude the whole fixture. Heading/placeholder/local-link problems are `invalid`; parser, path, baseline, and report-writing problems are `input-error`; no formal artifact means `empty`, which is not a business pass.

base reads only the exact commit/tree/blob for historical comparison; the target is always the complete current working files, including unstaged/untracked formal inputs, and unchanged identity/link errors cannot be hidden. Old metadata is not subjected to new rules; no filters/textconv, source commands, or network reads are run, and main/master/HEAD/staged content is not guessed. The report records the raw bytes and the actual read set; a read failure is not recorded as a deletion, and `comparison_complete` distinguishes incomplete comparisons; no index-only hook is provided.

The API does not write; by default the CLI only prints JSON and writes a report only to an explicit new `.json` path. It refuses to overwrite existing source/historical files, to create directories automatically, and to use UNC report paths; the report output is kept separate from the input hashes. `verify-change` only updates the earlier "checker not provided" note and keeps the boundaries that read-only mode runs no commands, makes no overwrites/exports, and does not certify approvals; no new method, role, prompt, or workflow was added.

### Actual result entry points

All raw execution evidence is under the authorized `files/ddd-alignment-execution/task6-evidence/` of session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; the locations below are accessible only on the local machine and are neither dependencies distributed downstream nor cross-machine CI proof.

| Record location | Object and notes |
|---|---|
| `start.json` | Actual root, branch, Git dir/common dir, starting commit/index state, and byte digests of the 108 original files |
| `red-01-missing-module.json`, `red-02-behavior.json`, `red-03-assertions.json` | First the missing module, then a real RED confirmed with an interface that has no checking behavior; after completing the preconditions of two test assertions: 52 methods, 77 assertion failures, 0 errors/skipped; source and raw stdout/stderr kept |
| `check-04-implementation.json`, `red-05-boundaries.json`, `green-06-boundaries.json` | Initially 52 methods passed; self-review found problems and reproduced them with eight new boundary cases, after which 60 methods passed: discovery with a missing delimiter/heading identity, false positives on an ordinary project, comment openers in inline code, UNC pre-rejection, and comparison completeness for unreadable files |
| `parser-01-shared-helper.json`, `parser-02-literal-comments.json` | Both bounded parser regressions ran the original 74 methods with 0 skipped; the shared extraction and the literal-comment fix did not break the old interface behavior |
| `full-01-precommit.json` | Full suite on the same final code object: 204 methods discovered/run, 361 subtests, 0 skipped/failures/errors, 24.468 seconds, exit 0; the original 74 parser + 70 schema/Git data + 60 new checker tests; the original suite was not replaced |
| `cli-01-receipts.json`, `cli-01-execution.json`, `cli-01/` | 9 real CLI runs: positive case, bad file, empty skeleton, exact base/re-run, invalid/symbolic base, wrong root type, old-report protection; each saves arguments/cwd/stdout/stderr/exit code and before/after source byte digests, with explicit reports listed separately |
| `check14-zero-*`, `check14-skipped-*` | Evidence gate verified in practice: zero discovered and all skipped are rejected. With zero discovered, the current Python 3.13 native CLI actually exits 5 (the observation that initially expected 0 is kept), whereas a real API runner that only uses `wasSuccessful()` exits 0 on zero discovered; the count gate still rejects it, and no self-proving product test was added |
| `worktree-01-receipts.json` | On the current real worktree, both full and base are empty: 0 formal artifacts, 40 excluded entries, 17 digests of actually read Markdown files; the bytes of 110 source files and the Git state were identical before and after both checks. That object predates this log's appended section and cannot serve as the final log byte digest |
| `syntax-01.json`, `dependencies-01.json` | compileall and pip check with the existing Python exited 0; the compile cache was explicitly written to the authorized evidence directory; no new install and no lock change |

The commands and gate entry points are used only for this authorized run; test code and the expected cases themselves are not run evidence. The raw records keep the distinct objects/stages of failures and successes; the initial missing module and the naive runner's exit 0 are not treated as a functional/regression pass. Read the final scope, self-review, document links, commit, and post-commit state from the full report.

### Limitations, items not run, and next steps

- The real run host was Windows, Python 3.13.15, with the existing PyYAML 6.0.2/jsonschema 4.23.0; real local SHA-1/SHA-256 Git, byte locks, and junctions were used. The minimum Python 3.11, other OSes, and all file systems/permission policies have not been verified in practice and are not inferred from the current success.
- Non-enumerable directories and some unreadable comparison paths use explicit OS-boundary injection; the UNC tests block resolution locally to guarantee no network access, and no ACL was modified. The real file byte lock was also actually exercised. The path checks are not OS isolation against concurrent malicious replacement.
- Markdown is the registered bounded syntax, not a complete renderer; ordinary guides, cross-file canonical coverage/hierarchy/semantics, and model export are not part of Task6. Open business facts are explicitly kept; Task5's two synthetic uncovered targets, the applicability of old results, and the `not-run` of business/software VTs were not upgraded.
- No subagent/independent reviewer, Task7, source onboarding, application, Gherkin runner, hooks/CI, media/PDF, platform, push, or PR was started; no dependency was installed and no permission changed. The method notes only received the directly coupled update about the available tool; no new independent agent stress test or reliability conclusion is claimed.
- Next, the caller independently checks this session's commit, the 12-file diff, the full report, and each piece of raw evidence; whoever takes over first checks the current working tree/index and whether the local evidence is readable. Task6 awaits that review; this execution stops after the local commit and report; the not-run gates of Task7–18 and the original P3 remain as they were.

<a id="pause-task6"></a>
## User pause and resume point

On 2026-10-15, the user asked: "Pause for now and save the state. I will continue in real time." Enhancement execution is paused, and later tasks are not advanced automatically. The bounded-scope gates of Task1–5 are closed; Task6's implementation commit is `b8d4f826db142de052038288f938d90b1581020e`, and **the independent review found two Important issues; fix round 1 is not yet closed**:

- For an artifact without a formal-ID file name/H1, an extra space in the opening delimiter can cause obvious metadata to be treated as an ordinary guide, so the artifact is missed.
- A `<!--` in a code fence's info string corrupts the body comment state, which can still hide broken links and real owner acceptance criteria after the fence closes.

The full read-only review is saved in `files/ddd-alignment-execution/task6-review-findings.md` of local session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; the original implementation and the appended fix/pause information are in `task6-report.md`, and the execution ledger is `progress.md` in the same directory. The parent session verified both code mechanisms and did not pass off static analysis as a new execution reproduction. The 204-test regression result on the original implementation object is kept and cannot prove that these two new scenarios are fixed.

Read-only Git observation at 18:19:55 +08:00: branch `callentan-repository-skeleton`, HEAD still the `b8d4f826` above; only the two tooling test files `test_artifact_check.py` and `test_artifact_io.py` have unstaged changes, with no staged/untracked paths. This pause record is a log change added afterwards; the unfinished tests were not committed to save the state, and no owner content was rolled back. The executor has received the instruction to stop new implementation, tests, and commits; its final pause report has not yet been received, and the commands already started and their RED results cannot be pre-filled here.

When resuming, first re-check Git, the two test changes, the latest pause section of the full report, and the actual evidence; continue the same fix round, and do a bounded review only after obtaining real reproduction/fix results; do not redo Task1–5. Task7's optional source entry point still awaits the user's choice: `model-sources.yaml` or explicit command/API input each time; this time the user only asked to pause and did not approve the recommended option. A later completion notice from the executor only supplements the pause state and does not automatically resume implementation or review.

**Pause confirmation addendum:** The executor has stopped, its tool status is idle, all commands it started have finished, and there is no new commit or production code change. The latest handoff is in section 10, `task6-fix1-paused`, of `task6-report.md`; `task6-evidence/red-fix1-01.json` stores the real RED completed before the pause: 143 methods, 26 failures, 0 errors/skipped. The two test files add 9 methods that reproduce both missed detections; this is not a passing fix, and the next steps remain the bounded production fix, GREEN, and independent review. This addendum only saves that state and does not resume execution; the unstaged changes to the two test files and this log are currently kept.

<a id="resume-task6"></a>
## Task6 fix round resumed

At 2026-10-15 20:16 +08:00, the user explicitly asked to "resume execution". Actual Git was re-checked: HEAD still `b8d4f826db142de052038288f938d90b1581020e`, branch `callentan-repository-skeleton`; the index was empty, and the unstaged scope was still only the two tooling test files and this log. The raw byte digests of the two test files match `red-fix1-01.json`, and the digests of the two production modules match the original implementation record; content from the pause period was not treated as a new fix.

This session continues fix round 1 on the two reproduced missed detections, keeping the pause record and the original RED, without redoing Task1–5. After the bounded fix, new results for the affected modules and an independent review must still be obtained; the old 204-test result does not automatically apply to the fixed object. The choice of Task7's source entry point has not been answered yet, and the resume instruction does not mean adopting the recommended list; the separate authorization boundaries for applications, platforms, and release are unchanged.

<a id="task6-fix1"></a>
## Task6 fix round 1: resuming from the saved RED

### Session, task, and Git

On 2026-10-15, the same fix round continued per the user's "resume execution" and the local `task6-fix1-resume-brief.md`; the basis is [Task6 / ENH-07](../docs/plan/2026-10-14-ddd-functional-alignment.md#task6) and the full review with its two Important findings. At resume time the branch was `callentan-repository-skeleton`, HEAD `b8d4f826db142de052038288f938d90b1581020e`, and the index was empty.

The pre-existing unstaged content was the two tooling test files and this log. The 9 new test methods come from the RED before the pause, and this execution did not rewrite the tests; this log's `pause-task6`, the pause confirmation, and `resume-task6` are the parent session's existing content for the same task, kept and included in the bounded commit, and not counted as this execution's implementation. The new resume snapshot protected this newer log prefix and did not reuse the old starting point that predates the pause record.

### Changes in this session

- The [checker](../.github/utilities/check_artifacts.py) changes only `_formal`: a recognizable but invalid delimiter on the first line no longer ends the metadata prefix early; actual syntax acceptance/rejection is still decided by the original parser. Fields in ordinary body text, code, and comments do not become part of the formal inventory as a result.
- The [shared parser](../.github/utilities/artifact_io.py) changes only `iter_markdown_lines`: it first checks the comment state before a fence, uses the raw info string to decide whether the fence is valid, and does not let the fence info or content open a body comment; actual body comments, code exclusion, and source line numbers are preserved.
- The [tool notes](../.github/utilities/README.md#checker-discovery) add the boundaries above; the [plan](../docs/plan/2026-10-14-ddd-functional-alignment.md#task6) distinguishes the original implementation result, this round's regression, and the still-open review gate. No new module, schema, dependency, model diagram, or business artifact.

### Actual result entry points

The full appended report is in section 11 of `files/ddd-alignment-execution/task6-report.md` in local session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; this section and the fix are saved with the new scoped commit; check the actual commit, file list, commands/cwd, output, and byte digests against that report and Git. The report is accessible only on the local machine and is not distributed cross-machine evidence.

`task6-evidence` in the same directory keeps the original `red-fix1-01.json` and adds `fix1-resume-start.json`, `green-fix1-resume-discovery.json`, `fix1-resume-before-green.json`, and `green-fix1-resume-01.json`. The discovery fix first ran 2 existing methods; the actual focused run of `test_artifact*.py` then gave 143 discovered/run (checker 65, parser 78), 173 subtests, 0 failures/errors/skipped, test subprocess exit 0, 47.530 seconds. The bytes of all 110 source paths were identical before and after the tests; the original test bytes, the 80 earlier evidence files, and the parent session's log/original report prefixes were all preserved. The subsequent self-review and post-commit check are located by `fix1-resume-review.json` and `fix1-resume-post.json` respectively.

This is a real-file, Git, and CLI regression of the maintenance tools, not business acceptance. The historical 204 methods and other results in the original report keep their original baseline; this round did not re-run the unchanged schema tests or the full suite, and did not upgrade the old pass into a pass of the fix.

### Limitations and next steps

- Verified in practice on local Windows / Python 3.13.15; Python 3.11 and other hosts have still not been run, and cross-host compatibility is not inferred. The 9 saved test methods gained no assertions and had none weakened; their source bytes match the pre-pause RED.
- Both fixes await the caller's bounded review; the executor did not close the Important findings or the independent gate itself. Whoever takes over first checks the new commit, the actual diff, the latest report, and evidence accessibility; do not blindly replay the scope assumptions of the old audit.
- Task7's source entry point still awaits the user's choice; this round did not choose `model-sources.yaml` or an alternative entry point; Task7–18, applications, hooks/CI, platforms, and release remain not run. No subagents, workflows, new worktrees, installs, permission changes, pushes, or PRs; work stops after the bounded local commit and the appended report.

<a id="task6-review"></a>
## Task6 round-1 bounded review and source entry-point decision

The parent session checked the complete seven-file bounded diff from `b8d4f826db142de052038288f938d90b1581020e` to `e0b9fae75a4ea07176e36e4b5b776887ab2a893c`: the selection/state boundaries of the two production functions, the nine retained failing cases, and the related notes. Both Important findings were addressed, and no major issue introduced by this fix was found; this is a bounded review done directly by the coordinator, not implementer self-review, and no duplicate review task was started. The actual commit/parent/trailer and the clean working tree/index were re-checked.

The local session's `files/ddd-alignment-execution/task6-fix1-review-result.md` stores the item-by-item basis; `task6-fix1-parent-tests.json` stores the exact command, cwd, and raw output of the parent session's independent run at `e0b9fae`: `test_artifact*.py` discovered and ran 143 methods, 0 skipped, exit 0, 43.040 seconds. The new results for the two modules do not replace the historical baseline of the original full 204-test suite, and they do not claim that Python 3.11, other hosts, or business behavior have been verified. The full report is still accessible only on the local machine.

Task6's implementation/scope review gate for this session is closed. After resuming, the user also separately chose "Use the optional model-sources.yaml source manifest (recommended)"; the executor in the previous section did not receive this later decision, and its "still awaiting choice" is the starting context, not the current open status. Task7 will accordingly register source paths and pinned baselines, without copying body text, results, or approval status; the formal source manifest, model export, and coverage tools have not yet been created, and no external read/write permission is granted.

This update syncs the current status of the specification, plan, and roadmap and keeps all old observations. The old Task8 sketch in the plan was also aligned with the implemented report schema as `entries[].execution` / `evidenceRefs`; no global result field was added, and no claim is made that Task8 has run. The next step continues with [Task7](../docs/plan/2026-10-14-ddd-functional-alignment.md#task7); the application, platform, and release gates are unchanged.

<a id="task7"></a>
## Task7: complete coverage, impact candidates, and the nine-view model

### Session, scope, and Git

Under the user's original execution authorization, "resume execution", and the separately chosen optional `model-sources.yaml`, only [Task7 / ENH-06, ENH-08](../docs/plan/2026-10-14-ddd-functional-alignment.md#task7) was implemented. The starting point was `def03cdc0f58414eeb4d59da61928d451b431aaa`, branch `callentan-repository-skeleton`, in the existing App-isolated worktree, with the index and working tree both clean at the start; there was no need to repeat the initial commit or the Task6 fix. The status is **implemented, awaiting independent review**; the implementer does not close the independent gate.

### Changes in this session

- Added a [source schema](../.github/contracts/model-sources.schema.json) and a [blank form](../_templates/config/model-sources.yaml); the manifest stores only view paths/pinned baselines under multiple explicit scopes. The original four schemas, 32 kinds, nine-view output, and the 8/21/3 counts of methods/entry points/modes are unchanged; no formal project manifest was created.
- The [coverage/impact tool](../.github/utilities/check_traceability.py) reads the complete actual inventory, distinguishes explicit deliveries from context, and reverse-looks-up all targets, the original owners' AC/VC, body hierarchy, and independent criteria. The old and new dependency graphs for an exact base keep deleted/removed references and produce candidates with source locations, without changing rules or results.
- The [model tool](../.github/utilities/export_model.py) references real Markdown or existing summaries and keeps scope-qualified refs, evidence paths/pinned baselines, and concrete gaps. YAML/evidence/manifests all enter the source identity; a missing primary input fails, while a missing optional source keeps the fixed view. Checking recomputes without repairing, and explicit output neither overwrites existing files nor occupies registered source paths.
- The parser/checker only factored out the shared already-read inventory, raw YAML mapping/historical blob parsing, and protected output; Task6's fence/comment handling and all original tests are kept. The actual contracts, the tooling/development/domain/verification/architecture guides, and the tool entry point of the verify method were updated; no method was rewritten and no agent flow was added.

### Actual evidence entry points

The full report and the actual post-commit state are in `files/ddd-alignment-execution/task7-report.md` of local session `1ff56941-bf56-4aa4-b769-fd4720915e1f`. The new receipts, helper scripts, and retained synthetic sources are only in `task7-evidence` in the same directory, and the transient unit-test fixtures are only in the repository-ignored `.venv`. These entry points are accessible only on the local machine and are not distributed cross-machine evidence.

- `baseline-213.json`: a **fresh run** of 213 methods at the starting point, 0 skipped, exit 0; Task6's old full-suite result was not used as this session's baseline.
- `manifest-red*.json` / `manifest-green.json`, `trace-impact-red.json` / `trace-impact-green.json`, `model-red.json` / `model-first-green.json`: independent expectations and actual failures came first, then implementation and re-runs. Initially 10 methods for the source schema, 25 for coverage/impact, and 28 for export; not a syntax-only check or an invented baseline.
- `self-review-boundaries-red.json` and each focused `*-green.json`: after self-review reproduced them, boundaries such as source merging, field completeness, cross-scope/nested evidence location, a single schema read point, and output conflicts were fixed; real failures are kept, and a first failed run is not recorded as GREEN.
- `final-full-suite.json`: the complete retained and new suites actually discovered/ran **293 methods**, 0 failures, 0 errors, 0 skipped, exit 0, 106.635 seconds; this includes the original schema 70, parser 78, and checker 65, plus Task7 trace 27 and model/manifest 53. The commands/cwd/stdout/stderr and per-source before/after byte digests are in that receipt; repository input bytes did not change during the tests.
- `observations/observations.json` and `outputs` in the same directory: keep the source files/old and new Git identities for the real four deliveries, the omitted software-only rejection, and the rule change 2→3, plus the nine-view model, the check, and the manually edited copy. The omitted item is exactly `sample/CTX-001/SR-001#sr-001-ac-02`; the two owner files were not deleted or changed, and the single rule change traced to five candidates: REQ/SR/two VTs/task. The actual CLIs of the two scripts each observed 0/1/2, and the input and old output bytes stayed unchanged.

This is behavioral verification of the local maintenance tools, not execution of business or software VTs. Check the full results, the tests corresponding to the 19 input cases, the self-review, and the commit list against the report/receipts; the log does not maintain a separate acceptance result table.

### Limitations and stopping point

- Verified in practice on Windows / Python 3.13.15; Python 3.11, other hosts, and larger real projects were not run. I/O fault injection is explicitly marked in the tests and does not pose as an actual permission configuration.
- The coverage criteria and the direct Markdown/summary adaptation are documented mechanical structure checks; they do not prove that natural-language criteria are sufficient, that risk is acceptable, or that approvals are real or published. Only actual canonical dependencies are handled; implicit semantics/lightweight links still need checking by the accountable owner. Reading is not a file-system transaction.
- No independent reviewer/agent stress test, Task8–18, application/Gherkin, hooks/CI, media, or platform/remote operations were run; no dependency installs, permission changes, amend, push, or PR. The implementation-report fields are still empty, and no Task8 collector was created.
- This session stops after the in-scope local commit and report. Next, the caller checks the exact commit, the 20-file scope, the raw evidence, and the complete source contract, and then decides on the Task7 independent review; complete functional equivalence cannot be inferred from a partial GREEN.

<a id="task7-fix1"></a>
## Task7 fix round 1: five Important findings

### Starting point and scope

The user authorized handling T7-I1–I5 in one round. Neither the independent review nor the parent session's mechanism check claimed a new run reproduction; this round started from a clean `fe1acd39e1e25025d037e0c072e437824e848911` in the same `callentan-repository-skeleton` worktree, first actually reproduced the issues, and then fixed them. Only the two tools, the necessary shared Markdown reading, the related tests/contracts/tool notes, and the current status were modified; the four original schemas, 32 kinds, nine views, and 8/21/3 are unchanged.

### Actual fixes and protection of the original assertions

- T7-I1: a direct quality view requires both verifiable QAS and a real utility-tree source/baseline; a missing source yields unverified with refs cleared, while an existing source with missing fields/entries is still partial. Adding one actual tree file to the original missing-measure fixture only isolates the missing-field condition; the original partial and responseMeasure assertions are unchanged; the missing-tree case has its own new RED, and no kind or production tree data was created.
- T7-I2: all nested locations of the selected resolved source documents are registered before dereferencing, so a missing/failed earlier item does not cause later items to be skipped; when a declaration cannot be registered safely, the read-only path can still report a gap, but output is refused, without falsely claiming that isolation is complete. A valid new model can be exported/checked as is, and old output is not overwritten.
- T7-I3: body text and closed code fences reuse the same comment/fence state machine, and the diagram check accepts only code blocks that actually belong to `diagram`. Comments, outer literals, unclosed blocks, or ordinary notes cannot stand in for a diagram; Task6's old fence/comment tests are kept.
- T7-I4: this owner's run sub-blocks and per-criterion multi-column tables are read from the real VT `runs` section, and each record is checked separately for explicit counts, date, notes, and baseline. `section_lines` is not relaxed, counts are not inferred from totals, and blocks are not stitched together; conflicting results on the same baseline keep the references on both sides plus a gap.
- T7-I5: the public `impact_report(root, None, task_ids)` returns INVALID_BASE/input-error directly, without going through the test helper's default base and without degrading into a clean empty comparison.

### Actual result entry points

fix1 is appended to the local session's `files/ddd-alignment-execution/task7-report.md`; the original report prefix and original evidence are kept. New receipts/helpers/retained samples use only `task7-evidence/fix1-*` names; transient test fixtures are still only in the ignored `.venv`. This is local evidence and is not distributed with the template.

- `fix1-start.json` records the clean starting point, 116 source files, 123 old evidence files, and digests of the original report/log prefixes.
- `fix1-all-red.json`: only tests were changed first, with production code still at the starting point; 18 methods, 20 failing subtests, 0 errors/skipped; all five issues were actually reproduced. The erroneous creation for I2 happened inside its own temporary input, not in production sources. The old 293-method result was not relabeled as this round's baseline.
- `fix1-i1-green.json`, `fix1-i2-green.json`, `fix1-i3-green.json`, `fix1-i4-green.json`, `fix1-i5-green.json` record the targeted GREEN for 8/6/10/9/7 methods respectively, including the corresponding normal/missing-item/isolation controls and the retained Task6 cases. The later supplementary RED/GREEN for unsafe locations is in `fix1-reservation-boundary-*.json`.
- `fix1-full-suite.json`: this round ran the complete retained + new suite only once, actually discovering/running **313 methods**, 0 failures, 0 errors, 0 skipped, exit 0, 105.466 seconds. The full commands/cwd/stdout/stderr and before/after source bytes are in the receipt; the bytes of the tools under test, tests, and schemas were re-checked before and after the commit and not substituted by syntax checks or old results.
- `fix1-observations/results.json` keeps eight new groups of source/result observations covering all five items: QAS with a missing/real tree, the actual CLI refusal for a later missing nested location, comment/outer literal/real diagram, the owned run tables, and a None base compared with a real exact Git base. All record input digests before and after tool execution; the run tables are only supplied synthetic source records, not a business/software execution.

### Limitations and stopping point

This round's self-review and tests do not close the review gate; Task7 remains **awaiting bounded review**. Verified in practice on Windows / Python 3.13.15; no claim is made that Python 3.11, other hosts, natural-language semantics, human approval, or business execution have been verified. A read-only source state is not pass/approval/release; Task8–18 were not implemented, and there were no reviewers/subagents/workflows, installs, permission changes, hook installs, remote operations, amend, push, or PR. Work stops after the new scoped commit and the report addendum; the caller checks the five fixes, the full diff, and the protection of new and old evidence.

<a id="task7-fix2"></a>
## Task7 fix round 2 (scoped): new F1-N1

On 2026-10-16, per the user's bounded request, work started from a clean `d622b14ed8a564a5ad11b28514ff9b41b484d4b8`. The fix1 bounded review had marked the original T7-I1–I5 as addressed; this round handles only the new Important F1-N1 and does not reopen the original five. The reviewer and the parent session gave only the static mechanism; the following is this round's new run evidence.

- First, in the original positive case, only `### VT-002-RUN-01` was changed to `## VT-002-RUN-01`, with the complete table/criteria unchanged and that source's baseline refreshed. `fix2-red.json` actually reproduced the wrong available; six focused methods showed six failing assertions/subtests, 0 errors/skipped. At that point only `test_model_export.py` had been changed.
- The production change is only in `_owned_runs`: an anchor is associated with the real heading that immediately follows it; the owning `runs` H2 must be established before lower-level headings are accepted; a peer/ancestor heading ends it immediately, and its preceding anchor cannot be accepted first. Blank lines/comments keep the association, while prose, code, or another anchor breaks an unpaired association. `section_lines`, the raw parser, and the shared literal scanner were not modified.
- `fix2-focused-green.json`: six new methods and seven retained run-record controls, 13 methods GREEN in total. Covers the single H2 change, an H1 ancestor, a valid H3, isolation of a subsequent peer/external section, and unpaired anchors; the original MULTIPLE_TITLES input error for H1 is still kept. Actual input bytes were checked before and after every tool call.
- `fix2-model-suite.json`: only the whole `test_model_export.py` selector was run, actually discovering/running **77 methods**, 0 failures, 0 errors, 0 skipped, exit 0, 40.500 seconds. The old 313-test full suite, the parent session's 243 methods, and the separate schema suite were not re-run or relabeled.

New evidence and helper scripts are saved only in the local session's `files/ddd-alignment-execution/task7-evidence/fix2-*`, and the fix2 addendum to the original report is in `task7-report.md`; the starting-point digest stores 116 source files, 266 old evidence files, and the original log/report prefixes. These results are scoped verification of the tool and source structure, not business execution or independent approval.

Task7 remains **awaiting bounded review**. This round changed only that function, the same model test file, the directly related contract notes, and the current status/this log; the four original schemas, 32 kinds, nine views, and 8/21/3 are unchanged. Work stops after the new scoped commit and the report addendum; no subagent, Task8, application, installs, permission/hook configuration, amend, push, PR, or remote operations.

<a id="task7-review"></a>
## Task7 review closed

On 2026-10-16, the parent session directly read the complete seven-file scoped diff from `d622b14ed8a564a5ad11b28514ff9b41b484d4b8` to `23c06b6bc46099c04091c61c036016b88cf4ae99` and checked the anchor/real-heading pairing in `_owned_runs`, the peer/ancestor cutoff, and the six new controls. F1-N1 is addressed, and no major issue introduced by this fix was found; the original T7-I1–I5 keep the addressed judgment from the previous round's independent review, and the original full review was not repeated. The actual head/parent/trailer, the seven-path scope, and the clean working tree/index were re-checked.

The local session's `files/ddd-alignment-execution/task7-fix2-review-result.md` stores this round's item-by-item basis; `task7-fix2-parent-tests.json` stores the parent session's actual project interpreter, cwd, `test_model_export.py`, and raw output at `23c06b6`: 77 methods, 0 skipped, exit 0, 48.748 seconds. Earlier, `task7-fix1-review-result.md` and `task7-fix1-parent-tests.json` stored the five judgments/new issue and the 243-method result on `d622b14e`, respectively. These different objects and scopes are not combined into one new full-suite pass; the old RED/reports are still kept.

Task7's bounded implementation and scope review gate is closed, with no outstanding review findings for this task; this is not a pass of the enhancement as a whole, of real business execution, or of cross-host qualification. This update only syncs the specification, plan, roadmap, and this log. The next step, under the existing authorization, handles Task8's implementation-summary bridge; real results still belong to VTs/raw reports and cannot be inferred from model availability, commits, or the existence of test files.

<a id="task8"></a>
## Task8: collecting a read-only implementation summary from existing owned VT records

### 2026-10-16: task, Git, and boundaries

Under the original execution authorization, "resume execution", and the user's separate choice "Directly reuse existing VT run records (recommended)", only [Task8 / ENH-12](../docs/plan/2026-10-14-ddd-functional-alignment.md#task8) was implemented. The starting point was `d30b87b805a133bca54d25ce5887e06071e605c1`, branch `callentan-repository-skeleton`, in the existing App-isolated worktree; the working tree/index were both clean at the start. Task7's two fix rounds and its review-closure conclusion are kept, and its review was not redone.

Before this section was written, the index was checked again and was empty; the uncommitted content belongs only to this round's tools, tests, forms, and direct documentation navigation. The actual object of the scoped commit and the post-commit state are as given in the final addendum of `files/ddd-alignment-execution/task8-report.md` in local session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; the commit's own SHA is not invented before the commit. That report and its receipts are accessible only on the local machine, and whoever takes over must obtain that session's material.

### Changes in this session

- The [collector](../.github/utilities/collect_implementation_report.py) reads the BC, acceptance, code, and test text from an explicit commit, and separately reads the VT owned runs/raw reports appended later. scope, owner, criterion, the object/requirement/plan baselines, and source markers must all actually match; without a record each target stays not-run, conflicts fail, and no separate execution-input ledger is created.
- The [shared VT reader](../.github/utilities/vt_records.py) narrowly extracts the original owned-run/four-column result reading, keeping H3 ownership and closure by H2/H1, comments/fences, and strict section isolation; the safe Git/pinned-bytes checks remain shared from the original module. Self-review then used RED/GREEN to cover shared criteria, applicability-table isolation, Unicode line boundaries, and declared-source protection.
- The [model bridge](../.github/utilities/export_model.py) uses the existing verification source selection, validates the report's schema/scope/baseline and reproducibility, and adds only a report reference. The remaining canonical/evidence/baseline data and the nine-view gaps are kept; entries/execution/applicability are not copied, and no new model is written to the domain sources.
- The [blank report form](../_templates/reports/implementation-report.yaml), [field contract](../.github/contracts/README.md#implementation-report), [usage entry point](../.github/utilities/README.md#implementation-report), the development/BC/verification notes, and direct handoff navigation were completed. The five schemas, 32 kinds, nine views, and 8/21/3 were not extended; no real business BC/config/model/VT/application was written to production directories.

### Actual result entry points

This round's raw evidence is in the same session's `files/ddd-alignment-execution/task8-evidence/`. The JSON files store the real interpreter, argument list, cwd, stdout/stderr, exit, discovered/run/skipped counts, and the checked input bytes; they are not a business result table reconstructed from the log.

- `baseline-retained.json`: 319 methods actually run at this round's starting point, 0 skipped, exit 0. The dates, scopes, and objects of the old 313/243/77 results are kept and not relabeled.
- `red-01/02` to `green-10`: first the missing-collector RED, then verification of per-target collection and the model bridge. One failure where the installed fixture omitted the shared reader, and its fix, are kept; nothing was unblocked by deleting tests. The pass/fail values in synthetic sources are only input, and text fixtures do not run an application.
- `full-11-retained-new.json`: the full 373-method suite passed at that time; the final self-review added five more controls, so this result cannot substitute for the new object.
- `red-12-final-boundaries.json`, `red-13-shared-criterion.json`, `green-14-final-boundaries.json`: reproduced with actual files and fixed writes into declared source directories, shared criteria, literal isolation of applicability, Unicode projection, and the wrong evidence collection shape. The fixture's line-ending fix and the product defects are recorded separately.
- `full-17-final-retained-new.json`: **378 methods actually discovered/run, 0 failures, 0 errors, 0 skipped, exit 0, 386.857 seconds**; the checked input bytes did not change. `retained-inventory-comparison.json` confirms that all 319 original test identities are kept and 59 were added; the final suite contains contract 70, parser 78, checker 65, trace 29, model 86, collector 50.
- Document/scope checks and protection of the original log and report prefixes are in `check-16-docs-scope.json` and the report's final-check addendum. The helper script initially did not preserve the checkout's CRLF semantics; its failure keeps the original output, and only the helper script's arguments were fixed, without changing repository configuration. The formal artifact check is still empty/0, which is not a business pass.

### Gaps and next steps

Task8's status is **implemented and locally verified, awaiting independent review**. Verified in practice on Windows/Python 3.13.15; Python 3.11, other hosts, human identity/approval, and real business execution are not certified by this. A bounded, explicit field/selector/marker syntax is supported; general import of historical records is not promised, and the tool cannot certify that external events actually happened. One raw-report I/O refusal control uses narrow boundary injection and does not pose as host ACL verification.

No subagents/reviewers/workflows, new worktrees, installs, permission or hook/CI configuration, amend, push, PR, application, remote, or Task9–18 operations. Work stops after the new scoped commit and report; next, the caller should check the exact commit, the source diff, the full-suite receipt, the read-only protection, and report accessibility, and then run the independent review. The not-run gates of the original P3 and later tasks remain as they were.

<a id="task8-fix1"></a>
## Task8 bounded fix round 1 (1/5): T8-I1, T8-I2, T8-I3

On 2026-10-16, per the user's bounded request for this round, work started from a clean `7f747e55e480b92822c5599d1e9f54dccba98d9d` on the original `callentan-repository-skeleton` branch. The independent review/parent session supplied static counterexamples without a new run reproduction; this round first wrote real file/Git/CLI tests and then changed production code, and it did not treat the previous round's 378-method record as verification of these three counterexamples.

### Scope and fixes

- T8-I1: only the [declared-location registration](../.github/utilities/export_model.py) was adjusted. Protection of root/path is separated from whether the baseline exists/is valid; an incomplete or unparsable domainSources declaration blocks explicit output, while the default optional read still keeps a gap. Parsable locations continue to protect their subpaths; a YAML alias does not lose the declaration context.
- T8-I2: only in [run collection](../.github/utilities/collect_implementation_report.py), after the existing per-target/criterion checks, the distinct testIds of pass/fail rows are used to check the lower bound of the recorded executed count. One test covering several independent criteria is counted once, and additional actual executions may be kept; counts are not inferred from command text, manual, skipped, or not-run.
- T8-I3: only in the [plan projection](../.github/utilities/vt_records.py), before subtrees are excluded, the real body anchors of all declared criteria are checked; a criterion located in the excluded runs/applicability area fails explicitly, so a modified criterion cannot pass as the old plan. The original heading ownership, strict criterion boundaries, and Unicode/BOM/CRLF bytes are preserved.
- Tests were added only to the two existing collector/model modules; the directly related documents only clarify these three rules and sync the current status. The five schemas, 32 kinds, nine views, and 8/21/3 are unchanged; there is no new result-input ledger.

### Actual evidence entry points

This round's full report is appended to `files/ddd-alignment-execution/task8-report.md` in local session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; all new receipts are in its `task8-evidence/fix1-*`. This material is accessible only on the local machine and is not a downstream runtime dependency.

- `fix1-before.json` stores the identities of 120 source files, 1305 old task materials, and this report's/the original log's prefixes.
- `fix1-red-01-all-findings.json`: with production code unchanged, 16 methods, 18 failing assertions/subtests, 0 errors/skipped, exit 1. `fix1-red-verified.json` confirms that the three production files still equal the starting point and that I3 was not masked by another guard.
- `fix1-red-02-i1-files.json`: 6 methods, 13 failing assertions/subtests; it was explicitly observed that files that should not have been created were actually written into the controlled fixture; an alias-context control was added. The tests clean up only their own erroneous output and did not write to real domain sources.
- `fix1-green-03-i1.json`, `fix1-green-04-i2.json`, `fix1-green-05-i3.json`: the three focused groups passed 6, 6, and 5 methods respectively, 0 skipped, exit 0; all check input bytes/file sets.
- `fix1-full-06-retained-new.json`: the complete retained+new suite actually discovered/ran **395 methods**, 0 failures, 0 errors, 0 skipped, exit 0, 460.423 seconds; the checked source bytes did not change. The original 378-test result keeps its original object, and the new result is not combined with the old 319/373/378 results or Task7's historical results.
- For the final scope, link/syntax, old-material, and post-commit byte checks, and for the new commit SHA, see the final addendum of the full report above; the commit's own SHA is not pre-filled before the commit.

### Gate and follow-up

This round's local fixes and verification are not independent approval; Task8 remains **awaiting bounded review**. The synthetic VT records verify only the collection/ownership/refusal paths and do not prove external business events or human approval; verification in practice is still limited to Windows/Python 3.13.15, and other hosts and Python 3.11 were not run.

No subagents, reviewers, workflows, Task9, application/native business tests, installs, permission/persistent hook configuration, amend, push, PR, or remote operations were started. Work stops after the new in-scope local commit and report; the caller checks this round's exact commit, the three mechanisms, all new raw evidence, and the protection of old records, and then does the bounded review.

<a id="task8-fix2"></a>
## Task8 bounded fix round 2 (2/5): T8-F1-N1

On 2026-10-16, per this round's bounded request, work started from a clean `062e607cde5cd5ecb2a0b2d83bff60ab2940c867` on the original branch/worktree. The round-1 bounded review had judged the original T8-I1/I2/I3 as **ADDRESSED**, and this round does not reopen them; it handles only the new Important finding that the root/path of a business tree was mistaken for a domain location, causing valid output to be refused. This new counterexample in the review is a static trace; the following is new run evidence.

- First only `test_model_export.py` was changed, reusing the existing complete QAS/utility-tree fixture, writing the mapping/list data given in the review, and refreshing the actual baseline. A string business-label control was also added to confirm that no false protected directory is produced. Both cases were checked with a real CLI export-and-check round trip; apart from the explicit new output, all source bytes/file sets stayed unchanged.
- `fix2-red-01-tree-roundtrip.json`: with production code unchanged, 2 methods failed: the actual read-only quality was available, but the valid output was refused with `REPORT_CONFLICT` / 2; 0 errors/skipped.
- The production change is only one condition and its comment in [reserve_declarations](../.github/utilities/export_model.py): the special protection for a missing baseline still applies in the context of real domainSources entries; other nodes return to the existing provenance shape requirement of a complete root/path/baseline, and directories are not guessed from two business keys. The tree keys were not disabled/renamed, the tree adapter and I1's missing/incomplete/alias/directory protections were not changed, and the reference/path+baseline handling was not changed.
- `fix2-green-02-tree-roundtrip.json`: 2 methods GREEN, 0 skipped, exit 0, 3.580 seconds.
- `fix2-model-03-complete.json`: only the whole model module was selected, actually discovering/running **94 methods**, 0 failures/errors/skipped, exit 0, 160.163 seconds; the checked source bytes did not change. All 92 original model tests are kept, and 2 were added; the 395-test full suite and the collector suite were not re-run.

The new material is in `files/ddd-alignment-execution/task8-evidence/fix2-*` of local session `1ff56941-bf56-4aa4-b769-fd4720915e1f`; the full report is appended to `task8-report.md` in the same place. `fix2-before.json` stores the identities of 120 source files, 1322 old task materials, and the original report/log prefixes. The old 395-test full suite and the parent session's 153-method run at the starting point keep their original scopes and objects and are not counted as execution evidence for this new counterexample.

This round changed only one production mechanism, the same model test file, the directly related contract notes, and the minimal status/log. The schemas, 32 kinds, nine views, and 8/21/3 are unchanged; the original I1/I2/I3 addressed judgment is kept, and Task8 is still **awaiting bounded review**. For the actual new commit and post-commit state, see the final addendum of the full report.

No subagents/reviewers, Task9, application/native execution, installs, persistent permission/hook changes, amend, push, PR, or remote operations. Verified in practice only on Windows/Python 3.13.15; readable/exportable sources do not certify business results, human approval, or cross-host qualification. Work stops after the scoped commit and handoff; the caller continues with the bounded review.

<a id="task8-review"></a>
## Task8 review closed

On 2026-10-16, the parent session directly checked the complete seven-file scoped diff from `062e607cde5cd5ecb2a0b2d83bff60ab2940c867` to `9a3055acf51bcebab9f2a833b91c577a0c1cae49`, the two real round-trip controls, and the report addendum. T8-F1-N1 is addressed: the protection for a missing baseline is still driven by the real domainSources context, and an ordinary business root/path no longer wrongly declares a path; the original domain-location, alias, directory, and reference protections are kept. No major issue introduced by this fix was found, and the original T8-I1/I2/I3 keep the previous round's addressed judgment.

The local session's `files/ddd-alignment-execution/task8-fix2-review-result.md` stores this round's review basis; `task8-fix2-parent-tests.json` stores the parent session's actual interpreter, cwd, and raw model-module output at `9a3055a`: 94 methods, 0 skipped, exit 0, 157.340 seconds. The previous round's three judgments and the new issue are in `task8-fix1-review-result.md`, and the corresponding independent collector/model 153-method result is in `task8-fix1-parent-tests.json`. These records and the old 395-test full suite are not merged and do not replace one another's objects and scopes.

The actual head/parent/trailer, the seven committed paths, and the clean working tree/index were re-checked. Task8's bounded implementation and scope review gate is closed, with no outstanding review findings for this task; this does not certify real business execution, human approval, or other hosts. The next step, per [Task 9](../docs/plan/2026-10-14-ddd-functional-alignment.md#task9), handles the optional governance/review/tool-qualification material; the separate boundaries for applications, media, platforms, and release remain.

<a id="task9"></a>
## Task9: optional review, tool use, Intended Use, and risk references

On 2026-10-16, under this round's explicit Task9 / ENH-09 authorization, work started in the original `callentan-repository-skeleton` worktree from a clean `002ad73a18700e7c95b21a0fa7d0d84a26f453b5`, with the index and the pre-existing uncommitted scope both empty. The closed gates of Tasks 1–8 are not reopened. The basis is the [enhancement specification](../docs/design/ddd-functional-alignment.md), the [Task9 plan](../docs/plan/2026-10-14-ddd-functional-alignment.md#task9), and the existing records for DOMAIN-08, DOMAIN-20, and FRAMEWORK-03 in the pinned matrix; reference sources were not re-fetched or run.

### Changes in this round and ownership

- Added the [governance guide](../docs/governance.md), the [AI tooling notes](../docs/ai-tooling.md), and four optional blank forms: [review record](../_templates/items/review-record.md), [tool qualification/use](../_templates/items/tool-qualification.md), [Intended Use](../_templates/items/intended-use.md), and [risk control reference](../_templates/items/risk-control.md).
- Merged in only the necessary navigation in the README and the related domain/requirement/architecture/verification/log guides, plus field entry points in the existing define-requirements, verify-change, and record-handoff. The new forms stay draft; identity/content claims/real relations belong to frontmatter, and actual decisions, evaluations, current applicability, and VT results do not substitute for one another.
- The existing source interfaces are kept: the original two-column `decision` field for review, and `analysis/control/residual` plus the original risk fields for risk. No production tool, schema, dependency, prompt, role, or new-method change, and no formal governance/QMS/business instance; still 8 methods, 21 prompts, 3 modes.

### Actual checks and evidence entry points

`files/ddd-alignment-execution/task9-evidence/` of local session `1ff56941-bf56-4aa4-b769-fd4720915e1f` stores this round's raw evidence; the sibling `task9-report.md` summarizes the exact commands, cwd, source bytes, status, and final commit. Accessible only on the local machine; not public or cross-machine CI evidence.

| Evidence entry point | Object, observation, and limitations |
|---|---|
| `baseline.json`, `baseline-reading.md` | The exact clean starting point and the byte identities of 120 original files and 1353 old task materials; the existing methods' safe decisions for the 10 situations already held, and no RED was fabricated |
| `method-use.md` | Item-by-item direct application of the three method navigation points; read-only input still returns findings without executing/saving; not an independent agent, manual T17, or native permission observation |
| `run-03/provenance.json`, `case-results.json` | 10 prepared situations and 11 actually copied/filled-in forms of the four types; stores template and filled-in bytes, fields, complete identities, and concrete gaps |
| `run-03/check-filled.json`, `command-*.json` | The existing checker actually attempted/checked 13 formal synthetic records: clean; four kinds of missing confirmation metadata are reported by the parser as INVALID_METADATA; both existing output targets (source/result) refuse overwriting |
| `run-03/model-alpha.json`, `model-beta.json`, `model-unavailable.json` | An available synthetic decision governance source does not equal approval; unknown pre-mitigation/residual risk is partial, and an unavailable source is unverified; same numbers in different scopes do not mix decisions |
| `run-03/coverage-missing.json`, `optional-free.json` | A complete two-item target inventory locates the second item as UNCOVERED_ACCEPTANCE, and the VT's original not-run is not rewritten; maintenance without governance requirements has an empty inventory, which is not a business pass |
| `run-03/navigation.json`, `protected-bytes.json` | 104 candidate files and 619 local links/anchors with no gaps; no maker material/test dependencies; input and old result bytes kept, with overwrite refusals listed separately |

Fixtures are only in the ignored `.venv`, and the report and recording scripts are only in the authorized absolute session directory above. The existing Python 3.13.15, PyYAML 6.0.2, and jsonschema 4.23.0 were used; the two own synthetic inputs actually evaluated by the parser, 0 skipped, and the environment/observations are saved in the fixture's raw `sources/evaluation.json`; this is not a business test. The unrelated full Python suite was not re-run. The first two bounded runs are kept as is; later runs only refined the exercise inputs' version change, use/follow-up, and object scope, without modifying the production validator; these runs are not merged into more acceptance items, and no failing baseline was fabricated.

### Limitations and next steps

This round completed the documentation implementation and self-review; **Task9 awaits independent scope review**, and no real expert/clinical/regulatory approval, risk acceptance, or tool qualification is recorded. Synthetic named decisions only show that the fields/navigation are usable; actual confirmation, organizational policy, external risk sources, manual T17, client/OS permissions, and business applications were not verified. The current Markdown rules do not become an ACL or sandbox.

This round authorized only 20 documentation paths; the actual local commit and post-commit Git state are as recorded at the end of the report, and the commit is not pre-filled. The old log prefix and historical results are kept; the later review should re-check the exact commit, the filled-in copies, the source field gaps, and the read-only/overwrite protection. No subagents/reviewers/workflows, Task10 or later implementation, applications, installs, hook/permission configuration, amend, push, PR, release, or remote operations; work stops after the commit and report are done, awaiting this task's scope review.

<a id="task9-review"></a>
## Task9 independent scope review closed

On 2026-10-16, an independent reviewer checked all 20 Markdown changes from `002ad73a18700e7c95b21a0fa7d0d84a26f453b5` to `3b818e5902f343a808fe476033256902f0d32a2d` and judged them within the Task9 / ENH-09 documentation scope and of acceptable quality, with no Critical/Important/Minor findings. It also separately checked, read-only, the compatibility of the review/risk fields with the existing confirmation schema and model-source; it did not run tools or re-review Task1–8.

The result locations and compatibility basis from the original review session are saved in the local session's `files/ddd-alignment-execution/task9-review-result.md`. The parent session re-checked the actual head/parent/trailer, the change scope, and the clean Git state; a separate `task9-parent-consumer.json` stores the real arguments, cwd, output, and before/after bytes of the existing checker/trace CLIs: the 13 formal synthetic records are clean, and the tool still precisely finds `task9/alpha/REQ-SYN-001#req-syn-001-ac-02` uncovered at line 16 of its source, with inputs unchanged. This deliberately retained fixture gap is not a product backlog item and was not faked as a pass.

Task9's documentation implementation/review gate is closed; this does not certify real expert decisions, tool qualification, risk acceptance, manual T17, or permissions. Next, per [Task10](../docs/plan/2026-10-14-ddd-functional-alignment.md#task10), implement optional hooks/CI and try them only in a controlled local Git fixture; no hook is installed in the current real working tree, remote required checks are not changed, and CI is not inferred to have run from the existence of documents.

<a id="task10"></a>
## Task10: optional index hooks and separate local/CI integration

### Session, basis, and Git

On 2026-10-16, implemented under the user's again-explicit Task10-only authorization; the basis is
[Task 10](../docs/plan/2026-10-14-ddd-functional-alignment.md#task10), ENH-10,
FRAMEWORK-05/08/09 in the pinned matrix, and the local session's full brief/16 prepared situations.
The closed scope gates of Task1–9 were not reopened, and there were no subagents, reviewers, or later tasks.

Starting point `7d22bd1d3889cd918d786991cfab9a9039292b97`,
branch `callentan-repository-skeleton`; the index and working tree were actually checked and both clean.
The existing isolated worktree, the Python 3.13.15 project venv, Git 2.53.0.windows.4,
and the original dependency lock were reused; no new dependency was installed. When this section was written, this round's source/tests/workflows/notes and status updates
were still the uncommitted Task10 scope on top of that starting point, unstaged; the exact object of the authorized local commit and the post-commit
state are recorded by `task10-report.md` below, and the commit's own SHA is not pre-filled inside the commit.

### Changes in this session

- [Python hooks, installation, and recovery notes](../.github/hooks/README.md): proposal by default, with the selected interpreter and
  hook, preserving owner bytes/config; existing hooksPath/files/links, shared metadata, and
  later owner edits are explicit conflicts: nothing is overwritten, and nothing is skipped and then called complete. Installation runs only in an own Git fixture.
- [Shared index adapter](../.github/utilities/hook_checks.py): raw blobs, the complete staged
  file set, mode/blob/tree/baseline, and the actual tool-version identity, including the real
  alternate index of a Git partial commit. Only private temporary regular files are used; staged source code, filters, and gitlinks are not executed.
  The [installer](../.github/utilities/install_hooks.py) does not commit, change config, or push.
- The checker's private historical-root entry point and trace's same-inventory function are narrowly reused; schemas, kinds,
  result ownership, and the original public working-tree/non-empty-delivery selection semantics were not changed. Coverage starts from all owner acceptance criteria; zero owners
  does not force an AC into existence and does not hide a declared dangling target.
- The commit-msg managed-path policy comes from FRAMEWORK-08's reviewed-by text capability;
  it does not authenticate identity, generate reviewers, or change messages; merge/fixup/squash titles get no special exemption.
- The downstream [validate-artifacts](../.github/workflows/validate-artifacts.yml) calls only distributed modules;
  the maker-only [tooling-tests](../.github/workflows/tooling-tests.yml) and
  the [counting runner](../.github/utilities/tests/run_tooling_tests.py) do not become downstream dependencies.
  Both workflows declare the lock, an explicit cwd, the exact PR head/base, and retained reports; they were not run remotely.

### Actual result entry points

In local session `1ff56941-bf56-4aa4-b769-fd4720915e1f`,
`files/ddd-alignment-execution/task10-evidence/` stores the raw receipts;
the sibling `task10-report.md` is the full handoff. Both are accessible only on the local machine and are not public or hosted CI evidence.

| Raw entry point | Actual object, observation, and limitations |
|---|---|
| `native-startup.json` | Two native-startup trials in own Git fixtures: an absolute Python shebang did not select the registered venv, and a quoted version did not succeed either; only then was the thinnest Git `sh` launcher adopted and verified with an actual commit. The current real index/config/hooks bytes were kept |
| `red-hooks/`, each `green-*/` and `red-*/` | First observed the missing implementation and specific boundary failures, then made focused fixes; the fixes to Windows path assertions, the run-module pre-check, directory aliases, source diagnostics, executing-tool identity, and owner receipt input all keep the original failures without overwriting old results |
| `final-suite/suite.json`, `unittest.txt`, `command.json` | A final retained+new run, **only once**: 428 discovered/run/executed, 0 skipped, 0 failures/errors; 397 retained methods and 31 new hook methods; the read set of source/contracts/entry points was unchanged before and after; the exact starting point/base and raw output are all kept |
| `final-suite/native-receipts/` | Real commands, cwd, output/exit, and index/working-file/config/owner-hook digests for the 31 new methods; commits after the actual installation did not hide a `--no-verify` or temporarily disable signing/hooks |
| `runner-controls-final/`, `green-runner-base/` | Separate real controls for zero discovered, all skipped, and failing/succeeding suites, plus exact/short/symbolic/unavailable bases; expected failures were indeed non-zero and are not mixed into the 428 regression count |
| `static-pre-final-02/` | Syntax of 8 Python sources, two YAML files and 4 shell snippets, this round's note links, and environment consistency; the real shared working tree was only inspected, the shared install was refused, and bytes were unchanged. The artifact scan is empty, which is not a business pass |

`static-pre-final/failure.json` keeps the initial check interruption when the packaged MinGit Bash was not found;
after locating it, another **already installed** Bash was used only for syntax checks of the YAML run snippets; Python was not substituted
for execution verification, and the syntax check is not called a GitHub hosted run. The native hook is still invoked by the current Git's `sh`, calling
the registered venv; paths with spaces/Unicode/quotes and missing-runtime failures all have real commit results.

### Self-review, limitations, and next steps

This round's self-review checked against the Task10 file list, all 16 prepared situations, distribution dependencies, and old and new API semantics;
it is not an independent reviewer or human approval. **The Task10 local implementation is complete and awaits independent scope review.**
The reviewer should re-check the final commit, the 31 new methods, and the native receipts, especially the separation of index and working tree,
the exact base/tool identity, owner hook/config preservation, empty coverage/errors, and the real count gate.

No hooks were installed in the current working tree, the main checkout, user/global configuration, or other projects;
a default install into shared metadata is explicitly refused. Hosted CI, POSIX native startup, required checks,
real identity authentication, applications, and the original P3 platform/manual items remain `not-run` or unverified. Local assertions passing alone
cannot close the whole of ENH-10; Task11's `.feature` fan-out and multi-target proposals are left entirely to that task.
After the commit, work stops to await this task's review; no amend, push, PR, propagation, release, or automatic continuation to later tasks.

<a id="resume-task10"></a>
## Task10 fix round resumed

At 2026-10-16 09:08 +08:00, the user again asked to "resume execution". The parent session re-read the entry points, the current task, and the local evidence; the actual branch was still `callentan-repository-skeleton`, HEAD `92e3d2ae4c576b523cc9a584a542966bcf7b2965`, and the working tree/index were clean at the resume check. Task1–9 are not re-run; Task10's two Important findings and one related write-recovery issue still await fixes, and the old implementation's 428-test result does not prove these issues are fixed.

The original executing agent is unavailable in the current runtime, and no active tool commands left by it were found. The local session's `files/ddd-alignment-execution/task10-evidence/fix1/` already keeps the install/environment records of an isolated Python 3.11.15, two real failures from the 3.11 native commit-argument problem, and the controlled observation of configuration loss on 3.11/3.13; there is no production fix commit. The existing test interpreter stays in the project's ignored area and is not downloaded or created again; the standard Windows venv loader's own refusal and the controlled fallback to the complete interpreter are recorded separately, and POSIX cannot be called tested.

That 3.11 environment restoration actually found that the old lock lacked the conditional dependency that `referencing` requires on Python <3.13; both the old failure and the subsequent environment-restoration records are kept. Later work only makes the necessary fixes to the lock's conditional entries needed for supported versions and to the directly related notes, without upgrading the original dependencies or changing the main environment. Resumed execution continues the same bounded fix round, re-checks the sources/runtime per the local `task10-fix1-resume-brief.md`, and then obtains new fix results and a review; no hooks are installed in the real working tree, no remote CI is run, and no qualification, business, or cross-host pass is inferred.

<a id="task10-fix1"></a>
## Task10 bounded fix round 1 (resumed execution)

### Task, Git, and existing state

On 2026-10-16, this continues the same fix round referred to by the user's "resume execution" at 09:08 +08:00; it does not redo
[Task10](../docs/plan/2026-10-14-ddd-functional-alignment.md#task10) or advance later tasks.
The starting point is `92e3d2ae4c576b523cc9a584a542966bcf7b2965`,
and the branch is still `callentan-repository-skeleton`; the index was empty, and the only pre-existing uncommitted content was the previous section's
resume note by the parent session. That note and the byte prefix of the entire earlier log are kept.
Under the existing authorization, this round makes one local commit with the specified co-author; the final object, exact file list, and post-commit
state are located by the addendum in the same local `task10-report.md` and its delivery receipts; no amend.

The basis is the original Task10/ENH-10, T10-I1/I2/M1 from the original independent review `task10-review-findings.md`,
and the resume brief's authorization for the associated conditional dependency. The interpreter configuration, dependency failure/recovery,
the two native REDs for I1, and the configuration-loss observation saved by the original worker are all read from the original records; they are not re-downloaded, overwritten, or re-recorded as actions of this round.

### Changes in this round

- The shared argument parsing in `hook_checks.py` is compatible with 3.11's native commit-msg order; managed and unmanaged
  actual commits are verified separately, and the verification logic is not moved into the shell.
- The installer probe and the two entry points share a narrow-purpose environment check. The launcher keeps the exact selected executable/
  prefix; at startup it first checks the version, venv/config, pinned direct dependencies, and importability, then reads the index/artifacts,
  and re-verifies the configuration/environment identity before finishing. Configuration loss or a fallback to base is no longer just a field in a success report.
- The installer records to its ledger immediately after exclusive creation; a short write or a write/flush/close failure keeps the exact path,
  expected/current bytes, and manual-recovery state, without automatic deletion. Actual later owner edits are kept, and reinstall/recovery
  still refuses when it meets leftovers or mismatched receipts. Errors are injected through controlled fixture I/O; no real full disk is produced.
- The lock only appends the conditional entry `typing-extensions==4.16.0` / Python `<3.13`, verified by an actual install.
  The original six pins are unchanged; the existing isolated 3.11 environment was restored offline from the updated lock and checked, while the main 3.13
  only had a dry-run/consistency read and still selects the original six. The directly related notes and the native/dependency contract tests were updated accordingly.

### Actual result entry points and applicability

In local session `1ff56941-bf56-4aa4-b769-fd4720915e1f`, this round's results are appended to the original
`files/ddd-alignment-execution/task10-report.md`; all new raw evidence
is in `task10-evidence/fix1-resume/`, accessible only on the local machine, and is not cross-machine or hosted evidence.

- `baseline.json`, `saved-native-audit.json`: the on-site state, the original log/report prefixes, the old evidence identities, and a read of the complete
  native receipts; the old 3.11 RED is still in `fix1/red311-i1/` and was not overwritten.
- `red313-runtime-recovery-lock/`, `red311-parser-lock/`, and each new `green*`:
  real counterexamples of configuration fallback/version drift, partial writes, and the conditional lock were observed first and then fixed item by item.
  The 3.13 RED's 8 methods had 12 assertion failures (including subtests), not 12 methods; 0 errors/skips.
- `runtime-lock.json`: the seven actual inventory items from the 3.11 offline sync/check and the metadata sources of the condition, plus
  the six selections of the 3.13 dry-run and the unchanged environment. No undeclared test-only dependencies.
- `final311/suite.json`, `unittest.txt`, `command.json`: this round's only complete final
  retained+new run; 3.11.15 actually discovered/ran/executed **439**, with 0 failures/errors/skipped,
  runner 723.375 seconds. All 428 original test identities are kept, and 11 were added; the source/test read set was unchanged before and after.
- `focused313-final/`: 3.13.15 ran only **42** focused hook/dependency regressions, with 0 failures/errors/
  skipped; the full suite was not re-run on that version just to prove the same thing again.
- `results-audit.json`: each of the two versions has 31 native commits after actual installation (13 accepted,
  18 rejected as expected), with no hidden bypass; controlled I/O and discovered/executed counts were checked separately.
- `runner-controls311/`: the separate zero-discovered, all-skipped, failing, and succeeding controls actually exited
  `1/1/1/0` and are not mixed into the 439 or 42 method counts. `static-final/` and the delivery receipts
  keep the documentation/syntax checks, the exact base, and the read-only and commit boundaries of the real index/config/hooks/source.

The standard Windows venv loader already refuses on its own when the configuration is lost, so that cannot count as a pre-fix failure of the new guard.
A complete Windows interpreter copy, by contrast, really started under explicit PYTHONHOME/PYTHONPATH boundary conditions;
after the venv prefix was lost, the shared guard returned an input error and no artifact/index check ran; no dependencies were installed into
base/global. These are local Windows experiments, **not verification in practice on POSIX/Ubuntu**.

### Self-review and next steps

This round's self-review covers only the three items above plus the associated lock, the directly related documents/status, and all existing regression identities; it did not change
schema/kind, source/report ownership, the original tool algorithms, workflows, or any other implementation of Task1–9.
**The fixes are implemented and await the Task10 bounded review; the review gate is not closed.**

No hooks were installed and no configuration was changed in the real working tree/main checkout/user/global; no application,
POSIX/WSL/container installs, remote CI, required checks, push, PR, release, or new worker.
The objects/runs of the original 428 and the new 439/42 are each kept; a local pass does not imply a hosted, identity-authentication, business, or
whole-enhancement pass. The branch/worktree are kept; work stops after the commit, and the only next step is this round's independent bounded review.

<a id="task10-fix2"></a>
## Task10 narrow fix round 2: Minor report-import boundary

On 2026-10-16, work continued on T10-F1-N1 as bounded by the user. Clean starting point
`edca016ca976642fb2bf93cef3f542018ba13e7a`, branch
`callentan-repository-skeleton`, with no pre-existing dirty/index changes.
The local `task10-fix1-review-result.md` had judged the original I1/I2/M1 and the conditional lock as ADDRESSED,
and they remain closed; there are no new Important/Critical findings. This round has only the new Minor and does not reopen those findings.

The original `run_hook` already refused and kept exit 2 when the selected prefix did not match, but `main --report`
still imported `check_artifacts` and the YAML/jsonschema/referencing chain to write the report. The actual RED
reproduced on both 3.11.15 and 3.13.15: 6 methods each, 8 failing subtest assertions, 0 errors/skips.
The refusal always held, and the native launcher does not request a report; this is not a successful fallback or a native commit vulnerability.

This round's production change is only the shared main/report hand-off and a boolean flag for the initial startup check. When startup is refused, the
validator is not imported and the report path is not checked or created; the stdout JSON and the recovery hint/exit 2 are kept, with explicit
`report_output.written: false` and `reason: startup-refused`. A valid environment still uses the original shared
exclusive/conflict write; source/baseline input errors in a valid environment can still save a new report, and the write engine is not duplicated.

The 6 new regressions cover both entry points, new/existing reports, explicit subprocess import observation and the real CLI without observation,
plus controls for creation/conflict and input-error reports in a valid environment. The import observation only records and delegates to the real import;
it does not mock the runtime or Git stdout, and it does not claim native POSIX. The bytes of sources, messages, index/config/hooks,
and existing reports are checked separately; the tests did not create a new interpreter or install hooks.

The new evidence is only in the local session's `files/ddd-alignment-execution/task10-evidence/fix2/`:
`baseline.json`, `red311-report-startup/`, `red313-report-startup/`, and
`green311-report-selectors/`, `green313-report-selectors/` store the complete arguments/cwd/
stdout/stderr/exit and before/after digests. Each version finally discovered/ran **9 methods** (6 new + 3 retained),
with 0 failures/errors/skipped; 63.000 seconds on 3.11 and 52.419 seconds on 3.13. These are the affected selectors,
not a re-run of the 439-test full suite, and they are not combined with the old 439/42 or the separate 112 recorded by the review into a new total.

The same local `task10-report.md` appends fix2's final commit, static/protection checks, and raw evidence entry points;
the original log's full 97,086-byte prefix and the earlier reports/evidence are kept, and historical results are not rewritten. Only after a bounded self-review,
one new local commit with the specified co-author is made under the authorization, with no amend; read the object and post-commit state from the report.
Local evidence is not a public or hosted result; the closure of the original I1/I2/M1/lock and the new Minor awaiting review are recorded separately.

**The round-2 fix is implemented and awaits the T10-F1-N1 bounded review; the task gate is not closed.**
No changes to schemas, the lock, workflows, the installer, or later tasks; no installing/changing of the real hook/config,
no redoing of native environment experiments, no installing of runtimes/dependencies, no starting of subagents, reviewers, applications, or Task11,
and no remote CI, push, PR, or release. The limitation that POSIX/hosted platforms were not run remains; work stops after the commit.

<a id="task10-review"></a>
## Task10 local scope review closed

On 2026-10-16, the original I1/I2/M1 and the `<3.13` conditional dependency had been confirmed ADDRESSED by the independent reviewer;
this time the parent session directly read the complete seven-file scoped diff from `edca016ca976642fb2bf93cef3f542018ba13e7a` to
`02657745e3b7212ebe2b3b58ec7a9a83713317f2` and the report addendum,
and confirmed that Minor T10-F1-N1 is addressed, with no new issue introduced by the fix. Only the initial-check flag and the report hand-off changed;
the report writer was not duplicated, and the exclusive/conflict protection of a normal environment was not weakened; the original full Task10 review was not repeated.

The local session's `files/ddd-alignment-execution/task10-fix1-review-result.md` and
`task10-fix2-review-result.md` keep the two rounds' judgments respectively. On the latest fix object, the parent session also used the existing
3.11.15/3.13.15 to run the 6 `StartupReportTests` on each, with no failures, errors, or skips, and exit 0;
the raw output/receipts are in `task10-evidence/fix2-parent311/` and `fix2-parent313/`.
The raw unittest duration was 32.213 seconds on 3.11 and 26.847 seconds on 3.13; capture overhead is recorded separately and not counted as test duration.
The earlier 112 tests in `task10-fix1-parent311.json` and the implementer's 439/42 keep their original objects and are not combined into a new full suite.

The actual head/parent/co-author, the seven committed paths, and the clean working tree/index were checked. Task10's local implementation
and bounded scope review gate is closed, with no outstanding findings for this task; this is not a pass of the whole of ENH-10 or of hosted platforms.
Real project installation, POSIX/Ubuntu native execution, server-side required checks, applications, and manual acceptance have still not been run.
The next step, per [Task11](../docs/plan/2026-10-14-ddd-functional-alignment.md#task11), implements the local three-way update
and multi-target proposals; this does not authorize clone/fetch/remote writes/PRs, automatic merges, or release.

<a id="task11"></a>
## Task11: read-only three-way template update and explicit BC scenario proposals

On 2026-10-16, only Task11 of the authorized enhancement plan was implemented, starting from a clean
`2a8c9a95ad991167756ba7b02ec5727b3100ed2c` in the original
`callentan-repository-skeleton` linked worktree; no new worktree was created and the main checkout was not accessed.
At the start, 135 original tracked files were verified, with no changes in the index/working files; the actual maintenance interpreter was still
3.13.15, and the existing minimum-version interpreter was 3.11.15. This round made no install, runtime, or dependency changes.
The 445 test identities at the start are only a discovery list, not a previously passed full suite.

### Implementation scope and judgments

- The [read-only core](../.github/utilities/plan_template_update.py) uses narrow dataclasses to compare the raw bytes of the real
  base/local/candidate; UPDATE-01–16 cover modify/delete conflicts in both directions, deliberate local deletions,
  add/add, local business files, exact content/local Git versions, aliases/exclusions, read failures, drift, and output protection.
- The [explicit registration contract](../docs/template-updates.md#registration) and
  the [blank data form](../_templates/config/template-updates.yaml) contain only sources, versions, and allowed files:
  scenario → explicit BC/repo/context → local mapping → separate no-change/proposed/conflict/unavailable.
  The safe YAML reader and the restricted Git helper are reused; roots/versions are not invented, and models or whole repositories are not copied.
  A target failure does not erase other proposals; unselected/missing registered target roots remain under output protection.
- Added the ninth [update-template method](../.github/skills/update-template/SKILL.md),
  the twenty-second [thin prompt](../.github/prompts/update-template.prompt.md), and the maintainer-side manual
  `propose-template-updates.yml`; the three modes are unchanged. The original eight methods are kept, no role pipeline was added,
  the workflow does not become a downstream runtime dependency, and the YAML was only read locally/self-reviewed for scope, not run.
- The [tool notes](../.github/utilities/README.md#template-update), development registration, README/AGENTS,
  integration navigation, plan/specification/roadmap, and the local gap for FRAMEWORK-09 were synced; the historical observation of six native methods/five prompts
  is not extended into nine/twenty-two verified by clients, and the old 38 files are not this round's release allowlist.

### TDD, self-review, and bounded self-use entry points

The new [regression tests](../.github/utilities/tests/test_template_update.py) started from an actual conflict RED;
then the three-way/read boundaries, version/scope, and batch registration each failed first and were implemented afterwards. Self-review also reproduced "a selected file that disappears after stat
is treated as absent" and "source/target diagnostics are confused", and fixed each; a failure to resolve the output-protection root also got a real refusal-path RED
before being narrowly mapped to input-error/2 rather than swallowed as success. The read-failure tests for Windows file locks, directory junctions, and real
Git objects/CLI use actual resources; I/O injection for directory enumeration, controlled changes, and output resolution is marked separately and does not pose as an OS ACL.

Evidence accessible only locally is in this session's `files/ddd-alignment-execution/task11-evidence/`,
and the full report entry point is the sibling `task11-report.md` (written at the completion stage); this is not distributed content or cross-machine public evidence.
`start.json` stores the original file digests/445 identities; `red-01`, `green-02`, `red-03/green-04`,
`red-05/green-06`, `red-07/check-08`, `red-09/green-10` store the exact runner argv/cwd,
stdout/stderr, discovered/run/failed/error/skipped counts, and the source read set. The most recent complete Task11 focused group is
58 methods, 0 failures/errors/skipped; the new separate consumer and the output-resolution guard each had 1 more method actually run,
and these selectors cannot be combined into one new full-suite result.

The new method had bounded self-use following writing-skills. `method-before-observation.md` keeps
project-onboarding's **correct** baseline and does not manufacture errors in the old method; positive/conflict/missing-base
read the actual fixtures and gave 0/1/2, with all source bytes/file sets unchanged. This is only explicit reading/self-use by the same agent,
not a fresh-context independent stress experiment, manual T17, native discovery, or permission trial.

### Status at this stage and remaining gates

The main local implementation is complete; the final retained + new full suite, the document/historical-prefix check, and the local commit still await actual results appended to this section.
The Task11 delivery will await independent scope review and does not close this gate itself. The original remote fan-out's clone/push/PR,
hosted/self-hosted workflow runs, POSIX native, server-side gates, real installation, applications, manual work, and Tasks12–18
were all not run; this round starts no subagent/reviewer and does not write to, commit to, or perform any remote operation on target repositories.

### Task11 wrap-up diagnostic fix and evidence objects

A wrap-up check with own fake markers found that the new tool echoes the original value when the helper refuses a URI/UNC.
No real credentials were used and no network was accessed. An actual CLI counterexample and four failing subtests were obtained first; then, only at the new planner boundary,
network roots are refused early, reusing the output error code without printing the original value; the old helpers and other tasks were not modified.
This new regression went RED→GREEN, and owner bytes/file sets are still protected.

To avoid mixing source objects, the first complete minimum-version attempt, still running, was explicitly aborted; it produced no complete runner
receipt/raw output and cannot be recorded as a pass or used to infer an execution count. `interrupted-13.json`,
`red-17-uri-diagnostic-probe.json`, and `green-20-uri-diagnostic-probe.json` keep the reason and
the real refusal output; all earlier evidence is kept. The final minimum-version full suite after the fix uses a separate new prefix and does not repeat the complete baseline.

With the same final core on the primary 3.13.15, `focus-19-primary313` actually discovered/ran
**61 new methods**, 0 failures/errors/skipped, exit 0; runner 43.924 seconds (unittest 42.532 seconds).
`inventory-23-retained.json` confirms that all 445 original identities are kept, 506 are currently discovered, and 61 were added;
this is still only a discovery/byte-protection record, not the minimum-version full-suite result. The bytes of the 39 original files (the original eight methods, twenty-one prompts,
three roles, five schemas, and two dependency manifests) are all unchanged.

The final practical use of the method/batch is kept separately in `method-after-final21.json`, `manual-batch-final21-use.json`, and
`manual-batch-final21-proposal.json`, which keep the final core digest, actual arguments/cwd/output/exit, and source hashes.
`static-22-corrected-core.json` checks the 14 changed Markdown files/364 local links, the actual 9/22/3 counts,
the old log's 101,890-byte prefix, and the original text of the historical native observations; no new/old link findings. External links were not visited;
the workflow was only parsed/self-reviewed, with checkout clean disabled, and the prepared sources must be outside the tool's checkout.

The minimum-version environment has no pip module, so the diagnostic `pip check` exited 1 and cannot be recorded as a pass; nothing was reinstalled for it.
`environment-15.json` stores the primary pip check/0, the actual package versions/successful imports of both interpreters, and the fact that nothing was installed.
The formal artifact check `formal-16-root.json` is empty/0, with 0 formal objects discovered/run;
it cannot substitute for the behavioral full suite or ordinary document checks. The final complete minimum-version result is still as given by the actual receipt appended afterwards.

### Task11 final complete verification and handoff state

The final `final-18-retained-new.json/.txt` ran completely on the non-reinstalled Python **3.11.15**:
**506 methods** actually discovered/run, failures/errors/skipped all **0**, exit **0**;
runner **838.141 seconds**, raw unittest **836.005 seconds**. This is one complete retained + new run of the final source,
not earlier selectors stitched into a full suite, and not the result of the aborted attempt.

`final-24-integrity.json` independently checks that the 506 actual `ok` identities in the raw output exactly equal the original 445 + new 61,
with no missing/extra identities; all checked tool/test/contract/dependency input hashes are unchanged, and the 61-method run on the primary 3.13
used the same inputs. The core digest in the final method/batch evidence also matches the current file, and the original log's
101,890-byte prefix is still preserved byte for byte. The exact fields of the empty artifact check in the previous section are
`checked_count/attempted_count=0`, not unittest discovered/run counts.

Implementation and in-scope self-review are complete; Task11's status is **implemented, awaiting independent scope review**.
Only one new local co-authored commit is prepared under this authorization; read the actual commit/parent/trailer, the 18 in-scope files,
the post-commit Git state, and the full raw result entry points from the local `task11-report.md`. The log does not guess the ID of the commit containing it
as an object that already exists, and there is no amend, push, PR, or cleanup of this App-managed worktree.

The only next step is the independent Task11 review; whoever takes over must re-check the commit, diff, final receipt, and accessibility.
POSIX/hosted/self-hosted execution, server-side required checks, real installation, remote fan-out/PRs,
applications/manual T17/new native discovery, and Tasks12–18 keep their respective not-run/authorization gates; this round stops after the commit.

<a id="task11-fix1"></a>
## Task11 fix1 (1/5): paths, root identity, and output reservation

On 2026-10-16, per this round's bounded request, work started from a clean
`94b47794d66e14dd26d561d7240748a967d784f0` in the original
`callentan-repository-skeleton` worktree. The independent review's three Important findings
(T11-I1/I2/I3) and one Minor (M1) were read in full; the reviewer/parent session previously had only static counterexamples,
so this round obtained real run evidence separately and does not record their static observations as reproduced.

### Scope, protection, and item-by-item fixes

This round changed only the new planner's topology/root/output-path logic, the focused tests, the directly updated notes, this plan, and this log.
Dependencies, shared Git/YAML helpers, methods/prompts/roles, workflows, business applications, and Task15 were not changed.
The original 3.11.15 minimum interpreter and the 3.13.15 primary interpreter are still used, with no installs or global environment changes.

- I1: before absence classification, files, directories, and parent prefixes get a unified case-folded check; mapping reads also verify actual directory entries,
  so an owner directory differing only in case is not treated as a location where new files can be added, and nothing is unblocked by narrowing the complete owner scope.
- I2: every actual prefix of the raw traversal is first checked for existence/directory/link identity and only then canonicalized.
  Roots, registration files, outputs, and all declared output-reservation locations no longer have `..` erased by abspath first;
  normal explicit sibling roots and exact local Git versions remain usable. Parent traversal after an unknown missing prefix is refused.
- I3: a report must not equal a declared root, lie below it, or become a file ancestor of that root; missing/unselected targets and missing sources are protected
  in the same way. A refused output still keeps the stdout results of independent selected targets, the non-zero exit, and the original file set.
- M1: only the one adjacent duplicate `task11` anchor was deleted; no unrelated Markdown cleanup.

### Focused evidence entry points (local only)

This session's `files/ddd-alignment-execution/task11-evidence/fix1/` separately stores this round's new evidence
without overwriting the original abort record or the 506/61 receipts. `baseline.json` captures the original 506 test identities (discovery only),
142 tracked sources, the 26,507-byte report prefix, the 110,283-byte log prefix, and digests of 50 existing evidence files.

`red-01-all-findings` actually ran 77 Task11 methods while the planner/plan still equaled the starting point,
including the new regressions; there were 16 failing subtests and two assertions with wrong expected values. Those two assertions were then made explicit as "forbid output creation as a file ancestor",
and `red-02-findings-assertions` ran 16 methods on the new group with 18 failing subtests and 0 errors/skipped,
obtaining a real RED for I1/I2/I3. The existing correct refusal of mapping directories and the ordinary sibling/Git cases are kept as controls.

After that, the I1 five-method, I2 twelve-method, and I3 six-method selectors each went GREEN; the raw traversal of registration files
and the directory prefix of absent files in mappings each had a single-case RED before getting the corresponding GREEN. All use real files,
Windows junctions, exact local Git, and the current interpreter's CLI; Git stdout was not mocked, and actual
file identities were not replaced. Expectations for case/paths/status are not derived from the implementation under test. Control cases and separate selectors cannot be stitched into a full suite.

`native-04-traversal-policy.json` records only the real Windows junction/parent-path observations:
local Win32 reads take the lexical shadow, and this round's policy still refuses a raw declaration with a cancelled-out junction;
this is not evidence of POSIX behavior. The provided execution host is Windows; this round did not access/create a POSIX host,
the POSIX runtime remains not-run, and no OS was installed and no Git shell was used to pose as that item.

The actual results of this round's final retained + new full suite, the complete raw execution identities, the prefix protection, and the new local commit are to be appended to this section
and also to the same local `task11-report.md`. The implementation does not approve its own bounded review; the platform/real installation/remote
propagation/PR, manual, and later-task gates are unchanged.

### fix1 final run, source protection, and stopping point

This round's only final minimum-version retained + new full suite, `fix1/final-11-retained-new.json/.txt`:
the existing Python 3.11.15 actually discovered/ran **524 methods**, 0 failures/errors/skipped, exit 0;
runner **851.172 seconds**, raw unittest **849.297 seconds**. On the primary 3.13.15,
`focus-12-new313` separately ran the 18 new cases, 0 failures/errors/skipped, exit 0,
capture 22.227 seconds, unittest 21.262 seconds; the complete baseline was not re-run.

`integrity-16-full.json` checks the 524 actual `ok` identities in the complete raw output:
exactly the original 506 + new 18, with no missing/extra items; the full suite, the 79-method focused group, and the new 3.13 cases used the same input hashes.
Source and test inputs did not change; `use-15-final-core.json` stores the current core's actual API/CLI
I1/I2/I3 refusals, an independent clean proposal, and normal sibling/Git exit 0, protecting all
own files/file sets before and after each call. The old 506/61 or this round's selectors were not added up to pose as a new full suite.

The original 26,507-byte report prefix, the 110,283-byte log prefix, and the 50 old evidence files all keep their original bytes;
M1 only changed the adjacent anchors from 2→1, and the existing nine methods/twenty-two prompts/three roles and all native observations are unchanged.
For the bounded document check, the final five-file scope, and the new commit's exact object/parent/co-author/post-commit Git state,
continue reading the fix1 addendum in the same local `task11-report.md`; the log does not pre-fill a commit ID that does not yet exist.

**This round's fixes for I1/I2/I3/M1 are implemented and self-reviewed and await the bounded review; the implementer does not close the gate.**
Only one new local co-authored commit is prepared under the authorization; no amend/push/PR, and this worktree is kept.
What follows is limited to the Task11 fix1 scope re-review; no reviewer/subagent, Task15, or other later task is started,
and no POSIX/hosted/server-side/real-installation/remote-propagation/application/manual or new native entry-point acceptance is performed.

<a id="task11-review"></a>
## Task11 local proposal scope re-review closed

On 2026-10-16, the original independent reviewer did a bounded re-review of the five-file fix1 from `94b47794d66e14dd26d561d7240748a967d784f0` to
`37cf6700af8f1fad1c60e2fe1135d25573cc1995`:
I1/I2/I3/M1 are all ADDRESSED, compliance and code quality match this round's scope, and there are no new Critical/Important/Minor
findings. Normal sibling roots, independent targets/mappings/versions, raw bytes, and the stdout results after an output refusal are preserved.
The original full 18-file review was not repeated, and the Windows junction observation is not called POSIX execution.

The local session's `files/ddd-alignment-execution/task11-fix1-review-result.md` stores the basis for each item;
the parent session also ran `test_template_update.py` on that fix object, where the existing 3.11.15 interpreter discovered/ran
79 methods, 0 failures/errors/skipped, exit 0, 87.843 seconds, with checked inputs unchanged; the raw command, output, cwd,
and digests are in `task11-fix1-parent311.json` and its invocation/raw-output files. The old 506/524
full suites and the other selector records keep their own objects and cannot be mixed into one new run. The Git head/parent/co-author,
the five committed paths, and the clean working tree/index were re-checked.

Task11's bounded local implementation/review gate is closed, with no outstanding findings for this task. The pinned capability matrix only updates the corresponding
local status; remote clone/push/PR, hosted workflows, and complete external functional equivalence have still not been run or accepted.
The next step, per [Task15](../docs/plan/2026-10-14-ddd-functional-alignment.md#task15), implements optional source onboarding;
the Task12 candidate is wrapped up only after Task16–18 are satisfied; prerequisite capabilities and authorization gates are not skipped because of numbering order.

<a id="task15"></a>
## Task15: explicit local domain-source onboarding (awaiting independent review)

### Session, task, and Git state

| Field | Record |
|---|---|
| Date and task | 2026-10-16; Task15 / ENH-15, this task only |
| Tools and mode | Implementing agent's self-use and self-review; existing Python 3.13.15 / 3.11.15, native Git, Windows; no subagent/reviewer |
| Task source and scope | [Task15 plan](../docs/plan/2026-10-14-ddd-functional-alignment.md#task15), [ENH-15](../docs/design/ddd-functional-alignment.md#requirements); the full brief and the 12 input categories are in the authorized local session outputs |
| Branch and starting point | `callentan-repository-skeleton`; `d38e7f6a71ef692c764d085df699a04c6844768b`; worktree/index re-checked and clean |
| Object and commit | The starting point above plus this round's Task15 code/documents; for the exact SHA of the scoped co-authored commit and the post-commit state, see actual Git and the local `task15-report.md` |
| Pre-existing and current scope | No pre-existing uncommitted changes; this round covers only the source tool/tests/guide, a narrow shared helper, direct navigation, and the current status; existing tests, schemas, the lock, hooks/workflows, and original acceptance results were not rewritten |
| Permissions and stop boundaries | Explicit onboarding and index consent only in own fixtures under `.venv`; no running of the original installer or source hooks/filters, no network requests, credential probing, changes to real project configuration, pushes, or PR creation |

### Changes in this session

- Added [setup_domain_source.py](../.github/utilities/setup_domain_source.py),
  [real local test cases](../.github/utilities/tests/test_domain_source.py), and
  the [distributed usage guide](../docs/domain-sources.md). inspect is always read-only; register only maintains the exact existing
  BC source list, and non-empty domain guides are not overwritten. Optional local submodule materialization is separate from registration
  and additionally requires an exact target, an ownership declaration, and separate index consent; it implies no commit/push.
- The original pinned-commit/domain-bytes comparison was narrowly extracted into
  [source_baseline.py](../.github/utilities/source_baseline.py) and shared with the collector;
  the original path-traversal and Git-environment helpers are shared by the planner/checker/onboarding, with no second YAML or source parser.
  BC v1's root/path/pinned baseline/readOnly are kept, and the configuration form only gains navigation comments.
- Self-review counterexamples went RED first and were then fixed: explicit CLI operations, invalid ID types, case variants of metadata roots,
  native complete index identity, Git format/Windows long paths, and exact partial-state bookkeeping.
  Real failures of native local clone/objects/index are kept; conflicts, missing items, or skips are not treated as success.
  onboarding only adds a link to the existing guide; still nine methods, twenty-two prompts, three modes.

### Actual result entry points and access limitations

The local session's `files/ddd-alignment-execution/task15-evidence/` keeps the real commands, cwd, interpreters,
raw output, and digests; the full entry point is the sibling `task15-report.md`. They are accessible only on the local machine,
were not distributed as cross-machine evidence, and are not business VT/human approval records:

- `red-03-behavior.*`: 44 new methods, 64 failing assertions/subtests, 0 errors/skipped; the earlier missing-module and
  scaffold runs are kept separately. `green-01-primary.*` and `green-02`–`green-07` are 3.13 focused results for different objects/
  selectors and cannot be merged into one new full suite.
- `final-minimum-suite.*`: this round's only final 3.11.15 retained + new full suite actually discovered/ran
  **579 methods**, 0 failures/errors/skipped, exit 0, runner 1104.109 seconds; the original 524 identities are kept,
  and 55 were added. Tool inputs did not change during the run; the historical result of the original 524 was not rewritten as this round's result.
- `inventory-before-final.json` and the execution-identity check keep the starting bytes of the methods and the original tests;
  the initial evidence-script comparison error between Windows CRLF working files and Git LF blobs is recorded separately, and neither the product nor the
  tests were changed to mask it. `receipts-01` stores, for each of SOURCE-01–12, the real API/CLI 0/1/2, the exact source/target/
  native metadata, and before/after hashes; `single-repository-receipt.json` additionally verifies that same-repository registration changes only the BC configuration,
  with the original domain guide and Git metadata unchanged.
- Local links/anchors in ordinary guides, the new distribution navigation, the BC form data, and the 9/22/3 inventory were checked separately;
  the original formal artifact check is `empty`, checked 0, and is not written up as a business pass. The old log prefix before the append and the original
  verification/client/native/human records are protected by raw working-byte digests; the old baselines/results are kept.

### Gaps, impact, and next steps

Task15 **local implementation and self-verification are complete, awaiting independent scope review**; this round has no reviewer or approval conclusion.
The readOnly/ownership parameters do not provide an OS ACL, and the inspect and write checks are not a
sandbox against a malicious concurrent file system. Non-empty targets/aliases/unsupported layouts/shared metadata/drift stop the operation; partial state is only for the owner to check path by path
and then restore manually, with no automatic cleanup, reset, or overwriting of later owner content.

Real project onboarding, network, POSIX, hosted platforms, applications, native clients, manual work, and release were all not run;
the external results of the original P3 and other ENH items are not upgraded. Task12–14 and 16–18 were not implemented, and Task12 is still subject to the 15–18
prerequisite constraint. Work stops after delivering this scoped commit and the full local report; next, the coordinator first arranges
the independent Task15 review against the actual baseline, and this round does not automatically start later tasks or external operations.

<a id="task15-fix1"></a>
## Task15 fix1 (1/5): bounded fixes, awaiting scope re-review

### Session, task, and Git scope

On 2026-10-16, per the full independent review and the four fix requests given by the user, only
**Task15-I1/I2/I3/M1** were handled. The starting point was re-checked as a clean
`3a99245ee7448f99579399bd9d560f34b536c4ed`, still in the original isolated worktree of
`callentan-repository-skeleton`, with no pre-existing uncommitted content.
At the time, the review and the parent session only confirmed these mechanisms statically; the new RED/GREEN below belong to this round's execution and are not attributed to the reviewer.
This round covers only two source mechanisms, one new regression file, the directly related guide/current status, and this addendum; the exact scoped commit SHA
and the post-commit Git state are recorded by the final local report/Git; no amend/push/PR.

### Changes and result entry points

- **I1:** before the first new checkout, metadata that exists in the owner's HEAD but is missing from the index is distinguished from a truly
  new/unborn state; staged deletions and case aliases are both treated as conflicts first, and index consent does not revoke the owner's intent.
  The raw HEAD/index/config/working bytes are kept; HEAD is used only for observing owner history and does not select the source version.
- **I2:** the BC token uses the raw acquired bytes that were actually parsed/planned; a change in a later consistency read yields
  INPUT_CHANGED. A controlled change of a real project ID/context A→B inside inspect triggers refusal, keeps B,
  and delivers no mixed token; this is not a claim to eliminate every malicious TOCTOU.
- **I3:** before running commands, the shared raw Git reader and the native helper check the local regular Gitfile,
  commondir, and common/worktree/explicit config, refusing include/includeIf and unsafe metadata.
  Git config is not invoked to discover includes, and declared targets are not opened; native clone re-checks the exact source separately.
  Relative config is bound to the command cwd, and incomplete metadata does not borrow ancestor discovery. This is only a narrow boundary protection;
  it does not expand or rewrite owner/user/global config and adds no general Git configuration model.
- **M1:** a checkout overlapping `.gitmodules` itself or its case variants/descendants is refused at pre-check, without creating partial
  checkout/module metadata; the original register, raw blob, and other owner-content protections are kept.

The real commands, cwd, interpreters, counts, before/after hashes, and limitations are in the local session's
`files/ddd-alignment-execution/task15-evidence/fix1/`; the overall entry point is still this round's addendum in the sibling
`task15-report.md`. The records are accessible only on the local machine and are not distributed as downstream dependencies:

- `red-01-regressions.*`: actually 28 methods (including the five retained controls that were already correct) with 28 failing entries, 0 errors/skipped;
  subtest failure counts are not treated as method counts. Later directly coupled boundaries keep their own RED.
  I1/I2/M1 use real files and CLI/native; I3 uses safe pre-command/file-system interception,
  **without running risky Git commands with includes or accessing a UNC endpoint**.
- `green-01`–`green-07` each have an exact selector and raw results and are not stitched into one new full suite.
  Separate controls exist for truly new/unborn, ordinary local, SHA1/SHA256, readable common metadata, and shared-native
  refusal; Git stdout was not simulated.
- `final-minimum-suite.*` is this round's only final 3.11.15 retained + new full suite:
  **611 discovered/run, 0 failures/errors/skipped, exit 0, runner 1443.297 seconds**.
  `test-identity-reconciliation.json` reconciles all 579 original identities and 32 new identities,
  among which the original 55 source methods are actually kept; tool inputs did not change during or after the run.
- `i1-* / i2-* / i3-*-pre-invocation / m1-*` store the exact source/target/metadata/output hashes;
  I2 explicitly marks the harness's owner-B modification, and I3 explicitly marks the static declarations and interception layers.
  The original 579/55 receipts, 70 old evidence files, the 20125-byte report prefix, and the 122389-byte log prefix are each protected by
  raw-bytes guards; the original results and baselines were not rewritten. The formal artifact check is still empty, checked 0,
  which is not a business pass.

### Gaps and stop boundaries

The fixes and local self-verification for I1/I2/I3/M1 are complete, **awaiting bounded re-review**; findings are not closed on the independent reviewer's behalf.
The schemas, lock, original tests/helpers, the 9/22/3 methods/prompts/modes, and the old external/native/client/human
results are unchanged. No dependencies were installed and no subagent/reviewer or new real app/worktree was started; no writes to real project
configuration, network/credential probing, source hooks/filters, implicit setup commits, or external platform operations.

This round stops after delivering only the new scoped co-authored commit and the report addendum, and does not start Task16 or any other later task.
Task12 is still subject to the 15–18 prerequisites and the corresponding review/authorization gates. Next, the coordinator arranges the bounded re-review
on the actual commit baseline; network, POSIX, platform, application, client, manual, and release results remain not-run.

<a id="task15-fix2"></a>
## Task15 fix2 (2/5): original I3 only, awaiting bounded re-review

On 2026-10-16, the fix1 re-review conclusion was read in full; I1/I2/M1 are already ADDRESSED with no new independent findings,
and this round does not reopen them. The starting point was re-checked as a clean `fcd25504053b32b698b74d2462a7349bf3c17d9b`,
with the original worktree/branch unchanged. Only the comment/continuation interaction in `_git_config_file`, the new fix2
source tests, and the minimal guide/current status were modified; the setup/guard placement, original tests/helpers, schema/lock,
collector/proposal, methods/prompts/modes, and old results are unchanged.

The problem was that backslash-newlines were deleted globally before comments were recognized, splicing the include on the next line into a physical comment.
The fix scans by physical bytes instead and recognizes LF/CRLF continuations outside comments; # / ; comments end at
the physical line break, actual quoted literals/ordinary comments still work, and an ambiguous/incomplete CR gets a typed refusal first.
This is not a general Git configuration interpreter, nor an actual reproduction against a network endpoint.

The local `files/ddd-alignment-execution/task15-evidence/fix2/` stores the exact commands/cwd,
input/output hashes, raw results, and protection records; the overall report is appended only to `task15-report.md`:

- `red-01-comment-continuations.*`: 10 methods, 48 failing subtests, 0 errors/skipped; two
  retained controls were already correct. Covers #/;, LF/CRLF, BOM, include/includeIf, inline/comment
  backslash parity, and real quoted continuation. Risky Git/UNC is stopped by a tripwire before invocation;
  no command with an include was actually run and no endpoint was accessed.
- `green-01-comment-continuations.*`: new cases on 3.13.15 10/10, zero failures/errors/skipped.
  `affected-source-minimum.*`, per the authorization, ran only `test_domain_source*.py` on 3.11.15:
  **97 discovered/run, 0 failures/errors/skipped, exit 0, runner 549.016 seconds**;
  the 87 original source identities and 10 new identities were checked one by one, and the checked bytes did not change.
- The 21 safe local declarations/retained controls in `scanner-receipts.json` record the typed outcome,
  zero affected Git / zero UNC filesystem access, and before/after byte digests. The protection of the original 132 evidence files,
  the parent's 611/32 receipts, and the report/log prefixes is kept; the 611-test full suite and the unchanged
  schema/collector suites were not re-run, and old successes were not relabeled as this round's results.

This round's self-review and scoped verification are complete; I3 awaits bounded re-review, and I1/I2/M1 remain confirmed as addressed.
No package/OS settings/real project/network, source hooks/filters, subagent/reviewer,
Task16/later work, or push/PR/release actions. Work stops after delivering the new scoped co-authored commit and the report addendum;
for the exact SHA, the clean post-commit state, and the evidence entry points, see actual Git and the overall local report.

<a id="task15-review"></a>
## Task15 local source-onboarding scope review closed

On 2026-10-16, the original I1/I2/M1 had been confirmed ADDRESSED by the independent reviewer; in this round the parent session directly checked
the complete seven-file scoped diff from `fcd25504053b32b698b74d2462a7349bf3c17d9b` to
`4f053d78c7eedd8bd3b490f61b81065414009b72`,
the physical comment/continuation scanning, and the 10 new controls, and confirmed that the original I3 is addressed, with no new issue introduced by the fix.
Only one scanner changed; the guard placement, setup/index/token, schema/lock, and original interfaces are unchanged.

The local session's `files/ddd-alignment-execution/task15-fix1-review-result.md` and
`task15-fix2-review-result.md` keep the dispositions of the two rounds. On the latest fix object, the parent session used the existing 3.11.15
to run the new test module: 10 discovered/run, 0 failures/errors/skipped, exit 0, 21.562 seconds, inputs unchanged;
the exact arguments, cwd, raw output, and digests are in `task15-fix2-parent311.json` and its adjacent files.
The original 97 source methods, the 611-test full suite, and the parent session's earlier 32 keep their own objects/scopes and are not merged into a new total.

The Git head/parent/co-author, the seven-path scope, and the clean working tree/index were checked. Task15's bounded local
implementation/scope review gate is closed, with no outstanding findings for this task; this is not acceptance of OS permissions, network/POSIX/platforms, real projects,
or business/manual/release. The risky include configuration was never passed to Git or used to access a UNC endpoint.
The next step, per [Task16](../docs/plan/2026-10-14-ddd-functional-alignment.md#task16), continues with local document extraction/transcription
and candidate scoring; optional dependencies, audio services, sending real data, and the remaining authorization gates are still kept.

<a id="task16"></a>
## Task16: local source candidates and transparent scoring (implemented, self-reviewed, awaiting independent review)

### Session, task, and Git

On 2026-10-16, based on the explicit Task16 brief given after the user resumed execution and the
[original plan](../docs/plan/2026-10-14-ddd-functional-alignment.md#task16), only the authorized local scope of ENH-16
was implemented. Original branch `callentan-repository-skeleton`, existing isolated worktree; the starting point
`6c0f8ec910ce1eeedfacbfcdd1fd756adc0a5478` was verified clean, with no pre-existing uncommitted content.
When this section was written, the state was still that HEAD plus the uncommitted Task16 scope; check the final commit identity against the local report;
neither the commit nor completion of the independent review is pre-filled.

### Changes in this session

Added [extract_source](../.github/utilities/extract_source.py),
[score_candidates](../.github/utilities/score_candidates.py),
[transcribe_audio](../.github/utilities/transcribe_audio.py),
two native tests, a media manifest containing only notes, and the [source contract](../docs/source-extraction.md).
The existing reverse-engineering method only gained tool navigation, and the related utilities/development/source guides and the plan/specification/roadmap were synced;
no new method/mode/prompt, candidate-confirmation engine, formal kind/schema, or mandatory dependency.

Candidates keep the actual raw-bytes SHA256, the fragment, the line/paragraph or supplied speaker/turn/time,
and the actual DOCX document/table/cell location. DOCX is read only with the stdlib from real own OPC ZIP/XML;
the part/total-size/expansion-ratio/XML-depth/node limits are public, nothing is unpacked to disk, and relationships are not followed.
Anything outside the supported subset of plain paragraphs/rectangular tables is explicitly refused, and common office layouts are not described as fully supported.
The transparent 0–100 factors are not calibrated probabilities or acceptance thresholds; contradictory/duplicate sources are not deleted and do not decide priority.

### Actual result entry points and current boundaries

The local session's `files/ddd-alignment-execution/task16-report.md` and the absolute, authorized
`task16-evidence/` keep the separate RED/GREEN, exact command/cwd, stdout/stderr,
discovered/run/skipped counts and exit codes, and the tool input SHA256. The final focused 3.13.15 result is
48 source/audio-refusal methods and 19 scoring methods, all with no failures/errors/skips;
these partial results are not a pass of the whole enhancement or of the independent review.

`format-invocations.json` and the own format originals/outputs also keep the real CLI runs for the four formats,
DOCX paragraph+table locations, and the candidate-scoring round trip, with source bytes and the exact file set unchanged.
`syntax-and-frozen-code.json` stores the in-memory compilation results of the five new Python files;
`pre-handoff-ownership.json` verifies the original 9/22/3 inventory, the old log bytes, and the unchanged
Task15 guard/setup, core lock, contracts, and retained tests.
This material is accessible only on the local machine, and whoever takes over must obtain this session's actual report; it does not form a downstream runtime precondition.

When this section was written, the only final 3.11.15 retained+new suite was still running, and its result was not yet asserted;
the actual entry point is appended separately once it completes. The current 621 retained test sources are not treated as an earlier 621-test full-suite pass.
The old 611-test full suite, the 97 source methods, and the 10 parent methods keep their own baselines/scopes;
this round does not rewrite old receipts or stitch old results into a new full result.

### Gaps, impact, and next steps

The audio API/CLI only checks honest refusals for authorization/missing items/an unavailable adapter; it does not read audio or keys, does not discover an environment
provider, does not call a service, and does not write a fake transcript. No service/model/SDK/data sending has been chosen or authorized;
actual transcription and EXTRACT-14's future service failure remain `not-run`, not a mock success.
ENH-16 and the Task12 prerequisites are not closed as a whole; format extensions beyond the bounded DOCX layout have not been verified either.

This round had only self-review; no reviewer/subagent, agent stress test, or manual/App workflow was run;
the Task15 physical-comment/include guard was not modified. Work stops after the final local evidence and one scoped co-authored
commit and is handed to independent review; no later tasks, installs, platform, push/PR, or release operations are started.

<a id="task16-local-verification"></a>
### Task16 final minimum-version check (addendum)

The only final retained+new run has completed: the existing 3.11.15 actually discovered/ran/executed **688**,
of which 621 are retained source methods + 67 new methods, 0 failures/errors/skipped, exit 0,
**1,799.906 seconds**, `inputs_unchanged=true`, with no expected failure or unexpected success.
The raw counts, per-method output, exact command/cwd/stdout/stderr/exit, and the code/contracts/lock
input identities are in the local `task16-evidence/final-minimum311.json` and the adjacent
`-invocation.json` and `-unittest.txt`; this is not a relabeling of the old 611/97/10 records or an invented old 621 full-suite pass.

This is the maintenance verification result for this session's offline tools/refusal contract, not acceptance of audio services, arbitrary DOCX layouts, App/manual work,
platforms, or business. The bytes of the first three tools and the two new tests remain identical to the focused GREEN;
later work only adds this session's actual documentation/handoff results, without re-running the complete baseline. For the final format/document check,
the preservation of inputs/the old log prefix, and the identity of the scoped local commit, see `task16-report.md`.
The local scope is implemented and awaits independent review; ENH-16's real audio/future service failure remain not-run,
and no progress is claimed toward Task12, 17, 18, or an overall functional-equivalence conclusion.

<a id="task16-fix1"></a>
## Task16 fix1: bounded fixes for three Important findings and one Minor (awaiting scope re-review)

### Session, basis, and starting point

Based on the user's fix round 1/5 request at 2026-10-16 23:46 and the complete local
`task16-review-findings.md`, T16-I1/I2/I3/M1 were handled; the static review is not treated as a repro that has already run.
Original branch, existing working tree; the starting point `9942e70a59577f3ead9049d006c2bd827a168101` was verified clean.
When this section was written, HEAD was still the starting point plus this round's uncommitted scope; read the actual final commit from the local report.

### Changes and boundaries

- The complete normalized source unit must agree with text/kind/nature/all uncertainty, and acceptance of arbitrary substrings was removed;
  Maybe and restrictive suffixes cannot be dropped to obtain a high score.
- `artifact_io.py` only narrowly exposes the existing Markdown state machine's comment state at the start of a line; the original line/fence interfaces are kept.
  The extractor/scorer use the same normalization logic and the declared context, supporting normal indented candidates after multi-line comments,
  without duplicating the parser and without trusting the caller's duplicated visible text.
- The whole input is validated before scoring; the envelope's total unit count, line groups/turns, DOCX paragraph/body/table/cell,
  and known empty-unit relations must be self-consistent. A bare list does not guess totals, read originals for authentication, or drop duplicate/partial sources.
- DOCX checks all rows against the grid when there is one, and otherwise against the first row's actual width, without enlarging the OOXML subset.
- Only the three related Python modules, the two native tests, and the directly related contract/status/log were changed.
  The source guard, schema, lock, roles/methods/prompts, runner, dependencies, and audio entry point are unchanged.

### Actual result entry points and original evidence

The fix1 addendum in the local session's `files/ddd-alignment-execution/task16-report.md`
and `task16-evidence/fix1/` keep the exact command/cwd/stdout/stderr, real counts/exit codes,
source/input SHA256, and independent expectations. The first actual run was the new failing regressions:
two M1 subtests failed among the 50 source methods, and 32 subtests failed among the 34 scoring methods; 0 errors/skips,
with production code at that point still identical to the starting point. The later focused RED/GREEN and the supplementary I2 constraint each have new receipts;
no failure record was overwritten, and no old baseline was relabeled with new results.

Current 3.13 focused results: source 50, scoring 36, and retained parser 78 methods each passed, with no failures/errors/skips;
the ASTs of all 67 original Task16 test methods are unchanged, and 19 methods were added.
`frozen-code-and-assertions.json` stores the in-memory compilation/frozen identities of the five Python files
and checks 47 protected paths such as guard/schema/lock/role/prompt/method/runner/audio.
The only new 3.11 retained+new suite is running; this section does not pre-fill the final counts/result.

Records such as the old Task16 688/67 and Task15 611/97/10, and the objects they apply to, are kept;
the raw prefixes of the old report (24,282 bytes) and the old log (135,973 bytes) have their starting identities listed separately,
old evidence is not overwritten, and they are re-checked before delivery. The original 688 does not cover this review's counterexamples
and cannot be carried over as a pass of the fixes or of the independent review.

### Limitations, impact, and next steps

The context, raw fragment, hash, and speaker are still supplied source claims; only internal consistency is proven, not the original
or prefixes that were not provided, and nothing becomes a calibrated probability/business decision. Valid blank lines/empty paragraphs and partial lists are kept,
and DOCX is still an explicit subset. Actual audio/service failure remains not-run, and ENH-16 and the later prerequisites are not closed as a whole.
This round had only self-review, with no subagent/reviewer, network, private inputs, provider/installs, App, or real project operations.
Work stops after the final local evidence and one new scoped co-authored commit and goes to the original scope re-review;
the disposition of the review findings is not rewritten, the four items are not automatically declared independently closed, and no later task or push/PR is started.

<a id="task16-fix1-minimum"></a>
### fix1 final minimum-version result (addendum)

The only new retained+new suite has completed: the existing 3.11.15 discovered/ran/executed **707**,
i.e. 688 retained methods + 19 new methods; 0 failures/errors/skipped, exit 0,
**1,799.438 seconds**, `inputs_unchanged=true`, with no expected failure or unexpected success.
The raw entry point is the local `task16-evidence/fix1/final-minimum311.json` and the adjacent
`-invocation.json` and `-unittest.txt`, which keep the exact command/cwd/stdout/stderr and input identities.
The 688 baseline was not re-run separately, and the old 688 record was not relabeled as this round's 707.

The actual execution entry points and the self-review scope for the complete contract/coordinate fixes are in the fix1 report; all old assertions are kept.
What remains is only the document/format and protection checks and one scoped co-authored commit, after which work stops.
This is currently a local fix awaiting scope re-review; it does not mean the four findings are independently closed, let alone close audio, ENH-16,
platform/real-project/business acceptance, or advance later tasks.

<a id="task16-review"></a>
## Task16: bounded offline scope re-review and continuation handoff

### Session, task, and Git

On 2026-10-17, coordinating session `1ff56941` continued the enhancement plan already authorized by the user.
Before this write, the original branch `callentan-repository-skeleton` was verified, with HEAD at the fix object
`97d35aa57a4fb6687da995858ab6009ec23e1bce`, parent commit
`9942e70a59577f3ead9049d006c2bd827a168101`, and an empty index and working tree.
This update only syncs the enhancement specification, implementation plan, roadmap, and this log; this documentation checkpoint is located through this file's
Git history, and its own commit hash is not pre-filled. The earlier implementation, self-review, failure, and pending-review records keep their original text and baselines.

### Re-review conclusion and actual result entry points

The original reviewer completed a read-only bounded re-review of the exact fix scope above: the three Important findings T16-I1/I2/I3
and the Minor T16-M1 are all ADDRESSED, with no new actionable findings in the fixes and the adjacent regressions.
The fixes for complete source units/qualifiers, known envelope coordinates, the shared Markdown start-of-line comment state, and rectangular width
without a grid were all checked; this is a conclusion about this code scope, not human approval or a pass of the complete ENH-16.
The reviewer did not run commands or tests, and the execution records it read are not relabeled as the reviewer's independent verification in practice.

The local evidence entry points are, under `files/ddd-alignment-execution/`,
`task16-fix1-rereview.md`, `task16-report.md#task16-fix1`, and
`task16-evidence/fix1/`, which keep the review source, the actual RED/GREEN, the 707-method minimum-version
run, and the raw output. The coordinator also ran the 86 source/scoring methods on the same object with the existing Python 3.11.15:
0 failures/errors/skipped, exit 0, 62.672 seconds, inputs unchanged; read the exact command/cwd/byte identities
and raw output from `task16-fix1-parent311.json` and the adjacent invocation/unittest files.
707, 86, and the old 688/67 are records of different scopes/objects and are not added up or relabeled as another full run.
These local files are not committed cross-machine evidence; if whoever takes over cannot access them, that limitation must be stated explicitly.

### Remaining gaps and next steps

This update closes only the offline implementation and its four review findings. Source context, fragments/hashes, and speakers are not authenticated;
DOCX is still a bounded paragraph/table subset and does not imply arbitrary Office compatibility or tool qualification.
Real audio, real service failure, App/manual work, platforms, applications, and overall functional equivalence remain not-run/open,
and the missing audio provider, model, SDK, data scope, and sending authorization have not been filled in by default.
No dependencies were installed, no services called, nothing pushed, no PR created, and no real permissions changed.

The next step, per [Task17](../docs/plan/2026-10-14-ddd-functional-alignment.md#task17),
carries out the authorized local relationship diagrams, SEQ/SWAS, and parameterized presentation export; the PDF/PPTX renderer and actual format acceptance
remain behind separate gates; the complete ENH-16 and the Task12 prerequisites are not closed by this.
