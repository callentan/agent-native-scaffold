# Repository template and agent file blueprint

**Updated: 2026-10-19. The 38 P1/P2 files are the historical first-release scope; the enhancement candidate is defined by the exact [distribution manifest](../distribution-manifest.json) and recorded separately from the P3 client, manual, application, and release status; see the [actual acceptance record](../plan/roadmap.md#actual-acceptance) and the [Task12 maker-side acceptance](../../verification/ddd-alignment.md).**

## 1. One template, two sets of content

The formal template's repository root is the downstream starting point; there is no framework install or generator step. Project materials ship with the agent capability files, and users own them directly once copied.

The deliverable is a repository skeleton, not a scaffold with a sample application. `src/` is left for users to create any kind of project; the first release puts only a guide there and chooses no language, framework, dependency manager, entry point, or test layout.

Three responsibilities are first-release content requirements, not just naming references: **DDD covers the business model and boundaries, the V-model covers traceability from requirements to verification, and templates, skills, and prompts let humans and agents share one process.** Forms define artifact structure, skills hold shared methods, and prompts only provide invocation entry points. Full DDD/V-model is not mandatory, but applicable minimum modeling and traceability are not skipped.

Directory naming follows the researched DDD projects: the domain side borrows the responsibilities of `ddd-subdomain` / `DM-Subdomain`, the implementation side borrows from `ddd-bc` / `DeviceRegistry-BC`, and document forms adopt the centralized `_templates` organization. Content is organized in a single repository; their submodule or multi-repository deployment is not reused.

Reference source code, internal research, and this project's design discussions must not be mixed into downstream PRDs or business documents. Distributable content is prepared before release; the current research repository must not simply be marked as a public template.

<a id="template-layout"></a>
## 2. First-release template layout

```text
project/
  README.md
  AGENTS.md
  .gitignore
  stakeholder-requirements/
    README.md
  domain-model/
    README.md
  software-requirements/
    README.md
  user-stories/
    README.md
  architecture/
    README.md
    decisions/          (created with the first ADR)
  verification/
    README.md
  logs/
    README.md
  docs/
    development.md
    ai-tooling.md
    governance.md
    distribution.md
    distribution-manifest.json
    domain-sources.md
    source-extraction.md
    document-exports.md
    template-updates.md
    project-flow.md
  _templates/
    items/              (blank forms)
    config/             (optional configuration templates)
    reports/            (report templates)
  src/
    README.md
  .github/
    copilot-instructions.md
    instructions/       (rules for Markdown, tests, code, and security)
    agents/             (planner, implementer, reviewer)
    skills/             (method SKILL.md files)
    prompts/            (optional prompt files)
    contracts/          (JSON schemas and their guide)
    utilities/          (optional Python maintenance tools)
    hooks/              (optional git hooks)
    workflows/          (validate-artifacts.yml)
    pull_request_template.md
```

This tree is an overview of the shipped layout, not an exhaustive list; the authoritative file list is `docs/distribution-manifest.json`. The first-release count of 38 files is historical (see section 8). A file's existence means neither native client discovery nor release authorization.

`architecture/decisions/` is the agreed ADR location, created together with the first ADR; do not add a fake decision to keep an empty directory. Project-material directories initially contain only filling guidance; REQ/SR/US artifacts are not pre-generated.

`src/README.md` explains that any kind of project can be created in `src/` or a subdirectory, with the real working directory and commands registered in the development guide. The historical `src/tests/` is not created in the first release; source code, tests, dependency manifests, and pipelines are decided downstream. Existing projects keep their original paths and are not forced into `src` or a separate test directory.

Blank forms are centralized in `_templates/items/`; copy one into the formal artifact directory instead of keeping a `_template.md` in every directory. The form file names are this template's own design; `user-story.md` and `verification-test.md` map directly to reference records, and the other files are also written independently, without copying original templates.

### Naming basis and changes from the previous version

| Previous-version purpose | Current path | Reference and adjustment |
|---|---|---|
| Domain facts scattered across project notes | `domain-model/` | Reuses the reference domain directory name; maintained in this repository, not as a read-only external mount |
| `prd/` product description | `stakeholder-requirements/` | Borrows the stakeholder requirements / REQ responsibility; top-level placement is this template's own arrangement, not a replica of the reference's nested path |
| `specs/` feature specifications | `software-requirements/`; design in `architecture/`, verification in `verification/` | Reuses the reference projects' SR/ABB/VT division of labor instead of one mixed specification directory |
| `tasks/` implementation tasks | Delivery slices and checklists in `user-stories/` | Reuses US; maintenance items that do not fit a user story use an issue/PR, not a forced user-value narrative |
| `docs/architecture.md`, `docs/decisions/` | `architecture/README.md`, `architecture/decisions/` | Adopts the reference architecture directory; the central decision location in a single repo is our own choice |
| Scattered `_template.md` files | `_templates/items/` | Reuses the reference template directory and its `items` organization, as local files, not a submodule |
| Development and takeover records | `logs/`, `docs/development.md`, `docs/agent-support.md` | Our own addition; no evidence that the reference projects use the same log or guide paths |
| Source code and test layout | `src/README.md` | `src` is the container for user projects; the historical `src/tests/` is not pre-created; test paths follow the downstream stack |

The naming basis comes from earlier research and the initial blueprint's path records; see the [directory-naming adoption record in the source register](../research/source-register.md). Borrowing directories does not mean inheriting source code, enforcing full DDD, or making the references a runtime dependency.

## 3. Minimum content of project materials

| File or directory | Minimum content |
|---|---|
| README | Project goal, current stage, staged setup checklist, a human activity entry point to shared methods/forms/artifacts, and the template source version |
| AGENTS | Short navigation, per-task reading rules, missing inputs and stop conditions; links existing materials first, skills in P2 |
| Domain model | Shared terms, core concepts and relationships, business rules, bounded context responsibilities and interactions, fact sources and open items; detailed filling in the next section |
| Stakeholder requirement (REQ) | Business entry point that takes over the PRD's goals and scope; the form records source, related domain rules/contexts, status, business requirements, and business acceptance criteria; create `REQ-001-<slug>.md` when needed |
| Software requirement (SR) | Upstream REQ or explicit task basis, owning context, software behavior, boundaries and error cases, acceptance criteria qualified by the owning artifact identifier, and necessary interface agreements |
| User story (US) | Delivery slice, requirement links, change scope, implementation checklist, status, and record links; not a second copy of requirements nor a mandatory layer between requirements and VT |
| Verification specification (VT) | Verification layer and targets, acceptance references each qualified by owning artifact, steps/test identifiers, expected results, actual results with baseline references, result applicability; no test code |
| `verification/README.md` | Coverage index for finding the current delivery scope's acceptance criteria and VTs, listing gaps and the checked baseline explicitly; no separate pass-status copy |
| Development log | Task, date and session identifier, branch or baseline, changes, verification, blockers, next steps |
| Architecture (ABB) and ADR | Current structure, related requirements and business boundaries, necessary design constraints and their verification basis, rationale and consequences; not every task needs a design artifact |
| `src/README.md` | How to place any project in its native layout, and the requirement to register development commands once a project exists; no sample application |
| Development guide | Initially explicitly not configured; later records per subproject the relative path, environment, dependencies, install/build/run/test commands, working directory, and troubleshooting entry point |
| Agent support guide | GitHub Copilot App as the first test target; entry points and skill locations; discovery/usage results per client and version; limitations; manual file reading; initially not marked as tested |
| `.gitignore` | Minimal generic ignore rules that do not ignore formal artifacts or development logs; downstream projects extend them for real tools; no prebuilt language configuration |
| PR form | Task basis, change scope, actual verification, open items and limitations; pass, approved, or released are not checked by default |

While no tech stack is chosen, the development guide says it is "not yet configured"; this does not block use of the skeleton. Complete it after the user decides to create a concrete project, and never add an empty test script that looks successful. Required first-time inputs and items that may stay open are listed in [P0 decision D09](../plan/decisions-and-risks.md). Placeholder hints in templates are normal, but before a task starts, identify which facts are still undetermined.

Formal files use readable names such as `SR-001-<slug>.md`, `US-001-<slug>.md`, `ABB-001-<slug>.md`, and `VT-001-<slug>.md`. Assign numbers only when the artifact is actually needed; do not invent requirements to complete a traceability chain or carry sample approval statuses into a new project. The PRD remains the product description and is not equated with a single REQ.

Development logs are committed and hold only the necessary summary and links to raw reports. Runtime logs, full chats, credentials, personal absolute paths, and sensitive output are not committed; configure the project's `.gitignore` for the real tools' output directories.

### 3.1 Minimum filling requirements for lightweight DDD

P1 provides these sections and guidance in the established `domain-model/README.md`, and P2's `define-requirements` follows the same requirements; no new modeling agent is added.

| Content | Questions it must answer |
|---|---|
| Shared terms | What does this term mean in the current context? Does a concept with the same name mean different things in different contexts? |
| Core concepts and relationships | Which important objects, behaviors, or states exist, and how are they related? Do not just list nouns without relationships |
| Business rules and invariants | Which conditions must hold, which behaviors are forbidden, and within which scope does each rule apply? Rules are referenced by a stable section or identifier |
| Bounded contexts | What is each context responsible and not responsible for, and which business facts does it maintain? Directory names or technical layers cannot replace business responsibilities |
| Context interactions | Which side provides what business information or capability, and which agreement does the other side depend on? Business boundaries need not map one-to-one to repositories, services, or `src` subprojects |
| Sources and open items | Which facts has the user given, and which content is inferred or to be confirmed? How do the related REQs/SRs locate their business basis? |

The initial skeleton provides only guidance and no prefilled business model; business tasks fill in or reference the existing model within their scope. Do not split one context artificially. For pure documentation or non-business tasks, state why the model does not apply instead of fabricating one. Entities, value objects, aggregates, the repository pattern, and code layering are adopted as needed, not mandated.

### 3.2 Traceability carriers and single source of truth

Forms stay at seven: REQ adds business acceptance and model references, SR adds its upstream basis, and VT makes explicit the verification layer, target criteria, run baseline, and result applicability. Each acceptance-criterion reference includes the owning artifact and a stable identifier; model rules also have locatable sections. US only organizes delivery; ABB/ADR join design traceability as needed and are not created just to complete the chain.

`verification/README.md` is built from the acceptance criteria of the current delivery, including criteria with no VT yet; do not collect existing VTs and claim complete coverage. SR stores upstream references and VT stores target acceptance references; reverse relationships are checked through these references and search, with no manual copy at each end. The index holds only links, gaps, and the checked baseline; acceptance text, relationships, and results stay with the owning artifacts.

Business acceptance, software behavior verification, design verification, gaps, dangling references, change impact, and old results are designed uniformly in [sections 3–4 of the working conventions](execution-contracts.md). P1 implements the fields and filling constraints in forms and guides, and P2 implements the operational steps in skills; downstream projects must not replace this content with links to undistributed design documents.

## 4. Copilot first, without duplicating rules

| Entry point | Intended use |
|---|---|
| `AGENTS.md` | Common rules and material navigation; does not depend on a specific model, personal settings, or hidden sessions |
| `.github/copilot-instructions.md` | Copilot repository-level guidance that requires reading the common rules and the current task's materials |
| `.github/instructions/*.instructions.md` | Scopes specialized rules with the client-supported `applyTo` patterns |
| `.github/agents/*.agent.md` | Selects a working mode; the main content references a skill, and tool restrictions are verified per client |
| `.github/skills/<name>/SKILL.md` | Single body of an activity method; references the `_templates/` forms and states the formal artifact directory |
| `.github/prompts/*.prompt.md` | Supplies the current task input and points to the corresponding method; does not hold the only copy of the workflow |

GitHub's official documentation lists several skill directories; this design maintains only `.github/skills`, so Copilot can use it natively. Clients that do not discover it automatically read the target `SKILL.md` explicitly. Add other entry points only after confirming an actual need, to avoid three bodies of text drifting apart under `.github`, `.agents`, and `.claude`.

Links between AGENTS and the Copilot entry points do not guarantee automatic loading; the first release must verify that Copilot actually read the task requirements and related rules, not merely that the files exist. A client may ignore unrecognized tool names in a custom agent, so do not infer a restriction from the names.

Prompt files are optional convenience entry points. Where GitHub.com and Copilot CLI lack the IDE prompt-file experience, specify the task and skill directly in natural language; the core process does not depend on slash commands, variable expansion, or client handoff features.

These locations and limitations come from the [official GitHub sources Q1–Q4](../research/source-register.md) consulted on 2026-10-13; they do not mean the template has passed client compatibility testing.

**GitHub Copilot App** has been selected as the first client to test. Its entry-point discovery, metadata, and tool-configuration support must be tested in practice separately; it cannot be inferred from VS Code or Copilot CLI. The 5 prompt files stay optional, not required App functionality; where unsupported, name the skill in natural language. Record native discovery, explicit reading, and unverified status separately.

### Specific responsibilities of first-release capabilities

Method text is maintained only in the 6 skills below; forms still reference `_templates/items/`, with no sample application or scripting layer.

| Skill | Input | Output and boundaries |
|---|---|---|
| `project-onboarding` | Current repository state; user-provided goals and constraints | Completes confirmable setup items and records the rest as open items; does not automatically choose a tech stack, install dependencies, or initialize a `src` project |
| `define-requirements` | Goals, users, scope, and business facts provided by the user | Works out model, rules, and boundaries per the lightweight DDD guidance; produces draft REQs traceable to sources, with business acceptance; clarifies missing facts first |
| `specify-feature` | Model and existing requirements or an explicit task; current structure and constraints | Reuses the existing basis; produces SR acceptance criteria and draft VTs as needed; lists coverage gaps; creates US and ABB/ADR as needed; no automatic approval |
| `implement-task` | Explicit task and change scope; coding also needs a concrete project and a real development guide | Checks the business basis and verification plan before implementing; handles model or requirement change impact first; creates no application on its own when development inputs are missing |
| `verify-change` | Complete acceptance list for the current delivery, changes, related VTs, and results | Checks coverage, dangling references, and baseline applicability both ways, then runs applicable checks; keeps document-check and software-behavior results separate; never disguises gaps as passes |
| `record-handoff` | Task, Git status, affected artifacts, actual results, gaps, and blockers | Log references the current baseline and items pending re-review or not run; on takeover, recheck facts and traceability first; do not treat old results as current results |

The three agents only define working modes: `planner` references the onboarding, requirements, and specification methods; `implementer` the implementation, verification, and handoff methods; `reviewer` the verification method. The model is inherited from user settings; a tool scope counts as an effective restriction only after testing in the App; the reviewer is not a human approver.

| Optional prompt | Referenced methods |
|---|---|
| `start-project.prompt.md` | `project-onboarding` |
| `plan-feature.prompt.md` | `define-requirements`, `specify-feature` |
| `implement-task.prompt.md` | `implement-task`, `verify-change` |
| `review-change.prompt.md` | `verify-change` |
| `resume-work.prompt.md` | The takeover check of `record-handoff`, then a method chosen for the current task |

Repository-level instructions provide guidance: `docs.instructions.md` covers documentation facts, status, and references; `tests.instructions.md` covers actually running test changes and mapping them to acceptance, without presetting a language, test directory, or commands. P2 sets path scopes per the target client's conventions and states in the common entry point how to read the rules explicitly. When a downstream project changes its layout, adjust the scopes; generic patterns do not cover any tech stack.

### Entry points shared by humans and agents

The formal README's "What do I need to do now?" activity navigation lists the required inputs, shared methods, forms, and artifact locations. Humans read the steps in `SKILL.md` and fill in forms by hand, while agents enter the same method from `AGENTS.md`; both follow the same fact sources, traceability requirements, completion conditions, and stop conditions. Skipping agents and prompt shortcuts does not affect usability.

P1 provides entry points to the existing materials and forms; P2 connects the activity navigation to the six skills. Skill steps are executable by humans; no specific agent role or dedicated tool call is mandatory, and no separate "manual workflow" is duplicated. Prompts only add the input for the current run and cannot change acceptance standards.

## 5. First-time setup and daily use

1. Create a repository from the prepared formal template, or merge the needed files into an existing project.
2. Following the README, fill in the user-confirmed project goals and scope; the onboarding skill can help. An unselected tech stack and commands stay not configured.
3. When the user decides to start coding, the user creates a concrete project in `src/` or explicitly asks an agent to do so; use the native tools of the chosen tech stack, register the actual paths, commands, and verification results, and do not apply a prebuilt application automatically.
4. Open GitHub Copilot App and choose a working mode that is actually available, or describe the task directly; other agents first read `AGENTS.md` explicitly.
5. Refine domain and business requirements as needed, elaborate SR/US, and record architecture and verification in their directories; after development, update the log and handoff. Use existing client and platform capabilities for any PR.

Project tools and the off-the-shelf Copilot CLI do not contradict the "no home-grown CLI" positioning, and the basic process needs no extra global skill, MCP service, or personal knowledge base.

## 6. Copying, merging, and updating

After copying, the project maintains the files. Template updates provide only versions, diffs, and change notes for users to review and merge; there is no `ans upgrade`, no generator-managed file category, and no background sync.

An existing project first inventories its README, AGENTS, Copilot configuration, skills, and documentation locations, then merges selectively. On conflict, keep the original content and list the differences; do not overwrite existing rules or automatically migrate historical PRDs, tasks, or code.

A Git tag or release records the template version; the README only records the source used. Application dependencies stay in the project's native dependency manifests; `agent.yaml`, `agent.lock.json`, and `.agent-state` are no longer required files.

## 7. Items to handle before releasing the template

The research directory holds internal project summaries; at release they must be separated and reviewed, and must not be copied or published with the business template. Distribute only the skeleton files listed in this blueprint, written for downstream use, with no sample application.

Prepare a clean candidate from the specific file manifest; do not copy the whole repository and its history, and do not carry research, design, implementation plans, maker logs, or exercise outputs downstream. Release links must not depend on excluded content. Handling boundaries and pre-release decisions: [P0 decision D01](../plan/decisions-and-risks.md).

Setting the repository as a GitHub template and configuring visibility, branch protection, CI permissions, and license are separate release operations, not completed automatically by the existence of design or template files. This round completed local production and a limited documentation exercise; these release operations were not performed.

## 8. Authorized six-repository functional enhancement

The 2026-10-15 execution request extends functionality beyond the original 38 files; the new files' responsibilities and dependencies are governed by the [enhancement plan](../plan/2026-10-14-ddd-functional-alignment.md), and their sources by the [six-repository capability matrix](../research/ddd-capability-matrix.md). The counts above and the "deliver only minimal modeling" convention remain the historical scope of the completed first release; files in the new plan are not treated as already existing.

The enhancement permits more domain/QAS/tactical/governance forms, nine shared methods with thin prompts, data schemas, and on-demand Python utilities. Optional domain-source integration needs no submodules; body text, relationships, run results, and derived views each keep a single source. Media, diagram/document export, and interaction ledgers each have their own task and authorization boundary; no general-purpose executor or background service returns.

Task12 froze the exact inventory from the delivered files; source-code research, the maker matrix, plans, real session/client results, logs, test/exercise material, and Git history still do not go downstream. The candidate and local checks are not release authorization; core documents remain readable without installing maintenance tools, and the business stack and application remain the user's decision.

