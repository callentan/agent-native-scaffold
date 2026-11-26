# Common work entry point

This common entry point sets the reading path and rules for all work. Humans and agents use the same methods, facts, and results. Method text is maintained only in the actual `SKILL.md` files listed in the [activity navigation](README.md#activities).

## Start here

1. Read the [project registration](PROJECT.md#project), and confirm the current task's goal, scope, basis, and completion conditions.
   - A maintenance request can itself serve as the basis.
   - Creating a US is not mandatory.
2. Choose the matching method from the [README activity navigation](README.md#activities). **Explicitly read the complete `SKILL.md`**, then read the current facts, guides, and forms it links to.
   - Follow this reading path even without native discovery; file names, links, and descriptions do not guarantee automatic inclusion.
3. Read the rules for what you change:
   - Markdown: read the [documentation rules](.github/instructions/docs.instructions.md).
   - Any test: read the [test rules](.github/instructions/tests.instructions.md).
   - Code: also explicitly read the [architecture](.github/instructions/architecture.instructions.md), [coding](.github/instructions/coding.instructions.md), and [security rules](.github/instructions/security.instructions.md) in full, even if the actual paths do not match their initial globs.
   - Extend the matched scope to the actual project; do not assume `src` is the only code location or that tests follow a uniform layout.
4. Before writing, check the actual directory, Git branch, commit, index (staging area), and uncommitted scope.
   - Preserve owner content, the existing locations of rules, and unrelated changes.

## Rules

### Locked files

- A file marked `scaffold: locked` in its first lines, or listed in `.scaffold/locked.txt`, is scaffold-owned. Do not modify, rename, or delete it in any task; only `ddd-scaffold update` writes it.
- Project content goes in project-owned files: [PROJECT.md](PROJECT.md), [project-development.md](docs/project-development.md), `product.md`, `overview.md`, `INDEX.md`, and new formal artifacts. When a locked file needs customizing, record the need in a project-owned file instead.
- `ddd-scaffold verify` lists locked files that differ from the installed receipt. It is a check, not a permission control.

### Authorization and facts

- Do only authorized tasks.
- **When a fact that affects behavior is missing, a source is unreadable, there is a conflict, or authorization is insufficient, stop the affected operations and explain why.**
- Never treat placeholders or proposals as facts.

### Code generation and maintenance

- While the [development guide](docs/development.md) is not configured, do not choose a stack, install dependencies, or generate a project on your own. Documentation-only maintenance with complete inputs may continue.
- Use [generate-code](.github/skills/generate-code/SKILL.md) for initial generation. Use [implement-task](.github/skills/implement-task/SKILL.md) for maintaining existing code or documents.
- Keep subdirectory `README.md` files as static guides; record project scope, lightweight domain tables, coverage gaps, or optional high-level navigation in `product.md`, `overview.md`, or `INDEX.md` rather than appending routine artifacts to `README.md`.
- On a conflict with a non-empty target, explicitly stop writing. Skipped files do not mean that generation is complete.
- The optional [BC configuration](architecture/README.md#bc-configuration) does not grant permission to write sources or execute anything.

### Template updates

- For template versions, or scenario proposals for explicitly named BCs, use [update-template](.github/skills/update-template/SKILL.md). Read the real old, local, and new sources and their exact versions.
- When the old baseline is missing, there is a conflict, or permissions are unclear, stop the affected operations.
- Proposals are not applied. They do not grant any cross-repository Git or platform permission.

### Evidence and handoff

- Handle evidence and impact with [verify-change](.github/skills/verify-change/SKILL.md).
- Handle completing, pausing, or taking over a task with [record-handoff](.github/skills/record-handoff/SKILL.md).
- Do not fabricate results, duplicate authoritative records, or depend on hidden chat context.

## Limits of these files

- Native client discovery and permissions must still be verified in practice, each separately. For the local distribution candidate's scope and the gates that have not been run, see the [distribution guide](docs/distribution.md).
- Roles are not independent human approvers, and they do not organize a team automatically.
- Markdown rules do not replace real permissions, sandboxes, or CI. External operations still require the corresponding authorization.
