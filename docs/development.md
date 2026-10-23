# Development guide

**The maintenance tools and the business application are registered separately.** The optional local maintenance tools use Python; this does not choose a tech stack for any downstream business application. The business application is still not configured: there is no application project, dependency, or run command. Filling in project materials and maintaining documentation can continue; application builds and tests do not apply to the current blank skeleton, and this does not mean the application has passed verification. If a business or software behavior VT has been planned, it stays `not-run`, and its reason records the missing object or environment.

<a id="maintenance-tools"></a>
## Repository maintenance tools (not a business application)

| Project information | Current value |
|---|---|
| Identifier and scope | `artifact-maintenance`: local parsing, artifact/coverage checks, impact candidates, derived reference models, implementation summaries, read-only three-way/multi-target proposals, optional source manifests, local domain-source preflight and explicit onboarding, document/transcript candidate scoring, local relationship-graph/architecture/presentation exports, an explicit interaction/usage ledger, and optional hook/documentation-CI integration; not a business application |
| Relative location and native layout | Modules are in `.github/utilities/`; JSON Schemas are in `.github/contracts/` |
| Tech stack | Python 3.11+; PyYAML 6.0.2 and jsonschema 4.23.0 are pinned and tested, and at runtime both only need to be importable |
| Environment | A Python environment chosen by the caller (venv, conda, or the system interpreter all work); `.venv` is only an example name. No global packages are installed, PowerShell 7 is not required, and no downstream application is configured |
| Dependency sources | The [direct dependency manifest](../.github/utilities/requirements.txt) and the [actually resolved lock](../.github/utilities/requirements.lock); the original six pinned versions are kept, and `typing-extensions`, which `referencing` needs on Python `<3.13`, is locked separately according to the actual metadata/installation results: seven entries are selected on 3.11 and the original six on 3.13 |
| Interfaces and boundaries | [Module invocation and error codes](../.github/utilities/README.md), [data contracts and complete examples](../.github/contracts/README.md), [source candidates and scoring](source-extraction.md), [local document exports](document-exports.md), [minimal interaction ledger](ai-tooling.md#interaction-ledger); the ledger does not connect to vendor/billing services and contains no actual application |
| Usage prerequisites | Users must check their local interpreter and installed dependencies; maintainer regression tests and run history are not distributed with the candidate and are not downstream runtime prerequisites |

The scripts target Windows, Linux, and macOS; platform differences are limited to the necessary lock and Git hook launch adapters. The checks serve DDD artifact structure, references, acceptance coverage, and derived results; they do not perform fixed-drive detection, native directory-handle audits, or isolation against malicious concurrent path replacement. Inputs/outputs are specified by arguments, and resources are read by project-relative location; temporary snapshots and test fixtures are allocated by `tempfile`, and nothing is written to the interpreter installation directory.

Git subprocesses keep `GIT_EXEC_PATH`, which the host's Git installation needs; like the system PATH, it is provided by the runtime environment. They still clear inherited overrides of the repository, index, and object locations. Do not drop Git's own helper location to isolate the repository context, and do not hard-code the Git installation directory.

All commands below use the repository root `.` as the cwd, and the Windows examples use `.venv\Scripts\python.exe`; on other hosts or in other environment locations, substitute the actual project interpreter (for example `.venv/bin/python`) instead of copying the example layout. There is no need to activate the environment or modify the global PATH; the scripts do not require the environment to be named `.venv`.

| Operation | Actual command | Raw output location and limitations |
|---|---|---|
| Initialize the local environment | `python -m venv .venv` | Current terminal; first check that the Python used is 3.11+ |
| Restore direct dependencies for the first time | `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.txt` | Current terminal; run only after the manifest has been created |
| Restore locked dependencies | `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.lock` | Current terminal; restores the local environment to the locked versions |
| Check installed versions | `.venv\Scripts\python.exe -m pip freeze` | Current terminal; compare the actual versions with the lock; the lock file is not updated automatically |
| Check environment consistency | `.venv\Scripts\python.exe -m pip check` | Current terminal; exit 0 cannot replace behavior tests |
| Tool source syntax | `.venv\Scripts\python.exe -X utf8 -m compileall -q .github\utilities` | Current terminal; checks only the syntax of the distributed source code and does not replace behavior verification |
| Full formal-artifact check | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_artifacts.py --root .` | JSON stdout; no report is saved automatically; empty/exit 0 does not mean a business pass |
| Exact historical comparison | Add `--base <verified full commit ID>` to the row above | The verification target is still the complete formal inventory of the current files, not only changed or staged content; exits 2 if the exact object is unreadable |
| Explicitly save a check report | Add `--report <authorized new JSON path>` to the check command | Relative paths resolve against the root; the parent directory must exist; any existing file is rejected; source files and history records are not rewritten |
| Complete delivery coverage | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_traceability.py --root . --delivery <full acceptance reference>` | Repeat `--delivery` for each delivery item; JSON on stdout, optional `--report`; scope is not inferred back from VTs, and VTs are not run |
| Impact candidates for rule changes | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_traceability.py --root . --base <full commit>` | `--task <actual scope/id>` may be repeated; old and new dependencies are merged; semantics are judged manually |
| Read-only model derivation | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\export_model.py --root . --scope <actual project/context>` | JSON stdout; sources are selected from the optional `model-sources.yaml`; exits 2 if the primary input fails |
| Check an existing model | Add `--check <existing .json/.yaml/.yml>` to the row above | Read-only recomputation; exits 1 on source changes/manual edits and 2 on input errors; does not repair the sources or the model |
| Explicitly create a new model | Add `--output <authorized new .json/.yaml/.yml>` to the read-only derivation command | Mutually exclusive with `--check`; exclusive create, no parent directory creation, and the output must not be a registered source path |
| Collect an implementation summary | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\collect_implementation_report.py --root . --object <full local commit>` | JSON stdout; repeat `--evidence <VT relative path[#run anchor]>` per actual selection; multiple BCs require `--scope`; VT commands are not run |
| Explicitly create a new implementation report | Add `--output <authorized new .json/.yaml/.yml>` to the collect command | Exclusive create, no parent directory creation; does not overwrite existing files or take over missing declared sources; does not register a model source automatically |
| Three-way template update proposal | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --base <actual old root> --local <actual local root> --candidate <actual candidate root>` | JSON stdout; `--base-version/--local-version/--candidate-version` may each be added to verify exact versions; a missing old root is an error; nothing is applied |
| Scenario proposal for explicit BCs | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --registration <actual local registration.yaml> --target <explicit ID>` | Repeat `--target` for each target; reads only existing local roots and returns per-target results; does not clone/fetch or copy the model/whole repository |
| Explicitly save an update proposal | Add `--output <authorized new .json>` to the proposal command | Exclusive create, no parent directory creation; must lie outside all registered sources/targets, including missing and unselected targets; conflict exits 1, unavailable/input-error exits 2; saving the report does not count as applying it |
| Check the actual staged snapshot | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\hook_checks.py pre-commit --root .` | JSON stdout; index/blob/tree identity, all owner acceptance criteria, and explicitly empty coverage; an exact `--base` and a new `--report` may be added; nothing is auto-fixed or staged |
| View the optional hook installation proposal | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\install_hooks.py --root . --python "<absolute path of the actual project interpreter>" --hook pre-commit --hook commit-msg` | No writes by default; reports targets/conflicts and the shared metadata scope; actual installation additionally requires authorization for this specific target and `--apply` |
| Check a registered local domain source | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\setup_domain_source.py --root . --config bc-config.yaml --source-id <explicit ID>` | JSON stdout, read-only by default; the source root/relative path/fixed baseline come from the original BC fields; 0 ready, 1 conflict, 2 unavailable |
| Explicitly register one local domain source | With the [exact source arguments](domain-sources.md#cli), inspect first, then add `--operation register --apply --owned-target --expect <this run's preflight>` | Maintains only the domainSources of the specified existing BC; does not copy domain files, stage, or commit; stops if there is no project configuration |
| Optional local submodule | With the same source arguments, choose `--operation submodule --target <exact relative target>` and inspect first; to apply, also add `--apply --owned-target --index-consent --expect <this run's preflight>` | The [native operation](domain-sources.md#submodule) writes .gitmodules/local config/module metadata/index, independently of BC registration; explicit local sources only; no network/commit/push |
| Local document/transcript candidates | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\extract_source.py --root . --source "<explicit local source>" --kind <markdown/text/transcript/docx>` | JSON stdout; [exact formats and bounded DOCX](source-extraction.md#formats); not a formal artifact; a non-existent `.json` inside the root may be given as `--output`; no parent directory creation |
| Transparent candidate scoring | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\score_candidates.py --root . --input "<explicit candidates.json>"` | JSON stdout; a new `--output` may be added; [public factors and ranges](source-extraction.md#scoring); does not decide acceptance or override conflicts |
| Audio unavailability check | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\transcribe_audio.py --source "<explicit local audio path>"` | Currently exits 2: authorization/missing inputs/adapter unavailable; does not read audio or environment secrets, call services, or write a transcript; [later separate gate](source-extraction.md#audio) |
| Append an explicitly provided interaction record | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\log_interaction.py --log "<absolute local CSV>" --record-id "<id>" --time "<ISO 8601 with time zone>" --tool "<name>" --tool-version "<version>" --task-ref "<task reference>" --object-ref "<object reference>" --object-baseline "<object baseline>" --summary "<short factual summary>" --attest-local-storage` | For the arguments and the optional decision/evidence/usage fields, see the [ledger contract](../.github/utilities/README.md#interaction-ledger); appends only to an existing log, and missing usage stays empty; the caller must confirm a non-network, non-synced local path; 0 success/replay, 1 input/ID conflict, 2 path/attestation/lock/recovery error |
| Read a usage summary | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\summarize_usage.py --log "<absolute local CSV>"` | JSON stdout; the API/CLI are truly read-only by default, read once, and create no lock sidecar or other files; units/currencies/tools/versions are kept separate |
| Explicitly create a new summary file | Add `--output "<absolute new .json>" --attest-local-storage` to the same summary command | The parent directory must already exist; after the caller confirms a non-synced local path, the file is created exclusively with the standard library and no existing file is overwritten; on partial failure, what was created is kept and its recovery state reported; no Windows directory handles are required |
| Local relationship graph | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_traceability.py --root . --scope <actual project/context> --format <json/svg/html>` | By default, the actual text goes to stdout; drift between the sources and a persisted model must be checked; with no data, the result is explicitly empty, and no demo is fabricated |
| Local architecture/SEQ document | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_architecture.py --root . --scope <actual project/context> --format <html/svg> --source "<actual reference>" --baseline <fixed object>` | Each source has a matching baseline; renders the actual source sections/nine views and limited SEQ diagrams; does not add deployment, risk, or approval content |
| Local parameterized presentation | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_presentation.py --root . --scope <actual project/context> --format <html/svg> --source "<actual reference>" --baseline <fixed object>` | The selected source sections drive the slides; not a fixed deck; HTML/SVG does not pass itself off as PDF/PPTX |
| Explicitly create an export file | Add `--output <authorized new file of the same format>` to the commands above | Exclusive create, no parent directory creation; [isolation/rejection/exit contract](document-exports.md#cli); unavailable PDF/PPTX creates no file |

These commands do not execute artifact bodies, referenced commands, or applications, and do not install hooks, CI, media, or platform packages; they do not depend on the maintainer tests excluded from the downstream candidate. Each tool's results are governed separately by its [discovery rules, statuses/counts, JSON, and baselines](../.github/utilities/README.md#artifact-checker), [coverage](../.github/utilities/README.md#traceability), [model](../.github/utilities/README.md#model-export), [implementation summary](../.github/utilities/README.md#implementation-report), and [read-only update proposals](template-updates.md); these check/derivation/proposal APIs write no files. The separate apply API of [source onboarding](domain-sources.md) is additionally bound by the exact target, preflight, and authorization, and gains no permission from readOnly or existing configuration. The source manifest stores only [local references and fixed baselines](../.github/contracts/README.md#model-sources); it is not an execution manifest. Reports reuse the owned runs of existing VTs and do not maintain a separate execution input; a collection exit 0 may include not-run, exit 1 means a fail was collected, and exit 2 is an input/output error. Model integrity, structural coverage, a successful collection, or a clean proposal does not equal a business pass or completed propagation. Replace angle-bracket arguments with the actual inputs for this run.

The source-onboarding preflight token is bound to the bytes actually read/parsed; apply stops if it differs from `--expect`;
index consent for a new submodule cannot undo an owner's already-staged deletion of `.gitmodules`.
The [Git invocation environment](domain-sources.md#git-config-boundary) clears inherited repository overrides and uses the selected root as the
discovery ceiling, without borrowing an ancestor repository; the repository's own configuration takes effect by Git's native rules. Network/real-project
onboarding still requires separate authorization, which readable materials or local fixture results do not grant.

Local exports reuse the primary inventory, source selection, raw baselines, and report/model checks above,
without creating a separate schema, result store, or execution input. JSON/SVG/HTML use the existing stdlib,
and the [rendering manifest](../.github/utilities/requirements-rendering.txt) adds no dependencies.
The actual PDF/PPTX engine, installation, signature/parser, non-zero pages/slides, and source-content/human/App checks
remain separately not-run; when no renderer is selected, global packages are not probed and the format is not silently switched.

For optional installation, recovery, and native runtime boundaries, see the [hooks guide](../.github/hooks/README.md).
The thin Windows launcher uses the `sh` bundled with Git and starts only the exact project interpreter; PowerShell 7 is not required.
The installer does not overwrite owner hooks or change `core.hooksPath`, and refuses to silently affect sibling worktrees.
Each hook launch, before reading artifacts/the index, only confirms Python 3.11+ and that PyYAML and jsonschema are importable;
venv, conda, or the system interpreter all work, and no fixed version or `pyvenv.cfg` is required. If these conditions are not met, the hook refuses explicitly
and does not fall back to another interpreter. An installation I/O failure keeps the per-path recovery state of fully/partially
created files and does not automatically delete later owner content; recovery must verify ownership according to the hooks guide.
The downstream documentation workflow calls only distributed modules; the maker repository's regression workflow/count runner is not distributed.
Copying YAML does not establish required checks; hosted runs and server-side configuration need separate authorization and actual evidence.
The template proposal workflow is likewise used only manually on the maker-repository maintainer side and requires exact local inputs that already exist on a trusted runner;
it is not a downstream runtime dependency, includes no target checkout/branch writes/PR, and the local implementation does not make it an executed platform capability.

Maker-repository regression runs with the current interpreter:

```text
<project-python> -B -X utf8 .github/utilities/tests/run_tooling_tests.py --start-directory .github/utilities/tests --top-level-directory .github/utilities --report <new-report.json> --raw-output <new-raw-output.txt>
```

The report's parent directory must already exist; outputs are specified by this invocation, and nothing is written to a fixed machine directory. `tooling-tests.yml` discovers and runs the tests separately on Windows, Ubuntu, and macOS and keeps each platform's artifacts separate; this includes regressions in which every CLI starts from a non-repository cwd, uses paths containing spaces or non-ASCII characters, and uses no fixed fixture directory. The run steps of all three workflows use the actual interpreter returned by Python and venv, without hard-coding `bin/python` or `Scripts/python.exe`. Template proposals still need a preconfigured `self-hosted, template-proposals` runner, but it is not restricted to a Linux label. A matrix configuration does not mean every platform has run successfully; take actual results from this run's report or from Actions.

<a id="creation-inputs"></a>
## When a project can be created

Generate or onboard a project with that project's native tools only after the user has explicitly chosen the target project, tech stack, and location, authorized creation, and provided a sufficient task goal, behavior basis, constraints, and valid development inputs. First check the target directory and existing changes; do not choose a language, install dependencies, or create a sample application automatically.

Existing projects keep their original paths and native code, test, and dependency layouts; they are not forced into `src/`, and no unified test directory is required. A new project may go directly in `src/` or in `src/<project>/`; both are only location options; neither one is an existing project.

<a id="project-registration"></a>
## Subproject location and command registration

This section registers only the **downstream business application**, which is still not configured; the maintenance tools above are not an application subproject. After a real project has been created or onboarded, copy the following set of registration tables for each subproject. Each set corresponds to one project; do not mix working directories between commands. Record every local location as a path relative to the repository root; resolve and confirm it in the current workspace before running, and do not record personal absolute paths.

| Project information | Current value |
|---|---|
| Subproject name or identifier | Not configured |
| Subproject relative location | Not configured |
| Native layout (actual locations of source, tests, and configuration) | Not configured |
| Tech stack, tools, and versions | Not configured; to be selected by the user |
| Environment prerequisites and dependency sources | Not configured; do not record credentials |
| Basis for the task/user selection and its scope | TBD |

| Operation | Actual command | Actual working directory (repository-relative path) | Raw report/output location | Applicability conditions and limitations |
|---|---|---|---|---|
| Install dependencies | Not configured | Not configured | Not configured | No project yet; do not run |
| Build | Not configured | Not configured | Not configured | No application yet; not applicable to the current documentation task |
| Run | Not configured | Not configured | Not configured | No application yet; do not run |
| Test | Not configured | Not configured | Not configured | No application yet; a planned behavior VT stays `not-run` |

These "Not configured" values are not executable commands. Do not use empty scripts, commands that only print success, or commands without real checks as placeholders. When filling them in, confirm the command, cwd, report location, and purpose against the real project; a zero exit code does not mean acceptance passed. Record the check scope, discovered, executed, and skipped counts, and the actual result according to the [verification guide](../verification/README.md#execution).

A report location points only to actual output or an authorized report entry point; if none exists yet, write "To be configured". Add ignore rules for files produced by project tools according to their real locations; never ignore formal requirements, verification documents, or development logs.

<a id="document-checks"></a>
## Documentation checks available now

The formal-artifact checker can check its [restricted Markdown syntax](../.github/utilities/README.md#checker-format), metadata, IDs, placeholders, and local links; when there are no formal artifacts, it explicitly outputs `empty`. It is not a scanner for all documents or a language CI; ordinary READMEs/guides, coverage, and semantics must still be checked for each task. In particular, valid files and anchors must not be taken to mean that [acceptance coverage and semantic impact](../verification/README.md#coverage-check) have been checked.

If an existing local tool is used for checks, record the actual tool, command, working directory, object baseline, and the entry point to the raw results; do not treat external scripts on the author's machine as capabilities shipped with the repository. Manual checks record the artifacts read, baselines, observations, and limitations, without fabricating commands. Documentation checks cannot replace business acceptance or software behavior runs.

<a id="troubleshooting"></a>
## Missing items and troubleshooting

| Missing item or problem | Known basis and impact | Inputs to add or next step |
|---|---|---|
| Business application environment and commands not configured | The maintenance-tool environment is listed separately; there is currently no business application, so documentation tasks are not blocked | After the user decides to create an actual project, complete the business application registration; do not reuse the tool stack to choose the application on the user's behalf |
| Other issues | TBD | TBD |

When a command is unavailable, inputs conflict, or the environment requirements are not met, report the specific reason; do not silently switch tools or record a not-run item as a success. After a command, project, or acceptance baseline changes, reassess result applicability, and keep pending re-review items and not-run items in the [log](../logs/README.md).
