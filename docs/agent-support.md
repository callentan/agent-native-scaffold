# Agent 接入与验证记录

**GitHub Copilot App 是首测目标，原生发现与显式读取均未实测。** 文件已提供不等于客户端已经加载。P1 的结构检查、本次编写会话或子代理结果都不算 App 接入测试；其他客户端、版本或运行模式的结果也不能互相代用。

<a id="reading"></a>
## 通用文件读取路径

人从 [README 的活动导航](../README.md#activities)选择方法；能读仓库文件的 Agent 先显式读取 [AGENTS.md](../AGENTS.md)，再读取活动对应的完整 `SKILL.md`、适用规则和实际工件。链接用于导航，不是自动包含语法，也不保证客户端继续加载链接目标。

没有原生发现或 prompt 支持时也可使用普通文件读取，不要求个人/全局 skill、参考仓库权限或隐藏聊天。可用自然语言发起，实际输入由用户填写：

```text
请先显式读取仓库根目录 AGENTS.md。
本次目标、范围、依据与完成条件：【待填写】。
从 README 活动导航选择对应的 .github/skills/<活动>/SKILL.md，
完整读取后再操作，并读取文档或测试变更所适用的 instructions。
说明实际读取的文件、缺失输入与证据限制，不把链接视为已加载。
```

这只是显式读取的操作入口，不是实测结果。六个共享方法可由人直接应用；可选提示词不要求通用 slash 语法，任何核心方法都不依赖 prompt 加载。

<a id="entry-points"></a>
## 已提供的薄入口

| 表面 | 文件与职责 |
|---|---|
| 通用入口 | [AGENTS](../AGENTS.md) 指向人与 Agent 共用的活动导航 |
| 仓库 instructions | [copilot-instructions.md](../.github/copilot-instructions.md) 指向通用入口及任务规则 |
| 路径规则 | [docs.instructions.md](../.github/instructions/docs.instructions.md) 适用 Markdown；[tests.instructions.md](../.github/instructions/tests.instructions.md) 使用有限的测试路径/名称 globs |
| 自定义角色 | [planner](../.github/agents/planner.agent.md)、[implementer](../.github/agents/implementer.agent.md)、[reviewer](../.github/agents/reviewer.agent.md) 只选择方法与工作视角，不是自动团队 |
| 共享方法 | [project-onboarding](../.github/skills/project-onboarding/SKILL.md)、[define-requirements](../.github/skills/define-requirements/SKILL.md)、[specify-feature](../.github/skills/specify-feature/SKILL.md)、[implement-task](../.github/skills/implement-task/SKILL.md)、[verify-change](../.github/skills/verify-change/SKILL.md)、[record-handoff](../.github/skills/record-handoff/SKILL.md)；正文只在各自文件维护 |
| 可选提示词 | [start-project](../.github/prompts/start-project.prompt.md)、[plan-feature](../.github/prompts/plan-feature.prompt.md)、[implement-task](../.github/prompts/implement-task.prompt.md)、[review-change](../.github/prompts/review-change.prompt.md)、[resume-work](../.github/prompts/resume-work.prompt.md) 提供当前输入栏与方法链接 |

测试规则的模式不是通用命名全集，也不指定测试布局。真实项目应按实际路径扩展模式；修改任何测试时，即使自动匹配未发生也要显式读该规则。

<a id="evidence-types"></a>
## 分别记录四类依据

| 类别 | 可以说明什么 | 不能据此说明什么 |
|---|---|---|
| 原生发现已实测 | 指定客户端、版本、环境中，未显式要求读文件时实际观察到入口被发现和使用 | 不能仅凭文件存在、选择角色或手动读取断言原生发现 |
| 显式读取已实测 | 明确要求读取后实际观察到文件被读取并用于当前任务，保留输入与证据 | 不能推出自动发现、其他入口或其他客户端也可用 |
| 仅官方文档依据 | 有对应客户端/功能的官方资料，记录链接、查阅日期及适用版本 | 不能替代本项目中的实际验证 |
| 未验证 | 尚无足够观察；缺版本、缺环境或未执行都要说明 | 不能写成支持，也不能未经测试写成不支持 |

<a id="official-sources"></a>
## 已登记的官方依据

以下依据于 **2026-10-14** 核对，全部属于“仅官方文档依据”，不是本仓库的客户端测试。客户端变化后应重新核对适用范围。

| 官方资料 | 已确认的文档内容及边界 |
|---|---|
| [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | `description` 必需、`name` 可选；不写 `model` 继承用户设置。本仓库三个角色均不固定模型。文档列出 `read`、`search`、`execute` 等别名，未知工具名会被忽略，不能凭虚构名称宣称已限制权限 |
| [Add skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) | 仓库技能使用 `.github/skills/<lowercase-name>/SKILL.md`，包含 `name` 和 `description`。文件格式不是执行授权 |
| [Repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) | 路径规则的 `applyTo` 支持逗号分隔 glob；具体客户端发现/匹配行为仍须实测 |
| [Customize GitHub Copilot App](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app) | App 文档说明仓库/CLI skills 可用，并描述自定义 agent 选择器；这不是本项目在 App 中的观察结论 |
| [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) | 矩阵将 prompt files 列为 GitHub.com 与 CLI 不支持；不能由仓库中存在 prompt 文件推断会加载 |
| [VS Code prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files) | `description` 可选，可用相对 Markdown 链接；当前文档说明 Agent Host sessions 不加载 prompt files，Local agent 仍支持。不能笼统宣称所有 IDE 模式均可用 |

<a id="client-records"></a>
## 按客户端登记（待实测）

每个客户端、版本和环境分别复制下面的登记组。每次只记录一个具体入口和一种方式；原生发现与显式读取分开，单个 skill/agent/prompt 的结果不能代表同类所有文件。

| 本组上下文 | 实际值 |
|---|---|
| 客户端名称 | GitHub Copilot App（首测目标，尚未运行） |
| 客户端版本/构建号 | 待填写 |
| 环境 | 待填写：系统、运行模式、工作区、权限/工具配置；不记录秘密 |
| 日期、记录者与观察标识 | 待填写 |
| 对象基线 | 待填写：分支、commit、未提交范围及所用文件版本 |

下表均为未执行占位。实测时复制相应行并填写具体文件、输入、可观察行为和可访问的原始记录；未测的入口保留未验证。

| 入口/场景 | 方式（原生发现或显式读取） | 实际输入 | 实际发现的文件 | 实际读取的文件 | 结果与原始记录入口 | 纠正与待重测项 |
|---|---|---|---|---|---|---|
| AGENTS 通用入口 | 待分别测试 | 待填写 | 未观察 | 未观察 | 未验证 | 待填写 |
| 仓库 instructions | 待分别测试 | 待填写 | 未观察 | 未观察 | 未验证 | 待填写 |
| Markdown 路径规则 | 待分别测试 | 待填写：含实际目标路径 | 未观察 | 未观察 | 未验证 | 待填写 |
| 测试路径规则 | 待分别测试 | 待填写：含匹配/不匹配的实际路径 | 未观察 | 未观察 | 未验证 | 待填写 |
| 单个自定义 agent | 待分别测试 | 待填写：角色名称与任务 | 未观察 | 未观察 | 未验证 | 待填写 |
| 单个共享 skill | 待分别测试 | 待填写：任务触发或明确读取请求 | 未观察 | 未观察 | 未验证 | 待填写 |
| 单个可选 prompt | 待分别测试 | 待填写：文件及客户端运行模式 | 未观察 | 未观察 | 未验证 | 待填写 |

发现与读取要分开记录，不以“Agent 说已读取”或一次任务完成代替可观察证据。结果注明成功范围、失败现象或未执行原因；纠正后保留原记录并记录重测基线。官方资料与观察不一致时保留差异，区分发现失败、文档明确不支持和未测试，不混成一个“已支持”标记。

<a id="boundaries"></a>
## 权限与运行边界

复制 Markdown 或显式读取 AGENTS 不会启用 sandbox、审批、CI、分支保护或工具限制；这些能力必须由客户端、操作系统和托管平台配置并核验。本仓库未预置应用或语言 CI，命令状态以[开发说明](development.md)为准。

三个角色是工作视角，不是独立人工批准者或自动团队编排。reviewer 不声明 `tools` 限制，其只读要求只是对话约定，**未配置强制限制且未在 App 验证**，不是保证安全的工具边界。若以后配置工具别名，须按官方格式和真实客户端验证；文件规则不能代替权限配置。

方法与 prompt 不预先批准 shell、安装、提交、推送、PR 或其他外部副作用；操作仍按当前授权执行。不要把本机证据、旧会话权限或官方功能说明当作当前任务的授权。
