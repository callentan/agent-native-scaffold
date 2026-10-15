# Agent 接入与验证记录

**GitHub Copilot App 已有有限的真实会话观察，逐项结果见[模板入口观察](#template-observations)。** 文件已提供不等于客户端已经加载；单个角色或 skill 的结果不能代表全部入口。文件检查、普通子代理结果及其他客户端的行为也不能替代 App 实测。

<a id="reading"></a>
## 通用文件读取路径

人从 [README 的活动导航](../README.md#activities)选择方法；能读仓库文件的 Agent 先显式读取 [AGENTS.md](../AGENTS.md)，再读取活动对应的完整 `SKILL.md`、适用规则和实际工件。链接用于导航，不是自动包含语法，也不保证客户端继续加载链接目标。

没有原生发现或 prompt 支持时也可使用普通文件读取，不要求个人/全局 skill、参考仓库权限或隐藏聊天。可用自然语言发起，实际输入由用户填写：

```text
请先显式读取仓库根目录 AGENTS.md。
本次目标、范围、依据与完成条件：【待填写】。
从 README 活动导航选择对应的 .github/skills/<活动>/SKILL.md，
完整读取后再操作，并读取文档/测试及代码变更所适用的 instructions。
说明实际读取的文件、缺失输入与证据限制，不把链接视为已加载。
```

这只是显式读取的操作入口，不是实测结果。当前八个共享方法可由人直接应用；可选提示词不要求通用 slash 语法，任何核心方法都不依赖 prompt 加载。

<a id="entry-points"></a>
## 已提供的薄入口

| 表面 | 文件与职责 |
|---|---|
| 通用入口 | [AGENTS](../AGENTS.md) 指向人与 Agent 共用的活动导航 |
| 仓库 instructions | [copilot-instructions.md](../.github/copilot-instructions.md) 指向通用入口及任务规则 |
| 路径规则 | [docs](../.github/instructions/docs.instructions.md)、[tests](../.github/instructions/tests.instructions.md)、[architecture](../.github/instructions/architecture.instructions.md)、[coding](../.github/instructions/coding.instructions.md)、[security](../.github/instructions/security.instructions.md) 共五份；globs 均为初始匹配范围，不代表自动加载已验证 |
| 自定义角色 | [planner](../.github/agents/planner.agent.md)、[implementer](../.github/agents/implementer.agent.md)、[reviewer](../.github/agents/reviewer.agent.md) 只选择方法与工作视角，不是自动团队 |
| 共享方法 | [project-onboarding](../.github/skills/project-onboarding/SKILL.md)、[define-requirements](../.github/skills/define-requirements/SKILL.md)、[reverse-engineer-domain](../.github/skills/reverse-engineer-domain/SKILL.md)、[specify-feature](../.github/skills/specify-feature/SKILL.md)、[implement-task](../.github/skills/implement-task/SKILL.md)、[generate-code](../.github/skills/generate-code/SKILL.md)、[verify-change](../.github/skills/verify-change/SKILL.md)、[record-handoff](../.github/skills/record-handoff/SKILL.md)；正文只在各自文件维护 |
| 可选提示词 | [start-project](../.github/prompts/start-project.prompt.md)、[plan-feature](../.github/prompts/plan-feature.prompt.md)、[implement-task](../.github/prompts/implement-task.prompt.md)、[review-change](../.github/prompts/review-change.prompt.md)、[resume-work](../.github/prompts/resume-work.prompt.md) 提供当前输入栏与方法链接 |
| 领域活动提示词 | [domain-interview](../.github/prompts/domain-interview.prompt.md)、[reverse-engineering](../.github/prompts/reverse-engineering.prompt.md)、[distill-domain](../.github/prompts/distill-domain.prompt.md)、[glossary-sync](../.github/prompts/glossary-sync.prompt.md)、[published-interface](../.github/prompts/published-interface.prompt.md)、[amend-intended-use](../.github/prompts/amend-intended-use.prompt.md) |
| 只读审阅/查询提示词 | [review-artifacts](../.github/prompts/review-artifacts.prompt.md)、[assess-impact](../.github/prompts/assess-impact.prompt.md)、[query-artifacts](../.github/prompts/query-artifacts.prompt.md)、[review-backlog](../.github/prompts/review-backlog.prompt.md)；执行或写入仍须当前任务授权 |
| BC 活动提示词 | [derive-requirements](../.github/prompts/derive-requirements.prompt.md)、[design-architecture](../.github/prompts/design-architecture.prompt.md)、[plan-verification](../.github/prompts/plan-verification.prompt.md)、[generate-code](../.github/prompts/generate-code.prompt.md)、[sequence-diagram](../.github/prompts/sequence-diagram.prompt.md)、[build-architecture-spec](../.github/prompts/build-architecture-spec.prompt.md)；只给当前输入和实际方法链接 |

当前合计八方法、二十一提示词、三个模式。新增初始生成及 BC 入口没有增加角色或授予权限；既有七方法保留，未提供模板更新方法。新增方法/小节/规则的原生发现、App prompt 调用和人工使用尚未验证，显式读文件的有限使用不能补记为这些客户端结果。

测试规则的模式不是通用命名全集，也不指定测试布局。真实项目应按实际路径扩展模式；修改任何测试时，即使自动匹配未发生也要显式读该规则。

代码规则初始覆盖 `src/app/apps/lib/packages/services` 等目录，架构规则另覆盖 `architecture` 文档；它们不是所有代码位置。修改其他位置的代码同样要显式完整读架构/编码/安全和适用测试规则；不为匹配改布局，也不从配置文本推导自动生效或真实 ACL。

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
## 按客户端登记

每个客户端、版本和环境分别复制下面的登记组。每次只记录一个具体入口和一种方式；原生发现与显式读取分开，单个 skill/agent/prompt 的结果不能代表同类所有文件。

| 本组上下文 | 实际值 |
|---|---|
| 客户端名称 | GitHub Copilot App（本项目登记待填写） |
| 客户端版本/构建号 | 待填写 |
| 环境 | 待填写：系统、运行模式、工作区、权限/工具配置；不记录秘密 |
| 日期、记录者与观察标识 | 待填写 |
| 对象基线 | 待填写：分支、commit、未提交范围及所用文件版本 |

下表是供采用模板的项目填写的占位，不是下面模板制作观察的副本。实测时复制相应行并填写具体文件、输入、可观察行为和可访问的原始记录；未测的入口保留未验证。

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

<a id="template-observations"></a>
## 模板入口观察（2026-10-14）

本节是原六方法、五提示词基线的历史观察；不因新增文件或修订方法而扩展为当前八方法、二十一提示词已在 App 验证。

以下是模板制作期间四个真实 App 会话的有限实测，不是新项目已经完成接入。对象为 P2 内容的独立本地 Git 副本及其文档演练 checkpoint，没有远端或应用。App 创建隔离 worktree，分别使用默认工作模式及 API 选择 reviewer、planner、implementer，不使用普通 task 子代理替代客户端。没有观察 GUI agent picker，也没有重启整个共享 App。

| 环境与基线 | 实际观察 |
|---|---|
| 宿主与后端 | GitHub Copilot App 1.1.29，CLI 1.0.95-3；工具进程 ancestry 连接二者，版本来自进程文件，不是 About 对话框 |
| 系统与运行模式 | Windows 10.0.26200.0，PowerShell 7.6.6，App `interactive` worktree 会话 |
| 内容基线 | P2 候选的干净测试 checkpoint `7e478845fc64ceb0b66ba5b655771c543728d0eb`；App 接入 `29eacba`，部分变更接手输入 `59aebcd`，新会话交接 `312c3f8` |
| 个人配置限制 | 本机有个人/插件 skills 与 MCP，未卸载它们；本次证明的是项目方法实际从仓库加载，不是无个人配置的干净安装 |

| 入口 | 已观察的行为 | 尚未证明的行为 |
|---|---|---|
| 三个自定义工作模式 | App API 分别选定 reviewer/planner/implementer，原生 selected-agent 事件与仓库名称一致；前两者只读，后者只写获授权的交接记录 | GUI 选择器、任意任务下的表现和强制工具边界 |
| 六个项目 skills | 启动列表有六项，六项均出现 `source=project` 的原生调用与成功 tool completion；路径在各自 worktree 的 `.github\skills`，完整正文已交付并用于接入、规划或核对/交接 | 全部自然触发情形、其他模型/配置或客户端，不以这次有限使用推导一般可靠性 |
| AGENTS 与仓库 instructions | 启动内容与文件对应，随后实际显式读取两文件并沿活动导航工作 | 两者各自自动加载机制的隔离证明、链接递归包含 |
| 两个路径 instructions | 启动清单有文件与 `applyTo` 范围，正文实际读取 | 匹配与非匹配路径的自动生效 |
| 五个可选 prompts | 实际作为文件读取，流程不依赖快捷入口 | App 原生 prompt 调用；不能据此声称支持或不支持 |
| 无 prompt 的实际接入 | 自然语言任务配合原生方法加载/显式文件读取，填写固定项目名称和范围，留下真实日志与本地 checkpoint；技术栈和命令保持未配置 | 不能据此宣称 GUI 快捷入口已测或业务应用能运行 |
| Git 新会话接手 | 新 implementer 只凭仓库、日志和实际 Git 从 source checkpoint 接手，识别精确覆盖缺口、过期边界、历史 B1 来源与未执行项，只修改日志/索引 | 未实施整个额度规格修正，不将交接成功当作当前文档一致性或行为通过 |

三个角色的原生 selected-agent 事件均记录 `tools: ["*"]`，与文件未配置白名单一致。reviewer/planner 实际遵守本次只读约定，不是工具权限被限制，也不证明 App/OS 的额外安全控制。没有使用危险操作试探拦截。

原始会话和工具事件由模板制作会话保存在本机，未随候选分发；分发副本不能把这段摘要当作可自行访问的原始报告。使用者应在自己的客户端、版本与权限配置下重新填写上面的项目登记，不能继承未测试入口的结论。

<a id="boundaries"></a>
## 权限与运行边界

复制 Markdown 或显式读取 AGENTS 不会启用 sandbox、审批、CI、分支保护或工具限制；这些能力必须由客户端、操作系统和托管平台配置并核验。本仓库未预置应用或语言 CI，命令状态以[开发说明](development.md)为准。

三个角色是工作视角，不是独立人工批准者或自动团队编排。reviewer 不声明 `tools` 限制，其只读要求只是对话约定；入口观察中实际工具选择为 `["*"]`，**角色没有建立强制只读边界，也不证明宿主安全控制有效**。若以后配置工具别名，须按官方格式和真实客户端验证；文件规则不能代替权限配置。

方法与 prompt 不预先批准 shell、安装、提交、推送、PR 或其他外部副作用；操作仍按当前授权执行。不要把本机证据、旧会话权限或官方功能说明当作当前任务的授权。
