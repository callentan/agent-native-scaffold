# Task13 Flagsmith POC preflight

## Session, task, and Git state

| Field | Record |
|---|---|
| Date and session identifier | 2026-10-19; Copilot project session `40a224f5-795a-4877-af01-159b9070254e` |
| Task source, goal, and authorization | The user selected the existing Flagsmith/OpenFeature POC and explicitly authorized placing a copy in this repository at `poc/flagsmith` for isolated verification |
| Current branch and starting baseline | `callentan-repository-skeleton`, `ee463901725ade1d0cab05261b8c875189fd229e`; the working tree/index was clean before copying |
| Current objects and changes | This session added the isolated `poc/flagsmith/` copy and local plan/status documents; not committed, not staged |
| Source object | Flagsmith POC source branch `master`, pinned commit `beade3c39c3bbb63f14e9c9072e797e24fafc163` |

## Changes in this session

- Copied the 86 tracked files of the pinned source commit to `poc/flagsmith/` and verified each file against its Git blob identity. To prevent the local `core.autocrlf=true` setting from changing the archive bytes, archive conversion was disabled during copying.
- The copy contains no `.git`, ignored dependency trees, worktree directories, local secrets/configuration, or service data. At copy time the source repository also had an untracked design file, `docs/superpowers/specs/2026-10-19-feature-flag-poc-docker-compose-design.md`; to preserve owner content, it was not included in the pinned-commit copy. The source repository was not modified.
- Updated the [enhancement plan](../docs/plan/2026-10-14-ddd-functional-alignment.md#task13), [enhancement specification](../docs/design/ddd-functional-alignment.md), [roadmap](../docs/plan/roadmap.md), and [capability matrix](../docs/research/ddd-capability-matrix.md) to scope the Task13/14 status as partial/blocked.

The source README defines the project as a local Angular/.NET technical POC, not an application connected to a business system; it contains two Boolean flags and 20 synthetic users, with no products, pricing, orders, authentication, or business database. The copy is therefore suitable for limited technical-flow checks and does not prove real business behavior or cloud acceptance.

The documented stack is .NET 10, Angular 20.3.0, and Node 22.12+ or 24; the OpenFeature and Flagsmith versions are pinned by lock files. Verified locally: PowerShell 7.6.6, .NET SDK 10.0.400, Node 24.14.0, npm 11.16.0. The copy's code and configuration were not changed; no DDD business acceptance was created, no new business behavior was selected, no application service was run, and no secrets were used.

## Actual result entry points

| Check and layer | Actual record | Object/baseline | Limitations |
|---|---|---|---|
| Copy integrity | Git archive of the pinned commit; each of the 86 files compared by Git blob hash; 86 files in total after copying | `beade3c39c3bbb63f14e9c9072e797e24fafc163` | Excludes that untracked document in the source repository and the ignored environment dependencies |
| Repository static check | `node scripts/validate-skill.mjs`, cwd `poc/flagsmith`, exit 1; all structure, link, shell, and skill-metadata checks except one reported PASS | The copied pinned commit | Sole failure: the existing non-English comparison document (`LaunchDarkly-vs-Flagsmith-*.md`) tripped the repository's English-only check. The existing document was not modified, and the check as a whole was not described as passing |
| POC Windows helper tests | `pwsh.exe -NoLogo -NoProfile -NonInteractive -File poc\flagsmith\poc\scripts\Test-PocScripts.ps1 -RepositoryRoot <isolated-root>`, cwd is the current repository root, exit 0, output `Test-PocScripts: PASS` | The copied pinned commit; the temporary fixture is in the session-state directory | Covers rejection of invalid actions/paths, forwarding of native arguments and cwd, and propagation of exit code 37; error output from the negative cases is expected, and the fixture was cleaned up by the tests. This test does not run the actual app |
| Application build and unit tests | `not-run` after the initial copy; later appended results are in the next section | `poc/backend`, `poc/backend.tests`, `poc/frontend` | The pinned locked dependencies are restored only into the isolated copy |
| Browser tests and live Flagsmith | `not-run` after the initial copy; live A01–A15 still `not-run` | POC control routes and local Flagsmith configuration | The later Chromium tests are controlled mocks and do not connect to real Flagsmith; there is no local POC config or secret |

## Gaps and next steps (initial preflight snapshot)

| Affected item | Gap/impact | Pending actions |
|---|---|---|
| Task13 application behavior | There is currently only a technical POC copy of the pinned commit; there are no concrete code-generation or existing-file maintenance changes driven by DDD requirements, and build and tests have not been run | First clarify the authorized modification scope for this POC and whether restoring the NuGet/npm locked dependencies only inside the copy is allowed; after restoring, run the Build/Test listed in its documentation. Real Flagsmith A01–A15 require separate configuration and actual testing |
| Task13 manual/App/client/platform | No actual participants, new client sessions, or isolated-platform authorization | Keep `not-run`; an Agent must not simulate a human or a client entry point |
| Task14 matrix and conclusion | The 44 capability groups and the owner-accepted differences have not yet been reviewed row by row | Continue once applicable Task13 evidence is obtained; do not declare full parity or release readiness |

The first half of this record keeps the preflight snapshot taken after copying and before dependency restore; at that point there were no source changes, live service/cloud calls, or commits/pushes/releases. Later restore and run results are recorded only in the appended sections below; the preflight state must not be mistaken for the final state.

## Appended run evidence (2026-10-19)

Within the user-authorized isolated POC verification scope, the lock files were not modified. NuGet/npm dependencies were restored only inside the `poc/flagsmith` copy; no Playwright browser was installed, and the locally available Chromium was used. No dependencies were restored into the source repository, no secrets were configured, and the local Flagsmith service was not accessed.

| Check and layer | Command/result | Object and limitations |
|---|---|---|
| NuGet restore | `dotnet restore Poc.Api.csproj --locked-mode --verbosity minimal`, cwd `poc/flagsmith/poc/backend`; `dotnet restore Poc.Api.Tests.csproj --locked-mode --verbosity minimal`, cwd `poc/flagsmith/poc/backend.tests`; exit 0 | Locked restore; restored the app, the test project, and two child fixture projects |
| Angular dependency restore | `npm ci --no-audit --no-fund`, cwd `poc/flagsmith/poc/frontend`; exit 0, 543 packages | npm reported several deprecated transitive packages and, under the current `allow-scripts` policy, blocked 4 dependency install scripts; these scripts were not approved or run, and the lockfile was not upgraded |
| POC unit tests | `pwsh.exe -NoLogo -NoProfile -NonInteractive -File poc\flagsmith\poc\scripts\Invoke-Poc.ps1 -RepositoryRoot <workspace-root>\poc\flagsmith -Action Test`; the outer cwd is the workspace root; exit 0 | .NET `19/19`, Angular/Vitest `35/35`; the helper sets each project's own cwd internally; only the POC's synthetic fixtures are used, with no connection to Flagsmith |
| POC build | `-Action Build` of the command above; the outer cwd is the workspace root; exit 0 | .NET build `0 warnings / 0 errors`; the Angular production build succeeded |
| Controlled browser tests | `-Action TestBrowser` of the command above; the outer cwd is the workspace root; exit 0, Chromium, 1 worker | `10/10` passed; Playwright intercepts the Flagsmith/API routes and uses a locally controlled frontend server; this is not live provider/targeting/rollout/propagation evidence |
| Skill repository static validator | `node scripts/validate-skill.mjs` still exits 1 | The sole failure is still the existing non-English comparison document tripping the English-only check; this session did not modify that file |

These results supersede the preflight snapshot earlier in this record, which showed "application build and unit tests: not-run", but they prove only these controlled cases in the technical POC. No new business behavior, initial code generation, or maintenance of existing non-empty source files was carried out on the copy; the A01–A15 live Flagsmith and Task13 manual/App/client/platform gates have still not been run. The copy does not represent a real business application.

### Gaps and next steps after the appended runs

- The Task13 technical POC unit/build/controlled-browser subscope has been run; the source application has no concrete new business behavior or maintenance acceptance scope, so no arbitrary code changes were made. To use it to verify code generation/existing-file maintenance, the behavior to implement this time must be provided or confirmed.
- Live Flagsmith acceptance requires an operator with the necessary permissions to provide/configure two dedicated local Projects, Environments, and secrets and to confirm that they are operable; secrets from other environments will not be read or copied, and the cloud will not be accessed.
- Manual, current App native entry-point, client, and platform operations still each require their own actual participants/environment/authorization. The Task14 full matrix reconciliation and the final parity conclusion are not yet complete.

## Current priority: a copyable local scaffold (2026-10-19)

The user stated explicitly that what is needed now is a ready scaffold, and that a real-application showcase exercise is not considered important. This work is therefore treated as a ready-to-use **local candidate**: showcase, live Flagsmith, release, and full parity are not prerequisites for this local delivery; the full-parity status of Task13/14 is neither rewritten nor falsely claimed as complete.

To keep `poc/flagsmith` as the user-authorized local practice copy while ensuring that it does not enter the template, `poc/` has been explicitly registered as an exclusion in the sole distribution manifest, [`distribution-manifest.json`](../docs/distribution-manifest.json).

| Current local candidate check | Result | Scope and limitations |
|---|---|---|
| Build a new candidate from the current working tree | The maker copier `distribute_candidate.py --target ...` returned `status=copied`, exit 0; source HEAD `ee463901725ade1d0cab05261b8c875189fd229e`, dirty scope 92, 132 files copied, 129 source inventory items excluded, 0 findings | The candidate is in `.venv/scaffold-ready-candidate-20261019/`, which `.gitignore` ignores, and does not enter Git; the candidate does not contain `poc/` |
| Re-verify the current candidate | The maker copier `--verify` returned `status=valid`, exit 0; same source HEAD/dirty scope, 132 verified, 0 findings | The receipt `scaffold-ready-candidate-verification.json` is in this session's session-local artifacts; it is not cross-machine evidence |
| Candidate distribution regression | Python 3.13.15 counted runner, `test_distribution.py` 40 discovered/40 executed, 0 skipped/failures/errors; `inputs_unchanged=true` | Covers the exact manifest, candidate bytes/file hashes, Markdown link anchors inside the candidate, copied-only imports, exclusion boundaries, and the Task12 protection regressions. The JSON/raw results `scaffold-ready-distribution-tests.json/.txt` are saved in session-local artifacts |
| Candidate formal artifact check | Candidate `check_artifacts.py --root <candidate>` exit 0, `status=empty`, checked 0, findings 0 | There are currently no formal business artifacts; `empty` is neither business acceptance nor a full Markdown semantic pass |

The local "ready" judgment means only that the scaffold candidate copyable from the sole manifest has a fresh copy, byte-by-byte verification, and a distribution regression. It is not authorization to release/push; it does not prove hosted CI, real client/manual use, business application onboarding, or live Flagsmith, and it does not close audio, PDF/PPTX, provider/billing/usage, or six-repository full parity. Current branch `callentan-repository-skeleton`, HEAD `ee463901725ade1d0cab05261b8c875189fd229e`; this round's documentation/manifest changes are uncommitted, and `poc/flagsmith` is an untracked local practice copy.

A later read-only check found additional owner changes in the working tree of the original Flagsmith source repository; this session did not read, copy, or modify that new content. The isolated copy is still bound to the original pinned commit `beade3c39c3bbb63f14e9c9072e797e24fafc163` and is already excluded from the template manifest, so it does not affect this scaffold candidate.

## P1/P2 landing and a standalone POC copy (after 2026-10-19 16:42)

The user asked to first complete P1/P2 according to the template blueprint and then provide a standalone clean copy for POC use. Checked against the 38 historical first-version paths listed in the current [repository blueprint](../docs/design/repository-blueprint.md): all 38/38 exist in the main scaffold. The current deliverable content is defined by the sole, enhanced [`distribution-manifest.json`](../docs/distribution-manifest.json), 132 files in total, rather than by a separate 38-file mode. The manifest excludes `poc/`, so the Flagsmith exercise is not mixed into the scaffold.

The final standalone copy is placed in the user-provided POC root as `agent-native-scaffold/`, a sibling of `flagsmith/`; the two are not merged, and neither is inside the scaffold working tree. It is a clean snapshot of the manifest and contains no `.git`, virtual environment, POC app, dependency trees, or local secrets/configuration. The old P1/P2 `docs/agent-support.md` is still explicitly excluded by the manifest because it contains real historical client observations; README/AGENTS keep the generic activity entry points. Therefore **all 38/38 blueprint paths are present in the main working tree**; the portable enhanced copy follows the manifest's privacy boundary and cannot be described as "a verbatim copy of each of the 38 historical paths".

The first copier `--target` run inside the working tree returned `SOURCE_SCOPE_CHANGED` and produced no successful copy receipt. Review of the copier implementation showed the root cause: the target directory was inside the `poc/` exclusion area of the source Git working tree, so creating the target changed the Git dirty/inventory scope that the copier checks before and after writing; a temporary helper was also inside that source tree. The 132-file copy left by the failed run later passed a read-only `--verify`, but its nested `_templates` caused the main working tree's formal artifact checker to misidentify those blank forms as formal artifacts, and the result became `invalid`. The copier was therefore used to create the final sibling copy in the authorized POC root outside the working tree, and the duplicate copy inside the working tree, created only by this session, was deleted; neither the Flagsmith POC copy nor the source code repository was deleted or modified. The main working tree's final formal artifact check returned to `empty`.

The final copy receipt and verify receipt are both in this session's session-local `files/`: source HEAD `8406fad1e40555b5a5351801343251e7d1ef5e32`; copy: 132 files, 261 exclusions, 0 findings, exit 0, SHA-256 `3265FD9AF4FA187A864FE0E73B5A0C6618323A406CB61AD2AA5DA8EAA7A796E9`; post-copy verify: 132 files, 129 exclusions, 0 findings, exit 0, SHA-256 `AF0FC71100F421695EC4BCBC480E1559F9AA082EFE2AAEFC7842C7FA5F26260B`. The `poc-scaffold-final-verification.json` of the earlier duplicate copy inside the working tree is an intermediate result and has been superseded by the final verify receipt of the external sibling. The current local `check_artifacts.py --root <maker root>` result is `empty`, checked 0, findings 0. `test_distribution.py` is 40/40 with 0 skipped/failures/errors and `inputs_unchanged=true`; the receipt `poc-copy-final-distribution-tests.json` has SHA-256 `057E45CB836BEC9EF6BDB8B3491BB1E6948F36806304F8FBF467DA98323372C0`. These session-local reports are not cross-machine evidence.

The final copy is the sibling `agent-native-scaffold/` in the user-provided POC root, separate from `flagsmith/`. Git was not initialized, the copy was not added to the scaffold working tree, and the current uncommitted Docker Compose work in the Flagsmith source repo was not changed. It is a clean template snapshot available for local POC adoption, not a merge automatically applied to the Flagsmith repo. If the copy is moved elsewhere, Git is initialized, the template is merged into Flagsmith, or the copy is handed over to other maintainers, it must be re-verified against the new target path and baseline; the local receipts do not constitute release authorization.
