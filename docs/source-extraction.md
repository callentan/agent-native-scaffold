# 本地来源候选与透明评分

这些可选工具读取本次明确选择的本地文件，返回候选，不写正式领域事实。
使用者先核对读取授权；可读文件不等于获准处理真实私有文档或发送资料。
[逆向方法](../.github/skills/reverse-engineer-domain/SKILL.md)仍负责回源、
比较相反陈述、请求澄清和后续获准拟稿。评分不能确认业务规则、认证说话者或批准候选。

工具使用[已有维护环境](development.md#maintenance-tools)，不要求新的媒体包。
[可选 media 清单](../.github/utilities/requirements-media.txt)目前只有说明，
没有选定 DOCX 包、音频服务、模型或 SDK；不要据此安装猜测的依赖。

<a id="interfaces"></a>
## API 与来源身份

从 `.github\utilities\` 导入以下窄接口；它们不扫描仓库、不执行正文或跟随链接：

```python
extract_candidates(source: str | os.PathLike[str], kind: str) -> dict
score_candidates(items: list[dict]) -> list[dict]
```

`source` 必须是明确的绝对本地普通文件路径。拒绝 URL、UNC、歧义的 drive-relative
路径、alternate stream 和链接/reparse 遍历；不是 OS sandbox，也不保证抵御其他进程的
恶意并发替换。来源身份是**本次实际读取的字节**，不是推断的 Git commit 或正式工件身份。
API 不写文件或改变 cwd。

提取返回一个 envelope，其中 `candidates` 是候选列表；保留 envelope 是为了让空输入也有
真实读取身份。固定字段如下，不属于正式 artifact schema，也不增加任何正式 kind：

| 字段 | 含义 |
|---|---|
| `status` | `extracted` 或 `empty`，不是业务通过/批准 |
| `source` | `path`：实际绝对本地路径；`kind`：明确的格式选择；`baseline`：`sha256:` 加原始字节的 64 位小写十六进制摘要；`byte_count`：实际读取字节数 |
| `unit_count` | 文本/Markdown/转录的原始物理行数，按 Python `str.splitlines()`；DOCX 为支持布局中全部段落数，含空段和单元格段落 |
| `candidate_count` | 实际列表长度，不是验收数量 |
| `candidates` | 按原始文件顺序保留候选，不按文本去重或重排时间 |

每个候选具有以下固定字段：

| 字段 | 含义 |
|---|---|
| `candidate_id` | `candidate-0001` 起的本次局部序号；不同来源可重号，不能当成 REQ/RULE 或 canonical ID |
| `kind` | `rule`、`capability`、`use-case`、`term` 或 `statement` 的候选类型 |
| `nature` | `observed`：显式标签；`inferred`：未标注文字的词法分类；`uncertain`：提案/待定措辞。均不表示事实已确认 |
| `text` | 所选来源单元的可见文字，去掉首尾空白，不补参与者、指标或结论 |
| `fragment` | 原始行/转录 JSON 行或 DOCX 段落文字；不冒充缺失的原始访谈或 XML 行号 |
| `source`、`location` | 同一实际字节身份及下述 1-based 格式坐标 |
| `uncertainty` | 保留检测到的提案词及理由；直接表述没有这些词时为空，不代表与其他来源一致 |
| `extraction_reason` | 显式标签或词法推断的分类依据 |
| `clarification` | 请求实际所有者确认范围、核对相反来源；不制造具名批准人或决定编号 |

支持的显式标签为 `Rule:`、`Capability:`、`Use case:` / `Use-case:`、
`Term:` 以及 `规则：`、`能力：`、`用例：`、`术语：`。英文大小写不敏感。
未标注文字仅按 `must/shall/never/required/cannot/必须/不得/禁止` 推断 rule，
按 `can/allows/supports/能够/支持` 推断 capability，其余为 statement。
这不是完整自然语言识别器，不能证明必要性或领域类型正确。
`maybe/should/proposed/perhaps/unconfirmed/待确认/可能/建议` 保留为 uncertainty，
覆盖普通的 observed/inferred 分类。相反来源可能都没有提案词，仍必须保留双方并由方法比较；
工具不自动检测全部业务矛盾、不选优先规则，也没有 supersedes/confirmed 状态。

<a id="formats"></a>
## 本地格式与精确定位

| `kind` / 扩展名 | 读取与候选单元 | `location` |
|---|---|---|
| `text` / `.txt` | UTF-8，每个非空行一个候选，命令样文本只是文字 | `line`、`paragraph` |
| `markdown` / `.md` | UTF-8，复用已有 Markdown 行扫描器跳过代码/注释、ATX 标题；可见非空行成为候选，不另解析 frontmatter 或正式身份 | `line`、`paragraph` |
| `transcript` / `.txt` | 以下严格 JSON Lines，每个非空行一个完整 turn | `line`、`turn`、`speaker`、`timestamp` |
| `docx` / `.docx` | 以下有界 OOXML 子集，一个非空段落一个候选，包括表格单元格 | `part`、`block`、`paragraph`；单元格再有 `table`、`row`、`cell`、`cell_paragraph` |

UTF-8 可有 BOM，支持 Unicode、空格路径与 CRLF。字节摘要保留 BOM/换行原貌；
`fragment` 的文本行不含行终止符。文本 paragraph 是**过滤前**以空白行分隔的连续非空
原始行组，所以 Markdown 标题、注释和围栏所在组仍计数，不伪装成渲染器语义段落。
Markdown 的 `text` 可去掉内联 HTML 注释，`fragment` 仍保留原始行，评分使用同一行扫描器
核对可见摘录。工具不是完整 Markdown renderer，不自动把表格、标题或 frontmatter 转成正式工件。

### 明确转录格式

每个非空物理行必须是 JSON object，恰好具有三个非空字符串字段，无重复/额外 key：

```json
{"speaker":"A","timestamp":"00:00:02.125","text":"Rule: Members must keep receipts."}
{"speaker":"B","timestamp":"00:00:01.000","text":"Maybe that policy should change."}
```

时间戳固定为 `HH:MM:SS.mmm`（两位小时，分/秒 00–59，三位毫秒）。
保留输入顺序、说话者和时间字符串；不认证姓名、校验真实时钟或推断先后关系。
`text` 是 JSON 解码后的文字，`fragment` 是原始 JSON 行，转义不改变 source baseline。
空行不增加 turn；非法 JSON、非有限数、缺字段、空 text、非法 Unicode/control 字符
或任意坏 turn 都让整次读取失败，不返回前半段“成功”。

### 有界 stdlib DOCX

实现使用已选 Python 标准库 `zipfile` 与 XML，不调用转换器或新增 parser 包。
实际读取 DOCX ZIP 容器，不把改后缀的文本当成文档。
当前只接受三个必需 OPC 部件：
`[Content_Types].xml`、`_rels/.rels`、`word/document.xml`，
可另有空的 `word/`、`_rels/` 目录项。content type 必须是非宏 DOCX document；
根 relationship 必须是固定的内部 main-document 关系，只校验，不跟随它读取其他位置。

支持 transitional WordprocessingML 的 `document/body`、普通 `p/r/t`、
run 中 `tab/br/cr`、末尾空 `sectPr`，以及矩形 `tbl/tr/tc` 表格。
表格可有空 `tblPr`、简单 `tblGrid/gridCol` 和仅含 `tcW` 的 `tcPr`。
保留 run 连接顺序、XML 解码文字、tab 和换行，不补空格、页面或音频时间。
`block` 是 body 中的位置；`paragraph` 按文档顺序计所有段落；
`cell_paragraph` 是该格内的段落位置，其他坐标按文档/表格内顺序计数。
坐标不是页码或 XML 行号，来源 baseline 仍是整个实际 ZIP 的字节摘要。

**不支持的布局明确拒绝，不返回部分成功：** 额外部件（含常见 styles/settings、
properties、headers/footers、脚注、图片、宏、附加 relationships）、
Strict OOXML、非 UTF-8 XML、合并/嵌套表格、样式属性、字段、超链接、修订、
内容控件、嵌入对象与其他正文布局。普通办公文档可能包含这些内容，不能据窄适配器
宣称任意 DOCX 已完整提取；需另行决定所需格式扩展和输入授权。

不会解包到磁盘、解析外部实体、访问 relationship 目标或执行文档内容。
拒绝 ZIP traversal/绝对路径/backslash/NUL/重名/类型别名、加密 ZIP、DTD/entity
声明、损坏 XML/CRC、缺必需部件及不支持的压缩/布局。XML 注释等非正文不作为业务候选；
它们仍在整个输入字节身份内。

| 资源边界 | 固定限制 |
|---|---|
| 单个来源或 CLI scoring JSON | 4 MiB 原始输入；超限失败，不截断成功 |
| 文本/Markdown/转录行数 | 10,000（含空/排除行），在候选扩展前检查 |
| 单次评分 | 10,000 个候选；API 与 CLI 均拒绝更大集合 |
| ZIP entries | 64，含目录项 |
| 单个 ZIP part / 全部解压 bytes | 1 MiB / 8 MiB |
| ZIP 展开比 | 每个 part 不大于 `100 × max(compressed_size, 1)` |
| 每个 XML part | 深度不大于 32，元素数不大于 10,000，解析时检查 |

<a id="scoring"></a>
## 透明评分

`score_candidates` 接受未评分候选的具体 list，先校验完整来源身份、位置、类型、
字面/Markdown 可见摘录或解码 turn 与 nature/uncertainty 的一致性。
无来源、非法枚举、负数、bool 冒充计数、非法 Unicode、缺位置或未知字段是错误，
不会偷偷记 0。空来源可有 empty envelope，但不能提供非空候选。
来源路径须是无 `.` / `..`、alternate stream 的绝对本地声明。

评分返回深复制的候选，追加 `score`，不改变输入、不去重、不开原始来源重算，
也不认证 source hash 或说话者；外部提供的 provenance 只作形状/一致性核对。
跨源矛盾或重复没有自动加分，全部保留其出处。

| factor | 分值与公开理由 |
|---|---|
| `evidence` | 30：非空摘录与所给 fragment 一致，身份语法完整；不是独立来源真实性证明 |
| `locator` | 25：该格式必需的正整数坐标及提供的 speaker/time 完整 |
| `completeness` | 显式类型标签 15，加 stripped text 至少 16 字符 10；不是业务语义完整性 |
| `uncertainty` | observed 20、inferred 10、uncertain 0 |

总分为四项之和，整数 0–100；`score.scale`、逐项 `factors[].value/reason`、
`meaning` 全部返回。显式标签的长直接陈述可得 100，长 uncertain 陈述为 80，
无标签的长 inferred 陈述为 75；相反的两条陈述也可能同分。
这是证据质量的确定性启发式，**不是校准概率、模型置信度、业务决策或自动接受阈值**。
高分不消除冲突、未知上下文或责任人确认关卡。

<a id="cli"></a>
## CLI、输出与错误

以下命令 cwd 为选择的资料仓库根；路径示例必须替换为本次实际文件。
API 只读；CLI 默认只输出 UTF-8 JSON。`--root` 必填，约束 CLI 输入及新输出范围，
相对路径均相对该 root，不自动读工作区其他文件。

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\extract_source.py --root . --source "sources\notes.md" --kind markdown
.venv\Scripts\python.exe -B -X utf8 .github\utilities\extract_source.py --root . --source "sources\notes.md" --kind markdown --output "reports\notes-candidates.json"
.venv\Scripts\python.exe -B -X utf8 .github\utilities\score_candidates.py --root . --input "reports\notes-candidates.json" --output "reports\notes-scored.json"
```

scoring CLI 可读完整提取 envelope（保留 source 和读取计数），或明确合并的候选 JSON list
（保留各自来源）；不会自动搜索或合并来源。JSON 同样拒绝重复 key/非有限数。
保存须显式指定不存在的 `.json`，父目录已存在、位于 root 内且不经别名，
不占用声明来源或输入；exclusive create，无覆盖、无 mkdir、无自动修复。
拒绝已有文件/源/目录、越界、stream 路径及缺父目录。I/O 部分失败不保证回滚；
保留明确错误和可能的本次部分输出，不能据此覆盖 owner 内容重试。

| 结果 / code | 含义与退出 |
|---|---|
| `extracted` / `empty` 或合法 scoring list | 退出 0，仅本次离线处理完成；空输入保留真实身份，不是业务通过 |
| `FILE_NOT_FOUND` / `FILE_READ_ERROR` / `INVALID_PATH` / `OUTSIDE_ROOT` | 本地读取/路径错误，退出 2 |
| `INVALID_ENCODING` / `INVALID_SOURCE_FORMAT` / `INVALID_TRANSCRIPT` | 输入格式/编码错误，退出 2，不返回假空成功 |
| `INVALID_DOCX` / `INVALID_DOCX_XML` / `UNSUPPORTED_DOCX` / `UNSAFE_DOCX` / `SOURCE_ENCRYPTED` | 实际容器、布局或安全边界拒绝，退出 2 |
| `SOURCE_LIMIT_EXCEEDED` / `CANDIDATE_LIMIT_EXCEEDED` | 超过公开资源界限，退出 2 |
| `INVALID_CANDIDATE` / `INVALID_CANDIDATE_KIND` / `INVALID_CANDIDATE_LOCATION` / `INVALID_SOURCE_IDENTITY` | 评分输入不成立，退出 2 |
| `REPORT_CONFLICT` / `REPORT_WRITE_ERROR` | 输出冲突/写入失败，退出 2；保留原输入 |
| `SOURCE_ADAPTER_UNAVAILABLE` | 没有当前支持的格式/适配器，含 compound/encrypted Office 容器和音频适配器，退出 2 |

API 抛已有 `ArtifactInputError`，保留 `code/path/line/message` 和底层异常链。
CLI 错误 stdout 为 `{"status":"input-error","error":{...}}`；
参数语法错误由 argparse 向 stderr 报错并退出 2。没有将候选判为接受/拒绝的退出 1。
未知 kind 不从扩展名猜测；read/parse 失败不降为 empty。

<a id="audio"></a>
## 音频关卡：仅有诚实拒绝入口

```python
transcribe_audio(
    source, *, service=None, model=None, data_scope=None,
    operation=None, output=None, authorized=False,
) -> NoReturn
```

当前没有选定或批准任何音频服务、模型、SDK、适配器或数据发送范围。
`transcribe_audio.py --source <本次明确输入>` 的 CLI 与 API 均不读取音频/密钥、
不发现环境 provider、不安装包、不发送数据、不写输出、不返回假空 transcript：

- 未独立授权：`AUDIO_AUTHORIZATION_REQUIRED`，列缺失输入。
- 声明 authorized 但缺 service/model/data_scope/operation/output：`AUDIO_INPUT_REQUIRED`。
- 所有未来字段都提供，operation 为 `transcribe`：仍为 `SOURCE_ADAPTER_UNAVAILABLE`。
  传入服务名或 `--authorized` **不能**选择、安装或启用一个适配器。

未来真实调用须另有明确输入/服务/模型/固定 SDK 版本、操作、允许的数据范围/发送目标、
准确新输出和授权，再实施具体适配器及真实失败传播。当前未验证任何转录服务成功或失败；
本地拒绝合同不替代实际音频验收，也不关闭相关增强条件。
