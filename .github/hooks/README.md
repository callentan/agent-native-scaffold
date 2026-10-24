# Optional Git hooks

These two files are Python entry points, not Git configuration enabled by default. Only after installation is authorized for a specific project does the [installer](../utilities/install_hooks.py) create the selected native hooks. Copying the template, selecting an agent, adding a workflow, or including a `Reviewed-by` line is not installation, human approval, or a server-side gate.

## Runtime dependencies and distribution

Requires Git, Python 3.11+ (venv, conda, or system interpreter), and importable PyYAML and jsonschema. The [locked dependencies](../utilities/requirements.lock) are the tested versions, not versions enforced at runtime. The interpreter is given as a full absolute path; nothing searches PATH for another Python, and no packages are installed. See the [development registration](../../docs/development.md#maintenance-tools) for commands and environment. The installation proposal and both hooks' startup share one check: minimum Python version and importable dependencies. On failure they exit 2 before reading the index or artifacts and prompt you to restore dependencies from the lock. The path or prefix the launcher passes in, and the actual interpreter and dependency versions, are recorded only in the report and are not grounds for refusal. This startup check is not an OS sandbox.

Both entry points only call `hook_checks.py`, a narrow adapter that obtains the index and reuses `artifact_io.py`, `check_artifacts.py`, `check_traceability.py`, and `artifact.schema.json`; there is no separate Markdown, acceptance, or coverage algorithm. These modules and contracts must be distributed as one version group. The installer additionally needs the selected entry points in this directory and the lock; it does not depend on maker-repository tests, research, logs, session scripts, or external repositories.

Actual startup trials on Git for Windows found that an absolute Python shebang did not select the specified venv, and a quoted shebang did not work either. There, the hooks use **Git's bundled `sh`**, which only checks that the interpreter exists and runs a quoted `exec`; all validation logic stays in Python. PowerShell 7 is not required. On POSIX, representable interpreter paths use a direct Python shebang and still pass `-B -X utf8` at startup; paths with whitespace or that are too long use the same minimal `sh` adapter. Windows, Linux, and macOS share the same Python check logic; runtime evidence for a specific host must come from the corresponding report, and the existence of code or YAML does not count as verified in practice.

## Inspect first, then install explicitly

The command shape below has paths to replace; it does not authorize installation in any working tree. Each `--hook` explicitly selects one hook; omitting it is an argument error, and there is no "install all by default".

```text
<project-python> -B -X utf8 .github/utilities/install_hooks.py --root "<checkout-root>" --python "<absolute-project-python>" --hook pre-commit --hook commit-msg
```

By default it outputs only a JSON proposal: Git root/git-dir/common-dir, known worktrees, the source of any effective `core.hooksPath`, exact hook and ownership receipt paths, the selected interpreter, and proposed operations. **It does not write hooks, configuration, the index, or source files.** Only after checking the specific targets, ownership, and authorization add `--apply` to the same command. The tool creates only the selected hooks and their receipts; it does not commit, push, or change signing configuration.

- Any existing target (including empty files, links, and old receipts) is a conflict: it is not overwritten, and the tool never skips it and reports a complete installation.
- Any effective `core.hooksPath` is a conflict; the tool does not take over or modify an organization, user, or project hook chain.
- Default hooks belong to the common Git metadata. For a linked worktree, or when multiple worktrees exist, the proposal states the shared scope and refuses to install or restore. No mode implicitly switches `extensions.worktreeConfig` or affects siblings; if shared adoption is needed, the owner designs and authorizes it separately, and this command does not unblock it.
- If the tool or entry points are missing, the interpreter is missing, Python is older than 3.11, or dependencies cannot be imported, it explicitly exits 2 and installs nothing further. For partial writes and the recovery boundary, see the next section; created files are not deleted automatically, and a failure is not a complete installation.
- The Git entry points reference this project's tool source and do not copy or freeze a separate implementation. Later source updates change hook behavior, so versions and applicability must be rechecked; locally editable tools are not a security boundary against malicious modification.

## Restore and owner changes

Next to each installed item the tool saves `<hook>.artifact-maintenance.json`: exact root/git-dir/path, original state `absent`, SHA256 of the installed bytes, actual mode, interpreter, and an empty list of configuration changes. This local ownership receipt supports restore; it is not an approval or cryptographic authentication. Do not carry generated receipts to another checkout.

```text
<project-python> -B -X utf8 .github/utilities/install_hooks.py --root "<checkout-root>" --hook pre-commit --hook commit-msg --restore
```

By default it still only checks and proposes. With `--apply`, it first checks all selected items, then deletes only hooks/receipts that still match their receipts. Later owner edits, mode changes, missing receipts, links, or configuration changes are conflicts; the current state is kept for the owner, and reinstalling cannot overwrite it. Other hooks, config, source, and the index stay unchanged. Directories are not cleaned recursively, and an empty hooks directory created during installation may remain. Restoring does not require the original interpreter to still be available, but running the installer still needs an authorized Python.

After an installation write/flush/close failure or short write, `written` contains every exact path this run has already created exclusively, even if it holds only some bytes. `recovery` is explicitly marked `manual-required` and reports, per item, whether write and close completed, the current existence/unreadable/owner-conflict state, and expected and actual digests and sizes. **There is no automatic rollback**; even complete, byte-identical files are kept, to avoid deleting later edits on insufficient ownership inference. The owner must first inspect these paths and their actual content, compare this run's receipts with later changes, and then decide how to reconcile. Do not rerun install or restore indiscriminately, or recursively delete the hooks directory. A later installation that meets a leftover hook/receipt still treats it as a conflict; a missing, partial, or mismatched receipt grants no permission to delete during restore. The failure JSON is a recovery clue, not a permanent certification of ownership or authorization for automatic cleanup.

## pre-commit: check the index that is actually about to be committed

The same entry point can be run directly to see JSON output and exit code:

```text
<project-python> -B -X utf8 .github/utilities/hook_checks.py pre-commit --root "<checkout-root>"
```

This differs from the working-file mode of `check_artifacts.py --root ...`:

1. It obtains the actual index entries, including the `GIT_INDEX_FILE` provided by Git's native partial commit. It does not scan working files in place of staged content: an unstaged fix cannot hide an invalid index, and unstaged damage does not invalidate a valid one. The complete file set after staged deletions and renames takes part.
2. It uses raw `cat-file` blobs to build a regular-file snapshot in a private temporary directory; Git `mktree` writes tree objects only into that space. The original index, source files, config, and source object database are not written. The temporary location comes from the host's standard temporary directory and is removed when the check ends; it does not require a writable project venv, and it is not a persistent executable project.
3. It records the original path, mode, blob ID, raw SHA256/size, index file and manifest digests, exact index tree, current HEAD, and comparison base/tree. `changes` uses added/modified/deleted; a rename is a deletion plus an addition, with no similarity guessing. An executable regular file's mode stays in the identity record, but the file is never executed.
4. Artifact and link rules call the same complete inventory checker; historical formal identities still identify the current path of a file whose metadata was deleted or damaged. Coverage starts from **all actual owner ACs/VCs**, including those with no VT. With zero owner acceptance criteria, coverage is `not-applicable`, without requiring optional entities to add ACs; declared dangling targets are still checked, and real input errors are never downgraded to an empty selection.
5. Unmerged entries, intent-to-add entries, unreadable blobs, symlinks/gitlinks, out-of-bounds or unrepresentable paths, and case/Unicode path aliases are explicitly rejected. It runs no filters, smudge, textconv, submodules, or network access, does not read Git link targets, and does not repair or stage content.

`--base` accepts only a complete 40- or 64-character commit ID readable locally; an explicit error never falls back to HEAD, main/master, or an empty comparison. With no base, the HEAD at hook call time is recorded; a history-free comparison is used only when an unborn state with no branch ref is confirmed. `snapshot.parent/head` is the HEAD used for this comparison; it does not promise to infer the full parent graph after an amend, rebase, or merge, and `base_origin` records the source. The index and HEAD are read only once, at the start of the check.

The report keeps the shared checker's owner, line, target, actual counts, and byte baseline; temporary-file diagnostics map back to original checkout paths. `runtime` also records the actual interpreter, dependency versions, and digests of the running tool source and schema; a staged tool blob cannot pass for the version actually executed. Git's own commit may refresh the index cache/stat; that differs from the checker modifying staged entries.

`0 = clean/empty`, `1 = invalid`, `2 = input-error`. `empty` and zero owners do not mean business or application acceptance passed; `checked_count/attempted_count` counts formal artifacts, not regression tests. Native Git may report 1 or 2 from the hook as a non-zero commit exit; the hook JSON keeps the original 0/1/2.

Only after initial environment validation passes (`startup_validated: true`) does an explicit `--report "<new.json>"` invoke the shared report writer; the parent directory must exist, and overwriting any existing output is always refused. `startup_validated: true` means only that the initial environment validation passed, not that the artifacts are valid. Artifact or baseline input errors in a normal environment can still be saved to a new report. On a startup refusal, the stdout JSON, recovery hint, and exit 2 are kept, but the result returns `report_output.written: false` and `reason: startup-refused`; validators are not imported for the report, and the requested report path is not checked, opened, or created. Restore the selected environment first, then request file output again.

## commit-msg: managed-path format policy, only once enabled

The local policy `managed-reviewed-by-text-v1` applies to differences between the current HEAD and the actual index, including both sides of deletions and renames. The managed scope is:

- `.md/.feature/.yaml/.yml/.json` files under `domain-model/`, `stakeholder-requirements/`, `software-requirements/`, `user-stories/`, `architecture/`, and `verification/`, including guides and scenario companions.
- The root-level `bc-config.yaml`, `model-sources.yaml`, `model.yaml`, and `model.json`.

Other paths need no reviewer line, and no repository-wide default commit convention is introduced. Managed changes need at least one `Reviewed-by: name` line; the key is case-insensitive. After trimming surrounding whitespace, the value must be at least two characters long and contain a letter. It must not be `reviewer/name/none/n/a/unknown/pending/not-run/tbd/to be confirmed`, a placeholder token of the existing artifact rules, or `<name>/<reviewer>`. With multiple such lines, every line must satisfy the rule; an email address is not required, and real identity is never judged from an email address. A missing or invalid line returns 1; message read, encoding, or path failures return 2.

The hook only reads the message file Git provides and records its digest; it does not add a reviewer, change the message, or execute its content. Merge, fixup, and squash subjects have no special exemption branch. The hook runs only when Git actually calls it; this file cannot extend the hook lifecycle to other Git commands.

**This proves only the shape of the text; it does not authenticate the reviewer, role, human involvement, approval, or a waiver.** Native `--no-verify`, replacing or disabling hooks, or editing the local tools can still bypass it; no bypass counts as a verified review. Server-side protection must be configured and verified separately on the actual platform and cannot be inferred from a local hook passing.

## Keep the two kinds of workflow separate

[validate-artifacts](../workflows/validate-artifacts.yml) is the distributable entry point for validating project materials; it needs only the Python modules, contracts, and lock listed above within the candidate, plus project files. It does not install hooks or run maker tests. For a PR, it checks out the exact head and takes the comparison argument from the exact PR base SHA; a missing or invalid base is an input error. Outside a PR, it uses the index of the checked-out HEAD. The JSON upload and raw job output are kept separately.

`tooling-tests.yml` and `tests/run_tooling_tests.py` are **maker-repository only** and are not distributed with downstream candidates. They run real unittest discovery and keep discovered, run, executed, skipped, failure, and error counts; zero discoveries, all tests skipped, or failures in a non-empty suite all fail the job. They are not a dependency of the material checker.

The material workflow uses Ubuntu 24.04; the maker-repository regression uses a Windows, Ubuntu, and macOS matrix; each keeps its own report. All run steps are Python, use the interpreter the venv returns rather than a hard-coded platform path, require a minimum of Python 3.11, and restore the same lock. There is no application, write permission, secret, `pull_request_target`, required-check configuration, or propagation job. Local YAML parsing and Git tests are not a hosted CI pass; an actual hosted run and server-side required checks still need raw platform results. Do not start remote workflows based on the examples here before authorization.
