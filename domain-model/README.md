# Domain model

This directory records business meaning and boundaries; it is not a diagram of code layers. It holds guidance notes and blank sections; there is no confirmed business model yet. For a business task, fill in known facts or reference the existing model; for a maintenance task without business involvement, state why this does not apply and do not invent content to fill the directory.

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
|---|---|---|---|
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

To reference an existing local domain source, check its actual root, path, and pinned baseline against the [existing BC fields](../architecture/README.md#bc-configuration) and the [read-only onboarding preflight](../docs/domain-sources.md).
Registering a reference does not replace this guide or business text. Creating a local submodule needs separate, explicit authorization; there is no permission to write back to the source, access the network, or commit. A readOnly declaration is not an OS permission setting.

When authorized to read local documents or explicit transcripts, you may optionally use [source candidates and transparent scoring](../docs/source-extraction.md); byte identities, paragraph/line/table/turn locations, and candidates are not formal facts or approvals.
Contradicting sources, open wording, and later confirmation still follow the [reverse-engineering method](../.github/skills/reverse-engineer-domain/SKILL.md); a high score does not select a business rule, and sending audio or data externally requires separate authorization.

| Fact or question ID | Content and the owning concept, rule, or context | Status (Confirmed / Proposal / Open) | Source location, date, and confirmation basis | Who needs to confirm what |
|---|---|---|---|---|
| TBD | TBD | Open | TBD | TBD |

Business goals and requirements go back to the [stakeholder requirements entry point](../stakeholder-requirements/README.md), and software behavior to the [software requirements entry point](../software-requirements/README.md). When a rule or boundary changes, handle dependencies, old results, and items pending re-review per the [semantic impact check](../verification/README.md#change-impact); a referencing artifact can be affected even if it did not copy the specific values.

<a id="optional-forms"></a>
## Standalone domain artifacts as needed

**The lightweight path above remains valid.** A single context or small maintenance task can keep recording terms, relationships, rules, responsibilities, exchanges, and sources in this README, without creating every artifact below or installing tools first. Adopting a form must not renumber, replace, or move existing IDs, anchors, rule text, or owner content.

Copy a form only when the material must be referenced on its own or has outgrown a single page. Default locations are in the tables below; existing project locations stay unchanged. When multiple subdomains or contexts are genuinely needed, the domain materials may be organized under `domain-model/subdomains/<slug>/contexts/<slug>/`; nesting is optional and imposes no split by service, repository, project, or code layer. REQs, QASs, SRs, and scenarios/VTs still belong in their own directories.

<a id="strategic-forms"></a>
### Business boundaries, capabilities, and behavior

| Content to record as needed | Form | Default formal location |
|---|---|---|
| Subdomain goal, boundaries, business responsibilities, and external relationships | [SD](../_templates/items/subdomain.md) | `domain-model/SD-NNN-<slug>.md` |
| Context responsibilities, owned/consumed facts, and direction | [CTX](../_templates/items/bounded-context.md) | `domain-model/CTX-NNN-<slug>.md` |
| Business capability, owner, and use case navigation | [CAP](../_templates/items/capability.md) | `domain-model/CAP-NNN-<slug>.md` |
| Actors, normal/alternative/rejection paths, and observable postconditions | [UC](../_templates/items/use-case.md) | `domain-model/UC-NNN-<slug>.md` |
| Constraints derived from a business RULE, applicable states, and criteria | [INV](../_templates/items/invariant.md) | `domain-model/INV-NNN-<slug>.md` |
| Specific questions, conflicts, impact, and decision evidence | [BL](../_templates/items/backlog-item.md) | `domain-model/BL-NNN-<slug>.md` |
| Quality stimulus, environment, response, and sourced measures | [QAS](../_templates/items/quality-attribute-scenario.md) | `stakeholder-requirements/QAS-NNN-<slug>.md` |
| Standalone scenario criteria and run entry points for UC/REQ/INV/QAS | [TS](../_templates/items/validation-scenario.md) | `verification/TS-NNN-<slug>.md` |

A RULE remains owned by its stable anchor in the original domain file. An INV first references the RULE, then states the constraint. Do not infer rules from code or aggregate candidates. A CAP's use case list is for navigation only; each UC declares its own upstream capability. Keep a BL's handling progress separate from its decision evidence; a passed response deadline does not mean the question is resolved. When a QAS lacks a metric, keep an explicit gap and fill in no default SLA; see [quality inputs](../stakeholder-requirements/README.md#quality-inputs) and the [scenario guide](../verification/README.md#domain-scenarios).

<a id="integration-forms"></a>
### Context integration materials

| Content to record as needed | Form | Default formal location |
|---|---|---|
| Fact owner, relationship type, translation, and dependency for each direction | [Context map](../_templates/items/context-map.md) | `domain-model/CM-NNN-<slug>.md` |
| Elements actually promised, consumers, semantic version, and change/notification proposals | [Published Interface](../_templates/items/published-interface.md) | `domain-model/PI-NNN-<slug>.md` |
| Partner responsibilities, producing/consuming direction, contract, and failure boundaries | [Integration partner](../_templates/items/integration-partner.md) | `domain-model/IP-NNN-<slug>.md` |

Choose relationship patterns from known needs; ACL, open host service, shared kernel, and similar patterns are not the default architecture. A consumer's information need does not automatically become a provider commitment. When version, failure policy, or translation responsibility is unknown, keep it as a question; a breaking change requires a recorded rationale, affected consumers, and a version/notification proposal. Without authorization, do not modify external sources or actually send notifications.

<a id="tactical-forms"></a>
### Optional tactical materials

Use these only when an explicit task genuinely needs them. Without a basis for boundaries, rules, or identity, keep candidates and questions; a form's existence is not a reason to choose an implementation pattern.

| What distinguishes the role | Form | Default formal location |
|---|---|---|
| Candidate boundary, root, and lifecycle for constraints that must be upheld together | [Aggregate](../_templates/items/aggregate.md) | `domain-model/AGG-NNN-<slug>.md` |
| A concept identified by an enduring business identity that changes over its lifecycle | [Entity](../_templates/items/entity.md) | `domain-model/ENT-NNN-<slug>.md` |
| Meaning identified by value, equality conditions, units, and validity | [Value object](../_templates/items/value-object.md) | `domain-model/VO-NNN-<slug>.md` |
| Object creation, initial state, and responsibility for validity | [Factory](../_templates/items/factory.md) | `domain-model/FAC-NNN-<slug>.md` |
| Domain operations that do not fit within a single entity/value object | [Domain service](../_templates/items/domain-service.md) | `domain-model/DS-NNN-<slug>.md` |
| Sourced business decisions, conditions, and conflict/expiry boundaries | [Policy](../_templates/items/policy.md) | `domain-model/POL-NNN-<slug>.md` |
| Meaning of a fact that has occurred, its production/consumption, and semantic evolution | [Domain event](../_templates/items/domain-event.md) | `domain-model/EVT-NNN-<slug>.md` |

These records presuppose no endpoints, databases, message middleware, transactions, or performance/delivery guarantees, and provide no regulatory classification. Fill in rules, lifecycles, collaborators, and version expectations from sources; without a source, state who must supply them. A completed form does not mean the implementation or behavior has been verified.

<a id="governance-forms"></a>
### Optional intended use and external risk references

| Content to record as needed | Form | Default formal location |
|---|---|---|
| Purpose, users, environment, use boundaries, and candidate changes | [Intended Use](../_templates/items/intended-use.md) | `domain-model/IU-NNN-<slug>.md` |
| Actual references to external analyses/controls/residual risks and decisions | [Risk control](../_templates/items/risk-control.md) | `domain-model/RC-NNN-<slug>.md` |

Existing locations and external-fact ownership stay unchanged; the [governance guide](../docs/governance.md#intended-use) explains applicability and responsibility gaps. Keep initial source organization separate from revising an existing intended use; a revision still reads the complete original text and baseline per the [existing method](../.github/skills/define-requirements/SKILL.md#intended-use). Medical/QMS is not assumed by default. Do not calculate or accept risk, or confirm intended use, on behalf of the external risk owner; unknowns block only the affected decisions.

When a standalone review or tool-use basis is needed, put the record in the [verification directory](../verification/README.md#optional-reviews), not in a domain rule or VT result. Read model sources through the [existing fields](../docs/governance.md#source-views); do not add risk values or fabricate relationships to complete an export.

<a id="artifact-metadata"></a>
## Optional structured identity and relationships

The [data contract](../.github/contracts/README.md) and its [artifact schema](../.github/contracts/artifact.schema.json) are the single definition of fields, the closed set of kinds, and syntax. New forms already carry `schemaVersion: 1`, the actual `kind`, and `contentState: draft`; `PROJECT/CTX-NNN` and `NNN` are placeholders awaiting project input, not confirmed identities. **Even if a blank form parses, it is not a verified formal artifact.**

When copying a form or adding metadata to existing materials:

1. Check the actual source, authorization, existing files, and stable IDs first. Fill in `scope` only once project/context ownership is clear; for a subdomain or cross-context map, the accountable owner chooses it. Do not guess from the directory or invent a "global" context.
2. Replace placeholders in the file name, frontmatter, title, acceptance IDs, and anchors. Identity is `scope/id`: different scopes may reuse a number, but a number must not repeat within one scope.
3. `upstream` declares the actual resolvable sources; `targets` declares the specific targets with this file's `criterionAnchor`. Relationships and content state are maintained only in the frontmatter; the body holds business meaning, source interpretation, and standalone criteria. Body links may navigate to these references but must not maintain a second state or relationship table.
4. Rules have no kind of their own: if the rule owner has metadata, reference `scope/<owner-id>#rule-...`; sources still using a lightweight README keep ordinary relative links. Do not automatically add metadata to old files just to obtain canonical keys.
5. Acceptance criteria use the full owner ID, such as the placeholder `UC-NNN-AC-01`, preceded on its own line by `<a id="uc-nnn-ac-01"></a>`. Targets use `scope/id#anchor`; `AC-01` alone is not enough. Keep original acceptance numbers; do not reuse a number after withdrawal.
6. Delete the prompts or turn them into explicit questions, and fix every relative URL for the actual location; path examples in prose use forward slashes `/`. `confirmed` requires an actual confirmation source and confirmed baseline; the template provides no approval.

Old materials without metadata can still be read and maintained as usual; valid frontmatter is required only for files explicitly passed to the [current parser](../.github/utilities/README.md). The parser validates each file's own metadata and criterion anchors and duplicate numbers within the given set; it does not verify cross-file coverage, business semantics, or approver identity, and it does not migrate files automatically. Record structural checks, document use, and business execution separately.

<a id="derived-model"></a>
## Optional derived reference view

For a machine index, use the [model tool](../.github/utilities/README.md#model-export) with an explicit real root and scope; do not guess the context from the directory. The optional [source manifest](../.github/contracts/README.md#model-sources) only selects existing artifacts, digests, and pinned baselines; it copies no rules, model text, or results and grants no external read or write permission.

In the nine views, `available/partial/unverified` indicates source completeness. A missing manifest or optional source keeps a specific gap; an invalid main inventory fails and is never downgraded to a missing optional item. The default is read-only; an explicit export only creates new files. An old model may be recomputed to check for source changes or manual edits, but is never overwritten automatically. Rule impact is still checked with the [impact method](../.github/skills/verify-change/SKILL.md#impact); mechanical dependency candidates cannot replace semantic review and the accountable owner's decision.

The [implementation report](../.github/contracts/README.md#implementation-report) reuses existing VT runs and their object/requirement/plan baselines, and checks domain sources read-only. To connect it to the model, select the report separately among existing verification sources; `implementationReports` stores only file references and verified baselines, carries no per-item results, and rewrites neither the domain model nor the source manifest. With no report selected or a source missing, the existing empty reference/gap remains; one successful collection cannot infer current applicability or approval.
