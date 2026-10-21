# Evidence and source register

Initial research date: 2026-10-12. The `R`, `E`, and `P` numbers used in other documents refer to the initial research; the official Copilot materials added on 2026-10-13 for the repo-template direction are registered separately with `Q` numbers.

## 1. Reading method and limits of the conclusions

- The first Git reads lacked credentials; after the user completed a browser sign-in, directories and selected files were viewed through the same-origin, read-only Azure DevOps API. No cookies, tokens, or passwords were read or exported.
- The recursive directory listings of all eight repositories were examined; key documents, prompts, templates, validators, and the business vertical sample were then read at specific commits.
- "Current repository HEAD", "submodule commit pinned by the consumer", and "capabilities proposed in the upstream roadmap" were kept distinct; none of the three was treated as an already-deployed feature.
- This is a study of architecture and development process, not a full code audit. No business builds, tests, or remote pipelines were run; an `Approved`, `Implemented`, or coverage rule written in a file is not a fact verified in this round.
- Azure DevOps branch policies, organization permissions, external architecture wikis, and QMS approval records were not inspected. Therefore only the mechanisms visible in the repositories can be assessed; we cannot assert that the organization has no controls at all outside them.
- A 404 returned by the API only proves that the current identity cannot resolve the target; on its own it cannot distinguish "the repository does not exist" from "no permission".

## 2. Snapshots of the eight reference repositories

"Entries" is the total number of trees, files, and gitlinks returned by the directory API, not the number of source files.

| ID | Repository (link to pinned version) | Full commit | Entries | Main role |
|---|---|---|---:|---|
| R1 | [DeviceRegistry-BC](https://dev.azure.com/shcgravity/Admin%20Center/_git/DeviceRegistry-BC?version=GC8ca62836e6f0f8c5be87e357302ed27136716d5a) | `8ca62836e6f0f8c5be87e357302ed27136716d5a` | 307 | Actual BC implementation project |
| R2 | [DM-Subdomain](https://dev.azure.com/shcgravity/Admin%20Center/_git/DM-Subdomain?version=GC9da2c2a0e22dffff2b41943a09033e4e2e410f39) | `9da2c2a0e22dffff2b41943a09033e4e2e410f39` | 111 | Actual domain model project |
| R3 | [ddd-bc](https://dev.azure.com/shcgravity/Center/_git/ddd-bc?version=GCbac263bea39988214b82cafb48f27e3a2136c534) | `bac263bea39988214b82cafb48f27e3a2136c534` | 33 | BC project skeleton and conventions |
| R4 | [ddd-bc-prompts](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-prompts?version=GC08f8219397d6fe6d000312f5956a493b1b28cc84) | `08f8219397d6fe6d000312f5956a493b1b28cc84` | 16 | BC workflows and skills |
| R5 | [ddd-bc-templates](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-templates?version=GC00705aef6c70f855ef95588b0137cf7f2387efb0) | `00705aef6c70f855ef95588b0137cf7f2387efb0` | 16 | SR, US, ABB, and VT templates |
| R6 | [ddd-subdomain](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain?version=GCe115ad4d03ac53359c608ce7d32262a508561496) | `e115ad4d03ac53359c608ce7d32262a508561496` | 107 | Domain modeling framework, tools, and roadmap |
| R7 | [ddd-subdomain-prompts](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain-prompts?version=GC1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c) | `1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c` | 20 | Domain modeling and reverse-extraction workflows |
| R8 | [ddd-subdomain-templates](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain-templates?version=GC59f98e352a150f99290a3855092298dbe11e0615) | `59f98e352a150f99290a3855092298dbe11e0615` | 66 | Domain structure, model, and scenario templates |

## 3. Consumed versions and upstream versions

| Consumer | Mount location | Pinned commit | Observation in this round |
|---|---|---|---|
| DeviceRegistry-BC | `domain-model/` | `a187ce9cc05dbba5f2186fe0b24e179c7ed880d1` | Not equal to R2 HEAD; the business vertical sample was read at this version |
| DeviceRegistry-BC, ddd-bc | `.github/prompts/` | `08f8219397d6fe6d000312f5956a493b1b28cc84` | Equal to R4 HEAD |
| DeviceRegistry-BC, ddd-bc | `_templates/` | `00705aef6c70f855ef95588b0137cf7f2387efb0` | Equal to R5 HEAD |
| DM-Subdomain | `.github/prompts/` | `3e6951504d79cf2d7d4a440986217d0b649d8179` | Not equal to R7 HEAD; the domain-modeling skill at this version was also read |
| DM-Subdomain | `_templates/` | `15792aac4f7f83be20815ed829397ea43b15f3e0` | Not equal to R8 HEAD |
| ddd-subdomain | `.github/prompts/` | `d7da752b7312dd9212c3fea15eba7fbf1c1edfba` | Also not equal to R7 HEAD |
| ddd-subdomain | `_templates/` | `9cc3338ba0d7fde01ac43c2562f0c7f8a57e8ab6` | Also not equal to R8 HEAD |

Pinning an older version is not a defect in itself; it may be a deliberate compatibility strategy. The point is that we must know "what was consumed, which schemas it fits, and whether re-approval is needed"; we cannot just compare dates or let an agent update to the latest version automatically.

## 4. Key evidence locations

The E numbers below support design judgments. Files in the same repository that are not linked directly can be reached from the pinned version of the corresponding R number.

| ID | File or location | Judgment supported |
|---|---|---|
| E01 | `.gitmodules` in R1 and R2; directory gitlinks | How the two layers of business repositories connect to the shared prompts/templates |
| E02 | [R1 `bc-config.yaml`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DeviceRegistry-BC?path=/bc-config.yaml&version=GC8ca62836e6f0f8c5be87e357302ed27136716d5a) | BC identity, language, framework, and relative domain path |
| E03 | [R4 `skills/bc-implementation/SKILL.md`](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-prompts?path=/skills/bc-implementation/SKILL.md&version=GC08f8219397d6fe6d000312f5956a493b1b28cc84) | Read the domain first, read-only boundary, approval order, bridge update rules |
| E04 | [R4 `code-generation.prompt.md`](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-prompts?path=/code-generation.prompt.md&version=GC08f8219397d6fe6d000312f5956a493b1b28cc84) | Generation scope, pre-checks, no test generation, no overwriting of non-empty files |
| E05 | [R2 `ADR-0005`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DM-Subdomain?path=/domain-model/decisions/ADR-0005-workflow-prompts-over-role-agents.md&version=GC9da2c2a0e22dffff2b41943a09033e4e2e410f39) | Explicitly chooses workflow-scoped prompts and does not adopt a role pipeline as the main flow |
| E06 | [R6 `_roadmap/02-execution-engine.md`](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain?path=/_roadmap/02-execution-engine.md&version=GCe115ad4d03ac53359c608ce7d32262a508561496) | Proposed gap detector, auto-approval, and child PR orchestration; not proof of an existing implementation |
| E07 | R6 `.github/utilities/validate_artifact.py`, `.github/hooks/commit-msg`, `azure-pipelines.yml` | Existing heading/placeholder validation, commit conventions, and sync pipeline; check depth and trust boundaries are limited |
| E08 | R6 `_roadmap/README.md`, `03-scaffolding-automation.md`, `05-tiered-profiles.md` | The Tantu roadmap already proposes a CLI, tiered profiles, version migration, and evaluation |
| E09 | R5 `items/user-story.md`, `items/verification-test.md`; R8 `context/model.yaml` | Existing design of statuses, ACs, test fields, and bridge versions |
| E10 | R1 `SR-001`, `US-001`, `ABB-001`, `VT-002`, `traceability-matrix.md` | Samples of the document traceability chain, approval status, scope, and implementation status |
| E11 | [R2 `model.yaml` at the consumed version](https://dev.azure.com/shcgravity/Admin%20Center/_git/DM-Subdomain?path=/domain-model/subdomains/device-management/contexts/device-registry/model.yaml&version=GCa187ce9cc05dbba5f2186fe0b24e179c7ed880d1); `use-cases.md`, `invariants.md`, and `REQ-001` at the same version | Real domain path, the Approved/Draft distinction, and bridge content |
| E12 | [R1 `RegisterDeviceCommandHandler.cs`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DeviceRegistry-BC?path=/src/application/commands/RegisterDeviceCommandHandler.cs&version=GC8ca62836e6f0f8c5be87e357302ed27136716d5a) | Actual code carries UC/SR/US/VT references |
| E13 | [R1 `VT002_RegisterDeviceIntegrationTests.cs`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DeviceRegistry-BC?path=/src/tests/integration/VT002_RegisterDeviceIntegrationTests.cs&version=GC8ca62836e6f0f8c5be87e357302ed27136716d5a) | A real integration test exists; its route and local AC numbers can be compared with the specification |
| E14 | R1 `src/Directory.Build.props`, `global.json`, `src/api/DeviceRegistry.Api.csproj` | `net10.0`, C# 14, actual references, and the API composition root |
| E15 | R7 `skills/domain-modeling/SKILL.md` at the current and consumed versions; current `reverse-engineering.prompt.md` | Domain expert confirmation, Draft output, reverse extraction, and confidence rules |
| E16 | R6 `.github/ai-tool-config.yaml` | Human review requirements, tool qualification records, manual interaction logs |

### Additional read-only resolution observations

1. At R2's consumed version `a187ce9c...`, `/domain-model/subdomains/device-management/contexts/device-registry/model.yaml` resolved successfully, while `/subdomains/device-management/contexts/device-registry/model.yaml` returned 404.
2. R1's `bc-config.yaml` uses the latter, in-repository relative path, while the prompt joins it as `domain-model/<domainContextPath>`. Resolved under the current contract, the path is missing one level: the `domain-model/` inside the mounted repository.
3. R1's `.gitmodules` configures `../ddd-bc-prompts` and `../ddd-bc-templates` for prompts/templates. Resolved as relative Git URLs, they point to the `Admin Center` project; for the current user, both targets return 404, while the corresponding repositories in `Center` are readable.

These observations are used only to derive design requirements for initialization and dependency resolution; this round did not modify any of them.

## 5. Public primary sources

The body text of every entry was read in this round. All access dates are 2026-10-12; dynamic product documentation is not treated as a pinned-version compatibility commitment.

| ID | Source | Content used in this round |
|---|---|---|
| P1 | OpenAI: [Harness engineering](https://openai.com/index/harness-engineering/); the text actually read in the browser was the [official Chinese-language version](https://openai.com/zh-Hans-CN/index/harness-engineering/) | Published 2026-02-11; short entry point, repository knowledge, observable environment, mechanical architecture constraints, long-term maintenance |
| P2 | Anthropic: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Split between initialization and incremental execution, progress handoff, feature list, end-to-end verification |
| P3 | Anthropic: [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | Explicit verifiable outcomes, planning after exploration, on-demand context, permission isolation |
| P4 | GitHub: [Spec Kit](https://github.com/github/spec-kit) | Specification, plan, tasks, implementation, and convergence; the current README also distinguishes separate entry points for bug fixing and idea assessment |
| P5 | AGENTS.md: [official repository README](https://github.com/agentsmd/agents.md) | A predictable repository instruction entry point for coding agents |
| P6 | Agent Skills: [format specification](https://agentskills.io/specification) | `SKILL.md`, resource directories, progressive loading; `allowed-tools` is an experimental field |
| P7 | GitHub: [About GitHub Agentic Workflows](https://docs.github.com/en/copilot/concepts/agents/about-github-agentic-workflows) | Markdown definitions, compiled workflows, read-only defaults, safe outputs, isolated credentials; the page states that the feature is in public preview |
| P8 | Cursor: [Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents) | Multi-agent coordination experiments, shared-state failures, planner/worker split, periodic resets still needed |
| P9 | Anthropic: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Difference between workflows and autonomous agents, preference for simple composition, real-environment feedback and stop conditions |

The AGENTS guide in the OpenAI developer documentation returned 403 to this round's HTTP read, so no unread content was used as a basis. The HTTP body extraction for P1 was also incomplete, so the official text was read in a browser instead.

## 6. Inferences not drawn from these sources

- Do not infer this project's quality, ROI, or schedule from the line counts, agent counts, or PR counts in corporate blogs.
- Do not treat the interpretations of medical regulations cited in existing files as a completed regulatory review.
- Do not equate pinned prompt versions with deterministic model output.
- Do not treat the eight repositories accessible in this round as a complete inventory of the organization's assets; external risk-management repositories and the ADR wiki were out of scope.

## 7. Copilot materials added for the repo-template direction

Access date: 2026-10-13. The file conventions and capability descriptions below were read from official pages; no content from this repository or the reference projects was sent to external sites.

| ID | Official source | Content checked in this round |
|---|---|---|
| Q1 | GitHub: [Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` with `applyTo`, and AGENTS-style entry points; mainly the sections on creating instructions were read, and GitHub.com rules are not extrapolated to all IDE behavior |
| Q2 | GitHub: [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | Agent Skills are an open convention; project locations such as `.github/skills`, `.claude/skills`, and `.agents/skills` are supported |
| Q3 | GitHub: [Copilot customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) | Purpose, location, triggering, and per-interface support of instructions, prompt files, custom agents, and skills; per the table, prompt files are not supported on GitHub.com or in Copilot CLI |
| Q4 | GitHub: [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | `.md`/`.agent.md` file names, frontmatter such as description, default model behavior, tool scope, and differences between interfaces; the configuration and tools sections were read, and not every extended property is listed as a general capability |

These sources support the current file-layout design; they do not mean that this project's Agent capability files have been generated or tested. Future compatibility records must still state the actual client, version, and verification result; dynamic official documentation may change.

This round did not revisit the eight reference repositories or rerun the initial public research. Their versions, evidence, and limitations still stand as recorded in the historical register above.

## 8. Directory naming adoption record

On 2026-10-13, the user asked that directory naming continue to follow DDD and the existing repos. This design adjustment is based on the existing research and on the reference-path record in section 3 of `docs/design/repository-blueprint.md` in the initial commit `4d67b20`; the remote repositories were not revisited and none of their files were imported.

| Adopted item | Existing basis | Treatment in this template |
|---|---|---|
| `domain-model/` | Directory and mount records in R1/R2 and E01/E11 | Keep the name and maintain our own domain materials within the single repository; submodules are not used by default |
| `stakeholder-requirements/` | The stakeholder requirements / REQ responsibilities in the domain research; the E11 sample | Borrow the terminology and division of labor and place it at the top level of the single repository; this does not assert that the reference repositories use the same level |
| `software-requirements/`, `user-stories/`, `architecture/`, `verification/` | Reference paths recorded in section 3 of the initial blueprint; the SR/US/ABB/VT samples in E10 | Adopt the directory names and artifact division of labor; write our own forms |
| `_templates/items/` | The `_templates` mount record in E01; `items/user-story.md` and `items/verification-test.md` in E09 | Adopt the centralized form organization; do not copy template source code or mount the template repository |
| `src/tests/` (historical reference) | The actual test path in E13 and the initial blueprint | Not adopted as a pre-built directory in P0; `src` contains only notes, and downstream projects choose their own project type and test layout |
| `.github/prompts/` and Copilot native entry points | The prompts location in E01; the native file conventions in Q1–Q4 | Keep the native discovery locations; skills, agents, and instructions are not moved into `_templates` because of the business directory changes |
| `logs/`, development guide, central location for architecture decisions | This project's handoff and maintenance needs | Our own additions or single-repository consolidation; we do not claim that every path has been verified in the reference repositories |

This table records naming choices and their basis at that granularity; it is not a new code or directory audit. The template stays independent, has no home-grown CLI, and is Copilot-first; adopting names does not mandate the full DDD process.

When P0 was completed the same day, the user chose the GitHub Copilot App for the first test and stated explicitly that only the repo skeleton is delivered, that users create projects of any type inside `src` themselves, and that the first version accepts only the skeleton and the documentation workflow. The historical sources above are unchanged and are not a basis for verifying the App's native capabilities; for the current decisions, see the [decision record](../plan/decisions-and-risks.md).

<a id="six-repo-source-inventory"></a>
## 9. Supplement: full source inventory of six repositories (2026-10-15)

Following the enhancement plan, this round used existing Git credentials to fetch, read-only, the six full commits of R3–R8. No credentials were exported, none of their programs were run, no submodules were updated, and no remotes were modified. The browser initially redirected to a sign-in page, but native Git could read the repositories; authentication was not bypassed because of the sign-in issue, and summaries were not substituted for source code.

The six `ls-tree -r -t` listings total 252 entries (195 blobs, 53 trees, 4 gitlinks), which differs from the root-inclusive API totals in the table above by the six repository roots. 185 files were read in full; 10 roadmap files were read within the recorded ranges and marked as proposals; directories and gitlinks were inventoried by metadata only. For each entry's capability carrier, original commit/path, read range, and limitations, see the [capability matrix](ddd-capability-matrix.md).

Newly confirmed existing capabilities include the BC's `tools/setup-domain-model-submodule.ps1`; the domain side's input adapters, audio, and scoring, plus its relationship graph and interaction ledger; and QAS, tactical artifacts, SEQ/Gherkin, SWAS/PDF, and more in the templates and methods. Each of these is a script, pipeline, Agent method, or form; the presence of source code does not mean it runs successfully. The old E07 is partial evidence, not an exhaustive list of tools.

The raw Git objects, hash manifest, three sets of reports, and the independent manifest check are stored as local maker-side artifacts and are not distributed with the candidate; four citation ranges that ran past the end of a file have been corrected. The differing consumer gitlink versions, external ADR/risk/ADO/service sources, human qualification, and run results remain untested, and the conclusions of this source inventory are not extended to them.
