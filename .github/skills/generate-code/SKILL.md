---
name: generate-code
description: Use when initial code generation or project scaffolding is requested for an identified task, including when project, stack, target paths or execution inputs may be missing.
---

# 安全的初始代码生成

这是人和 Agent 共用的文件方法，不是生成器程序。只处理获准的初始生成；既有代码维护用 [implement-task](../implement-task/SKILL.md)，独立文档修正也走其文档路径，不为缺应用输入而停掉无关的文档任务。

## 输入

- 实际任务、已确认范围/非目标、行为来源及全部验收、计划 VT 和各自基线；US/ABB 仅在任务确实需要时提供。
- 用户选定的应用/项目、语言/栈及版本、目标位置、创建授权；[开发登记](../../../docs/development.md#project-registration)中的实际布局、环境/依赖来源、命令、各自 cwd 与报告位置。
- 获准读目录、拟写目录/文件和应保留内容；采用 [BC 配置](../../../architecture/README.md#bc-configuration)时的实际源根、路径、固定对象与只读性质。

<a id="preflight"></a>
## 生成前核对

1. 核对目录、Git 分支/完整 commit、暂存与原有修改。读取任务和实际来源，按 [specify-feature](../specify-feature/SKILL.md#plan-verification)核对验收/计划；未确认规则、不可读来源或冲突只支持问题/候选，不据此生成确定业务行为。
2. 逐项核实[项目创建输入](../../../docs/development.md#creation-inputs)及命令的执行授权。新项目尚无源码时明确其不存在，并核实预定原生布局与工具可产生的文件；已有项目保留实际布局。缺项目、栈/版本、路径、环境、真实命令/cwd/报告或创建权限时记 `blocked` 与精确缺项，相关行为 VT 为 `not-run`，不能借维护工具的 Python 栈、示例应用或假命令解阻。
3. 显式完整读取[架构](../../instructions/architecture.instructions.md)、[编码](../../instructions/coding.instructions.md)、[安全](../../instructions/security.instructions.md)及适用的[测试规则](../../instructions/tests.instructions.md)。规则 globs 不是全部真实代码位置，也不授权执行。
4. 解析每个拟写路径的实际根、父目录及链接目标，核对允许范围和全部已有内容。目录不符、越界、不可读或非空目标冲突均停止该写入并列确切路径；未经明确授权不覆盖、追加、删除、改名。已有文件的任务修改转维护路径，不用初始化器代替审查。保留原始字节/可回查快照；**跳过冲突不等于生成完整**。

<a id="proposed-files"></a>
## 拟生成说明

写入前向请求者展示或在获准任务记录中保存下列信息，不自动视为批准：

| 每个拟生成文件 | 需要记录的内容 |
|---|---|
| 路径与动作 | 解析后的准确目标、所属项目、原有内容/冲突及允许的创建范围 |
| 来源与职责 | 实际原文、固定基线、负责与不负责的行为；缺项不得变成默认实现 |
| 验收与 trace marker | 完整 owner-qualified ID/锚点，以及项目原生注释、测试标识或任务记录中的定位方式 |
| 原生生成/检查范围 | 真实工具及参数、明确 cwd、可能附带写入的文件、环境/依赖、报告位置与当前授权 |

没有足够信息列清输出、副作用或命令时停止依赖该工具的生成，不增加未展示的 bootstrap、依赖选择、认证/部署配置或测试工程。没有正式工件的维护任务可引用实际任务条件，不编造 ID。

<a id="generation"></a>
## 写入与验证

1. 仅对预检无冲突且已授权的目标进行生成；写前重新核对已有内容，保持用户内容、只读领域源及无关路径不变。若工具产生范围外输出或新冲突，停止后续动作，说明实际变化并请求处理，不自行清理所有者文件。
2. 对照拟生成说明核对实际 diff、来源和 trace marker；遗漏、跳过或未授权额外文件分别报告，不将部分生成称为完整。缺业务政策保留明确阻塞，不生成“看似可用”的默认行为。
3. 按 [verify-change](../verify-change/SKILL.md)仅运行已登记且获准的原生检查，核对发现/执行/跳过数和逐项报告。文件存在、编译成功、测试名或退出零均不能单独证明行为验收；未运行的测试为 `not-run`，不补造结果或自动生成测试来冒充执行。
4. 按 [record-handoff](../record-handoff/SKILL.md)链接实际文件、检查及其基线、保留内容、冲突与剩余输入。提交、安装、远端或发布另按当前授权处理，本方法不授予这些权限。

## 完成与停点

只有授权文件完整写入、差异与来源核对完成、所需原生检查有实际证据且残留缺口清楚时，才报告对应范围的生成结果。被阻塞/部分生成、文档推导、源码生成、实际运行和验收成功分别表述；任一缺源、路径冲突或执行前提不足都不能以“已完成”掩盖。
