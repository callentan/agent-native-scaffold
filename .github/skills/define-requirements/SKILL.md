---
name: define-requirements
description: Use when supplied business goals or rules need clarification, a domain model is incomplete, or a business requirement changes.
---

# 整理领域事实与业务需求

先把业务含义和来源说清，再写可观察的业务验收。只建当前任务需要的模型与需求，不用技术模式填补未知事实。

## 输入

- 用户提供的目标、使用者、范围、约束与来源；哪些已确认、哪些只是提案。
- 现有[产品说明](../../../stakeholder-requirements/README.md#product)、领域模型、REQ 和本次变更依据。

## 操作

1. 对照输入整理目标、用户、范围内外事项和来源，填入产品说明的对应栏。只问会改变当前行为或范围的缺项，区分阻塞当前步骤的问题与可留待后续的问题。纯技术或文档维护可说明业务建模不适用，直接使用明确任务，不制造 REQ。
2. 在[共同术语](../../../domain-model/README.md#terms)说明业务含义与上下文；在[概念与关系](../../../domain-model/README.md#concepts)同时记录概念、状态含义及关系的方向、数量与成立条件。未知关系约束保持未决，不能只有名词清单。
3. 在[上下文职责](../../../domain-model/README.md#contexts)写清负责、不负责、拥有的事实及只消费的外部事实；在[定向信息交换](../../../domain-model/README.md#exchanges)明确提供方 → 使用方、事实所有者及已知业务约定。不强拆服务，不默认聚合、仓储或其他战术设计。
4. 按[规则栏](../../../domain-model/README.md#rules)分配稳定规则 ID 和锚点，写条件、边界、禁止行为及未知项；把事实来源、确认人与日期记入[来源栏](../../../domain-model/README.md#sources)。规则正文只维护一次；已有规则改变时先按 [verify-change 的影响检查](../verify-change/SKILL.md#impact)处理依赖。
5. 需要正式业务需求时按[REQ 指引](../../../stakeholder-requirements/README.md#req-writing)使用 [REQ 表单](../../../_templates/items/stakeholder-requirement.md#basis)，填写来源/状态、业务需要与范围，链接实际概念、上下文及规则。验收使用“前提与场景→动作→可观察结果→边界/禁止结果”的表单字段，每项分配带所属工件的完整稳定 ID 与锚点，如 `REQ-NNN-AC-01`；不复制规则正文，也不只写 `AC-01`。
6. 在 REQ 的“变更与未决项”保留问题、影响及确认依据；更新[正式需求入口](../../../stakeholder-requirements/README.md#requirements)。将全部本次业务验收交给 [specify-feature](../specify-feature/SKILL.md)规划分层验证，不以软件检查替代业务验收。未经确认的 REQ 仍为草稿，不能代用户批准。

## 产出与完成

领域事实落在 `domain-model/README.md` 的现有栏目或其已链接模型；产品信息落在 `stakeholder-requirements/README.md`；按需创建 `stakeholder-requirements/REQ-NNN-<slug>.md`。表单只作来源，不把正式内容留在 `_templates`。

术语、概念与关系、规则、职责与定向交换有依据，验收可逐项定位，未决项与影响明确，即可交付需求草稿；不表示业务验收已执行。维护任务交付其适用性说明即可。

## 停止条件

行为来源缺失、规则冲突或责任边界不明时停止受影响的细化，提出需确认的具体问题；可以保留已知部分和未决草稿，但不能推导默认政策、伪造确认或以期限压力补齐事实。
