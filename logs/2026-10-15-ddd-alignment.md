# 六仓增强执行：来源、契约与领域表单

本文件是制作记录，不进入下游模板候选。

<a id="session"></a>
## 会话、任务与 Git 状态

| 字段 | 实际记录 |
|---|---|
| 日期/会话 | 2026-10-15；`1ff56941-bf56-4aa4-b769-fd4720915e1f` |
| 任务 | 用户“先commit 当前的变更。然后开始按照增强计划执行优化”；依据[增强计划](../docs/plan/2026-10-14-ddd-functional-alignment.md)与[规格](../docs/design/ddd-functional-alignment.md) |
| 分支/起始 | `callentan-repository-skeleton`；规划版本 `f9aab56` |
| 当前变更先提交 | README 原两处排版已按新授权提交 `1a6f594`；随后 Git 状态干净，不再保留为未提交 |
| 本次范围 | 六仓固定版本源码盘点、能力矩阵与范围补全，然后按依赖推进；不发布、不推送、不执行上游程序 |
| 对象定位 | 本日志和矩阵的实际提交由 Git 文件历史定位；后续实现各自记录，不预填完成 |

<a id="changes"></a>
## 本次变化

按约定六个完整 SHA 用 native Git 只读获取，未更新 submodule、运行 hook 或改参考仓库。浏览器曾跳转登录，Git 凭据已可用；源读取问题没有被当成“无要求”。

三组独立盘点报告覆盖 252 entries/195 blobs，合并结果见[能力矩阵](../docs/research/ddd-capability-matrix.md)。目录和 gitlink 只读元数据，10 个上游路线文件标提案；其余 185 个文件全文读取。44 组 current 能力有交叉，不是已交付功能计数。

原 plan 漏了 QAS/战术资料、SEQ/Gherkin/SWAS、接口/词汇演化、来源接入/适配、图/导出和账本。用户确认完整纳入，媒体/PDF/平台依赖及执行另行授权；补入任务/ENH-15–18，更新原任务职责和首版/增强的适用边界。Python-first 不变；旧源的隐含 commit/push、读写矛盾与空成功不是需照搬的功能。

<a id="verification"></a>
## 实际结果入口

| 对象 | 来源记录 | 限制 |
|---|---|---|
| 六仓源码分类和能力 | [能力矩阵](../docs/research/ddd-capability-matrix.md)、[来源登记补充](../docs/research/source-register.md#9-六仓完整源码盘点补充2026-10-15) | 核对的是固定源码/载体，不是上游程序/平台运行 |
| 原始快照与完整性 | 本机 `ddd-alignment-execution\references` 六份 manifest/Git 对象；`source-audit.json` | 仅本机，不能当跨机器 CI 链接；原 Git URL/commit/路径足以重新只读获取 |
| 分组读取 | 同目录 BC/DOMAIN/FRAMEWORK inventory/capabilities | source 属性与我们的计划建议分别处理，不把建议当已实现 |

独立核对检查所有条目/object ID/commit/源散列、能力引用及来源行界限；四处超出文件末尾的报告引用已按实际长度纠正，再次检查没有错误。没有改源码来满足报告，也没有声称目录/gitlink 全文已读。

来源关卡审阅补清了 Task 1 范围映射、单一 32-kind 枚举、九个视图的来源字段引用、DOCX 和演示导出的必需等价判据。再次审阅确认这些问题已处理，另指出主输入错误与可选视图缺项的表述矛盾；现已明确：root/schema/scope/主工件基线错误失败，单个可选摘要缺失/不可读/无效形成 unverified+gap，不吞错、不把空视图当完整模型。增强实现仍需按真实 tests 验证这些契约。

<a id="follow-up"></a>
## 影响与未执行项

计划、规格、蓝图及 P0 适用范围需要按完整来源修订；原首版/P3 记录不作废。不同消费 gitlink、外部 ADR/风险/ADO 实例、媒体服务、PDF/PPTX 引擎与真实 CI/权限/审批未运行，不能从源码盘点推导成功。

任务 1 结束时尚未创建增强工具环境、安装依赖或初始化应用。核心工具环境已由用户选择 Python，随后按任务 2 先创建 manifest 与本地 `.venv`，实际结果在下方独立记录，不把工具栈作为业务语言；业务/平台/媒体验收仍受独立授权控制。

<a id="handoff"></a>
## 下一步

完成来源矩阵/范围的一致性审阅后进入任务 2：四个数据契约、类型化解析器与真实文件 tests，明确输入错误、重复 YAML 键、未知版本/状态、scope/ID、路径与确认声明。先看到测试的预期失败再实现，依赖只在 manifest 就绪后恢复。

接手先检查 Git 与本日志之后的真实提交、计划 ledger 和来源可访问性，不重复获取/重做已完成来源组，也不把旧“仅规划”状态当当前未授权。发布、PR、业务项目和外部数据发送没有新增授权。

<a id="task2"></a>
## Task 2：元数据契约、parser 与维护工具环境

本节追加 Task 2 实际结果，不改写前面的 Task 1 当时状态。依据为[增强计划 Task 2](../docs/plan/2026-10-14-ddd-functional-alignment.md)及获准的 `ddd-alignment-execution\task2-brief.md`；范围只含本任务列出的 17 个仓库文件。起点为干净工作树、分支 `callentan-repository-skeleton`、完整 commit `81ffd45b3b9b7643d643a9162b533af92613c553`。此前 README 排版提交不重复执行。

新增[四个数据契约](../.github/contracts/README.md)、[不可变 parser 与显式集合接口](../.github/utilities/README.md)、独立 schema/parser 测试及真实文件/Git helpers。`.gitignore` 只增加项目 `.venv` 和 Python 字节码；[开发登记](../docs/development.md#maintenance-tools)将维护环境与尚未配置的业务应用分开。原技能、表单、业务资料、源码、hooks、workflow 和远端均未修改。

| 实际记录入口 | 对象与依据 | 可访问性与限制 |
|---|---|---|
| 本会话获准报告 `files\ddd-alignment-execution\task2-report.md` | Task 2 起点及本段同批文件的 Git 提交；完整 SHA、RED/GREEN 命令、原始输出摘要、版本和自审修复均在报告 | 会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的本机 artifact，不进入仓库或分发候选；不是跨机器 CI 证据 |
| [parser 行为测试](../.github/utilities/tests/test_artifact_io.py) 与[四类 schema 测试](../.github/utilities/tests/test_contracts.py) | 32 kind 各有 parser/schema 正例；九个视图的数据、完整引用、主输入错误和证据约束分别核对 | 可用已登记环境重跑；测试源码不是结果，本次运行定位在上行报告 |
| [实际依赖 lock](../.github/utilities/requirements.lock) 与[维护命令](../docs/development.md#maintenance-tools) | 先建 manifest 后创建 `.venv`；Python 3.13.15，六项实际依赖版本，`pip check` 无冲突 | 当前 Windows 环境；未声称其他 Python/OS 已实际验证 |

验证先有初始模块缺失错误，再用故意不校验的可读文件实现运行行为 RED：6 个 parser 方法产生 12 个失败，4 个 schema 方法产生 14 个失败；这些数含子例，不是额外发现的方法。实现后首轮 140 项通过；自审补充并复现 BOM 行号偏移、merge 归一化吞掉嵌套重复 `<<`、safe-tag 无效值泄漏内建异常，逐项修复后全量为 **143 个方法发现/执行、0 跳过、0 失败/错误**（parser 73、schema/Git 数据 70）。5 个 Python 文件通过语法检查，4 个契约文档示例实际解析/校验。完整命令与关键失败详情回报告读取。

Windows 的外部/内部目录 junction 和真实文件字节锁测试均已执行，没有用 skip 隐藏边界覆盖。`ArtifactInputError` 保留 code、文件、1-based 行号、错误信息与原始异常链；同 scope 重复只针对显式集合，不扫描或改写全仓。

### Task 2 限制与下一步

- Task 2 完成的是 ENH-02、ENH-06 的输入契约与 parser，不是六仓增强全部完成。九个视图的真实源读取/派生、跨文件存在性/层次/覆盖、主基线真实性及手改检测仍由 Task 7/8 执行，当前为 `not-run`，没有为了“通过”增加 exporter。
- 业务应用、媒体/PDF、外部来源接入、hook/CI、传播、发布、PR 和远端写入均未执行；相应独立授权关卡保持不变。schema-valid 的确认或 pass 声明也不认证人或证据真实性。
- Markdown 读取限于已记录的显式 anchor + owner ATX 标题模式；没有通用 Markdown 渲染、隐式 anchor 推断或自动旧格式转换。Windows junction 的结果不泛化为其他宿主全部链接类型，路径检查也不是防并发恶意替换的 OS sandbox。
- 没有已知阻塞 Task 2 的缺项。父会话按实际提交和报告进行范围复核后，再分派后续任务；本执行者未启动 Task 3 或任何嵌套代理/审阅者。接手重新核对 Git 与本机报告可访问性，不能只继承本摘要的通过结论。

<a id="task2-review-1"></a>
## Task 2：范围审阅反馈修正，第 1 轮

2026-10-15 12:44 的反馈给出三个修正：根错误定位、分发文档对排除资料的依赖、计划当前状态矛盾。开始时实际核对分支仍为 `callentan-repository-skeleton`，HEAD 为 `4b833dfad154e71e982e7e107d6cb9ae0cdc0464`，工作树与暂存区干净。反馈另报告父会话已在该对象独立执行 143 项、0 跳过；这是父会话的运行，不冒充本轮新证据。

本轮仅修改 7 个既有文件：`.github\utilities\artifact_io.py`、`.github\utilities\tests\test_artifact_io.py`、`.github\contracts\README.md`、`.github\utilities\README.md`、`docs\development.md`、`docs\plan\2026-10-14-ddd-functional-alignment.md`、`logs\2026-10-15-ddd-alignment.md`。另在原会话 `files\ddd-alignment-execution\task2-report.md` 追加完整记录；报告仍是本机 artifact，不进入提交。

- `parse_artifact` 只改一行根错误上下文为 `str(root)`，与集合 API 一致。新增真实文件回归同时断言两个 API 的 `code/path/line`，包含缺失根、实际文件充当根、null、错误类型及空选择。
- 分发文档移除内部规格/计划/制作日志链接与依赖被排除 tests 的命令，契约字段及示例保留自包含。维护者测试与历史导航统一放在[制作仓检查约定](../docs/plan/2026-10-14-ddd-functional-alignment.md#maintainer-checks)及本日志，不新增检查器或文档文件。
- 计划页首、页尾与相关状态句改为 Task 1 完成、Task 2 实现在范围审阅中、后续任务 `not-run`。原 P3、源码盘点和初始 `4b833df` 的 143 项结果保留其基线；Task 3–18 内容及 ENH 覆盖表与本轮基线逐字对比无变化。

本轮所有命令 cwd 均为仓库根，复用现有 `.venv`，没有安装或恢复依赖。定向回归命令：

```text
.venv\Scripts\python.exe -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_artifact_io.py -v -k test_invalid_root_errors_identify_root_in_both_apis
```

先运行新增测试：1 个方法、12 个子例，其中单文件 API 的 4 个子例失败；错误都是 `INVALID_ROOT.path` 指向 `REQ-001.md` 而不是无效根，code 和行号仍为 `INVALID_ROOT` / 1。原输出为 `Ran 1 test in 0.009s; FAILED (failures=4)`，退出 1。只修一行后，同命令为 `Ran 1 test in 0.007s; OK`，退出 0，没有削弱断言。

分发依赖诊断用现有解释器执行限定 inline Python，读取 3 份分发文档并按已排除路径检查真实相对链接，同时检查是否要求 `unittest discover`：原来 19 条本地链接中有 5 条指向排除资料，另有 2 条下游命令依赖排除 tests，共 7 个问题、退出 1；修改后为 `3 documents, 16 local links, 0 findings`、退出 0。诊断不作为新工具分发，完整执行代码与输出追加在原 Task 2 报告。

覆盖套件和语法检查实际执行：

```text
.venv\Scripts\python.exe -X utf8 -u -m unittest discover -s .github\utilities\tests -t .github\utilities -p test_*.py -v
.venv\Scripts\python.exe -X utf8 -m compileall -q .github\utilities
git --no-pager diff --check
```

全量输出 `Ran 144 tests in 5.440s; OK`：144 个方法发现/执行、0 跳过、0 失败/错误；语法及 diff 检查退出 0。独立执行计数复核为 parser 74、schema/Git 数据 70、参数化子例 327（子例不另加到方法数），同样 0 跳过/失败/错误。限定的 5 份 Markdown 共 39 个相对链接及锚点均有效；3 份分发文档无排除目标依赖；4 个保留的契约示例实际解析/校验有效。完整诊断代码、输出与提交对象追加在原报告，不用旧 143 项替代当前证据。

本轮未修改 schema、依赖、共享技能/表单或后续工具，没有子代理/审阅者、安装、hook、workflow、push、PR 或其他远端操作。提交后停在 Task 2，等待父会话核对本轮实际 diff 与证据；“修正已实现”不等于审阅已关闭或增强全部交付。

### 父会话范围核对完成

在修正提交 `322cd9082c0f99a4583cf54b04590075c5e1b42f` 上回读了单行 parser 修正、新增双 API 的真实 invalid-root 回归，以及分发文档/计划的范围修订；三项反馈均已处理，没有扩展 schema 或引入新运行功能。

父会话使用现有项目 `.venv`、显式仓库 cwd 独立执行全套工具测试：`Ran 144 tests in 5.054s; OK`，退出 0、跳过 0。原始命令/输出与 commit 在本机 `ddd-alignment-execution\task2-final-tests.json`，不是复述实现者结果。当前 Task 2 的范围审阅关闭，下一步为 Task 3；这不关闭后续模型导出、追溯、App/人工或业务执行验收。

<a id="task3"></a>
## Task3：可选领域表单与实际文档使用

### 会话、范围与对象

| 项目 | 本次记录 |
|---|---|
| 日期与执行者 | 2026-10-15；Task3 implementer 单会话执行、自审，无嵌套 Agent |
| 任务依据 | 用户批准的 [Task3](../docs/plan/2026-10-14-ddd-functional-alignment.md#task3)，父会话固定的 Task3 brief 与 case input；不是新业务需求 |
| 分支与起始基线 | `callentan-repository-skeleton`；`6f8a0f9667f7b4d81840a7d4d6a994ceff45934b`，已核对完整 SHA 与 Task2 修正的祖先关系 |
| 原有改动 | 开始时暂存区与工作树均干净，没有待代为提交的旧改动 |
| 本次对象 | 下列 24 个分发文件及 Task3 计划状态、本日志；同次局部提交，完整提交号回 Git 与会话报告读取 |
| 非目标 | 不改 parser/schema、共享 skills/agents/prompts、应用/测试布局；不安装依赖、不执行参考源、hooks/CI、媒体/平台操作或远端操作，不启动 Task4+ |

### 实际变化

- 新增 18 个独立编写的领域/QAS/战术表单，完整列表与正式落点见[领域工件导航](../domain-model/README.md#optional-forms)；所有空表保留 draft 与待项目确认的身份。
- 接入[领域指引](../domain-model/README.md#artifact-metadata)、[REQ/QAS 指引](../stakeholder-requirements/README.md#domain-inputs)、[场景/VT 指引](../verification/README.md#domain-scenarios)及[根表单导航](../README.md#forms)。旧轻量正文、稳定锚点和项目事实没有替换。
- [REQ 表单](../_templates/items/stakeholder-requirement.md)与 [VT 表单](../_templates/items/verification-test.md)接入现有 frontmatter，删除重复的内容状态栏；VT 的目标关系归元数据，正文按 criterionAnchor 保存独立判据，历史执行与当前适用性分开。
- 没有修改其他字段指引。制作资料、演练实例、一次性检查脚本与报告没有进入分发文件或成为它们的依赖。

### 结果入口与可访问性

原始结果在父会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution\` 下；以下是该已授权入口内的定位，不是仓库自带命令或跨机器报告。接手时须取得该目录或重新执行有界检查。

| 检查层次 | 实际记录定位 | 对象与限制 |
|---|---|---|
| parser/schema 与实际表单复制使用 | `task3-artifacts\run-03\results.json`、`template-provenance.json`，实际实例在同级 `used-copy\` | 27 个草稿工件覆盖全部 18 新 kind；10 个 owner-qualified 验收与 10 条目标引用；同 scope 重号拒绝。不是通用覆盖图或业务执行 |
| 本地文档链接与保留性 | 同一 `results.json`、`lightweight-before.txt` 和 `lightweight-copy\domain-model\README.md` | 24 个变更分发文件及 57 个复制 Markdown 依赖、正例/重号副本均检查本地链接；轻量正文和所有者标记逐字节保留 |
| 规则变化的文档操作 | `task3-artifacts\run-03\allowance-change-plan.md` | 针对 UC/INV/REQ/SR/TS/VT 的影响计划，保留原文件与未知项；未实际迁移或执行业务 |
| 本次真实维护工具回归 | `task3-report.md` 的命令与终端摘录 | 当前工作树上新运行一次现有全套测试：144 项、0 跳过、退出 0；未复用 Task2 历史通过 |
| 自审与提交交接 | `task3-report.md` | 精确变更文件、复制路径、操作/结果、提交号与语义限制；同一执行者自审，不代表父会话或人工批准 |

检查过程中保留了两个检查脚本问题的记录：`run-01` 用归一化换行与 parser 保留的 CRLF 比较而误报，按原始字节比较后 `run-02` 完成；随后扩查重号反例，发现移入 `negative\` 后的相对链接未重定位，补正该临时副本构造后 `run-03` 全部有限检查完成。两项都只修正会话检查脚本，未改 parser、schema 或分发表单，旧产物保留。

### 缺口、影响与停点

- 自用演练明确保留资格失效、并发、QAS 度量、战术边界/身份/事件、接口版本及失败政策缺口。全部业务/软件行为记录仍为 `not-run`，没有应用、runner 或批准可作为执行依据。
- 全部 18 类都有真实填表后的 parser/schema 正例；语义复核限于实际操作的固定文档案例。其他战术模式的设计正确性、真实应用行为、性能与跨平台支持未验证。
- 当前 parser 不检查完整跨文件覆盖或批准真实性；本次只对明确选择的夹具关系做有界核对，没有交付后续 checker/exporter。
- Task3 实现与自审结束，等待父会话/用户的独立范围复核；交接者需重新核对本次提交、工作树和本机证据可访问性。本执行停在 Task3，不把 Task4+ 或原 P3 未完成项改成完成，不推送或创建 PR。

### Task3 独立范围复核与下一阶段基线

对 `0aef102257de02cd4cee40ac1ee4af46d14e2251` 的独立审阅未指出表单/身份/来源边界缺陷，只发现计划页尾仍写“下一步任务 3”；现已与页首和任务小节统一为 Task3 本次范围完成、下一步 Task4，不重复执行已交付表单。父会话在该 commit 上实际复跑 `144 tests in 4.870s; OK`，0 跳过、退出 0，结果位于本机 `task3-parent-tests.json`。

另一个独立消费者只用当前六个共享方法与新表单处理五个固定输入场景，实际填 UC、QAS 和 Published Interface 三个草稿，parser 成功解析，未改仓库。来源不全、2 与 3 的规则冲突、active 的同名异义、QAS 缺指标、接口/审批/覆盖缺项均保留；它没有伪造缺失的文件、行号、actor、指标或验收 ID。报告位于 `task4-baseline-use\task4-baseline-report.md`，既是 Task3 的有限消费者观察，也是 Task4 增强前基线，不是人工参与或 App 原生测试。

该基线已有正确控制行为，不能为新方法编造 RED 或可靠性提升。可确认的功能缺口是独立反向提取活动尚未提供，Task4 尚未实施；新的领域方法需对同一输入再观察并明确覆盖范围。
