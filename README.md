# 待填写：项目名称

这里是项目资料入口。先记录已知目标、业务事实和当前任务，再按需要创建项目；阅读和维护资料不要求先选技术栈。所有“待填写”和 `NNN` 都是占位，不代表已确认事实或正式工件。

<a id="project"></a>
## 项目登记

| 项目 | 当前值 |
|---|---|
| 项目名称 | 待填写 |
| 当前阶段 | 待填写，尚未确认 |
| 当前工作范围摘要 | 待填写，尚未确认 |
| 模板来源版本 | unreleased；待从经批准的 tag 或 commit 填写，不自行编造版本号 |

产品目标、用户、范围和约束的详细内容归[业务需求入口](stakeholder-requirements/README.md#product)，本页不另存一份 PRD。技术栈、环境和开发命令见[开发说明](docs/development.md)，当前均未配置。

<a id="first-setup"></a>
## 首次设置

人和 Agent 都使用 [project-onboarding](.github/skills/project-onboarding/SKILL.md)。新接入或更新模板时按该方法盘点现有内容、逐项合入差异，保留所有者内容与原规则位置；不要整仓覆盖。

只填已确认信息，资料维护不要求技术栈。只有用户选定项目、技术栈与位置、授权创建且[开发输入](docs/development.md#creation-inputs)齐备，才进入编码路径。使用 Agent 时另读[通用入口](AGENTS.md)和[接入说明](docs/agent-support.md)；App 的有限入口观察与未验证项按客户端分别记录，不把模板存在当成全部入口已支持。

<a id="daily-work"></a>
## 日常工作

明确本次目标、范围、依据和完成条件后，从下表选择方法并读取所链接的实际工件。小维护请求或现有 issue 可直接作任务依据，不必补齐 REQ/SR/US/ABB 链。

方法正文只维护在六个 `SKILL.md` 中；现有指引与表单定义字段，正式工件保存事实和结果。需要提交审阅时可用 [PR 表单](.github/pull_request_template.md)，文件或角色都不代表批准，也不自动授权外部操作。

<a id="resume"></a>
## 接手或继续

按 [record-handoff 的接手顺序](.github/skills/record-handoff/SKILL.md#resume)重新核对任务、资料、Git 和证据，从尚未完成且输入齐备的步骤继续。旧日志的“通过”、无法访问的报告和未保存状态不自动成为当前证据。

<a id="activities"></a>
## 按活动查找资料

| 活动 | 人与 Agent 共用的方法 | 输入与字段指引 | 表单 | 正式落点 |
|---|---|---|---|---|
| 接入项目资料 | [project-onboarding](.github/skills/project-onboarding/SKILL.md) | 已确认项目输入、已有文件与 Git；[项目登记](#project) | 本页登记、[开发登记](docs/development.md#project-registration)、[日志](_templates/items/development-log.md) | 本页、[产品说明](stakeholder-requirements/README.md#product)、[开发说明](docs/development.md)、[日志](logs/README.md) |
| 整理模型与业务需求 | [define-requirements](.github/skills/define-requirements/SKILL.md) | 目标、用户、范围与来源；[领域指引](domain-model/README.md)、[REQ 指引](stakeholder-requirements/README.md) | 领域入口填写栏、[REQ](_templates/items/stakeholder-requirement.md) | [领域模型](domain-model/README.md)、[业务需求](stakeholder-requirements/README.md) |
| 细化行为与验证计划 | [specify-feature](.github/skills/specify-feature/SKILL.md) | 实际模型/REQ 或维护请求；[SR 指引](software-requirements/README.md)、[验证指引](verification/README.md) | [SR](_templates/items/software-requirement.md)、[VT](_templates/items/verification-test.md) | [软件要求](software-requirements/README.md)、[验证计划与索引](verification/README.md) |
| 实施明确任务 | [implement-task](.github/skills/implement-task/SKILL.md) | 任务、验收、实际目录与授权；编码另需[开发输入](docs/development.md#creation-inputs) | 现有任务；按需 [US](_templates/items/user-story.md) | 指定文档或[项目实际位置](src/README.md)，不强改原生布局 |
| 核对覆盖与证据 | [verify-change](.github/skills/verify-change/SKILL.md) | 全部交付验收、旧新基线、真实记录；[验证指引](verification/README.md) | [VT](_templates/items/verification-test.md) | [验证目录](verification/README.md)与实际报告入口；测试代码在项目原生位置 |
| 交接或恢复任务 | [record-handoff](.github/skills/record-handoff/SKILL.md) | 任务、Git、变化、结果入口与缺口；[日志指引](logs/README.md) | [开发日志](_templates/items/development-log.md) | [日志目录](logs/README.md)；结果仍回原记录读取 |

附加工件只按需使用：[US 表单](_templates/items/user-story.md)落在[交付目录](user-stories/README.md)；[ABB](_templates/items/architecture-building-block.md)与 [ADR](_templates/items/architecture-decision.md)依[架构指引](architecture/README.md)落在 `architecture\` 或首份决策创建时的 `architecture\decisions\`。它们不是强制链路。

[Copilot 薄入口](docs/agent-support.md#entry-points)只链接上述方法；不自动发现时显式读取具体 `SKILL.md` 和适用规则。链接不是自动包含保证，可选 prompt files 也不是执行这些方法的前提。

<a id="forms"></a>
## 填写约定

表单在 `_templates\items\`，正式工件放入上表对应目录。只在需要时分配唯一编号；复制后删除表单提示，替换文件名、标题、ID 与锚点中的占位符，并按落点检查相对链接。

正文中的文件路径示例使用反斜杠；Markdown 链接使用相对 URL 和 `/`。验收项使用带所属工件的稳定 ID，例如 `REQ-NNN-AC-01`、`SR-NNN-AC-01`，并设置对应的 ASCII 锚点。编号示意不是已批准的需求，表单也不是实际结果记录。
