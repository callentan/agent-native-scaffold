---
applyTo: "**/test/**,**/tests/**,**/Tests/**,**/*.test.*,**/*.spec.*,**/*_test.*,**/test_*.*"
---

# Test change conventions

**Read these rules explicitly whenever you modify any test, even if automatic matching did not trigger.** Only actual runs count as evidence.

## Scope of these rules

- These comma-separated path/name patterns are only an initial match. They do not cover every language or project naming scheme, and they do not prescribe code or test directories.
- Extend `applyTo` to fit the real project when adopting it.

## Before changing tests

- Keep the project's actual test layout and existing style.
- First read the target acceptance criteria, the corresponding VT, and [verify-change](../skills/verify-change/SKILL.md).
- Start from the full acceptance scope and check gaps across it, not only existing tests.

## Test content

- Map each test to specific behaviors, boundaries, and forbidden side effects, and use full acceptance IDs.
- When requirements change, re-review the source and expected outcome first. Do not hide differences by changing assertions or deleting targets.

## Commands and evidence

- Take commands, tools, environment, and cwd from the [actual development registration](../../docs/development.md#project-registration) and the actual project. Do not assume a runner or invent build/test commands.
- Record only actual runs and per-item evidence. Zero discoveries, all-skipped, or a zero exit code alone cannot prove that acceptance passed.
- When the object or environment is missing, write `not-run` with the reason.
- Document checks do not replace business or software runs.

## Maintenance-tool regression tests

- In regression tests for the maintenance tools, keep positive and negative subprocess cases that use real files, local Git objects, and the current interpreter. Run them with argument lists, an explicit cwd, and `shell=False`.
- Do not mock Git stdout. Do not compute expected identities, counts, or states from the implementation under test.
- Inject an explicit I/O boundary only where an OS failure cannot be produced safely. Distinguish actually observed results from injected ones.

## Fixtures and platforms

- Fixtures use the standard temporary directory. They must not require a fixed `.venv` under the checkout or the interpreter installation directory to be writable.
- Resolve the canonical path of the temporary directory on the host.
- Generic script behavior must run in CI on Windows, Linux, and macOS. Separate cases only for genuinely platform-specific adaptation details.
- Do not hide missing functionality by skipping whole categories.
- CLIs should be launchable from another cwd and cover spaces, non-ASCII paths, and non-default environment locations.

## Checker counts and regression records

- The `checked_count/attempted_count` of the [formal artifact check](../utilities/README.md#artifact-checker) are not test discovered/executed/skipped counts.
- Regression records must list runner counts separately and reject a "success" with zero discoveries or all tests skipped.
- Compare the raw bytes of inputs before and after the check, and list report output separately.
- Maker-repository tests are not distributed with downstream candidates and are not a prerequisite for running the downstream checker.
