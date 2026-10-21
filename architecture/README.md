# Architecture and decisions

This directory records the necessary structure, constraints, and trade-offs. There is no confirmed project architecture yet; do not infer services or code layers from directory names. [Business contexts](../domain-model/README.md#contexts) need not map one-to-one to technical components.

Actual design work starts from [specify-feature](../.github/skills/specify-feature/SKILL.md#design-architecture); read the method in full and explicitly read the [architecture rules](../.github/instructions/architecture.instructions.md). The forms below only provide optional structure; they do not imply that an application, an architecture decision, or an approval exists.

<a id="building-blocks"></a>
## Architecture building blocks (ABB, as needed)

When structure, responsibilities, interface collaboration, or design constraints need a separate description, use the [ABB form](../_templates/items/architecture-building-block.md) and save it as `architecture/ABB-NNN-<slug>.md`.

- Read the actual REQ/SR, CAP/context, rules, applicable QAS/ADR, or standalone task; following the [metadata conventions](../domain-model/README.md#artifact-metadata), keep the real identity, draft, and `upstream` in the frontmatter. The body only explains sources and provides reading navigation, without a separate copy of relationships/content state. Old materials are not migrated automatically.
- Distinguish what the block is and is not responsible for, the fact owners, and the directions of dependencies and interactions; design assumptions and open items must not be written as business facts.
- Describe interface contracts, dependency versions, runtime/deployment constraints, quality responses, and observation methods as actually needed. A draft QAS, an undecided ADR, or an unpinned dependency version keeps a gap and blocks the related commitments/selections; do not default to four layers, a language, a cloud platform, or containers.
- Describe sourced design constraints, alternatives, and trade-offs, and how they need to be verified. Distinguish permitted composition-root wiring from dependencies of domain/business control logic; the wiring exception does not authorize every controller to access the database directly or to bypass rules.
- Design constraints that need to be checked on their own use stable identifiers and anchors qualified by their owning artifact, such as `ABB-NNN-VC-01` and `abb-nnn-vc-01`. Reference existing constraints directly instead of writing them again.

For design verification, choose suitable checks according to the [verification layers](../verification/README.md#layers); design verification is not automatically equivalent to REQ business acceptance or SR software behavior verification. Do not force a new ABB for every change; a US is not a mandatory prerequisite for an ABB, and ABBs and VTs can be planned independently once their respective inputs are complete.

<a id="decisions"></a>
## Architecture decision records (ADR, as needed)

Use the [ADR form](../_templates/items/architecture-decision.md) only when a real decision needs its context, alternatives, and history preserved. Create `decisions/` only when creating the first `architecture/decisions/ADR-NNN-<slug>.md`; do not preset an empty directory or fake decisions.

Distinguish proposals, actual decisions, and superseded history. A new ADR starts as `draft`, and the confirmation declaration in the frontmatter is filled in only when a real decision can be located. The body holds the business boundary, options, rationale, costs, consequences, and verification needs, without maintaining a separate approval table. Without a decision by an authorized person, do not write "accepted".

For an incoming ADR, use the actual original text and version, and list the impact on contexts, consumers, interfaces, and verification; notifications are drafts only. For the activity, see [define-requirements](../.github/skills/define-requirements/SKILL.md#incoming-adr). Later decisions are appended as new records linked to the records before and after them; do not rewrite old history or publish automatically to external systems.

<a id="sequences"></a>
## Sequence diagrams (SEQ, as needed)

Use the [SEQ form](../_templates/items/sequence-diagram.md) and save it as `architecture/SEQ-NNN-<slug>.md`; the method entry point is [sequence-diagram](../.github/skills/specify-feature/SKILL.md#sequence-diagram). Based on the actual UC, ABB, rules, and event/interface contracts, state the preconditions, participant responsibilities, information directions, success/rejection/error paths, and their source baselines.

A conceptual cross-context exchange must not automatically be interpreted as a service or transport. When an existing integration/event consumer explicitly requires asynchrony, keep the corresponding boundary; when a contract is missing, do not fill in synchronous calls, a broker, timeouts/retries/ordering/idempotency, or delivery guarantees. When there are only conceptual roles without an ABB mapping, mark the diagram as a partial description with gaps and do not call it a complete runtime sequence. Neither Mermaid source nor rendered output is execution evidence.

<a id="architecture-specifications"></a>
## Architecture specifications (SWAS, as needed)

Use the [SWAS form](../_templates/items/architecture-specification.md) and save it as `architecture/SWAS-NNN-<slug>.md`; compile the actual sources according to [build-architecture-spec](../.github/skills/specify-feature/SKILL.md#build-architecture-spec). Describe the business, logical, runtime, and deployment aspects separately, and check source completeness against the nine views of the [existing model contract](../.github/contracts/README.md).

- `requirements/stories/architecture/sequences/verification/quality/governance/risk/release` only navigate to real original text/evidence and baselines; they do not become a second store of domain facts, relationships, or results.
- A missing optional source keeps `unverified` and a specific gap; partially readable sources give `partial` and keep checkable navigation; only when the required sources are complete is a view `available`. None of these means pass or approval. Not applicable requires a scope basis. An error in a required main input still blocks and cannot be masked by nine empty views.
- When a model exists, first use the [read-only check](../.github/utilities/README.md#model-export) to verify its source baselines, then go back to the original text. The optional [source manifest](../.github/contracts/README.md#model-sources) can register real files/baselines for several explicit scopes; unregistered and missing optional sources each keep their own gap. Do not fabricate ABBs, deployments, risk classifications, or approvals. The model is a reference index, and the SWAS body is still compiled in Markdown; the optional [local export](../docs/document-exports.md) generates sourced HTML/SVG architecture/SEQ views and parameterized presentations, while PDF/PPTX remains unavailable and must not be imitated with another format.

governance/risk sources can use [review records](../_templates/items/review-record.md) and [risk control references](../_templates/items/risk-control.md) as needed; for field ownership, see the [governance guide](../docs/governance.md#source-views). The original decisions on intended use, risk, or waivers still belong to their owners; ADRs/SWAS do not take over external authority, and neither a source being available nor a tool qualification record counts as architecture/regulatory approval.

<a id="bc-configuration"></a>
## Optional BC data configuration

When multiple contexts or domain sources need to be registered explicitly, copy the [configuration form](../_templates/config/bc-config.yaml) to `bc-config.yaml` at the authorized project root. Following the [BC schema](../.github/contracts/bc-config.schema.json) and the [contract notes](../.github/contracts/README.md), fill in the project identity, the contexts, and each source's `id/kind/root/path/baseline/readOnly`; do not add custom command fields.

`root` is the explicit source root, and `path` is a relative path within that root; a pinned baseline must come from an actual object/digest, and a Git source must not use HEAD, a branch name, or an abbreviated hash. The placeholders in the blank form are not Git facts and have not passed valid-configuration acceptance. `developmentRegistration` only references the [actual development registration](../docs/development.md#project-registration) and does not copy commands, secrets, or application configuration; a readable pointer does not mean that the development inputs are complete.

The schema validates structure only; it does not access or download sources or verify their authorization. Before use, confirm that the read directory, write directory, and source baselines match the registration; the configuration does not authorize cloning, updating, committing, or modifying read-only sources. You can use the [local domain source tool](../docs/domain-sources.md#operations) to inspect sources read-only; an explicit register only maintains the existing configuration, and materialization/submodule creation requires a separately chosen target and consent for the index. Filling in the configuration or getting a ready proposal does not mean the source is connected, and it permits no network requests or implicit commits.

When an existing BC needs an implementation summary, provide an explicit commit, scope, and the original VT records according to the [collection contract](../.github/contracts/README.md#implementation-report). The collector checks the local domain root/path/pinned baseline in the configuration and neither clones nor writes back; the source configuration and the code/test locations bind the test object, and new runs keep their own byte baselines. The [output form](../_templates/reports/implementation-report.yaml) is not an execution-input ledger. After the report is separately and explicitly registered as a verification source of the model, it is connected only through the report reference; the nine views still belong to the model, and governance/risk/sequence and similar sources must not be passed off as execution evidence.

## Maintenance entry points

Add links here once real ABBs/ADRs/SEQs/SWASs are created. Record ordinary work progress in the [development log](../logs/README.md); when rules or requirements change, re-review the design and old results according to the [semantic impact check](../verification/README.md#change-impact). Do not use the log as a substitute for the source of design decisions.
