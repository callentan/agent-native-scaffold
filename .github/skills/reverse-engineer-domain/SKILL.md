---
name: reverse-engineer-domain
description: Use when domain knowledge is implicit in existing documents, code, supplied excerpts or authorized external records, or those sources conflict with stated business rules. Not for clarifying or deciding business rules (use define-requirements) or for reviewing domain artifacts (use verify-change).
---

# Extract domain candidates from existing sources

Extract grounded candidate knowledge from sources you are authorized to read. Extraction is never business approval. Every extracted item stays a candidate (`observed`, `inferred`, or `uncertain`) until the actual accountable owner confirms it against an explicit baseline. A status read from an implementation or a record proves only that the statement exists there. It does not prove that anything actually ran, that a rule is correct, or that an expert has confirmed it.

## Inputs

- Required:
  - The extraction question and the domain/context scope.
  - The actual documents, code, explicit excerpts, or authorized external records you are allowed to read.
  - The desired candidates.
  - For each source: its kind, identity, and version/date or object baseline.
  - The existing model, rules, artifacts/BLs, and the actual fact owners.
  - Read, write, and execution authorization, each checked separately.
- When applicable:
  - The locations you are allowed to write. Saving any file requires them.

List unknowns explicitly.

<a id="extract"></a>
## Extract and compare

Purpose: turn the authorized sources into traceable candidates and keep conflicts visible.

1. Check which sources this session can read, with their scope and versions. List what was actually read and what was unreadable.
   - Do not expand access by following links.
   - When read access to local sources is authorized, you may use the tools in Optional local extraction tools below.
2. Record the location of each source:
   - Files: the actual paths, lines/sections, and versions.
   - External records: whichever of system/project, object type, actual ID, revision, and excerpt location were provided.
   - Supplied excerpts: the actual section or excerpt identifiers in this session's input file or message.
3. When the original file, original line numbers, or external ID of a supplied excerpt were not provided, record them as unknown.
   - Do not require a fictitious original file before taking notes.
   - Do not pass off the excerpt's current location as its original location.
4. Break business language, relationships, rules, responsibilities/exchanges, and possible use cases into traceable candidates. Keep their evidence and derivation as described in Record candidates below.
   - Do not simply relabel class names, endpoints, or field lists as a domain model.
   - Actors, measures, state transitions, or error/concurrency policies without a source stay unknown.
5. Compare the candidates against the existing model and across sources. Keep both sides of any conflict, with their applicable versions.
   - When an implementation constant disagrees with an expert statement, ask the actual rule owner to confirm the applicable scope and the trade-off. Neither one is approved merely because it exists.
   - Do not pick one value to hide the conflict.
   - Do not modify source code.
   - Do not run the implementation in place of a business decision.

Record: the sources read and unreadable, their locations, the candidates, and the conflicts, as candidate records.

<a id="candidates"></a>
## Record candidates

Purpose: keep every candidate traceable to its source and visibly unconfirmed.

1. For each item, fill in the information in the candidate table below. Do not build a second store of confirmations or results.
2. You may record two directly observed conflicting statements separately and list the proposed business conclusion as `uncertain`.
3. Never merge "what the code says" and "what the business should do" into a single confirmed fact.
4. Business rules come before derived INVs. Extraction does not automatically decide technical or tactical choices.

| Information | What to record |
|---|---|
| Candidate content and kind | Terms, relationships, rule statements, responsibilities, or explainable model candidates actually observed |
| Source kind, identity, and location | The kind (document, implementation, expert excerpt, or external work item), and the actual file/line/version, object ID, or section of a supplied excerpt. Mark anything missing explicitly as unknown |
| Original basis | Necessary short quotations or observations, with their context. Keep qualifiers. Do not collect complete sensitive material |
| Knowledge category and rationale | `observed`: stated directly by the source. `inferred`: derived from the listed basis. `uncertain`: the basis is insufficient or conflicting, or the meaning is still undetermined. The category is not a calibrated probability or an approval status |
| Conflicts and confirmation needs | Contrary sources and their versions, what is still missing, and who actually needs to confirm. When no accountable owner is named, ask for one. Do not role-play the expert |
| Impact and destination | The full identity and source location of known artifacts, blocked decisions, content that can continue independently, and existing BLs. When no target ID was provided, do not invent references |

Record: the candidate entries in the source/open-items section of an authorized note or draft.

## Optional local extraction tools

This method remains responsible for reading and judgment. It provides no automatic code/schema adapters or external-record connectors.

- When read access to local sources is authorized, you may use [source candidates and transparent scoring](../../../docs/source-extraction.md) to read Markdown/plain text, explicit JSONL transcripts, and bounded stdlib DOCX.
- As that contract requires, keep the actual byte identity, locations, duplicate/contrary sources, and uncertainty.
- Scores are not probabilities, confirmations, or precedence rules. Verify tool candidates against the source or clarify them, as in Extract and compare.
- The audio entry point currently returns only authorization, missing-input, or adapter-unavailable errors. Such a response does not mean anything was transcribed.
- For unsupported layouts or formats, keep an explicit limitation and request authorized readable excerpts.
  - Do not install dependencies.
  - Do not convert over the network.
  - Do not falsely claim the material was parsed.

## Draft artifacts when authorized

Purpose: turn candidates into draft domain artifacts, only when drafting is authorized.

1. First read the [domain guide and the actual forms](../../../domain-model/README.md#optional-forms).
2. Choose SD/CTX/CAP/UC/INV, PI, QAS, or [BL](../../../_templates/items/backlog-item.md) as needed.
3. Following the [metadata contract](../../../domain-model/README.md#artifact-metadata), keep the draft state and single ownership of each relationship.
4. When the scope/ID is not explicit, first return or save an authorized plain note.
   - Do not invent a project identity just to pass the parser.
   - Do not bulk-migrate old materials.
5. Leave rules owned by their original domain file. In candidates, state the source interpretation clearly without copying a second set of rules.
6. Write only to authorized targets. Do not overwrite sources.
7. Turn unknown policies, metrics, actors, tactical/technical choices, and concurrency choices into specific questions.
8. Send business clarification and decisions back to the [define-requirements interview](../define-requirements/SKILL.md#interview).

A missing source blocks only the confirmations that depend on it. Independent drafts that do have sources are not blocked.

Record: drafts in the formal locations listed under Outputs.

## Guardrails

- **Never change a candidate to confirmed. Confirmation must be made by the actual accountable owner against an explicit baseline.**
- Do not substitute delivery deadlines, automatic scores, or source status for a decision.
- Do not treat an extraction report as a confirmation or a run record.
- Reading an implementation does not authorize running it.
- An external reference does not authorize connecting to services, sending materials, updating sources, or retrieving additional records.

## Outputs

- By default, return candidates, differences, and questions.
- Save files only with explicit authorization and an output location. Then use these locations:
  - Formal drafts: `domain-model/` or the existing owning directory, following the [domain locations](../../../domain-model/README.md#strategic-forms).
  - QAS/REQ: `stakeholder-requirements/`.
  - Scenarios/VTs: `verification/`.
- Do not leave formal content in `_templates`.
- At the end, list the files/excerpts actually read and their versions, the candidate scope, conflicts, unread parts, who must supply what, and the actual write locations.

## Done when

- The sources and impact of this session's candidates are checked with [verify-change](../verify-change/SKILL.md#domain-review).
- This limited extraction has traceable evidence. Report completion only then.

Completion does not mean the domain model or business acceptance is complete.

## Stop conditions

- Stop the affected extraction, writing, or confirmation when any of these holds:
  - Necessary sources are unreadable.
  - Version/identity information is insufficient.
  - Confirmations conflict.
  - Target files have unresolved changes.
  - Authorization is insufficient.
- Then keep locatable candidates and exact gaps.
- Do not start follow-on implementation.
