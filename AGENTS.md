# Common work entry point

Humans and agents use the same methods, facts, and results. Method text is maintained only in the actual `SKILL.md` files listed in the [activity navigation](README.md#activities).

## What to read

1. Read the [README project registration](README.md#project) and the goal, scope, basis, and completion conditions of the current task; a maintenance request can itself serve as the basis, and creating a US is not mandatory.
2. Choose the matching method from the [README activity navigation](README.md#activities), **explicitly read the complete `SKILL.md`**, and then read the current facts, guides, and forms it links to. File names, links, and descriptions do not guarantee automatic inclusion; follow this reading path even when there is no native discovery.
3. When changing Markdown, read the [documentation rules](.github/instructions/docs.instructions.md); when changing any test, read the [test rules](.github/instructions/tests.instructions.md). When changing code, also explicitly read the [architecture](.github/instructions/architecture.instructions.md), [coding](.github/instructions/coding.instructions.md), and [security rules](.github/instructions/security.instructions.md) in full, even if the actual paths do not match their initial globs. Extend the matched scope to fit the actual project; do not assume that `src` is the only code location or that there is a uniform test layout.
4. Before writing, check the actual directory, Git branch, commit, index (staging area), and uncommitted scope; preserve owner content, the existing locations of rules, and unrelated changes.

## Boundaries

- Do only authorized tasks. When a fact that affects behavior is missing, a source is unreadable, there is a conflict, or authorization is insufficient, stop the affected operations and explain why; never treat placeholders or proposals as facts.
- While the [development guide](docs/development.md) is not configured, do not choose a stack, install dependencies, or generate a project on your own; documentation-only maintenance with complete inputs may continue.
- Use [generate-code](.github/skills/generate-code/SKILL.md) for initial generation and [implement-task](.github/skills/implement-task/SKILL.md) for maintaining existing code/documents. On a conflict with a non-empty target, explicitly stop writing; skipped files do not mean that generation is complete. The optional [BC configuration](architecture/README.md#bc-configuration) does not grant permission to write to sources or to execute anything.
- For template versions or scenario proposals for explicitly named BCs, use [update-template](.github/skills/update-template/SKILL.md) and read the real old/local/new sources and their exact versions; when the old baseline is missing, there is a conflict, or permissions are unclear, stop the affected operations. Proposals are not applied, and they do not grant any cross-repository Git/platform permission.
- Handle evidence and impact with [verify-change](.github/skills/verify-change/SKILL.md); handle completing, pausing, or taking over a task with [record-handoff](.github/skills/record-handoff/SKILL.md). Do not fabricate results, duplicate authoritative records, or depend on hidden chat context.

Native client discovery and permissions must still be verified in practice, each separately; for the scope of the local distribution candidate and the gates that have not been run, see the [distribution guide](docs/distribution.md). Roles are not independent human approvers and do not organize a team automatically; Markdown rules do not replace real permissions, sandboxes, or CI, and external operations still require the corresponding authorization.
