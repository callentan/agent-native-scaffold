# 本地维护工具

本目录提供 `artifact_io.py` 解析模块和 `check_artifacts.py` 正式工件检查器；不是应用、CLI 框架、通用执行器或全局库。schema 字段和完整示例只在[契约说明](../contracts/README.md)维护。当前没有跨文件验收覆盖、模型导出或实施报告收集，不能从解析或文档检查成功推导这些能力已交付。

## 工具环境

运行工具需要 Python 3.11+。环境及命令登记见[开发说明的维护工具一节](../../docs/development.md#maintenance-tools)，与下游业务应用分开；制作仓回归测试和执行历史不是下游使用前提。

- [requirements.txt](requirements.txt) 只列获准的 PyYAML 6.0.2、jsonschema 4.23.0。
- [requirements.lock](requirements.lock) 保存项目 `.venv` 成功解析后的六项实际版本。没有猜测 pins/hashes；pip 是 venv 自带安装工具，不是运行依赖。
- 从仓库根执行 `python -m venv .venv` 后，用 `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.lock` 恢复锁定环境，再运行 `.venv\Scripts\python.exe -m pip check`。
- 不需要激活环境或全局 pip；没有媒体、DOCX/PDF、渲染、云端 SDK 或应用依赖。其他宿主使用其实际 `.venv/bin/python`；使用者须核对本机解释器与已安装依赖。

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

`metadata_locations` 是 `(字段路径 tuple, SourceLocation)` 的 tuple，来自同一次 YAML 解析，例如 `("scope",)` 或 `("targets", 0, "target")`，不是第二套字段解析。共享 `iter_markdown_lines(body, start=1)` 保留行号，移除 HTML 注释，代码行返回 `None`；parser 与检查器共用它处理字面内容。owner 验收仍只由 parser 的显式锚点与所属 ID 标题产生。

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

| 稳定 code | 分类 |
|---|---|
| 上方 parser 全部输入错误（包括 `DUPLICATE_ARTIFACT_ID`） | `input-error`；不吞错或转为空对象 |
| `MISSING_TITLE`, `EMPTY_TITLE`, `MULTIPLE_TITLES` | `invalid`；H1 结构 |
| `INCOMPLETE_ARTIFACT` | `invalid`；明确残留占位 |
| `BROKEN_LINK`, `BROKEN_ANCHOR`, `UNRESOLVED_REFERENCE`, `UNSUPPORTED_FRAGMENT`, `INVALID_LINK` | `invalid`；本地链接或支持范围 |
| `DIRECTORY_READ_ERROR`, `INPUT_CHANGED`, `EXCLUDED_TARGET` | `input-error`；读取或边界；其他路径/解码代码复用 parser |
| `INVALID_BASE`, `BASE_UNAVAILABLE` | `input-error`；基线形状或精确对象读取失败 |
| `REPORT_CONFLICT`, `REPORT_WRITE_ERROR` | `input-error`；输出冲突或写入失败 |

`--report` 只能显式创建本地新 `.json` 文件；相对路径以 root 为准，绝对路径按本次授权使用。父目录必须已经存在，不自动建目录，不覆盖任何已有文件（包括空文件、源文件和历史报告）。使用 exclusive create，失败退出 2；若已创建新文件后写入失败，可能留下不完整的新报告，不能当成功证据。CLI 的 `report_output={path,written}` 独立于保护的输入读集，默认/API 不产生此文件。CLI 参数用法错误由 argparse 输出到 stderr 并退出 2；其他已定义错误在 JSON 中返回。

## 使用范围

下游使用只依赖本目录已提供的模块、同级依赖清单与相邻 contracts；不要求下载制作规格、执行日志或维护者回归测试。那些维护资料不随下游候选分发。正式工件检查不覆盖普通 guide 的全部链接、跨文件 canonical target/层次/验收覆盖，不生成模型或运行 `.feature`、应用和业务 VT，也不认证批准人。
