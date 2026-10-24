# Overall design: repository template and Agent capability files

**Updated: 2026-10-14. The P1/P2 template files have been produced per this design; for local P3 results and the outstanding App, manual, and release items, see the [actual acceptance record](../plan/roadmap.md#actual-acceptance). This document replaces the earlier CLI- and execution-coordinator-centered proposal.**

## 1. The deliverable is a set of repository content

`agent-native-scaffold` provides our own R&D repository skeleton. Recipients need not start a framework process or register an Agent; the client they already have reads project materials, chooses a working method, and carries out tasks. The GitHub Copilot App is the first interface tested, and its entry-point support must be recorded separately.

The template gives a project a stable place for requirements, implementation basis, verification, progress, and how another Agent can continue. It contains both engineering document templates and Agent working conventions; it must not shrink to empty directories or prompts.

The core division of labor is: **DDD owns the business model and its boundaries, the V-model owns traceability from requirements to verification, and templates, skills, and prompts unify the workflow of humans and Agents.** Adopting a lightweight method means more than directory names; the first version must provide fill-in and operating conventions for minimal modeling, traceability, and change impact.

The reference projects provide experience. As the user chose, directory and artifact names follow their clear, familiar conventions; their business content, tech stacks, ADRs, and roadmaps do not become our requirements. Adopting names does not mean copying implementations or inheriting multi-repository dependencies.

## 2. Two content groups, one set of project facts

| Content group | What it contains | Maintenance principle |
|---|---|---|
| Project materials and records | Domain model, stakeholder and software requirements, user stories, architecture, verification, and development logs | Belongs to the project; record real requirements and results; do not invent business facts to fill templates |
| Agent capability files | Common entry point, Copilot instructions, custom agents, skills, prompts | Explain how to use the materials; do not duplicate a second set of requirements, progress, or acceptance criteria |

The skeleton's `src/` contains only usage notes; users may create any type of project there. It presets no business code, language project, dependency manifest, lock file, or fixed test directory. Source code, tests, and manifests follow the native conventions of the downstream stack, and existing projects keep their layout. The template does not become a production dependency of the business application.

## 3. Each document has its own job

| Location | Question it answers | Responsibilities it does not take on |
|---|---|---|
| `domain-model/` | Business concepts and their relationships, shared terminology, rules, and context responsibilities and interactions | Does not mix in implementation code; does not equate business boundaries with directories, services, or technical layers |
| `stakeholder-requirements/` | Why it is built, for whom, product scope, and business requirements | Does not duplicate every interface and implementation detail |
| `software-requirements/` | How the software should behave and which acceptance criteria it must meet | Does not record daily task progress |
| `user-stories/` | Current delivery slice, its basis, and what is still missing | Is not a mandatory layer between requirements and verification; does not equate all maintenance work with user stories |
| `architecture/` | How it is implemented; current structure and key trade-offs | Does not repeat product requirements |
| `verification/` | How business/software requirements are verified, what coverage gaps exist, and which baseline a result applies to | Does not equate complete links, verification specifications, or document checks with passing software behavior |
| `_templates/` | Which forms to use when creating these documents | Does not treat fill-in hints as formal requirements or facts |
| `logs/` | What was done and verified, why work paused, and how to take over | Does not pose as CI results; does not store all chats and run output |
| `docs/development.md` | Entry point for environment, dependencies, build, run, test, and troubleshooting | Does not invent runnable commands while the tech stack is undecided |

The PRD's product overview lives in the stakeholder-requirements entry point; functional specifications are split by the responsibilities of SR, architecture, and verification, with no second set of generic directories. A user story may list an implementation checklist; maintenance tasks unrelated to user deliverables use issues or PRs. Naming and single-repository adjustments: see the [template blueprint](repository-blueprint.md).

Connect content with plain Markdown headings, relative links, and recognizable file names. An acceptance reference carries its owning REQ/SR or standalone maintenance task plus a stable identifier, so that `AC-1` in different files is not confused. An SR references its upstream basis and a VT its target criteria directly; reverse checks use references and search, not a US. Minimum domain content: see the [blueprint](repository-blueprint.md); traceability, coverage gaps, and change impact: see the [working conventions](execution-contracts.md).

Small changes use a light process: fixing a typo needs no new stakeholder requirement, and a clearly scoped defect can link directly to an existing SR/US and a reproduction record. Adopting DDD-style naming does not mean every change must create a new REQ, SR, US, ABB, and VT.

## 4. How the Agent entry points are organized

`AGENTS.md` holds common navigation and shared working conventions and stays short; it points to product materials, the current task, development commands, relevant rules, and logs without copying their full text.

`.github/copilot-instructions.md` is Copilot's native repository entry point; it requires reading the common entry point and task-relevant materials first. It keeps only necessary guidance and Copilot-specific differences, and must not define different completion criteria. Links do not automatically include referenced files; verify that they are actually read.

Path-scoped rules live in `.github/instructions/` for documentation, tests, or a later-selected tech stack. The common entry point must state where they are, so non-Copilot Agents can read them explicitly per task; do not assume other tools understand `applyTo`.

## 5. Division of labor between templates and Agent capability files

| Type | Purpose | Examples |
|---|---|---|
| Template | Artifact structure and fill-in hints shared by humans and Agents | REQ/SR acceptance criteria, VT targets and baselines, log references |
| Instructions | Conventions followed continuously within their scope | Do not invent requirements; preserve existing changes; actually verify before completion |
| Custom agent | A working mode chosen by the user, together with its tool scope | Planning, implementation, review |
| Skill | Method, inputs, steps, outputs, and exit criteria shared by humans and Agents | Modeling and requirements, specification and verification planning, implementation, change verification, handoff recording |
| Prompt | Shortcut entry point that carries the current task's input | Start a project, plan a feature, continue a task |

Agents need not form an automatic chained "virtual R&D department". A single general-purpose Agent can complete a whole task; a custom agent is used only when role focus or tool restriction adds value. A custom agent's model inherits the user's settings by default, with no hard-coded vendor or model version.

Each skill body is maintained once in `.github/skills/<name>/SKILL.md`, with references, scripts, or assets as needed; document forms reference `_templates/` files. Prompts and custom agents reference skills rather than copying the process. Each capability entry point must state which artifact directory its outputs go to; formal requirements are not stored beside a skill or prompt.

The formal README provides human navigation by activity into shared methods and forms; people follow the steps without an Agent service. AGENTS and prompts lead into the same methods and must not change business facts or completion criteria. P1 connects existing materials and forms, P2 connects skills, with no duplicated manual version.

Scripts are introduced only when a concrete check or project operation genuinely needs them; skills are not used to rebuild a hidden CLI or scheduler.

## 6. How "any Agent can plug in" is achieved

Compatibility has two layers:

- Common layer: any Agent that can read the repository can work through `AGENTS.md`, plain Markdown, and explicit project commands.
- Native-experience layer: uses the instructions, skills, agent selection, and prompt shortcuts the client supports, Copilot first.

For clients without automatic discovery, explicitly ask in natural language to read the entry point and target skill. If a dedicated entry such as `CLAUDE.md` is needed, add a short reference for the actual client instead of duplicating the capability set. A chat-only model that cannot read files or run project tools is outside direct out-of-the-box scope.

The official GitHub documentation checked this time supports project skill locations such as `.github/skills` and custom agents in `.github/agents`. Prompt-file support varies by interface, so VS Code shortcuts must not be promised for GitHub.com or Copilot CLI. Basis: [source register Q1–Q4](../research/source-register.md); documented support does not mean this template has been verified in the corresponding client.

Choosing the GitHub Copilot App in P0 does not mean it inherits all native capabilities above. P3 records native discovery, explicit reading, and unverified items separately; prompt files are optional, and core work does not depend on the App discovering them.

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

First use is via a template repository or by copying files. The README's staged checklist and the onboarding skill help fill in user-confirmed project information; the skeleton is usable while the stack and commands remain not configured. The stack is identified or confirmed, and its real paths and commands registered, only after the user decides to create a concrete project. No language is chosen, no application is initialized automatically, and no custom initialization program is needed.

The development log records task, branch or version, work done, verification results, blockers, and next steps. On session switch, continue from the task files, the log, and the current Git state. This is a readable handoff, not process-level recovery, and does not guarantee that external operations run exactly once.

The template is released by Git tag or release, and a project can record its source version in its README. Later updates are merged through normal diffs and review; business files are not overwritten remotely, and the reference repositories' HEAD is not tracked continuously.

## 9. First-version boundaries

The first version delivers a tech-stack-agnostic repository skeleton, project document templates, a common Agent entry point, and Copilot capability files. In a clean copy, acceptance of the entry points, lightweight modeling, requirement-to-VT traceability, gap discovery, rule-change impact, and takeover after a session switch uses only document-only exercises. No application is created and no reference business project is integrated; application code, build, test, and CI are left downstream, and no language toolchain is claimed to be verified.

Out of scope: a custom CLI, coordinator, SQLite state store, artifact graph database, artifact manifest or lock, custom agent manifest/lock, automatic upgrader, cross-repository sync, web console, or multi-Agent scheduling. Domain-modeling depth and additional requirements for regulated scenarios are decided per project need; the complete method process is not mandatory, but the business basis, verification mapping, and open items applicable to the current task are kept.
