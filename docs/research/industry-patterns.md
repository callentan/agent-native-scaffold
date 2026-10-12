# 公开主流实践对照

## 1. 研究口径

这里的“主流”指 OpenAI、Anthropic、GitHub、Cursor 等有代表性的公开工程实践与开放约定，不是市场占有率调查，也不是各家公司已经达成统一标准。

资料以官方正文为主，访问日期为 2026-10-12。实验文章、开放格式、产品功能与公开预览分别标明，不能互相替代。完整链接和读取范围见[来源登记](source-register.md)。

## 2. 最值得采用的模式

| 来源 | 已公开的模式 | 适合本项目的部分 | 不应直接照搬的部分 |
|---|---|---|---|
| [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)（P1，工程实验） | 短 AGENTS 入口、仓库作为知识记录、可观测开发环境、机械架构检查、持续文档维护 | 把可读性、可运行性和可验证性作为框架交付物 | 文中的少阻塞合并门、agent 自主合并，不适合作为本项目默认治理 |
| [Anthropic 长时任务 harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（P2，研究实践） | 初始化与增量执行分工、功能列表、交接记录、真实 E2E 验证 | 小任务、可恢复检查点、先检查基线再开发 | JSON 的 `passes` 字段和 agent 自述不是不可伪造的验收证明 |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices)（P3，产品实践） | 给 agent 可运行的验证条件；先探索和计划；精简常驻说明；权限与隔离 | 统一验证入口、按需上下文、任务范围与权限分离 | 不把某个客户端专有命令或权限模式当作跨工具标准 |
| [GitHub Spec Kit](https://github.com/github/spec-kit)（P4，开源工具） | specification → plan → tasks → implement → converge，项目 constitution | 规范和执行计划作为一等工件；按任务选择流程 | SDD 工件不能代替运行隔离、可信审批或实际测试证据 |
| [AGENTS.md](https://github.com/agentsmd/agents.md)（P5，开放格式） | 面向 agent 的可预测仓库入口 | 统一导航、命令、约束、停止条件 | 不写成巨型百科；不同客户端的加载与覆盖行为仍需验证 |
| [Agent Skills](https://agentskills.io/specification)（P6，格式规范） | SKILL.md + references/scripts/assets，渐进式披露 | 工作流技能包与按需加载 | `allowed-tools` 是实验字段，不能作为操作系统或托管平台 ACL |
| [GitHub Agentic Workflows](https://docs.github.com/en/copilot/concepts/agents/about-github-agentic-workflows)（P7，public preview） | Markdown 定义、编译后的执行配置、只读默认、safe outputs、凭据隔离 | 将“提议操作”和“执行有权限的操作”分开 | 不是 Azure DevOps 原生能力；不能把 GitHub YAML 原样搬过去 |
| [Cursor 长时多 agent 实验](https://cursor.com/blog/scaling-agents)（P8，规模实验） | 分离 planner/worker；共享锁和自协调会失败；结构需要迭代 | 任务所有权、隔离、显式依赖、少量独立并行 | 上百 agent、同分支写入、代码行数不应成为本项目目标 |
| [Anthropic Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)（P9，基础模式） | 简单组合优先；固定工作流与自主决策分开；环境反馈和停止条件 | 确定性外壳包住非确定性执行 | 不为“AI-native”默认引入复杂通用 agent 框架 |

## 3. 可归纳成三条路线

### 路线 A：让仓库成为 agent 的工作环境

核心不是“多提供上下文”，而是**提供正确、可定位、有版本和可信度的信息**。

采用：

- 短入口指向深层文档，不把整个知识库常驻注入。
- 业务规范、架构决定、运行方式、已知问题能在授权范围内被读取。
- 每个关键约束尽量有检查器，而不只是一句“必须遵守”。
- 可查询日志、测试报告、API 行为；UI 项目才进一步提供浏览器验证。

与参考框架的结合：保留 DDD 工件目录与术语，新增可解析索引和任务上下文包。

### 路线 B：把一次对话变成可恢复交付

长时任务的难点包括错误宣布完成、遗忘、上下文耗尽和留下半成品。

采用：

- 一次执行绑定一组固定输入版本和一项明确交付目标。
- 每次恢复先核验基线、未提交改动和已有运行证据。
- 可解释的暂停、失败、预算耗尽和升级状态。
- 清晰的 handoff，而非把上次聊天全文当唯一记忆。

与参考框架的结合：`BL-NNN` 继续记录未知项，但任务进度、运行状态和验收结果进入专门契约，不能全部挤进 backlog 或 `model.yaml`。

### 路线 C：让自主权受工程机制约束

成熟方向并非“agent 什么都不能做”，而是**低风险操作自动化，高风险决定由可审计策略约束**。

采用：

- worker 使用最小权限和隔离环境。
- 外部写入由受信发布器执行，令牌不进入 agent 上下文。
- 受保护检查器独立确认运行结果。
- 自动化的风险预算与停止条件有明确所有者。

与参考框架的结合：人类批准领域意图和风险边界，agent 自主完成批准范围内的代码与测试，不自行批准新增业务事实。

## 4. 需要处理的取舍

### 4.1 Spec-driven 与 harness engineering 是互补关系

Spec-driven 回答“做什么、为什么、验收是什么”；harness 回答“如何可靠运行、知道当前状态、失败怎样恢复”。

只做前者会得到大量文档和人工操作；只做后者会更快地实现未经确认的需求。新框架必须连接两者，但让小改动使用轻流程，避免每次修一个拼写都经历完整 V-model。

### 4.2 角色 agent 与工作流节点不能混为一谈

参考 ADR 拒绝 PM → Architect → Developer → QA 式角色主流程；Cursor 的 planner/worker 实验并不意味着应推翻该决策。

规划、执行、验证可以是不同职责，甚至由不同进程承担；业务事实和审批权仍不能由“扮演某角色”产生。MVP 使用一个 coding worker，独立验证主要由程序完成；只有明确不共享写集合的任务才考虑并行。

### 4.3 敏捷自治与监管治理不是二选一

可以自动执行重复劳动，而不把 Intended Use、风险接受或未知领域判断交给模型。相反，如果让 agent 自己降低规则强度，任何“regulated profile”都会失去意义。

监管配置必须由合格责任人确认。框架提供证据能力，不宣称仅安装一个 profile 就达到法规合规。

### 4.4 统一接口不等于所有工具天然兼容

AGENTS、Skills、MCP 的作用分别是入口、能力包和工具连接。它们不是统一的完整执行协议，也不会自动消除不同 agent 的权限、恢复、上下文和输出差异。

新框架需要少量适配器和兼容用例，而不是声称“一份 prompt 可在任何模型上可靠运行”。

## 5. 建设与复用边界

| 能力 | 建议 |
|---|---|
| 模型推理、编辑、终端工具循环 | 复用 Copilot CLI / Claude Code / Codex 等现有运行时；首版选一种 |
| 一般需求规范流程 | 参考 Spec Kit；可做导入映射，不同时维护两个权威 spec |
| Skill 分发格式 | 使用 Agent Skills 约定，验证目标客户端支持的实际安装路径 |
| 项目身份、任务契约、追溯规则、策略执行 | 新框架核心价值，应自己拥有 |
| Git、测试框架、容器、CI 和代码托管 | 复用现有工具，不重新实现 |
| 图数据库、向量库、agent 通讯总线、Web 控制台 | 暂不建设；先用文件、索引和单主状态存储验证必要性 |
| 多 agent 调度 | 后续基于评估增加；不作为 AI-native 的定义 |

## 6. 不以这些指标证明成功

不使用代码行数、prompt 数量、agent 数量或累计 token 作为主要成果指标。主要观察：

- 在冻结验收条件下，任务是否真正交付；
- 错误宣布完成、越界修改和失效审批是否被阻止；
- 人工澄清、返工、评审与恢复成本是否下降；
- 换一个新会话或受支持的运行环境后，能否继续可靠工作。

这些指标的目标和试验方法见[实施计划](../plan/roadmap.md)。
