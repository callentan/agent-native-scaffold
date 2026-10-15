# 六仓固定版本能力矩阵

**2026-10-15：源码盘点已完成，功能对齐尚未完成。** 本轮通过现有 Git 凭据只读获取六个约定的完整 commit，不依赖登录页或旧研究摘要。原始对象和内容只保存在制作会话的资料区，没有执行上游脚本、安装 hook、更新 submodule 或修改参考仓库。

当前本仓库实施起点为 `1a6f594`（提交此前 README 排版后的干净工作区）；六仓基线见下表。用户本轮确认把新发现的现有功能一并纳入增强，音频、PDF 和外部平台的依赖/执行仍各自授权。实现语言仍 Python 优先，默认单仓，不强制建立领域子模块。

## 1. 如何读取这份矩阵

- `observed-current` 只表示固定源中有该文件/功能载体；形态另分真实脚本、声明式 pipeline、Agent 方法、模板/规则，不表示已在我们的项目运行或实现。
- `proposed-upstream` 专指上游路线图，不能混入功能等价分母。本计划新增自动化是独立设计，不称为上游现有实现。
- `instance-only` 是实例占位或一次性内容；记录其用途，但不把示例业务当当前事实。无源外部系统/批准结果为 `unverified`。
- 目录/gitlink 属元数据盘点，不算完整文件阅读。195 个 blob 中 185 个全文读取；10 个 `_roadmap` 文件按所列范围读取并排除出当前实现能力。57 个目录/gitlink 只读元数据。
- 三组来源合计 44 个 current 能力组，存在交叉职责，**不是 44 个互不重叠的产品功能或已完成任务**。另有 6 组上游提案和 1 组未解析依赖。

六个 Git 树共有 252 entries：195 blobs、53 trees、4 gitlinks。Git `ls-tree` 不包含仓库根；旧 API 的 258 条目包含六个根，二者不是版本差异。每个 manifest entry 在文件清单恰有一行；审核还核对 commit/object ID、文件散列、能力 ID 和引用行界限。

## 2. 需要修正的先前认识

`ddd-bc` **确有** `tools\setup-domain-model-submodule.ps1`，负责领域子模块接入，且会改 Git 设置、索引和创建提交。之前只能确认部分历史摘要，不能由“没有确认 PowerShell”推导它不存在。新版本将提供等价的可选 Python 接入能力，拆开预检、明确安装与提交授权，不复制其隐含副作用。

`ddd-subdomain` 不仅有标题/占位校验、commit-msg 和 fan-out，还包含文档/转录适配、音频转录、置信度评分、关系图、交互记账和一次性管理演示工具。哪些是部分实现或依赖外部服务，见各能力载体；源码存在不等于运行通过。

目前计划确实遗漏的持续功能还有 QAS、战术领域工件、Published Interface/词汇演化、SEQ 与 sequenceSummary、Markdown+Gherkin 场景，以及 SWAS/PDF。用户已确认扩充计划承接，不能用增加 JSON Schema 或 checker 代替这些原本不同的用户活动。

## 3. 来源与实现边界的处理

| 来源差异 | 本增强处理及接受标准 |
|---|---|
| PowerShell 子模块安装器隐含 commit | Python 预检/可选接入；默认单仓，本地变更/网络/提交分别授权，冲突保留原文 |
| 领域源只读但 prompt 要回写/推送 `model.yaml` | 原业务事实只读，本地派生视图与实施摘要单独维护；跨仓贡献走获授权提案/PR，不把源中矛盾作为必须复刻的行为 |
| Draft/Approved/Implemented/Passing 等状态混用 | 内容声明、任务进度、实际结果、适用性独立；有来源的旧值明确映射，不伪造批准 |
| VT/场景的 Markdown 与 `.feature` 都声称 canonical | `.feature` 拥有可执行 Gherkin 正文，Markdown 记录元数据/判据与引用；不存在应用时计划仍 not-run |
| validator 的 main/master/staged fallback 与 graph 的 demo fallback | 显式对象基线，输入失败不回退；空图/空库存如实显示，不注入演示成功 |
| fan-out 自动 clone/commit/push/PR | 明确目标清单、固定输入、差异提案、逐目标结果；实际远端操作在授权关卡后验证 |
| 音频/文档/PDF 依赖外部 SDK、模型、容器或引擎 | 可选适配器，默认不发送资料；依赖、数据处理范围与凭据另行确认，没有依赖时明确 unavailable/not-run |
| `_gen_ppt.py` 硬编码管理内容和个人路径 | 不复制原演示内容；保留“从指定资料生成演示文件”的可选功能，输入与输出显式，实际渲染依赖另验 |
| 工具资格/审阅文本与不受约束的执行权限 | 保留资格、风险和实际人工决定记录，不把 trailer、角色或通过的格式检查当身份/权限认证 |

## 4. 跨组与外部依赖

BC 的 prompts/templates gitlink 指向本轮已取回的两仓版本，可以解析。领域 framework 的 `.github\prompts` 固定 `d7da752b7312dd9212c3fea15eba7fbf1c1edfba`，`_templates` 固定 `9cc3338ba0d7fde01ac43c2562f0c7f8a57e8ab6`，不同于本次指定的两个独立参考版本；本矩阵分别登记，不声称其消费组合已验。

真实领域实例、中央 ADR wiki、Risk Management、ADO 查询对象、组织权限、真实 pipeline、工具资格决定和外部执行结果不属于这六个固定树，仍未验证。六仓能力盘点完成不以读取这些实例为前提，但所有依赖它们的执行/兼容/审批结论必须保持未验证。

本地 manifest、独立分组报告和 `source-audit.json` 在制作会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution` 中。它们不是跨机器可访问的 CI 证据；不能访问时按本文件的完整 commit 与路径重新只读获取。以下仅保存独立概括和定位，不复制源码/模板正文，不进入下游分发。

<!-- generated-source-tables -->

## 5. 固定版本与实际清单计数

| 仓库 | 完整 commit | entries / blobs |
|---|---|---|
| [ddd-bc](https://dev.azure.com/shcgravity/Center/_git/ddd-bc?version=GCbac263bea39988214b82cafb48f27e3a2136c534) | `bac263bea39988214b82cafb48f27e3a2136c534` | 32 / 22 |
| [ddd-bc-prompts](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-prompts?version=GC08f8219397d6fe6d000312f5956a493b1b28cc84) | `08f8219397d6fe6d000312f5956a493b1b28cc84` | 15 / 13 |
| [ddd-bc-templates](https://dev.azure.com/shcgravity/Center/_git/ddd-bc-templates?version=GC00705aef6c70f855ef95588b0137cf7f2387efb0) | `00705aef6c70f855ef95588b0137cf7f2387efb0` | 15 / 11 |
| [ddd-subdomain-prompts](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain-prompts?version=GC1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c) | `1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c` | 19 / 17 |
| [ddd-subdomain-templates](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain-templates?version=GC59f98e352a150f99290a3855092298dbe11e0615) | `59f98e352a150f99290a3855092298dbe11e0615` | 65 / 47 |
| [ddd-subdomain](https://dev.azure.com/shcgravity/Center/_git/ddd-subdomain?version=GCe115ad4d03ac53359c608ce7d32262a508561496) | `e115ad4d03ac53359c608ce7d32262a508561496` | 106 / 85 |

## 6. 当前来源能力与目标任务

任务号对应增强计划；新增 15–18 为本轮核实遗漏后补入。本节的目标均未实施，不把 source 的 current 当作我们的完成状态。

### BC-01：BC 身份与领域输入挂载

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc:bc-config.yaml:1-20`；`ddd-bc:.gitmodules:1-6`；`ddd-bc:tools/setup-domain-model-submodule.ps1:31-114`；`ddd-bc:.github/copilot-instructions.md:17-31` |
| 原载体 | real executable + template/config |
| 输入 | bc-config.yaml 中的 BC/子域/领域仓 URL/相对路径，以及 Git 根目录和 DomainModelUrl。 |
| 输出 | 实例身份字段、domain-model 挂载、.gitmodules 递归策略和本地 submodule 配置。 |
| 前提 | 必须从真实 Git 根目录运行；配置和领域仓 URL 由维护者提供；当前快照仍为占位配置。 |
| 失败与写入边界 | 脚本会在根目录或 Git 操作失败时抛错；可移除占位目录、改写索引/.gitmodules、写本地 Git 配置、添加子模块并提交。不会自动取得领域内容。 |
| 当前骨架差距 | 尚无 BC 配置或领域来源接入脚本；已有 onboarding 的不覆盖/缺输入停止约定。 |
| 目标任务 / 增强验收 | 15 / ENH-01、ENH-02、ENH-06、ENH-10、ENH-15 |
| 目标验收 | 在含空格路径的空白实例中，错误根目录、无效 URL、占位目录和已存在子模块分别给出非零结果；成功路径只在明确授权后改变列出的 Git 对象，并能读取固定领域基线。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-02：底层 V 工件模型与唯一事实边界

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc:.github/copilot-instructions.md:7-15,33-50,63-86`；`ddd-bc:CONCEPTS.md:8-31,34-157`；`ddd-bc-templates:items/sr.md:1-50`；`ddd-bc-templates:items/user-story.md:1-46`；`ddd-bc-templates:items/verification-test.md:1-35` |
| 原载体 | template/config + documented Agent operation |
| 输入 | 领域 REQ/UC/INV/验证源和 bottom-of-V 的 SR、US、ABB、VT 关系。 |
| 输出 | Markdown front matter、正文 AC/范围/验证方法、目录索引和 traceability-matrix 行。 |
| 前提 | 先有领域模型；SR 先于 US，US 批准后才允许 ABB/VT/代码相应步骤；实例需从模板填值。 |
| 失败与写入边界 | 规则要求缺源、错序或未批准时停止；创建工件会写本仓 Markdown 和矩阵，模型摘要另触及 domain-model/model.yaml。 |
| 当前骨架差距 | 已有 REQ/SR/US/ABB/VT 基础职责；完整领域种类、Gherkin/风险与桥接字段未交付。 |
| 目标任务 / 增强验收 | 1、2、3、5、12 / ENH-01、ENH-02、ENH-03、ENH-05、ENH-13 |
| 目标验收 | 同一 scope 重号、不同 scope 同号、缺必填元数据和空骨架分别产生可定位结果；正文与原 AC/锚点字节不被迁移器覆盖。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-03：软件需求派生

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:sr-derivation.prompt.md:14-62,91-104`；`ddd-bc-templates:items/sr.md:1-50`；`ddd-bc:.github/instructions/implementation.instructions.md:1-55` |
| 原载体 | documented Agent operation |
| 输入 | bc-config、领域 use-cases/invariants、被引用 REQ、已有 SR 和人工范围选择。 |
| 输出 | 可测 SR Markdown、REQ/UC/INV/RC 关系、traceability 行及 model.yaml 的 srSummary。 |
| 前提 | 领域路径可读，REQ/UC 已批准，Draft INV 不能生成强制 SR；需人工指定范围。 |
| 失败与写入边界 | 路径、状态、歧义或缺领域输入时停并报告；写入本仓 SR/矩阵，随后按现有 prompt 还会写 domain-model/model.yaml 并提交/推送。 |
| 当前骨架差距 | specify-feature 已支持通用软件验收；完整 UC/INV/QAS/RC 派生及结构化来源未交付。 |
| 目标任务 / 增强验收 | 1、4、5 / ENH-01、ENH-04、ENH-05 |
| 目标验收 | 缺 UC、未批准 REQ、Draft INV、重复 SR 和有歧义替代路径均停止并报告；合格输入只生成 Draft SR 并给出完整来源定位。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-04：用户故事切片与不变量 AC

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:story-derivation.prompt.md:8-68,89-108`；`ddd-bc-templates:items/user-story.md:1-46`；`ddd-bc:user-stories/README.md:1-42` |
| 原载体 | documented Agent operation + template |
| 输入 | 已存在且批准的 SR、其 UC actor/alternate/INV、REQ 业务价值和已有 US。 |
| 输出 | Backlog 状态的 US、正/替代/强制不变量 AC、DoD、矩阵关联和 storySummary。 |
| 前提 | SR 必须存在且 Approved；UC、INV 和 REQ 可读；范围按用户价值切片而非技术层。 |
| 失败与写入边界 | 无 SR、Draft SR、冲突修改或安全链变化时停；正常写入本仓 US/矩阵，摘要更新仍可能写入领域子模块。 |
| 当前骨架差距 | 已有可选 US 表单；更完整的角色/价值/路径派生、状态映射及覆盖关系需补。 |
| 目标任务 / 增强验收 | 1、3、4、5 / ENH-01、ENH-03、ENH-04、ENH-05 |
| 目标验收 | 未批准 SR 不产生 US；每个生成 US 的 AC 可回指 UC/INV，且更改父 SR 会列出下游回退而不静默覆盖。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-05：ABB 架构、ADR 与 QAS 约束

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:abb-design.prompt.md:8-115`；`ddd-bc:architecture/README.md:1-42`；`ddd-bc-templates:items/abb.md:1-55`；`ddd-bc:architecture/adr-references.md:1-24` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 批准 US、领域 capability/context-map/QAS/model、已有 ABB 和 ADR 登记。 |
| 输出 | 逻辑 ABB 文档、接口/依赖版本/部署/观测字段、矩阵/ADR 引用和 abbSummary。 |
| 前提 | 至少一个 Approved US、领域相关文件及 ADR 约束可读；Draft QAS 只能标临时。 |
| 失败与写入边界 | 缺领域文件或未批准 US 时停；技术跨边界无 ADR 不选型；写入本仓 ABB/矩阵/ADR 日志，并按 prompt 改 model.yaml。 |
| 当前骨架差距 | 已有 ABB/ADR 表单；QAS、运行/部署、集成来源与完整架构视图需补。 |
| 目标任务 / 增强验收 | 1、5、9 / ENH-01、ENH-05、ENH-06、ENH-09 |
| 目标验收 | 无 Approved US、Draft QAS、缺 ADR、未固定依赖版本分别阻断或标注；有效 ABB 关系能反查至少一个 US 和来源版本。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-06：验证规格与 Gherkin 两件套

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:verification-test.prompt.md:8-79,86-128`；`ddd-bc-templates:items/verification-test.md:1-35`；`ddd-bc-templates:items/verification-test.feature:1-56`；`ddd-bc:verification/README.md:1-48` |
| 原载体 | documented Agent operation + template |
| 输入 | 批准 US/SR、INV、ABB、已有 VT 和领域 TS 场景；由人选择范围。 |
| 输出 | 每个 VT 的 Markdown 规格和同名 feature，类型、安全标记、AC 映射、测试文件字段及 verificationSummary。 |
| 前提 | US 文件存在且 Approved；领域不变量和相关 ABB 可读；实现测试不由该 prompt 生成。 |
| 失败与写入边界 | 缺 US/INV/ABB、状态不允许或修改已自动化安全 VT 时停；写入本仓 verification 文档/feature，摘要更新仍触及领域子模块。 |
| 当前骨架差距 | 已有分层 VT 与逐项目标/not-run；Gherkin companion、完整验证类型/标签未交付。 |
| 目标任务 / 增强验收 | 1、5、6、10、13 / ENH-01、ENH-05、ENH-07、ENH-10、ENH-14 |
| 目标验收 | 每个 US AC 至少有一个 VT，INV AC 有负例，未运行保持 not-run；非法映射和安全链断点在报告中有源行定位。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-07：四层 DDD 代码生成护栏

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:code-generation.prompt.md:30-77,102-238`；`ddd-bc:.github/instructions/architecture.instructions.md:1-66`；`ddd-bc:.github/instructions/coding-standards.instructions.md:1-67` |
| 原载体 | documented Agent operation |
| 输入 | bc-config 语言/框架、批准 US、ABB、领域聚合/实体/值对象/事件/不变量、已有 src 状态。 |
| 输出 | 按 scope 的 domain/application/infrastructure/api scaffold 或增量文件、trace marker 和冲突报告。 |
| 前提 | 领域路径可读、语言/框架不是占位、批准 US 与 ABB 存在；已有非空文件不可静默覆盖。 |
| 失败与写入边界 | 缺输入、Draft 不变量、非空冲突或领域缺口时停/跳过并报告；只写 src，不生成测试代码、不修改只读领域源。 |
| 当前骨架差距 | implement-task 可指导已配置项目维护；尚无独立初始代码生成方法或实际应用验收。 |
| 目标任务 / 增强验收 | 1、5、13 / ENH-01、ENH-05、ENH-14 |
| 目标验收 | 缺语言/框架/批准 US/ABB/领域对象时不写；非空目标和路径越界被列为 conflict；生成结果不含未授权业务行为且测试仍 not-run。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-08：追溯矩阵、审阅、查询与 backlog 治理

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:traceability-build.prompt.md:14-64`；`ddd-bc-prompts:review.prompt.md:14-104`；`ddd-bc-prompts:backlog-review.prompt.md:14-96`；`ddd-bc-prompts:query.prompt.md:14-77`；`ddd-bc:traceability-matrix.md:1-52` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 领域 REQ/UC/INV 和本仓 SR/US/ABB/VT、现有矩阵/backlog；查询由自然语言给出。 |
| 输出 | 矩阵行、覆盖统计、断链/缺口、review 摘要、BL-NNN 状态和只读查询结果。 |
| 前提 | 领域子模块与所有工件可读；矩阵重建必须先保留手工区段；安全链需能回源。 |
| 失败与写入边界 | 领域不可读时不得生成不完整矩阵；build/backlog 可写本仓矩阵/backlog，review/query 只报告；当前无独立 validator。 |
| 当前骨架差距 | 已有验收库存、缺口核对与审阅方法；完整 query/backlog/矩阵活动入口需补。 |
| 目标任务 / 增强验收 | 1、6、7、9、14 / ENH-01、ENH-07、ENH-08、ENH-09、ENH-12 |
| 目标验收 | 给定精确交付 ID 和 Git 基线时，缺目标、悬空引用、同号异主、旧基线和空骨架均能确定性定位，矩阵正文不被静默改写。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-09：领域变更影响与状态回退

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:impact-assessment.prompt.md:18-124`；`ddd-bc-prompts:skills/bc-implementation/SKILL.md:19-28,114-124`；`ddd-bc:backlog.md:1-32` |
| 原载体 | documented Agent operation |
| 输入 | REQ/UC/INV 变化 ID、更新后的领域源和本仓 SR/US/ABB/VT。 |
| 输出 | 直接/间接影响表、RC 链检查、SR→US→VT 状态回退建议和 BL-NNN。 |
| 前提 | 领域源须先更新到可读版本；任何回退要有用户确认，安全关键链需书面复核。 |
| 失败与写入边界 | 源未更新或子模块未初始化时停止；默认只产报告，获指令后才改本仓状态/backlog，禁止改领域文件。 |
| 当前骨架差距 | 已有规则语义影响和旧结果适用性；完整 UC/INV/QAS/风险链尚未建模。 |
| 目标任务 / 增强验收 | 1、4、7 / ENH-01、ENH-04、ENH-08 |
| 目标验收 | 修改 REQ/UC/INV 后能列出受影响工件、理由和状态回退；未确认或安全关键项不会自动改状态或关闭 backlog。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-10：新成员接入与领域子模块安装

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:onboarding.prompt.md:14-44,48-121`；`ddd-bc:tools/setup-domain-model-submodule.ps1:31-114`；`ddd-bc:domain-model/README.md:1-29` |
| 原载体 | real executable + documented Agent operation |
| 输入 | 交互式 BC 名称、子域、领域 URL、上下文路径、仓库/团队、语言/框架和角色。 |
| 输出 | 填好的 bc-config、初始化后的领域挂载和按角色的只读导览。 |
| 前提 | 用户逐项提供配置并确认安装脚本成功；领域源可初始化。 |
| 失败与写入边界 | 占位字段、空领域目录或脚本失败会停止导览；配置和子模块安装有真实写入/提交副作用，导览本身只读。 |
| 当前骨架差距 | 已有不选栈 onboarding；可选外部领域配置/接入及来源检测未交付。 |
| 目标任务 / 增强验收 | 4、15 / ENH-01、ENH-06、ENH-10、ENH-14、ENH-15 |
| 目标验收 | 角色选择和占位检查可重复；未完成安装不展示下游解释；已授权成功安装后能读取固定领域基线，未授权时不改仓。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-11：运行时序列图与异步边界

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:sequence-diagram.prompt.md:3-12,14-58,60-177`；`ddd-bc-templates:items/sequence-diagram.md:1-67` |
| 原载体 | documented Agent operation + template |
| 输入 | 批准 UC/US、ABB、INV、domain-events catalog、integration 和 context-map，及既有 SEQ 编号。 |
| 输出 | 含成功/错误路径的 Mermaid SEQ Markdown、矩阵关联和 model.yaml sequenceSummary。 |
| 前提 | UC 非 Draft、至少一个 ABB/US、集成参与者和异步模式可回源；已有 Approved SEQ 修改需确认。 |
| 失败与写入边界 | 无 ABB 参与者、无异步集成支持或 Draft UC 时标 BL/停止；写本仓 sequence 文件/矩阵，另写领域子模块摘要并提交推送。 |
| 当前骨架差距 | 尚无 SEQ 表单、序列活动和 sequenceSummary 的实际引用。 |
| 目标任务 / 增强验收 | 5、8、17 / ENH-01、ENH-05、ENH-06、ENH-14、ENH-17 |
| 目标验收 | 每个批准 UC 的参与者和消息都有 ABB/领域证据，跨集成调用保持异步；缺参与者/异步映射/错误路径时报告而非生成完整图。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-12：model.yaml 派生桥接与版本摘要

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc-prompts:skills/bc-implementation/SKILL.md:19-28,114-124`；`ddd-bc-prompts:sr-derivation.prompt.md:64-88`；`ddd-bc-prompts:abb-design.prompt.md:70-99`；`ddd-bc-prompts:sequence-diagram.prompt.md:136-161` |
| 原载体 | documented Agent operation |
| 输入 | 各类工件派生事件、领域 model.yaml、版本号和关系。 |
| 输出 | srSummary/storySummary/abbSummary/verificationSummary/sequenceSummary/releaseStatus 等机器摘要。 |
| 前提 | 领域子模块本地可写且 Git 身份/权限/远端可用；每个 prompt 负责在相应 milestone 更新。 |
| 失败与写入边界 | 当前规则同时宣称 domain-model 只读又允许修改 model.yaml；prompt 示例要求在子模块 commit/push，再推进 BC 指针，副作用越出本仓。 |
| 当前骨架差距 | 已有只读/授权约定；结构化实现摘要、来源固定与跨仓贡献提案未交付。 |
| 目标任务 / 增强验收 | 1、2、7、8、14 / ENH-01、ENH-02、ENH-06、ENH-08、ENH-12 |
| 目标验收 | 同一源输入导出字节稳定且可回源；领域正文不被写入；无远端权限时只产本地摘要/提案，不报告已同步。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-13：架构、编码、安全与测试规则集

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc:.github/instructions/architecture.instructions.md:1-66`；`ddd-bc:.github/instructions/coding-standards.instructions.md:1-67`；`ddd-bc:.github/instructions/security.instructions.md:1-65`；`ddd-bc:.github/instructions/testing.instructions.md:1-72` |
| 原载体 | documented Agent operation |
| 输入 | src、工件和测试文件路径匹配，领域术语/风险控制/依赖版本作为上下文。 |
| 输出 | 供 Agent 生成/评审时遵守的规则：依赖方向、命名、输入安全、测试覆盖和日志边界。 |
| 前提 | 宿主支持 path-scoped instructions 并正确加载；实际语言、框架和领域 glossary 可用。 |
| 失败与写入边界 | 规则本身没有执行器、发现数或退出码；违反时只依赖 Agent/人工发现，源文件不会被规则自动修改。 |
| 当前骨架差距 | 已有文档/测试规则；独立编码/架构/安全规则及适用例外需补。 |
| 目标任务 / 增强验收 | 1、5、6、9、10 / ENH-01、ENH-05、ENH-07、ENH-09、ENH-10 |
| 目标验收 | 路径匹配和不匹配样例分别可观察；机械违规给出 code/path/line，无法机械判断的安全或架构决定保持 review-required。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### BC-14：模板驱动创建与模板生命周期

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-bc:.github/copilot-instructions.md:52-61`；`ddd-bc:TEMPLATE-CHANGELOG.md:1-29`；`ddd-bc-templates:items:metadata-only`；`ddd-bc-templates:verification:metadata-only` |
| 原载体 | template/config + documented Agent operation |
| 输入 | 工件类型、对应模板、实际领域值和目标编号。 |
| 输出 | 去占位的 SR/US/ABB/VT/SEQ/验证规格文件，并在同一操作更新矩阵。 |
| 前提 | 模板子模块固定且文件可读；需要 Agent 按提示复制和填充，不得把占位交付为实例结果。 |
| 失败与写入边界 | 没有模板更新器、版本比较或 fan-out 工具；自动创建规则会写本仓工件/矩阵，模板变更只能靠 Git 子模块版本和人工合并。 |
| 当前骨架差距 | 已有七种基础表单；原来源的完整种类、同名 feature 与演进判据需补。 |
| 目标任务 / 增强验收 | 1、3、11、12 / ENH-01、ENH-02、ENH-03、ENH-11、ENH-13 |
| 目标验收 | 模板候选与本地业务改动三方比较能列出 preserved/changes/conflicts；冲突不写入、不自动合并，排除目录不会被候选引用。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-01：领域建模技能与入口路由

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:skills/domain-modeling/SKILL.md:1-91`；`ddd-subdomain-prompts:onboarding.prompt.md:10-16` |
| 原载体 | documented Agent operation |
| 输入 | 目标、角色、子域/BC 范围和现有资料。 |
| 输出 | 适用 prompt、阅读顺序、guardrails 和下一步活动。 |
| 前提 | 先读规则和目标模型；缺角色/范围时逐问。 |
| 失败与写入边界 | 未知进 BL；技能不授予批准、权限或远端写入。 |
| 当前骨架差距 | 已有六共享方法与三个模式；领域原活动的完整输入/产出覆盖需补。 |
| 目标任务 / 增强验收 | 1、4、9、13 / ENH-01、ENH-02、ENH-04、ENH-09、ENH-14 |
| 目标验收 | 给定活动/角色/范围能列唯一方法、前置、可写文件和停止条件，且不自动产生批准事实。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-02：领域访谈与战略边界建模

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:elicitation.prompt.md:40-186`；`ddd-subdomain-templates:subdomain/subdomain-definition.md:9-107`；`ddd-subdomain-templates:context/use-cases.md:1-47` |
| 原载体 | documented Agent operation + template/config |
| 输入 | Intended Use、专家输入、候选边界、术语、演员和业务规则。 |
| 输出 | 子域、BC、词汇、UC、BR、INV 和战术候选，默认 Draft。 |
| 前提 | Intended Use/目标至少 Draft；先战略后战术；BR 先于 INV。 |
| 失败与写入边界 | 逐问、记录排除理由；用户确认后写，未知进 BL。 |
| 当前骨架差距 | 已有最低术语/关系/规则/职责；完整战略访谈和可选战术派生需补。 |
| 目标任务 / 增强验收 | 3、4 / ENH-03、ENH-04、ENH-06 |
| 目标验收 | 两个上下文同号可按 scope 区分；未确认边界不能 Approved/战术派生。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-03：知识锤炼、模型评审与漂移挑战

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:distillation.prompt.md:10-141`；`ddd-subdomain-prompts:review.prompt.md:10-136`；`ddd-subdomain-templates:context/aggregates/README.md:7-24` |
| 原载体 | documented Agent operation |
| 输入 | 已有模型、专家/开发者/监管角色、开放存根和漂移线索。 |
| 输出 | 语言、概念、边界、聚合、INV、事件、追溯问题及 BL/ADR 建议。 |
| 前提 | 需领域专家；Intended Use 至少 Draft；先扫描存根。 |
| 失败与写入边界 | 只提发现/建议；边界变化先 BL/ADR；不自动认证健康。 |
| 当前骨架差距 | 已有通用审阅/影响方法；独立锤炼、边界挑战和模型漂移活动需补。 |
| 目标任务 / 增强验收 | 4、9、13 / ENH-04、ENH-09、ENH-14 |
| 目标验收 | 同一问题有文件/行、严重度、建议、影响链和人工决定状态。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-04：棕地 ADO 反向提取与置信度分层

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:reverse-engineering.prompt.md:12-78`；`ddd-subdomain-prompts:reverse-engineering.prompt.md:140-292`；`ddd-subdomain-prompts:reverse-engineering.prompt.md:335-409` |
| 原载体 | documented Agent operation |
| 输入 | ADO MCP、组织/项目/Area Path/子域/安全分类和 Epic/Feature/Story/Test Case。 |
| 输出 | Draft REQ/CAP/UC/INV/词汇/矩阵/BL 及 High/Medium/Low confidence 报告。 |
| 前提 | ADO MCP 可用且有 Epic；子域/安全分类确认；BC 逐一人工确认。 |
| 失败与写入边界 | 缺 MCP/Epic/边界争议/安全前置时停止；不把 ADO 状态当 Approved。 |
| 当前骨架差距 | 尚无独立逆向方法、来源适配或置信度候选报告。 |
| 目标任务 / 增强验收 | 1、4、7、13 / ENH-01、ENH-04、ENH-08、ENH-14 |
| 目标验收 | 每个对象可回指 ADO 类型/ID/位置和置信度；Medium/Low 不升级状态。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-05：需求与质量属性场景捕获

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:requirements-capture.prompt.md:12-143`；`ddd-subdomain-prompts:requirements-capture.prompt.md:161-228`；`ddd-subdomain-templates:requirements/_template.md:1-121`；`ddd-subdomain-templates:requirements/_template-qas.md:1-108` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 业务问题、Intended Use、治理目录、UC/词汇/追溯和 QAS 触发。 |
| 输出 | Draft REQ、ATAM QAS、领域影响、UC/矩阵/变更日志链接。 |
| 前提 | 先查治理/自动派生；REQ solution-free 且专家确认；QAS 可量化。 |
| 失败与写入边界 | 治理缺口、范围扩展、约束冲突或不可测时停留 BL/未决。 |
| 当前骨架差距 | 已有 REQ 业务验收；独立 QAS、治理映射与量化场景表单未交付。 |
| 目标任务 / 增强验收 | 3、4、5 / ENH-03、ENH-05、ENH-07、ENH-14 |
| 目标验收 | 无覆盖/测量/专家确认不 Approved；ATAM 六要素和响应数字可定位。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-06：架构决策编制与来件影响处理

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:adr.prompt.md:18-129`；`ddd-subdomain-prompts:adr.prompt.md:133-196`；`ddd-subdomain-templates:items/adr.md:1-71` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 决策/来件 ADR、决策人、问题、选项和当前模型影响。 |
| 输出 | ADR 草稿或来件影响报告、通知表、BL 和发布后引用计划。 |
| 前提 | Mode 明确、影响已读；确认后产出/应用；外部 wiki 由人发布。 |
| 失败与写入边界 | 缺内容/影响不清时只留问题/BL；不宣称 wiki 发布或批准。 |
| 当前骨架差距 | 已有本地 ADR 表单；来件 ADR 的跨上下文影响/通知提案需补。 |
| 目标任务 / 增强验收 | 4、5、9、13 / ENH-04、ENH-05、ENH-09、ENH-12、ENH-14 |
| 目标验收 | 未确认只能草稿/BL；来件能列受影响上下文、消费者和动作且无自动 wiki 写入。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-07：需求变更影响分析与授权门槛

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:impact-assessment.prompt.md:10-81`；`ddd-subdomain-prompts:impact-assessment.prompt.md:81-138`；`ddd-subdomain-templates:requirements/_template.md:47-121` |
| 原载体 | documented Agent operation |
| 输入 | REQ、变更类型/确认状态、模型、矩阵、QAS/ADR/接口/风险关系。 |
| 输出 | 影响工件表、严重度分类、冲突表、推荐顺序和问题。 |
| 前提 | REQ/QAS/矩阵源已读；库存证据组装；报告后等待批准。 |
| 失败与写入边界 | 链接缺失/不确定不猜；建议顺序不是已执行写入。 |
| 当前骨架差距 | 已有基本规则/验收影响；完整需求/QAS/接口/风险依赖需补。 |
| 目标任务 / 增强验收 | 4、7、13 / ENH-04、ENH-08、ENH-14 |
| 目标验收 | 一次 REQ 变更列出所有受影响对象、原因和待批准动作。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-08：Intended Use 变更与风险升级

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:intended-use-amendment.prompt.md:10-167`；`ddd-subdomain-templates:subdomain/intended-use.md:1-154` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 当前/拟议 Intended Use、目标章节、理由及 safety/utility sections。 |
| 输出 | 修订分类、监管显著性、RA 升级、下游影响、风险再分析和 BL。 |
| 前提 | 当前文件完整、章节/基线明确；高显著性扩展先 RA 审阅。 |
| 失败与写入边界 | 不确定按高风险升级或保留问题；风险分析不在这里代做。 |
| 当前骨架差距 | 尚无 Intended Use 表单与变更/升级路径；不自作监管判断。 |
| 目标任务 / 增强验收 | 3、4、9 / ENH-03、ENH-04、ENH-09、ENH-14 |
| 目标验收 | 范围/患者/用户/约束/安全变化产生升级记录；无确认不留 Approved。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-09：评审、开放问题与 backlog/一致性同步

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:review.prompt.md:10-136`；`ddd-subdomain-prompts:backlog-review.prompt.md:10-75`；`ddd-subdomain-templates:subdomain/strategic/bounded-contexts.md:33-37` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 模型、需求、测试、矩阵、规则和 NEEDS CLARIFICATION/AUTO-DERIVED/BL。 |
| 输出 | 严重度发现、BL 建议、解决统计、上下文健康摘要和追溯缺口。 |
| 前提 | 需完整模型和指引；解决项须有书面证据。 |
| 失败与写入边界 | 不重构/不假设；不能证明就 Open；不认证合规。 |
| 当前骨架差距 | 已有缺口和交接；独立 BL/评审记录、关闭依据和 backlog 活动需补。 |
| 目标任务 / 增强验收 | 3、4、6、7、9、13 / ENH-04、ENH-07、ENH-08、ENH-09、ENH-14 |
| 目标验收 | 每个开放项都有源文件/行、BL、影响和状态；无证据保持 Open。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-10：词汇对齐与上下文语言治理

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:glossary-sync.prompt.md:10-121`；`ddd-subdomain-templates:subdomain/glossary/ubiquitous-language.md:1-46`；`ddd-subdomain-templates:subdomain/glossary/business-rules.md:1-66` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 外部/本地 glossary、术语状态、上下文和未确认标记。 |
| 输出 | 逐术语分类报告、冲突选项、获批后的词汇/弃用/BL 更新。 |
| 前提 | 两边词汇完整读取；未确认术语不参加对齐；冲突需用户选择。 |
| 失败与写入边界 | 不静默采用外部含义；重命名先扫影响；只应用获批变更。 |
| 当前骨架差距 | 已有共同术语栏；外部/本地词汇对齐、弃用和冲突决策流程未交付。 |
| 目标任务 / 增强验收 | 3、4、11 / ENH-03、ENH-04、ENH-11、ENH-12 |
| 目标验收 | 同名异义/外部专有/内部专有/未确认词分别列出，未批准不改 canonical term。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-11：Published Interface 合约生命周期

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:published-interface.prompt.md:10-126`；`ddd-subdomain-templates:subdomain/published-interface.md:1-129`；`ddd-subdomain-templates:context/integration/README.md:17-80` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 操作类型、当前接口、模型/词汇/消费者、模式、版本和差异。 |
| 输出 | 变更分类、版本、消费者影响、通知消息和待更新文件。 |
| 前提 | 元素已建模、词汇 canonical、能力已分类、model/context 注册有效。 |
| 失败与写入边界 | 未建模/未分类/影响不清时阻止或按 breaking；不实际发送通知。 |
| 当前骨架差距 | 尚无 Published Interface 的版本、消费者与通知提案工件。 |
| 目标任务 / 增强验收 | 3、4、5、11 / ENH-03、ENH-04、ENH-10、ENH-11、ENH-12、ENH-14 |
| 目标验收 | 语义变更自动 breaking+major+全消费者通知草稿，未批准不改源。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-12：查询与只读模型库存

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:query.prompt.md:10-70`；`ddd-subdomain-templates:context/model.yaml:36-147`；`ddd-subdomain-templates:context/domain-events/catalog.md:1-36` |
| 原载体 | documented Agent operation + template/config |
| 输入 | 对象类型和范围。 |
| 输出 | 实际源文件上的列表、过滤结果或 BC 摘要。 |
| 前提 | 范围明确，读取对应源文件，不猜不存在对象。 |
| 失败与写入边界 | 只读，不补造对象；没有持久化索引或导出副作用。 |
| 当前骨架差距 | 可显式读现有资料；尚无结构化库存及完整领域 query 活动。 |
| 目标任务 / 增强验收 | 2、3、7、8 / ENH-02、ENH-06、ENH-07、ENH-08 |
| 目标验收 | 同一输入得确定排序/计数；scope 同号、重复 ID、失效链接和手改视图可发现。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-13：领域场景、验收与 QAS 验证编制

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:test-scenario.prompt.md:10-223`；`ddd-subdomain-templates:scenarios/domain-scenario.md:1-45`；`ddd-subdomain-templates:scenarios/acceptance-test.feature:1-48` |
| 原载体 | documented Agent operation + template/config |
| 输入 | Approved UC/INV、REQ/QAS、词汇和现有矩阵。 |
| 输出 | BC/跨 BC/REQ acceptance/QAS 的元数据与 `.feature` Gherkin。 |
| 前提 | Draft/NEEDS CLARIFICATION 对象不生成；场景需 UC/REQ 和领域语言。 |
| 失败与写入边界 | 不发明演员/结果；非行为 QAS 只留规格；本组不运行实现测试。 |
| 当前骨架差距 | 已有基础业务 VT；跨上下文/QAS 场景和 Gherkin companion 未交付。 |
| 目标任务 / 增强验收 | 3、5、10、13 / ENH-05、ENH-07、ENH-08、ENH-14 |
| 目标验收 | 每个场景有 UC/REQ/INV/QAS 定位和类型；前置不满足时只报 gap/BL。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-14：追溯矩阵、覆盖和 QMS 风险核对

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:traceability-build.prompt.md:10-230`；`ddd-subdomain-templates:qms-traceability-matrix.md:1-61`；`ddd-subdomain-templates:context/model.yaml:181-278` |
| 原载体 | documented Agent operation + template/config |
| 输入 | REQ/CAP/UC/INV/BR/TS、矩阵和 SR/US/VT/riskSummary 桥接。 |
| 输出 | 普通矩阵、gap/orphan、coverage、QMS risk trace、阻塞和统计。 |
| 前提 | 以库存为准；NEEDS CLARIFICATION 不算覆盖；写入前展示并批准。 |
| 失败与写入边界 | 不推断链接；缺证据保持 Partial/None/blocked；不证明业务批准。 |
| 当前骨架差距 | 已有完整验收起点/逐项目标；完整领域和可选风险矩阵、机器核对未交付。 |
| 目标任务 / 增强验收 | 2、5、6、7、8、10、13、14 / ENH-02、ENH-05、ENH-06、ENH-07、ENH-08、ENH-10、ENH-12、ENH-14 |
| 目标验收 | 给定 delivery IDs 能报告缺判据、悬空/同号异主和 RC-VT 缺口，稳定区分输入错误和发现。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-15：SWAS 体系编制与 PDF 构建流水线

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:swas.prompt.md:6-226`；`ddd-subdomain-templates:subdomain/architecture-spec/AS-[SubdomainName].md:1-315`；`ddd-subdomain-templates:subdomain/architecture-spec/pipelines/generate-pdf.yml:1-30` |
| 原载体 | documented Agent operation + real executable declarative pipeline |
| 输入 | 子域/BC/需求/QAS/ABB/sequence/risk/verification bridge。 |
| 输出 | SWAS Markdown/metadata 各视图和 PDF 构件。 |
| 前提 | 源可读；缺 ABB/风险/序列保留警告；外部容器可用才跑 PDF。 |
| 失败与写入边界 | 不造技术事实；pipeline 构建不等同审批。 |
| 当前骨架差距 | 尚无 SWAS 工件/方法与可验证 PDF 导出。 |
| 目标任务 / 增强验收 | 5、8、17 / ENH-01、ENH-05、ENH-07、ENH-09、ENH-10、ENH-12、ENH-13、ENH-14、ENH-17 |
| 目标验收 | 缺数据时有可定位 TODO；固定版本构建失败传播实际错误且不写回源。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-16：领域工件分类、身份和状态语义

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-prompts:skills/domain-modeling/SKILL.md:10-49`；`ddd-subdomain-templates:context/README.md:15-60`；`ddd-subdomain-templates:context/capabilities.md:1-47`；`ddd-subdomain-templates:context/invariants.md:1-60` |
| 原载体 | template/config + documented Agent operation |
| 输入 | 子域/BC/CAP/UC/INV 的事实、来源、关系和人工状态。 |
| 输出 | Markdown 工件、Draft/Approved/Deprecated 和 release/open question 语义。 |
| 前提 | 按模板创建；scope 内 ID 唯一；确认/批准由人完成；目录同步。 |
| 失败与写入边界 | 空占位/重复/未确认只保持 Draft/开放；无统一 parser/status 校验。 |
| 当前骨架差距 | 已有最小领域及七基础表单；完整类型、scope/metadata 和状态契约未交付。 |
| 目标任务 / 增强验收 | 2、3、5、6、7 / ENH-02、ENH-03、ENH-06、ENH-07 |
| 目标验收 | 每种正式工件可由 kind/scope/id#anchor/状态/来源定位；旧 Markdown 仍可读但不报已验证。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-17：战术模型工件：聚合、实体、值对象、工厂、服务、策略与事件

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-templates:items/aggregate.md:1-194`；`ddd-subdomain-templates:items/domain-event.md:1-128`；`ddd-subdomain-templates:items/policy.md:1-87`；`ddd-subdomain-templates:items/integration-partner.md:1-67` |
| 原载体 | template/config |
| 输入 | 已确认边界/UC/BR/INV、领域行为、状态和集成事实。 |
| 输出 | 聚合、实体/VO、Factory、服务、策略、事件 schema/消费者/版本和演化记录。 |
| 前提 | 边界/用例先确认；INV 有 BR；跨边界关系用 ID/集成记录。 |
| 失败与写入边界 | 只是设计记录，不执行代码；不明确规则留 BL；不验证事件幂等/兼容。 |
| 当前骨架差距 | 原轻量规则不强制战术模式；完整可选聚合/实体/值对象/事件等表单未交付。 |
| 目标任务 / 增强验收 | 3、4、5 / ENH-03、ENH-04、ENH-05、ENH-08、ENH-12 |
| 目标验收 | 战术工件互相引用且可定位；缺 BR/消费者/版本/状态会失败或保持 Draft。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-18：上下文集成、ACL/OHS/共享内核与传播边界

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-templates:subdomain/strategic/context-map.md:1-82`；`ddd-subdomain-templates:context/integration/README.md:1-89`；`ddd-subdomain-templates:subdomain/published-interface.md:29-129` |
| 原载体 | template/config + documented Agent operation |
| 输入 | 上下文所有权/方向/模式、发布事件/服务、ACL、版本和消费者。 |
| 输出 | context-map、伙伴合同、producer/consumer、共享内核/Separate Ways 和通知要求。 |
| 前提 | 方向/团队关系和发布项明确；跨团队共享需 producer+published interface。 |
| 失败与写入边界 | 模式不清进 BL；不把 API 细节放领域正文；远端传播另授权。 |
| 当前骨架差距 | 已有方向/事实所有权；context map、集成模式/伙伴契约、演化约定需补。 |
| 目标任务 / 增强验收 | 3、4、5、11 / ENH-03、ENH-04、ENH-05、ENH-06、ENH-10、ENH-11、ENH-12 |
| 目标验收 | 每个关系有方向/模式/版本/翻译/失败边界/消费者；破坏变更只生成差异/通知提案。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-19：机器模型与跨仓实施桥接

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-templates:context/model.yaml:1-101`；`ddd-subdomain-templates:context/model.yaml:103-180`；`ddd-subdomain-templates:context/model.yaml:181-291` |
| 原载体 | template/config |
| 输入 | BC 正文、实现仓 ABB/sequence/SR/US/VT、治理、风险和发布状态。 |
| 输出 | model.yaml 快照和跨仓桥接，供 SWAS/矩阵读取。 |
| 前提 | BC team 同步；外部来源先存在；跨仓写入需授权。 |
| 失败与写入边界 | 不是正文事实或执行结果；不自动回写 source。 |
| 当前骨架差距 | 尚无带来源基线的 model 视图与结构化实施摘要。 |
| 目标任务 / 增强验收 | 2、5、7、8、10、12、13 / ENH-02、ENH-05、ENH-06、ENH-07、ENH-08、ENH-10、ENH-12、ENH-13 |
| 目标验收 | 源或实现对象改变时能发现过期/手改；缺执行证据保持 not-run/输入错误。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### DOMAIN-20：子域、临床安全、业务规则与治理基础资料

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain-templates:subdomain/subdomain-definition.md:1-149`；`ddd-subdomain-templates:subdomain/intended-use.md:1-173`；`ddd-subdomain-templates:subdomain/glossary/business-rules.md:1-66` |
| 原载体 | template/config + documented Agent operation |
| 输入 | 临床/监管范围、患者/用户/环境、愿景/分类、业务规则、BC 和边界事件。 |
| 输出 | 子域定义、Intended Use、安全/环境摘要、BR/词汇、BC/release、依赖和问题。 |
| 前提 | 责任人参与；Intended Use 在 REQ/UC 前至少 Draft；跨子域事实回产品级源。 |
| 失败与写入边界 | 不认证批准/法规/风险；缺资料阻塞受影响建模，不填默认值。 |
| 当前骨架差距 | 已有产品/领域来源；完整可选 Intended Use/治理/安全引用资料未交付。 |
| 目标任务 / 增强验收 | 3、4、5、8、9、13 / ENH-03、ENH-04、ENH-05、ENH-09、ENH-12、ENH-14 |
| 目标验收 | 无 Intended Use/目标/安全分类时明确阻塞；Draft/Review/Approved 和负责人可定位且不自动升级。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-01：说明驱动的领域建模与角色工作流

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:.github/copilot-instructions.md:1-172`；`ddd-subdomain:.github/instructions/domain-model.instructions.md:1-198`；`ddd-subdomain:.github/role-profiles/README.md:1-116`；`ddd-subdomain:docs/roles/README.md:1-45` |
| 原载体 | documented Agent operation |
| 输入 | 人类领域事实、角色选择、现有 Markdown 和提示词入口。 |
| 输出 | 按步骤导航/审阅 domain-model、requirements、testing 文档工件。 |
| 前提 | 宿主需读取本地 instructions/role guides；提示词正文依赖未核实 gitlink；结构决策需人确认。 |
| 失败与写入边界 | 规则要求未知事实进入 BL、结构变更先影响分析并等待确认，但没有工具权限或写保护。 |
| 当前骨架差距 | 已有基础共享方法/入口；原领域活动范围与完整模型组织需补。 |
| 目标任务 / 增强验收 | 1、4、5、14 / ENH-01、ENH-03、ENH-04、ENH-05、ENH-08 |
| 目标验收 | 隔离 fixture 显式读取一个方法，能定位输入、确认闸门、未决项和写入路径。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-02：顶层 V 模型工件、身份和追溯契约

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:README.md:116-210`；`ddd-subdomain:domain-model/README.md:1-63`；`ddd-subdomain:testing/README.md:1-143`；`ddd-subdomain:traceability-matrix.md:1-66`；`ddd-subdomain:docs/reference/artifact-ids.md:1-116` |
| 原载体 | documented Agent operation |
| 输入 | REQ、CAP、UC、INV、BR、TS、风险引用和底部 V 摘要。 |
| 输出 | 带 ID、Status、来源/关系语义的 Markdown 工件和追溯矩阵。 |
| 前提 | 人工确认业务事实和 ownership；需要正确 templates/prompts 子模块。 |
| 失败与写入边界 | 文档约定 Draft/未决/缺口，但矩阵、backlog、model.yaml 没有同仓解析器和独立写保护。 |
| 当前骨架差距 | 已有基础资料与验收链；完整领域工件/范围/追溯种类需补。 |
| 目标任务 / 增强验收 | 1、2、3、5、7、8、12、14 / ENH-01、ENH-02、ENH-03、ENH-05、ENH-06、ENH-08、ENH-12、ENH-13 |
| 目标验收 | 两个 scope 的同号 fixture 可双向定位 owner、anchor、layer、缺口和对象基线。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-03：人工审阅、风险与治理记录

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:.github/ai-tool-config.yaml:1-120`；`ddd-subdomain:.github/PULL_REQUEST_TEMPLATE.md:1-64`；`ddd-subdomain:requirements/_governance-catalog.md:1-176`；`ddd-subdomain:domain-model/decisions/README.md:1-40`；`ddd-subdomain:docs/roles/README.md:36-45` |
| 原载体 | template/config |
| 输入 | 具名 reviewer、RC、GOV、ADR、PR 变化和 waiver 证据。 |
| 输出 | PR checklist、reviewed-by 约定、REQ/waiver、ADR/backlog 和风险文档。 |
| 前提 | 需要人工/RA/Architect 权责与外部 QMS/中心 ADR；配置仍有占位。 |
| 失败与写入边界 | hook 只匹配 reviewed-by 字符串，表单/waiver 无机器身份/批准验证；写入由 PR/Git 完成。 |
| 当前骨架差距 | 已有授权和不冒充审批约定；专门的工具资格/审阅记录未交付。 |
| 目标任务 / 增强验收 | 1、9、10、12、14 / ENH-01、ENH-09、ENH-10、ENH-12、ENH-14 |
| 目标验收 | 缺 reviewer、waiver approver 或 RC 来源的 fixture 产生定位发现；文本 Approved 不自动改状态。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-04：转录与文档的领域候选提取

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:.github/utilities/input_source_adapter.py:1-119`；`ddd-subdomain:.github/utilities/transcript_adapter.py:1-382`；`ddd-subdomain:.github/utilities/document_adapter.py:1-476`；`ddd-subdomain:.github/utilities/audio_transcriber.py:1-264`；`ddd-subdomain:.github/utilities/tests/test_p4_01_cardiac_imaging.py:1-254` |
| 原载体 | real executable |
| 输入 | 本地 txt/md、Markdown/DOCX、mp3/wav/m4a/flac；音频可选外部凭据。 |
| 输出 | ExtractedArtifact 列表含来源、类型、摘录、置信初值、澄清问题和近似行号。 |
| 前提 | 文件存在；DOCX/音频需要可选依赖；模块以 utilities 目录为 import 上下文。 |
| 失败与写入边界 | 缺文件/格式/依赖/凭据抛异常；音频会外调服务；适配器不写正式领域文件。 |
| 当前骨架差距 | 尚无文档/转录/音频提取及候选评分工具。 |
| 目标任务 / 增强验收 | 4、16 / ENH-03、ENH-04、ENH-08、ENH-12、ENH-14、ENH-16 |
| 目标验收 | 离线 fixture 产生稳定候选和源定位；低/中置信度只进 draft/BL，缺输入时不写源。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-05：Markdown 标题与占位符校验

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:.github/utilities/validate_artifact.py:1-274`；`ddd-subdomain:.vscode/tasks.json:1-44`；`ddd-subdomain:azure-pipelines.yml:51-66` |
| 原载体 | real executable |
| 输入 | 显式 Markdown 路径/目录，或默认 Git diff/staged 文件集合。 |
| 输出 | stdout 错误清单；当前 0=无文件/无发现，1=标题或占位符发现。 |
| 前提 | Python、可读仓库、默认模式可调用 git；Azure job 先提供 Python 3.11。 |
| 失败与写入边界 | 只读文件；未匹配规则跳过；默认基线尝试 origin/main、origin/master、main、master 后回退暂存区，空集合仍 0。 |
| 当前骨架差距 | 仅有制作 artifacts 的一次性检查，尚未分发正式 validator。 |
| 目标任务 / 增强验收 | 1、6、7、10、12 / ENH-01、ENH-07、ENH-08、ENH-10、ENH-13 |
| 目标验收 | 不存在的完整 base SHA 返回 input-error/2；正常、违规、空骨架分别报告 checked/excluded/object baseline。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-06：追溯矩阵图生成与交互查看

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:.github/utilities/graph_generator.py:1-436`；`ddd-subdomain:docs/artifact-graph.html:1-232`；`ddd-subdomain:traceability-matrix.md:1-66` |
| 原载体 | real executable |
| 输入 | 根目录 traceability-matrix.md 和可选 QMS 矩阵。 |
| 输出 | --json stdout JSON；默认写交互 Cytoscape HTML，可搜索上下游和 gap-only。 |
| 前提 | 矩阵含可识别 ID；浏览 HTML 需 Cytoscape CDN 或本地脚本。 |
| 失败与写入边界 | 无节点切换内置 demo；默认创建父目录写 HTML，--json 不写。 |
| 当前骨架差距 | 尚无来源驱动的交互/静态关系图导出工具。 |
| 目标任务 / 增强验收 | 7、17 / ENH-01、ENH-08、ENH-12、ENH-14、ENH-17 |
| 目标验收 | 同一 fixture 的 --json 稳定，空矩阵返回 empty 而不是 demo，节点/边能回指真实 artifact/anchor。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-07：AI 交互记录与 credits 估算

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:.github/utilities/log_interaction.py:1-332`；`ddd-subdomain:.github/ai-interaction-log.csv:1-12`；`ddd-subdomain:.github/ai-tool-config.yaml:65-120` |
| 原载体 | real executable |
| 输入 | 日期、PR、版本、模型、token、prompt、artifact 类型、reviewer 和备注。 |
| 输出 | 追加 CSV，或输出按模型/月汇总和单次 credits 估算。 |
| 前提 | 日志可写；模型价格表/硬编码 ID；可选读取个人绝对路径 models.json。 |
| 失败与写入边界 | 未知模型 credits=0；解析错误回默认；models.json 异常吞掉；不认证 reviewer/模型。 |
| 当前骨架差距 | 已有开发日志摘要；无专用交互/用量账本和核对统计。 |
| 目标任务 / 增强验收 | 9、18 / ENH-01、ENH-09、ENH-12、ENH-14、ENH-18 |
| 目标验收 | 合法记录可追加并保留字段；未知模型/非法输入明确报告而非静默零值；不写凭据。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-08：提交消息 reviewed-by hook 与安装

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:.github/hooks/commit-msg:36-96`；`ddd-subdomain:.github/hooks/install_hooks.py:21-63`；`ddd-subdomain:.github/ai-tool-config.yaml:44-63` |
| 原载体 | real executable |
| 输入 | Git 提交消息、暂存文件名和本机 .git/hooks 状态。 |
| 输出 | hook 以 0/1 放行或拒绝；安装器写 hook 和 Windows cmd 包装。 |
| 前提 | 手工运行 installer；目标是 Git 仓；Windows 需要 PATH 中 python，Unix 需要 symlink。 |
| 失败与写入边界 | 只拒绝受管路径缺 reviewed-by；merge/fixup/squash/--no-verify 可绕过；installer 覆盖/删除目标且无备份。 |
| 当前骨架差距 | 尚未交付可选 hook/installer；没有部署强制审阅门禁。 |
| 目标任务 / 增强验收 | 9、10 / ENH-09、ENH-10、ENH-14 |
| 目标验收 | 隔离 Git fixture 区分合法/非法 reviewed-by、非受管路径、空格路径和缺依赖；既有 hook 可恢复。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-09：Azure DevOps 领域资料 fan-out 管道

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:azure-pipelines.yml:28-222`；`ddd-subdomain:README.md:278-337`；`ddd-subdomain:.gitmodules:1-6` |
| 原载体 | real executable |
| 输入 | master push 的 model.yaml/.feature/Markdown 变化、repoUrl 和 System.AccessToken。 |
| 输出 | 克隆目标 BC、复制 feature、commit/push 和创建 ADO PR；按 BC 汇总失败。 |
| 前提 | Azure Ubuntu、Python/PyYAML、az CLI、token、目标权限和 repoUrl。 |
| 失败与写入边界 | 校验失败阻断；repoUrl 缺失/解析失败聚合；feature/model 查找可漏；成功路径写远端。 |
| 当前骨架差距 | 尚无 feature fan-out 或多目标更新提案/实际运行证据。 |
| 目标任务 / 增强验收 | 10、11、13 / ENH-01、ENH-06、ENH-10、ENH-11、ENH-12、ENH-13、ENH-14 |
| 目标验收 | 获授权隔离 ADO fixture 可验证对象、复制清单、失败聚合和 PR；无授权只出逐目标提案。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

### FRAMEWORK-10：管理摘要 PPT 生成

| 项目 | 来源观察 / 本地计划 |
|---|---|
| 来源定位 | `ddd-subdomain:.github/utilities/_gen_ppt.py:1-477`；`ddd-subdomain:TEMPLATE-CHANGELOG.md:1-56` |
| 原载体 | real executable |
| 输入 | 脚本内硬编码框架说明、颜色、页面内容和输出路径。 |
| 输出 | python-pptx 写出固定文件并打印路径。 |
| 前提 | python-pptx、可写 D:\CPWS\DomainModeling；无 CLI 参数。 |
| 失败与写入边界 | 缺依赖/目录/权限保存失败；写固定绝对路径，不改领域 Markdown。 |
| 当前骨架差距 | 尚无通用演示导出；不复制原一次性管理内容和固定输出路径。 |
| 目标任务 / 增强验收 | 17 / ENH-01、ENH-13、ENH-17 |
| 目标验收 | 若保留则参数化输出并记录输入基线；否则 distribution allowlist 明确排除。 |
| 本地实现状态 | 来源已核验；目标方法/工具按计划实现与验证，未计为功能完成 |

## 7. 上游提案和未解析能力

| ID | 名称 | 来源状态 | 定位 |
|---|---|---|---|
| FRAMEWORK-11 | 路线图 gap detector 与自动修复编排 | proposed-upstream | `ddd-subdomain:_roadmap/02-execution-engine.md:1-309`；`ddd-subdomain:.github/utilities/validate_artifact.py:31-274` |
| FRAMEWORK-12 | 路线图 CLI、迁移和 tiered profiles | proposed-upstream | `ddd-subdomain:_roadmap/01-ddd-abstraction.md:1-130`；`ddd-subdomain:_roadmap/03-scaffolding-automation.md:1-283`；`ddd-subdomain:_roadmap/05-tiered-profiles.md:1-179` |
| FRAMEWORK-13 | 路线图 GHE CODEOWNERS、Ruleset 与 Knowledge Base | proposed-upstream | `ddd-subdomain:_roadmap/04-ghe-native-integration.md:1-150`；`ddd-subdomain:.github/PULL_REQUEST_TEMPLATE.md:1-64`；`ddd-subdomain:.github/ai-tool-config.yaml:44-63` |
| FRAMEWORK-14 | 路线图真实图谱与 PR 影响触发 | proposed-upstream | `ddd-subdomain:_roadmap/07-graph-generator.md:1-175`；`ddd-subdomain:_roadmap/08-impact-assessment-trigger.md:1-183`；`ddd-subdomain:.github/utilities/graph_generator.py:73-436` |
| FRAMEWORK-15 | 路线图 Web 查询与 @tantu 扩展 | proposed-upstream | `ddd-subdomain:_roadmap/06-web-surface.md:1-160`；`ddd-subdomain:docs/concepts/three-repos.md:1-120` |
| FRAMEWORK-16 | 路线图代码/SQL 反向适配与完整置信流水线 | proposed-upstream | `ddd-subdomain:_roadmap/P4-01-reverse-engineering.md:1-265`；`ddd-subdomain:.github/utilities/confidence_scorer.py:55-335`；`ddd-subdomain:.github/utilities/tests/test_p4_01_cardiac_imaging.py:109-254` |
| FRAMEWORK-17 | 固定版本 prompt/template 依赖 | unverified | `ddd-subdomain:.gitmodules:1-6`；`ddd-subdomain:.github/prompts:metadata-only`；`ddd-subdomain:_templates:metadata-only` |

## 8. 逐文件、目录与 gitlink 清单

各仓完整版本/来源见第 5 节；路径相对该仓根。object ID 用短前缀导航，完整值保留在原 Git 树和本机 manifest。目录/gitlink 的 metadata-only 不伪装成全文阅读。

### ddd-bc

| 原仓路径 | 类型 / object | 分类 / 来源状态 | 读取覆盖 | 能力 | 概括 |
|---|---|---|---|---|---|
| `.github` | tree / `44a7da3823a7` | directory / observed-current | metadata-only | BC-02、BC-13 | GitHub 配置目录，承载仓库级指令与共享入口。 |
| `.github/copilot-instructions.md` | blob / `6ac1e555d9c9` | guide / observed-current | full | BC-02、BC-03、BC-07、BC-12、BC-14 | 定义底层 V 工件边界、派生顺序、模板创建、只读领域源和风险/ADR 规则。 |
| `.github/instructions` | tree / `966c17cc6382` | directory / observed-current | metadata-only | BC-13 | 按路径匹配的实现、架构、安全、编码和测试规则目录。 |
| `.github/instructions/architecture.instructions.md` | blob / `3ca998d6d973` | guide / observed-current | full | BC-05、BC-07、BC-13 | 规定四层依赖方向、接口边界、云原生端点、可观测性和容器要求。 |
| `.github/instructions/coding-standards.instructions.md` | blob / `c908a81f9ce0` | guide / observed-current | full | BC-07、BC-13 | 规定命名、函数职责、错误处理、领域模式、依赖和静态质量约束。 |
| `.github/instructions/implementation.instructions.md` | blob / `a41bb9ef48e8` | guide / observed-current | full | BC-02、BC-03、BC-04、BC-05、BC-06 | 要求先读配置和领域源，按 SR/US/VT 追溯生成实现，禁止越界补造。 |
| `.github/instructions/security.instructions.md` | blob / `484d2d22912f` | guide / observed-current | full | BC-13 | 提供秘密、输入、认证授权、密码学、依赖供应链和日志泄露的安全护栏。 |
| `.github/instructions/testing.instructions.md` | blob / `defd20e25d74` | guide / observed-current | full | BC-06、BC-13 | 定义单元/集成/E2E 分层、覆盖率、AAA、确定性、风险控制和 CI 质量门槛。 |
| `.github/prompts` | commit / `08f8219397d6` | gitlink / observed-current | metadata-only | BC-03、BC-04、BC-05、BC-06、BC-07、BC-08、BC-09、BC-10、BC-11、BC-12 | 固定指向共享 prompt 仓，实际内容由同组固定 commit 单独盘点。 |
| `.gitignore` | blob / `e7b3cae321d1` | marker / observed-current | full | BC-01 | 忽略虚拟环境、演示文档和 src 目录，体现模板仓的分发边界。 |
| `.gitmodules` | blob / `030c87cb0b73` | config / observed-current | full | BC-01、BC-10 | 登记 prompts 与 templates 两个相对 URL 子模块，未登记真实 domain-model 子模块。 |
| `CONCEPTS.md` | blob / `6637d3a2f537` | guide / observed-current | full | BC-02、BC-03、BC-08、BC-12、BC-13 | 解释 V 模型、四类工件、追溯链、领域只读规则、风险链及 prompt 交互模式。 |
| `README.md` | blob / `3470b9929c12` | guide / instance-only | full | BC-01、BC-02、BC-03、BC-10 | 提供实例化后的快速开始、步骤表、目录、角色归属和 prompt 导航；当前仍是占位 BC。 |
| `TEMPLATE-CHANGELOG.md` | blob / `a011bbdfa437` | roadmap / proposed-upstream | full | BC-14 | 记录模板版本的结构性演进及未发布 skill 变更，不能当作运行时自动化。 |
| `_templates` | commit / `00705aef6c70` | gitlink / observed-current | metadata-only | BC-02、BC-14 | 固定指向实现侧表单仓，实际模板内容由同组固定 commit 单独盘点。 |
| `architecture` | tree / `2d458f3aa2f3` | directory / observed-current | metadata-only | BC-05、BC-11 | 架构工件目录，承载 ABB、ADR 引用和后续序列图。 |
| `architecture/README.md` | blob / `908a39672f8e` | guide / instance-only | full | BC-05、BC-14 | 说明 ABB 类型、创建入口、ADR 要求和索引；实例索引仍为空。 |
| `architecture/_abb-template.md` | blob / `4788a5d49b9b` | template / observed-current | full | BC-05、BC-14 | 提供带 ADR、QAS、接口、依赖版本、部署和可观测性的 ABB 表单。 |
| `architecture/adr-references.md` | blob / `36bc737d91f5` | config / instance-only | full | BC-05 | 登记中央架构 wiki 的 ADR 及尚待决定的架构事项；当前只有占位行。 |
| `backlog.md` | blob / `f8f3f8df1af1` | roadmap / instance-only | full | BC-08、BC-09 | 定义 BL-NNN 开放/关闭事项、类别和依赖记录；实例当前只有替换占位项。 |
| `bc-config.yaml` | blob / `a83e4f116f21` | config / instance-only | full | BC-01、BC-12 | 定义 BC、子域、领域仓、上下文路径、实现仓、语言和框架字段；全部仍为占位值。 |
| `domain-model` | tree / `ca31f8ccafe5` | directory / instance-only | metadata-only | BC-01、BC-03、BC-07、BC-10、BC-12 | 领域源挂载点目录；此快照仍是占位目录，不是已解析的跨仓 gitlink。 |
| `domain-model/README.md` | blob / `01368bb9497e` | guide / instance-only | full | BC-01、BC-10 | 说明领域子模块的初始化、只读边界和预期目录；未提供实际 UC/INV 内容。 |
| `software-requirements` | tree / `5b63ecad5556` | directory / observed-current | metadata-only | BC-02、BC-03 | 软件需求目录及其底层 V 工件落点。 |
| `software-requirements/README.md` | blob / `374ceacaf934` | guide / instance-only | full | BC-02、BC-03 | 规定 SR 的来源、可测性、命名、索引和追溯要求；实例索引为空。 |
| `tools` | tree / `f9c07fc66516` | directory / observed-current | metadata-only | BC-01 | 维护脚本目录，当前只有领域子模块安装脚本。 |
| `tools/setup-domain-model-submodule.ps1` | blob / `30e186a5a284` | utility / observed-current | full | BC-01、BC-10 | 真实 PowerShell 安装器：检查根目录、移除占位、添加领域子模块、禁用递归并提交变更。 |
| `traceability-matrix.md` | blob / `a9fe9f9607b9` | guide / instance-only | full | BC-02、BC-08 | 提供 REQ/UC/INV/SR/US/ABB/VT/RC 的矩阵列、覆盖统计和开放缺口区。 |
| `user-stories` | tree / `49e70aeb562b` | directory / observed-current | metadata-only | BC-02、BC-04 | 用户故事目录及底层 V 交付切片落点。 |
| `user-stories/README.md` | blob / `73583abee064` | guide / instance-only | full | BC-02、BC-04 | 规定 US 必须由已批准 SR 派生、按价值切片及进入矩阵；实例索引为空。 |
| `verification` | tree / `7508315d2b39` | directory / observed-current | metadata-only | BC-02、BC-06 | 验证规格目录，承载 VT 文档和后续实现测试引用。 |
| `verification/README.md` | blob / `ba7ebe1d55b8` | guide / instance-only | full | BC-02、BC-06 | 定义 VT 规格与验证代码的边界、三类测试、安全关键标记和索引字段。 |

### ddd-bc-prompts

| 原仓路径 | 类型 / object | 分类 / 来源状态 | 读取覆盖 | 能力 | 概括 |
|---|---|---|---|---|---|
| `abb-design.prompt.md` | blob / `ef8716372ff9` | prompt / observed-current | full | BC-05、BC-12 | 交互式从批准 US、能力、QAS 和 context map 设计 ABB，并要求 ADR、版本和模型摘要。 |
| `backlog-review.prompt.md` | blob / `42722b07142b` | prompt / observed-current | full | BC-08 | 自治扫描 backlog 与工件，关闭已解决项、识别陈旧项和新增追溯/风险缺口。 |
| `code-generation.prompt.md` | blob / `2dc9aef4dff7` | prompt / observed-current | full | BC-07、BC-12 | 交互式生成四层 DDD 源代码，检查语言/框架/批准 US/ABB，非空文件冲突则停写。 |
| `impact-assessment.prompt.md` | blob / `d21da381d51e` | prompt / observed-current | full | BC-09 | 针对 REQ/UC/INV 变化追踪直接/间接影响、风险链和需确认的状态回退。 |
| `onboarding.prompt.md` | blob / `92cc23dac911` | prompt / observed-current | full | BC-10 | 逐步收集实例配置并引导从领域模型到 SR/US/ABB/VT 的阅读顺序；保持只读讲解。 |
| `query.prompt.md` | blob / `e22ccfd09a33` | prompt / observed-current | full | BC-08 | 只读按 ID、追溯链、缺口、安全链、覆盖统计或 ABB 查询工件并被动报告缺口。 |
| `review.prompt.md` | blob / `cb36a31fb402` | prompt / observed-current | full | BC-08、BC-13 | 自治检查追溯完整性、RC 安全链、SR/US/ABB/VT 质量和 backlog 健康度，仅报告不写入。 |
| `sequence-diagram.prompt.md` | blob / `3eacf30ae706` | prompt / observed-current | full | BC-11、BC-12 | 根据 UC/ABB/事件/集成关系生成 Mermaid 正反路径序列图并更新 sequenceSummary。 |
| `skills` | tree / `86dcb726abc6` | directory / observed-current | metadata-only | BC-03、BC-12 | 共享 Agent skill 目录。 |
| `skills/bc-implementation` | tree / `7ba065dbd84c` | directory / observed-current | metadata-only | BC-03、BC-12 | BC 实施技能目录，包含唯一 SKILL.md。 |
| `skills/bc-implementation/SKILL.md` | blob / `ebc3bc2babfa` | skill / observed-current | full | BC-03、BC-04、BC-05、BC-06、BC-07、BC-08、BC-09、BC-10、BC-12 | 集中规定领域先读、只读子模块、提案确认、状态、追溯链、四层架构和 model.yaml 更新。 |
| `sr-derivation.prompt.md` | blob / `54a6457a94d3` | prompt / observed-current | full | BC-03、BC-12 | 按批准 REQ/UC/INV 逐路径起草可测 SR，更新矩阵和 srSummary，并对变更做回退保护。 |
| `story-derivation.prompt.md` | blob / `98c2330486b8` | prompt / observed-current | full | BC-04、BC-12 | 从批准 SR 和 UC actor 切分可交付 US，覆盖正/替代/不变量 AC，并更新 storySummary。 |
| `traceability-build.prompt.md` | blob / `a058e3b244d7` | prompt / observed-current | full | BC-08、BC-12 | 从领域与底层工件重建矩阵、统计覆盖、登记空白和断链，并可追加 backlog 缺口。 |
| `verification-test.prompt.md` | blob / `522a30b2857c` | prompt / observed-current | full | BC-06、BC-12 | 从 US/SR/INV/ABB 生成 VT Markdown 与 Gherkin 两件套，区分单元/集成/E2E 和安全关键项。 |

### ddd-bc-templates

| 原仓路径 | 类型 / object | 分类 / 来源状态 | 读取覆盖 | 能力 | 概括 |
|---|---|---|---|---|---|
| `items` | tree / `032f2d86e544` | directory / observed-current | metadata-only | BC-02、BC-14 | 实现侧工件条目表单目录。 |
| `items/abb.md` | blob / `0ee1674c9824` | template / observed-current | full | BC-05、BC-14 | ABB 条目表单，含 ADR、QAS、接口、依赖版本、部署和观测字段。 |
| `items/sequence-diagram.md` | blob / `14f450de19ea` | template / observed-current | full | BC-11、BC-14 | 序列图表单，固定参与者、成功/错误 Mermaid 场景和未决项说明。 |
| `items/sr.md` | blob / `4a0cbea15a5f` | template / observed-current | full | BC-03、BC-14 | SR 表单，含 REQ/UC/INV/RC 元数据、可测 AC、范围和验证方法。 |
| `items/user-story.md` | blob / `7e7985e57abd` | template / observed-current | full | BC-04、BC-14 | US 表单，固定 actor/价值叙述、正替代路径、强制不变量 AC 和 DoD。 |
| `items/verification-test.feature` | blob / `b219c3e7efb5` | template / observed-current | full | BC-06、BC-14 | VT Gherkin 表单，规定标签、背景、成功路径、不变量负例和参数化示例。 |
| `items/verification-test.md` | blob / `a629fa3dfc66` | template / observed-current | full | BC-06、BC-14 | VT 规格表单，固定类型、US/SR/AC、安全标记、测试文件和状态字段。 |
| `software-requirements` | tree / `5c14cdbcccb9` | directory / observed-current | metadata-only | BC-03、BC-14 | 软件需求专用表单目录。 |
| `software-requirements/_template.md` | blob / `0c30173a2534` | template / observed-current | full | BC-03、BC-14 | 软件需求目录表单，补充 SR 的可观察陈述、范围和验证方法。 |
| `user-stories` | tree / `d063b5c1015d` | directory / observed-current | metadata-only | BC-04、BC-14 | 用户故事专用表单目录。 |
| `user-stories/_template.md` | blob / `232603adf6ed` | template / observed-current | full | BC-04、BC-14 | 用户故事目录表单，固定 actor/需求/价值、强制 AC、DoD 和 PR 检查。 |
| `verification` | tree / `9ae6ee3ebc81` | directory / observed-current | metadata-only | BC-06、BC-14 | 按 E2E、集成、单元拆分的验证表单目录。 |
| `verification/e2e-test-spec.md` | blob / `497a75ac5b3f` | template / observed-current | full | BC-06、BC-14 | E2E 规格表单，固定端到端边界、环境、旅程、外部结果和负例。 |
| `verification/integration-test-spec.md` | blob / `3e8c9b3d852e` | template / observed-current | full | BC-06、BC-14 | 集成规格表单，固定两个组件边界、真实基础设施、刺激、断言和清理。 |
| `verification/unit-test-spec.md` | blob / `7248b40d4e0f` | template / observed-current | full | BC-06、BC-14 | 单元规格表单，固定单一行为、无基础设施前提、可观察断言和测试框架字段。 |

### ddd-subdomain-prompts

| 原仓路径 | 类型 / object | 分类 / 来源状态 | 读取覆盖 | 能力 | 概括 |
|---|---|---|---|---|---|
| `adr.prompt.md` | blob / `28664bca680e` | prompt / observed-current | full | DOMAIN-06 | ADR 新建与外来 ADR 影响评估；收集决策、影响、确认和 BL 跟踪。 |
| `backlog-review.prompt.md` | blob / `a84d75b3c6c1` | prompt / observed-current | full | DOMAIN-09 | 扫描开放问题、占位符、一致性和追溯缺口，维护 backlog 并报告剩余项。 |
| `distillation.prompt.md` | blob / `df64853e619b` | prompt / observed-current | full | DOMAIN-03 | 让领域专家复核语言、概念、边界、突破和模型-代码漂移。 |
| `elicitation.prompt.md` | blob / `38fdba38f8ae` | prompt / observed-current | full | DOMAIN-02、DOMAIN-16、DOMAIN-20 | 以 Intended Use 为前置，访谈子域、BC、词汇、UC、BR 和 INV。 |
| `glossary-sync.prompt.md` | blob / `c61f774486e7` | prompt / observed-current | full | DOMAIN-10 | 比较内外部 glossary，分类对齐/分歧并在批准后改本地术语。 |
| `impact-assessment.prompt.md` | blob / `f131fe25e563` | prompt / observed-current | full | DOMAIN-07 | 沿 REQ-CAP-UC-INV-TS 链分析 REQ 变更影响，先报告后编辑。 |
| `intended-use-amendment.prompt.md` | blob / `af7415c9c8e1` | prompt / observed-current | full | DOMAIN-08、DOMAIN-20 | 对 Intended Use、约束和安全分类变更做监管分级、风险再分析和升级。 |
| `onboarding.prompt.md` | blob / `47c2b32b148d` | prompt / observed-current | full | DOMAIN-01、DOMAIN-16、DOMAIN-20 | 按角色和顺序导览 Intended Use、模型、需求、追溯、稳定区和开放区。 |
| `published-interface.prompt.md` | blob / `271d1a81d886` | prompt / observed-current | full | DOMAIN-11、DOMAIN-18 | 处理接口发布、消费者、弃用、版本、破坏性分类和变更通知。 |
| `query.prompt.md` | blob / `6cb6ca8df6ac` | prompt / observed-current | full | DOMAIN-12 | 按对象类型和范围只读列出、过滤或汇总模型对象。 |
| `requirements-capture.prompt.md` | blob / `aac2c2664eff` | prompt / observed-current | full | DOMAIN-05、DOMAIN-14 | 捕获 REQ/QAS，检查治理、自动派生、质量特征、UC 链接和矩阵。 |
| `reverse-engineering.prompt.md` | blob / `aa68b5e57fd9` | prompt / observed-current | full | DOMAIN-04、DOMAIN-14 | 从 ADO Epic/Feature/Story/Test Case 反向产生 Draft 对象、置信度报告和 BL。 |
| `review.prompt.md` | blob / `bd5492456f21` | prompt / observed-current | full | DOMAIN-03、DOMAIN-09、DOMAIN-20 | 按 Intended Use、聚合、INV、职责、事件、UC、跨上下文、词汇和 QAS 审阅。 |
| `skills` | tree / `a6c3ae3939f9` | directory / observed-current | metadata-only | DOMAIN-01 | 目录：domain-modeling 技能入口。 |
| `skills/domain-modeling` | tree / `fcec52d9939d` | directory / observed-current | metadata-only | DOMAIN-01、DOMAIN-16 | 目录：统一领域建模技能正文。 |
| `skills/domain-modeling/SKILL.md` | blob / `b0f71eaf999a` | skill / observed-current | full | DOMAIN-01、DOMAIN-16、DOMAIN-20 | 统一技能定义 guardrails、追溯链、状态规则和 prompt 路由。 |
| `swas.prompt.md` | blob / `cf85ba3b58ff` | prompt / observed-current | full | DOMAIN-15、DOMAIN-19 | 以模型、需求、ABB、风险和验证桥接编制 SWAS，缺资料留占位。 |
| `test-scenario.prompt.md` | blob / `78d269efab2e` | prompt / observed-current | full | DOMAIN-13、DOMAIN-14 | 从已批准 UC/INV/REQ/QAS 生成 BC、跨 BC、验收和 QAS 场景。 |
| `traceability-build.prompt.md` | blob / `8ad1242cedef` | prompt / observed-current | full | DOMAIN-14、DOMAIN-19 | 从 REQ/CAP/UC/INV/TS 和桥接数据构建矩阵、缺口、孤儿和 QMS 风险表。 |

### ddd-subdomain-templates

| 原仓路径 | 类型 / object | 分类 / 来源状态 | 读取覆盖 | 能力 | 概括 |
|---|---|---|---|---|---|
| `context` | tree / `2169baf36a9c` | directory / observed-current | metadata-only | DOMAIN-16、DOMAIN-19 | 目录：bounded context 模板根。 |
| `context/README.md` | blob / `2eacba8ea2a6` | guide / observed-current | full | DOMAIN-16 | BC 入口和边界→核心模型→细节阶段清单，含 release unit/open questions。 |
| `context/aggregates` | tree / `1e23c06e961a` | directory / observed-current | metadata-only | DOMAIN-17 | 目录：聚合根文件容器。 |
| `context/aggregates/README.md` | blob / `b5292947b58a` | guide / observed-current | full | DOMAIN-17 | 聚合目录与一致性边界检查，要求根、生命周期、原子保存和 ID 引用。 |
| `context/capabilities.md` | blob / `5f92f4c3642c` | template / observed-current | full | DOMAIN-16 | CAP 目录/详情，要求聚合多个 REQ、关联 UC、依赖、扩展点、发布单元和状态。 |
| `context/domain-events` | tree / `a5492ec626a0` | directory / observed-current | metadata-only | DOMAIN-17 | 目录：领域事件文件容器。 |
| `context/domain-events/README.md` | blob / `701a46afe6f1` | guide / observed-current | full | DOMAIN-17 | 领域事件设计入口：过去式业务事实、来源聚合、消费者和数据边界。 |
| `context/domain-events/catalog.md` | blob / `06dc1c661387` | template / observed-current | full | DOMAIN-17、DOMAIN-18 | 发布/消费/废弃事件库存，记录来源、反应、ACL、版本和 sunset。 |
| `context/entities` | tree / `240586966865` | directory / observed-current | metadata-only | DOMAIN-17 | 目录：非根实体文件容器。 |
| `context/entities/README.md` | blob / `f8a4be0755c3` | guide / observed-current | full | DOMAIN-17 | 非根实体目录及 Entity/Value Object/Aggregate Root 判定表。 |
| `context/integration` | tree / `626f89a86f5a` | directory / observed-current | metadata-only | DOMAIN-18 | 目录：上下文集成伙伴文件容器。 |
| `context/integration/README.md` | blob / `e442c86bf94f` | guide / observed-current | full | DOMAIN-18 | 消费者/生产者伙伴契约，覆盖 ACL/OHS、版本、失败处理和通知。 |
| `context/invariants.md` | blob / `1c185f209b7b` | template / observed-current | full | DOMAIN-16、DOMAIN-17、DOMAIN-20 | 区分外部前置与本上下文 INV，关联 BR/RC、scope、执行者、测试和状态。 |
| `context/model.yaml` | blob / `a302efb7b9f1` | config / observed-current | full | DOMAIN-19 | 机器快照：release unit、领域对象、事件/策略及 ABB/sequence/SR/US/VT/governance/risk/release 桥接。 |
| `context/policies` | tree / `d00e1e806c53` | directory / observed-current | metadata-only | DOMAIN-17 | 目录：策略文件容器。 |
| `context/policies/README.md` | blob / `5a4db54ee725` | guide / observed-current | full | DOMAIN-17 | 反应式策略说明与检查清单，要求事件触发、业务动作和 model.yaml 同步。 |
| `context/policies/catalog.md` | blob / `1e53b1a9d851` | template / observed-current | full | DOMAIN-17 | 策略库存，含触发、动作、BR、状态、退休和单触发器约束。 |
| `context/purpose.md` | blob / `4c0d62ef209a` | template / observed-current | full | DOMAIN-16、DOMAIN-20 | BC 核心责任、唯一拥有/明确不拥有的概念、参与者和实现属性。 |
| `context/services` | tree / `e060c4cc9969` | directory / observed-current | metadata-only | DOMAIN-17 | 目录：领域服务文件容器。 |
| `context/services/README.md` | blob / `cf33f983642a` | guide / observed-current | full | DOMAIN-17 | 领域服务目录及适用边界：跨聚合可用，编排/集成不放这里。 |
| `context/use-cases.md` | blob / `67938a11800c` | template / observed-current | full | DOMAIN-16、DOMAIN-17 | UC 目录/详情记录 Actor、Trigger、Outcome、REQ、流程、事件、BR 和状态。 |
| `context/value-objects` | tree / `253d73e8509b` | directory / observed-current | metadata-only | DOMAIN-17 | 目录：值对象文件容器。 |
| `context/value-objects/README.md` | blob / `4b928a7b579f` | guide / observed-current | full | DOMAIN-17 | 值对象目录和不可变、无身份、自校验、无副作用检查清单。 |
| `items` | tree / `4aeac975a32e` | directory / observed-current | metadata-only | DOMAIN-06、DOMAIN-17 | 目录：单项领域工件表单容器。 |
| `items/adr.md` | blob / `cf6ea44f52f7` | template / observed-current | full | DOMAIN-06 | ADR 表单：问题、范围、驱动、选项、结论、利弊、治理和链接。 |
| `items/aggregate.md` | blob / `d8b078214c98` | template / observed-current | full | DOMAIN-17 | 聚合表单：身份、根、组成、Factory、规则、状态、事件、仓储、边界理由和演化。 |
| `items/capability.md` | blob / `4239f438885f` | template / observed-current | full | DOMAIN-16 | 单 CAP 详情：目的、REQ、UC、能力依赖、扩展点、发布单元和 BL。 |
| `items/domain-event.md` | blob / `6caf281cfd9d` | template / observed-current | full | DOMAIN-17、DOMAIN-18 | 事件表单：事实、触发、schema、消费者、幂等、版本和样例载荷。 |
| `items/domain-service.md` | blob / `6f805662cacc` | template / observed-current | full | DOMAIN-17 | 无状态领域服务：归属理由、操作、纯领域依赖、规则、事件和演化。 |
| `items/entity.md` | blob / `ae3438ba38d7` | template / observed-current | full | DOMAIN-17 | 实体表单：身份、聚合归属、属性、生命周期、规则、关系和演化。 |
| `items/factory.md` | blob / `11992950a32c` | template / observed-current | full | DOMAIN-17 | Factory 表单：创建理由、前置、不变式、输入、事件、位置和 BL。 |
| `items/integration-partner.md` | blob / `84c6d7ecab57` | template / observed-current | full | DOMAIN-18 | 伙伴集成表单：方向、模式、接收/发布、ACL、版本、失败处理和开放问题。 |
| `items/policy.md` | blob / `09c1be20feef` | template / observed-current | full | DOMAIN-17 | 策略表单以 when-event/then-action 表达规则，并记 guard、effect、冲突和边界。 |
| `items/value-object.md` | blob / `03423e216fe6` | template / observed-current | full | DOMAIN-17 | 值对象表单：属性约束、构造校验、相等、不可变、行为、样例和演化。 |
| `qms-traceability-matrix.md` | blob / `39a38ac71611` | template / observed-current | full | DOMAIN-14、DOMAIN-19 | QMS forward/risk 追溯表，把 REQ/SR/ABB/VT 与 RISK/RC 分开统计缺口和阻塞。 |
| `requirements` | tree / `7aadc567614c` | directory / observed-current | metadata-only | DOMAIN-05 | 目录：REQ/QAS 表单容器。 |
| `requirements/_template-qas.md` | blob / `da42e352bc77` | template / observed-current | full | DOMAIN-05、DOMAIN-14 | ATAM QAS 表单：可测响应、验收、领域影响、追溯、限制、风险和问题。 |
| `requirements/_template.md` | blob / `9ef10c5db817` | template / observed-current | full | DOMAIN-05、DOMAIN-14 | REQ 表单：身份、问题/结果、AC/范围、领域影响、追溯、质量检查和状态日志。 |
| `scenarios` | tree / `14d1b891f3e5` | directory / observed-current | metadata-only | DOMAIN-13 | 目录：领域、验收和跨 BC 场景容器。 |
| `scenarios/acceptance-test.feature` | blob / `37a2d930fa6b` | template / observed-current | full | DOMAIN-13 | REQ 验收 Gherkin：标签、背景、AC 场景和边界拒绝场景。 |
| `scenarios/acceptance-test.md` | blob / `97aa087a29f9` | template / observed-current | full | DOMAIN-13、DOMAIN-14 | 验收元数据：REQ/UC/QAS/BC、状态、范围和配套 feature 链接。 |
| `scenarios/cross-bc-scenario.feature` | blob / `5282a0802591` | template / observed-current | full | DOMAIN-13 | 跨 BC Gherkin：上下文、组件场景、前置条件和端到端结果。 |
| `scenarios/cross-bc-scenario.md` | blob / `e784f21e71c6` | template / observed-current | full | DOMAIN-13、DOMAIN-14 | 跨 BC 元数据：参与 BC、组件场景、E2E 仓库、接口、事件和状态。 |
| `scenarios/domain-scenario.feature` | blob / `072ef1daa2c1` | template / observed-current | full | DOMAIN-13 | BC 领域 Gherkin：happy/alternate/negative 路径、UC/REQ 标签和 INV 违规例。 |
| `scenarios/domain-scenario.md` | blob / `56bb0255c982` | template / observed-current | full | DOMAIN-13、DOMAIN-14 | 领域场景元数据：UC/REQ/INV/BR/QAS 和 Gherkin/负载/混沌/安全验证方法。 |
| `subdomain` | tree / `925a0a9b8cfc` | directory / observed-current | metadata-only | DOMAIN-16、DOMAIN-20 | 目录：子域级模板根。 |
| `subdomain/architecture-spec` | tree / `f0affa94f8c1` | directory / observed-current | metadata-only | DOMAIN-15 | 目录：子域 SWAS 及构建资源。 |
| `subdomain/architecture-spec/.order` | blob / `660756da304c` | marker / observed-current | full | DOMAIN-15 | 保留 SWAS 文档生成顺序的标记文件。 |
| `subdomain/architecture-spec/AS-[SubdomainName].md` | blob / `cc5f25ae3155` | template / observed-current | full | DOMAIN-15 | QMS SWAS 骨架：目标、约束、上下文、构建、运行、部署、数据、威胁、验证、质量和安全。 |
| `subdomain/architecture-spec/diagrams` | tree / `d564d0bc3dd9` | directory / observed-current | metadata-only | DOMAIN-15 | 目录：SWAS 图示资源容器。 |
| `subdomain/architecture-spec/diagrams/.gitkeep` | blob / `e69de29bb2d1` | marker / observed-current | full | DOMAIN-15 | 空标记，保留 SWAS 图示目录。 |
| `subdomain/architecture-spec/metadata.json` | blob / `60cf832ae540` | config / observed-current | full | DOMAIN-15 | PDF 封面、页眉页脚、版本日期和免责声明配置。 |
| `subdomain/architecture-spec/pipelines` | tree / `45f593209917` | directory / observed-current | metadata-only | DOMAIN-15 | 目录：SWAS PDF pipeline 容器。 |
| `subdomain/architecture-spec/pipelines/generate-pdf.yml` | blob / `74a9b14b3e4f` | pipeline / observed-current | full | DOMAIN-15 | Azure pipeline 在 master 触发外部 markdown-to-qmspdf 容器并发布 PDF。 |
| `subdomain/contexts` | tree / `c3d297fc0d5d` | directory / observed-current | metadata-only | DOMAIN-16 | 目录：子域 bounded context 容器。 |
| `subdomain/contexts/README.md` | blob / `f8d583455696` | guide / observed-current | full | DOMAIN-16 | 说明由 prompt 创建 BC、命名、责任归属、边界文件顺序和目录维护。 |
| `subdomain/glossary` | tree / `f1f834a36265` | directory / observed-current | metadata-only | DOMAIN-10、DOMAIN-20 | 目录：子域词汇和业务规则容器。 |
| `subdomain/glossary/business-rules.md` | blob / `c0f08cdb56cc` | template / observed-current | full | DOMAIN-16、DOMAIN-20 | 子域 BR 表单：跨/单上下文规则、来源、执行者、INV 索引和变更日志。 |
| `subdomain/glossary/ubiquitous-language.md` | blob / `9da68a21d025` | template / observed-current | full | DOMAIN-10、DOMAIN-20 | 子域词汇表：术语、上下文、歧义、弃用词和命名约定。 |
| `subdomain/intended-use.md` | blob / `e5262ecbe1d9` | template / observed-current | full | DOMAIN-08、DOMAIN-20 | 监管/临床锚点：目的、使用、患者/用户、运行原理、误用、批准和演化。 |
| `subdomain/published-interface.md` | blob / `6ee93e00702a` | template / observed-current | full | DOMAIN-11、DOMAIN-18 | 对外接口合同：身份、语言、模型、事件、服务、版本/通知、消费者和问题。 |
| `subdomain/strategic` | tree / `8f43f0142140` | directory / observed-current | metadata-only | DOMAIN-18、DOMAIN-20 | 目录：战略 BC/context-map 容器。 |
| `subdomain/strategic/bounded-contexts.md` | blob / `787c97f0ecf3` | template / observed-current | full | DOMAIN-16、DOMAIN-20 | BC 清单：release unit、责任团队、状态、Core/Supporting/Generic 指引和健康摘要。 |
| `subdomain/strategic/context-map.md` | blob / `bb49057fb40e` | template / observed-current | full | DOMAIN-18、DOMAIN-20 | 上下文关系：方向、模式、合同、翻译、SDK、共享内核、Separate Ways 和问题。 |
| `subdomain/subdomain-definition.md` | blob / `4cd65bd7079f` | template / observed-current | full | DOMAIN-16、DOMAIN-18、DOMAIN-20 | 子域总表：Intended Use、安全/环境、愿景、分类、责任、BC、Core、接口、依赖和事件。 |

### ddd-subdomain

| 原仓路径 | 类型 / object | 分类 / 来源状态 | 读取覆盖 | 能力 | 概括 |
|---|---|---|---|---|---|
| `.github` | tree / `e869d7b509b8` | directory / observed-current | metadata-only | FRAMEWORK-01、FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `.github/PULL_REQUEST_TEMPLATE.md` | blob / `861e8c554efc` | template / observed-current | full | FRAMEWORK-03 | PR 表单收集摘要、工件类型、AI 审阅、追溯和检查项；勾选项本身不执行验证。 |
| `.github/ai-interaction-log.csv` | blob / `64d48d1bb34c` | marker / instance-only | full | FRAMEWORK-07 | AI 交互日志只有固定字段与注释，快照中没有实际记录行。 |
| `.github/ai-tool-config.yaml` | blob / `e195376c34c6` | config / observed-current | full | FRAMEWORK-03、FRAMEWORK-07、FRAMEWORK-08 | 声明 Copilot 工具角色、人工审阅、hook、校验、日志和计费控制；状态仍未资格化并含占位。 |
| `.github/copilot-instructions.md` | blob / `20cc440dd753` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 工作区 Agent 指引列出建模步骤、工件边界、追溯、角色、模板和外部仓边界；属于提示规则。 |
| `.github/hooks` | tree / `9345216b4efc` | directory / observed-current | metadata-only | FRAMEWORK-08 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `.github/hooks/commit-msg` | blob / `29aa48a03af8` | hook / observed-current | full | FRAMEWORK-08 | 提交消息 hook 对受管路径要求 reviewed-by，并跳过 merge/fixup/squash。 |
| `.github/hooks/install_hooks.py` | blob / `df359c1bd8c6` | hook / observed-current | full | FRAMEWORK-08 | 安装器在 Windows 复制 hook/生成 cmd，在 Unix 删除旧目标后建 symlink；无冲突备份。 |
| `.github/instructions` | tree / `078d68bcba4e` | directory / observed-current | metadata-only | FRAMEWORK-01、FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `.github/instructions/architecture.instructions.md` | blob / `835e5cbabef4` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-03 | 架构规则要求分层依赖、ADR、可测 QAS、健康检查、外部化配置和 SWAS/model.yaml 一致。 |
| `.github/instructions/domain-model.instructions.md` | blob / `4215b4ac61dc` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 领域模型规则定义目录、命名、追溯、invariant 责任、RC 引用和结构变更确认闸门。 |
| `.github/prompts` | commit / `d7da752b7312` | gitlink / unverified | metadata-only | FRAMEWORK-17 | 固定 gitlink 指向 ddd-subdomain-prompts；本次未跟随其 commit，无法核实 prompt/skill 正文。 |
| `.github/role-profiles` | tree / `1dd54e6d6817` | directory / observed-current | metadata-only | FRAMEWORK-01、FRAMEWORK-02 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `.github/role-profiles/README.md` | blob / `df38ce73acb2` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-02 | 角色索引把架构、产品、开发、风险和新成员引到工作指南；文件存在两套叙述。 |
| `.github/role-profiles/architect.md` | blob / `43ecb246343a` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 架构角色指南要求七步建模、审阅、追溯和 SWAS；前后各有一版工作流。 |
| `.github/role-profiles/developer.md` | blob / `4684fb8dd74b` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-02 | 开发角色指南描述读模型、实现、测试和反馈；前后两版 mandatory/optional 有差异。 |
| `.github/role-profiles/new-team-member.md` | blob / `ee9633fa6abd` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-02 | 新成员指南提供两小时导览、角色选择、样例读取、工具入口和禁止事项。 |
| `.github/role-profiles/product-manager.md` | blob / `80673e348161` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 产品角色指南说明 intended use、REQ、QAS、utility tree 和验收审阅；两版 mandatory 不完全一致。 |
| `.github/role-profiles/risk-manager.md` | blob / `3274a4cf2780` | skill / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 风险角色指南覆盖 intended use、RC→INV→REQ→TS、审批与残余风险；含两套流程。 |
| `.github/terminology-bridge.md` | blob / `eaf25d5f4be8` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02 | 提供 DDD、平台和业务语言映射及目录别名，供人和 Agent 阅读。 |
| `.github/utilities` | tree / `53cb7df7fc76` | directory / observed-current | metadata-only | FRAMEWORK-04、FRAMEWORK-05、FRAMEWORK-06、FRAMEWORK-07、FRAMEWORK-10 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `.github/utilities/_gen_ppt.py` | blob / `57a8a2d2856f` | utility / observed-current | full | FRAMEWORK-10 | 使用 python-pptx 生成固定内容的管理摘要 PPT，并写到硬编码 D: 路径。 |
| `.github/utilities/audio_transcriber.py` | blob / `f38dd60b46b5` | utility / observed-current | full | FRAMEWORK-04 | 为 Azure Speech、OpenAI Whisper 和未实现的 Copilot MCP 提供音频转写适配及回退。 |
| `.github/utilities/confidence_scorer.py` | blob / `5e4b872d0246` | utility / observed-current | full | FRAMEWORK-04、FRAMEWORK-16 | 按基础分、重复词、术语和不确定/否定/意见惩罚给候选打分；跨源/冲突增益为零。 |
| `.github/utilities/document_adapter.py` | blob / `53eba7aba4a4` | utility / observed-current | full | FRAMEWORK-04 | 读取 Markdown/DOCX，按标题提取 requirement/use-case/invariant/glossary 候选并返回近似行号。 |
| `.github/utilities/graph_generator.py` | blob / `8a64047f03fc` | utility / observed-current | full | FRAMEWORK-06、FRAMEWORK-14 | 从两个追溯矩阵解析 ID 链，输出 JSON/交互 HTML；无 ID 时使用内置 demo。 |
| `.github/utilities/input_source_adapter.py` | blob / `07289f196987` | utility / observed-current | full | FRAMEWORK-04、FRAMEWORK-16 | 定义 ExtractedArtifact 数据形状和适配器抽象接口，统一校验、提取、supported_types。 |
| `.github/utilities/log_interaction.py` | blob / `d7c4fa89e906` | utility / observed-current | full | FRAMEWORK-07 | 交互式追加 AI 日志并按硬编码模型价格计算 credits，支持 summary/estimate。 |
| `.github/utilities/tests` | tree / `4691131681bf` | directory / observed-current | metadata-only | FRAMEWORK-04 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `.github/utilities/tests/sample_cardiac_imaging_spec.md` | blob / `a3f3bb12b457` | asset / instance-only | full | FRAMEWORK-04 | 反向提取测试用心脏超声规格样例，含 requirements/use cases/invariants/glossary。 |
| `.github/utilities/tests/sample_cardiac_imaging_transcript.txt` | blob / `488ab97557cf` | asset / instance-only | full | FRAMEWORK-04 | 反向提取测试用心脏超声会议转录样例，含延迟、同意、加密和归档约束。 |
| `.github/utilities/tests/test_p4_01_cardiac_imaging.py` | blob / `afab499836d6` | utility / observed-current | full | FRAMEWORK-04、FRAMEWORK-16 | 脚本式 P4 测试串联适配和评分，使用 assert/打印而非 unittest；跨源相关性未实现。 |
| `.github/utilities/transcript_adapter.py` | blob / `616345007678` | utility / observed-current | full | FRAMEWORK-04 | 读取 txt/md 或调用转写器，用正则提取 requirement/use-case/invariant/重复术语候选。 |
| `.github/utilities/validate_artifact.py` | blob / `8bfaa6505ac0` | utility / observed-current | full | FRAMEWORK-05、FRAMEWORK-11 | 按路径规则检查 Markdown 标题和少数占位符；默认基线会回退到 main/master/origin 或暂存区。 |
| `.gitignore` | blob / `0f34ded61c52` | config / observed-current | full | FRAMEWORK-05、FRAMEWORK-10 | 忽略虚拟环境、缓存、演示/评估文件和本地脚本，避免实例资料进入候选。 |
| `.gitmodules` | blob / `b788e0af7174` | config / observed-current | full | FRAMEWORK-17 | 登记 prompts 与 templates 两个相对 URL 子模块；内容由固定 gitlink 提供。 |
| `.vscode` | tree / `fa7ae7f454fa` | directory / observed-current | metadata-only | FRAMEWORK-05、FRAMEWORK-06 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `.vscode/tasks.json` | blob / `53c6abed1ad1` | config / observed-current | full | FRAMEWORK-05、FRAMEWORK-06 | 编辑器任务直接调用 graph_generator.py 和 validate_artifact.py，使用宿主 python。 |
| `CONCEPTS.md` | blob / `78da12b0118f` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 解释 DDD/V-model、工件、风险追溯、提示模式、model.yaml 和 repo 边界；约 800 行后重复大章节。 |
| `README.md` | blob / `73b804b9fb87` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-04、FRAMEWORK-09 | 框架入口说明角色、路径、追溯、提示词、原始数据反向提取和实施仓 fan-out。 |
| `TEMPLATE-CHANGELOG.md` | blob / `62cf83c19719` | marker / observed-current | full | FRAMEWORK-03 | 记录模板仓结构变更和范围边界；不是业务领域变更日志。 |
| `_roadmap` | tree / `ec886cb0ed6b` | directory / observed-current | metadata-only | FRAMEWORK-11、FRAMEWORK-12、FRAMEWORK-13、FRAMEWORK-14、FRAMEWORK-15、FRAMEWORK-16 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `_roadmap/01-ddd-abstraction.md` | blob / `a1c6a28c7668` | roadmap / proposed-upstream | range:1-130 | FRAMEWORK-12 | 提出先改提示词/模板语言、后进行破坏性目录重命名及迁移脚本；全部是未来方案。 |
| `_roadmap/02-execution-engine.md` | blob / `70eede4d9432` | roadmap / proposed-upstream | range:1-309 | FRAMEWORK-11 | 提出 GitHub composite action、gap_detector、profile 检查、指标、PR 评论及后续自动子 PR/auto-merge。 |
| `_roadmap/03-scaffolding-automation.md` | blob / `4bf7d43ac0a6` | roadmap / proposed-upstream | range:1-283 | FRAMEWORK-12 | 提出 tantu init/migrate/check/version CLI、模板渲染、版本迁移、CODEOWNERS 和可选 GHE 建仓。 |
| `_roadmap/04-ghe-native-integration.md` | blob / `6ece7b0c0553` | roadmap / proposed-upstream | range:1-150 | FRAMEWORK-13 | 提出 CODEOWNERS、组织 Ruleset 和 Knowledge Base 的 GHE 治理接入。 |
| `_roadmap/05-tiered-profiles.md` | blob / `69d9fb2325f1` | roadmap / proposed-upstream | range:1-179 | FRAMEWORK-12 | 提出 lightweight/standard/regulated 三档 model.yaml/profile、路径骨架、profile 检查和升级迁移。 |
| `_roadmap/06-web-surface.md` | blob / `bbca6e977581` | roadmap / proposed-upstream | range:1-160 | FRAMEWORK-15 | 提出 Knowledge Base、Web 查询/审阅应用和 @tantu Copilot Extension，均为未来入口。 |
| `_roadmap/07-graph-generator.md` | blob / `23dba48ae928` | roadmap / proposed-upstream | range:1-175 | FRAMEWORK-14 | 提出从实际工件/model.yaml 解析节点边、模板渲染、指标和 CI 图产物。 |
| `_roadmap/08-impact-assessment-trigger.md` | blob / `6f81d0c10868` | roadmap / proposed-upstream | range:1-183 | FRAMEWORK-14 | 提出 PR 变更触发下游 BFS 影响评论，先结构化后语义化；当前没有对应脚本/workflow。 |
| `_roadmap/P4-01-reverse-engineering.md` | blob / `1f4a9eec1ddd` | roadmap / proposed-upstream | range:1-265 | FRAMEWORK-16 | 规划从转录、文档、代码和 SQL 提取模型候选及置信度；代码/Schema 适配器仍标未开始。 |
| `_roadmap/README.md` | blob / `d3cf542f3145` | roadmap / proposed-upstream | range:1-87 | FRAMEWORK-11 | 路线图总表把 P1/P2/P3/P4 自动化列为未来优先级，不能作为当前实现证据。 |
| `_templates` | commit / `9cc3338ba0d7` | gitlink / unverified | metadata-only | FRAMEWORK-17 | 固定 gitlink 指向 ddd-subdomain-templates；本次未跟随其 commit，无法核实表单、schema 和 waiver 模板。 |
| `azure-pipelines.yml` | blob / `0746f2506b89` | pipeline / observed-current | full | FRAMEWORK-05、FRAMEWORK-09 | Azure Pipeline 先跑标题/占位校验，再按 model.yaml.repoUrl 克隆 BC、复制 feature、commit/push 并建 PR。 |
| `docs` | tree / `1d1cb2116adf` | directory / observed-current | metadata-only | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `docs/README.md` | blob / `6afafe9a55bb` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 文档导航串起角色、DDD/V-model、三仓、提示模式、ID、model.yaml 和 QMS 主题。 |
| `docs/artifact-graph.html` | blob / `b792834fc49b` | asset / instance-only | full | FRAMEWORK-06 | 快照内交互追溯图是内嵌 demo HTML，浏览器依赖 Cytoscape CDN；不是现场矩阵证据。 |
| `docs/concepts` | tree / `4fc4f0b007c7` | directory / observed-current | metadata-only | FRAMEWORK-02、FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `docs/concepts/artifacts.md` | blob / `607ec4ecb982` | guide / observed-current | full | FRAMEWORK-02 | 说明 REQ/CAP/UC/INV/BR/TS 的问题、作者、使用者、基数和缺口诊断。 |
| `docs/concepts/bc-artifacts.md` | blob / `3f9187433721` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-09 | 说明底部 V 的 SR/US/ABB/VT 及 model.yaml 桥接，并声明不在本仓的边界。 |
| `docs/concepts/faq.md` | blob / `737cb8c12890` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 按角色解释自动生成、质量检查、追溯和影响分析的预期收益；多为流程承诺。 |
| `docs/concepts/overview.md` | blob / `c9930da41570` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 介绍 DDD、V-model、ISO 14971、AI sparring/autonomous 的定位与非目标。 |
| `docs/concepts/sparring-vs-autonomous.md` | blob / `19ae4a0ea5da` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-03 | 把提示词分为人决策的 sparring 与读取已确认输入的 autonomous；不是权限控制。 |
| `docs/concepts/three-repos.md` | blob / `250cab631213` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-09 | 描述 DomainModeling、BC implementation、RiskManagement 三仓输入输出和 model.yaml 桥。 |
| `docs/concepts/v-model.md` | blob / `69d3dc60bf3f` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 定义顶层/底部 V、风险分支、REQ→CAP→UC→INV→TS 和覆盖级别。 |
| `docs/getting-started` | tree / `5fba065cd1f9` | directory / observed-current | metadata-only | FRAMEWORK-01、FRAMEWORK-09 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `docs/getting-started/setup.md` | blob / `54e18bc1ea06` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-09 | 给出 clone、submodule、角色入口、BC/Risk 配置和 VS Code agent 手工设置。 |
| `docs/reference` | tree / `803884b98f7e` | directory / observed-current | metadata-only | FRAMEWORK-02、FRAMEWORK-03、FRAMEWORK-09 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `docs/reference/artifact-ids.md` | blob / `d1b399002d07` | guide / observed-current | full | FRAMEWORK-02 | 规定工件 ID、文件名、序号、状态和上下游追溯格式。 |
| `docs/reference/model-yaml.md` | blob / `f4ebc80e4114` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-09 | 给出 BC model.yaml 示例、summary/release/risk 字段、双提交和一致性规则；无同仓实例。 |
| `docs/reference/prompts.md` | blob / `2b4c48abe921` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-17 | 列出三仓提示词模式、读写工件和 human gate；正文在未读取 gitlink。 |
| `docs/reference/qms-traceability.md` | blob / `88f994bdeb34` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03、FRAMEWORK-09 | 说明工作矩阵/QMS 矩阵、IEC 62304/ISO 14971 映射和发布阻塞条件。 |
| `docs/roles` | tree / `afc6bbd2c0c4` | directory / observed-current | metadata-only | FRAMEWORK-01、FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `docs/roles/README.md` | blob / `6a722d3d3a5c` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-03 | 角色索引和决策权表分开 PM、架构、开发、风险职责。 |
| `docs/roles/architect.md` | blob / `80393b161cb3` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 架构指南覆盖领域模型、SWAS、ABB、ADR、审阅和发布检查。 |
| `docs/roles/developer.md` | blob / `91c8500a9978` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-09 | 开发指南定义 BC 仓前置条件、SR/US/ABB/VT 派生和 model.yaml 双提交。 |
| `docs/roles/domain-modeler.md` | blob / `127349033dd6` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02 | 领域建模指南强调 sparring、术语、invariant 责任和结构变更影响。 |
| `docs/roles/requirements-engineer.md` | blob / `bc18b0496b8f` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-03 | 产品指南定义 REQ 七项质量检查、QAS、矩阵和 intended-use amendment。 |
| `docs/roles/risk-manager.md` | blob / `b879089dd2f5` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 风险指南定义六步风险生命周期、RC/REQ/INV/VT 链和残余风险前置。 |
| `domain-model` | tree / `3508d38b153a` | directory / observed-current | metadata-only | FRAMEWORK-02、FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `domain-model/README.md` | blob / `66c1188f8896` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 领域目录声明 domain-model 为事实源，列出 backlog/glossary/subdomains/decisions 和追溯链。 |
| `domain-model/backlog.md` | blob / `c385513ffa65` | marker / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 开放问题含 ADR-0002/3/4/5 与治理扩展问题，体现未决事实和责任人。 |
| `domain-model/decisions` | tree / `da3679786387` | directory / observed-current | metadata-only | FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `domain-model/decisions/ADR-0001-v-model-repo-split.md` | blob / `b9a45b1ae713` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-09 | 接受两仓 V-model 切分与 implementation repo 只读 domain 子模块；中心发布仍未完成。 |
| `domain-model/decisions/ADR-0002-swas-placement.md` | blob / `627dc4ee2915` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-09 | 接受 SWAS 在 subdomain DomainModeling 仓并由 model.yaml abbSummary 驱动，声明 PDF pipeline。 |
| `domain-model/decisions/ADR-0003-model-yaml-abb-bridge.md` | blob / `4b3b429db3df` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-09 | 接受 model.yaml abbSummary 作为 BC→SWAS 桥，规定更新与双提交；示例和参考字段不完全一致。 |
| `domain-model/decisions/ADR-0004-prompts-governance.md` | blob / `89abaf6f4ba3` | guide / observed-current | full | FRAMEWORK-03、FRAMEWORK-17 | 接受中央 prompts/instructions/templates 子模块但延期实施，并提出 CODEOWNERS 过渡。 |
| `domain-model/decisions/ADR-0005-workflow-prompts-over-role-agents.md` | blob / `9ef944e79877` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-03 | 接受工作流提示词优先于角色代理，要求人工闸门、显式来源和可查询桥接。 |
| `domain-model/decisions/README.md` | blob / `d439749adecd` | guide / observed-current | full | FRAMEWORK-03 | 登记五份 ADR 的中心 wiki 发布状态及起草/发布/回链流程。 |
| `domain-model/domain-definition.md` | blob / `05a3d1834e70` | guide / observed-current | full | FRAMEWORK-02 | 提供多 subdomain 定义、分类、责任、上下文图和开放问题结构。 |
| `domain-model/glossary` | tree / `cac24f5e07c8` | directory / observed-current | metadata-only | FRAMEWORK-02、FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `domain-model/glossary/business-rules.md` | blob / `dd627a163d5c` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 提供跨 subdomain BR、invariant 索引和变更日志空白结构。 |
| `domain-model/glossary/ubiquitous-language.md` | blob / `3464bd7bed48` | guide / observed-current | full | FRAMEWORK-02 | 提供共享术语、歧义术语、废弃术语和命名约定空白结构。 |
| `domain-model/subdomains` | tree / `40c58f8f09a8` | directory / observed-current | metadata-only | FRAMEWORK-01、FRAMEWORK-02 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `domain-model/subdomains/README.md` | blob / `8748b92a8f80` | guide / observed-current | full | FRAMEWORK-01、FRAMEWORK-02、FRAMEWORK-17 | 说明 subdomain 应由 Copilot 从模板创建并维护目录索引。 |
| `glossary-digital-backbone.md` | blob / `68a4cee10db4` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 登记组织级 Digital Backbone 术语、角色、运行时、治理会议和开放问题。 |
| `platform-model.md` | blob / `0df1c5a82ab3` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 用 Mermaid/表格定义 Offering/BC、需求、领域、验证、QMS 和实施仓关系。 |
| `requirements` | tree / `ae7d9609d555` | directory / observed-current | metadata-only | FRAMEWORK-02、FRAMEWORK-03 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `requirements/README.md` | blob / `49a25ad0ac35` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 要求用 requirements-capture 写 REQ，补领域影响、矩阵和变更日志。 |
| `requirements/_governance-catalog.md` | blob / `63f970ea9891` | guide / observed-current | full | FRAMEWORK-03 | 登记 GOV-001..006 的 SBOM、依赖、威胁、审计、驻留、可访问性和 waiver 结构。 |
| `requirements/change-log.md` | blob / `cb69dfafb5a0` | marker / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 提供按 REQ 记录 subdomain/BC/术语/规则变化的审计日志结构。 |
| `requirements/utility-tree.md` | blob / `746bd0d788df` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-03 | 提供业务目标、QAS 优先级/难度、架构显著项、硬约束和开放问题结构。 |
| `sample_spec.md` | blob / `61b0d1aa214b` | asset / instance-only | full | FRAMEWORK-04 | 根目录病人管理示例规格，展示 REQ/UC/invariant/constraint/glossary 形状，不是当前业务事实。 |
| `testing` | tree / `ca6e946c152b` | directory / observed-current | metadata-only | FRAMEWORK-02、FRAMEWORK-06 | 目录项；仅登记 Git tree，不把目录本身计作文件能力。 |
| `testing/README.md` | blob / `ddab4dfba9c9` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-06 | 规定 BC/跨 BC 场景、验收测试、feature 文件和 REQ/UC/INV 覆盖条件。 |
| `traceability-matrix.md` | blob / `88a91e79d03d` | guide / observed-current | full | FRAMEWORK-02、FRAMEWORK-06 | 提供 REQ→CAP→UC→INV→SR→TS/GOV 表格、覆盖符号和待补缺口。 |
