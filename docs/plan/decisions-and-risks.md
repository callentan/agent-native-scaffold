# Confirmed Direction, Pending Details, and Capability Boundaries

**Updated: 2026-10-14. P0 has been realized as P1/P2; the P3 local document exercise, core integration in the real App, methods/roles, and Git takeover have been recorded; the remaining entry-point, human, and release confirmations are still outstanding. The [acceptance record](roadmap.md#actual-acceptance) is authoritative for the actual scope.**

## 1. Confirmed direction (2026-10-13)

The user has made clear that the existing repos are only references and that the goal is to build our own development skeleton; the deliverable is a repo template plus Agent capability files, with no custom CLI; directory naming still follows DDD and the examples in those repos.

This round further confirmed: the first client to test is **GitHub Copilot App**; the deliverable is a repo with a predefined skeleton, and users create projects of any type inside `src/` themselves; the first release accepts only the skeleton, Agent entry points, document workflow, and handoff. It does not require creating or integrating a real business project, and no throwaway application-project exercise is planned.

Following the goals and reinforcement requirements the user raised afterwards, the first release further specifies: **DDD owns the business model and boundaries, the V-model owns traceability from requirements to verification, and prompts/templates work with shared skills so that humans and Agents follow one workflow.** These three points become requirements for file content and phase acceptance, not merely reference names; the document-only exercise must cover the model, traceability gaps, and change impact, but still creates no application.

The current direction is therefore:

- The project side is organized by domain model, stakeholder requirements, software requirements, user stories, architecture, and verification, and keeps development logs and a development guide.
- The Agent side contains a generic entry point, instructions, custom agents, skills, and prompts.
- GitHub Copilot App is the first interface to test; other Agents that can read repository files integrate through the generic content, and native support is recorded per client.
- `src/` ships with usage notes only, with no application code, dependency manifest, lock file, fixed test directory, or tech stack; downstream projects decide these.
- Reference directory names are adopted, but cloning or mounting the reference repositories is not required, and nothing depends on their source code, access permissions, or business models.
- Development uses existing Agents and project tools; the template itself has no execution, isolation, approval, or release capability.

"Any Agent can integrate" is a goal of reusable files and workflow, not a fact that every client supports the same native configuration. Specific compatibility records must distinguish results verified in practice, those based on official documentation, and those that are unverified.

See the [template blueprint](../design/repository-blueprint.md) for the current directory plan: the purpose of a PRD is carried by the stakeholder requirement documents, software specifications are split across SR/architecture/verification, and delivery tasks go into a US's implementation checklist; forms are gathered in `_templates`. `logs` and the development guide are our own additions. Reusing these names does not mean every small task must produce the full DDD/V-model artifact set, and it does not change the CLI-free, Copilot-first product shape.

## 2. Designs removed from the previous version

These items are no longer implementation tasks for this project's first release, nor are they phases to be built by default once the template is done.

| Previous-version item | Current handling |
|---|---|
| Python/Typer skeleton CLI, `ans` command group | Removed; start from a template repository or by copying files, and use native project commands |
| Context Builder, unified artifact-parsing core | Replaced by short entry points, relative links, clear document responsibilities, and on-demand reading |
| `agent.yaml`, `agent.lock.json` | Not required configuration; project notes, native dependency manifests, and the template source version each serve their own purpose |
| SQLite state store, execution state machine, automatic recovery | Replaced by tasks and development logs; the next session checks Git state and then takes over |
| Custom verifier, approval service, trusted publisher | Reuse project tests, existing CI, client permissions, and platform review; no promise that the template enforces anything by itself |
| Automatic upgrades, cross-repository report sync | Normal Git diff and review; design separately once a concrete collaboration need appears |
| Method/assurance/stack package-management system | Provide the necessary documentation and rules first; do not build a pluggable framework up front |

The lessons kept are: facts are locatable, tasks are scoped, verification is real, records support takeover, and rules are not duplicated. The over-extended software platform built to achieve these goals is not kept.

## 3. P0 decision record

### 3.1 First-release scope baseline

D03 and D04 record the user's chosen client and delivery boundary; D10–D12 record this round's method and acceptance reinforcements; the directories and file count in D02 stay unchanged. The [template blueprint](../design/repository-blueprint.md) is authoritative for file responsibilities and the [implementation plan](roadmap.md) for acceptance; no separate lists are maintained in multiple places.

| ID | Decision | P0 conclusion | Status and boundary |
|---|---|---|---|
| D01 | Template content and release | Downstream repo roots use the blueprint layout; distribute only the skeleton files written for downstream use, without copying this repository's research material or Git history | Content boundary settled; license, release location, visibility, version, and maintainers are confirmed before release |
| D02 | First-release file and capability list | Fix the blueprint's project-material entry points, seven form types, 6 skills, 3 agents, 5 optional prompts, plus Copilot instructions and the PR form | Settled; no new roles, generators, sample applications, or tech-stack packs |
| D03 | First Copilot interface to test | GitHub Copilot App; record the actual App version and runtime environment, and observe entry-point discovery and file reading item by item | Limited core results from the real App exist; the other entry points are unverified, and compatibility conclusions from other clients are not carried over |
| D04 | `src` and first-release acceptance scope | `src/README.md` explains how to put any project in place; the first release accepts only the skeleton, entry points, document workflow, and handoff | Settled; replaces the original "choose a synthetic project and tech stack" decision; `src/tests/` is not pre-created, and no application coding exercise is required |
| D05 | Formal review, CI, and permissions | The first release preconfigures no business CI, approval, or release configuration; downstream projects configure their existing platforms for the actual project | Default boundary settled; the permissions and review arrangements needed for a formal release are confirmed separately by the maintainers |
| D06 | Entry points for other Agents | The first release provides only `AGENTS.md` and a path for explicitly reading the same skills, with no client-specific copies | Settled; dedicated thin entry points are added later only as practical testing shows a need |
| D07 | Reuse of external material or templates | The first release writes generic content independently, borrowing only existing names and methods, without carrying over reference source code, templates, or branding | Settled; future reuse requires separate confirmation of authorization and source |
| D08 | Specialized domain or regulatory documents | The first release adds no specialized domain, regulatory, or full V-model document suite | Settled; when a real need arises, the accountable owner confirms it; no compliance qualification is claimed |
| D09 | First-time setup and coding prerequisites | Browsing and using the skeleton does not require choosing a tech stack; formal project material and coding each check their own required inputs | Settled; missing values are marked explicitly; detailed rules are in the table below |
| D10 | Minimum requirements for lightweight DDD | The existing domain entry point provides guidance for terms, concept relationships, rules, context responsibilities/interactions, and sources; requirements can locate their business basis | Settled; no new forms or agents; aggregates, repository patterns, or a one-to-one mapping between business boundaries and code directories are not mandated |
| D11 | Minimal V-model traceability | Distinguish business acceptance from software verification; for the acceptance criteria of the current delivery, check coverage, dangling references, change impact, and result applicability | Settled; US is not a mandatory layer; no new database and no duplicated bidirectional facts; a complete mapping is not passed off as verification passing |
| D12 | Shared human/Agent method and semantic acceptance | README gives humans the same skills/forms entry points; P3 uses fixed document inputs to check the model, traceability, rule changes, and takeover | Settled; no application is created; the human path must actually be recorded, and Agent simulation or not-run results cannot be passed off as verified |

"Should we have our own CLI?" and "Which framework state database should we choose?" are no longer listed as pending decisions. If the first-release scope needs to grow or shrink, update this baseline and the blueprint first; do not expand it implicitly during implementation.

<a id="distribution-boundary"></a>
### 3.2 Maker-side and distribution boundary

- P1/P2 build the skeleton files in this repository; the target layout maps directly to a downstream repo root and requires no installer package, generator, or extra runtime layer.
- The release candidate is built by copying the specific files listed in the blueprint, one by one, into a clean directory; project-material directories initially contain only filling instructions, and `src/` contains only a README. Do not copy the current `docs/`, `.github/`, or `logs/` as whole directories.
- This repository's `docs/research/`, `docs/design/`, `docs/plan/`, maker-process logs, exercise outputs, and `.git` history never go downstream; downstream files must not link back to this undistributed material. The README and development guide named in the blueprint are the versions P1/P2 write for downstream use, not verbatim copies of the current design documents.
- The current research repository is not turned directly into a public template. Release happens only in an authorized way, after the content and authorization review is complete and the release items are confirmed; this round does not create a remote repository, change visibility, set the template flag, or choose a license.

### 3.3 Inputs needed for first-time setup

| Usage stage | Required inputs or checks | Content that may stay open | Where to record and when to stop |
|---|---|---|---|
| Browsing and copying the skeleton | Files can be read; when merging into an existing repo, first check directories, Git state, and existing rules | Project name, business goals, tech stack, and commands may all remain unfilled | README shows the not-yet-set-up state; merely browsing or merging the skeleton is not blocked by an unselected tech stack |
| Filling in formal project material | The user provides the project name, goals, users, current scope, and known constraints | Features, architecture, and release details outside the current scope; missing facts are marked to be confirmed | Goals and scope go in the stakeholder requirements entry point, terms in the domain entry point; gaps that affect current requirements are clarified first, never invented |
| Starting a task | A clear user request, US, or issue, with a change scope and observable completion criteria | Other artifacts unrelated to this task; completing the whole traceability chain is not required | The task references existing basis; unconfirmed requirements stay draft and are not automatically recorded as approved |
| Creating or changing a project in `src/` | The user has chosen the project type/tech stack; confirm the target subdirectory, existing project conventions, environment and dependencies, and the actual install, build, run, and test methods | Inapplicable steps may be annotated with a reason; missing commands must not be disguised as empty scripts that succeed | Record the relative path, working directory, and commands per subproject in `docs/development.md`; without these inputs, record only the gaps and do not choose a stack or generate an application automatically |
| Verifying a code change | Acceptance basis, actual commands, and an available environment; run with the real tools and record the results | Checks that cannot be run are explicitly marked `not-run` with a reason and are not treated as passing | Results belong in verification records, and logs only reference them; a skeleton without an application does not claim build or test success |
| Pushing, releasing, or changing permissions | User authorization for that operation; a formal release also requires confirming content, license, visibility, version, and maintainers | Unconfirmed release items do not block local building or authorized development collaboration, but release operations that depend on them must not be performed | Use existing platform mechanisms; do not infer authorization from the template's existence or an Agent's own claims |

Filling hints in the template are not downstream project facts. First-time setup does not automatically run project-initialization commands such as `npm init` or `dotnet new`; once the user decides to create a specific project, it is handled with the native tooling of the chosen tech stack.

### 3.4 P0 exit and follow-up decisions

P0 has settled file responsibilities, the first client to test, the `src` boundary, input requirements, and how materials are handled, and has reinforced lightweight DDD, minimal traceability, and the shared human/Agent method. P1 builds the skeleton to these content requirements, P2 connects the methods, and P3 runs the document-only semantic exercise; completing P0 does not mean the template exists or that any scenario has passed.

The license, release location, visibility, version, and maintainers in D01, and the permissions and review arrangements needed for a formal release in D05, are left to be confirmed before the P3 release. They do not block building the skeleton locally, but nothing may be distributed externally or released until they are confirmed; support for other clients must not be marked as verified in advance either.

## 4. Risks and responses

| Risk | Concrete symptom | Response |
|---|---|---|
| Directories only, no usage method | A new project still has to ask from scratch how to get started | The template includes filling hints, a startup checklist, and matching skills, exercised with skeleton document tasks |
| Binding a tech stack for the sake of exercises | The first release sneaks in a sample application, fixed test directory, or install commands | `src` keeps only notes; skeleton acceptance is separate from downstream application verification |
| Excessive documentation burden | Every small fix requires a new PRD, spec, ADR, and log | Choose only the artifacts each task needs and reuse existing basis |
| DDD reduced to terms and directories | Concept relationships, rule ownership, and context responsibilities cannot be explained | Set minimum filling requirements in the existing domain entry point and the requirements skill, and check boundaries with document scenarios |
| Links without closed-loop traceability | Requirements without a VT, dangling targets, or old results applied to new requirements go unnoticed | Check coverage from the acceptance-criteria list, trace VT targets back, and handle change impact by baseline; do not equate coverage with passing |
| Human and Agent workflows diverge | Humans can only read forms while Agents follow a separate set of implicit steps | README and AGENTS point to the same skills; record the actual human and App paths separately |
| Duplicated or conflicting rules | AGENTS, instructions, agents, and prompts each hold their own copy of the workflow | Method text stays in skills, project facts only in project documents, and entry points use references |
| Directories renamed but responsibilities not adjusted | The same specification lives in several directories, or maintenance tasks are forced into user stories | Define clear locations for REQ/SR/US/ABB/VT and use the same mapping in entry points and skills; maintenance tasks can keep using issues/PRs |
| False compatibility | Claiming every Agent loads the files just because they exist | Distinguish generic reading from native discovery, record the client and version, and verify in practice |
| False security | Claiming sandboxing, approval, or budget control merely because "no overreach" is written down | Rely on the actual host and platform configuration, and state the template's capability boundary clearly |
| False completion | The log says passed, but there is no real result or matching version | Record actual commands, results, and reports; mark anything not run as not run |
| Stale or leaking logs | A new session blindly trusts old progress, or full chats and sensitive output are committed | Check Git first when taking over; logs keep only the necessary summary and never store keys or private runtime data |
| Merge breaks the original project | The template overwrites existing instructions, documents, or source code | Compare before merging; on conflict, keep the existing content and report it |
| Reference material distributed by mistake | Internal research summaries are copied into a public business template | Separate and review before release; distribute only our own or authorized content |
| Drifting back to platform building | Adding parsers, services, and configuration for every working convention | Prefer plain files and native tools; any new program needs a clear usage need |

## 5. Current work scope

P1 has built the project-material entry points and seven form types; P2 has connected six skills, three agents, five optional prompts, and the instructions; `src` still contains only notes. P3 has run the modeling, traceability, independent-fault, rule-change, and generic-agent takeover exercises in a copy that excludes research material; no exercise business facts or check helpers were left in the formal template.

P3 is not complete as a whole. This round authorized a standalone local Git test project; four real App sessions completed fresh onboarding, loading of six project methods, three API working modes, and Git takeover; the conflicting-merge preflight kept all original text. Automatic path matching, GUI/optional prompts, the human comparison, and release confirmation remain unverified; the human path is deferred to later at the user's choice. No business tech stack was chosen, no application was created, not every client was tested, and no release was announced; see the [implementation plan](roadmap.md#actual-acceptance) for scope and evidence limitations.

The original research facts and sources are kept, but a custom executor is no longer a product requirement. The official basis for Copilot file conventions is registered in the [integration notes](../agent-support.md#official-sources) and still kept separate from actual client observations. Records of naming adoption are not evidence that the reference repositories were re-verified, and local exercises do not imply that native entry points have passed.

No reference repository was modified, no new remote repository was created, visibility and the template flag were not changed, and no auto-merge, deployment, or other permissions were enabled.

## 6. Planning decisions for the six-repo functional enhancement (2026-10-14)

The user asked for a plan covering the functional gaps described above and chose to:

- Align with the existing capabilities of the six `ddd-*` repositories by functional equivalence, keeping the single-repo model and downstream tech-stack neutrality, without requiring direct compatibility with the original formats.
- Implement maintenance tools as in-project Python scripts; on 2026-10-15 the user further confirmed that scripts are essentially unified on Python, replacing the previously required PowerShell Windows wrapper entry points. No custom CLI, executor, or business application is reinstated.

The [enhancement specification](../design/ddd-functional-alignment.md) is the basis for the concrete design and acceptance. After the user authorized execution on 2026-10-15, a full inventory of the six repositories found items missing from the original plan; the user confirmed including all of them, and the [enhancement plan](2026-10-14-ddd-functional-alignment.md) grew to 18 tasks with dependencies. A completed source inventory does not mean the new forms, structured views, tools, or pipelines have been implemented.

The capability inventory reads only pinned sources; it must not copy internal source code or count upstream roadmap items as existing capabilities. Choosing Python for the tools does not determine the language of business projects; application acceptance, hook installation, CI gates, propagation/PRs, and release still each need their scope and permissions confirmed separately. The original P3 human comparison, path/GUI/prompt observations, and release gaps are not inferred to pass from this planning.

Repeatable logic for local runs, hooks, and CI reuses the same Python implementation; CI YAML still carries the host-native declarations, no separate PowerShell validation/update logic is written, and PowerShell 7 is not required to use the tools. A thin launch adapter is kept only where a host genuinely needs one; methods and judgment remain in the shared skills, so this does not become a custom execution flow. This implementation strategy does not prove that every planned script is an existing upstream capability; source alignment and new automation are checked separately in Task 1.

### 6.1 Execution-phase scope baseline (2026-10-15)

See the [capability matrix](../research/ddd-capability-matrix.md) for the full sources and per-file classification. Confirmed additions cover QAS/tactical models, SEQ/Gherkin/SWAS, glossary/Published Interface evolution, optional domain-source integration, document/transcript/audio adapters, diagram/PDF/presentation export, and interaction accounting. The sources do contain a PowerShell submodule installer and more Python utilities, so the simplified judgment based only on old summaries cannot be carried over.

The "seven forms, six methods, no structured tools" of D02/D08/D10/D11 remain the original first-release delivery boundary but no longer limit the authorized enhancement file list. The enhancement uses nine shared methods and allows data contracts, Python tools, and optional tactical/regulatory material that have a clear purpose, without forcing lightweight projects to use every artifact. The original three roles, single repo, no-application default, and non-autonomous approval boundary are unchanged.

Contradictions in the original repositories, such as a read-only model that still requires write-back/push, baseline/demo fallbacks, and installers that commit implicitly, are not features that must be copied; they are replaced by pinned sources, explicit failures, read-only views, and separate authorization. The source, target task, and acceptance of each new tool are traced back to their sources separately, and our new automation is not called an existing upstream capability. Dependencies, data transmission, and execution for audio/PDF/external platforms require separate authorization; "full inclusion" does not automatically run services or modify remotes.
