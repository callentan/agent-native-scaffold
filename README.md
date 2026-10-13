# 自有研发 Skeleton：Repo Template + Agent Kit

**状态：P0 决策已完成，P1 资料骨架待制作；当前仍是研究与设计文档，尚未交付完整模板。更新：2026-10-13。**

我们的交付物是一套可直接使用的研发仓库模板：目录命名参考已有 DDD 工程，包含领域模型、需求、User Stories、架构、验证与开发记录，以及配套的 instructions、agents、skills 和 prompts。项目从模板开始，打开现有 coding agent 就能按同一套资料和流程工作，优先做好 GitHub Copilot 的使用体验。

**DDD 负责业务模型与边界，V-model 负责需求到验证的追溯，prompts/templates 配合共享 skills 让人和 Agent 按统一流程工作。** 首版提供最低建模与追溯约定，不仅借用目录名；也不强制完整 DDD/V-model、特定代码模式或技术栈。

不开发自己的 CLI、执行引擎或管理平台。现有 Agent 客户端负责读写文件和调用工具；项目自己的构建、测试和 CI 负责验证；模板提供可读的上下文、工作方法和记录格式。

## 已确认的定位

- 研究过的 repo 都只是参考项目，不是默认的代码底座、改造对象或运行依赖。
- 最终交付我们自己的 repo 模板及 Agent 能力文件，不要求安装额外的 skeleton 软件包。
- 以 GitHub Copilot App 为首测使用界面，同时让其他能读取仓库文件的 Agent 接入；客户端支持分别记录。
- 交付已经定义好结构和工作方法的 repo 骨架，用户在 `src\` 内创建任意类型的项目；不预置业务应用、技术栈或依赖。
- 目录和工件命名参考 DDD 及已有 repo 的例子；模板内容由我们维护，不继承参考项目的运行依赖。
- 保留 PRD、功能规格和任务的用途，按参考工程的需求与交付结构组织；不强制完整 DDD/V-model、.NET、Azure DevOps 或多仓库结构。

“不用 CLI”指不自研 skeleton CLI；用户仍可使用现成的 Copilot CLI、Git 和项目工具。首版范围、文件职责及方法要求已在[P0 决策](docs/plan/decisions-and-risks.md)中确定，正式文件尚待制作。首版验收骨架、入口、纯文档建模与追溯、变更影响及交接，不要求创建或接入业务项目。

## 模板包含什么

| 内容 | 用途 |
|---|---|
| `domain-model\` | 共同术语、核心概念及关系、业务规则、上下文职责与交互、事实来源 |
| `stakeholder-requirements\` | 产品目标、用户、场景与业务需求；承接 PRD 的产品说明 |
| `software-requirements\` | 软件要求（SR）：功能行为、接口约定、边界和验收条件 |
| `user-stories\` | 交付切片（US）、实施清单、范围与进度；不是需求到验证的必经层级 |
| `architecture\` | 架构说明、必要的设计工件（ABB）和架构决策 |
| `verification\` | 分层验证规格（VT）、覆盖索引、缺口与结果基线引用；映射完整不等于验证通过 |
| `_templates\` | 集中维护可复制的文档表单，不与项目正式工件混放 |
| `logs\` | 开发记录、验证摘要、阻塞与交接；不保存完整聊天或敏感运行日志 |
| `docs\` | 开发环境、真实命令及 Agent 接入说明，不再重复存一套需求或架构 |
| `src\` | 只预置使用说明；由用户放入任意类型的项目，保留该项目原生代码与测试布局 |
| `AGENTS.md` | 面向不同 Agent 的短入口：先读什么、怎样工作、何时停止 |
| `.github\copilot-instructions.md`、`.github\instructions\` | Copilot 的仓库级入口和按文件范围生效的约定 |
| `.github\agents\` | 可选择的规划、实现、审阅等工作模式，不是自建调度系统 |
| `.github\skills\` | 人和 Agent 共用的可读工作方法，采用 `SKILL.md` 约定 |
| `.github\prompts\` | 可选的设置、规划、实施、审阅与继续工作入口；不作为 App 必需功能 |

具体布局和命名依据见[仓库模板蓝图](docs/design/repository-blueprint.md)。`logs` 与开发说明是自有补充，不声称参考仓库也采用相同路径。首版不预建 `src\tests\` 或任何语言工程；代码、测试、依赖与流水线由下游项目决定，已有工程保留原路径。

## 怎样使用

正式模板发布后，通过 GitHub 的模板功能或复制获准的模板文件创建项目；已有项目则先对比并合入需要的文件，不覆盖原有说明和配置。

第一次使用时，按 README 填写用户已确认的项目名称、目标与范围，也可以让 Copilot 按 onboarding skill 协助填写；技术栈与开发命令可以保持未配置。用户决定在 `src\` 中创建项目后，再按该项目补齐环境、工作目录与真实命令，不由骨架自动选栈或生成应用。

日常围绕“领域与业务需求 → 必要的 SR/US → 实现与验证 → 日志与交接”工作。小修复可以直接关联已有工件或 issue，不必新建完整追溯链，也不把所有维护任务硬写成 User Story。

正式骨架的 README 将提供按活动查找方法、表单与产物的导航：人可直接阅读同一份 skill 并手工操作，Agent 从 AGENTS 或可选 prompt 进入相同方法，不维护两套流程。需求或领域规则变化后，沿引用检查受影响工件与旧结果，明确覆盖缺口、待复核和未执行项。

“开箱即用”是指研发资料、模板和 Agent 入口可直接使用，不是无需填写业务事实、安装所选技术栈，或配置组织权限，就能运行任意业务应用。

## 多 Agent 接入的边界

通用资料和 skill 正文都是可直接阅读的 Markdown，Copilot 专用文件只是原生入口，不另存一套业务事实。不自动识别这些文件的 Agent，可以显式读取 `AGENTS.md` 和相应 skill；后续专用入口也只引用同一套内容。

文件可读不等于所有客户端都自动发现或支持全部功能。例如，GitHub 官方支持表当前将 prompt files 列为 IDE 功能，GitHub.com 和 Copilot CLI 不支持同样的快捷入口。缺少该功能时使用自然语言指定任务和文件，不需要另造一个运行时。

GitHub Copilot App 的入口发现与使用行为将在 P3 单独记录，当前不视为已验证，也不沿用 VS Code 或 Copilot CLI 的结论。

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

当前仓库含内部项目研究摘要，不能直接将整仓当作可公开的业务模板分发。正式发布前按骨架文件清单整理干净候选，不复制研究、设计、实施计划、制作日志、演练产物或 Git 历史；只使用自有或获准的通用内容。许可证、发布位置、版本、维护者与权限在发布前确认。本次不搬运参考源码、不改变远端可见性，也不将仓库设置为 GitHub 模板。
