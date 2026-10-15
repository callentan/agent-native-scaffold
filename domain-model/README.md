# 领域模型

本目录记录业务含义与边界，不是代码分层图。下面是填写指引和空栏，尚无已确认业务模型。涉及业务的任务填入已知事实或引用现有模型；不涉及业务的维护任务说明不适用原因，不为填满目录编造内容。

<a id="terms"></a>
## 共同术语

同一个词在不同上下文中的含义可能不同。写清业务定义、容易混淆的含义及来源，不用技术类名代替定义。

| 术语 | 所属上下文 | 业务含义 | 别名或易混淆含义 | 来源与确认状态 |
|---|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 | 待确认，来源待填写 |

<a id="concepts"></a>
## 概念与关系

既要写概念，也要写它们如何关联。关系中的方向、数量约束、成立条件或状态含义不明确时，保留问题，不补默认规则。

| 概念标识与名称 | 所属上下文 | 业务含义、相关行为或状态 | 来源与确认状态 |
|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待确认 |

| 关系标识 | 起点概念 → 终点概念 | 关系含义、方向与数量约束 | 成立条件或限制 | 来源与未决项 |
|---|---|---|---|---|
| 待填写 | 待填写 → 待填写 | 待填写 | 待填写 | 待填写 |

<a id="rules"></a>
## 业务规则

每条真实规则分配稳定的 `RULE-NNN` 标识与 ASCII 锚点。下面的 `rule-nnn` 仅演示占位结构；填写时同时替换 ID 和锚点。文字调整不随意改号，撤销时保留依据，不把旧号分配给另一条规则。

<a id="rule-nnn"></a>
### RULE-NNN：待填写（占位规则）

| 字段 | 内容 |
|---|---|
| 状态 | 待确认，尚不是业务事实 |
| 适用上下文与范围 | 待填写 |
| 条件、必须成立的约束与禁止的行为 | 待填写 |
| 边界、例外及未定义的处理 | 待填写；未知不补默认值 |
| 事实来源、确认人及日期 | 待填写 |
| 变更依据与原基线 | 待填写 |

REQ、SR 和设计引用规则所在文件与锚点，不为方便在多处维护相同规则正文。

<a id="contexts"></a>
## 上下文职责与事实归属

上下文按业务责任划分，不强制对应服务、仓库、子项目或代码层。一个上下文足够时不人为拆分；实体、值对象、聚合、仓储等技术模式并非必选。

<a id="ctx-nnn"></a>
### CTX-NNN：待填写（占位上下文）

| 字段 | 内容 |
|---|---|
| 负责的业务能力与决定 | 待填写 |
| 明确不负责的事项 | 待填写 |
| 拥有并维护的业务事实 | 待填写 |
| 只使用、不拥有的外部事实及其所有者 | 待填写 |
| 相关概念、规则链接 | 待填写 |
| 来源、确认状态与未决边界 | 待填写 |

<a id="exchanges"></a>
## 定向信息交换

分别写清提供方与使用方、信息的事实所有者及依赖约定。不要仅写“两个上下文交互”，也不提前决定消息中间件或接口实现。

| 提供方 → 使用方 | 提供的信息或能力 | 事实所有者 | 触发、时效及失败时的业务约定 | 来源、状态与未决项 |
|---|---|---|---|---|
| 待填写 → 待填写 | 待填写 | 待填写 | 待确认 | 待填写 |

<a id="sources"></a>
## 来源、事实与未决项

给事实保留可定位的来源、日期和确认依据。把用户确认的事实、分析提案和未决问题分开；推导合理不等于已经确认。来源不可读时记录限制，不以猜测补齐。

| 事实或问题标识 | 内容及所属概念、规则或上下文 | 状态（已确认／提案／未决） | 来源定位、日期与确认依据 | 需谁确认什么 |
|---|---|---|---|---|
| 待填写 | 待填写 | 未决 | 待填写 | 待填写 |

业务目标和需求回到[业务需求入口](../stakeholder-requirements/README.md)，软件行为回到[软件要求入口](../software-requirements/README.md)。规则或边界变化时按[语义影响检查](../verification/README.md#change-impact)处理依赖、旧结果和待复核项，即使引用方没有复制规则中的具体数值，也可能受影响。

<a id="optional-forms"></a>
## 按需使用独立领域工件

**上面的轻量路径继续有效。** 一个上下文或一次小维护可以仍在本 README 记录术语、关系、规则、职责、交换和来源，不必创建下列全部工件，不必先安装工具。已有 ID、锚点、规则正文和所有者内容不得因采用表单而被改号、替换或搬移。

当资料需要独立引用或范围已超过一页时再复制表单。默认落点见下表；已有项目位置保持不变。确需多子域/上下文时，也可在 `domain-model\subdomains\<slug>\contexts\<slug>\` 下组织所属领域资料。嵌套目录只是可选组织方式，不是服务、仓库、项目或代码层的强制划分；REQ、QAS、SR、场景/VT 仍各回所属目录。

<a id="strategic-forms"></a>
### 业务边界、能力与行为

| 按需记录的内容 | 表单 | 默认正式落点 |
|---|---|---|
| 子域目标、边界、业务责任与外部关系 | [SD](../_templates/items/subdomain.md) | `domain-model\SD-NNN-<slug>.md` |
| 上下文职责、拥有/消费事实与方向 | [CTX](../_templates/items/bounded-context.md) | `domain-model\CTX-NNN-<slug>.md` |
| 业务能力、所有者及用例导航 | [CAP](../_templates/items/capability.md) | `domain-model\CAP-NNN-<slug>.md` |
| 参与者、正常/替代/拒绝路径及可观察后置条件 | [UC](../_templates/items/use-case.md) | `domain-model\UC-NNN-<slug>.md` |
| 源自业务 RULE 的约束、适用状态与判据 | [INV](../_templates/items/invariant.md) | `domain-model\INV-NNN-<slug>.md` |
| 具体问题、冲突、影响与决定证据 | [BL](../_templates/items/backlog-item.md) | `domain-model\BL-NNN-<slug>.md` |
| 质量刺激、环境、响应与有来源的度量 | [QAS](../_templates/items/quality-attribute-scenario.md) | `stakeholder-requirements\QAS-NNN-<slug>.md` |
| UC/REQ/INV/QAS 的独立场景判据与执行入口 | [TS](../_templates/items/validation-scenario.md) | `verification\TS-NNN-<slug>.md` |

RULE 仍由原领域文件的稳定锚点拥有，不增加第二份规则正文。INV 先引用 RULE 再说明约束，不从代码或聚合候选反推规则。CAP 的用例列表只作导航，UC 自己声明上游能力。BL 的处理进度与问题决定证据分开，过了答复期限不代表问题已解决。QAS 缺指标时保留明确缺口，不补默认 SLA；具体见[质量输入](../stakeholder-requirements/README.md#quality-inputs)和[场景指引](../verification/README.md#domain-scenarios)。

<a id="integration-forms"></a>
### 上下文集成资料

| 按需记录的内容 | 表单 | 默认正式落点 |
|---|---|---|
| 每个方向的事实所有者、关系类型、翻译与依赖 | [Context map](../_templates/items/context-map.md) | `domain-model\CM-NNN-<slug>.md` |
| 实际承诺元素、消费者、语义版本与变更/通知提案 | [Published Interface](../_templates/items/published-interface.md) | `domain-model\PI-NNN-<slug>.md` |
| 伙伴职责、生产/消费方向、契约与失败边界 | [Integration partner](../_templates/items/integration-partner.md) | `domain-model\IP-NNN-<slug>.md` |

关系模式按已知需要选择；ACL、开放主机服务、共享内核等不是默认架构。消费者需要的信息不自动成为提供方承诺。版本、失败政策或翻译责任未知时保持问题；破坏变更需记录理由、受影响消费者及版本/通知提案，未经授权不修改外部源或实际发送通知。

<a id="tactical-forms"></a>
### 可选战术资料

只有明确任务确实需要时才使用。没有边界、规则或身份依据时保留候选和问题，不因为表单存在就决定实现模式。

| 角色区别 | 表单 | 默认正式落点 |
|---|---|---|
| 需要共同保持约束的候选边界、根与生命周期 | [Aggregate](../_templates/items/aggregate.md) | `domain-model\AGG-NNN-<slug>.md` |
| 以持续业务身份辨认、随生命周期变化的概念 | [Entity](../_templates/items/entity.md) | `domain-model\ENT-NNN-<slug>.md` |
| 以值辨认的含义、相等条件、单位与合法性 | [Value object](../_templates/items/value-object.md) | `domain-model\VO-NNN-<slug>.md` |
| 对象创建、初始状态与有效性责任 | [Factory](../_templates/items/factory.md) | `domain-model\FAC-NNN-<slug>.md` |
| 不宜归入单个实体/值对象的领域操作 | [Domain service](../_templates/items/domain-service.md) | `domain-model\DS-NNN-<slug>.md` |
| 有来源的业务决策、条件与冲突/失效边界 | [Policy](../_templates/items/policy.md) | `domain-model\POL-NNN-<slug>.md` |
| 已发生事实的含义、生产/消费与语义演化 | [Domain event](../_templates/items/domain-event.md) | `domain-model\EVT-NNN-<slug>.md` |

这些记录不预设端点、数据库、消息中间件、事务或性能/交付保证，也不提供监管分类。规则、生命周期、协作者和版本期望按来源填写；没有来源就说明谁需要补充什么。填写完成不表示实现或行为已验证。

<a id="governance-forms"></a>
### 可选用途与外部风险引用

| 按需记录的内容 | 表单 | 默认正式落点 |
|---|---|---|
| 目的、使用者、环境、用途边界及候选变更 | [Intended Use](../_templates/items/intended-use.md) | `domain-model\IU-NNN-<slug>.md` |
| 外部分析/控制/残余风险与决定的实际引用 | [Risk control](../_templates/items/risk-control.md) | `domain-model\RC-NNN-<slug>.md` |

已有位置与外部事实所有权不变；[治理指引](../docs/governance.md#intended-use)说明适用性和责任缺口。初次来源整理与已有用途修订分开，修订仍按[现有方法](../.github/skills/define-requirements/SKILL.md#intended-use)读取完整原文/基线。不默认医疗/QMS，不替外部风险所有者计算、接受风险或确认用途；未知只阻塞受影响的决定。

需要独立审阅或工具使用依据时，记录落在[验证目录](../verification/README.md#optional-reviews)，不写成另一份领域规则或 VT 结果。模型来源沿[已有字段](../docs/governance.md#source-views)读取；不得为了完整导出补风险数值或制造关系。

<a id="artifact-metadata"></a>
## 可选结构化身份与关系

[数据契约](../.github/contracts/README.md)及其 [artifact schema](../.github/contracts/artifact.schema.json)是字段、封闭 kind 集合与语法的唯一定义。新表单已带 `schemaVersion: 1`、实际 `kind` 和 `contentState: draft`；`PROJECT/CTX-NNN`、`NNN` 均是等待项目输入的占位，不是确认过的身份。**空表即使能解析，也不构成已验证的正式工件。**

复制或给旧资料补元数据时：

1. 先核对实际来源、授权、已有文件和稳定 ID。只有 project/context 归属已明确才填写 `scope`；子域或跨上下文地图也由责任人选定其实际归属，不从目录猜测或新造一个“全局”上下文。
2. 替换文件名、frontmatter、标题、验收 ID 和锚点中的占位；保留旧正式 ID 和锚点。身份为 `scope/id`，不同 scope 可有同号，同 scope 不得重号。
3. `upstream` 声明实际可解析来源，`targets` 声明具体目标及本文件的 `criterionAnchor`。这些关系与内容状态只在 frontmatter 维护；正文保存业务含义、来源解释和独立判据。正文链接可导航这些引用，不维护第二份状态或关系表。
4. 规则没有单独 kind：若规则所有者已有元数据，可引用 `scope/所有者ID#rule-...`；仍用轻量 README 的来源可以继续普通相对链接。不要为得到 canonical key 而自动给所有旧文件加元数据。
5. 验收采用完整 owner ID，例如占位 `UC-NNN-AC-01`，紧前放独占一行的 `<a id="uc-nnn-ac-01"></a>`。目标使用 `scope/id#anchor`，不能只写 `AC-01`；保留原验收编号，撤销不复用。
6. 将提示删除或转成明确问题，修正实际落点的所有相对 URL；文件路径示例用反斜杠。来源事实、推导候选和未决问题分开；`confirmed` 需要实际确认来源和被确认基线，模板不提供批准。

不使用元数据的旧资料仍可照常阅读和维护；显式送给[当前 parser](../.github/utilities/README.md)才要求合法 frontmatter。parser 校验本文件元数据/判据锚点和显式集合内的重号，不核实跨文件覆盖、全部业务语义或批准身份，也不会自动迁移文件。结构检查、文档使用与实际业务执行须分别记录。

<a id="derived-model"></a>
## 可选派生引用视图

需要机器索引时使用[模型工具](../.github/utilities/README.md#model-export)，显式给出真实 root 与 scope；不从目录猜上下文。可选[来源清单](../.github/contracts/README.md#model-sources)只选择已有工件/摘要及固定基线，不复制规则、模型正文或结果，也不授予外部读写权限。

九视图的 `available/partial/unverified` 表示来源完整性。缺清单或可选源保留具体 gap；主库存非法则失败，不能把它降为可选缺项。默认只读，显式导出只创建新文件；旧模型可重算检查来源变化或手改，不自动覆盖。规则影响仍按[影响方法](../.github/skills/verify-change/SKILL.md#impact)核对，机械依赖候选不能替代语义和责任人决定。

实现侧的[实施报告](../.github/contracts/README.md#implementation-report)复用既有 VT 运行及其对象/要求/计划基线，领域源只读核对。需要连接 model 时另行在现有 verification 来源中选择该报告；`implementationReports` 只存文件引用与已核实基线，不搬入逐项结果，也不改写领域 model 或来源清单。未选择报告或缺源保持原有空引用/gap，不能因一次收集成功推导当前适用或批准。
