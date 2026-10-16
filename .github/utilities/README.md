# 本地维护工具

本目录提供解析、正式工件检查、覆盖/影响候选、确定性引用模型、只读实施报告收集、三方/明确多目标更新提案、明确本地来源预检/接入，以及本地文档/转录候选与透明评分；可选 hook 适配与安装入口见下节。它们不是应用、统一 CLI 框架、通用执行器或全局库。schema 字段和完整示例只在[契约说明](../contracts/README.md)维护；这些机械工具不证明业务执行或批准。

## 工具环境

运行工具需要 Python 3.11+。环境及命令登记见[开发说明的维护工具一节](../../docs/development.md#maintenance-tools)，与下游业务应用分开；制作仓回归测试和执行历史不是下游使用前提。

- [requirements.txt](requirements.txt) 只列获准的 PyYAML 6.0.2、jsonschema 4.23.0。
- [requirements.lock](requirements.lock) 保留 Python 3.13 环境实际解析的六项版本，另有 Python `<3.13` 所需、在 3.11 实际安装核对的 `typing-extensions==4.16.0` 条件项；3.11 选择七项，3.13 仍选择原六项。条件来自 `referencing` 的包元数据，不升级原 pins。pip 是环境安装工具，不是工具运行依赖；没有猜测 hashes。
- 从仓库根执行 `python -m venv .venv` 后，用 `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.lock` 恢复锁定环境，再运行 `.venv\Scripts\python.exe -m pip check`。
- 不需要激活环境或全局 pip；没有媒体、DOCX/PDF 额外包、渲染、云端 SDK 或应用依赖。窄 DOCX 适配使用 stdlib ZIP/XML；[可选 media 清单](requirements-media.txt)没有选定包。其他宿主使用其实际 `.venv/bin/python`；使用者须核对本机解释器与已安装依赖。

<a id="source-candidates"></a>
## 本地来源候选与评分

`extract_source.extract_candidates(source, kind)` 只读明确的绝对本地文件，返回实际
字节身份/读取计数及 `candidates` 列表；支持 Markdown/plain text、严格 JSONL 转录与
有界 stdlib DOCX。`score_candidates.score_candidates(items)` 保留重复/相反来源并返回
公开 0–100 因素与理由，不是概率或接受阈值。类型、定位、输入限制、CLI 和错误的
单一说明见[来源候选契约](../../docs/source-extraction.md)，不加入正式工件 schema。

API/default CLI 无写入；显式输出只 exclusive create root 内的新 JSON，不建目录或
覆盖声明输入。`transcribe_audio` 当前只有授权/缺项/不可用拒绝入口，不读音频或环境密钥、
不安装 SDK 或调用服务。候选仍回[共享逆向方法](../skills/reverse-engineer-domain/SKILL.md)
核对和澄清，不能由工具写成 confirmed 事实。

<a id="native-hooks"></a>
## 可选原生 hook 与同源 CI

[hook 说明](../hooks/README.md)定义安装提案、显式应用、逐路径恢复、index 语义和
受管路径 `Reviewed-by` 文本政策。`install_hooks.py` 默认不写，拒绝已有 hook、
配置冲突和共享 worktree metadata；从不修改 Git 配置或自动 commit/push。
安装 I/O 失败时保留并逐项报告本次完整/部分创建，不猜测删除后续 owner 内容。

`hook_checks.py pre-commit --root <checkout-root>` 也可由选定项目 Python 直接调用，
使用实际 index 与原始 blobs，而不是工作文件；可给精确 `--base` 与新 `--report`。
两份 Python hook 入口和下游资料 workflow 复用此模块。适配器仅负责快照/上下文与
格式政策，工件、Markdown、owner AC/VC 和覆盖规则仍归现有三个模块。
入口在读取 index/工件前核对选定解释器、项目 venv/prefix、`pyvenv.cfg`、
Python 最低版本及固定直接依赖的版本/可导入性；配置丢失或回到 base 环境时拒绝，
不是仅把实际 prefix 记入成功报告。原生 launcher 保存选定绝对路径与 prefix，
检查前后还核对环境配置/依赖身份；不会自行恢复或切换解释器。
`read_inventory` 的私有 `_base_root` 只使临时快照从原 Git root 取得历史原始对象；
`_trace_inventory` 复用同一已获取库存，零 owner 时仍反查 targets。公开本地
`run_check`、`trace_report` 的工作树/非空交付选择契约不变。

这组入口须与 `artifact_io.py`、`check_artifacts.py`、`check_traceability.py`、
`artifact.schema.json`、依赖清单一起分发。制作仓的测试 runner/workflow、测试数据、
研究和历史记录不成为下游依赖。native Git 失败与 JSON 的 0/1/2 各自保留；
空库存不算业务通过，本地格式检查不认证 reviewer，YAML 存在不等于 hosted CI 已运行。

## Parser 接口

这是供同目录后续脚本直接导入的模块，不提供假成功的命令行入口。调用者显式提供本次的真实根目录和文件，不靠切换 cwd、自动扫描或业务命令登记。

```python
parse_artifact(path: str | os.PathLike[str], root: str | os.PathLike[str]) -> Artifact

parse_artifacts(
    paths: Iterable[str | os.PathLike[str]],
    root: str | os.PathLike[str],
) -> tuple[Artifact, ...]
```

相对 `path` 相对显式 `root` 解析；根须是实际目录，输入须是解析后的根目录内的可读普通文件。解析 symlink/junction 后越界会失败；不存在、错误类型、乱码或失败读取不是空工件。UTF-8/BOM、LF/CRLF、中文及含空格路径均有实际文件测试。不保证抵御另一个进程在检查和打开之间恶意替换路径；它不是操作系统 sandbox。

`parse_artifacts` 只处理明确给出的集合，保留输入顺序；同 scope/id 重复时报告第二处和第一处位置。不同 scope 的同号 ID 有效。空集合返回空 tuple，但仍校验 root；这不表示业务覆盖完整。单文件解析不会为了去重扫描其他文件。

所有返回记录都是 `frozen=True, slots=True` dataclass，集合为 tuple：

| 类型 | 可用字段 |
|---|---|
| `Artifact` | `schema_version`, `id`, `kind`, `scope`, `content_state`, `upstream`, `targets`, `confirmation`, `path`, `relative_path`, `location`, `id_location`, `body_start_line`, `source`, `body`, `anchors`, `acceptances`, `metadata_locations`；派生属性 `key`、`acceptance_ids` |
| `SourceLocation` | `path: Path`（实际绝对路径）、`line: int`（1-based） |
| `Target` | `target`, `criterion_anchor`, `test_id: str \| None`, `location`, `criterion_location` |
| `Confirmation` | `by`, `reference`, `baseline`, `location`；存在不意味着批准人已核实 |
| `Anchor` | `name`, `location` |
| `Acceptance` | 标题完整 `id`、`owner`（scope/id）、`anchor`、标题 `location`、`anchor_location`；派生属性 `reference`（scope/id#anchor） |

`source` 是去除 UTF-8 BOM 后的原文，`body` 从闭合 frontmatter 分隔行之后开始；两者保留原 LF/CRLF，不重排或写回文件。`body_start_line`、目标和验收位置用于后续检查定位；`relative_path` 使用解析后相对根的 `/` 路径。原始字节需要调用者另行读取，不能拿解码后的 `source` 替代原文件的字节摘要。

`metadata_locations` 是 `(字段路径 tuple, SourceLocation)` 的 tuple，来自同一次 YAML 解析，例如 `("scope",)` 或 `("targets", 0, "target")`，不是第二套字段解析。共享 `iter_markdown_lines(body, start=1)` 保留行号，移除 HTML 注释，代码行返回 `None`；parser 与检查器共用它处理字面内容。`iter_markdown_fences(body, start=1)` 从**同一个**状态机返回真正闭合的 `MarkdownFence(start_line, end_line, info, body)`，注释或外层代码中的围栏示例不变成新代码块。owner 验收仍只由原 parser 的显式锚点与所属 ID 标题产生。

## 输入错误

`ArtifactInputError(ValueError)` 的稳定属性是 `code`、`path`、`line`、`message`。字符串包含这四项；YAML、解码、文件读取和 schema 失败保留原始异常链。路径尚不能建立时，`path` 保存输入的可读表示；文件读取前的错误行用 1，空元数据用 2。

| code | 判定 |
|---|---|
| `INVALID_ROOT` | 根类型错误、空值、不存在、不可读或不是目录；两个 API 的 `path` 均为无效 root 的字符串表示，行号为 1；空选择也不能绕过 |
| `INVALID_PATH` | 输入类型/路径无效、歧义的 drive-relative 路径、目录或其他非普通文件；集合接口误传单个路径 |
| `OUTSIDE_ROOT` | 规范化路径、symlink 或 junction 目标越过显式根 |
| `FILE_NOT_FOUND` | 根内文件不存在 |
| `FILE_READ_ERROR` | stat/read 失败；保留具体 OS 错误，不默认空正文 |
| `INVALID_ENCODING` | UTF-8 解码失败；按解码器原输入计算行号，包含 BOM 的失败也不偏移 |
| `MISSING_FRONTMATTER` / `UNTERMINATED_FRONTMATTER` | 文件开头缺 `---` 或缺闭合 `---` |
| `INVALID_YAML` | YAML 语法、非字符串 mapping key、不安全/未知 tag、循环别名或超出 parser 嵌套限制 |
| `DUPLICATE_YAML_KEY` | 任意深度的重复 key，包括重复 `<<` 和 merge 后的覆盖；先检查原始 node 图，不能让归一化吞掉重键 |
| `INVALID_METADATA` | 非 mapping、缺字段、scope/id/关系/确认形状错误、未知字段或重复关系记录 |
| `UNSUPPORTED_SCHEMA_VERSION` | 不是真正的整数 1；不回退解析 |
| `INVALID_KIND` / `INVALID_CONTENT_STATE` | 不在固定契约枚举中 |
| `MISSING_ACCEPTANCE_ANCHOR` / `DUPLICATE_ANCHOR` | owner 验收标题缺匹配显式锚点，或正文锚点不唯一 |
| `MISSING_CRITERION_ANCHOR` | 目标的判据锚点不在当前正文 |
| `DUPLICATE_ARTIFACT_ID` | 显式集合内出现同 scope/id；不合并、不丢弃 |
| `CONTRACT_ERROR` | 本地 artifact schema 不能读取/解析/校验，或含非本地、无法定位的 `$ref` |

使用 SafeLoader，不构造 Python 对象、不执行 YAML/Markdown/引用命令。合法、非循环且不引入重键的 YAML 别名可以解析；有值的 malformed `upstream` / `targets` 先报错，不被空 tuple 替代。schema 缓存限于当前进程；修改本地契约后须用新进程重新加载，不能沿用旧缓存。

<a id="artifact-checker"></a>
## 正式工件检查器

```python
run_check(root: str | os.PathLike[str], base_sha: str | None = None) -> CheckReport
```

从同目录 `check_artifacts` 导入。API 不写文件、不改变 cwd、不执行来源里的命令；`root` 必须是明确的本地目录。CLI 默认只向 stdout 打印 UTF-8 JSON：

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_artifacts.py --root .
```

本例 cwd 是仓库根，`.` 指当前选择的资料根；其他宿主替换为其实际项目解释器。可另传 `--base <完整 commit>`，或 `--report <明确的新 JSON 文件路径>`。尖括号参数必须替换为本次真实值。无需 shell 包装、hooks 或 CI；`-B` 避免运行时生成 Python 字节码。

| status | 退出码 | 含义 |
|---|---|---|
| `clean` | 0 | 至少一个正式工件完成检查，没有本工具范围内的发现 |
| `empty` | 0 | 没有发现正式输入，`checked_count=0`；不是需求、业务或应用通过 |
| `invalid` | 1 | 有标题、占位或本地 Markdown 链接违反项 |
| `input-error` | 2 | 输入、parser、路径、基线或报告输出失败；优先于 `invalid`，其他已取得的发现保留 |

<a id="checker-discovery"></a>
### 发现范围与排除

按相对路径稳定排序，递归检查 `.md`（扩展名不分大小写）。下列任一信号将文件纳入正式输入：

- 文件名以大写连字符 ID 开头，例如 `REQ-001.md`、`SR-SYN-001-title.md`、`REQ-NNN.md`；对应模式为 `^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+`，后接分隔符或文件名末尾。
- 起始 frontmatter 出现 `schemaVersion/id/kind/scope/contentState/upstream/targets/confirmation` 字段信号，或开头缺少分隔符但仍有这种元数据前缀。首行可辨认但不合法的 `---`（例如多一个前导空格）也保留紧随其后的元数据候选；遇到普通正文或代码后不再搜索元数据前缀。这里只做选择，分隔符是否合法及实际字段、类型、重复键、版本和确认形状全部交给现有 parser。
- 非代码/注释内的 H1 以同样的正式 ID 开头。精确 base 模式还保留历史上已识别为正式的当前路径，不能靠删掉全部元数据藏起修改。

字段被删坏、没有 frontmatter 的正式文件仍会报输入错误，不会自动迁移或改写。没有任何身份/元数据信号的普通 README、说明或旧轻量正文只作 guide；检查器不能凭空恢复已彻底删除的身份。任意命名的文件只要保留正式元数据（包括 README）仍会检查。

`excluded` 中每条是 `{path, reason}`；目录用尾部 `/` 表示整个子树，均相对**本次 root**，不匹配 root 的祖先。因此位于工具 `.venv` 下的独立测试根仍可扫描。

| reason | 精确排除规则 |
|---|---|
| `TEMPLATE` | 根下 `_templates/`、`.github/pull_request_template.md` |
| `NATIVE_METADATA` | 根下 `.github/skills/`、`instructions/`、`agents/`、`prompts/`、`workflows/` 及 `.github/copilot-instructions.md` |
| `MAKER_DATA` | 根下 `docs/design/`、`docs/plan/`、`docs/research/` |
| `TEST_FIXTURE` | 相对路径中的 `tests`、`test`、`fixtures` 目录段 |
| `TOOL_DATA` | 相对路径中的 `.git`、`.venv`、`venv`、`node_modules`、`__pycache__`、`.pytest_cache`、`.mypy_cache`、`.tox`、`.nox` 段 |
| `DIRECTORY_ALIAS` | 指向根内的目录 symlink/junction 别名；实际目录只扫描一次，避免重复和循环 |
| `NON_MARKDOWN` / `LIGHTWEIGHT_GUIDE` | 非 Markdown 文件 / 已读取但没有正式信号的 Markdown |

越界目录链接是错误而不是排除；正式输入不接受符号链接文件。被明确引用的根内模板或 guide 可以作为链接目标读取，不因此变成正式库存；Git、环境和依赖数据不能作为链接读取许可。目录不可枚举、文件不可读、乱码不默认为空。UNC/URL 根及 UNC 本地引用在文件解析前拒绝；不访问网络地址。路径解析不是 OS sandbox，也不保证抵御并发恶意替换。

<a id="checker-format"></a>
### 检查的 Markdown 与占位语法

- 正式正文需要一个非空 ATX H1（`# Title`），不能有第二个 H1。沿用 parser 的元数据、唯一 scope/id、显式 anchor 和 owner AC/VC 结构检查；不同 scope 同 ID 合法。
- 支持单行内联链接/图片、尖括号目的地址、可选单引号/双引号标题、引用定义与 full/collapsed reference links；已定义的 shortcut reference 也会解析。空格路径用 `%20` 或 `<path with spaces.md>`，目的地址可含一层括号。
- 本地文件必须存在且在 root 内。fragment 匹配 parser 风格的独立 `<a id="ascii-anchor"></a>` 或 ATX 标题 slug：转小写、保留 Unicode 字母/数字及空格、`_`、`-`，空格转 `-`，重复标题加 `-1` 等后缀。标题 slug 只用于导航，不替代 owner 验收的显式锚点。非 Markdown fragment 返回 `UNSUPPORTED_FRAGMENT`。
- 忽略反引号/波浪号 fenced code、四空格/tab 开头的代码行、单行 inline code 和 HTML 注释。外部 URI 不抓取；未定义的显式 `[label][reference]` 报错。Setext、跨行链接、复杂嵌套、原始 HTML `href` 和渲染器特有锚点不在本检查语法内；这不是完整 CommonMark/GFM renderer。
- 围栏前的实际正文注释仍按注释处理；围栏信息字符串及内容不改变正文的注释状态。反引号围栏的信息字符串不得包含反引号，不能先移除其中的注释样文本再判合法。关闭围栏后继续读取真实链接和 owner 验收，保留原始行号。
- 显式残留标记为 `待填写`、独立 token `TODO/TBD/PROJECT`、独立 `NNN`（含小写锚点）、`<slug/project/context/id>`、`{{字段}}`。从 parser 已读出的身份/关系/确认字段检查元数据占位，不把 YAML 注释当值；正文代码与注释里的示例不算占位。普通 `project` 一词不算占位。
- `未决/待确认/not-run` 等有具体上下文的事实可以保留；检查器不补写业务决定。没有这些机械违反项也不代表语义完整、审批可信或行为执行成功。

<a id="checker-baseline"></a>
### 精确基线与当前文件比较

无 base 时只读当前 root，不需要 Git。有 base 时 root 必须正好是所选 checkout 的顶层（支持 linked worktree），拒绝借用祖先仓库。base 只接受实际可读的完整 40/64 位十六进制 **commit 对象**；分支、短号、tag/blob 对象和不存在的对象都不回退。

**两种模式的验证目标始终是当前工作文件的完整正式库存。** base 只是附加历史比较，不省略未改工件，不是暂存区 hook 检查；未暂存和未跟踪的正式文件同样纳入。历史 Markdown 只按原始 Git blob 读取与识别，不要求旧元数据满足新规则。

Git 读取使用参数列表、显式 cwd、`shell=False` 和原始 `ls-tree/cat-file`，不调用 diff/textconv、clean/smudge filters、hooks 或来源命令；清除继承的仓库/index/Git 配置环境，不用替换 refs 或 lazy fetch，不寻找 main/master 或新的 HEAD。失败保留诊断并返回输入错误。

共享 reader 在 Git 命令前另检查本地 Gitfile/common/worktree metadata，拒绝
`include` / `includeIf` 声明、网络指针、配置别名和不完整布局；不靠 transport 禁止
推导 include 安全，也不调用 Git 探测被包含位置。[明确读取边界](../../docs/domain-sources.md#git-config-boundary)
说明兼容限制；普通无 Git 的本地内容输入不要求建立仓库。

<a id="checker-output"></a>
### JSON 字段、计数与稳定代码

报告及内部记录为窄用途不可变 dataclass；`report.to_dict()` 可直接 JSON 序列化，tuple 编码为数组，缺值为 `null`：

| 字段 | 实际表示 |
|---|---|
| `status`, `findings`, `checked_count`, `baseline`, `excluded`, `attempted_count` | 顶层字段；`checked_count` 为已成功解析并做正文检查的正式文件数，含发现违反项的文件；`attempted_count` 另计解析失败/不可读的已识别正式候选。目录读取失败可能尚无法列出候选，状态仍是错误 |
| `findings[]` | `{code, path, line, owner, target, message, related}`；`path` 为实际绝对路径或无效输入的字符串，`line` 为 1-based；已解析 owner 为 `scope/id`，否则 `null`。链接发现定位引用方行号和原始 target；重复 ID 的 `related={path,line}` 保存第一处，主位置是第二处 |
| `baseline` | 根/base 在读取前失败时为 `null`；否则含 `root`, `target="working-tree"`, `base_sha`, `base_tree`, `comparison_complete`, `snapshot_sha256`, `files`, `base_files`, `changes` |
| `baseline.files[]` | `{path, sha256, size, role, owner}`；root 相对路径、实际读取的原始字节 SHA-256/大小（保留 BOM/换行差异），`role=formal/guide/reference`。包含已读取的选择用 guide/本地引用，不是整个仓库或工具源码/schema 的摘要 |
| `baseline.base_files[]` | `{path, blob, sha256, size, formal}`；历史合资格 Markdown 的 Git blob ID、原始字节摘要和选择信号；不解析历史 schema |
| `baseline.changes[]` | 正式路径并集的 `{path, status, base_blob, before_sha256, after_sha256}`；`status=added/modified/deleted`，没有对应侧时为 `null`；不是整个仓库 diff |
| `baseline.comparison_complete` | 无 base 为 `null`；base 比较遇到读取/路径问题为 `false`，只列已知比较且不把缺少读数冒充删除；正常读取为 `true`。这不等于元数据/文档有效 |
| `baseline.snapshot_sha256` | 按 path 排序的 `files` 数组，经 `json.dumps(sort_keys=True, separators=(",", ":"))` 编码后计算 SHA-256；标识本次实际读集，不把脏工作树标成只有 HEAD |

两个读点不一致报 `INPUT_CHANGED`。读集并非文件系统事务；记录调用所用工具版本，后续文件或工具改变后重新检查，不把摘要当批准证明。

供同目录工具复用的 `read_inventory(root, base_sha=None) -> Inventory` 与 `run_check` 使用同一次完整发现/解析/检查。`Inventory` 的 `report` 就是上述 `CheckReport`，另保留不可变 tuple：`artifacts`、`raw_files`（实际路径与已读 bytes）和 `base_raw_files`（历史相对路径与原始 blob bytes）。消费者不重新读取 Markdown 猜测同一个快照。历史解析使用原 parser 的字节入口；独立 YAML/JSON 来源使用 `load_yaml_mapping(text, path)`，仍是同一 SafeLoader、重键/别名检查和 1-based 定位，不另有 frontmatter 或 owner parser。

| 稳定 code | 分类 |
|---|---|
| 上方 parser 全部输入错误（包括 `DUPLICATE_ARTIFACT_ID`） | `input-error`；不吞错或转为空对象 |
| `MISSING_TITLE`, `EMPTY_TITLE`, `MULTIPLE_TITLES` | `invalid`；H1 结构 |
| `INCOMPLETE_ARTIFACT` | `invalid`；明确残留占位 |
| `BROKEN_LINK`, `BROKEN_ANCHOR`, `UNRESOLVED_REFERENCE`, `UNSUPPORTED_FRAGMENT`, `INVALID_LINK` | `invalid`；本地链接或支持范围 |
| `DIRECTORY_READ_ERROR`, `INPUT_CHANGED`, `EXCLUDED_TARGET` | `input-error`；读取或边界；其他路径/解码代码复用 parser |
| `INVALID_BASE`, `BASE_UNAVAILABLE` | `input-error`；基线形状或精确对象读取失败 |
| `GIT_CONFIG_INCLUDES_UNSUPPORTED`, `GIT_CONFIG_UNSAFE` | `input-error`；命令前拒绝不支持的本地 include 或不安全 Git metadata，不访问其外部位置 |
| `REPORT_CONFLICT`, `REPORT_WRITE_ERROR` | `input-error`；输出冲突或写入失败 |

`--report` 只能显式创建本地新 `.json` 文件；相对路径以 root 为准，绝对路径按本次授权使用。父目录必须已经存在，不自动建目录，不覆盖任何已有文件（包括空文件、源文件和历史报告）。使用 exclusive create，失败退出 2；若已创建新文件后写入失败，可能留下不完整的新报告，不能当成功证据。CLI 的 `report_output={path,written}` 独立于保护的输入读集，默认/API 不产生此文件。CLI 参数用法错误由 argparse 输出到 stderr 并退出 2；其他已定义错误在 JSON 中返回。

<a id="traceability"></a>
## 完整交付覆盖

```python
trace_report(root, delivery_ids) -> CheckReport
```

从同目录 `check_traceability` 导入。`delivery_ids` 是调用者给定的**完整交付验收集合**，每项必须是实际 owner 的 `scope/id#anchor`，不是文件标题、短 ID 或由 VT 倒推的列表。空集合、单字符串、非法、重复或未知项均为输入错误。先读取完整正式库存，再从所有者提取 AC/VC；其他工件可作为引用上下文，但不会自动变成“本次交付”。

反查每个实际 `targets`，包括不在交付集合里的目标。只有真实 owner 验收、兼容层次及独立判据均满足机械要求的 VT/TS 才计入覆盖。层次来自 VT 的 `plan` 节 `验证层次` 表格行，或 TS 的 `basis` 节 `业务范围与场景类型`，不从文件名推断，不扩展 frontmatter。VT 接受表单的四个明确层次；TS 接受上下文内、跨上下文、REQ 业务验收或 QAS 的明确业务声明。缺失、多值、未知声明必须报告。

| owner kind | 目标层次 |
|---|---|
| stakeholder-requirement、use-case、invariant、quality-attribute-scenario、domain-model | business |
| software-requirement | software |
| architecture-building-block、architecture-decision、architecture-specification、sequence-diagram、published-interface | design |
| development-log、backlog-item、user-story、tool-qualification、review-record | maintenance |
| 其他 kind | 不猜层次，报告 `UNKNOWN_TARGET_LAYER` |

判据按现有表单读取：VT 每个 `criterionAnchor` 下需要“本目标预期与独立判定标准”“对应方法/步骤或实际测试标识”“前提、禁止副作用及未决事项”三行实际表格值；TS 使用四条同名表单项目。仅锚点/标题、代码/注释、占位或泛化“全部通过”不满足要求。不同目标共用锚点或完全相同的判据内容会报告 `SHARED_CRITERION`。这是可解释的结构下限，不是自然语言语义证明；实际预期是否足以判断原验收仍需人工审阅。

返回字段、正式文件 `checked_count/attempted_count` 和读集 `baseline` 复用上文契约；不是覆盖率分母，也不是测试运行数量。parser/库存输入错误优先，不把解析失败制造为“未覆盖”或成功。新增代码：

| code | 状态 |
|---|---|
| `INVALID_DELIVERY`, `EMPTY_DELIVERY`, `INVALID_DELIVERY_ID`, `DUPLICATE_DELIVERY_ID`, `UNKNOWN_DELIVERY_ID` | `input-error` / 2 |
| `DANGLING_TARGET`, `TARGET_NOT_ACCEPTANCE`, `INVALID_TARGET_SOURCE` | `invalid` / 1；保留实际引用方位置/target |
| `UNKNOWN_VALIDATION_LAYER`, `UNKNOWN_TARGET_LAYER`, `LAYER_MISMATCH` | `invalid` / 1 |
| `INSUFFICIENT_CRITERION`, `SHARED_CRITERION` | `invalid` / 1；定位判据声明 |
| `UNCOVERED_ACCEPTANCE` | `invalid` / 1；定位实际验收 owner、路径、标题行与完整 target |

命令为 `.venv\Scripts\python.exe -B -X utf8 .github\utilities\check_traceability.py --root <资料根> --delivery <完整验收引用>`；每个交付 ID 重复一个 `--delivery`。stdout 是 `CheckReport` JSON，CLI 另保留实际 `delivery_ids`；可加 `--report <新 .json>`，沿用保护输出契约。无参数、错误用法退出 2；完整结构无发现退出 0，不表示 VT 被执行。

<a id="impact-candidates"></a>
## 精确基线的影响候选

```python
impact_report(root, base_sha, task_ids=()) -> dict
```

同属 `check_traceability`，采用明确完整 commit 和当前工作文件，不选 HEAD/分支、不只看暂存内容。公开 API 的 base 是必需项，显式传 `None` 也返回 `INVALID_BASE` / input-error / 2，不沿共享库存的可选 base 语义退化为 clean 空比较。返回 `CheckReport.to_dict()` 的字段及：

- `changed_sources`：正式变更路径、added/modified/deleted、旧 blob/前后 SHA256；`before/after` 保存可解析的 `{key, path, sha256}`，没有对应侧为 null。
- `candidates`：按 key 排序的传递依赖候选，保留同形状的 `before/after`、`requested_task` 和 `reasons`。每条 reason 有实际 `source/consumer/reference/relation/path/line/snapshot`；`relation` 为 upstream 或 target，`snapshot` 为 base/current。
- `task_ids`：调用者明确指定的已有正式任务 key（不是验收集合）；空列表可用，非法、重复、未知项分别报告 `INVALID_TASK* / DUPLICATE_TASK_ID / UNKNOWN_TASK_ID`。没有提供的任务不会被发明。

已变更 owner 是 `changed_sources` 中的种子，其余可达 owner 是候选；依赖图合并旧新两侧，删除源或移除引用不抹去历史链，循环只访问一次。只有规则文件的数值变化也可经 canonical 引用触及 REQ/SR、VT 和任务。历史正式文件无法解析报告 `HISTORICAL_INPUT_ERROR` / 2，并保留已知候选，不伪装为完整比较。此接口比 `run_check` 的原始历史字节比较多做历史身份解析。

CLI 使用 `--base <完整 commit>` 代替 `--delivery`，可重复 `--task <scope/id>`；两种模式互斥。报告仍可显式写到新 `.json`。候选不是严重度、批准或业务影响的最终结论；非 canonical 的轻量链接、语义隐含依赖及 scope 外未知来源仍须按[共享影响方法](../skills/verify-change/SKILL.md#impact)补充。工具不改规则、不执行 VT、不重写旧结果。

<a id="model-export"></a>
## 九视图引用模型与漂移检查

```python
export_view(root, scope) -> dict
check_model(root, scope, model_path) -> CheckReport
```

从同目录 `export_model` 导入。两 API 均不写文件。主输入复用完整库存和实际读集；选定 scope 必须在真实正式工件中存在，同号异 scope 不混合。所有正式来源必须有效，canonical upstream/targets 必须能定位真实 owner/anchor。非法 root/scope/契约/正式库存不能用九个空视图掩盖。导出 API 抛带 code/path/line 的 `ArtifactInputError`；check API 与 CLI 映射为输入错误 / 2。

采用[可选 model-sources 契约](../contracts/README.md#model-sources)选择各 scope 的已有 Markdown 或 YAML/JSON 汇总。缺清单/缺 scope 登记/缺 view 各有具体 gap；主索引仍可用。供应了非法清单是 `INVALID_SOURCE_MANIFEST` / 2。单个可选源缺失、不可读、格式或基线问题为该 view 的 `unverified`，refs 清空；可读但字段/条目不完整为 `partial`；完整为 `available`。原九个键永不省略，值/正文/结果仍归源，不从状态推出批准。可选失败 gap 带选择路径、实际失败来源与 code；不输出个人绝对路径或原始敏感异常内容。

直接 quality 同时核对实际 QAS 和 utility-tree 来源（可显式选已有顶层 `tree` mapping/list 文件）；缺源为 unverified，已知源缺字段/条目才 partial。直接 verification 读取当前 VT 表单的所属子运行块和四列结果表，逐运行记录缺项/冲突并保留原锚点；不从总数推算自动/人工数量，不把相邻运行或 criterion 内容拼合。SEQ 完整性读取受共享注释/围栏状态约束的真实图代码，不回扫原始字面示例。具体源形状仍以契约说明为准。

主 `source.root` 固定为可移植的 `.`。各 artifact baseline 是实际读到的原始 bytes 的 `sha256:`（含 BOM/换行），upstream/targets、工件、视图、refs 与 gaps 确定排序。主 `source.baseline` 是以下对象经 `json.dumps(sort_keys=True, separators=(",", ":"))`、UTF-8 编码后的 `sha256:`：`scope`、按 path 排序的 Task6 `files` 读集记录、`manifest: absent/present`、排序的可选失败 `(选择路径, code)`、artifact/model/model-sources 所用契约的原始摘要；采用实施报告 adapter 时还包括 bc-config/implementation-report 契约。读集包括选择用 guide、清单、实际可选 YAML/JSON 与证据文件，不只包含正式 Markdown。无时间戳/随机数据；工具版本另随检查记录保存。

canonical 引用还保留其实际 owner 文件的 evidence baseline，跨 scope 消费者也能回源。代码/表头/普通 AC 提及不会自动成为 source 字段或 owner 验收。两次读取不一致返回 `INPUT_CHANGED` / 2；这不是文件系统事务，仍不保证抵御检查/打开之间的恶意替换。

`check_model` 读取显式本地 `.json/.yaml/.yml`（可为 root 外另行授权的模型文件），校验并重算；主来源身份变化为 `STALE_MODEL_SOURCE` / 1，同源但手改结构为 `MODEL_MISMATCH` / 1。非法持久模型/schemaVersion/scope 为输入错误 / 2。它不修复旧模型，派生 model 也不能作为源或来源证据；清单自引用被拒绝。

实施报告须在既有清单的 `verification` 来源中另行显式选择。专用 adapter 核对 v1 schema、scope、报告 baseline，并从其精确对象/owned VT 引用只读重建；手改且无法重建为 `REPORT_MISMATCH`，原始报告缺失/漂移也只保留该可选视图的 gap，不接受一个 schema-valid pass 声明。model 的 `implementationReports` 与 verification 视图只保存报告的 `reference + baseline`，不复制 entries/执行/适用性。其他八视图及原有来源不被报告替换；没有选择报告时仍为空列表。`available` 仅表示引用可核对，不能推出执行通过。

| CLI 参数（均需 `--root` 与 `--scope`） | 输出与退出 |
|---|---|
| 无输出参数 | 校验/派生到 JSON stdout，不创建文件；主输入可派生退出 0，即使有可选 gap |
| `--check <已有模型>` | JSON CheckReport；无漂移 0、发现漂移 1、输入错误 2 |
| `--output <新模型>` | 显式 exclusive create 本地 `.json/.yaml/.yml`，stdout 仍是 schema-valid model；父目录须存在 |

`--check` 与 `--output` 互斥。输出路径复用 Task6 的本地/冲突约束：任何已存在源、模型、报告、空文件或目录均不覆盖；清单或所选 YAML/JSON 来源中已声明的嵌套 source/evidence 位置，即使缺失也不能被模型占用。工具先登记整个已解析文档中的 `reference`、`path + baseline` 位置，再逐项解引用；前一项失败不会跳过后续声明的保护。登记不授予读取权限，不把未读取的数据判为可用。

声明位置本身非法、不能安全登记时，默认只读派生仍可报告可选 gap，但显式创建输出返回 `REPORT_CONFLICT`，不假称已建立输入/输出隔离。正常的新输出路径可导出后原样检查，不自动成为自身源。`REPORT_CONFLICT / REPORT_WRITE_ERROR` 退出 2；主输入失败不创建输出，写入中失败可能留下不完整的新文件。无网络、fetch、filters/textconv、hook 或来源命令执行，不自动修订清单基线。

实施报告中明确的领域 `root/path` 同样先登记再核验，保护该位置和子路径，不要求 baseline 已存在或有效。`domainSources` 的位置声明不完整或不能安全解析时，默认读取仍可报告 optional gap，但显式输出必须返回 `REPORT_CONFLICT`；可解析位置则仍保护全部子路径。登记不代表这些数据可读、有效或获准写入。

<a id="implementation-report"></a>
## 从现有 VT 收集实施摘要

```python
build_report(root, object_sha, evidence_files, *, scope=None) -> dict
```

从同目录 `collect_implementation_report` 导入。API 只读，返回既有 [implementation-report v1](../contracts/README.md#implementation-report)，没有根级 execution/views。完整字段及支持的 **VT 选择、原表单字段/基线、注释 marker、适用性语法**均在该契约说明；不另建输入 manifest 或复制结果账本。[空白报告表单](../../_templates/reports/implementation-report.yaml)只是输出结构导航，不是实际结果。

- 主 BC 配置、全部 owner 验收和代码/测试位置来自给定完整本地 commit；不是 HEAD、index 或当前文件快照。多个配置上下文时须明确 scope，无实际 scope/验收时失败。
- 当前供应的 VT 可在对象之后追加记录；只接受原 owner/同路径的 owned child run，单文件多运行必须带锚点。原记录 bytes、测试对象、要求基线、VT 计划与原始报告各自核对，不将新证据标为旧对象中的 bytes。
- 每项目标独立处理。未选中运行为 not-run、空 evidenceRefs 和原因；fail/skipped 及原因保留。原始报告的存在、测试文本定位、Approved、数量零、全跳过和视图 available 都不能替代执行。
- 源运行、报告、日期、观察和命令是**被收集的数据**，不是收集器自己的运行结果。收集器不执行源命令、不运行应用/测试，也不能认证人或证明外部事件发生。人工记录用具体步骤，不编造 auto/manual 数量。
- 领域输入按配置的 root/path 和固定基线读取并比对，始终不写回。报告的对象根为 `.`；无个人绝对路径、原始敏感正文或业务摘要复制。

| CLI 参数 | 行为与退出 |
|---|---|
| `--root <checkout> --object <完整 commit>` | stdout 为逐目标报告，不写文件；可重复 `--evidence <VT相对路径[#运行锚点]>`，多个 BC 增加 `--scope <project/context>` |
| 增加 `--output <明确的新 .json/.yaml/.yml>` | exclusive create，父目录须存在；不创建报告目录、不改来源选择。已有或登记/引用的源路径即使缺失也不能成为输出 |
| 成功收集且无 fail | 退出 0，可全部 not-run/skipped；仅说明收集动作完成，不表示目标通过 |
| 收集到某目标 fail | 仍输出完整逐目标报告，退出 1；不改成成功 |
| 输入/来源/输出错误 | JSON `status: input-error` 与带 code/path/line/message 的 findings，退出 2；不输出伪造的空成功 |

主要诊断包括 `INVALID_BASE / BASE_UNAVAILABLE / OBJECT_PATH_MISSING / BASE_MISMATCH / PLAN_MISMATCH / OBJECT_MISMATCH`（对象/来源）、`AMBIGUOUS_SCOPE / INVALID_SCOPE / UNKNOWN_SCOPE / EMPTY_ACCEPTANCE`（范围）、`INVALID_EVIDENCE_OWNER / SCOPE_MISMATCH / REQUIREMENT_MISMATCH`（所有者）、`DUPLICATE_EVIDENCE / AMBIGUOUS_RUN / UNKNOWN_RUN / AMBIGUOUS_RESULT / INVALID_RUN`（选择/记录）、`INVALID_EXECUTION / INVALID_OBSERVATION / INVALID_EVIDENCE / MISSING_TEST_REFERENCE / INVALID_MARKER`（实际定位/证据）、`INVALID_APPLICABILITY / AMBIGUOUS_APPLICABILITY`（独立复核）。共用文件/schema 诊断仍保留；`REPORT_CONFLICT / REPORT_WRITE_ERROR` 不会静默覆盖旧报告。

报告可重建但不是来源事务：读取期间发现同一路径字节变化会失败；不宣称防御所有并发恶意替换。报告写入中断可能留下不完整的新文件，下一次仍拒绝覆盖。领域源 `readOnly: false` 也不授权写入；不执行 hooks、filter、replace-ref、fetch 或配置中的任何命令。

<a id="template-update"></a>
## 只读模板与明确 BC 场景提案

`plan_template_update.plan_update(base, local, candidate) -> UpdatePlan` 比较真实三根，
返回 `changes/conflicts/preserved/sources`，不写源或输出。可用窄 `TreeSource(root, version, files)`
给出确切本地 Git/content 身份及一致的文件 scope；缺旧基线、读取失败或版本错误直接失败。
`plan_batch(registration, target_ids) -> BatchPlan` 仅为显式登记/选定的 BC 映射 `.feature`，
保留来源场景、仓库/上下文/版本、允许文件及每个目标的独立结果，不传播 model 或整个仓库。

[完整输入、摘要配方、16 类判定、登记、状态和输出契约](../../docs/template-updates.md)
只在更新说明维护；[共享方法](../skills/update-template/SKILL.md)处理判断与停点。
CLI 默认 stdout，三根模式为 `--base <旧根> --local <本地根> --candidate <候选根>`；
批量模式为 `--registration <本地登记> --target <明确ID>`（每个目标重复）。
`no-change/proposed` 退出 0，`conflict` 退出 1，任一 `unavailable` 或输入/输出错误退出 2。
干净提案可以有增/改/删；不是应用成功。显式 `--output <新的 .json>` 必须在所有输入/
登记位置之外，不建父目录、不覆盖历史，不能占用缺失或未选的目标根。

输入解析/安全 YAML 和受限原始 Git helper 复用 `artifact_io.py`、`check_artifacts.py`；
与它们及既有锁定依赖一起使用即可，不依赖维护者 tests、制作资料、workflow 或新依赖。
没有 `--apply`、clone/fetch、commit/push、PR、外部源写回或后台同步。
所有者业务数据、原规则及主动删除保留；原始字节与来源漂移按完整契约核对。

<a id="domain-sources"></a>
## 可选本地领域源预检与明确接入

`setup_domain_source.inspect_domain_source(root, source_config) -> dict` 默认只读，
按原 BC 的六个来源字段核对真实 root/path/固定基线，返回 `ready / conflict / unavailable`
与 0/1/2、准确路径/所有权声明/目标/拟操作。源、index、config、refs 和对象不写，
不选择 HEAD 或远端 fallback。网络地址在调用 Git/凭据工具前拒绝，不回显原 URL。

`apply_domain_source` 只有明确给出操作、既有配置、准确 preflight 和目标所有权声明才写；
register 只追加 BC 的来源条目，不 materialize 或暂存。可选本地 submodule 不编辑
BC 配置，必须另给准确 target 与独立 index 同意；原始 blob 写入绕过 checkout/filters/hooks，
原生 metadata 和 gitlink 变更逐项披露，不含 commit/push。非空目标/别名/冲突/漂移不跳过成功。

BC token 只标识实际用于解析/规划的原始配置 bytes，inspect 内的后续读取变化也拒绝。
新 native 目标不会复活 HEAD 中已由 owner 暂存删除的 `.gitmodules`，目标本身也不能
占用 metadata 文件。共享 Git reader 与 native helper 都在命令前拒绝不支持的 includes，
包括准确源仓、父仓、common/worktree config 和显式配置文件，不运行 include 检测命令。

完整 API/CLI、可编辑配置布局、原生命令和保留部分状态的恢复边界见
[领域源说明](../../docs/domain-sources.md)，字段仍归[原契约](../contracts/README.md#bc-configuration)。
复用 `artifact_io.py` 的唯一安全 YAML/schema reader、`check_artifacts.py` 的路径/Git 边界，
以及 `source_baseline.py` 的固定 commit/原始领域 bytes 比较；收集器共用后者，
不维护第二份基线 parser 或来源模型。核心依赖不变，无额外安装。

## 使用范围

下游使用只依赖本目录已提供的模块（含共用 `vt_records.py`、`source_baseline.py`）、同级依赖清单与相邻 contracts；不要求下载制作规格、执行日志或维护者回归测试。正式工件检查、覆盖、影响候选、模型、实施摘要、更新提案和来源接入各有上述边界，不互相替代；普通 guide 的全部链接和语义仍需审阅。所有工具都不运行 `.feature`、应用或业务 VT，也不认证批准人。
