# Six-repository functional alignment enhancement implementation plan

**Task8 re-review record (2026-10-16):** Two rounds of scoped re-review closed the original three Important findings and the new T8-F1-N1; the latest fix is `9a3055a`. The original 378/395 full-suite results and the partial results for different objects are each kept; see the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task8-review) for the complete entry point.

> **For AI agent workers:** On 2026-10-15 the user authorized committing the current changes first and then executing this plan. Check existing completion records first and do not repeat work; proceed task by task with subagent-driven-development or executing-plans, and track steps with checkboxes. The separate authorization gates for applications, audio/PDF, platforms, and release remain in place.

**Goal:** On the existing single-repository skeleton, provide capabilities equivalent to the existing features of the six `ddd-*` repositories, and use item-by-item evidence to distinguish what is delivered, what is not run, and what is explicitly substituted.

**Architecture:** The body text of project materials continues to own business facts, and a small amount of structured metadata connects contexts, artifacts, and verification; the model and the implementation summary are rebuildable views. Shared methods handle activities that require judgment; in-project scripts handle deterministic checks, exports, and update proposals; Git/CI/existing agents handle actual execution and authorization.

**Tech stack:** Maintenance tools use Python 3.11+, `unittest`, PyYAML 6.0.2, and jsonschema 4.23.0; local runs, hooks, and CI reuse the Python logic and do not require PowerShell wrapper scripts. The downstream application tech stack is still not selected.

**Specification:** The [six-repository functional alignment enhancement specification](../design/ddd-functional-alignment.md) contains ENH-01 to ENH-18, the complete pinned versions, and the tool interfaces. Executors must read that file and must not infer behavior from the titles in this plan alone.

**Current status:** Tasks 1–11, Task15, the offline scope of Task16, the local export scope of Task17, and the local ledger scope of Task18 have each completed their limited local implementation and review; the exact file-level candidate of Task12 and its fix wave have also completed an independent scoped re-review. There are currently nine methods, twenty-two prompts, and three modes. Task16's real audio service remains not-run, and ENH-16 is not closed as a whole. Task17's local JSON/SVG/HTML relationship graphs, architecture/SEQ, and parameterized presentation have completed a scoped review; PDF/PPTX and their actual format gates have no renderer selection/execution authorization, so ENH-17 and overall parity remain open. Task18's test results of base 804, fix1 815, and fix2 817 are kept separately; the fix2 resume-identity issue has completed re-review, real provider/billing/usage is not integrated, and ENH-18 is not closed as a whole. The `summarize_usage(lock_timeout=...)` Minor finding is deferred because the new API is unreleased and has no in-repository caller; it is handed to the final overall review for triage. The Task12 local candidate gate is closed; the 132-file candidate and its provenance passed a scoped review, but they have no release authorization and do not prove overall parity. Task13 has a user-selected Flagsmith/OpenFeature technical POC, copied at a pinned commit into the isolated `poc/flagsmith`; that object is not a real application integrated with a business system. Its locked dependencies were restored inside the copy, and the POC unit/build/controlled-browser results are 19/19, 35/35, and 10/10 respectively; live Flagsmith, code generation/maintenance, and human/App/client/platform gates remain not-run; see the [Task13 handoff](../../logs/2026-10-19-task13-flagsmith-poc.md) for details. Task14's full-matrix/release conclusions must not bypass applicable external gates. Hooks were not installed in a real working tree, and hosted CI/required checks and external fan-out are not-run. The original P3 native/manual records and the overall enhancement completion status are not upgraded as a result; no application is created and no real platform gate is changed.

**Current delivery goal (2026-10-19):** The user explicitly stated that "scaffold ready" is the priority and does not consider a real-application showcase exercise the current focus. Current readiness targets a locally copyable exact manifest candidate, candidate isolation, and applicable local verification of documentation/tools; it does not require a live showcase, a release, or a claim of full six-repository parity. The open acceptance of Task13/14 remains as separate gates for full parity/external evidence and is not used to block the local scaffold-ready judgment.

**Local candidate readiness (2026-10-19):** The 132-file candidate, freshly copied according to the current manifest, is bound to source HEAD `ee463901725ade1d0cab05261b8c875189fd229e` and its dirty scope; independent verify reports 132/132 and 0 findings, and the focused `test_distribution.py` run reports 40/40 with 0 skipped/failure/error. The temporary local `poc/` is explicitly excluded by the manifest; the complete receipt/raw output is in the session-local artifacts referenced by the [Task13/ready-scope handoff](../../logs/2026-10-19-task13-flagsmith-poc.md). This evidence supports only copyable-candidate readiness; it is not a release or full parity.

**P1/P2 and the POC copy (2026-10-19):** All 38 historical P1/P2 paths in the blueprint exist in the main scaffold. A separate POC copy is placed under the user-provided POC root as `agent-native-scaffold/`, a sibling of the Flagsmith repo, and is built from the current 132-file enhanced manifest. The copy intentionally excludes `docs/agent-support.md`, which contains historical client observations, and it also contains no `.git`, environments, application POC, dependencies, or secrets. `--verify` on the external copy reports 132 files and 0 findings; the test copy inside the main working tree has been cleaned up so that its forms do not pollute the root-level formal artifact scan. See the [Task13 handoff](../../logs/2026-10-19-task13-flagsmith-poc.md) for detailed paths, the reason for the first copy refusal, and limitations. This local snapshot does not authorize a release or full parity.

**2026-10-15 planning revision (historical):** Following the user's decision to "basically use Python scripts for everything", the required PowerShell launcher files and their tasks were removed; host-native YAML and the thinnest launch adapters are kept, and method bodies remain in Markdown. That revision changed only the plan and does not classify all new automation as features the original repositories already had; current implementation progress is governed by the status above and the per-task records.

**Same-day execution supplement:** A complete read confirmed ongoing capabilities that the original plan did not cover, and the user chose to include all of them. Original tasks 3/4/5/8/9/10/11 expand the actual artifacts and activities, and new tasks 15–18 cover optional domain-source onboarding, source adaptation, diagram/document export, and the interaction ledger. These tasks are completed according to their dependencies before the 12–14 close-out; the numbering does not mean that dependencies may be skipped.

## Global constraints

- The user chose functional equivalence: automatic import/export compatibility with old IDs/fields/paths is not required, and neither the six-repository split nor mandatory submodules are restored.
- Pin the existing versions of the six repositories; do not count sample applications, roadmaps, automatic approval/merge, or a general-purpose executor as implemented capabilities.
- Write content independently; internal materials do not enter the distribution candidate, unlicensed source code or templates are not copied, and private materials are not sent to third parties.
- New fields do not create a second copy of any fact; metadata, acceptance body text, VT actual results, and derived views each have a single owner.
- Check Git, the original files, and the scope first. The earlier README formatting was committed with authorization as `1a6f594`; after that, unrelated changes found at the start of each session are still preserved and not overwritten by default.
- When the necessary inputs are incomplete, stop the affected task and do not treat missing items as defaults; record task failures, not-run items, empty checks, and passes separately.
- Do not automatically initialize applications, install dependencies, install hooks, change CI gates, write back to external sources, push, open PRs, release, or change permissions.
- Documentation work may continue while the application is not configured; actual application acceptance of generated code first requires separate inputs and authorization in Task 13.
- The capabilities of the original six methods, three modes, and existing prompts are kept; enhancements are split by activity, without adding a role pipeline.
- Repeatable maintenance logic uses Python throughout and calls the project interpreter directly; local runs/hooks/CI do not maintain three implementations, and PowerShell 7 is not a prerequisite for using the tools.
- The Task2 contracts/parser, Task3 forms, Task4 methods/entry points, Task5 material contracts, Task6 checker, Task7 model/traceability, Task8 implementation summary, Task9 documentation, Task10 local integration, Task11 limited proposals, Task15 local source onboarding, Task16 offline source candidates/scoring, Task17 local export, Task18 local ledger, and Task12 file-level candidate have each completed the review of their own scope for this round; see each record for results. Task16's actual audio gate is not closed; Task17 PDF/PPTX and full ENH-17 are not closed; Task18 real provider/billing and usage are not integrated, and ENH-18 is not closed as a whole. The Task12 fix-wave review confirmed that the verify-report overlap, reparse TOCTOU, hardlink, stale status sentence, and provenance argument order issues have all been addressed; the 848/856/857 test baselines and the provenance receipts are each kept, and the fixed new candidate verifies as 132 files, 41 exclusions, 0 findings, a source commit equal to `cda3cfd`, and an empty dirty scope. The Task12 local candidate gate is complete but does not represent release/overall parity. Task13 still lacks the real app/stack/location/commands/allowed scope and the human/client/platform inputs and authorization; Task14 must not record unrun external gates as passed.

## 1. File structure and responsibilities

All paths are relative to the repository root. The following is the implementation scope; it does not require creating empty files or formal business instances in advance.

| File group | Specific paths to create or modify | Responsibility |
|---|---|---|
| Maker basis | Create `docs/research/ddd-capability-matrix.md`; modify the specification, this plan, `docs/plan/decisions-and-risks.md`, `docs/design/repository-blueprint.md`, and `docs/plan/roadmap.md` | Per-file sources of the six repositories, equivalence criteria, enhancement scope, and progress; not distributed downstream |
| Metadata contracts | Create `.github/contracts/artifact.schema.json`, `bc-config.schema.json`, `model.schema.json`, `implementation-report.schema.json`, and `README.md` | Data version, identity, relations, sources, and status; not run or permission configuration |
| Domain forms | Create `_templates/items/subdomain.md`, `bounded-context.md`, `capability.md`, `use-case.md`, `invariant.md`, `validation-scenario.md`, and `backlog-item.md` | Copyable structures for SD/CTX/CAP/UC/INV/validation scenarios/BL |
| Data forms | Create `_templates/config/bc-config.yaml` and `_templates/reports/implementation-report.yaml` | Blank forms for optional configuration and reports; no real project or result is prefilled |
| Existing artifacts/entry points | Modify the seven existing `_templates/items/` forms and the READMEs of `domain-model`, REQ, SR, US, architecture, verification, and logs; modify the root README/AGENTS as needed | The new contracts coexist with the old lightweight flow; describe formal locations, sources, current metadata, and results |
| Existing methods/modes | Modify the six existing SKILLs in `.github/skills`, the three `.github/agents`, the related instructions, and the five original prompts | Keep a single copy of each method and connect it to the new materials and tools |
| New activity methods | Create `.github/skills/reverse-engineer-domain/SKILL.md`, `generate-code/SKILL.md`, and `update-template/SKILL.md` | Reverse extraction, initial code generation, and safe template updates |
| Optional activity entry points | Create `.github/prompts/domain-interview.prompt.md`, `reverse-engineering.prompt.md`, `derive-requirements.prompt.md`, `design-architecture.prompt.md`, `plan-verification.prompt.md`, `generate-code.prompt.md`, `assess-impact.prompt.md`, `review-artifacts.prompt.md`, and `update-template.prompt.md` | Link the current inputs to the method; do not copy the procedure or grant permissions |
| Local tools | Create `.github/utilities/artifact_io.py`, `check_artifacts.py`, `check_traceability.py`, `export_model.py`, `collect_implementation_report.py`, `plan_template_update.py`, `README.md`, `requirements.txt`, and `requirements.lock` | Standalone Python scripts with a clear scope, called directly; no required shell wrapper, unified CLI, execution engine, or background service is added |
| Tool tests | Create `.github/utilities/tests/__init__.py`, `helpers.py`, `test_artifact_io.py`, `test_artifact_check.py`, `test_traceability.py`, `test_model_export.py`, `test_implementation_report.py`, `test_template_update.py`, `test_hooks.py`, and `test_distribution.py`; fixtures live in `fixtures/` in the same directory | Positive and negative cases with real files/Git; the downstream `src/tests` is not pre-created |
| Review/tool governance | Create `docs/ai-tooling.md`, `_templates/items/review-record.md`, and `tool-qualification.md` | Tool versions, scope, human decisions, and interaction summaries; they do not self-certify approval or compliance |
| Optional engineering integration | Create `.github/hooks/pre-commit`, `commit-msg`, `README.md`, `.github/utilities/install_hooks.py`, `.github/workflows/validate-artifacts.yml`, `tooling-tests.yml`, and `propose-template-updates.yml` | Python Git entry points, explicit installation, same-source validation, and proposal propagation; the tooling-tests/propagation workflows are maintainer-side, and platform side effects still require authorization |
| Update/distribution guides | Create `docs/template-updates.md` and `docs/distribution.md`; modify `docs/development.md`, `docs/agent-support.md`, `.gitignore`, and the PR form | Keep maintenance tools separate from the application environment; file-level distribution, version differences, and compatibility limits |
| Maker acceptance | Create `verification/ddd-alignment.md`; logs follow the existing form | ENH-* object/result/not-run records; maker acceptance, fixtures, and logs do not enter the candidate |

### Additional files added after the complete source inventory

| Task | Specific files | Purpose and boundaries |
|---|---|---|
| 3 | `_templates/items/quality-attribute-scenario.md`, `context-map.md`, `published-interface.md`, `aggregate.md`, `entity.md`, `value-object.md`, `factory.md`, `domain-service.md`, `policy.md`, `domain-event.md`, and `integration-partner.md` | Optional strategic/tactical/QAS forms; this formality is not imposed on lightweight maintenance tasks |
| 4 | `.github/prompts/distill-domain.prompt.md`, `glossary-sync.prompt.md`, `published-interface.prompt.md`, `query-artifacts.prompt.md`, `review-backlog.prompt.md`, and `amend-intended-use.prompt.md` | Each covers one source activity and reuses existing methods; no body text is copied and nothing is approved automatically |
| 5 | `_templates/items/sequence-diagram.md`, `architecture-specification.md`, and `verification-test.feature`; `.github/prompts/sequence-diagram.prompt.md` and `build-architecture-spec.prompt.md`; `.github/instructions/architecture.instructions.md`, `coding.instructions.md`, and `security.instructions.md` | SEQ/SWAS, the Gherkin companion, and rules; follow the project's real stack and necessary wiring exceptions; no application is prefilled |
| 9 | `_templates/items/intended-use.md` and `risk-control.md`; `docs/governance.md` | References to optional regulatory/risk materials that the sources actually contain, accountable owners, and confirmation gates; they do not replace external risk analysis or compliance decisions |
| 15 | `.github/utilities/setup_domain_source.py` and `tests/test_domain_source.py`; `docs/domain-sources.md` | Python preflight and explicitly approved domain-source onboarding; no submodule or commit by default |
| 16 | `.github/utilities/extract_source.py`, `score_candidates.py`, `transcribe_audio.py`, and `requirements-media.txt`; `tests/test_source_extraction.py` and `test_candidate_scoring.py`; `docs/source-extraction.md` | Markdown/plain-text, transcription, DOCX/audio adapters, candidates, and confidence; external dependencies and data transmission are authorized separately; no proposal executor is developed |
| 17 | `.github/utilities/render_traceability.py`, `render_architecture.py`, `render_presentation.py`, and `requirements-rendering.txt`; `tests/test_rendering.py`; `docs/document-exports.md` | Local relationship graphs/SEQ/SWAS and the required equivalent parameterized presentation output; PDF/PPTX renderer dependencies are authorized per format, with explicit inputs/outputs and no demo fallback, hard-coded content, or default dependency on an online CDN |
| 18 | `.github/utilities/log_interaction.py`, `summarize_usage.py`, and `tests/test_interaction_log.py`; `_templates/reports/ai-interaction-log.csv` | Record and summarize from real inputs; do not capture full chats or secrets, and do not estimate billing that was not provided |

If Task 1 finds existing features of the six repositories that this table does not cover, first update the specification, acceptance, and the corresponding file responsibilities according to the sources, and then open a bounded task. Do not delete capability rows in order to claim alignment. Dedicated domain/risk files enter this change set only after they are confirmed to be existing capabilities of the six repositories; they are not derived from business instances.

## 2. Dependencies and execution gates

| Task | Depends on | Independent deliverable |
|---|---|---|
| 1 | None | Complete source/capability matrix and scope freeze |
| 2 | 1, contract review | Metadata/schema/tool environment that parses valid input and rejects invalid input |
| 3 | 2 | Complete domain artifacts and multi-context filling paths |
| 4 | 3 | Usable methods for domain activities and reverse extraction |
| 5 | 2, 3, 4 | BC derivation/review/initial generation and the contract for modifying existing code |
| 6 | 2, 3, 5 | Repeatable artifact checks |
| 7 | 6 | Derived model, acceptance coverage, and semantic impact entry point |
| 8 | 5, 7 | Implementation summary bridge over read-only sources |
| 9 | 1, 6 | Human review and tool qualification records |
| 10 | 6, 7 | Optional hook/CI with actual failure propagation |
| 11 | 6, 7 | Three-way update and multi-target propagation proposals |
| 12 | 3–11, 15–18 | Self-contained enhancement candidate and regression of the original skeleton |
| 13 | 12, application/platform acceptance authorization | End-to-end behavior and real client results |
| 14 | 13, a conclusion for every matrix row | Functional equivalence conclusion and pre-release handoff |
| 15 | 2, 6 | Optional domain-source onboarding and protection of the original text |
| 16 | 2, 4, 6 | Locatable source extraction/scoring and optional transcription |
| 17 | 5, 7, 8 | Relationship graphs and document exports that do not fabricate data |
| 18 | 2, 9 | Minimal interaction/usage ledger and statistics |

Tasks 4/5 both touch the original methods and modes, so they run serially as 4→5 and must not overwrite these entry points in parallel. The tool tests of tasks 8/9/10/11 can be verified independently once their own dependencies are met, but changes to the shared methods/development guide are still merged serially by a single writer. Being independently verifiable is not a reason to start a separate workflow or increase the number of agents.

<a id="maintainer-checks"></a>
## 3. Maker-repository maintainer commands and test conventions

The tool tests in this section are only for a maintainer's full checkout; they are not distributed with the downstream candidate and are not a prerequisite for running the parser/checker downstream. Downstream usage guides link only to the distributed modules, contracts, dependency manifests, and development registration; the maintainer's RED/GREEN, test counts, object baselines, and historical navigation stay in this plan and the [maker log](../../logs/2026-10-15-ddd-alignment.md#task6).

No `.venv` was created and no packages were installed during Task 1. Task 2 first registered the maintenance environment and created the manifest, then restored the project's own `.venv`; the actual environment is Python 3.13.15. The existing parser/schema and Task6 checker tests use this environment and do not install new dependencies. The checker's formal discovery, exact base, and JSON contract are implemented, and the two round-1 fixes have completed focused regression and scoped re-review; for the current local scope of hooks/CI see [Task10](#task10), which does not mean that hosted runs have passed. Multi-step maintenance logic goes into `.py` files, and subprocess calls use argument lists, an explicit cwd, and `shell=False`; local runs, hooks, and CI reuse the scripts directly, and personal absolute paths are not written into templates.

| Check | Explicit cwd | Executable and arguments |
|---|---|---|
| Targeted Python tests | Current repository root | `.venv\Scripts\python.exe -B -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_artifact_check.py -v`; for targeted parser tests, replace it with `test_artifact_io.py` |
| Regression of the modules affected by the Task6 fixes | Current repository root | `.venv\Scripts\python.exe -B -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p "test_artifact*.py" -v`; discovered/executed/skipped counts are checked separately against the actual receipt, and the unchanged schema suite is not rerun to serve as evidence for the fixes |
| All tool tests (with count gate) | Current repository root | `.venv\Scripts\python.exe -B -X utf8 -u .github\utilities\tests\run_tooling_tests.py --start-directory .github\utilities\tests --top-level-directory .github\utilities --pattern test_*.py`; an exact `--base`, a new `--report <new.json>`, and `--raw-output <new.txt>` may be added, and their parent directories must already exist; zero discovered, all skipped, and failures all exit non-zero |
| Task10 targeted native tests | Current repository root | Change `--pattern` in the row above to `test_hooks.py`; real installs/commits happen only in owned Git fixtures under `.venv`, never in the current working tree |
| Syntax of maintenance tool sources and tests | Current repository root | `.venv\Scripts\python.exe -X utf8 -m compileall -q .github\utilities` |
| Artifact check (implemented and reviewed within this scope) | Current repository root | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_artifacts.py --root <root resolved for this run>`; JSON on stdout; `--report <existing authorized directory>\new-artifacts.json` may be added explicitly; old reports are not overwritten |
| Explicit historical comparison (implemented) | Current repository root | Add `--base <verified full commit>` to the row above; an unreadable exact object exits 2; the complete current formal inventory is kept, including unstaged/untracked files; this is not an index (staging-area) hook |
| Task7 targeted regression | Current repository root | The same unittest discovery command as the full tests, with `-p` set to `test_traceability.py` and `test_model_export.py` respectively; the full suite still keeps the existing schema/parser/checker tests |
| Task7 coverage/impact and model | Current repository root | Per the [actual tool contract](../../.github/utilities/README.md#traceability), use `check_traceability.py --root <materials root> --delivery <full ID>`, or `--base <full commit> --task <task key>`; for the model, use `export_model.py --root <materials root> --scope <scope>`; only an explicit `--output` writes a new file, and `--check` recomputes without repairing |
| Task8 targeted regression | Current repository root | Set `-p` of the full unittest discovery command to `test_implementation_report.py`; the bridge and the retained model mechanism use `test_model_export.py`; the full `test_*.py` suite is still run at the end |
| Task8 implementation report collection | Current repository root | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\collect_implementation_report.py --root <local checkout> --object <full commit>`; `--evidence <VT relative path[#owned run]>` may be repeated, and multiple BCs use `--scope`; only an explicit `--output` creates a new local report |
| Task11 targeted regression | Current repository root | Set `--pattern` of the full count-gated runner to `test_template_update.py`; covers three real roots, content/Git versions, per-target registration/file mapping, CLI 0/1/2, and byte protection; the retained + new full suite is still run at the end |
| Task11 proposals | Current repository root or an explicit cwd for this run | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --base <old root> --local <local root> --candidate <candidate root>`, or `--registration <local registration> --target <explicit ID>`; see the [full contract](../../docs/template-updates.md); read-only, and does not authorize propagation |
| Task15 targeted regression | Current repository root | `--pattern` of the count-gated runner is `test_domain_source.py`; covers actual pinned local Git/content, 12 input categories, API/CLI 0/1/2, native local submodules, and error recovery, without mocking Git stdout; the final retained + new full suite uses the configured minimum-version interpreter |
| Task15 source preflight/explicit onboarding | Current repository root or an explicit cwd for this run | `setup_domain_source.py --root <exact project root> --config <existing BC config> --source-id <explicit ID>` is read-only by default; a new source requires all six fields. For the exact arguments of register and submodule and their separate consent, see the [domain source guide](../domain-sources.md); operate only on authorized owned local fixtures |

Task 2's maintainer cases are split into [parser behavior](../../.github/utilities/tests/test_artifact_io.py) and [four kinds of schema data](../../.github/utilities/tests/test_contracts.py); [helpers](../../.github/utilities/tests/helpers.py) only creates temporary files under the project `.venv` and Git fixtures without remotes. Windows boundary fixtures use local junctions and byte locks; a failure to create a junction is reported as an error rather than silently skipped; on non-Windows hosts, if host privileges bypass the permission setup, the skip is reported explicitly. These are not runtime dependencies of the downstream tools, and test code is not execution evidence.

Task6's [real file/Git/CLI cases](../../.github/utilities/tests/test_artifact_check.py) do not replace the suites above. Raw stdout/stderr, cwd, exit codes, discovered/executed/skipped counts, and protected-byte digests are recorded in the authorized session evidence directory; CHECK-14 uses real zero-discovery/all-skipped runner control cases to check the evidence gate, and no "assert that it exists" case is added to the product tests. A tool's `empty`/exit 0 and zero discovered tests in a regression are different situations; the latter must not count as a passing regression. Limited OS failure injection is listed separately and does not pose as real permission configuration.

The table uses Windows paths and runs the project Python directly, without any `.ps1`. Other hosts register the interpreter location for their actual environment and do not copy the Windows `.venv\Scripts\python.exe` verbatim to Linux. Angle brackets denote path/Git object arguments resolved from the current workspace at run time; they are not invented executable values. The checker handles paths with `pathlib.Path` and passes each argument separately; the real record of commands and cwd is saved at run time.

Every Python tool task first writes behavior tests, runs them to see the expected failures, implements the minimal code, reruns, and only then commits. Tests actually read fixtures/real Git objects instead of only grepping code or mocking return values. Documentation methods are verified with real positive and negative usage examples; "a certain word appears" does not count as a correct procedure.

## 4. Task-by-task plan

### Task 1: Freeze the six-repository capability baseline

**Files:** `docs/research/ddd-capability-matrix.md`, the specification, this plan, the P0 decisions, and the blueprint.

- [x] Read the recursive trees of the six full commits in the specification and all active conventions, forms, workflows, tools, and hooks/pipelines; 185 blobs were read in full and 10 roadmaps were read within scope, and all 252 entries are classified; no upstream script was executed.
- [x] Each file records repo/full commit/path/object/read coverage, and each capability records inputs and outputs, preconditions, writes, and the target task/criterion; hashes, missing/duplicate items, and cited line bounds have been checked.
- [x] Distinguish existing methods/scripts, upstream proposals, sample placeholders, and unresolved external dependencies; keep the different consumed gitlink versions, and do not infer successful runs from directories or roadmaps.
- [x] The user confirmed full inclusion of the newly found capabilities; file responsibilities and ENH-15–18 were added, while functional substitution and the Python-first approach are unchanged. Actual audio/PDF/platform execution is still controlled by separate gates.
- [x] Completed a line-by-line review back against the sources and updated the enhancement scope of the P0 "seven forms/six methods/no tools" decision while keeping the original deliveries and P3 results; this item closes only the scope review and does not mean that any later implementation is complete.

| Original P0 decision | Original boundary (still valid) | Exact coverage of the newly found scope |
|---|---|---|
| D02 | Seven forms, six methods, three agents, five prompts, and no in-house execution layer remain the first-version baseline | Task 1 / ENH-01 owns the source scope; Task 2 / ENH-02, ENH-06 cover the contracts; Task 3 / ENH-03, Task 7 / ENH-08, and Task 8 / ENH-12 cover the new structured bridge; Tasks 9, 15, 16, 17, 18 / ENH-09, ENH-15, ENH-16, ENH-17, ENH-18 are enhancements and do not rewrite the first-version list |
| D08 | The first version does not prefill dedicated domain/regulatory suites and does not claim compliance qualification | The QAS/tactical materials of Task 3 / ENH-03, the governance/risk references of Task 8 / ENH-12, the qualification records of Task 9 / ENH-09, and the SWAS/PDF of Task 17 / ENH-17 serve only as optional, traceable inputs and produce no compliance or approval conclusion |
| D10 | Lightweight DDD requires only terms, relations, rules, context responsibilities/interactions, and sources; tactical patterns are not mandatory | Task 3 / ENH-03, Task 4 / ENH-04, Task 5 / ENH-05, Task 8 / ENH-12, and Task 16 / ENH-16 cover the new domain artifacts, derivation, bridge, and candidate extraction; the minimum filling boundary of lightweight projects is unchanged |
| D11 | The V-model still distinguishes business acceptance, software verification, coverage/impact, and actual applicability; US is not a mandatory layer | Task 2 / ENH-02, Task 6 / ENH-07, Task 7 / ENH-08, Task 8 / ENH-12, Task 14 / ENH-14, and Task 17 / ENH-17 cover the new contracts, checks, bridge, and export references; a complete mapping is not recorded as passed verification |

The above records the scope mapping and original boundaries completed in Task 1; it is not an overall acceptance conclusion for the enhancement. For the Task 2
input contracts/parser and the limited local deliveries and scope reviews of Task3–11 and Task15, see the following sections; the remaining prerequisite and close-out tasks are still not implemented, and completion of the whole enhancement must not be inferred from this table.

**Exit:** ENH-01; every tree entry of the six repositories has an owner, and no existing capability has a "no task/no criterion" row. Without this step, later work can only be design discussion and cannot claim full alignment.

**Task 1 result:** The source inventory is complete; this phase does not include implementing the target features, and the implementation and review status of Task 2 is in the next section. The matrix's 44 current capability groups overlap, so the count must not be treated as delivery progress; 6 upstream proposal groups and 1 unresolved dependency group are listed separately. Four source line numbers that pointed past the end of their files were corrected against the actual manifest, without changing source code or hiding unread content.

### Task 2: Metadata, schemas, and tool environment

**Current status: implementation and the review of this scope are complete.** The three feedback items on the initial object `4b833df` were fixed in `322cd90`; the parent session checked the root error-location regression, distribution dependencies, and status revisions, and independently reran 144 tests with 0 skipped and exit 0. See the [maker log](../../logs/2026-10-15-ddd-alignment.md#task2-review-1) for the real evidence and limitations; later exporters, cross-file traceability, and application acceptance are not included.

**Files:** the four contracts and their README, `artifact_io.py`, the dependency/tool README, `tests/__init__.py`, `tests/helpers.py`, `test_artifact_io.py`, `test_contracts.py`, `.gitignore`, and `docs/development.md`; this section and the same-day log record only Task 2.

- [x] Checked fact ownership, scope, status, and lossless evolution of existing materials against the frozen specification and the Task 2 brief; schemaVersion is `1`, and unknown versions and type errors such as boolean/string are not interpreted in a degraded way; old body text and forms were not modified.
- [x] Per specification 3.2.1, tested the **data contracts** of the main input and the optional views separately: the parser fails on real root/schema/scope errors, and the model schema rejects a missing/invalid main object baseline; for each of the nine views, the structures of unverified + empty references + a specific gap, partial + known references + gap, and available are verified. Actual lookup/derivation of optional sources and baseline authenticity are left to Task 7/8; this task does not fake an exporter run.
- [x] Fixed `kind` to the 32 values listed in the specification and wrote at least one parseable, schema-valid real fixture for each value: `domain-model`, `subdomain`, `bounded-context`, `capability`, `use-case`, `invariant`, `validation-scenario`, `backlog-item`, `stakeholder-requirement`, `software-requirement`, `user-story`, `architecture-building-block`, `architecture-decision`, `verification-test`, `review-record`, `tool-qualification`, `development-log`, `quality-attribute-scenario`, `context-map`, `published-interface`, `aggregate`, `entity`, `value-object`, `factory`, `domain-service`, `policy`, `domain-event`, `integration-partner`, `intended-use`, `risk-control`, `architecture-specification`, `sequence-diagram`; 32 parser positive cases and another 32 schema positive cases actually ran, and an unknown kind fails.
- [x] First created `.github/utilities/requirements.txt` (two direct pins) and the tool environment registration, then created and restored this project's `.venv`. The actual Python is 3.13.15, the six dependencies are locked via `pip freeze`, and `pip check` reports no conflicts; there was no global/media/cloud installation.
- [x] First wrote real-fixture tests: a normal document, the same number in two scopes, a duplicate number within one scope, duplicate YAML keys at any level, unknown status/version, out-of-bounds paths, and missing required fields. The minimal test shape below is kept; the complete cases are in the actual test files:

```python
import tempfile
import unittest
from pathlib import Path
from artifact_io import ArtifactInputError, parse_artifact

class ArtifactIOTests(unittest.TestCase):
    def test_rejects_unknown_schema_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "REQ-001.md"
            path.write_text(
                "---\nschemaVersion: 9\nid: REQ-001\n"
                "kind: stakeholder-requirement\nscope: sample/CTX-001\n"
                "contentState: draft\n---\n# Requirement\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ArtifactInputError, "UNSUPPORTED_SCHEMA_VERSION"):
                parse_artifact(path, root)
```

- [x] Verified the nine fixed views with real model data, keeping the canonical references and source baseline pointers of `sequenceSummary`, `governanceSummary`, `riskSummary`, and `releaseStatus` separately; missing views, missing fields, fabricated passed/approved status, and empty gaps all have negative cases. Only the data is verified; there is no claim that the corresponding optional sources were read.
- [x] First ran to get the initial module-not-found error, then ran a minimal implementation that reads real files without validating them: 6 parser test methods produced 12 behavioral failures; the 4 methods for the four permissive schemas produced 14 failures (both include parameterized subtests; the failure count is not treated as the method count).
- [x] Implemented immutable dataclasses, SafeLoader, the raw YAML node graph and post-normalization duplicate-key checks, local schemas, and exact line numbers. Self-review first added RED tests and then fixed the BOM error location, nested `<<` duplicate keys, and exception normalization for invalid safe-tag values, keeping the original cause; no network access and no execution of body text.
- [x] Rerun of the initial implementation `4b833df`: 143 test methods discovered/executed, 0 skipped, 0 failures/errors; 73 parser tests and 70 schema/Git data tests. 5 actual Python files passed compileall, and 4 documentation examples were actually parsed/validated. The original baseline result is kept here; the new results after the fixes are appended separately; see the [same-day log](../../logs/2026-10-15-ddd-alignment.md#task2) for evidence and limitations.

`helpers.py` only creates real files/Git for tests: `seed_git_repo(root)` writes a README in a temporary directory, commits it with an explicit test identity, and returns the full commit without creating a remote; `write_artifact(root, schema_version, id, scope, kind, upstream, targets, acceptance_ids)` writes actual Markdown in this specification's format. Task 7 extends this file for later trace fixtures. Expected values are given independently by the tests; the parser under test is not called to generate expectations.

**Implemented interface choices:** `parse_artifacts(paths, root) -> tuple[Artifact, ...]` checks duplicate scope/id only within the explicit set; `Artifact.acceptance_ids` stores `scope/id#anchor`, and `acceptances` additionally keeps the full heading ID and the two line numbers. BC uses `developmentRegistration` to reference an existing registration, the model uses `source` / `implementationReports`, and the implementation report separates historical results from applicability via `entries[].execution` / `applicability`. See the [contract guide](../../.github/contracts/README.md) for the fields and the sole example; this is not a compatibility statement for the original fields.

**Exit:** the input contracts of ENH-02 and ENH-06; both the new syntax and the retained old style can be located, and reading blank templates does not require installing tools first.

<a id="task3"></a>
### Task 3: Complete domain artifacts and multiple contexts

**Current status: implementation and the independent review of this scope are complete.** Commit `0aef102` added 18 kinds of optional forms while protecting the parser/schema and the lightweight path. The stale status at the end of the page flagged by the scope review has been corrected; the parent session reran 144 tests with 0 skipped, and an independent consumer additionally used the UC/QAS/Published Interface forms and kept the missing items. See the [maker log for Task3](../../logs/2026-10-15-ddd-alignment.md#task3) for results and limitations; this is not business execution, all-scenario reliability, or human approval.

**Files:** 18 new domain/QAS/tactical forms; the domain, REQ, and verification guides; the necessary hooks into the original REQ/VT forms; the related form navigation in the root README; this task's status and the maker log. The parser/schema, shared methods/roles/prompts, applications, and repository tests were not modified.

- [x] Used `task3-case-input.md`, pinned in advance by the parent session, and kept a copy and digest of the input in the session artifacts: two contexts, one capability, normal/rejected borrowing paths, source rules and INV, scenarios, and two BLs; post-expiry handling and concurrency remain open, and the reference sources were not re-inventoried.
- [x] Independently wrote the actual fields for SD/CTX/CAP/UC/INV/validation/BL using the existing schemaVersion/kind/scope contract; all blank forms are draft; source facts, derived candidates, and questions are kept separate.
- [x] Per the frozen DOMAIN-05/17/18 scope, added QAS, context map/Published Interface, the seven tactical roles, and integration partner; when measures, boundaries, versions, or delivery policies are missing, the questions are kept, and no architecture or guarantee is prefilled.
- [x] The same executor copied the actual distributed forms and applied the pinned input field by field, using the unchanged Task2 `parse_artifact/parse_artifacts` to verify positive cases for all 18 kinds, UC-001 in two scopes, and the negative case of a duplicate number within one scope; the specific targets and local criteria were checked. This is a self-use exercise, not a claim of a new independent consumer or business execution.
- [x] The original lightweight README body text and anchors are kept; in an isolated copy, the owner markers and raw body bytes are identical before and after metadata is explicitly added. Candidate links do not depend on maker materials, and the repository has no business instances or automatic migration.
- [x] Saved records of the limited document checks, real tool regression, self-review, and check-script fixes; the forms/guides and the Task3 status are included in this partial commit. There is no passed-verification conclusion for business/software behavior, QAS measures, or tactical decisions.

**Exit:** This task's documentation scope for ENH-03 is implemented and has completed self-use and limited independent review; the 18 kinds of forms are copyable and structurally parseable, and their source/unknown boundaries are locatable; old materials need not be moved. For the current status of Task4–11, see the following sections; Task12–18, application execution, and the original P3 gates are not closed.

<a id="task4"></a>
### Task 4: Domain interviews, review, and reverse extraction

**Current status: the review of this scope is complete.** `f8df392` added a standalone reverse-engineering method and ten thin prompts, keeping the original six methods and three modes. The independent review found no major issues, and the parent session reran 144 tests on that object with 0 skipped; the three drafts from the independent post-change consumer were also actually parsed. The original baseline remains the correct control observation made before the change; a "baseline" written ad hoc after the change is not used for comparison. See the [maker log for Task4](../../logs/2026-10-15-ddd-alignment.md#task4) for results and limitations; this is not App-native, human, or business-run acceptance.

**Files:** `define-requirements`, `verify-change`, the new `reverse-engineer-domain`, ten interview/reverse/review/impact/distill/glossary/interface/query/backlog/intended-use prompts, and thin routing for planner and plan-feature; navigation in README/AGENTS/agent-support, the current plan, and the appended log. 20 repository files in total; the parser, schemas, forms, tests, and later tools are not modified.

- [x] Reused the recorded independent baseline: five pinned inputs cover incomplete sources, a 2/3 conflict, differences in word meaning, missing interface/evidence items, and deadline pressure. The original baseline control was correct; the seven baseline outputs and their inputs are kept, and no RED or reliability improvement is fabricated.
- [x] Enhanced define with interviews/iterative confirmation, knowledge crunching, glossary/interfaces, incoming ADRs, and optional Intended Use; the new reverse-engineering method records candidates located by actual files/versions, external objects, or supplied excerpts, distinguishes `observed | inferred | uncertain`, does not invent missing original paths/lines, and puts rules before INV.
- [x] Mapped the domain source activities to actual method subsections and the ten thin entry points; verify keeps the complete acceptance inventory, exact targets, and reverse lookup, and adds artifact/BL review and read-only queries. Status, metadata relations, unknown items, and authorization keep the original contract; no method, governance, or architecture form that does not yet exist is referenced.
- [x] The same implementer read the three current methods in full and applied the same five cases, keeping the after-case decision records and three actual filled-form drafts for UC/QAS/PI; the existing parser parsed all three successfully, which neither confirms business facts nor certifies coverage. Neither 2 nor 3 was selected; no source was changed, no notification was sent, and no missing acceptance ID was invented.
- [x] Limited self-use included new domain candidate notes and revision proposals for existing statements/interfaces; the stop points when no ADR/Intended Use original text exists and the actual blank domain inventory were additionally checked. Revisions once real incoming documents exist, full consumer impact, and App-native and human use are untested; general reliability is not inferred from file existence or self-use.
- [x] Checked the current distribution dependency closure, YAML, actual relative links/anchors, and the lightweight path; ran the existing full test suite only once in the existing `.venv` with an explicit repository cwd: `144 tests in 4.654s; OK`, 0 skipped, exit 0. The methods/entry points and this section are saved with this scoped commit; the evidence is in the authorized session artifacts, and the historical P3 conclusions are not upgraded.

**Exit:** This task's documentation scope for ENH-04 is implemented and has passed limited self-use/independent review; reverse-engineered candidates can be traced back to their source, confidence nature, confirmation needs, and stop points. For the status of Task5–11, see the following sections; Task12–18 and Task13's actual behavior/client/human acceptance are not complete, so overall enhancement equivalence, improved reliability, or passed native discovery of the new entry points must not be claimed.

<a id="task5"></a>
### Task 5: BC derivation, review, and safe code generation

**Current status: the review of this scope is complete.** Implementation object `5d39f407630d557b8b0bd51fa12efdde0b5bfef8`, starting from `d7693a8e481dd84effc155378ae16c255c04d9b7`; the independent review found no major issues, and the independent post-change observation of the ten cases used only explicit files. The parent session reran 144 tests on the implementation object with 0 skipped. At that time the Task5 object had eight methods, twenty-one prompts, and three modes; this is not the current inventory after the later Task11. See the [maker log for Task5](../../logs/2026-10-15-ddd-alignment.md#task5) and the [review addendum](../../logs/2026-10-15-ddd-alignment.md#task5-review) for results and limitations.

**Files:** the five existing SR/US/ABB/ADR/VT forms and four guides; SEQ/SWAS/feature/BC-config; specify/implement/verify and the new generate-code; six thin prompts and three code rule files; thin routing for planner/implementer, README/AGENTS/agent-support, this plan's current status, and the appended log; 33 files in total. The reviewer reads the new BC subsections through the original verify entry point, without changing roles or permissions; the original fifteen prompts do not need to duplicate the routing.

- [x] Defined sourced derivation from REQ/UC/INV/CAP/QAS to SR, optional US slices, and independent ABB/ADR and VT plans. Metadata exclusively owns identity/content state/declared relations, while body text explains meaning and criteria; US is not a mandatory bridge, and ABB/VT do not form a role pipeline.
- [x] Provided SEQ fields for known participants, direction, success/rejection/error, and gaps; asynchronous interaction is used only when an actual integration/event contract requires it, and conceptual exchanges are not turned into fictitious services. SWAS references real sources by business/logical/runtime/deployment views and the existing nine views; missing sources stay partial/unverified, and no deployment, risk, or approval is invented.
- [x] `.feature` exclusively owns the Gherkin body, while the VT maintains the real companion/baseline navigation, targets, and independent criteria. The blank form has no business actors or safety-critical tags; actual copies are used only for text/mapping checks, and the Gherkin parser/runner and all behavior are `not-run`.
- [x] The architecture/coding/security rules use limited globs plus an explicit-read fallback when a code path does not match; they distinguish a legitimate composition root from bypassing domain/control logic, follow the actual language/project, and do not pre-build four layers, platforms, or permissions.
- [x] generate-code is a standalone file method: it verifies sources/development inputs, exact read/write directories/all targets, existing content, the planned generation notes, and trace markers; non-empty/out-of-bounds conflicts stop writing, and skipping is not complete generation. Existing code uses implement-task's task/diff/reproduction path; standalone documentation fixes do not wait for application inputs.
- [x] Left self-use decisions and actual filled forms for the same ten cases: 11 form copies (9 Markdown, BC-config, feature); the existing parser parsed 9 drafts, 5 synthetic acceptance criteria, and 3 independent targets; the two exact uncovered items, SR rejection and the ABB constraint, are kept. Actual schema validation of BC/the nine views kept the wrong-owner and non-pinned-baseline negative cases locatable; parser/schema/tests were not modified.
- [x] The actual original owner file stayed at 225 bytes with the same digest as before the change; non-empty and out-of-bounds cases were only preflighted, not written. The missing identity/approval/run inputs of the original ten cases were not unblocked with synthetic data; a separate, explicitly synthetic Markdown link changed only one place with the surrounding bytes kept, and it does not pose as a real target that the original cases did not provide.
- [x] Checked the distribution closure, metadata, and actual relative links/anchors, keeping the old lightweight materials and the original P3 observations; ran the original full suite only once in the existing `.venv` with an explicit repository cwd: `144 tests in 4.977s; OK`, 0 skipped/failures/errors, exit 0. Each contract/entry point and this section are the objects of this scoped commit; the full SHA is recorded in actual Git/the local report.
- [x] Independently reviewed the actual 33-file change; the independent consumer read only the same ten cases, identified missing items and stop points, and did not create another baseline or run the parser/application. The parent session reran the original 144 tests with 0 skipped and exit 0; after the consumer observation, it reconfirmed that the implementation HEAD and the working tree/index were unchanged.

**Exit:** This task's material contract for ENH-05 and the limited self-use/independent review are complete; the original baseline control was correct, and no discipline fix or reliability improvement is claimed. Real code generation, native runners, client/human use, PDF/platform, and approval are all unaccepted and require Task13 and other tasks to meet their inputs/authorization separately. The prerequisite material gate for Task6 is met, and later work proceeds per the plan; partial structural checks are not called completion of the whole enhancement.

<a id="task6"></a>
### Task 6: Formal artifact checker

**Files:** `check_artifacts.py`, `test_artifact_check.py`, the utilities README, the development guide, and the docs/tests instructions; necessary shared line handling/field location stays in `artifact_io.py`, and only verify-change's directly coupled tool notes are corrected. The four schemas, the 32 kinds, dependencies, other methods/entry points, applications, and later tools were not changed.

**Current status: the round-1 fixes and this scoped re-review are complete.** The initial implementation started from `fea6e3f7f5749f223528a0311734e062e392a1b3`, and the two Important findings were fixed in `e0b9fae75a4ea07176e36e4b5b776887ab2a893c`. The parent session directly checked the complete scoped diff, confirmed that both were addressed and that the fix introduced no major issue, and independently reran 143 affected-module methods on that object with 0 skipped. For the actual entry points, see the [original implementation](../../logs/2026-10-15-ddd-alignment.md#task6), the [fix handoff](../../logs/2026-10-15-ddd-alignment.md#task6-fix1), and the [re-review addendum](../../logs/2026-10-15-ddd-alignment.md#task6-review). The original implementation results below keep their historical object and do not serve as post-fix results.

- [x] Wrote failing real-file tests: duplicate IDs, missing headings/metadata, leftover placeholders in formal artifacts, broken files/anchors, invalid baselines, and empty directories; the actual tests use the original `temporary_workspace` and write fixtures only under the authorized `.venv`. Original interface sketch:

```python
import tempfile
import unittest
from pathlib import Path
from check_artifacts import run_check
from tests.helpers import seed_git_repo

class ArtifactCheckTests(unittest.TestCase):
    def test_invalid_base_never_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_git_repo(root)
            report = run_check(root, base_sha="0" * 40)
            self.assertEqual("input-error", report.status)
            self.assertIn("BASE_UNAVAILABLE", {f.code for f in report.findings})
```

- [x] The targeted run showed real behavioral RED: 52 methods/77 assertion failures, 0 errors/skips; the proof is not merely the initial missing-module error. The eight boundaries added during self-review also reproduced failures first before being changed; the complete source and raw output are kept in the authorized evidence directory.
- [x] Implemented full current input, exact historical comparison, explicit exclusions, source locations/both locations for duplicates, the raw-byte read set, and counts. base reads the exact commit/tree/blob, does not guess main/master/HEAD/index, and does not run filters/textconv; new rules are not applied to historical metadata. A read failure must not pose as a deletion; an empty skeleton is `empty`, and a parser failure is `input-error`.
- [x] Tested the real script with the current interpreter via `subprocess.run`, argument lists, an explicit cwd, and `shell=False`; spaces/Unicode, 0/1/2, explicit JSON output and overwrite refusal, 40/64-character Git object IDs, unstaged/untracked files, and the unchanged inventory are all checked. The 60 targeted methods and the original 74 parser methods were all executed, 0 skipped.
- [x] A full regression on the same code object actually executed 204 methods (original 144 + new 60), 0 skipped/failures/errors; the source bytes for 9 independent CLI uses and the full/base checks of the current working tree are all kept. CHECK-14's zero-discovery/all-skipped controls were rejected by the evidence gate. The implementation, positive and negative cases, and this section's registration are included in this partial commit; the actual commit identity and the final documentation/scope check are located through Git and the handoff report; this is not the closing of an independent review.

- [x] Round 1 continued from the saved RED of 143 methods / 26 failures: the original 9 new test methods and their bytes were kept, and only `_formal`'s retention of first-line delimiter candidates and `iter_markdown_lines`'s fence/comment ownership were fixed. The new focused regression discovered and executed 143 methods (checker 65, parser 78) and 173 subtests, 0 failures/errors/skips; input bytes were not rewritten by the tests. The old 204-method and schema results are not rewritten and do not pose as this round's execution.
- [x] The scoped re-review confirmed that both Important findings are addressed; the parent session's independent `test_artifact*.py` run executed 143 methods, 0 skipped, exit 0, in 43.040 seconds. The original test bytes and the historical RED are kept; this conclusion does not extend to a new full suite, other hosts, or business acceptance.

**Exit boundary:** This task's ENH-07 mechanical checks and the review of this scope are complete; this is not acceptance of the whole enhancement, business VT, the coverage graph, or an index (staging-area) hook. The prerequisite gate for Task7 is met, and the user has also selected the source entry point; its implementation and later tasks still proceed within their own scopes.

<a id="task7"></a>
### Task 7: Model views, coverage, and impact checks

**Current status: implementation and the review of this scope are complete.** The original T7-I1–I5 were addressed in the fix1 scoped re-review; F1-N1 was fixed in `23c06b6bc46099c04091c61c036016b88cf4ae99`, and the parent session directly checked the complete partial diff and the model module regression and found no major issue introduced by that fix. The initial 293-method result, fix1's 313-method result, and fix2's partial result each keep their original baseline; see the [original implementation](../../logs/2026-10-15-ddd-alignment.md#task7), [round 1](../../logs/2026-10-15-ddd-alignment.md#task7-fix1), [round 2](../../logs/2026-10-15-ddd-alignment.md#task7-fix2), and the [re-review addendum](../../logs/2026-10-15-ddd-alignment.md#task7-review).

**Files:** `export_model.py`, `check_traceability.py`, `test_model_export.py`, `test_traceability.py`, the necessary shared helpers, the model/verification guides, and the verify method; per the user's choice, `.github/contracts/model-sources.schema.json`, `_templates/config/model-sources.yaml`, and the contract/tool/development guides were added. Only a blank form is provided; no formal project `model-sources.yaml` is created in the maker repository.

- [x] Defined the multi-scope path/pinned-baseline contract for the optional source list, reusing the existing nine-view output without adding result/approval fields. The list does not copy source body text; missing/format/baseline problems in optional sources are kept separate from errors in the required main input. By default there is no network access and no write-back, and `model.yaml` is not read as a source of its own facts. The user selected this entry-point approach separately after resuming; it is not authorization inferred from "continue".
- [x] Defined `write_delivery_fixture(root, omit_software_reject=False)` in `helpers.py`; it writes four real REQ/SR acceptance criteria, two layered VTs, and their criteria, and returns four full delivery IDs. `True` omits only VT-002's software rejection target and does not delete the original SR acceptance criterion. There are also dangling references, the same number with different owners, an unreadable local optional source, a rule change, and stale view copies.
- [x] First wrote tests for exact gaps and deterministic export:

```python
import unittest
from pathlib import Path
from check_traceability import trace_report
from tests.helpers import temporary_workspace, write_delivery_fixture

class TraceabilityTests(unittest.TestCase):
    def test_missing_software_acceptance_is_reported(self):
        with temporary_workspace() as directory:
            root = Path(directory)
            delivery = write_delivery_fixture(root, omit_software_reject=True)
            report = trace_report(root, delivery)
            missing = {f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"}
            self.assertEqual({"sample/CTX-001/SR-001#sr-001-ac-02"}, missing)
```

- [x] Ran `test_traceability.py` and `test_model_export.py` separately and saw failures; implemented inventory-first bidirectional checks that precisely locate source/anchor/layer/criterion and do not count a summary with missing targets as coverage.
- [x] Used a fixture with `sequenceSummary`, `governanceSummary`, `riskSummary`, `releaseStatus`, and quality/QAS references to check that `export_view` keeps canonical artifact/evidence/baseline references; when any optional source is deleted, the corresponding view still outputs `unverified` and a specific gap, and it must not copy body text or map `state` to passed/approved.
- [x] Implemented deterministic ordering, source hashes, and relation export; identical input bytes produce an identical structure, and a source change/hand-edited view fails the check. Views do not copy business body text, results, or approvals, and explicit export does not write back to sources.
- [x] A 2→3 rule change yields the affected REQ/SR/VT/task candidates and reasons; a referrer can be affected even if it did not copy the number. Shared methods own semantic judgment, retention of original results, and new runs; the mechanical graph does not declare business correctness.
- [x] Reran the positive and negative cases and the before/after hashes: the full 293 methods, 0 skipped, keeping the original schema/parser/checker; the raw commands, results, and byte evidence are located through the appended log. The two scripts, tests, methods, and format notes are handed off with this partial commit; the actual commit/clean state is governed by Git and the final report.

<a id="task7-fix1"></a>
**Round 1 scoped fix:** T7-I1 adds the real utility-tree source/baseline, with a missing QAS/tree reported as unverified; T7-I2 protects all parsed nested declarations before a dereference failure, and an invalid location blocks unsafe output; T7-I3 uses a shared literal state machine to recognize actual Mermaid; T7-I4 independently reads its own child run block, multi-column results, and explicit counts without stitching across blocks; T7-I5's public API rejects a None base. Adding a tree to the original missing-measure fixture only isolates the "missing field" condition; the original partial/responseMeasure assertions are kept, and a missing tree has its own failing regression. The new results do not overwrite the old 293-method record.

- [x] Two rounds of scoped re-review closed the original five findings and the new F1-N1. The parent session separately keeps fix1's 243-method result and the `test_model_export.py` result on `23c06b6` of 77 methods, 0 skipped, exit 0, 48.748 seconds; they are not combined into a full-suite result for a single object.

**Exit:** This task's ENH-06/08 mechanical tools and the review of this scope are complete; coverage works without US, the original scope is not deleted, and old results remain bound to the old baselines. When Task7 exited, Tasks8–18 had not started; for the current Task8 status, see the next section; this is not full functional equivalence or a business/application pass.

<a id="task8"></a>
### Task 8: Implementation summary bridge over read-only domain input

**Files:** `collect_implementation_report.py`, `test_implementation_report.py`, `tests/helpers.py`, the report form, the BC/config/model guides, and the handoff method.

- [x] Defined `seed_implementation_fixture(root)` in the test helper: it writes a contract-conformant BC configuration, pinned local domain input, four acceptance criteria/two VTs, and owned code text with source IDs, commits the complete fixture, and returns the object commit. The code text does not run an application. The raw evidence given to the report is, respectively, executed, not-run, baseline mismatch, and absent.
- [x] First tested that a link or commit is not treated as execution:

```python
import tempfile
import unittest
from pathlib import Path
from collect_implementation_report import build_report
from tests.helpers import seed_implementation_fixture

class ImplementationReportTests(unittest.TestCase):
    def test_absent_execution_evidence_is_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            object_sha = seed_implementation_fixture(root)
            report = build_report(root, object_sha, evidence_files=[])
            self.assertTrue(report["entries"])
            for entry in report["entries"]:
                self.assertEqual("not-run", entry["execution"]["status"])
                self.assertEqual([], entry["execution"]["evidenceRefs"])
```

- [x] Implemented a summary of the BC/domain baseline, related SR/US/ABB/VT, code/test identifiers, and actual result entry points; missing evidence does not fabricate a pass, and out-of-bounds input or baseline mismatches are reported as input errors.
- [x] Kept the artifact/evidence/baseline references of sequence/governance/risk/release and quality/QAS together in the report/model fixtures; the nine views still belong to the model, and the report does not add views or stuff governance sources into execution evidenceRefs. For a deleted optional source, an unreadable source, and missing execution evidence respectively, the original `unverified`/specific gap or per-target not-run is kept.
- [x] Checked against sources BC-12/DOMAIN-19 that sequence, QAS, governance/risk, and release associations can all be expressed with artifact/evidence references; the views that original consumers need are not lost because we use a narrower summary, and source body text is neither copied into the summary nor written back to the read-only domain.
- [x] The summary is written to an explicit local output, and the domain source hashes are unchanged before and after; the model only references the summary. Cross-repository commits/write-back are separately authorized operations; without permission, that side effect is stopped.
- [x] Fully reran the tool- and form-related verification and recorded accessibility; the actual SHA of the partial commit and the post-commit state are governed by the final addendum of this round's report; no private logs, credentials, or full chats are saved.

**Local verification (2026-10-16):** A clean worktree at starting point `d30b87b805a133bca54d25ce5887e06071e605c1`. The complete 319-method baseline was kept first, then collection, the report adapter, and source boundaries were completed via real RED/GREEN; the final full suite actually discovered/executed **378 methods**, 0 failures/errors/skips, exit 0, 386.857 seconds. A per-test identity comparison confirmed that all 319 original methods are kept and 59 were added; the historical 313/243/77 results for different objects were not stitched into current evidence.

For the raw commands, cwd, stdout/stderr, exit codes, counts, before/after bytes, and document check entry points, see [this round's log](../../logs/2026-10-15-ddd-alignment.md#task8) and its local session report. The synthetic VT pass/fail only verifies the collector and does not prove a business run; the Windows/Python 3.13.15 results are not extrapolated to Python 3.11 or other hosts.

**Exit:** This round's ENH-12 implementation and scope review are complete; the implementation report is a rebuildable reference and does not become a second approval/result input or an uncontrolled write-back. When Task8 exited, Task9–18 had not started; see each section for later task status; application/platform/remote operations and the complete enhancement still have no pass conclusion.

**Round 1 scoped fix (1/5):** Starting from a clean `7f747e55e480b92822c5599d1e9f54dccba98d9d`, real counterexamples were first obtained for T8-I1/I2/I3, and then only location registration, the lower bound of distinct executed testIds, and rejection of declared criteria inside excluded subtrees were changed. The focused groups went GREEN with 6, 6, and 5 methods respectively; the final full suite actually discovered/executed **395 methods**, 0 failures/errors/skips, exit 0, 460.423 seconds. All 378 original test identities are kept, and 17 were added. See the [fix log](../../logs/2026-10-15-ddd-alignment.md#task8-fix1) for the actual arguments, byte protection, commit object, and report navigation. The subsequent scoped re-review closed the original three findings and handed the new T8-F1-N1 to the second round; the original run is kept here and is not the second-round result.

**Round 2 scoped fix (2/5):** The round-1 scoped re-review judged the original I1/I2/I3 as ADDRESSED and added only T8-F1-N1. Starting from a clean `062e607cde5cd5ecb2a0b2d83bff60ab2940c867`, the export rejection of a valid utility-tree was reproduced first, and then only the context judgment of `reserve_declarations` was narrowed. 2 new round-trip tests went RED→GREEN; the whole model module actually discovered/executed **94 methods**, 0 failures/errors/skips, exit 0, 160.163 seconds. The original 92 model tests and the already-fixed source isolation mechanism are kept; the unchanged 395-method full suite and the collector suite were not rerun; see [this round's handoff](../../logs/2026-10-15-ddd-alignment.md#task8-fix2) for the implementation record.

- [x] The parent session's scoped re-review confirmed that the new T8-F1-N1 is addressed and found no major issue introduced by that partial fix. The independent model-module run on `9a3055a` executed 94 methods, 0 skipped, exit 0, 157.340 seconds; the original three findings remain addressed. See the [Task8 re-review](../../logs/2026-10-15-ddd-alignment.md#task8-review) for the complete entry point; the partial result and the old full suite are not merged into a single result.

<a id="task9"></a>
### Task 9: Human review and tool qualification records

**Status: implementation and the independent review of this scope are complete.** Implementation object `3b818e5902f343a808fe476033256902f0d32a2d`, starting point `002ad73a18700e7c95b21a0fa7d0d84a26f453b5`; the review found no documentation issue requiring a fix. The parent session additionally used the existing CLI to check the retained filled copies and the exact coverage gap, without reopening tasks 1–8 or certifying real qualification; see the [re-review addendum](../../logs/2026-10-15-ddd-alignment.md#task9-review).

**Files:** `docs/ai-tooling.md`, `docs/governance.md`, the four review-record/tool-qualification/intended-use/risk-control forms, and the navigation in the directly related guides and the original review/intended-use/handoff methods. No tool, schema, dependency, or formal business instance was changed.

- [x] Read the recorded conclusions of DOMAIN-08, DOMAIN-20, and FRAMEWORK-03 in the Task 1 pinned matrix; per the actual contract, provided fields for purpose/version/environment, evaluation inputs/evidence/limitations, responsibility, and decision scope, without re-fetching the original repositories or adopting an external QMS policy.
- [x] Filled in a draft lacking a named decision and a record with a locatable independent decision source; the positive case is explicitly an owned synthetic declaration, not a real external/human approval. Four confirmed copies, each missing confirmation or a required subfield, were all rejected by the existing parser; a valid declaration still does not certify identity.
- [x] Completed the optional Intended Use and risk control references within the confirmed source scope; a missing source, responsible policy, or decision blocks only the affected confirmation and does not default to medical/QMS.
- [x] Kept the "Review conclusion/Limitations and notes" of `decision` and the original source fields of `analysis/control/residual`; in the actual export, unknown risk stays partial and an unavailable risk source stays unverified, with no default level/score, risk acceptance, or regulatory certification filled in.
- [x] Review findings, actual decisions, VT results, and logs each have their own owner; the four forms keep only the necessary pointers, with no full chat or ledger format. The fields/guides are delivered with this round's authorized local documentation commit; see the handoff report for the actual commit.

**Local bounded check (2026-10-16):** Per the prepared GOV-01–10, 11 copies of the four kinds of forms were actually copied/filled, and the existing parser/checker checked 13 formal synthetic records; the missing test target in the complete delivery list was located precisely, and the original VT not-run was not rewritten. New drafts after a change in version/configuration/purpose/object do not inherit old decisions; the same number in different scopes stays independent. The 104-file local candidate checked 619 relative links/anchors with no navigation gaps; refusal to overwrite sources and existing results and raw-byte protection each have their own evidence.

For the final inputs and raw results, see the [Task9 handoff](../../logs/2026-10-15-ddd-alignment.md#task9) and `run-03` listed in the local report; the first two bounded runs and the value-refinement records are kept as they are and not merged into a larger acceptance count. The unrelated Python full suite was not rerun, and empty results, structural validity, or agent self-use are not called real human T17, native permissions, or business execution.

- [x] The independent review checked all 20 Markdown changes and two actual contract compatibility risks, with no Critical/Important/Minor findings. The parent session's independent checker/trace CLI kept the 13 synthetic records and the exact uncovered AC-02 item, with input bytes unchanged; these are documentation evidence, not human T17 or qualification certification.

**Exit criteria and current limitations:** This task's documentation scope for ENH-09 and the independent review are complete; content declarations do not certify named persons, qualifications, or approvals. For the later local status of Task10/11/15, see each section; Task12–14, 16–18, real external policy/risk decisions, and application and platform operations have not been run, and the enhancement as a whole is not complete.

<a id="task10"></a>
### Task 10: Optional Git hooks and CI

**Status: local implementation and the review of this scope are complete.** The original I1/I2/M1 and the conditional lock were confirmed by the round-1 independent re-review; Minor T10-F1-N1 was fixed in `02657745e3b7212ebe2b3b58ec7a9a83713317f2` and has completed a direct scoped review. Real project installation, POSIX/hosted platforms, and server-side gates each remain not run; see the [re-review addendum](../../logs/2026-10-15-ddd-alignment.md#task10-review).

**Files:** Python hook entry points, `install_hooks.py`, `test_hooks.py`, the validate-artifacts/tooling-tests workflows, and the tool/CI usage guides.

- [x] By default the installer only proposes, and conflicts with existing hooks/links/hooksPath are not overwritten; it creates only explicitly selected hooks/ownership receipts and does not change Git configuration. Restoration checks bytes/mode/paths; later owner edits or an invalid receipt are conflicts; shared worktree metadata is explicitly rejected.
- [x] Owned local Git fixtures actually executed the installed hooks: valid input, invalid staged content with an unstaged fix, valid staged content with unstaged damage, delete/rename, the actual alternate index of a partial commit, paths with spaces/Unicode/quotes, and a missing interpreter/dependencies all have raw output; direct Python calls do not replace a native commit.
- [x] The two Python entry points call `hook_checks.py`; they build a private snapshot only from real blobs, keeping mode/blob/index tree/the exact base. Complete owner acceptance is left to the shared coverage rules; zero owners and dangling targets are handled separately. The default behavior of the original checker/trace APIs is unchanged, and there is no second check algorithm. Only after testing showed that the Windows Python shebang did not select the project interpreter was the thinnest Git `sh` launcher adopted and tested; commit-msg's `Reviewed-by` policy for managed paths only checks text and does not certify identity.
- [x] The downstream [validate-artifacts](../../.github/workflows/validate-artifacts.yml) is separate from the maker-only [tooling-tests](../../.github/workflows/tooling-tests.yml); the former was tested to be callable in a fixture without maker tests/research/logs. Both declare an explicit cwd, lock, exact PR head/base, and report; the [count runner](../../.github/utilities/tests/run_tooling_tests.py) actually rejects zero discovered and all skipped and propagates non-empty failures. YAML/local shell syntax checks are not a hosted pass.
- [ ] **Reserved for Task11/13, not implemented in Task10:** The actual object of the original ADO fan-out is `.feature`, not a whole-repository overwrite. The proposal registration must still express source scenario → explicit BC target → file scope → individual results; missing targets, no change, conflicts, and failures must not be lumped together as success. This round added no propagation workflow.
- [x] **Original results of the initial implementation:** CLI/native fixtures keep 0/1/2 and Git non-zero rejection; that object had only one final retained+new full suite, with 428 discovered/executed, 0 skipped, 0 failures/errors (397 retained + 31 new methods). The separate zero/all-skipped/fail/pass and exact/invalid base controls are not mixed into this count; this old result must not be called proof of this round's fixes.
- [x] **Round 1 narrow fix:** The shared parser is compatible with the native message argument order of 3.11; the two entry points and the installer share a startup check that keeps the selected absolute path/prefix and rejects a missing or drifted venv/config/dependency before reading artifacts/the index. Exclusive I/O creation is recorded immediately; short writes and write/flush/close errors keep the exact path and a manual recovery state, and later owner edits are not deleted automatically.
- [x] **Round 1 actual verification:** Reused the old 3.11 native RED and the existing isolated interpreters; the new regressions went RED first. The lock update added only the actually verified `<3.13` conditional entry; the 3.11 offline restore installs seven packages, while the 3.13 dry-run still shows the original six. One final minimum-version full suite discovered/executed 439 (all 428 original identities kept + 11 new methods), 0 failures/errors/skips; 3.13 ran only the 42 focused regressions and did not repeat the full suite. The count controls, the Windows loader, and the complete interpreter boundary experiments each have their own evidence; see [this round's handoff](../../logs/2026-10-15-ddd-alignment.md#task10-fix1).
- [x] **Round 2 Minor fix:** When the initial startup validation fails, main explicitly does not write the requested report, keeps the original stdout JSON/exit 2 and `written: false` / `reason: startup-refused`, and no longer imports the validator chain. A valid environment continues to use the original shared exclusive/conflict write protection, and an input error can still be saved to a new report. 3.11/3.13 each executed 9 affected hook/CLI selectors (6 new + 3 retained), all with zero failures/errors/skips; the original 439 full suite and the native environment experiments were not rerun; see the [round 2 handoff](../../logs/2026-10-15-ddd-alignment.md#task10-fix2).

- [x] **Scoped review closed:** The parent session directly checked the complete round-2 partial diff and confirmed that the Minor finding is addressed and that no new finding requiring a fix was introduced; on `0265774`, it independently executed the 6 startup-report regressions with 3.11.15 and 3.13.15 respectively, all with 0 failures/errors/skips. The original 439/42/112 results stay with their own objects and are not stitched into a new full suite.

**Current exit status:** The Task10 local implementation/scope review gate is closed, with no outstanding findings for this task; the [initial handoff](../../logs/2026-10-15-ddd-alignment.md#task10), [round 1](../../logs/2026-10-15-ddd-alignment.md#task10-fix1), [round 2](../../logs/2026-10-15-ddd-alignment.md#task10-fix2), and [review](../../logs/2026-10-15-ddd-alignment.md#task10-review) each keep their own baseline. Nothing was installed or reconfigured in the real working tree or at user/global level; hosted runs, POSIX native startup, and server-side required checks remain not-run; neither ENH-10 as a whole nor Task13 is closed. The next step is only the local proposal implementation of Task11, which does not authorize propagation.

<a id="task11"></a>
### Task 11: Three-way updates and multi-target propagation

**Status: local implementation and the review of this scope are complete.** I1/I2/I3/M1 from the initial review were all fixed in `37cf6700af8f1fad1c60e2fe1135d25573cc1995`, and the scoped re-review confirmed that they are addressed, with no new findings. See the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task11-review) for results and external execution limits.

**Files:** `plan_template_update.py`, `test_template_update.py`, the update-template method/prompt, the template-updates guide, and the proposal workflow.

- [x] Pinned three real roots and UPDATE-01…16, including modify/delete conflicts in both directions, intentional local deletion, add/add, local business files, exact versions, raw bytes, out-of-bounds/exclusions, read failures, and output isolation.
- [x] First proved conflicts and no writes; the following is the minimal criterion in the plan, and the actual regression also checks source versions and all input bytes/file sets:

```python
import tempfile
import unittest
from pathlib import Path
from plan_template_update import plan_update

class TemplateUpdateTests(unittest.TestCase):
    def test_three_way_conflict_is_not_skipped_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base, local, candidate = [root / name for name in ("base", "local", "candidate")]
            for path in (base, local, candidate):
                path.mkdir()
            (base / "AGENTS.md").write_bytes(b"base rule\n")
            (local / "AGENTS.md").write_bytes(b"owner rule\n")
            (candidate / "AGENTS.md").write_bytes(b"new template rule\n")
            result = plan_update(base, local, candidate)
            self.assertEqual({"AGENTS.md"}, {item.path for item in result.conflicts})
            self.assertEqual(b"owner rule\n", (local / "AGENTS.md").read_bytes())
```

- [x] Implemented `changes/conflicts/preserved/sources` of a narrow `UpdatePlan`; each item has the actual three-way paths, versions, raw hashes/explicit absence, and reasons; the default/API does not write, and an explicit new report does not occupy sources or history.
- [x] Narrow optional registration and a safe YAML reader: source scenario → explicit BC/repo/context/local root/version → allowed `.feature` mapping → individual no-change/proposed/conflict/unavailable. Errors do not become success, missing targets/roots/versions are not guessed, and unselected/missing target roots are equally protected from output.
- [x] Added the planned ninth method, the twenty-second thin prompt, the update guide, and a maintainer-only manual proposal workflow; the same-source Python core is not distributed as a downstream runtime dependency.
- [x] Recorded the authorization boundary for real synchronization: there is no apply, clone/fetch, target commit/push/PR, or sync service. Actual cross-repository/platform runs are reserved for Task 13; YAML/local proposals are not evidence of external functional equivalence.
- [x] Actual method self-use: the correct existing method baseline is kept; the positive/conflict/missing-baseline cases got 0/1/2, and the sources were unchanged; this is not an independent agent pressure experiment, human T17, or native client discovery.
- [x] The initial implementation's final minimum-version retained + new full suite, documentation/core consumer dependencies, and append-only protection were checked: 3.11.15 actually 506/506, 0 failures/errors/skips; 3.13.15 additionally ran the 61 new methods, all passed. These results belong to `94b4779` and do not serve as new execution evidence for fix1.
- [x] The initial independent scope review is complete and found T11-I1/I2/I3 and M1; it does not close the task gate.
- [x] The fix1 scoped re-review confirmed that I1/I2/I3/M1 are all addressed, with no new Critical/Important/Minor findings. On `37cf670`, the parent session independently executed 79 proposal module methods, 0 skipped, exit 0, 87.843 seconds; real platform fan-out/PR and POSIX execution remain not-run.

**Initial implementation and verification (2026-10-16):** Starting from a clean `2a8c9a95ad991167756ba7b02ec5727b3100ed2c`,
work iterated in focused TDD steps; self-review reproduced a selected file disappearing after stat, confused source/target diagnostics, a failure to resolve
reserved output locations, and echoing of the raw value of a rejected URI, each going RED first before a narrow fix. To avoid mixing objects, the first full suite, which had not finished, was aborted
and not counted as passing; the final complete 3.11.15 suite actually discovered/executed 506, 0 failures/errors/skips, 838.141 seconds.
All 445 original test identities are kept and actually executed, and 61 were added; there is no pretense that an earlier 445 full suite passed.
See [this handoff](../../logs/2026-10-15-ddd-alignment.md#task11) for the final full suite, raw execution identities, byte protection, and commit result.
The ENH-11 local proposals and the review of this scope are complete; the differences from the original remote clone/push/PR and similar operations remain,
and complete external equivalence must not be declared on the basis of "having a script" or local tests.

**fix1 (1/5):** Starting from a clean `94b47794d66e14dd26d561d7240748a967d784f0`,
counterexamples were first obtained with real files, Windows junctions/parent traversal, local Git, and the CLI. Only I1's unified
case/directory/file prefix check, I2's raw traversal identity verification, and I3's bidirectional output reservation were fixed;
M1 only removed the adjacent duplicate Task11 anchor. Normal explicit sibling roots, independent target results, raw bytes, and
redacted errors are unchanged; the original reports/logs/506/61 and the abort record are all kept. In this round, one final 3.11.15 full suite actually
discovered/executed **524**, 0 failures/errors/skips, 851.172 seconds; all 506 original identities were actually kept and executed,
and 18 were added. 3.13.15 additionally ran only these 18 new cases, which all passed. Input/source/old-prefix protection was checked;
read the actual results/new coauthored local commit from the [fix1 handoff](../../logs/2026-10-15-ddd-alignment.md#task11-fix1);
the subsequent scoped re-review closed all four findings; see the [re-review addendum](../../logs/2026-10-15-ddd-alignment.md#task11-review).
The fix1 executor did not start a subagent/reviewer, change dependencies, or implement Task15, and did not run POSIX/platform/remote propagation.

<a id="task12"></a>
### Task 12: Enhancement candidate, tool distribution, and regression of original behavior

**Files:** `docs/distribution.md`, the exact file/owner manifest `docs/distribution-manifest.json`, the maker-only `.github/utilities/distribute_candidate.py`, the actual test layout `.github/utilities/tests/test_distribution.py`, plus `verification/ddd-alignment.md` and the directly related navigation/status. The manifest is the sole file list; counts and per-file hashes are stored only in the actual receipts/reports.

- [x] Froze the exact file allowlist and component owners based on the actually delivered files; `docs/`, `logs/`, `.github/`, and `.github/utilities/` are not copied recursively. Research/plans, real session/client results, maker tests/fixtures/count runner, maintainer workflows, and Git history are explicitly excluded.
- [x] `test_distribution.py` generates the candidate by copying real files and checks Markdown links/anchors, Python imports, schemas/resources, and the validation workflow closure inside the copy; maker tests/the copy helper do not enter the candidate, and the candidate does not fill gaps from maker paths.
- [x] Verified that basic docs have no Python/import prerequisite; the optional maintenance environment uses the original lock. Business commands stay not configured, and maintenance tools do not replace application tests.
- [x] Redid the applicable T01/T05/T07–T16 local file/CLI paths; the original P3 client/human/release results are not inherited. T17/GUI/native client and the hosted platform remain not run.
- [x] Completed the single retained+new fully counted suite on the selected minimum Python 3.11.15; kept the real copy/verification receipts, file hashes, dirty scope, exclusion list, and raw output. The initial candidate, fix1, and fix2 are saved as the original commit and narrow-scope follow-up commits; nothing is released or pushed, and no PR is opened.

**Fix1 continuation (2026-10-19):** After the original implementer became unavailable, work continued in the same workspace while keeping HEAD `4ec5efbc199f4c61878ef35a0af29167fed0af69`, the original candidate, and the existing evidence. Report output now rejects source-tree/candidate overlap; source and candidate hardlinks are rejected before reading; actual Windows junction races are blocked by handle-relative no-reparse I/O. 8 real file/hardlink/directory-replacement boundary cases went RED on the exact original copier (7 failed; the retained copy-mode overlap case, 1, passed); after the fix, targeted 39/39 and the single minimum-version retained+fix 856/856 passed, 0 skipped/failures/errors. For the exact commands, cwd, environment, report/output hashes, and the new-root candidate copy and post-commit verification, see the [maker-side acceptance record](../../verification/ddd-alignment.md) and the Task12 session-local report. The earlier first-round 848/848 result is kept as is, and the counts are not merged. At that stage, independent scoped review was still pending; this result does not represent business/application/client/platform acceptance, release, or overall parity.

**Fix2 / round2 (2026-10-19):** After fix1 was committed, it was found that the `_verify_receipt` call passed `dirty` and `commit` in reverse order, so although byte verification was valid, `source_commit`/`dirty_scope` in the fix1 receipt were swapped. A new real CLI provenance test was added: it independently queries the expected HEAD and porcelain dirty paths through Git, checks the 132-item count/hashes, and uses a new report outside the candidate. On the exact fix1 commit, only this new case among the 40 focused tests went RED as expected (the other 39 passed); after the minimal fix of the argument order, focused 40/40 and the single Python 3.11.15 retained+new full suite 857/857 passed, 0 skipped/failures/errors. fix1's 848/856 receipts and the malformed verification receipt are all kept; fix2's new single candidate copy, post-commit verification, and correct provenance are recorded separately in the session-local Task12 report and are not merged with old runs. The new commit is a narrow coauthored follow-up after fix1; at that time, independent review, Task13/14, and the external and release gates had not been run.

**Current exit status:** The Task12 local candidate implementation, provenance, and independent fix-wave scoped review are all complete; the manifest is the sole file list. A valid 132-file candidate is a local file-level result and does not represent a release, business/software VT, or overall parity conclusion. Task13 has selected and copied a local technical POC, and its unit/build/controlled-browser subscopes passed; live Flagsmith, code generation/existing-file maintenance acceptance, and the human/App/client/platform gates are still incomplete; Task14 remains partial/blocked.

<a id="task13"></a>
### Task 13: Real behavior and client acceptance

**Status: deferred for the current scaffold-readiness goal; open for full Task13 acceptance.** The user explicitly stated that a ready-to-use scaffold is what is needed now and does not consider the exercise a priority. The isolated copy of the selected Flagsmith/OpenFeature POC and the limited unit/build/controlled-browser evidence are kept; a live showcase is no longer a prerequisite for local candidate readiness. However, the real application behavior, live Flagsmith, code generation/existing-file maintenance, and human/App/client/platform items planned for Task13 are still `not-run`; Task13 must not be called fully complete, and this decision must not be used to close overall parity. See the [Task13 handoff](../../logs/2026-10-19-task13-flagsmith-poc.md) for details.

**Files:** `verification/ddd-alignment.md`, `docs/agent-support.md`, and the authorized development log; the application/target repo is a separate disposable trial object and does not enter the candidate.

- [ ] **Obtain application inputs and authorization first:** The user selects the exercise type/stack/path, native commands/cwd, and the allowed modification scope; without a selection, stop any pass claim for code generation, and do not let the maintenance tools' Python choose on the user's behalf.
- [ ] On the selected trial object, go through domain input → SR → necessary US/ABB → VT → initial generation → actual tests, and perform authorized maintenance on one non-empty existing file. Tests include normal, rejection/no-side-effect, and known-failure cases; keep complete trace markers and raw run results.
- [ ] Reverse-extract a candidate model from that owned object and compare it with the given facts; unknowns/conflicts remain open. After a rule change, locate the affected artifacts/tests, keep the old results and not-run status, and then record the new runs.
- [ ] Run the applicable entry points of the three modes and nine methods in a real new session of the current GitHub Copilot App; record the version, inputs, native invocation, explicit reads, path match/non-match, and prompt availability. Register GUI/unsupported/untested separately, and do not use task subagents to simulate the client.
- [ ] A person performs and records the human path with the same method and inputs, and the result is then compared with the App's fact boundaries/gaps/status. Without actual participation it is not-run; do not simulate a person.
- [ ] **Platform gate:** Once an authorized isolated target and credentials/permissions are in place, try one hook/CI raw failure and success, a multi-target difference proposal, and an explicitly approved update/PR; without platform authorization, keep only the local results, and the corresponding ENH-10/11 items cannot be closed.
- [ ] Write an independent criterion/actual result for each applicable acceptance item, and report the different boundaries of behavior, document checks, approval, and release. A VT with no execution result remains not-run.

**Exit:** Actual behavior evidence for ENH-05/10/11/14. Any missing authorization/environment blocks only the corresponding acceptance; it does not block documentation and tool tasks that can already be done, nor does it lower the final alignment standard.

<a id="task14"></a>
### Task 14: Matrix close-out, versions, and handoff

**Current status: partial / blocked for full parity; not a gate for the user's current local scaffold-readiness goal.** The local plan, specification, and roadmap have recorded the results of Task12's candidate scope review, and the capability matrix has also made explicit its pinned sources/pre-implementation baseline and the gates that are currently still open; however, the line-by-line check back against the sources, the comparison of implementation locations/baselines/results, and the accountable owner's decision on every retained difference that this task requires are not yet complete. Task13's local technical POC unit/build/controlled-browser subscopes have been actually tested, but they are not connected to a real business system or the Flagsmith service; actual participants, client/platform evidence, and authorization are still insufficient, so full equivalence or release readiness cannot be claimed on this basis. The current local candidate's copyable state is checked independently and does not inherit a full parity conclusion.

**Files:** the capability matrix, enhancement acceptance, roadmap, blueprint, distribution, and one maker handoff.

- [ ] Starting from the complete six-repository capability matrix, check each item back against the sources: every row has an applicable criterion, implementation location, baseline, and result; do not inventory only the tools/methods we have already finished.
- [ ] Record the accountable owner's decision on every retained difference and explicit substitution; unconfirmed, untested, or failed items stay visible, and full equivalence is not claimed.
- [ ] Review the version relationships of changed tools/contracts/methods and the normal diff update notes; the new candidate contains no old research, business/test projects, or personal absolute paths.
- [ ] Make explicit the relationship between the original P3 human/client/release items that are not yet complete and this enhancement's evidence; without re-execution they cannot be updated to passed.
- [ ] Use the original log form to save the real Git state, completed/blocked items, raw evidence limitations, and next steps; release separately only after content/license/location/version/maintainer and operation permissions are all confirmed, and do not push by default in this task.

**Exit:** The applicable items of ENH-01 to ENH-18 have factual conclusions. Until this condition is reached, the deliverable is "completed parts and gaps", not "full functional parity with the six repositories".

<a id="task15"></a>
### Task 15: Optional domain-source onboarding

**Depends on:** 2, 6; unlocks Task 12 when complete. **Files:** `setup_domain_source.py`, `test_domain_source.py`, `docs/domain-sources.md`, and the onboarding and BC configuration guides.

**Status: the limited local implementation and the review of this scope are complete.** I1/I2/M1 were confirmed by independent re-review, and I3 fix2
completed its partial fix and scoped review in `4f053d78c7eedd8bd3b490f61b81065414009b72`,
with no outstanding review findings for this task; see the [re-review addendum](../../logs/2026-10-15-ddd-alignment.md#task15-review) for the entry point. The clean starting point of the initial implementation was
`d38e7f6a71ef692c764d085df699a04c6844768b`; this round implemented only Task15 and does not close Task12 or
the later real-environment gates of ENH-15. See [this round's handoff](../../logs/2026-10-15-ddd-alignment.md#task15) for the complete entry point.

- [x] Covered SOURCE-01–12 with owned Git/content fixtures under the project `.venv`: missing fields, exact pinned commit/file digests, wrong-level root/path, non-empty owner targets, duplicates/conflicts/aliases, unavailable/symbolic/non-commit baselines, readOnly, no network authorization, Unicode/junctions, and drift.
- [x] `inspect_domain_source` returns the exact source/location/version/ownership declaration/target/planned operation, 0/1/2, and a re-verifiable preflight; it does not write sources, files, objects, the index, refs, config, or the global cwd. Network input is rejected before any external tool/credential probing, and the original URL is not echoed.
- [x] register edits only the exact existing BC source list and keeps all other raw bytes; a non-empty domain guide in the same repository can be registered as a reference. submodule is a separate optional materialization that additionally requires an exact target and index consent; it does not automatically register the BC, commit, or push; non-empty/partial targets are not skipped as success.
- [x] Actually tested local native `clone --no-checkout`, raw blob writes, and index/gitlink; checkout/filters/source hooks are not used. Consistent SHA1/SHA256 is supported, and mixing them is rejected before writing. Native commands/exit codes, complete/partial state, and manual recovery are recorded; there is no broad rollback/cleanup.
- [x] Completed the implementation and the self-review counterexamples starting from real RED; kept the old schema/dependencies and all original tests, and narrowly extracted the shared path/Git environment and `source_baseline.py` for joint use by the collector and onboarding. Onboarding adds only navigation; methods/prompts/modes remain 9/22/3; for real prerequisites/API/CLI/failures and recovery, see the distributed guide; the code and tests are delivered with this partial commit.

**Local verification of the initial implementation (2026-10-16):** The 44 new methods first produced 64 assertion/subtest failures against a no-op interface,
with 0 errors/skips; the subsequent 3.13.15 GREEN of the 44 methods and the focused self-review boundary results each have their own evidence
and are not stitched into one larger run. In the end, only one minimum-version 3.11.15 retained + new full suite actually discovered/executed
**579 methods**, 0 failures/errors/skips, exit 0, runner 1104.109 seconds. The 524 original identities were actually kept,
and 55 were added; tool inputs did not change during the run. The 12 categories of independent local API/CLI/native receipts and the same-repository registration
additionally keep the real hashes of source/target/index/config/HEAD and 0/1/2; they are not counted in that method number.

**Exit boundary:** The ENH-15 local implementation/scope review gate is closed; ownership/readOnly is not an OS ACL.
No real project onboarding, network, POSIX/platform, application, native client, or human acceptance was done; old results are not rewritten,
and passing this round does not close full functional equivalence or release. Task12 still awaits the applicable prerequisites from 15–18.

<a id="task15-fix1"></a>
**fix1 (1/5):** Starting from a clean `3a99245ee7448f99579399bd9d560f34b536c4ed`,
real local file/CLI/native REDs were first produced for I1/I2/I3/M1 from the initial review, plus safe-read boundary REDs that do not execute risky Git/UNC.
Only the following were fixed: first-onboarding protection against deletion of owner-staged metadata, consistency between the raw bytes obtained for the BC
and the token, pre-command guards in the shared Git/native helper for include/Gitfile/common/worktree,
and write-path overlap in the `.gitmodules` checkout; directly coupled boundaries such as letter case, relative config cwd, and incomplete metadata
each have their own evidence. There was no actual network/UNC access, automatic config expansion, or user/global config modification.

In this round, only one final minimum-version 3.11.15 full suite actually discovered/executed **611 methods**, 0 failures/errors/skips,
exit 0, runner **1443.297 seconds**. All 579 original execution identities are kept, and 32 were added;
the original 55 source methods and their file bytes are unchanged, and source/tool inputs did not change during the run. For 3.13, only
the respective focused RED/GREEN results are kept, and they are not combined into a new full suite. The original 579/55 evidence and the report/log prefixes were not rewritten;
see the [fix1 handoff](../../logs/2026-10-15-ddd-alignment.md#task15-fix1) for the new records.
The independent re-review after fix1 closed I1/I2/M1, and the I3 comment line-continuation issue moved to fix2; this section keeps the original run,
which is not a fix2 result; the fix1 executor did not start a reviewer, Task16, or later/external operations.

<a id="task15-fix2"></a>
**fix2 (2/5, I3 only):** The re-review judged I1/I2/M1 as ADDRESSED. This round started from a clean
`fcd25504053b32b698b74d2462a7349bf3c17d9b` and fixed only the scanner's global joining of backslash line continuations
before deciding on comments, keeping the guard positions and quoted/comment control; an incomplete CR
continuation first gets a typed refusal. After the safe RED with 10 methods/48 subtest failures, the 3.13 new cases went 10/10 GREEN;
as authorized, only 3.11.15 `test_domain_source*.py` was run: **97 discovered/executed, 0 failures/errors/skips,
exit 0, 549.016 seconds** (87 retained + 10 new cases). The 611 full suite/schema/collector were not rerun;
the original 611/32 receipts and prefixes are kept; see the [fix2 handoff](../../logs/2026-10-15-ddd-alignment.md#task15-fix2).
The subsequent scoped review confirmed that I3 is addressed, and I1/I2/M1 were not reopened. On the latest fix object, the parent session used 3.11.15
to independently execute the 10 new cases, 0 failures/errors/skips, exit 0, 21.562 seconds; the original 97/611 results keep their original scope.
There were no actual risky Git/UNC, OS/package, or real project actions; see the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task15-review) for the complete entry point.

<a id="task16"></a>
### Task 16: Document/transcript source adapters and candidate scoring

**Depends on:** 2, 4, 6; unlocks Task 12 when complete. **Files:** the three Python tools in the source table, two tests, the media manifest, the source-extraction guide, and the reverse-engineering method.

- [x] Pinned owned text/transcript samples: named speakers, timestamps, repeated and conflicting statements, open expressions, and missing sources; this round's DOCX uses only explicitly authorized owned synthetic ZIP/XML input, with no real audio or internal interviews.
- [x] Defined `extract_candidates(source, kind)` to output a read-identity envelope and a `candidates` list, recording source file/excerpt/time, candidate type, original basis, and `observed | inferred | uncertain`; `score_candidates(items)` only performs transparent rule-based scoring with reasons and does not pose as a calibrated probability. Empty input keeps the actual read identity, conflicts are not automatically confirmed, and duplicates do not lose their provenance.
- [x] Implemented local Markdown/plain-text, explicit JSONL transcripts, and a bounded DOCX subset; each candidate keeps the file, paragraph/table or turn/timestamp/original excerpt location. A corrupt DOCX returns an explicit input error, and unsupported layouts are rejected rather than partially succeeding; compound/encrypted Office files and unknown adapters are explicitly unavailable. See the [source contract](../source-extraction.md) for scope and limitations; there is no claim that arbitrary office DOCX files are supported. External parsers, SDKs/models, and pinned versions still require separate authorization; the media manifest has no selected packages, and the core lock is unchanged.
- [x] Actually processed owned DOCX paragraphs/tables with the selected Python standard library ZIP/XML; tested corruption, CRC, entities, container path/resource boundaries, and source bytes. No DOCX package is installed, and no real private documents or online conversion are processed; external parsers/audio SDKs and data transmission still require separate authorization.
- [ ] `transcribe_audio.py` is called only after input authorization, an explicit service/model/data scope, and local output are all in place; sending materials unconditionally, picking up arbitrary keys from the environment, and online fallback are all prohibited. A transcription failure keeps the actual error and does not output a fake empty success.
- [x] Candidates go back to the original reverse-engineering method for clarification, confirmation requests, or backlog items as authorized, and never write formal domain facts directly; local adapters, missing items, and forbidden side effects have real-file tests. For audio, only the rejections for authorization/missing items/no adapter are currently tested; real transcription and service failures are not-run, and the rejection contract is not used to check off the previous item.

**Exit:** ENH-16; keep the original adapter/scoring purpose, without extending to the Code/Schema automatic inference engine that appears only in the sources' roadmaps.

**This round's scope:** The offline implementation and its scoped re-review are complete; ENH-16 as a whole is not closed. The 621 retained test sources are not a record of a past 621-test full-suite pass;
this round added source/scoring tests, and the independent RED/GREEN and the final minimum suite each keep their actual objects/counts;
see the [Task16 handoff](../../logs/2026-10-15-ddd-alignment.md#task16) for the entry point.
The single final 3.11.15 suite actually discovered/executed 688 (621 retained + 67 new), 0 failures/errors/skips,
exit 0, 1,799.906 seconds, with test inputs unchanged; this is not a claim that a 621-test full-suite pass existed before.
The actual audio service/model/SDK/data transmission has not been selected or authorized, so ENH-16 and the Task12 prerequisite are not closed on this basis.

<a id="task16-fix1"></a>
**fix1 (1/5, scoped re-review complete):** Starting from a clean `9942e70a59577f3ead9049d006c2bd827a168101`,
real REDs were first obtained for T16-I1/I2/I3/M1. A candidate's complete normalized unit must agree with its classification/all of its markers,
and a substring must not drop qualifiers; the comment context before a Markdown line and whole-file extraction share the same state machine.
Before scoring, the envelope checks the knowable relationships among units/counts/raw line groups/turns/DOCX coordinates,
and an incomplete read range for empty units and bare lists is not mistaken for the total count. Tables without a grid keep a rectangular subset based on the first-row width.
19 regression methods were added, and the AST of the original 67 Task16 test methods is unchanged; the 3.13 focused source (50),
scoring (36), and retained parser (78) tests each passed. The actual result of the single minimum-version retained+new suite is appended separately in the
[fix1 handoff](../../logs/2026-10-15-ddd-alignment.md#task16-fix1),
without relabeling the original 688 or rerunning a 688 baseline. There were no schema/guard/lock/role/runner/dependency/
audio service changes, and the fix executor did not advance other tasks; the audio and ENH-16 gates remain.

fix1's single final minimum run is complete: 3.11.15 discovered/executed 707 (688 retained + 19 new),
0 failures/errors/skips, exit 0, 1,799.438 seconds, with test inputs unchanged. The old 688/67 keep their original baseline;
the scoped re-review of fix object `97d35aa` confirmed that T16-I1/I2/I3/M1 are all addressed,
with no new related findings; the coordinator additionally executed 86 source/scoring methods on the same object, 0 failures/errors/skips.
See the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task16-review) for the complete entry point and the boundaries of each result.
This closes only this review of the offline scope and does not unlock Task12 or actual audio; the next step continues with Task17's local formats.

<a id="task17"></a>
### Task 17: Relationship graphs, SWAS/PDF, and presentation export

**Depends on:** 5, 7, 8; unlocks Task 12 when complete. **Files:** the three render Python tools, the rendering manifest, `test_rendering.py`, the document-exports guide, and the optional workflow.

- [x] First tested an empty model, isolated nodes, broken relations, SEQ success/error paths, SWAS with missing ABB/risk sources, and an existing non-empty output file. Fixtures are pinned; each of the 16 prepared cases has a corresponding independent test; RENDER-15 only confirms that future renderer gates stay not-run and does not pretend that actual formats ran.
- [x] `render_traceability(view)` outputs deterministic JSON/self-contained HTML/SVG based on exact nodes/relations/gaps and requests no external resources by default; empty data is explicitly empty, and no demo nodes are fabricated.
- [x] `render_architecture(inputs, format)` assembles source chapters and limited SEQ diagrams by source ID/baseline; `render_presentation(inputs, format)` provides the required parameterized equivalent HTML/SVG output, without relying on the distribution allowlist to exclude the presentation and without copying the hard-coded content or personal output locations of the original `_gen_ppt.py`.
- [ ] The actual PDF/PPTX renderer/dependencies/templates still await separate selection and authorization; no renderer is currently installed or probed, and `requirements-rendering.txt` declares no unapproved packages. Requesting those formats returns `unavailable`/`not-run` without creating fake format files; the actual engine, signature/parser, non-zero pages or slides, and source content checks remain open, and no floating latest container is used. Every file write requires an explicit new target, and an existing file is treated as a conflict first.
- [ ] Once an authorized renderer is available, check the real binaries with an actual parser/signature, non-zero page or slide counts, and source content checks, and then perform the applicable human/App checks; the current independent structural parsing of local HTML/SVG does not replace these gates. A successful export also does not mean that the SWAS is approved.

**Current status: Task17 fix1 corrected the exact binding between structured source fragments and nine-view evidence, and turned YAML-native scalars that cannot be JSON-serialized into a typed input error; the scoped re-review confirmed that both original findings are addressed, with no new findings.** The JSON/SVG/HTML implementation and the Python 3.11.15 full tool regression are complete; the final suite discovered/executed 787 tests, with 0 skipped, failed, or errored, exit 0; for RED/GREEN and the review entry points, see the Task17 handoff report and [this re-review record](../../logs/2026-10-18-task17-resume.md#task17-fix1-review). Actual PDF/PPTX formats, the corresponding human/App checks, and ENH-17 as a whole are not closed; until every applicable format has real results, full parity must not be claimed from local text/graph output. Task12 still needs Task18 and the candidate delivery.

<a id="task18"></a>
### Task 18: Minimal interaction/usage ledger

**Depends on:** 2, 9; the Task18 local implementation is one of Task12's prerequisites, but Task12 can continue only after an independent scoped review and the candidate delivery. **Files:** `.github/utilities/log_interaction.py`, `summarize_usage.py`, `tests/test_interaction_log.py`, the blank CSV form, the utilities/development/README navigation, and the ai-tooling guide.

- [x] Pinned the v1 CSV fields: record ID, timezone-aware time, tool/version, task/object reference and baseline, an action summary of at most 512 characters, decision/evidence references, and optional usage value/unit/currency; missing usage stays unknown, and no bill is extrapolated.
- [x] Wrote real file/API/CLI tests from 12 expected cases; Task18 base has 17 tests, fix1 adds 11, and fix2 adds 2, covering lock-free read-only snapshots, concurrent/partial source changes, write-path caller attestation, output parent-directory junction races, and the recovery identity after a native create/fstat failure; the current module is 30/30.
- [x] Implemented Python append and read-only summary with explicit path and argument input; the default summary creates no lock or other files; every write path requires an explicit `attest_local_storage`/`--attest-local-storage`. Attestation is only a caller declaration; it does not certify the OS/provider and does not probe sync services. There is no environment/session/billing reading and no provider price lookup; summaries are separated by tool/version/unit/currency, unknowns are not turned into zero, and no savings are claimed.
- [x] Source bytes and file identity are checked before and after writing; summary output locks the Windows parent-directory handle chain, creates the file with exclusive/no-reparse `NtCreateFile` relative to a pinned directory handle, and then rechecks the parent directory, the source baseline, and the output identity. As soon as a native create succeeds, the file identity is cached first; a failure in `open_osfhandle`, the first `os.fstat`, or later I/O returns a recovery identity without automatically truncating, deleting the lock, or silently recreating; if binding cannot be done safely, it fails closed.
- [x] The historical minimum-version suite for Task18 base commit `be2872d` is 804/804, and fix1 is 815/815; fix2's Task18 targeted run is 30/30, and the final retained+new Python 3.11.15 minimum-version suite executed 817/817, 0 skipped/failures/errors, exit 0, `inputs_unchanged=true`. For RED/GREEN, the native create failure, and the recovery test entry points, see the [Task18 fix2 handoff](../../logs/2026-10-19-task18-resume.md#fix2) and the local session artifact.

**Current status: the scoped re-review confirmed that the three Important findings from fix1/round1 and the new Important finding from fix2/round2 are all addressed, and fix2 introduced no new actionable findings.** Task18 targeted 30/30 and the retained+new Python 3.11 suite 817/817 passed. The old 804/815 results and all fix1/fix2 RED/GREEN receipts are each kept and do not overwrite one another; the intermediate two-test receipt `green-create-failure-report-02.json` has exit code 1 and a `KeyError` in its raw output, so it is not success evidence; the final basis is 30/30 and 817/817. For the Minor suggestion to remove `summarize_usage(lock_timeout=...)`, a local call search confirmed that there is no in-repo caller; per the user's instruction, it is deferred as a new-API minor, with no unrelated changes. Task12's local dependencies are complete, and the next step begins candidate delivery; ENH-18 and repository-wide parity remain open; there is no actual provider/billing, real usage, or qualification conclusion. Repeatable record-keeping does not expand into session monitoring, automatic budget control, or a workflow run-state database.

## 5. Specification coverage self-check

| Acceptance | Covering tasks | Key failure cases |
|---|---|---|
| ENH-01 | 1, 14 | Unreadable source, missed existing capability, roadmap treated as implementation |
| ENH-02 | 2, 3, 5 | Duplicate number within the same scope, mixed states, dual sources of truth, old materials overwritten |
| ENH-03 | 3 | Only nouns/directories, INV without a rule source, unknown policy fabricated |
| ENH-04 | 4, 13 | Implementation defaults automatically becoming approved rules, confidence without a source |
| ENH-05 | 5, 13 | Overwriting non-empty files, US forced as a bridge, generating despite a missing stack, not running after generation |
| ENH-06 | 2, 7 | Misspelled mount path, unpinned source, hand-edited/stale model |
| ENH-07 | 6, 10 | Fallback without a baseline, empty scan/zero discovered posing as acceptance |
| ENH-08 | 7, 13 | Exact missing items/dangling references, same number with different owners, old pass automatically carried forward |
| ENH-09 | 9 | Textual "Approved", trailers/roles treated as authentication |
| ENH-10 | 10, 13 | Checking only the working tree instead of the index, scripts/hooks/CI not propagating failures, CI not run |
| ENH-11 | 11, 13 | Three-way conflict skipped yet still reported as success, unauthorized remote propagation |
| ENH-12 | 8 | Pass without evidence, write-back to read-only domain sources |
| ENH-13 | 12, 14 | Exercise/research/internal paths mixed in, candidate depending on excluded files |
| ENH-14 | 12–14 | Agent simulating humans, old App results used as new results, not-run recorded as passed |
| ENH-15 | 15, 13 | Wrong source version, overwriting a non-empty directory, implicit commit during installation |
| ENH-16 | 16, 4, 13 | Conflicting candidates approved, fake empty success when adapter output is missing, uploading materials without authorization |
| ENH-17 | 17, 5, 13 | Demo injected into an empty graph, output overwritten, claiming PDF/PPTX success without rendering |
| ENH-18 | 18, 9, 13 | Duplicate/conflicting records, arbitrarily adding unknown charges, ledger posing as approval |

Execution status is updated according to this plan and the maker log: the limited local deliveries and reviews of tasks 1–12 and Task15–18 are complete; there are currently nine methods, twenty-two prompts, and three modes. Task16 audio remains not-run, and ENH-16 is not closed as a whole; Task17 PDF/PPTX and ENH-17/full parity remain open; Task18 real provider/billing/usage and the overall ENH-18 conclusion remain open, and the Minor API compatibility item is left for the final overall review. Task12's exact file-level candidate and fix-wave review are complete, but this is not a release or full parity. Task13 lacks the required real app/project/stack/location/commands/allowed scope and human/client/platform inputs/authorization and remains blocked/not-run; Task14 depends on the applicable external gate results and has not been run. The original P3 and source inventory conclusions keep their baselines; passing partial tests, a valid candidate, future plans, or the existence of source code must not substitute for complete enhancement acceptance.
