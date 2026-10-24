---
schemaVersion: 1
id: SWAS-NNN
kind: architecture-specification
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# SWAS-NNN: TBD

> Optional architecture specification compilation; not proof of architecture approval, risk acceptance, or release. Read the [SWAS guide](../../architecture/README.md#architecture-specifications) and [metadata conventions](../../domain-model/README.md#artifact-metadata), then copy to `architecture/SWAS-NNN-<slug>.md` as needed; once project and context are clear, replace the placeholders, delete this notice, and check relative links from the actual location.

<a id="basis"></a>
## Compilation scope and original baselines

| Field | Content |
|---|---|
| Purpose, scope of use, and non-goals | TBD |
| Scope actually read this time, and source version/digest baselines | TBD; state each unreadable original file or unknown baseline item by item |
| Record date and author | TBD; content state and confirmation statements belong in the frontmatter |
| Completeness limitations and required decisions | TBD; when sources are missing, only a partial description can be delivered |

The frontmatter `upstream` declares the actual artifact references; the body only explains and navigates to sources and keeps no other relationship or approval table. An existing derived model can be an entry point, but its baselines must be checked against the original text; without a model, do not fabricate export results or write back to read-only domain sources.

<a id="perspectives"></a>
## Architecture description

| Perspective | Navigation to the actual original text/baseline and necessary explanation | Missing items and blocked conclusions |
|---|---|---|
| Business: goals, contexts, capabilities, and responsibilities | TBD: domain/REQ sources | TBD |
| Logical: components, dependencies, interfaces, and decisions | TBD: ABB/ADR sources | TBD |
| Runtime: scenarios, participants, events, and failure boundaries | TBD: UC/SEQ/interface sources | TBD |
| Deployment: actual environment, node/process allocation, and constraints | TBD: existing deployment/environment sources; if none, not available | TBD |

Logical components do not imply a deployment topology. Cite languages, frameworks, endpoints, containers, safety classifications, and service guarantees only when actually selected or provided; do not fill unknowns with a "conventional architecture".

<a id="views"></a>
## Completeness of the nine source views

This table follows the nine view semantics of the [model contract](../../.github/contracts/README.md) but is not a second model; it keeps only readability status, original-text navigation and baselines, and gaps, and does not copy domain text, the canonical relationship list, or results.

`available`: the required sources are readable and complete, with at least one verifiable reference. `partial`: some references exist, with specific gaps. `unverified`: the sources are missing, unreadable, or their baselines cannot be verified, so no reference can be claimed. None of the three equals `pass`, approval, or released. A missing required primary input is an input error and must not be disguised as a missing optional view. Keep the row even when an optional view is missing; marking a view not applicable needs a scope basis, not a blank.

| View | Readability this time | Navigation to the checked original text and baseline | Specific gap/scope of applicability |
|---|---|---|---|
| requirements | unverified | Not provided yet | TBD: actual locations and baselines of REQ/SR/UC |
| stories | unverified | Not provided yet | To be verified whether US is used; not using it does not prevent direct SR/VT |
| architecture | unverified | Not provided yet | TBD: ABB/ADR/integration basis |
| sequences | unverified | Not provided yet | TBD: SEQ, participants, and contracts |
| verification | unverified | Not provided yet | TBD: plans/actual reports and their baselines; an existing file does not mean a run happened |
| quality | unverified | Not provided yet | TBD: QAS, response measures, and measurement basis |
| governance | unverified | Not provided yet | To be verified: applicable governance sources and decision basis |
| risk | unverified | Not provided yet | To be verified: applicable risk/control sources; do not assess acceptability yourself |
| release | unverified | Not provided yet | TBD: version/change control and actual release records |

With real model data, `artifactRefs` / `evidenceRefs` / `gaps` follow the schema: `unverified` uses empty references and a specific gap; `partial` keeps the checked references and missing items. This navigation does not replace data validation or claim that an exporter exists.

<a id="review"></a>
## Review, risk, and verification limitations

- Entry points to the original requirements, design constraints, and actual VTs: TBD; results stay in the original records and are never summarized as "all passed".
- Unconfirmed decisions, missing views, and who must supply what: TBD.
- Differences between old and new baselines, affected diagrams/requirements/verification, and entry points pending re-review: TBD.
- Delivery format and checks this time: TBD; this form provides Markdown only, with no PDF/presentation renderer; mark exports not run as `not-run`.

A document that calls itself Approved, has a complete table of contents, or has diagrams that render cannot certify approval; only an actual, locatable decision for this baseline can form a confirmation statement. When risk, release, or verification sources are missing, do not invent conclusions.
