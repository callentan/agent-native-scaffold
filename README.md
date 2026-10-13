# 自有研发 Skeleton：Repo Template + Agent Kit

**状态：模板形态已明确，当前仍是研究与设计文档，尚未交付完整模板。设计调整：2026-10-13。**

我们的交付物是一套可直接使用的研发仓库模板：目录命名参考已有 DDD 工程，包含领域模型、需求、User Stories、架构、验证与开发记录，以及配套的 instructions、agents、skills 和 prompts。项目从模板开始，打开现有 coding agent 就能按同一套资料和流程工作，优先做好 GitHub Copilot 的使用体验。

不开发自己的 CLI、执行引擎或管理平台。现有 Agent 客户端负责读写文件和调用工具；项目自己的构建、测试和 CI 负责验证；模板提供可读的上下文、工作方法和记录格式。

## 已确认的定位

- 研究过的 repo 都只是参考项目，不是默认的代码底座、改造对象或运行依赖。
- 最终交付我们自己的 repo 模板及 Agent 能力文件，不要求安装额外的 skeleton 软件包。
- 以 GitHub Copilot 为主要使用对象，同时让其他能读取仓库文件的 Agent 接入。
- 目录和工件命名参考 DDD 及已有 repo 的例子；模板内容由我们维护，不继承参考项目的运行依赖。
- 保留 PRD、功能规格和任务的用途，按参考工程的需求与交付结构组织；不强制完整 DDD/V-model、.NET、Azure DevOps 或多仓库结构。

“不用 CLI”指不自研 skeleton CLI；用户仍可使用现成的 Copilot CLI、Git 和项目工具。产品形态与参考命名的方向已明确，具体文件内容仍是设计方案。

## 模板包含什么

| 内容 | 用途 |
|---|---|
| `domain-model\` | 领域术语、业务规则、用例和上下文边界 |
| `stakeholder-requirements\` | 产品目标、用户、场景与业务需求；承接 PRD 的产品说明 |
| `software-requirements\` | 软件要求（SR）：功能行为、接口约定、边界和验收条件 |
| `user-stories\` | 交付切片（US）、实施清单、范围、进度与完成条件 |
| `architecture\` | 架构说明、必要的设计工件（ABB）和架构决策 |
| `verification\` | 验证规格（VT）、验收映射与结果引用；测试代码与它分开 |
| `_templates\` | 集中维护可复制的文档表单，不与项目正式工件混放 |
| `logs\` | 开发记录、验证摘要、阻塞与交接；不保存完整聊天或敏感运行日志 |
| `docs\` | 开发环境、真实命令及 Agent 接入说明，不再重复存一套需求或架构 |
| `AGENTS.md` | 面向不同 Agent 的短入口：先读什么、怎样工作、何时停止 |
| `.github\copilot-instructions.md`、`.github\instructions\` | Copilot 的仓库级入口和按文件范围生效的约定 |
| `.github\agents\` | 可选择的规划、实现、审阅等工作模式，不是自建调度系统 |
| `.github\skills\` | 可重复的工作方法和配套资源，采用 `SKILL.md` 约定 |
| `.github\prompts\` | 启动项目、规划功能、实现任务、审阅和继续工作的快捷入口 |

具体布局和命名依据见[仓库模板蓝图](docs/design/repository-blueprint.md)。`logs` 与开发说明是自有补充，不声称参考仓库也采用相同路径。新项目的代码与测试布局参考 `src\`、`src\tests\`，具体服从技术栈；已有工程保留原路径。

## 怎样使用

正式模板发布后，通过 GitHub 的模板功能或复制获准的模板文件创建项目；已有项目则先对比并合入需要的文件，不覆盖原有说明和配置。

第一次使用时，按 README 完成项目名称、目标、技术栈和开发命令的设置，也可以让 Copilot 按初始化 skill 协助填写。之后围绕“领域与业务需求 → 必要的 SR/US → 实现与验证 → 日志与交接”工作。小修复可以直接关联已有工件或 issue，不必新建完整追溯链，也不把所有维护任务硬写成 User Story。

“开箱即用”是指研发资料、模板和 Agent 入口可直接使用，不是无需填写业务事实、安装所选技术栈，或配置组织权限，就能运行任意业务应用。

## 多 Agent 接入的边界

通用资料和 skill 正文都是可直接阅读的 Markdown，Copilot 专用文件只是原生入口，不另存一套业务事实。不自动识别这些文件的 Agent，可以显式读取 `AGENTS.md` 和相应 skill；后续专用入口也只引用同一套内容。

文件可读不等于所有客户端都自动发现或支持全部功能。例如，GitHub 官方支持表当前将 prompt files 列为 IDE 功能，GitHub.com 和 Copilot CLI 不支持同样的快捷入口。缺少该功能时使用自然语言指定任务和文件，不需要另造一个运行时。

权限、隔离、审批和 CI 必需检查由客户端、操作系统及托管平台实际配置。Markdown 约定不会自动建立这些保护，也不保证 Agent 永远遵守。兼容性需按客户端分别验证，不能宣称已经兼容所有 Agent。

## 文档导航

| 文档 | 回答的问题 |
|---|---|
| [总体设计](docs/design/architecture.md) | 项目资料与 Agent 能力如何组织，哪些交给现有工具 |
| [仓库模板蓝图](docs/design/repository-blueprint.md) | 目录、模板、Copilot 入口、复制与维护方式 |
| [研发工作流与交接约定](docs/design/execution-contracts.md) | 怎样开发、记录验证、暂停和换一个 Agent 继续 |
| [首版实施与验收](docs/plan/roadmap.md) | 首版先交付什么，怎样证明模板可用 |
| [决策与边界](docs/plan/decisions-and-risks.md) | 已确认的方向、尚未确定的细节和模板不能保证的事 |
| [参考仓库研究](docs/research/reference-repositories.md) | 可借鉴的模式与反例，不是改造清单 |
| [公开实践对照](docs/research/industry-patterns.md) | 哪些经验适合文件式模板，哪些不需要自建 |
| [来源登记](docs/research/source-register.md) | 历史研究证据及本次 Copilot 文件约定的官方依据 |

## 资料与发布边界

当前仓库含内部项目研究摘要，不能直接将整仓当作可公开的业务模板分发。正式发布前需分离研究材料和可分发内容，使用自有或获准的通用模板与合成示例。本次不搬运参考源码、不改变远端可见性，也不将仓库设置为 GitHub 模板。
