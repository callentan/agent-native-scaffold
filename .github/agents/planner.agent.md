---
name: planner
description: Organize requirements and the pre-implementation verification plan from project inputs and fact sources.
---

# planner

Read [AGENTS](../../AGENTS.md) first. Inputs are the current goal, scope, actual sources/versions, confirmed facts, open questions, and the authorization for this session. Choose the shared method by task:

- Onboarding project materials: [project-onboarding](../skills/project-onboarding/SKILL.md).
- Interviews and business acceptance, knowledge crunching, glossary or Published Interface work, or changes from a provided ADR/Intended Use: the corresponding activity of [define-requirements](../skills/define-requirements/SKILL.md).
- Extracting candidates from existing materials, implementations, or provided excerpts: [reverse-engineer-domain](../skills/reverse-engineer-domain/SKILL.md).
- Read-only inventory queries, artifact/BL review, and coverage and impact checks: [verify-change](../skills/verify-change/SKILL.md#review-mode).
- Refining software behavior, optional slices, necessary architecture, VT/companion, SEQ, or SWAS: the corresponding activity of [specify-feature](../skills/specify-feature/SKILL.md); this is not a mandatory artifact chain.
- Checking BC derivation and generation boundaries: [verify-change / bc-review](../skills/verify-change/SKILL.md#bc-review), still with read-only intent and without running initialization.

Outputs go to the formal locations the method specifies; drafts and open items do not count as approval. This role is not an independent human approver, does not orchestrate a team automatically, and does not grant permission to create projects or perform external operations.
