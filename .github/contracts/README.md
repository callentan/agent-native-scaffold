# 维护工具的数据契约 v1

本目录实现[增强规格 3.1–3.5](../../docs/design/ddd-functional-alignment.md)的 Task 2 输入契约。它们是本仓的功能等价设计，**不是原六仓字段、文件格式或自动导入的兼容声明**。字段含义和示例集中在本页；工具调用与错误码见[工具说明](../utilities/README.md)。

四份 schema 均为 JSON Schema Draft 2020-12，必填 `schemaVersion: 1`，拒绝未知字段。`$ref` 仅使用文件内部的 JSON Pointer；`$schema` URI 是方言标识，不要求联网下载。测试检查 schema 本身、全部本地引用及实际正反例。

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

以下都是**结构示例**，不是已确认工件、配置或执行记录。为展示固定对象格式，示例复用本任务已核对的输入 commit `81ffd45b3b9b7643d643a9162b533af92613c553`；这不证明示例 scope、来源、报告或验收项在该对象中存在。

## 1. Artifact frontmatter

[artifact.schema.json](artifact.schema.json) 只拥有机器元数据；Markdown 正文仍拥有业务含义和判据。

| 字段 | 必要性与含义 |
|---|---|
| `schemaVersion`, `id`, `kind`, `scope`, `contentState` | 均必填。`kind` 的唯一正式枚举在 schema 的 `$defs.kind`，恰好为规格列出的 32 项；没有自定义插件 kind |
| `upstream` | 可省略；完整来源引用的去重列表。只有真正省略时 parser 才返回空 tuple；`null`、对象、字符串或无效元素均报错 |
| `targets` | 可省略；去重的结构化记录列表。每条必填 `target`、`criterionAnchor`，可选非空 `testId`；有值时不得丢弃 owner、锚点或测试标识 |
| `confirmation` | `confirmed` 必须有；若提供则必填非空 `by`、`reference`、`baseline`。仅验证声明形状，不能认证人、权限或批准 |

目标记录形如 `{"target": "sample/CTX-001/SR-001#sr-001-ac-01", "criterionAnchor": "criterion-01", "testId": "native::test_reject"}`。`criterionAnchor` 必须是当前文档正文中真实的显式锚点，不在代码围栏、注释或链接文字里。完全相同的目标记录拒绝；同一目标由不同测试/判据引用可以保留。目标的跨文件存在性、层次和覆盖由后续 Task 7 检查。

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

现有资料不搬移、不改号、不覆盖正文。只有 scope 已确认后才显式补充 frontmatter；本任务没有批量转换任何旧文档或表单。没有 frontmatter 的普通资料仍可直接阅读，但显式交给此 parser 会得到 `MISSING_FRONTMATTER`，不会悄悄生成默认工件。

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
| `views` | 必须且只能有规格 3.2.1 的九个键，每项必填 `state`、`artifactRefs`、`evidenceRefs`、`gaps` |

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

数据测试分别保留 `sequenceSummary`、`governanceSummary`、`riskSummary`、`releaseStatus` 的源引用和基线，并逐个验证九个视图的 available/partial/unverified 形状、缺字段及错误状态。实际可选源查找、字段派生、范围/基线一致性和手改检测是 Task 7/8，不在本任务伪造导出器或运行结果。

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

没有全局“通过”字段；空 entries 或空证据不能建立通过。即使 pass 的数据结构有效，仍须回证据核对实际对象、逐项目标、执行数量与结果；schema 不认证报告真实性，不执行测试，不回写只读源。字段是 Task 2 的最小明确命名选择，后续改变需版本/契约变更，不静默兼容未知字段。
