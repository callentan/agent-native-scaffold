# Six-repository functional alignment: enhancement specification

**Task8 re-review record (2026-10-16):** The original T8-I1/I2/I3 and the later T8-F1-N1 have all been fixed and passed a scoped re-review; the latest fixed object is `9a3055a`. The results for different objects (the full suite of 395, the 153 affected methods, and the 94 model methods) are kept separately; see the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task8-review).

**Status:** For the scoped local delivery/re-review status of Tasks 1–11 and Task15–18, see each task and its report; there are currently nine methods, twenty-two prompts, and three modes. Task12 has completed the exact file-level candidate, the maker-only copy/verify, the candidate-isolation regression, and the minimum-Python retained+new full suite, and the independent scoped fix-wave re-review has closed the original findings; for the local evidence, see the [maker-side acceptance record](../../verification/ddd-alignment.md) and the [Task12 handoff](../../logs/2026-10-19-task12-candidate.md). That candidate is not a release and not full parity. The user's current goal is a ready-to-use local scaffold, and a real showcase exercise is not required as a precondition for this local readiness; a fresh exact manifest candidate has been copied/verified separately, see the [Task13/ready-scope handoff](../../logs/2026-10-19-task13-flagsmith-poc.md). Task13 selected a Flagsmith/OpenFeature technical POC and copied it into the isolated `poc/flagsmith`; the unit/build/controlled-browser sub-scopes passed, but the POC is not a real application integrated with a business system, and evidence for live Flagsmith, code generation/maintenance, and actual participants/client/platform is still insufficient; see the [same handoff](../../logs/2026-10-19-task13-flagsmith-poc.md). Task14 must not claim overall equivalence while the line-by-line matrix and the applicable external gates remain open. Task16 actual audio, Task17 PDF/PPTX binary formats, and Task18 real provider/billing/usage all remain `not-run` or unavailable; human/App/client native discovery, hosted CI/required checks, platform, and release have not been run either. The candidate and the local tests do not inherit the old P3 results and do not close all applicable ENH-01–18 items or overall parity. The detailed scope of the maintenance tools/contracts remains in this specification and the plan; permissions, CI gates, and remotes are not changed automatically.

**Task16 fix1 (scoped re-review completed):** The independent review of `9942e70` raised T16-I1/I2/I3/M1.
This round first obtained RED with real regressions, then fixed complete source units, the shared Markdown context,
envelope/format-coordinate consistency, and the width of tables without a grid; it did not change the formal schema, source guard,
lock, roles, or audio provider. The original 688 results keep their original baseline; read the new check/minimum-version results in the
[fix1 handoff](../../logs/2026-10-15-ddd-alignment.md#task16-fix1).
The original reviewer's scoped re-review confirmed that fix `97d35aa` addressed all four items, with no new related findings;
the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task16-review) keeps the scope and the evidence entry point.
This closes only this review of the offline implementation; ENH-16 and actual audio are still not closed as a whole.

**Task15 fix1 (2026-10-16):** After scoped fixes to the four items from the initial review, an independent re-review confirmed that I1/I2/M1 were addressed;
the comment-continuation gap from the original I3 then moved into fix2. The fix protects metadata deletions already staged before the first onboarding, the exact configuration
bytes as obtained/planned, and the local include/metadata read boundary before Git commands, and rejects a checkout
that occupies `.gitmodules`. I3 was only a local boundary check of the safety interception and did not actually access UNC paths or the network;
the original 579/55 records are kept; see [this round's handoff](../../logs/2026-10-15-ddd-alignment.md#task15-fix1).

**Task15 fix2:** The re-review confirmed I1/I2/M1 as ADDRESSED; only the comment/continuation interaction from the original I3
entered this round. The fix keeps physical comment boundaries; after a safe RED/GREEN it ran only the affected source suite on 3.11:
97 methods, 0 skipped; the full suite of 611/schema/collector was not rerun. The local fix for I3 has completed a scoped re-review,
with no remaining findings for this task; see the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task15-review).

**Task10 round 1 fixes (2026-10-16):** The issues raised by the original review (minimum-version native message parameters, fallback of the selected venv, and partial-write bookkeeping) received narrow fixes confirmed by a scoped re-review; the conditional transitive dependency for `<3.13` that was actually found was also added, without upgrading the original six pins. For the real Windows 3.11/3.13 results and the recovery boundary, see the [fix handoff](../../logs/2026-10-15-ddd-alignment.md#task10-fix1). The old implementation results keep their original baseline and do not close POSIX/hosted CI or ENH-10 as a whole.

**Task10 re-review and round 2 (2026-10-16):** The original I1/I2/M1, the conditional lock, and the later Minor T10-F1-N1 have all been addressed and passed a scoped re-review. The latest fix `0265774` blocks report import after a startup rejection, while output protection for valid environments is kept; for results and boundaries, see the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task10-review). Different runs keep their own objects and are not expanded into conclusions about hosted platforms, business, or identity authentication.

The original P1/P2/P3 implementation baseline is `453189135af07f8ba5ab65dd4dd58879b8741c17`, and the planning revision is `f9aab56`. At the user's request, this round started after the README formatting was committed separately as `1a6f594`, with a clean working tree at the start; these two formatting changes are no longer treated as uncommitted. The original 38 P1/P2 files and the [original P3 outstanding items](../plan/roadmap.md#actual-acceptance) remain and are not erased by the new implementation status.

## 1. Scope and reference baselines

Align only with the **existing functionality** of the six repositories below, without copying their source code, business content, branding, or six-repository deployment shape. This round obtained and checked these full commits through read-only Git; for the per-file classification and capability evidence, see the [six-repository capability matrix](../research/ddd-capability-matrix.md). The earlier [historical source register](../research/source-register.md) is kept as historical observations.

| Reference repository | Pinned commit | Responsibilities of interest |
|---|---|---|
| ddd-bc | `bac263bea39988214b82cafb48f27e3a2136c534` | BC engineering conventions, configuration, domain inputs, and implementation boundaries |
| ddd-bc-prompts | `08f8219397d6fe6d000312f5956a493b1b28cc84` | SR/US/ABB/VT derivation, code generation, and maintenance workflows |
| ddd-bc-templates | `00705aef6c70f855ef95588b0137cf7f2387efb0` | Implementation-side artifact forms |
| ddd-subdomain | `e115ad4d03ac53359c608ce7d32262a508561496` | Domain engineering, checks, hooks, propagation, and governance records |
| ddd-subdomain-prompts | `1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c` | Interview, modeling, reverse extraction, review, and change activities |
| ddd-subdomain-templates | `59f98e352a150f99290a3855092298dbe11e0615` | Domain structure, model, and validation-scenario forms |

Task 1 must freeze the capability matrix file by file, registering the functionality that already exists in the original repositories separately from the automation newly added by this plan. Using Python throughout is an implementation strategy; it does not prove that export, automatic traceability, or three-way update each has a counterpart script in the original repositories. Historical summaries, how instance repos are used, and upstream roadmaps must not pose as capabilities the six repositories already implement. When reading is restricted, record the specific missing items and stop any equivalence judgment that depends on them; do not guess file contents or follow a new HEAD.

This round's inventory covers 252 Git entries and 195 blobs: 185 files were read in full, 10 roadmap files were read within scope and marked as proposals, and directories/gitlinks were registered as metadata only. The newly adopted scope is what already exists in the sources: QAS/tactical artifacts, SEQ/Gherkin/SWAS, glossary and Published Interface evolution, optional domain-source onboarding, input adapters, diagram/document/presentation export, and the interaction ledger. These are not disguised as already covered by the original plan.

`DM-Subdomain` and `DeviceRegistry-BC` may provide only authorized research leads; they are not the deliverables list or the application base of this enhancement. The Tantu CLI, a general execution engine, automatic approval/merge, a state database, a web platform, and a dedicated tech stack are out of scope for this specification.

<a id="requirements"></a>
## 2. Enhancement acceptance criteria

This maintenance request serves directly as the basis; no product REQ/SR is manufactured in the blank templates. `ENH-*` are the acceptance identifiers of this enhancement.

| ID | Requirement and observable completion condition |
|---|---|
| ENH-01 | Every file in the pinned versions of the six repositories is classified; each existing capability has a source, current gap, target equivalence approach, task, and verification evidence. Roadmaps, duplicate entry points, and instance content are listed separately. No difference that is unchecked or not accepted may be counted as aligned |
| ENH-02 | Artifact identity, scope, source, relationships, content state, task progress, and run results have explicit contracts; the new structure can evolve losslessly from the existing single-context Markdown without moving/overwriting existing materials |
| ENH-03 | Supports subdomain/context, capability, UC, INV, business validation scenarios, and BL open items; rules, sources, relationships, and responsibilities are locatable, identical numbers across contexts are not confused, and unknown facts stay unknown |
| ENH-04 | Interview, modeling, domain review, reverse extraction, and impact analysis can be completed with the shared methods. Reverse extraction carries source locations, evidence confidence, and confirmation state, and does not treat a behavior as an approved business fact just because code exists |
| ENH-05 | Derivation and review of SR, optional US, ABB/ADR, and VT, initial code generation, and modification of existing code each have a separately executable contract; missing inputs, non-empty target conflicts, and tests not run are reported explicitly, without narrowing acceptance or forcing a path through US |
| ENH-06 | BC configuration can locate the identity, contexts, pinned domain inputs, read/write nature, and command registration; `model.yaml` is a derived index with source baselines and does not become a second copy of the domain facts, and wrong paths/versions and hand-edited views are detectable |
| ENH-07 | Artifact checks can be run repeatedly within the repository, covering metadata, required structure, IDs, placeholders, links, and input errors; exit codes, check counts, and object baselines are explicit, and an empty skeleton is not called a passed business acceptance |
| ENH-08 | Inventory VTs from the complete set of delivery acceptance criteria and check each target in reverse, precisely finding omissions, dangling/same-ID-different-owner references, and stale baselines; support impact lists for rule changes, keeping mechanical checks separate from human semantic judgment |
| ENH-09 | Records of tool qualification, human review, and interaction summaries are traceable; content declarations cannot authenticate a reviewer or approve automatically. Only where existing files in the six repositories really contain dedicated domain/risk artifacts are optional corresponding forms added according to the capability matrix, without claiming regulatory compliance |
| ENH-10 | Optional Git hooks and CI call the same checker; an explicit baseline that cannot be resolved must fail, without falling back to main/master/the index to manufacture an empty check. Disabling a hook does not mean bypassing server-side required checks, which need actual platform configuration |
| ENH-11 | Template version updates support a three-way comparison of old baseline/project local/new candidate, and multi-target propagation has explicit registration, diff, and conflict results; by default only proposals are produced, only an authorized native Git/platform process may write or create a PR, and business facts are not overwritten |
| ENH-12 | The implementation summary links the BC, domain sources, SR/US/ABB/VT, real code/test identifiers, and result baselines; the report does not certify a pass by itself or write back to read-only domain sources |
| ENH-13 | A clean candidate is distributed by file manifest. The template body, optional tools, and their dependencies and tests are described separately; research, plans, maker logs, internal sources, exercise data, and Git history do not enter the candidate |
| ENH-14 | Fixed positive/negative document examples, a real App workflow, new-session takeover, and authorized code generation/propagation exercises all have clearly scoped results; items not run stay unverified, and the original P3 manual and client gaps are not inherited as passed |
| ENH-15 | Optional domain-source onboarding supports an explicit repository/version/actual path, read-only/local ownership, and placeholder-conflict checks; Python provides a preflight and explicit execution, and does not create submodules, commit, or push by default |
| ENH-16 | Local Markdown/plain text, explicit transcript formats, and DOCX, plus separately approved audio input, can produce candidate artifacts with source locations/confidence; document locations keep at least the paragraph/table or an equivalent source position, support source association and uncertainty, and are not approved automatically. When an optional parser/dependency is missing, report it explicitly as unavailable, without sending materials or faking a transcript; while DOCX has not actually been run this item stays `not-run`, and audio services still need separate authorization |
| ENH-17 | Source-traceable relationship diagrams, SEQ, SWAS, and parameterized presentation output via `render_presentation(inputs, format)` can be generated from specified inputs; the presentation is a required equivalent capability and must not be excluded through an allowlist; no data shows empty, and no demo data is injected; local output is explicit and contains no personal paths, and PDF/PPTX dependencies and actual format checks still run only as authorized |
| ENH-18 | AI interaction and usage summaries can be recorded by explicit scope/tool/time and produce verifiable statistics; without real usage, no billing/qualification result is invented, complete sensitive conversations are not stored, and the ledger does not replace approval or run evidence |

## 3. Design conventions

### 3.1 Single source of truth and structure

Keep the existing top-level material directories; lightweight projects can keep using `domain-model/README.md`. When multiple domains are genuinely needed, organize formal materials as `domain-model/subdomains/<slug>/contexts/<slug>/`; do not prefill real SD/CTX, and do not require business boundaries to equal services or code layers.

The full-functionality path also provides optional forms for QAS, context map, Published Interface, aggregate, entity, value object, factory, domain service, policy, domain event, integration partner, Intended Use/risk references, and architecture specification/SEQ. Choose them per current task; no maintenance item is forced to complete the full set of tactical or regulatory artifacts. Dedicated fields record only sources and decisions given by the accountable owner and do not declare compliance.

For domain/software scenarios, the `.feature` file keeps the executable Gherkin body, while Markdown keeps the targets, metadata, criteria, and file references, so the scenario body is never duplicated; without a runner/application, the plan stays not-run. Bridge fields such as sequence, QAS, risk, and release are expressed as artifact/evidence references, and business content is not moved into `model.yaml`.

The artifact's Markdown body owns business meaning, rules, and acceptance. A formal artifact's YAML frontmatter owns machine identity, scope, declared state, and upstream/target relationships; status/relationship fields in the original forms that duplicate this metadata are changed into references or removed. A VT body keeps each criterion under its `criterionAnchor`, and the target records in frontmatter only locate the corresponding source and criterion. Reverse indexes are derived from these relationships; no separate mapping is hand-written.

The unified machine identity is `scope/id#anchor`; `scope` consists of the project and the context, for example `sample/CTX-001/SR-001#sr-001-ac-02` in the exercise. A duplicate ID within the same scope is an error; artifacts with the same number in different scopes are allowed. Existing REQ/SR acceptance IDs and anchors are kept; renumbering is not used to hide history.

The declared content state is `draft | confirmed | retired`, and task progress remains `todo | in-progress | blocked | review-ready | done`. The actual result is `not-run | pass | fail | skipped`, and current applicability is recorded independently. A confirmation record must point to a named source and the confirmed baseline; the presence of a declaration or link does not mean a human identity has been verified.

### 3.2 BC configuration and derived model

`bc-config.yaml` is **optional data configuration**, not a project execution manifest. Its fields are `schemaVersion`, `projectId`, `boundedContexts`, `domainSources`, and a reference to the development registration. Each domain source states its `kind`, `root`, repository-relative `path`, pinned `baseline`, and `readOnly`; the mount root and the in-repository path are never combined by guesswork, and no credentials are stored or development commands copied.

`model.yaml` stores only `schemaVersion`, `scope`, source object baselines, artifact locations/IDs/relationships, and implementation-summary references. Body content is not copied into it; content declarations still live in Markdown, and results still live in VTs/real reports. The exporter uses a deterministic order, keeps complete original IDs, and does not access the network or update external repositories while reading.

After execution resumed on 2026-10-15, the user explicitly chose the optional `model-sources.yaml` to register view sources. Task7 adopts the [standalone source contract](../../.github/contracts/README.md#model-sources) with `schemaVersion: 1` and `scopes: {project/context: {view: [{path, baseline}]}}`, together with its [blank form](../../_templates/config/model-sources.yaml). It reads only actual files inside the root, identified by raw SHA256 or an exact local Git commit/blob, and rejects network access, parent-directory traversal, duplicate keys, conflicting baselines, and self-references to the derived model; it copies no body content, results, or approval states and grants no execution/write-back permission. This maker repository has no formal project manifest.

The concrete shapes of existing Markdown sections and YAML/JSON source fields are maintained in the contract notes and do not change the nine-view output schema below. The complete main inventory is checked first, and the selected scope is not inferred from directories; direct Markdown may merge multiple explicit sources, while summary sources keep only the actual navigation of the source field. A missing manifest, a missing scope registration, a missing view, and invalid configuration are each handled separately. For the actual APIs/CLI, source identity, and drift codes, see the [tool notes](../../.github/utilities/README.md#model-export); tests/self-review are not independent re-review or business verification.

The Task7 round 1 fixes follow the original semantics of the table below to complete: the missing-source judgment for QAS/utility-tree, output protection for all parsed nested declarations, attribution of real Mermaid fences, VT child run blocks/per-criterion results, and the required base for the impact API. Run records are not moved ahead of their parent heading, fields are not stitched together across runs, and counts are not inferred; the original four schemas, 32 kinds, and nine views are unchanged. Implementation and regression tests do not by themselves close the scoped re-review.

#### 3.2.1 View bridge contract

The nine views are stored only in the derived model; the implementation report keeps the standalone v1 `entries[].execution/applicability` and has no root-level execution/views. Once a report is separately and explicitly selected as a verification source, the model stores only report references that passed baseline/rebuildability checks, without copying run entries. The fixed keys of the cross-repository `views` map are
`requirements`, `stories`, `architecture`, `sequences`, `verification`,
`quality`, `governance`, `risk`, and `release`. Every view must have the following shape; a view
stores only references and locatable gaps, without copying domain content, approval declarations, or actual results:

```yaml
views:
  <view-key>:
    state: available | partial | unverified
    artifactRefs:
      - scope/id#anchor
    evidenceRefs:
      - reference: repo-relative/path#anchor
        baseline: source-object-or-report-baseline-pointer
    gaps:
      - specific reason string
```

`state` expresses only the readability and completeness of the sources: `available` means the sources the view needs are readable and
complete, `partial` means the sources are readable but fields/entries are missing, and `unverified` means an optional source
is missing, a source is unreadable, or the evidence baseline cannot be verified. It is never `passed`, `approved`, or
any actual result. `artifactRefs` uses the unique `scope/id#anchor` canonical key;
`evidenceRefs` must keep both the `reference` and the `baseline` pointer. When an optional source is missing,
the view is still output, with `unverified`, an empty reference set, and specific `gaps` reasons; data must not be faked
and the view must not be omitted. Domain content still belongs to the domain artifacts, and real results still belong to their original owners: the VT/run reports/governance or
risk records.

| View | Source field mapping | Contents of `artifactRefs` | Contents of `evidenceRefs` | Missing/incomplete rule |
|---|---|---|---|---|
| `requirements` | `srSummary.srVersion`, `srSummary.entries[].reqId/srIds/ucId/status/notes` | `scope/id#anchor` of REQ, SR, and UC | SR/REQ source paths and pinned object/report baselines | If `srSummary` is missing, write `unverified` with the gap "`srSummary` source is absent"; if the version or entries are incomplete, write `partial` and state the missing fields |
| `stories` | `storySummary.storyVersion`, `storySummary.entries[].srId/usIds/status` | Canonical keys of SR and US | Story source paths and object/report baselines | If `storySummary` is missing, write `unverified` and state "SR→US bridge is unavailable"; if an entry lacks a status, write `partial` |
| `architecture` | `abbSummary.abbVersion/language/framework/blocks/integrations`, including `adrRef` | Canonical keys of ABB, ADR, and integration partners | ABB/ADR/interface source paths and version or Git baselines | If the ABB or ADR source is missing, write `unverified` and state which kind is missing; if only some blocks are read, write `partial` |
| `sequences` | `sequenceSummary.seqVersion`, `sequenceSummary.entries[].seqId/ucId/title/hasAsync/externalPartners/status` | Canonical keys of SEQ, UC, ABB, and partners | SEQ files and source object/generated report baselines | If `sequenceSummary` is missing, write `unverified` and state that the runtime sequence source is unavailable; if the version/participants are incomplete, write `partial` |
| `verification` | `verificationSummary.vtVersion/lastRunDate`, `verificationSummary.entries[].usId/vtIds/result/automatedCount/manualCount/notes` | Canonical keys of US, VT, and REQ/SR | VT files, run reports, and their object/requirement baselines | If the verification source is missing, write `unverified` and state that the evidence source is unavailable; `result` only references the original record and is not rewritten by the view |
| `quality` | QAS/utility-tree artifacts and their `testScenarios` references; the source `model.yaml` has no separately invented `qasSummary` field | Canonical keys of QAS, REQ, and TS/feature | QAS/utility-tree/scenario files and version or report baselines | If QAS/utility-tree is missing, write `unverified` with a gap that specifically states the quality source is missing; if only some scenarios are read, write `partial` |
| `governance` | `governanceSummary.govVersion`, `governanceSummary.entries[].govId/status/ref/notes` | Canonical keys of GOV, REQ, and waivers | Governance catalog, REQ/waiver, and baseline pointers | If the governance source is missing, write `unverified` and state that the governance source is unavailable; `status` is not converted into an approval conclusion |
| `risk` | `riskSummary.riskVersion`, `riskSummary.entries[].riskId/title/preMitigationLevel/rcIds/residualRiskLevel/reqIds/vtCoverage/status` | Canonical keys of RISK, RC, REQ, and VT | Risk/control sources, VT reports, and their respective baselines | If the risk source is missing, write `unverified` and state that the risk source is unavailable; if fields are incomplete, write `partial` and do not derive residual risk |
| `release` | `releaseStatus.lifecycle/safetyClass/currentVersion/lastReleaseDate/nextPlannedRelease/changeControlRef` | Canonical keys of release/change-control/related BCs | Release/change-control records and version/object baselines | If the release record is missing, write `unverified` and state that the release source is unavailable; if lifecycle fields are empty, write `partial`, which does not mean released |

The required inputs are the current `root`, a supported schema version, the selected `scope`, the formal artifacts of that scope, and their explicit object baselines. A nonexistent/unreadable input, invalid YAML/schema, an out-of-bounds path, duplicate keys/IDs, unregistered hand edits to derived files, or a baseline mismatch is an input error. These errors must not be downgraded to "optional source missing".

The external/summary sources of all nine `views` are optional view inputs: when one does not exist, is unreadable, has a summary format that does not meet the view's convention, or has a baseline that cannot be verified, always output that view with `unverified`, an empty reference set, and a specific reason; do not omit the view or abort the other checkable views. When a valid source was read but only some entries are missing, the state is `partial`; keep the references already checked and list each gap. If the main root/artifacts themselves cannot establish a trustworthy baseline, still fail as described in the previous paragraph, instead of interpreting the whole input as nine empty views.

Export and checking are separate: by default only checking runs, and files are written only on explicit export to an allowed local target. The required-input errors above must fail; missing optional-view items are output according to the fixed `unverified/partial` rules, without swallowing errors or automatically "fixing" authoritative files.

<a id="method-tool-boundaries"></a>
### 3.3 Method and tool boundaries

Enhance the original six shared methods without duplicating a manual version of the process. Add three activity methods: `reverse-engineer-domain`, `generate-code`, and `update-template`; the three existing agents connect only to the applicable methods. Glossary sync/Published Interface, knowledge crunching, incoming ADRs, Intended Use changes, read-only query, backlog/traceability, and SWAS/SEQ each have explicit input/output entry points and reuse these nine methods by responsibility; no new role or process engine is created for each prompt.

The tools live in `.github/utilities/` and by default perform local reading/checking/export/diff proposals. Input parsing, formal artifact checks, coverage/impact, model views, implementation summaries, local hook onboarding, [read-only update proposals](../template-updates.md), and [local source onboarding](../domain-sources.md) have completed this round's scoped re-review. An explicit apply only maintains the source list of a selected BC, or, with separate index consent, creates an exact local submodule; it does not write back to sources or make network requests. Task16's [offline source candidates/scoring](../source-extraction.md) has completed this round's scoped re-review, with no actual audio adapter; Task17's [source-driven local export](../document-exports.md) and its fix1 have completed scoped re-review; Task18's explicit CSV ledger and its fix1/fix2 have completed scoped re-review, all four original Important items have been addressed, and there are no new issues. Task18 targeted 30/30, minimum Python 3.11.15 817/817; the reviewer did not rerun them, relying on the author's final receipts and the parent session's hash verification of 47 inputs. One intermediate two-test receipt had a count/raw-output inconsistency; the final basis remains the later 30/30 and 817/817 receipts. The Minor `summarize_usage(lock_timeout=...)` item is deferred as a compatibility comment on an unreleased API. Real billing/vendor data, PDF/PPTX, and actual binary-format gates have not been run. Task6's base only adds an exact historical comparison; the verification target is still the complete current working files; for the actual discovery/count/JSON boundaries, see the [tool contract](../../.github/utilities/README.md#artifact-checker). Task10's [private index snapshot adapter](../../.github/utilities/README.md#native-hooks) reuses these rules and did not turn the original working-tree API into a staged check. There is no globally installed package, unified skeleton command, run loop, daemon, or state database. Python 3.11+; standard-library `unittest`; YAML uses `PyYAML==6.0.2`, and JSON Schema uses `jsonschema==4.23.0`. Task 2 first created the manifest, then actually restored and locked the transitive dependencies in the project `.venv`; Task10 added the actually checked minimum-version conditional items, without installing global, media, or cloud packages.

The repeatable logic for checking, export, report collection, update comparison, and hook handling is written uniformly in Python; local runs and CI call the same scripts directly, no mandatory `.ps1` wrapper layer is shipped, and no extra PowerShell 7 runtime is required. Use `pathlib.Path`, argument lists, and an explicit cwd; invoke subprocesses with `shell=False`, and keep the actual output and exit code on failure. PowerShell can be the user's current Windows terminal, but it no longer carries a separate set of maintenance logic.

Git hook entry points use Python, and CI keeps native YAML to declare triggers, environments, and Python invocations. Add the thinnest launch adapter only when the host truly requires it, without duplicating check/update logic; before declaring support, verify the interpreter, paths containing spaces, staged content, and failure propagation in an actual commit trial with Git for Windows. Markdown, prompts, and skills still carry the methods and the activities that require judgment; they are not rewritten as Python execution flows just because the script language is unified.

The maintainers' tool-regression workflow is separate from the downstream material-check workflow. The former runs the tools tests, which are not distributed; the latter calls only the tools/contracts inside the candidate and the project artifacts, and must not reference the excluded maker tests, research, or exercise files. The template-propagation workflow also belongs to the maintainer side and is not copied to every business project by default.

Dependencies for source adapters, audio transcription, PDF/PPTX, and the like are listed separately as optional and are not added to the core environment that every user must install. Local text/transcripts, deterministic diagrams, and candidate reports come first; external services, SDKs, renderers, and data sending are configured only after confirmation in the corresponding task. The management PPT content hard-coded in the original repositories is not copied; only a parameterized output capability of the same kind is provided. A missing dependency returns an explicit input/environment error, without switching to an unapproved online service.

### 3.4 Checks and side effects

Checker exit codes: `0` means this documentation-tool check found nothing, `1` means documentation/traceability violations were found, and `2` means the input, configuration, version, or baseline is unreadable. The output includes the actual check count, the exclusions, and the object baseline; with no formal artifacts it reports `empty`, and even with exit 0 it does not call the requirements or the application passed.

`CheckReport.status` is `clean | invalid | input-error | empty`, and a `Finding`'s code is kept separate from its path/line/target. The script layer catches only defined input errors and maps them to exit 2; it never uses a broad exception catch to return a success report. Neither `clean` nor `empty` means business acceptance passed.

Only these are checked: format, declared relationships, locatability, baselines, and the agreed mechanical conditions. The checker cannot infer all business semantics, authenticate expert approval, or prove software execution. A rule-impact report lists candidate dependencies and reasons; the final semantic judgment is still made through the shared methods and by the accountable owner.

Every modification of existing files, hook installation, CI required check, cross-repository write, PR, release, and permission change is authorized separately. Propagation defaults to proposal mode; configuring `apply` does not mean authorization has been granted. Without review or credentials, a clean diff proposal can be delivered, but completed remote propagation must not be recorded.

### 3.5 Implementation interfaces (the tests in the tasks use these names)

| Module and interface | Input and output contract |
|---|---|
| `artifact_io.parse_artifact(path, root)` | Reads a local formal Markdown file and returns an `Artifact` with `key`, `kind`, `scope`, `content_state`, `upstream`, `targets`, `acceptance_ids`, and the original file location. Invalid YAML/path/version raises `ArtifactInputError` instead of returning an empty object |
| `check_artifacts.run_check(root, base_sha=None)` | With `base_sha=None`, runs a full scan; when given, must read that exact Git object and the target snapshot. Returns a `CheckReport`: `status`, `findings`, `checked_count`, `baseline`, `excluded` |
| `check_traceability.trace_report(root, delivery_ids)` | Checks targets and criteria against an explicit, complete acceptance list and returns a `CheckReport`; each `Finding` has `code`, `path`, `line`, `owner`, `target`, `message` |
| `export_model.export_view(root, scope)` | Returns a JSON-serializable dictionary including the agreed `views` map, without writing files; source hashes and artifact relationships are sorted deterministically. Script-layer checks/explicit writes are handled separately |
| `export_model.check_model(root, scope, model_path)` | Validates and recomputes an explicit local model and returns a `CheckReport`; source-identity changes and hand-edited views are reported separately and are not fixed automatically |
| `check_traceability.impact_report(root, base_sha, task_ids=())` | Canonical transitive-dependency candidates between an exact commit and the current snapshot; keeps old and new identities, source locations, and reasons, and is not a semantic approval |
| `collect_implementation_report.build_report(root, object_sha, evidence_files, *, scope=None)` | Inventories the complete BC acceptance from an exact local commit and reads explicit existing VT files/owned runs and raw reports; a single BC keeps the three-argument API, and multiple BCs require choosing a scope. Missing evidence is per-target not-run, and conflicts/baseline errors fail; it does not run the application, copy a result ledger, or write back to sources |
| `plan_template_update.plan_update(base, local, candidate)` | Returns an `UpdatePlan` containing `changes`, `conflicts`, and `preserved`; none of the three directories is written. Modifications and deletions are only proposed, and a missing old baseline is an error |
| `setup_domain_source.inspect_domain_source(root, source_config)` | Checks the exact local root/relative path/pinned baseline against the original BC source fields and returns ready/conflict/unavailable, the actual target, and the proposed operation; always read-only, with no network, fetch, hooks/filters, or cwd change |
| `setup_domain_source.apply_domain_source(root, source_config, *, operation, config_path, expected, owned=False, target=None, index_consent=False)` | register only maintains the source list of an explicitly existing BC; the optional local submodule additionally needs an exact target and separate index consent, and does not register a BC automatically; drift/owner conflicts stop the operation, partial state is left for manual recovery, and nothing is committed/pushed |
| `extract_source.extract_candidates(source, kind)` | Takes an explicit absolute local file and returns the raw-bytes identity/read count and a candidate list; keeps original lines, turn/time, or bounded DOCX paragraph/table positions. Unknown/corrupt/over-limit input is an explicit error, and no formal facts are written |
| `score_candidates.score_candidates(items)` | Shape/excerpt consistency checks and disclosed-factor scoring for a fixed candidate list; deep-copies and keeps duplicate/contradicting sources; does not authenticate sources or make acceptance decisions |
| `transcribe_audio.transcribe_audio(source, *, service=None, model=None, data_scope=None, operation=None, output=None, authorized=False)` | Currently refuses with an authorization/missing-item/adapter-unavailable result; there is no actual call path, environment-key discovery, data sending, or fake transcript, and real audio acceptance remains not-run |

`Artifact`, `Finding`, `CheckReport`, and `UpdatePlan` are narrow-purpose dataclasses defined in their respective modules; no general domain/execution framework is built. Test helper functions are maintained only inside the tools tests.

The frontmatter of a new formal artifact requires `schemaVersion`, `id`, `kind`, `scope`, and `contentState`; `upstream` and `targets` default to empty lists. Each target record contains a complete `target`, a `criterionAnchor`, and an optional `testId`; the target is located by the owner's acceptance anchor, and the criterion anchor must exist in the current VT body. Body headings/acceptance anchors are independently searchable targets; the acceptance inventory is not reverse-engineered from ID strings that happen to appear anywhere in the text.

In schema v1, `kind` is a closed set that supports exactly the following 32 values:
`domain-model`, `subdomain`, `bounded-context`, `capability`, `use-case`,
`invariant`, `validation-scenario`, `backlog-item`,
`stakeholder-requirement`, `software-requirement`, `user-story`,
`architecture-building-block`, `architecture-decision`, `verification-test`,
`review-record`, `tool-qualification`, `development-log`,
`quality-attribute-scenario`, `context-map`, `published-interface`,
`aggregate`, `entity`, `value-object`, `factory`, `domain-service`, `policy`,
`domain-event`, `integration-partner`, `intended-use`, `risk-control`,
`architecture-specification`, and `sequence-diagram`. An unknown kind must be reported as an input error;
no general extension mechanism is provided. Rules can remain stable RULE anchors in domain documents, without forcing
a separate rules body. `upstream` is a list of strings holding complete source references; targets are a list of records
with the structure above. `confirmed` content also requires `confirmation` with `by`, `reference`, and
`baseline`; the checker verifies only the declared structure and does not authenticate the identity/authority behind the decision.

## 4. Authorization gates and completion criteria

1. **Capability gate:** After the per-file matrix of the six repositories is checked, items missing from the specification must enter a sourced change; unknown must not be recorded as not needed.
2. **Contract gate:** Tool implementation that depends on the metadata, data schemas, the way existing Markdown is merged in, and the source read/write boundaries starts only after they have been reviewed. Do not write a parser first and then reverse-engineer the document format from it.
3. **Tool gate:** Dependencies may be restored only after the manifest exists; the tool environment is kept separate from the downstream application's development registration, and reading the materials does not require installing Python packages first.
4. **Application acceptance gate:** The actual project, tech stack, location, and execution mode for code generation are confirmed by the user before Task 13 runs. Tools using Python does not mean the downstream application also chooses Python; this round has no authorization to create an exercise application.
5. **Platform gate:** Automatic propagation, hook installation, remote PRs, CI required checks, and releases are authorized per specific operation; without authorization the corresponding result is not run, and the ENH-10/11/14 standard is not lowered because of it.

"Six-repository functional equivalence" may be claimed only when every existing-capability row of ENH-01 has completion evidence or an explicit alternative accepted by the accountable owner, and all applicable items of ENH-02 to ENH-18 have passed. Original-format compatibility, application verification in any language, regulatory compliance, and support for all Agents are not part of that claim. External ADR/risk instances and run combinations of different consuming gitlink versions are registered only as dependencies; the six-repository source inventory is not used to claim they are verified.

For the implementation order, file responsibilities, and per-task checks, see the [enhancement plan](../plan/2026-10-14-ddd-functional-alignment.md).
