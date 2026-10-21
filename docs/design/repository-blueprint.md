# Repository template and agent file blueprint

**Updated: 2026-10-19. The 38 P1/P2 files are the historical first-release scope; the enhancement candidate is now defined by the exact [distribution manifest](../distribution-manifest.json). The candidate is recorded separately from the P3 client, manual, application, and release status; see the [actual acceptance record](../plan/roadmap.md#actual-acceptance) and the [Task12 maker-side acceptance](../../verification/ddd-alignment.md).**

## 1. One template, two sets of content

The repository root of the formal template is the starting point of a downstream project; there is no longer a step of installing a framework and then running a generator command. Project materials are distributed together with the agent capability files, and users own these files directly once they copy them.

What is delivered is a repo skeleton, not a scaffold bundled with a sample application. `src/` is left for users to create any kind of project; the first release puts only a guide there and does not choose a language, framework, dependency manager, application entry point, or test layout.

Three responsibilities are first-release content requirements, not just naming references: **DDD covers the business model and boundaries, the V-model covers traceability from requirements to verification, and templates, skills, and prompts let humans and agents work through one shared process.** Forms define artifact structure, skills hold the shared methods, and prompts only provide invocation entry points; full DDD/V-model is not mandatory, but the applicable minimum modeling and traceability are not skipped either.

Directory naming follows the DDD projects and the repos researched earlier: the domain side borrows the responsibilities of `ddd-subdomain` / `DM-Subdomain`, the implementation side borrows from `ddd-bc` / `DeviceRegistry-BC`, and document forms adopt the centralized organization of `_templates`. We organize the needed content in a single repo and do not reuse their submodule or multi-repository deployment approach.

Reference source code, internal research material, and this project's own design discussions must not be mixed into downstream PRDs or business documents. Prepare the distributable content before release; the current research repository must not simply be marked as a public template.

<a id="template-layout"></a>
## 2. First-release template layout

```text
project/
  README.md
  AGENTS.md
  .gitignore
  domain-model/
    README.md
  stakeholder-requirements/
    README.md
  software-requirements/
    README.md
  user-stories/
    README.md
  architecture/
    README.md
    decisions/
  verification/
    README.md
  logs/
    README.md
  docs/
    development.md
    agent-support.md
  _templates/
    items/
      stakeholder-requirement.md
      software-requirement.md
      user-story.md
      architecture-building-block.md
      verification-test.md
      architecture-decision.md
      development-log.md
  src/
    README.md
  .github/
    copilot-instructions.md
    instructions/
      docs.instructions.md
      tests.instructions.md
    agents/
      planner.agent.md
      implementer.agent.md
      reviewer.agent.md
    skills/
      project-onboarding/
        SKILL.md
      define-requirements/
        SKILL.md
      specify-feature/
        SKILL.md
      implement-task/
        SKILL.md
      verify-change/
        SKILL.md
      record-handoff/
        SKILL.md
    prompts/
      start-project.prompt.md
      plan-feature.prompt.md
      implement-task.prompt.md
      review-change.prompt.md
      resume-work.prompt.md
    pull_request_template.md
```

This is the first-release distribution manifest as produced: 38 files in total. The 21 P1 files are README, AGENTS, `.gitignore`, the guides of the project-material directories, the seven forms, the two guides in `docs`, `src/README.md`, and the PR form; P2 adds the remaining 17 `.github` capability files and connects them to the P1 entry points. That a file exists does not mean a client has natively discovered it, nor that release has been authorized.

`architecture/decisions/` is the agreed location for later ADRs and is created together with the first ADR; do not add a fake decision just to keep an empty directory. Project-material directories initially contain only filling guidance; business artifacts such as REQ/SR/US are not pre-generated.

`src/README.md` explains that any kind of project can be created directly in `src/` or in a subdirectory of it, and that the real working directory and commands are registered in the development guide. The `src/tests/` from the historical reference is not created in the first release; actual source code, tests, dependency manifests, and pipelines are decided by the downstream project. Existing projects keep their original paths and are not forced to move into `src` or to create a separate test directory.

Blank forms are centralized in `_templates/items/`; copy one into the corresponding formal artifact directory instead of keeping a `_template.md` in every directory. The form file names above are this template's own design; of these, `user-story.md` and `verification-test.md` map directly to reference records. The content of the remaining files is likewise written independently by us, without copying the original templates.

### Naming basis and changes from the previous version

| Previous-version purpose | Current path | Reference and adjustment |
|---|---|---|
| Domain facts scattered across project notes | `domain-model/` | Reuses the reference domain directory name; maintained inside this repo, not as an external read-only mount |
| `prd/` product description | `stakeholder-requirements/` | Borrows the stakeholder requirements / REQ responsibility; placing it at the top level of a single repo is this template's own arrangement and does not claim to replicate the reference repository's nested path |
| `specs/` feature specifications | `software-requirements/`; design and verification go in `architecture/` and `verification/` respectively | Reuses the reference projects' SR/ABB/VT division of labor instead of mixing all specifications into one directory |
| `tasks/` implementation tasks | Delivery slices and implementation checklists in `user-stories/` | Reuses US; maintenance items that do not fit a user story use an issue/PR instead of being forced into a user-value narrative |
| `docs/architecture.md`, `docs/decisions/` | `architecture/README.md`, `architecture/decisions/` | Adopts the reference projects' architecture directory; the central location for architecture decisions in a single repo is our own choice |
| Scattered `_template.md` files | `_templates/items/` | Reuses the reference template directory and its `items` organization, as local files rather than a submodule |
| Development and takeover records | `logs/`, `docs/development.md`, `docs/agent-support.md` | Kept as our own addition; existing evidence does not show that the reference projects use the same log or guide paths |
| Source code and test layout | `src/README.md` | `src` is the container for user projects; the `src/tests/` from the historical reference is not pre-created, and test paths follow the downstream tech stack |

The naming basis comes from earlier research and the path records of the initial blueprint; see the [directory-naming adoption record in the source register](../research/source-register.md). Borrowing directories does not mean inheriting source code, enforcing full DDD, or making the reference projects a runtime dependency.

## 3. Minimum content of project materials

| File or directory | Minimum content |
|---|---|
| README | Project goal, current stage, staged setup checklist, a human entry point for finding shared methods/forms/artifacts by activity, and the template source version |
| AGENTS | Short navigation, per-task reading rules, missing inputs and stop conditions; first link the existing materials, then connect the skills in P2 |
| Domain model | Shared terms, core concepts and their relationships, business rules, bounded context responsibilities and interactions, fact sources and open items; see the next section for the detailed filling requirements |
| Stakeholder requirement (REQ) | The business entry point takes over the PRD's goals and scope; the form records the source, related domain rules/contexts, status, business requirements, and business acceptance criteria; create `REQ-001-<slug>.md` when needed |
| Software requirement (SR) | Upstream REQ or explicit task basis, owning context, software behavior, boundaries and error cases, acceptance criteria qualified with the owning artifact identifier, and necessary interface agreements |
| User story (US) | Delivery slice, requirement links, change scope, implementation checklist, status, and record links; it is neither a second copy of the requirements nor a mandatory layer between requirements and VT |
| Verification specification (VT) | Verification layer and targets, acceptance references each qualified with its owning artifact, steps/test identifiers, expected results, actual results with baseline references, and result applicability; it does not store test code |
| `verification/README.md` | A coverage index for finding the acceptance criteria and VTs of the current delivery scope, listing gaps and the checked baseline explicitly; relationships and results are read from their sources, with no separate copy of pass status |
| Development log | Task, date and session identifier, branch or baseline, changes, verification, blockers, next steps |
| Architecture (ABB) and ADR | Current structure, related requirements and business boundaries, necessary design constraints and their verification basis, rationale and consequences of choices; not every task is required to add a design artifact |
| `src/README.md` | How to place any kind of project, keeping its native layout, and the requirement to register development commands once a project is created; contains no sample application |
| Development guide | Initially explicitly not configured; later records, per subproject, the relative path, environment, dependencies, install/build/run/test commands, working directory, and troubleshooting entry point |
| Agent support guide | GitHub Copilot App as the first test target, entry points and skill locations, discovery/usage results recorded per client and version, limitations, and how to read files manually; initially not marked as tested |
| `.gitignore` | Minimal generic ignore rules that do not ignore formal artifacts or development logs; downstream projects extend them for their real tools, with no prebuilt full language configuration |
| PR form | Task basis, change scope, actual verification, open items and limitations; pass, approved, or released are not checked by default |

While no tech stack is chosen, the development guide explicitly says it is "not yet configured"; this does not block use of the skeleton. Complete it after the user decides to create a concrete project, and do not provide an empty test script that looks successful. The required inputs for first-time setup and the items that may stay open are listed in [P0 decision D09](../plan/decisions-and-risks.md). Placeholder filling hints in document templates are normal, but before a task starts you must identify which facts are still undetermined.

Formal files can use readable names such as `SR-001-<slug>.md`, `US-001-<slug>.md`, `ABB-001-<slug>.md`, and `VT-001-<slug>.md`. Numbers are assigned only when the corresponding artifact actually needs to be created; do not invent requirements to complete a traceability chain, and do not carry sample approval statuses into a new project. A PRD still serves as the product description; do not simply equate a whole PRD with a single REQ.

Development logs are committed to the repository and hold only the necessary summary and links to raw reports. Application runtime logs, full chats, credentials, personal absolute paths, and output containing sensitive data are not committed; configure the project's `.gitignore` according to the real tools' output directories.

### 3.1 Minimum filling requirements for lightweight DDD

P1 provides the following sections and filling guidance in the established `domain-model/README.md`, and P2's `define-requirements` works to the same requirements; no eighth form type and no new modeling agent are added.

| Content | Questions it must answer |
|---|---|
| Shared terms | What does this term mean in the current context? Does a concept with the same name mean different things in different contexts? |
| Core concepts and relationships | Which important objects, behaviors, or states exist in the business, and how are they related? Do not just list nouns without explaining the relationships |
| Business rules and invariants | Which conditions must hold, which behaviors are forbidden, and within which scope does each rule apply? Rules are referenced by a stable section or identifier |
| Bounded contexts | What is each context responsible and not responsible for, and which business facts does it maintain? Directory names or technical layers cannot replace business responsibilities |
| Context interactions | Which side provides what business information or capability, and which agreement does the other side depend on? Business boundaries need not map one-to-one to repos, services, or `src` subprojects |
| Sources and open items | Which facts has the user given, and which content is inferred or to be confirmed? How do the related REQs/SRs locate their business basis? |

The initial skeleton provides only guidance and does not prefill a business model; business-related tasks fill in or reference the existing model within the current scope. When one context is enough, do not split it artificially; pure documentation maintenance and tasks that do not involve the business state why the model is not applicable instead of fabricating one. Entities, value objects, aggregates, the repository pattern, and code layering are adopted as actually needed; they are not an implementation form mandated by the template.

### 3.2 Traceability carriers and single source of truth

The number of forms stays at seven: REQ adds business acceptance and model references, SR adds its upstream basis, and VT makes explicit the verification layer, target acceptance criteria, run baseline, and result applicability. Each acceptance criterion reference includes the owning artifact and a stable identifier; model rules also have locatable sections. US only organizes delivery; ABB/ADR take part in design traceability as needed and are not created just to complete the chain.

`verification/README.md` builds its navigation from the list of acceptance criteria in the current delivery, including those that have no VT yet; do not just collect the existing VTs and then claim complete coverage. SR stores its upstream references and VT stores its target acceptance references; reverse relationships are checked through these references and search, without manually maintaining a copy on each end. The index provides only links, gaps, and the checked baseline; acceptance text, relationships, and results remain governed by the owning artifacts.

How business acceptance, software behavior verification, and applicable design verification correspond, and how gaps, dangling references, change impact, and old results are handled, are designed uniformly in [sections 3–4 of the working conventions](execution-contracts.md). P1 implements the fields and filling constraints in the forms and directory guides, and P2 implements the operational steps in the existing skills; downstream projects do not replace this content with links to this repository's undistributed design documents.

## 4. Copilot first, without duplicating rules

| Entry point | Intended use |
|---|---|
| `AGENTS.md` | Common rules and material navigation; does not depend on a specific model, personal settings, or hidden sessions |
| `.github/copilot-instructions.md` | Copilot repository-level guidance that requires reading the common rules and the current task's materials |
| `.github/instructions/*.instructions.md` | Scopes specialized rules with the client-supported `applyTo` patterns |
| `.github/agents/*.agent.md` | Selects a working mode; the main content references a skill, and tool restrictions are verified per client |
| `.github/skills/<name>/SKILL.md` | The single body text of an activity method; references the `_templates/` forms and states the formal artifact directory |
| `.github/prompts/*.prompt.md` | Supplies the current task input and points to the corresponding method; does not hold the only copy of the workflow |

GitHub's official documentation lists several skill directories; this design chooses only `.github/skills` as the maintained location so that Copilot can use it natively. When other clients do not discover it automatically, read the target `SKILL.md` explicitly; confirm an actual need before adding other entry points, to avoid three bodies of text drifting apart under `.github`, `.agents`, and `.claude`.

Links between AGENTS and the Copilot entry points do not guarantee automatic loading. The first release needs to verify that Copilot actually read the task requirements and related rules, not merely that the files exist. A client may ignore unrecognized tool names in a custom agent, so do not infer from the names that a restriction is in effect.

Prompt files are optional convenience entry points. Where GitHub.com and Copilot CLI do not currently support the IDE prompt-file experience, specify the task and the corresponding skill directly in natural language; the core process does not depend on slash commands, specific variable expansion, or client handoff features.

These locations and limitations come from the [official GitHub sources Q1–Q4](../research/source-register.md) consulted on 2026-10-13; they do not mean the template has passed client compatibility testing.

**GitHub Copilot App** has been selected as the first client to test. The App's entry-point discovery, metadata, and tool-configuration support must be tested in practice separately and cannot be inferred from VS Code or Copilot CLI. The 5 prompt files remain optional convenience entry points and are not required App functionality; where they are unsupported, name the skill in natural language. Native discovery, explicit reading, and unverified status must be recorded separately.

### Specific responsibilities of first-release capabilities

Method text is maintained only in the 6 skills below; filling in forms still references `_templates/items/`, with no separate sample application or scripting tool layer.

| Skill | Input | Output and boundaries |
|---|---|---|
| `project-onboarding` | Current repository state; project goals and constraints provided by the user | Completes the setup items that can be confirmed and records the rest as open items; does not automatically choose a tech stack, install dependencies, or initialize a `src` project |
| `define-requirements` | Goals, users, scope, and business facts provided by the user | Works out the model, rules, and boundaries following the lightweight DDD guidance, and produces draft REQs traceable to their sources, with business acceptance; clarifies missing facts first |
| `specify-feature` | Model and existing requirements or an explicit task; current structure and constraints | Reuses the existing basis, produces SR acceptance criteria and corresponding draft VTs as needed, and lists coverage gaps; creates US and ABB/ADR as needed, without automatic approval |
| `implement-task` | Explicit task and change scope; coding also needs a concrete project and a real development guide | Checks the related business basis and verification plan before implementing; handles the impact of model or requirement changes first; does not create an application on its own when development inputs are missing |
| `verify-change` | Complete list of acceptance criteria for the current delivery, the changes, related VTs, and results | Checks coverage, dangling references, and baseline applicability in both directions, then runs the applicable checks; keeps document-check results separate from software-behavior results, and must not disguise gaps as passes |
| `record-handoff` | Task, Git status, affected artifacts, actual results, gaps, and blockers | The log references the current baseline and the items pending re-review or not run; on takeover, recheck facts and traceability first, and do not treat old results as current results |

The three agents only define working modes: `planner` references the onboarding, requirements, and specification methods; `implementer` references the implementation, verification, and handoff methods; `reviewer` references the verification method. The model is inherited from the user's settings; a tool scope can be described as an effective restriction only after it has been tested in practice in the App, and the reviewer is not treated as a human approver.

| Optional prompt | Referenced methods |
|---|---|
| `start-project.prompt.md` | `project-onboarding` |
| `plan-feature.prompt.md` | `define-requirements`, `specify-feature` |
| `implement-task.prompt.md` | `implement-task`, `verify-change` |
| `review-change.prompt.md` | `verify-change` |
| `resume-work.prompt.md` | The takeover check of `record-handoff`, then a method chosen for the current task |

Repository-level instructions provide guidance; `docs.instructions.md` covers documentation facts, status, and references; `tests.instructions.md` covers actually running test changes and mapping them to acceptance, without presetting a language, test directory, or commands. P2 sets the path scopes according to the target client's conventions and explains in the common entry point how to read the rules explicitly; when a downstream project changes its layout, adjust the scopes accordingly, and do not claim that generic patterns cover any tech stack.

### Entry points shared by humans and agents

The formal README provides "What do I need to do now?" activity navigation that lists the required inputs, shared methods, forms, and formal artifact locations. Humans can read the steps in `SKILL.md` directly and fill in the forms by hand, while agents enter the same method from `AGENTS.md`; both follow the same fact sources, traceability requirements, completion conditions, and stop conditions. Not using an agent or prompt shortcut commands does not affect the method's usability.

P1 first provides entry points to the existing materials and forms; P2 connects the activity navigation to the six created skills. Skill text uses steps that humans can execute; it does not make a specific agent role or a dedicated tool call a mandatory step, and it does not duplicate a separate "manual workflow". Prompts only add the input for the current run and cannot change a method's acceptance standards.

## 5. First-time setup and daily use

1. Create a repository from the prepared formal template, or merge the needed files into an existing project.
2. Following the README, fill in the project goals and scope that the user has confirmed; the onboarding skill can help. An unselected tech stack and commands stay not configured, which does not hinder work on project materials.
3. When the user decides to start coding, the user creates a concrete project in `src/` or explicitly asks an agent to do so; use the native tools of the chosen tech stack, register the actual paths, commands, and verification results, and do not automatically apply a prebuilt application.
4. Open GitHub Copilot App and choose a working mode that is actually available, or describe the task directly; other agents first read `AGENTS.md` explicitly.
5. Refine the domain and business requirements as needed, elaborate SR/US, and record architecture and verification in the corresponding directories; after development, update the log and handoff. When a PR is needed, use the existing client and platform capabilities.

Using project tools and the off-the-shelf Copilot CLI does not contradict the "no home-grown CLI" positioning. Nor does the template require any extra global skill installation, MCP service, or personal knowledge base to complete the basic process.

## 6. Copying, merging, and updating

Once a new project copies the template, the files are maintained by that project. Template updates provide only versions, diffs, and change notes, which users review and merge; there is no `ans upgrade`, no generator-managed file category, and no background sync.

An existing project should first inventory its README, AGENTS, Copilot configuration, skills, and documentation locations, and then merge selectively. On conflict, keep the original content and list the differences explicitly; do not overwrite existing rules, and do not automatically migrate historical PRDs, tasks, or code.

A Git tag/release records the template version, and the README only needs to record the source used. Application dependencies continue to be managed by the project's native dependency manifests; `agent.yaml`, `agent.lock.json`, and `.agent-state` are no longer added as required files.

## 7. Items to handle before releasing the template

The current research directory contains internal project summaries; at release they must be separated and reviewed, and must not be copied or published along with the business template. Distribute only the skeleton files listed in this blueprint and written for downstream use, without a sample application.

Prepare a clean candidate from the specific file manifest; do not copy the whole current repository and its history, and do not carry this repository's research, design, implementation plans, maker logs, or exercise outputs to downstream projects; links in the release candidate must not depend on this excluded content. For the handling boundaries and pre-release decisions, see [P0 decision D01](../plan/decisions-and-risks.md).

Setting the repository as a GitHub template and configuring visibility, branch protection, CI permissions, and the license are all separate release operations; they are not completed automatically because design documents or template files exist. This round completed local production and a limited documentation exercise; these release operations were not performed.

## 8. Authorized six-repository functional enhancement

The execution request of 2026-10-15 extends functionality beyond the original 38 files; the responsibilities and dependencies of the new files are governed by the [enhancement plan](../plan/2026-10-14-ddd-functional-alignment.md), and their sources by the [six-repository capability matrix](../research/ddd-capability-matrix.md). The counts above and the "deliver only minimal modeling" convention are kept as the historical scope of the completed first release; files in the new plan are not treated as already existing.

The enhancement permits more domain/QAS/tactical/governance forms, nine shared methods with thin prompts, data schemas, and Python utilities run on demand. Optional domain-source integration does not require submodules; body text, relationships, run results, and derived views each keep a single source. Media, diagram/document export, and interaction ledgers each have their own task and authorization boundaries, and do not bring back a general-purpose executor or background service.

Task12 froze the exact inventory based on the actually delivered files; source-code research, the maker matrix, plans, real session/client results, logs, test/exercise material, and Git history still do not go downstream. The candidate and local checks are not release authorization; the core documents can still be read without installing the maintenance tools, and the business stack/application continues to be decided by the user.
