# Read-only template updates and explicit multi-target proposals

Use [update-template](../.github/skills/update-template/SKILL.md). This page maintains the tool's input/output contract; it does not store business facts or a second copy of run results. The tool only compares an **existing local** old baseline, owner files, and a new candidate; it does not apply, merge, clone/fetch, commit/push, create PRs, discover credentials, or update external domain sources. A proposal is not permission, and neither is configuration.

<a id="api"></a>
## API and actual inputs

Import from `.github/utilities/plan_template_update.py`:

```python
plan_update(base, local, candidate) -> UpdatePlan
TreeSource(root, version=None, files=None)
plan_batch(registration, target_ids) -> BatchPlan
```

`base/local/candidate` are each an explicit local directory path or an immutable `TreeSource`.
The three roots must exist, be enumerable, and not contain one another; files must be readable regular files.
URL/UNC paths, ambiguous drive-relative paths, and file-system roots are rejected; root paths are resolved
in the host's normal way, and an ancestor reached through a symlink/junction (such as macOS `/tmp`) is
equivalent to its actual location. Links **inside** a root are still not followed, and a missing root or
read failure is never interpreted as an empty tree. Other local sources outside the roots are selected only through explicit roots.

`files=None` compares the complete eligible file set of each of the three roots; the union of paths
across all three sides is evaluated, including local-only files.
If `files` is provided, it must be the **same** non-empty tuple in all three inputs, with paths relative
to each root using `/`, and without empty segments, `.`, `..`, backslashes, colons, fragments, control
characters, duplicates, or case aliases; no globs are used and no targets are guessed.
A selected path may be absent on a side; a failed complete read is not absence.
Multi-target mode additionally maps different source and target file locations explicitly, as described below.
File/directory topology conflicts, or paths that differ only in case across sides, are input errors that
the owner must resolve; renames are not guessed.
Files, directories, and parent prefixes of the complete tree are all checked by case-folded identity, so a
`Settings` file and the directory containing `settings/owner.md` cannot be judged as "absent locally,
candidate may add". Explicit mappings also check the actual directory entry names before deciding
absence; local owner files are not trimmed or hidden to eliminate collisions.

For roots, registration files, and output paths, `..` is first normalized literally and links are resolved
afterwards, so `link/../sibling` points to the same `sibling` on Windows, Linux, and macOS. A normal
explicit `../sibling` works; a nonexistent root is still an input error and is not used to derive a successful source.

Exclusions apply only to directory/file segments **below the root of this run**: `.git`, `.venv`, `venv`,
`node_modules`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.tox`, and `.nox` are `TOOL_DATA`;
`test/tests/fixtures` are `TEST_FIXTURE`; matching is case-insensitive. Exclusion records contain the
relative path and the reason, directories carry a trailing `/`, and their contents are not read; an
explicit file selection containing these segments is rejected rather than silently narrowed.
A `.venv` ancestor of the root does not take part in exclusion, so standalone fixtures can still be read.
`_templates`, skills, and rules are not excluded automatically.
This is not a release allowlist; when preparing a candidate, separately provide the file list authorized
for this run. Do not reuse the historical 38-file baseline, and do not treat the whole maker repository
or a business repository as an authorized template version.

### Exact versions and digests

When no `version` is given, a content identity is generated from the actual read set; a "dirty working
tree" never borrows HEAD's identity. When a version is given, it must be verified: it cannot serve as a
mere label, and there is no fallback to a branch, main/master, the index, or an empty ancestor.

| Version | How it is checked |
|---|---|
| `sha256:` followed by 64 lowercase hex digits | Checked against the exact scoped snapshot algorithm below; it is not a single-file digest |
| Full 40/64-character lowercase Git commit ID | The root must be exactly the top level of the corresponding local checkout; the raw regular blobs of that exact commit are read and must match the actual eligible file set/bytes. An explicit file scope checks only those paths and their absence and does not require unrelated files to match |

The content snapshot is the SHA256 of the object `{"files": records, "selection": selection}` after
`json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True)` and UTF-8 encoding, prefixed
with `sha256:`. `records` is sorted by path, and each entry is
`{"path": <root-relative path>, "sha256": "sha256:<raw file digest>", "size": <raw byte count>}`;
it contains only files that actually exist. `selection` is `null` (complete scope) or the sorted array of explicit paths.
Therefore a complete scope and an explicit scope over the same file set have different identities; line
endings, BOM, binary content, and Unicode are not normalized.
An empty root that exists and is readable is different from a nonexistent root. The comparison does not plan chmod/file permission changes.

Git reads reuse the existing restricted local helper: an argument list, an explicit cwd, and `shell=False`;
no hooks, filter/textconv, replace refs, source commands, lazy fetch, or inherited Git configuration overrides take effect.
If an exact object/regular blob is unreadable, the read fails. Each input is read only once; this is not a
file-system transaction or an OS sandbox, so do not modify the input trees while the tool runs.

### Narrow output records

The `changes/conflicts/preserved/sources` of `UpdatePlan` are all immutable tuples.
`status` is `proposed/no-change/conflict`, and `to_dict()` can be serialized to JSON directly.

- Each `UpdateItem` has a target `path`, an `action`, a `reason`, and three identities: `base/local/candidate`.
- Each file identity has the actual `path` on that side, `source` (its role among the three sides), `version`, the raw `sha256`, and `size`.
  `sha256: null, size: null` **explicitly means that the path is absent**, not that a read failed.
- Each source has `role/root/version/snapshot/files/excluded/selection`; `files` holds the identities of existing files.
  For a single three-root call, root is the actual local path; in multi-target mode, root keeps the
  declaration relative to the registration location, which eases handoff.
  No file bodies, auto-merged content, or diff patches are output; this is an exact operation proposal per path/version/digest.
- API input failures raise the existing `ArtifactInputError(code, path, line, message)` rather than returning a successful empty proposal.
  Reports contain only the necessary diagnostics; values/snippets from raw YAML errors are not copied to stdout.

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
| Absent in base and both sides add the same content; deleted on both sides | preserve / `SAME_ADDITION`, `BOTH_DELETED` |
| Base root missing/unreadable, or a provided version is wrong | input error, not a file deletion |
| Binary content, BOM, line endings, paths with non-ASCII (for example CJK) characters or spaces | decided on raw bytes with deterministic paths/order; no text normalization |
| Links/out-of-bounds paths/caches/fixtures; source drift or output conflicts | explicit errors or the exclusions above; sources are not written and history is not overwritten |

<a id="registration"></a>
## Optional local multi-target registration v1

The [blank data form](../_templates/config/template-updates.yaml) can be copied and filled in; empty values/lists are not a usable configuration.
The actual registration is read as YAML/JSON by the shared SafeLoader, which reuses the rejection rules
for duplicate keys, merge conflicts, recursive aliases, and unknown/unsafe tags; only the fields below are
accepted, and no commands, credentials, `apply`, or authorization flags are accepted. No new results database is needed.

| Location | Required shape |
|---|---|
| Top level | `schemaVersion: 1` (a real integer), `source`, and a non-empty `targets` list |
| `source` | `repository`, `base`, `candidate`, and a non-empty `files` list |
| `source.base/candidate` | Only `root` and `version`; the version must be one of the exact Git/content identities above |
| `source.files[]` | Only `scenario` and `path`; a unique source scenario reference `project/context/ID#anchor` and a unique allowed root-relative `.feature` file |
| `targets[]` | Only a unique `id`, `repository`, `scope`, `local`, and a non-empty `files` list |
| `targets[].local` | Only `root` and `version`; it cannot be missing or be replaced by the source repository or another target |
| `targets[].files[]` | Only `source` and `path`; source must be in the source allow list, and path is an explicit `.feature` location in this BC; target paths are unique (including by case) |

`repository` is a portable `owner/repository` identity, and `scope` is the actual `project/context`;
each segment and each target id starts with a letter or digit, followed by letters, digits, dots, underscores, or hyphens.
The three segments of `scenario` follow the same rule, and the anchor starts with an ASCII letter,
followed by letters, digits, dots, underscores, colons, or hyphens.
It is a scenario source reference supplied by the caller; the tool does not parse Gherkin semantics or certify business approval.
The unit of propagation is the raw bytes of the whole registered `.feature` file; partial file slices or other targets are not derived from scenario tags.

`root` is relative to the **parent directory of the registration file**, and an explicit `../` can select
an existing sibling checkout on this machine; personal absolute paths, URL/UNC, backslashes, colons,
empty segments, environment variables, `~/$/%` expansion, and aliases are not accepted.
Each target's local version is checked against **all of its mapped target paths**; the source
base/candidate versions are checked against the full set of files allowed by source. A source file that
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

`BatchPlan` keeps the raw digest of the registration file, the source repository, and the
`TargetProposal` entries sorted stably by the selected ids. Each target has its actual
`repository/scope/mappings`, an independent `status`, and a `plan` or explicit `findings`; an
unregistered target is `UNKNOWN_TARGET` with repository/scope set to null, and it is never created or guessed.
A target with missing fields/root/version, or one that is unreadable or out of bounds, is `unavailable`
for that target only, and the other results are kept; a failure of the shared source makes the dependent targets unavailable.
Drift of a single target makes only that target unavailable, while drift of the shared source invalidates
all dependent proposals. An invalid or drifted registration itself is an input error for the whole input.
Diagnostics distinguish source locations such as `source/base` from `targets/<id>/local`; one successful
target does not mean that propagation of the whole batch is complete.

<a id="cli"></a>
## CLI, new reports, and exit codes

The cwd is the directory the caller explicitly chooses for this run; the script is invoked directly from
the complete repository or from a self-contained candidate. A Windows example from the repository root:

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --base "<base-root>" --local "<local-root>" --candidate "<candidate-root>"
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --registration "<registration.yaml>" --target "<ID-A>" --target "<ID-B>"
```

Three-root mode can add `--base-version/--local-version/--candidate-version` for the respective roots;
for an explicit file scope, use the `TreeSource` API or the multi-target registration above; versions are
not guessed from directory names. The two CLI modes are mutually exclusive, and there is no `--apply`.
On other hosts, substitute the verified actual project interpreter; neither PowerShell 7 nor an extra wrapper script is required.

| Top-level status / exit | Actual meaning |
|---|---|
| `no-change` / 0 | Comparison completed with no proposed changes; a run that preserves owner modifications can also be no-change |
| `proposed` / 0 | Comparison completed with a clean proposal; nothing applied |
| `conflict` / 1 | At least one conflict and no unavailable target; clean targets/paths are still kept |
| `input-error` / 2 | A source/registration/output error, or at least one unavailable target; cannot be downgraded to success |

By default, JSON goes to stdout and neither sources nor outputs are written. An explicit
`--output <new-local.json>` uses exclusive create; it does not create parent directories or overwrite
existing files/directories/history, and it cannot be placed in any of the three root inputs or in a
source/target root of the registration, including cached, missing, or target roots **not selected in this run**.
The output and protected locations are compared after resolution (case-insensitively); when registration
locations cannot be resolved, only the stdout result is kept and writing is refused. The protection covers
locations that are equal to, below, or would become a **file ancestor** of such a root; for example, when an
unselected target is `proposal.json/checkout`, a `proposal.json` file cannot be created to block it.
When output is refused, the proposals/unavailable results of independent targets are still on stdout, and the exit code is non-zero;
a complete per-target report, even one containing unavailable targets, can be explicitly saved to an exact, safe new location and still exits 2;
if the whole input cannot be parsed, no report is created. An interrupted write may leave an incomplete **new** file; owner content is not deleted or replaced.
Relative report output paths are relative to the calling cwd, not to some implicit project root.

Main errors: `INVALID_ROOT/UNSAFE_ROOT/OVERLAPPING_ROOTS`, `UNSAFE_PATH/INVALID_SCOPE/
PATH_TYPE_CONFLICT/PATH_COLLISION`, `FILE_READ_ERROR/DIRECTORY_READ_ERROR`,
`INVALID_BASE/BASE_UNAVAILABLE/BASE_MISMATCH`, `REGISTRATION_UNAVAILABLE/INVALID_REGISTRATION/
INVALID_TARGET_REGISTRATION/INVALID_TARGETS/UNKNOWN_TARGET/TARGET_FILE_NOT_ALLOWED/
SOURCE_FILE_MISSING`, and `REPORT_CONFLICT/REPORT_WRITE_ERROR`.
Command usage errors return 2 via argparse; there is no broad exception handler that produces a successful empty proposal.

<a id="maintainer-workflow"></a>
## Maintainer workflow and gates not yet run

The maker repository's `propose-template-updates.yml` is **for maintainers only**, to generate proposals
manually; it is not distributed as a runtime dependency of business projects.
It uses the same Python core, read-only contents permission, and explicitly selected targets; it checks out
only the maker tool's own event commit, disables checkout's clean, and does not clone/fetch targets. A
trusted self-hosted runner (any OS) must prepare the actual local registration and the three-way trees in
advance, outside the tool checkout, and must not put work inputs into the tool path that will be checked out;
the registration gives an exact version for each entry; there is no successful fallback via tokens, secrets, or fetching sources over the network.
The run steps use Python, the actual interpreter returned by the standard-library venv, and explicit temporary outputs, without hard-coding a shell or environment layout.
The file keeps the tool environment preparation and artifact saving, but it has no target-branch, PR, or auto-apply step.

The existence of the YAML file, or the fact that it parses locally, does not mean that hosted execution,
self-hosted permissions, or server-side required checks have been verified.
Concrete external runs, artifact uploads, and native Git/platform propagation still happen at separately
authorized gates; until they are run, they remain `not-run`. Local tools, the method's own use, and
maintainer tests cannot stand in for external fan-out, the manual T17, or native discovery of new entry points.
