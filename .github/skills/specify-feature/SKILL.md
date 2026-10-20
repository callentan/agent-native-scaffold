---
name: specify-feature
description: Use when a feature or maintenance task has a basis but its software acceptance, delivery slice, architecture constraints, sequence or verification plan is not yet precise.
---

# 细化行为与验证计划

实施前先确定要观察什么、由哪一层验收、怎样逐项判定。规格、必要设计与验证计划可以先完成，执行结果不能预填；各活动不是自动角色流水线。

## 输入

- 本次任务、范围、非目标、完成条件与读写授权；实际模型、REQ/UC/INV/CAP/QAS，或可定位的独立维护请求。
- 当前全部验收、相关 SR/US/ABB/ADR/VT、接口或序列及各自基线；只读取本任务适用且真实提供的资料。
- [开发说明](../../../docs/development.md)中的真实配置或未配置状态；采用 [BC 配置](../../../architecture/README.md#bc-configuration)时另核对身份、源根/路径、固定对象、只读性质与登记引用。配置不授予执行权。

## 先选择活动

先读原文并区分实际确认、候选与未知；来源不足时回 [define-requirements](../define-requirements/SKILL.md)，不把 Approved 标签、实现常量或 draft INV 当成强制事实。明确本次是分析、拟稿还是获准修订，检查所有拟写文件及已有内容，冲突停写。

按任务选择下面的小节；SR/VT 不必经过 US，ABB 与 VT 可在各自必要输入齐备后独立开展。小维护可沿用任务完成条件，不建完整工件链。采用元数据时按[现有契约](../../../domain-model/README.md#artifact-metadata)填写，来源关系/内容声明归 frontmatter，正文写含义、阅读导航与判据，旧轻量资料不自动迁移。

<a id="derive-requirements"></a>
## 派生软件要求

1. 从实际 REQ 验收、UC 路径、源规则/INV、CAP/上下文职责及适用 QAS 逐项确定软件要表达的行为。记录源位置、确认依据与固定基线；缺源或歧义阻塞相应要求确认，已知部分可保留草稿/问题。缺身份时先用获准笔记，不发明 canonical 引用。
2. 按[SR 指引](../../../software-requirements/README.md#sr-writing)填写 [SR](../../../_templates/items/software-requirement.md#basis)，新稿始终为 draft。`upstream` 声明可定位来源，正文说明细化理由；分别写正常/允许、边界、拒绝、错误与禁止副作用。缺接口、资格失效、并发或指标政策时列具体问题，不替业务作决定。
3. 每项软件验收用完整 owner ID 和稳定锚点；只写软件层可观察标准，规则仍回原文。核对既有 SR，避免重号、重复要求或无声覆盖；来源变更先走 [语义影响](../verify-change/SKILL.md#impact)，再规划下面的分层 VT。

<a id="delivery-slice"></a>
## 可选交付切片

需要组织交付时才使用 [US](../../../_templates/items/user-story.md)与[交付指引](../../../user-stories/README.md#delivery)。基于 SR 的正式切片先核实 SR 及适用 UC/INV 的确认依据；未确认来源只留下候选拆分与阻塞，不产出可实施承诺。按实际角色/价值、路径与约束说明范围、修改位置、依赖和清单，不造角色、不按固定技术层分故事，也不复制第二份 AC。

任务进度归 US 正文，内容声明归 frontmatter，执行归 VT。没有独立交付需要时跳过建 US，不影响可直接规划的 SR、设计或 VT；独立维护任务仍沿其原依据。

<a id="design-architecture"></a>
## 必要架构与决策

1. 读取实际 SR、CAP/上下文、接口、适用 QAS/ADR 和已有设计，显式读[架构规则](../../instructions/architecture.instructions.md)。有独立结构约束才写 [ABB](../../../_templates/items/architecture-building-block.md)；真实取舍才写 [ADR](../../../_templates/items/architecture-decision.md)，不要求先有 US。
2. 按[架构指引](../../../architecture/README.md#building-blocks)说明拥有/消费事实、职责、依赖和协作方向；选型、接口/依赖版本、运行/部署、观测与质量均须有源。未决定 ADR、draft QAS、未知版本或边界只支持候选与缺口，不预设四层目录或平台。
3. 将领域依赖与合法 composition root 装配分开；装配不成为控制器绕开领域规则的通行证。真实设计约束有独立 VC/锚点或引用原所有者，由 VT 规划适当判据。来件 ADR 交给 [incoming-adr](../define-requirements/SKILL.md#incoming-adr)，决定和通知不自动生效。

<a id="plan-verification"></a>
## 实施前验证计划

1. 按[全量验收盘点](../../../verification/README.md#coverage-check)先列所有范围内 REQ、UC/INV/QAS、SR、必要设计和维护完成条件的所有者、完整 ID、原文与基线，包括**没有 VT 的项**。缺源/身份先留精确缺口，不用已有 VT 倒推或缩小范围。
2. 按[验证层次](../../../verification/README.md#layers)分别规划业务、软件、适用设计或文档检查，使用 [VT](../../../_templates/items/verification-test.md#plan)。每条 `targets` 声明实际 `scope/id#anchor` 和本地 `criterionAnchor`；正文逐项保存独立判据、观察方式、前提/禁止副作用与未决项，不再抄目标关系表。反查源 owner、锚点与层次，不能一句“全部通过”覆盖多个目标。
3. 需要 Gherkin 时按[companion 指引](../../../verification/README.md#feature-companion)使用 [feature](../../../_templates/items/verification-test.feature)；它独占场景正文，VT 保存真实文件/基线导航和逐项判据。只用已知正常/负例和度量，安全标签须有具名来源。不存在步骤实现/runner 时只有文本计划，不称自动化完成。
4. 记录对象、要求/任务与 VT 计划基线，核实实际环境、方法、命令/cwd 与报告位置。缺项目、命令或报告时逐目标为 `not-run` 并说明缺项，不造测试标识。业务验收不是软件结果的汇总，文档检查也不能填进行为运行。
5. 在[验证索引](../../../verification/README.md#coverage-index)登记导航、核对基线与缺口，不另建结果表。实施与执行前按 [verify-change](../verify-change/SKILL.md#coverage)核对完整覆盖及语义影响；只有实际证据支持时才由原记录作结论。

<a id="sequence-diagram"></a>
## 时序说明

读取本场景的实际 UC、ABB、规则、参与者及事件/接口契约与版本，使用 [SEQ](../../../_templates/items/sequence-diagram.md)。逐路径说明提供/生产方 → 使用/消费方、消息含义与成功/拒绝/错误的已知预期；缺 ABB 参与者映射或契约时标局部说明和缺口，必要时暂不作图。

已有来源明确异步集成/事件消费才采用对应异步边界；只有上下文概念交换时不发明同步调用、broker、重试/超时/幂等/顺序或交付保证。Mermaid 只表达可回源部分，不是运行测试。已确认图的修订先核对授权、旧新基线和验证影响，不覆盖原证据。

<a id="build-architecture-spec"></a>
## 汇编架构规格

按 [SWAS](../../../_templates/items/architecture-specification.md)读取获准范围的业务/逻辑/运行/部署来源；若提供 model/实施摘要，核对源基线并回原文。未提供摘要不假造导出，不修改只读领域源。

保留[九个来源视图](../../../architecture/README.md#architecture-specifications)与原始基线：缺失/不可读/不可核实为 `unverified` 并列具体 gap，部分可读为 `partial`，完整来源才为 `available`。这些只表示来源完整性，不表示风险可接受、批准或发布。必需输入错误仍阻塞；缺 ABB、风险、部署或发布资料不能补基础设施/分类。只产 Markdown 汇编，本方法不提供 PDF/演示 renderer。

## 产出与完成

按需创建或修订 SR、VT/companion 和索引；US、ABB/ADR、SEQ/SWAS 沿各自指引落点，正式内容不留在表单里。现有代码维护使用 [implement-task](../implement-task/SKILL.md)，初始生成另用 [generate-code](../generate-code/SKILL.md)，需要各自开发输入及授权。

全部范围内验收已盘点、逐项目标与层次明确、实施前的验证计划和缺项可定位，才可交付本次规格/计划；不表示行为验证通过。没有应用时应用检查对文档任务不适用，已规划的业务/软件 VT 仍为 `not-run`。

## 停止条件

来源不能确定行为、验收目标无法定位、边界冲突或授权不明时，停止受影响的规格确认/实施，保留已知草稿与精确缺口。不能通过删除范围内验收、强建 US 或把其他层结果挪用过来结束任务。
