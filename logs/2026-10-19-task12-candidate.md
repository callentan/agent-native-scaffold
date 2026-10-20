# Task12 candidate implementation handoff

<a id="session"></a>
## Session, task, and Git state

| Field | Record |
|---|---|
| Date and session identifier | 2026-10-19; the runtime did not expose a session ID. Task artifacts are kept in the existing session-local `ddd-alignment-execution` area. |
| Tool/environment | Implementer; Python 3.11.15 Windows venv for candidate regression. |
| Task source | User-authorized Task12 under the [DDD functional-alignment plan](../docs/plan/2026-10-14-ddd-functional-alignment.md#task12); acceptance scope is ENH-13 and the 20 prepared DIST cases. |
| Scope and non-goals | Exact file-level portable candidate, source/target byte provenance, candidate-only imports/resources, downstream validation, and applicable local T01/T05/T07–T16 paths. No release, application, client/human simulation, provider, audio/PDF/PPTX processing, hosted CI, or publication. |
| Branch and starting baseline | `callentan-repository-skeleton`; `a8554d005c4c3a73d6587598e0eca531ad391aea`. The worktree and index were clean at entry; all Task12 edits are this task's changes. |
| Current commit and uncommitted scope | The minimum-version retained+new run and single scoped Task12 local commit are complete. The exact SHA, committed-source verification, and clean final repository status are recorded in the session-local Task12 report; no remote operation was performed. |

## Changes

- Added [distribution guide](../docs/distribution.md) and the sole explicit file/owner inventory [manifest](../docs/distribution-manifest.json). The maker-only copier/verifier reads exact paths, refuses an existing target, hashes bytes, captures local Git commit/dirty scope, and does not initialize Git or install anything.
- Added maker regression coverage at `.github/utilities/tests/test_distribution.py`; it is not in the candidate. Updated only direct candidate navigation away from `docs/agent-support.md`, which contains historical client observations excluded from distribution.
- Replaced a real maker commit used as a sample baseline in the contract guide with a clearly synthetic fixed-format example; no source schema or historical acceptance result was changed.
- Added this handoff and the maker-side [Task12 verification record](../verification/ddd-alignment.md). Neither is in the candidate.

## Verification evidence

Evidence files below are in session-local `task12-evidence`; they are not repository files or cross-machine evidence.

| Check/layer | Actual result and location | Baseline/limitation |
|---|---|---|
| Test-first manifest RED | One test discovered/executed; one expected assertion failure because the inventory was not yet present; report `red-distribution-test-report-02.json` and raw `red-distribution-test-output-02.txt`. | Python 3.11.15; source HEAD `a8554d0…`; no product code existed yet. |
| Real isolated copied-fixture RED | The copied checker ran with isolated imports and failed `CONTRACT_ERROR` on the deliberately absent candidate schema. The candidate report is under ignored `.venv/task12-fixtures/red-missing-schema-02/red-report.json`; its SHA-256 is recorded in the full Task12 report. Source/copy bytes were identical for the two copied modules. | No maker checkout/test import could supply the schema. This is a controlled negative fixture, not a candidate success result. |
| Candidate-focused GREEN | Python 3.11.15; 31 discovered/executed, 0 skipped/failures/errors; exit 0; `inputs_unchanged=true`. Final focused report/raw output: `distribution-target-report-08.json` / `distribution-target-output-08.txt`. | Source baseline `a8554d0…`; covers the actual candidate copy, local source fixtures, exact-base CLI, optional refusals, and output protection. |
| Retained+new full suite | Python 3.11.15; 848 discovered/executed, 0 skipped/failures/errors; exit 0; `inputs_unchanged=true`; 1753.313 seconds. Report/raw output: `final-full-311-report.json` / `final-full-311-output.txt`. | Exact base `a8554d0…`. This was the single final full run before the local commit. |
| Precommit candidate copy/verification | `copied`; 132 manifest files copied and byte/hash compared; 41 actual repository inventory files excluded; final precommit verifier `valid`, 132 verified, 0 findings. | Receipt `candidate-copy-receipt.json`; reports `candidate-precommit-verification.json` and `candidate-final-verification.json`; source identity is parent HEAD `a8554d0…` plus the exact dirty scope and per-file raw-byte hashes. Candidate files are worktree bytes; Git blob normalization is not inferred. |
| Committed-source candidate verification | `valid`; 132 candidate files verified, 0 findings, against the single committed source snapshot and clean worktree. | `candidate-committed-source-verification.json`; exact commit identity and receipt hash are in the session-local Task12 report. |
| Dependency consistency utility | `not-run`; the existing Python 3.11.15 environment has no `pip` module, so `python -m pip check` could not execute. | No package was installed. Candidate module imports and exact direct dependency versions were exercised by the targeted suite. |

Two earlier attempts are retained, not overwritten or counted as passing evidence: the first selected the embedded Python 3.11 runtime rather than its existing dependency venv (`input-error`, `No module named 'yaml'`); a first `-I` fixture launch then omitted the explicit candidate import path, and an intermediate receipt-reading assertion used a field the checker does not emit. The corrected runs above are the usable RED/GREEN evidence.

## Gaps and next steps

| Scope | State / reason |
|---|---|
| Task12 candidate-local acceptance | Candidate-focused suite and final full suite passed; committed-source candidate verification is separately recorded. |
| Task12 independent scoped review | Pending; self-review and tests are not independent review. |
| Actual PDF/PPTX and audio service | `not-run`/unavailable; no renderer/provider, package install, data transfer, or service call was authorized. |
| Ledger writer and actual usage/billing | Writer not run because this worktree is under OneDrive and no non-synchronized local attestation is available. Only read-only synthetic summary and the no-attestation refusal were checked. No real usage or charge was read. |
| App/client-native discovery, human T17, real application, hosted CI/required checks, platform and publication | `not-run`; no simulation, external operation, or release authorization was inferred. |
| Historical P3 and earlier Task outcomes | Remain at their original baselines; they are neither candidate content nor current Task12 results. |

Task12 was saved in one scoped local coauthored commit. The complete session-local `task12-report.md` records its SHA, candidate/exclusion inventory, committed-source verification, raw outputs, hashes, and protection evidence. The next action is independent scoped review. Do not push, create a PR, release, or close the remaining gates.

<a id="fix1-takeover"></a>
## Task12 fix1 takeover

The original fix1 implementer session was unavailable. Work resumed without resetting, cleaning, stashing, or replacing the existing workspace. The takeover base was `4ec5efbc199f4c61878ef35a0af29167fed0af69` on `callentan-repository-skeleton`; the initial uncommitted scope was limited to `distribute_candidate.py`, `test_distribution.py`, and `docs/distribution.md`. The pre-existing `.venv/task12-fixtures/candidate` still matched its original 132-file receipt, and the earlier `task12-evidence/fix1` artifacts were left in place. Takeover-specific reports are in the separate child directory `task12-evidence/fix1/takeover-20261019`.

The fix1 regressions use real local files, `os.link` hardlinks, and Windows directory junction swaps around the source-read, output-create, and candidate-read boundaries. The exact committed pre-fix copier at the starting HEAD was loaded from Git for the RED control: 8 tests discovered/executed, 7 expected failures, 1 retained copy-mode target/report-overlap pass, 0 skips/errors. The controlled report showed the old verifier writing a report into its candidate and reading the external marker through the candidate junction; the source junction fixture copied the external marker, and the destination junction fixture created output outside the allowed root. This is intentional RED evidence, not an acceptance pass.

After the narrow fixes, the distribution module ran **39/39**, with 0 skips/failures/errors and exit 0. The single final Python 3.11.15 retained+fix suite ran **856/856**, with 0 skips/failures/errors, `inputs_unchanged=true`, and exit 0. The original Task12 848/848 run and its receipt remain a separate historical result. A first 37-method focused attempt exposed a test assertion `KeyError`; that failed report/output was preserved, the test was corrected to read the actual JSON report, and only the later 39/39 run counts as focused GREEN. Exact commands, cwd, input hashes, report/output hashes, raw findings, and the new-root copy plus committed-source verification are recorded in the append-only session-local Task12 report. This log and the maker verification record remain excluded from the candidate.

The single scoped coauthored local commit and post-commit candidate verification are recorded in the session-local Task12 report; independent scoped review is next. Human/App/client, application, hosted platform/required-check, audio, PDF/PPTX, ledger-write attestation, publication, and release gates remain `not-run` or unavailable. No Task13/14 or external operation is authorized here.

<a id="fix2-provenance"></a>
## Task12 fix2 / round2 provenance correction

After fix1 commit `d3efa8ffbcc133c78cb68d545827a32e05128720`, inspection of the actual committed-source verification JSON found `provenance.source_commit=[]` and `dirty_scope` set to the commit SHA. The byte verifier had returned `valid`, but the provenance receipt was not usable. The call in `main` passed `(dirty, commit)` to `_verify_receipt`, whose signature expects `(commit, dirty)`.

Fix2 adds a real CLI test over the current checkout and a real copied candidate. Expected `HEAD` and the exact Git porcelain dirty-scope pairs come from separate Git subprocesses, not copier helpers; the test asserts 132 file hashes and source/candidate/report separation. Exact-base RED ran the 40-method distribution module with exactly one expected failure, 0 errors/skips. After only the argument-order change, focused GREEN was **40/40**, and the sole final Python 3.11.15 retained+new minimum suite was **857/857**, 0 skips/failures/errors, `inputs_unchanged=true`. The original 848 and fix1 856 runs remain separate.

The malformed fix1 receipt/report is preserved. Fix2 creates a new unique candidate target and reports, then verifies that candidate against the fix2 commit; the corrected commit, clean dirty scope, receipt hashes and old-candidate preservation are documented in the session-local Task12 report. Independent scoped review is next. No Task13/14 or external operation is authorized.

<a id="task12-fix-wave-review"></a>
## Task12 fix-wave independent scoped review

The independent reviewer inspected the exact fix range
`4ec5efbc199f4c61878ef35a0af29167fed0af69..cda3cfd8d0391324abfc5865654614a2012afece`
and confirmed all findings ADDRESSED: verify-report output overlap; reparse/junction
TOCTOU for source/copy/verify; hardlinked source/candidate files; stale plan-level
suite status; and the committed-source provenance argument order. No new issue was
found in the fix wave. The review is limited to this candidate-boundary fix work;
it is not a release or full-parity review.

The provenance correction has an independent real CLI regression comparing the
receipt to separate Git HEAD/porcelain subprocess results. After fix2, a new
candidate copy and committed-source verification report `source_commit` exactly
`cda3cfd8d0391324abfc5865654614a2012afece`, `dirty_scope=[]`, 132 files verified,
41 excluded inventory paths and 0 findings. Parent independently rehashed all132
source/candidate file bytes. The malformed fix1 provenance report remains in
session-local evidence but is explicitly superseded; no prior report was erased.

Task12 author final minimum Python3.11 suite is 857/857, zero failures/errors/skips,
with49 current input hashes verified by the parent. These are maker/test/candidate
results, not reviewer runtime execution, application VT, human use or publication.
The earlier intermediate report with exit1/raw `KeyError` is retained as failed,
not treated as green; final supported receipts remain the subsequent40/40 focused
and857/857 full run.

Task12 local candidate scope is closed. Still not run/open: Task13 actual project/
stack/environment/commands, human/App/client/native discovery and authorized
platform/hosted CI; Task14 full capability reconciliation/publication; audio,
PDF/PPTX, provider/billing/real usage, required checks and release. The deferred
`summarize_usage(lock_timeout=...)` compatibility Minor remains for final branch
triage. This log does not authorize external actions or declare ENH-01–18 fully
equivalent.
