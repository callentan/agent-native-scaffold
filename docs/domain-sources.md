# Optional local domain source integration

The default remains single-repository material; no external source, submodule, or new application
is required. When an existing source needs to be registered, use
`id/kind/root/path/baseline/readOnly` from the
[original BC configuration](../.github/contracts/README.md#bc-configuration); this tool adds no source
manifest, execution command, or approval field.
Python and dependencies follow the [maintenance tools environment](development.md#maintenance-tools).

The entry point is [setup_domain_source.py](../.github/utilities/setup_domain_source.py); the shared
YAML/schema, path, and fixed-baseline logic is provided by `artifact_io.py`,
`check_artifacts.py`, and `source_baseline.py` in the same directory. The tool does not read the maker
repository's tests or run history.

<a id="operations"></a>
## The three operations

| Operation | Read and modification scope |
|---|---|
| inspect (default) | Checks the explicit local source, actual path, fixed baseline, existing BC sources, and target state, and returns a proposal only to stdout. Source/target files, Git objects, the index, refs, and config are not written |
| register | Appends this one source only to the **explicitly selected existing** BC configuration; it does not copy domain files, create a checkout, or stage automatically. If an identical source is already registered, the result is no-change |
| submodule | Creates a local native Git submodule at an explicit empty or nonexistent target, writing `.gitmodules`, this repository's local config, the module metadata, and the gitlink/index. It **does not modify the BC configuration**; to adopt the submodule afterwards, separately use the exact `suggested_registration` returned by inspect/register |

A non-empty `domain-model/README.md` does not prevent registering a read-only reference. Conversely,
if that directory is the materialization target, its existing content is a conflict: you cannot
delete the placeholder, overwrite it, or skip it and then claim the integration is complete.
A repeated run is no-change only when the source, files, and native metadata match exactly; an
incomplete installation must first be checked and recovered.

`readOnly` describes the nature of the source; it is not an OS ACL and grants no write permission.
Even when it is declared false, this tool still does not write the source. `--owned-target` only means
that the caller declares it has permission for this target operation; it cannot prove identity or
change operating system permissions.

<a id="inputs"></a>
## Exact inputs and stop conditions

- `root` is the local project root selected for this run. `--config` is the path of an **existing**
  BC configuration inside that root; the configuration must conform to the original schemaVersion 1
  and point to a real development registration file/anchor. This tool does not initialize the project configuration.
- The source `root` is an explicit directory relative to this project root; `../existing-domain-source`
  can select an authorized independent local source. `path` is interpreted only relative to this source root.
  Spaces, non-ASCII characters, and a lone `.` are allowed; variables are not expanded,
  and repeated directories are not trimmed. The source root is resolved in the host's normal way, and an
  ancestor path through a symlink/junction is equivalent to its actual location; `..` is first normalized
  literally so that Windows/Linux/macOS reach the same location. Paths that escape the project or source
  root, and Git/environment data paths, are still rejected.
- A `git` source must give a readable, full, lowercase 40/64-character **commit**; a `local` source can
  use the same kind of commit or the raw `sha256:` digest of one file. The commit's files/directories must
  match the actual local file set and bytes. SHA256 is not a directory digest. There is no fallback to a
  default HEAD, main/master, branch, short hash, tree/blob/tag, index, or remote.
- Source ID conflicts, aliased/overlapping locations, and wrong mount levels are all reported explicitly;
  nothing is merged, the first entry is not picked, and `root/path` is not silently changed.
  Structural validity does not mean that the source is authorized, the business meaning is correct, or acceptance has passed.
- URL, SCP-style address, and UNC sources are always unavailable/proposal-only. This tool has no network
  authorization switch; it does not probe DNS, credentials, or remotes, and does not fetch/clone network
  sources. When network material is needed, first prepare a local checkout in a separately authorized process.

<a id="git-config-boundary"></a>
### Git invocation environment

The tool runs local commands in a clean Git environment: it does not inherit repository/index/object
location overrides; it disables global/system configuration, network transports, and interactive prompts;
and it keeps the `GIT_EXEC_PATH` that the host Git itself needs. Each invocation sets
`GIT_CEILING_DIRECTORIES` to the parent directory of the selected root, so incomplete or missing Git
metadata returns `BASE_UNAVAILABLE` instead of borrowing an ancestor repository through discovery.
A plain local file source without Git metadata can still be checked by content digest; this does not
require creating a repository.

The repository's own Git configuration (including includes) takes effect under Git's native rules; the
tool does not separately parse or rewrite the owner's configuration. When strict isolation from external
configuration is needed, prepare the local checkout in an authorized independent environment; this is
not an OS ACL or an isolation guarantee against malicious concurrent file-system activity.

register keeps other keys, source entries, comments, and line-ending bytes, and edits only `domainSources`:
it can append to a standalone `domainSources: []` or a block-style list; it does not reformat the whole
file to edit flow-style, JSON, or YAML that cannot be located safely. When it cannot append safely, it
returns `CONFIG_EDIT_UNSUPPORTED`, and the owner must handle it in a separate, explicit maintenance task.
A valid configuration that is already fully registered can still be checked read-only with no-change;
it need not be reformatted for the tool.

<a id="api"></a>
## Python API and return values

Import from the module in the same directory:

```python
inspect_domain_source(root, source_config, *,
                      operation="register", config_path="bc-config.yaml", target=None) -> dict

apply_domain_source(root, source_config, *,
                    operation, config_path, expected,
                    owned=False, target=None, index_consent=False) -> dict
```

`source_config` is one mapping entry of the original contract, not a second configuration file. inspect
does not change the global cwd. apply must explicitly give the operation/configuration path, the target
ownership declaration, and the `preflight` from this inspect run; submodule additionally needs `target`
and a separate `index_consent=True`. These parameters are only explicit inputs and do not replace the
caller's actual authorization.

| Field | Meaning |
|---|---|
| `status / exit_code` | `ready / 0`: local preparation is feasible or the explicit operation succeeded; `conflict / 1`: a readable owner/baseline/target conflict; `unavailable / 2`: missing items, unavailable paths/configuration/objects, refused authorization, or I/O failure |
| `outcome` | `proposed / no-change / registered / materialized / not-applied / partial`, distinguishing preparation, no change, an actual operation, and a leftover state; it does not indicate a business pass |
| `source / location` | The original source declaration, the resolved source root, the relative path, the exact selected path, and the original baseline; rejected network addresses are not echoed |
| `ownership` | The original readOnly, plus source_writes and os_enforced, which are always false; a declaration is not treated as access control |
| `config / target / actions` | The exact configuration/target and the paths to be modified; submodule lists the local config, metadata, and the index (which needs separate consent) individually |
| `preflight` | A digest of the identities of the exact source files, registration, configuration, target, and related Git index/refs/config for this run; the BC configuration is bound to the raw bytes actually parsed/planned; it is not an approval or a permanent credential |
| `findings / written / native` | Stable codes, actual paths, and reasons; the paths written; the native commands actually run, with their cwd, exit code, and raw stdout/stderr |
| `suggested_registration` | The new source root for the submodule with the original path/version; only input for a later, separate registration, and not applied automatically |
| `recovery` | The exact paths kept after a failure, readable state/digests, and manual recovery requirements; owner content is never cleaned up or restored automatically |

`BASE_MISMATCH` is a conflict; a missing/invalid fixed object is unavailable.
`SOURCE_ID_CONFLICT / SOURCE_ALIAS / TARGET_CONFLICT / SUBMODULE_CONFLICT / INDEX_CONFLICT`
keep the conflict scope. `INPUT_CHANGED` means that the preflight re-obtained during apply differs from
the given `--expect`: the parsed raw bytes are part of the token, so you must inspect again rather than
reuse the old token.
`OWNERSHIP_CONSENT_REQUIRED / PREFLIGHT_REQUIRED / INDEX_CONSENT_REQUIRED` grant no implicit permission.

Each input is read only once; the tool is neither a file-system transaction nor a sandbox against
malicious concurrent processes. Do not inspect or apply while the source or target is still being
modified by another process.

<a id="cli"></a>
## Read-only CLI by default

In the following, the cwd is the selected project root; use the actual configured script/interpreter
locations on this machine. Angle-bracket placeholders must be replaced with the real inputs for this run.
An existing BC source can be selected directly by ID:

```text
python -B -X utf8 .github/utilities/setup_domain_source.py --root . --config bc-config.yaml --source-id owned-domain
```

When proposing a source that is not yet registered, supply all six fields:

```text
python -B -X utf8 .github/utilities/setup_domain_source.py --root . --config bc-config.yaml --source-id owned-domain --kind git --source-root "../existing-domain-source" --source-path domain-model --baseline <full-local-commit> --read-only
```

`--owned-source` replaces `--read-only` only to declare readOnly false; it does not allow writing the source.
Missing fields are not filled in from the existing configuration or HEAD. Output is JSON; there is no
file-report switch, and inspect writes nothing to disk.
Argument usage errors exit 2 via argparse; readable conflicts and input failures still produce JSON, with exit 1 and 2 respectively.

After confirming that this exact config operation is authorized, add the following to the **same set of source arguments**:

```text
--operation register --apply --owned-target --expect <preflight-from-this-inspect>
```

If the configuration/index/refs/source have changed, the old token is invalid; you cannot simply swap
the token to get around the conflict.
register does not commit or stage, and does not interpret a readonly registration as materialized.

<a id="submodule"></a>
## Optional: create a native submodule only from an owned local repository

This is not the default. First inspect with `--operation submodule --target <exact-relative-target>`;
the proposal lists the target checkout, `.gitmodules`, local config, `.git/modules/<source-id>`, and the index.
Only after both the local source/target operation and the index change have been authorized, add:

```text
--apply --owned-target --index-consent --expect <preflight-from-this-submodule-proposal>
```

The actual native operations are: `git clone --local --no-hardlinks --no-checkout --template=`
with an explicit `--separate-git-dir`; `update-ref --no-deref HEAD` in the **new module** to pin the
object; writing files from the original regular blobs; and building the module index with
`update-index --index-info`. No `checkout`, clean/smudge/textconv, source hooks, template hooks, or
recursive submodule update is run. Links/gitlinks in the full commit, paths that cannot be written
safely, and case aliases are rejected before writing.

It then appends only this native module's `.gitmodules`/local config sections, and stages `.gitmodules`
and the exact gitlink with raw `hash-object --stdin` and `update-index --index-info`; `.gitattributes`
filters are not allowed to write these bytes. Staged entries, refs, and configuration prefixes unrelated
to the target are kept. The local URL uses the file-system path of the explicit source root, which the
proposal/log discloses; this is a local-machine integration, not a portable remote URL.

The source must have self-contained local objects; shallow/promisor/alternates are not supported. The
target must be an independent, non-shared checkout, and the source and parent repositories must use the
same Git object format (SHA1 or SHA256, never mixed).
An existing module ID/path, a mismatch between the staged and working `.gitmodules`, an owner lock, a
non-empty target, or incomplete metadata all stop the operation. If HEAD already has `.gitmodules` but it
is missing from the index, this is treated as a deletion already staged by the owner, even if the working
file is still present and the new checkout target does not exist yet, and it conflicts before clone;
index consent cannot undo that intent. Likewise, the metadata identity of a case alias cannot be silently
rebuilt. Only when HEAD truly lacks this metadata, or the parent repository is truly unborn, can the
operation be treated as a genuinely new creation; an unreadable HEAD is not treated as a new repository.
HEAD here is used only to check the parent repository's owner/index intent and does not replace the
explicit fixed baseline of the domain source.
The checkout target must not be the same as or overlap the `.gitmodules` file, including case variants
and descendant paths. Allowing the file protocol is limited to that exact local clone command, and the
user/global Git config is never changed.
There is no commit/push operation, and neither source readOnly, the existing configuration, nor `--apply`
is treated as index consent.

<a id="recovery"></a>
## Failure and recovery

The configuration is replaced by creating a new temporary file in the same directory and checking the
original bytes; the owner's file is never truncated first. If writing/replacing fails, the created
temporary file or the partial checkout/module metadata is kept, and `outcome: partial` and `recovery`
give the exact locations; nothing is deleted recursively, the index is not reset, the source is not
written back, and unfinished steps are not reported as successfully skipped.

Recovery requires an authorized owner to first compare the previous digests in the report with the
current bytes, index/refs, and subsequent edits, and to handle only the exact files/metadata confirmed
to belong to this operation. The tool has no automatic restore/cleanup command.
When a partial directory exists, a retry does not claim no-change; later owner content remains protected.
Successful local preparation/integration does not prove that domain facts, the application, remote
platforms, human approval, or a release have passed.

On Windows, native commands set `core.longpaths=true` only for that invocation, to prevent failures on
the longer SHA256 object paths in module metadata; the owner's core.longpaths configuration is not
changed. Other hosts must be verified in their actual environment.
