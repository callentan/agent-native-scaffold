# 六仓功能对齐：增强规格

**状态：规划规格，未实施。** 2026-10-14 用户确认按功能等价对齐六个 `ddd-*` 仓库，保留单仓与下游技术栈中立，不要求原文件格式直接兼容。2026-10-15 进一步确认脚本基本统一使用 Python；取消必须交付的 PowerShell 包装层，不自研 CLI 或执行器。下文是实现计划的设计依据，不表示新工具、工件或工作流已交付。

当前实现基线为 `453189135af07f8ba5ab65dd4dd58879b8741c17`。原 P1/P2 的 38 文件与 P3 结果继续有效，README 的既有未提交排版不属于本增强。实施前先核对实际 Git；[原 P3 未完成项](../plan/roadmap.md#actual-acceptance)不能被新计划抹掉。

## 1. 范围与参考基线

只对齐以下六仓的**现有功能**，不复制其源码、业务内容、品牌或六仓部署形态。以下 commit 来自[历史来源登记](../research/source-register.md)；本轮规划没有重新审计它们的全部文件。

| 参考仓库 | 固定 commit | 关注职责 |
|---|---|---|
| ddd-bc | `bac263bea39988214b82cafb48f27e3a2136c534` | BC 工程约定、配置、领域输入与实现边界 |
| ddd-bc-prompts | `08f8219397d6fe6d000312f5956a493b1b28cc84` | SR/US/ABB/VT 派生、代码生成及维护工作流 |
| ddd-bc-templates | `00705aef6c70f855ef95588b0137cf7f2387efb0` | 实现侧工件表单 |
| ddd-subdomain | `e115ad4d03ac53359c608ce7d32262a508561496` | 领域工程、校验、hooks、传播与治理记录 |
| ddd-subdomain-prompts | `1aa44fd89f27d2913f72309d0ea4c8c7c60ed59c` | 访谈、建模、反向提取、评审与变更活动 |
| ddd-subdomain-templates | `59f98e352a150f99290a3855092298dbe11e0615` | 领域结构、模型和验证场景表单 |

任务 1 必须逐文件冻结能力矩阵，将原仓已有功能与本计划新增的自动化分别登记。统一使用 Python 是实现策略，不证明导出、自动追溯或三方更新各自都有原仓脚本对应。历史摘要、实例 repo 的使用情况和上游路线图不能冒充六仓已经实现的能力。读取受限时记录具体缺项，停止依赖它的等价判定；不猜测文件内容或追随新的 HEAD。

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

## 3. 设计约定

### 3.1 唯一事实源与结构

保留现有顶层资料目录；轻量项目可继续用 `domain-model\README.md`。确需多个领域时，正式资料按 `domain-model\subdomains\<slug>\contexts\<slug>\` 组织；不预填真实 SD/CTX，不要求业务边界等于服务或代码层。

工件 Markdown 正文拥有业务含义、规则和验收。正式工件的 YAML frontmatter 拥有机器身份、作用域、声明状态及上游/目标关系；原表单中重复表达这些元数据的状态/关系栏改为引用或删除。VT 的正文按 `criterionAnchor` 保存逐项判据，frontmatter 的目标记录只定位对应来源与判据。反向索引从这些关系派生，不再手写另一份映射。

统一机器身份为 `scope/id#anchor`；`scope` 由项目与上下文组成，例如演练中的 `sample/CTX-001/SR-001#sr-001-ac-02`。同一个 scope 下重复 ID 是错误，不同 scope 的同号工件允许存在。现有 REQ/SR 验收 ID 和锚点保留，不用改号掩盖历史。

声明内容状态为 `draft | confirmed | retired`，任务进度仍为 `todo | in-progress | blocked | review-ready | done`。实际结果为 `not-run | pass | fail | skipped`，当前适用性独立记录。确认记录必须指向具名来源和被确认基线；存在声明或链接不等于已核实人工身份。

### 3.2 BC 配置与派生模型

`bc-config.yaml` 是**可选的数据配置**，不是项目执行 manifest。字段为 `schemaVersion`、`projectId`、`boundedContexts`、`domainSources` 和开发登记的引用。每个领域来源明确 `kind`、`root`、仓库内相对 `path`、固定 `baseline`、`readOnly`；不把挂载根和仓库内路径拼成猜测，不保存凭据或复制开发命令。

`model.yaml` 只保存 `schemaVersion`、`scope`、来源对象基线、工件位置/ID/关系和实施摘要引用。正文不复制进去；内容声明仍回 Markdown，结果仍回 VT/真实报告。导出器采用确定顺序，保留完整原 ID，不在读取时联网或更新外部仓库。

导出与检查分开：默认只检查，显式导出到允许的本地目标才写文件。遇到未知版本、来源缺失、越界路径、重复键/ID、未登记手改派生文件或原基线不符时失败，不吞错或自动“修正”权威文件。

### 3.3 方法与工具边界

增强原六个共享方法，不复制人工版流程。新增 `reverse-engineer-domain`、`generate-code`、`update-template` 三个活动方法；三个现有 agents 仅连接适用方法。新增 prompts 仍是可选输入入口，不决定审批或工具权限。

工具位于 `.github\utilities\`，仅执行明确定义的本地读/检查/导出/差异提案；没有全局安装包、统一 skeleton 命令、运行循环、守护进程或状态数据库。Python 3.11+；标准库 `unittest`；YAML 使用 `PyYAML==6.0.2`，JSON Schema 使用 `jsonschema==4.23.0`。任务 2 创建依赖清单并实测后锁定传递依赖；本次规划不安装任何包。

校验、导出、报告收集、更新比较和 hook 处理的可重复逻辑统一写在 Python 中，本地与 CI 直接调用同一套脚本，不交付必需的 `.ps1` 包装层，也不要求额外的 PowerShell 7 运行时。使用 `pathlib.Path`、参数列表和显式 cwd；调用子进程使用 `shell=False`，失败保留实际输出与退出码。PowerShell 可以是用户当前的 Windows 终端，但不再承载另一套维护逻辑。

Git hook 的入口使用 Python，CI 保留原生 YAML 来声明触发、环境和 Python 调用。只有宿主确实要求时才添加最薄的启动适配，不复制校验/更新逻辑；在 Git for Windows 的实际提交试验中验证解释器、含空格路径、暂存内容与失败传播，再声明支持。Markdown、prompts 和 skills 仍承载方法与需要判断的活动，不因统一脚本语言而改写为 Python 执行流程。

维护者的工具回归 workflow 与下游的资料校验 workflow 分开。前者运行不分发的 tools tests；后者只调用候选内的工具/contracts 和项目工件，不能引用被排除的制作 tests、研究或演练文件。模板传播 workflow 也属于维护者侧，不默认复制给每个业务项目。

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
| `export_model.export_view(root, scope)` | 返回 JSON 可序列化字典，不写文件；来源散列与工件关系确定排序。脚本层检查/显式写入另行处理 |
| `collect_implementation_report.build_report(root, object_sha, evidence_files)` | 读取精确 Git 对象和实际报告，返回可定位摘要；缺证据保持 `not-run` 或输入错误，不推导 pass，不运行应用 |
| `plan_template_update.plan_update(base, local, candidate)` | 返回 `UpdatePlan`，包含 `changes`、`conflicts`、`preserved`；三方目录不写入。修改与删除均只给提案，缺旧基线是错误 |

`Artifact`、`Finding`、`CheckReport`、`UpdatePlan` 为窄用途 dataclass，定义在对应模块，不另建通用领域/执行框架。测试辅助函数只在工具 tests 内维护。

新正式工件的 frontmatter 必填 `schemaVersion`、`id`、`kind`、`scope`、`contentState`；`upstream` 与 `targets` 缺省为空列表。每条目标记录含完整 `target`、`criterionAnchor` 和可选 `testId`，目标以 owner 的验收锚点定位，判据锚点必须存在于当前 VT 正文。正文标题/验收锚点是可检索的独立目标，不从全文随意出现的 ID 字符串倒推验收库存。

`kind` 的本版枚举为 `domain-model`、`subdomain`、`bounded-context`、`capability`、`use-case`、`invariant`、`validation-scenario`、`backlog-item`、`stakeholder-requirement`、`software-requirement`、`user-story`、`architecture-building-block`、`architecture-decision`、`verification-test`、`review-record`、`tool-qualification`、`development-log`。规则可以保留为领域文档中的稳定 RULE 锚点，不强建另一份规则正文。`upstream` 是完整来源引用的字符串列表；目标是上述结构的记录列表。`confirmed` 内容还需 `confirmation` 的 `by`、`reference`、`baseline`，校验器只核对声明结构，不认证该决定的身份/权限。

## 4. 授权关卡与完成判定

1. **能力关卡：** 六仓逐文件矩阵核对后，规格遗漏项必须进入有来源的变更；不能把未知写成不需要。
2. **契约关卡：** 元数据、数据 schema、现有 Markdown 合入方式及来源读写边界审阅后，才开始依赖它们的工具实现。不能先写解析器再倒推文档格式。
3. **工具关卡：** manifest 建立后才能恢复依赖；工具环境与下游应用开发登记分开，读取资料不要求先安装 Python 包。
4. **应用验收关卡：** 代码生成的实际工程、技术栈、位置与执行方式在任务 13 执行前由用户确认。工具采用 Python 不代表下游应用也选 Python；本轮没有授权创建演练应用。
5. **平台关卡：** 自动传播、hooks 安装、远端 PR、CI 必需检查及发布按具体操作授权；无授权时对应结果为未执行，不因此降低 ENH-10/11/14 的标准。

“六仓功能等价”只有在 ENH-01 的每个现有能力行有完成证据或责任人接受的明确替代方式，且 ENH-02 至 ENH-14 的适用项均通过时才可声明。原格式兼容、任意语言应用验证、法规符合性及全部 Agent 支持不在该声明内。

实施顺序、文件职责和逐任务检查见[增强计划](../plan/2026-10-14-ddd-functional-alignment.md)。
