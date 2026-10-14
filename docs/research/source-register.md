# 证据与来源登记

初始研究日期：2026-10-12。其他文档中的 `R`、`E`、`P` 编号指向初始研究；2026-10-13 为 repo 模板方向补充的 Copilot 官方资料使用 `Q` 编号单独登记。

## 1. 读取方法与结论边界

- 最初的 Git 读取缺少凭据；用户完成浏览器登录后，通过同源 Azure DevOps 只读 API 查看目录及选定文件。未读取或导出 cookie、令牌、密码。
- 检视了全部八个仓库的递归目录，随后按具体 commit 读取关键文档、prompts、模板、校验器和业务纵向样本。
- 区分“当前仓库 HEAD”“消费方固定的 submodule commit”“上游路线图中的拟建能力”，没有把三者混为已经部署的功能。
- 这是架构与开发流程研究，不是全量代码审计。未运行业务构建、测试、远端流水线；文件里写的 `Approved`、`Implemented` 或覆盖率规则不等于本轮验证过的事实。
- 未检查 Azure DevOps 分支策略、组织权限、外部架构 wiki 或 QMS 审批记录。因此只能判断仓库可见机制，不能断言组织外部完全没有控制措施。
- 接口返回的 404 只证明当前身份无法解析该目标，不能单凭它区分“仓库不存在”和“没有权限”。

## 2. 八个参考仓库的快照

“条目”是目录 API 返回的树、文件和 gitlink 总数，不是源代码文件数。

| 编号 | 仓库及固定版本入口 | 完整 commit | 条目 | 主要角色 |
|---|---|---|---:|---|
| R1 | [DeviceRegistry-BC](https://dev.azure.com/shcgravity/Admin%20Center/_git/DeviceRegistry-BC?version=GC8ca62836e6f0f8c5be87e357302ed27136716d5a) | `8ca62836e6f0f8c5be87e357302ed27136716d5a` | 307 | 实际 BC 实现工程 |
| R2 | [DM-Subdomain](https://dev.azure.com/shcgravity/Admin%20Center/_git/DM-Subdomain?version=GC9da2c2a0e22dffff2b41943a09033e4e2e410f39) | `9da2c2a0e22dffff2b41943a09033e4e2e410f39` | 111 | 实际领域模型工程 |
| R3 | [ddd-bc](https://dev.azure.com/shcgravity/Center/_git/ddd-bc?version=GCbac263bea39988214b82cafb48f27e3a2136c534) | `bac263bea39988214b82cafb48f27e3a2136c534` | 33 | BC 工程骨架与约定 |
| R4 | [ddd-bc-prompts](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-prompts?version=GC08f8219397d6fe6d000312f5956a493b1b28cc84) | `08f8219397d6fe6d000312f5956a493b1b28cc84` | 16 | BC 工作流及 skill |
| R5 | [ddd-bc-templates](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-templates?version=GC00705aef6c70f855ef95588b0137cf7f2387efb0) | `00705aef6c70f855ef95588b0137cf7f2387efb0` | 16 | SR、US、ABB、VT 模板 |
| R6 | [ddd-subdomain](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain?version=GCe115ad4d03ac53359c608ce7d32262a508561496) | `e115ad4d03ac53359c608ce7d32262a508561496` | 107 | 领域建模框架、工具及路线图 |
| R7 | [ddd-subdomain-prompts](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain-prompts?version=GC1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c) | `1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c` | 20 | 领域建模及反向提取工作流 |
| R8 | [ddd-subdomain-templates](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain-templates?version=GC59f98e352a150f99290a3855092298dbe11e0615) | `59f98e352a150f99290a3855092298dbe11e0615` | 66 | 领域结构、模型和场景模板 |

## 3. 消费版本与上游版本

| 消费方 | 挂载位置 | 固定的 commit | 本次观察 |
|---|---|---|---|
| DeviceRegistry-BC | `domain-model/` | `a187ce9cc05dbba5f2186fe0b24e179c7ed880d1` | 不等于 R2 HEAD；业务纵向样本按这个版本读取 |
| DeviceRegistry-BC、ddd-bc | `.github/prompts/` | `08f8219397d6fe6d000312f5956a493b1b28cc84` | 等于 R4 HEAD |
| DeviceRegistry-BC、ddd-bc | `_templates/` | `00705aef6c70f855ef95588b0137cf7f2387efb0` | 等于 R5 HEAD |
| DM-Subdomain | `.github/prompts/` | `3e6951504d79cf2d7d4a440986217d0b649d8179` | 不等于 R7 HEAD；另读取了该版本的 domain-modeling skill |
| DM-Subdomain | `_templates/` | `15792aac4f7f83be20815ed829397ea43b15f3e0` | 不等于 R8 HEAD |
| ddd-subdomain | `.github/prompts/` | `d7da752b7312dd9212c3fea15eba7fbf1c1edfba` | 也不等于 R7 HEAD |
| ddd-subdomain | `_templates/` | `9cc3338ba0d7fde01ac43c2562f0c7f8a57e8ab6` | 也不等于 R8 HEAD |

固定旧版本本身不是缺陷；它可能是有意的兼容策略。问题在于必须知道“消费了什么、适配哪些 schema、是否需要重新审批”，不能只比较日期或者让 agent 自动更新到最新版本。

## 4. 关键证据定位

下列 E 编号用于支持设计判断。未直接链接的同仓库文件可从对应 R 编号的固定版本进入。

| 编号 | 文件或位置 | 支持的判断 |
|---|---|---|
| E01 | R1、R2 的 `.gitmodules`；目录 gitlink | 两层业务仓库和共享 prompts/templates 的连接方式 |
| E02 | [R1 `bc-config.yaml`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DeviceRegistry-BC?path=/bc-config.yaml&version=GC8ca62836e6f0f8c5be87e357302ed27136716d5a) | BC 身份、语言、框架和领域相对路径 |
| E03 | [R4 `skills/bc-implementation/SKILL.md`](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-prompts?path=/skills/bc-implementation/SKILL.md&version=GC08f8219397d6fe6d000312f5956a493b1b28cc84) | 先读领域、只读边界、审批顺序、桥接更新规则 |
| E04 | [R4 `code-generation.prompt.md`](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-prompts?path=/code-generation.prompt.md&version=GC08f8219397d6fe6d000312f5956a493b1b28cc84) | 生成范围、前置检查、不生成测试、不覆盖非空文件 |
| E05 | [R2 `ADR-0005`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DM-Subdomain?path=/domain-model/decisions/ADR-0005-workflow-prompts-over-role-agents.md&version=GC9da2c2a0e22dffff2b41943a09033e4e2e410f39) | 明确选择 workflow-scoped prompts，不采用角色流水线作为主流程 |
| E06 | [R6 `_roadmap/02-execution-engine.md`](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain?path=/_roadmap/02-execution-engine.md&version=GCe115ad4d03ac53359c608ce7d32262a508561496) | 拟建 gap detector、自动批准与 child PR orchestration；不是现有实现证明 |
| E07 | R6 `.github/utilities/validate_artifact.py`、`.github/hooks/commit-msg`、`azure-pipelines.yml` | 已有标题/占位符校验、commit 约定及同步流水线；检查深度和信任边界有限 |
| E08 | R6 `_roadmap/README.md`、`03-scaffolding-automation.md`、`05-tiered-profiles.md` | Tantu 路线图已经提出 CLI、分层 profile、版本迁移和评估 |
| E09 | R5 `items/user-story.md`、`items/verification-test.md`；R8 `context/model.yaml` | 状态、AC、测试字段与桥接版本的既有设计 |
| E10 | R1 `SR-001`、`US-001`、`ABB-001`、`VT-002`、`traceability-matrix.md` | 文档追溯链、批准状态、范围和实现状态样本 |
| E11 | [R2 被消费版本的 `model.yaml`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DM-Subdomain?path=/domain-model/subdomains/device-management/contexts/device-registry/model.yaml&version=GCa187ce9cc05dbba5f2186fe0b24e179c7ed880d1)；同版本 `use-cases.md`、`invariants.md`、`REQ-001` | 真实领域路径、批准/Draft 区别及桥接内容 |
| E12 | [R1 `RegisterDeviceCommandHandler.cs`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DeviceRegistry-BC?path=/src/application/commands/RegisterDeviceCommandHandler.cs&version=GC8ca62836e6f0f8c5be87e357302ed27136716d5a) | 实际代码带 UC/SR/US/VT 引用 |
| E13 | [R1 `VT002_RegisterDeviceIntegrationTests.cs`](https://dev.azure.com/shcgravity/Admin%20Center/_git/DeviceRegistry-BC?path=/src/tests/integration/VT002_RegisterDeviceIntegrationTests.cs&version=GC8ca62836e6f0f8c5be87e357302ed27136716d5a) | 真实集成测试存在；测试路由和局部 AC 编号可与规格对照 |
| E14 | R1 `src/Directory.Build.props`、`global.json`、`src/api/DeviceRegistry.Api.csproj` | `net10.0`、C# 14、实际引用及 API composition root |
| E15 | R7 当前及被消费版本的 `skills/domain-modeling/SKILL.md`、当前 `reverse-engineering.prompt.md` | 领域专家确认、Draft 输出、反向提取及置信度规则 |
| E16 | R6 `.github/ai-tool-config.yaml` | 人工审阅要求、工具资格记录、手动交互日志 |

### 额外的只读解析观察

1. 在 R2 的被消费版本 `a187ce9c...`，`/domain-model/subdomains/device-management/contexts/device-registry/model.yaml` 返回成功；`/subdomains/device-management/contexts/device-registry/model.yaml` 返回 404。
2. R1 的 `bc-config.yaml` 使用后一种仓库内相对路径，而 prompt 按 `domain-model/<domainContextPath>` 拼接。按当前契约解析，少了一层被挂载仓库内部的 `domain-model/`。
3. R1 `.gitmodules` 为 prompts/templates 配置 `../ddd-bc-prompts`、`../ddd-bc-templates`。按相对 Git URL 解析，它们指向 `Admin Center` 项目；当前用户访问这两个目标均返回 404，而 `Center` 中的对应仓库可读。

以上仅用于提出初始化和依赖解析的设计要求，本轮没有修改它们。

## 5. 公开一手资料

所有条目均在本轮读取了正文。访问日期均为 2026-10-12；动态产品文档不视为固定版本兼容承诺。

| 编号 | 来源 | 本次使用的内容 |
|---|---|---|
| P1 | OpenAI：[Harness engineering](https://openai.com/index/harness-engineering/)；浏览器实际读取[官方中文版本](https://openai.com/zh-Hans-CN/index/harness-engineering/) | 2026-02-11 发布；短入口、仓库知识、可观测环境、机械架构约束、长期维护 |
| P2 | Anthropic：[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 初始化与增量执行、进度交接、功能列表、端到端验证 |
| P3 | Anthropic：[Claude Code best practices](https://code.claude.com/docs/en/best-practices) | 明确可验证结果、探索后计划、按需上下文、权限隔离 |
| P4 | GitHub：[Spec Kit](https://github.com/github/spec-kit) | 规范、计划、任务、实现和收敛；当前 README 还区分 bug fixing 与 idea assessment 入口 |
| P5 | AGENTS.md：[官方仓库 README](https://github.com/agentsmd/agents.md) | 为 coding agent 提供可预测的仓库说明入口 |
| P6 | Agent Skills：[格式规范](https://agentskills.io/specification) | `SKILL.md`、资源目录、渐进式加载；`allowed-tools` 为实验字段 |
| P7 | GitHub：[About GitHub Agentic Workflows](https://docs.github.com/en/copilot/concepts/agents/about-github-agentic-workflows) | Markdown 定义、编译后的 workflow、只读默认值、safe outputs、隔离凭据；页面注明 public preview |
| P8 | Cursor：[Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents) | 多 agent 协调实验、共享状态失败、planner/worker 分工、仍需周期性重置 |
| P9 | Anthropic：[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 工作流与自治 agent 的区别、简单组合优先、真实环境反馈与停止条件 |

OpenAI 开发者文档的 AGENTS 指南在本次 HTTP 读取中返回 403，没有将未读内容作为依据。P1 的 HTTP 正文提取也不完整，已改用浏览器读取官方正文。

## 6. 不据此作出的推断

- 不据企业博客的代码行数、agent 数量或 PR 数量推断本项目的质量、ROI 或工期。
- 不把现有文件引用的医疗法规解释当作已经完成的法规审查。
- 不把固定 prompt 版本等同于模型输出确定性。
- 不把本次可访问的八个仓库当作完整组织资产清单；外部风险管理仓库和 ADR wiki 未纳入范围。

## 7. Repo 模板方向的 Copilot 资料补充

访问日期：2026-10-13。以下通过官方页面读取文件约定和能力说明，没有向外部站点发送本仓库或参考项目的内容。

| 编号 | 官方来源 | 本次核对的内容 |
|---|---|---|
| Q1 | GitHub：[Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) | `.github/copilot-instructions.md`、`.github/instructions/*.instructions.md` 与 `applyTo`，以及 AGENTS 类入口；主要读取创建 instructions 的章节，不将 GitHub.com 规则推断成全部 IDE 行为 |
| Q2 | GitHub：[About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | Agent Skills 是开放约定；支持 `.github/skills`、`.claude/skills`、`.agents/skills` 等项目位置 |
| Q3 | GitHub：[Copilot customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) | Instructions、prompt files、custom agents、skills 的用途、位置、触发与使用界面支持；表中 prompt files 不支持 GitHub.com 和 Copilot CLI |
| Q4 | GitHub：[Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | `.md`/`.agent.md` 文件名、description 等 frontmatter、模型默认行为、工具范围及使用界面差异；读取配置与 tools 章节，未将所有扩展属性列为通用能力 |

这些来源支持当前文件布局设计，不代表已经生成或测试了本项目的 Agent 能力文件。未来兼容记录仍需注明实际客户端、版本和验证结果；动态官方文档可能变化。

本次没有重新访问八个参考仓库，也没有重跑初始公开研究。其版本、证据与限制仍按上面的历史登记理解。

## 8. 目录命名采用记录

2026-10-13 用户要求目录命名继续参考 DDD 与已有 repo。本次依据已有研究及初始提交 `4d67b20` 中 `docs\design\repository-blueprint.md` 第 3 节的参考路径记录作出设计调整，没有重新访问远端仓库或导入其文件。

| 采用项 | 已有依据 | 本模板的处理 |
|---|---|---|
| `domain-model\` | R1/R2、E01/E11 的目录与挂载记录 | 沿用名称，在单仓内维护自己的领域资料，不默认使用 submodule |
| `stakeholder-requirements\` | 领域研究中的 stakeholder requirements / REQ 职责、E11 样本 | 借鉴术语与分工，放在单仓顶层；未据此断言参考仓库采用相同层级 |
| `software-requirements\`、`user-stories\`、`architecture\`、`verification\` | 初始蓝图第 3 节记录的参考路径，E10 的 SR/US/ABB/VT 样本 | 采用目录名与工件分工，自行编写表单 |
| `_templates\items\` | E01 的 `_templates` 挂载记录，E09 的 `items/user-story.md`、`items/verification-test.md` | 采用集中表单组织方式，不复制模板源码或挂载模板仓库 |
| `src\tests\`（历史参考） | E13 的实际测试路径及初始蓝图 | P0 不采用为预建目录；`src` 只留说明，下游自行选择项目类型与测试布局 |
| `.github\prompts\` 与 Copilot 原生入口 | E01 的 prompts 位置，Q1–Q4 的原生文件约定 | 保留原生发现位置；skills、agents 和 instructions 不因业务目录调整而迁入 `_templates` |
| `logs\`、开发说明、架构决策集中位置 | 本项目的交接与维护需求 | 自有补充或单仓整理，不声称全部路径都在参考仓库中得到验证 |

这一表记录命名选择与依据的粒度，不是新一轮代码或目录审计。模板保持独立、无自研 CLI、Copilot 优先；采用名称不等于强制完整 DDD 流程。

同日补齐 P0 时，用户选择 GitHub Copilot App 首测，并明确只交付 repo 骨架、在 `src` 内自行创建任意类型的项目，首版只验收骨架与文档流程。上述历史来源不变，也不是 App 原生能力的验证依据；当前决策见[决策记录](../plan/decisions-and-risks.md)。
