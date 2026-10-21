# Overall design: repository template and Agent capability files

**Updated: 2026-10-14. The P1/P2 template files have been produced according to this design; for the local P3 results and the outstanding App, manual, and release items, see the [actual acceptance record](../plan/roadmap.md#actual-acceptance). This document replaces the earlier proposal centered on a CLI and an execution coordinator.**

## 1. The deliverable is a set of repository content

`agent-native-scaffold` provides our own R&D repo skeleton. Users who receive it do not need to start a framework process or register an Agent; they can use the client they already have to read project materials, choose a working method, and carry out tasks. The GitHub Copilot App is the first interface tested, and support for its entry points must be recorded separately.

The template gives a project a stable place to work: where requirements live, what the implementation is based on, how it is verified, how far the work has progressed, and how another Agent can continue. It contains both engineering document templates and Agent working conventions; it must not shrink to a set of empty directories or prompts.

The core division of labor is: **DDD owns the business model and its boundaries, the V-model owns traceability from requirements to verification, and templates, skills, and prompts unify the workflow of humans and Agents.** Adopting a lightweight method means more than adopting directory names; the first version must provide fill-in and operating conventions for minimal modeling, traceability, and change impact.

The reference projects provide experience. As the user chose, directory and artifact naming follows their clear, familiar conventions; their business content, tech stacks, ADRs, and roadmaps do not thereby become our requirements. Adopting directory names does not mean copying implementations or inheriting multi-repository dependencies.

## 2. Two content groups, one set of project facts

| Content group | What it contains | Maintenance principle |
|---|---|---|
| Project materials and records | Domain model, stakeholder and software requirements, user stories, architecture, verification, and development logs | The content belongs to the project; record real requirements and results, and do not invent business facts just to fill in templates |
| Agent capability files | Common entry point, Copilot instructions, custom agents, skills, prompts | Explain how to use the project materials; do not duplicate a second set of requirements, progress, or acceptance criteria |

The skeleton's `src/` contains only usage notes; users may create any type of project in it. It does not preset business code, language projects, dependency manifests, lock files, or a fixed test directory. Source code, tests, and dependency manifests later follow the native conventions of the tech stack chosen downstream, and existing projects keep their original layout. The template does not become a production dependency of the business application.

## 3. Each document has its own job

| Location | Question it answers | Responsibilities it does not take on |
|---|---|---|
| `domain-model/` | What the business concepts and their relationships, the shared terminology, the rules, and the context responsibilities and interactions are | Does not mix in implementation code; does not equate business boundaries with directories, services, or technical layers |
| `stakeholder-requirements/` | Why it is built, for whom, and what the product scope and business requirements are | Does not duplicate every interface and implementation detail |
| `software-requirements/` | How the software should behave and which acceptance criteria it must meet | Does not record daily task progress |
| `user-stories/` | What the current delivery slice is, what it is based on, and what is still missing | Is not a mandatory layer between requirements and verification; does not equate all maintenance work with user stories |
| `architecture/` | How it is implemented, and what the current structure and key trade-offs are | Does not repeat product requirements |
| `verification/` | How business/software requirements are verified, what coverage gaps exist, and which baseline a result applies to | Does not equate complete links, verification specifications, or document checks with passing software behavior |
| `_templates/` | Which forms to use when creating these documents | Does not treat fill-in hints as formal requirements or facts |
| `logs/` | What was done, what was verified, why work paused, and how to take over | Does not pose as CI results; does not store all chats and run output |
| `docs/development.md` | Entry point for environment, dependencies, build, run, test, and troubleshooting | Does not invent runnable commands while the tech stack is undecided |

The PRD's product overview lives in the stakeholder-requirements entry point; functional specifications are organized by the responsibilities of software requirements, architecture, and verification. No second set of generic directories with the same content is maintained. A user story may list an implementation checklist; maintenance tasks unrelated to user deliverables continue to use issues or PRs. For detailed naming and single-repository adjustments, see the [template blueprint](repository-blueprint.md).

Connect this content with plain Markdown headings, relative links, and recognizable file names. An acceptance reference carries its owning REQ/SR or standalone maintenance task plus a stable identifier, so that `AC-1` in different files is not confused. An SR references its upstream basis, and a VT references its target acceptance criteria directly; reverse checks use references and search and are not forced through a US. For the minimum domain content, see the [blueprint](repository-blueprint.md); for traceability, coverage gaps, and change impact, see the [working conventions](execution-contracts.md). No artifact graph database, manifest, or lock is created.

Small changes use a light process: fixing a typo needs no new stakeholder requirement, and a clearly scoped defect can link directly to an existing SR/US and a reproduction record. Adopting DDD-style naming does not mean every change must create a new REQ, SR, US, ABB, and VT.

## 4. How the Agent entry points are organized

`AGENTS.md` holds the common navigation and shared working conventions and stays short. It points to product materials, the current task, development commands, relevant rules, and logs, without stuffing the full text of every document into the entry point.

`.github/copilot-instructions.md` is Copilot's native repository entry point; it explicitly requires reading the common entry point and the task-relevant materials first. It keeps only the necessary guidance and Copilot-specific differences, and must not rewrite a different set of completion criteria. Links are not an automatic inclusion mechanism; whether referenced files are actually read must be verified.

Path-scoped rules live in `.github/instructions/`, for conventions specific to documentation, tests, or a tech stack selected later. The common entry point must state where these rules are, so that non-Copilot Agents can also read them explicitly per task; do not assume other tools understand `applyTo`.

## 5. Division of labor between templates and Agent capability files

| Type | Purpose | Examples |
|---|---|---|
| Template | Artifact structure and fill-in hints shared by humans and Agents | REQ/SR acceptance criteria, VT targets and baselines, log references |
| Instructions | Conventions followed continuously within their scope | Do not invent requirements; preserve existing changes; actually verify before completion |
| Custom agent | A working mode chosen by the user, together with its tool scope | Planning, implementation, review |
| Skill | Method, inputs, steps, outputs, and exit criteria shared by humans and Agents | Modeling and requirements, specification and verification planning, implementation, change verification, handoff recording |
| Prompt | Shortcut entry point that carries the current task's input | Start a project, plan a feature, continue a task |

Agents do not need to form an automatically chained "virtual R&D department". A single general-purpose Agent can complete a whole task; a specialized agent is used only when role focus or tool restrictions add value. Its model selection inherits the user's settings by default, without hard-coding a vendor or model version.

Each skill's body is maintained once in `.github/skills/<name>/SKILL.md`, with references, scripts, or assets attached as needed; document forms consistently reference files in `_templates/`. Prompts and custom agents reference skills instead of each pasting the complete process. A capability entry point must also state which artifact directory its outputs are written to; formal requirements are not stored separately next to a skill or prompt.

The formal README provides human navigation by activity into the shared methods and forms; people follow the steps directly without needing an Agent service. AGENTS and prompts lead into the same methods and must not change business facts or completion criteria. P1 first connects the existing materials and forms, and P2 then connects the skills, without duplicating a separate manual version of the process.

Scripts are introduced only when a concrete check or project operation genuinely needs them; skills are not used to rebuild a hidden CLI or scheduler.

## 6. How "any Agent can plug in" is achieved

Compatibility has two layers:

- Common layer: any Agent that can read the repository can work through `AGENTS.md`, plain Markdown, and explicit project commands.
- Native-experience layer: uses the instructions, skills, agent selection, and prompt shortcuts that the client actually supports, covering Copilot first.

For clients without automatic discovery, explicitly ask in natural language for the entry point and the target skill to be read. If a dedicated entry point such as `CLAUDE.md` is needed, add a short reference for the actual client instead of duplicating the whole capability set. A chat-only model that cannot read files or run project tools is outside the scope of direct out-of-the-box use.

The official GitHub documentation checked this time supports project skill locations such as `.github/skills`, as well as custom agents in `.github/agents`. Prompt file support varies by interface, so VS Code shortcuts must not be promised for GitHub.com or Copilot CLI. For the basis, see [source register Q1–Q4](../research/source-register.md); documented support does not mean this template has been verified in practice in the corresponding client.

Choosing the GitHub Copilot App in P0 does not mean the App inherits all native capabilities of the interfaces above. P3 records native discovery, explicit reading, and unverified items separately; prompt files are an optional convenience entry point, and core work does not depend on the App discovering them.

## 7. Execution is left to existing tools

| Concern | Actual owner |
|---|---|
| Reading, planning, changing code, and running commands | The coding agent chosen by the user and its tools |
| Tool authorization, session control, and resource limits | The Agent client and the host environment |
| Build, lint, test, and running the application | The project's native toolchain |
| CI checks, PR review, and branch protection | The configured code-hosting platform and the maintainers |
| Progress and handoff summaries | The Agent or developer updates files from the templates; the next session re-checks them |

The template itself provides no execution loop, permission isolation, trusted publisher, or automatic recovery engine. A Git worktree can isolate file changes but is not a security sandbox for running arbitrary code. Branch protection, required reviews, and CI are not enabled automatically just because Markdown was copied.

The working conventions still require: stop and clarify when business facts are missing; record verification failures truthfully; never manufacture success by deleting tests or lowering acceptance criteria. Controls that must be enforced belong in platform, permission, and actual check configuration, rather than in a claim that a prompt is a security boundary.

## 8. Initialization, maintenance, and handoff

First use is done through a template repository or by copying files. The README provides a staged setup checklist, and the onboarding skill can help fill in project information the user has confirmed; the skeleton is usable even while the tech stack and commands remain not configured. Only after the user decides to create a concrete project is its tech stack identified or confirmed and its real paths and development commands registered; no language is chosen and no application is initialized automatically, and no custom initialization program is needed.

The development log records the task, branch or version, work done, verification results, blockers, and next steps. When switching sessions, continue from the task files, the log, and the current Git state; this is a readable work handoff, not process-level recovery, and it does not guarantee that external operations run exactly once.

The template is released by Git tag or release, and a project can record its source version in its README. Later updates are merged through normal diffs and review; business files are not overwritten remotely, and the reference repositories' HEAD is not tracked continuously.

## 9. First-version boundaries

The first version delivers a tech-stack-agnostic repo skeleton, project document templates, a common Agent entry point, and Copilot capability files. In a clean copy, acceptance of the entry points, lightweight modeling, requirement-to-VT traceability, gap discovery, rule-change impact, and takeover after a session switch consists entirely of document-only exercises. No application is created and no reference business project is integrated; application code, build, test, and CI are left downstream, and no language toolchain is claimed to be verified.

Out of scope: a custom CLI, coordinator, SQLite state store, custom agent manifest/lock, automatic upgrader, cross-repository sync, web console, or multi-Agent scheduling. Domain-modeling depth and additional requirements for regulated scenarios are decided per project need; the complete method process is not mandatory, but the business basis, verification mapping, and open items applicable to the current task are kept.
