---
name: project-onboarding
description: Use when joining an existing repository, adopting this skeleton, or starting with incomplete project information.
---

# 项目接入

先分清已有内容、已确认输入和未决事项。人可直接按本方法操作，不需要 Agent 服务，也不需要先有应用。

## 输入

- 当前任务的目标、范围、完成条件和授权；用户已确认的项目资料及来源。
- 当前目录、Git 状态、已有 README、AGENTS、规则与资料位置；采用的模板来源（如已确认）。

## 操作

1. 核对实际工作目录、分支、commit、暂存区和未提交范围；读取[项目登记](../../../README.md#project)及现有规则。区分原有内容与本次拟合入内容，保留所有者标记、规则位置和无关修改。逐项比较差异，不整仓覆盖或搬移代码。
2. 只把已确认的名称、阶段、范围摘要与来源版本填入项目登记；未知阶段不猜，版本无依据就保持原占位。目标、用户、范围与约束详情归[产品说明](../../../stakeholder-requirements/README.md#product)，不在 README 另存一份。
3. 把缺项按所影响的阶段登记：影响当前资料或业务决定的问题，写入产品说明的未决栏并注明阻塞范围；只影响以后编码的输入，留在[开发登记](../../../docs/development.md#project-registration)及[缺项栏](../../../docs/development.md#troubleshooting)。纯文档任务可以继续，不能为展示“已完成”补造信息。
4. 涉及业务时沿[领域来源](../../../domain-model/README.md#sources)核对事实，再使用 [define-requirements](../define-requirements/SKILL.md)；需要可选本地领域源时另读[登记与 materialization 的区别](../../../docs/domain-sources.md#operations)。技术或文档维护可说明业务建模不适用。接入本身不初始化代码、不安装依赖、不选择技术栈。只有用户选择项目、技术栈、位置并授权，且[真实开发输入](../../../docs/development.md#creation-inputs)齐备后，才另行进入实施。
5. 核对本次登记和链接，说明哪些字段仍未确认。用[日志表单](../../../_templates/items/development-log.md#session)记录任务与 Git 范围，在“本次变化”“实际结果入口”“阻塞与下一步”留下有效交接；按 [record-handoff](../record-handoff/SKILL.md)收尾，不用完整聊天代替记录。

## 产出与完成

正式内容按需落在根 `README.md`、`stakeholder-requirements/README.md`、`docs/development.md` 和 `logs/YYYY-MM-DD-<task>-<session>.md`，已有项目沿用其实际资料位置。日志字段见[日志指引](../../../logs/README.md#recording)。

已知信息有来源、原有内容保留、当前与后续阶段缺项分开且下一步明确，即可完成本次接入；这不表示开发环境已配置或业务验收已通过。

## 停止条件

资料不可读、行为事实冲突、合入冲突或授权不足时，保留现状，列出具体路径、问题和需谁确认什么，停止受影响的写入。缺技术栈只阻塞需要它的编码工作，不阻塞输入齐备的文档维护。
