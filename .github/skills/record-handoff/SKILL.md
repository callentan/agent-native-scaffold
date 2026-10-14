---
name: record-handoff
description: Use when pausing or finishing a task, handing work to another session, or resuming from incomplete logs and uncertain evidence.
---

# 记录交接与恢复任务

让接手者不靠旧聊天也能判断现状和下一步。日志只总结变化与链接权威记录，不再维护一份验收结果。

## 输入

- 当前任务、日期、会话标识、范围与授权；已确认判断及其来源。
- 实际 Git 分支、commit、暂存与未提交范围；本次修改/受影响的模型、REQ、SR、VT 和任务。
- 实际检查记录入口、对象/要求/VT 基线，精确缺口、待复核项、未执行工作与阻塞。

## 记录顺序

1. 读取[日志指引](../../../logs/README.md#recording)，使用[日志表单](../../../_templates/items/development-log.md#session)填“会话、任务与 Git 状态”。重新检查 Git，不预填干净；区分起始基线、当前 commit、已提交范围、原有与本次未提交范围及暂存情况。已有任务直接链接；确无持久来源的维护请求才填写表单的可选任务依据栏。
2. 在“本次变化”列实际路径/工件 ID、有关规则/需求/VT/任务及变化依据，说明未完成或无法保留的状态。长期决策引用其正式来源，不用进度日志替代需求或设计正文。
3. 在[实际结果入口](../../../_templates/items/development-log.md#verification)逐类链接真正存在的 VT 运行、报告或独立文档检查记录，以及其基线和访问限制。没有证据只写未执行或不可访问，不把旧摘要当新结果，不复制结果状态表。
4. 在[缺口与影响栏](../../../_templates/items/development-log.md#follow-up)写完整未覆盖/悬空验收 ID、受影响工件、当前适用性待复核入口、`not-run` 动作及原因；用 [verify-change](../verify-change/SKILL.md)核对来源。保留旧结果及原基线。
5. 在“阻塞与下一步”写需谁补什么、下一步的输入和授权前提、接手要重查的 Git/证据/外部状态。只保存必要事实与链接，不存完整聊天、凭据、个人绝对路径或敏感输出；本机报告注明局限，不称为跨机器证据。

<a id="resume"></a>
## 接手顺序

1. 从 [README](../../../README.md#resume) 和 [AGENTS](../../../AGENTS.md)进入，读当前任务、[领域事实](../../../domain-model/README.md)、相关 [REQ](../../../stakeholder-requirements/README.md)/[SR](../../../software-requirements/README.md)、[覆盖索引](../../../verification/README.md#coverage-index)、实际 VT 及[最近的相关日志](../../../logs/README.md#handoff)。索引和摘要不能代替目标原文。
2. 重新核对实际目录、Git 分支/commit/dirty 范围与记录是否一致；沿结果入口检查对象、要求、VT 基线及证据可访问性。报告不可访问就明确记录，旧“通过”不能继承为当前通过；日志也不能恢复未保存编辑或原进程。
3. 核对规则/范围/授权的变化，按 [verify-change](../verify-change/SKILL.md)检查语义影响、遗漏、待复核和 `not-run` 工作。仍未知的事实保持未知，先选择**尚未完成且输入齐备**的下一步，再读活动对应的方法；开发输入不足时可继续独立文档工作。
4. 对不确定是否已完成的外部操作，先核验可读状态或请求确认，不盲目重试。没有授权就不推送、不创建 PR，也不从旧日志推导新的副作用权限。把本次恢复发现、限制与下一步写入获授权的交接记录。

## 产出与完成

正式交接落在 `logs/YYYY-MM-DD-<task>-<session>.md`，字段沿用现有表单；任务、验收与运行仍由各自源文件维护。恢复时只更新获授权的记录，真正实施由对应活动方法负责。

接手者能从记录定位任务、当前基线、实际结果或其缺失、受影响项和输入齐备的下一步，即可完成交接；不代表所有工作完成、历史证据已恢复或行为验收通过。

## 停止条件

必需任务/证据不可读、Git 范围冲突、来源矛盾或授权变化不明时，停止依赖它的操作，说明限制并给出最小补充输入。不能靠旧聊天、重放不确定外部动作或补造结果越过阻塞。
