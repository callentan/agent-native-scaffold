# Repo Template First Release: Implementation and Acceptance

**Updated: 2026-10-14. P1/P2 have been built locally; P3 has completed the local document exercise, core integration/methods/roles in the real App, and Git takeover, while entry-point matching, the human comparison, and release confirmation remain outstanding. See the [actual acceptance record](#actual-acceptance) for per-item scope; P3 is not declared passed as a whole.** The P0 decisions were completed on 2026-10-13; the earlier development milestones for the CLI, coordinator, state store, and platform adapters are no longer followed.

## 1. First-release delivery goal

Deliver a development repo with a predefined skeleton that can be copied and used directly, containing project-material templates and Agent capability files. It is meant primarily for GitHub Copilot App; other Agents that can read and write the repository have a clear generic integration path. Users create projects of any type inside `src/` themselves; the skeleton presets no application, tech stack, or dependencies.

Directory names follow DDD and the reference projects' examples: `domain-model`, `stakeholder-requirements`, `software-requirements`, `user-stories`, `architecture`, `verification`, with forms gathered in `_templates`. Methodologically, the skeleton explicitly uses lightweight DDD to express the business model and boundaries, the V-model to organize traceability from requirements to verification, and templates/skills/prompts to unify the human and Agent workflow; it does not merely borrow the names, nor does it inherit the full methods, reference source code, or multi-repository dependencies.

Acceptance focuses on "with the skeleton in hand, one can find the project material, express the model and boundaries, check requirement-to-verification relationships and change impact, and leave records that both humans and Agents can take over", not on whether an executor can run unattended or whether some business application runs. The template needs no extra skeleton software package, service, personal skills, or access to the reference repositories.

| Included in the first release | Not included |
|---|---|
| README, AGENTS, and filling guides and forms for domain/REQ/SR/US/ABB/VT/logs/ADR | Custom CLI, generators, execution loop, state database |
| Conventions for lightweight domain modeling, requirement-to-verification mapping, coverage gaps, and result applicability | Mandatory tactical DDD patterns, a full V-model artifact suite, or a traceability database |
| Copilot repository-wide and path-specific instructions | A home-built approval system, trusted publisher, or permission-isolation layer |
| A small number of practical custom agents, skills, and prompt files | Auto-orchestrated role teams, task queues, or a web platform |
| Real template usage notes, handoff conventions, and compatibility records | A promise that every client's native features behave identically |
| Document-only exercises in a clean copy covering modeling, traceability, rule changes, and human/Agent takeover | Synthetic applications, throwaway coding projects, business-project integration, or a fixed tech stack |
| Template source version, update notes, normal diff-based merging | Automatic overwriting upgrades and cross-repository sync |

A tech-stack-agnostic template should be directly usable for requirements, planning, and records; having no tech stack selected is a valid initial state and does not block skeleton delivery. Coding, building, and testing run with the project's native tools once the user later creates a specific project; they are not part of the first-release skeleton's application-acceptance commitment.

## 2. Implementation sequence

| Phase | Deliverables | Prerequisites | Current status |
|---|---|---|---|
| P0: Settle the minimum content | File responsibilities, App as the first test, `src` boundary, lightweight modeling/traceability and shared methods, setup inputs, and distribution boundary | Template shape and reference-naming direction confirmed | Decisions completed and reinforced |
| P1: Project-material templates | The defined project-material skeleton and seven form types, including domain-modeling guidance, acceptance reference/coverage fields, and human navigation; other files per the blueprint | P0 | Built locally, `52735a0` |
| P2: Agent capability files | The defined instructions, 3 agents, 6 skills, 5 optional prompts; connect the model, traceability, impact analysis, and the shared human/Agent entry points | P1 project-material skeleton ready | Built locally, `4856c47` |
| P3: Skeleton use and release preparation | Cold start, document semantic and fault scenarios, change impact, human/Agent paths and handoff; assemble a clean release candidate | P1, P2, and GitHub Copilot App available | In progress; local and App core scenarios done, remaining entry-point, human, and release items outstanding |

See the [P0 decision record](decisions-and-risks.md) for the decision basis and the items held until release. No separate release package is built per file; first complete the skeleton document tasks with one reviewable set of content, then revise the rules based on issues found in use.

## 3. Phase exit criteria

### P0: Scope small and concrete enough (decisions completed)

- [x] Separate the formal template from research material: distribute by an explicit file list, without research, maker records, or Git history; license and release permissions are confirmed separately.
- [x] Fix the first set of documents and capabilities; file responsibilities and the skill/agent/prompt mapping are in the blueprint, with no runtime layer or tech-stack packs added.
- [x] Keep the origin of directory names and distinguish reference naming from single-repo organization; the historical `src/tests/` path no longer becomes a pre-created directory.
- [x] Choose GitHub Copilot App as the first test and record other clients separately; prompt files are not a required App entry point.
- [x] As the user requested, replace the synthetic-application exercise with skeleton document tasks; choose no tech stack and create no throwaway business project.
- [x] Define the required inputs for browsing, filling in project material, coding, and releasing; the tech stack and commands may stay not configured at first use.
- [x] List lightweight DDD, minimal traceability, change impact, and the shared human method as content requirements, keeping the defined directories and file count.
- [x] Define the fixed inputs, coverage gaps, dangling references, rule change, and result judgment for the document-only semantic exercise, without treating document checks as application verification.

These check marks mean only that the P0 decisions are complete; P1/P2 build records and P3 actual results are registered separately, and passing acceptance is not inferred from the decision check marks.

### P1: Project-material templates are directly usable

- README clearly separates first-time setup, day-to-day development, and taking over a task, and gives humans directly usable navigation to activities, project material, and forms.
- `domain-model/README.md` provides filling guidance for shared terms, concept relationships, business rules, context responsibilities and interactions, and fact sources; no business model is prefilled initially.
- REQ, SR, US, ABB, VT, and logs have non-overlapping responsibilities; forms are kept separate from formal artifacts, and filling hints are not mistaken for confirmed facts.
- REQ has business acceptance and model references, SR has upstream basis and software acceptance, and VT has fields for verification layer, per-item targets, expectations, result baselines, and applicability; US does not become a mandatory traceability layer.
- The verification entry point explains how to check coverage from the delivery's acceptance-criteria list, trace VT targets back, and record gaps; indexes do not copy a second set of requirement text or result statuses.
- The product description and functional specification of a PRD have clear locations, with no parallel set of generic directories holding the same content; maintenance tasks need not be forced into user stories.
- Verification documents are separate from actual test code, and development logs only reference results instead of maintaining another copy of acceptance facts.
- `src/` contains only usage notes, with no preset code, dependencies, or `src/tests/`; downstream users can create projects of any type.
- When no tech stack is selected, it is clearly marked as not configured, with no fake build or fake test success; later, real commands and working directories are recorded per actual subproject.
- The generic entry point can locate goals, specifications, tasks, development commands, and related logs.
- Entry points link only to delivered files; P2 adds the capability-file links later, and files not yet created are not treated as usable entry points.
- No extra manifest, state file, or global tool installation is needed to read the skeleton and start using it.

### P2: Capability files are connected

- Directories, names, and required metadata of Copilot native files follow the target client's conventions.
- A custom agent defines only a working mode; a skill holds the method text; a prompt supplies the inputs for one run; the workflow is not copied three times.
- Skills reference the forms in `_templates` and state the formal output directory, without depending on the author's local paths, personal skills, or hidden chat memory.
- README and AGENTS point to the same method; a human can follow the steps without launching an Agent; both use the same inputs, outputs, and stop conditions, and no human-only copy of the workflow is made.
- `define-requirements` handles the minimum business model and boundaries, and `specify-feature` settles the applicable acceptance criteria and VTs before implementation; business acceptance is not reduced to a pass summary of software tests.
- `verify-change` checks coverage starting from acceptance criteria rather than only from existing VTs, and handles dangling references and baseline changes; `record-handoff` keeps the impact scope, gaps, and items pending re-review or not run.
- The generic entry point explains how to explicitly read skills and the specific rules, with a workable integration method when nothing is auto-discovered.
- GitHub Copilot App is the first test target; its native discovery behavior must actually be recorded, without borrowing results from VS Code or Copilot CLI.
- The 5 prompt files are optional convenience entry points; if the App does not support them, the same task can be done in natural language, with no dedicated shortcut command required.
- Onboarding does not automatically choose a stack or initialize an application; implement-task reports the gaps when a concrete project and development inputs are missing, instead of generating a project itself.
- Restricted tool configurations must actually be verified; until verified, they are not advertised as a security boundary.

### P3: Release only after the exercises pass

- In a clean skeleton copy, go from reading the entry point through one document change, actually completing the document checks, records, and handoff, without creating an application project.
- Complete the modeling and traceability for the fixed semantic inputs below, find the coverage gap and dangling reference in the fault copies, and handle the rule change and old results correctly.
- A new session takes over using only the repository, the necessary external authorization, and the current task, without depending on the old conversation.
- Complete the GitHub Copilot App checks, recording the version, environment, and actual entry-point behavior; other clients are explicitly listed as tested, documentation-backed only, or untested.
- In a new session, exercise generic integration with natural language and explicit file reads; this must not be stretched into "all Agents verified".
- On the human path, a person actually follows the shared steps and records the process, comparing business boundaries, references, gaps, and statuses with the App path; without human participation, it stays unverified and is not replaced by Agent simulation.
- Check that the candidate skeleton contains no internal research material, maker records, exercise outputs, personal absolute paths, keys, or fake business facts, and does not depend on excluded files.
- Release notes include the template version, scope of application, required setup, and limitations; the repository template flag, permissions, and visibility are confirmed separately by the maintainers.

The document exercise uses this fixed input: "In the clean copy's README, fill in the name as 'Skeleton document exercise' and the scope as 'Maintain project material only; create no application'; keep the tech stack and commands not configured, and check that `src/README.md` points to where the development guide registers subproject paths and commands." Use the development log form to record the task scope, the actual document checks, the reason application checks are not applicable, and the next step, then take over in a new session. The name and scope are exercise inputs only, not downstream business facts; filled-in copies and exercise records do not enter the release candidate.

### Fixed inputs for the document-only semantic exercise

T05's setup and log task stays, but it alone cannot prove that modeling and traceability work. T13–T17 additionally use the following in-house document material; it is not a sample application, creates no project, dependencies, interface implementation, or runnable tests, and is not distributed with the skeleton.

| Input | Facts explicitly given in the exercise |
|---|---|
| Concepts and relationships | Member, item, loan record; each record links one member and one item, and an unreturned record counts as an active loan |
| Business boundary | The "Membership" context reports whether a membership is valid and does not manage loans, returns, or quotas; the "Lending" context manages loans, returns, and the active-loan quota based on the membership result and does not modify membership. They are not predefined services or project directories |
| Initial rule | Borrowing requires a valid membership, and each member may have at most 2 items on active loan. All quota scenarios assume a valid membership as a precondition: with 1 item already on loan, a 2nd can be borrowed; with 2 already on loan, a new loan is rejected and existing records are unchanged |
| Undefined matters | Handling of existing loans after a membership lapses, concurrency consistency, and similar matters are outside this exercise; when asked, keep them open and do not invent business decisions |
| Rule change | The active-loan limit changes to 3 and the membership rule is unchanged; the quota boundary scenarios become: with 2 on loan, a 3rd can be borrowed; with 3 on loan, a new loan is rejected and existing records are unchanged |

In a temporary copy, produce at least a locatable quota rule, REQ-001's business acceptance, SR-001's quota-behavior acceptance, VT-001's business acceptance plan, and VT-002's software behavior verification plan. References must lead from requirements to verification and from verification back to the targets; US or ABB may be omitted. The rule text stays in the domain material and requirements reference it; after a change, check the semantic impact, without requiring every affected file to rewrite the same number just to leave a trace.

The business or software behavior of VT-001/VT-002 is not actually run and is always marked `not-run`. The document-consistency checks actually completed record their object, result, and baseline separately and must not be entered into these two VTs to pass as business verification. After the rule changes, keep the old document-check results and their original baseline, with current applicability pending re-review; record new document-check results after updating the affected artifacts.

The coverage fault and the dangling target are each set up in a separate copy; the problems must not be removed by deleting real acceptance criteria or inventing requirements. The new session must identify the changed rule, the affected artifacts, the gaps not yet handled, and which items are only document checks and which behaviors are still not run. All exercise inputs, fault copies, and results are excluded from the release candidate.

## 4. First acceptance scenarios

These are the fixed acceptance criteria; whether each was actually run and the scope in which it passed are recorded in the next section. A scenario is not inferred to pass in full just because the files have been implemented.

| ID | Scenario | Observable pass condition |
|---|---|---|
| T01 | Copy the skeleton and open it for the first time | No custom tools or business dependencies are installed; README distinguishes browsing, filling in project material, and later creating a project, and open items are recorded explicitly |
| T02 | App cold start | Actually reads the entry point and related material, correctly identifies the locations of goals, specifications, tasks, commands, and logs, and recognizes what is not yet configured |
| T03 | App capability entry points | Discovery and reading are observed one by one for each native entry point claimed as supported; unsupported and unverified are recorded separately, and neither file existence nor manual reading may pass as native discovery |
| T04 | No dependence on prompt shortcuts | The same work steps are completed with natural language and explicit file reads |
| T05 | Skeleton document task | Fill in the README with the fixed input above, check the project-material navigation, and record the corresponding document checks with the log form; create no application and invent no development commands or application test results |
| T06 | Takeover in a new session | Continues from the task, model/requirements/VTs, logs, and Git state; can identify the impact, gaps, and not-run items in the semantic exercise, without blindly reusing old results |
| T07 | Missing requirement or development inputs | Asks clear questions; when no project has been created in `src`, does not automatically choose a stack, install dependencies, or generate an application, and does not record unrun application verification as passed |
| T08 | Merging into existing content | Check merging with a copy that has existing notes, rules, and user-marked files; keep the original content and report conflicts, without requiring a real business project to be integrated |
| T09 | No access to reference projects | Complete the skeleton document exercise without reading reference source code or depending on reference-project credentials |
| T10 | Permission and release limits | Without authorization, do not push or change protection settings; copying the template is not reported as having enabled approval, isolation, or CI |
| T11 | Directory and artifact ownership | Entry points, forms, and skills use the same naming; business/software acceptance, US, VT, and logs are distinguished; US is not a mandatory layer, and facts are not maintained twice |
| T12 | Tech-stack neutrality | The release candidate's `src` contains only a README, with no preset project, fixed test directory, application dependencies, or lock file; the setup notes do not require choosing a language before using the skeleton |
| T13 | Minimum business model and boundaries | The three concepts and their relationships, the quota rule, and the responsibilities and interactions of the two contexts in the fixed material are locatable; undefined matters stay open, and no service or code structure is generated |
| T14 | Layered verification and bidirectional traceability | REQ-001's business acceptance and SR-001's software acceptance each link to an appropriate VT; every in-scope acceptance criterion can be checked for coverage, and every VT leads back to its exact target; this works without a US, and a complete mapping does not change `not-run` |
| T15 | Coverage gap and dangling reference | In one fault copy, keep an existing acceptance criterion but remove all of its VT links; in a separate copy, add a reference to a nonexistent acceptance criterion; report the exact uncovered item and the wrong target respectively, without inventing facts or narrowing scope |
| T16 | Rule change and result applicability | After the limit changes from 2 to 3, locate the REQ/SR/VT that need re-review and update the necessary boundary scenarios; the membership rule is not rewritten without reason, old document results keep their original baseline and are not treated as current success, and behavior verification remains not run |
| T17 | Shared method for humans and the App | A human and the App each follow the shared steps from the same fixed input and reach consistent business boundaries, acceptance references, gaps, and not-run statuses; identical wording is not required; the human and client processes are recorded, and a side that did not run does not report a pass |

Record the interface used, the version, the files actually read, the run results, and any manual corrections. On failure, revise the template; an Agent's "done" is not the sole criterion; scenarios that were not run are explicitly kept as unverified.

Template checks and model-behavior exercises are two different things: relative links, metadata, and file formats can be checked with existing tools, whereas correct modeling, explaining traceability, and handling missing inputs and rule changes require actual operation. Passing T13–T17 means only that the exercise of document semantics and the shared method is complete, not that the planned business/software behavior VTs have been run. The first release has not verified coding, building, or testing of any application and does not use this to claim support for every language toolchain. Limited exercises are neither a security proof nor a success-rate promise.

<a id="actual-acceptance"></a>
## 5. Actual acceptance record (2026-10-14)

This section is the acceptance record for this skeleton build and is not distributed with the downstream template. The source baselines are P1 `52735a0` and P2 `4856c47`; the [blueprint](../design/repository-blueprint.md#template-layout) remains authoritative for the formal distribution list of 38 files. P1 and P2 each went through scope and content review. The template keeps business facts blank, and `src` contains only notes.

The first round used local tools and two general-purpose subagents, so its results support only the **local file path**. Later, the user allowed a standalone local test project, and the App's `create_session` started four real isolated sessions: default integration, reviewer, planner, and implementer/Git takeover. All completed within their limited scope; this is not ordinary subagents relabeled as App testing. The host process file version is App 1.1.29, the CLI metadata at launch of all four sessions is 1.0.95-3, and the OS is Windows 10.0.26200.0; the GUI picker, a restart of the whole App, other clients, and actual human operation remain untested.

| ID | Status this round | Actual observations and unfinished parts |
|---|---|---|
| T01 | Passed locally | Copied as the 38 specific files; readable and fillable without business dependencies, with not-configured items kept |
| T02 | Passed in a new App session | A new worktree session actually found the goals, specifications, current task, commands, and log locations and recognized what is not configured; the version, native events, and source records are kept; this is not equivalent to having tested a cold restart of the whole App |
| T03 | Partially done | API selection of the three roles and native invocation of the six project skills were confirmed successful; automatic path matching/non-matching, the GUI, and native entry points for optional prompts remain unverified |
| T04 | Passed on the App path | Natural-language tasks, native method loading, and explicit file reads completed the document work without using prompt shortcuts |
| T05 | Passed locally and in the App | Both paths filled in the fixed name/scope, checked the src navigation, and recorded the actual document checks and log; no application was created |
| T06 | Passed for App/Git takeover | A fresh implementer took over from the real source commit and the repository/logs, identifying the exact gaps, historical sources, and not-run items; it committed only the handoff log/index and did not claim to have fixed the quota specification |
| T07 | Passed locally | Coding was blocked when the project, tech stack, cwd, commands, and creation authorization were missing; document work continued, and unknown business policy was not invented |
| T08 | Passed locally | An independent fixture with existing rules identified 5 conflicts and stopped the affected writes, and the hashes of all 7 files were fully preserved; what passed is the refuse-to-overwrite/preflight branch, not a completed unconfirmed migration |
| T09 | Passed locally | The exercise used only the clean copy and the given material, without reading reference projects or depending on their credentials |
| T10 | Partially done | No push, release, or permission change; the real reviewer's tool selection is `["*"]`, so read-only is a conversational convention rather than an established gate; App/OS-enforced permission boundaries are unverified |
| T11 | Passed locally | Actually produced the model, REQ, SR, layered VTs, and log; traceable without creating a US/ABB, with a clear division of labor between results and indexes |
| T12 | Passed locally | The candidate's `src` contains only a README, with no application, fixed test directory, dependencies, or lock file; development commands are not configured |
| T13 | Passed locally | Concept relationships, the two rules, and the two contexts' responsibilities and interactions are locatable; handling of existing loans after a membership lapses and concurrency consistency remain open |
| T14 | Passed locally | The four REQ/SR acceptance criteria are each covered by exact target references in VT-001/VT-002; there is no US, and the behavior plans are still `not-run` |
| T15 | Passed locally | The two independent fault copies identified `SR-001-AC-02` as uncovered and `SR-001-AC-99` as dangling, respectively; real acceptance criteria were not deleted, and the fault copies were not dressed up as passing |
| T16 | Passed locally | After the limit changed 2→3, the REQ/SR/VT boundaries were updated; the membership rule and the original text of the old run were kept; the B1 result was first marked as pending re-review for current applicability, then a new B2 document result was added; behavior is still not run |
| T17 | Unverified | The user chose to complete App/local acceptance first this round; the human comparison stays unverified, and no agent simulates a human |

### Objects, results, and evidence

The initial copy formed B1 from the prescribed member, item, and loan-record material; a new agent completed B2 in a separate copy. The B1 and B2 document checks each ran 16 checks, all exiting 0; their results are recorded in a separate document-type VT-003 and **are not written into the business VT-001 or the software VT-002**. The B1 and B2 records of both behavior VTs are `not-run`.

A separate read-only check covered 32 candidate and evidence constraints: inventorying the four acceptance criteria from the real REQ/SR anchors, parsing the actual VT targets, and confirming exact fault isolation, the SHA-256 of the five B1 objects and nine B2 objects, the old report and the original RUN-01 text, the membership rule, the not-run behavior status, and candidate consistency. All 32 passed. This is not an application test and is not proof of client security or general reliability.

The first round's final candidate has 38/38 files and 228 resolvable relative links, with no research, design, plan, maker logs, exercise files, or Git history. After the copy was created, two table-separator formatting changes in the source README were detected; they were neither reverted nor committed on the owner's behalf. The candidate recaptured the current bytes, and the receipt explicitly records `README.md` as an uncommitted distribution file. The later update to the integration notes was saved as a new candidate and receipt; neither the old candidate nor the formatting changes are treated as bytes of the same commit.

The raw records are in the local `files` of maker session `1ff56941-bf56-4aa4-b769-fd4720915e1f`:

| Local artifact identifier | Content and limitations |
|---|---|
| `release-candidate-final`, `release-candidate-final-receipt.json` | The 38-file candidate with its sources, uncommitted scope, and per-file hashes; a local candidate only, not yet released |
| `candidate-final-check.json`, `evidence-audit.json` | Actual output of the file/link check and of the read-only integrity check |
| `exercise-baseline`, `exercise-coverage`, `exercise-dangling`, `exercise-change` | The B1, independent fault, and B2 copies; all excluded from distribution |
| `p3-initial-report.md`, `p3-followup-report.md`, `p3-findings.json` | What the agents actually read and did, commands, results, and limitations; not CI evidence usable across machines |

`document-check-b1.ps1` / `document-check-b2.ps1`, produced during the exercise, are one-off local document-check helpers and are **not in the 38-file candidate**. The follow-up report's description of the B1 helper as "shipped" is inaccurate. The B1 helper overwrites the snapshot of the same name and uses a fixed file list, so it cannot simply be rerun on the changed copy to serve as new evidence. This round keeps its original record, creates a separate B2 record, and checks the history with read-only hashes; these helpers are not delivered as a template runtime layer.

If whoever takes over cannot access the local artifacts above, rebuild the copies from this plan's fixed inputs and record new results; do not pretend the original evidence was recovered. See the [development log](../../logs/2026-10-14-skeleton-p1-p3.md) for the maker handoff.

### Later App and conflict observations

The local test project is a standalone Git repository built from the 38-file candidate, with no remote; its initial checkpoint is `7e478845fc64ceb0b66ba5b655771c543728d0eb`. After registration, all work happened only in App-managed worktrees; neither the original project configuration nor the test project's main checkout was modified.

[P3 reviewer entry](ghapp://sessions/40a224f5-795a-4877-af01-159b9070254e) selected its working mode through the App API; its launch events include `subagent.selected`, which here records a role selection, not the creation of a task subagent. The `skill.invoked` events on lines 70 and 244 of the raw events are `verify-change` and `record-handoff` respectively, with `source=project` and paths pointing to that worktree's `.github/skills`. The Git status at start and end shows only the branch line, with no actual file changes. The `tools` of both selected-agent events are `["*"]`, so this cannot be called enforced read-only.

[P3 app cold start](ghapp://sessions/712829a4-a056-4e78-a55a-b5e39d717c50) completed the fixed setup, document checks, log, and a local commit at checkpoint `29eacba44f7d63f0a930ed23963feabac7fb86b0`, changing only five document/evidence files and leaving the other 36 original files unchanged. It actually invoked four methods natively: onboarding, implementation, verification, and handoff; the parent session's 11 read-only checks of immutable Git objects and tool events passed. A new App session does not mean the whole shared App was restarted.

After that session finished and went idle, the parent session prepared a partial-change checkpoint `59aebcda25ff671cf19a0d7177d1ade6c777ccc4` in that session's worktree only: the historical B1 is kept as historical material, RULE-002 has changed to 3, and the old downstream boundaries and VT gaps are awaiting checks; the old helper was not rerun. It is not a "completed" result of this quota update.

[P3 planner entry](ghapp://sessions/fcf7e330-6f15-47f1-954a-4349967cf605) applied the requirements/specification methods read-only and correctly identified the old boundaries, the missing SR-001-AC-02, the index mismatch, and the B1 historical source; it made no writes and no new plan. [P3 git resumption](ghapp://sessions/9d65e97e-92ed-442d-b257-ed238dea848d) took over from the source and produced `312c3f8a067170f3d3621d41fd936282c6781255`: it changed only the log index and added a handoff, kept the 52 other original files, and left the working tree/index clean. The parent session's 12 read-only checks passed. Behavior and specification fixes have not been carried out yet, and passing the takeover or log checks is not treated as quota verification.

Checking the native events of the four real sessions together, each of the six project methods has `source=project`, a path in its own worktree, and a successful tool completion; each of the three custom roles has an actual selected-agent event, all with tool selection `["*"]`. What is confirmed, therefore, is API selection, method loading, and limited use in this environment, not the GUI, arbitrary natural triggering, automatic path matching, or enforced permissions. See the [integration notes](../agent-support.md#template-observations) for the per-entry-point scope.

For T08, onboarding was also actually applied to a seven-file fixture of existing content: the README facts, AGENTS's source-of-truth locations/numbering, the Copilot entry points, Markdown scope rules, and the `logs` ignore policy each conflicted with the candidate. The affected merge was stopped, contradictory rules were not appended side by side, and before/after SHA-256 lists confirm that all original text was kept. Future migration choices are up to the maintainers and are not part of this preflight's success claim.

New local evidence includes the host version, four `app-*-events.json` files, `app-native-audit.json`, the two immutable-checkpoint checks for onboarding/resumption, their respective observation summaries, and the T08 conflict/hash records. The versions come from the tool process ancestry and file metadata, not the About screen; events are kept separate from manual excerpts, and these "manual excerpts/checks" are Agent file operations, not T17 human participation. The session links above serve only for access through the current App history and are not public cross-machine evidence. All raw material lives only in the maker session or the local test repository and is not distributed with the candidate.

### Remaining P3 exit criteria

T03's automatic path matching/non-matching, GUI, and native entry points for optional prompts still need additional observation; the existing traces prove only listing, loading, and explicit reading, and these results are not backfilled. T17 stays unverified per the user's choice this round. Later, fill in the [client records](../agent-support.md#client-records) separately, using the same fixed input and real human/App operation; neither API selection nor Agent simulation substitutes for them. Observed items and untested items cannot be combined into "fully supported".

Before release, the accountable owner still needs to confirm the license, location, visibility, version, maintainers, permissions, and review arrangements. The current research repository must not be distributed wholesale and has not been turned into a GitHub template; P3 has not passed as a whole.

## 6. Later expansion based on actual need

Thin entry points for more Agents, tech-stack-specific rules, interface/data/operations document templates, and deeper DDD modeling content all require a real usage need first. The existing directory names do not require filling in every domain artifact, and multiple copies of the text should not be made in advance for compatibility.

When a project needs CI, a dev container, or check scripts, reuse the native mechanisms of that tech stack and platform. Do not expand these needs back into a skeleton runtime, an automatic release engine, or a cross-project management platform.

## 7. Six-repo functional alignment enhancement (started)

On 2026-10-19, Task12 froze the exact per-file owner manifest and completed candidate copy/validation, isolated import and resource closure, and the applicable local-path regression of the original T01/T05/T07–T16; the complete independent scoped re-review of the fix wave confirmed that the 3 Important findings and the 1 Minor/follow-up provenance finding have all been addressed, with no new issues. The new fix2 committed-source verification receipt matches the current commit's provenance (132 files, 41 exclusions, 0 findings, empty dirty scope). The final minimum-version retained+new result is 857/857; the historical 848/856 runs and the old report with malformed fix1 provenance are kept as they were. See the [maker-side acceptance record](../../verification/ddd-alignment.md) and the [Task12 handoff](../../logs/2026-10-19-task12-candidate.md) for evidence and `not-run` gates; this does not inherit the old 38-file candidate or the App/human/application/platform/release results, and it does not close overall parity.

On 2026-10-14 the user asked for an enhancement plan for functional alignment with the six `ddd-*` repositories and confirmed keeping the single-repo model and tech-stack neutrality, with functional equivalence rather than compatibility with the old formats. On 2026-10-15 the user further confirmed that scripts are essentially unified on Python: local runs, hooks, and CI reuse the same logic, and the required PowerShell wrapper layer is dropped; native CI YAML and the necessary thin launch adapters are kept, with no custom CLI/executor.

On 2026-10-19 the user made a ready-to-use local scaffold the current priority and does not treat a real-application showcase exercise as a prerequisite for current readiness. Copying the candidate by the exact manifest and verifying it in isolation is not equivalent to release authorization or full six-repo parity; the Task13 live/human/App/client/platform conclusions and the Task14 full-matrix equivalence conclusion remain listed separately as unfinished gates.

A new local candidate has been produced under the current manifest: 132 files, source HEAD `ee46390`, dirty scope recorded separately, 132/132 re-verified, 0 findings; `test_distribution.py` 40/40 with no skips/failures/errors. The isolated Flagsmith POC's `poc/` is listed in the manifest exclusions, so the candidate does not carry the exercise copy. See the [Task13/ready-scope handoff](../../logs/2026-10-19-task13-flagsmith-poc.md) for the detailed receipts; the artifact and the raw test report exist only as session-local evidence of this session and are not used as cross-machine evidence.

On 2026-10-19 the 38 historical P1/P2 paths were checked against the template blueprint, and all 38/38 exist in the main working tree; a complete 132-file enhanced-manifest copy, the sibling `agent-native-scaffold/`, was created in the POC root directory provided by the user, separate from `flagsmith/`. This copy is not an item-by-item verbatim replica of the old 38-file path set: `docs/agent-support.md` contains historical client observations and remains safely excluded by the manifest. A candidate inside the working tree once caused the root-level artifact checker to recognize nested forms as formal artifacts, so it was moved outside the working tree and the duplicate copy inside the working tree was cleaned up; the final sibling copy verify is 132/132 with 0 findings, and the root-level artifact checker is back to `empty`; see the [Task13 handoff](../../logs/2026-10-19-task13-flagsmith-poc.md) for the record.

The user then asked to commit the current changes first and only then start execution; the README formatting was committed as `1a6f594`. Task 1's [six-repo capability matrix](../research/ddd-capability-matrix.md) has completed the source inventory: six full commits, 252 entries, 195 blobs; existing capabilities, roadmap proposals, instance placeholders, and unverified external dependencies are registered separately.

After the source code confirmed the features the original plan had missed, the user chose to include them all; the [enhancement specification](../design/ddd-functional-alignment.md) and the [plan](2026-10-14-ddd-functional-alignment.md) added ENH/Tasks 15–18 and completed the scope of the existing tasks; media/PDF/platform dependencies and execution still require separate authorization. The scoped local implementation/review of Tasks 1–11, Task15, the Task16 offline scope, Task17 local export, the Task18 local ledger, and the Task12 candidate is complete, with no outstanding scoped review findings, but this does not mean real qualification or approval. Task16 audio is still not-run and ENH-16 is not closed; Task17 PDF/PPTX and the actual binary-format gates have not been run, and ENH-17/full parity are open; Task18 provider/billing/real usage and the overall ENH-18 conclusion remain open. The Task12 fix-wave review closed the candidate-report overlap, reparse TOCTOU, hardlink, stale plan status, and provenance argument order issues; the new candidate's provenance is bound exactly to cda3cfd, with 132 files matching byte for byte, 41 exclusions, and 0 findings. A candidate is not a release or full parity. Task13 created the isolated copy `poc/flagsmith` for the Flagsmith/OpenFeature technical POC the user chose; it copied only the 86 tracked files of pinned commit `beade3c`, without copying `.git`, ignored dependency/secret configuration, or untracked design files newly added in the source repository. After a locked restore in the isolated copy, the POC unit/build/controlled-browser results are 19/19, success, and 10/10; one pre-existing failure of the static structure/link check on a non-English document remains on record. This POC is not an application integrated with a business system; live Flagsmith, code generation/maintenance, and the human/App/client/platform gates are not yet complete; see the [Task13 handoff](../../logs/2026-10-19-task13-flagsmith-poc.md) for details. Closing out the Task14 row-by-row matrix is still not done; no overall equivalence conclusion may bypass the applicable external gates. The original P3 entry-point/human observations are not upgraded; remote gates are not changed and no external fan-out is performed.

The scope completed so far also includes the optional source manifest, the nine views, and the coverage and impact candidates; this is not a pass of the entire enhancement. The Task7/8 review fixes are closed; reports and models still only reference the original sources. The Task9 exercise does not fill in unknown risks or decisions and does not rewrite VTs. The Task10 results for native launch, environment, and report boundaries are kept separately; see the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task10-review). There is no real project installation, and hosted CI, POSIX native launch, and required checks remain not-run. The original P3, application/code-generation, and release gates remain, and historical records are not rewritten.

The independent Task8 review on 2026-10-16 raised three Important findings; after the [round 1 narrow fix](../../logs/2026-10-15-ddd-alignment.md#task8-fix1) completed RED/GREEN and full verification of 395 test methods, the scoped re-review closed the original three and pointed out a new compatibility issue. This does not upgrade the business/approval or complete-enhancement conclusions.

The new T8-F1-N1 was closed through the [round 2 local fix](../../logs/2026-10-15-ddd-alignment.md#task8-fix2) and the [scoped re-review](../../logs/2026-10-15-ddd-alignment.md#task8-review); the export/check round trip for valid business trees is restored, and the protection of actual domain sources is kept. The old full 395 suite and the partial results for different objects are each kept and are not relabeled as one new run.

The independent Task16 review at `9942e70` raised three Important findings and one Minor; this round's
[fix1](2026-10-14-ddd-functional-alignment.md#task16-fix1) corrected only the source-unit qualifier,
the shared Markdown context, count/position relationships, and gridless table width, and its scoped re-review is complete.
The old 688 results and this round's new partial/minimum-version results are kept separately; actual audio/ENH-16 is not closed as a whole;
the scoped re-review at `97d35aa` confirmed that all four original findings were addressed, with no new related findings;
see the [re-review handoff](../../logs/2026-10-15-ddd-alignment.md#task16-review) for the entry point.
Task17's local formats and fix1 have completed scoped re-review; both original findings were addressed, with no new findings; see the [re-review record](../../logs/2026-10-18-task17-resume.md#task17-fix1-review). PDF/PPTX remain `unavailable` / `not-run`.
The audio rejection contract is not passed off as a real service result, local formats do not close ENH-17/full parity, and Task12 is not unlocked by bypassing Task18/candidate delivery.

On 2026-10-19, Task18 implemented an explicit local CSV interaction ledger and a grouped usage summary, adding 17 tests; the final Python 3.11.15 retained+new regression ran 804/804 with 0 skips/failures/errors. The implementation is currently local-scope only and awaits independent scoped review; no real user sessions, bills, provider prices, or production data were read. The actual single-machine multi-process behavior of the byte-range lock on Windows fixed local disks is tested; durability on network, cross-host, or synced directories is outside the support claim. Task12 still needs the Task18 review and candidate delivery; ENH-18 real provider/billing and overall parity remain open; see the [Task18 handoff](../../logs/2026-10-19-task18-resume.md) for the entry point.

On 2026-10-19, Task18 fix1/round1 made updates for the three Important review findings: a summary without output is now a stable two-pass byte/identity snapshot with no sidecar file side effects; both appends and new summary outputs require the caller to pass `--attest-local-storage`/`attest_local_storage=True` explicitly; summary output performs an `NtCreateFile` relative exclusive create through a pinned Windows directory handle and, after writing, rechecks the identity of the parent directory, the source, and the new file. 11 new regression tests were added, and the Task18 targeted suite passed 28/28 with 0 skips/failures/errors; the final retained+new Python 3.11 suite for fix1 is still pending, after which the change will be committed and await scoped re-review. Attestation is a caller declaration, not proof from a storage provider/OS; real usage/cost, Task12, and ENH-18/parity remain open.

On 2026-10-19 the final fix1 Python 3.11.15 minimum retained+new regression ran 815/815 with 0 skips/failures/errors and exit code 0; `inputs_unchanged=true`. The implementation awaits a local coauthor commit and independent scoped re-review; Task12 is not unlocked, and real provider/billing/usage and overall parity remain open.

On 2026-10-19 the final minimum-version retained+new Python 3.11.15 regression for Task18 fix1 ran 815/815 with 0 skips/failures/errors and exit code 0, with inputs unchanged; all Task18 targeted tests are 28/28. The fix's local commit is still pending, followed by independent scoped re-review; Task12 is not unlocked. The raw fix1 RED/GREEN and final receipts are in the local Task18 fix1 report/evidence; this result does not mean provider/billing/real usage or overall parity has been verified.

On 2026-10-19, Task18 fix2/round2 addressed the new Important finding: after the native `FILE_CREATE`, a stable identity is first cached from the native file handle, and only then is the CRT descriptor wrapped and the first `fstat` run; every post-create failure keeps and reports the recovery identity and does not delete the output. The two injected post-create failure tests passed, and Task18 targeted is 30/30; the retained+new Python 3.11 full suite for fix2 awaits its final run. The reviewer's Minor (remove the `summarize_usage(lock_timeout=...)` kwarg) is recorded as deferred per the user's instruction, since a local `rg` found no callers, and fix2 is not expanded. Task12 still awaits scoped re-review/the candidate.

On 2026-10-19 the final minimum-version retained+new Python 3.11.15 regression for Task18 fix2 ran 817/817 with 0 skips/failures/errors and exit code 0, `inputs_unchanged=true`; Task18 targeted is 30/30. The Minor parameter suggestion for the new API stays deferred; the fix awaits a local commit and independent scoped re-review, and Task12 is not unlocked.

On 2026-10-19 an independent scoped re-review confirmed that Task18 fix2 addressed the post-native-create recovery identity Important finding, with no new breakage found; the Task18 local implementation/review scope is now closed. The intermediate two-test receipt `green-create-failure-report-02.json` has an inconsistency between its JSON summary and raw output (exit 1/raw `KeyError`) and does not count as a pass; only the later Task18 targeted 30/30 and minimum 817/817 receipts are used as final, and the raw file is kept. The Minor `summarize_usage(lock_timeout=...)` parameter suggestion is deferred because there are no in-repo calls and the API is unreleased, and it is listed for the final overall review. The local prerequisites for Task12 are now all in place, and the next step is to start candidate delivery; the candidate and the later human/application/platform gates are still accepted separately.
