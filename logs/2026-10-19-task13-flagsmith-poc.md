# Task13 Flagsmith POC preflight

## 会话、任务与 Git 状态

| 字段 | 内容 |
|---|---|
| 日期与会话标识 | 2026-10-19；Copilot project session `40a224f5-795a-4877-af01-159b9070254e` |
| 任务来源、目标与授权 | 用户选择现有 Flagsmith/OpenFeature POC，并明确授权将副本放在当前仓库 `poc/flagsmith` 以隔离验证 |
| 当前分支与起始基线 | `callentan-repository-skeleton`，`ee463901725ade1d0cab05261b8c875189fd229e`；复制前工作树/暂存区干净 |
| 当前对象与改动 | 本次新增 `poc/flagsmith/` 隔离副本及本地计划/状态文档；未提交、未暂存 |
| 源对象 | Flagsmith POC 来源分支 `master`，固定提交 `beade3c39c3bbb63f14e9c9072e797e24fafc163` |

## 本次变化

- 将固定来源提交的 86 个已跟踪文件复制到 `poc/flagsmith/`，逐文件与 Git blob 身份核对。为避免本机 `core.autocrlf=true` 改变归档字节，复制时关闭归档转换。
- 副本不含 `.git`、忽略的依赖树、工作树目录、本地密钥/配置或服务数据。复制时源仓库另有一个未跟踪设计文件 `docs/superpowers/specs/2026-10-19-feature-flag-poc-docker-compose-design.md`；为保留所有者内容，未将它纳入固定提交副本。源仓库未修改。
- 已更新[增强计划](../docs/plan/2026-10-14-ddd-functional-alignment.md#task13)、[增强规格](../docs/design/ddd-functional-alignment.md)、[路线图](../docs/plan/roadmap.md)与[能力矩阵](../docs/research/ddd-capability-matrix.md)，将 Task13/14 状态限定为 partial/blocked。

该源 README 将项目定义为本地 Angular/.NET 技术 POC，不是已接入业务系统的应用；它包含两个 Boolean flag 和 20 个合成用户，没有产品、定价、订单、认证或业务数据库。因此副本适合有限技术流程检查，不证明真实业务行为或云端验收。

文档登记的栈为 .NET 10、Angular 20.3.0、Node 22.12+ 或 24，OpenFeature 与 Flagsmith 版本由锁文件固定。本机实测 PowerShell 7.6.6、.NET SDK 10.0.400、Node 24.14.0、npm 11.16.0。没有改变副本代码或配置，也没有创建 DDD 业务验收、选择新业务行为、运行应用服务或使用密钥。

## 实际结果入口

| 检查与层次 | 实际记录 | 对象/基线 | 限制 |
|---|---|---|---|
| 副本完整性 | Git archive 固定提交；86 个文件逐个比较 Git blob hash，复制后文件总数 86 | `beade3c39c3bbb63f14e9c9072e797e24fafc163` | 不含源仓库那个未跟踪文档和忽略的环境依赖 |
| 仓库静态检查 | `node scripts/validate-skill.mjs`，cwd `poc/flagsmith`，exit 1；除一项外所有结构、链接、shell、skill 元数据检查均报告 PASS | 复制后的固定提交 | 唯一失败：`LaunchDarkly-vs-Flagsmith-深度对比.md` 命中仓库的 English-only 检查。未修改该已有文档，也未把整项检查描述为通过 |
| POC Windows helper 测试 | `pwsh.exe -NoLogo -NoProfile -NonInteractive -File poc\flagsmith\poc\scripts\Test-PocScripts.ps1 -RepositoryRoot <isolated-root>`，cwd 为当前仓库根，exit 0，输出 `Test-PocScripts: PASS` | 复制后的固定提交；临时 fixture 在会话状态目录 | 覆盖无效 action/路径拒绝、原生参数与 cwd 转发、exit code 37 传播；负例错误输出是预期，fixture 已由测试清理。此测试不执行实际 app |
| 应用构建与单元测试 | 初始复制后 `not-run`；后续追加结果见下节 | `poc/backend`、`poc/backend.tests`、`poc/frontend` | 固定锁定依赖仅恢复到隔离副本 |
| 浏览器测试与 live Flagsmith | 初始复制后 `not-run`；live A01–A15 仍 `not-run` | POC 控制路由与本机 Flagsmith 配置 | 后续 Chromium 测试是受控 mock，不连接真实 Flagsmith；没有本地 POC config 或密钥 |

## 缺口与下一步（初始预检快照）

| 受影响项 | 缺口/影响 | 待执行 |
|---|---|---|
| Task13 应用行为 | 目前只有固定提交的技术 POC 副本；没有 DDD 需求驱动的具体代码生成/既有文件维护变更，构建和测试也未运行 | 先明确该 POC 的授权修改范围及是否允许只在副本恢复 NuGet/npm 锁定依赖；恢复后再运行其文档所列 Build/Test。真实 Flagsmith A01–A15 需要单独配置和实测 |
| Task13 人工/App/client/platform | 没有实际参与者、客户端新会话或隔离平台授权 | 保持 `not-run`；不可用 Agent 模拟人或客户端入口 |
| Task14 矩阵与结论 | 尚未逐行审查 44 个能力组和责任人接受的差异 | Task13 可适用证据取得后继续；不得宣布完整 parity 或发布就绪 |

本记录前半部分保留复制后、依赖恢复前的预检快照；该时点没有源码改动、live service/cloud 调用或提交/推送/发布。后续恢复和执行结果只记录在以下追加，不把预检状态误作最终状态。

## 追加执行证据（2026-10-19）

用户授权的隔离 POC 验证范围内，锁文件未修改。只在 `poc/flagsmith` 副本内恢复 NuGet/npm 依赖；未安装 Playwright 浏览器，使用本机已有的 Chromium。没有恢复依赖到源仓库，也没有配置密钥或访问本机 Flagsmith 服务。

| 检查与层次 | 命令/结果 | 对象与限制 |
|---|---|---|
| NuGet restore | `dotnet restore Poc.Api.csproj --locked-mode --verbosity minimal`，cwd `poc/flagsmith/poc/backend`；`dotnet restore Poc.Api.Tests.csproj --locked-mode --verbosity minimal`，cwd `poc/flagsmith/poc/backend.tests`；exit 0 | Locked restore；恢复 app、test 与两个 child fixture 项目 |
| Angular dependency restore | `npm ci --no-audit --no-fund`，cwd `poc/flagsmith/poc/frontend`；exit 0，543 packages | npm 提示若干 deprecated transitive packages，并因当前 `allow-scripts` 策略阻止 4 个依赖安装脚本；未批准或运行这些脚本，未升级 lockfile |
| POC unit tests | `pwsh.exe -NoLogo -NoProfile -NonInteractive -File poc\flagsmith\poc\scripts\Invoke-Poc.ps1 -RepositoryRoot <workspace-root>\poc\flagsmith -Action Test`；外层 cwd 为 workspace root；exit 0 | .NET `19/19`、Angular/Vitest `35/35`；helper 在项目内部设置各自 cwd；只使用 POC 合成 fixture，不连接 Flagsmith |
| POC build | 上述命令的 `-Action Build`；外层 cwd 为 workspace root；exit 0 | .NET build `0 warnings / 0 errors`；Angular production build 成功 |
| Controlled browser tests | 上述命令的 `-Action TestBrowser`；外层 cwd 为 workspace root；exit 0，Chromium，1 worker | `10/10` 通过；Playwright 拦截 Flagsmith/API 路由，使用本机受控前端服务，不是 live provider/targeting/rollout/propagation 证据 |
| Skill repository static validator | `node scripts/validate-skill.mjs` 仍为 exit 1 | 唯一失败仍是既有中文对比文档触发 English-only 检查；本次未修改该文件 |

以上结果 supersede 本记录前文“应用构建与单元测试 not-run”的预检快照，但只证明技术 POC 中这些受控用例。未对副本实施新业务行为、初始代码生成或既有非空源文件维护；A01–A15 live Flagsmith、Task13 人工/App/client/platform 关卡仍未运行。副本不代表真实业务应用。

### 追加后的缺口与下一步

- Task13 的技术 POC 单元/构建/受控浏览器子范围已执行；源应用没有具体的新增业务行为或维护验收范围，因此没有做任意代码改动。若要用它验证代码生成/既有文件维护，需要提供或确认这次要实现的行为。
- Live Flagsmith 验收须由有权限的操作者提供/配置两个专用本地 Project、Environment、密钥并确认可操作；不会读取/复制其他环境密钥，也不会访问云端。
- 人工、当前 App 原生入口、客户端和平台操作仍须各自的实际参与者/环境/授权。Task14 全量矩阵核对与最终 parity 结论尚未完成。

## 当前优先目标：本地脚手架可复制（2026-10-19）

用户明确表示当前更需要脚手架 ready，不认为真实应用展示演练重要。此次按 ready-to-use **本地候选**处理：不把 showcase、live Flagsmith、发布或 full parity 作为此本地交付的前置；不改写 Task13/14 的全量 parity 状态或伪称其已完成。

为了保留 `poc/flagsmith` 作为用户授权的本地练习副本，同时确保它不进入模板，已在唯一分发清单 [`distribution-manifest.json`](../docs/distribution-manifest.json) 显式登记 `poc/` 为排除项。

| 当前本地候选检查 | 结果 | 范围与限制 |
|---|---|---|
| 从当前工作树制作新候选 | maker copier `distribute_candidate.py --target ...` 返回 `status=copied`、exit 0；来源 HEAD `ee463901725ade1d0cab05261b8c875189fd229e`，dirty scope 92，复制 132 文件，129 个源库存项排除，0 findings | 候选在被 `.gitignore` 忽略的 `.venv/scaffold-ready-candidate-20261019/`，不进入 Git；候选不包含 `poc/` |
| 当前候选复核 | maker copier `--verify` 返回 `status=valid`、exit 0；同一来源 HEAD/dirty scope，132 verified，0 findings | receipt `scaffold-ready-candidate-verification.json` 在当前会话 session-local artifacts；不是跨机器证据 |
| 候选分发回归 | Python 3.13.15 counted runner，`test_distribution.py` 40 discovered/40 executed，0 skipped/failures/errors；`inputs_unchanged=true` | 覆盖精确 manifest、候选字节/文件哈希、候选内 Markdown 链接锚点、copied-only imports、排除边界和 Task12 防护回归。JSON/raw 结果 `scaffold-ready-distribution-tests.json/.txt` 保存在 session-local artifacts |
| 候选正式工件检查 | 候选 `check_artifacts.py --root <candidate>` exit 0，`status=empty`、checked 0、findings 0 | 当前无正式业务工件；`empty` 不是业务验收，也不是完整 Markdown 语义通过 |

本地 ready 判断仅表示：依据唯一 manifest 可复制的脚手架候选已有新鲜复制、逐字节校验和分发回归。它不是发布/推送授权，不证明 hosted CI、真实客户端/人工、业务应用接入、live Flagsmith，亦不关闭音频、PDF/PPTX、provider/billing/usage 或六仓 full parity。当前分支 `callentan-repository-skeleton`、HEAD `ee463901725ade1d0cab05261b8c875189fd229e`；本轮文档/manifest 修改未提交，`poc/flagsmith` 是未跟踪本地练习副本。

后续只读检查发现原始 Flagsmith 来源仓库的工作树出现更多 owner 修改；本会话未读取、复制或改动这些新增内容。隔离副本仍绑定原先固定提交 `beade3c39c3bbb63f14e9c9072e797e24fafc163`，而且已经从模板 manifest 排除，因此不影响本次脚手架候选。

## P1/P2 落地与独立 POC 副本（2026-10-19 16:42 后）

用户要求先按模板蓝图完成 P1/P2，再提供独立干净副本供 POC 使用。以当前[仓库蓝图](../docs/design/repository-blueprint.md)所列的 38 个历史首版路径做核对：主脚手架中 38/38 均已存在；当前可交付内容以增强后的唯一 [`distribution-manifest.json`](../docs/distribution-manifest.json) 为准，共 132 个文件，而不是另造 38 文件模式。manifest 排除 `poc/`，所以 Flagsmith 演练不会被混入脚手架。

最终独立副本放在用户提供的 POC 根目录中，与 `flagsmith/` 同级为 `agent-native-scaffold/`；两者不合并，也不位于脚手架工作树。它是 manifest 的 clean snapshot，不含 `.git`、虚拟环境、POC app、依赖树或本地密钥/配置。旧 P1/P2 的 `docs/agent-support.md` 因含真实历史客户端观察而仍按 manifest 明确排除；README/AGENTS 保留通用活动入口。故**主工作树 38/38 蓝图路径齐备**；portable enhanced copy 遵循 manifest 的隐私边界，不能称为“历史 38 路径逐一原样复制”。

首次在工作树内运行 copier `--target` 时返回 `SOURCE_SCOPE_CHANGED`，未产生成功 copy receipt。核对 copier 实现后，根因为目标目录位于源 Git 工作树的 `poc/` 排除区：创建目标改变了 copier 在写入前后核对的 Git dirty/inventory scope；临时 helper 也位于该源树内。失败流程留下的 132 文件副本后来通过只读 `--verify`，但嵌套的 `_templates` 使主工作树正式工件检查器把这些空白表单误识为正式工件，结果变为 `invalid`。因此用 copier 在工作树外的授权 POC 根目录创建最终 sibling copy，并删除仅由本会话创建的工作树内重复副本；Flagsmith POC 副本和源码仓库均未删除或修改。最终主工作树的正式工件检查恢复为 `empty`。

最终 copy receipt 与 verify receipt 均在本会话 session-local `files/`：来源 HEAD `8406fad1e40555b5a5351801343251e7d1ef5e32`；copy 为 132 文件、261 exclusions、0 findings，exit 0，SHA-256 `3265FD9AF4FA187A864FE0E73B5A0C6618323A406CB61AD2AA5DA8EAA7A796E9`；copy 后 verify 为 132 文件、129 exclusions、0 findings，exit 0，SHA-256 `AF0FC71100F421695EC4BCBC480E1559F9AA082EFE2AAEFC7842C7FA5F26260B`。前一份工作树内重复副本的 `poc-scaffold-final-verification.json` 是中间结果，已由外部 sibling 的最终 verify receipt supersede。当前本地 `check_artifacts.py --root <maker root>` 为 `empty`，checked 0、findings 0。`test_distribution.py` 为 40/40、0 跳过/失败/错误，`inputs_unchanged=true`；receipt `poc-copy-final-distribution-tests.json` 的 SHA-256 `057E45CB836BEC9EF6BDB8B3491BB1E6948F36806304F8FBF467DA98323372C0`。这些 session-local 报告不是跨机器证据。

最终副本位于用户提供 POC 根目录的 sibling `agent-native-scaffold/`，与 `flagsmith/` 分开；未初始化 Git、未纳入脚手架工作树，也未改变 Flagsmith 来源 repo 当前的未提交 Docker Compose 工作。它是可供本地 POC 采用的干净模板快照，不是自动应用到 Flagsmith repo 的合并。若将副本移到其他位置、初始化 Git、把模板合入 Flagsmith，或交付给其他维护者，须按新目标路径与基线重新核验；本地 receipt 不构成发布授权。
