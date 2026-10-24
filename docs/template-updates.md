# Read-only template updates and explicit multi-target proposals

Use [update-template](../.github/skills/update-template/SKILL.md). This page maintains the tool's input/output contract; it stores no business facts or second copy of run results. The tool only compares an **existing local** old baseline, owner files, and a new candidate; it does not apply, merge, clone/fetch, commit/push, create PRs, discover credentials, or update external domain sources. A proposal is not permission, and neither is a configuration.

<a id="api"></a>
## API and actual inputs

Import from `.github/utilities/plan_template_update.py`:

```python
plan_update(base, local, candidate) -> UpdatePlan
TreeSource(root, version=None, files=None)
plan_batch(registration, target_ids) -> BatchPlan
```

`base/local/candidate` are each an explicit local directory or an immutable `TreeSource`. The three roots must exist, be enumerable, and not contain one another; files must be readable regular files.
URL/UNC, ambiguous drive-relative, and file-system roots are rejected; roots resolve the host's normal way (an ancestor reached through a symlink/junction, such as macOS `/tmp`, equals its actual location). Links **inside** a root are not followed, and a missing root or read failure is never an empty tree. Other local sources are selected only through explicit roots.

`files=None` compares each root's complete eligible file set; the union of paths across all three sides is evaluated, including local-only files. A given `files` must be the **same** non-empty tuple in all three inputs: `/`-separated paths relative to each root, with no empty segments, `.`, `..`, backslashes, colons, fragments, control characters, duplicates, or case aliases; no globs and no guessed targets.
A selected path may be absent on a side; a failed complete read is not absence.
Multi-target mode maps source and target locations explicitly (see below).
File/directory topology conflicts, or paths differing only in case across sides, are input errors the owner must resolve; renames are not guessed.
Files, directories, and parent prefixes of the complete tree are checked by case-folded identity, so a `Settings` file and a directory containing `settings/owner.md` cannot be judged "absent locally, candidate may add". Explicit mappings also check actual directory entry names before deciding absence; local owner files are not trimmed or hidden to eliminate collisions.

For roots, registration files, and output paths, `..` is normalized literally before links are resolved, so `link/../sibling` is the same `sibling` on Windows, Linux, and macOS. A normal explicit `../sibling` works; a nonexistent root is still an input error and never derives a successful source.

Exclusions apply only to segments **below this run's root**: `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.tox`, and `.nox` are `TOOL_DATA`; `test/tests/fixtures` are `TEST_FIXTURE`; matching is case-insensitive. Exclusion records hold the relative path and reason (directories end with `/`), and their contents are not read. An explicit file selection containing these segments is rejected, not silently narrowed. A `.venv` ancestor of the root does not count, so standalone fixtures can be read. `_templates`, skills, and rules are not excluded automatically. This is not a release allowlist: separately provide the file list authorized for each run. Do not reuse the historical 38-file baseline, and do not treat the whole maker or business repository as an authorized template version.

### Exact versions and digests

With no `version`, a content identity is generated from the actual read set; a "dirty working tree" never borrows HEAD's identity. A given version must be verified: it cannot be a mere label, and there is no fallback to a branch, main/master, the index, or an empty ancestor.

| Version | How it is checked |
|---|---|
| `sha256:` followed by 64 lowercase hex digits | Checked against the exact scoped snapshot algorithm below; it is not a single-file digest |
| Full 40/64-character lowercase Git commit ID | The root must be exactly the top level of the local checkout; the raw regular blobs of that exact commit must match the actual eligible file set/bytes. An explicit file scope checks only those paths and their absence; unrelated files need not match |

The content snapshot is `sha256:` plus the SHA256 of `{"files": records, "selection": selection}` serialized with `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True)` in UTF-8. `records` is sorted by path, with entries `{"path": <root-relative path>, "sha256": "sha256:<raw file digest>", "size": <raw byte count>}` for existing files only. `selection` is `null` (complete scope) or the sorted explicit paths, so a complete and an explicit scope over the same files have different identities. Line endings, BOM, binary content, and Unicode are not normalized. An empty readable root differs from a nonexistent root. The comparison plans no chmod or permission changes.

Git reads use the existing restricted local helper: argument list, explicit cwd, `shell=False`; no hooks, filter/textconv, replace refs, source commands, lazy fetch, or inherited Git config overrides apply. An unreadable exact object or regular blob fails the read. Each input is read once; this is not a file-system transaction or an OS sandbox, so do not modify input trees while the tool runs.

### Narrow output records

The `changes/conflicts/preserved/sources` of `UpdatePlan` are all immutable tuples.
`status` is `proposed/no-change/conflict`, and `to_dict()` can be serialized to JSON directly.

- Each `UpdateItem` has a target `path`, `action`, `reason`, and three identities: `base/local/candidate`.
- Each file identity has the actual `path` on that side, `source` (its role among the three sides), `version`, the raw `sha256`, and `size`. `sha256: null, size: null` **explicitly means the path is absent**, not that a read failed.
- Each source has `role/root/version/snapshot/files/excluded/selection`; `files` holds identities of existing files. A three-root call gives the actual local root; multi-target mode keeps the root relative to the registration location, which eases handoff. No file bodies, auto-merged content, or diff patches are output; this is an exact operation proposal per path/version/digest.
- API input failures raise the existing `ArtifactInputError(code, path, line, message)` rather than returning a successful empty proposal. Reports contain only necessary diagnostics; values or snippets from raw YAML errors are not copied to stdout.

### Three-way path decisions (UPDATE-01…16)

| Input: base / local / candidate | Result and reason |
|---|---|
| All three sides identical | preserve / `UNCHANGED` |
| Only local modified; candidate equals base | preserve / `LOCAL_MODIFIED` |
| Only candidate modified; local equals base | modify / `CANDIDATE_MODIFIED` |
| Both sides modified to the same content | preserve / `ALREADY_ALIGNED` |
| Both sides modified differently | conflict / `BOTH_MODIFIED` |
| Candidate deleted; local unchanged | delete / `CANDIDATE_DELETED`; nothing is actually deleted |
| Candidate deleted; local modified | conflict / `DELETE_MODIFY` |
| Local deleted; candidate unchanged | preserve / `LOCAL_DELETED`; not resurrected |
| Local deleted; candidate modified | conflict / `MODIFY_DELETE` |
| Absent in base/local; added by candidate | add / `CANDIDATE_ADDED`; nothing is actually created |
| Absent in base; local and candidate add different content | conflict / `ADD_ADD` |
| Business file present only locally | preserve / `LOCAL_ONLY` |
| Absent in base and both sides add the same content; or both sides delete the file | preserve / `SAME_ADDITION`, `BOTH_DELETED` |
| Base root missing/unreadable, or a provided version is wrong | input error, not a file deletion |
| Binary content, BOM, line endings, paths with non-ASCII characters or spaces | decided on raw bytes with deterministic paths/order; no text normalization |
| Links/out-of-bounds paths/caches/fixtures; source drift or output conflicts | explicit errors or the exclusions above; sources are not written and history is not overwritten |

<a id="registration"></a>
## Optional local multi-target registration v1

The [blank data form](../_templates/config/template-updates.yaml) can be copied and filled in; empty values or lists are not a usable configuration.
The registration is read as YAML/JSON by the shared SafeLoader, which rejects duplicate keys, merge conflicts, recursive aliases, and unknown/unsafe tags; only the fields below are accepted, and no commands, credentials, `apply`, or authorization flags. No new results database is needed.

| Location | Required shape |
|---|---|
| Top level | `schemaVersion: 1` (a real integer), `source`, and a non-empty `targets` list |
| `source` | `repository`, `base`, `candidate`, and a non-empty `files` list |
| `source.base/candidate` | Only `root` and `version`; the version must be one of the exact Git/content identities above |
| `source.files[]` | Only `scenario` and `path`; a unique source scenario reference `project/context/ID#anchor` and a unique allowed root-relative `.feature` file |
| `targets[]` | Only a unique `id`, `repository`, `scope`, `local`, and a non-empty `files` list |
| `targets[].local` | Only `root` and `version`; it cannot be missing or be replaced by the source repository or another target |
| `targets[].files[]` | Only `source` and `path`; source must be in the source allow list, and path is an explicit `.feature` location in this BC; target paths are unique (including by case) |

`repository` is a portable `owner/repository` identity, and `scope` is the actual `project/context`; each segment and each target id starts with a letter or digit, followed by letters, digits, dots, underscores, or hyphens.
The three segments of `scenario` follow the same rule, and the anchor starts with an ASCII letter, followed by letters, digits, dots, underscores, colons, or hyphens.
The scenario reference is supplied by the caller; the tool does not parse Gherkin semantics or certify business approval.
The unit of propagation is the raw bytes of the whole registered `.feature` file; partial file slices or other targets are not derived from scenario tags.

`root` is relative to the **parent directory of the registration file**, and an explicit `../` can select
an existing sibling checkout on this machine; personal absolute paths, URL/UNC, backslashes, colons,
empty segments, environment variables, `~/$/%` expansion, and aliases are not accepted.
Each target's local version is checked against **all of its mapped target paths**; the source
base/candidate versions are checked against the full set of files allowed by the source list. A source file that
exists in neither the old nor the new version is `SOURCE_FILE_MISSING` and is not disguised as no change.
There is no default target; the API `target_ids` must be a non-empty iterable of unique, valid IDs and cannot be a single string.

The following shows only the shape; every angle-bracket value must be replaced with a real input. These versions are not evidence of an example run:

```yaml
schemaVersion: 1
source:
  repository: example/domain
  base: {root: ../old-source, version: "<actual full commit or scoped sha256>"}
  candidate: {root: ../new-source, version: "<actual full commit or scoped sha256>"}
  files:
    - {scenario: example/CTX-domain/TS-001#allow, path: verification/TS-001.feature}
targets:
  - id: bc-a
    repository: example/bc-a
    scope: example/CTX-a
    local: {root: ../bc-a, version: "<actual version of this BC's mapped files>"}
    files:
      - {source: verification/TS-001.feature, path: specs/incoming/TS-001.feature}
```

`BatchPlan` keeps the raw digest of the registration file, the source repository, and `TargetProposal` entries sorted stably by selected ids. Each target has its actual `repository/scope/mappings`, an independent `status`, and a `plan` or explicit `findings`. An unregistered target is `UNKNOWN_TARGET` with repository/scope null; it is never created or guessed. A target with missing fields/root/version, or that is unreadable or out of bounds, is `unavailable` for that target only, and other results are kept; a shared-source failure makes dependent targets unavailable. Drift of a single target makes only that target unavailable; drift of the shared source invalidates all dependent proposals. An invalid or drifted registration is an input error for the whole input. Diagnostics distinguish source locations such as `source/base` from `targets/<id>/local`; one successful target does not mean propagation of the whole batch is complete.

<a id="cli"></a>
## CLI, new reports, and exit codes

The cwd is the directory the caller chooses for this run; the script is invoked directly from the complete repository or a self-contained candidate. Windows example from the repository root:

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --base "<base-root>" --local "<local-root>" --candidate "<candidate-root>"
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --registration "<registration.yaml>" --target "<ID-A>" --target "<ID-B>"
```

Three-root mode can add `--base-version/--local-version/--candidate-version` for the respective roots; for an explicit file scope, use the `TreeSource` API or the registration above; versions are not guessed from directory names. The two CLI modes are mutually exclusive, and there is no `--apply`.
On other hosts, substitute the verified actual project interpreter; neither PowerShell 7 nor a wrapper script is required.

| Top-level status / exit | Actual meaning |
|---|---|
| `no-change` / 0 | Comparison completed with no proposed changes; a run that preserves owner modifications can also be no-change |
| `proposed` / 0 | Comparison completed with a clean proposal; nothing applied |
| `conflict` / 1 | At least one conflict and no unavailable target; clean targets/paths are still kept |
| `input-error` / 2 | A source/registration/output error, or at least one unavailable target; cannot be downgraded to success |

By default, JSON goes to stdout and neither sources nor outputs are written. An explicit `--output <new-local.json>` uses exclusive create; it creates no parent directories, overwrites no existing files, directories, or history, and cannot be placed in any of the three root inputs or in a source/target root of the registration, including cached, missing, or target roots **not selected in this run**.
Output and protected locations are compared after resolution, case-insensitively; if registration locations cannot be resolved, only stdout is kept and writing is refused. Protection covers locations equal to, below, or becoming a **file ancestor** of such a root; for example, with an unselected target `proposal.json/checkout`, a `proposal.json` file cannot be created because it would block that root.
When output is refused, independent targets' proposals and unavailable results are still on stdout and the exit code is non-zero; a complete per-target report, even one with unavailable targets, may be saved to an exact, safe new location and still exits 2; if the whole input cannot be parsed, no report is created.
An interrupted write may leave an incomplete **new** file; owner content is not deleted or replaced. Relative report output paths are relative to the calling cwd, not to an implicit project root.

Main errors: `INVALID_ROOT/UNSAFE_ROOT/OVERLAPPING_ROOTS`, `UNSAFE_PATH/INVALID_SCOPE/
PATH_TYPE_CONFLICT/PATH_COLLISION`, `FILE_READ_ERROR/DIRECTORY_READ_ERROR`,
`INVALID_BASE/BASE_UNAVAILABLE/BASE_MISMATCH`, `REGISTRATION_UNAVAILABLE/INVALID_REGISTRATION/
INVALID_TARGET_REGISTRATION/INVALID_TARGETS/UNKNOWN_TARGET/TARGET_FILE_NOT_ALLOWED/
SOURCE_FILE_MISSING`, and `REPORT_CONFLICT/REPORT_WRITE_ERROR`.
Command usage errors return 2 via argparse; there is no broad exception handler that produces a successful empty proposal.

<a id="maintainer-workflow"></a>
## Maintainer workflow and gates not yet run

The maker repository's `propose-template-updates.yml` is **for maintainers only**, to generate proposals manually; it is not distributed as a runtime dependency of business projects.
It uses the same Python core, read-only contents permission, and explicitly selected targets; it checks out only the maker tool's own event commit, disables checkout's clean, and does not clone/fetch targets. A trusted self-hosted runner (any OS) must prepare the actual local registration and three-way trees in advance, outside the tool checkout, and must not put work inputs into the tool path that will be checked out; the registration gives an exact version for each entry, and no fallback succeeds through tokens, secrets, or network fetches of sources.
The run steps use Python, the actual interpreter from the standard-library venv, and explicit temporary outputs, without hard-coding a shell or environment layout.
The file keeps tool environment preparation and artifact saving, with no target-branch, PR, or auto-apply step.

The existence of the YAML file, or its local parse, does not mean that hosted execution, self-hosted permissions, or server-side required checks have been verified.
Concrete external runs, artifact uploads, and native Git/platform propagation still require separate authorization at each gate; until run, they remain `not-run`. Local tools, use of the method itself, and maintainer tests cannot stand in for external fan-out, the manual T17 run, or native discovery of new entry points.
