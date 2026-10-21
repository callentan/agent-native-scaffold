---
applyTo: "src/**,app/**,apps/**,lib/**,packages/**,services/**"
---

# Follow the real project's coding conventions

Read these rules explicitly whenever you modify any real code. Follow the actual project's conventions, and implement only what the task and confirmed behavior sources cover.

## Scope of these rules

- The `applyTo` patterns are only an initial match and do not enumerate every code location.
- The rules apply equally to project directories that do not match. Code does not have to be moved into `src/`.

## Read first

- First read the actual language/tool versions, native layout, nearby implementation, and formatter/linter/test configuration.
- Follow that project for naming, casing, exceptions, async, resource disposal, and test locations. Do not apply a one-size-fits-all language template.
- Read structural constraints separately in the [architecture rules](architecture.instructions.md). Follow the [test rules](tests.instructions.md) for tests and the [security rules](security.instructions.md) for security boundaries.

## Implementation

- Implement only what the task and confirmed behavior sources cover.
- Keep domain terms, responsibilities, and interface semantics. Do not add concurrency, expiry, retry, or boundary policies for implementation convenience.
- Make inputs, outputs, errors, and forbidden side effects explicit.
- Do not swallow errors. Do not disguise unfinished work with empty implementations or hard-coded success return values.
- Bound each change by a reproducible problem and the smallest relevant diff. Keep user code and unrelated formatting.

## Portable scripts and checkers

- Scaffold scripts must behave identically on Windows, Linux, and macOS.
- Take paths from explicit arguments, project-relative resources, or the standard temporary directory. Do not hard-code personal directories, drive letters, or virtual environment layouts.
- Encapsulate necessary OS adaptation at the file-lock/startup boundary, without changing DDD meaning.
- Checkers serve artifact structure, references, and coverage. Do not make fixed-drive detection, native directory-handle auditing, or protection against malicious concurrent file replacement a prerequisite for running them.
- Keep basic protections, such as explicit errors and never overwriting existing output.

## Traceability

- Use the project's existing comments, test annotations/identifiers, or task records to locate the full owner-qualified acceptance criterion and the real code location. Do not tag only an ownerless `AC-01`.
- Do not add a traceability SDK, and do not copy a set of requirements/statuses into the code.

## Dependencies, builds, and evidence

- Base dependency/API usage on the current project and its versions.
- Without a selected version or authorization to install, stop at the gap. Do not upgrade or install automatically.
- Builds, checks, and tests must use the commands, cwd, and output locations in the [actual registration](../../docs/development.md#project-registration).
- Record the real check scope, exit code, and per-item results. A file name, zero discoveries, or a not-run state cannot prove the implementation correct.
