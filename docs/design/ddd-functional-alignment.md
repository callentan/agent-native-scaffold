# 六仓功能对齐：增强规格

**Task8 修正进度（2026-10-16）：** 原 T8-I1/I2/I3 沿用限定复审的 ADDRESSED 判定。第 2 轮仅修正新 T8-F1-N1 的业务 tree 误判，聚焦 RED/GREEN 和整个 model 模块 94 方法验证完成，等待限定复审；没有重跑或改标原 395 全套结果。原 schema、32 kinds、九视图和 Tasks9–18 的未开始状态不变，结果入口见[第 2 轮交接](../../logs/2026-10-15-ddd-alignment.md#task8-fix2)。

**状态：执行中，任务 1–7 的有限实现与范围复核已完成，Task8 已实施并经本地验证、等待独立复核，完整增强尚未交付。** Task7 原五项 Important 和后续 F1-N1 均已修正并完成限定复审，最新修正对象为 `23c06b6`；当前八方法、二十一 prompts、三模式。现有工具提供覆盖/影响候选、带可选来源清单的九视图，以及按用户单独选择复用现有 VT 运行的只读实施摘要。Task9–18 未开始，本轮在 Task8 本地提交和交接后停止等待 review。代码生成方法已经提供，但实际应用生成与运行尚未验收。2026-10-14 用户确认功能等价、单仓和下游技术栈中立，不要求原格式直接兼容；2026-10-15 确认 Python 优先并要求先提交当前变更、再执行计划。完整六仓核对后，用户确认将新发现的现有功能完整纳入，音频/PDF/外部平台的依赖与执行另行授权。不自研 CLI 或执行器。

原 P1/P2/P3 实现基线为 `453189135af07f8ba5ab65dd4dd58879b8741c17`，规划修订为 `f9aab56`。本轮按用户要求将 README 排版单独提交为 `1a6f594` 后开始，起点工作树干净；不再把这两处排版视为未提交。原 P1/P2 的 38 文件与[原 P3 未完成项](../plan/roadmap.md#actual-acceptance)继续保留，不被新实施状态抹掉。

## 1. 范围与参考基线

只对齐以下六仓的**现有功能**，不复制其源码、业务内容、品牌或六仓部署形态。本轮通过只读 Git 获取并核对这些完整 commit，逐文件分类与能力证据见[六仓能力矩阵](../research/ddd-capability-matrix.md)；原有[历史来源登记](../research/source-register.md)保留为历史观察。

| 参考仓库 | 固定 commit | 关注职责 |
|---|---|---|
| ddd-bc | `bac263bea39988214b82cafb48f27e3a2136c534` | BC 工程约定、配置、领域输入与实现边界 |
| ddd-bc-prompts | `08f8219397d6fe6d000312f5956a493b1b28cc84` | SR/US/ABB/VT 派生、代码生成及维护工作流 |
| ddd-bc-templates | `00705aef6c70f855ef95588b0137cf7f2387efb0` | 实现侧工件表单 |
| ddd-subdomain | `e115ad4d03ac53359c608ce7d32262a508561496` | 领域工程、校验、hooks、传播与治理记录 |
| ddd-subdomain-prompts | `1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c` | 访谈、建模、反向提取、评审与变更活动 |
| ddd-subdomain-templates | `59f98e352a150f99290a3855092298dbe11e0615` | 领域结构、模型和验证场景表单 |

任务 1 必须逐文件冻结能力矩阵，将原仓已有功能与本计划新增的自动化分别登记。统一使用 Python 是实现策略，不证明导出、自动追溯或三方更新各自都有原仓脚本对应。历史摘要、实例 repo 的使用情况和上游路线图不能冒充六仓已经实现的能力。读取受限时记录具体缺项，停止依赖它的等价判定；不猜测文件内容或追随新的 HEAD。

本轮盘点覆盖 252 个 Git entries、195 个 blobs；185 个文件全文读取，10 个 roadmap 文件按范围阅读并标为提案，目录/gitlink 只登记元数据。新增承接的是来源中已存在的 QAS/战术工件、SEQ/Gherkin/SWAS、词汇与发布接口演化、可选领域源接入、输入适配、图/文档/演示导出和交互账本；不是把它们伪装成原计划已经覆盖。

`DM-Subdomain`、`DeviceRegistry-BC` 只可提供已授权的研究线索，不是本增强的交付清单或应用底座。Tantu CLI、通用执行引擎、自动批准/合并、状态数据库、Web 平台和专用技术栈不纳入本规格。

<a id="requirements"></a>
## 2. 增强验收项

本维护请求直接作为依据，不在空白模板中制造产品 REQ/SR。`ENH-*` 是本增强的验收标识。

| ID | 要求与可观察完成条件 |
|---|---|
| ENH-01 | 六仓固定版本的全部文件有分类；每个现有能力有来源、当前差距、目标等价方式、任务及验证证据。路线图、重复入口和实例内容单列。任何未核验或未接受的差异都不能计为已对齐 |
| ENH-02 | 工件身份、作用域、来源、关系、内容状态、任务进度与执行结果有明确契约；新结构可从现有单上下文 Markdown 无损演进，不搬移/覆盖已有资料 |
| ENH-03 | 支持 subdomain/context、capability、UC、INV、业务验证场景与 BL 未决项；规则、来源、关系和职责可定位，多上下文同号不混淆，未知事实保持未知 |
| ENH-04 | 访谈、建模、领域评审、反向提取及影响分析可按共享方法完成。反向提取带源定位、证据置信度和确认状态，不因代码存在把行为认定为批准的业务事实 |
| ENH-05 | SR、可选 US、ABB/ADR、VT 的派生、评审、初始代码生成及既有代码修改有分别可执行的契约；缺输入、非空目标冲突和未执行测试明确报告，不缩小验收或强制经过 US |
| ENH-06 | BC 配置能定位身份、上下文、固定领域输入、读写性质及命令登记；`model.yaml` 是带来源基线的派生索引，不成为第二份领域事实，错误路径/版本和手改视图可检测 |
| ENH-07 | 仓库内可重复执行工件校验，覆盖元数据、必要结构、ID、占位、链接和输入错误；明确退出码、检查数量和对象基线，空骨架不被称为业务验收通过 |
| ENH-08 | 从完整交付验收盘点 VT，反查每个目标，精确发现漏项、悬空/同号异主和失效基线；支持规则变化的影响清单，机械检查与人工语义判定分开 |
| ENH-09 | 工具资格、人工审阅与交互摘要的记录可追溯；内容声明不能认证审阅人或自动批准。仅当六仓现有文件确有专用领域/风险工件时，按能力矩阵补充可选对应表单，不宣称法规符合性 |
| ENH-10 | 可选 Git hooks 和 CI 调用同一校验器；显式基线无法解析必须失败，不回退 main/master/暂存区制造空检查。禁用 hook 不等于绕过服务端必需检查，后者须实际平台配置 |
| ENH-11 | 模板版本更新支持旧基线/项目本地/新候选三方比较，多目标传播有明确登记、差异和冲突结果；默认只产提案，获授权的原生 Git/平台流程才能写入或建 PR，不覆盖业务事实 |
| ENH-12 | 实施摘要连接 BC、领域来源、SR/US/ABB/VT、真实代码/测试标识及结果基线；报告不自行认证通过或回写只读领域源 |
| ENH-13 | 干净候选按文件清单分发。模板正文、可选工具及其依赖与测试分别说明；研究、计划、制作日志、内部来源、演练数据和 Git 历史不进入候选 |
| ENH-14 | 固定文档正反例、真实 App 工作流、新会话接手和经授权的代码生成/传播演练均有范围明确的结果；未运行项保持未验证，原 P3 的人工与客户端缺项不被继承为通过 |
| ENH-15 | 可选领域源接入支持明确仓库/版本/实际路径、只读/本地所有权和占位冲突检查；以 Python 提供预检与明确执行，不默认创建子模块、提交或推送 |
| ENH-16 | 本地 Markdown/plain text、明确转录格式和 DOCX，以及经单独批准的音频输入能形成带来源定位/置信度的候选工件；文档定位至少保留段落/表格或等价源位置，支持来源关联和不确定性，不自动批准。缺可选解析器/依赖时明确不可用，不发送资料或伪造转录；DOCX 未实际运行时本项保持 `not-run`，音频服务仍单独授权 |
| ENH-17 | 来源可追溯的关系图、SEQ、SWAS 及 `render_presentation(inputs, format)` 参数化演示输出可从指定输入生成；演示是必需的等价能力，不得靠 allowlist 排除；无数据显示 empty，不注入 demo；本地输出明确、无个人路径，PDF/PPTX 依赖与实际格式检查仍须按授权执行 |
| ENH-18 | AI 交互与用量摘要可按明确范围/工具/时间记录并形成可核对统计；无真实用量不编造计费/资格结果，不保存完整敏感对话，不用账本替代审批或执行证据 |

## 3. 设计约定

### 3.1 唯一事实源与结构

保留现有顶层资料目录；轻量项目可继续用 `domain-model\README.md`。确需多个领域时，正式资料按 `domain-model\subdomains\<slug>\contexts\<slug>\` 组织；不预填真实 SD/CTX，不要求业务边界等于服务或代码层。

完整功能路径还提供可选 QAS、context map、published interface、aggregate、entity、value object、factory、domain service、policy、domain event、integration partner、Intended Use/风险引用和架构规格/SEQ 表单。按当前任务选用，不强制每个维护事项完成全套战术或监管工件。专用字段只记录责任人给定的来源和决定，不声明合规。

领域/软件场景的 `.feature` 保留可执行 Gherkin 正文，Markdown 保存目标、元数据、判据与文件引用，不复制两份场景正文；没有 runner/应用时保持计划 not-run。sequence、QAS、风险与 release 等桥接字段用工件/证据引用表示，不搬运业务正文进 `model.yaml`。

工件 Markdown 正文拥有业务含义、规则和验收。正式工件的 YAML frontmatter 拥有机器身份、作用域、声明状态及上游/目标关系；原表单中重复表达这些元数据的状态/关系栏改为引用或删除。VT 的正文按 `criterionAnchor` 保存逐项判据，frontmatter 的目标记录只定位对应来源与判据。反向索引从这些关系派生，不再手写另一份映射。

统一机器身份为 `scope/id#anchor`；`scope` 由项目与上下文组成，例如演练中的 `sample/CTX-001/SR-001#sr-001-ac-02`。同一个 scope 下重复 ID 是错误，不同 scope 的同号工件允许存在。现有 REQ/SR 验收 ID 和锚点保留，不用改号掩盖历史。

声明内容状态为 `draft | confirmed | retired`，任务进度仍为 `todo | in-progress | blocked | review-ready | done`。实际结果为 `not-run | pass | fail | skipped`，当前适用性独立记录。确认记录必须指向具名来源和被确认基线；存在声明或链接不等于已核实人工身份。

### 3.2 BC 配置与派生模型

`bc-config.yaml` 是**可选的数据配置**，不是项目执行 manifest。字段为 `schemaVersion`、`projectId`、`boundedContexts`、`domainSources` 和开发登记的引用。每个领域来源明确 `kind`、`root`、仓库内相对 `path`、固定 `baseline`、`readOnly`；不把挂载根和仓库内路径拼成猜测，不保存凭据或复制开发命令。

`model.yaml` 只保存 `schemaVersion`、`scope`、来源对象基线、工件位置/ID/关系和实施摘要引用。正文不复制进去；内容声明仍回 Markdown，结果仍回 VT/真实报告。导出器采用确定顺序，保留完整原 ID，不在读取时联网或更新外部仓库。

2026-10-15 恢复执行后，用户明确选择可选的 `model-sources.yaml` 登记视图来源。Task7 采用 `schemaVersion: 1`、`scopes: {project/context: {view: [{path, baseline}]}}` 的[独立来源契约](../../.github/contracts/README.md#model-sources)及[空表](../../_templates/config/model-sources.yaml)。只读取 root 内的实际文件与原始 SHA256/精确本地 Git commit/blob，拒绝网络、跳转、重键、冲突基线和派生 model 自引用；不复制正文、结果或批准状态，不授予执行/写回权限。本制作仓没有正式项目清单。

具体已有 Markdown 章节与 YAML/JSON 源字段形状归契约说明维护，不改变下面的九视图输出 schema。完整主库存先核对，选定 scope 不从目录推断；直接 Markdown 可合并多个显式来源，汇总源只保留 source 字段的实际导航。缺清单、缺 scope 登记、缺 view 与非法配置分别处理。实际 APIs/CLI、源身份和漂移码见[工具说明](../../.github/utilities/README.md#model-export)，测试/自审不是独立复核或业务验证。

Task7 第 1 轮修正按下表的原语义补足 QAS/utility-tree 缺源判断、全部已解析嵌套声明的输出保护、真实 Mermaid 围栏归属、VT 子运行块/逐判据结果，以及 impact API 的必需 base。运行记录不挪到父标题前，不跨运行拼字段或推算数量；原四份 schema、32 kind 和九视图不变。实现和回归不自行关闭限定复审。

#### 3.2.1 视图桥接契约

九视图只在派生 model 中保存；实施报告沿用独立 v1 的 `entries[].execution/applicability`，没有根级 execution/views。报告另行显式选择为 verification 来源后，model 只保存经基线/可重建性核对的报告引用，不复制执行条目。跨仓来源的 `views` map 固定键为
`requirements`、`stories`、`architecture`、`sequences`、`verification`、
`quality`、`governance`、`risk`、`release`。每个视图必须具有以下形状；视图
只保存引用和可定位缺口，不复制领域正文、审批声明或实际结果：

```yaml
views:
  <view-key>:
    state: available | partial | unverified
    artifactRefs:
      - scope/id#anchor
    evidenceRefs:
      - reference: repo-relative/path#anchor
        baseline: source-object-or-report-baseline-pointer
    gaps:
      - specific reason string
```

`state` 只表示来源的可读性和完整性：`available` 表示该视图所需来源可读且
完整，`partial` 表示来源可读但有字段/条目缺失，`unverified` 表示可选来源
缺失、来源不可读或证据基线不能核实。它永远不是 `passed`、`approved` 或
任何实际结果。`artifactRefs` 使用唯一的 `scope/id#anchor` canonical key；
`evidenceRefs` 必须同时保留 `reference` 与 `baseline` 指针。可选来源缺失时
仍输出该视图，使用 `unverified`、空引用集合和具体 `gaps` 原因，不能伪造
数据或省略视图。领域正文仍归领域工件，真实结果仍归 VT/运行报告/治理或
风险记录的原所有者。

| 视图 | 源字段映射 | `artifactRefs` 的内容 | `evidenceRefs` 的内容 | 缺失/不完整规则 |
|---|---|---|---|---|
| `requirements` | `srSummary.srVersion`、`srSummary.entries[].reqId/srIds/ucId/status/notes` | REQ、SR、UC 的 `scope/id#anchor` | SR/REQ 源路径与固定对象、报告基线 | 缺 `srSummary` 写 `unverified`，gap 为“`srSummary` source is absent”；版本或条目不全写 `partial` 并说明缺少字段 |
| `stories` | `storySummary.storyVersion`、`storySummary.entries[].srId/usIds/status` | SR、US 的 canonical key | 故事源路径与对象/报告基线 | 缺 `storySummary` 写 `unverified` 并指出“SR→US bridge is unavailable”；条目缺状态写 `partial` |
| `architecture` | `abbSummary.abbVersion/language/framework/blocks/integrations`，含 `adrRef` | ABB、ADR、集成伙伴的 canonical key | ABB/ADR/接口源路径与版本或 Git 基线 | 缺 ABB 或 ADR 源写 `unverified` 并说明缺哪类；只读到部分 blocks 写 `partial` |
| `sequences` | `sequenceSummary.seqVersion`、`sequenceSummary.entries[].seqId/ucId/title/hasAsync/externalPartners/status` | SEQ、UC、ABB、伙伴的 canonical key | SEQ 文件与来源对象/生成报告基线 | 缺 `sequenceSummary` 写 `unverified` 并说明 runtime sequence source is unavailable；版本/参与者不完整写 `partial` |
| `verification` | `verificationSummary.vtVersion/lastRunDate`、`verificationSummary.entries[].usId/vtIds/result/automatedCount/manualCount/notes` | US、VT、REQ/SR 的 canonical key | VT 文件、运行报告与其对象/要求基线 | 缺验证源写 `unverified` 并说明 evidence source is unavailable；`result` 只引用原记录，不由视图改写 |
| `quality` | QAS/utility-tree 工件与其 `testScenarios` 引用；源 `model.yaml` 没有另造 `qasSummary` 字段 | QAS、REQ、TS/feature 的 canonical key | QAS/utility-tree/场景文件与版本或报告基线 | 缺 QAS/utility-tree 写 `unverified`，gap 具体说明 quality source is missing；只读到部分场景写 `partial` |
| `governance` | `governanceSummary.govVersion`、`governanceSummary.entries[].govId/status/ref/notes` | GOV、REQ、waiver 的 canonical key | governance catalog、REQ/waiver 与基线指针 | 缺治理源写 `unverified` 并说明 governance source is unavailable；`status` 不转成审批结论 |
| `risk` | `riskSummary.riskVersion`、`riskSummary.entries[].riskId/title/preMitigationLevel/rcIds/residualRiskLevel/reqIds/vtCoverage/status` | RISK、RC、REQ、VT 的 canonical key | 风险/控制源、VT 报告与各自基线 | 缺风险源写 `unverified` 并说明 risk source is unavailable；字段不全写 `partial`，不推导残余风险 |
| `release` | `releaseStatus.lifecycle/safetyClass/currentVersion/lastReleaseDate/nextPlannedRelease/changeControlRef` | release/change-control/相关 BC 的 canonical key | release/change-control 记录与版本/对象基线 | 缺 release 记录写 `unverified` 并说明 release source is unavailable；生命周期字段空缺写 `partial`，不表示已发布 |

必需输入是当前 `root`、支持的 schema 版本、选定 `scope`、该范围的正式工件及其明确对象基线；不存在/不可读、非法 YAML/schema、越界路径、重复键/ID、未登记的派生文件手改或基线不符均为输入错误。不能把这些错误降成“可选来源缺失”。

九个 `views` 的外部/汇总来源均为可选视图输入：不存在、不可读、摘要格式不满足该视图约定或其基线无法核实时，固定输出该视图的 `unverified`、空引用集合和具体原因；不得省略该视图或终止其他可核对视图。已读到合法来源但只缺部分条目时为 `partial`，保留已经核对的引用并逐项列 gap。若主根/工件本身无法建立可信基线则仍按上一段失败，而不是把整个输入解释为九个空视图。

导出与检查分开：默认只检查，显式导出到允许的本地目标才写文件。上述必需输入错误必须失败；可选视图缺项按固定 `unverified/partial` 规则输出，不吞错或自动“修正”权威文件。

### 3.3 方法与工具边界

增强原六个共享方法，不复制人工版流程。新增 `reverse-engineer-domain`、`generate-code`、`update-template` 三个活动方法；三个现有 agents 仅连接适用方法。词汇对齐/发布接口、知识锤炼、ADR 来件、Intended Use 变更、只读 query、backlog/追溯和 SWAS/SEQ 各有明确输入/产出入口，按职责复用这九个方法，不为每个 prompt 新建角色或流程引擎。

工具位于 `.github\utilities\`，职责限于本地读/检查/导出/差异提案；输入解析、正式工件检查、覆盖/影响与模型视图已完成本次范围复核，Task8 实施摘要已完成本地验证但独立复核待办，其余工具未实施。Task6 的 base 只附加精确历史比较，验证目标仍为完整当前工作文件；实际发现/计数/JSON 边界见[工具契约](../../.github/utilities/README.md#artifact-checker)，不是 index-only hook。没有全局安装包、统一 skeleton 命令、运行循环、守护进程或状态数据库。Python 3.11+；标准库 `unittest`；YAML 使用 `PyYAML==6.0.2`，JSON Schema 使用 `jsonschema==4.23.0`。任务 2 已先建 manifest，再在项目 `.venv` 实际恢复并锁定传递依赖，没有安装全局、媒体或云端包。

校验、导出、报告收集、更新比较和 hook 处理的可重复逻辑统一写在 Python 中，本地与 CI 直接调用同一套脚本，不交付必需的 `.ps1` 包装层，也不要求额外的 PowerShell 7 运行时。使用 `pathlib.Path`、参数列表和显式 cwd；调用子进程使用 `shell=False`，失败保留实际输出与退出码。PowerShell 可以是用户当前的 Windows 终端，但不再承载另一套维护逻辑。

Git hook 的入口使用 Python，CI 保留原生 YAML 来声明触发、环境和 Python 调用。只有宿主确实要求时才添加最薄的启动适配，不复制校验/更新逻辑；在 Git for Windows 的实际提交试验中验证解释器、含空格路径、暂存内容与失败传播，再声明支持。Markdown、prompts 和 skills 仍承载方法与需要判断的活动，不因统一脚本语言而改写为 Python 执行流程。

维护者的工具回归 workflow 与下游的资料校验 workflow 分开。前者运行不分发的 tools tests；后者只调用候选内的工具/contracts 和项目工件，不能引用被排除的制作 tests、研究或演练文件。模板传播 workflow 也属于维护者侧，不默认复制给每个业务项目。

来源适配、音频转录、PDF/PPTX 等依赖单列为可选，不加入所有用户必装的核心环境。先做本地文本/转录、确定性图与候选报告；外部服务、SDK、渲染器和数据发送在对应任务中确认后才配置。原仓硬编码的管理 PPT 内容不复制，只提供参数化的同类输出能力。缺依赖返回明确输入/环境错误，不改用未批准的在线服务。

### 3.4 检查与副作用

校验器退出码：`0` 为该文档工具检查无发现，`1` 为发现文档/追溯违反项，`2` 为输入、配置、版本或基线不可读。输出含实际检查数、排除项与对象基线；没有正式工件时报告 `empty`，即使退出 0 也不称需求或应用通过。

`CheckReport.status` 为 `clean | invalid | input-error | empty`，`Finding` 的 code 与路径/行/目标分开。脚本层只捕获已定义的输入错误并映射到退出 2，不用宽泛异常捕获返回成功报告。`clean`/`empty` 均不表示业务验收通过。

只检查：格式、声明关系、可定位性、基线及约定的机械条件。它不能推断所有业务语义、认证专家批准或证明软件执行。规则影响报告列候选依赖和原因，最终语义判断仍由共享方法和责任人完成。

所有既有文件修改、hook 安装、CI 必需检查、跨仓写入、PR、发布和权限变更分别授权。传播默认提案模式；配置 `apply` 不等于获得授权。没有审阅或凭据时可交付干净差异提案，但不能登记已完成远端传播。

### 3.5 实施接口（任务中的测试使用这些名字）

| 模块与接口 | 输入与输出契约 |
|---|---|
| `artifact_io.parse_artifact(path, root)` | 读取本地正式 Markdown，返回 `Artifact`；含 `key`、`kind`、`scope`、`content_state`、`upstream`、`targets`、`acceptance_ids`、原文件定位。非法 YAML/路径/版本抛 `ArtifactInputError`，不返回空对象 |
| `check_artifacts.run_check(root, base_sha=None)` | `base_sha=None` 执行完整扫描；给定时必须读取该精确 Git 对象及目标快照。返回 `CheckReport`：`status`、`findings`、`checked_count`、`baseline`、`excluded` |
| `check_traceability.trace_report(root, delivery_ids)` | 从明确完整的验收清单核对目标与判据，返回 `CheckReport`；每项 `Finding` 有 `code`、`path`、`line`、`owner`、`target`、`message` |
| `export_model.export_view(root, scope)` | 返回 JSON 可序列化字典及约定的 `views` map，不写文件；来源散列与工件关系确定排序。脚本层检查/显式写入另行处理 |
| `export_model.check_model(root, scope, model_path)` | 校验并重算显式本地模型，返回 `CheckReport`；来源身份变化和手改视图分别报告，不自动修复 |
| `check_traceability.impact_report(root, base_sha, task_ids=())` | 精确 commit 与当前快照的 canonical 传递依赖候选；保留旧新身份、源位置和理由，不是语义批准 |
| `collect_implementation_report.build_report(root, object_sha, evidence_files, *, scope=None)` | 从精确本地 commit 盘点完整 BC 验收，读取显式既有 VT 文件/owned run 及原始报告；单 BC 保持三参数 API，多 BC 须选 scope。缺证据为逐目标 not-run，冲突/基线错误失败；不运行应用、复制结果账本或写回来源 |
| `plan_template_update.plan_update(base, local, candidate)` | 返回 `UpdatePlan`，包含 `changes`、`conflicts`、`preserved`；三方目录不写入。修改与删除均只给提案，缺旧基线是错误 |

`Artifact`、`Finding`、`CheckReport`、`UpdatePlan` 为窄用途 dataclass，定义在对应模块，不另建通用领域/执行框架。测试辅助函数只在工具 tests 内维护。

新正式工件的 frontmatter 必填 `schemaVersion`、`id`、`kind`、`scope`、`contentState`；`upstream` 与 `targets` 缺省为空列表。每条目标记录含完整 `target`、`criterionAnchor` 和可选 `testId`，目标以 owner 的验收锚点定位，判据锚点必须存在于当前 VT 正文。正文标题/验收锚点是可检索的独立目标，不从全文随意出现的 ID 字符串倒推验收库存。

`kind` 在 schema v1 中是一个封闭集合，恰好支持以下 32 个值：
`domain-model`、`subdomain`、`bounded-context`、`capability`、`use-case`、
`invariant`、`validation-scenario`、`backlog-item`、
`stakeholder-requirement`、`software-requirement`、`user-story`、
`architecture-building-block`、`architecture-decision`、`verification-test`、
`review-record`、`tool-qualification`、`development-log`、
`quality-attribute-scenario`、`context-map`、`published-interface`、
`aggregate`、`entity`、`value-object`、`factory`、`domain-service`、`policy`、
`domain-event`、`integration-partner`、`intended-use`、`risk-control`、
`architecture-specification`、`sequence-diagram`。未知 kind 必须报输入错误；
不提供通用扩展机制。规则可以保留为领域文档中的稳定 RULE 锚点，不强建
另一份规则正文。`upstream` 是完整来源引用的字符串列表；目标是上述结构
的记录列表。`confirmed` 内容还需 `confirmation` 的 `by`、`reference`、
`baseline`，校验器只核对声明结构，不认证该决定的身份/权限。

## 4. 授权关卡与完成判定

1. **能力关卡：** 六仓逐文件矩阵核对后，规格遗漏项必须进入有来源的变更；不能把未知写成不需要。
2. **契约关卡：** 元数据、数据 schema、现有 Markdown 合入方式及来源读写边界审阅后，才开始依赖它们的工具实现。不能先写解析器再倒推文档格式。
3. **工具关卡：** manifest 建立后才能恢复依赖；工具环境与下游应用开发登记分开，读取资料不要求先安装 Python 包。
4. **应用验收关卡：** 代码生成的实际工程、技术栈、位置与执行方式在任务 13 执行前由用户确认。工具采用 Python 不代表下游应用也选 Python；本轮没有授权创建演练应用。
5. **平台关卡：** 自动传播、hooks 安装、远端 PR、CI 必需检查及发布按具体操作授权；无授权时对应结果为未执行，不因此降低 ENH-10/11/14 的标准。

“六仓功能等价”只有在 ENH-01 的每个现有能力行有完成证据或责任人接受的明确替代方式，且 ENH-02 至 ENH-18 的适用项均通过时才可声明。原格式兼容、任意语言应用验证、法规符合性及全部 Agent 支持不在该声明内。外部 ADR/风险实例和不同消费 gitlink 版本的运行组合只登记为依赖，不以六仓源码盘点宣称已验证它们。

实施顺序、文件职责和逐任务检查见[增强计划](../plan/2026-10-14-ddd-functional-alignment.md)。
