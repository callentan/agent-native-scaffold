# 仓库模板与 Agent 文件蓝图

**以下是计划交付的目录，不是当前已经存在的模板文件。当前仓库仍保留研究与设计资料。**

## 1. 一个模板，两组内容

正式模板的仓库根目录就是下游项目的起点，不再先安装一个框架再运行生成命令。项目资料与 Agent 能力文件一起分发，用户复制后直接拥有这些文件。

目录命名参考 DDD 工程及此前研究的 repo：领域侧借鉴 `ddd-subdomain` / `DM-Subdomain` 的职责，实现侧借鉴 `ddd-bc` / `DeviceRegistry-BC`，文档表单采用 `_templates` 的集中组织方式。我们把需要的内容组织在一个 repo 中，不沿用它们的 submodule 或多仓库部署方式。

参考源码、内部研究材料和本项目自身的设计讨论不应混进下游的 PRD 或业务文档。发布前先整理可分发内容，不能直接把当前研究仓库标为公开模板。

## 2. 建议的模板目录

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
    tests\
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

这是目标布局，不要求第一步填满所有目录。`src\tests\` 参考现有 BC 工程的测试布局；实际源码、测试工程、依赖清单和流水线在选定技术栈后创建。已有项目或技术栈有不同的标准路径时保留原布局，在入口说明，不重复建立另一套测试目录。

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

命名依据来自已有研究和初始蓝图的路径记录，详见[来源登记中的目录命名采用记录](../research/source-register.md)。借鉴目录不等于继承源码、强制完整 DDD 或让参考项目成为运行依赖。

## 3. 项目资料的最小内容

| 文件或目录 | 最小内容 |
|---|---|
| README | 项目目标、当前阶段、设置清单、目录导航、模板来源版本 |
| 领域模型 | 术语、业务规则、用例与边界；按实际复杂度补充，不生成空的领域事实 |
| 业务需求（REQ） | `stakeholder-requirements\README.md` 承接 PRD 的目标与范围，必要时用 `REQ-001-<slug>.md` 表达具体业务要求 |
| 软件要求（SR） | 关联业务要求、软件行为、边界与错误情况、验收条件、必要的接口或数据约定 |
| User Story（US） | 交付切片、SR 链接、修改范围、实施清单、状态、验证与日志链接；不是第二份软件要求 |
| 验证规格（VT） | 关联 SR/US 的验收条件、验证步骤或测试标识、执行结果位置；不存测试实现代码 |
| 开发日志 | 任务、日期和会话标识、分支或基线、变更、验证、阻塞、下一步 |
| 架构（ABB）与 ADR | 当前结构、必要设计、选择理由、被替代方案、影响；不强制每个任务新增设计工件 |
| 开发说明 | 实际操作系统、依赖、安装/构建/运行/测试命令、工作目录与排障入口 |
| Agent 接入说明 | 入口与技能位置、已测客户端、使用限制、手动读取方式 |

技术栈未选定时，开发说明明确写“尚未配置”，由首次设置补全；不提供貌似成功的空测试脚本。文档模板预留填写提示是正常的，但任务开始前必须辨认哪些事实仍未确定。

正式文件可采用 `SR-001-<slug>.md`、`US-001-<slug>.md`、`ABB-001-<slug>.md` 和 `VT-001-<slug>.md` 等可读名称。编号只有在对应工件需要创建时才分配；不为凑齐追溯链编造需求，也不把示例批准状态带进新项目。PRD 仍是产品说明的用途，不将整个 PRD 简单等同一条 REQ。

开发日志入库，只保存必要摘要和原始报告链接。应用运行日志、完整聊天、凭据、个人绝对路径和含敏感数据的输出不入库；项目的 `.gitignore` 根据真实工具输出目录配置。

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

## 5. 首次设置与日常使用

1. 从整理后的正式模板创建仓库，或向已有项目合入需要的文件。
2. 按 README 填写项目目标，确认技术栈和开发环境；可用 onboarding skill 协助，但不替用户猜业务事实。
3. 用项目原生工具初始化必要代码，记录并实际执行开发命令。
4. 打开 Copilot，选择工作模式或直接描述任务；其他 Agent 先显式读取 `AGENTS.md`。
5. 按需完善领域与业务要求，细化 SR/US，在相应目录记录架构和验证；开发后更新日志与交接。需要 PR 时使用现有客户端和平台能力。

使用项目工具和现成 Copilot CLI 不违反“不自研 CLI”的定位。模板也不要求额外的全局 skill 安装、MCP 服务或个人知识库才能完成基本流程。

## 6. 复制、合入和更新

新项目复制后，文件归项目维护。模板更新只提供版本、差异和变更说明，由用户审阅合入；没有 `ans upgrade`、生成器托管文件类别或后台同步。

已有项目应先盘点 README、AGENTS、Copilot 配置、skills 和文档位置，再选择性合入。冲突时保留原内容并明确列出差异，不覆盖已有规则，也不自动迁移历史 PRD、任务或代码。

Git tag/release 记录模板版本，README 记录所用来源即可。应用依赖继续由项目原生依赖清单管理，不再增加 `agent.yaml`、`agent.lock.json` 或 `.agent-state` 作为必需文件。

## 7. 模板发布前必须处理的事项

当前研究目录含内部项目摘要；发布时需分离并审查，不能随业务模板复制或公开。只分发自有或授权的通用内容与合成示例。

把仓库设置为 GitHub template、配置可见性、分支保护、CI 权限和许可证都是单独的发布操作，不会因设计文档或模板文件存在而自动完成。本次只调整设计，不执行这些操作。
