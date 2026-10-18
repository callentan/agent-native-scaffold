# 有来源的本地文档导出

这些工具只生成可重建的派生文档，不接管领域、架构决定、VT 结果或批准。
使用 Python 3.11+ 和[既有维护环境](development.md#maintenance-tools)；
本地 JSON、SVG、HTML 只用 stdlib，没有浏览器、CDN、远程字体或来源命令。
[rendering 清单](../.github/utilities/requirements-rendering.txt)不选择 PDF/PPTX 引擎。

## 输入和返回值

三个绑定函数从同名模块导入，API 不写文件，也不改变 cwd：

```python
render_traceability(view)
render_architecture(inputs, format)
render_presentation(inputs, format)
```

`view` 是普通 Python mapping，只有必填 `root`、`scope`，可选 `format`
（默认 `json`）和 `model_path`。`inputs` 是同样的显式 `root`、`scope`、
可选 `model_path`，以及必填的 `sources` 列表。它不是另一个文件 manifest。
每个 source 沿用现有 evidence 指针：`{"reference": "architecture/SWAS-001.md",
"baseline": "sha256:实际原始字节摘要"}`；reference 可以带真实显式锚点，
baseline 也可为可读的完整本地 Git commit/blob。未知字段、重复选择、非法版本、
路径、引用和不匹配的基线都不是空数据。

每次调用都读取显式 root 的真实库存，复用 parser、九视图派生、来源选择和
基线核对。`model_path` 仅是待核对的已有模型：按 `check_model` 重算，
`STALE_MODEL_SOURCE` / `MODEL_MISMATCH` 阻止渲染，不信任 schema-valid YAML。
不接受脱离 root 的模型 dict 作为已验证事实。这里没有公开的“任意数据已验证”
投影捷径，也不从文件名、扩展名、cwd 或 `available` 推断来源、执行或批准。

架构/演示 sources 的 Markdown 必须是库存中的真实正式工件；保留 source ID、
路径、原始 baseline、行号和实际章节。JSON/YAML 必须是九视图已经核对的来源，
不把任意 mapping 当 SWAS。实施报告只沿既有 report adapter 核对并保留导航，
不将其执行/适用性条目重新解释为本次结果。引用不授予执行或写回权限。

返回普通 dict，固定具有：

| 字段 | 含义 |
|---|---|
| `status` | `rendered`、`partial`、`empty`、`unsupported` 或 `unavailable`，均不是业务结果 |
| `format` / `media_type` | 实际格式和 MIME；不可用时 MIME 为 null |
| `content` | 完整 UTF-8 文本内容；不可用时为 null，不返回伪造二进制 |
| `counts` | 实际 `nodes/edges/sections/diagrams/messages/slides` 数量；没有该类则 0 |
| `source` | 选定 scope 的真实派生 source 身份；空 trace 使用库存的实际 snapshot 身份 |
| `gaps` | 实际来源、完整性和有限语法缺口，不据此计算风险/批准 |
| `gates` | 本地格式为空；PDF/PPTX 列出尚未执行的授权、依赖、解析、页数/slide 数及内容检查 |

输入/来源/格式/I/O 错误抛现有 `ArtifactInputError(code, path, line, message)`。
API 不吞错、不安装、不发送数据。渲染末尾重查读集字节，变化为 `INPUT_CHANGED`；
这不是文件系统事务或 OS sandbox，不保证抵御并发恶意替换。

## 关系图

trace 支持 `json`、`svg`、`html`。JSON content 是实际关系投影，含 `status`、
`scope`、`source`、`nodes`、`edges`、九个 `views` 和 `gaps`。
节点 `key` 是完整 `scope/id`，保留路径、baseline、身份行和完整锚点引用。
边保留 `source/target` 节点 key、`sourceRef/targetRef`、`relation`、
原声明路径/行；targets 另保留 criterion/testId。

- `upstream` 是**声明者 → 所依赖的来源**，不是反转的消息流；
  targets 是**验证/声明者的 criterion → 被验证目标**。
- 选定 scope 的全部 owner 都保留，包括孤立节点；沿实际关系纳入跨 scope
  依赖闭包，同短 ID 不合并。环只遍历一次，边不丢失。
- 没有正式工件且库存合法时，trace 明确 `empty`，节点/边均为 0。
  此时 scope 只记录请求，不确认其存在；不是成功导出的业务模型。
  空库存不能满足显式 `model_path` 检查或架构/演示的主 scope 要求。
- JSON、SVG 和 HTML 都带实际 source/gaps；图中箭头不推断 transport。

## 架构、SEQ 与演示

architecture 支持 `html`、`svg`。输出保留九视图的原 `state/artifactRefs/
evidenceRefs/gaps`，以及所选业务、逻辑、运行、部署来源的实际章节。
业务/逻辑/运行导航分别回 requirements/architecture/sequences；只有实际选择的
`deployment` 章节才提供部署内容，否则明确缺源，不从 ABB 推出部署拓扑。
SWAS 的 `perspectives` 仍按原文展示；不会替作者补语言、容器、分类、风险接受、
生命周期或发布。缺 ABB/风险/部署时仍可输出有缺口的文档，不称完整 SWAS。

SEQ 的 `diagram` 显式锚点章节内，只接受共享 scanner 识别出的**一个闭合**
Mermaid 围栏，无附加 fence options；多个图明确 unsupported，不拼接。
有限子集是：

- `sequenceDiagram`；`participant ID [as 标签]`、`actor ID [as 标签]`，
  ID 为 ASCII 字母/下划线开头的字母数字下划线。
- 两端已明确声明的 `ID->>ID: 文本`、`ID-->>ID: 文本`，包括自消息。
  保留原箭头 token 和虚实线，不把它们重新解释成同步/异步传输保证。
- 非嵌套的 `alt 文本` / `else 文本` / `end`，以及 `opt 文本`、
  `loop 文本` / `end`；每个区域至少有一条源消息，所有分支、标签与消息保持源顺序。
- 空行及普通整行 `%%` 注释不画；init 指令、隐式参与者、激活、note、
  嵌套片段、其他箭头/语句、空消息、未闭合片段或零消息均明确 unsupported。

不支持的图整体不画成“完整”序列；文档保留来源与具体行/语法缺口，
status 为 `unsupported`，CLI 退出 1。注释、外层 literal、相邻章节和未闭合
fence 不会借位产生消息。成功/拒绝/错误边界来自原 `paths` 节和实际图，
不会由工具补齐。没有完整 Mermaid 兼容承诺。

presentation 是必需的参数化能力，支持 `html`、`svg`，不是固定管理 deck。
每个选中源的真实章节产生对应 slide；长段落分页但不删文本、来源或缺口。
保留全部九视图的来源状态导航，以及实际 SEQ 绘图。两个不同 source 集合
必须产生各自标题、章节、内容和 source ID，不共享硬编码业务叙事。
SVG 是单个可解析的纵向多页画布，HTML 是可打印的连续 slide 文档，
两者都不是 PPTX、PDF 或原生演示应用的验收。

视觉约定是静态、离线的浅色文档，使用系统 serif/sans/monospace fallback，
不建立品牌 profile。完整身份和内容优先，长图/文档滚动，不截掉环或孤立 owner。
SVG 使用可访问 title/desc、完整内容文本和实际方向；不请求外部资源。
源 HTML、脚本、URL 和命令只作安全编码后的文字，输出链接仅为内部导航。

## CLI、写入和错误边界

以仓库根为 cwd，用实际项目解释器执行各脚本：

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_traceability.py --root . --scope sample/CTX-001 --format svg
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_architecture.py --root . --scope sample/CTX-001 --format html --source architecture/SWAS-001.md --baseline sha256:实际摘要
.venv\Scripts\python.exe -B -X utf8 .github\utilities\render_presentation.py --root . --scope sample/CTX-001 --format html --source architecture/SWAS-001.md --baseline sha256:实际摘要
```

替换示例的 scope/来源/baseline；每个 `--source` 有同位置的 `--baseline`。
无 source 的架构/演示 CLI 明确传空选择，只输出来源/缺口导航，不造内容。
可给 `--model-path` 核对已有模型。默认只向 stdout 输出实际文本；
失败/不可用时 stdout 为结构化 JSON 诊断。没有默认写入或目录创建。

`--output` 只允许本次明确的新本地文件，后缀必须与 `--format` 一致，
父目录须已存在，采用 exclusive create。任何已有文件（含空文件）/目录、
源/报告/历史、清单/已解析引用、未选/缺失声明的位置和其祖先/子路径都不能占用；
路径不得进入 `.git` 元数据/历史，即使目标文件尚不存在；输出遍历也不允许
symlink/junction/reparse alias。case/规范化后也须隔离。
非法声明导致无法建立隔离时拒绝写入。写入失败可能留下部分新文件，
不自动清理、覆盖或换路径；下次仍拒绝覆盖。

| 情况 | CLI 退出 |
|---|---|
| 真实本地格式 `rendered/partial/empty` | 0；有内容不表示业务通过 |
| 持久模型漂移，或所选 SEQ unsupported | 1 |
| 输入、源、格式、I/O 错误，或 PDF/PPTX unavailable | 2 |

## 单独未运行的格式关卡

PDF 和 PPTX 请求返回 `unavailable`，`content: null`，不会创建对应输出，
也不探测全局包来推断授权。当前未选择/批准引擎、版本、模板、包、容器或服务。
未来须分别取得选择/安装/处理输入的授权，锁定实际依赖，再执行真实签名、
parser、非零页面/slide 数、完整源内容及人/App 检查。只有文件名、
`%PDF`/`PK` 前缀或零页文件不合格。有限 refusal 回归不是这些格式的成功证据。
本地 HTML/SVG 不关闭完整 ENH-17 或总体 parity。
