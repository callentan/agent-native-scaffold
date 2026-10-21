# Agent integration and verification records

**GitHub Copilot App has limited real-session observations; per-item results are in [template entry-point observations](#template-observations).** Providing a file does not mean the client has loaded it, and a result for a single role or skill cannot represent all entry points. File checks, ordinary sub-agent results, and the behavior of other clients cannot replace actual testing in the App either.

<a id="reading"></a>
## Common file-reading path

People choose a method from the [README activity navigation](../README.md#activities); an Agent that can read repository files first explicitly reads [AGENTS.md](../AGENTS.md), then the complete `SKILL.md` for the activity, the applicable rules, and the actual artifacts. Links are for navigation; they are not include syntax and do not guarantee that the client goes on to load the link targets.

Ordinary file reading also works when there is no native discovery or prompt support; it requires no personal/global skills, access to a reference repository, or hidden chat. You can start in natural language, with the user filling in the actual inputs:

```text
First explicitly read AGENTS.md in the repository root.
Goal, scope, basis, and completion criteria for this task: [TBD].
From the README activity navigation, choose the matching .github/skills/<activity>/SKILL.md,
read it completely before acting, and read the instructions that apply to documentation/test and code changes.
State which files were actually read, the missing inputs, and the evidence limitations; do not treat links as loaded.
```

This is only an operational entry point for explicit reading, not a tested result. People can apply the current nine shared methods directly; the optional prompts do not require a universal slash syntax, and no core method depends on prompt loading.

<a id="entry-points"></a>
## Thin entry points provided

| Surface | Files and responsibilities |
|---|---|
| Common entry point | [AGENTS](../AGENTS.md) points to the activity navigation shared by people and Agents |
| Repository instructions | [copilot-instructions.md](../.github/copilot-instructions.md) points to the common entry point and task rules |
| Path rules | [docs](../.github/instructions/docs.instructions.md), [tests](../.github/instructions/tests.instructions.md), [architecture](../.github/instructions/architecture.instructions.md), [coding](../.github/instructions/coding.instructions.md), and [security](../.github/instructions/security.instructions.md), five in total; all globs are initial match scopes and do not mean that automatic loading has been verified |
| Custom roles | [planner](../.github/agents/planner.agent.md), [implementer](../.github/agents/implementer.agent.md), and [reviewer](../.github/agents/reviewer.agent.md) only select a method and a working perspective; they are not an automatic team |
| Shared methods | [project-onboarding](../.github/skills/project-onboarding/SKILL.md), [define-requirements](../.github/skills/define-requirements/SKILL.md), [reverse-engineer-domain](../.github/skills/reverse-engineer-domain/SKILL.md), [specify-feature](../.github/skills/specify-feature/SKILL.md), [implement-task](../.github/skills/implement-task/SKILL.md), [generate-code](../.github/skills/generate-code/SKILL.md), [update-template](../.github/skills/update-template/SKILL.md), [verify-change](../.github/skills/verify-change/SKILL.md), [record-handoff](../.github/skills/record-handoff/SKILL.md); each method's content is maintained only in its own file |
| Optional prompts | [start-project](../.github/prompts/start-project.prompt.md), [plan-feature](../.github/prompts/plan-feature.prompt.md), [implement-task](../.github/prompts/implement-task.prompt.md), [review-change](../.github/prompts/review-change.prompt.md), and [resume-work](../.github/prompts/resume-work.prompt.md) provide the current input fields and method links |
| Domain-activity prompts | [domain-interview](../.github/prompts/domain-interview.prompt.md), [reverse-engineering](../.github/prompts/reverse-engineering.prompt.md), [distill-domain](../.github/prompts/distill-domain.prompt.md), [glossary-sync](../.github/prompts/glossary-sync.prompt.md), [published-interface](../.github/prompts/published-interface.prompt.md), [amend-intended-use](../.github/prompts/amend-intended-use.prompt.md) |
| Read-only review/query prompts | [review-artifacts](../.github/prompts/review-artifacts.prompt.md), [assess-impact](../.github/prompts/assess-impact.prompt.md), [query-artifacts](../.github/prompts/query-artifacts.prompt.md), [review-backlog](../.github/prompts/review-backlog.prompt.md); running or writing still requires authorization for the current task |
| BC activity prompts | [derive-requirements](../.github/prompts/derive-requirements.prompt.md), [design-architecture](../.github/prompts/design-architecture.prompt.md), [plan-verification](../.github/prompts/plan-verification.prompt.md), [generate-code](../.github/prompts/generate-code.prompt.md), [sequence-diagram](../.github/prompts/sequence-diagram.prompt.md), [build-architecture-spec](../.github/prompts/build-architecture-spec.prompt.md); they provide only the current inputs and the actual method links |
| Update-proposal prompt | [update-template](../.github/prompts/update-template.prompt.md) provides only the inputs for this run's three-way sources, explicit targets, and scope; it does not approve applying or propagating |

In total there are currently nine methods, twenty-two prompts, and three modes. The template-update method and its thin entry points reuse the same read-only Python core; the existing eight methods are kept, and no role is added and no permission granted. Native discovery, App prompt invocation, and manual use of the new methods/subsections/rules have not been verified; limited use through explicit file reading cannot be recorded retroactively as results for these clients.

The test-rule patterns are not a universal set of naming conventions and do not prescribe a test layout. Real projects should extend the patterns to their actual paths; when modifying any test, read that rule explicitly even if no automatic match occurs.

The coding rules initially cover directories such as `src/app/apps/lib/packages/services`, and the architecture rules also cover `architecture` documents; these are not all code locations. When modifying code elsewhere, likewise explicitly read the architecture/coding/security rules and the applicable test rules in full; do not change the layout to make it match, and do not infer automatic activation or real ACLs from configuration text.

<a id="evidence-types"></a>
## Record four kinds of basis separately

| Category | What it can show | What it cannot show |
|---|---|---|
| Native discovery tested | In a specified client, version, and environment, the entry point was actually observed being discovered and used without an explicit request to read files | Native discovery cannot be asserted from file existence, role selection, or manual reading alone |
| Explicit reading tested | After an explicit request to read, the file was actually observed being read and used for the current task, with the inputs and evidence kept | It cannot imply automatic discovery, or that other entry points or other clients also work |
| Official documentation only | Official material exists for the corresponding client/feature; record the link, consultation date, and applicable version | It cannot replace actual verification in this project |
| Unverified | Not enough observation yet; missing versions, missing environments, or items not run must be stated | It must not be written as supported, nor as unsupported without testing |

<a id="official-sources"></a>
## Registered official sources

The following sources were checked on **2026-10-14**. All of them are "Official documentation only" and are not client tests in this repository. Recheck the applicable scope after the clients change.

| Official material | Confirmed documentation content and boundaries |
|---|---|
| [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | `description` is required and `name` is optional; omitting `model` inherits the user's setting. None of this repository's three roles pins a model. The documentation lists aliases such as `read`, `search`, and `execute`; unknown tool names are ignored, so fictitious names cannot be used to claim that permissions are restricted |
| [Add skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) | Repository skills use `.github/skills/<lowercase-name>/SKILL.md` containing `name` and `description`. The file format is not execution authorization |
| [Repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) | `applyTo` in path rules supports comma-separated globs; the specific client discovery/matching behavior must still be tested in practice |
| [Customize GitHub Copilot App](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app) | The App documentation says repository/CLI skills are available and describes the custom agent picker; this is not a conclusion observed for this project in the App |
| [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) | The matrix lists prompt files as unsupported on GitHub.com and in the CLI; loading cannot be inferred from prompt files existing in the repository |
| [VS Code prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files) | `description` is optional, and relative Markdown links can be used; the current documentation says Agent Host sessions do not load prompt files, while the Local agent still supports them. Do not claim across the board that all IDE modes work |

<a id="client-records"></a>
## Registration by client

Copy the registration set below separately for each client, version, and environment. Record only one specific entry point and one mode each time; keep native discovery and explicit reading separate, and do not let the result for a single skill/agent/prompt represent all files of the same type.

| Context of this set | Actual value |
|---|---|
| Client name | GitHub Copilot App (registration for this project: TBD) |
| Client version/build number | TBD |
| Environment | TBD: system, run mode, workspace, permission/tool configuration; do not record secrets |
| Date, recorder, and observation identifier | TBD |
| Object baseline | TBD: branch, commit, uncommitted scope, and versions of the files used |

The table below is a placeholder for projects adopting the template to fill in; it is not a copy of the template-making observations further below. When testing, copy the relevant row and fill in the specific files, inputs, observable behavior, and accessible raw records; untested entry points remain Unverified.

| Entry point/scenario | Mode (native discovery or explicit reading) | Actual input | Files actually discovered | Files actually read | Result and raw-record entry point | Corrections and items to retest |
|---|---|---|---|---|---|---|
| AGENTS common entry point | To be tested separately | TBD | Not observed | Not observed | Unverified | TBD |
| Repository instructions | To be tested separately | TBD | Not observed | Not observed | Unverified | TBD |
| Markdown path rule | To be tested separately | TBD: include the actual target path | Not observed | Not observed | Unverified | TBD |
| Test path rule | To be tested separately | TBD: include actual matching/non-matching paths | Not observed | Not observed | Unverified | TBD |
| A single custom agent | To be tested separately | TBD: role name and task | Not observed | Not observed | Unverified | TBD |
| A single shared skill | To be tested separately | TBD: task trigger or explicit read request | Not observed | Not observed | Unverified | TBD |
| A single optional prompt | To be tested separately | TBD: file and client run mode | Not observed | Not observed | Unverified | TBD |

Record discovery and reading separately; do not substitute "the Agent says it has read the file" or one completed task for observable evidence. Results state the scope of success, the failure symptoms, or the reason for not running; after a correction, keep the original record and record the retest baseline. When official material and observations disagree, keep the difference and distinguish discovery failure, explicit non-support in the documentation, and untested, instead of merging them into a single "supported" mark.

<a id="template-observations"></a>
## Template entry-point observations (2026-10-14)

This section is a historical observation against the baseline of the original six methods and five prompts; new files or method revisions do not extend it into a claim that the current nine methods and twenty-two prompts have been verified in the App.

The following are limited tests in four real App sessions during template making; they do not mean that a new project has completed onboarding. The object was an independent local Git copy of the P2 content and its documentation-exercise checkpoint, with no remote and no application. The App created isolated worktrees and used the default work mode and, via the API, selected reviewer, planner, and implementer respectively, without substituting an ordinary task sub-agent for the client. The GUI agent picker was not observed, and the whole shared App was not restarted.

| Environment and baseline | Actual observation |
|---|---|
| Host and backend | GitHub Copilot App 1.1.29, CLI 1.0.95-3; the tool process ancestry links the two; the versions come from process files, not the About dialog |
| System and run mode | Windows 10.0.26200.0, PowerShell 7.6.6, App `interactive` worktree session |
| Content baseline | Clean test checkpoint `7e478845fc64ceb0b66ba5b655771c543728d0eb` of the P2 candidate; App onboarding `29eacba`, partial-change takeover input `59aebcd`, new-session handoff `312c3f8` |
| Personal configuration limitation | This machine has personal/plugin skills and MCP, which were not uninstalled; what this shows is that the project methods were actually loaded from the repository, not a clean installation without personal configuration |

| Entry point | Observed behavior | Behavior not yet proven |
|---|---|---|
| Three custom work modes | The App API selected reviewer/planner/implementer respectively, and the native selected-agent events matched the repository names; the first two were read-only, and the last wrote only the authorized handoff record | The GUI picker, behavior under arbitrary tasks, and enforced tool boundaries |
| Six project skills | The startup list had six entries, and all six showed native invocations with `source=project` and successful tool completions; the paths were in each worktree's `.github\skills`, and the complete content was delivered and used for onboarding, planning, or checking/handoff | All natural triggering situations, other models/configurations or clients; general reliability is not inferred from this limited use |
| AGENTS and repository instructions | The startup content matched the files; both files were then actually read explicitly, and work followed the activity navigation | Isolated proof of each one's automatic loading mechanism; recursive inclusion of links |
| Two path instructions | The startup manifest had the files and their `applyTo` scopes, and the content was actually read | Automatic activation for matching and non-matching paths |
| Five optional prompts | Actually read as files; the flow does not depend on shortcut entry points | Native App prompt invocation; neither support nor non-support can be claimed from this |
| Real onboarding without prompts | Natural-language tasks, combined with native method loading/explicit file reading, filled in a fixed project name and scope and left real logs and a local checkpoint; the tech stack and commands remained not configured | Cannot be used to claim that GUI shortcut entry points were tested or that a business application can run |
| New-session Git takeover | A new implementer took over from the source checkpoint relying only on the repository, logs, and actual Git, identified the exact coverage gap, stale boundaries, the historical B1 source, and not-run items, and modified only logs/indexes | Did not implement the whole quota-specification correction; a successful handoff is not taken as current documentation consistency or a behavior pass |

The native selected-agent events for all three roles recorded `tools: ["*"]`, consistent with the files configuring no allowlist. reviewer/planner actually followed the read-only agreement of this run; tool permissions were not restricted, and this does not prove additional App/OS security controls. No dangerous operations were used to probe for blocking.

The raw sessions and tool events were saved on the local machine by the template-making sessions and are not distributed with the candidate; distributed copies cannot treat this summary as a raw report they can access themselves. Users should fill in the project registration above again under their own client, version, and permission configuration, and cannot inherit conclusions for untested entry points.

<a id="boundaries"></a>
## Permission and runtime boundaries

Copying Markdown or explicitly reading AGENTS does not enable a sandbox, approvals, branch protection, or tool restrictions; these capabilities must be configured and verified by the client, the operating system, and the hosting platform. This repository has no preset business application or application-language CI; the [development guide](development.md) is authoritative for command status.

The [optional hooks and documentation workflow](../.github/hooks/README.md) provide only explicit opt-in:
the installer proposes by default and does not change real project/user/global configuration; the installed pre-commit checks the actual index,
and commit-msg checks only the text format of declared managed paths, without authenticating manual review. Maker-side tests and downstream documentation
validation are separate, and platform runs/required checks stay not-run until actually tested. They do not expand any Agent's permissions,
and a single local fixture commit cannot be recorded retroactively as all clients or hosting platforms having passed.

The three roles are working perspectives, not independent human approvers or automatic team orchestration. reviewer declares no `tools` restriction, so its read-only requirement is only a conversational agreement; in the entry-point observations the actual tool selection was `["*"]`, **so the role does not establish an enforced read-only boundary and does not prove that host security controls are effective**. If tool aliases are configured later, verify them according to the official format and with a real client; file rules cannot replace permission configuration.

Methods and prompts do not pre-approve shell use, installation, commits, pushes, PRs, or other external side effects; operations still follow the current authorization. Do not treat local-machine evidence, permissions from old sessions, or official feature descriptions as authorization for the current task.
