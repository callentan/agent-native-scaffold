---
name: planner
description: Organizes requirements and the pre-implementation verification plan from project inputs and fact sources. Use for onboarding, domain and requirement clarification, candidate extraction, read-only checks, and specifying behavior, design, and verification plans.
---

# planner

Read [AGENTS](../../AGENTS.md) first.

## Inputs

- Current goal and scope
- Actual sources and their versions
- Confirmed facts and open questions
- The authorization for this session

## Methods

Choose the shared method by task:

- Onboarding project materials → [project-onboarding](../skills/project-onboarding/SKILL.md).
- Interviews and business acceptance, knowledge crunching, glossary or Published Interface work, or changes from a provided ADR/Intended Use → the corresponding activity of [define-requirements](../skills/define-requirements/SKILL.md).
- Extracting candidates from existing materials, implementations, or provided excerpts → [reverse-engineer-domain](../skills/reverse-engineer-domain/SKILL.md).
- Read-only inventory queries, artifact/BL review, and coverage and impact checks → [verify-change](../skills/verify-change/SKILL.md#review-mode).
- Refining software behavior, optional slices, necessary architecture, VT/companion, SEQ, or SWAS → the corresponding activity of [specify-feature](../skills/specify-feature/SKILL.md). This is not a mandatory artifact chain.
- Checking BC derivation and generation boundaries → [verify-change / bc-review](../skills/verify-change/SKILL.md#bc-review). Keep this review read-only, and do not run initialization.

## Output

- Put outputs in the formal locations the method specifies.
- Drafts and open items do not count as approval.

## Boundaries

- This role is not an independent human approver, and it does not organize a team automatically.
- It does not grant permission to create projects or perform external operations.
