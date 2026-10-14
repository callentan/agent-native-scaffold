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

1. 检查工作目录、分支和已有修改，例如运行 `git status --short`、`git --no-pager diff`。合入已有项目时先盘点 `README.md`、`AGENTS.md`、已有规则和资料位置，保留原内容。
2. 只选择需要的文件，逐项比较差异后合入；冲突时列出路径、差异和待决定事项，停止受影响的写入。不要整仓覆盖、自动替换规则或搬移已有代码。后续更新也按同样方式审阅 diff，再记录实际采用的来源版本。
3. 用用户已经确认的信息填写本页和业务需求入口。涉及业务时，按[领域模型指引](domain-model/README.md)记录术语、关系、规则和边界；未知事项保持未决。纯维护任务不必补造业务模型。
4. 暂无应用时保持开发说明未配置。只有用户明确选择项目与技术栈、授权创建且开发输入齐备，才按[项目登记要求](docs/development.md#project-registration)创建或接入项目。
5. 使用 Agent 时先读[通用入口](AGENTS.md)和[接入说明](docs/agent-support.md)。GitHub Copilot App 是首测目标，尚未测试；也可以完全由人按这些资料操作。

<a id="daily-work"></a>
## 日常工作

1. 明确本次目标、非目标、依据、修改范围和完成条件。小维护请求或现有 issue 可以直接作为任务依据，不必创建整条 REQ/SR/US 链。
2. 按下表读取有关指引和事实，仅创建需要的工件。实施前先[盘点全部范围内验收项](verification/README.md#coverage-check)，找出缺口；US 不是需求到 VT 的必经层级。
3. 保留无关改动，遇到影响行为的缺失事实、矛盾、冲突或授权不足时停下相应操作并说明。领域规则变化时先检查[语义影响](verification/README.md#change-impact)。
4. 运行适用的真实检查，留下对象、依据与结果基线。文档检查不能替代业务或软件行为验证；未执行写 `not-run` 和原因。
5. 用[开发日志](logs/README.md)记录变化、结果入口、缺口和下一步。需要提交审阅时可使用 [PR 表单](.github/pull_request_template.md)，不要预填通过或批准。

<a id="resume"></a>
## 接手或继续

先读取当前任务、相关模型与需求、验证索引和[最近的相关日志](logs/README.md#handoff)，再核对 Git 分支、基线与未提交范围。确认哪些结果属于旧基线、哪些待复核或未执行，不能把“有 VT”或历史成功当成当前已验证。

无法访问的报告、未保存的改动和外部状态应明确列为缺项，不假装已恢复。目标或授权有变化时先确认，从输入齐备的下一步继续；不依赖旧聊天记忆。

<a id="activities"></a>
## 按活动查找资料

| 活动 | 必需输入与现有指引 | 表单 | 正式落点 |
|---|---|---|---|
| 首次设置 | 已知项目资料、现有文件；[设置步骤](#first-setup) | 本页登记栏 | 本页、[开发说明](docs/development.md) |
| 整理业务模型 | 业务事实与来源；[领域指引](domain-model/README.md) | 入口中的填写栏 | [`domain-model\`](domain-model/README.md) |
| 写 PRD 与业务需求 | 产品目标、用户和边界；[业务需求指引](stakeholder-requirements/README.md) | [REQ](_templates/items/stakeholder-requirement.md) | [`stakeholder-requirements\`](stakeholder-requirements/README.md) |
| 细化软件行为 | REQ 或明确任务依据；[软件要求指引](software-requirements/README.md) | [SR](_templates/items/software-requirement.md) | [`software-requirements\`](software-requirements/README.md) |
| 组织交付切片（可选） | 已有需求或任务；[交付指引](user-stories/README.md) | [US](_templates/items/user-story.md) | [`user-stories\`](user-stories/README.md) |
| 记录结构或决策（按需） | 需求、业务边界、约束；[架构指引](architecture/README.md) | [ABB](_templates/items/architecture-building-block.md)、[ADR](_templates/items/architecture-decision.md) | [`architecture\`](architecture/README.md)、后续 `architecture\decisions\` |
| 规划验证、核对覆盖与执行 | 全部范围内验收项、基线；[验证指引](verification/README.md) | [VT](_templates/items/verification-test.md) | [`verification\`](verification/README.md)；实际测试代码按项目原生布局放置 |
| 创建或维护实际项目 | 用户选择、授权和开发输入；[开发说明](docs/development.md#project-registration) | 开发登记栏 | [`src\`](src/README.md) 或已有项目原路径 |
| 记录与交接 | 当前任务、Git 状态、实际结果；[日志指引](logs/README.md) | [开发日志](_templates/items/development-log.md) | [`logs\`](logs/README.md) |

这里链接的是现有指引和表单。P2 的专用 instructions、agents、skills 与可选 prompts 尚未提供，不是当前操作的前提。

<a id="forms"></a>
## 填写约定

表单在 `_templates\items\`，正式工件放入上表对应目录。只在需要时分配唯一编号；复制后删除表单提示，替换文件名、标题、ID 与锚点中的占位符，并按落点检查相对链接。

正文中的文件路径示例使用反斜杠；Markdown 链接使用相对 URL 和 `/`。验收项使用带所属工件的稳定 ID，例如 `REQ-NNN-AC-01`、`SR-NNN-AC-01`，并设置对应的 ASCII 锚点。编号示意不是已批准的需求，表单也不是实际结果记录。
