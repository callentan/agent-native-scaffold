# ddd-scaffold usage

`ddd-scaffold` installs the scaffold into a new project directory and later updates it. This package is maker-side: it is not copied into projects.

## Requirements

- Python 3.11+ and `git` on the PATH.
- Network access only to fetch the scaffold repository (install and update).

## Run it

```
uvx --from git+https://github.com/callentan/agent-native-scaffold ddd-scaffold my-project
```

`pipx install` of the same URL works too. From a checkout, use `PYTHONPATH=cli python -m ddd_scaffold my-project --source .`.

## Install

```
ddd-scaffold                 # prompts: Project name:
ddd-scaffold my-project
```

- Creates `./my-project/` in the current directory and copies every file listed in `docs/distribution-manifest.json`, keeping relative paths.
- Writes the project name into `PROJECT.md` (title and the `Project name` row). No other file is changed except the locked markers below.
- Refuses an existing non-empty target or an invalid name (letters, digits, `.`, `_`, `-`; no reserved names such as `install`, `update`, `verify`, `CON`). Nothing is written on refusal.
- Does not run `git init`, install hooks, create a virtual environment, or choose a tech stack.
- Options: `--source <git URL or local checkout>` (default: the official repository), `--ref <tag or branch>` (default: the latest tag, else the default branch).

Afterwards, read `AGENTS.md`, fill in `PROJECT.md`, and commit the result before any update. Commit `.scaffold/` too; it is the update baseline.

## Locked and project-owned files

| Kind | Which files | Rule |
| --- | --- | --- |
| Locked (default) | Methods, rules, tools, contracts, hooks, workflows, templates, guides | Never edited by the project or agents. Only `update` writes them. |
| Project-owned | Files marked `"projectOwned": true` in the manifest: `PROJECT.md`, `docs/project-development.md`, `.gitignore`, `product.md`, `overview.md`, every `INDEX.md` | Seeded once. `update` never overwrites them. |

Locked files carry a visible marker where the type allows a comment: `<!-- scaffold: locked -->` in Markdown, `# scaffold: locked` in Python, YAML, text, lock files, and shebang scripts. JSON files, `_templates/`, and extensionless files without a shebang have no marker; `.scaffold/locked.txt` lists every locked file.

## Update

```
ddd-scaffold update                 # dry run: prints the plan
ddd-scaffold update --apply         # writes it
```

Run it from the project directory (or pass `--root`). It takes the same `--source` and `--ref` options as install.

| Situation | Result |
| --- | --- |
| Locked file unchanged locally, changed upstream | `update`: overwritten |
| Locked file modified locally | `conflict`: not written, exit code 1 |
| Locked file modified locally and `--force-locked` | `overwrite`: old content saved to `.scaffold/overwritten/<time>/` first |
| Locked file deleted locally | `restore` |
| New upstream file | `add` (locked) or `seed` (project-owned) |
| Project-owned file changed upstream | `review`: never written; the diff against the installed baseline goes to `.scaffold/update-report.md` |
| File removed upstream | `removed-upstream`: reported only, file kept |

- `--apply` refuses a Git workspace with uncommitted changes unless `--allow-dirty` is given, so every change can be rolled back with Git.
- Without `.scaffold/receipt.json` the update stops; it never guesses a baseline.
- Exit codes: 0 success, 1 conflicts remain, 2 error.
- Nothing is committed. Review the result with `git diff`.

## Verify

```
ddd-scaffold verify
```

Lists locked files that are `modified` or `missing` compared with the receipt (exit code 1 if any). It is a check, not a permission control; wire it into a hook or CI if the project wants it enforced.

## State directory

| Path | Purpose |
| --- | --- |
| `.scaffold/receipt.json` | Source, ref, commit, and the SHA-256 of each installed file |
| `.scaffold/locked.txt` | One locked path per line |
| `.scaffold/base/` | Upstream copies of project-owned files, used for update diffs |
| `.scaffold/update-report.md` | Latest applied update report |
| `.scaffold/overwritten/` | Backups made by `--force-locked` |

## Tests

```
python cli/tests/test_cli.py
```

The tests install from a copy of this repository's manifest files into temporary directories. The remote fetch path (`git clone`, latest-tag lookup) is not covered by them.
