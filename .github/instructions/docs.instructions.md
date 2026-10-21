---
applyTo: "**/*.md"
---

# Documentation facts and references

- Distinguish confirmed facts, proposals, open items, and actual results. Every status needs a source and an applicable baseline; never pre-fill approval or a pass.
- Read methods from the [README activity navigation](../../README.md#activities). Formal artifacts use the existing forms according to the [form conventions](../../README.md#forms) and go in their owning directories; do not copy whole method bodies.
- Rule text belongs to the domain model, upstream relationships to the SR, and acceptance-target relationships and run records to the VT. Indexes only navigate and record gaps; logs only summarize and link to authoritative records.
- Links use real relative paths and stable anchors, and acceptance IDs include their owning artifact. Renames and withdrawals keep their basis and history, and numbers are never reused. Handle semantic changes according to [verify-change](../skills/verify-change/SKILL.md#impact); checking only that links open is not enough.
- Keep document checks separate from behavioral acceptance. Old results keep their original baseline; write `not-run` for anything not run, and state explicitly when evidence is inaccessible.
- When authorized to run the formal artifact check, follow the [tool contract](../utilities/README.md#artifact-checker): an explicit root, an optional exact base, and a new report path. Keep the findings' owner/line/target, the counts, and the raw byte baseline. `empty` is not a business pass; `--base` does not omit the unchanged inventory, and it is not an index (staging area) check.
- The checker covers only the agreed formal inputs and Markdown syntax. Do not clear errors by removing identity fields, narrowing the scope, or overwriting old reports; ordinary guides, coverage, and semantics still need separate review.
- Write scaffold-owned prose, headings, form labels, placeholders, and code comments in English; keep the exact form labels that the maintenance tools parse (see the [tool reference](../utilities/README.md)).
