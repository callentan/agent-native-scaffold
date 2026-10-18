# 开发说明

**维护工具与业务应用分别登记。** 可选的本地维护工具使用 Python；这不为下游业务应用选择技术栈。业务应用仍未配置，没有应用项目、依赖或运行命令。资料填写和文档维护可以继续；应用构建与测试对当前空白骨架不适用，不代表应用验证通过。若已规划业务或软件行为 VT，它仍保持 `not-run`，并记录缺少对象或环境的原因。

<a id="maintenance-tools"></a>
## 仓库维护工具（不是业务应用）

| 项目信息 | 当前值 |
|---|---|
| 标识与范围 | `artifact-maintenance`；本地解析、工件/覆盖检查、影响候选、派生引用模型、实施摘要、只读三方/多目标提案、可选来源清单、本地领域源预检/明确接入、文档/转录候选评分、本地关系图/架构/演示导出和可选 hook/资料 CI 接入，不是业务应用 |
| 相对位置与原生布局 | 模块在 `.github\utilities\`，JSON Schema 在 `.github\contracts\` |
| 技术栈 | Python 3.11+、PyYAML 6.0.2、jsonschema 4.23.0 |
| 环境 | 仓库自己的 `.venv\`；不安装全局包，不要求 PowerShell 7，不配置下游应用 |
| 依赖来源 | [直接依赖 manifest](../.github/utilities/requirements.txt) 与[实际解析的 lock](../.github/utilities/requirements.lock)；原六项版本保留，`referencing` 在 Python `<3.13` 所需的 `typing-extensions` 另按实际元数据/安装结果锁定，3.11 选七项、3.13 选原六项 |
| 接口与边界 | [模块调用与错误码](../.github/utilities/README.md)、[数据契约与完整示例](../.github/contracts/README.md)、[来源候选与评分](source-extraction.md)、[本地文档导出](document-exports.md)；音频/PDF/PPTX 仅拒绝入口，不包含实际服务、二进制 renderer、云端或业务应用 |
| 使用前提 | 使用者须核对本地解释器和已安装依赖；维护者回归与执行历史不随候选分发，不是下游运行前提 |

以下命令均以仓库根目录 `.` 为 cwd，Windows 使用 `.venv\Scripts\python.exe`；其他宿主应使用其实际项目解释器（例如 `.venv/bin/python`），不要照搬 Windows 路径。无需激活环境或修改全局 PATH。

| 操作 | 真实命令 | 原始输出位置与限制 |
|---|---|---|
| 初始化本地环境 | `python -m venv .venv` | 当前终端；先核对所用 Python 为 3.11+ |
| 首次恢复直接依赖 | `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.txt` | 当前终端；仅在 manifest 已创建后执行 |
| 恢复已锁定依赖 | `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.lock` | 当前终端；按锁定版本恢复本地环境 |
| 核对安装版本 | `.venv\Scripts\python.exe -m pip freeze` | 当前终端；与 lock 核对实际版本，不自动更新锁定清单 |
| 核对环境一致性 | `.venv\Scripts\python.exe -m pip check` | 当前终端；不能用退出 0 代替行为测试 |
| 工具源码语法 | `.venv\Scripts\python.exe -X utf8 -m compileall -q .github\utilities` | 当前终端；只检查已分发源码的语法，不替代行为验证 |
| 正式工件完整检查 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_artifacts.py --root .` | JSON stdout；不自动保存报告，empty/退出 0 不代表业务通过 |
| 精确历史比较 | 上行增加 `--base <已核对的完整 commit ID>` | 验证目标仍是当前文件的完整正式库存，不只检查变更或暂存内容；精确对象不可读退出 2 |
| 明确保存检查报告 | 检查命令增加 `--report <获准的新 JSON 路径>` | 相对路径以 root 为准；父目录须存在，已有文件一律拒绝，不改写源文件或历史记录 |
| 完整交付覆盖 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_traceability.py --root . --delivery <完整验收引用>` | 每个交付项重复 `--delivery`；stdout JSON，可选 `--report`；不从 VT 倒推范围，不执行 VT |
| 规则变化影响候选 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_traceability.py --root . --base <完整 commit>` | 可重复 `--task <实际 scope/id>`；合并旧新依赖，人工判断语义 |
| 模型只读派生 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\export_model.py --root . --scope <实际 project/context>` | JSON stdout；从可选 `model-sources.yaml` 选择来源，主输入失败退出 2 |
| 旧模型检查 | 上行增加 `--check <已有 .json/.yaml/.yml>` | 只读重算；来源变化/手改退出 1，输入错误退出 2，不修复源或模型 |
| 明确创建新模型 | 只读派生命令增加 `--output <获准的新 .json/.yaml/.yml>` | 与 `--check` 互斥；exclusive create、不建父目录，不占用登记来源路径 |
| 收集实施摘要 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\collect_implementation_report.py --root . --object <完整本地 commit>` | JSON stdout；按实际选择重复 `--evidence <VT相对路径[#运行锚点]>`，多 BC 须加 `--scope`；不执行 VT 命令 |
| 明确创建新实施报告 | 收集命令增加 `--output <获准的新 .json/.yaml/.yml>` | exclusive create、不建父目录，不覆盖已有文件或占用缺失的声明来源；不自动登记 model 来源 |
| 三方模板更新提案 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --base <实际旧根> --local <实际本地根> --candidate <实际候选根>` | JSON stdout；可各加 `--base-version/--local-version/--candidate-version` 验证准确版本；缺旧根为错误，不应用 |
| 明确 BC 的场景提案 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --registration <实际本地登记.yaml> --target <明确ID>` | 每个目标重复 `--target`；只读已存在的本地根，逐目标结果，不 clone/fetch 或复制 model/整仓 |
| 明确保存更新提案 | 提案命令增加 `--output <获准的新 .json>` | exclusive create、不建父目录；必须在所有登记来源/目标之外，含缺失及未选目标；conflict 退出 1、unavailable/input-error 退出 2，不以保存报告当应用 |
| 检查实际暂存快照 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\hook_checks.py pre-commit --root .` | JSON stdout；index/blob/tree 身份、全部 owner 验收和显式空覆盖；可加精确 `--base` 与新 `--report`，不自动修复/暂存 |
| 查看可选 hook 安装提案 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\install_hooks.py --root . --python "<实际项目解释器绝对路径>" --hook pre-commit --hook commit-msg` | 默认无写入；报告目标/冲突及 shared metadata 范围；实际安装另需本次目标授权和 `--apply` |
| 检查已登记的本地领域源 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\setup_domain_source.py --root . --config bc-config.yaml --source-id <明确ID>` | JSON stdout，默认只读；来源根/相对路径/固定基线来自原 BC 字段；0 ready、1 conflict、2 unavailable |
| 明确登记一个本地领域源 | 按[准确来源参数](domain-sources.md#cli)先 inspect，再加 `--operation register --apply --owned-target --expect <本次preflight>` | 只维护指定既有 BC 的 domainSources，不复制领域文件、不暂存、不提交；没有项目配置就停止 |
| 可选本地子模块 | 同一来源参数另选 `--operation submodule --target <准确相对目标>` 先 inspect；应用另加 `--apply --owned-target --index-consent --expect <本次preflight>` | [原生操作](domain-sources.md#submodule)会写 .gitmodules/local config/module metadata/index，独立于 BC 登记；仅明确本地源，无网络/commit/push |
| 本地文档/转录候选 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\extract_source.py --root . --source "<明确本地源>" --kind <markdown/text/transcript/docx>` | JSON stdout；[精确格式与有界 DOCX](source-extraction.md#formats)，不是 formal artifact；可加 root 内不存在的 `.json` `--output`，不建父目录 |
| 透明候选评分 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\score_candidates.py --root . --input "<明确候选.json>"` | JSON stdout；可加新 `--output`；[公开因素与范围](source-extraction.md#scoring)，不决定接受或覆盖冲突 |
| 音频不可用检查 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\transcribe_audio.py --source "<明确本地音频路径>"` | 当前退出 2：授权/缺项/适配器不可用；不读音频/环境密钥、不调用服务、不写 transcript；[后续独立关卡](source-extraction.md#audio) |
| 本地关系图 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_traceability.py --root . --scope <实际 project/context> --format <json/svg/html>` | 默认实际文本 stdout；源与持久 model 漂移须核对，无数据明确 empty、不造 demo |
| 本地架构/SEQ 文档 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_architecture.py --root . --scope <实际 project/context> --format <html/svg> --source "<实际引用>" --baseline <固定对象>` | 每个 source 有对应 baseline；实际源章节/九视图和有限 SEQ 图，不补部署、风险或批准 |
| 本地参数化演示 | `.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_presentation.py --root . --scope <实际 project/context> --format <html/svg> --source "<实际引用>" --baseline <固定对象>` | 选中源章节驱动 slides，不是固定 deck；HTML/SVG 不冒充 PDF/PPTX |
| 明确创建导出文件 | 上述命令增加 `--output <获准的新同格式文件>` | exclusive create、不建父目录；[隔离/拒绝/退出契约](document-exports.md#cli写入和错误边界)；PDF/PPTX unavailable 不创建文件 |

这组命令不执行工件正文、引用命令或应用，也不安装 hooks、CI、媒体或平台包；不依赖已从下游候选排除的维护者测试。各工具的[发现规则、状态/计数、JSON 和基线](../.github/utilities/README.md#artifact-checker)、[覆盖](../.github/utilities/README.md#traceability)、[模型](../.github/utilities/README.md#model-export)、[实施摘要](../.github/utilities/README.md#implementation-report)与[只读更新提案](template-updates.md)分别约束其结果；这些检查/派生/提案 API 不写文件。[来源接入](domain-sources.md)的独立 apply API 另受准确目标、preflight 与授权限制，不因 readOnly 或已有配置获得许可。来源清单只保存[本地引用与固定基线](../.github/contracts/README.md#model-sources)，不是执行 manifest。报告复用现有 VT 的 owned runs，不维护另一份执行输入；收集退出 0 可含 not-run，退出 1 表示收集到 fail，退出 2 是输入/输出错误。模型完整性、结构覆盖、成功收集或干净提案都不等于业务通过或传播完成。尖括号参数由本次实际输入替换。

来源接入的配置 token 绑定实际读取/解析的 bytes，inspect 过程中变化也停止；
新子模块的 index 同意不能撤销 owner 已暂存的 `.gitmodules` 删除。
[Git 配置读取边界](domain-sources.md#git-config-boundary)在受影响命令前拒绝本地 include/
includeIf、网络 metadata 指针和别名，不去包含位置探测或自动改配置。网络/真实项目
接入仍需独立授权，不由资料可读或本地夹具结果授予。

本地导出复用上述主库存、来源选择、原始基线和 report/model 核对，
不另建 schema、结果库或执行输入。JSON/SVG/HTML 使用既有 stdlib，
[rendering 清单](../.github/utilities/requirements-rendering.txt)没有新增依赖。
PDF/PPTX 的实际引擎、安装、签名/parser、非零页/slide 与源内容/人/App 检查
保持单独 not-run；未选 renderer 时不探测全局包或静默换格式。

可选安装、恢复和原生运行边界见[hooks 说明](../.github/hooks/README.md)。
Windows 薄 launcher 使用 Git 自带 `sh`，只启动准确项目解释器；不要求 PowerShell 7。
installer 不覆盖 owner hook、不改 `core.hooksPath`，也拒绝默默影响 sibling worktrees。
每次 hook 启动在读取工件/index 前重验选定 venv、配置和固定依赖；环境丢失时
明确拒绝，不仅记录 prefix，也不回退全局。安装 I/O 失败保留完整/部分创建的
逐路径恢复状态，不自动删除后续 owner 内容；恢复须按 hooks 说明核对所有权。
下游资料 workflow 只调用分发模块；制作仓回归 workflow/计数 runner 不分发。
复制 YAML 不建立 required checks；托管运行与服务端配置须另有授权及实际证据。
模板提案 workflow 也只在制作仓维护者侧手动使用，要求可信 runner 上预先存在的准确本地输入；
它不是下游运行依赖，不包含目标 checkout/写分支/PR，也未因本地实现而成为已执行的平台能力。

<a id="creation-inputs"></a>
## 何时可以创建项目

只有用户明确选择目标项目、技术栈和位置，授权创建，并提供足够的任务目标、行为依据、约束及有效开发输入后，才使用该项目的原生工具生成或接入工程。先检查目标目录和已有修改，不自动选择语言、安装依赖或创建示例应用。

已有项目保留其原路径和原生代码、测试、依赖布局，不强制搬进 `src\`，也不要求建立统一测试目录。新项目可直接放在 `src\`，或放在 `src\<project>\`；两者只是位置选项，不是已经存在的工程。

<a id="project-registration"></a>
## 子项目位置与命令登记

本节只登记**下游业务应用**，当前仍未配置；上面的维护工具不是应用子项目。创建或接入真实项目后，按子项目复制下面这一组登记表。每组对应一个项目，多个命令不要混用工作目录。所有本地位置以仓库根目录为基准记录相对路径；执行前在当前工作区解析并确认，不记录个人绝对路径。

| 项目信息 | 当前值 |
|---|---|
| 子项目名称或标识 | 未配置 |
| 子项目相对位置 | 未配置 |
| 原生布局（源码、测试、配置的实际位置） | 未配置 |
| 技术栈、工具与版本 | 未配置，待用户选择 |
| 环境前提与依赖来源 | 未配置；不记录凭据 |
| 任务/用户选择依据及适用范围 | 待填写 |

| 操作 | 真实命令 | 实际工作目录（仓库相对路径） | 原始报告/输出位置 | 适用条件与限制 |
|---|---|---|---|---|
| 安装依赖 | 未配置 | 未配置 | 未配置 | 暂无项目，不执行 |
| 构建 | 未配置 | 未配置 | 未配置 | 暂无应用，对当前文档任务不适用 |
| 运行 | 未配置 | 未配置 | 未配置 | 暂无应用，不执行 |
| 测试 | 未配置 | 未配置 | 未配置 | 暂无应用；已规划行为 VT 仍为 `not-run` |

这些“未配置”不是可执行命令。不要用空脚本、打印成功或无实际检查的命令占位。填写时依据真实工程确认命令、cwd、报告位置及用途；命令退出为零不等于验收通过。检查范围、发现数、执行数、跳过数和实际结果按[验证指引](../verification/README.md#execution)记录。

报告位置只指向实际输出或获准的报告入口；尚不存在就写待配置。项目工具产生的文件按真实位置补充忽略规则，不能忽略正式需求、验证文档或开发日志。

<a id="document-checks"></a>
## 当前可做的文档检查

可用正式工件检查器核对其[限定 Markdown 语法](../.github/utilities/README.md#checker-format)、元数据、ID、占位与本地链接；没有正式工件时明确输出 `empty`。它不是全部文档扫描器或语言 CI，普通 README/guide、覆盖与语义仍须按本次任务核对。尤其不能把文件/锚点有效等同于[验收覆盖和语义影响](../verification/README.md#coverage-check)已核对。

若使用已有本地工具检查，应记录实际工具、命令、工作目录、对象基线和原始结果入口；不把作者机器上的外部脚本当作仓库自带能力。人工核对记录所读工件、基线、观察和限制，不伪造命令。文档检查不能替代业务验收或软件行为执行。

<a id="troubleshooting"></a>
## 缺项与排障入口

| 缺项或问题 | 已知依据与影响 | 需补充的输入或下一步 |
|---|---|---|
| 业务应用环境与命令未配置 | 维护工具环境已单列；当前无业务应用，不阻塞文档任务 | 用户决定创建实际项目后补全业务应用登记，不复用工具栈代选应用 |
| 其他问题 | 待填写 | 待填写 |

命令不可用、输入冲突或环境不满足时报告具体原因，不静默换工具或把未执行写成成功。命令、项目或验收基线改变后重新判断结果适用性，在[日志](../logs/README.md)中保留待复核和未执行项。
