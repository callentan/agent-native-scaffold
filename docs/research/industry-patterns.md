# Comparison with mainstream public practices

## 1. Research scope

Here "mainstream" means representative public engineering practices and open conventions from OpenAI, Anthropic, GitHub, Cursor, and others. It is not a market-share survey, and it does not mean these companies have agreed on a unified standard.

The initial materials are mainly official texts, accessed on 2026-10-12. Experimental articles, open formats, product features, and public previews are labeled separately and cannot substitute for one another. The design trade-offs below were adjusted for the template direction of 2026-10-13; the official Copilot materials added in that round are listed separately as Q1–Q4; see the [source register](source-register.md).

These materials and projects have the same standing as the internal reference repositories: they provide design experience and do not directly determine the product scope or dependencies of our own skeleton. Using a particular open convention also does not mean adopting that source's implementation as a whole.

## 2. Patterns most worth adopting

| Source | Published pattern | Parts suited to this project | Parts not to copy directly |
|---|---|---|---|
| [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) (P1, engineering experiment) | Short AGENTS entry point, repository as the record of knowledge, observable development environment, mechanical architecture checks, continuous documentation maintenance | Treat readability, runnability, and verifiability as framework deliverables | The article's minimally blocking merge gates and autonomous agent merging are not suitable as this project's default governance |
| [Anthropic long-running task harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (P2, research practice) | Split between initialization and incremental execution, feature list, handoff records, real E2E verification | Small tasks, resumable checkpoints, checking the baseline before development | A JSON `passes` field and an agent's self-report are not tamper-proof acceptance evidence |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) (P3, product practice) | Give the agent runnable verification conditions; explore and plan first; keep always-loaded instructions lean; permissions and isolation | A unified verification entry point, on-demand context, separation of task scope and permissions | Do not treat a client-specific command or permission mode as a cross-tool standard |
| [GitHub Spec Kit](https://github.com/github/spec-kit) (P4, open-source tool) | specification → plan → tasks → implement → converge, project constitution | Specifications and execution plans as first-class artifacts; choose the process per task | SDD artifacts cannot replace run isolation, trusted approval, or actual test evidence |
| [AGENTS.md](https://github.com/agentsmd/agents.md) (P5, open format) | A predictable repository entry point for agents | Unified navigation, commands, constraints, and stop conditions | Do not write it as a giant encyclopedia; loading and override behavior in different clients still needs verification |
| [Agent Skills](https://agentskills.io/specification) (P6, format specification) | SKILL.md + references/scripts/assets, progressive disclosure | Workflow skill packages and on-demand loading | `allowed-tools` is an experimental field and cannot serve as an operating-system or hosted-platform ACL |
| [GitHub Agentic Workflows](https://docs.github.com/en/copilot/concepts/agents/about-github-agentic-workflows) (P7, public preview) | Markdown definitions, compiled execution configuration, read-only defaults, safe outputs, credential isolation | Separate "proposing an operation" from "executing a privileged operation" | Not a native Azure DevOps capability; GitHub YAML cannot be carried over as is |
| [Cursor long-running multi-agent experiment](https://cursor.com/blog/scaling-agents) (P8, scale experiment) | Separate planners and workers; shared locks and self-coordination fail; structure needs iteration | Task ownership, isolation, explicit dependencies, a small amount of independent parallelism | Hundreds of agents, writes to the same branch, and lines of code should not become this project's goals |
| [Anthropic Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (P9, foundational patterns) | Prefer simple composition; separate fixed workflows from autonomous decisions; environment feedback and stop conditions | Write working methods into skills; verify with the project's native tools | Do not introduce a complex general-purpose agent framework by default just to be "AI-native" |

## 3. Three routes emerge

### Route A: make the repository the agent's working environment

The core is not "provide more context" but **provide information that is correct, locatable, versioned, and of known reliability**.

Adopt:

- Short entry points that point to deeper documents, instead of keeping the whole knowledge base permanently injected.
- Business specifications, architecture decisions, how to run things, and known issues can be read within the authorized scope.
- Give each key constraint a checker wherever possible, rather than only a sentence saying "must comply".
- Logs, test reports, and API behavior are queryable; only UI projects go further and provide browser verification.

Implication for our own skeleton: use short entry points and explicit links to help Agents read project materials on demand, without building a context-compilation program. Directory naming follows DDD engineering as the user chose; which domain artifacts actually need to be filled in is still decided by the project.

### Route B: turn a single conversation into resumable delivery

The hard parts of long-running tasks include falsely declaring completion, forgetting, running out of context, and leaving half-finished work.

Adopt:

- Bind each run to one fixed set of input versions and one explicit delivery goal.
- On every resume, first verify the baseline, uncommitted changes, and existing run evidence.
- Record pauses, failures, and unfinished items clearly; use the client's existing mechanisms for budget control.
- Hand off clearly, instead of treating the full text of the last chat as the only memory.

Implication for our own skeleton: record open questions, task progress, and verification results separately in project files. On handoff, check Git and the logs; do not build a run-state database, and do not claim that text can restore an entire process.

### Route C: constrain autonomy with engineering mechanisms

The mature direction is not "the agent may do nothing" but **automating low-risk operations while constraining high-risk decisions with auditable policies**.

Adopt:

- Workers run with least privilege in isolated environments.
- Releases and credentials go through the controlled channels of the client or existing platform; tokens are not written into templates, prompts, or logs.
- Project tests, CI, and reviews provide the real basis; when protected checks are needed, maintainers configure them.
- Client permissions, budgets, and stop conditions have explicit owners; do not assume the template can enable them automatically.

Implication for our own skeleton: humans approve domain intent and risk boundaries; agents autonomously complete code and tests within the approved scope and do not approve new business facts on their own.

## 4. Trade-offs to handle

### 4.1 Spec-driven development and harness engineering are complementary

Spec-driven development answers "what to build, why, and what the acceptance criteria are"; the harness answers "how to run reliably, know the current state, and recover from failure".

This project uses document templates and skills to describe the workflow and reuses off-the-shelf Agents and project tools as the execution environment, rather than building its own harness. Small changes use a lightweight process, so fixing a single typo does not require going through the full V-model.

### 4.2 Role agents and workflow nodes must not be conflated

The reference ADR rejects a PM → Architect → Developer → QA role-based main flow, while Cursor demonstrated a planner/worker experiment. Both are inputs to trade-offs; neither is an architecture decision this project must follow.

Custom agents can offer different working modes for planning, implementation, and review, but they are not automatically chained into a role pipeline. A single general-purpose Agent can also complete a whole task, and choosing the reviewer mode does not create a human approval identity. Verification still uses the real project tools.

### 4.3 Agile autonomy and regulatory governance are not either-or

Repetitive work can be automated without handing Intended Use, risk acceptance, or judgments on unknown domain matters to a model. Conversely, if agents are allowed to weaken the rules themselves, any "regulated profile" loses its meaning.

Regulatory requirements must be confirmed by qualified accountable owners. Documents and records can support traceability, but no one may claim that copying a template or adding a set of rules achieves regulatory compliance.

### 4.4 A unified interface does not make all tools inherently compatible

AGENTS, Skills, and MCP serve as the entry point, the capability package, and the tool connection, respectively. They are not a unified, complete execution protocol, and they do not automatically remove the differences between agents in permissions, resumption, context, and output.

The template uses generic Markdown and a small number of client-native entry points and verifies discovery behavior item by item. It does not develop adapter programs for integration, and it does not claim that "one prompt runs reliably on any model".

## 5. Build-versus-reuse boundaries

| Capability | Recommendation |
|---|---|
| Model reasoning, editing, and the terminal tool loop | Reuse existing coding agents, with GitHub Copilot as the priority; do not build our own CLI |
| General requirements specification process | Follow Spec Kit's specification-to-implementation approach, name directories after the chosen DDD references, and write our own lightweight requirement and delivery forms; installing that tool is not required |
| Skill distribution format | Use the Agent Skills convention and verify the actual installation paths that target clients support |
| Conventions for project materials, working methods, verification, and handoff | We maintain the templates, instructions, agents, skills, and prompts |
| Git, test frameworks, containers, CI, and code hosting | Reuse existing tools; do not reimplement them |
| Graph databases, vector stores, state stores, agent message buses, web consoles | Not part of the template deliverable |
| Multi-agent scheduling | Use the client's existing capabilities and enable them only as needed; do not build our own scheduling system |

## 6. Metrics not used to prove success

Lines of code, number of prompts, number of agents, and cumulative tokens are not used as primary outcome metrics. The main observations are:

- whether tasks are actually delivered under frozen acceptance criteria;
- whether false declarations of completion, out-of-scope changes, and stale approvals are prevented;
- whether the costs of human clarification, rework, review, and recovery go down;
- whether work continues reliably after switching to a new session or another supported runtime environment.

The targets for these metrics and the trial method are in the [implementation plan](../plan/roadmap.md).

## 7. Copilot file conventions added in this round

The official GitHub materials Q1–Q4 list the native locations of repository instructions, custom agents, skills, and prompt files. This is enough to support the "repo template + capability files" form without building a separate runtime layer.

This project maintains skill bodies in `.github/skills`; `.github/agents` provides working modes, and `.github/prompts` provides shortcut entry points for clients that support the feature. AGENTS and the project documents remain directly readable, so prompt files never become the only entry point.

The support table distinguishes between interfaces; for example, prompt files are currently not supported on GitHub.com or in Copilot CLI. Some custom agent properties also differ by interface, so referencing the same Markdown does not automatically grant every native capability. Only the official conventions were checked here; the actual template has not yet been exercised in a client.

P0 has chosen the GitHub Copilot App as the first client to test and accepts only the skeleton, entry points, documentation workflow, and handoff; creating an application project is not required. The App's native capabilities are tested separately and cannot be inferred from the VS Code or Copilot CLI materials above; prompt files remain an optional entry point.
