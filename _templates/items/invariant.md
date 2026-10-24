---
schemaVersion: 1
id: INV-NNN
kind: invariant
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# INV-NNN: TBD business invariant

> Optional blank form; not a rule reverse-engineered from code. Read the [rules guide](../../domain-model/README.md#rules) and [metadata conventions](../../domain-model/README.md#artifact-metadata) first. Copy to `domain-model/INV-NNN-<slug>.md` only when needed; confirm project and context, replace `PROJECT/CTX-NNN`, the ID, title, and acceptance anchors, fix relative links, keep any existing rules, then delete this hint.

<a id="basis"></a>
## Rule basis and derivation boundary

- Location and baseline of the original business RULE: TBD; a business basis must exist first, and an implementation default cannot be cited in its place.
- Known facts and the basis for confirming them: TBD.
- Explanation of how this constraint is derived from the RULE: TBD; the derivation itself does not gain approval.
- Open questions and who needs to confirm them: TBD.

Declare the parsable rule owner and its RULE anchor in `upstream`; legacy rules without metadata keep plain links, and do not invent keys for them.

<a id="constraint"></a>
## Exact constraint

| Constraint information | Content |
|---|---|
| Business objects and boundary it applies to | TBD |
| Relationship or condition that must hold | TBD; point to the original rule instead of creating a separate numeric policy |
| States and points in time where the constraint applies | TBD |
| Actions that may affect the constraint | TBD |
| Outcomes forbidden when the constraint is violated | TBD; keep undefined handling as a gap |
| Business rationale and source of the constraint | TBD |

An invariant does not automatically decide the aggregate root, transactions, locks, or storage approach. When the points in time where it applies, or the concurrency rules, are unclear, do not claim that every state transition preserves it.

<a id="acceptance"></a>
## Constraint criteria

<a id="inv-nnn-ac-01"></a>
### INV-NNN-AC-01: Constraint is maintained

- Preconditions, affected actions, and observation point: TBD.
- Business relationship to maintain and how to judge it: TBD.
- Boundary/violation cases and side effects that must not occur: TBD.
- Parts that cannot be judged yet and why: TBD; this is a draft criterion, not a passed verification.

<a id="questions"></a>
## Gaps and evolution

- Impact of missing rules, conflicting rules, or unconfirmed derivations: TBD.
- Who needs to supply what, and related BLs: TBD.
- Old and new rule baselines, and UC, REQ, SR, and scenario/VT items pending re-review: TBD; do not overwrite historical results.
