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

1. 检查当前目录、分支、commit、暂存区、原有未提交改动和真实文件树；读取任务来源及其完成条件。修改 Markdown 时读[文档规则](../../instructions/docs.instructions.md)，修改任何测试时显式读[测试规则](../../instructions/tests.instructions.md)，不只依赖自动匹配。
2. 写入前读受影响的领域规则/上下文、REQ、SR 和 VT；按 [specify-feature](../specify-feature/SKILL.md)确认适用的验收和实施前验证计划。若任务改变模型或要求，先按 [verify-change 的语义影响检查](../verify-change/SKILL.md#impact)处理来源、下游、预期和基线，不能只按旧任务机械实现。
3. 选择路径：
   - **纯文档维护：** 有明确路径、依据与完成条件即可按[文档检查说明](../../../docs/development.md#document-checks)继续；不等待技术栈，也不新建业务工件。
   - **编码：** 核实用户选定项目/栈/位置/环境、真实源码与测试布局、配置中的命令/cwd/报告位置及授权。缺项就将受影响任务记为 `blocked`，相关未执行检查记为 `not-run`，列出需要谁补什么；不能用新项目、默认栈或假命令解阻。[项目创建前提](../../../docs/development.md#creation-inputs)不齐备时不初始化或安装依赖。
4. 输入齐备后，按实际任务选择可重复的现有检查或复现，进行最小完整修改，保留无关内容和原生布局。只执行已确认且获授权的操作；发现范围扩大、意外副作用或失败时先定位原因，不静默换检查对象或降低完成条件。
5. 按 [verify-change](../verify-change/SKILL.md)执行适用检查并保存真实证据，区分文档结果、行为 VT、旧结果与当前适用性。再次核对 diff 与任务范围，只按实际完成情况更新已有任务清单；清单勾选不是验收结果。
6. 按 [record-handoff](../record-handoff/SKILL.md)用[日志表单](../../../_templates/items/development-log.md#follow-up)留下改动、结果入口、精确缺口、阻塞及下一步。提交、推送、PR 或其他外部副作用另按实际授权处理，本方法不授予权限。

## 产出与完成

修改落在明确指定的文档或真实项目路径，测试保留项目原生位置；验证以现有 VT/实际报告为准，交接落在 `logs/YYYY-MM-DD-<task>-<session>.md`。不额外建立运行层、示例工程或任务镜像。

约定修改完成、适用检查有可追溯记录、未完成项明确且交接可继续，才报告对应任务状态。被阻塞的编码不能报完成；独立文档任务完成也不表示业务或软件验收通过。

## 停止条件

目录或输入与登记不符、行为事实未确认、必需资料不可读、修改冲突、检查失败未解释或授权不足时，停止受影响的操作并报告具体缺项。其他输入齐备且独立的文档工作不因此被一并阻塞。
