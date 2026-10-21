# TBD: Project name

This is the entry point to the project's materials. Record the known goals, business facts, and current task first, and create a project only when needed; reading and maintaining the materials does not require choosing a tech stack first. All "TBD" values and `NNN` are placeholders; they do not represent confirmed facts or formal artifacts.

<a id="project"></a>
## Project registration

| Item | Current value |
| --- | --- |
| Project name | TBD |
| Current stage | TBD; not yet confirmed |
| Current work scope summary | TBD; not yet confirmed |
| Template source version | unreleased; fill in from an approved tag or commit; do not invent a version number |

Details of product goals, users, scope, and constraints belong in the [stakeholder requirements entry point](stakeholder-requirements/README.md#product); this page does not keep a separate copy of the PRD. The tech stack, environment, and development commands are described in the [development guide](docs/development.md); none of them is configured yet.

<a id="first-setup"></a>
## First-time setup

Humans and agents onboard a project with [project-onboarding](.github/skills/project-onboarding/SKILL.md); to compare old, local, and new template versions or to propose scenarios for explicitly named BCs, use [update-template](.github/skills/update-template/SKILL.md). Keep owner content and the existing locations of rules, and never overwrite the whole repository; a proposal neither applies changes nor authorizes propagation.

Fill in confirmed information only; maintaining the materials does not require a tech stack. Take the coding path only when the user has chosen the project, tech stack, and location, has authorized creation, and the [development inputs](docs/development.md#creation-inputs) are complete. When working with an agent, also read the [common entry point](AGENTS.md) and the [distribution scope](docs/distribution.md). The distribution candidate does not include historical client observations, and the presence of a file does not mean that any entry point has been verified in practice.

<a id="daily-work"></a>
## Daily work

Once the goal, scope, basis, and completion conditions of the current task are clear, choose a method from the table below and read the actual artifacts it links to. A small maintenance request or an existing issue can serve directly as the task basis; there is no need to complete a REQ/SR/US/ABB chain.

Method text is maintained only in the nine `SKILL.md` files listed below; the existing guides and forms define fields, and formal artifacts hold facts and results. To submit work for review you can use the [PR form](.github/pull_request_template.md). Neither a file nor a role constitutes approval, and neither automatically authorizes external operations.

<a id="resume"></a>
## Take over or resume

Follow the [record-handoff takeover order](.github/skills/record-handoff/SKILL.md#resume) to recheck the task, materials, Git state, and evidence, then continue from an unfinished step whose inputs are complete. A "pass" in an old log, an inaccessible report, or unsaved state does not automatically become current evidence.

<a id="activities"></a>
## Find materials by activity

| Activity | Method shared by humans and agents | Inputs and field guidance | Forms | Formal location |
| --- | --- | --- | --- | --- |
| Onboard project materials | [project-onboarding](.github/skills/project-onboarding/SKILL.md) | Confirmed project inputs, existing files, and Git; [project registration](#project) | Registration on this page, [development registration](docs/development.md#project-registration), [log](_templates/items/development-log.md) | This page, [product description](stakeholder-requirements/README.md#product), [development guide](docs/development.md), [logs](logs/README.md) |
| Shape the domain model and stakeholder requirements | [define-requirements](.github/skills/define-requirements/SKILL.md) | Goals, users, scope, and sources; [domain guide](domain-model/README.md), [REQ guide](stakeholder-requirements/README.md) | Fill-in sections of the domain entry point, [optional domain forms](domain-model/README.md#optional-forms), [REQ](_templates/items/stakeholder-requirement.md), [QAS](_templates/items/quality-attribute-scenario.md) | [Domain model](domain-model/README.md), [stakeholder requirements](stakeholder-requirements/README.md) |
| Extract domain candidates from existing materials | [reverse-engineer-domain](.github/skills/reverse-engineer-domain/SKILL.md) | Documents, implementations, excerpts, or external records you are authorized to read, with their actual locations/versions; [source boundaries](domain-model/README.md#sources) | [Existing domain forms](domain-model/README.md#optional-forms) as needed; when identity is missing, keep authorized notes first | Authorized candidate records or the owning domain/requirements directory; never write back to sources or confirm automatically |
| Refine behavior, necessary design, and the verification plan | [specify-feature](.github/skills/specify-feature/SKILL.md) | The actual domain/REQ or maintenance request; [SR guide](software-requirements/README.md), [architecture guide](architecture/README.md), [verification guide](verification/README.md) | [SR](_templates/items/software-requirement.md), [validation scenario](_templates/items/validation-scenario.md), [VT](_templates/items/verification-test.md), and additional artifacts as needed | [Software requirements](software-requirements/README.md), [architecture](architecture/README.md), [verification plans and index](verification/README.md) |
| Maintain existing code or specified documents | [implement-task](.github/skills/implement-task/SKILL.md) | Task, acceptance criteria, actual directories, and authorization; coding also requires the [development inputs](docs/development.md#creation-inputs) | The existing task; [US](_templates/items/user-story.md) as needed | The specified documents or the [project's actual location](src/README.md); do not force changes to the native layout |
| Safe initial code generation | [generate-code](.github/skills/generate-code/SKILL.md) | Confirmed task/acceptance criteria, the user-chosen project/stack/path, real commands/cwd/reports, and authorization to create | The existing development registration; [BC configuration](_templates/config/bc-config.yaml) as needed | Only authorized targets with no conflicts in the preflight check; stop when inputs are missing; never create an application by default |
| Compare template versions and make explicit multi-target proposals | [update-template](.github/skills/update-template/SKILL.md) | Actual old/local/new roots and versions, and owner changes; [tool contract](docs/template-updates.md) | Optional [path/version/file registration](_templates/config/template-updates.yaml), which contains no commands or authorization | stdout or an explicitly named new local report; keep conflicting/unavailable targets; never apply changes or write back to sources |
| Check coverage and evidence | [verify-change](.github/skills/verify-change/SKILL.md) | All delivery acceptance criteria, old and new baselines, and real records; [verification guide](verification/README.md), [governance fields](docs/governance.md) as needed | [VT](_templates/items/verification-test.md); [review record](_templates/items/review-record.md) or [tool usage record](_templates/items/tool-qualification.md) as needed | [Verification directory](verification/README.md) and actual report entry points; test code stays in the project's native location |
| Hand off or resume a task | [record-handoff](.github/skills/record-handoff/SKILL.md) | Task, Git, changes, result entry points, and gaps; [log guide](logs/README.md), [minimal tool record](docs/ai-tooling.md#minimal-record) as needed | [Development log](_templates/items/development-log.md) | [Logs directory](logs/README.md); results and decisions are still read from their original records |

Domain and review activities can go straight to the subsections below. You must still read the owning method in full; there is no separate process:

| Current need | Method subsection and inputs |
|---|---|
| Interview or iterative confirmation | [define-requirements / interview](.github/skills/define-requirements/SKILL.md#interview): goals, participants, scope, sources, and open questions |
| Knowledge crunching, model drift | [define-requirements / distill](.github/skills/define-requirements/SKILL.md#distill): actual model version, statements, and usage clues |
| Glossary sync | [define-requirements / glossary-sync](.github/skills/define-requirements/SKILL.md#glossary-sync): local/external definitions, contexts, and explicit versions |
| Published Interface evolution | [define-requirements / published-interface](.github/skills/define-requirements/SKILL.md#published-interface): actual contract, differences, and known consumers; [PI form](_templates/items/published-interface.md) |
| Incoming ADR or Intended Use change | [incoming-adr](.github/skills/define-requirements/SKILL.md#incoming-adr) / [intended-use](.github/skills/define-requirements/SKILL.md#intended-use): handle only the original text, baseline, and authorization actually provided; the optional [IU form](_templates/items/intended-use.md) and [governance guide](docs/governance.md#intended-use) do not replace the original text and are not required for every project |
| Domain artifact review | [verify-change / domain-review](.github/skills/verify-change/SKILL.md#domain-review): full scope, actual artifacts, and evidence; read-only by default |
| Query the inventory | [verify-change / query](.github/skills/verify-change/SKILL.md#query): real root directory, types, scope, and question; read-only by default |
| Review open questions | [verify-change / backlog-review](.github/skills/verify-change/SKILL.md#backlog-review): original question/BL, decision basis, and residual impact; read-only by default |
| Coverage and semantic impact | [coverage](.github/skills/verify-change/SKILL.md#coverage) / [impact](.github/skills/verify-change/SKILL.md#impact): all acceptance sources, each individual target, old and new baselines, and raw results |
| BC software requirements and optional slices | [derive-requirements](.github/skills/specify-feature/SKILL.md#derive-requirements) / [delivery-slice](.github/skills/specify-feature/SKILL.md#delivery-slice): actual REQ/UC/INV/CAP/QAS, confirmation basis, and task scope |
| Necessary architecture and verification plan | [design-architecture](.github/skills/specify-feature/SKILL.md#design-architecture) / [plan-verification](.github/skills/specify-feature/SKILL.md#plan-verification): plan each independently once its own necessary inputs are complete; a US is not required |
| Sequence diagrams and architecture specifications | [sequence-diagram](.github/skills/specify-feature/SKILL.md#sequence-diagram) / [build-architecture-spec](.github/skills/specify-feature/SKILL.md#build-architecture-spec): actual participants, contracts, source views, and baselines; keep missing items visible |
| BC derivation and generation-boundary review | [bc-review](.github/skills/verify-change/SKILL.md#bc-review): actual artifacts, code scope/conflicts, and per-item evidence; read-only by default |
| Optional human review, waivers, and tool-use checks | [domain-review](.github/skills/verify-change/SKILL.md#domain-review) and [handoff](.github/skills/record-handoff/SKILL.md): for fields and locations see [governance](docs/governance.md#records)/[tooling notes](docs/ai-tooling.md); use the [minimal interaction ledger](docs/ai-tooling.md#interaction-ledger) as needed; no new approval or execution process is added |

Use additional artifacts only as needed: the [US form](_templates/items/user-story.md) goes in the [delivery directory](user-stories/README.md); [ABB](_templates/items/architecture-building-block.md) and [ADR](_templates/items/architecture-decision.md) follow the [architecture guide](architecture/README.md) and go in `architecture/`, or in `architecture/decisions/`, which is created together with the first decision. They are not a mandatory chain.

Adopt [SEQ](_templates/items/sequence-diagram.md), [SWAS](_templates/items/architecture-specification.md), and the [Gherkin companion](_templates/items/verification-test.feature) only when needed. Diagrams and scenario text are not run evidence. The optional [local document export](docs/document-exports.md) generates JSON/SVG/HTML relationship diagrams and HTML/SVG architecture views and parameterized presentations from explicit sources; PDF/PPTX still has no authorized renderer and remains an unavailable gate. The [BC data configuration](architecture/README.md#bc-configuration) only registers actual identities/sources and the development entry point; it is not an application or execution manifest.

When a standalone Intended Use or a reference to external risk is needed, use the [Intended Use](_templates/items/intended-use.md) and [risk control](_templates/items/risk-control.md) forms and save them at the [domain location](domain-model/README.md#governance-forms). All four governance/tool records are optional; keep a gap for any unknown policy, source, or decision. A blank form does not establish a QMS, a qualification, or an approval.

The [thin Copilot entry point](.github/copilot-instructions.md) only links to the methods above; when they are not discovered automatically, explicitly read the specific `SKILL.md` and the applicable rules. A link does not guarantee automatic inclusion, and optional prompt files are not a prerequisite for running these methods.

<a id="forms"></a>
## Filling-in conventions

Artifact forms are in `_templates/items/` and optional configuration is in `_templates/config/`; formal content goes in the locations given in the table above and in each guide. Assign a unique number only when needed. After copying a form, delete its prompts, replace the placeholders in the file name, title, IDs, and anchors, and check the relative links against the final location.

Path examples in prose use forward slashes `/`, the same separator as Markdown links (which use relative URLs). Acceptance criteria use stable IDs qualified by their owning artifact, such as `REQ-NNN-AC-01` and `SR-NNN-AC-01`, each with a matching ASCII anchor. Example numbers are not approved requirements, and forms are not records of actual results.

Fill in the frontmatter of the standalone domain/QAS/scenario, REQ/SR/US/ABB/ADR/VT, SEQ/SWAS, and four optional governance/tool forms according to the [metadata conventions](domain-model/README.md#artifact-metadata); do not guess the scope while the project and context are unclear. Relationships and content state belong in the metadata, the body holds meaning and criteria, and task progress and actual results are recorded separately; the [decision fields](docs/governance.md#ownership) do not constitute a second content state. The original single-context README and existing formal artifacts remain usable; they are not migrated automatically, and filling in every optional form is not mandatory.
