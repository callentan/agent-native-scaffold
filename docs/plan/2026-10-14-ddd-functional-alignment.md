# 六仓功能对齐增强实施计划

> **面向 AI 代理的工作者：** 执行时使用 subagent-driven-development 或 executing-plans 逐任务推进；先核对已有完成记录，不重复执行。步骤以复选框跟踪。当前只获授权生成计划，不开始下面的实施任务。

**目标：** 在现有单仓骨架上提供六个 `ddd-*` 仓库现有功能的等价能力，并用逐项证据区分已交付、未执行和明确替代。

**架构：** 资料正文继续拥有业务事实，少量结构化元数据连接上下文、工件与验证；模型与实施摘要是可重建视图。共享方法负责需要判断的活动，项目内脚本负责确定性检查、导出与更新提案，Git/CI/现有 Agent 负责实际执行和授权。

**技术栈：** 维护工具 Python 3.11+、`unittest`、PyYAML 6.0.2、jsonschema 4.23.0；本地、hooks 与 CI 复用 Python 逻辑，不要求 PowerShell 包装脚本。下游应用技术栈仍未选择。

**规格：** [六仓功能对齐增强规格](../design/ddd-functional-alignment.md)，包含 ENH-01 至 ENH-14、完整固定版本和工具接口。执行者必须读取该文件，不能仅凭本计划标题推断行为。

**当前状态：** 规划完成不等于实现批准。以当前实现 `4531891` 为起点，现有 38 文件和 P3 证据不改写为增强交付；来源盘点是第一任务，余下阶段受明确关卡约束。

**2026-10-15 修订：** 按用户“基本都用 Python 脚本”的决定，移除必需的 PowerShell 启动文件及其任务；宿主原生 YAML/最薄启动适配保留，方法正文仍归 Markdown。此修订不开始实现，也不将新增自动化一概归为原仓已有功能。

## 全局约束

- 用户选择的是功能等价，不要求旧 ID/字段/路径的自动导入导出兼容，不恢复六仓拆分或强制 submodule。
- 固定六仓现有版本；不把实例应用、路线图、自动批准/合并或通用执行器纳入已实现能力。
- 独立编写内容；内部材料不进入分发候选，不复制未获许可的源码或模板，不向第三方发送私有资料。
- 新字段不产生第二份事实；元数据、验收正文、VT 实际结果和派生视图各有单一归属。
- 先核对 Git、原文件和范围。README 的现有排版未提交，任何任务均不得代为丢弃或混入提交。
- 没有完整必要输入时停止受影响任务，不把缺项当默认值；任务失败、未执行、空检查与通过分别记录。
- 不自动初始化应用、安装依赖、安装 hook、变更 CI 门禁、回写外部来源、推送、PR、发布或改变权限。
- 文档工作可在应用未配置时继续；生成代码的实际应用验收须在任务 13 先获独立输入和授权。
- 原六个方法、三个模式和现有 prompt 的能力保留；增强以活动拆分，不增加角色流水线。
- 可重复维护逻辑统一用 Python，直接调用项目解释器；本地/hooks/CI 不维护三套实现，不把 PowerShell 7 设为工具使用前提。
- 这里提到的工具、schema、测试与新工件均是拟创建文件，不是当前可执行功能。

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
| 12 | 3–11 | 自包含增强候选与原骨架回归 |
| 13 | 12、应用/平台验收授权 | 端到端行为与真实客户端结果 |
| 14 | 13、全部矩阵行有结论 | 功能等价结论与发布前交接 |

任务 4/5 都触及原方法与模式，按 4→5 串行，不能并行覆盖这些入口。任务 8/9/10/11 的工具测试可在各自依赖满足后独立验证，但 shared methods/开发说明的修改仍按一个写入者串行合入。不因可独立验证而另起工作流或扩大代理数。

## 3. 执行命令与测试约定

本计划只记录**未来执行方式**，本次不创建 `.venv` 或安装包。任务 2 先登记工具环境并创建 manifest，之后才在仓库自己的 `.venv` 恢复依赖。多步维护逻辑放入 `.py`，调用子进程使用参数列表、显式 cwd 与 `shell=False`；本地、hooks 和 CI 直接复用脚本，不把个人绝对路径写进模板。

| 检查 | 明确 cwd | 可执行程序及参数 |
|---|---|---|
| 定向 Python 测试 | 当前仓库根 | `.venv\Scripts\python.exe -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_artifact_io.py -v`；逐任务替换为其明确测试文件名 |
| 全部工具测试 | 当前仓库根 | `.venv\Scripts\python.exe -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_*.py -v` |
| 工件检查 | 当前仓库根 | `.venv\Scripts\python.exe -X utf8 -u .github\utilities\check_artifacts.py --root <本次已解析根目录> --report <获准结果目录>\artifacts.json` |
| 显式变更基线 | 当前仓库根 | 在上行增加 `--base <已核对的完整 commit>`；不存在则退出 2，不换分支或回退暂存区 |

表中使用 Windows 路径，直接执行项目 Python，不需要 `.ps1`。其他宿主按实际环境登记解释器位置，不把 Windows 的 `.venv\Scripts\python.exe` 照搬到 Linux。尖括号表示执行时从当前工作区解析的路径/Git 对象参数，不是虚构的可执行值。检查器使用 `pathlib.Path` 处理路径，每个参数单独传递；命令与 cwd 的真实记录在执行时保存。

所有 Python 工具任务先编写行为测试、运行看到预期失败、实现最小代码、重跑，再提交。测试实读夹具/真实 Git 对象，不只 grep 代码或模拟返回值。文档方法用真实使用正反例验证，不把“出现某个词”当流程正确。

## 4. 逐任务计划

### 任务 1：冻结六仓能力基线

**文件：** `docs\research\ddd-capability-matrix.md`、本规格、本计划、P0 决策与蓝图。

- [ ] 读取规格六个完整 commit 的递归树及所有约定、表单、工作流、工具、hook/pipeline；可以使用已有获准快照，不能用旧摘要代替未读文件。
- [ ] 每个文件登记 repo、commit、路径、原始证据位置和分类；每个能力登记输入/输出、前提、失败、写入边界、现实现差距、目标任务和 ENH 标识。重复入口关联到同一能力，不丢文件。
- [ ] 区分 `observed-current`、`proposed-upstream`、`unverified`、`instance-only`；特别核对反向提取、model/config、validator、commit-msg、fan-out 和工具治理是否现有，不从路线图推导。
- [ ] 对齐用户两项已确认决定，列出功能替代而非格式兼容；发现缺规格的现有功能就补有来源的验收/任务。源不可读时只交付阻塞记录，不宣布矩阵完整。
- [ ] 回源逐行审阅，更新 P0 中“七表单/六方法/无工具”的增强适用范围，但保留原版已交付与 P3 结果。仅提交矩阵和范围文档。

**退出：** ENH-01；六仓树条目都有归属，现有能力没有“无任务/无判据”行。未经这一步，后面只能作设计讨论，不能声明全面对齐。

### 任务 2：元数据、schema 与工具环境

**文件：** 四个 contracts、`artifact_io.py`、依赖/工具 README、`tests\helpers.py`、`test_artifact_io.py`、`docs\development.md`。

- [ ] 审阅规格 3.1/3.2 的事实归属、作用域、状态及现有资料无损演进；冻结 schemaVersion `1`，unknown version 是错误，不降级解释。
- [ ] 先创建 `.github\utilities\requirements.txt`（规格两项 direct pins）与工具环境登记，再在项目 `.venv` 恢复依赖，核对 Python 3.11+ 和 unittest 发现路径。这一步没有解析器实现，不把缺解释器/包当功能 RED。
- [ ] 编写真实夹具测试：正常文档、两个 scope 同号、同 scope 重号、重复 YAML 键、未知状态/版本、越界路径、缺必要字段。最小测试形状如下：

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

- [ ] 定向运行 `test_artifact_io.py`；失败应是缺解析/校验行为，不是错的 cwd 或缺已配置解释器。
- [ ] 实现 dataclass、SafeLoader、重复键拒绝、本地 schema 和准确行号，不启用远程 `$ref` 或联网解析；实测后保存传递依赖 lock。对既有正式文档只在确认作用域后补元数据，保留原正文与锚点，未确认的 scope 不猜。
- [ ] 重跑并登记实际数量/结果；工具环境单列，根开发说明仍不声称有业务应用。提交契约、解析器、测试与环境说明。

`helpers.py` 只为测试创建真实文件/Git：`seed_git_repo(root)` 在临时目录写一份 README，显式测试身份提交并返回完整 commit，不建远端；`write_artifact(root, schema_version, id, scope, kind, upstream, targets, acceptance_ids)` 写本规格格式的实际 Markdown。后续 trace 夹具由任务 7 扩展该文件。期望值由测试独立给出，不调用被测解析器生成期望。

**退出：** ENH-02、ENH-06 的输入契约；新语法与旧保留方式都可定位，读取空白模板无需先安装工具。

### 任务 3：完整领域工件与多上下文

**文件：** 七个新领域表单、领域/REQ/verification 入口及原相关表单。

- [ ] 先固定一份自有演练输入：两个上下文、一个共同 capability、一个 UC 正常/拒绝路径、一个规则约束的 INV、业务场景与两个未决 BL。沿用原借用额度素材，资格失效后处理和并发仍不决定。
- [ ] 编写 SD/CTX/CAP/UC/INV/validation/BL 表单的实际字段：身份/来源/责任、规则关联、正常与替代路径、判定、阻塞影响和确认依据；不预填批准或执行结果。
- [ ] 让一位执行者按表单写入隔离副本，再反查概念关系、规则先于 INV、来源/未决、上下文所有权与逐项业务场景。使用两个 scope 的同号验证不会混淆。
- [ ] 核对旧 `domain-model\README.md` 的单上下文轻流程和稳定链接仍可使用；正式工件只在实际需要时创建，空模板候选不包含演练 SD/UC/INV。
- [ ] 登记文档检查对象/结果并提交表单与指引，不把填写成功当业务验证。

**退出：** ENH-03；七类工件可用、来源明确，旧资料不用搬移也可继续使用。

### 任务 4：领域访谈、评审与反向提取

**文件：** `define-requirements`、`verify-change`、新 `reverse-engineer-domain` 及对应 interview/reverse/review/impact prompts，planner 入口。

- [ ] 用无新指导的隔离使用案例记录基线：来源不完整、旧代码与专家陈述冲突、未知 invariant、只读输入和紧迫交付压力。真实基线正确就如实记，不捏造行为失败。
- [ ] 增强 define 的访谈/迭代确认和领域评审输入输出；逆向方法产物为候选事实+源路径/行或版本+`observed | inferred | uncertain` 置信类别+问题，初始内容状态为 draft。
- [ ] 对同一案例应用完整方法，确认不会从实现默认值导出批准业务规则；冲突进入 BL 或来源差异，不改只读源，不自动提升状态。
- [ ] 测一个新领域与一个既有资料修正；同一方法供人/App 读取，prompt 只带输入。一次测试仅说明所执行场景，不保证所有模型。
- [ ] 记录原生加载与显式读取的不同证据，提交方法/入口与可访问的有限结果。

**退出：** ENH-04；反向提取有证据、置信度、确认和停止条件，不是从名词列表自动建模。

### 任务 5：BC 派生、评审与安全代码生成

**文件：** 原 SR/US/ABB/VT/ADR 表单、specify/implement/verify、新 generate-code、BC 配置表单、derive/design/verification/generate prompts。

- [ ] 明确领域依据 → SR → 可选 US → ABB/VT 的派生字段、边界与确认来源。业务 VT 不由软件结果汇总，ABB/VT 可在输入齐备后独立规划，维护任务不强制完整链。
- [ ] 初始生成契约给出明确来源/文件范围/已有内容预检/拟生成说明；非空冲突停写，不以“跳过”报告生成完整。既有代码修改走 implement-task 的任务/diff/验证路径，不复用初始化覆盖规则。
- [ ] 代码和测试的 trace marker 可定位 owner-qualified ID；缺项目类型、真实路径、命令、cwd 或执行前提时 block，不使用工具层 Python 代选应用栈。
- [ ] 在隔离已有内容副本演练目标非空、假审批、无开发输入和路径错配，验证源与 owner 文件原文保留。此步只验证流程/停止分支，不能报代码生成已通过。
- [ ] 更新原有活动导航与三个模式，完整代码生成的实际行为验证留给任务 13；提交各契约和入口。

**退出：** ENH-05 的资料/工作契约；代码生成行为仍未验收，不把原 BC prompt 的生成限制等同托管闭环。

### 任务 6：正式工件检查器

**文件：** `check_artifacts.py`、`test_artifact_check.py`、utilities README、相关 docs/test instructions。

- [ ] 编写真实文件失败测试：重复 ID、缺标题/元数据、正式工件残留占位、坏文件/锚点、非法基线、空目录。例：

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

- [ ] 定向运行 `test_artifact_check.py` 看到失败；以用户提供的完整基线扫描指定 Git 对象，不读取 main/master 猜测，不把失败当无变化。
- [ ] 实现全量/精确变更输入、模板排除、位置明确的 findings、基线及计数。空骨架输出 `status=empty`，不宣称需求通过；正式来源解析错误返回明确 input-error。
- [ ] 在 `test_artifact_check.py` 通过 `subprocess.run` 直接调用当前测试解释器和该脚本，使用参数列表、显式 cwd 与 `shell=False`；用含空格目录及正常、违反项、输入错误夹具核对实际输出和 0/1/2 退出码，不添加 shell 包装或把失败转成成功。
- [ ] 重跑，核对检查前后所有输入散列完全相同；提交实现、正反例及执行登记。

**退出：** ENH-07；工具实际可重复，未发生静默 fallback、零发现冒充验收或写入源工件。

### 任务 7：模型视图、覆盖与影响核对

**文件：** `export_model.py`、`check_traceability.py`、`test_model_export.py`、`test_traceability.py`、`tests\helpers.py`、model/verification 指引与 verify 方法。

- [ ] 在 `helpers.py` 定义 `write_delivery_fixture(root, omit_software_reject=False)`，写真实 REQ/SR 四项验收、两个分层 VT 及其判据，返回四个完整交付 ID。`True` 只省略 VT-002 的软件拒绝目标，不删 SR 原验收。另复制悬空、同号异主、外部源不可读、规则变化与旧视图副本。
- [ ] 先写精确缺口与确定性导出测试：

```python
import tempfile
import unittest
from pathlib import Path
from check_traceability import trace_report
from tests.helpers import write_delivery_fixture

class TraceabilityTests(unittest.TestCase):
    def test_missing_software_acceptance_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            delivery = write_delivery_fixture(root, omit_software_reject=True)
            report = trace_report(root, delivery)
            missing = {f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"}
            self.assertEqual({"sample/CTX-001/SR-001#sr-001-ac-02"}, missing)
```

- [ ] 分别运行 `test_traceability.py`、`test_model_export.py` 看到失败；实现库存优先的双向核对，精确定位 source/anchor/layer/criterion，不把缺目标的摘要算覆盖。
- [ ] 实现确定排序、来源散列与关系导出；相同输入字节输出相同结构，源变化/手改 view 检查失败。视图不复制业务正文、结果或审批，显式导出不回写源。
- [ ] 2→3 规则变化给出受影响 REQ/SR/VT/任务候选及原因；即使引用方未抄数字也可受影响。共享方法负责语义判定、原结果保留与新运行，机械图不宣布业务正确。
- [ ] 重跑正反例与前后散列；提交两脚本、tests、方法和格式说明。

**退出：** ENH-06/08；无 US 也能覆盖，原范围不删，旧结果仍绑定旧基线。

### 任务 8：只读领域输入下的实施摘要桥接

**文件：** `collect_implementation_report.py`、`test_implementation_report.py`、`tests\helpers.py`、报告表单、BC/config/model 说明及 handoff 方法。

- [ ] 在测试 helper 定义 `seed_implementation_fixture(root)`：写入符合契约的 BC 配置、固定本地领域输入、四项验收/两 VT、带来源 ID 的自有代码文本，并提交该完整夹具，返回 object commit。代码文本不运行应用。给报告的原始证据分别为已执行、not-run、基线不符和不存在。
- [ ] 先测不会把链接或 commit 当执行：

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
            self.assertEqual("not-run", report["execution"]["status"])
            self.assertEqual([], report["execution"]["evidence"])
```

- [ ] 实现 BC/领域 baseline、相关 SR/US/ABB/VT、代码/测试标识与实际结果入口的摘要；缺证据不伪造 pass，越界或基线错配报输入错误。
- [ ] 在显式本地输出写摘要，领域源前后散列不变；model 仅引用摘要。跨仓提交/回写属于独立获授权操作，没有权限就停止该副作用。
- [ ] 重跑、提交工具和表单，记录可访问性；不保存私有日志、凭据或完整聊天。

**退出：** ENH-12；实施报告可追溯而不成为第二份审批/结果或不受控写回。

### 任务 9：人工审阅与工具资格记录

**文件：** `docs\ai-tooling.md`、review/tool-qualification 表单、审阅与交接入口。

- [ ] 从任务 1 矩阵准确读取已有治理功能；为工具用途/版本/运行环境、评估输入/结果/限制、责任人、批准范围与来源，以及重要交互摘要设计字段。
- [ ] 用一条没有具名决定的记录和一条有可定位外部决定的记录演练：前者不能写 confirmed，后者也不因文本存在就由机器认证身份。
- [ ] 如果确有六仓专用领域/风险工件，按已确认矩阵在本任务增补有独立职责的可选表单和验收；来源或适用责任缺失时保持阻塞，不默认医疗/QMS。
- [ ] 审阅记录与结果、日志分开；不要求完整聊天，不生成“合规认证”声明。提交字段/指引。

**退出：** ENH-09；所有资格/审阅声明有范围与证据，不把 commit trailer 或 reviewer 模式当批准。

### 任务 10：可选 Git hooks 与 CI

**文件：** Python hook 入口、`install_hooks.py`、`test_hooks.py`、validate-artifacts/tooling-tests workflows、工具/CI 使用说明。

- [ ] 测试 installer 默认不更改 Git 配置、既有 hook 冲突不覆盖；显式安装只处理获准 hook，提供逐路径恢复说明，不改组织门禁。
- [ ] 在本地 Git 夹具做真实提交试验：合法输入通过、非法暂存工件失败、含空格路径成功、缺解释器/依赖明确失败。hook 检查暂存快照，不用工作树未暂存修复掩盖即将提交的问题。
- [ ] 实现 Python hook 入口与 installer；pre-commit 从 index 的已登记 blob 构造临时只读快照并检查，报告 index tree 与对象散列，不直接扫描被未暂存修改替换的文件。commit-msg 只能检查约定/提醒，不能认证 `reviewed-by` 身份。若 Git 宿主确需薄启动适配，适配中只调用同一 Python 逻辑；实际提交失败就修正后重测，不能以直接运行 Python 成功代替 hook 验证。
- [ ] 制作仓库的 tooling-tests 运行 tools tests，下游 validate-artifacts 只调用候选内检查器与数据契约；不引用不会分发的 tests。都保存明确基线/报告，PR 输入采用精确 base commit。未知对象、回归测试零发现或全跳过失败，不做成功形状 fallback；空项目的文档扫描仍单独标 empty。
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

**退出：** ENH-01 至 ENH-14 的适用项有事实结论。未到达此条件时交付“已完成部分及差距”，不是“六仓功能全一致”。

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

本轮只完成规格/计划编写与文档检查，未运行任何增强测试、恢复依赖或执行上述任务。执行批准时先做任务 1，不从中间写生成器开始。
