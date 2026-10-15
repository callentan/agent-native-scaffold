# 六仓功能对齐增强实施计划

**Task8 复核记录（2026-10-16）：** 两轮限定复审已关闭原三个 Important 及新 T8-F1-N1，最新修正为 `9a3055a`。原 378/395 全套及不同对象的局部结果各自保留，完整入口见[复审交接](../../logs/2026-10-15-ddd-alignment.md#task8-review)。

> **面向 AI 代理的工作者：** 用户于 2026-10-15 授权先提交当前变更、再执行本计划。先核对已有完成记录，不重复执行；按 subagent-driven-development 或 executing-plans 分任务推进，步骤以复选框跟踪。应用、音频/PDF、平台与发布的单独授权关卡仍保留。

**目标：** 在现有单仓骨架上提供六个 `ddd-*` 仓库现有功能的等价能力，并用逐项证据区分已交付、未执行和明确替代。

**架构：** 资料正文继续拥有业务事实，少量结构化元数据连接上下文、工件与验证；模型与实施摘要是可重建视图。共享方法负责需要判断的活动，项目内脚本负责确定性检查、导出与更新提案，Git/CI/现有 Agent 负责实际执行和授权。

**技术栈：** 维护工具 Python 3.11+、`unittest`、PyYAML 6.0.2、jsonschema 4.23.0；本地、hooks 与 CI 复用 Python 逻辑，不要求 PowerShell 包装脚本。下游应用技术栈仍未选择。

**规格：** [六仓功能对齐增强规格](../design/ddd-functional-alignment.md)，包含 ENH-01 至 ENH-18、完整固定版本和工具接口。执行者必须读取该文件，不能仅凭本计划标题推断行为。

**当前状态：** 任务 1–8 已完成各自的有限实现与范围复核，没有遗留的这些任务审阅发现。Task8 按用户单独选择复用现有 VT 运行，不另建结果输入账本。当前八方法、二十一 prompts、三模式，不是最终规划的九方法。Task9–18 未开始，下一步按既有授权实现可选治理/审阅/工具资格资料。原 P3 原生/人工记录和增强整体完成状态不随之升级，不创建应用。

**2026-10-15 规划修订（历史）：** 按用户“基本都用 Python 脚本”的决定，移除必需的 PowerShell 启动文件及其任务；宿主原生 YAML/最薄启动适配保留，方法正文仍归 Markdown。该次只修改规划，不将新增自动化一概归为原仓已有功能；当前实现进度以上述状态及逐任务记录为准。

**同日执行期补充：** 完整读取后确认存在原计划未承接的持续能力，用户选择完整纳入。原任务 3/4/5/8/9/10/11 扩展实际工件与活动，新增任务 15–18 承接可选领域源接入、来源适配、图/文档导出和交互账本；这些任务按依赖在 12–14 收口前完成，编号不表示可跳过依赖。

## 全局约束

- 用户选择的是功能等价，不要求旧 ID/字段/路径的自动导入导出兼容，不恢复六仓拆分或强制 submodule。
- 固定六仓现有版本；不把实例应用、路线图、自动批准/合并或通用执行器纳入已实现能力。
- 独立编写内容；内部材料不进入分发候选，不复制未获许可的源码或模板，不向第三方发送私有资料。
- 新字段不产生第二份事实；元数据、验收正文、VT 实际结果和派生视图各有单一归属。
- 先核对 Git、原文件和范围。此前 README 排版已授权提交为 `1a6f594`，后续仍保留每次开始时发现的无关改动，不默认覆盖。
- 没有完整必要输入时停止受影响任务，不把缺项当默认值；任务失败、未执行、空检查与通过分别记录。
- 不自动初始化应用、安装依赖、安装 hook、变更 CI 门禁、回写外部来源、推送、PR、发布或改变权限。
- 文档工作可在应用未配置时继续；生成代码的实际应用验收须在任务 13 先获独立输入和授权。
- 原六个方法、三个模式和现有 prompt 的能力保留；增强以活动拆分，不增加角色流水线。
- 可重复维护逻辑统一用 Python，直接调用项目解释器；本地/hooks/CI 不维护三套实现，不把 PowerShell 7 设为工具使用前提。
- Task2 契约/parser、Task3 表单、Task4 方法/入口、Task5 资料契约、Task6 检查器、Task7 模型/追溯和 Task8 实施摘要已完成本次范围复核，结果见各自记录。Task9–18 未实施；不能把其他计划路径当成已存在的功能。

## 1. 文件结构与职责

路径均相对仓库根；以下是实现范围，不要求提前创建空文件或正式业务实例。

| 文件组 | 创建或修改的具体路径 | 职责 |
|---|---|---|
| 制作依据 | 创建 `docs\research\ddd-capability-matrix.md`；修改本规格、本计划、`docs\plan\decisions-and-risks.md`、`docs\design\repository-blueprint.md`、`docs\plan\roadmap.md` | 六仓逐文件来源、等价判据、增强范围与进度；不分发给下游 |
| 元数据契约 | 创建 `.github\contracts\artifact.schema.json`、`bc-config.schema.json`、`model.schema.json`、`implementation-report.schema.json`、`README.md` | 数据版本、身份、关系、来源和状态；不是运行/权限配置 |
| 领域表单 | 创建 `_templates\items\subdomain.md`、`bounded-context.md`、`capability.md`、`use-case.md`、`invariant.md`、`validation-scenario.md`、`backlog-item.md` | SD/CTX/CAP/UC/INV/业务场景/BL 的可复制结构 |
| 数据表单 | 创建 `_templates\config\bc-config.yaml`、`_templates\reports\implementation-report.yaml` | 可选配置与报告空表单；不预置真实项目或结果 |
| 原工件/入口 | 修改七个既有 `_templates\items\` 表单及 `domain-model`、REQ、SR、US、architecture、verification、logs 的 README；按需修改根 README/AGENTS | 新契约与旧轻流程共存，说明正式落点、来源、当前元数据和结果 |
| 原方法/模式 | 修改 `.github\skills` 中六个既有 SKILL、三个 `.github\agents`、相关 instructions 与五个原 prompts | 沿用单份方法并接入新资料和工具 |
| 新活动方法 | 创建 `.github\skills\reverse-engineer-domain\SKILL.md`、`generate-code\SKILL.md`、`update-template\SKILL.md` | 反向提取、初始代码生成和安全模板更新 |
| 可选活动入口 | 创建 `.github\prompts\domain-interview.prompt.md`、`reverse-engineering.prompt.md`、`derive-requirements.prompt.md`、`design-architecture.prompt.md`、`plan-verification.prompt.md`、`generate-code.prompt.md`、`assess-impact.prompt.md`、`review-artifacts.prompt.md`、`update-template.prompt.md` | 本次输入与方法链接，不复制流程或授予权限 |
| 本地工具 | 创建 `.github\utilities\artifact_io.py`、`check_artifacts.py`、`check_traceability.py`、`export_model.py`、`collect_implementation_report.py`、`plan_template_update.py`、`README.md`、`requirements.txt`、`requirements.lock` | 范围明确的独立 Python 脚本，直接调用，不另建必需的 shell 包装、统一 CLI、执行引擎或后台服务 |
| 工具测试 | 创建 `.github\utilities\tests\__init__.py`、`helpers.py`、`test_artifact_io.py`、`test_artifact_check.py`、`test_traceability.py`、`test_model_export.py`、`test_implementation_report.py`、`test_template_update.py`、`test_hooks.py`、`test_distribution.py`；夹具在同目录 `fixtures\` | 真实文件/Git 正反例；不预建下游的 `src\tests` |
| 审阅/工具治理 | 创建 `docs\ai-tooling.md`、`_templates\items\review-record.md`、`tool-qualification.md` | 工具版本、范围、人工决定与交互摘要，不自证审批或合规 |
| 可选工程接入 | 创建 `.github\hooks\pre-commit`、`commit-msg`、`README.md`、`.github\utilities\install_hooks.py`、`.github\workflows\validate-artifacts.yml`、`tooling-tests.yml`、`propose-template-updates.yml` | Python Git 入口、明确安装、同源校验和提案传播；tooling-tests/传播 workflow 为维护者侧，平台副作用仍须授权 |
| 更新/分发说明 | 创建 `docs\template-updates.md`、`docs\distribution.md`；修改 `docs\development.md`、`docs\agent-support.md`、`.gitignore`、PR 表单 | 维护工具与应用环境分开，文件级分发与版本差异、兼容限制 |
| 制作验收 | 创建 `verification\ddd-alignment.md`，日志沿现有表单 | ENH-* 对象/结果/未执行记录；制作验收、夹具和日志不进入候选 |

### 完整来源盘点后的新增承接文件

| 任务 | 具体文件 | 作用与边界 |
|---|---|---|
| 3 | `_templates\items\quality-attribute-scenario.md`、`context-map.md`、`published-interface.md`、`aggregate.md`、`entity.md`、`value-object.md`、`factory.md`、`domain-service.md`、`policy.md`、`domain-event.md`、`integration-partner.md` | 战略/战术/QAS 的可选表单；不把形式强加给轻量维护任务 |
| 4 | `.github\prompts\distill-domain.prompt.md`、`glossary-sync.prompt.md`、`published-interface.prompt.md`、`query-artifacts.prompt.md`、`review-backlog.prompt.md`、`amend-intended-use.prompt.md` | 分别承接来源活动，复用现有方法，不复制正文、不自动批准 |
| 5 | `_templates\items\sequence-diagram.md`、`architecture-specification.md`、`verification-test.feature`；`.github\prompts\sequence-diagram.prompt.md`、`build-architecture-spec.prompt.md`；`.github\instructions\architecture.instructions.md`、`coding.instructions.md`、`security.instructions.md` | SEQ/SWAS、Gherkin companion 及规则；沿用项目真实栈与必要装配例外，不预置应用 |
| 9 | `_templates\items\intended-use.md`、`risk-control.md`；`docs\governance.md` | 来源确有的可选监管/风险资料引用，责任人与确认关卡，不替代外部风险分析或合规决定 |
| 15 | `.github\utilities\setup_domain_source.py`、`tests\test_domain_source.py`；`docs\domain-sources.md` | Python 预检与明确批准的领域源接入，不默认子模块或提交 |
| 16 | `.github\utilities\extract_source.py`、`score_candidates.py`、`transcribe_audio.py`、`requirements-media.txt`；`tests\test_source_extraction.py`、`test_candidate_scoring.py`；`docs\source-extraction.md` | Markdown/plain-text、转录、DOCX/音频适配、候选与置信度；外部依赖和数据发送单独授权，不发展提案执行器 |
| 17 | `.github\utilities\render_traceability.py`、`render_architecture.py`、`render_presentation.py`、`requirements-rendering.txt`；`tests\test_rendering.py`；`docs\document-exports.md` | 本地关系图/SEQ/SWAS 与必须提供的参数化 presentation 等价输出；PDF/PPTX renderer 依赖按格式授权，显式输入/输出，无 demo fallback、硬编码内容或线上 CDN 默认依赖 |
| 18 | `.github\utilities\log_interaction.py`、`summarize_usage.py`、`tests\test_interaction_log.py`；`_templates\reports\ai-interaction-log.csv` | 按真实输入记账/统计，不抓取完整聊天、秘密或估算未提供的计费 |

若任务 1 发现此表没有承接的六仓现有功能，先按来源修改规格、验收与对应文件职责，再开有边界的任务。不得为宣称对齐而删除能力行。专用领域/风险文件只在确认其属于六仓现有能力后进入这套变更，不从业务实例推导。

## 2. 依赖与执行关卡

| 任务 | 依赖 | 独立交付物 |
|---|---|---|
| 1 | 无 | 完整来源/能力矩阵与范围冻结 |
| 2 | 1、契约审阅 | 可解析且拒绝无效输入的元数据/schema/工具环境 |
| 3 | 2 | 完整领域工件及多上下文填写路径 |
| 4 | 3 | 领域活动和反向提取的可用方法 |
| 5 | 2、3、4 | BC 派生/评审/初始生成与既有修改契约 |
| 6 | 2、3、5 | 可重复工件检查 |
| 7 | 6 | 派生模型、验收覆盖与语义影响入口 |
| 8 | 5、7 | 只读来源下的实施摘要桥接 |
| 9 | 1、6 | 人工审阅与工具资格记录 |
| 10 | 6、7 | 可选 hook/CI 实际失败传播 |
| 11 | 6、7 | 三方更新与多目标传播提案 |
| 12 | 3–11、15–18 | 自包含增强候选与原骨架回归 |
| 13 | 12、应用/平台验收授权 | 端到端行为与真实客户端结果 |
| 14 | 13、全部矩阵行有结论 | 功能等价结论与发布前交接 |
| 15 | 2、6 | 可选领域源接入与原文保护 |
| 16 | 2、4、6 | 可定位的来源提取/评分与可选转录 |
| 17 | 5、7、8 | 不造数据的关系图和文档导出 |
| 18 | 2、9 | 最小交互/用量账本与统计 |

任务 4/5 都触及原方法与模式，按 4→5 串行，不能并行覆盖这些入口。任务 8/9/10/11 的工具测试可在各自依赖满足后独立验证，但 shared methods/开发说明的修改仍按一个写入者串行合入。不因可独立验证而另起工作流或扩大代理数。

<a id="maintainer-checks"></a>
## 3. 制作仓维护者的执行命令与测试约定

本节的工具测试只用于维护者完整 checkout，不随下游候选分发，也不是下游运行 parser/checker 的前提。下游使用说明只连接已分发的模块、contracts、依赖清单和开发登记；维护者的 RED/GREEN、测试数量、对象基线与历史导航留在本计划和[制作日志](../../logs/2026-10-15-ddd-alignment.md#task6)。

任务 1 阶段没有创建 `.venv` 或安装包；任务 2 已先登记维护环境、创建 manifest，再恢复项目自己的 `.venv`，实际环境为 Python 3.13.15。现有 parser/schema 与 Task6 checker 测试使用这一环境，不安装新依赖。checker 的正式发现、精确 base 与 JSON 契约已实现，第 1 轮两项修正已完成聚焦回归和限定复审；hooks/CI 仍是后续任务。多步维护逻辑放入 `.py`，调用子进程使用参数列表、显式 cwd 与 `shell=False`；本地、hooks 和 CI 直接复用脚本，不把个人绝对路径写进模板。

| 检查 | 明确 cwd | 可执行程序及参数 |
|---|---|---|
| 定向 Python 测试 | 当前仓库根 | `.venv\Scripts\python.exe -B -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_artifact_check.py -v`；parser 定向时替换为 `test_artifact_io.py` |
| Task6 修正的受影响模块回归 | 当前仓库根 | `.venv\Scripts\python.exe -B -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p "test_artifact*.py" -v`；发现/执行/跳过另由实际 receipt 核对，不重跑无变化的 schema 套件充当修正证据 |
| 全部工具测试 | 当前仓库根 | `.venv\Scripts\python.exe -B -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_*.py -v`；须另核对真实发现/执行/跳过数量 |
| 维护工具源码与测试语法 | 当前仓库根 | `.venv\Scripts\python.exe -X utf8 -m compileall -q .github\utilities` |
| 工件检查（已实现并经本次范围复核） | 当前仓库根 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_artifacts.py --root <本次已解析根目录>`；JSON stdout，可显式加 `--report <已存在获准目录>\new-artifacts.json`，不覆盖旧报告 |
| 显式历史比较（已实现） | 当前仓库根 | 上行增加 `--base <已核对的完整 commit>`；精确对象不可读退出 2；保留完整当前正式库存，含未暂存/未跟踪文件，不是暂存区 hook |
| Task7 定向回归 | 当前仓库根 | 与完整测试相同的 unittest discovery 命令，将 `-p` 分别设为 `test_traceability.py`、`test_model_export.py`；全套仍保留既有 schema/parser/checker |
| Task7 覆盖/影响与模型 | 当前仓库根 | 按[实际工具契约](../../.github/utilities/README.md#traceability)使用 `check_traceability.py --root <资料根> --delivery <完整 ID>`，或 `--base <完整 commit> --task <任务 key>`；模型用 `export_model.py --root <资料根> --scope <scope>`，仅显式 `--output` 写新文件，`--check` 重算不修复 |
| Task8 定向回归 | 当前仓库根 | 完整 unittest discovery 命令的 `-p` 设为 `test_implementation_report.py`；bridge 与保留模型机制使用 `test_model_export.py`，最终仍执行完整 `test_*.py` |
| Task8 收集实施报告 | 当前仓库根 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\collect_implementation_report.py --root <本地 checkout> --object <完整 commit>`，可重复 `--evidence <VT相对路径[#owned运行]>`，多 BC 用 `--scope`；仅显式 `--output` 创建新本地报告 |

Task 2 的维护者用例分为 [parser 行为](../../.github/utilities/tests/test_artifact_io.py)和[四类 schema 数据](../../.github/utilities/tests/test_contracts.py)；[helpers](../../.github/utilities/tests/helpers.py)只创建项目 `.venv` 下的临时文件和无远端 Git fixture。Windows 边界夹具用本地 junction 和字节锁，junction 创建失败报错而非静默 skip；非 Windows 权限若被宿主特权绕过会明确报告跳过。它们不是下游工具的运行依赖，测试代码也不等于执行证据。

Task6 的[真实文件/Git/CLI 用例](../../.github/utilities/tests/test_artifact_check.py)不替换上述套件。原始 stdout/stderr、cwd、退出码、发现/执行/跳过和保护字节摘要记录在获准会话证据目录；CHECK-14 用真实零发现/全跳过 runner 控制例核对证据门禁，不在产品测试里添加“断言自己存在”的用例。工具 `empty`/退出 0 和回归零发现是不同情形，后者不得作为回归通过。有限 OS 失败注入单列，不冒充真实权限配置。

表中使用 Windows 路径，直接执行项目 Python，不需要 `.ps1`。其他宿主按实际环境登记解释器位置，不把 Windows 的 `.venv\Scripts\python.exe` 照搬到 Linux。尖括号表示执行时从当前工作区解析的路径/Git 对象参数，不是虚构的可执行值。检查器使用 `pathlib.Path` 处理路径，每个参数单独传递；命令与 cwd 的真实记录在执行时保存。

所有 Python 工具任务先编写行为测试、运行看到预期失败、实现最小代码、重跑，再提交。测试实读夹具/真实 Git 对象，不只 grep 代码或模拟返回值。文档方法用真实使用正反例验证，不把“出现某个词”当流程正确。

## 4. 逐任务计划

### 任务 1：冻结六仓能力基线

**文件：** `docs\research\ddd-capability-matrix.md`、本规格、本计划、P0 决策与蓝图。

- [x] 读取规格六个完整 commit 的递归树及所有 active 约定、表单、工作流、工具、hook/pipeline；185 个 blob 全文、10 个 roadmap 范围阅读，所有 252 entries 有分类；没有执行上游脚本。
- [x] 每个文件登记 repo/完整 commit/路径/object/读取覆盖，能力登记输入输出、前提、写入和目标任务/判据；散列、漏项/重复项及引用行界限已核对。
- [x] 区分现有方法/脚本、上游提案、实例占位与未解析外部依赖；保留不同消费 gitlink 版本，不从目录或路线图推导运行成功。
- [x] 用户确认完整纳入新发现能力；增补文件职责和 ENH-15–18，功能替代与 Python 优先不变。音频/PDF/平台实际执行仍由独立关卡控制。
- [x] 已完成回源逐行审阅，更新 P0 中“七表单/六方法/无工具”的增强适用范围，同时保留原版已交付与 P3 结果；本项只关闭范围审阅，不表示任何后续实现完成。

| 原 P0 决策 | 原版边界（仍有效） | 新发现范围的确切承接 |
|---|---|---|
| D02 | 七表单、六方法、三 agents、五 prompts 和无自研执行层仍是首版基线 | Task 1 / ENH-01 负责来源范围；Task 2 / ENH-02、ENH-06 承接契约；Task 3 / ENH-03、Task 7 / ENH-08、Task 8 / ENH-12 承接新增结构化桥接；Tasks 9、15、16、17、18 / ENH-09、ENH-15、ENH-16、ENH-17、ENH-18 是增强，不改写首版清单 |
| D08 | 首版不预置专用领域/监管套件，不宣称合规资格 | Task 3 / ENH-03 的 QAS/战术资料、Task 8 / ENH-12 的治理/风险引用、Task 9 / ENH-09 的资格记录和 Task 17 / ENH-17 的 SWAS/PDF 只作可选、可追溯输入，不产生合规或批准结论 |
| D10 | 轻量 DDD 只要求术语、关系、规则、上下文职责/交互和来源，不强制战术模式 | Task 3 / ENH-03、Task 4 / ENH-04、Task 5 / ENH-05、Task 8 / ENH-12、Task 16 / ENH-16 分别承接新增领域工件、派生、桥接和候选提取；不改变轻量项目的最低填写边界 |
| D11 | V-model 仍区分业务验收、软件验证、覆盖/影响和实际适用性，US 不是必经层 | Task 2 / ENH-02、Task 6 / ENH-07、Task 7 / ENH-08、Task 8 / ENH-12、Task 14 / ENH-14、Task 17 / ENH-17 承接新增契约、检查、桥接和导出引用；不把映射完整写成验证通过 |

以上是任务 1 已完成的范围映射和原版边界记录，不是增强整体验收结论。Task 2
的输入契约/parser、Task3–8 的有限交付与范围复核见下节；Task9–18 未实施，不能从本表推导整项增强完成。

**退出：** ENH-01；六仓树条目都有归属，现有能力没有“无任务/无判据”行。未经这一步，后面只能作设计讨论，不能声明全面对齐。

**任务 1 结果：** 来源盘点完成；这一阶段不包含目标功能实现，Task 2 的实现和审阅状态见下节。矩阵 44 组 current 能力存在交叉，不能把数量当交付进度；6 组上游提案、1 组未解析依赖单列。四处超出文件末尾的来源行号已按实际 manifest 修正，没有改动源码或掩盖未读内容。

### 任务 2：元数据、schema 与工具环境

**当前状态：实现及本次范围审阅完成。** 初始对象 `4b833df` 的三项反馈已在 `322cd90` 修正；父会话核对根错误定位回归、分发依赖和状态修订，并独立复跑 144 项、0 跳过、退出 0。真实证据与限制见[制作日志](../../logs/2026-10-15-ddd-alignment.md#task2-review-1)；不包含后续导出器、跨文件追溯或应用验收。

**文件：** 四个 contracts 及其 README、`artifact_io.py`、依赖/工具 README、`tests\__init__.py`、`tests\helpers.py`、`test_artifact_io.py`、`test_contracts.py`、`.gitignore`、`docs\development.md`；本段与当日日志只记录 Task 2。

- [x] 按已冻结规格与 Task 2 brief 核对事实归属、作用域、状态及现有资料无损演进；schemaVersion `1`，unknown version、布尔/字符串等类型错误不降级解释；旧正文和表单未修改。
- [x] 按规格 3.2.1 分开测试主输入与可选视图**数据契约**：parser 对真实 root/schema/scope 错误失败，model schema 拒绝缺失/非法主对象基线；九个视图分别验证 unverified+空引用+具体 gap、partial+已知引用+gap，以及 available 的结构。可选源实际查找/派生和基线真实性留给 Task 7/8，本任务不假造 exporter 运行。
- [x] 将 `kind` 固定为规格列出的 32 个值，并为每个值各写至少一个可解析且 schema-valid 的真实 fixture：`domain-model`、`subdomain`、`bounded-context`、`capability`、`use-case`、`invariant`、`validation-scenario`、`backlog-item`、`stakeholder-requirement`、`software-requirement`、`user-story`、`architecture-building-block`、`architecture-decision`、`verification-test`、`review-record`、`tool-qualification`、`development-log`、`quality-attribute-scenario`、`context-map`、`published-interface`、`aggregate`、`entity`、`value-object`、`factory`、`domain-service`、`policy`、`domain-event`、`integration-partner`、`intended-use`、`risk-control`、`architecture-specification`、`sequence-diagram`；32 个 parser 正例和另 32 个 schema 正例实际运行，未知 kind 失败。
- [x] 先创建 `.github\utilities\requirements.txt`（两项 direct pins）与工具环境登记，再创建本项目 `.venv` 并恢复。实际 Python 3.13.15，六项依赖按 `pip freeze` 锁定，`pip check` 无冲突；没有全局/媒体/云端安装。
- [x] 先编写真实夹具测试：正常文档、两个 scope 同号、同 scope 重号、任意层重复 YAML 键、未知状态/版本、越界路径、缺必要字段。保留以下最小测试形状，完整用例在实际测试文件：

```python
import tempfile
import unittest
from pathlib import Path
from artifact_io import ArtifactInputError, parse_artifact

class ArtifactIOTests(unittest.TestCase):
    def test_rejects_unknown_schema_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "REQ-001.md"
            path.write_text(
                "---\nschemaVersion: 9\nid: REQ-001\n"
                "kind: stakeholder-requirement\nscope: sample/CTX-001\n"
                "contentState: draft\n---\n# Requirement\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ArtifactInputError, "UNSUPPORTED_SCHEMA_VERSION"):
                parse_artifact(path, root)
```

- [x] 用真实 model 数据验证九个固定视图，单独保留 `sequenceSummary`、`governanceSummary`、`riskSummary`、`releaseStatus` 的 canonical 引用与 source baseline 指针；缺视图、缺字段、伪造 passed/approved 状态及空 gap 均有反例。只验证数据，不宣称读取过对应可选来源。
- [x] 先运行得到模块不存在的初始错误，再运行可读真实文件但不校验的最小实现：6 个 parser 测试方法产生 12 个行为失败；四个 permissive schema 的 4 个方法产生 14 个失败（均含参数化子例，不将失败数当方法数）。
- [x] 实现不可变 dataclass、SafeLoader、原始 YAML node 图和归一化后重键检查、本地 schema 与准确行号。自审先补 RED 再修复 BOM 错误位置、嵌套 `<<` 重键及 safe-tag 无效值的异常归一化，保留原始原因；不联网、不执行正文。
- [x] 初始实现 `4b833df` 重跑：143 个测试方法发现/执行、0 跳过、0 失败/错误；73 个 parser、70 个 schema/Git 数据测试。5 个实际 Python 文件通过 compileall，4 个文档示例实际解析/校验。此处保留原基线结果；修正后的新结果另行追加，证据与限制见[当日日志](../../logs/2026-10-15-ddd-alignment.md#task2)。

`helpers.py` 只为测试创建真实文件/Git：`seed_git_repo(root)` 在临时目录写一份 README，显式测试身份提交并返回完整 commit，不建远端；`write_artifact(root, schema_version, id, scope, kind, upstream, targets, acceptance_ids)` 写本规格格式的实际 Markdown。后续 trace 夹具由任务 7 扩展该文件。期望值由测试独立给出，不调用被测解析器生成期望。

**已落实的接口选择：** `parse_artifacts(paths, root) -> tuple[Artifact, ...]` 只检查显式集合内的重复 scope/id；`Artifact.acceptance_ids` 保存 `scope/id#anchor`，`acceptances` 另保留完整标题 ID 与两处行号。BC 使用 `developmentRegistration` 引用已有登记，model 使用 `source` / `implementationReports`，实施报告按 `entries[].execution` / `applicability` 分离历史结果和适用性。字段与唯一示例见[契约说明](../../.github/contracts/README.md)，不是原字段兼容声明。

**退出：** ENH-02、ENH-06 的输入契约；新语法与旧保留方式都可定位，读取空白模板无需先安装工具。

<a id="task3"></a>
### 任务 3：完整领域工件与多上下文

**当前状态：实现及本次独立范围复核完成。** 提交 `0aef102` 新增 18 类可选表单，保护 parser/schema 与轻量路径。范围审阅指出的页尾旧状态已纠正；父会话复跑 144 项、0 跳过，独立消费者另使用 UC/QAS/Published Interface 三种表单并保留缺项。结果及限制见[制作日志 Task3](../../logs/2026-10-15-ddd-alignment.md#task3)；不是业务执行、全场景可靠性或人工批准。

**文件：** 18 个新领域/QAS/战术表单；领域、REQ、verification 指引；REQ/VT 原表单的必要接入；根 README 的相关表单导航；本任务状态与制作日志。未修改 parser/schema、共享方法/角色/prompt、应用或仓库测试。

- [x] 使用父会话事先固定的 `task3-case-input.md`，在会话产物保留输入副本和摘要：两个上下文、一个 capability、借用正常/拒绝路径、源规则与 INV、场景及两个 BL；失效后处理和并发保持未决，没有重新盘点参考源。
- [x] 独立编写 SD/CTX/CAP/UC/INV/validation/BL 的实际字段，使用已有 schemaVersion/kind/scope 契约，所有空表为 draft；来源事实、推导候选与问题分开。
- [x] 按冻结的 DOMAIN-05/17/18 范围增补 QAS、context map/Published Interface 与七类战术角色及 integration partner；度量、边界、版本和交付政策缺失时保留问题，不预填架构或保证。
- [x] 同一执行者从实际分发表单复制并逐字段应用固定输入，使用未改动的 Task2 `parse_artifact/parse_artifacts` 验证全部 18 类的正例、两个 scope 的 UC-001 和同 scope 重号反例；核对具体目标及本地判据。此为自用操作，不是假称新的独立消费者或业务执行。
- [x] 原轻量 README 正文与锚点保留；隔离副本显式补元数据前后，所有者标记及正文原始字节一致。候选链接不依赖制作资料，仓库无业务实例或自动迁移。
- [x] 保存有限文档检查、真实工具回归、自审及检查脚本修正的记录；表单/指南与 Task3 状态纳入本次局部提交。业务/软件行为、QAS 度量及战术决定没有验证通过结论。

**退出：** ENH-03 的本任务文档范围已实现并完成自用和有限独立复核；18 类表单可复制、结构可解析、来源/未知边界可定位，旧资料无需搬移。Task4–8 的当前状态另见下节；Task9–18、应用执行与原 P3 关卡未关闭。

<a id="task4"></a>
### 任务 4：领域访谈、评审与反向提取

**当前状态：本次范围复核完成。** `f8df392` 新增独立反向方法及十个薄 prompts，保留原六方法和三模式。独立审阅无重大问题，父会话在该对象复跑 144 项、0 跳过；独立修改后消费者的三个草稿也实际解析。原基线仍为修改前那次正确控制观察，不采用修改后临时编写的“baseline”作比较。结果与限制见[制作日志 Task4](../../logs/2026-10-15-ddd-alignment.md#task4)；不是 App 原生、人工或业务运行验收。

**文件：** `define-requirements`、`verify-change`、新 `reverse-engineer-domain`，十个 interview/reverse/review/impact/distill/glossary/interface/query/backlog/intended-use prompts，planner 与 plan-feature 的薄路由；README/AGENTS/agent-support 的导航、当前计划及追加日志。共 20 个仓库文件，不修改 parser、schema、表单、测试或后续工具。

- [x] 复用已记录的独立基线：五个固定输入覆盖来源不完整、2/3 冲突、词义差异、接口/证据缺项与期限压力。原基线控制正确；七个基线产物及输入保留，不捏造 RED 或可靠性提升。
- [x] 增强 define 的访谈/迭代确认、知识锤炼、词汇/接口、来件 ADR 与可选 Intended Use；新逆向方法以实际文件/版本、外部对象或提供片段定位记录候选，区分 `observed | inferred | uncertain`，缺原路径/行不编造，规则先于 INV。
- [x] 将领域来源活动映射到实际方法小节与十个薄入口；verify 保留完整验收库存、精确目标与反查，新增工件/BL 审阅和只读查询。状态、元数据关系、未知项与授权保持原契约；未引用尚不存在的方法、治理或架构表单。
- [x] 同一实施者完整读取三份当前方法并应用同一五案例，分别保留 after-case 决策记录及 UC/QAS/PI 三份实际填表草稿；现有 parser 成功解析三份，既不确认业务事实也不认证覆盖。没有选定 2 或 3，没有改源、通知或发明缺失验收 ID。
- [x] 有限自用包含新领域候选笔记与既有陈述/接口的修订提案；额外核对无 ADR/Intended Use 原文的停点和实际空白领域库存。具备真实来件后的修订、完整消费者影响、App 原生与人工使用未测，不由文件存在或自用推导一般可靠性。
- [x] 核对当前分发依赖闭包、YAML、实际相对链接/锚点与轻量路径；在现有 `.venv`、明确仓库 cwd 只运行一次既有全套测试：`144 tests in 4.654s; OK`，0 跳过、退出 0。方法/入口及本段随本次限定提交保存，证据在获准会话产物，不升级历史 P3 结论。

**退出：** ENH-04 的本任务文档范围已实现并经有限自用/独立复核；反向候选可回查来源、置信性质、确认需要与停点。Task5–8 状态见下节；Task9–18 及 Task13 的实际行为/客户端/人工验收未完成，不能声明增强整体等价、可靠性提升或新入口原生发现已通过。

<a id="task5"></a>
### 任务 5：BC 派生、评审与安全代码生成

**当前状态：本次范围复核完成。** 实现对象 `5d39f407630d557b8b0bd51fa12efdde0b5bfef8`，起点为 `d7693a8e481dd84effc155378ae16c255c04d9b7`；独立审阅无重大问题，十例独立修改后观察仅作显式文件使用。父会话在实现对象复跑 144 项、0 跳过。当前八方法、二十一 prompts、三模式。结果与限制见[制作日志 Task5](../../logs/2026-10-15-ddd-alignment.md#task5)及[复核追加](../../logs/2026-10-15-ddd-alignment.md#task5-review)。

**文件：** 五个既有 SR/US/ABB/ADR/VT 表单与四份指引；SEQ/SWAS/feature/BC-config；specify/implement/verify 与新 generate-code；六个薄 prompts、三份代码规则；planner/implementer 的薄路由、README/AGENTS/agent-support、本计划当前状态和追加日志，共 33 个文件。reviewer 通过原 verify 入口读取新增 BC 小节，不改角色或权限；原十五 prompts 无需再复制路由。

- [x] 明确 REQ/UC/INV/CAP/QAS 到 SR 的有源推导、可选 US 切片、独立 ABB/ADR 及 VT 计划。元数据独占身份/内容状态/声明关系，正文解释含义与判据；US 不作必经桥梁，ABB/VT 不组成角色流水线。
- [x] 提供 SEQ 的已知参与者、方向、成功/拒绝/错误与缺口字段；只在实际集成/事件契约要求时使用异步，不把概念交换改成虚构服务。SWAS 按业务/逻辑/运行/部署及现有九视图引用真实来源；缺源保持 partial/unverified，不编造部署、风险或批准。
- [x] `.feature` 独占 Gherkin 正文，VT 维护真实 companion/基线导航、目标及独立判据。空表没有业务演员或安全关键标签；实际副本仅作文本/映射核对，Gherkin parser/runner 与所有行为均 `not-run`。
- [x] 架构/编码/安全规则使用有限 globs 和代码路径未匹配时的显式读取后备；区分合法 composition root 与领域/控制逻辑绕过，沿实际语言/项目，不预建四层、平台或权限。
- [x] generate-code 是独立文件方法：核实来源/开发输入、准确读写目录/全部目标、现有内容、拟生成说明和 trace marker；非空/越界冲突停写，跳过不是完整生成。既有代码用 implement-task 的任务/diff/复现路径；独立文档修正不等待应用输入。
- [x] 对同一十例留下自用决策和实际填表：11 个表单副本（9 个 Markdown、BC-config、feature），现有 parser 解析 9 个 draft、5 个合成验收、3 条独立目标；保留 SR 拒绝与 ABB 约束两个精确未覆盖项。实际 schema 校验 BC/九视图，wrong-owner 与非固定基线负例保持可定位，未修改 parser/schema/tests。
- [x] 实际原 owner 文件始终为 225 字节、摘要与修改前相同；非空与越界只做预检不写入。原十例的缺身份/审批/运行输入没有用合成数据解阻；另一个明确合成 Markdown 链接只改一处、周围字节保留，不冒充原案例未提供的真实目标。
- [x] 核对分发闭包、元数据和实际相对链接/锚点，保留旧轻量资料与原 P3 观察；现有 `.venv`、明确仓库 cwd 仅运行一次原全套：`144 tests in 4.977s; OK`，0 跳过/失败/错误、退出 0。各契约/入口与本段作为本次限定提交对象，完整 SHA 在实际 Git/本机报告记录。
- [x] 独立审阅实际 33 文件变更；独立消费者只读同一十例，明确缺项与停点，没有另造基线或执行 parser/应用。父会话复跑原 144 项、0 跳过、退出 0；消费观察后重新确认实现 HEAD 与工作树/暂存区未变。

**退出：** ENH-05 的本任务资料契约及有限自用/独立复核完成；原基线控制正确，不宣称纪律修复或可靠性提升。真正代码生成、原生 runner、客户端/人工、PDF/平台与审批均未验收，需 Task13 等分别满足输入/授权。Task6 的前置资料关卡已满足，后续按计划实施；不把局部结构检查称为增强整体完成。

<a id="task6"></a>
### 任务 6：正式工件检查器

**文件：** `check_artifacts.py`、`test_artifact_check.py`、utilities README、开发说明及 docs/tests instructions；必要共享行处理/字段定位保留在 `artifact_io.py`，只修正 verify-change 的直接耦合工具说明。未改四个 schema、32-kind、依赖、其他方法/入口、应用或后续工具。

**当前状态：第 1 轮修正及本次限定复审完成。** 初次实现起始为 `fea6e3f7f5749f223528a0311734e062e392a1b3`，两项 Important 在 `e0b9fae75a4ea07176e36e4b5b776887ab2a893c` 修正。父会话直接核对完整限定 diff，确认两项均已处理且未发现本修正引入的重大问题，并在该对象独立复跑 143 个受影响模块方法、0 跳过。实际入口见[原实现](../../logs/2026-10-15-ddd-alignment.md#task6)、[修正交接](../../logs/2026-10-15-ddd-alignment.md#task6-fix1)与[复审追加](../../logs/2026-10-15-ddd-alignment.md#task6-review)。以下原实现结果保留其历史对象，不充当修正后的结果。

- [x] 编写真实文件失败测试：重复 ID、缺标题/元数据、正式工件残留占位、坏文件/锚点、非法基线、空目录；实际测试使用原 `temporary_workspace`，只在获准 `.venv` 下写夹具。原接口示意：

```python
import tempfile
import unittest
from pathlib import Path
from check_artifacts import run_check
from tests.helpers import seed_git_repo

class ArtifactCheckTests(unittest.TestCase):
    def test_invalid_base_never_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_git_repo(root)
            report = run_check(root, base_sha="0" * 40)
            self.assertEqual("input-error", report.status)
            self.assertIn("BASE_UNAVAILABLE", {f.code for f in report.findings})
```

- [x] 定向运行见到真实行为 RED：52 方法/77 断言失败、0 错误/跳过；不是只拿最初的缺模块错误作证明。自审补充的八个边界也先复现失败再修改，完整源码与原始输出在获准证据目录保留。
- [x] 实现全量当前输入、精确历史比较、明确排除、源位置/重复双位置、原始字节读集及计数。base 读取精确 commit/tree/blob，不猜 main/master/HEAD/index，不执行 filters/textconv；历史元数据不套新规则。读失败不能冒充删除，空骨架为 `empty`，parser 失败为 `input-error`。
- [x] 用当前解释器通过 `subprocess.run`、参数列表、显式 cwd 与 `shell=False` 测试真实脚本；含空格/Unicode、0/1/2、明确 JSON 输出和覆盖拒绝、40/64 位 Git 对象、未暂存/未跟踪文件及未改库存均有检查。定向 60 方法与原 parser 74 方法均已执行，0 跳过。
- [x] 同一代码对象完整回归实际执行 204 方法（原 144 + 新 60）、0 跳过/失败/错误；9 次独立 CLI 使用及当前工作树 full/base 检查的源字节均保留。CHECK-14 的零发现/全跳过控制被证据门禁拒绝。实现、正反例及本段登记纳入本次局部提交，实际提交身份与最终文档/范围核对由 Git 和交接报告定位；不是独立审阅关闭。

- [x] 第 1 轮从已保存的 143 方法 / 26 失败 RED 继续：保留原 9 个新增测试方法及其字节，只修正 `_formal` 的首行分隔符候选保留和 `iter_markdown_lines` 的围栏/注释归属。新聚焦回归发现并执行 143 方法（checker 65、parser 78）、173 个子例，0 失败/错误/跳过；输入字节未被测试改写。旧 204 方法与 schema 结果不重写、不冒充本轮执行。
- [x] 两项 Important 经限定复审均已处理；父会话独立 `test_artifact*.py` 执行 143 方法、0 跳过、退出 0，43.040 秒。原测试字节及历史 RED 保留；此结论不扩展为新全套、其他宿主或业务验收。

**退出边界：** 本任务承接 ENH-07 的机械检查及本次范围复核完成，不是增强整体、业务 VT、覆盖图或暂存区 hook 验收。Task7 前置关卡已满足，来源入口也获用户选择；其实现与后续任务仍按各自范围推进。

<a id="task7"></a>
### 任务 7：模型视图、覆盖与影响核对

**当前状态：实现与本次范围复核完成。** 原 T7-I1–I5 已在 fix1 限定复审中处理；F1-N1 在 `23c06b6bc46099c04091c61c036016b88cf4ae99` 修正，并由父会话直接核对完整局部 diff 和模型模块回归，未发现该修正引入的重大问题。初始 293 方法、fix1 的 313 方法和 fix2 的局部结果各自保留原基线，入口见[原实现](../../logs/2026-10-15-ddd-alignment.md#task7)、[第 1 轮](../../logs/2026-10-15-ddd-alignment.md#task7-fix1)、[第 2 轮](../../logs/2026-10-15-ddd-alignment.md#task7-fix2)与[复审追加](../../logs/2026-10-15-ddd-alignment.md#task7-review)。

**文件：** `export_model.py`、`check_traceability.py`、`test_model_export.py`、`test_traceability.py`、必要的共享 helpers、model/verification 指引与 verify 方法；按用户选择增加 `.github\contracts\model-sources.schema.json`、`_templates\config\model-sources.yaml` 及契约/工具/开发说明。只提供空表，不在制作仓创建正式项目 `model-sources.yaml`。

- [x] 定义可选来源清单的多 scope 路径/固定基线契约，复用既有九视图输出而不增加结果/批准字段。清单不复制源正文；可选源的缺失/格式/基线问题与必需主输入错误分开。缺省不联网、不回写、不把 `model.yaml` 读作其自身事实来源。该入口方式已由用户于恢复后单独选择，不是从“继续”推断的授权。
- [x] 在 `helpers.py` 定义 `write_delivery_fixture(root, omit_software_reject=False)`，写真实 REQ/SR 四项验收、两个分层 VT 及其判据，返回四个完整交付 ID。`True` 只省略 VT-002 的软件拒绝目标，不删 SR 原验收。另有悬空、同号异主、本地可选源不可读、规则变化与旧视图副本。
- [x] 先写精确缺口与确定性导出测试：

```python
import unittest
from pathlib import Path
from check_traceability import trace_report
from tests.helpers import temporary_workspace, write_delivery_fixture

class TraceabilityTests(unittest.TestCase):
    def test_missing_software_acceptance_is_reported(self):
        with temporary_workspace() as directory:
            root = Path(directory)
            delivery = write_delivery_fixture(root, omit_software_reject=True)
            report = trace_report(root, delivery)
            missing = {f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"}
            self.assertEqual({"sample/CTX-001/SR-001#sr-001-ac-02"}, missing)
```

- [x] 分别运行 `test_traceability.py`、`test_model_export.py` 看到失败；实现库存优先的双向核对，精确定位 source/anchor/layer/criterion，不把缺目标的摘要算覆盖。
- [x] 用含 `sequenceSummary`、`governanceSummary`、`riskSummary`、`releaseStatus` 和 quality/QAS 引用的 fixture 核对 `export_view` 保留 canonical artifact/evidence/baseline 引用；删除任一可选 source 时仍输出对应 view 的 `unverified` 与具体 gap，不能复制正文或把 `state` 映射为 passed/approved。
- [x] 实现确定排序、来源散列与关系导出；相同输入字节输出相同结构，源变化/手改 view 检查失败。视图不复制业务正文、结果或审批，显式导出不回写源。
- [x] 2→3 规则变化给出受影响 REQ/SR/VT/任务候选及原因；即使引用方未抄数字也可受影响。共享方法负责语义判定、原结果保留与新运行，机械图不宣布业务正确。
- [x] 重跑正反例与前后散列：完整 293 方法、0 跳过，保留原 schema/parser/checker；原始命令、结果和字节证据由追加日志定位。两脚本、tests、方法和格式说明随本次局部提交交接，实际 commit/干净状态以 Git 与最终报告为准。

<a id="task7-fix1"></a>
**第 1 轮限定修正：** T7-I1 补真实 utility-tree 来源/基线，缺 QAS/tree 为 unverified；T7-I2 在解引用失败前保护全部已解析的嵌套声明，非法位置阻止不安全输出；T7-I3 共享字面状态机识别实际 Mermaid；T7-I4 独立读取所属子运行块、多列结果和明确数量，不跨块拼合；T7-I5 公开 API 拒绝 None base。原缺度量 fixture 补树仅为隔离“字段缺失”条件，保留原 partial/responseMeasure 断言，缺树另有失败回归。新结果不覆盖旧 293 方法记录。

- [x] 两轮限定复审已关闭原五项与新 F1-N1。父会话分别保留 fix1 的 243 方法结果，以及 `23c06b6` 上 `test_model_export.py` 的 77 方法、0 跳过、退出 0、48.748 秒结果；不拼成同一对象的全套结果。

**退出：** 本任务承接 ENH-06/08 的机械工具及本次范围复核完成；无 US 也能覆盖，原范围不删，旧结果仍绑定旧基线。Task7 退出时 Tasks8–18 未开始；当前 Task8 状态见下一节，不是完整功能等价或业务/应用通过。

<a id="task8"></a>
### 任务 8：只读领域输入下的实施摘要桥接

**文件：** `collect_implementation_report.py`、`test_implementation_report.py`、`tests\helpers.py`、报告表单、BC/config/model 说明及 handoff 方法。

- [x] 在测试 helper 定义 `seed_implementation_fixture(root)`：写入符合契约的 BC 配置、固定本地领域输入、四项验收/两 VT、带来源 ID 的自有代码文本，并提交该完整夹具，返回 object commit。代码文本不运行应用。给报告的原始证据分别为已执行、not-run、基线不符和不存在。
- [x] 先测不会把链接或 commit 当执行：

```python
import tempfile
import unittest
from pathlib import Path
from collect_implementation_report import build_report
from tests.helpers import seed_implementation_fixture

class ImplementationReportTests(unittest.TestCase):
    def test_absent_execution_evidence_is_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            object_sha = seed_implementation_fixture(root)
            report = build_report(root, object_sha, evidence_files=[])
            self.assertTrue(report["entries"])
            for entry in report["entries"]:
                self.assertEqual("not-run", entry["execution"]["status"])
                self.assertEqual([], entry["execution"]["evidenceRefs"])
```

- [x] 实现 BC/领域 baseline、相关 SR/US/ABB/VT、代码/测试标识与实际结果入口的摘要；缺证据不伪造 pass，越界或基线错配报输入错误。
- [x] 在 report/model fixture 中同时保留 sequence/governance/risk/release 与 quality/QAS 的 artifact/evidence/baseline 引用；九视图仍归 model，报告不增加 views 或把治理来源塞入执行 evidenceRefs。分别删除可选源、源不可读和执行证据缺失，保留原有 `unverified`/具体 gap 或逐目标 not-run。
- [x] 以来源 BC-12/DOMAIN-19 核对 sequence、QAS、治理/风险、release 关联都能用工件/证据引用表达；不因我们使用较窄摘要而丢失原消费方需要的视图，也不把源正文复制进摘要或写回只读领域。
- [x] 在显式本地输出写摘要，领域源前后散列不变；model 仅引用摘要。跨仓提交/回写属于独立获授权操作，没有权限就停止该副作用。
- [x] 完整重跑工具和表单相关验证，记录可访问性；局部提交的实际 SHA 与提交后状态以本轮报告的最终追加为准，不保存私有日志、凭据或完整聊天。

**本地验证（2026-10-16）：** 起点 `d30b87b805a133bca54d25ce5887e06071e605c1` 的干净 worktree。先保留 319 方法完整基线，再按真实 RED/GREEN 完成收集、报告 adapter 和源边界；最终完整套件实际发现/执行 **378 方法**，0 失败/错误/跳过，退出 0，386.857 秒。逐测试身份比较确认全部 319 个原方法保留，新增 59；未把不同对象的 313/243/77 历史结果拼成当前证据。

原始命令、cwd、stdout/stderr、退出码、计数、前后字节和文档检查入口见[本轮日志](../../logs/2026-10-15-ddd-alignment.md#task8)及其本机会话报告。合成 VT pass/fail 只验证收集器，不证明业务运行；Windows/Python 3.13.15 的结果不外推 Python 3.11 或其他宿主。

**退出：** ENH-12 的本轮实现及范围复核完成；实施报告是可重建引用，不成为第二份审批/结果输入或不受控写回。Task9–18、应用、平台与远端操作未开始，完整增强未获批准。

**第 1 轮限定修正（1/5）：** 从干净的 `7f747e55e480b92822c5599d1e9f54dccba98d9d` 开始，先为 T8-I1/I2/I3 取得真实反例，再仅修改位置登记、不同 executed testId 下限、被排除子树内的声明判据拒绝。聚焦组分别为 6、6、5 方法 GREEN；最终完整套件实际发现/执行 **395 方法**，0 失败/错误/跳过，退出 0，460.423 秒。原 378 个测试身份全部保留，新增 17。实际参数、字节保护、提交对象及报告导航见[修正日志](../../logs/2026-10-15-ddd-alignment.md#task8-fix1)。随后限定复审关闭原三项，并将新 T8-F1-N1 交第二轮处理；此处保留原运行，不作为第二轮结果。

**第 2 轮限定修正（2/5）：** 第 1 轮限定复审已将原 I1/I2/I3 判为 ADDRESSED，仅新增 T8-F1-N1。以 `062e607cde5cd5ecb2a0b2d83bff60ab2940c867` 为干净起点，先复现合法 utility-tree 的导出拒绝，再仅收窄 `reserve_declarations` 的上下文判断。2 个新往返测试 RED→GREEN；整个 model 模块实际发现/执行 **94 方法**，0 失败/错误/跳过，退出 0，160.163 秒。保留原 92 个模型测试和已修正的源隔离机制，没有重跑未改的 395 全套或 collector 套件；实现记录见[本轮交接](../../logs/2026-10-15-ddd-alignment.md#task8-fix2)。

- [x] 父会话限定复审确认新 T8-F1-N1 已处理，未发现该局部修正引入的重大问题。`9a3055a` 上独立模型模块执行 94 方法、0 跳过、退出 0、157.340 秒；原三项维持 addressed。完整入口见[Task8 复审](../../logs/2026-10-15-ddd-alignment.md#task8-review)，不把局部与旧全套合成一条结果。

<a id="task9"></a>
### 任务 9：人工审阅与工具资格记录

**文件：** `docs\ai-tooling.md`、review/tool-qualification 表单、审阅与交接入口。

- [ ] 从任务 1 矩阵准确读取已有治理功能；为工具用途/版本/运行环境、评估输入/结果/限制、责任人、批准范围与来源，以及重要交互摘要设计字段。
- [ ] 用一条没有具名决定的记录和一条有可定位外部决定的记录演练：前者不能写 confirmed，后者也不因文本存在就由机器认证身份。
- [ ] 如果确有六仓专用领域/风险工件，按已确认矩阵在本任务增补有独立职责的可选表单和验收；来源或适用责任缺失时保持阻塞，不默认医疗/QMS。
- [ ] 本轮来源已确认 Intended Use、风险控制引用及 QMS/SWAS 关系。加入约定的两个可选表单与 governance 说明，分别记录范围变更、责任人、外部风险源、确认基线和需升级的动作；不沿用原文件冲突的小节编号，不代做风险接受或法规认证。
- [ ] 审阅记录与结果、日志分开；不要求完整聊天，不生成“合规认证”声明。提交字段/指引。

**退出：** ENH-09；所有资格/审阅声明有范围与证据，不把 commit trailer 或 reviewer 模式当批准。

### 任务 10：可选 Git hooks 与 CI

**文件：** Python hook 入口、`install_hooks.py`、`test_hooks.py`、validate-artifacts/tooling-tests workflows、工具/CI 使用说明。

- [ ] 测试 installer 默认不更改 Git 配置、既有 hook 冲突不覆盖；显式安装只处理获准 hook，提供逐路径恢复说明，不改组织门禁。
- [ ] 在本地 Git 夹具做真实提交试验：合法输入通过、非法暂存工件失败、含空格路径成功、缺解释器/依赖明确失败。hook 检查暂存快照，不用工作树未暂存修复掩盖即将提交的问题。
- [ ] 实现 Python hook 入口与 installer；pre-commit 从 index 的已登记 blob 构造临时只读快照并检查，报告 index tree 与对象散列，不直接扫描被未暂存修改替换的文件。commit-msg 只能检查约定/提醒，不能认证 `reviewed-by` 身份。若 Git 宿主确需薄启动适配，适配中只调用同一 Python 逻辑；实际提交失败就修正后重测，不能以直接运行 Python 成功代替 hook 验证。
- [ ] 制作仓库的 tooling-tests 运行 tools tests，下游 validate-artifacts 只调用候选内检查器与数据契约；不引用不会分发的 tests。都保存明确基线/报告，PR 输入采用精确 base commit。未知对象、回归测试零发现或全跳过失败，不做成功形状 fallback；空项目的文档扫描仍单独标 empty。
- [ ] 原 ADO fan-out 的实际传播对象是 `.feature`，不是任意整仓覆盖。任务 11 的提案登记必须能表达来源场景→明确 BC 目标→文件范围→各自结果；托管平台实现可不同，但缺目标、无变化、冲突和失败不能一概报成功。
- [ ] 用脚本/夹具验证 0/1/2 传播；真实托管运行和必需检查配置在任务 13 单独授权，未跑就 not-run。提交源码、workflow 与说明。

**退出：** ENH-10 的工具与本地接入；服务端门禁是否实际启用由真实平台结果决定。

### 任务 11：三方更新与多目标传播

**文件：** `plan_template_update.py`、`test_template_update.py`、update-template 方法/prompt、template-updates 说明、proposal workflow。

- [ ] 固定三方夹具：本地未改、只改本地、只改候选、两边相同、两边不同、候选删除、本地业务文件、缺旧基线。
- [ ] 先证明冲突和不写入：

```python
import tempfile
import unittest
from pathlib import Path
from plan_template_update import plan_update

class TemplateUpdateTests(unittest.TestCase):
    def test_three_way_conflict_is_not_skipped_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base, local, candidate = [root / name for name in ("base", "local", "candidate")]
            for path in (base, local, candidate):
                path.mkdir()
            (base / "AGENTS.md").write_bytes(b"base rule\n")
            (local / "AGENTS.md").write_bytes(b"owner rule\n")
            (candidate / "AGENTS.md").write_bytes(b"new template rule\n")
            result = plan_update(base, local, candidate)
            self.assertEqual({"AGENTS.md"}, {item.path for item in result.conflicts})
            self.assertEqual(b"owner rule\n", (local / "AGENTS.md").read_bytes())
```

- [ ] 实现 `UpdatePlan` 的 `changes/conflicts/preserved`，标明来源版本、每条旧/本地/候选散列、拟修改/删除与理由；默认只返回/写提案，不覆盖业务文档、规则或源码。
- [ ] 多目标登记必须列允许的 repo/版本/文件范围；proposal workflow 只为这些目标生成独立差异与冲突。源不可读、授权不足或某目标失败逐项报告，不能把少数成功汇总成全体传播完成。
- [ ] 真正同步由原生 Git/平台在明确批准后执行；不自建调度器/同步服务，不自动更新领域 source 或自动合并。测试实际跨仓写入在任务 13 平台关卡后进行。
- [ ] 重跑所有原目标散列、方法停止案例及差异输出，提交工具/方法/说明。

**退出：** ENH-11 的可重复更新提案；原 fan-out 的已观察功能若还存在未实现的自动化差异，矩阵保留该缺项，不能靠“有脚本”宣布等价。

### 任务 12：增强候选、工具分发与原行为回归

**文件：** distribution 说明、blueprint、入口/PR 表单、`test_distribution.py`；结果在 `verification\ddd-alignment.md`。

- [ ] 冻结具体文件 allowlist：基础资料、增强表单/方法、可选工具/contracts/依赖及 validate-artifacts workflow 分别列明，不整目录复制 docs/logs。工具 tests、tooling-tests/传播 workflows、研究/计划、治理演练和内部 URL 不进入下游候选。
- [ ] `test_distribution.py` 使用真实复制候选：Markdown、工具资源/schema 和分发 workflow 的文件依赖在候选内可读，尤其不指向被排除的 tools tests；不要求研究 repo 或个人 skills，`src` 仍只含 README，没有预填 SD/REQ/VT 或批准事实。
- [ ] 基础阅读无工具依赖，启用工具时按本地 manifest 恢复并运行工具正反例。业务命令仍未配置，不能让 maintenance tools 替它们成功。
- [ ] 重做原 T01、T05、T07–T16 的适用回归；原 T17 和未测原生路径的状态仍保留，不复制旧结果充数。
- [ ] 整体运行工具测试和候选检查，保存对象/要求/工具版本、数量、原始结果与未执行项；提交文档及 tests，临时副本不提交。

**退出：** ENH-13；增强文件数量以新 allowlist 为准，不沿用“38 文件”描述或把临时检查器当分发功能。

### 任务 13：真实行为和客户端验收

**文件：** `verification\ddd-alignment.md`、`docs\agent-support.md`、获授权的开发日志；应用/目标 repo 为独立可丢弃试验对象，不进入候选。

- [ ] **先取得应用输入与授权：** 用户选择演练类型/栈/路径、原生命令/cwd、允许修改范围；没有选择就停止代码生成的通过声明，不用维护工具 Python 代选。
- [ ] 在选定试验对象走领域输入→SR→必要 US/ABB→VT→初始生成→实际测试，并对一个非空已有文件执行已授权维护。测试包含正常、拒绝/无副作用和已知失败；保留完整 trace marker 和原始运行结果。
- [ ] 反向提取该自有对象得到候选模型，与已给定事实比较；未知/冲突仍未决。规则变化后定位受影响工件/测试，保留旧结果及未执行状态，再记录新执行。
- [ ] 在当前 GitHub Copilot App 真实新会话执行三模式与九方法适用入口；记录版本、输入、原生调用、显式读、路径匹配/非匹配及 prompt 可用性。GUI/不支持/未测分别登记，不以 task 子代理模拟客户端。
- [ ] 人工路径由人按同一方法和输入操作并记录，再与 App 的事实边界/缺口/状态比较。无实际参与就 not-run，不模拟人。
- [ ] **平台关卡：** 获准的隔离目标与凭据/权限到位后，试一次 hook/CI 原始失败与成功、多目标差异提案及明确批准的更新/PR；没有平台授权就只保留本地结果，ENH-10/11 对应项不能关闭。
- [ ] 每个适用验收项写独立判据/实际结果，报告行为、文档检查、审批和发布的不同边界。不存在执行结果的 VT 仍 not-run。

**退出：** ENH-05/10/11/14 的实际行为证据。任何授权/环境缺失只阻塞对应验收；不阻塞已经可做的文档与工具任务，也不降低最终对齐标准。

### 任务 14：矩阵收口、版本与交接

**文件：** 能力矩阵、enhancement 验收、roadmap、blueprint、distribution 与一份制作 handoff。

- [ ] 从六仓完整能力矩阵开始逐项回源：每行有适用判据、实现位置、基线与结果；不能只盘点我们已经做完的工具/方法。
- [ ] 记录每个保留差异与明确替代的责任人决定；未确认、未测或失败保持可见，不称全面等价。
- [ ] 审阅已更改工具/contracts/方法的版本关系与正常 diff 更新说明；新候选不含旧研究、业务/测试工程或个人绝对路径。
- [ ] 明确原 P3 尚未完成的人工/客户端/发布项与本增强的证据关系；没有重新执行就不能更新为通过。
- [ ] 用原日志表单保存真实 Git、已完成/阻塞、原始证据限制与下一步；只在内容/许可证/位置/版本/维护者和操作权限都获确认后另行发布，不在本任务默认推送。

**退出：** ENH-01 至 ENH-18 的适用项有事实结论。未到达此条件时交付“已完成部分及差距”，不是“六仓功能全一致”。

### 任务 15：可选领域源接入

**依赖：** 2、6；完成后解锁任务 12。**文件：** `setup_domain_source.py`、`test_domain_source.py`、`docs\domain-sources.md`、onboarding 与 BC 配置说明。

- [ ] 用临时本地 Git 源和目标夹具覆盖未配置、正确固定 commit、缺版本、已有非空 `domain-model`、错层路径、无网络授权及只读目标。
- [ ] 定义 `inspect_domain_source(root, source_config)` 返回 `ready | conflict | unavailable` 与精确路径/版本/拟变更，不写文件；测试现有 owner 字节在冲突后仍相同，缺 commit 不改用远端 HEAD。
- [ ] 实现 Python 接入：默认单仓/local-source，显式用户选择 submodule 时才提出 native Git 操作；网络读取、文件/配置写入、index 更新和 commit 分开，不因执行脚本顺便提交。
- [ ] 在授权的本地夹具验证干净接入、二次执行、冲突与恢复；不得运行原 PowerShell 安装器或改原参考仓。测试远端来源时另确认权限。
- [ ] 将真实前置/返回/退出码写入开发说明，提交脚本与 tests。

**退出：** ENH-15；保留可选领域来源功能，避免强制六仓部署和隐含副作用。

### 任务 16：文档/转录来源适配与候选评分

**依赖：** 2、4、6；完成后解锁任务 12。**文件：** 来源表中三个 Python 工具、两 tests、media manifest、source-extraction 说明与逆向方法。

- [ ] 固定自有文本/转录样本：具名说话者、时间戳、重复与冲突语句、未决表达、缺来源；非文本和音频样本仅在获准处理后使用，不复制内部访谈。
- [ ] 定义 `extract_candidates(source, kind)` 输出候选列表，记录来源文件/片段/时间、候选类型、原始依据、`observed | inferred | uncertain`；`score_candidates(items)` 仅做透明规则评分与原因，不伪装校准概率。测试空输入返回空候选、有冲突不自动 confirmed、重复不丢出处。
- [ ] 实现本地 Markdown/plain-text、明确转录格式和 DOCX 适配；每个候选保留文件、段落/表格或转录时间戳/源片段位置。损坏或不可解析的 DOCX 必须返回明确输入错误（不能变成空成功），缺 DOCX 适配器/可选依赖必须返回 `SOURCE_ADAPTER_UNAVAILABLE`。document/audio 的具体解析器、SDK/模型与固定版本经单独授权后加入 `requirements-media.txt`；本轮不选择或安装 DOCX 包，缺可选依赖不关闭 ENH-16，DOCX 未运行时 ENH-16 仍是 `not-run`，音频服务保持单独授权。
- [ ] `transcribe_audio.py` 只在输入授权、明确服务/模型/数据范围和本地输出齐备后调用；无条件发送资料、从环境任取密钥、在线 fallback 均禁止。转录失败保留实际错误，不输出假空成功。
- [ ] 候选先由逆向方法确认/列 BL，永不直接写成正式领域事实；测试可执行适配、缺依赖和禁止副作用，实际音频服务未跑就保持该项 not-run。

**退出：** ENH-16；保留原有适配/评分用途，不扩展到源中仅在路线图的 Code/Schema 自动推理引擎。

### 任务 17：关系图、SWAS/PDF 与演示导出

**依赖：** 5、7、8；完成后解锁任务 12。**文件：** 三个 render Python 工具、rendering manifest、`test_rendering.py`、document-exports 说明及可选 workflow。

- [ ] 先测试空模型、孤立节点、坏关系、SEQ 的成功/错误路径、缺 ABB/风险来源的 SWAS、已有非空输出文件。输入固定，输出无随机 demo 或硬编码业务内容。
- [ ] `render_traceability(view)` 输出确定性 JSON/自包含 HTML 或 SVG，基于准确节点/关系/缺口，默认不请求 CDN；空数据明确 empty，不伪造演示节点。
- [ ] `render_architecture(inputs, format)` 以 source ID/基线组装 SWAS 和引用的序列视图；`render_presentation(inputs, format)` 是必须提供的等价参数化输出，不得以 distribution allowlist 排除 presentation 来满足 parity，也不得复制原 `_gen_ppt.py` 的硬编码内容或个人输出位置。
- [ ] PDF/PPTX 的实际 renderer/依赖/模板在获准后锁定到 `requirements-rendering.txt`；请求相应 format 时仍必须通过依赖、文件签名及页面/slide 计数 gates，缺依赖或未执行实际格式检查只能记 `unavailable`/`not-run`，不称导出成功。不依赖浮动 latest 容器；文件写入均需显式目标，已有文件先报冲突。
- [ ] 以解析器/文件签名与页面或 slide 计数检查真实输出，再做人/App 内容检查；没有对应 renderer 时仅完成可执行格式，其余 not-run。导出成功不等于 SWAS 已批准。

**退出：** ENH-17；所有适用格式均有真实结果，纯文本/图输出不能冒充 PDF/PPTX 验收。

### 任务 18：最小交互/用量账本

**依赖：** 2、9；完成后解锁任务 12。**文件：** `log_interaction.py`、`summarize_usage.py`、`test_interaction_log.py`、CSV 表单和 ai-tooling 说明。

- [ ] 定义固定字段：记录 ID、时间、工具/版本、任务/对象基线、操作摘要、人工决定来源、已提供的用量值/单位和证据引用；没有用量写 unknown，不推算用户账单。
- [ ] 测试真实 CSV 追加、重复 ID、无效时间/负用量、特殊字符和源记录缺失。重放同一 ID 不复制账目，冲突值显式失败，不覆盖已有行。
- [ ] 实现 Python 显式输入追加，不读取完整聊天、cookie、密钥或未授权日志；统计只按已知单位/计费依据分组，不把不同单位或未知值相加成“成本节省”。
- [ ] 对写入前后非目标字节和重复运行做验证，工具资格/审阅仍回原始记录，不因账本存在认定流程受控。
- [ ] 提交工具、tests 与字段说明；真实计费/平台数据没提供时对应集成结论保持未验证。

**退出：** ENH-18；可重复记账不扩大到会话监控、自动预算控制或工作流运行状态库。

## 5. 规格覆盖自检

| 验收 | 承接任务 | 关键失败例 |
|---|---|---|
| ENH-01 | 1、14 | 来源不可读、遗漏现有能力、路线图被当实现 |
| ENH-02 | 2、3、5 | 同 scope 重号、状态混用、双重真值、旧资料覆盖 |
| ENH-03 | 3 | 只有名词/目录、INV 无规则来源、未知政策被补造 |
| ENH-04 | 4、13 | 实现默认值自动成为批准规则、无源置信度 |
| ENH-05 | 5、13 | 非空覆盖、US 强制桥梁、缺栈仍生成、生成后不运行 |
| ENH-06 | 2、7 | 挂载路径拼错、未固定来源、手改/过期 model |
| ENH-07 | 6、10 | 无基线 fallback、空扫描/零发现冒充验收 |
| ENH-08 | 7、13 | 精确漏项/悬空、同号异主、旧 pass 自动沿用 |
| ENH-09 | 9 | 文字 Approved、trailer/角色被当认证 |
| ENH-10 | 10、13 | 只检查工作树而非暂存、脚本/hook/CI 不传播失败、CI 未跑 |
| ENH-11 | 11、13 | 三方冲突被跳过后仍成功、无授权远端传播 |
| ENH-12 | 8 | 无证据仍 pass、回写只读领域源 |
| ENH-13 | 12、14 | 演练/研究/内部路径混入、候选依赖排除文件 |
| ENH-14 | 12–14 | Agent 模拟人工、旧 App 结果充新结果、未执行写通过 |
| ENH-15 | 15、13 | 错误来源版本、覆盖非空目录、安装时隐含 commit |
| ENH-16 | 16、4、13 | 冲突候选被批准、缺适配输出假空成功、无授权上传资料 |
| ENH-17 | 17、5、13 | 空图注入 demo、输出覆盖、渲染未执行但宣称 PDF/PPTX 成功 |
| ENH-18 | 18、9、13 | 重复/冲突记账、未知计费乱加、账本冒充审批 |

执行状态按本计划和制作日志更新：任务 1–8 的有限交付及范围复核已完成；当前八方法、二十一 prompts、三模式。Tasks9–18 尚未实施，下一步为可选治理/审阅/工具资格记录。原 P3 与来源盘点结论保留其基线；音频/PDF/平台/应用与人工的实际执行保持各自关卡，不能用局部测试通过、未来计划或源码存在代替完整增强验收。
