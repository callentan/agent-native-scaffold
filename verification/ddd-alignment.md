# Task12 candidate verification record

This is the maker-side record for the Task12/ENH-13 local candidate scope. `DIST-01`–`DIST-20` are the prepared Task12 case labels, not product REQ/SR IDs, a formal downstream VT, or a business-result table.

## Scope and basis

- **Task:** [Task12](../docs/plan/2026-10-14-ddd-functional-alignment.md#task12), under the approved single-repository enhancement plan.
- **Candidate contract:** [distribution guide](../docs/distribution.md) and its single file/owner manifest.
- **Starting source object:** `a8554d005c4c3a73d6587598e0eca531ad391aea`, branch `callentan-repository-skeleton`; the starting index and worktree were clean.
- **Candidate boundaries:** no maker research/design/plan/history, test modules/fixtures/count runner, client observations, Git history, session artifacts, or populated business/result artifacts. `src/` remains its README only. Hooks are optional and are not installed by copying.
- **Validation layer:** real local file copies, candidate-only imports/resource loading, and local maintenance-tool behavior. No application, external service, hosted CI, client-native discovery, human participation, publication, or release was performed.

The case results below describe this candidate mechanism only. They do not establish overall functional parity, ENH-14, a business/software VT pass, reviewer approval, or publication readiness.

## Candidate cases

| Case | Local candidate observation |
|---|---|
| DIST-01 | Explicit manifest uses exact present files and one owner component per entry. The copy receipt compared each listed source/candidate byte stream and SHA-256; source commit, dirty scope, and allowed output roots are recorded. |
| DIST-02 | An existing nonempty target returned a conflict before replacement; owner bytes remained unchanged. |
| DIST-03 | Basic guide files were read in an isolated standard-library-only process without importing the optional runtime dependencies. |
| DIST-04 | Project, stack, application commands, and formal business instances remain unconfigured; `src/` contains only its guide. |
| DIST-05 | Every shipped Markdown local path and fragment was checked within the actual copy; no link was resolved outside the candidate. |
| DIST-06 | All copied runtime modules imported from the candidate-only utility path with the selected locked environment. The deliberately incomplete copy failed with `CONTRACT_ERROR` for its absent candidate schema rather than using the maker checkout. |
| DIST-07 | The shipped validation workflow's referenced runtime/lock are in the manifest; the maker test runner is not a workflow dependency. Hosted workflow execution was not attempted. |
| DIST-08 | Maker tests, fixtures, count runner, copier, and maintainer workflows are excluded; the maker regression module remains outside the copied tree. |
| DIST-09 | Optional hook files and installer are present, while the candidate has no Git metadata or installation receipt; copy did not alter the source checkout's Git configuration. |
| DIST-10 | The copied manifests declare the selected Python 3.11+ runtime and locked dependencies. No package was installed or upgraded. |
| DIST-11 | Audio authorization refusal and PDF/PPTX `unavailable` refusals were exercised. Actual audio, PDF, and PPTX processing remain `not-run`. |
| DIST-12 | Candidate CLI distinguished empty, valid, invalid, exact-full-commit, and invalid-base inputs. An invalid/short base did not fall back to HEAD. |
| DIST-13 | A four-owner fixture mapped all canonical REQ/SR targets; a separate omission produced only the intended `SR-001-AC-02` gap, and a dangling target retained its exact source location. |
| DIST-14 | Candidate model/report tools preserved source baselines, nine-view gaps, report ownership, `not-run` execution, and unverified applicability. A conflicting model output was refused without changing fixture inputs. |
| DIST-15 | Candidate source inspection, read-only update proposal, text extraction/scoring, HTML/SVG presentation, and read-only ledger summary were exercised on controlled local fixtures. Ledger append was not performed: the authorized fixture root is under a OneDrive worktree and cannot be truthfully attested as nonsynchronized storage. |
| DIST-16 | The actual copied files were scanned for maker/session paths, internal results, and credential-like markers; no such content was found in the bounded candidate scan. |
| DIST-17 | The applicable local portions of original T01/T05/T07–T16 were re-exercised with their stated inputs or conditions. This does not repeat or inherit historical App/client/human results; actual semantic human/App use remains `not-run`. |
| DIST-18 | A controlled exact-base fixture changed the limit 2→3 and surfaced the affected source chain. Historical source objects remained intact; the fixture's business VTs stayed `not-run`. Historical maker result applicability was not re-certified. |
| DIST-19 | Candidate verification produced path-specific hash-drift and missing-resource findings; it did not fall back to maker files. |
| DIST-20 | Repeated copies and verification over identical source inputs produced stable file identities/results without changing allowlisted source bytes or adding timestamps/random/demo content. |

The initial Task12 candidate-focused run was Python 3.11.15: **31 discovered, 31 executed, 0 skipped, 0 failures, 0 errors**, exit 0, with `inputs_unchanged=true`. Its single initial retained+new full-suite run was Python 3.11.15: **848 discovered, 848 executed, 0 skipped, 0 failures, 0 errors**, exit 0, duration 1753.313 seconds, with `inputs_unchanged=true`. The runner receipt and raw output are `task12-evidence/final-full-311-report.json` and `task12-evidence/final-full-311-output.txt`; SHA-256 values and command details are in the session-local `task12-report.md`. These original results remain unchanged and are not combined with fix1 counts.

The exact manifest candidate was copied to the controlled ignored `.venv/task12-fixtures/candidate` root. Its receipt binds source HEAD `a8554d005c4c3a73d6587598e0eca531ad391aea` plus the recorded dirty scope; 132 listed files were copied and raw-byte verified, and 41 actual Git-inventory paths were explicitly excluded. The final precommit candidate verifier, after direct status updates, reported 132 verified files and no findings (`candidate-final-verification.json`). Copy and verification receipts, including exact byte hashes, are retained in the session-local Task12 report. The receipt distinguishes the original Git commit from this dirty worktree snapshot; it does not claim that Git blob bytes are interchangeable with working-tree bytes. A committed-source verification is recorded separately after the single scoped commit.

## Fix1 report containment and filesystem boundaries

The original fix1 implementer session was unavailable. The takeover preserved the same branch, starting HEAD `4ec5efbc199f4c61878ef35a0af29167fed0af69`, original candidate target/receipt, and all existing Task12 evidence. A separate new target `.venv/task12-fixtures/candidate-fix1-20261019` and separate receipts were used; the original candidate remained 132/132 files with 0 receipt mismatches.

Tests covered verify-mode report-under-candidate rejection without a candidate inventory change, report-under-source-tree rejection, and the preserved copy-mode report-equals-target rejection. Hardlink cases used actual `os.link` files for both source and candidate; reports asserted `HARDLINK_REFUSED`, invalid/not-copied outcomes, and no candidate hash for rejected hardlinks. Windows 10 local junction races were executed at source file open, candidate file creation, and candidate verification read boundaries. The baseline tests observed the original failures, including the source marker copied into the candidate, an output file created through the destination junction, and the external marker hash from verification through the candidate junction. Corrected runs assert those bytes are not copied/read into results and the external marker remains unchanged.

- Exact pre-fix copier: starting HEAD `4ec5efbc199f4c61878ef35a0af29167fed0af69`, Git blob `8b3153c54377f302d9053558d706d780fda769b6`; the eight target tests were 8/8 discovered/executed, 7 expected failures, 1 retained copy-mode check passed, 0 skips/errors. This RED is against the exact committed script, not the earlier partial-WIP RED receipts.
- Focused GREEN: Python 3.11.15 / Windows 10 build `10.0.26200`; `test_distribution.py` 39/39 discovered/executed, 0 skips/failures/errors, exit 0, `inputs_unchanged=true`.
- Final retained+fix GREEN: Python 3.11.15, 856/856 discovered/executed, 0 skips/failures/errors, exit 0, duration 1238.078 seconds, `inputs_unchanged=true`. This is the only full-suite run for fix1; the initial 848/848 remains a separate historical result.
- New-root copy: source HEAD `4ec5efbc199f4c61878ef35a0af29167fed0af69` plus five recorded dirty paths; 132 listed files copied, 41 actual Git-inventory paths excluded, manifest SHA-256 `24eabdd69f5b7df5d621e5f7e7a629d8818a842fae1899c7b0179426c0711660`. A direct file-by-file check found 132/132 candidate files matching the copy receipt with 0 mismatches/missing files. The subsequent post-commit verification is retained in the session-local Task12 report.
- Exact report/output hashes, commands, cwd, executable, full path inventory, and dirty scope are in `task12-evidence/fix1/takeover-20261019/` and the append-only session-local `task12-report.md`. The runner-reported first 37-method focused attempt had one test-only `KeyError`; that failed receipt is preserved but not counted. The corrected 39/39 focused report is the applicable focused result.

## Open gates and handoff

| Gate | State and reason |
|---|---|
| Task12 independent scoped review | Pending; local implementation, full suite, and candidate receipts are not independent review. |
| Final retained+new Python 3.11 suite | Fix1 pass: 856 discovered/executed, 0 skips/failures/errors; the initial Task12 848/848 receipt remains a separate historical run. Runner input hashes and raw output are in the session-local report/evidence. |
| Human/App/native-client and T17 observations | `not-run`; no human or client simulation was performed. |
| Real application, generated code, and application behavior | `not-run`; no application project, stack, or command was selected. |
| Hosted CI, native POSIX hooks, required checks, external platform operations, and publication | `not-run`; no platform configuration or external action was authorized. |
| Audio, PDF/PPTX, provider/billing/actual usage | `not-run` or unavailable; no service, renderer, provider, actual usage, or charge was invoked. |
| Historical results and applicability | Preserved under their original maker records/baselines; not copied into the candidate or upgraded to current passes. |

Task12's local implementation is handed off for independent scoped review; the single local commit, committed-source candidate verification, and complete session-local report preserve the final source identity and evidence. Keep the separate not-run gates visible. The local candidate is not a release or a declaration that ENH-01–18 are all satisfied.
