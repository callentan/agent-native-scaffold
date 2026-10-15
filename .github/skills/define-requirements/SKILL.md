---
name: define-requirements
description: Use when business goals or rules are unclear, a domain model has gaps or drift, terms conflict across contexts, or a published interface, incoming ADR or Intended Use changes.
---

# 整理领域事实与业务需求

先把业务含义和来源说清，再写可观察的业务验收。只建当前任务需要的模型与需求，不用技术模式填补未知事实。

## 输入

- 用户提供的目标、使用者、范围、约束与来源；哪些已确认、哪些只是提案。
- 现有[产品说明](../../../stakeholder-requirements/README.md#product)、领域模型、REQ 和本次变更依据。
- 实际文件或已提供片段的定位、版本/日期、事实所有者与确认依据；本次希望得到的草稿或修订、允许读写的范围。缺原始定位或版本就记未知，不补造。
- ADR、Intended Use、治理/风险资料只在本次任务实际提供且适用时读取，不是所有项目的前置条件。来源提取而非澄清业务含义时，使用 [reverse-engineer-domain](../reverse-engineer-domain/SKILL.md)。

## 选择本次活动

新领域或事实不全用[访谈](#interview)；已有模型用[锤炼](#distill)；外部词汇、承诺或决策来件分别用[词汇对齐](#glossary-sync)、[发布接口](#published-interface)、[来件 ADR](#incoming-adr)或 [Intended Use 修订](#intended-use)。这些是同一方法的聚焦入口，不要求每次遍历全部活动。

先确认本次是分析、拟稿还是获准修订；未获写入授权时只返回发现、问题或草稿。确认业务含义与允许写文件是两回事，均不能从角色、期限、代码或文档状态推断。

<a id="interview"></a>
## 访谈与迭代确认

1. 对照输入整理目标、用户、范围内外事项和来源，填入产品说明的对应栏。只问会改变当前行为或范围的缺项，逐轮回述新增事实、候选解释、冲突和待确认问题，记录实际答复者、依据与被确认基线；未取得答复不模拟专家。区分阻塞当前决定的问题与可留待后续的问题。纯技术或文档维护可说明业务建模不适用，直接使用明确任务，不制造 REQ。
2. 在[共同术语](../../../domain-model/README.md#terms)说明业务含义与上下文；在[概念与关系](../../../domain-model/README.md#concepts)同时记录概念、状态含义及关系的方向、数量与成立条件。未知关系约束保持未决，不能只有名词清单。
3. 在[上下文职责](../../../domain-model/README.md#contexts)写清负责、不负责、拥有的事实及只消费的外部事实；在[定向信息交换](../../../domain-model/README.md#exchanges)明确提供方 → 使用方、事实所有者及已知业务约定。不强拆服务，不默认聚合、仓储或其他战术设计。
4. 按[规则栏](../../../domain-model/README.md#rules)分配稳定规则 ID 和锚点，写条件、边界、禁止行为及未知项；把事实来源、证据性质与局限、实际确认人与日期记入[来源栏](../../../domain-model/README.md#sources)。先有规则才可按 [INV 表单](../../../_templates/items/invariant.md#basis)说明推导；先澄清战略责任边界，再按需讨论[战术候选](../../../domain-model/README.md#tactical-forms)。推导、实现常量或高置信判断不等于业务确认。规则正文只维护一次；已有规则改变时先按 [verify-change 的影响检查](../verify-change/SKILL.md#impact)处理依赖。
5. 需要正式业务需求时按[REQ 指引](../../../stakeholder-requirements/README.md#req-writing)使用 [REQ 表单](../../../_templates/items/stakeholder-requirement.md#basis)，说明来源、业务需要与范围，链接实际概念、上下文及规则。验收使用“前提与场景→动作→可观察结果→边界/禁止结果”的表单字段，每项分配带所属工件的完整稳定 ID 与锚点，如 `REQ-NNN-AC-01`；不复制规则正文，也不只写 `AC-01`。按需使用 [UC](../../../_templates/items/use-case.md) 或 [QAS](../../../_templates/items/quality-attribute-scenario.md)，参与者、后置条件、并发政策、指标与测量方法未提供时保持问题，不凭经验补齐。
6. 在 REQ 的“变更与未决项”保留问题、影响及确认依据；更新[正式需求入口](../../../stakeholder-requirements/README.md#requirements)。将全部本次业务验收交给 [specify-feature](../specify-feature/SKILL.md)规划分层验证，不以软件检查替代业务验收。未经确认的 REQ 仍为草稿，不能代用户批准。

<a id="distill"></a>
## 知识锤炼与模型漂移

- 以给定模型版本、专家陈述及实际使用线索比较语言、概念关系、规则、边界与已采用的战术资料；先列存根和未决项。区分文字歧义、业务变化与实现偏离，不能仅凭类名或目录判断模型错误。
- 按 [领域工件审阅](../verify-change/SKILL.md#domain-review)返回有来源/位置、严重度理由、影响链和所需决定的发现。保留旧模型及冲突来源，提出候选解释、边界调整或 BL/ADR 建议；没有实际决定不重构架构、不全局改名，也不宣称模型健康或漂移已消除。

<a id="glossary-sync"></a>
## 词汇对齐

1. 对照实际提供的本地/外部词汇版本，逐词列上下文、原定义与定位、已确认或未决的依据，区分同义、同名异义、仅外部、仅本地和未确认词。版本缺失时只作临时比较，明确无法确认的差异；未确认词不作为统一定义。
2. 保留同名但不同上下文的含义，提出限定名称、映射、别名或弃用选项。沿规则、UC/REQ、接口和已知消费者列影响及需谁决定；不静默采用外部“标准词”，不全局替换。
3. 只有具体选择和写入范围均获确认后才修订原词汇所有者，保留旧称、来源版本、弃用依据及历史引用；外部源更新另需授权。冲突或版本待补时交付对齐提案，不把比较完成写成语言已统一。

<a id="published-interface"></a>
## Published Interface 演化

1. 明确本次是梳理承诺还是修订；读取提供的契约、模型/词汇、原版本、拟议差异和已知消费者。按 [PI 表单](../../../_templates/items/published-interface.md#direction)分清提供方 → 消费者、事实所有者与实际承诺，消费者需要不自动成为承诺。
2. 比较元素含义、适用条件、缺失值与失败处理，记录潜在破坏性及消费方影响。语义改变不能仅因字段名不变就称兼容；原契约、消费者或错误政策缺失时标待确认，停止兼容保证和发布决定，不默认失败策略。
3. 在[演化栏](../../../_templates/items/published-interface.md#evolution)提出版本、迁移/兼容窗口、撤销及通知方案。版本建议依据实际版本政策，已知破坏变化需提出相应升级；当前版本或政策未知时不编造版本号。通知草稿列对象、旧新基线、差异、影响和待确认事项，**拟稿不是发送**；实际通知、源修改与发布须分别获准并有原始记录。

<a id="incoming-adr"></a>
## 来件 ADR

读取实际提供的 ADR 原文、版本/决定基线、提出者或决定者及本次处理目的；只有摘要、标题或“Accepted”字样不能认证决定。沿 [语义影响检查](../verify-change/SKILL.md#impact)列受影响规则、上下文、REQ/QAS、设计、发布接口、消费者与验证，以及冲突和需确认的适用范围。

产出影响发现、BL 或获准的[本地 ADR 提案](../../../_templates/items/architecture-decision.md)，注明待更新位置、责任人和通知草稿；外部 ADR 保持原所有者与历史。缺来件正文/基线或授权时停止依赖它的采纳与修改，仍可返回已知问题。不自动改外部 wiki、通知消费者或将来件决定泛化到本项目。

<a id="intended-use"></a>
## Intended Use 修订（可选）

只处理用户提供的**现有文件**：当前完整内容与基线、目标章节、拟议内容/理由、事实所有者和允许修改的范围；缺必要原文时先索取，不创建替代事实或要求普通项目补医疗/QMS 资料。

比较目标、用户、使用环境、范围内外与约束；来源涉及患者、安全或监管时再核对相应变化。列受影响上下文、REQ/QAS、接口/消费者及验证，并引用实际提供的治理/风险依据。不确定的范围扩大或安全影响保留问题，按来源要求提交实际责任人及适用的风险/法规负责人复核；未给升级规则就请求其确定，不擅判风险可接受或代做风险分析。

产出章节级差异和影响/升级提案、需谁确认什么及被阻塞动作；没有责任人的适用范围和风险决定，不确认新用途、不改下游承诺。获准修订也须保留旧基线与尚未解决事项，不能由文档齐全推出合规或批准。

## 产出与完成

领域事实落在 `domain-model/README.md` 的现有栏目或其已链接模型；产品信息落在 `stakeholder-requirements/README.md`；按需创建 `stakeholder-requirements/REQ-NNN-<slug>.md`。独立领域工件、QAS 与 BL 按[现有落点](../../../domain-model/README.md#optional-forms)使用，ADR 按[架构指引](../../../architecture/README.md#decisions)落点；来件与 Intended Use 沿用提供文件的所有权和位置。表单只作来源，不把正式内容留在 `_templates`。

采用元数据时按[当前契约](../../../domain-model/README.md#artifact-metadata)保留身份、scope、内容状态和上游关系的单一归属；正文写依据、推导和问题，不再复制状态/关系表。scope 或 ID 缺失先留获准的普通笔记；旧轻量资料不强制迁移。确认、任务进度与执行结果分别记录。

术语、概念与关系、规则、职责与定向交换有依据，验收可逐项定位，未决项与影响明确，即可交付需求草稿；不表示业务验收已执行。维护任务交付其适用性说明即可。

## 停止条件

行为来源缺失、规则冲突或责任边界不明时停止受影响的细化，提出需确认的具体问题；可以保留已知部分和未决草稿，但不能推导默认政策、伪造确认或以期限压力补齐事实。
