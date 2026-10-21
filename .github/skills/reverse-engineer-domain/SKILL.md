---
name: reverse-engineer-domain
description: Use when domain knowledge is implicit in existing documents, code, supplied excerpts or authorized external records, or those sources conflict with stated business rules.
---

# Extract domain candidates from existing sources

What you extract is grounded candidate knowledge, not business approval. A status read from an implementation or a record proves only that the corresponding statement exists there; it cannot support a claim that anything actually ran, that a rule is correct, or that an expert has confirmed it.

## Inputs

- The extraction question, the domain/context scope, and the actual documents, code, explicit excerpts, or authorized external records you are allowed to read; the desired candidates and the locations you are allowed to write.
- Source kind, identity, version/date or object baseline, plus the existing model, rules, artifacts/BLs, and the actual fact owners; list unknowns explicitly.
- Check read, write, and execution authorization separately. Reading an implementation does not authorize running it; an external reference does not authorize connecting to services, sending materials, updating sources, or retrieving additional records.

<a id="extract"></a>
## Extraction and comparison

1. First check this session's readable sources, scope, and versions, and list what was actually read and what was unreadable; do not expand access by following links. For files, use actual paths, lines/sections, and versions; for external records, keep whichever of system/project, object type, actual ID, revision, and excerpt location were provided.
2. For supplied excerpts, use the actual section or excerpt identifiers in this session's input file/message. If the original file, original line numbers, or external ID were not provided, record them as unknown; do not require a fictitious original file before taking notes, and do not pass off the excerpt's current location as its original location.
3. Break business language, relationships, rules, responsibilities/exchanges, and possible use cases into traceable candidates, keeping evidence and derivation as described in the table below. Do not simply relabel class names, endpoints, or field lists as a domain model; actors, measures, state transitions, or error/concurrency policies without a source stay unknown.
4. Compare against the existing model and across sources, keeping both sides of any conflict and their applicable versions. When an implementation constant disagrees with an expert statement, ask the actual rule owner to confirm the applicable scope and the trade-off; neither one is approved merely because it exists. Do not pick one value to hide the conflict, do not modify source code, and do not run the implementation in place of a business decision.

<a id="candidates"></a>
## Candidate records

For each item, keep the following information in the source/open-items section of an authorized note or draft; do not build a second store of confirmations or results:

| Information | What to record |
|---|---|
| Candidate content and kind | Actually observed terms, relationships, rule statements, responsibilities, or explainable model candidates |
| Source kind, identity, and location | Document/implementation/expert excerpt/external work item; the actual file/line/version, object ID, or section of a supplied excerpt; mark anything missing explicitly as unknown |
| Original basis | Necessary short quotations or observations with their context; keep qualifiers, and do not collect complete sensitive material |
| Knowledge category and rationale | `observed`: stated directly by the source; `inferred`: derived from the listed basis; `uncertain`: insufficient or conflicting basis, or the meaning is still undetermined. The category is not a calibrated probability or an approval status |
| Conflicts and confirmation needs | Contrary sources and their versions, what is still missing, and who actually needs to confirm; when there is no named accountable owner, ask for one; do not role-play the expert |
| Impact and destination | Full identity/source location of known artifacts, blocked decisions, content that can continue independently, and existing BLs; do not invent references when no target ID was provided |

You may record two directly observed conflicting statements separately and list the proposed business conclusion as `uncertain`; you must not merge "what the code says" and "what the business should do" into a single confirmed fact. Business rules come before derived INVs, and extraction does not automatically decide technical or tactical choices.

## When authorized to draft

First read the [domain guide and the actual forms](../../../domain-model/README.md#optional-forms), and choose SD/CTX/CAP/UC/INV, PI, QAS, or [BL](../../../_templates/items/backlog-item.md) as needed. Following the [metadata contract](../../../domain-model/README.md#artifact-metadata), keep the draft state and single ownership of each relationship. When the scope/ID is not explicit, first return or save an authorized plain note; do not invent a project identity just to pass the parser, and do not bulk-migrate old materials.

Rules remain owned by their original domain file; candidates state their source interpretation clearly without copying a second set of rules. Write only to authorized targets; do not overwrite sources or change candidates to confirmed. Unknown policies, metrics, actors, tactical/technical choices, and concurrency choices become specific questions; a missing source blocks the confirmations that depend on it, but not independent drafts that do have sources. Business clarification and decisions go back to the [define-requirements interview](../define-requirements/SKILL.md#interview).

## Outputs and completion

By default, return candidates, differences, and questions; saving files requires explicit authorization and an output location. Formal drafts follow the [domain locations](../../../domain-model/README.md#strategic-forms) into `domain-model/` or the existing owning directory; QAS/REQ go to `stakeholder-requirements/`, and scenarios/VTs to `verification/`. Do not leave formal content in `_templates`, and do not treat an extraction report as a confirmation or a run record.

At the end, list the files/excerpts actually read and their versions, the candidate scope, conflicts, unread parts, who must supply what, and the actual write locations. Check the sources and impact of this session's candidates with [verify-change](../verify-change/SKILL.md#domain-review), and report completion only when this limited extraction has traceable evidence; this does not mean the domain model or business acceptance is complete.

This method remains responsible for reading and judgment; it provides no automatic code/schema adapters or external-record connectors.
When read access to local sources is authorized, you may optionally use [source candidates and transparent scoring](../../../docs/source-extraction.md) to read
Markdown/plain text, explicit JSONL transcripts, and bounded stdlib DOCX; as that contract requires, keep the actual byte identity,
locations, duplicate/contrary sources, and uncertainty. Scores are not probabilities, confirmations, or precedence rules; candidates still go back to the source or to clarification as described above.
The audio entry point currently returns only authorization, missing-input, or adapter-unavailable errors; this does not mean anything was transcribed. For unsupported layouts/formats,
keep an explicit limitation and request authorized readable excerpts; do not install dependencies, convert over the network, or falsely claim the material was parsed.

## Stop conditions

When necessary sources are unreadable, version/identity information is insufficient, confirmations conflict, target files have unresolved changes, or authorization is insufficient, stop the affected extraction, writing, or confirmation, and keep locatable candidates and exact gaps. Confirmation must be made by the actual accountable owner against an explicit baseline; do not substitute delivery deadlines, automatic scores, or source status for a decision, and do not start follow-on implementation.
