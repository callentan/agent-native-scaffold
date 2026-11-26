# Lightweight domain overview (TBD)

Single-context or lightweight projects can maintain shared terms, concept relationships, business rules, context responsibilities, directed exchanges, and sources here while keeping [domain-model/README.md](README.md) as a static modeling guide. When a section outgrows this page, adopt the [standalone forms](README.md#optional-forms) without renumbering or moving existing rule anchors.

<a id="terms"></a>
## Shared terms

The same word can mean different things in different contexts. Record the business definition, easily confused meanings, and source; do not use a technical class name in place of a definition.

| Term | Owning context | Business meaning | Aliases or easily confused meanings | Source and confirmation status |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | To be confirmed; source TBD |

<a id="concepts"></a>
## Concepts and relationships

Record the concepts and how they relate. When a relationship's direction, cardinality, conditions, or state meaning is unclear, keep it as a question; do not fill in default rules.

| Concept ID and name | Owning context | Business meaning, related behavior, or states | Source and confirmation status |
|---|---|---|---|---|
| TBD | TBD | TBD | To be confirmed |

| Relationship ID | From concept → to concept | Meaning, direction, and cardinality constraints of the relationship | Conditions under which it holds, or restrictions | Sources and open items |
|---|---|---|---|---|
| TBD | TBD → TBD | TBD | TBD | TBD |

<a id="rules"></a>
## Business rules

Give each real rule a stable `RULE-NNN` identifier and an ASCII anchor; the `rule-nnn` below only demonstrates the placeholder structure, so replace both when filling it in. Do not renumber a rule when its wording changes; when withdrawn, keep its basis and never reassign the number.

<a id="rule-nnn"></a>
### RULE-NNN: TBD (placeholder rule)

| Field | Content |
|---|---|
| Status | To be confirmed; not yet a business fact |
| Applicable context and scope | TBD |
| Conditions, constraints that must hold, and forbidden behavior | TBD |
| Boundaries, exceptions, and handling of undefined cases | TBD; do not fill unknowns with default values |
| Fact source, confirmer, and date | TBD |
| Change basis and original baseline | TBD |

REQs, SRs, and designs reference the file and anchor where a rule lives; do not copy rule text into several places.

<a id="contexts"></a>
## Context responsibilities and fact ownership

Contexts are divided by business responsibility and need not map to services, repositories, subprojects, or code layers. When one context is enough, do not split it artificially; technical patterns such as entities, value objects, aggregates, and repositories are not mandatory.

<a id="ctx-nnn"></a>
### CTX-NNN: TBD (placeholder context)

| Field | Content |
|---|---|
| Business capabilities and decisions it is responsible for | TBD |
| Matters it is explicitly not responsible for | TBD |
| Business facts it owns and maintains | TBD |
| External facts it only uses but does not own, and their owners | TBD |
| Links to related concepts and rules | TBD |
| Sources, confirmation status, and open boundaries | TBD |

<a id="exchanges"></a>
## Directed information exchange

State the provider and consumer separately, with the fact owner and dependency agreement. Do not merely write "the two contexts interact", and do not decide message middleware or interface implementation in advance.

| Provider → consumer | Information or capability provided | Fact owner | Trigger, timeliness, and business agreement on failure | Source, status, and open items |
|---|---|---|---|---|
| TBD → TBD | TBD | TBD | To be confirmed | TBD |

<a id="sources"></a>
## Sources, facts, and open items

Keep a locatable source, a date, and a confirmation basis for every fact. Keep user-confirmed facts, analysis proposals, and open questions apart; a reasonable derivation is not a confirmation. For an unreadable source, record the limitation instead of guessing.

| Fact or question ID | Content and the owning concept, rule, or context | Status (Confirmed / Proposal / Open) | Source location, date, and confirmation basis | Who needs to confirm what |
|---|---|---|---|---|
| TBD | TBD | Open | TBD | TBD |
