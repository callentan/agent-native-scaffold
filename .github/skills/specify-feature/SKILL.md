---
name: specify-feature
description: Use when a feature or maintenance task has a basis but its software acceptance, boundaries, or verification plans are not yet precise.
---

# 细化行为与验证计划

实施前先确定要观察什么、由哪一层验收、怎样逐项判定。规格与验证计划可以先完成，执行结果不能预填。

## 输入

- 本次任务、范围与完成条件；实际领域模型和 REQ，或可定位的独立维护请求。
- 当前验收、相关 SR/VT、必要设计及对象基线；[开发说明](../../../docs/development.md)中的真实配置或未配置状态。

## 操作

1. 读取实际依据，确认任务涉及的规则、上下文与非目标；业务含义未清时回到 [define-requirements](../define-requirements/SKILL.md)。独立维护请求可直接作依据，不补造业务链。
2. 需要独立软件规格时按[SR 指引](../../../software-requirements/README.md#sr-writing)填写 [SR 表单](../../../_templates/items/software-requirement.md#basis)：在“上游 REQ 验收项或明确任务依据”维护来源；在“软件行为与边界”“接口与责任约定”写正常、边界、错误和禁止副作用，未知接口或政策保留未决。软件验收逐项使用完整 ID 与锚点，并在“对应上游验收项或任务完成条件”给出精确链接。
3. 按需要选择附加工件：交付拆分用 [US](../../../_templates/items/user-story.md)，独立结构约束用 [ABB](../../../_templates/items/architecture-building-block.md)，真实取舍用 [ADR](../../../_templates/items/architecture-decision.md)。判定依据见[交付指引](../../../user-stories/README.md#delivery)和[架构指引](../../../architecture/README.md)。没有相应需要就不建；US 不是 REQ/SR 到 VT 的桥梁。
4. 在写验证计划前，按[全量验收盘点](../../../verification/README.md#coverage-check)列出所有范围内 REQ、SR、必要设计和维护完成条件的所有者、完整 ID、原文链接与基线；包括没有 VT 的项。先记录缺口，再寻找既有计划，不能只盘点已有 VT。
5. 根据[验证层次](../../../verification/README.md#layers)分别规划业务验收与软件行为，按需加入设计或独立文档检查。使用 [VT 表单](../../../_templates/items/verification-test.md#plan)，每个目标在“逐项目标与判据”独占一行：完整目标 ID、所属条目稳定链接、独立判定标准、对应步骤/测试标识、前提与未决项。多目标不能共用一句“全部通过”；VT 拥有这些目标关系，SR 拥有上游关系。
6. 填清 VT 的计划对象、要求/任务及 VT 计划基线，登记实际可用的方法、环境、cwd、命令来源和报告位置；不存在的项目、命令或测试标识不猜。初始计划保持草稿/待确认，每个目标为 `not-run` 并说明缺项。业务验收不是软件通过的汇总，文档检查不能填入行为 VT 冒充执行。
7. 在[验证索引](../../../verification/README.md#coverage-index)登记来源、核对基线和精确缺口，不另建结果表。规格或规则有变更时按 [verify-change](../verify-change/SKILL.md)复核影响；把已具备输入的实施任务交给 [implement-task](../implement-task/SKILL.md)。

## 产出与完成

按需创建或修订 `software-requirements/SR-NNN-<slug>.md`、`verification/VT-NNN-<slug>.md` 和验证索引；可选工件落在各自指引指定的 `user-stories`、`architecture` 位置。正式内容不留在表单里。

全部范围内验收已盘点、逐项目标与层次明确、实施前的验证计划和缺项可定位，才可交付本次规格/计划；不表示行为验证通过。没有应用时应用检查对文档任务不适用，已规划的业务/软件 VT 仍为 `not-run`。

## 停止条件

来源不能确定行为、验收目标无法定位、边界冲突或授权不明时，停止受影响的规格确认/实施，保留已知草稿与精确缺口。不能通过删除范围内验收、强建 US 或把其他层结果挪用过来结束任务。
