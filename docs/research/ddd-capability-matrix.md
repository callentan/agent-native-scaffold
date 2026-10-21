# Six-repository pinned-version capability matrix

**2026-10-15: the source inventory is complete; functional alignment is not yet complete.** This round fetched the six agreed full commits read-only with existing Git credentials, without relying on sign-in pages or earlier research summaries. Raw objects and content are kept only in the maker session's files area; no upstream script was run, no hook was installed, no submodule was updated, and no reference repository was modified.

The implementation starting point of this repository is `1a6f594` (the clean working tree after committing the earlier README layout changes); the six-repository baselines are in the table below. In this round the user confirmed that the newly discovered existing features are also included in the enhancement; dependencies on and execution of audio, PDF, and external platforms still each require their own authorization. The implementation language remains Python-first, a single repository is the default, and a domain submodule is not mandatory.

## 1. How to read this matrix

- `observed-current` only means that the pinned source contains the file/feature carrier; its form is classified separately as a real script, a declarative pipeline, an Agent method, or a template/rule. It does not mean the feature has been run or implemented in our project.
- `proposed-upstream` refers only to the upstream roadmap and must not be mixed into the denominator for functional equivalence. Automation newly added by this plan is an independent design and is not described as an existing upstream implementation.
- `instance-only` marks instance placeholders or one-off content; record its purpose, but do not treat the sample business content as a current fact. External systems or approval results without a source are `unverified`.
- Directories/gitlinks are a metadata inventory and do not count as full file reads. Of the 195 blobs, 185 were read in full; the 10 `_roadmap` files were read within the listed ranges and excluded from current implemented capabilities. For the 57 directories/gitlinks, only metadata was read.
- The three source groups total 44 current capability groups with overlapping responsibilities; **they are not 44 non-overlapping product features or completed tasks**. There are also 6 upstream proposal groups and 1 unresolved dependency group.

The six Git trees contain 252 entries in total: 195 blobs, 53 trees, and 4 gitlinks. Git `ls-tree` does not include the repository roots; the 258 entries from the old API include the six roots, so the two totals do not indicate a version difference. Each manifest entry has exactly one row in the file inventory; the audit also checked commit/object IDs, file hashes, capability IDs, and cited line ranges.

## 2. Earlier understanding that needs correcting

`ddd-bc` **does have** `tools/setup-domain-model-submodule.ps1`, which handles domain submodule onboarding; it changes Git settings and the index and creates a commit. Previously only part of the historical summary could be confirmed, and its absence cannot be inferred from "PowerShell not confirmed". The new version will provide an equivalent optional Python onboarding capability that separates preflight checks, explicit installation, and commit authorization, without copying the script's implicit side effects.

`ddd-subdomain` has not only heading/placeholder validation, commit-msg, and fan-out, but also document/transcript adapters, audio transcription, confidence scoring, relationship graphs, interaction accounting, and a one-off management presentation tool. See each capability's carriers for which ones are partial implementations or depend on external services; the presence of source code does not mean it runs successfully.

Ongoing features that the plan genuinely missed also include QAS, tactical domain artifacts, Published Interface/vocabulary evolution, SEQ and sequenceSummary, Markdown+Gherkin scenarios, and SWAS/PDF. The user has confirmed that the expanded plan takes these on; adding a JSON Schema or a checker cannot substitute for these distinct user activities.

## 3. Handling of source and implementation boundaries

| Source difference | Handling in this enhancement and acceptance criterion |
|---|---|
| PowerShell submodule installer commits implicitly | Python preflight/optional onboarding; single repository by default; local changes, network access, and commits are authorized separately; conflicts keep the original text |
| Domain source is read-only, but prompts write back/push `model.yaml` | Original business facts stay read-only; local derived views and implementation summaries are maintained separately; cross-repository contributions go through authorized proposals/PRs; contradictions in the source are not treated as behavior that must be replicated |
| States such as Draft/Approved/Implemented/Passing are mixed | Content declaration, task progress, actual result, and applicability are independent; sourced legacy values are mapped explicitly; approval is never fabricated |
| The Markdown and the `.feature` file of a VT/scenario both claim to be canonical | `.feature` owns the executable Gherkin body; Markdown records metadata/criteria and references; when no application exists, the plan remains not-run |
| The validator's main/master/staged fallback and the graph's demo fallback | Explicit object baseline; no fallback on input failure; empty graphs/inventories are shown as they are, without injecting demo success |
| fan-out automatically clones/commits/pushes/opens PRs | Explicit target list, pinned inputs, diff proposals, and per-target results; actual remote operations are verified after the authorization gate |
| Audio/document/PDF depend on external SDKs, models, containers, or engines | Optional adapters that send no material by default; dependencies, data-processing scope, and credentials are confirmed separately; without the dependency, report unavailable/not-run explicitly |
| `_gen_ppt.py` hardcodes management content and personal paths | Do not copy the original presentation content; keep the optional feature of "generating a presentation file from specified material" with explicit inputs and outputs; actual rendering dependencies are verified separately |
| Tool qualification/review text alongside unconstrained execution permissions | Keep records of qualification, risk, and actual human decisions; a trailer, a role, or a passing format check is not treated as identity/permission authentication |

## 4. Cross-group and external dependencies

The BC prompts/templates gitlinks point to the two repository versions fetched in this round and can be resolved. The domain framework pins `.github/prompts` at `d7da752b7312dd9212c3fea15eba7fbf1c1edfba` and `_templates` at `9cc3338ba0d7fde01ac43c2562f0c7f8a57e8ab6`, which differ from the two independent reference versions specified this time; this matrix registers them separately and does not claim that the combination it consumes has been verified.

Real domain instances, the central ADR wiki, Risk Management, ADO query objects, organizational permissions, real pipelines, tool qualification decisions, and external execution results are not part of these six pinned trees and remain unverified. Completing the six-repository capability inventory does not depend on reading these instances, but every execution, compatibility, or approval conclusion that depends on them must remain unverified.

The local manifest, the independent per-group reports, and `source-audit.json` are in `files/ddd-alignment-execution` of maker session `1ff56941-bf56-4aa4-b769-fd4720915e1f`. They are not CI evidence accessible across machines; when they cannot be accessed, fetch the sources again read-only using the full commits and paths in this file. The content below keeps only independent summaries and locations; it does not copy source or template bodies and is not distributed downstream.

<!-- generated-source-tables -->

## 5. Pinned versions and actual inventory counts

| Repository | Full commit | entries / blobs |
|---|---|---|
| [ddd-bc](https://dev.azure.com/shcgravity/Center/_git/ddd-bc?version=GCbac263bea39988214b82cafb48f27e3a2136c534) | `bac263bea39988214b82cafb48f27e3a2136c534` | 32 / 22 |
| [ddd-bc-prompts](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-prompts?version=GC08f8219397d6fe6d000312f5956a493b1b28cc84) | `08f8219397d6fe6d000312f5956a493b1b28cc84` | 15 / 13 |
| [ddd-bc-templates](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-templates?version=GC00705aef6c70f855ef95588b0137cf7f2387efb0) | `00705aef6c70f855ef95588b0137cf7f2387efb0` | 15 / 11 |
| [ddd-subdomain-prompts](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain-prompts?version=GC1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c) | `1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c` | 19 / 17 |
| [ddd-subdomain-templates](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain-templates?version=GC59f98e352a150f99290a3855092298dbe11e0615) | `59f98e352a150f99290a3855092298dbe11e0615` | 65 / 47 |
| [ddd-subdomain](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain?version=GCe115ad4d03ac53359c608ce7d32262a508561496) | `e115ad4d03ac53359c608ce7d32262a508561496` | 106 / 85 |

<a id="current-source-capabilities"></a>
## 6. Current source capabilities and target tasks

Task numbers correspond to the enhancement plan; the new tasks 15–18 were added after this round confirmed what had been missed. The tables below preserve the 2026-10-15 pinned-source inventory and the pre-implementation gap/acceptance baseline; later local implementation and scoped re-reviews do not rewrite the original source facts, nor do they automatically satisfy the full equivalence acceptance of each row. For the scoped local status of Task1–12 and 15–18, see the [enhancement plan](../plan/2026-10-14-ddd-functional-alignment.md) and its per-item evidence. Task13 has an isolated copy of the user-selected Flagsmith/OpenFeature technical POC; the unit/build/controlled-browser sub-scopes pass, but the live Flagsmith, real business application, code generation/maintenance, human, client, and platform gates are still incomplete. Task14's row-by-row re-review of implementation locations/baselines/results and the accountable owner's decisions accepting differences are not yet complete. Therefore, this matrix cannot use the completed local tasks to claim that the six repositories' features are fully aligned.

### BC-01: BC identity and domain input mounting

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc:bc-config.yaml:1-20`; `ddd-bc:.gitmodules:1-6`; `ddd-bc:tools/setup-domain-model-submodule.ps1:31-114`; `ddd-bc:.github/copilot-instructions.md:17-31` |
| Original carrier | real executable + template/config |
| Inputs | BC/subdomain/domain repository URL/relative path in bc-config.yaml, plus the Git root directory and DomainModelUrl. |
| Outputs | Instance identity fields, the domain-model mount, the .gitmodules recursion policy, and local submodule configuration. |
| Preconditions | Must run from the real Git root directory; the configuration and domain repository URL are supplied by maintainers; the current snapshot still contains placeholder configuration. |
| Failure and write boundaries | The script throws when the root directory or a Git operation fails; it can remove the placeholder directory, rewrite the index/.gitmodules, write local Git configuration, add the submodule, and commit. It does not fetch domain content automatically. |
| Current skeleton gap | There is no BC configuration or domain-source onboarding script yet; onboarding already has the conventions of not overwriting and stopping on missing input. |
| Target tasks / enhancement acceptance | 15 / ENH-01, ENH-02, ENH-06, ENH-10, ENH-15 |
| Target acceptance | In a blank instance whose path contains spaces, a wrong root directory, an invalid URL, a placeholder directory, and an existing submodule each yield a non-zero result; the success path changes the listed Git objects only after explicit authorization and can read the pinned domain baseline. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-02: Bottom-of-V artifact model and single-source-of-truth boundary

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc:.github/copilot-instructions.md:7-15,33-50,63-86`; `ddd-bc:CONCEPTS.md:8-31,34-157`; `ddd-bc-templates:items/sr.md:1-50`; `ddd-bc-templates:items/user-story.md:1-46`; `ddd-bc-templates:items/verification-test.md:1-35` |
| Original carrier | template/config + documented Agent operation |
| Inputs | Domain REQ/UC/INV/verification sources and the bottom-of-V SR, US, ABB, and VT relationships. |
| Outputs | Markdown front matter, body AC/scope/verification methods, directory indexes, and traceability-matrix rows. |
| Preconditions | The domain model exists first; SR precedes US, and the corresponding ABB/VT/code steps are allowed only after the US is approved; instances must be filled in from templates. |
| Failure and write boundaries | The rules require stopping when a source is missing, the order is wrong, or approval is missing; creating artifacts writes this repository's Markdown and matrix, and model summaries additionally touch domain-model/model.yaml. |
| Current skeleton gap | Basic REQ/SR/US/ABB/VT responsibilities exist; the full set of domain kinds, Gherkin/risk, and bridge fields are not delivered. |
| Target tasks / enhancement acceptance | 1, 2, 3, 5, 12 / ENH-01, ENH-02, ENH-03, ENH-05, ENH-13 |
| Target acceptance | Duplicate numbers within the same scope, the same number across different scopes, missing required metadata, and an empty skeleton each produce a locatable result; body text and the original AC/anchor bytes are not overwritten by the migrator. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-03: Software requirement derivation

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:sr-derivation.prompt.md:14-62,91-104`; `ddd-bc-templates:items/sr.md:1-50`; `ddd-bc:.github/instructions/implementation.instructions.md:1-55` |
| Original carrier | documented Agent operation |
| Inputs | bc-config, domain use-cases/invariants, referenced REQs, existing SRs, and a manual scope selection. |
| Outputs | Testable SR Markdown, REQ/UC/INV/RC relationships, traceability rows, and the srSummary in model.yaml. |
| Preconditions | The domain path is readable and REQ/UC are approved; a Draft INV cannot produce a mandatory SR; the scope must be specified manually. |
| Failure and write boundaries | Stops and reports on path, status, or ambiguity problems or missing domain input; writes this repository's SR/matrix, and the existing prompt then also writes domain-model/model.yaml and commits/pushes. |
| Current skeleton gap | specify-feature already supports general software acceptance; full UC/INV/QAS/RC derivation and structured sources are not delivered. |
| Target tasks / enhancement acceptance | 1, 4, 5 / ENH-01, ENH-04, ENH-05 |
| Target acceptance | A missing UC, an unapproved REQ, a Draft INV, a duplicate SR, and an ambiguous alternate path each stop and report; valid input produces only a Draft SR with complete source locations. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-04: User story slicing and invariant ACs

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:story-derivation.prompt.md:8-68,89-108`; `ddd-bc-templates:items/user-story.md:1-46`; `ddd-bc:user-stories/README.md:1-42` |
| Original carrier | documented Agent operation + template |
| Inputs | Existing, approved SRs; their UC actors/alternates/INVs; REQ business value; and existing USs. |
| Outputs | USs in Backlog status, positive/alternate/mandatory-invariant ACs, DoD, matrix links, and storySummary. |
| Preconditions | The SR must exist and be Approved; UC, INV, and REQ are readable; scope is sliced by user value rather than by technical layer. |
| Failure and write boundaries | Stops when there is no SR, the SR is Draft, edits conflict, or the safety chain changes; normally writes this repository's US/matrix, and summary updates may still write to the domain submodule. |
| Current skeleton gap | An optional US form exists; fuller role/value/path derivation, status mapping, and coverage relationships still need to be added. |
| Target tasks / enhancement acceptance | 1, 3, 4, 5 / ENH-01, ENH-03, ENH-04, ENH-05 |
| Target acceptance | An unapproved SR produces no US; each generated US's ACs trace back to a UC/INV, and changing the parent SR lists the downstream rollbacks instead of silently overwriting them. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-05: ABB architecture, ADR, and QAS constraints

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:abb-design.prompt.md:8-115`; `ddd-bc:architecture/README.md:1-42`; `ddd-bc-templates:items/abb.md:1-55`; `ddd-bc:architecture/adr-references.md:1-24` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Approved USs, the domain capability/context-map/QAS/model, existing ABBs, and the ADR register. |
| Outputs | Logical ABB documents, interface/dependency-version/deployment/observability fields, matrix/ADR references, and abbSummary. |
| Preconditions | At least one Approved US exists, and the relevant domain files and ADR constraints are readable; a Draft QAS can only be marked provisional. |
| Failure and write boundaries | Stops when domain files are missing or the US is not approved; no cross-boundary technology is chosen without an ADR; writes this repository's ABB/matrix/ADR log and, per the prompt, changes model.yaml. |
| Current skeleton gap | ABB/ADR forms exist; QAS, runtime/deployment, integration sources, and full architecture views still need to be added. |
| Target tasks / enhancement acceptance | 1, 5, 9 / ENH-01, ENH-05, ENH-06, ENH-09 |
| Target acceptance | No Approved US, a Draft QAS, a missing ADR, and an unpinned dependency version are each blocked or flagged; a valid ABB relationship can be traced back to at least one US and the source version. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-06: Verification specification and Gherkin pair

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:verification-test.prompt.md:8-79,86-128`; `ddd-bc-templates:items/verification-test.md:1-35`; `ddd-bc-templates:items/verification-test.feature:1-56`; `ddd-bc:verification/README.md:1-48` |
| Original carrier | documented Agent operation + template |
| Inputs | Approved US/SR, INV, ABB, existing VTs, and domain TS scenarios; a human selects the scope. |
| Outputs | For each VT, a Markdown specification and a feature file of the same name, plus type, safety markers, AC mapping, test-file fields, and verificationSummary. |
| Preconditions | The US file exists and is Approved; domain invariants and related ABBs are readable; implementation tests are not generated by this prompt. |
| Failure and write boundaries | Stops when US/INV/ABB is missing, the status does not allow it, or an already-automated safety VT would be modified; writes this repository's verification documents/features, and summary updates still touch the domain submodule. |
| Current skeleton gap | Layered VTs with per-item targets/not-run exist; the Gherkin companion and full verification types/tags are not delivered. |
| Target tasks / enhancement acceptance | 1, 5, 6, 10, 13 / ENH-01, ENH-05, ENH-07, ENH-10, ENH-14 |
| Target acceptance | Each US AC has at least one VT, INV ACs have negative cases, and anything not run stays not-run; invalid mappings and safety-chain breaks have source-line locations in the report. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-07: Four-layer DDD code generation guardrails

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:code-generation.prompt.md:30-77,102-238`; `ddd-bc:.github/instructions/architecture.instructions.md:1-66`; `ddd-bc:.github/instructions/coding-standards.instructions.md:1-67` |
| Original carrier | documented Agent operation |
| Inputs | bc-config language/framework, approved USs, ABBs, domain aggregates/entities/value objects/events/invariants, and the existing src state. |
| Outputs | Per-scope domain/application/infrastructure/api scaffolds or incremental files, trace markers, and a conflict report. |
| Preconditions | The domain path is readable, the language/framework is not a placeholder, and approved USs and ABBs exist; existing non-empty files must not be silently overwritten. |
| Failure and write boundaries | Stops/skips and reports on missing input, Draft invariants, non-empty conflicts, or domain gaps; writes only src, generates no test code, and does not modify the read-only domain source. |
| Current skeleton gap | implement-task can guide maintenance of configured projects; there is no standalone initial code generation method or actual application acceptance yet. |
| Target tasks / enhancement acceptance | 1, 5, 13 / ENH-01, ENH-05, ENH-14 |
| Target acceptance | Nothing is written when the language/framework/approved US/ABB/domain objects are missing; non-empty targets and out-of-bounds paths are listed as conflict; generated output contains no unauthorized business behavior, and tests remain not-run. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-08: Traceability matrix, review, query, and backlog governance

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:traceability-build.prompt.md:14-64`; `ddd-bc-prompts:review.prompt.md:14-104`; `ddd-bc-prompts:backlog-review.prompt.md:14-96`; `ddd-bc-prompts:query.prompt.md:14-77`; `ddd-bc:traceability-matrix.md:1-52` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Domain REQ/UC/INV and this repository's SR/US/ABB/VT, plus the existing matrix/backlog; queries are given in natural language. |
| Outputs | Matrix rows, coverage statistics, broken links/gaps, review summaries, BL-NNN statuses, and read-only query results. |
| Preconditions | The domain submodule and all artifacts are readable; rebuilding the matrix must first preserve the manual sections; safety chains must be traceable back to their sources. |
| Failure and write boundaries | An incomplete matrix must not be generated when the domain is unreadable; build/backlog may write this repository's matrix/backlog, while review/query only report; there is currently no standalone validator. |
| Current skeleton gap | Acceptance inventory, gap checking, and review methods exist; full query/backlog/matrix activity entry points still need to be added. |
| Target tasks / enhancement acceptance | 1, 6, 7, 9, 14 / ENH-01, ENH-07, ENH-08, ENH-09, ENH-12 |
| Target acceptance | Given exact delivery IDs and a Git baseline, missing targets, dangling references, the same number under different owners, stale baselines, and an empty skeleton can all be located deterministically, and the matrix body is not silently rewritten. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-09: Domain change impact and status rollback

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:impact-assessment.prompt.md:18-124`; `ddd-bc-prompts:skills/bc-implementation/SKILL.md:19-28,114-124`; `ddd-bc:backlog.md:1-32` |
| Original carrier | documented Agent operation |
| Inputs | IDs of the changed REQ/UC/INV, the updated domain source, and this repository's SR/US/ABB/VT. |
| Outputs | Direct/indirect impact tables, RC chain checks, SR→US→VT status rollback recommendations, and BL-NNN. |
| Preconditions | The domain source must first be updated to a readable version; any rollback requires user confirmation, and safety-critical chains require a written re-review. |
| Failure and write boundaries | Stops when the source is not updated or the submodule is not initialized; by default it only produces a report, changes this repository's statuses/backlog only when instructed, and must not change domain files. |
| Current skeleton gap | Rule semantic impact and old-result applicability exist; full UC/INV/QAS/risk chains are not yet modeled. |
| Target tasks / enhancement acceptance | 1, 4, 7 / ENH-01, ENH-04, ENH-08 |
| Target acceptance | After REQ/UC/INV changes, the affected artifacts, rationale, and status rollbacks can be listed; unconfirmed or safety-critical items do not automatically change status or close backlog items. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-10: New member onboarding and domain submodule installation

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:onboarding.prompt.md:14-44,48-121`; `ddd-bc:tools/setup-domain-model-submodule.ps1:31-114`; `ddd-bc:domain-model/README.md:1-29` |
| Original carrier | real executable + documented Agent operation |
| Inputs | Interactively supplied BC name, subdomain, domain URL, context path, repository/team, language/framework, and role. |
| Outputs | A filled-in bc-config, the initialized domain mount, and a read-only role-based tour. |
| Preconditions | The user supplies each configuration item and confirms that the installation script succeeded; the domain source can be initialized. |
| Failure and write boundaries | Placeholder fields, an empty domain directory, or a script failure stop the tour; configuration and submodule installation have real write/commit side effects, while the tour itself is read-only. |
| Current skeleton gap | Onboarding that does not select a tech stack exists; optional external domain configuration/onboarding and source detection are not delivered. |
| Target tasks / enhancement acceptance | 4, 15 / ENH-01, ENH-06, ENH-10, ENH-14, ENH-15 |
| Target acceptance | Role selection and placeholder checks are repeatable; downstream explanations are not shown until installation is complete; after an authorized, successful installation the pinned domain baseline can be read, and without authorization the repository is not changed. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-11: Runtime sequence diagrams and asynchronous boundaries

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:sequence-diagram.prompt.md:3-12,14-58,60-177`; `ddd-bc-templates:items/sequence-diagram.md:1-67` |
| Original carrier | documented Agent operation + template |
| Inputs | Approved UC/US, ABB, INV, the domain-events catalog, integration and context-map, and existing SEQ numbers. |
| Outputs | Mermaid SEQ Markdown with success/error paths, matrix links, and the model.yaml sequenceSummary. |
| Preconditions | The UC is not Draft; at least one ABB/US exists; integration participants and asynchronous patterns can be traced to sources; modifying an existing Approved SEQ requires confirmation. |
| Failure and write boundaries | Marks a BL/stops when there is no ABB participant, no asynchronous integration support, or the UC is Draft; writes this repository's sequence files/matrix, and also writes the domain submodule summary and commits and pushes it. |
| Current skeleton gap | There is no SEQ form, sequence activity, or actual reference to sequenceSummary yet. |
| Target tasks / enhancement acceptance | 5, 8, 17 / ENH-01, ENH-05, ENH-06, ENH-14, ENH-17 |
| Target acceptance | Every participant and message of each approved UC has ABB/domain evidence, and cross-integration calls stay asynchronous; a missing participant/asynchronous mapping/error path is reported instead of producing a complete diagram. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-12: model.yaml derivation bridge and version summaries

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc-prompts:skills/bc-implementation/SKILL.md:19-28,114-124`; `ddd-bc-prompts:sr-derivation.prompt.md:64-88`; `ddd-bc-prompts:abb-design.prompt.md:70-99`; `ddd-bc-prompts:sequence-diagram.prompt.md:136-161` |
| Original carrier | documented Agent operation |
| Inputs | Derivation events for each artifact type, the domain model.yaml, version numbers, and relationships. |
| Outputs | Machine summaries such as srSummary/storySummary/abbSummary/verificationSummary/sequenceSummary/releaseStatus. |
| Preconditions | The domain submodule is locally writable and Git identity/permissions/remote are available; each prompt is responsible for updating it at the corresponding milestone. |
| Failure and write boundaries | The current rules both declare domain-model read-only and allow model.yaml to be modified; the prompt examples require a commit/push in the submodule followed by advancing the BC pointer, so side effects extend beyond this repository. |
| Current skeleton gap | Read-only/authorization conventions exist; structured implementation summaries, source pinning, and cross-repository contribution proposals are not delivered. |
| Target tasks / enhancement acceptance | 1, 2, 7, 8, 14 / ENH-01, ENH-02, ENH-06, ENH-08, ENH-12 |
| Target acceptance | Exports from the same source input are byte-stable and traceable to the source; the domain body is not written; without remote permissions, only local summaries/proposals are produced and nothing is reported as synchronized. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-13: Architecture, coding, security, and testing rule set

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc:.github/instructions/architecture.instructions.md:1-66`; `ddd-bc:.github/instructions/coding-standards.instructions.md:1-67`; `ddd-bc:.github/instructions/security.instructions.md:1-65`; `ddd-bc:.github/instructions/testing.instructions.md:1-72` |
| Original carrier | documented Agent operation |
| Inputs | Path matches for src, artifacts, and test files, with domain terminology/risk controls/dependency versions as context. |
| Outputs | Rules for Agents to follow when generating/reviewing: dependency direction, naming, input safety, test coverage, and logging boundaries. |
| Preconditions | The host supports path-scoped instructions and loads them correctly; the actual language, framework, and domain glossary are available. |
| Failure and write boundaries | The rules themselves have no executor, finding counts, or exit codes; violations depend solely on Agent/human detection, and the rules never modify source files automatically. |
| Current skeleton gap | Documentation/test rules exist; standalone coding/architecture/security rules and their applicable exceptions still need to be added. |
| Target tasks / enhancement acceptance | 1, 5, 6, 9, 10 / ENH-01, ENH-05, ENH-07, ENH-09, ENH-10 |
| Target acceptance | Matching and non-matching path samples are each observable; mechanical violations report code/path/line, and security or architecture decisions that cannot be judged mechanically remain review-required. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### BC-14: Template-driven creation and template lifecycle

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-bc:.github/copilot-instructions.md:52-61`; `ddd-bc:TEMPLATE-CHANGELOG.md:1-29`; `ddd-bc-templates:items:metadata-only`; `ddd-bc-templates:verification:metadata-only` |
| Original carrier | template/config + documented Agent operation |
| Inputs | Artifact type, the corresponding template, actual domain values, and the target number. |
| Outputs | SR/US/ABB/VT/SEQ/verification specification files with placeholders removed, with the matrix updated in the same operation. |
| Preconditions | The template submodule is pinned and its files are readable; the Agent must copy and fill as prompted and must not deliver placeholders as instance results. |
| Failure and write boundaries | There is no template updater, version comparison, or fan-out tool; the automatic creation rules write this repository's artifacts/matrix, and template changes can only rely on Git submodule versions and manual merges. |
| Current skeleton gap | Seven basic forms exist; the original source's full set of kinds, same-name feature files, and evolution criteria still need to be added. |
| Target tasks / enhancement acceptance | 1, 3, 11, 12 / ENH-01, ENH-02, ENH-03, ENH-11, ENH-13 |
| Target acceptance | A three-way comparison of the template candidate and local business changes can list preserved/changes/conflicts; conflicts are not written or merged automatically, and excluded directories are not referenced by the candidate. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-01: Domain modeling skill and entry-point routing

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:skills/domain-modeling/SKILL.md:1-91`; `ddd-subdomain-prompts:onboarding.prompt.md:10-16` |
| Original carrier | documented Agent operation |
| Inputs | Goal, role, subdomain/BC scope, and existing material. |
| Outputs | Applicable prompts, reading order, guardrails, and the next activity. |
| Preconditions | Read the rules and the target model first; when the role/scope is missing, ask one question at a time. |
| Failure and write boundaries | Unknowns go to BL; the skill grants no approval, permissions, or remote writes. |
| Current skeleton gap | Six shared methods and three modes exist; full input/output coverage of the original domain activities still needs to be added. |
| Target tasks / enhancement acceptance | 1, 4, 9, 13 / ENH-01, ENH-02, ENH-04, ENH-09, ENH-14 |
| Target acceptance | Given an activity/role/scope, it lists a single method, prerequisites, writable files, and stop conditions, without automatically producing approval facts. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-02: Domain interviews and strategic boundary modeling

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:elicitation.prompt.md:40-186`; `ddd-subdomain-templates:subdomain/subdomain-definition.md:9-107`; `ddd-subdomain-templates:context/use-cases.md:1-47` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Intended Use, expert input, candidate boundaries, terminology, actors, and business rules. |
| Outputs | Subdomains, BCs, vocabulary, UCs, BRs, INVs, and tactical candidates, Draft by default. |
| Preconditions | Intended Use/goals are at least Draft; strategic before tactical; BR precedes INV. |
| Failure and write boundaries | Ask one question at a time and record exclusion reasons; write only after user confirmation; unknowns go to BL. |
| Current skeleton gap | Minimal terminology/relationships/rules/responsibilities exist; full strategic interviews and optional tactical derivation still need to be added. |
| Target tasks / enhancement acceptance | 3, 4 / ENH-03, ENH-04, ENH-06 |
| Target acceptance | The same number in two contexts can be distinguished by scope; unconfirmed boundaries cannot be Approved or used for tactical derivation. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-03: Knowledge crunching, model review, and drift challenges

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:distillation.prompt.md:10-141`; `ddd-subdomain-prompts:review.prompt.md:10-136`; `ddd-subdomain-templates:context/aggregates/README.md:7-24` |
| Original carrier | documented Agent operation |
| Inputs | The existing model, expert/developer/regulatory roles, open stubs, and drift clues. |
| Outputs | Language, concept, boundary, aggregate, INV, event, and traceability issues, plus BL/ADR recommendations. |
| Preconditions | A domain expert is required; Intended Use is at least Draft; scan stubs first. |
| Failure and write boundaries | Only raises findings/recommendations; boundary changes go to BL/ADR first; model health is never certified automatically. |
| Current skeleton gap | General review/impact methods exist; standalone knowledge crunching, boundary challenge, and model drift activities still need to be added. |
| Target tasks / enhancement acceptance | 4, 9, 13 / ENH-04, ENH-09, ENH-14 |
| Target acceptance | Each issue has its file/line, severity, recommendation, impact chain, and human decision status. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-04: Brownfield ADO reverse extraction and confidence tiers

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:reverse-engineering.prompt.md:12-78`; `ddd-subdomain-prompts:reverse-engineering.prompt.md:140-292`; `ddd-subdomain-prompts:reverse-engineering.prompt.md:335-409` |
| Original carrier | documented Agent operation |
| Inputs | ADO MCP, organization/project/Area Path/subdomain/safety classification, and Epic/Feature/Story/Test Case. |
| Outputs | Draft REQ/CAP/UC/INV/vocabulary/matrix/BL and a High/Medium/Low confidence report. |
| Preconditions | ADO MCP is available and Epics exist; the subdomain/safety classification is confirmed; each BC is confirmed manually one by one. |
| Failure and write boundaries | Stops on a missing MCP/Epic, a boundary dispute, or a missing safety prerequisite; ADO status is not treated as Approved. |
| Current skeleton gap | There is no standalone reverse engineering method, source adapter, or confidence-rated candidate report yet. |
| Target tasks / enhancement acceptance | 1, 4, 7, 13 / ENH-01, ENH-04, ENH-08, ENH-14 |
| Target acceptance | Each object traces back to its ADO type/ID/location and confidence; Medium/Low does not promote status. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-05: Requirements and quality attribute scenario capture

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:requirements-capture.prompt.md:12-143`; `ddd-subdomain-prompts:requirements-capture.prompt.md:161-228`; `ddd-subdomain-templates:requirements/_template.md:1-121`; `ddd-subdomain-templates:requirements/_template-qas.md:1-108` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Business problems, Intended Use, the governance catalog, UC/vocabulary/traceability, and QAS triggers. |
| Outputs | Draft REQs, ATAM QAS, domain impact, and UC/matrix/change-log links. |
| Preconditions | Check governance/automatic derivation first; REQs are solution-free and expert-confirmed; QAS are quantifiable. |
| Failure and write boundaries | Governance gaps, scope expansion, constraint conflicts, or untestable items stay in BL/open. |
| Current skeleton gap | REQ business acceptance exists; standalone QAS, governance mapping, and a quantified scenario form are not delivered. |
| Target tasks / enhancement acceptance | 3, 4, 5 / ENH-03, ENH-05, ENH-07, ENH-14 |
| Target acceptance | Nothing is Approved without coverage/measurement/expert confirmation; the six ATAM elements and response figures are locatable. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-06: Architecture decision authoring and incoming ADR impact handling

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:adr.prompt.md:18-129`; `ddd-subdomain-prompts:adr.prompt.md:133-196`; `ddd-subdomain-templates:items/adr.md:1-71` |
| Original carrier | documented Agent operation + template/config |
| Inputs | The decision or incoming ADR, decision makers, problem, options, and impact on the current model. |
| Outputs | An ADR draft or incoming-ADR impact report, a notification table, BLs, and a post-publication reference plan. |
| Preconditions | The Mode is explicit and the impact has been read; produce/apply only after confirmation; the external wiki is published by a human. |
| Failure and write boundaries | When content is missing or the impact is unclear, leave only questions/BLs; never claim wiki publication or approval. |
| Current skeleton gap | A local ADR form exists; cross-context impact/notification proposals for incoming ADRs still need to be added. |
| Target tasks / enhancement acceptance | 4, 5, 9, 13 / ENH-04, ENH-05, ENH-09, ENH-12, ENH-14 |
| Target acceptance | Unconfirmed items can only be drafts/BLs; an incoming ADR can list affected contexts, consumers, and actions, with no automatic wiki writes. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-07: Requirement change impact analysis and authorization threshold

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:impact-assessment.prompt.md:10-81`; `ddd-subdomain-prompts:impact-assessment.prompt.md:81-138`; `ddd-subdomain-templates:requirements/_template.md:47-121` |
| Original carrier | documented Agent operation |
| Inputs | REQ, change type/confirmation status, model, matrix, and QAS/ADR/interface/risk relationships. |
| Outputs | An impacted-artifact table, severity classification, a conflict table, a recommended order, and questions. |
| Preconditions | REQ/QAS/matrix sources have been read; inventory evidence is assembled; after reporting, wait for approval. |
| Failure and write boundaries | Missing or uncertain links are not guessed; a recommended order is not a write that has been performed. |
| Current skeleton gap | Basic rule/acceptance impact exists; full requirement/QAS/interface/risk dependencies still need to be added. |
| Target tasks / enhancement acceptance | 4, 7, 13 / ENH-04, ENH-08, ENH-14 |
| Target acceptance | A single REQ change lists all affected objects, the reasons, and the actions awaiting approval. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-08: Intended Use changes and risk escalation

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:intended-use-amendment.prompt.md:10-167`; `ddd-subdomain-templates:subdomain/intended-use.md:1-154` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Current/proposed Intended Use, target sections, rationale, and the safety/utility sections. |
| Outputs | Amendment classification, regulatory significance, RA escalation, downstream impact, risk re-analysis, and BLs. |
| Preconditions | The current file is complete and the sections/baseline are explicit; high-significance expansions go to RA review first. |
| Failure and write boundaries | Uncertainty is escalated as high risk or kept as an open question; risk analysis is not performed here on anyone's behalf. |
| Current skeleton gap | There is no Intended Use form or change/escalation path yet; no regulatory judgment is made unilaterally. |
| Target tasks / enhancement acceptance | 3, 4, 9 / ENH-03, ENH-04, ENH-09, ENH-14 |
| Target acceptance | Changes in scope/patients/users/constraints/safety produce an escalation record; without confirmation, nothing remains Approved. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-09: Review, open questions, and backlog/consistency sync

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:review.prompt.md:10-136`; `ddd-subdomain-prompts:backlog-review.prompt.md:10-75`; `ddd-subdomain-templates:subdomain/strategic/bounded-contexts.md:33-37` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Model, requirements, tests, matrix, rules, and NEEDS CLARIFICATION/AUTO-DERIVED/BL markers. |
| Outputs | Severity-rated findings, BL recommendations, resolution statistics, context health summaries, and traceability gaps. |
| Preconditions | The complete model and guidance are required; resolved items must have written evidence. |
| Failure and write boundaries | No refactoring and no assumptions; anything that cannot be proven stays Open; compliance is not certified. |
| Current skeleton gap | Gap and handoff handling exist; standalone BL/review records, a closure basis, and a backlog activity still need to be added. |
| Target tasks / enhancement acceptance | 3, 4, 6, 7, 9, 13 / ENH-04, ENH-07, ENH-08, ENH-09, ENH-14 |
| Target acceptance | Every open item has its source file/line, BL, impact, and status; without evidence it stays Open. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-10: Glossary sync and context language governance

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:glossary-sync.prompt.md:10-121`; `ddd-subdomain-templates:subdomain/glossary/ubiquitous-language.md:1-46`; `ddd-subdomain-templates:subdomain/glossary/business-rules.md:1-66` |
| Original carrier | documented Agent operation + template/config |
| Inputs | External/local glossaries, term statuses, contexts, and unconfirmed markers. |
| Outputs | A per-term classification report, conflict options, and approved vocabulary/deprecation/BL updates. |
| Preconditions | Both vocabularies are read in full; unconfirmed terms do not take part in the sync; conflicts require a user choice. |
| Failure and write boundaries | External meanings are never adopted silently; renames scan for impact first; only approved changes are applied. |
| Current skeleton gap | A shared terminology column exists; the external/local glossary sync, deprecation, and conflict decision process are not delivered. |
| Target tasks / enhancement acceptance | 3, 4, 11 / ENH-03, ENH-04, ENH-11, ENH-12 |
| Target acceptance | Homonyms, external-only terms, internal-only terms, and unconfirmed terms are listed separately; the canonical term is not changed without approval. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-11: Published Interface contract lifecycle

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:published-interface.prompt.md:10-126`; `ddd-subdomain-templates:subdomain/published-interface.md:1-129`; `ddd-subdomain-templates:context/integration/README.md:17-80` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Operation type, current interface, model/vocabulary/consumers, pattern, version, and differences. |
| Outputs | Change classification, version, consumer impact, notification messages, and files to update. |
| Preconditions | Elements are modeled, vocabulary is canonical, capabilities are classified, and the model/context registration is valid. |
| Failure and write boundaries | Blocks, or treats the change as breaking, when elements are unmodeled/unclassified or the impact is unclear; no notification is actually sent. |
| Current skeleton gap | There are no Published Interface version, consumer, or notification proposal artifacts yet. |
| Target tasks / enhancement acceptance | 3, 4, 5, 11 / ENH-03, ENH-04, ENH-10, ENH-11, ENH-12, ENH-14 |
| Target acceptance | A semantic change automatically becomes breaking + major with notification drafts for all consumers; the source is not changed without approval. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-12: Query and read-only model inventory

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:query.prompt.md:10-70`; `ddd-subdomain-templates:context/model.yaml:36-147`; `ddd-subdomain-templates:context/domain-events/catalog.md:1-36` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Object type and scope. |
| Outputs | Lists, filtered results, or BC summaries based on the actual source files. |
| Preconditions | The scope is explicit; read the corresponding source files and do not guess objects that do not exist. |
| Failure and write boundaries | Read-only; no objects are fabricated; no persisted index or export side effects. |
| Current skeleton gap | Existing material can be read explicitly; there is no structured inventory or full domain query activity yet. |
| Target tasks / enhancement acceptance | 2, 3, 7, 8 / ENH-02, ENH-06, ENH-07, ENH-08 |
| Target acceptance | The same input yields a deterministic order/count; same numbers across scopes, duplicate IDs, broken links, and hand-edited views are detectable. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-13: Domain scenario, acceptance, and QAS verification authoring

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:test-scenario.prompt.md:10-223`; `ddd-subdomain-templates:scenarios/domain-scenario.md:1-45`; `ddd-subdomain-templates:scenarios/acceptance-test.feature:1-48` |
| Original carrier | documented Agent operation + template/config |
| Inputs | Approved UC/INV, REQ/QAS, vocabulary, and the existing matrix. |
| Outputs | Metadata and `.feature` Gherkin for BC/cross-BC/REQ acceptance/QAS scenarios. |
| Preconditions | Nothing is generated for Draft/NEEDS CLARIFICATION objects; scenarios need a UC/REQ and the domain language. |
| Failure and write boundaries | Actors/outcomes are not invented; non-behavioral QAS remain specifications only; this group does not run implementation tests. |
| Current skeleton gap | Basic business VTs exist; cross-context/QAS scenarios and the Gherkin companion are not delivered. |
| Target tasks / enhancement acceptance | 3, 5, 10, 13 / ENH-05, ENH-07, ENH-08, ENH-14 |
| Target acceptance | Each scenario has UC/REQ/INV/QAS locations and a type; when prerequisites are unmet, only a gap/BL is reported. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-14: Traceability matrix, coverage, and QMS risk reconciliation

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:traceability-build.prompt.md:10-230`; `ddd-subdomain-templates:qms-traceability-matrix.md:1-61`; `ddd-subdomain-templates:context/model.yaml:181-278` |
| Original carrier | documented Agent operation + template/config |
| Inputs | REQ/CAP/UC/INV/BR/TS, the matrix, and the SR/US/VT/riskSummary bridge. |
| Outputs | The regular matrix, gap/orphan, coverage, QMS risk trace, blockers, and statistics. |
| Preconditions | The inventory is authoritative; NEEDS CLARIFICATION does not count as coverage; show and approve before writing. |
| Failure and write boundaries | Links are not inferred; missing evidence stays Partial/None/blocked; it does not prove business approval. |
| Current skeleton gap | A full acceptance starting point/per-item targets exist; the full domain and optional risk matrices and machine reconciliation are not delivered. |
| Target tasks / enhancement acceptance | 2, 5, 6, 7, 8, 10, 13, 14 / ENH-02, ENH-05, ENH-06, ENH-07, ENH-08, ENH-10, ENH-12, ENH-14 |
| Target acceptance | Given delivery IDs, it can report missing criteria, dangling references/the same number under different owners, and RC-VT gaps, and it consistently distinguishes input errors from findings. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-15: SWAS document-set authoring and PDF build pipeline

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:swas.prompt.md:6-226`; `ddd-subdomain-templates:subdomain/architecture-spec/AS-[SubdomainName].md:1-315`; `ddd-subdomain-templates:subdomain/architecture-spec/pipelines/generate-pdf.yml:1-30` |
| Original carrier | documented Agent operation + real executable declarative pipeline |
| Inputs | The subdomain/BC/requirements/QAS/ABB/sequence/risk/verification bridge. |
| Outputs | SWAS Markdown/metadata views and the PDF build artifact. |
| Preconditions | Sources are readable; missing ABB/risk/sequence data keeps a warning; the PDF is built only when the external container is available. |
| Failure and write boundaries | No technical facts are fabricated; a pipeline build is not equivalent to approval. |
| Current skeleton gap | There are no SWAS artifacts/method or verifiable PDF export yet. |
| Target tasks / enhancement acceptance | 5, 8, 17 / ENH-01, ENH-05, ENH-07, ENH-09, ENH-10, ENH-12, ENH-13, ENH-14, ENH-17 |
| Target acceptance | Missing data yields a locatable TODO; a pinned-version build failure propagates the actual error and does not write back to the source. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-16: Domain artifact classification, identity, and status semantics

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-prompts:skills/domain-modeling/SKILL.md:10-49`; `ddd-subdomain-templates:context/README.md:15-60`; `ddd-subdomain-templates:context/capabilities.md:1-47`; `ddd-subdomain-templates:context/invariants.md:1-60` |
| Original carrier | template/config + documented Agent operation |
| Inputs | Facts, sources, relationships, and manually set statuses of subdomains/BCs/CAPs/UCs/INVs. |
| Outputs | Markdown artifacts, Draft/Approved/Deprecated, and release/open question semantics. |
| Preconditions | Created from templates; IDs are unique within a scope; confirmation/approval is done by humans; directories are kept in sync. |
| Failure and write boundaries | Empty placeholders, duplicates, and unconfirmed items only stay Draft/open; there is no unified parser/status validation. |
| Current skeleton gap | A minimal domain and seven basic forms exist; full types, scope/metadata, and the status contract are not delivered. |
| Target tasks / enhancement acceptance | 2, 3, 5, 6, 7 / ENH-02, ENH-03, ENH-06, ENH-07 |
| Target acceptance | Each formal artifact type can be located by kind/scope/id#anchor/status/source; old Markdown remains readable but is not reported as verified. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-17: Tactical model artifacts: aggregates, entities, value objects, factories, services, policies, and events

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-templates:items/aggregate.md:1-194`; `ddd-subdomain-templates:items/domain-event.md:1-128`; `ddd-subdomain-templates:items/policy.md:1-87`; `ddd-subdomain-templates:items/integration-partner.md:1-67` |
| Original carrier | template/config |
| Inputs | Confirmed boundaries/UC/BR/INV, domain behavior, states, and integration facts. |
| Outputs | Aggregates, entities/VOs, Factories, services, policies, event schemas/consumers/versions, and evolution records. |
| Preconditions | Boundaries/use cases are confirmed first; every INV has a BR; cross-boundary relationships use IDs/integration records. |
| Failure and write boundaries | These are design records only and execute no code; unclear rules stay in BL; event idempotency/compatibility is not verified. |
| Current skeleton gap | The original lightweight rules do not mandate tactical patterns; full optional forms for aggregates/entities/value objects/events and similar are not delivered. |
| Target tasks / enhancement acceptance | 3, 4, 5 / ENH-03, ENH-04, ENH-05, ENH-08, ENH-12 |
| Target acceptance | Tactical artifacts reference each other and are locatable; a missing BR/consumer/version/status fails or stays Draft. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-18: Context integration, ACL/OHS/shared kernel, and propagation boundaries

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-templates:subdomain/strategic/context-map.md:1-82`; `ddd-subdomain-templates:context/integration/README.md:1-89`; `ddd-subdomain-templates:subdomain/published-interface.md:29-129` |
| Original carrier | template/config + documented Agent operation |
| Inputs | Context ownership/direction/pattern, published events/services, ACLs, versions, and consumers. |
| Outputs | context-map, partner contracts, producer/consumer, Shared Kernel/Separate Ways, and notification requirements. |
| Preconditions | Direction/team relationships and published items are explicit; cross-team sharing requires a producer + published interface. |
| Failure and write boundaries | Unclear patterns go to BL; API details are kept out of the domain body; remote propagation requires separate authorization. |
| Current skeleton gap | Direction/fact ownership exists; the context map, integration patterns/partner contracts, and evolution conventions still need to be added. |
| Target tasks / enhancement acceptance | 3, 4, 5, 11 / ENH-03, ENH-04, ENH-05, ENH-06, ENH-10, ENH-11, ENH-12 |
| Target acceptance | Each relationship has a direction/pattern/version/translation/failure boundary/consumers; breaking changes produce only diff/notification proposals. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-19: Machine model and cross-repository implementation bridge

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-templates:context/model.yaml:1-101`; `ddd-subdomain-templates:context/model.yaml:103-180`; `ddd-subdomain-templates:context/model.yaml:181-291` |
| Original carrier | template/config |
| Inputs | The BC body, implementation-repository ABB/sequence/SR/US/VT, governance, risk, and release status. |
| Outputs | A model.yaml snapshot and a cross-repository bridge for SWAS/the matrix to read. |
| Preconditions | The BC team keeps it in sync; external sources exist first; cross-repository writes require authorization. |
| Failure and write boundaries | It is neither body facts nor execution results; it does not write back to the source automatically. |
| Current skeleton gap | There is no model view with a source baseline or structured implementation summary yet. |
| Target tasks / enhancement acceptance | 2, 5, 7, 8, 10, 12, 13 / ENH-02, ENH-05, ENH-06, ENH-07, ENH-08, ENH-10, ENH-12, ENH-13 |
| Target acceptance | When the source or implementation objects change, staleness/hand edits are detected; missing execution evidence stays not-run/input error. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### DOMAIN-20: Subdomain, clinical safety, business rule, and governance foundation material

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain-templates:subdomain/subdomain-definition.md:1-149`; `ddd-subdomain-templates:subdomain/intended-use.md:1-173`; `ddd-subdomain-templates:subdomain/glossary/business-rules.md:1-66` |
| Original carrier | template/config + documented Agent operation |
| Inputs | Clinical/regulatory scope, patients/users/environment, vision/classification, business rules, BCs, and boundary events. |
| Outputs | Subdomain definition, Intended Use, safety/environment summary, BR/vocabulary, BC/release, dependencies, and questions. |
| Preconditions | Accountable owners take part; Intended Use is at least Draft before REQ/UC; cross-subdomain facts go back to the product-level source. |
| Failure and write boundaries | It does not certify approval/regulatory compliance/risk; missing material blocks the affected modeling, and no default values are filled in. |
| Current skeleton gap | Product/domain sources exist; full optional Intended Use/governance/safety reference material is not delivered. |
| Target tasks / enhancement acceptance | 3, 4, 5, 8, 9, 13 / ENH-03, ENH-04, ENH-05, ENH-09, ENH-12, ENH-14 |
| Target acceptance | Without an Intended Use/goals/safety classification, work is explicitly blocked; Draft/Review/Approved and the accountable owner are locatable and never promoted automatically. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-01: Instruction-driven domain modeling and role workflows

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:.github/copilot-instructions.md:1-172`; `ddd-subdomain:.github/instructions/domain-model.instructions.md:1-198`; `ddd-subdomain:.github/role-profiles/README.md:1-116`; `ddd-subdomain:docs/roles/README.md:1-45` |
| Original carrier | documented Agent operation |
| Inputs | Human-supplied domain facts, role selection, existing Markdown, and prompt entry points. |
| Outputs | Step-by-step navigation/review of domain-model, requirements, and testing document artifacts. |
| Preconditions | The host must read the local instructions/role guides; the prompt bodies depend on an unverified gitlink; structural decisions require human confirmation. |
| Failure and write boundaries | The rules require unknown facts to go to BL and structural changes to get an impact analysis first and then wait for confirmation, but there are no tool permissions or write protection. |
| Current skeleton gap | Basic shared methods/entry points exist; the original domain activity scope and full model organization still need to be added. |
| Target tasks / enhancement acceptance | 1, 4, 5, 14 / ENH-01, ENH-03, ENH-04, ENH-05, ENH-08 |
| Target acceptance | An isolated fixture explicitly reads one method and can locate its inputs, confirmation gates, open items, and write paths. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-02: Top-of-V model artifacts, identity, and traceability contract

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:README.md:116-210`; `ddd-subdomain:domain-model/README.md:1-63`; `ddd-subdomain:testing/README.md:1-143`; `ddd-subdomain:traceability-matrix.md:1-66`; `ddd-subdomain:docs/reference/artifact-ids.md:1-116` |
| Original carrier | documented Agent operation |
| Inputs | REQ, CAP, UC, INV, BR, TS, risk references, and bottom-of-V summaries. |
| Outputs | Markdown artifacts with ID, Status, and source/relationship semantics, plus the traceability matrix. |
| Preconditions | Humans confirm business facts and ownership; the correct templates/prompts submodules are required. |
| Failure and write boundaries | The documents define Draft/open/gap conventions, but the matrix, backlog, and model.yaml have no in-repository parser and no independent write protection. |
| Current skeleton gap | Basic material and the acceptance chain exist; the full set of domain artifact, scope, and traceability kinds still needs to be added. |
| Target tasks / enhancement acceptance | 1, 2, 3, 5, 7, 8, 12, 14 / ENH-01, ENH-02, ENH-03, ENH-05, ENH-06, ENH-08, ENH-12, ENH-13 |
| Target acceptance | A fixture with the same number in two scopes can locate owner, anchor, layer, gaps, and object baseline in both directions. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-03: Human review, risk, and governance records

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:.github/ai-tool-config.yaml:1-120`; `ddd-subdomain:.github/PULL_REQUEST_TEMPLATE.md:1-64`; `ddd-subdomain:requirements/_governance-catalog.md:1-176`; `ddd-subdomain:domain-model/decisions/README.md:1-40`; `ddd-subdomain:docs/roles/README.md:36-45` |
| Original carrier | template/config |
| Inputs | Named reviewers, RC, GOV, ADR, PR changes, and waiver evidence. |
| Outputs | PR checklist, the reviewed-by convention, REQ/waiver, ADR/backlog, and risk documents. |
| Preconditions | Requires human/RA/Architect responsibilities and the external QMS/central ADRs; the configuration still contains placeholders. |
| Failure and write boundaries | The hook only matches the reviewed-by string; forms/waivers have no machine identity/approval verification; writes are made through PR/Git. |
| Current skeleton gap | Conventions for authorization and for never impersonating approval exist; dedicated tool qualification/review records are not delivered. |
| Target tasks / enhancement acceptance | 1, 9, 10, 12, 14 / ENH-01, ENH-09, ENH-10, ENH-12, ENH-14 |
| Target acceptance | Fixtures missing a reviewer, a waiver approver, or an RC source produce located findings; the text Approved does not change status automatically. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-04: Domain candidate extraction from transcripts and documents

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:.github/utilities/input_source_adapter.py:1-119`; `ddd-subdomain:.github/utilities/transcript_adapter.py:1-382`; `ddd-subdomain:.github/utilities/document_adapter.py:1-476`; `ddd-subdomain:.github/utilities/audio_transcriber.py:1-264`; `ddd-subdomain:.github/utilities/tests/test_p4_01_cardiac_imaging.py:1-254` |
| Original carrier | real executable |
| Inputs | Local txt/md, Markdown/DOCX, mp3/wav/m4a/flac; audio optionally uses external credentials. |
| Outputs | A list of ExtractedArtifact entries with source, type, excerpt, initial confidence, clarification questions, and approximate line numbers. |
| Preconditions | The file exists; DOCX/audio require optional dependencies; the modules use the utilities directory as their import context. |
| Failure and write boundaries | A missing file/format/dependency/credential raises an exception; audio calls an external service; the adapters do not write formal domain files. |
| Current skeleton gap | There are no document/transcript/audio extraction or candidate scoring tools yet. |
| Target tasks / enhancement acceptance | 4, 16 / ENH-03, ENH-04, ENH-08, ENH-12, ENH-14, ENH-16 |
| Target acceptance | Offline fixtures produce stable candidates and source locations; low/medium confidence goes only to draft/BL, and nothing is written to the source when input is missing. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-05: Markdown heading and placeholder validation

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:.github/utilities/validate_artifact.py:1-274`; `ddd-subdomain:.vscode/tasks.json:1-44`; `ddd-subdomain:azure-pipelines.yml:51-66` |
| Original carrier | real executable |
| Inputs | Explicit Markdown paths/directories, or by default the Git diff/staged file set. |
| Outputs | An error list on stdout; currently 0 = no files/no findings, 1 = heading or placeholder findings. |
| Preconditions | Python, a readable repository, and, in default mode, the ability to call git; the Azure job provides Python 3.11 first. |
| Failure and write boundaries | Reads files only; files matching no rule are skipped; the default baseline tries origin/main, origin/master, main, and master and then falls back to the index (staging area); an empty set still returns 0. |
| Current skeleton gap | There is only a one-off check of the maker artifacts; no formal validator is distributed yet. |
| Target tasks / enhancement acceptance | 1, 6, 7, 10, 12 / ENH-01, ENH-07, ENH-08, ENH-10, ENH-13 |
| Target acceptance | A nonexistent full base SHA returns input-error/2; normal, violating, and empty-skeleton cases each report checked/excluded/object baseline. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-06: Traceability matrix graph generation and interactive viewing

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:.github/utilities/graph_generator.py:1-436`; `ddd-subdomain:docs/artifact-graph.html:1-232`; `ddd-subdomain:traceability-matrix.md:1-66` |
| Original carrier | real executable |
| Inputs | The root traceability-matrix.md and the optional QMS matrix. |
| Outputs | --json writes JSON to stdout; by default it writes interactive Cytoscape HTML with upstream/downstream search and a gap-only view. |
| Preconditions | The matrix contains recognizable IDs; viewing the HTML requires the Cytoscape CDN or a local script. |
| Failure and write boundaries | With no nodes it switches to a built-in demo; by default it creates parent directories and writes HTML, while --json writes nothing. |
| Current skeleton gap | There is no source-driven interactive/static relationship graph export tool yet. |
| Target tasks / enhancement acceptance | 7, 17 / ENH-01, ENH-08, ENH-12, ENH-14, ENH-17 |
| Target acceptance | --json is stable for the same fixture, an empty matrix returns empty rather than a demo, and nodes/edges trace back to real artifacts/anchors. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-07: AI interaction logging and credits estimation

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:.github/utilities/log_interaction.py:1-332`; `ddd-subdomain:.github/ai-interaction-log.csv:1-12`; `ddd-subdomain:.github/ai-tool-config.yaml:65-120` |
| Original carrier | real executable |
| Inputs | Date, PR, version, model, tokens, prompt, artifact type, reviewer, and notes. |
| Outputs | Appends to a CSV, or outputs per-model/per-month summaries and per-call credits estimates. |
| Preconditions | The log is writable; a model price table/hardcoded IDs; optionally reads models.json from a personal absolute path. |
| Failure and write boundaries | Unknown models get credits=0; parse errors fall back to defaults; models.json exceptions are swallowed; the reviewer/model is not authenticated. |
| Current skeleton gap | Development log summaries exist; there is no dedicated interaction/usage ledger or reconciliation statistics. |
| Target tasks / enhancement acceptance | 9, 18 / ENH-01, ENH-09, ENH-12, ENH-14, ENH-18 |
| Target acceptance | Valid records can be appended with their fields preserved; unknown models/invalid input are reported explicitly instead of silently becoming zero; no credentials are written. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-08: Commit message reviewed-by hook and installation

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:.github/hooks/commit-msg:36-96`; `ddd-subdomain:.github/hooks/install_hooks.py:21-63`; `ddd-subdomain:.github/ai-tool-config.yaml:44-63` |
| Original carrier | real executable |
| Inputs | The Git commit message, staged file names, and the local .git/hooks state. |
| Outputs | The hook allows or rejects with 0/1; the installer writes the hook and a Windows cmd wrapper. |
| Preconditions | The installer is run manually; the target is a Git repository; Windows requires python on PATH, and Unix requires symlinks. |
| Failure and write boundaries | Only rejects managed paths that lack reviewed-by; merge/fixup/squash/--no-verify can bypass it; the installer overwrites/deletes the target with no backup. |
| Current skeleton gap | No optional hook/installer has been delivered yet; no mandatory review gate is deployed. |
| Target tasks / enhancement acceptance | 9, 10 / ENH-09, ENH-10, ENH-14 |
| Target acceptance | An isolated Git fixture distinguishes valid/invalid reviewed-by, unmanaged paths, paths with spaces, and missing dependencies; an existing hook can be restored. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

### FRAMEWORK-09: Azure DevOps domain material fan-out pipeline

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:azure-pipelines.yml:28-222`; `ddd-subdomain:README.md:278-337`; `ddd-subdomain:.gitmodules:1-6` |
| Original carrier | real executable |
| Inputs | model.yaml/.feature/Markdown changes from a push to master, repoUrl, and System.AccessToken. |
| Outputs | Clones target BCs, copies features, commits/pushes, and creates ADO PRs; failures are aggregated per BC. |
| Preconditions | Azure Ubuntu, Python/PyYAML, az CLI, a token, target permissions, and repoUrl. |
| Failure and write boundaries | Validation failures block; missing repoUrl and parse failures are aggregated; feature/model lookups can miss files; the success path writes to the remote. |
| Current skeleton gap | Task11 has implemented local, explicit per-BC three-way `.feature` proposals; the original remote clone/push/PR fan-out and platform run evidence are still missing, and the local proposals cannot be treated as an accepted complete replacement. |
| Target tasks / enhancement acceptance | 10, 11, 13 / ENH-01, ENH-06, ENH-10, ENH-11, ENH-12, ENH-13, ENH-14 |
| Target acceptance | An authorized, isolated ADO fixture can verify objects, the copy list, failure aggregation, and PRs; without authorization, only per-target proposals are produced. |
| Local implementation status | Task11's local read-only proposals and this scoped re-review are complete, and the path isolation fix is confirmed; see the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task11-review). The maintainer workflow has not been run, and external propagation remains not-run; the full equivalence conclusion for ENH-11/Task14 is not closed |

### FRAMEWORK-10: Management summary PPT generation

| Item | Source observation / local plan |
|---|---|
| Source location | `ddd-subdomain:.github/utilities/_gen_ppt.py:1-477`; `ddd-subdomain:TEMPLATE-CHANGELOG.md:1-56` |
| Original carrier | real executable |
| Inputs | Framework descriptions, colors, page content, and the output path, all hardcoded in the script. |
| Outputs | python-pptx writes a fixed file and prints the path. |
| Preconditions | python-pptx and a writable D:\CPWS\DomainModeling; no CLI arguments. |
| Failure and write boundaries | Saving fails when the dependency/directory/permission is missing; writes to a fixed absolute path and does not change domain Markdown. |
| Current skeleton gap | There is no general presentation export yet; the original one-off management content and fixed output path are not copied. |
| Target tasks / enhancement acceptance | 17 / ENH-01, ENH-13, ENH-17 |
| Target acceptance | Must provide parameterized equivalent output through render_presentation(inputs, format); parity must not be satisfied by excluding presentation via the distribution allowlist, and the original script's hardcoded content or personal paths must not be copied. When PDF/PPTX is requested, dependency, file signature, and page/slide count checks remain required gates; a missing dependency or an actual format check that was not run can only be recorded as unavailable/not-run and must not be called a passing presentation export. |
| Local implementation status | Source verified; implementation and verification of the target methods/tools follow the plan; not counted as functionally complete |

## 7. Upstream proposals and unresolved capabilities

| ID | Name | Source status | Location |
|---|---|---|---|
| FRAMEWORK-11 | Roadmap gap detector and auto-fix orchestration | proposed-upstream | `ddd-subdomain:_roadmap/02-execution-engine.md:1-309`; `ddd-subdomain:.github/utilities/validate_artifact.py:31-274` |
| FRAMEWORK-12 | Roadmap CLI, migration, and tiered profiles | proposed-upstream | `ddd-subdomain:_roadmap/01-ddd-abstraction.md:1-130`; `ddd-subdomain:_roadmap/03-scaffolding-automation.md:1-283`; `ddd-subdomain:_roadmap/05-tiered-profiles.md:1-179` |
| FRAMEWORK-13 | Roadmap GHE CODEOWNERS, Ruleset, and Knowledge Base | proposed-upstream | `ddd-subdomain:_roadmap/04-ghe-native-integration.md:1-150`; `ddd-subdomain:.github/PULL_REQUEST_TEMPLATE.md:1-64`; `ddd-subdomain:.github/ai-tool-config.yaml:44-63` |
| FRAMEWORK-14 | Roadmap real graph and PR impact trigger | proposed-upstream | `ddd-subdomain:_roadmap/07-graph-generator.md:1-175`; `ddd-subdomain:_roadmap/08-impact-assessment-trigger.md:1-183`; `ddd-subdomain:.github/utilities/graph_generator.py:73-436` |
| FRAMEWORK-15 | Roadmap web query and @tantu extension | proposed-upstream | `ddd-subdomain:_roadmap/06-web-surface.md:1-160`; `ddd-subdomain:docs/concepts/three-repos.md:1-120` |
| FRAMEWORK-16 | Roadmap code/SQL reverse-engineering adapters and full confidence pipeline | proposed-upstream | `ddd-subdomain:_roadmap/P4-01-reverse-engineering.md:1-265`; `ddd-subdomain:.github/utilities/confidence_scorer.py:55-335`; `ddd-subdomain:.github/utilities/tests/test_p4_01_cardiac_imaging.py:109-254` |
| FRAMEWORK-17 | Pinned-version prompt/template dependencies | unverified | `ddd-subdomain:.gitmodules:1-6`; `ddd-subdomain:.github/prompts:metadata-only`; `ddd-subdomain:_templates:metadata-only` |

## 8. Per-file, directory, and gitlink inventory

See section 5 for each repository's full version and source; paths are relative to that repository's root. Object IDs use short prefixes for navigation; the full values are kept in the original Git trees and the local manifest. A metadata-only entry for a directory/gitlink is never presented as a full-text read.

### ddd-bc

| Original repository path | Type / object | Classification / source status | Read coverage | Capabilities | Summary |
|---|---|---|---|---|---|
| `.github` | tree / `44a7da3823a7` | directory / observed-current | metadata-only | BC-02, BC-13 | GitHub configuration directory holding repository-level instructions and shared entry points. |
| `.github/copilot-instructions.md` | blob / `6ac1e555d9c9` | guide / observed-current | full | BC-02, BC-03, BC-07, BC-12, BC-14 | Defines bottom-of-V artifact boundaries, derivation order, template-based creation, the read-only domain source, and risk/ADR rules. |
| `.github/instructions` | tree / `966c17cc6382` | directory / observed-current | metadata-only | BC-13 | Directory of path-matched implementation, architecture, security, coding, and testing rules. |
| `.github/instructions/architecture.instructions.md` | blob / `3ca998d6d973` | guide / observed-current | full | BC-05, BC-07, BC-13 | Specifies four-layer dependency direction, interface boundaries, cloud-native endpoints, observability, and container requirements. |
| `.github/instructions/coding-standards.instructions.md` | blob / `c908a81f9ce0` | guide / observed-current | full | BC-07, BC-13 | Specifies naming, function responsibilities, error handling, domain patterns, dependencies, and static quality constraints. |
| `.github/instructions/implementation.instructions.md` | blob / `a41bb9ef48e8` | guide / observed-current | full | BC-02, BC-03, BC-04, BC-05, BC-06 | Requires reading the configuration and domain source first and generating implementation traced to SR/US/VT; forbids out-of-scope fabrication. |
| `.github/instructions/security.instructions.md` | blob / `484d2d22912f` | guide / observed-current | full | BC-13 | Provides security guardrails for secrets, input, authentication/authorization, cryptography, the dependency supply chain, and log leakage. |
| `.github/instructions/testing.instructions.md` | blob / `defd20e25d74` | guide / observed-current | full | BC-06, BC-13 | Defines unit/integration/E2E layering, coverage, AAA, determinism, risk controls, and CI quality gates. |
| `.github/prompts` | commit / `08f8219397d6` | gitlink / observed-current | metadata-only | BC-03, BC-04, BC-05, BC-06, BC-07, BC-08, BC-09, BC-10, BC-11, BC-12 | Pinned pointer to the shared prompt repository; the actual content is inventoried separately from the pinned commit in the same group. |
| `.gitignore` | blob / `e7b3cae321d1` | marker / observed-current | full | BC-01 | Ignores virtual environments, demo documents, and the src directory, reflecting the template repository's distribution boundary. |
| `.gitmodules` | blob / `030c87cb0b73` | config / observed-current | full | BC-01, BC-10 | Registers two relative-URL submodules, prompts and templates; no real domain-model submodule is registered. |
| `CONCEPTS.md` | blob / `6637d3a2f537` | guide / observed-current | full | BC-02, BC-03, BC-08, BC-12, BC-13 | Explains the V model, the four artifact types, traceability chains, the read-only domain rule, risk chains, and prompt interaction modes. |
| `README.md` | blob / `3470b9929c12` | guide / instance-only | full | BC-01, BC-02, BC-03, BC-10 | Provides the post-instantiation quick start, step table, directory layout, role ownership, and prompt navigation; it is still a placeholder BC. |
| `TEMPLATE-CHANGELOG.md` | blob / `a011bbdfa437` | roadmap / proposed-upstream | full | BC-14 | Records structural evolution across template versions and unreleased skill changes; must not be treated as runtime automation. |
| `_templates` | commit / `00705aef6c70` | gitlink / observed-current | metadata-only | BC-02, BC-14 | Pinned pointer to the implementation-side forms repository; the actual template content is inventoried separately from the pinned commit in the same group. |
| `architecture` | tree / `2d458f3aa2f3` | directory / observed-current | metadata-only | BC-05, BC-11 | Architecture artifact directory holding ABBs, ADR references, and later sequence diagrams. |
| `architecture/README.md` | blob / `908a39672f8e` | guide / instance-only | full | BC-05, BC-14 | Describes ABB types, the creation entry point, ADR requirements, and the index; the instance index is still empty. |
| `architecture/_abb-template.md` | blob / `4788a5d49b9b` | template / observed-current | full | BC-05, BC-14 | Provides the ABB form with ADR, QAS, interface, dependency version, deployment, and observability fields. |
| `architecture/adr-references.md` | blob / `36bc737d91f5` | config / instance-only | full | BC-05 | Registers ADRs from the central architecture wiki and architecture matters still to be decided; currently contains only placeholder rows. |
| `backlog.md` | blob / `f8f3f8df1af1` | roadmap / instance-only | full | BC-08, BC-09 | Defines BL-NNN open/closed items, categories, and dependency records; the instance currently has only placeholder items to replace. |
| `bc-config.yaml` | blob / `a83e4f116f21` | config / instance-only | full | BC-01, BC-12 | Defines the BC, subdomain, domain repository, context path, implementation repository, language, and framework fields; all are still placeholder values. |
| `domain-model` | tree / `ca31f8ccafe5` | directory / instance-only | metadata-only | BC-01, BC-03, BC-07, BC-10, BC-12 | Mount-point directory for the domain source; in this snapshot it is still a placeholder directory, not a resolved cross-repository gitlink. |
| `domain-model/README.md` | blob / `01368bb9497e` | guide / instance-only | full | BC-01, BC-10 | Describes domain submodule initialization, the read-only boundary, and the expected directories; provides no actual UC/INV content. |
| `software-requirements` | tree / `5b63ecad5556` | directory / observed-current | metadata-only | BC-02, BC-03 | Software requirements directory and its bottom-of-V artifact location. |
| `software-requirements/README.md` | blob / `374ceacaf934` | guide / instance-only | full | BC-02, BC-03 | Specifies SR source, testability, naming, index, and traceability requirements; the instance index is empty. |
| `tools` | tree / `f9c07fc66516` | directory / observed-current | metadata-only | BC-01 | Maintenance script directory; it currently contains only the domain submodule installation script. |
| `tools/setup-domain-model-submodule.ps1` | blob / `30e186a5a284` | utility / observed-current | full | BC-01, BC-10 | Real PowerShell installer: checks the root directory, removes the placeholder, adds the domain submodule, disables recursion, and commits the changes. |
| `traceability-matrix.md` | blob / `a9fe9f9607b9` | guide / instance-only | full | BC-02, BC-08 | Provides REQ/UC/INV/SR/US/ABB/VT/RC matrix columns, coverage statistics, and an open-gaps section. |
| `user-stories` | tree / `49e70aeb562b` | directory / observed-current | metadata-only | BC-02, BC-04 | User story directory and bottom-of-V delivery slice location. |
| `user-stories/README.md` | blob / `73583abee064` | guide / instance-only | full | BC-02, BC-04 | Specifies that USs must be derived from approved SRs, sliced by value, and entered into the matrix; the instance index is empty. |
| `verification` | tree / `7508315d2b39` | directory / observed-current | metadata-only | BC-02, BC-06 | Verification specification directory holding VT documents and later references to implementation tests. |
| `verification/README.md` | blob / `ba7ebe1d55b8` | guide / instance-only | full | BC-02, BC-06 | Defines the boundary between VT specifications and verification code, the three test types, safety-critical markers, and index fields. |

### ddd-bc-prompts

| Original repository path | Type / object | Classification / source status | Read coverage | Capabilities | Summary |
|---|---|---|---|---|---|
| `abb-design.prompt.md` | blob / `ef8716372ff9` | prompt / observed-current | full | BC-05, BC-12 | Interactively designs ABBs from approved USs, capabilities, QAS, and the context map, and requires ADRs, versions, and the model summary. |
| `backlog-review.prompt.md` | blob / `42722b07142b` | prompt / observed-current | full | BC-08 | Autonomously scans the backlog and artifacts, closes resolved items, and identifies stale items and new traceability/risk gaps. |
| `code-generation.prompt.md` | blob / `2dc9aef4dff7` | prompt / observed-current | full | BC-07, BC-12 | Interactively generates four-layer DDD source code, checks the language/framework/approved US/ABB, and stops writing on non-empty file conflicts. |
| `impact-assessment.prompt.md` | blob / `d21da381d51e` | prompt / observed-current | full | BC-09 | For REQ/UC/INV changes, traces direct/indirect impact, risk chains, and status rollbacks that need confirmation. |
| `onboarding.prompt.md` | blob / `92cc23dac911` | prompt / observed-current | full | BC-10 | Collects instance configuration step by step and guides the reading order from the domain model to SR/US/ABB/VT; the walkthrough stays read-only. |
| `query.prompt.md` | blob / `e22ccfd09a33` | prompt / observed-current | full | BC-08 | Queries artifacts read-only by ID, traceability chain, gap, safety chain, coverage statistics, or ABB, and passively reports gaps. |
| `review.prompt.md` | blob / `cb36a31fb402` | prompt / observed-current | full | BC-08, BC-13 | Autonomously checks traceability completeness, RC safety chains, SR/US/ABB/VT quality, and backlog health; reports only and does not write. |
| `sequence-diagram.prompt.md` | blob / `3eacf30ae706` | prompt / observed-current | full | BC-11, BC-12 | Generates Mermaid sequence diagrams for success and failure paths from UC/ABB/event/integration relationships and updates sequenceSummary. |
| `skills` | tree / `86dcb726abc6` | directory / observed-current | metadata-only | BC-03, BC-12 | Shared Agent skill directory. |
| `skills/bc-implementation` | tree / `7ba065dbd84c` | directory / observed-current | metadata-only | BC-03, BC-12 | BC implementation skill directory containing a single SKILL.md. |
| `skills/bc-implementation/SKILL.md` | blob / `ebc3bc2babfa` | skill / observed-current | full | BC-03, BC-04, BC-05, BC-06, BC-07, BC-08, BC-09, BC-10, BC-12 | Centrally specifies domain-first reading, the read-only submodule, proposal confirmation, statuses, traceability chains, the four-layer architecture, and model.yaml updates. |
| `sr-derivation.prompt.md` | blob / `54a6457a94d3` | prompt / observed-current | full | BC-03, BC-12 | Drafts testable SRs path by path from approved REQ/UC/INV, updates the matrix and srSummary, and protects changes with rollback guards. |
| `story-derivation.prompt.md` | blob / `98c2330486b8` | prompt / observed-current | full | BC-04, BC-12 | Slices deliverable USs from approved SRs and UC actors, covers positive/alternate/invariant ACs, and updates storySummary. |
| `traceability-build.prompt.md` | blob / `a058e3b244d7` | prompt / observed-current | full | BC-08, BC-12 | Rebuilds the matrix from domain and bottom-of-V artifacts, computes coverage, registers blanks and broken links, and can append backlog gaps. |
| `verification-test.prompt.md` | blob / `522a30b2857c` | prompt / observed-current | full | BC-06, BC-12 | Generates the VT Markdown and Gherkin pair from US/SR/INV/ABB, distinguishing unit/integration/E2E and safety-critical items. |

### ddd-bc-templates

| Original repository path | Type / object | Classification / source status | Read coverage | Capabilities | Summary |
|---|---|---|---|---|---|
| `items` | tree / `032f2d86e544` | directory / observed-current | metadata-only | BC-02, BC-14 | Directory of implementation-side artifact item forms. |
| `items/abb.md` | blob / `0ee1674c9824` | template / observed-current | full | BC-05, BC-14 | ABB item form with ADR, QAS, interface, dependency version, deployment, and observability fields. |
| `items/sequence-diagram.md` | blob / `14f450de19ea` | template / observed-current | full | BC-11, BC-14 | Sequence diagram form that fixes participants, success/error Mermaid scenarios, and notes on open items. |
| `items/sr.md` | blob / `4a0cbea15a5f` | template / observed-current | full | BC-03, BC-14 | SR form with REQ/UC/INV/RC metadata, testable ACs, scope, and verification method. |
| `items/user-story.md` | blob / `7e7985e57abd` | template / observed-current | full | BC-04, BC-14 | US form that fixes the actor/value narrative, positive and alternate paths, mandatory invariant ACs, and DoD. |
| `items/verification-test.feature` | blob / `b219c3e7efb5` | template / observed-current | full | BC-06, BC-14 | VT Gherkin form specifying tags, background, success path, invariant negative cases, and parameterized examples. |
| `items/verification-test.md` | blob / `a629fa3dfc66` | template / observed-current | full | BC-06, BC-14 | VT specification form that fixes the type, US/SR/AC, safety marker, test file, and status fields. |
| `software-requirements` | tree / `5c14cdbcccb9` | directory / observed-current | metadata-only | BC-03, BC-14 | Dedicated software requirement form directory. |
| `software-requirements/_template.md` | blob / `0c30173a2534` | template / observed-current | full | BC-03, BC-14 | Software requirements directory form that adds the SR's observable statement, scope, and verification method. |
| `user-stories` | tree / `d063b5c1015d` | directory / observed-current | metadata-only | BC-04, BC-14 | Dedicated user story form directory. |
| `user-stories/_template.md` | blob / `232603adf6ed` | template / observed-current | full | BC-04, BC-14 | User stories directory form that fixes actor/need/value, mandatory ACs, DoD, and PR checks. |
| `verification` | tree / `9ae6ee3ebc81` | directory / observed-current | metadata-only | BC-06, BC-14 | Verification form directory split into E2E, integration, and unit. |
| `verification/e2e-test-spec.md` | blob / `497a75ac5b3f` | template / observed-current | full | BC-06, BC-14 | E2E specification form that fixes the end-to-end boundary, environment, journey, external outcomes, and negative cases. |
| `verification/integration-test-spec.md` | blob / `3e8c9b3d852e` | template / observed-current | full | BC-06, BC-14 | Integration specification form that fixes the boundary between two components, real infrastructure, stimulus, assertions, and cleanup. |
| `verification/unit-test-spec.md` | blob / `7248b40d4e0f` | template / observed-current | full | BC-06, BC-14 | Unit specification form that fixes a single behavior, the no-infrastructure precondition, observable assertions, and the test framework field. |

### ddd-subdomain-prompts

| Original repository path | Type / object | Classification / source status | Read coverage | Capabilities | Summary |
|---|---|---|---|---|---|
| `adr.prompt.md` | blob / `28664bca680e` | prompt / observed-current | full | DOMAIN-06 | Creates new ADRs and assesses the impact of incoming ADRs; collects decisions, impacts, confirmations, and BL tracking. |
| `backlog-review.prompt.md` | blob / `a84d75b3c6c1` | prompt / observed-current | full | DOMAIN-09 | Scans open questions, placeholders, consistency, and traceability gaps, maintains the backlog, and reports remaining items. |
| `distillation.prompt.md` | blob / `df64853e619b` | prompt / observed-current | full | DOMAIN-03 | Has domain experts review language, concepts, boundaries, breakthroughs, and model-code drift. |
| `elicitation.prompt.md` | blob / `38fdba38f8ae` | prompt / observed-current | full | DOMAIN-02, DOMAIN-16, DOMAIN-20 | With Intended Use as a prerequisite, interviews for subdomains, BCs, vocabulary, UCs, BRs, and INVs. |
| `glossary-sync.prompt.md` | blob / `c61f774486e7` | prompt / observed-current | full | DOMAIN-10 | Compares internal and external glossaries, classifies alignments/divergences, and changes local terms after approval. |
| `impact-assessment.prompt.md` | blob / `f131fe25e563` | prompt / observed-current | full | DOMAIN-07 | Analyzes REQ change impact along the REQ-CAP-UC-INV-TS chain; reports first, edits afterwards. |
| `intended-use-amendment.prompt.md` | blob / `af7415c9c8e1` | prompt / observed-current | full | DOMAIN-08, DOMAIN-20 | Performs regulatory grading, risk re-analysis, and escalation for changes to Intended Use, constraints, and safety classification. |
| `onboarding.prompt.md` | blob / `47c2b32b148d` | prompt / observed-current | full | DOMAIN-01, DOMAIN-16, DOMAIN-20 | Gives a role-based, ordered tour of Intended Use, the model, requirements, traceability, stable areas, and open areas. |
| `published-interface.prompt.md` | blob / `271d1a81d886` | prompt / observed-current | full | DOMAIN-11, DOMAIN-18 | Handles interface publication, consumers, deprecation, versions, breaking-change classification, and change notifications. |
| `query.prompt.md` | blob / `6cb6ca8df6ac` | prompt / observed-current | full | DOMAIN-12 | Lists, filters, or summarizes model objects read-only by object type and scope. |
| `requirements-capture.prompt.md` | blob / `aac2c2664eff` | prompt / observed-current | full | DOMAIN-05, DOMAIN-14 | Captures REQ/QAS and checks governance, automatic derivation, quality characteristics, UC links, and the matrix. |
| `reverse-engineering.prompt.md` | blob / `aa68b5e57fd9` | prompt / observed-current | full | DOMAIN-04, DOMAIN-14 | Reverse-engineers Draft objects, a confidence report, and BLs from ADO Epic/Feature/Story/Test Case items. |
| `review.prompt.md` | blob / `bd5492456f21` | prompt / observed-current | full | DOMAIN-03, DOMAIN-09, DOMAIN-20 | Reviews by Intended Use, aggregates, INVs, responsibilities, events, UCs, cross-context concerns, vocabulary, and QAS. |
| `skills` | tree / `a6c3ae3939f9` | directory / observed-current | metadata-only | DOMAIN-01 | Directory: domain-modeling skill entry point. |
| `skills/domain-modeling` | tree / `fcec52d9939d` | directory / observed-current | metadata-only | DOMAIN-01, DOMAIN-16 | Directory: body of the unified domain modeling skill. |
| `skills/domain-modeling/SKILL.md` | blob / `b0f71eaf999a` | skill / observed-current | full | DOMAIN-01, DOMAIN-16, DOMAIN-20 | The unified skill defines guardrails, traceability chains, status rules, and prompt routing. |
| `swas.prompt.md` | blob / `cf85ba3b58ff` | prompt / observed-current | full | DOMAIN-15, DOMAIN-19 | Authors the SWAS from the model, requirements, ABBs, risk, and the verification bridge; missing material is left as placeholders. |
| `test-scenario.prompt.md` | blob / `78d269efab2e` | prompt / observed-current | full | DOMAIN-13, DOMAIN-14 | Generates BC, cross-BC, acceptance, and QAS scenarios from approved UC/INV/REQ/QAS. |
| `traceability-build.prompt.md` | blob / `8ad1242cedef` | prompt / observed-current | full | DOMAIN-14, DOMAIN-19 | Builds the matrix, gaps, orphans, and the QMS risk table from REQ/CAP/UC/INV/TS and bridge data. |

### ddd-subdomain-templates

| Original repository path | Type / object | Classification / source status | Read coverage | Capabilities | Summary |
|---|---|---|---|---|---|
| `context` | tree / `2169baf36a9c` | directory / observed-current | metadata-only | DOMAIN-16, DOMAIN-19 | Directory: bounded context template root. |
| `context/README.md` | blob / `2eacba8ea2a6` | guide / observed-current | full | DOMAIN-16 | BC entry point and a boundary→core model→details stage checklist, including release unit/open questions. |
| `context/aggregates` | tree / `1e23c06e961a` | directory / observed-current | metadata-only | DOMAIN-17 | Directory: container for aggregate root files. |
| `context/aggregates/README.md` | blob / `b5292947b58a` | guide / observed-current | full | DOMAIN-17 | Aggregate directory and consistency boundary checks, requiring a root, lifecycle, atomic saves, and ID references. |
| `context/capabilities.md` | blob / `5f92f4c3642c` | template / observed-current | full | DOMAIN-16 | CAP catalog/details, requiring grouping of multiple REQs, linked UCs, dependencies, extension points, release unit, and status. |
| `context/domain-events` | tree / `a5492ec626a0` | directory / observed-current | metadata-only | DOMAIN-17 | Directory: container for domain event files. |
| `context/domain-events/README.md` | blob / `701a46afe6f1` | guide / observed-current | full | DOMAIN-17 | Domain event design entry point: past-tense business facts, source aggregate, consumers, and data boundaries. |
| `context/domain-events/catalog.md` | blob / `06dc1c661387` | template / observed-current | full | DOMAIN-17, DOMAIN-18 | Inventory of published/consumed/deprecated events, recording source, reaction, ACL, version, and sunset. |
| `context/entities` | tree / `240586966865` | directory / observed-current | metadata-only | DOMAIN-17 | Directory: container for non-root entity files. |
| `context/entities/README.md` | blob / `f8a4be0755c3` | guide / observed-current | full | DOMAIN-17 | Non-root entity directory and an Entity/Value Object/Aggregate Root decision table. |
| `context/integration` | tree / `626f89a86f5a` | directory / observed-current | metadata-only | DOMAIN-18 | Directory: container for context integration partner files. |
| `context/integration/README.md` | blob / `e442c86bf94f` | guide / observed-current | full | DOMAIN-18 | Consumer/producer partner contracts covering ACL/OHS, versions, failure handling, and notifications. |
| `context/invariants.md` | blob / `1c185f209b7b` | template / observed-current | full | DOMAIN-16, DOMAIN-17, DOMAIN-20 | Distinguishes external preconditions from this context's INVs and links BR/RC, scope, enforcer, tests, and status. |
| `context/model.yaml` | blob / `a302efb7b9f1` | config / observed-current | full | DOMAIN-19 | Machine snapshot: release unit, domain objects, events/policies, and the ABB/sequence/SR/US/VT/governance/risk/release bridge. |
| `context/policies` | tree / `d00e1e806c53` | directory / observed-current | metadata-only | DOMAIN-17 | Directory: container for policy files. |
| `context/policies/README.md` | blob / `5a4db54ee725` | guide / observed-current | full | DOMAIN-17 | Reactive policy guidance and checklist, requiring an event trigger, a business action, and model.yaml sync. |
| `context/policies/catalog.md` | blob / `1e53b1a9d851` | template / observed-current | full | DOMAIN-17 | Policy inventory with trigger, action, BR, status, retirement, and a single-trigger constraint. |
| `context/purpose.md` | blob / `4c0d62ef209a` | template / observed-current | full | DOMAIN-16, DOMAIN-20 | BC core responsibility, concepts it exclusively owns/explicitly does not own, participants, and implementation attributes. |
| `context/services` | tree / `e060c4cc9969` | directory / observed-current | metadata-only | DOMAIN-17 | Directory: container for domain service files. |
| `context/services/README.md` | blob / `cf33f983642a` | guide / observed-current | full | DOMAIN-17 | Domain service directory and its applicability boundary: usable across aggregates; orchestration/integration does not belong here. |
| `context/use-cases.md` | blob / `67938a11800c` | template / observed-current | full | DOMAIN-16, DOMAIN-17 | UC catalog/details recording Actor, Trigger, Outcome, REQ, flow, events, BR, and status. |
| `context/value-objects` | tree / `253d73e8509b` | directory / observed-current | metadata-only | DOMAIN-17 | Directory: container for value object files. |
| `context/value-objects/README.md` | blob / `4b928a7b579f` | guide / observed-current | full | DOMAIN-17 | Value object directory and a checklist for immutability, no identity, self-validation, and no side effects. |
| `items` | tree / `4aeac975a32e` | directory / observed-current | metadata-only | DOMAIN-06, DOMAIN-17 | Directory: container for single-item domain artifact forms. |
| `items/adr.md` | blob / `cf6ea44f52f7` | template / observed-current | full | DOMAIN-06 | ADR form: problem, scope, drivers, options, conclusion, pros and cons, governance, and links. |
| `items/aggregate.md` | blob / `d8b078214c98` | template / observed-current | full | DOMAIN-17 | Aggregate form: identity, root, composition, Factory, rules, states, events, repository, boundary rationale, and evolution. |
| `items/capability.md` | blob / `4239f438885f` | template / observed-current | full | DOMAIN-16 | Single CAP details: purpose, REQ, UC, capability dependencies, extension points, release unit, and BL. |
| `items/domain-event.md` | blob / `6caf281cfd9d` | template / observed-current | full | DOMAIN-17, DOMAIN-18 | Event form: fact, trigger, schema, consumers, idempotency, version, and sample payload. |
| `items/domain-service.md` | blob / `6f805662cacc` | template / observed-current | full | DOMAIN-17 | Stateless domain service: placement rationale, operations, pure domain dependencies, rules, events, and evolution. |
| `items/entity.md` | blob / `ae3438ba38d7` | template / observed-current | full | DOMAIN-17 | Entity form: identity, owning aggregate, attributes, lifecycle, rules, relationships, and evolution. |
| `items/factory.md` | blob / `11992950a32c` | template / observed-current | full | DOMAIN-17 | Factory form: creation rationale, preconditions, invariants, inputs, events, location, and BL. |
| `items/integration-partner.md` | blob / `84c6d7ecab57` | template / observed-current | full | DOMAIN-18 | Partner integration form: direction, pattern, received/published items, ACL, version, failure handling, and open questions. |
| `items/policy.md` | blob / `09c1be20feef` | template / observed-current | full | DOMAIN-17 | Policy form that expresses rules as when-event/then-action and records guard, effect, conflicts, and boundaries. |
| `items/value-object.md` | blob / `03423e216fe6` | template / observed-current | full | DOMAIN-17 | Value object form: attribute constraints, construction validation, equality, immutability, behavior, examples, and evolution. |
| `qms-traceability-matrix.md` | blob / `39a38ac71611` | template / observed-current | full | DOMAIN-14, DOMAIN-19 | QMS forward/risk traceability tables that count gaps and blockers separately for REQ/SR/ABB/VT and for RISK/RC. |
| `requirements` | tree / `7aadc567614c` | directory / observed-current | metadata-only | DOMAIN-05 | Directory: container for REQ/QAS forms. |
| `requirements/_template-qas.md` | blob / `da42e352bc77` | template / observed-current | full | DOMAIN-05, DOMAIN-14 | ATAM QAS form: testable response, acceptance, domain impact, traceability, limitations, risks, and questions. |
| `requirements/_template.md` | blob / `9ef10c5db817` | template / observed-current | full | DOMAIN-05, DOMAIN-14 | REQ form: identity, problem/outcome, AC/scope, domain impact, traceability, quality checks, and status log. |
| `scenarios` | tree / `14d1b891f3e5` | directory / observed-current | metadata-only | DOMAIN-13 | Directory: container for domain, acceptance, and cross-BC scenarios. |
| `scenarios/acceptance-test.feature` | blob / `37a2d930fa6b` | template / observed-current | full | DOMAIN-13 | REQ acceptance Gherkin: tags, background, AC scenarios, and boundary rejection scenarios. |
| `scenarios/acceptance-test.md` | blob / `97aa087a29f9` | template / observed-current | full | DOMAIN-13, DOMAIN-14 | Acceptance metadata: REQ/UC/QAS/BC, status, scope, and the link to the companion feature. |
| `scenarios/cross-bc-scenario.feature` | blob / `5282a0802591` | template / observed-current | full | DOMAIN-13 | Cross-BC Gherkin: contexts, component scenarios, preconditions, and end-to-end outcomes. |
| `scenarios/cross-bc-scenario.md` | blob / `e784f21e71c6` | template / observed-current | full | DOMAIN-13, DOMAIN-14 | Cross-BC metadata: participating BCs, component scenarios, E2E repository, interfaces, events, and status. |
| `scenarios/domain-scenario.feature` | blob / `072ef1daa2c1` | template / observed-current | full | DOMAIN-13 | BC domain Gherkin: happy/alternate/negative paths, UC/REQ tags, and INV violation examples. |
| `scenarios/domain-scenario.md` | blob / `56bb0255c982` | template / observed-current | full | DOMAIN-13, DOMAIN-14 | Domain scenario metadata: UC/REQ/INV/BR/QAS and Gherkin/load/chaos/security verification methods. |
| `subdomain` | tree / `925a0a9b8cfc` | directory / observed-current | metadata-only | DOMAIN-16, DOMAIN-20 | Directory: subdomain-level template root. |
| `subdomain/architecture-spec` | tree / `f0affa94f8c1` | directory / observed-current | metadata-only | DOMAIN-15 | Directory: subdomain SWAS and build resources. |
| `subdomain/architecture-spec/.order` | blob / `660756da304c` | marker / observed-current | full | DOMAIN-15 | Marker file that preserves the SWAS document generation order. |
| `subdomain/architecture-spec/AS-[SubdomainName].md` | blob / `cc5f25ae3155` | template / observed-current | full | DOMAIN-15 | QMS SWAS skeleton: goals, constraints, context, building blocks, runtime, deployment, data, threats, verification, quality, and safety. |
| `subdomain/architecture-spec/diagrams` | tree / `d564d0bc3dd9` | directory / observed-current | metadata-only | DOMAIN-15 | Directory: container for SWAS diagram resources. |
| `subdomain/architecture-spec/diagrams/.gitkeep` | blob / `e69de29bb2d1` | marker / observed-current | full | DOMAIN-15 | Empty marker that keeps the SWAS diagram directory. |
| `subdomain/architecture-spec/metadata.json` | blob / `60cf832ae540` | config / observed-current | full | DOMAIN-15 | Configuration for the PDF cover, headers/footers, version date, and disclaimer. |
| `subdomain/architecture-spec/pipelines` | tree / `45f593209917` | directory / observed-current | metadata-only | DOMAIN-15 | Directory: container for the SWAS PDF pipeline. |
| `subdomain/architecture-spec/pipelines/generate-pdf.yml` | blob / `74a9b14b3e4f` | pipeline / observed-current | full | DOMAIN-15 | Azure pipeline that, on master, triggers the external markdown-to-qmspdf container and publishes the PDF. |
| `subdomain/contexts` | tree / `c3d297fc0d5d` | directory / observed-current | metadata-only | DOMAIN-16 | Directory: container for the subdomain's bounded contexts. |
| `subdomain/contexts/README.md` | blob / `f8d583455696` | guide / observed-current | full | DOMAIN-16 | Describes creating BCs via prompt, naming, ownership, boundary file order, and directory maintenance. |
| `subdomain/glossary` | tree / `f1f834a36265` | directory / observed-current | metadata-only | DOMAIN-10, DOMAIN-20 | Directory: container for subdomain vocabulary and business rules. |
| `subdomain/glossary/business-rules.md` | blob / `c0f08cdb56cc` | template / observed-current | full | DOMAIN-16, DOMAIN-20 | Subdomain BR form: cross-context/single-context rules, source, enforcer, INV index, and change log. |
| `subdomain/glossary/ubiquitous-language.md` | blob / `9da68a21d025` | template / observed-current | full | DOMAIN-10, DOMAIN-20 | Subdomain glossary: terms, contexts, ambiguities, deprecated terms, and naming conventions. |
| `subdomain/intended-use.md` | blob / `e5262ecbe1d9` | template / observed-current | full | DOMAIN-08, DOMAIN-20 | Regulatory/clinical anchor: purpose, use, patients/users, principle of operation, misuse, approval, and evolution. |
| `subdomain/published-interface.md` | blob / `6ee93e00702a` | template / observed-current | full | DOMAIN-11, DOMAIN-18 | External interface contract: identity, language, model, events, services, versions/notifications, consumers, and questions. |
| `subdomain/strategic` | tree / `8f43f0142140` | directory / observed-current | metadata-only | DOMAIN-18, DOMAIN-20 | Directory: container for strategic BC/context-map files. |
| `subdomain/strategic/bounded-contexts.md` | blob / `787c97f0ecf3` | template / observed-current | full | DOMAIN-16, DOMAIN-20 | BC list: release unit, owning team, status, Core/Supporting/Generic guidance, and health summary. |
| `subdomain/strategic/context-map.md` | blob / `bb49057fb40e` | template / observed-current | full | DOMAIN-18, DOMAIN-20 | Context relationships: direction, pattern, contract, translation, SDK, Shared Kernel, Separate Ways, and questions. |
| `subdomain/subdomain-definition.md` | blob / `4cd65bd7079f` | template / observed-current | full | DOMAIN-16, DOMAIN-18, DOMAIN-20 | Subdomain master table: Intended Use, safety/environment, vision, classification, responsibilities, BCs, Core, interfaces, dependencies, and events. |

### ddd-subdomain

| Original repository path | Type / object | Classification / source status | Read coverage | Capabilities | Summary |
|---|---|---|---|---|---|
| `.github` | tree / `e869d7b509b8` | directory / observed-current | metadata-only | FRAMEWORK-01, FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `.github/PULL_REQUEST_TEMPLATE.md` | blob / `861e8c554efc` | template / observed-current | full | FRAMEWORK-03 | PR form that collects a summary, artifact types, AI review, traceability, and check items; ticking the boxes does not itself perform verification. |
| `.github/ai-interaction-log.csv` | blob / `64d48d1bb34c` | marker / instance-only | full | FRAMEWORK-07 | The AI interaction log has only fixed fields and comments; the snapshot contains no actual record rows. |
| `.github/ai-tool-config.yaml` | blob / `e195376c34c6` | config / observed-current | full | FRAMEWORK-03, FRAMEWORK-07, FRAMEWORK-08 | Declares Copilot tool roles, human review, hooks, validation, logging, and billing controls; its status is still unqualified and it contains placeholders. |
| `.github/copilot-instructions.md` | blob / `20cc440dd753` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Workspace Agent guidance listing modeling steps, artifact boundaries, traceability, roles, templates, and external repository boundaries; these are prompt rules. |
| `.github/hooks` | tree / `9345216b4efc` | directory / observed-current | metadata-only | FRAMEWORK-08 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `.github/hooks/commit-msg` | blob / `29aa48a03af8` | hook / observed-current | full | FRAMEWORK-08 | Commit message hook that requires reviewed-by for managed paths and skips merge/fixup/squash. |
| `.github/hooks/install_hooks.py` | blob / `df359c1bd8c6` | hook / observed-current | full | FRAMEWORK-08 | Installer that copies the hook/generates a cmd on Windows and, on Unix, deletes the old target and creates a symlink; no conflict backup. |
| `.github/instructions` | tree / `078d68bcba4e` | directory / observed-current | metadata-only | FRAMEWORK-01, FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `.github/instructions/architecture.instructions.md` | blob / `835e5cbabef4` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-03 | Architecture rules requiring layered dependencies, ADRs, testable QAS, health checks, externalized configuration, and SWAS/model.yaml consistency. |
| `.github/instructions/domain-model.instructions.md` | blob / `4215b4ac61dc` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Domain model rules defining directories, naming, traceability, invariant responsibility, RC references, and the confirmation gate for structural changes. |
| `.github/prompts` | commit / `d7da752b7312` | gitlink / unverified | metadata-only | FRAMEWORK-17 | Pinned gitlink to ddd-subdomain-prompts; its commit was not followed this time, so the prompt/skill bodies cannot be verified. |
| `.github/role-profiles` | tree / `1dd54e6d6817` | directory / observed-current | metadata-only | FRAMEWORK-01, FRAMEWORK-02 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `.github/role-profiles/README.md` | blob / `df38ce73acb2` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-02 | Role index that points architecture, product, development, risk, and new members to working guides; the file contains two sets of narratives. |
| `.github/role-profiles/architect.md` | blob / `43ecb246343a` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Architect role guide requiring seven-step modeling, review, traceability, and SWAS; the first and second halves each contain a version of the workflow. |
| `.github/role-profiles/developer.md` | blob / `4684fb8dd74b` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-02 | Developer role guide describing reading the model, implementation, testing, and feedback; the two versions differ on mandatory/optional. |
| `.github/role-profiles/new-team-member.md` | blob / `ee9633fa6abd` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-02 | New member guide providing a two-hour tour, role selection, sample reading, tool entry points, and prohibited actions. |
| `.github/role-profiles/product-manager.md` | blob / `80673e348161` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Product role guide covering intended use, REQ, QAS, the utility tree, and acceptance review; the mandatory items of the two versions are not fully consistent. |
| `.github/role-profiles/risk-manager.md` | blob / `3274a4cf2780` | skill / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Risk role guide covering intended use, RC→INV→REQ→TS, approval, and residual risk; contains two sets of processes. |
| `.github/terminology-bridge.md` | blob / `eaf25d5f4be8` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02 | Provides mappings between DDD, platform, and business language plus directory aliases, for humans and Agents to read. |
| `.github/utilities` | tree / `53cb7df7fc76` | directory / observed-current | metadata-only | FRAMEWORK-04, FRAMEWORK-05, FRAMEWORK-06, FRAMEWORK-07, FRAMEWORK-10 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `.github/utilities/_gen_ppt.py` | blob / `57a8a2d2856f` | utility / observed-current | full | FRAMEWORK-10 | Uses python-pptx to generate a management summary PPT with fixed content and writes it to a hardcoded D: path. |
| `.github/utilities/audio_transcriber.py` | blob / `f38dd60b46b5` | utility / observed-current | full | FRAMEWORK-04 | Provides audio transcription adapters and fallback for Azure Speech, OpenAI Whisper, and an unimplemented Copilot MCP. |
| `.github/utilities/confidence_scorer.py` | blob / `5e4b872d0246` | utility / observed-current | full | FRAMEWORK-04, FRAMEWORK-16 | Scores candidates by base score, repeated words, terminology, and uncertainty/negation/opinion penalties; the cross-source/conflict boosts are zero. |
| `.github/utilities/document_adapter.py` | blob / `53eba7aba4a4` | utility / observed-current | full | FRAMEWORK-04 | Reads Markdown/DOCX, extracts requirement/use-case/invariant/glossary candidates by heading, and returns approximate line numbers. |
| `.github/utilities/graph_generator.py` | blob / `8a64047f03fc` | utility / observed-current | full | FRAMEWORK-06, FRAMEWORK-14 | Parses ID chains from the two traceability matrices and outputs JSON/interactive HTML; uses a built-in demo when there are no IDs. |
| `.github/utilities/input_source_adapter.py` | blob / `07289f196987` | utility / observed-current | full | FRAMEWORK-04, FRAMEWORK-16 | Defines the ExtractedArtifact data shape and the abstract adapter interface, unifying validation, extraction, and supported_types. |
| `.github/utilities/log_interaction.py` | blob / `d7c4fa89e906` | utility / observed-current | full | FRAMEWORK-07 | Interactively appends to the AI log and computes credits from hardcoded model prices; supports summary/estimate. |
| `.github/utilities/tests` | tree / `4691131681bf` | directory / observed-current | metadata-only | FRAMEWORK-04 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `.github/utilities/tests/sample_cardiac_imaging_spec.md` | blob / `a3f3bb12b457` | asset / instance-only | full | FRAMEWORK-04 | Sample cardiac ultrasound specification for reverse extraction tests, with requirements/use cases/invariants/glossary. |
| `.github/utilities/tests/sample_cardiac_imaging_transcript.txt` | blob / `488ab97557cf` | asset / instance-only | full | FRAMEWORK-04 | Sample cardiac ultrasound meeting transcript for reverse extraction tests, with latency, consent, encryption, and archiving constraints. |
| `.github/utilities/tests/test_p4_01_cardiac_imaging.py` | blob / `afab499836d6` | utility / observed-current | full | FRAMEWORK-04, FRAMEWORK-16 | Script-style P4 test that chains adaptation and scoring, using assert/print rather than unittest; cross-source correlation is not implemented. |
| `.github/utilities/transcript_adapter.py` | blob / `616345007678` | utility / observed-current | full | FRAMEWORK-04 | Reads txt/md or calls the transcriber, and uses regular expressions to extract requirement/use-case/invariant/repeated-term candidates. |
| `.github/utilities/validate_artifact.py` | blob / `8bfaa6505ac0` | utility / observed-current | full | FRAMEWORK-05, FRAMEWORK-11 | Checks Markdown headings and a few placeholders by path rule; the default baseline falls back to main/master/origin or the index (staging area). |
| `.gitignore` | blob / `0f34ded61c52` | config / observed-current | full | FRAMEWORK-05, FRAMEWORK-10 | Ignores virtual environments, caches, demo/evaluation files, and local scripts, keeping instance material out of candidates. |
| `.gitmodules` | blob / `b788e0af7174` | config / observed-current | full | FRAMEWORK-17 | Registers two relative-URL submodules, prompts and templates; their content is provided by the pinned gitlinks. |
| `.vscode` | tree / `fa7ae7f454fa` | directory / observed-current | metadata-only | FRAMEWORK-05, FRAMEWORK-06 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `.vscode/tasks.json` | blob / `53c6abed1ad1` | config / observed-current | full | FRAMEWORK-05, FRAMEWORK-06 | Editor tasks that call graph_generator.py and validate_artifact.py directly, using the host python. |
| `CONCEPTS.md` | blob / `78da12b0118f` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Explains DDD/V-model, artifacts, risk traceability, prompt modes, model.yaml, and repo boundaries; large sections repeat after about line 800. |
| `README.md` | blob / `73b804b9fb87` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-04, FRAMEWORK-09 | Framework entry point describing roles, paths, traceability, prompts, reverse extraction from raw data, and fan-out to implementation repositories. |
| `TEMPLATE-CHANGELOG.md` | blob / `62cf83c19719` | marker / observed-current | full | FRAMEWORK-03 | Records structural changes and scope boundaries of the template repository; it is not a business domain change log. |
| `_roadmap` | tree / `ec886cb0ed6b` | directory / observed-current | metadata-only | FRAMEWORK-11, FRAMEWORK-12, FRAMEWORK-13, FRAMEWORK-14, FRAMEWORK-15, FRAMEWORK-16 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `_roadmap/01-ddd-abstraction.md` | blob / `a1c6a28c7668` | roadmap / proposed-upstream | range:1-130 | FRAMEWORK-12 | Proposes changing prompt/template language first and then breaking directory renames with migration scripts; all are future plans. |
| `_roadmap/02-execution-engine.md` | blob / `70eede4d9432` | roadmap / proposed-upstream | range:1-309 | FRAMEWORK-11 | Proposes a GitHub composite action, gap_detector, profile checks, metrics, PR comments, and later automatic child PRs/auto-merge. |
| `_roadmap/03-scaffolding-automation.md` | blob / `4bf7d43ac0a6` | roadmap / proposed-upstream | range:1-283 | FRAMEWORK-12 | Proposes a tantu init/migrate/check/version CLI, template rendering, version migration, CODEOWNERS, and optional GHE repository creation. |
| `_roadmap/04-ghe-native-integration.md` | blob / `6ece7b0c0553` | roadmap / proposed-upstream | range:1-150 | FRAMEWORK-13 | Proposes GHE governance integration through CODEOWNERS, organization Rulesets, and a Knowledge Base. |
| `_roadmap/05-tiered-profiles.md` | blob / `69d9fb2325f1` | roadmap / proposed-upstream | range:1-179 | FRAMEWORK-12 | Proposes three lightweight/standard/regulated model.yaml/profile tiers, path skeletons, profile checks, and upgrade migration. |
| `_roadmap/06-web-surface.md` | blob / `bbca6e977581` | roadmap / proposed-upstream | range:1-160 | FRAMEWORK-15 | Proposes a Knowledge Base, a web query/review application, and an @tantu Copilot Extension, all future entry points. |
| `_roadmap/07-graph-generator.md` | blob / `23dba48ae928` | roadmap / proposed-upstream | range:1-175 | FRAMEWORK-14 | Proposes parsing nodes and edges from actual artifacts/model.yaml, template rendering, metrics, and CI graph outputs. |
| `_roadmap/08-impact-assessment-trigger.md` | blob / `6f81d0c10868` | roadmap / proposed-upstream | range:1-183 | FRAMEWORK-14 | Proposes PR changes triggering downstream BFS impact comments, structural first and semantic later; there is currently no corresponding script/workflow. |
| `_roadmap/P4-01-reverse-engineering.md` | blob / `1f4a9eec1ddd` | roadmap / proposed-upstream | range:1-265 | FRAMEWORK-16 | Plans extracting model candidates and confidence from transcripts, documents, code, and SQL; the code/Schema adapters are still marked not started. |
| `_roadmap/README.md` | blob / `d3cf542f3145` | roadmap / proposed-upstream | range:1-87 | FRAMEWORK-11 | Roadmap overview listing P1/P2/P3/P4 automation as future priorities; must not be used as evidence of the current implementation. |
| `_templates` | commit / `9cc3338ba0d7` | gitlink / unverified | metadata-only | FRAMEWORK-17 | Pinned gitlink to ddd-subdomain-templates; its commit was not followed this time, so the forms, schemas, and waiver templates cannot be verified. |
| `azure-pipelines.yml` | blob / `0746f2506b89` | pipeline / observed-current | full | FRAMEWORK-05, FRAMEWORK-09 | Azure Pipeline that first runs heading/placeholder validation, then clones BCs by model.yaml.repoUrl, copies features, commits/pushes, and creates PRs. |
| `docs` | tree / `1d1cb2116adf` | directory / observed-current | metadata-only | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `docs/README.md` | blob / `6afafe9a55bb` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Documentation navigation linking roles, DDD/V-model, the three repositories, prompt modes, IDs, model.yaml, and QMS topics. |
| `docs/artifact-graph.html` | blob / `b792834fc49b` | asset / instance-only | full | FRAMEWORK-06 | The interactive traceability graph in the snapshot is embedded demo HTML that depends on the Cytoscape CDN in the browser; it is not evidence from a live matrix. |
| `docs/concepts` | tree / `4fc4f0b007c7` | directory / observed-current | metadata-only | FRAMEWORK-02, FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `docs/concepts/artifacts.md` | blob / `607ec4ecb982` | guide / observed-current | full | FRAMEWORK-02 | Describes the question, authors, users, cardinality, and gap diagnosis for each of REQ/CAP/UC/INV/BR/TS. |
| `docs/concepts/bc-artifacts.md` | blob / `3f9187433721` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-09 | Describes the bottom-of-V SR/US/ABB/VT and the model.yaml bridge, and declares what lies outside this repository's boundary. |
| `docs/concepts/faq.md` | blob / `737cb8c12890` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Explains, by role, the expected benefits of automatic generation, quality checks, traceability, and impact analysis; mostly process promises. |
| `docs/concepts/overview.md` | blob / `c9930da41570` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Introduces the positioning and non-goals of DDD, the V-model, ISO 14971, and AI sparring/autonomous modes. |
| `docs/concepts/sparring-vs-autonomous.md` | blob / `19ae4a0ea5da` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-03 | Splits prompts into human-decided sparring prompts and autonomous prompts that read confirmed inputs; this is not access control. |
| `docs/concepts/three-repos.md` | blob / `250cab631213` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-09 | Describes the inputs and outputs of the three repositories DomainModeling, BC implementation, and RiskManagement, and the model.yaml bridge. |
| `docs/concepts/v-model.md` | blob / `69d3dc60bf3f` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Defines the top/bottom of the V, the risk branch, REQ→CAP→UC→INV→TS, and coverage levels. |
| `docs/getting-started` | tree / `5fba065cd1f9` | directory / observed-current | metadata-only | FRAMEWORK-01, FRAMEWORK-09 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `docs/getting-started/setup.md` | blob / `54e18bc1ea06` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-09 | Gives clone, submodule, role entry point, BC/Risk configuration, and manual VS Code agent setup steps. |
| `docs/reference` | tree / `803884b98f7e` | directory / observed-current | metadata-only | FRAMEWORK-02, FRAMEWORK-03, FRAMEWORK-09 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `docs/reference/artifact-ids.md` | blob / `d1b399002d07` | guide / observed-current | full | FRAMEWORK-02 | Specifies artifact IDs, file names, sequence numbers, statuses, and the upstream/downstream traceability format. |
| `docs/reference/model-yaml.md` | blob / `f4ebc80e4114` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-09 | Gives a BC model.yaml example, summary/release/risk fields, the dual commit, and consistency rules; there is no instance in the same repository. |
| `docs/reference/prompts.md` | blob / `2b4c48abe921` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-17 | Lists the prompt modes of the three repositories, the artifacts they read/write, and human gates; the bodies are in the gitlink that was not read. |
| `docs/reference/qms-traceability.md` | blob / `88f994bdeb34` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03, FRAMEWORK-09 | Describes the working matrix/QMS matrix, the IEC 62304/ISO 14971 mapping, and release-blocking conditions. |
| `docs/roles` | tree / `afc6bbd2c0c4` | directory / observed-current | metadata-only | FRAMEWORK-01, FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `docs/roles/README.md` | blob / `6a722d3d3a5c` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-03 | Role index and decision-rights table separating PM, architecture, development, and risk responsibilities. |
| `docs/roles/architect.md` | blob / `80393b161cb3` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Architecture guide covering the domain model, SWAS, ABB, ADR, review, and release checks. |
| `docs/roles/developer.md` | blob / `91c8500a9978` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-09 | Developer guide defining BC repository prerequisites, SR/US/ABB/VT derivation, and the model.yaml dual commit. |
| `docs/roles/domain-modeler.md` | blob / `127349033dd6` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02 | Domain modeling guide emphasizing sparring, terminology, invariant responsibility, and the impact of structural changes. |
| `docs/roles/requirements-engineer.md` | blob / `bc18b0496b8f` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-03 | Product guide defining the seven REQ quality checks, QAS, the matrix, and intended-use amendment. |
| `docs/roles/risk-manager.md` | blob / `b879089dd2f5` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Risk guide defining the six-step risk lifecycle, the RC/REQ/INV/VT chain, and residual-risk prerequisites. |
| `domain-model` | tree / `3508d38b153a` | directory / observed-current | metadata-only | FRAMEWORK-02, FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `domain-model/README.md` | blob / `66c1188f8896` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Domain directory declaring domain-model as the source of truth and listing backlog/glossary/subdomains/decisions and the traceability chain. |
| `domain-model/backlog.md` | blob / `c385513ffa65` | marker / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Open questions include ADR-0002/3/4/5 and governance extension questions, reflecting open facts and accountable owners. |
| `domain-model/decisions` | tree / `da3679786387` | directory / observed-current | metadata-only | FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `domain-model/decisions/ADR-0001-v-model-repo-split.md` | blob / `b9a45b1ae713` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-09 | Accepts the two-repository V-model split and the read-only domain submodule in the implementation repo; central publication is still incomplete. |
| `domain-model/decisions/ADR-0002-swas-placement.md` | blob / `627dc4ee2915` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-09 | Accepts placing the SWAS in the subdomain DomainModeling repository, driven by model.yaml abbSummary, and declares the PDF pipeline. |
| `domain-model/decisions/ADR-0003-model-yaml-abb-bridge.md` | blob / `4b3b429db3df` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-09 | Accepts model.yaml abbSummary as the BC→SWAS bridge and specifies updates and the dual commit; the example and reference fields are not fully consistent. |
| `domain-model/decisions/ADR-0004-prompts-governance.md` | blob / `89abaf6f4ba3` | guide / observed-current | full | FRAMEWORK-03, FRAMEWORK-17 | Accepts central prompts/instructions/templates submodules but defers implementation, and proposes a CODEOWNERS transition. |
| `domain-model/decisions/ADR-0005-workflow-prompts-over-role-agents.md` | blob / `9ef944e79877` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-03 | Accepts workflow prompts over role agents, requiring human gates, explicit sources, and a queryable bridge. |
| `domain-model/decisions/README.md` | blob / `d439749adecd` | guide / observed-current | full | FRAMEWORK-03 | Registers the central wiki publication status of the five ADRs and the drafting/publication/back-linking process. |
| `domain-model/domain-definition.md` | blob / `05a3d1834e70` | guide / observed-current | full | FRAMEWORK-02 | Provides the structure for multiple subdomain definitions, classification, responsibilities, the context map, and open questions. |
| `domain-model/glossary` | tree / `cac24f5e07c8` | directory / observed-current | metadata-only | FRAMEWORK-02, FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `domain-model/glossary/business-rules.md` | blob / `dd627a163d5c` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Provides a blank structure for cross-subdomain BRs, the invariant index, and the change log. |
| `domain-model/glossary/ubiquitous-language.md` | blob / `3464bd7bed48` | guide / observed-current | full | FRAMEWORK-02 | Provides a blank structure for shared terms, ambiguous terms, deprecated terms, and naming conventions. |
| `domain-model/subdomains` | tree / `40c58f8f09a8` | directory / observed-current | metadata-only | FRAMEWORK-01, FRAMEWORK-02 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `domain-model/subdomains/README.md` | blob / `8748b92a8f80` | guide / observed-current | full | FRAMEWORK-01, FRAMEWORK-02, FRAMEWORK-17 | States that subdomains should be created by Copilot from templates and that the directory index should be maintained. |
| `glossary-digital-backbone.md` | blob / `68a4cee10db4` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Registers organization-level Digital Backbone terms, roles, runtime, governance meetings, and open questions. |
| `platform-model.md` | blob / `0df1c5a82ab3` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Uses Mermaid/tables to define relationships among Offering/BC, requirements, domain, verification, QMS, and implementation repositories. |
| `requirements` | tree / `ae7d9609d555` | directory / observed-current | metadata-only | FRAMEWORK-02, FRAMEWORK-03 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `requirements/README.md` | blob / `49a25ad0ac35` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Requires writing REQs with requirements-capture and adding domain impact, matrix, and change log entries. |
| `requirements/_governance-catalog.md` | blob / `63f970ea9891` | guide / observed-current | full | FRAMEWORK-03 | Registers the GOV-001..006 structure for SBOM, dependencies, threats, audit, residency, accessibility, and waivers. |
| `requirements/change-log.md` | blob / `cb69dfafb5a0` | marker / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Provides an audit log structure that records subdomain/BC/term/rule changes per REQ. |
| `requirements/utility-tree.md` | blob / `746bd0d788df` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-03 | Provides the structure for business goals, QAS priority/difficulty, architecturally significant items, hard constraints, and open questions. |
| `sample_spec.md` | blob / `61b0d1aa214b` | asset / instance-only | full | FRAMEWORK-04 | Root-level sample patient management specification showing the shape of REQ/UC/invariant/constraint/glossary; it is not a current business fact. |
| `testing` | tree / `ca6e946c152b` | directory / observed-current | metadata-only | FRAMEWORK-02, FRAMEWORK-06 | Directory entry; only the Git tree is registered, and the directory itself is not counted as a file capability. |
| `testing/README.md` | blob / `ddab4dfba9c9` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-06 | Specifies BC/cross-BC scenarios, acceptance tests, feature files, and REQ/UC/INV coverage conditions. |
| `traceability-matrix.md` | blob / `88a91e79d03d` | guide / observed-current | full | FRAMEWORK-02, FRAMEWORK-06 | Provides REQ→CAP→UC→INV→SR→TS/GOV tables, coverage symbols, and gaps still to be filled. |
