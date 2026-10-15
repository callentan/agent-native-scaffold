# 仓库模板与 Agent 文件蓝图

**更新：2026-10-14。本蓝图的 38 个 P1/P2 文件已制作；P3 本地文档演练与未完成的客户端、人工及发布事项见[实际验收记录](../plan/roadmap.md#actual-acceptance)。**

## 1. 一个模板，两组内容

正式模板的仓库根目录就是下游项目的起点，不再先安装一个框架再运行生成命令。项目资料与 Agent 能力文件一起分发，用户复制后直接拥有这些文件。

交付的是 repo 骨架，不是附带示例应用的脚手架。`src\` 留给用户创建任意类型的项目，首版只放说明，不选择语言、框架、依赖管理器、应用入口或测试布局。

三项职责是首版内容要求，而不只是命名参考：**DDD 负责业务模型与边界，V-model 负责需求到验证的追溯，templates、skills 与 prompts 让人和 Agent 按统一流程工作。** 表单定义产物结构，skills 保存共享方法，prompts 只提供调用入口；不强制完整 DDD/V-model，也不省略适用的最小建模与追溯。

目录命名参考 DDD 工程及此前研究的 repo：领域侧借鉴 `ddd-subdomain` / `DM-Subdomain` 的职责，实现侧借鉴 `ddd-bc` / `DeviceRegistry-BC`，文档表单采用 `_templates` 的集中组织方式。我们把需要的内容组织在一个 repo 中，不沿用它们的 submodule 或多仓库部署方式。

参考源码、内部研究材料和本项目自身的设计讨论不应混进下游的 PRD 或业务文档。发布前先整理可分发内容，不能直接把当前研究仓库标为公开模板。

## 2. 首版模板目录

```text
project\
  README.md
  AGENTS.md
  .gitignore
  domain-model\
    README.md
  stakeholder-requirements\
    README.md
  software-requirements\
    README.md
  user-stories\
    README.md
  architecture\
    README.md
    decisions\
  verification\
    README.md
  logs\
    README.md
  docs\
    development.md
    agent-support.md
  _templates\
    items\
      stakeholder-requirement.md
      software-requirement.md
      user-story.md
      architecture-building-block.md
      verification-test.md
      architecture-decision.md
      development-log.md
  src\
    README.md
  .github\
    copilot-instructions.md
    instructions\
      docs.instructions.md
      tests.instructions.md
    agents\
      planner.agent.md
      implementer.agent.md
      reviewer.agent.md
    skills\
      project-onboarding\
        SKILL.md
      define-requirements\
        SKILL.md
      specify-feature\
        SKILL.md
      implement-task\
        SKILL.md
      verify-change\
        SKILL.md
      record-handoff\
        SKILL.md
    prompts\
      start-project.prompt.md
      plan-feature.prompt.md
      implement-task.prompt.md
      review-change.prompt.md
      resume-work.prompt.md
    pull_request_template.md
```

这是已制作的首版分发清单，共 38 个文件。P1 的 21 个文件包括 README、AGENTS、`.gitignore`、资料目录说明、七类表单、`docs` 中两份说明、`src\README.md` 和 PR 表单；P2 新增其余 17 个 `.github` 能力文件，并连接 P1 入口。文件已存在不表示客户端已原生发现，也不表示已获发布授权。

`architecture\decisions\` 是后续 ADR 的约定位置，首次创建 ADR 时再建立，不为保留空目录添加虚假决策。资料目录初始只有填写说明，不预先生成 REQ/SR/US 等业务工件。

`src\README.md` 说明可以直接在 `src\` 或其子目录创建任意类型的项目，并在开发说明中登记真实工作目录与命令。历史参考中的 `src\tests\` 不在首版创建；实际源码、测试、依赖清单和流水线由下游项目决定。已有工程保留原路径，不强制搬入 `src` 或另建测试目录。

空白表单集中在 `_templates\items\`，复制后放入对应的正式工件目录，不再在每个目录放一份 `_template.md`。上面的表单文件名是本模板的设计，其中 `user-story.md`、`verification-test.md` 可直接对应参考记录；其余文件内容也由我们独立编写，不搬运原模板。

### 命名依据与上一版的调整

| 上一版用途 | 当前路径 | 参考与调整 |
|---|---|---|
| 领域事实散在项目说明中 | `domain-model\` | 沿用参考领域目录名，在本 repo 内维护，不是外部只读挂载 |
| `prd\` 产品说明 | `stakeholder-requirements\` | 借鉴 stakeholder requirements / REQ 的职责；放在单仓顶层是本模板的整理，不声称复刻参考仓库嵌套路径 |
| `specs\` 功能规格 | `software-requirements\`，设计与验证分别放 `architecture\`、`verification\` | 沿用参考工程的 SR/ABB/VT 分工，不把所有规格混进一个目录 |
| `tasks\` 实施任务 | `user-stories\` 中的交付切片与实施清单 | 沿用 US；不适合用户故事的维护事项使用 issue/PR，不强行改写成用户价值叙事 |
| `docs\architecture.md`、`docs\decisions\` | `architecture\README.md`、`architecture\decisions\` | 采用参考工程的架构目录；单仓架构决策集中位置由我们确定 |
| 分散的 `_template.md` | `_templates\items\` | 沿用参考模板目录与 items 的组织方式，作为本地文件而非 submodule |
| 开发与接手记录 | `logs\`、`docs\development.md`、`docs\agent-support.md` | 保留为自有补充；现有证据没有证明参考工程采用相同日志或说明路径 |
| 源码与测试布局 | `src\README.md` | `src` 作为用户项目的容器；不预建历史参考中的 `src\tests\`，测试路径服从下游技术栈 |

命名依据来自已有研究和初始蓝图的路径记录，详见[来源登记中的目录命名采用记录](../research/source-register.md)。借鉴目录不等于继承源码、强制完整 DDD 或让参考项目成为运行依赖。

## 3. 项目资料的最小内容

| 文件或目录 | 最小内容 |
|---|---|
| README | 项目目标、当前阶段、分阶段设置清单、按活动查找共享方法/表单/产物的人工入口、模板来源版本 |
| AGENTS | 短导航、按任务读取规则、缺失输入与停止条件；先链接已存在资料，P2 再连接 skills |
| 领域模型 | 共同术语、核心概念及关系、业务规则、限界上下文职责与交互、事实来源与未决项；具体填写要求见下节 |
| 业务需求（REQ） | 业务入口承接 PRD 的目标与范围；表单记录来源、相关领域规则/上下文、状态、业务要求及业务验收条件，必要时创建 `REQ-001-<slug>.md` |
| 软件要求（SR） | 上游 REQ 或明确任务依据、所属上下文、软件行为、边界与错误情况、带所属工件标识的验收条件、必要接口约定 |
| User Story（US） | 交付切片、需求链接、修改范围、实施清单、状态与记录链接；不是第二份要求，也不是需求到 VT 的必经层级 |
| 验证规格（VT） | 验证层次与目标、逐项限定所属工件的验收引用、步骤/测试标识、预期结果、实际结果及基线引用、结果适用性；不存测试代码 |
| `verification\README.md` | 按当前交付范围查找验收项与 VT 的覆盖索引，显式列出缺口和核对基线；关系与结果回源读取，不另存一份通过状态 |
| 开发日志 | 任务、日期和会话标识、分支或基线、变更、验证、阻塞、下一步 |
| 架构（ABB）与 ADR | 当前结构、关联需求与业务边界、必要设计约束及验证依据、选择理由与影响；不强制每个任务新增设计工件 |
| `src\README.md` | 任意类型项目的放置方式、保留原生布局、创建项目后登记开发命令的要求；不包含应用样例 |
| 开发说明 | 初始明确未配置；以后按子项目记录相对路径、环境、依赖、安装/构建/运行/测试命令、工作目录与排障入口 |
| Agent 接入说明 | GitHub Copilot App 首测目标、入口与技能位置、按客户端和版本记录的发现/使用结果、限制与手动读取方式；初始不标为已测 |
| `.gitignore` | 最小通用忽略规则，不忽略正式工件与开发日志；下游按真实工具补充，不预置整套语言配置 |
| PR 表单 | 任务依据、修改范围、实际验证、未决项与限制；不默认勾选通过、批准或已发布 |

技术栈未选定时，开发说明明确写“尚未配置”，不阻塞骨架使用；在用户决定创建具体项目后补全，不提供貌似成功的空测试脚本。首次设置的必需输入与可留未决项见[P0 决策 D09](../plan/decisions-and-risks.md)。文档模板预留填写提示是正常的，但任务开始前必须辨认哪些事实仍未确定。

正式文件可采用 `SR-001-<slug>.md`、`US-001-<slug>.md`、`ABB-001-<slug>.md` 和 `VT-001-<slug>.md` 等可读名称。编号只有在对应工件需要创建时才分配；不为凑齐追溯链编造需求，也不把示例批准状态带进新项目。PRD 仍是产品说明的用途，不将整个 PRD 简单等同一条 REQ。

开发日志入库，只保存必要摘要和原始报告链接。应用运行日志、完整聊天、凭据、个人绝对路径和含敏感数据的输出不入库；项目的 `.gitignore` 根据真实工具输出目录配置。

### 3.1 轻量 DDD 的最低填写要求

P1 在既定的 `domain-model\README.md` 中提供以下栏目与填写指引，P2 的 `define-requirements` 按同一要求工作；不增加第八类表单或新的建模 agent。

| 内容 | 必须能回答的问题 |
|---|---|
| 共同术语 | 当前上下文中这个词指什么？同名概念在不同上下文是否含义不同？ |
| 核心概念与关系 | 业务中有哪些重要对象、行为或状态，它们怎样关联？不能只列名词，不说明关系 |
| 业务规则与不变量 | 哪些条件必须成立、哪些行为禁止、规则在哪个范围内适用？规则引用稳定小节或标识 |
| 限界上下文 | 每个上下文负责和不负责什么，哪些业务事实由它维护？不能用目录名或技术层替代业务职责 |
| 上下文交互 | 哪一方提供什么业务信息或能力，另一方依赖什么约定？业务边界不要求与 repo、服务或 `src` 子项目一一对应 |
| 来源与未决项 | 哪些是用户已给出的事实、哪些是推导或待确认内容？相关 REQ/SR 如何定位其业务依据？ |

初始骨架只提供指引，不预填业务模型；涉及业务的任务按当前范围填写或引用已有模型。一个上下文足够时不人为拆分；纯文档维护或不涉及业务的任务说明不适用原因，不补造模型。实体、值对象、聚合、仓储模式和代码分层按实际需要采用，不是模板的强制实现形态。

### 3.2 追溯的载体与唯一来源

七类表单的数量不变：在 REQ 中补足业务验收及模型引用，在 SR 中补足上游依据，在 VT 中明确验证层次、目标验收项、执行基线和结果适用性。每个验收项的引用包含所属工件及稳定标识；模型规则也有可定位的小节。US 只组织交付，ABB/ADR 按需参与设计追溯，不为补齐链条而创建。

`verification\README.md` 从当前交付的验收项清单建立导航，包括尚无 VT 的项；不能只收集已有 VT 后声称覆盖完整。SR 保存其上游引用，VT 保存其目标验收引用；逆向关系通过这些引用和搜索核对，不要求在每端手工维护一套副本。索引只提供链接、缺口和核对基线，验收正文、关系和结果仍以所属工件为准。

业务验收、软件行为验证与适用的设计验证如何对应，以及缺口、悬空引用、变更影响和旧结果的处理，统一按[工作约定第 3–4 节](execution-contracts.md)设计。P1 将字段与填写约束落实到表单和目录说明，P2 将操作步骤落实到现有 skills；下游不通过链接本仓库未分发的设计文档来代替这些内容。

## 4. Copilot 优先，但不复制多份规则

| 入口 | 设计用法 |
|---|---|
| `AGENTS.md` | 通用规则与资料导航；不依赖特定模型、个人设置或隐藏会话 |
| `.github\copilot-instructions.md` | Copilot 仓库级引导，要求读取通用规则和当前任务资料 |
| `.github\instructions\*.instructions.md` | 用客户端支持的 `applyTo` 范围限定专项规则 |
| `.github\agents\*.agent.md` | 选择工作模式；主要内容引用 skill，工具限制按客户端验证 |
| `.github\skills\<name>\SKILL.md` | 活动方法的唯一正文，引用 `_templates\` 表单并说明正式产物目录 |
| `.github\prompts\*.prompt.md` | 提供当前任务输入并指向相应方法；不承载唯一的工作流程 |

GitHub 官方文档列出了多种 skill 目录，本方案只选 `.github\skills` 作为维护位置，以便 Copilot 原生使用。其他客户端不自动发现时，显式读取目标 `SKILL.md`；增加其他入口前先确认实际需要，避免 `.github`、`.agents`、`.claude` 下三套正文漂移。

AGENTS 和 Copilot 入口之间的链接不是自动加载保证。首版需要验证 Copilot 确实读到了任务要求与相关规则，而不是只看到文件存在。Custom agent 的未识别工具名可能被客户端忽略，不能靠名称推断限制有效。

Prompt files 是可选便利入口。GitHub.com 和 Copilot CLI 当前不支持 IDE 的 prompt files 体验时，直接用自然语言指定任务和相应 skill；核心流程不依赖斜杠命令、特定变量展开或客户端 handoff 功能。

这些位置和限制来自 2026-10-13 查阅的[GitHub 官方资料 Q1–Q4](../research/source-register.md)，不表示模板已经通过客户端兼容测试。

首测客户端已选为 **GitHub Copilot App**。App 的入口发现、元数据和工具配置支持需要单独实测，不能从 VS Code 或 Copilot CLI 推断。5 个 prompt files 保留为可选便利入口，不构成 App 的必需功能；不支持时用自然语言指定 skill。原生发现、显式读取与未验证必须分开记录。

### 首版能力的具体职责

方法正文只在下列 6 个 skills 中维护；填写表单仍引用 `_templates\items\`，不另建样例应用或脚本工具层。

| Skill | 输入 | 产物与边界 |
|---|---|---|
| `project-onboarding` | 仓库现状、用户已提供的项目目标与约束 | 完成可确认的设置项，记录其余未决项；不自动选技术栈、装依赖或初始化 `src` 项目 |
| `define-requirements` | 用户提供的目标、使用者、范围与业务事实 | 按轻量 DDD 指引梳理模型、规则和边界，形成可回溯来源的 REQ 草案及业务验收；缺事实先澄清 |
| `specify-feature` | 模型与已有需求或明确任务、当前结构与约束 | 复用已有依据，按需形成 SR 验收项及对应 VT 草案，列出覆盖缺口；US、ABB/ADR 按需创建，不自动批准 |
| `implement-task` | 明确任务、修改范围；编码时还需具体项目与真实开发说明 | 实施前检查相关业务依据与验证计划；发现模型或需求变化先处理影响，缺开发输入时不自行创建应用 |
| `verify-change` | 当前交付的完整验收项清单、变更、相关 VT 与结果 | 双向核对覆盖、悬空引用和基线适用性，再执行适用检查；文档检查与软件行为结果分开，缺口不得伪装成通过 |
| `record-handoff` | 任务、Git 状态、受影响工件、实际结果、缺口与阻塞 | 日志引用当前基线、待复核或未执行项；接手先重查事实与追溯，不把旧结果当当前结果 |

三个 agents 只定义工作模式：`planner` 引用 onboarding、需求与规格方法；`implementer` 引用实施、验证与交接方法；`reviewer` 引用验证方法。模型继承用户设置；工具范围在 App 中实测后才能描述为有效限制，不把 reviewer 当人工批准者。

| 可选 prompt | 引用的方法 |
|---|---|
| `start-project.prompt.md` | `project-onboarding` |
| `plan-feature.prompt.md` | `define-requirements`、`specify-feature` |
| `implement-task.prompt.md` | `implement-task`、`verify-change` |
| `review-change.prompt.md` | `verify-change` |
| `resume-work.prompt.md` | `record-handoff` 的接手核对，再按当前任务选择方法 |

仓库级 instructions 负责引导；`docs.instructions.md` 负责文档事实、状态和引用；`tests.instructions.md` 负责测试变更的真实执行与验收对应，不预设语言、测试目录或命令。P2 按目标客户端约定设置路径范围，并在通用入口说明如何显式读取；下游改变布局时同步调整范围，不宣称通用匹配能覆盖任意技术栈。

### 人与 Agent 共用的入口

正式 README 提供“我现在要做什么”的活动导航，列出必需输入、共享方法、表单与正式产物位置。人可以直接阅读 `SKILL.md` 的步骤并手工填写，Agent 从 `AGENTS.md` 进入同一方法；两者遵循相同的事实来源、追溯要求、完成条件和停止条件。不使用 Agent 或 prompt 快捷命令，不影响方法的可用性。

P1 先提供已存在的资料与表单入口；P2 将活动导航连接到六个已创建的 skills。Skill 正文使用人可执行的步骤，不将特定 Agent 角色或专属工具调用写成必经流程，也不再复制一套“人工版工作流”。Prompts 只补本次输入，不能改变方法的验收标准。

## 5. 首次设置与日常使用

1. 从整理后的正式模板创建仓库，或向已有项目合入需要的文件。
2. 按 README 填写用户已确认的项目目标与范围；可用 onboarding skill 协助。未选技术栈与命令保持未配置，不妨碍资料工作。
3. 当用户决定开始编码时，自行或明确要求 Agent 在 `src\` 中创建具体项目；使用所选技术栈的原生工具，登记实际路径、命令与验证结果，不自动套入预制应用。
4. 打开 GitHub Copilot App，选择实际可用的工作模式或直接描述任务；其他 Agent 先显式读取 `AGENTS.md`。
5. 按需完善领域与业务要求，细化 SR/US，在相应目录记录架构和验证；开发后更新日志与交接。需要 PR 时使用现有客户端和平台能力。

使用项目工具和现成 Copilot CLI 不违反“不自研 CLI”的定位。模板也不要求额外的全局 skill 安装、MCP 服务或个人知识库才能完成基本流程。

## 6. 复制、合入和更新

新项目复制后，文件归项目维护。模板更新只提供版本、差异和变更说明，由用户审阅合入；没有 `ans upgrade`、生成器托管文件类别或后台同步。

已有项目应先盘点 README、AGENTS、Copilot 配置、skills 和文档位置，再选择性合入。冲突时保留原内容并明确列出差异，不覆盖已有规则，也不自动迁移历史 PRD、任务或代码。

Git tag/release 记录模板版本，README 记录所用来源即可。应用依赖继续由项目原生依赖清单管理，不再增加 `agent.yaml`、`agent.lock.json` 或 `.agent-state` 作为必需文件。

## 7. 模板发布前必须处理的事项

当前研究目录含内部项目摘要；发布时需分离并审查，不能随业务模板复制或公开。只分发本蓝图所列、为下游编写的骨架文件，不包含应用样例。

按具体文件清单整理干净候选，不复制当前整仓及其历史，也不把本仓库的研究、设计、实施计划、制作日志或演练产物带给下游；发布候选中的链接不得依赖这些排除内容。处理边界与发布前决策见[P0 决策 D01](../plan/decisions-and-risks.md)。

把仓库设置为 GitHub template、配置可见性、分支保护、CI 权限和许可证都是单独的发布操作，不会因设计文档或模板文件存在而自动完成。本次完成本地制作与有限文档演练，未执行这些发布操作。

## 8. 已授权的六仓功能增强

2026-10-15 的执行请求在原 38 文件之上扩展功能，新增文件职责与依赖以[增强计划](../plan/2026-10-14-ddd-functional-alignment.md)为准，来源以[六仓能力矩阵](../research/ddd-capability-matrix.md)为准。上文数量和“只交付最低建模”的约定保留为已完成首版的历史范围，不把新计划文件当作已存在。

增强允许更多领域/QAS/战术/治理表单、九个共享方法及薄 prompts、数据 schema 和按需运行的 Python utilities。可选领域源接入不强制子模块；正文、关系、执行结果和派生视图保持单一来源。媒体、图/文档导出和交互记账有各自任务与授权边界，不恢复通用执行器或后台服务。

正式候选须在新增工具和方法交付后重新冻结具体 allowlist；源码研究、制作矩阵、计划、日志、测试/演练材料及 Git 历史不进入下游。核心文档仍可不安装维护工具而阅读，业务栈/应用继续由用户决定。
