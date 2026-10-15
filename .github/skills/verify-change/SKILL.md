---
name: verify-change
description: Use when assessing acceptance or domain artifacts, querying current inventory, reviewing backlog evidence, or checking coverage and result applicability after a rule or baseline change.
---

# 核对验收、影响与证据

从完整交付验收清单开始，不从已有 VT 倒推范围。追溯完整、实际执行和执行成功是三个不同结论。

## 输入

- 当前任务与完整交付范围，实际模型、REQ、SR、必要设计及维护完成条件。
- Git 分支、commit、未提交范围，要求与 VT 基线；全部相关 VT、既有运行和原始报告。
- 检查模式与授权；真实对象、[开发配置](../../../docs/development.md#project-registration)或其缺项。
- 领域审阅另需本次实际提供的工件、来源、上下文及开放问题；查询需明确根目录、对象类型与过滤范围；BL 核对需原问题及决定证据。治理/风险资料仅在已提供且适用时纳入。

<a id="review-mode"></a>
## 先确认模式

执行模式才进行下文获授权的检查与记录。**只读审阅模式**只读现有材料、核对证据并返回发现；下文的执行和写入步骤在此模式下仅用于列出待办，不运行验证命令，不修改 VT、索引、日志或其他输出文件。报告需要执行什么、缺少什么，不能编造结果或代授权人批准。此约定不是客户端强制权限边界。

领域审阅、库存查询和 BL 审阅默认采用只读意图；如需执行或保存报告，先取得该任务的具体授权。文件可定位、结构合法、追溯覆盖、实际执行、成功和当前适用性各有不同依据；“Approved”、角色名称或提交不能替代具名决定、范围与基线。

<a id="coverage"></a>
## 覆盖核对

1. 按[验收盘点](../../../verification/README.md#coverage-check)读取本次范围内的全部验收来源，逐项记下所有者、完整 ID、原文链接、层次和基线；包括相关 UC/INV/QAS、REQ、SR、必要设计、维护条件及**没有 VT 的目标**。即使每个现有 VT 都有有效文件链接，也不能跳过全量盘点。排除项要有确认依据，不能通过缩小范围消除缺口。
2. 逐项搜索 VT/业务场景的目标字段，检查方法、前提、边界和独立判据是否足以判断该验收。再**反查每个实际目标**：文件/锚点存在吗，完整 ID 与所有者/条目一致吗，层次正确吗，判据是否真正覆盖目标？有元数据时按 `scope/id#anchor` 查找；旧资料仍按原所有者 ID 与稳定链接核对，不为查找而迁移。同号异主、泛化标题、漏项和悬空目标分别列出精确 ID/位置；输入没给身份时记录实际可得来源与缺项，请求补充，不发明目标编号。
3. 核对来源关系：上游依据留在 [SR](../../../software-requirements/README.md#traceability)，目标关系留在 [VT/场景的目标声明](../../../verification/README.md#domain-scenarios)。采用元数据时，`upstream` / `targets` 归 frontmatter，正文判据由 `criterionAnchor` 定位；旧记录保留其原有字段。[验证索引](../../../verification/README.md#coverage-index)只登记导航、基线、缺口和引用差异，不复制验收正文、反向映射或另一张结果表。

获准执行工具时按[实际覆盖接口](../../utilities/README.md#traceability)调用 `trace_report(root, delivery_ids)`，完整清单来自第 1 步，不能从 VT 重建。反查所有实际 targets，保留输入错误与源定位；分层和判据检查是机械下限，不能代替第 2 步的语义审阅或证明执行。

<a id="domain-review"></a>
## 领域工件审阅

读取范围内的来源和当前工件，先按上文盘点全部适用验收，再核对术语含义、概念关系、规则到 INV 的依据、上下文拥有/消费事实、UC 路径、QAS 度量及已采用的接口/战术约定。未采用的可选资料不强造，确认依据、未知事实与模型漂移分别列出。

每条发现包含：实际来源与文件/行或章节、对象基线、观察或推断、严重度及理由、受影响工件/目标、所需决定或证据、建议动作和已有 BL。严重度表达本次问题影响，不自行赋予临床/监管等级。缺文件、ID、责任人或证据时逐项写明；无 BL 就提出建项建议，不冒充已创建或已解决。

输出发现与残留缺口，不自动重构、修正状态或宣布健康。内容写“confirmed/approved”但缺具名决定及适用基线，不能确认其批准；结构校验也不能认证身份。语言/边界的候选解释可用 [知识锤炼](../define-requirements/SKILL.md#distill)，实际修改仍回获授权任务。

<a id="query"></a>
## 查询实际库存

按给定根目录、对象类型、scope 与问题读取真实文件，按路径和完整身份稳定排序，返回匹配项、实际读取/未读范围、数量、来源版本与精确缺口。没有正式对象与无法读取是不同结论；不从空白表单、目录名或未来文件推导对象。仅查某类库存不等于全量验收覆盖；问覆盖时仍从[全部验收](#coverage)开始。

查询不生成模型、不补写工件或持久索引。若有派生摘要，返回其来源并核对基线，不能以摘要替代原文；没有摘要就读现有资料。[parser 与正式工件检查器](../../utilities/README.md#artifact-checker)处理元数据、身份、结构、占位和本地链接，与覆盖接口分工。只读审阅模式不运行工具；获准执行时记录明确 root、完整当前库存、可选精确 base、实际计数与读集摘要，`empty` 不能当通过。另获模型派生/检查授权时用[模型接口](../../utilities/README.md#model-export)和[可选本地来源清单](../../contracts/README.md#model-sources)，九视图的来源状态不是业务结果；只有显式新输出授权才写文件。

<a id="bc-review"></a>
## BC 派生与实现边界审阅

沿[完整验收](#coverage)核对实际 SR、可选 US、ABB/ADR、VT/companion、SEQ/SWAS 与来源基线，默认遵守[只读模式](#review-mode)，不自动生成或执行。正式关系和内容状态以现有元数据为准，正文只解释来源与独立判据；旧轻量资料不强制迁移。

- REQ/UC/INV/CAP/QAS 是否足以支持已写的软件行为、拒绝/错误与禁止副作用？未确认来源、角色、指标和并发/失效政策是否仍明确未决？US 是否只组织切片而未成为强制桥梁，ABB/VT 是否只依赖各自必需输入？
- ABB/ADR 是否只有有源的结构约束与真实取舍？代码相关审阅显式读[架构](../../instructions/architecture.instructions.md)、[编码](../../instructions/coding.instructions.md)、[安全](../../instructions/security.instructions.md)与适用[测试规则](../../instructions/tests.instructions.md)，即使真实目录未匹配。区分合法装配入口与业务逻辑绕过，不由边界名称推断权限。
- VT 是否逐项反查真实 owner/锚点、独立判据及实际场景/测试定位？`.feature` 是否独占场景正文？没有应用、步骤实现、runner 或报告就保持 `not-run`；Approved、测试名和 parser 成功均不证明批准或执行。
- SEQ 是否区分概念参与者和真实 ABB/接口、保留有源方向与异步契约而未发明传输保证？SWAS 的九类来源可读性是否回原文/基线核对，缺 ABB/部署/风险/发布时是否保留 gap 而不是虚构基础设施或批准？
- 初始生成是否经过 [generate-code 预检](../generate-code/SKILL.md#preflight)，列明所有准确路径、来源/验收和授权范围？非空冲突、路径错配或缺开发输入必须有阻塞记录，跳过不算完整生成。既有维护核对任务/diff/复现，而非初始化覆盖；只读源和所有者内容应保留。

发现按[已有字段](#domain-review)返回实际位置、基线、理由、影响与缺项。实际修改/执行仍需具体授权；本小节不新增 checker、安全审计或应用通过结论。

<a id="backlog-review"></a>
## 开放问题与 BL 审阅

逐项对照原问题、冲突来源、影响/阻塞范围、实际责任人及[决定证据](../../../_templates/items/backlog-item.md#decision)。报告尚待答复、已有决定但待落实、证据不足及可建议关闭的项；这些是本次发现分类，不是替换原状态枚举。只有可定位且适用的决定/处理证据才支持关闭建议，过期、排期、实现常量、链接齐全或自称“done”均不够。

按[发现字段](#domain-review)列残留影响与待核对的验收/VT；统计注明本次真实盘点范围，不把未知项算已解决。获准修改时才更新原 BL 的处理进度、决定依据和后续复核，保留历史；`contentState`、处理进度、实际执行结果与当前适用性互不转换。

<a id="impact"></a>
## 语义影响（执行前）

1. 对照旧新规则、上下文、验收与基线，记录实际变更 ID/位置、来源和确认状态。沿引用及业务含义追踪依赖的模型、UC/INV、REQ/QAS、SR、US、ABB/ADR、SEQ/SWAS、场景/VT 及 companion 和任务；边界变化还核对 CAP、context map、Published Interface 与消费者。即使数值只存在于一个规则文件，引用方的行为边界仍可能受影响。只有实际提供且适用时才加入[来件 ADR](../define-requirements/SKILL.md#incoming-adr)、[Intended Use](../define-requirements/SKILL.md#intended-use)和治理/风险引用；缺源标明受影响判断不能完成，不代作风险决定。
2. 按[影响指引](../../../verification/README.md#change-impact)列受影响项及各自来源、理由、严重度、需谁确认什么和建议顺序；仅在变化已确认且修改获准后更新验收边界、错误/禁止副作用和 VT 预期，保留仍成立的回归场景。无影响的判断给出理由；未确认的业务变化先澄清，不擅改规则或删除原验收，建议顺序不是已执行的修改。
3. 保留旧运行的实际结果及其原对象、要求和 VT 基线；在原结果的[适用性栏](../../../_templates/items/verification-test.md#applicability)追加对当前基线的“待复核”和影响理由。不能把旧成功改写为新成功或历史失败，新检查须追加独立记录。

获准执行工具时，使用[影响候选接口](../../utilities/README.md#impact-candidates) `impact_report(root, base_sha, task_ids=())`。传入精确完整 commit 及已提供任务 key，读取当前快照；旧新依赖、删除源和移除引用均保留理由。候选不代表最终业务影响、严重度或确认；非 canonical 的依赖和未知语义继续按上文核对，工具不回写规则/原结果，也不执行 VT。

## 执行与记录

1. 依[验证层次](../../../verification/README.md#layers)确定当前可执行对象和逐项判据。没有应用时应用检查对文档任务不适用，已规划业务/软件 VT 仍为 `not-run`；已有应用但对象、环境或命令不可用时，相关检查为 `not-run` 并写具体原因，不能称不适用来跳过。
2. 只运行实际配置且获授权的命令、cwd 或明确人工步骤。按[执行指引](../../../verification/README.md#execution)核对实际范围、发现/执行/跳过数量和逐项目标观察；零发现、全跳过、缺证据或退出码为零，都不能单独建立验收成功。
3. 在 [VT 实际执行栏](../../../_templates/items/verification-test.md#runs)追加真实对象/要求/VT 基线、时间、环境、步骤、原始报告及逐项结果；未执行仍为 `not-run`，跳过记 `skipped` 与原因。报告不可访问则说明限制，不造链接或补写未观察的结果。
4. [独立文档检查](../../../docs/development.md#document-checks)使用自己的对象、判据、结果与基线，可记录于文档层 VT 或已有获准检查记录；绝不填进计划中的行为 VT。业务验收也不能由软件通过汇总得出。用 [record-handoff](../record-handoff/SKILL.md)链接权威记录、精确缺口和剩余动作，日志不复制结果表。

## 产出与完成

获授权的记录落在 `verification/README.md#coverage-index`、相关 `verification/VT-NNN-<slug>.md` 的目标/运行/适用性/缺口栏，以及实际报告入口；必要的验收修改回到其所有者。领域问题按需进入原工件未决栏或[BL 的正式落点](../../../domain-model/README.md#strategic-forms)，不另建结果或状态镜像。只读审阅/查询只返回可定位的发现、库存、证据限制和建议执行项，不写文件。

全量验收已核对、悬空/未覆盖项明确、语义影响已追踪、实际证据可定位且未执行项保留后，可报告本次核对完成及其范围。只有逐项目标的实际证据满足判据，才能声明对应验收通过。

## 停止条件

完整范围或必要来源不可读、确认依据冲突、检查前提缺失、执行失败或授权不足时，停止受影响的执行/通过声明，保留已知发现和下一步。不得删范围、发明目标或拿其他层结果补缺口。
