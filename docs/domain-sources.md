# 可选本地领域源接入

默认仍是单仓资料，不要求外部来源、子模块或新应用。已有来源需要登记时，使用
[原 BC 配置](../.github/contracts/README.md#bc-configuration)中的
`id/kind/root/path/baseline/readOnly`；本工具不增加来源 manifest、执行命令或批准字段。
Python 与依赖沿用[维护工具环境](development.md#maintenance-tools)。

入口是 [setup_domain_source.py](../.github/utilities/setup_domain_source.py)，共同的
YAML/schema、路径与固定基线逻辑由同目录的 `artifact_io.py`、
`check_artifacts.py`、`source_baseline.py` 提供。它不读取制作仓的测试或执行历史。

<a id="operations"></a>
## 先区分三种操作

| 操作 | 读取与修改范围 |
|---|---|
| inspect（默认） | 核对明确的本地源、实际路径、固定基线、已有 BC 来源和目标状态，只向 stdout 返回提案。源/目标文件、Git 对象、index、refs 和 config 都不写 |
| register | 只向**明确选中的既有** BC 配置追加这一项来源；不复制领域文件、不建 checkout，也不自动暂存。完全相同的来源已经登记时为 no-change |
| submodule | 在明确的空或不存在目标创建本地原生 Git 子模块，写入 `.gitmodules`、本仓 local config、模块 metadata 和 gitlink/index。**不修改 BC 配置**；随后要采用它，另行 inspect/register 返回的准确 `suggested_registration` |

非空 `domain-model\README.md` 不妨碍登记一项只读引用。反过来，该目录若是
materialization 的目标，既有内容就是冲突，不能删除占位、覆盖或跳过后称接入完成。
重复运行只有在来源、文件和原生 metadata 完全匹配时才是 no-change；残缺安装需先核对恢复。

`readOnly` 描述来源性质，不是 OS ACL，也不授予任何写入权。即使声明为 false，
本工具仍不写来源。`--owned-target` 只表示调用者声明拥有本次目标操作权限，
不能证明身份或改变操作系统权限。

<a id="inputs"></a>
## 准确输入与停止条件

- `root` 是本次选定的本地项目根。`--config` 是该根内**已有**的 BC 配置路径；
  配置必须符合原 schemaVersion 1，并指向真实的开发登记文件/锚点。本工具不初始化项目配置。
- 来源 `root` 是相对此项目根的明确目录，可用 `../已有领域源` 选择获准的独立本地源；
  `path` 只相对此源根解释。允许空格/中文和单独的 `.`，不展开变量，不修剪重复目录。
  来源根按宿主正常方式解析，经过 symlink/junction 的祖先路径与其实际位置等价；`..` 先按字面
  归一，使 Windows/Linux/macOS 得到同一位置。越出项目或来源根、Git/环境数据路径仍被拒绝。
- `git` 来源须给可读的完整小写 40/64 位 **commit**；`local` 可用同样的 commit，
  或一个文件的原始 `sha256:` 摘要。commit 的文件/目录须与本地实际文件集和 bytes 一致。
  SHA256 不是目录摘要。没有默认 HEAD、main/master、分支、短号、tree/blob/tag、index 或远端 fallback。
- 来源 ID 冲突、别名/重叠位置和错误挂载层次都明确报告，不合并、不选第一项、不静默改 `root/path`。
  结构合法不表示来源获准、业务含义正确或已通过验收。
- URL、SCP 样式地址和 UNC 来源始终 unavailable/proposal-only。本工具没有网络授权开关，
  不探测 DNS、凭据或远端，不 fetch/clone 网络来源。需要网络资料时先在单独获授权的流程准备本地 checkout。

<a id="git-config-boundary"></a>
### Git 调用环境

工具用干净的 Git 环境运行本地命令：不继承仓库/index/对象位置覆盖，禁用全局/系统配置、
网络 transport 与交互提示，保留宿主 Git 自身所需的 `GIT_EXEC_PATH`。每次调用把
`GIT_CEILING_DIRECTORIES` 设为所选根的上级目录，因此不完整或缺失的 Git metadata 返回
`BASE_UNAVAILABLE`，不会通过 discovery 借用祖先仓库。没有 Git metadata 的普通 local 文件
来源仍可按内容摘要检查，不因此要求建立仓库。

仓库自身的 Git 配置（包括 include）按 Git 原生规则生效，工具不另行解析或改写所有者配置。
需要严格隔离外部配置时，应在获授权的独立环境中准备本地 checkout；这不是 OS ACL 或
恶意并发文件系统的隔离保证。

register 保留其他键、来源条目、注释及换行 bytes，只编辑 `domainSources`：
可追加独立的 `domainSources: []` 或 block-style list；不为编辑 flow-style/JSON/无法安全定位的
YAML 而重排全文件。不可安全追加时返回 `CONFIG_EDIT_UNSUPPORTED`，须由所有者在另一次明确维护中处理。
已完全登记的合法配置仍可只读核对/no-change，不要求为工具改格式。

<a id="api"></a>
## Python API 与返回

从同目录模块导入：

```python
inspect_domain_source(root, source_config, *,
                      operation="register", config_path="bc-config.yaml", target=None) -> dict

apply_domain_source(root, source_config, *,
                    operation, config_path, expected,
                    owned=False, target=None, index_consent=False) -> dict
```

`source_config` 是原契约的一项 mapping，不是第二个配置文件。inspect 不变更全局 cwd。
apply 必须明确给出操作/配置路径、目标所有权声明和本次 inspect 的 `preflight`；
submodule 另需 `target` 与独立 `index_consent=True`。这些参数只是显式输入，不替代调用者实际授权。

| 字段 | 含义 |
|---|---|
| `status / exit_code` | `ready / 0`：本地准备可行或明确操作成功；`conflict / 1`：可读的所有者/基线/目标冲突；`unavailable / 2`：缺项、路径/配置/对象不可用、拒绝授权或 I/O 失败 |
| `outcome` | `proposed / no-change / registered / materialized / not-applied / partial`，区分准备、无变化、实际操作与残留状态，不表示业务通过 |
| `source / location` | 原来源声明、解析后的源根、相对 path、准确 selected 路径与原 baseline；被拒绝的网络地址不回显 |
| `ownership` | 原 readOnly、始终 false 的 source_writes 与 os_enforced；不把声明当访问控制 |
| `config / target / actions` | 准确配置/目标及拟修改路径；submodule 单列 local config、metadata 和需要另行同意的 index |
| `preflight` | 本次准确来源文件、登记、配置、目标和相关 Git index/refs/config 身份的摘要；BC 配置绑定实际解析/规划的原始 bytes，不是批准或永久凭证 |
| `findings / written / native` | 稳定 code、实际路径和原因；已写路径；真正执行的原生命令、cwd、退出码与原始 stdout/stderr |
| `suggested_registration` | submodule 对应的新源根与原 path/版本；只是下一次独立登记的输入，不自动应用 |
| `recovery` | 失败后的准确保留路径、可读状态/摘要和手工恢复要求；不会自动清理或恢复所有者内容 |

`BASE_MISMATCH` 是 conflict；缺失/非法固定对象为 unavailable。
`SOURCE_ID_CONFLICT / SOURCE_ALIAS / TARGET_CONFLICT / SUBMODULE_CONFLICT / INDEX_CONFLICT`
保留冲突范围。`INPUT_CHANGED` 表示 apply 时重新取得的 preflight 与给定 `--expect` 不同：
已解析的原始 bytes 参与 token，必须重新 inspect，不能沿用旧 token。
`OWNERSHIP_CONSENT_REQUIRED / PREFLIGHT_REQUIRED / INDEX_CONSENT_REQUIRED` 不授予隐含许可。

每个输入只读一次；工具不是文件系统事务，也不是恶意并发进程的 sandbox。
不要在来源或目标仍被其他进程修改时 inspect 或 apply。

<a id="cli"></a>
## 默认只读 CLI

以下 cwd 为选定项目根；脚本/解释器用本机实际已配置位置。尖括号必须替换为本次真实输入。
已有 BC 来源可直接按 ID 选择：

```text
python -B -X utf8 .github/utilities/setup_domain_source.py --root . --config bc-config.yaml --source-id owned-domain
```

提出尚未登记的来源时，完整供应这六项中的其余字段：

```text
python -B -X utf8 .github/utilities/setup_domain_source.py --root . --config bc-config.yaml --source-id owned-domain --kind git --source-root "../已有领域源" --source-path domain-model --baseline <完整本地commit> --read-only
```

`--owned-source` 仅替代 `--read-only` 声明 readOnly false，不允许写来源。
缺字段不会根据已有配置或 HEAD 补齐。输出为 JSON；无文件报告开关，inspect 不落盘。
参数用法错误由 argparse 退出 2；可读冲突/输入失败分别保留 JSON 和 1/2。

确认本次 exact config 操作已获授权后，在**同一组来源参数**上增加：

```text
--operation register --apply --owned-target --expect <本次inspect的preflight>
```

若配置/index/refs/来源已变，旧 token 无效；不能只更换 token 规避冲突。
register 不提交、不暂存，也不将 readonly 登记解释成已 materialize。

<a id="submodule"></a>
## 可选：只从自有本地仓创建原生子模块

这不是默认方式。先选 `--operation submodule --target <准确相对目标>` 做 inspect；
提案会列出目标 checkout、`.gitmodules`、local config、`.git\modules\<source-id>` 和 index。
仅在该本地源/目标操作及 index 变化分别获准后，再增加：

```text
--apply --owned-target --index-consent --expect <该submodule提案的preflight>
```

实际原生操作是：`git clone --local --no-hardlinks --no-checkout --template=`
配合明确的 `--separate-git-dir`，在**新模块**中 `update-ref --no-deref HEAD` 固定对象，
从原始普通 blobs 写文件并用 `update-index --index-info` 建立模块 index。
不执行 `checkout`、clean/smudge/textconv、来源 hooks、模板 hook 或递归 submodule update。
完整 commit 中的链接/gitlink、不可安全写入路径或大小写别名会在写入前拒绝。

随后只追加该 native module 的 `.gitmodules`/local config 区段，用原始 `hash-object --stdin`
和 `update-index --index-info` 暂存 `.gitmodules` 与准确 gitlink；不让 `.gitattributes` 的 filter
代写这些 bytes。与目标无关的 staged entries、refs 和配置前缀保留。
本地 URL 使用明确源根的文件系统路径，提案/日志会披露它；这是本机接入，不是可移植远端 URL。

来源必须有自包含本地对象，不支持 shallow/promisor/alternates；目标须为独立非共享 checkout，
且源/父仓的 Git 对象格式一致（SHA1 或 SHA256，不混用）。
已有模块 ID/path、staged 与 working `.gitmodules` 不符、owner lock、非空目标或残缺 metadata
均停止。若 HEAD 已有 `.gitmodules`，但 index 中缺失，即使 working 文件仍在、新 checkout
目标尚不存在，也按所有者已暂存删除处理，在 clone 前冲突；index 同意不能撤销该意图。
大小写别名的 metadata 身份同样不能被静默重建。只有 HEAD 确无此 metadata，或确为
unborn 父仓时，才可能按真正新建处理；不把不可读 HEAD 当作新仓。
这里的 HEAD 只用于核对父仓 owner/index 意图，不替代领域来源的明确固定 baseline。
checkout 目标不得与 `.gitmodules` 文件相同或重叠，包括大小写/后代路径。
文件协议放行只限该次准确的本地 clone 命令，绝不改 user/global Git config。
没有 commit/push 操作，也没有把 source readOnly、既有配置或 `--apply` 当作 index 同意。

<a id="recovery"></a>
## 失败与恢复

配置通过新建同目录临时文件、核对原 bytes 后替换，不先截断所有者文件。
若写入/替换失败，保留已创建的临时文件或部分 checkout/module metadata，
`outcome: partial` 和 `recovery` 指明准确位置；不递归删除、不 reset index、不回写源，
也不把未完成步骤说成跳过成功。

恢复须由获授权的所有者先比较报告中的先前摘要、现有 bytes、index/refs 和后续编辑；
只处理已确认属于本次操作的准确文件/metadata。工具没有自动 restore/清理命令。
部分目录存在时重试不会宣称 no-change；后续 owner 内容仍受保护。
本地准备/接入成功不证明领域事实、应用、远端平台、人工批准或发布通过。

Windows 的原生命令仅对该次调用设置 `core.longpaths=true`，避免模块 metadata 中较长的
SHA256 对象路径失败；不会更改所有者的 core.longpaths 配置。其他宿主须按实际环境验证。
