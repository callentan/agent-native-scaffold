# 本地维护工具

本目录提供 `artifact_io.py` 本地解析模块；不是应用、CLI 框架、通用执行器或安装到全局的库。schema 字段和完整示例只在[契约说明](../contracts/README.md)维护。当前不提供完整工件检查器、追溯、模型导出或实施报告收集，不能从解析成功推导这些能力已交付。

## 工具环境

运行工具需要 Python 3.11+。环境及命令登记见[开发说明的维护工具一节](../../docs/development.md#maintenance-tools)，与下游业务应用分开；制作仓回归测试和执行历史不是下游使用前提。

- [requirements.txt](requirements.txt) 只列获准的 PyYAML 6.0.2、jsonschema 4.23.0。
- [requirements.lock](requirements.lock) 保存项目 `.venv` 成功解析后的六项实际版本。没有猜测 pins/hashes；pip 是 venv 自带安装工具，不是运行依赖。
- 从仓库根执行 `python -m venv .venv` 后，用 `.venv\Scripts\python.exe -m pip install -r .github\utilities\requirements.lock` 恢复锁定环境，再运行 `.venv\Scripts\python.exe -m pip check`。
- 不需要激活环境或全局 pip；没有媒体、DOCX/PDF、渲染、云端 SDK 或应用依赖。其他宿主使用其实际 `.venv/bin/python`；使用者须核对本机解释器与已安装依赖。

## Python 接口

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
| `Artifact` | `schema_version`, `id`, `kind`, `scope`, `content_state`, `upstream`, `targets`, `confirmation`, `path`, `relative_path`, `location`, `id_location`, `body_start_line`, `source`, `body`, `anchors`, `acceptances`；派生属性 `key`、`acceptance_ids` |
| `SourceLocation` | `path: Path`（实际绝对路径）、`line: int`（1-based） |
| `Target` | `target`, `criterion_anchor`, `test_id: str \| None`, `location`, `criterion_location` |
| `Confirmation` | `by`, `reference`, `baseline`, `location`；存在不意味着批准人已核实 |
| `Anchor` | `name`, `location` |
| `Acceptance` | 标题完整 `id`、`owner`（scope/id）、`anchor`、标题 `location`、`anchor_location`；派生属性 `reference`（scope/id#anchor） |

`source` 是去除 UTF-8 BOM 后的原文，`body` 从闭合 frontmatter 分隔行之后开始；两者保留原 LF/CRLF，不重排或写回文件。`body_start_line`、目标和验收位置用于后续检查定位；`relative_path` 使用解析后相对根的 `/` 路径。原始字节需要调用者另行读取，不能拿解码后的 `source` 替代原文件的字节摘要。

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

## 使用范围

下游使用只依赖本模块、同级依赖清单与相邻 contracts；不要求下载制作规格、执行日志或维护者回归测试。那些维护资料不随下游候选分发。本模块的解析成功不等于工件图覆盖完整、应用通过或业务验收完成。
