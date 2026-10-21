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

> Optional architecture specification compilation; not proof of architecture approval, risk acceptance, or release. Read the [SWAS guide](../../architecture/README.md#architecture-specifications) and the [metadata conventions](../../domain-model/README.md#artifact-metadata) first, then copy it to `architecture/SWAS-NNN-<slug>.md` as needed. Once the project/context is clear, replace the placeholders, delete this notice, and check the relative links from the actual location.

<a id="basis"></a>
## Compilation scope and original baselines

| Field | Content |
|---|---|
| Purpose, scope of use, and non-goals | TBD |
| Scope actually read this time, and source version/digest baselines | TBD; state each unreadable original file or unknown baseline item by item |
| Record date and author | TBD; content state and confirmation statements belong in the frontmatter |
| Completeness limitations and required decisions | TBD; when sources are missing, only a partial description can be delivered |

The frontmatter `upstream` declares the actual artifact references; the body only explains and navigates to sources and does not maintain another relationship or approval table. An existing derived model can serve as an entry point, but baselines must be checked against the original text; without a model, do not fabricate export results, and do not write back to read-only domain sources.

<a id="perspectives"></a>
## Architecture description

| Perspective | Navigation to the actual original text/baseline and necessary explanation | Missing items and blocked conclusions |
|---|---|---|
| Business: goals, contexts, capabilities, and responsibilities | TBD: domain/REQ sources | TBD |
| Logical: components, dependencies, interfaces, and decisions | TBD: ABB/ADR sources | TBD |
| Runtime: scenarios, participants, events, and failure boundaries | TBD: UC/SEQ/interface sources | TBD |
| Deployment: actual environment, node/process allocation, and constraints | TBD: existing deployment/environment sources; if none, not available | TBD |

Logical components do not imply a deployment topology. Cite languages, frameworks, endpoints, containers, safety classifications, and service guarantees only when they have actually been selected or provided; do not fill unknowns with a "conventional architecture".

<a id="views"></a>
## Completeness of the nine source views

This table follows the nine view semantics of the [model contract](../../.github/contracts/README.md), but it is not a second model: it keeps only readability, original-text navigation/baselines, and gaps, and does not copy domain text, the canonical relationship list, or actual results.

`available` means the required sources are readable and complete, with at least one verifiable reference; `partial` means some references exist and there are specific gaps; `unverified` means the sources are missing, unreadable, or their baselines cannot be verified, so no reference can be claimed. None of the three equals `pass`, approval, or released. A missing required primary input is an input error and must not be disguised as a missing optional view. Keep the row even when an optional view is missing; marking a view not applicable also needs a scope basis and cannot be done merely by leaving it blank.

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

When real model data is used, the shape of `artifactRefs` / `evidenceRefs` / `gaps` follows the existing schema: `unverified` uses empty references and a specific gap, and `partial` keeps the checked references and missing items. The reading navigation here does not replace data validation and does not claim that an exporter exists.

<a id="review"></a>
## Review, risk, and verification limitations

- Reading entry points for the original requirements, design constraints, and actual VTs: TBD; results stay in the original records and are not summarized as "all passed".
- Unconfirmed decisions, missing views, and who must supply what: TBD.
- Differences between old and new baselines, affected diagrams/requirements/verification, and entry points pending re-review: TBD.
- Delivery format and actual checks this time: TBD; this form provides only Markdown, not a PDF/presentation renderer; mark exports not run as `not-run`.

Content that calls itself Approved, a complete table of contents, or diagrams that render cannot certify approval. Only an actual, locatable decision for this baseline can form a confirmation statement; when risk, release, or verification sources are missing, do not invent conclusions.
