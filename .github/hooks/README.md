# 可选 Git hooks

这两份文件是 Python 入口，不是默认启用的 Git 配置。只有在具体项目获准安装后，才由
[安装器](../utilities/install_hooks.py)创建选定的原生 hook。复制模板、选择 Agent、
添加 workflow 或出现 `Reviewed-by` 都不构成安装、人工批准或服务端门禁。

## 运行依赖与分发

需要 Git、Python 3.11+（venv、conda 或系统解释器均可）以及可导入的 PyYAML 与
jsonschema；[锁定依赖](../utilities/requirements.lock)是已测试版本，不是运行时强制版本。
解释器使用完整绝对路径；不会从 PATH 寻找另一个 Python，也不安装包。命令与环境见
[开发登记](../../docs/development.md#maintenance-tools)。安装提案和两份 hook 的启动共用同一
检查：最低 Python 版本和两项依赖可导入。不满足时在读取 index/工件前退出 2 并提示按
lock 恢复依赖。launcher 传入的选定路径/prefix 与实际解释器、依赖版本只记入报告，
不作为拒绝理由；这不是 OS sandbox。

两份入口只调用 `hook_checks.py`。该窄用途适配器获取 index 并复用
`artifact_io.py`、`check_artifacts.py`、`check_traceability.py` 和
`artifact.schema.json`；没有另一套 Markdown、验收或覆盖算法。上述模块/契约须作为
同一版本组分发。安装器另需要本目录的选定入口与 lock，不依赖制作仓 tests、
研究、日志、会话脚本或外部仓库。

Git for Windows 的实际启动试验发现：绝对 Python shebang 没有选到指定 venv，
加引号的 shebang 也未成功。因此该宿主使用 **Git 自带的 `sh`**，只做解释器存在性
检查与带引号的 `exec`；验证逻辑仍全在 Python。无需 PowerShell 7。POSIX 上可表示的
解释器路径使用直接 Python shebang，启动时仍传入 `-B -X utf8`；含空白或过长路径
使用同样的最薄 `sh` 适配。Windows、Linux、macOS 共用相同的 Python 检查逻辑；
具体宿主的运行证据仍须回到对应报告，不因有代码或 YAML 就算已实测。

## 先查看，再明确安装

以下为需要替换路径的命令形状，不授权在任何当前工作树执行安装。每个 `--hook`
明确选一份；不指定就报参数错误，没有“默认安装全部”。

```text
<project-python> -B -X utf8 .github/utilities/install_hooks.py --root "<checkout-root>" --python "<absolute-project-python>" --hook pre-commit --hook commit-msg
```

默认只输出 JSON 提案：Git root/git-dir/common-dir、已知 worktrees、有效
`core.hooksPath` 来源、准确 hook/ownership receipt 路径、选定解释器及拟议操作。
**不写 hook、配置、index 或源文件。** 核对具体目标、所有权和授权后，才在同一命令
加 `--apply`。工具只创建选定 hook 和对应 receipt；不提交、不推送、不改签名配置。

- 任何已有目标（包括空文件、链接、旧 receipt）都是冲突，不覆盖、不跳过后报完整安装。
- 任何有效 `core.hooksPath` 都是冲突；不接管组织/用户/项目已有 hook 链，不修改它。
- 默认 hooks 属于 common Git metadata。linked worktree 或存在多个 worktrees 时，
  提案说明共享范围并拒绝安装/恢复；本工具没有隐式切换 `extensions.worktreeConfig`
  或影响 sibling 的模式。需要共享接入时由所有者另行设计和授权，不以本命令解阻。
- 工具/入口缺失、解释器缺失、Python 低于 3.11 或依赖无法导入时明确退出 2，
  不安装剩余部分。安装期间的部分写入与恢复边界见下节，不自动删除
  已创建文件，也不把失败当作完整安装。
- Git 入口引用本项目的工具源码，不复制并冻结另一套实现。后续更新源码会改变 hook
  行为，必须重新检查版本与适用性；本地可编辑工具不是对恶意修改的安全边界。

## 恢复与所有者改动

每个安装项旁保存 `<hook>.artifact-maintenance.json`：准确 root/git-dir/路径、
原状态 `absent`、安装字节 SHA256、实际 mode、解释器和空配置变更清单。这是恢复所需
的本地所有权收据，不是批准或加密认证；不要把生成的收据带到另一个 checkout。

```text
<project-python> -B -X utf8 .github/utilities/install_hooks.py --root "<checkout-root>" --hook pre-commit --hook commit-msg --restore
```

默认仍只检查和提案。加 `--apply` 后，先核对全部选中项，再仅删除仍匹配收据的
hook/receipt。后续所有者编辑、mode 改变、缺收据、链接或配置变化均为冲突，保留
现状供所有者处理；不能靠再次安装来覆盖。其他 hooks/config/source/index 不变。
不递归清理目录，安装时新建的空 hooks 目录可保留。恢复不要求原解释器仍可用，
但运行安装器本身仍需要一个获准的 Python。

安装 write/flush/close 或短写失败后，`written` 包含本次已经独占创建的每个准确
路径，即使它只有部分字节；`recovery` 明确标为 `manual-required`，逐项报告
写入/关闭是否完成、当前存在/不可读/owner 冲突状态、预期与实际摘要及大小。
**不做自动 rollback**，连完整且字节相同的文件也保留，避免根据不充分的所有权
推断删除后续编辑。所有者须先检查这些路径及实际内容、核对本次收据与后续改动，
再决定如何协调；不能不加区分地重跑安装/恢复，或递归删除 hooks 目录。
后续安装遇到残留 hook/receipt 仍是冲突；缺失、部分或不匹配的 receipt 不授予
恢复删除权限。失败 JSON 是恢复线索，不是永久所有权认证或自动清理授权。

## pre-commit：检查真正准备提交的 index

本地也可直接观察同一入口的 JSON 与退出码：

```text
<project-python> -B -X utf8 .github/utilities/hook_checks.py pre-commit --root "<checkout-root>"
```

这与 `check_artifacts.py --root ...` 的工作文件模式不同：

1. 获取实际 index 条目，包括 Git 原生 partial commit 提供的 `GIT_INDEX_FILE`。
   不扫描工作文件来替代已暂存内容；未暂存修复不能隐藏无效 index，未暂存损坏也
   不使有效 index 失效。暂存删除和重命名后的完整文件集合参与检查。
2. 使用原始 `cat-file` blob，在私有临时目录构造普通文件快照；Git `mktree` 只向
   同一临时空间写树对象。原 index、源文件、config 与源对象库不写入。
   临时位置由宿主标准临时目录分配，随本次检查回收，不要求项目 venv 可写，
   也不是可持久执行工程。
3. 保存原路径、mode、blob ID、原始 SHA256/大小、index 文件与 manifest 摘要、
   精确 index tree、当前 HEAD 和比较 base/tree。`changes` 用
   added/modified/deleted 表示，rename 是旧路径删除加新路径添加，不猜相似度。
   可执行普通文件的 mode 留在身份记录中，但不会执行它。
4. 工件/链接规则调用同一个完整库存检查器；历史正式身份仍用于识别被删坏元数据的
   当前路径。覆盖从**所有实际 owner AC/VC**出发，包含没有 VT 的验收。零 owner
   验收时覆盖标 `not-applicable`，不要求可选实体都增加 AC；已声明的悬空 targets
   仍检查，真实输入错误不降为空选择。
5. unmerged、intent-to-add、不可读 blob、symlink/gitlink、越界/不可表示路径、
   大小写/Unicode 路径别名明确拒绝。不运行 filters、smudge、textconv、submodule
   或网络访问，不读取 Git 链接的目标，也不修复或暂存内容。

`--base` 只接受本地可读取的完整 40/64 位 commit ID。显式错误绝不回退到 HEAD、
main/master 或空比较。未给 base 时记录 hook 调用时的当前 HEAD；仅在确认为尚无
分支 ref 的 unborn 状态才使用无历史比较。`snapshot.parent/head` 是这个比较用的
HEAD，不承诺推断 amend/rebase/merge 完成后的完整 parent 图；`base_origin`
明确记录来源。index 与 HEAD 只在检查开始时读取一次。

报告保留共享检查器的 owner、行、target、实际计数和字节基线，临时文件诊断映射回
原 checkout 路径。`runtime` 另记实际解释器、依赖版本和运行中的工具源码/schema
摘要；不能将暂存的工具 blob 冒充实际执行的工作版本。Git 自己的 commit 操作可能
刷新 index cache/stat；这不同于检查器修改暂存条目。

`0 = clean/empty`、`1 = invalid`、`2 = input-error`。empty 与零 owner 不代表业务
或应用验收通过；`checked_count/attempted_count` 是正式工件数，不是回归测试数。
原生 Git 自身可能把 hook 的 1/2 均归为非零 commit 退出，hook JSON 中保留原 0/1/2。
初始环境校验通过（`startup_validated: true`）后，显式 `--report "<new.json>"`
才调用共享报告写入；父目录须存在，已有输出一律拒绝覆盖。该标记只表示初始环境
校验通过，不表示工件有效；正常环境下的工件/基线输入错误仍可保存到新报告。
启动拒绝时保留 stdout JSON、恢复提示和退出 2，但明确返回
`report_output.written: false`、`reason: startup-refused`；不为报告再导入 validators，
也不检查、打开或创建所请求的报告路径。先恢复所选环境，再重新请求文件输出。

## commit-msg：仅启用后的受管路径格式政策

本地政策 `managed-reviewed-by-text-v1` 对当前 HEAD 与实际 index 的差异生效，
包括删除与 rename 的两侧。受管范围是：

- `domain-model/`、`stakeholder-requirements/`、`software-requirements/`、
  `user-stories/`、`architecture/`、`verification/` 下的
  `.md/.feature/.yaml/.yml/.json`，含 guide 和场景 companion。
- 根目录 `bc-config.yaml`、`model-sources.yaml`、`model.yaml`、`model.json`。

其他路径不要求 reviewer 行，不引入全仓默认提交约定。受管变化需要至少一行
`Reviewed-by: name`，键不区分大小写。值去除两端空白后至少两个字符并含字母，
不能是 `reviewer/name/none/n/a/unknown/pending/not-run/待确认`、已有工件规则的
占位 token，或 `<name>/<reviewer>`。出现多行时每一行都必须满足规则；邮箱不是
必填项，也不会据邮箱判断真实身份。缺失/无效返回 1；消息读取/编码/路径失败返回 2。

hook 只读取 Git 提供的消息文件，保存摘要，不添加 reviewer、不改消息、不执行其中
的内容。merge/fixup/squash 标题没有特殊放行分支。它只在 Git 真正调用该 hook 时
执行；不同 Git 命令的 hook 生命周期不能由本文件扩大。

**这只证明文本形状，不认证 reviewer、角色、人工参与、批准或 waiver。**
原生 `--no-verify`、更换/禁用 hooks 或编辑本地工具仍可绕过；任何绕过都不是已验证
审阅。服务端保护须由实际平台单独配置和验证，不能从本地 hook 的通过推导。

## 两类 workflow 分开

[validate-artifacts](../workflows/validate-artifacts.yml)是可分发的资料校验入口：
只需候选内上述 Python/契约/lock 和项目文件。它不安装 hooks，不运行制作 tests。
PR checkout 精确 head，比较参数取精确 PR base SHA；缺失/非法 base 按输入错误处理。
非 PR 使用实际 checkout HEAD 的 index。JSON 上传与原始 job 输出分别保留。

`tooling-tests.yml` 和 `tests/run_tooling_tests.py` 是**制作仓专用**，不随下游候选
分发。它们运行真实 unittest discovery，保留发现、运行、执行、跳过、失败和错误；
零发现、全跳过或非空套件失败都使 job 失败。它们不是资料检查器的依赖。

资料 workflow 使用 Ubuntu 24.04；制作仓回归使用 Windows、Ubuntu、macOS 矩阵，
各自保留报告。运行步骤均为 Python，使用 venv 返回的实际解释器而非写死平台路径；
最低版本为 Python 3.11，恢复同一 lock。无应用、写权限、secret、
`pull_request_target`、required-check 配置或传播任务。本地 YAML 解析和 Git 测试
不是托管 CI 通过；实际 hosted run 和服务端必需检查仍需原始平台结果。
不要在授权前因本文示例启动远端流程。
