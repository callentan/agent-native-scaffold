# 维护工具的数据契约 v1

本目录定义工件元数据、可选 BC 配置、派生模型和实施报告的输入契约。这些是本仓的功能等价设计，**不是原六仓字段、文件格式或自动导入的兼容声明**。本页和同目录 schema 完整说明字段与示例，无需读取内部制作规格；工具调用与错误码见[工具说明](../utilities/README.md)。

原四份 schema 的 v1 语义保持不变；可选来源清单有独立的第五份 schema。均为 JSON Schema Draft 2020-12，必填 `schemaVersion: 1`，拒绝未知字段。`$ref` 仅使用文件内部的 JSON Pointer；`$schema` URI 是方言标识，不要求联网下载，也不依赖制作仓的测试或历史记录。

## 共用表示

| 表示 | 约定 |
|---|---|
| `id` / `projectId` / 上下文 `id` | ASCII 字母或数字开头，后续可含字母、数字、点、下划线、连字符；不含路径分隔符或空白 |
| `scope` | 精确的 `project/context` 两段；不从目录名或当前应用猜测 |
| 工件 `key` | `scope/id`，例如 `sample/CTX-001/SR-001` |
| canonical 引用 | `scope/id#anchor`；目标、视图及报告的工件引用必须带锚点。`upstream` 也允许不带锚点的完整工件 key |
| 锚点 | ASCII 字母开头，后续可含字母、数字、点、下划线、冒号、连字符；不含 `#` 或空白 |
| `path` | 仓库相对路径，使用 `/`，允许中文和空格；不允许绝对路径、反斜杠、空段、`.` / `..` 中间段。单独的 `.` 可表示源根 |
| 文件 `reference` | 仓库相对文件路径及可选 `#anchor`，不是可执行命令或网络下载指令 |
| 固定对象 `baseline` | 完整的小写 Git 对象 ID（40 / 64 位），或 `sha256:` 加 64 位内容摘要；不接受 `HEAD`、分支名、缩写。Git 类型领域源必须用完整 Git 对象 ID |
| 证据/确认 `baseline` | 非空、含非空白字符的对象或报告基线指针；schema 不认证其真实性。与主输入的固定对象格式分别定义，不能拿可选证据缺失替代主输入错误 |
| 三种状态 | 内容声明是 `draft / confirmed / retired`；任务进度仍由任务所有者维护 `todo / in-progress / blocked / review-ready / done`；执行结果另记 `not-run / pass / fail / skipped`，互不转换 |

JSON Schema 的整数遵循 JSON 数值语义；布尔值、字符串不是整数。Markdown parser 进一步要求 YAML 解码结果的 `schemaVersion` 是真正的 Python `int` 且等于 1，拒绝 `true`、`"1"` 和 `1.0`，不作强制转换。

以下都是**结构示例**，不是已确认工件、配置或执行记录。示例 baseline 只展示固定对象格式；采用时须替换为本项目可读取的真实对象。这些示例不证明 scope、来源、报告或验收项存在。

## 1. Artifact frontmatter

[artifact.schema.json](artifact.schema.json) 只拥有机器元数据；Markdown 正文仍拥有业务含义和判据。

| 字段 | 必要性与含义 |
|---|---|
| `schemaVersion`, `id`, `kind`, `scope`, `contentState` | 均必填。`kind` 的唯一正式枚举在 schema 的 `$defs.kind`，是封闭的 32 项集合；没有自定义插件 kind |
| `upstream` | 可省略；完整来源引用的去重列表。只有真正省略时 parser 才返回空 tuple；`null`、对象、字符串或无效元素均报错 |
| `targets` | 可省略；去重的结构化记录列表。每条必填 `target`、`criterionAnchor`，可选非空 `testId`；有值时不得丢弃 owner、锚点或测试标识 |
| `confirmation` | `confirmed` 必须有；若提供则必填非空 `by`、`reference`、`baseline`。仅验证声明形状，不能认证人、权限或批准 |

目标记录形如 `{"target": "sample/CTX-001/SR-001#sr-001-ac-01", "criterionAnchor": "criterion-01", "testId": "native::test_reject"}`。`criterionAnchor` 必须是当前文档正文中真实的显式锚点，不在代码围栏、注释或链接文字里。完全相同的目标记录拒绝；同一目标由不同测试/判据引用可以保留。目标的跨文件存在性、层次和覆盖不在该 parser 的检查范围内。

````markdown
---
schemaVersion: 1
id: REQ-001
kind: stakeholder-requirement
scope: sample/CTX-001
contentState: draft
upstream: []
targets: []
---
# REQ-001：结构示例

<a id="req-001-ac-01"></a>
### REQ-001-AC-01：第一项

这是本工件的独立判据示例，不是一次通过记录。

<a id="req-001-ac-02"></a>
### REQ-001-AC-02：第二项

引用其他 ID 的正文不是额外验收项。
````

parser 识别现有仓库模式：独占一行的 `<a id="..."></a>`（单/双引号均可），紧接所属工件的 ATX 标题 `### REQ-001-AC-01：...`；中间允许空行。锚点须为完整标题 ID 的小写形式。支持 `AC` 和设计验证 `VC`；不把全文 ID、链接、其他 owner 的标题、注释、缩进代码或反引号/波浪号代码围栏变成验收库存。它不是通用 Markdown 渲染器，不推导隐式标题锚点。

上例返回的 `acceptance_ids` 为 `sample/CTX-001/REQ-001#req-001-ac-01` 和 `sample/CTX-001/REQ-001#req-001-ac-02`，不是 `AC-01`。每个 `Acceptance` 同时保留标题完整 ID、owner、锚点和标题/锚点的原文件行号。缺少对应锚点或锚点重复会报错。

现有资料不搬移、不改号、不覆盖正文。只有 scope 已确认后才显式补充 frontmatter；parser 不批量转换旧文档或表单。没有 frontmatter 的普通资料仍可直接阅读，但显式交给此 parser 会得到 `MISSING_FRONTMATTER`，不会悄悄生成默认工件。

## 2. 可选 BC 配置

[bc-config.schema.json](bc-config.schema.json) 是数据配置，不是 shell manifest。

| 字段 | 含义 |
|---|---|
| `schemaVersion`, `projectId` | 数据版本、项目身份 |
| `boundedContexts` | 非空列表，每条只有显式 `id`；scope 由项目和该 ID 组成，不再存一份可漂移的 scope |
| `domainSources` | 列表；每条必填 `id`、`kind: local / git`、`root`、`path`、`baseline`、`readOnly` |
| `developmentRegistration` | 指向既有开发登记的仓库相对路径和必需锚点；不复制命令、凭据或环境变量 |

`root` 保留显式源根：本地目录、已选 clone 根或 Git 仓库定位；`path` 单独保存其仓库内相对位置。`id` 是后续接入时稳定引用该源的短标识。schema 不连接 Git、不访问远端、不创建子模块，也不通过 `readOnly: false` 授予写入权限。实际路径、对象类型/可读性、来源 ID 冲突与登记是否匹配仍需后续来源接入检查。

```yaml
schemaVersion: 1
projectId: sample
boundedContexts:
  - id: CTX-001
domainSources:
  - id: owned-domain
    kind: local
    root: .
    path: domain-model
    baseline: 81ffd45b3b9b7643d643a9162b533af92613c553
    readOnly: true
developmentRegistration: docs/development.md#project-registration
```

## 3. 派生 model

[model.schema.json](model.schema.json) 只存引用，不复制业务正文、确认声明或实际结果。

| 字段 | 含义 |
|---|---|
| `schemaVersion`, `scope` | 版本和选定范围 |
| `source` | 必需主输入的 `root` 与固定对象 `baseline`；不能降为“可选源未验证” |
| `artifacts` | 每条必填 `key`、仓库相对 `path`、对象 `baseline`、`upstream`、`targets`；后两项使用与 frontmatter 相同的引用形状 |
| `implementationReports` | `reference + baseline` 证据指针列表 |
| `views` | 必须且只能有 `requirements`、`stories`、`architecture`、`sequences`、`verification`、`quality`、`governance`、`risk`、`release` 九个键；每项必填 `state`、`artifactRefs`、`evidenceRefs`、`gaps` |

`unverified` 必须是空引用和具体非空 gap；`partial` 必须有至少一条已知工件/证据引用以及具体 gap；`available` 无 gap 且保留至少一条来源引用（已知空源也用证据引用定位）。这些状态不表示业务验收、批准或发布。缺必需字段、非法引用或主对象基线格式是无效输入数据，不由 schema 转为九个空视图。

```yaml
schemaVersion: 1
scope: sample/CTX-001
source:
  root: .
  baseline: 81ffd45b3b9b7643d643a9162b533af92613c553
artifacts: []
implementationReports: []
views:
  requirements:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["srSummary source is absent"]
  stories:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["SR to US bridge is unavailable"]
  architecture:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["ABB and ADR sources are absent"]
  sequences:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["runtime sequence source is unavailable"]
  verification:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["verification evidence source is unavailable"]
  quality:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["QAS and utility-tree sources are absent"]
  governance:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["governance source is unavailable"]
  risk:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["risk source is unavailable"]
  release:
    state: unverified
    artifactRefs: []
    evidenceRefs: []
    gaps: ["release source is unavailable"]
```

本 schema 只校验视图数据的形状，不查找实际来源、不派生字段，也不核实范围/基线一致性或手改情况。调用者仍需核对真实来源和证据；schema-valid 不表示模型已经由导出器生成或经过运行验证。

## 4. 实施报告

[implementation-report.schema.json](implementation-report.schema.json) 把对象、来源、执行记录和适用性分开。

| 字段 | 含义 |
|---|---|
| `schemaVersion`, `scope`, `object` | 版本、范围；`object` 必填源根 `root` 和固定对象 `baseline` |
| `bcConfig`, `domainSources` | BC 配置的 `reference + baseline`；领域源逐条保存 `root + path + baseline` |
| `artifactRefs` | 完整的 SR/US/ABB/VT 等 canonical 引用；ID 前缀不是额外 kind 枚举 |
| `entries[].target` | 本条记录对应的完整验收引用 |
| `entries[].codeRefs` | 仓库相对 `path`、固定对象 `baseline`，可选 `symbol` |
| `entries[].testRefs` | 仓库相对 `path`、固定对象 `baseline`、非空 `testId`；不限制应用测试目录或语言 |
| `entries[].execution` | `status` 和 `evidenceRefs`；pass/fail 必须有非空证据引用，not-run/skipped 必须有具体 `reason` |
| `entries[].applicability` | 独立的 `state: unverified / applicable / not-applicable` 与具体 `reason`；不会从历史 pass 自动生成当前适用 |

```yaml
schemaVersion: 1
scope: sample/CTX-001
object:
  root: .
  baseline: 81ffd45b3b9b7643d643a9162b533af92613c553
bcConfig:
  reference: bc-config.yaml
  baseline: 81ffd45b3b9b7643d643a9162b533af92613c553
domainSources:
  - root: .
    path: domain-model
    baseline: 81ffd45b3b9b7643d643a9162b533af92613c553
artifactRefs:
  - sample/CTX-001/SR-001#sr-001-ac-01
  - sample/CTX-001/VT-001#criterion-01
entries:
  - target: sample/CTX-001/SR-001#sr-001-ac-01
    codeRefs: []
    testRefs: []
    execution:
      status: not-run
      evidenceRefs: []
      reason: Application environment is not configured
    applicability:
      state: unverified
      reason: No execution evidence is available
```

没有全局“通过”字段；空 entries 或空证据不能建立通过。即使 pass 的数据结构有效，仍须回证据核对实际对象、逐项目标、执行数量与结果；schema 不认证报告真实性，不执行测试，不回写只读源。改变本版本字段需要显式版本/契约变更，不静默兼容未知字段。

<a id="model-sources"></a>
## 5. 可选 model 来源清单

[model-sources.schema.json](model-sources.schema.json) 与[空白来源表单](../../_templates/config/model-sources.yaml)只登记来源选择。采用时放在所选资料根的 `model-sources.yaml`，不新增第二份 BC/模型/执行清单。原四类契约、32 个 kind 和九视图不变。

清单只有 `schemaVersion: 1` 与 `scopes`。后者是以明确 `project/context` 为键的 map；每个 scope 的值是九视图中所需视图的 map，每个视图对应非空的 `{path, baseline}` 列表。`scopes: {}` 是合法空表，不代表已登记真实项目；scope 值 `{}` 表示尚未选择任何视图源。重复 YAML key、同一视图重复路径或同一路径相互冲突的基线是配置错误，不作覆盖合并。

`path` 是 root 内的实际文件相对路径，允许中文和空格，拒绝网络/绝对路径、父级跳转、锚点、反斜杠、控制字符及首尾空白；解析后的 symlink/junction 也不能出界。`baseline` 是原始文件字节的 `sha256:` 摘要，或完整小写本地 Git commit/blob ID。commit 必须能在明确 checkout 根定位同一路径的普通 blob，blob 必须与当前所读字节完全一致；不能用分支、HEAD、短号、tag/tree、textconv 或联网替代。清单不是权限，不含 root/URL、命令、凭据、正文、结果、批准或写回开关。

结构示意如下；路径及 digest 均须由实际本地输入替换，不是已存在资料：

```yaml
schemaVersion: 1
scopes:
  sample/CTX-001:
    requirements:
      - path: software-requirements/SR-001.md
        baseline: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  sample/CTX-002:
    sequences:
      - path: sources/sequences.yaml
        baseline: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

主 root、scope、schema、正式库存或主基线错误始终失败；供应了非法清单也失败，不能降为“缺可选来源”。合法清单中的可选文件缺失、不可读、格式错误或基线不可核实，只使所选视图 `unverified`，空 refs 并列具体来源 gap。合法但不完整来源为 `partial`；来源完整为 `available`。这些仅描述来源，不解释为通过或批准。

未提供清单、清单没有选定 scope、scope 没有某个 view 分别给出明确 gap。只要主库存中有该 scope，缺清单登记不阻塞主工件索引；不存在的主 scope 仍是输入错误，不能通过清单虚构。来源可以是已有正式 Markdown 工件或下节约定的已有 YAML/JSON 摘要，不要求为了导出复制一份模型正文。持久化派生 model 不能再作为来源。

### 5.1 已有来源的两种读取形状

优先选择原工件，不要为工具新抄一份业务模型。正式 Markdown 复用 artifact parser 和原显式锚点：来源版本用原始字节基线，内容声明留在元数据，含义与结果留在正文。视图保留实际 owner 的锚点、相关 `upstream` / `targets` 导航和文件基线。选中的工件及依赖没有该视图所需类别/章节时为 `partial`，不根据文件名补字段。

| view | Markdown 所需来源及章节（只核对结构，不认证内容） |
|---|---|
| requirements | REQ、SR、UC；REQ/SR 的 owner AC，UC 的明确正文锚点 |
| stories | US 的 `task`、`checklist` 和 SR 来源 |
| architecture | ABB 的 `structure`、`interfaces`、`runtime` 与 ADR 的 `decision` |
| sequences | SEQ 的 `basis`、`participants`、`paths`、`diagram`，UC 与 ABB 来源；时序、伙伴/异步含义回源阅读 |
| verification | VT 的 `plan`、`targets`、`runs` 及其实际所属子运行块，与 REQ/SR；计划结构不证明已有实际运行 |
| quality | QAS 的 `scenario`、`measurement`、实际 utility-tree 来源，以及 REQ、实际 TS/VT 目标；缺 QAS 或树源为 unverified，不复制树或场景正文 |
| governance | review-record 的 `decision`；批准/waiver 含义仍归原记录 |
| risk | risk-control 的 `analysis`、`control`、`residual` 与 REQ/VT 来源；不计算风险等级 |
| release | development-log 的 `release`、`change-control`；生命周期/分类/版本仍归原发布记录 |

仅有章节或一段泛化正文不足以定位原汇总字段。直接 Markdown 还核对以下**原所有者中的表格值**（二列表格），没有就保留字段级 `partial` gap，不根据代码箭头、元数据状态、文件名或常用值推断。版本由实际对象 baseline 定位，ID/关系仍从 parser 取得；这些不是新的 frontmatter 字段，也不要求为导出复制一个模型。

| 来源位置 | 需要可定位的值（`/` 分隔可接受的原文标签） |
|---|---|
| US `task` | `任务进度/status`，不拿 contentState 代替任务进度 |
| ABB `runtime` | `language/实现语言`、`framework/框架`；未选定则缺项，不选默认栈 |
| SEQ `paths` | `hasAsync/异步交互` 的明确 `true/false` 声明，不从 Mermaid 箭头推断 |
| SEQ `participants` | 已有 integration-partner upstream；没有时需 `externalPartners/外部伙伴` 的明确来源说明，包括已知无伙伴 |
| VT `runs` 下的本 owner `vt-…-run-NN` 子块 | 日期、notes、三个运行基线及明确 auto/manual 数量在各自子块读取；实际结果来自该块的逐判据多列表，不要求在 `runs` 标题前再抄一份 |
| QAS `scenario` | 现有六要素表全部六个值；也接受 `stimulusSource/stimulus/environment/object/response/responseMeasure` 原字段标签 |
| review-record `decision` | `status/审阅结论`、`notes/限制与说明`；读取声明不认证批准 |
| risk-control `analysis` / `residual` | `preMitigationLevel/控制前风险`、`residualRiskLevel/残余风险`；不计算或接受风险 |
| development-log `release` | `lifecycle/safetyClass/currentVersion/lastReleaseDate/nextPlannedRelease` 五个原字段值；变更控制仍通过其独立原文节定位 |

同一字段的重复/缺值、明确未知、缺原文节或必要关联均为具体 gap。计数为非负十进制，布尔只接受 `true/false`，已知的零和 false 不视为缺值。只有表头/分隔行不是内容；SEQ 图必须是其 `diagram` 节内真正闭合的 Mermaid 代码围栏，具有序列头和消息。HTML 注释、外层 literal fence 中的示例、未闭合围栏或普通说明不能补位；正文和图复用同一注释/围栏状态机，不再回扫原始文本猜图。非支持形状的已有文档保留具体缺口，不自动迁移。

直接 quality 可在同一清单视图中并列选择原 QAS Markdown 与已有 utility-tree YAML/JSON。树文件的顶层 `tree` 为 mapping/list，数据仍归该文件，导出只保留 `文件#tree + baseline`，不增加 kind 或抄树节点。空 `tree` 是已知来源的条目缺口（partial）；没有 QAS、没有树源、树不可读/格式错误/基线不可核实为 unverified、空 refs 和具体缺源原因。QAS 和树都可核实后，缺响应度量或部分场景才是 partial。也可直接引用已有 `quality.utilityTree` 证据指针；不要求为工具新造一份模型。

直接 VT 从真实 `runs` 二级章节内查找本 owner 的 `vt-…-run-NN` 锚点，各子块仍以严格锚点边界隔离。读取原表单的“日期、执行者与方式”“报告可访问性与限制”、实际对象/当时要求/VT 三个基线，以及“判据链接（目标由 frontmatter 定位）／实际观察及原始报告定位／实际结果／未执行或跳过原因”四列。每个已声明 criterion 都需自己的结果行；重复、缺行、无效状态或未知 criterion 有源位置 gap。结果不抄进 model。

auto/manual 数量只能来自该运行块中明确的 `automatedCount/自动检查数量`、`manualCount/人工检查数量` 行，或原“退出码、发现/执行/跳过数量（适用时）”值中明确注明的这两项（例如“自动检查数量 0；人工检查数量 2”）。不能从总发现/执行数、结果行数或文件名推算。多个运行分别保留源锚点/基线；互补缺字段不能拼成完整运行，同对象/要求/VT 基线却结果冲突时保留两侧引用并标 partial 的冲突 gap。不同基线的完整历史记录可分别定位，不选最新、不合并成全局结果。

已有 YAML/JSON 汇总可直接选为来源。文件顶层包含下表对应的对象；允许同一文件有多个已知汇总，但**不是本工具派生的 model**。字段值仍由源维护，导出仅保存 `文件#汇总键 + baseline` 及下面的实际引用；不把 status/result/度量/安全分类抄进 model。JSON 使用同一个安全 YAML 数据读取器读取其兼容子集，拒绝重键、危险 tag 与循环别名。

下表 `ref` 是已存在 owner/显式 anchor 的 canonical 引用，不是短 ID。`evidence` 是实际本地文件的 `{reference, baseline}`，baseline 同样必须能按原始字节或精确本地 Git 对象核实；Markdown fragment 为真实锚点，YAML/JSON fragment 为真实顶层键，其他文件只允许无 fragment 引用。数组的实际关系不会用 suffix/title 补齐。每个对象可另给 `evidenceRefs: [evidence]` 定位它已有的原始记录；这不是执行授权。

| view / 顶层键 | 必要的源字段（源数据，不是 manifest 字段） |
|---|---|
| requirements / `srSummary` | `srVersion: text`, `entries: [{reqId: ref, srIds: [ref], ucId: ref, status: text, notes: text}]` |
| stories / `storySummary` | `storyVersion: text`, `entries: [{srId: ref, usIds: [ref], status: text}]` |
| architecture / `abbSummary` | `abbVersion/language/framework: text`, `blocks: [{abbId: ref, adrRef: ref}]`, `integrations: [ref]` |
| sequences / `sequenceSummary` | `seqVersion: text`, `entries: [{seqId: ref, ucId: ref, title: text, hasAsync: boolean, externalPartners: [ref], status: text}]`；ABB/伙伴也沿 SEQ 原 `upstream` 定位 |
| verification / `verificationSummary` | `vtVersion/lastRunDate: text`, `entries: [{usId: ref, vtIds: [ref], result: text, automatedCount: nonnegative integer, manualCount: nonnegative integer, notes: text}]` |
| quality / `quality` | `qasRefs: [ref]`, `utilityTree: evidence`, `testScenarios: [ref 或 evidence]`；不新造 `qasSummary`，没有 feature 工件身份时用文件证据，不发明 canonical ID |
| governance / `governanceSummary` | `govVersion: text`, `entries: [{govId: ref, status: text, ref: evidence, notes: text}]`；已有 `reqIds/waiverRefs: [ref]` 也保留 |
| risk / `riskSummary` | `riskVersion: text`, `entries: [{riskId: ref, title: text, preMitigationLevel: text, rcIds: [ref], residualRiskLevel: text, reqIds: [ref], vtCoverage: [ref], status: text}]` |
| release / `releaseStatus` | `lifecycle/safetyClass/currentVersion/lastReleaseDate/nextPlannedRelease: text`, `changeControlRef: evidence`；已有 `releaseRef: ref`、`bcRefs: [ref]` 也保留 |

缺少整个汇总对象或字段类型错误是可选源格式错误：`unverified`、空 refs。来源已提供但缺具体字段、null/空文本或缺必要关联条目时为 `partial`，gap 带源文件及完整字段路径，例如 `sequenceSummary.entries[0].externalPartners`；已知 ref 和来源指针继续保留。quality 的 QAS/utility-tree 是必需的来源组成，缺任一来源优先按 unverified 处理，不能降为普通字段 partial。显式空 `entries/blocks` 表示可核对的空汇总；`srIds/usIds/vtIds/testScenarios` 空列表报告缺关联，`externalPartners/integrations/rcIds/reqIds/vtCoverage` 显式空列表不推导不存在的对象。`false`、计数 `0` 是有效源值，但字符串布尔与布尔计数不是有效类型。引用的 owner/anchor、文件或基线无法核实时为 `unverified`，不保留无法确认的引用。

同一视图有多个来源时，任一来源无法核实使该视图 `unverified` 并清空 refs；全部可核实但有结构缺项则为 `partial`。其他视图不受牵连。每个状态都只说明所选来源的结构/可定位性；完整文本、数值/异步含义、批准真实性和结果适用性仍须回到原所有者判断。
