# 架构与决策

本目录记录必要的结构、约束及取舍。当前尚无已确认项目架构，不从目录名推导服务或代码分层；[业务上下文](../domain-model/README.md#contexts)不必与技术组件一一对应。

实际设计活动从 [specify-feature](../.github/skills/specify-feature/SKILL.md#design-architecture)进入，完整读取方法并显式读取[架构规则](../.github/instructions/architecture.instructions.md)。下列表单只提供可选结构，不意味着存在应用、架构决定或批准。

<a id="building-blocks"></a>
## 架构构件 ABB（按需）

当结构、职责、接口协作或设计约束需要单独说明时，使用 [ABB 表单](../_templates/items/architecture-building-block.md)，放入 `architecture\ABB-NNN-<slug>.md`。

- 读取实际 REQ/SR、CAP/上下文、规则、适用 QAS/ADR 或独立任务；按[元数据约定](../domain-model/README.md#artifact-metadata)把真实身份、draft 和 `upstream` 留在 frontmatter。正文只解释来源与提供阅读导航，不另存关系/内容状态。旧资料不自动迁移。
- 区分负责与不负责的事项、事实所有者、依赖与交互方向；设计假设和未决项不能写成业务事实。
- 按实际需要说明接口契约、依赖版本、运行/部署约束、质量响应与观测方式。draft QAS、未决定 ADR 或未固定依赖版本保留缺口并阻塞相关承诺/选型，不默认四层、语言、云平台或容器。
- 说明有来源的设计约束、备选方案与取舍，以及需要怎样验证。区分允许的 composition root 装配和领域/业务控制逻辑依赖；装配例外不授权所有控制器直达数据库或绕开规则。
- 需要独立核对的设计约束使用带所属工件的稳定标识和锚点，例如 `ABB-NNN-VC-01`、`abb-nnn-vc-01`。已有约束直接引用，避免再写一份。

设计验证按[验证层次](../verification/README.md#layers)选择合适的检查，不自动等同于 REQ 业务验收或 SR 软件行为验证。不为每次修改强制新建 ABB；US 不是它的强制前提，ABB 和 VT 可在各自输入齐备后独立规划。

<a id="decisions"></a>
## 架构决策 ADR（按需）

只有真实决策需要保留背景、备选方案和历史时，才使用 [ADR 表单](../_templates/items/architecture-decision.md)。在创建第一份 `architecture\decisions\ADR-NNN-<slug>.md` 时再建立 `decisions\`，不预置空目录或虚假决策。

提案、实际决定和被取代的历史要区分；新 ADR 初始为 `draft`，只有真实决定可定位时才填写 frontmatter 的确认声明。正文保存业务边界、选项、理由、代价、后果与验证需要，不再维护一份批准表。没有获授权者的决定时不能写“已接受”。

来件 ADR 使用实际原文与版本，列上下文、消费者、接口和验证影响，通知仅为草稿；活动见 [define-requirements](../.github/skills/define-requirements/SKILL.md#incoming-adr)。后续决定追加记录并链接前后关系，不重写旧历史或自动发布到外部系统。

<a id="sequences"></a>
## 时序说明 SEQ（按需）

使用 [SEQ 表单](../_templates/items/sequence-diagram.md)，落在 `architecture\SEQ-NNN-<slug>.md`；方法入口为 [sequence-diagram](../.github/skills/specify-feature/SKILL.md#sequence-diagram)。依据实际 UC、ABB、规则与事件/接口契约，注明前提、参与者职责、信息方向、成功/拒绝/错误路径及其来源基线。

跨上下文概念交换不能自动解释成服务或 transport。已有集成/事件消费者明确要求异步时保留相应边界；缺契约时不补同步调用、broker、超时/重试/顺序/幂等或交付保证。只有概念角色而无 ABB 映射时标明局部说明与缺口，不称完整运行序列。Mermaid 源和渲染结果都不是执行证据。

<a id="architecture-specifications"></a>
## 架构规格 SWAS（按需）

使用 [SWAS 表单](../_templates/items/architecture-specification.md)，落在 `architecture\SWAS-NNN-<slug>.md`；按 [build-architecture-spec](../.github/skills/specify-feature/SKILL.md#build-architecture-spec)汇编实际来源。分别说明业务、逻辑、运行与部署，并按[现有 model 契约](../.github/contracts/README.md)的九个视图核对来源完整性。

- `requirements/stories/architecture/sequences/verification/quality/governance/risk/release` 只导航真实原文/证据与基线，不成为第二份领域事实、关系或结果库。
- 缺可选来源保留 `unverified` 与具体 gap；部分可读则 `partial` 并保留可核对导航；所需来源完整才为 `available`，均不表示通过/批准。不适用需要范围依据。必需主输入错误仍阻塞，不能用九个空视图掩盖。
- model 存在时先用[只读检查](../.github/utilities/README.md#model-export)核对其来源基线并回原文。可选[来源清单](../.github/contracts/README.md#model-sources)能登记多个明确 scope 的真实文件/基线，未登记或缺可选源各有 gap；不制造 ABB、部署、风险分类或审批。模型是引用索引，SWAS 正文仍归 Markdown 汇编；可选[本地导出](../docs/document-exports.md)生成有源的 HTML/SVG 架构/SEQ 与参数化演示，PDF/PPTX 仍不可用，不以其他格式冒充。

governance/risk 来源可按需使用[审阅记录](../_templates/items/review-record.md)与[风险控制引用](../_templates/items/risk-control.md)，字段归属见[治理指引](../docs/governance.md#source-views)。用途、风险或 waiver 的原决定仍回其所有者；ADR/SWAS 不接管外部权威，不把来源 available 或工具资格记录当架构/法规批准。

<a id="bc-configuration"></a>
## 可选 BC 数据配置

需要显式登记多上下文或领域源时，从[配置表单](../_templates/config/bc-config.yaml)复制到获准项目根的 `bc-config.yaml`。按[BC schema](../.github/contracts/bc-config.schema.json)及[契约说明](../.github/contracts/README.md)填写项目身份、上下文和每个来源的 `id/kind/root/path/baseline/readOnly`，不增加自定义命令字段。

`root` 是明确源根，`path` 是该根内的相对路径；固定基线须来自实际对象/摘要，Git 源不能用 HEAD、分支或缩写。空表中的占位不是 Git 事实，也未通过有效配置验收。`developmentRegistration` 只引用[实际开发登记](../docs/development.md#project-registration)，不复制命令、秘密或应用配置；指针可读不表示开发输入齐全。

schema 只校验结构，不访问/下载来源或核实其授权。使用前明确读目录、写目录、来源基线与登记相符；配置不授权 clone、更新、提交或修改只读源。可用[本地领域源工具](../docs/domain-sources.md#operations)只读 inspect；明确 register 只维护既有配置，materialization/submodule 另选目标及 index 同意。填写配置或 ready 提案不表示已接入，不允许网络请求或隐含提交。

已有 BC 需要实施摘要时，按[收集契约](../.github/contracts/README.md#implementation-report)给出明确 commit、scope 和原 VT 记录。收集器核对配置中的本地领域 root/path/固定基线，不 clone、不回写；源配置和代码/测试位置绑定测试对象，新增运行保留自己的 bytes 基线。[输出表单](../_templates/reports/implementation-report.yaml)不是执行输入账本。报告另行显式登记到 model 的 verification 来源后，只以报告引用连接；九视图仍归 model，不把治理/风险/序列等来源冒充执行证据。

## 维护入口

真实 ABB/ADR/SEQ/SWAS 创建后在这里添加链接。普通工作进度写[开发日志](../logs/README.md)，规则或需求变化按[语义影响检查](../verification/README.md#change-impact)复核设计及旧结果；不把日志当设计决策来源的替代品。
