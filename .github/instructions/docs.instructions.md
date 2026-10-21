---
applyTo: "**/*.md"
---

# Documentation facts and references

Apply these rules to every Markdown change. They keep facts, proposals, open items, and results distinct, and keep content in its owning record.

## Facts and status

- Distinguish confirmed facts, proposals, open items, and actual results.
- Give every status a source and an applicable baseline. Never pre-fill approval or a pass.
- Keep document checks separate from behavioral acceptance.
- Keep old results with their original baseline. Write `not-run` for anything not run, and state explicitly when evidence is inaccessible.

## Where content belongs

- Read methods from the [README activity navigation](../../README.md#activities). Do not copy whole method bodies.
- Base formal artifacts on the existing forms, following the [form conventions](../../README.md#forms), and keep them in their owning directories.
- Put rule text in the domain model, upstream relationships in the SR, and acceptance-target relationships and run records in the VT.
- Use indexes only to navigate and record gaps. Use logs only to summarize and link to authoritative records.

## Links, IDs, and changes

- Use real relative paths and stable anchors in links. Include the owning artifact in every acceptance ID.
- When renaming or withdrawing, keep the basis and history. Never reuse numbers.
- Handle semantic changes according to [verify-change](../skills/verify-change/SKILL.md#impact). Checking only that links open is not enough.

## Formal artifact check

- When authorized to run the formal artifact check, follow the [tool contract](../utilities/README.md#artifact-checker): an explicit root, an optional exact base, and a new report path.
- Keep the findings' owner/line/target, the counts, and the raw byte baseline.
- `empty` is not a business pass. `--base` does not omit the unchanged inventory, and it is not an index (staging area) check.
- The checker covers only the agreed formal inputs and Markdown syntax. Ordinary guides, coverage, and semantics still need separate review.
- Do not clear errors by removing identity fields, narrowing the scope, or overwriting old reports.

## Language and parsed labels

- Write scaffold-owned prose, headings, form labels, placeholders, and code comments in English.
- Keep the exact form labels that the maintenance tools parse (see the [tool reference](../utilities/README.md)).
