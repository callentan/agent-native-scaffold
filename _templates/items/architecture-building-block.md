---
schemaVersion: 1
id: ABB-NNN
kind: architecture-building-block
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# ABB-NNN: TBD

> Optional design form; there is no confirmed architecture yet. Read the [architecture guide](../../architecture/README.md#building-blocks) and the [metadata conventions](../../domain-model/README.md#artifact-metadata) first, then copy it to `architecture/ABB-NNN-<slug>.md` as needed. Once the project/context is clear, replace placeholder IDs and anchors, delete this notice, and check the relative links.

<a id="basis"></a>
## Basis and scope

| Field | Content |
|---|---|
| Source reading navigation and design rationale | TBD: actual REQ/SR, CAP/context, QAS, applicable ADR, or task basis, with baselines |
| Related business context, rules, and boundaries | TBD: links; do not copy the full rule text |
| Design scope and non-goals | TBD |
| Record date and proposer | TBD; content state and confirmation statements belong in the frontmatter |

`upstream` is the only place to declare sources; the body navigation explains the sources and does not maintain a separate relationship table. An existing US can explain the slice, but it is not a mandatory prerequisite for an ABB. While a QAS is still draft, an ADR is undecided, or versions are unknown, the related design is only a candidate; do not use the form to complete technology selection.

<a id="structure"></a>
## Structure, responsibilities, and collaboration

| Item | Content |
|---|---|
| Components and structure description | TBD |
| What it is and is not responsible for | TBD |
| Facts owned and external facts only used | TBD |
| Provider → user, information or capability, and agreements | TBD |
| Interfaces, dependencies, and failure boundaries | TBD |
| Constraint sources, assumptions, and open items | TBD |

Contexts are not required to map to services, repositories, or code layers. Record uncertain boundaries and implementations only as proposals.

<a id="interfaces"></a>
## Interfaces, dependencies, and integration (when applicable)

| Provider → consumer and fact owner | Contract text, version, and semantics | Port/adapter boundary and dependency direction | Source or missing item for failure, timing, and compatibility agreements |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

Adopt an asynchronous boundary only when a source provides an event consumption/asynchronous integration contract; a conceptual exchange is not a service call. While dependency products and versions are not selected, keep the missing items; do not add a default SDK, broker, or delivery guarantee. Check the legitimate composition entry point and the domain dependency direction separately against the [architecture rules](../../.github/instructions/architecture.instructions.md).

<a id="runtime"></a>
## Runtime, deployment, and quality constraints (when applicable)

| Concern | Navigation to actual sources/baselines, applicability, and specific gaps |
|---|---|
| Runtime collaboration and SEQ | TBD; if there is no sequence source, state that it is not available |
| Deployment/environment and dependency versions | TBD; do not derive infrastructure from logical components |
| QAS response, observation, and judgment method | TBD; while metrics/measurement are undecided, satisfaction cannot be confirmed |
| Safety, governance, or risk constraints | TBD: sources actually provided and applicable; without such material, do not derive classifications or approvals |

<a id="verification-needs"></a>
## Design constraints and verification needs

Copy the block below once for each constraint that needs separate verification; link existing constraints directly. A design check is not automatically equivalent to business or software behavior acceptance.

<a id="abb-nnn-vc-01"></a>
### ABB-NNN-VC-01: TBD

- Sourced design constraint and its scope of application: TBD.
- Refinement basis and navigation to the original text: TBD; relationships and this artifact's content statements still belong in the frontmatter.
- Observable pass criterion: TBD.
- Required design/component/integration checks and their preconditions: TBD; do not presume tests already exist.

The VT maintains the target reference to this constraint; verification results are not stored again here.

<a id="tradeoffs"></a>
## Trade-offs and changes

| Alternative or change | Rationale for adopting or rejecting it, cost, and risk | Basis, status, or related ADR link |
|---|---|---|
| TBD | TBD | To be confirmed |

Write an ADR only when a long-term decision needs to be kept. After related rules or requirements change, re-review the design boundaries and verification needs; old results remain bound to their original baselines.
