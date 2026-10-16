# 只读模板更新与明确多目标提案

使用 [update-template](../.github/skills/update-template/SKILL.md)。本页维护工具输入/输出契约，不保存业务事实或另一份执行结果。工具只比较**已存在的本地**旧基线、所有者文件和新候选；不应用、合并、clone/fetch、commit/push、建 PR、发现凭据或更新外部领域源。提案不是许可，配置也不是许可。

<a id="api"></a>
## API 与实际输入

从 `.github\utilities\plan_template_update.py` 导入：

```python
plan_update(base, local, candidate) -> UpdatePlan
TreeSource(root, version=None, files=None)
plan_batch(registration, target_ids) -> BatchPlan
```

`base/local/candidate` 各为显式本地目录路径，或一个不可变 `TreeSource`。
三个根必须存在、可枚举、互不包含且没有目录别名；文件必须是可读普通文件。
拒绝 URL/UNC、歧义 drive-relative、文件系统根、symlink/junction/reparse point，
不跟随链接到根外，也不把缺根/读失败解释为空树。根外的其他本地源只通过显式根选择。

`files=None` 比较三个根各自的完整合资格文件集；三方路径并集参与判定，包含本地专有文件。
`files` 若提供，须在三个输入中都是**同一组**非空 tuple，路径按 `/` 相对各自根，
无空段、`.`、`..`、反斜杠、冒号、片段、控制字符、重复或大小写别名；
不使用 glob 或猜测目标。选定路径可在某侧缺席；完整读取失败不是缺席。
多目标模式另按下面显式映射源和目标的不同文件位置。
文件/目录拓扑冲突或跨侧仅大小写不同的路径为输入错误，需所有者解决，不猜重命名。
完整树的文件、目录及父前缀统一按 case-folded 身份检查，不能将 `Settings` 文件与
`settings/owner.md` 所在目录判成“本地缺席、候选可新增”。显式映射也先核对实际目录项名称，
再判断缺席；不裁剪或隐藏本地所有者文件来消除碰撞。

根、登记文件与输出路径的原始 traversal 在 canonicalize 前逐前缀核对。
经过 symlink/junction/reparse point 后再用 `..` 抵消、或经不存在/非目录前缀再返回的声明，
都不会被 `abspath` 替换成另一棵可读树。正常的显式 `../sibling` 仍可用；
不能验证的缺失前缀/父遍历不用于推导成功来源或输出保留位置。

排除仅按**本次根之下**的目录/文件段：`.git`、`.venv`、`venv`、`node_modules`、
`__pycache__`、`.pytest_cache`、`.mypy_cache`、`.tox`、`.nox` 为 `TOOL_DATA`；
`test/tests/fixtures` 为 `TEST_FIXTURE`，大小写不敏感。排除记录含相对路径及理由，
目录尾随 `/`，不读取其内容；显式文件选择若含这些段则拒绝，不静默缩小范围。
根的 `.venv` 祖先不参与排除，独立夹具仍能读取。`_templates`、skills、rules 并非自动排除。
这不是发布 allowlist；准备候选时须另提供本次获准的文件清单，不复用历史 38 文件基线，
也不把整个制作仓或业务仓当成已获准的模板版本。

### 精确版本与摘要

未给 `version` 时，以实际读集生成内容身份；不给“脏工作树”冒用 HEAD。
给了版本则必须验证，既不能只作标签，也不回退分支、main/master、index 或空祖先。

| 版本 | 核对方式 |
|---|---|
| `sha256:` 加 64 位小写十六进制 | 对下述确切 scoped snapshot 算法核对，不是单个文件摘要 |
| 完整 40/64 位小写 Git commit ID | 根必须正好是相应本地 checkout 顶层；读取该精确 commit 的原始普通 blobs，与实际合资格文件集/bytes 相同。显式文件范围只核对那些路径及缺席，不要求无关文件相同 |

内容 snapshot 是对象 `{"files": records, "selection": selection}` 经
`json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True)`、UTF-8 编码后的
SHA256，并加 `sha256:`。`records` 按 path 排序，每项为
`{"path": 根相对路径, "sha256": "sha256:原始文件摘要", "size": 原始字节数}`，
只含实际存在的文件；`selection` 为 `null`（完整范围）或排序后的显式路径数组。
因此同一文件集的完整范围与显式范围身份不同；换行、BOM、二进制和 Unicode 不归一化。
空但实际存在且可读的根与不存在的根不同。该比较不规划 chmod/文件权限变化。

Git 读取复用已有受限本地 helper：参数列表、显式 cwd、`shell=False`，不运行 hooks、
filter/textconv、replace refs、来源命令、lazy fetch 或继承的 Git 配置覆盖。
精确对象/普通 blob 不可读就失败。读取后重新核对字节、文件/目录集及登记文件；
变化为 `INPUT_CHANGED`。这不是文件系统事务或 OS sandbox，不能防御所有并发恶意替换。

### 窄输出记录

`UpdatePlan` 的 `changes/conflicts/preserved/sources` 均为不可变 tuple。
`status` 为 `proposed/no-change/conflict`，`to_dict()` 可直接 JSON 序列化。

- 每个 `UpdateItem` 有目标 `path`、`action`、`reason` 及 `base/local/candidate` 三个身份。
- 每个文件身份有实际该侧 `path`、`source`（三方角色）、`version`、原始 `sha256`、`size`。
  `sha256: null, size: null` **明确表示该路径缺席**，不表示读失败。
- 每个来源有 `role/root/version/snapshot/files/excluded/selection`；`files` 保存存在的文件身份。
  单次三根调用的 root 是实际本机路径；多目标 root 保持相对登记位置的声明，便于移交。
  不输出文件正文、自动合并内容或差异 patch；这是逐路径/版本/摘要的精确操作提案。
- API 输入失败抛现有 `ArtifactInputError(code, path, line, message)`，不返回成功空提案。
  报告只含必要诊断；不将原始 YAML 错误中的值/片段复制到 stdout。

### 三方路径判定（UPDATE-01…16）

| 输入：旧 / 本地 / 候选 | 结果与 reason |
|---|---|
| 三侧相同 | preserve / `UNCHANGED` |
| 仅本地修改，候选等于旧 | preserve / `LOCAL_MODIFIED` |
| 仅候选修改，本地等于旧 | modify / `CANDIDATE_MODIFIED` |
| 两侧修改后相同 | preserve / `ALREADY_ALIGNED` |
| 两侧修改不同 | conflict / `BOTH_MODIFIED` |
| 候选删除、本地未改 | delete / `CANDIDATE_DELETED`，不实际删除 |
| 候选删除、本地修改 | conflict / `DELETE_MODIFY` |
| 本地删除、候选未改 | preserve / `LOCAL_DELETED`，不复活 |
| 本地删除、候选修改 | conflict / `MODIFY_DELETE` |
| 旧/本地无、候选新增 | add / `CANDIDATE_ADDED`，不实际创建 |
| 旧无、本地/候选不同新增 | conflict / `ADD_ADD` |
| 仅本地有业务文件 | preserve / `LOCAL_ONLY` |
| 旧无、两侧相同新增；两侧都删除 | preserve / `SAME_ADDITION`、`BOTH_DELETED` |
| 旧根缺失/不可读、提供的版本错误 | input error，不是文件删除 |
| 二进制、BOM、换行、中文/空格路径 | 原始 bytes 与确定路径/顺序判定，不做文本归一化 |
| 链接/越界/缓存/夹具；源漂移或输出冲突 | 明确错误或上述排除；不写源、不覆盖历史 |

<a id="registration"></a>
## 可选本地多目标登记 v1

[空白数据表单](../_templates/config/template-updates.yaml)可复制填写，空值/列表不是可用配置。
实际登记由共享 SafeLoader 读取 YAML/JSON，复用重键、merge 冲突、循环别名、未知/不安全
tag 的拒绝规则；只接受下列字段，不接收命令、凭据、`apply` 或授权标志。无须新结果数据库。

| 位置 | 必填形状 |
|---|---|
| 顶层 | `schemaVersion: 1`（真正的整数）、`source`、非空 `targets` 列表 |
| `source` | `repository`、`base`、`candidate`、非空 `files` 列表 |
| `source.base/candidate` | 仅 `root`、`version`；版本必须为上述确切 Git/content 身份 |
| `source.files[]` | 仅 `scenario`、`path`；唯一来源场景引用 `project/context/ID#anchor`，唯一允许的根相对 `.feature` 文件 |
| `targets[]` | 仅唯一 `id`、`repository`、`scope`、`local`、非空 `files` 列表 |
| `targets[].local` | 仅 `root`、`version`；不能缺失或以源仓库/其他目标替代 |
| `targets[].files[]` | 仅 `source`、`path`；source 必须在源允许列表内，path 是本 BC 的明确 `.feature` 位置；目标路径唯一（包括大小写） |

`repository` 为可移植的 `owner/repository` 身份，`scope` 为实际 `project/context`；
每段及目标 id 采用字母/数字开头、后续字母/数字/点/下划线/连字符。
`scenario` 的三段同样采用此规则，anchor 为 ASCII 字母开头、后续可含数字/点/下划线/
冒号/连字符。它是调用者给出的场景来源引用，工具不解析 Gherkin 语义或认证业务批准。
传播单位是整个已登记 `.feature` 的原始 bytes，不从场景标签推导部分文件切片或其他目标。

`root` 相对**登记文件父目录**，可用明确 `../` 选择本机已有 sibling checkout；
不接受个人绝对路径、URL/UNC、反斜杠、冒号、空段、环境变量、`~/$/%` 展开或别名。
每个 target 的 local 版本按其**全部映射目标路径**核对；源 base/candidate 版本按 source
允许文件全集核对。源文件在旧/新版本中都不存在是 `SOURCE_FILE_MISSING`，不伪装无变化。
没有默认目标；API `target_ids` 必须是非空、唯一、合法 ID 的 iterable，不能传单字符串。

以下只展示形状，尖括号均须替换为真实输入；这些版本不是示例运行证据：

```yaml
schemaVersion: 1
source:
  repository: example/domain
  base: {root: ../old-source, version: "<实际完整 commit 或 scoped sha256>"}
  candidate: {root: ../new-source, version: "<实际完整 commit 或 scoped sha256>"}
  files:
    - {scenario: example/CTX-domain/TS-001#allow, path: verification/TS-001.feature}
targets:
  - id: bc-a
    repository: example/bc-a
    scope: example/CTX-a
    local: {root: ../bc-a, version: "<该 BC 映射文件的实际版本>"}
    files:
      - {source: verification/TS-001.feature, path: specs/incoming/TS-001.feature}
```

`BatchPlan` 保留登记文件原始摘要、source repository，以及按所选 id 稳定排序的
`TargetProposal`。每个 target 有实际 `repository/scope/mappings`、独立 `status`、
`plan` 或明确 `findings`；未注册目标为 `UNKNOWN_TARGET`，repository/scope 为 null，
绝不创建或猜测。目标缺字段/根/版本、不可读或越界为该目标 `unavailable`，其他结果保留；
公共来源失败使依赖目标 unavailable。局部目标漂移只使该目标不可用，公共来源漂移使所有
依赖提案失效。登记本身非法或漂移为整个输入错误。诊断区分 `source/base` 等来源位置与
`targets/<id>/local`；不因一个目标成功宣布整批传播完成。

<a id="cli"></a>
## CLI、新报告与退出码

cwd 为调用者本次明确的目录；脚本从完整仓库或自包含候选直接调用。仓库根的 Windows 例：

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --base "<旧根>" --local "<本地根>" --candidate "<候选根>"
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --registration "<登记.yaml>" --target "<ID-A>" --target "<ID-B>"
```

三根模式可各加 `--base-version/--local-version/--candidate-version`；显式文件 scope 用
`TreeSource` API 或上面的多目标登记，不从目录名猜版本。两种 CLI 模式互斥，无 `--apply`。
使用其他宿主时替换为已核对的实际项目解释器，不要求 PowerShell 7 或额外包装脚本。

| 顶层 status / 退出 | 实际含义 |
|---|---|
| `no-change` / 0 | 比较完成，无待提议变化；保留所有者修改也可以是 no-change |
| `proposed` / 0 | 比较完成，有干净提案；未应用 |
| `conflict` / 1 | 至少一个冲突，无 unavailable；干净目标/路径仍保留 |
| `input-error` / 2 | 来源/登记/输出错误，或至少一个目标 unavailable；不能降为成功 |

默认 stdout JSON，不写源或输出。显式 `--output <新的本地 .json>` 使用 exclusive create，
不建父目录、不覆盖已有文件/目录/历史，也不能放入任何三根输入或登记的来源/目标根，
包括缓存、缺失或**未被本次选中**的目标根。输出不能穿越目录别名；登记位置不能安全解析
时仅保留 stdout 结果，拒绝写出。保护同时覆盖相等、根下方以及会成为该根**文件祖先**
的位置，例如未选目标为 `proposal.json/checkout` 时，不能创建 `proposal.json` 文件阻断它。
缺失尾部可以保留为声明位置，但不会抹去前面的链接、缺失目录或不明 traversal。
拒绝输出时独立目标的提案/不可用结果仍在 stdout，退出非零；完整逐目标报告即使含
unavailable 也可显式保存到确切的安全新位置且仍退出 2；
整个输入不可解析则不创建报告。写入中断可能留下不完整的**新**文件，不删除/替换 owner 内容。
报告输出的相对路径相对调用 cwd，不相对某个隐含项目根。

主要错误：`INVALID_ROOT/UNSAFE_ROOT/OVERLAPPING_ROOTS`、`UNSAFE_PATH/INVALID_SCOPE/
PATH_TYPE_CONFLICT/PATH_COLLISION`、`FILE_READ_ERROR/DIRECTORY_READ_ERROR/INPUT_CHANGED`、
`INVALID_BASE/BASE_UNAVAILABLE/BASE_MISMATCH`、`REGISTRATION_UNAVAILABLE/INVALID_REGISTRATION/
INVALID_TARGET_REGISTRATION/INVALID_TARGETS/UNKNOWN_TARGET/TARGET_FILE_NOT_ALLOWED/
SOURCE_FILE_MISSING`，以及 `REPORT_CONFLICT/REPORT_WRITE_ERROR`。
命令用法错误由 argparse 返回 2；没有宽泛异常捕获的成功空提案。

<a id="maintainer-workflow"></a>
## 维护者 workflow 与未执行关卡

制作仓的 `propose-template-updates.yml` **仅供维护者**手动生成提案，不分发为业务项目运行依赖。
它使用同一 Python core、只读 contents 权限、明确所选 targets；只 checkout 制作工具自己的
事件 commit，禁用 checkout 的 clean，不 clone/fetch 目标。可信自托管 Linux runner 须在
工具 checkout 之外预先准备实际本地登记及三方树，不把工作输入放进将被 checkout 的工具路径；
登记逐个给出确切版本；没有 token、秘密或联网补源的成功 fallback。
该文件保留工具环境准备及 artifact 保存，但不存在目标分支、PR 或自动应用步骤。

YAML 文件存在/本地可解析，不表示托管执行、自托管权限或服务端 required checks 已验证。
具体外部运行、artifact 上传和原生 Git/平台传播仍在另外授权的关卡执行；未执行时保持
`not-run`。本地工具、方法自用与维护者测试不能冒充外部 fan-out、人工 T17 或新入口原生发现。
