---
applyTo: "src/**,app/**,apps/**,lib/**,packages/**,services/**"
---

# Follow the real project's coding conventions

The patterns are only an initial match and do not enumerate every code location. Read these rules explicitly whenever you modify any real code; they apply equally to project directories that do not match, and code does not have to be moved into `src/`.

- First read the actual language/tool versions, native layout, nearby implementation, and formatter/linter/test configuration. Naming, casing, exceptions, async, resource disposal, and test locations follow that project; do not apply a one-size-fits-all language template.
- Implement only what the task and confirmed behavior sources cover. Keep domain terms, responsibilities, and interface semantics; do not add concurrency, expiry, retry, or boundary policies for implementation convenience. Read structural constraints separately in the [architecture rules](architecture.instructions.md).
- Make inputs, outputs, errors, and forbidden side effects explicit; do not swallow errors or disguise unfinished work with empty implementations or hard-coded success return values. Bound each change by a reproducible problem and the smallest relevant diff; keep user code and unrelated formatting.
- Scaffold scripts must behave identically on Windows, Linux, and macOS. Paths come from explicit arguments, project-relative resources, or the standard temporary directory; do not hard-code personal directories, drive letters, or virtual environment layouts. Encapsulate necessary OS adaptation at the file-lock/startup boundary without changing DDD meaning. Checkers serve artifact structure, references, and coverage; do not make fixed-drive detection, native directory-handle auditing, or protection against malicious concurrent file replacement a prerequisite for running them. Keep basic protections such as explicit errors and never overwriting existing output.
- Use the project's existing comments, test annotations/identifiers, or task records to locate the full owner-qualified acceptance criterion and the real code location; do not tag only an ownerless `AC-01`. Do not add a traceability SDK, and do not copy a set of requirements/statuses into the code.
- Base dependency/API usage on the current project and its versions. Without a selected version or authorization to install, stop at the gap; do not upgrade or install automatically. Builds, checks, and tests must use the commands, cwd, and output locations in the [actual registration](../../docs/development.md#project-registration).
- Tests follow the [test rules](tests.instructions.md), and security boundaries follow the [security rules](security.instructions.md). Record the real check scope, exit code, and per-item results; a file name, zero discoveries, or a not-run state cannot prove the implementation correct.
