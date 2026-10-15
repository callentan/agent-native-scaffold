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

<a id="task4"></a>
## Task4：领域方法、反向候选与薄入口

本节追加 Task4 实际结果，保留上节作为实施前的历史观察。**当前 Task4 已实现，等待独立复核；本执行停在 Task4，Task5–18 为 `not-run`。**

### 会话、任务与 Git 对象

| 项目 | 实际记录 |
|---|---|
| 日期与执行者 | 2026-10-15；Task4 implementer 单会话实施与自用，无嵌套 Agent 或独立 reviewer |
| 依据与范围 | 用户批准的 [Task4](../docs/plan/2026-10-14-ddd-functional-alignment.md#task4) 与本机会话 brief；只实现方法/入口和状态记录，不重新获取源或重做基线 |
| 分支与起始对象 | `callentan-repository-skeleton`；`6f617e101b88e85bbeecfb3347187f24d0f90891`，已核对完整 SHA |
| 原有未提交内容 | 开始时工作树与暂存区均干净，无需重做“先提交当前变更” |
| 本次对象定义 | 18 个分发文档，加计划当前状态与本日志追加段，共 20 个仓库文件；包含本节的 Git 提交及会话报告记录完整提交号 |
| 授权边界 | 允许本次限定文件、显式自用/文档检查、一次既有回归与含 coauthor 的本地提交；不推送、PR、安装、联网、执行应用/源程序、hooks/CI 或后续任务 |

### 实际变化与判断

- 新增 [reverse-engineer-domain](../.github/skills/reverse-engineer-domain/SKILL.md)，从实际文件、外部记录或已提供摘录保存候选、原始依据、认识类别、冲突、确认需要与影响。缺原文件/行号不补造；实现默认值不成为业务批准，未提供的指标/演员/政策继续未知。
- 聚焦 [define-requirements](../.github/skills/define-requirements/SKILL.md) 的访谈、知识锤炼、词汇、接口、来件 ADR 和可选 Intended Use；扩展 [verify-change](../.github/skills/verify-change/SKILL.md) 的领域/BL 审阅、查询和影响。保留完整验收优先、精确目标反查、旧新基线及只读/执行分支，遵循实际 Task3 元数据和表单契约。
- 新增十个[薄 prompts](../docs/agent-support.md#entry-points)，每个只含当前输入与一个实际方法小节链接；仅校准 planner/plan-feature 的选择路由及 README/AGENTS/agent-support 导航。当前实际为七方法、十五 prompts、三个模式，不是最终计划的九方法。
- 原四份未涉及方法、其余模式、copilot-instructions、表单、parser/schema、依赖、tests 与空白项目事实没有改动；未发现需要修改 record-handoff 或 copilot-instructions 的集成问题。未链接未来方法或治理/架构表单。

### 实际结果入口

下列位置均在父会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 已授权的 `files\ddd-alignment-execution\`，仅本机可访问、不进入分发候选；不能当作跨机器 CI 链接。接手需取得该目录或重新执行有界检查。

| 层次 | 实际记录定位 | 对象与限制 |
|---|---|---|
| 实施前独立基线 | `task4-baseline-use\task4-baseline-report.md` 及七份原产物 | 原六方法已有正确控制行为；本轮只读取并核对散列，不重跑、不制造失败 |
| 三方法同题自用 | `task4-after-use\case-interview.md`、`case-reverse.md`、`case-glossary.md`、`case-interface.md`、`case-review.md` | 同一实施者的五个有限案例；具体选择、来源位置、冲突、需谁补什么及禁止副作用分别记录，不是独立复核或人工参与 |
| 表单使用与附加停点 | `task4-after-use` 中 UC/QAS/PI 草稿与 `supplemental-stops.md` | 三份实际表单使用，fixture 身份不是生产事实；ADR/Intended Use 只覆盖缺输入停点，查询只覆盖当前领域目录 |
| 文档/结构检查 | `task4-checks.py` 的实际 stdout 与 `task4-report.md` | 限定闭包/相对链接/锚点、YAML、scope 与基线保留检查；不交付新 checker/exporter，不把 parser 当完整追溯引擎 |
| 维护工具回归 | `task4-report.md` 的实际命令与输出摘录 | 当前项目 `.venv`、明确仓库 cwd，新运行一次原 144 项；不是方法语义、业务/软件行为或 App 测试 |

本次回归实际输出为 `Ran 144 tests in 4.654s; OK`，144 项均执行、0 跳过、0 失败/错误，退出 0；没有改动测试或复用 Task3 的通过结果。原输入和基线产物的散列保留。既有原生六方法/P3 记录不升级为七方法已测，新增及修订方法只作显式文件自用记录。

### 缺口、影响与停点

- CASE-REVIEW 未给真实缺失软件验收的 owner/ID/路径，只能精确回指输入的章节/行并请求原文；没有发明目标，也没有报告覆盖完整。“Approved”缺决定/基线仍不获认可。
- 原路径/行号、2 与 3 的取舍、actor、QAS 度量、契约版本/错误政策与完整消费者清单仍有缺口。新记录为候选或提案，没有把既有正确基线描述为纪律失败或声称可靠性提升。
- 新 ADR/Intended Use 的真实来件修订、广泛模型/客户端表现、App 原生入口和人工 T17 均未验证；没有假造风险分类或给借用案例施加医疗/QMS 前置。
- 独立复核由父会话/用户另行进行，本执行者没有认证批准。后续工具/适配器、应用、媒体/PDF/平台、hooks/CI、推送和 PR 未执行；独立授权关卡与完整增强验收不变。
- 接手先核对本次完整提交、工作树、计划全部当前状态及本机报告可读性；只复核 Task4，不从本次局部结果自动启动 Task5 或其他任务。

### Task4 父会话范围复核

对 `f8df3924da01d807091236651f22f047edff19ca` 的独立代码/文档范围审阅未发现重大问题；父会话另在该对象实际运行原工具套件，`144 tests in 2.906s; OK`，0 跳过、退出 0。新方法是 Markdown 活动说明，不把该回归当方法行为或 App 原生通过。

独立修改后消费者实际读取三个完整方法，形成五个案例的来源/冲突/缺项判断和 UC/QAS/PI 草稿；父会话重解析三份实际草稿，身份、kind、draft 和验收数量符合该合成输入。这只支持有限修改后使用，不代表全部工作流正确或性能提升。

该消费者另外在修改后任务中生成了一个所谓 “no-new-method baseline”，不是独立修改前观察；其中的失败叙述不作为 RED、对照或改进证据。唯一有效的修改前基线仍为 `task4-baseline-use` 中此前保留未知/冲突的正确控制记录。原报告原样保留，方法论限制由本记录说明，不改写旧观察。

消费者还因相对输出路径歧义把十个临时文件写到仓库未跟踪的 `execution` 目录；父会话保留全部原字节并迁入本机会话 `task4-independent-observation`，空目录清理后 Git 无这些未跟踪文件，未修改或提交源文件。字节迁移和无效对照说明在 `task4-observation-relocation.json`；路径清理首次因目录属性失败，显式核对为空后才针对性删除。

消费者报告本会话 callable skill 列表未包含新方法，使用显式文件读取完成；本次没有独立客户端加载 trace，因此仍保留原生发现未验证，不能扩大成所有客户端不支持。Task4 本次范围复核关闭，下一步 Task5 的 BC 方法；媒体/平台/业务/人工验收关卡不变。

<a id="task5"></a>
## Task5：BC 表单、方法与安全初始生成契约

本节追加 Task5 实际记录，保留上文各阶段的历史观察。**当前 Task5 已实施，等待独立审查；本执行停于 Task5，Task6–18 为 `not-run`。**

### 会话、任务与 Git 状态

| 项目 | 实际记录 |
|---|---|
| 日期与执行者 | 2026-10-15；Task5 implementer 单会话实施与自用，无 subagent/reviewer |
| 依据与授权 | 用户批准的 [Task5](../docs/plan/2026-10-14-ddd-functional-alignment.md#task5)、本机 task5-brief 与固定十案例；仅文档/方法/规则、有限检查、一次既有回归和含 coauthor 的本地提交 |
| 起始分支/完整对象 | `callentan-repository-skeleton`；`d7693a8e481dd84effc155378ae16c255c04d9b7` |
| 原有未提交内容 | 开始时工作树/暂存区干净，无需重复“先提交旧变更” |
| 本次范围与对象 | 31 个分发文件加本计划状态和本日志追加，共 33 个文件；同批提交由 Git 文件历史定位，完整 SHA/提交后状态回本机 task5-report 读取 |
| 不变边界 | 不修改 parser/schema/依赖/测试、Task3 领域表单、其他四个方法或 reviewer；不生成业务应用、运行后续工具、联网/安装、配置 hooks/CI、推送或 PR |

### 实际变化

- [SR](../_templates/items/software-requirement.md)、[US](../_templates/items/user-story.md)、[ABB](../_templates/items/architecture-building-block.md)、[ADR](../_templates/items/architecture-decision.md) 接入现有元数据，删除重复内容状态/关系表；VT 只补 [companion](../verification/README.md#feature-companion) 接入，原运行/适用性与全量目标盘点保留。
- 增加 [SEQ/SWAS 与 BC 配置字段指引](../architecture/README.md)、空白 feature；九视图只引用来源，不制造模型导出、基础设施、质量度量、风险分类或批准。
- [specify-feature](../.github/skills/specify-feature/SKILL.md) 提供 SR、可选切片、必要架构、VT/feature、SEQ/SWAS 聚焦小节；[generate-code](../.github/skills/generate-code/SKILL.md) 单独处理初始输入/路径/非空冲突/拟生成说明。既有维护仍用 implement-task，文档路径不依赖应用输入。
- 新增三份有限代码规则和六个薄 prompts；planner/implementer 只作相关路由，reviewer 仍沿 verify 的原入口。原十五 prompts 无需手术式修订；通过共享方法可到达新分支。当前实数为 **8 方法、21 prompts、3 模式**，没有 Task11 的 update-template。
- 分发内容没有依赖制作 design/plan/research、实际日志、tests 或本机会话产物；仅共享的日志指引/空表继续分发。原 P3 六方法/五 prompts/两规则的历史观察保留，不能升级为新入口原生发现已测。

### 实际证据入口

所有本轮辅助文件都在父会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的绝对授权 artifact 根内，没有仓库相对的 execution 输出目录。下表只给该本机入口内定位；不是跨机器证据或新分发工具。

| 记录入口 | 实际对象与限制 |
|---|---|
| `files\ddd-alignment-execution\task5-report.md` | 本次完整报告、准确命令/cwd/路径、范围、真实检查、提交与限制；提交后重查实际 Git |
| `task5-baseline-use\task5-baseline-report.md` | 唯一真实修改前基线；本次只读，控制原已正确，不补造 RED 或可靠性提升 |
| `task5-after-use\start-state.json`、`copy-provenance.json` | 起始 94 个 tracked 文件与四份固定输入摘要；90 个实际分发副本、11 个表单复制前字节摘要 |
| `task5-after-use\BC-USE-01.md` 至 `BC-USE-10.md` | 同一实施者对同一十例的有限操作/停点；原身份、项目、审批与旧报告缺项仍保留，不是独立审查 |
| `task5-after-use\consumer-copy`、`use-check-01.json` | 九个实际填表 Markdown 经原 parser 解析、五个 owner-qualified 合成验收和三条目标；BC 使用真实本地输入摘要，九视图用现有 schema 校验；feature 只作文本/映射 |
| `task5-after-use\tool-tests.json` | 当前 `.venv`、明确仓库 cwd，只运行一次原套件：`144 tests in 4.977s; OK`，0 跳过/失败/错误，退出 0 |

初轮有限文档检查覆盖 90 个分发文件，其中 80 个 Markdown、63 份 YAML frontmatter、512 个本地链接；实际消费副本的 92 个 Markdown/568 个本地链接也可定位，六个已有外链未访问。最终状态/日志核对另留最终 receipt，不用这些数量证明业务语义或原生客户端运行。

原 owner fixture 在预检与检查后仍为 225 字节，SHA-256 为 `2b060d2f641e7a1f02ccaf35c676f402aa49726ba06cef4a8b5b6921eda84466`。另一个合成 Markdown 修正严格只替换一个链接并保留周围字节；原 BC-USE-04 缺实际目标，未被该补充例假装解阻。错误 owner 的 VT 可解析但目标不存在，BC `HEAD` 基线被实际 schema 拒绝；空配置仍带明确占位而不是有效项目登记。

本次没有为 Task5 消费副本建立 Git 仓库或提交。原 144 项套件内部按其既有 helpers 在受控临时目录构造并清理本地 Git/文件夹具，这是原套件的内部行为，不是新增业务工程或 Task5 生成活动；未修改 helper、安装 hook 或连接远端。

### 缺口与下一步

- 合成身份只用于局部结构例，不补原十案例未给的 owner/ID/源文件/基线。没有实际 UC/INV/CAP/QAS、参与者/错误/副作用/并发/失效政策或确认时，相关要求/US/架构仍为候选或阻塞。
- 有界库存明确保留 `task5-synthetic/CTX-BORROW/SR-SYN-001#sr-syn-001-ac-02` 与 `task5-synthetic/CTX-BORROW/ABB-SYN-008#abb-syn-008-vc-01` 两个未覆盖目标；metadata/schema 与链接检查不等于这些验收通过。
- 新 SEQ 是已知概念方向的部分说明；SWAS 缺真实 ABB/部署/风险/发布来源，九视图仅 requirements 为 partial、其余 unverified。没有 Gherkin parser/runner、Mermaid/PDF/演示渲染或应用行为执行；全部相应结果为 `not-run`。
- Task13 正向应用生成/原生 runner 需要另选实际项目/栈/路径、命令/cwd/报告和授权；本次不为了声称成功要求创建应用。后续 checker/exporter、源接入、hooks/CI、平台/人工验收均未启动。
- 下一步由父会话独立复核本次 33 文件、完整报告、十例实际副本与全部当前状态；接手先核对完整 commit、工作树和本机证据可访问性。Task5 尚未获得独立审查结论，不自动进入 Task6。

<a id="task5-review"></a>
## Task5 复核追加

2026-10-15，父会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 按既有增强执行授权关闭本次资料契约关卡。实际核对分支仍为 `callentan-repository-skeleton`，HEAD 为 `5d39f407630d557b8b0bd51fa12efdde0b5bfef8`；独立消费观察后 status 只有分支行，没有暂存、未暂存或未跟踪文件。本次只追加本日志并同步规格、计划和 roadmap 的当前状态，不改变 Task5 的实现或旧记录。

Task5 的独立范围审阅返回无重大问题。父会话在上述实现对象运行的原始记录为本机会话 `files\ddd-alignment-execution\task5-parent-tests.json`：当前项目解释器、明确仓库 cwd、原 144 项工具测试、0 跳过、退出 0，实际用时 2.564 秒。这是对未改 parser/schema 的工具回归，不是新业务行为结果。

独立修改后消费者记录在同一入口的 `task5-independent-use\task5-independent-report.md`。它实际只读固定十例、当前方法/规则/表单和 owner fixture，逐例区分可草拟、缺身份、非空冲突、缺运行输入、历史适用性及对应停点；没有另造修改前基线，没有运行 parser、应用或 renderer，也没有修改仓库。其观察中的 fixture 仍是 225 字节，摘要与前节原值相同。该报告仅支持本次显式文件使用和手工结构核对，不证明原生发现、人工对照或一般可靠性提升。上述完整报告和原始工具记录仅在本机可访问，换机须重新取得或执行相应检查。

前节两个合成未覆盖目标继续保留，真正应用生成、Gherkin runner、客户端/人工、PDF/平台和批准均未验收。下一步按[任务 6](../docs/plan/2026-10-14-ddd-functional-alignment.md)实现有明确输入、定位、基线和退出码的 Python 工件检查器；不因此创建应用或安装后续可选依赖。接手仍须重新核对当前 Git、任务状态及证据可访问性。

<a id="task6"></a>
## Task6：正式工件检查器

### 会话、范围与 Git

本节追加 Task6 / ENH-07 的实际实现与执行记录，保留前面各任务的原始结果。任务来源为[既有 Task6 计划](../docs/plan/2026-10-14-ddd-functional-alignment.md#task6)和用户“先commit 当前的变更。然后开始按照增强计划执行优化”的本次限定授权；没有新建业务 REQ/SR。状态为**已实现，等待独立审阅**，不是实现者自行关闭 review gate。

- 起始完整对象 `fea6e3f7f5749f223528a0311734e062e392a1b3`，分支 `callentan-repository-skeleton`；已核对为原 App 管理的 isolated worktree、无 superproject，108 个原 tracked 源文件、工作树/暂存区干净。前序提交已完成，不做空的“先提交”或修改主 checkout。
- 本次只修改 12 个范围内文件：新增 checker/对应测试，共享 parser 的最小行处理和字段定位，utilities README、开发说明、docs/tests instructions、verify-change 的耦合工具说明，以及规格、计划、roadmap、本日志。四个 schema、32-kind、依赖、既有 tests/helpers、应用与其他工具/入口保持原位。
- 完整报告为本会话 `files\ddd-alignment-execution\task6-report.md`；同批提交的实际 SHA 由 Git 文件历史和报告定位。提交前后 Git/暂存范围分别记录，不将测试时未提交的对象写成只有 HEAD。

### 实际变化与判定边界

新增 [check_artifacts.py](../.github/utilities/check_artifacts.py) 的 `run_check(root, base_sha=None)` 与独立 CLI；[使用契约](../.github/utilities/README.md#artifact-checker)登记发现规则、支持的 Markdown、占位、JSON、错误码、计数和输出保护。继续使用 `Artifact`、`ArtifactInputError`、canonical key、owner acceptance 和源位置，没有第二套 YAML/frontmatter/验收解析器或配置框架。

明确 root 下的文件名/元数据信号决定正式库存，template/native/maker/test/Git/环境目录有精确排除；普通轻量 guide 不冒充正式工件，root 祖先的 `.venv` 也不误排除整个夹具。标题/占位/本地链接为 `invalid`；parser、路径、基线和写报告问题为 `input-error`；没有正式工件为 `empty`，不是业务通过。

base 只读取精确 commit/tree/blob 作历史比较，目标始终是完整当前工作文件，含未暂存/未跟踪正式输入；未改的身份/链接错误不能隐藏。旧元数据不套用新规则，不运行 filters/textconv、来源命令或网络读取，不猜 main/master/HEAD/暂存内容。报告记录原始字节与实际读集，读失败不记成删除，`comparison_complete` 区分不完整比较；没有提供 index-only hook。

API 不写入；CLI 默认只输出 JSON，只有显式新 `.json` 路径才写报告。拒绝覆盖已有源/历史文件、自动建目录和 UNC 报告路径；报告输出与输入散列分开。`verify-change` 只更新原来“检查器未提供”的说明，保留只读模式不运行命令、无覆盖/导出和不认证批准的边界；没有新增方法、角色、prompt 或工作流。

### 实际结果入口

所有原始执行证据都在会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的获准 `files\ddd-alignment-execution\task6-evidence\` 下；以下定位仅在本机可访问，不是随下游分发的依赖或跨机器 CI 证明。

| 记录定位 | 对象与说明 |
|---|---|
| `start.json` | 实际 root、分支、Git dir/common dir、起始 commit/index 状态和 108 个原文件字节摘要 |
| `red-01-missing-module.json`、`red-02-behavior.json`、`red-03-assertions.json` | 先缺模块，再使用无检查行为的接口确认真实 RED；补足两处测试断言前提后为 52 方法、77 断言失败、0 错误/跳过，源码和 raw stdout/stderr 保留 |
| `check-04-implementation.json`、`red-05-boundaries.json`、`green-06-boundaries.json` | 初步 52 方法通过；自审发现并用八个新增边界复现问题，再到 60 方法通过：缺分隔符/标题身份的发现、普通 project 误报、inline-code 注释开头、UNC 预拒绝和不可读文件的比较完整性 |
| `parser-01-shared-helper.json`、`parser-02-literal-comments.json` | 两次有界 parser 回归均为原 74 方法、0 跳过；共享提取及字面注释修正未破坏旧接口行为 |
| `full-01-precommit.json` | 同一最终代码对象完整 suite：204 方法发现/执行、361 个子例、0 跳过/失败/错误、24.468 秒、退出 0；原 74 parser + 70 schema/Git 数据 + 新 60 checker，没有替换原套件 |
| `cli-01-receipts.json`、`cli-01-execution.json`、`cli-01\` | 9 次真实 CLI：正例、坏文件、空骨架、精确 base/重跑、无效/符号 base、错误 root 类型、旧报告保护；逐条保存参数/cwd/stdout/stderr/退出码和源字节前后摘要，显式报告另列 |
| `check14-zero-*`、`check14-skipped-*` | 证据门禁实测：零发现和全跳过拒绝。当前 Python 3.13 原生 CLI 零发现实际退出 5（最初预期 0 的观察保留），仅用 `wasSuccessful()` 的真实 API runner 则零发现退出 0；计数门禁仍拒绝，未添加自我证明的产品测试 |
| `worktree-01-receipts.json` | 当前真实 worktree 的 full/base 均为 empty、0 正式工件、40 排除条目、17 个实际读取 Markdown 摘要；两次检查前后 110 个源文件字节和 Git 状态相同。该对象在本日志追加之前，不能当最终日志字节摘要 |
| `syntax-01.json`、`dependencies-01.json` | 现有 Python 的 compileall 和 pip check 退出 0；编译缓存明确写入获准证据目录，没有新安装或改 lock |

命令和门禁入口只用于这次获准执行，测试代码与预期病例本身不是运行证据。原始记录保留失败和成功的不同对象/阶段；未把初次模块缺失或 naive runner 的退出 0 当作功能/回归通过。最终范围、自审、文档链接、提交及提交后状态回完整报告读取。

### 限制、未执行与下一步

- 真实运行宿主为 Windows、Python 3.13.15、现有 PyYAML 6.0.2/jsonschema 4.23.0；本机真实 SHA-1/SHA-256 Git、字节锁及 junction 已用。最低 Python 3.11、其他 OS、所有文件系统/权限策略尚未实测，不由当前成功推导。
- 目录不可枚举及部分不可读比较路径采用明确 OS 边界注入；UNC 测试在本地阻止解析以保证不联网，没有修改 ACL。真实文件字节锁另有实际执行。路径检查不是防并发恶意替换的操作系统隔离。
- Markdown 是已登记的有限语法，不是完整 renderer；普通 guide、跨文件 canonical 覆盖/层次/语义、模型导出不属于 Task6。明确保留未决业务事实，Task5 的两个合成未覆盖目标、旧结果适用性和业务/软件 VT 的 `not-run` 未升级。
- 未启动子代理/独立审阅者、Task7、来源接入、应用、Gherkin runner、hooks/CI、媒体/PDF、平台、推送或 PR，没有安装依赖或改变权限。方法说明只做直接耦合的可用工具更新，不声称新的独立 Agent 压力测试或可靠性结论。
- 下一步由调用方独立核对本次 commit、12 文件 diff、完整报告与各原始证据；接手先检查当前工作树/暂存区和本机证据是否可读。Task6 等待该复核，本执行在本地提交与报告后停止；Task7–18 及原 P3 的未执行关卡仍保持原状。

<a id="pause-task6"></a>
## 用户暂停与恢复点

2026-10-15，用户要求“先暂停 保存一下状态。 我会实时继续”。增强执行暂停，不自动推进后续任务。Task1–5 的有限范围关卡已关闭；Task6 的实现提交为 `b8d4f826db142de052038288f938d90b1581020e`，**独立审阅发现两项 Important，修复第 1 轮尚未关闭**：

- 无正式 ID 文件名/H1 的工件，开头分隔符多一个空格时，明显的元数据可能被当作普通 guide，导致漏检。
- 代码围栏信息字符串中的 `<!--` 会污染正文注释状态，关闭围栏后仍可能隐藏坏链接和真实 owner 验收项。

完整只读审阅保存在本机会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution\task6-review-findings.md`；原始实现、追加修复/暂停信息回 `task6-report.md`，执行总账为同目录 `progress.md`。父会话已核对两处代码机制，未把静态分析伪称为新的执行复现。原实现对象上的 204 项回归结果保留，不能证明这两个新增场景已经修复。

18:19:55 +08:00 的只读 Git 观察：分支 `callentan-repository-skeleton`，HEAD 仍为上述 `b8d4f826`；仅 `test_artifact_check.py`、`test_artifact_io.py` 两个工具测试文件有未暂存改动，无暂存/未跟踪路径。本暂停记录是随后新增的日志改动；没有为保存状态提交尚未完成的测试，也没有回滚所有者内容。执行者已收到停止新实现、测试和提交的指令；其最终暂停回报仍待收到，已启动命令和 RED 结果不能在此预填。

恢复时先重查 Git、两个测试改动、完整报告的最新暂停段及实际证据；继续同一修复轮，取得真实复现/修复结果后再做限定复核，不重做 Task1–5。Task7 的可选来源入口仍待用户选择：`model-sources.yaml` 或每次显式命令/API 输入；用户此次只要求暂停，没有批准推荐方案。收到执行者的后续完成通知也只补充暂停状态，不自动恢复实现或审阅。

**暂停确认追加：** 执行者已停止，工具状态为 idle，所启动的命令均已结束，没有新提交或生产代码修改。最新交接位于 `task6-report.md` 第 10 节 `task6-fix1-paused`；`task6-evidence\red-fix1-01.json` 保存暂停前已完成的真实 RED：143 个方法、26 个失败、0 错误/跳过。两个测试文件新增 9 个方法，已复现两项漏检；这不是修复通过，下一步仍是限定生产修正、GREEN 和独立复核。本次只补保存该状态，没有恢复执行；当前保留两份测试及本日志的未暂存改动。

<a id="resume-task6"></a>
## Task6 修复轮恢复

2026-10-15 20:16 +08:00，用户明确要求“恢复执行”。重新核对实际 Git：HEAD 仍为 `b8d4f826db142de052038288f938d90b1581020e`，分支 `callentan-repository-skeleton`；暂存区为空，未暂存范围仍只有两个工具测试文件及本日志。两个测试文件的原始字节摘要与 `red-fix1-01.json` 一致，两个生产模块摘要与原实现记录一致，没有把暂停期间的内容当成新修复。

本次从第 1 修复轮继续两项已复现的漏检，保留暂停记录和原 RED，不重做 Task1–5。限定修正后仍须取得新的受影响模块结果和独立复核，旧 204 项结果不自动适用于修复对象。Task7 来源入口的选择尚未答复，恢复指令不等于采用推荐清单；应用、平台和发布的单独授权边界不变。

<a id="task6-fix1"></a>
## Task6 第 1 轮修正：从保存的 RED 恢复

### 会话、任务与 Git

2026-10-15，按用户“恢复执行”和本机 `task6-fix1-resume-brief.md` 继续同一轮修正；依据为[Task6 / ENH-07](../docs/plan/2026-10-14-ddd-functional-alignment.md#task6)及完整两项 Important 审阅。恢复时分支 `callentan-repository-skeleton`、HEAD `b8d4f826db142de052038288f938d90b1581020e`，暂存区为空。

原有未暂存内容是两个工具测试文件和本日志。9 个新增测试方法来自暂停前的 RED，本执行未重写测试；本日志的 `pause-task6`、暂停确认与 `resume-task6` 是父会话的原有同任务内容，保留后随限定提交纳入，不计为本执行的实现。新恢复快照保护了这份较新的日志前缀，未重用早于暂停记录的旧起点。

### 本次变化

- [检查器](../.github/utilities/check_artifacts.py)只修改 `_formal`：首行可辨认但不合法的分隔符不再提前终止元数据前缀；真正的语法接受/拒绝仍由原 parser 决定。普通正文、代码与注释中的字段不因此成为正式库存。
- [共享 parser](../.github/utilities/artifact_io.py)只修改 `iter_markdown_lines`：先核对围栏前的注释状态，使用原始信息字符串判断围栏合法性，不让围栏信息或内容开启正文注释；保留实际正文注释、代码排除及源行号。
- [工具说明](../.github/utilities/README.md#checker-discovery)补充上述边界；[计划](../docs/plan/2026-10-14-ddd-functional-alignment.md#task6)区分原实现结果、本轮回归和仍开放的复审关卡。没有新模块、schema、依赖、模型图或业务工件。

### 实际结果入口

完整追加报告在本机会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution\task6-report.md` 第 11 节；本节与修正随新局部提交保存，实际 commit、文件清单、命令/cwd、输出及字节摘要回该报告和 Git 核对。报告只在本机可访问，不是已分发的跨机器证据。

同目录 `task6-evidence` 保留原 `red-fix1-01.json`，并新增 `fix1-resume-start.json`、`green-fix1-resume-discovery.json`、`fix1-resume-before-green.json` 与 `green-fix1-resume-01.json`。发现修正先执行 2 个既有方法；随后实际聚焦 `test_artifact*.py`：发现/执行均为 143（checker 65、parser 78），173 个子例，0 失败/错误/跳过，测试子进程退出 0，47.530 秒。测试前后全部 110 个源路径字节一致；原测试字节、80 个此前证据文件和父会话日志/原报告前缀均保留。后续自审、提交后核对分别由 `fix1-resume-review.json`、`fix1-resume-post.json` 定位。

这是维护工具的真实文件、Git 和 CLI 回归，不是业务验收。原报告中的历史 204 方法及其他结果保持原基线；本轮未重跑无变化的 schema 或全套测试，也未把旧通过升级为修正通过。

### 限制与下一步

- 本机 Windows / Python 3.13.15 实测；Python 3.11 和其他宿主仍未执行，不推导跨宿主兼容。保存的 9 个测试方法未新增或削弱断言，源字节与暂停前 RED 一致。
- 两项修正等待调用方限定复审，未自行关闭 Important 或独立关卡。接手先检查新 commit、实际 diff、最新报告和证据可访问性；不要盲目重放旧 audit 的范围假设。
- Task7 来源入口仍待用户选择，本轮没有选定 `model-sources.yaml` 或替代入口；Task7–18、应用、hooks/CI、平台和发布保持未执行。没有子代理、工作流、新 worktree、安装、权限变更、push 或 PR；完成限定本地提交与追加报告后停止。

<a id="task6-review"></a>
## Task6 第 1 轮限定复审与来源入口决定

父会话核对了 `b8d4f826db142de052038288f938d90b1581020e` 至 `e0b9fae75a4ea07176e36e4b5b776887ab2a893c` 的完整七文件限定 diff：两个生产函数的选择/状态边界、保留的九个失败用例及相关说明。两项 Important 均已处理，未发现本修正引入的重大问题；这是协调者直接完成的限定复审，不是实现者自审，也未另起重复审阅任务。实际 commit/parent/trailer 和干净工作树/暂存区已重查。

本机会话 `files\ddd-alignment-execution\task6-fix1-review-result.md` 保存逐项依据；`task6-fix1-parent-tests.json` 保存父会话在 `e0b9fae` 独立执行的准确命令、cwd 和原始输出：`test_artifact*.py` 发现并执行 143 方法、0 跳过、退出 0，43.040 秒。两模块的新结果不替换原 204 项全套的历史基线，不声明 Python 3.11、其他宿主或业务行为已经验证。完整报告仍只有本机可访问。

Task6 的本次实现/范围复核关卡关闭。恢复后，用户还单独选择了“使用可选 model-sources.yaml 来源清单（推荐）”；上一节执行者未收到该后续决定，其“仍待选择”是起始上下文，不作为当前未决状态。Task7 将依此登记来源路径和固定基线，不复制正文、结果或批准状态；正式来源清单、模型导出和覆盖工具尚未创建，不获得外部读写权限。

本次同步规格、计划、roadmap 的当前状态，保留全部旧观察。计划中 Task8 的旧示意也与已实现的报告 schema 对齐为 `entries[].execution` / `evidenceRefs`，没有新增全局结果字段或声称 Task8 已运行。下一步按[Task7](../docs/plan/2026-10-14-ddd-functional-alignment.md#task7)继续；应用、平台及发布关卡不变。

<a id="task7"></a>
## Task7：完整覆盖、影响候选与九视图模型

### 会话、范围与 Git

按用户原执行授权、“恢复执行”及另行选择的可选 `model-sources.yaml`，仅实施[Task7 / ENH-06、ENH-08](../docs/plan/2026-10-14-ddd-functional-alignment.md#task7)。起点为 `def03cdc0f58414eeb4d59da61928d451b431aaa`，分支 `callentan-repository-skeleton`，现有 App-isolated worktree，暂存区及工作树起始均干净；无需重复初始提交或 Task6 修正。状态为**已实施，等待独立复核**，不是实现者关闭独立关卡。

### 本次变化

- 新增[来源 schema](../.github/contracts/model-sources.schema.json)和[空表](../_templates/config/model-sources.yaml)，清单只保存多个明确 scope 下的视图路径/固定基线。原四份 schema、32 kind、九视图输出和 8/21/3 方法/入口/模式数量不变；没有创建正式项目清单。
- [覆盖/影响工具](../.github/utilities/check_traceability.py)读取完整实际库存，区分显式交付与上下文，反查所有目标、原所有者 AC/VC、正文层次和独立判据。精确 base 的旧新依赖图保留删除/移除引用，产生候选与源位置，不改规则或结果。
- [模型工具](../.github/utilities/export_model.py)引用真实 Markdown 或已有摘要，保留 scope-qualified refs、证据路径/固定基线及具体 gap。YAML/证据/清单均进入来源身份；缺主输入失败，缺可选源保留固定视图。检查重算不修复，显式输出不覆盖已有文件或占用登记源路径。
- parser/checker 仅抽出共享已读库存、原始 YAML mapping/历史 blob 解析与保护输出；保留 Task6 的围栏/注释处理和全部原测试。更新实际契约、工具/开发/领域/验证/架构指引及 verify 方法的工具入口，未重写方法或增加代理流程。

### 实际证据入口

完整报告与提交后实况在本机会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution\task7-report.md`。新 receipts、辅助脚本及保留的合成来源都仅在同目录 `task7-evidence`，单元测试的瞬时夹具只在仓库忽略的 `.venv`。这些入口仅本机可访问，不是已分发的跨机器证据。

- `baseline-213.json`：在起点**新跑** 213 方法、0 跳过、退出 0，未将 Task6 的旧全套结果当作本次基线。
- `manifest-red*.json` / `manifest-green.json`、`trace-impact-red.json` / `trace-impact-green.json`、`model-red.json` / `model-first-green.json`：先有独立预期和实际失败，再实现并重跑。来源 schema 初始 10 方法、覆盖/影响初始 25 方法、导出初始 28 方法；不是只看语法或虚构 baseline。
- `self-review-boundaries-red.json` 及各聚焦 `*-green.json`：自审复现后修正来源合并、字段完整性、跨 scope/嵌套证据定位、同一 schema 读点和输出冲突等边界；保留真实失败，不把首次未通过记成 GREEN。
- `final-full-suite.json`：完整保留与新增套件实际发现/执行 **293 方法**，0 失败、0 错误、0 跳过，退出 0，106.635 秒；包含原 schema 70、parser 78、checker 65，以及 Task7 trace 27、model/manifest 53。命令/cwd/stdout/stderr 和逐源前后字节摘要在该 receipt；测试期间仓库输入字节未变。
- `observations\observations.json` 和同目录 `outputs`：保留真实四项交付、仅软件拒绝遗漏、规则 2→3 的源文件/旧新 Git 身份，以及九视图模型、检查和手改副本。省略项精确为 `sample/CTX-001/SR-001#sr-001-ac-02`；两 owner 文件未删改，规则单改追到 REQ/SR/两 VT/任务五个候选。两脚本实际 CLI 分别观察到 0/1/2，输入和旧输出字节保持不变。

这是本地维护工具的行为验证，不是业务或软件 VT 执行。完整结果、19 个输入案例的对应测试、自审和提交清单回报告/receipts 核对，日志不维护另一份验收结果表。

### 限制与停点

- 实测为 Windows / Python 3.13.15；Python 3.11、其他宿主和更大真实项目未运行。I/O 故障注入已在测试中明确标注，不冒充实际权限配置。
- 覆盖判据和直接 Markdown/摘要适配是已说明的机械结构检查，不证明自然语言判据充分、风险可接受、批准真实或已发布。只处理实际 canonical 依赖，隐含语义/轻量链接仍需责任人核对。读取不是文件系统事务。
- 未执行独立 reviewer/Agent 压力测试、Task8–18、应用/Gherkin、hooks/CI、媒体、平台/远端操作；未安装依赖、改权限、amend、push 或 PR。实施报告字段仍为空，未创建 Task8 收集器。
- 本次完成范围内本地提交和报告后停止。下一步由调用方核对精确 commit、20 文件范围、原始证据及完整来源契约，再决定 Task7 独立复核；不能从局部 GREEN 推导完整功能等价。

<a id="task7-fix1"></a>
## Task7 第 1 轮修正：五项 Important

### 起点与范围

用户授权在同一轮处理 T7-I1–I5。独立审阅和父会话机制核对均未声称新运行复现；本轮从干净的 `fe1acd39e1e25025d037e0c072e437824e848911`、同一 `callentan-repository-skeleton` worktree 开始，实际补复现后再修。只修改两个工具、必要的共享 Markdown 读取、相关测试/契约/工具说明及当前状态；四份原 schema、32 kind、九视图与 8/21/3 不变。

### 实际修正与原断言保护

- T7-I1：直接 quality 同时需要可核实 QAS 与真实 utility-tree 来源/基线，缺源为 unverified 且清空 refs；已有源缺字段/条目仍 partial。原缺度量 fixture 补一个实际树文件只是隔离缺字段条件，原 partial 与 responseMeasure 断言不变；缺树另有新 RED，不创造 kind 或生产树数据。
- T7-I2：在解引用前登记所选已解析源文档的全部嵌套位置，缺失/前项失败不漏掉后项；声明不能安全登记时只读仍可给 gap，但输出被拒绝，不假称完成隔离。合法新模型可原样 export/check，旧输出不覆盖。
- T7-I3：正文与闭合代码围栏复用同一个注释/围栏状态机，图检查只接受实际归属 `diagram` 的代码块。注释、外层 literal、未闭合块或普通说明均不能补图；Task6 的旧围栏/注释测试保留。
- T7-I4：按真实 VT `runs` 章节读取本 owner 的子运行块和逐判据多列表，每条记录分别核对明确数量、日期、说明和基线。不放宽 `section_lines`，不从总数推算数量、不跨块拼合；同基线结果冲突保留两侧引用及 gap。
- T7-I5：公开 `impact_report(root, None, task_ids)` 直接返回 INVALID_BASE/input-error，不通过测试 helper 的默认 base，也不退化成 clean 空比较。

### 真实结果入口

本机会话 `files\ddd-alignment-execution\task7-report.md` 追加 fix1，原报告前缀和原证据保留。新 receipts/helpers/保留样本仅用 `task7-evidence\fix1-*` 名称；瞬时测试夹具仍只在忽略的 `.venv`。这些是本机证据，不随模板分发。

- `fix1-start.json` 记录干净起点、116 个源文件、123 个旧证据文件和原报告/日志前缀摘要。
- `fix1-all-red.json`：先只改测试，生产代码仍为起点；18 方法、20 个失败子例、0 错误/跳过，五项都实际复现。I2 的错误创建发生在自有临时输入里，不是生产源。旧 293 方法结果没有被重标成本轮基线。
- `fix1-i1-green.json`、`fix1-i2-green.json`、`fix1-i3-green.json`、`fix1-i4-green.json`、`fix1-i5-green.json` 分别记录 8/6/10/9/7 方法的定向 GREEN；包含对应正常/缺项/隔离控制及保留 Task6 用例。后续不安全位置的补充 RED/GREEN 另见 `fix1-reservation-boundary-*.json`。
- `fix1-full-suite.json`：本轮只执行一次完整保留＋新增套件，实际发现/执行 **313 方法**，0 失败、0 错误、0 跳过，退出 0，105.466 秒。完整命令/cwd/stdout/stderr 与前后源字节在 receipt；被测工具、tests 与 schemas 的字节在提交前后再核对，不用语法或旧结果替代。
- `fix1-observations\results.json` 保留八组新来源/结果观察，涵盖五项：QAS 缺树/实树、后续缺失嵌套位置的实际 CLI 拒绝、注释/外层 literal/真实图、所属运行表，以及 None base 与真实精确 Git base 对照。均记录工具执行前后输入摘要；运行表仅为已提供的合成来源记录，不是一次业务/软件执行。

### 限制与停点

本轮自审与测试不关闭审阅关卡；Task7 保持**待限定复审**。Windows / Python 3.13.15 实测，不声称 Python 3.11、其他宿主、自然语言语义、人工批准或业务执行已验证。只读来源状态不是 pass/approval/release；未实施 Task8–18，没有 reviewer/subagent/workflow、安装、权限变更、hook 安装、远程操作、amend、push 或 PR。完成新局部提交及报告追加后停止，由调用方核对五项修正、完整 diff 和新旧证据保护。

<a id="task7-fix2"></a>
## Task7 第 2 轮局部修正：新 F1-N1

2026-10-16，按用户限定请求从干净的 `d622b14ed8a564a5ad11b28514ff9b41b484d4b8` 开始。fix1 限定复审已将原 T7-I1–I5 标为 addressed；本轮只处理新 Important F1-N1，不重新打开原五项。审阅者和父会话仅给出静态机制，以下是本轮新运行证据。

- 先在原正例中仅将 `### VT-002-RUN-01` 改为 `## VT-002-RUN-01`，完整表格/判据不变并刷新该来源基线。`fix2-red.json` 实际复现错误 available；六个聚焦方法出现六个失败断言/子例，0 错误/跳过。当时只改 `test_model_export.py`。
- 生产修改仅在 `_owned_runs`：锚点和紧随的真实标题关联，所属 `runs` H2 必须先建立，再接收下级标题；遇 peer/ancestor 标题立即结束，不能先接收其前置锚点。空行/注释可保留关联，说明、代码或另一锚点会打断未配对关联。`section_lines`、raw parser 和共享字面扫描器均未修改。
- `fix2-focused-green.json`：六个新方法和七个保留的运行记录控制，共 13 方法 GREEN。覆盖 H2 唯一变更、H1 ancestor、有效 H3、随后 peer/外部章节隔离及未配对锚点；H1 的原 MULTIPLE_TITLES 输入错误仍保留。各工具调用前后都核对实际输入字节。
- `fix2-model-suite.json`：只运行整个 `test_model_export.py` selector，实际发现/执行 **77 方法**，0 失败、0 错误、0 跳过，退出 0，40.500 秒。没有重跑或重标旧 313 全套、父会话 243 方法或独立 schema 套件。

新证据与辅助脚本只保存在本机会话 `files\ddd-alignment-execution\task7-evidence\fix2-*`，原报告的 fix2 追加位于 `task7-report.md`；起点摘要保存 116 个源文件、266 个旧证据文件及原日志/报告前缀。上述结果是局部工具与来源结构验证，不是业务执行或独立批准。

Task7 保持**待限定复审**。本轮只有该函数、同一模型测试文件、直接契约说明和当前状态/本日志变更；四份原 schema、32 kind、九视图与 8/21/3 不变。完成新局部提交和报告追加后停止；没有 subagent、Task8、应用、安装、权限/hook 配置、amend、push、PR 或远程操作。

<a id="task7-review"></a>
## Task7 复审关闭

2026-10-16，父会话直接读取 `d622b14ed8a564a5ad11b28514ff9b41b484d4b8` 至 `23c06b6bc46099c04091c61c036016b88cf4ae99` 的完整七文件局部 diff，核对 `_owned_runs` 的锚点/真实标题配对、peer/ancestor 截断和六个新控制。F1-N1 已处理，未发现此修正引入的重大问题；原 T7-I1–I5 沿用上一轮独立复审的 addressed 判定，不重复开展原始全量审阅。实际 head/parent/trailer、七路径范围和干净工作树/暂存区已重查。

本机会话 `files\ddd-alignment-execution\task7-fix2-review-result.md` 保存本轮逐项依据；`task7-fix2-parent-tests.json` 保存父会话在 `23c06b6` 的实际项目解释器、cwd、`test_model_export.py` 和原始输出：77 方法、0 跳过、退出 0，48.748 秒。此前 `task7-fix1-review-result.md` 与 `task7-fix1-parent-tests.json` 分别保存五项判定/新问题及 `d622b14e` 上的 243 方法结果。这些不同对象和范围不拼成一次新全套通过，旧 RED/报告仍保留。

Task7 的有限实现和范围复核关卡关闭，没有遗留的本任务审阅发现；不是增强整体、真实业务执行或跨宿主资格通过。本次只同步规格、计划、roadmap 和本日志。下一步按既有授权处理 Task8 的实施摘要桥接；真实结果仍归 VT/原始报告，不能由模型 available、commit 或测试文件存在推导。

<a id="task8"></a>
## Task8：从既有 owned VT 记录收集只读实施摘要

### 2026-10-16：任务、Git 与边界

按原执行授权、“恢复执行”以及用户单独选择“直接复用现有 VT 运行记录（推荐）”，只实施 [Task8 / ENH-12](../docs/plan/2026-10-14-ddd-functional-alignment.md#task8)。起点为 `d30b87b805a133bca54d25ce5887e06071e605c1`、分支 `callentan-repository-skeleton`，现有 App-isolated worktree；起始工作树/暂存区均干净。Task7 的两轮修正和复审关闭结论保留，未重做其审阅。

本节写入前再次检查暂存区为空，未提交内容仅属本轮工具、测试、表单及直接资料导航。局部提交的实际对象和提交后状态以本机会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution\task8-report.md` 最终追加为准；不在提交前编造自身 SHA。该报告/receipts 只在本机可访问，接手者须取得该会话材料。

### 本次变化

- [收集器](../.github/utilities/collect_implementation_report.py) 从明确 commit 读取 BC、验收、代码和测试文本，单独读取后追加的 VT owned runs/原始报告。scope、owner、criterion、对象/要求/计划基线和源码 marker 都需实际匹配；无记录保留逐目标 not-run，冲突失败，不建立另一个执行输入账本。
- [共用 VT reader](../.github/utilities/vt_records.py) 窄提取原 owned-run/四列结果读取，保留 H3 与关闭 H2/H1 的归属、注释/围栏和严格节隔离；安全 Git/固定 bytes 检查沿原模块共享。自查又用 RED/GREEN 覆盖共享判据、适用性表隔离、Unicode 行边界和声明来源保护。
- [model 桥接](../.github/utilities/export_model.py) 使用既有 verification 来源选择，验证报告 schema/scope/baseline 和可重建性，仅增加报告引用。其余 canonical/evidence/baseline 与九视图 gap 保留，不复制 entries/执行/适用性，也不向领域源写新 model。
- [报告空表](../_templates/reports/implementation-report.yaml)、[字段契约](../.github/contracts/README.md#implementation-report)、[使用入口](../.github/utilities/README.md#implementation-report)、开发/BC/验证说明及 handoff 直达导航已补齐。五份 schema、32 kinds、九视图、8/21/3 均未扩展；没有真实业务 BC/config/model/VT/application 写入生产目录。

### 实际结果入口

本轮原始证据在同一会话 `files\ddd-alignment-execution\task8-evidence\`。JSON 保存真实解释器、参数列表、cwd、stdout/stderr、退出、发现/执行/跳过和受检输入字节；不是日志重建的业务结果表。

- `baseline-retained.json`：在本轮起点实际运行 319 方法，0 跳过，退出 0。保留旧 313/243/77 的日期、范围和对象，不重标。
- `red-01/02` 至 `green-10`：先缺收集器 RED，再验证逐目标收集与 model bridge。保留安装夹具遗漏共用 reader 的一次失败及修正，不通过删测试解阻。合成源 pass/fail 只是输入，文本 fixture 不运行应用。
- `full-11-retained-new.json`：当时 373 方法全套通过；最终自查后新增五个控制，不能用此结果替代新对象。
- `red-12-final-boundaries.json`、`red-13-shared-criterion.json`、`green-14-final-boundaries.json`：按实际文件复现并修正声明来源目录写入、共享判据、适用性字面隔离、Unicode 投影和错误 evidence collection 形状。夹具的换行修正与产品缺陷分别记录。
- `full-17-final-retained-new.json`：**378 方法实际发现/执行，0 失败、0 错误、0 跳过，退出 0，386.857 秒**；受检输入 bytes 未变。`retained-inventory-comparison.json` 确认全部 319 个原测试身份保留，新增 59；最终含 contract 70、parser 78、checker 65、trace 29、model 86、collector 50。
- 文档/范围检查及原日志、报告前缀保护见 `check-16-docs-scope.json` 和报告的最终检查追加。辅助脚本最初未保留 checkout 的 CRLF 语义，其失败已留原输出，只修正辅助脚本参数，未改仓库配置。正式工件检查仍是 empty/0，不是业务通过。

### 缺口与下一步

Task8 状态为**已实施并完成本地验证，等待独立复核**。Windows/Python 3.13.15 实测；Python 3.11、其他宿主、人工身份/审批及真实业务执行均未据此认证。支持有限且明确的字段/selector/marker 语法，不承诺通用历史记录导入；不能认证外部事件实际发生。一个原始报告 I/O 拒绝控制采用窄边界注入，不冒充宿主 ACL 验证。

没有 subagent/reviewer/workflow、新 worktree、安装、权限或 hook/CI 配置、amend、push、PR、应用、远端及 Task9–18 操作。完成新局部提交和报告后停止；调用方下一步应核对精确 commit、源差异、全量 receipt、只读保护及报告可访问性，再进行独立 review。原 P3 和后续任务的未执行关卡保持原状。

<a id="task8-fix1"></a>
## Task8 第 1 轮限定修正（1/5）：T8-I1、T8-I2、T8-I3

2026-10-16，按用户本轮限定请求，从干净的 `7f747e55e480b92822c5599d1e9f54dccba98d9d`、原 `callentan-repository-skeleton` 分支开始。独立审阅/父会话给出的是静态反例，未提供新的运行复现；本轮先写真实文件/Git/CLI 测试，再改生产代码，不把上一轮 378 方法记录当作这三个反例的验证。

### 范围与修正

- T8-I1：仅调整 [声明位置登记](../.github/utilities/export_model.py)。root/path 的保护与 baseline 是否存在/有效分开；不完整或不可解析的 domainSources 声明阻止显式输出，但默认可选读取仍保留 gap。可解析位置继续保护子路径；YAML alias 不丢声明上下文。
- T8-I2：仅在[运行收集](../.github/utilities/collect_implementation_report.py)已有逐目标/判据核对之后，以 pass/fail 行的不同 testId 核对 recorded executed 下限。同一测试覆盖多个独立判据只计一次，额外实际执行可保留；不从命令文本、manual、skipped 或 not-run 推算数量。
- T8-I3：仅在[计划投影](../.github/utilities/vt_records.py)排除子树前检查全部声明 criterion 的真实正文锚点；位于 runs/applicability 被排除区的判据明确失败，不让修改后的判据冒充旧计划。原标题归属、严格判据边界及 Unicode/BOM/CRLF bytes 保留。
- 测试只增加在两个已有 collector/model 模块；直接文档仅澄清这三处规则并同步当前状态。五份 schema、32 kinds、九视图、8/21/3 不变，没有新的结果输入账本。

### 实际证据入口

本机会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution\task8-report.md` 追加本轮完整报告；新 receipts 均在其 `task8-evidence\fix1-*`。这些材料仅本机可访问，不是下游运行依赖。

- `fix1-before.json` 保存 120 个源文件、1305 个旧任务材料及本报告/原日志前缀身份。
- `fix1-red-01-all-findings.json`：生产代码未变时 16 方法、18 个失败断言/子例、0 错误/跳过，退出 1。`fix1-red-verified.json` 确认三个生产文件仍等于起点，I3 未被其他 guard 掩盖。
- `fix1-red-02-i1-files.json`：6 方法、13 个失败断言/子例，明确观察到不该创建的文件实际被写入受控 fixture；新增 alias 上下文控制。测试只清理自己的错误输出，没有写真实领域源。
- `fix1-green-03-i1.json`、`fix1-green-04-i2.json`、`fix1-green-05-i3.json`：三个聚焦组分别 6、6、5 方法通过，0 跳过、退出 0；均核对输入 bytes/file-set。
- `fix1-full-06-retained-new.json`：完整 retained+new 实际发现/执行 **395 方法**，0 失败、0 错误、0 跳过，退出 0，460.423 秒；受检源字节未变。原 378 项结果保留原对象，新结果不拼接旧 319/373/378 或 Task7 的历史结果。
- 最终范围、链接/语法、旧材料与提交后字节核对，以及新 commit SHA，沿上述完整报告的最终追加查看；不在提交前预填自身 SHA。

### 关卡与后续

本轮本地修正和验证不等于独立批准，Task8 保持**等待限定复审**。合成 VT 记录只验证收集/归属/拒绝路径，不证明外部业务事件或人工审批；实测仍限 Windows/Python 3.13.15，其他宿主和 Python 3.11 未运行。

未启动子代理、reviewer、工作流、Task9、应用/原生业务测试、安装、权限/持久 hook 配置、amend、push、PR 或远端操作。完成新范围内本地提交与报告后停止，由调用方核对本轮精确 commit、三处机制、全部新原始证据及旧记录保护，再做限定复审。

<a id="task8-fix2"></a>
## Task8 第 2 轮限定修正（2/5）：T8-F1-N1

2026-10-16，按本轮限定请求，从干净的 `062e607cde5cd5ecb2a0b2d83bff60ab2940c867` 和原分支/worktree 开始。第 1 轮限定复审已将原 T8-I1/I2/I3 判为 **ADDRESSED**，本轮不重开；只处理业务 tree 的 root/path 被误作领域位置而拒绝合法输出的新 Important。审阅中的这一新反例是静态追踪，下面是新的运行证据。

- 先只改 `test_model_export.py`，复用现有完整 QAS/utility-tree 夹具，写入审阅给出的 mapping/list 数据并刷新实际 baseline。另加字符串业务标签控制，确认不会生成虚假的受保护目录。两例均通过真实 CLI 导出与 check 往返核对，除显式新输出外全部源 bytes/file-set 保持原样。
- `fix2-red-01-tree-roundtrip.json`：生产代码未改时 2 方法失败，实际只读 quality 为 available，但合法输出被 `REPORT_CONFLICT` / 2 拒绝，0 错误/跳过。
- 生产修改仅在 [reserve_declarations](../.github/utilities/export_model.py) 的一个判断条件及注释：缺 baseline 的特殊保护仍在真正的 domainSources 条目上下文生效；其余节点恢复完整 root/path/baseline 的既有 provenance 形状要求，不凭两个业务键猜目录。没有禁用/改名 tree 键，没有改 tree adapter 或 I1 的缺失/不完整/alias/目录保护，也没有改 reference/path+baseline 处理。
- `fix2-green-02-tree-roundtrip.json`：2 方法 GREEN，0 跳过，退出 0，3.580 秒。
- `fix2-model-03-complete.json`：只选择整个 model 模块，实际发现/执行 **94 方法**，0 失败/错误/跳过，退出 0，160.163 秒，受检源字节未变。原 92 个模型测试均保留，新增 2；未重跑 395 全套或 collector 套件。

新材料在本机会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution\task8-evidence\fix2-*`；完整报告追加至同处 `task8-report.md`。`fix2-before.json` 保存 120 个源文件、1322 个旧任务材料及原报告/日志前缀身份。旧 395 全套及父会话在起点运行的 153 方法记录保留其原范围和对象，不计作此次新反例的执行证据。

本轮只改一处生产机制、同一模型测试文件、直接契约说明和最小状态/日志。schema、32 kinds、九视图和 8/21/3 不变；原 I1/I2/I3 addressed 判定保留，Task8 仍**等待限定复审**。实际新提交与提交后状态沿完整报告最终追加查看。

没有子代理/reviewer、Task9、应用/原生执行、安装、持久权限/hook 变更、amend、push、PR 或远端操作。实测仅 Windows/Python 3.13.15；来源可读/可导出不认证业务结果、人工批准或跨宿主资格。局部提交和交接后停止，由调用方继续限定复审。

<a id="task8-review"></a>
## Task8 复审关闭

2026-10-16，父会话直接核对 `062e607cde5cd5ecb2a0b2d83bff60ab2940c867` 至 `9a3055acf51bcebab9f2a833b91c577a0c1cae49` 的完整七文件局部 diff、两个真实往返控制及报告追加。T8-F1-N1 已处理：缺 baseline 的保护仍由真实 domainSources 上下文驱动，普通业务 root/path 不再误声明路径；原域位置、alias、目录和引用保护保持。未发现本修正引入的重大问题，原 T8-I1/I2/I3 维持上一轮 addressed 判定。

本机会话 `files\ddd-alignment-execution\task8-fix2-review-result.md` 保存本轮复核依据；`task8-fix2-parent-tests.json` 保存父会话在 `9a3055a` 的实际解释器、cwd 和模型模块原始输出：94 方法、0 跳过、退出 0，157.340 秒。前轮三项判定及新问题在 `task8-fix1-review-result.md`，对应独立 collector/model 153 方法结果在 `task8-fix1-parent-tests.json`。这些记录及旧 395 全套不合并、不替换彼此的对象与范围。

实际 head/parent/trailer、七个提交路径和干净工作树/暂存区已重查。Task8 的有限实现与范围复核关卡关闭，没有遗留的本任务审阅发现；不认证真实业务执行、人工批准或其他宿主。下一步按[任务 9](../docs/plan/2026-10-14-ddd-functional-alignment.md#task9)处理可选治理/审阅/工具资格资料；应用、媒体、平台和发布的独立边界仍保留。

<a id="task9"></a>
## Task9：可选审阅、工具用途、Intended Use 与风险引用

2026-10-16，按本轮 Task9 / ENH-09 明确授权，在原 `callentan-repository-skeleton` worktree 从干净的 `002ad73a18700e7c95b21a0fa7d0d84a26f453b5` 开始，暂存区及原有未提交范围均为空。任务 1–8 的已关闭关卡不重开。依据[增强规格](../docs/design/ddd-functional-alignment.md)、[Task9 计划](../docs/plan/2026-10-14-ddd-functional-alignment.md#task9)及固定矩阵 DOMAIN-08、DOMAIN-20、FRAMEWORK-03 的既有记录，不重新获取或运行参考来源。

### 本轮变化与归属

- 新增[治理指引](../docs/governance.md)、[AI 工具说明](../docs/ai-tooling.md)，以及[审阅记录](../_templates/items/review-record.md)、[工具资格/使用](../_templates/items/tool-qualification.md)、[Intended Use](../_templates/items/intended-use.md)、[风险控制引用](../_templates/items/risk-control.md)四张可选空表。
- 只合入 README、相关领域/要求/架构/验证/日志指引的必要导航，以及原 define-requirements、verify-change、record-handoff 的字段入口。新表保持 draft；身份/内容声明/真实关系归 frontmatter，实际决定、评价、当前适用性和 VT 结果不互相替代。
- 保留现有源接口：review 的 `decision` 两列原字段，risk 的 `analysis/control/residual` 与原风险字段。没有生产工具、schema、依赖、prompt、角色或新方法变更，没有正式治理/QMS/业务实例；仍为 8 方法、21 prompts、3 模式。

### 实际检查与证据入口

本机会话 `1ff56941-bf56-4aa4-b769-fd4720915e1f` 的 `files\ddd-alignment-execution\task9-evidence\` 保存本轮原始证据；同级 `task9-report.md` 汇总精确命令、cwd、源字节、状态与最终提交。只在本机可访问，不是公共或跨机器 CI 证据。

| 证据入口 | 对象、观察与限制 |
|---|---|
| `baseline.json`、`baseline-reading.md` | 精确干净起点，120 个原文件与 1353 个旧任务材料的 bytes 身份；已有方法对 10 情形的安全决定原本成立，没有伪造 RED |
| `method-use.md` | 三处方法导航的逐项直接应用；只读输入仍返回发现，不执行/保存；不是独立 Agent、人工 T17 或原生权限观察 |
| `run-03\provenance.json`、`case-results.json` | 10 个预备情形、11 份实际复制/填写的四类表单，保存模板与实填 bytes、字段、完整身份及具体缺口 |
| `run-03\check-filled.json`、`command-*.json` | 现有 checker 实际尝试/检查 13 个正式合成记录，clean；四种缺确认元数据由 parser 报 INVALID_METADATA；source/result 两个已存在输出目标均拒绝覆盖 |
| `run-03\model-alpha.json`、`model-beta.json`、`model-unavailable.json` | 合成决定治理来源 available 不等于批准；未知控制前/残余风险为 partial，不可用来源为 unverified；异 scope 同号不混用决定 |
| `run-03\coverage-missing.json`、`optional-free.json` | 完整两项目标盘点定位第二项 UNCOVERED_ACCEPTANCE，VT 原 not-run 不改写；无治理要求的维护为 empty 库存，不算业务通过 |
| `run-03\navigation.json`、`protected-bytes.json` | 104 个候选文件、619 条本地链接/锚点无缺口；不含制作资料/测试依赖，输入与旧结果 bytes 保留，拒绝覆盖另列 |

夹具只在忽略的 `.venv` 中，报告与记录脚本只在上述获准的绝对会话目录。采用现有 Python 3.13.15、PyYAML 6.0.2、jsonschema 4.23.0；实际 parser 评价的两个自有合成输入、0 跳过与环境/观察保存在夹具原始 `sources\evaluation.json`，不是业务测试。没有重跑无关 Python 全套。前两次有界运行原样保留；后续只细化演练输入的版本变更、用途/跟进与对象范围，未修改生产 validator，不把这些运行合并为更多验收项或伪造失败基线。

### 限制与下一步

本轮已完成文档实施与自审，**Task9 等待独立范围审阅**，不记录真实 expert/clinical/regulatory approval、风险接受或工具资格。合成具名决定仅证明字段/导航可用；实际确认、组织政策、外部风险源、人工 T17、客户端/OS 权限与业务应用均未验证。当前 Markdown 规则不成为 ACL 或 sandbox。

本轮只授权 20 个文档路径；实际本地提交及提交后 Git 状态以报告最终记录为准，不预填 commit。旧日志前缀与历史结果保持，后续审阅应重查精确提交、实填副本、源字段缺口和只读/覆盖保护。没有子代理/reviewer/workflow、Task10 或后续实现、应用、安装、hook/权限配置、amend、push、PR、发布或远端操作；提交与报告完成后停止，等待本任务的范围审阅。

<a id="task9-review"></a>
## Task9 独立范围审阅关闭

2026-10-16，独立 reviewer 核对 `002ad73a18700e7c95b21a0fa7d0d84a26f453b5` 至 `3b818e5902f343a808fe476033256902f0d32a2d` 的全部 20 个 Markdown 变更，判定符合 Task9 / ENH-09 文档范围、质量可接受，无 Critical/Important/Minor 发现。另行只读核对既有 confirmation schema 和 model-source 的 review/risk 字段兼容，没有执行工具或重新审查 Task1–8。

原始审阅会话的结果定位与兼容性依据保存在本机会话 `files\ddd-alignment-execution\task9-review-result.md`。父会话已重查实际 head/parent/trailer、变更范围和干净 Git；独立 `task9-parent-consumer.json` 保存现有 checker/trace CLI 的真实参数、cwd、输出与前后字节：13 个正式合成记录 clean，仍精确发现 `task9/alpha/REQ-SYN-001#req-syn-001-ac-02` 在来源第 16 行未覆盖，输入未变。此故意保留的夹具缺口不是产品待办，也没有被伪造为通过。

Task9 的文档实现/审阅关卡关闭，不认证真实专家决定、工具资格、风险接受、人工 T17 或权限。后续按[Task10](../docs/plan/2026-10-14-ddd-functional-alignment.md#task10)实现可选 hooks/CI，并只在受控本地 Git 夹具试验；不在当前真实工作树安装 hook，不更改远端 required checks，也不从文档存在推断 CI 已运行。
