---
name: implement-task
description: Use when an identified task is ready for scoped edits, or an implementation request may lack project or development inputs.
---

# 实施当前任务

以真实目录、任务依据和验收为起点。文档维护与编码走不同前提，不为执行一个请求而擅自生成工程。

## 输入

- 目标、范围、非目标、完成条件及授权来源；当前任务或已有 [US](../../../user-stories/README.md)（若有）。
- 实际工作树与 Git 状态；受影响模型、REQ、SR、VT 和必要设计。
- 编码时还需用户选定的项目、技术栈、位置与环境，以及已核实的[开发登记](../../../docs/development.md#project-registration)。

## 操作

1. 检查当前目录、分支、commit、暂存区、原有未提交改动和真实文件树；读取任务来源及其完成条件。修改 Markdown 时读[文档规则](../../instructions/docs.instructions.md)，修改任何测试时显式读[测试规则](../../instructions/tests.instructions.md)。修改代码还须完整读[架构](../../instructions/architecture.instructions.md)、[编码](../../instructions/coding.instructions.md)和[安全规则](../../instructions/security.instructions.md)，即使实际路径未匹配 globs，也不只依赖自动加载。
2. 写入前读受影响的领域规则/上下文、REQ、SR 和 VT；按 [specify-feature](../specify-feature/SKILL.md)确认适用的验收和实施前验证计划。若任务改变模型或要求，先按 [verify-change 的语义影响检查](../verify-change/SKILL.md#impact)处理来源、下游、预期和基线，不能只按旧任务机械实现。
3. 选择路径：
   - **纯文档维护：** 有明确路径、依据与完成条件即可按[文档检查说明](../../../docs/development.md#document-checks)继续；不等待技术栈，也不新建业务工件。
   - **初始代码生成：** 使用 [generate-code](../generate-code/SKILL.md)，本方法不重跑初始化器覆盖现有代码。[项目创建前提](../../../docs/development.md#creation-inputs)不齐备时不初始化或安装依赖。
   - **既有代码维护：** 核实用户选定项目/栈/位置/环境、真实源码/测试布局及命令/cwd/报告登记。采用 BC 配置时核对实际源根、相对路径、固定基线与只读性质，不回写来源。缺项就将受影响任务记为 `blocked`，相关检查为 `not-run`，列明需谁补什么；不能用新项目、默认栈或假命令解阻。
4. 输入齐备后，代码维护读取任务指定目录的相关实现、调用/边界、原生测试与已有 diff，建立可重复检查或实际复现；文档维护只核对指定资料、依据与适用文档检查，不要求应用布局。记录准确拟改文件和验收对应，再作最小完整修改；代码用项目既有注释/测试标识或任务记录定位完整 owner-qualified 验收，不创专用追溯框架。保留所有者内容、无关改动和原生布局；发生冲突、未预期路径写入或检查失败时停止受影响动作并定位，不切换到初始化覆盖、不缩小验收。
5. 按 [verify-change](../verify-change/SKILL.md)执行适用检查并保存真实证据，区分文档结果、行为 VT、旧结果与当前适用性。再次核对 diff 与任务范围，只按实际完成情况更新已有任务清单；清单勾选不是验收结果。
6. 按 [record-handoff](../record-handoff/SKILL.md)用[日志表单](../../../_templates/items/development-log.md#follow-up)留下改动、结果入口、精确缺口、阻塞及下一步。提交、推送、PR 或其他外部副作用另按实际授权处理，本方法不授予权限。

## 产出与完成

修改落在明确指定的文档或真实项目路径，测试保留项目原生位置；验证以现有 VT/实际报告为准，交接落在 `logs/YYYY-MM-DD-<task>-<session>.md`。不额外建立运行层、示例工程或任务镜像。

约定修改完成、适用检查有可追溯记录、未完成项明确且交接可继续，才报告对应任务状态。被阻塞的编码不能报完成；独立文档任务完成也不表示业务或软件验收通过。

## 停止条件

目录或输入与登记不符、行为事实未确认、必需资料不可读、修改冲突、检查失败未解释或授权不足时，停止受影响的操作并报告具体缺项。其他输入齐备且独立的文档工作不因此被一并阻塞。
