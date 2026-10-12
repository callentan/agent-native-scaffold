# 独立仓库与生成项目蓝图

本文所有目录与命令都是**设计示意**。本轮没有创建这些程序、配置或业务模板。

## 1. 两种仓库不能混在一起

| 仓库 | 生命周期 | 拥有的内容 |
|---|---|---|
| `agent-native-scaffold` | 作为框架独立版本发布 | 契约、检查器、skills、模板、适配器、迁移与评估 |
| 生成或接入的业务仓库 | 自己的产品版本和交付节奏 | 业务事实、需求、代码、测试、项目配置和被锁定的框架版本 |

框架不是业务应用的生产运行时依赖。卸载开发工具后，应用仍应能按自己的构建流程运行；不能把 agent 控制层混入业务服务。

## 2. 建议的框架仓库结构

```text
agent-native-scaffold/
  README.md
  AGENTS.md                         框架自身也遵守 agent-ready 约定
  CONTRIBUTING.md
  docs/
    architecture/
    decisions/
    guides/
    reference/
  schemas/                          唯一权威契约定义
    project.schema.json
    task.schema.json
    evidence.schema.json
    implementation-report.schema.json
  src/agent_scaffold/               一个包，不是多个微服务
    cli/
    context/
    artifacts/
    execution/
    verification/
    adapters/
      agents/
      providers/
  skills/                           通用活动，而非企业角色
    orient/
    specify-change/
    implement-task/
    verify-change/
    recover-task/
    assess-impact/
  profiles/
    methods/
      basic/
      ddd-v-model/
    assurance/
      standard/
      regulated/
  stacks/
    dotnet-service/                 命令、依赖规则、模板、结果解析
  integrations/
    azure-devops/
    github/
  migrations/
  examples/                         合成、可公开的黄金样例
    minimal-service/
    ddd-service/
    legacy-import/
  tests/
    unit/
    contracts/
    golden/
    integration/
    evals/
  pyproject.toml
  <依赖锁文件>
```

这是完整方向，不要求首个 commit 就填满所有目录。MVP 只实现一个 agent、一个托管平台和一个技术栈包；其他适配器先保留设计边界，不建空壳冒充支持。

## 3. 建议的业务工程结构

```text
sample-service/
  README.md                         人类入口、运行方式与业务概述
  AGENTS.md                         agent 导航，短而稳定
  agent.yaml                        项目身份、方法、技术栈、命令与知识源
  agent.lock.json                   框架、方法包、规则、模板和输入版本
  .agent/
    policies/                       项目级受保护规则
    adapters/                       生成的客户端映射与能力声明
    context/                        自动生成的索引/上下文清单
  docs/
    product/
    architecture/
    decisions/
    runbooks/
  specs/                            basic 方法的权威规范与 AC
  tasks/
    TASK-<id>.md                    意图、范围、依赖与完成条件
  src/
  tests/
  .agent-state/                     忽略入库；运行状态、缓存、局部日志
```

DDD 方法包可以沿用原工程的 `software-requirements/`、`user-stories/`、`architecture/`、`verification/` 和 `src/tests/`。这些路径通过 mapping 声明，不为了统一好看而复制一套 `specs/`、`tests/`。

领域知识可通过只读 submodule、导出的快照或授权连接器提供。首版兼容现有 submodule，但新项目不必强制维护 prompts/templates/domain-model 三层 Git 子模块。

### 客户端入口

`AGENTS.md` 是通用导航。若所选客户端需要 `.github/copilot-instructions.md`、`CLAUDE.md` 或特定 skill 安装路径，由 adapter 生成薄入口并指向同一规则来源。

不能假设任何客户端会自动扫描 `.agent/`。适配器必须依据所支持版本验证实际 discovery 行为，并记录“已验证/未验证/不支持”，而不是复制文件后宣布兼容。

## 4. 项目清单应声明什么

`agent.yaml` 的概念模型：

| 字段组 | 必须表达的内容 |
|---|---|
| Identity | 稳定项目 ID、仓库身份、所有者、工程类型 |
| Method / Assurance / Stack | 启用的配置及对应版本 |
| Sources | 来源仓库、固定 commit、挂载根、仓库内路径、读写性质 |
| Artifact mapping | 工件种类、位置、ID 和状态解析方式 |
| Commands | 安装、启动、build、lint、unit、integration、contract、smoke 等稳定命令标识 |
| Environment | SDK、容器、服务、端口分配、允许读取的凭据引用 |
| Boundaries | 业务代码写集合、受保护文件、只读源、允许网络范围 |
| Delivery | 目标平台、交付为本地变更还是待审 PR、所需审批 |
| Retention | 状态、日志、证据位置与保留要求 |

清单保存凭据引用名称，**不保存凭据值**。它可以声明策略需求，但实际权限上限仍由组织与执行环境控制。

manifest 与 lock 都需要 `schemaVersion`。schema 不支持、required 字段缺失、版本不兼容、路径越界或同名 ID 冲突时，必须明确报错。

## 5. CLI 是稳定的 agent 接口

以下使用暂定命令名 `ans`；不是可安装或可运行的现有命令。

| 设计命令 | 职责 | 副作用边界 |
|---|---|---|
| `ans init --dry-run` | 展示将生成的文件、参数、依赖和冲突 | 无写入 |
| `ans init` | 在明确目标目录生成工程配置及模板 | 仅批准的本地文件；不顺带创建或推送远端仓库 |
| `ans doctor` | 验证路径、版本、运行时与权限能力 | 默认只读；安装依赖需另行授权 |
| `ans context --task <id>` | 解析限定任务的事实、规则和依赖 | 写入可再生上下文缓存 |
| `ans check` | 校验 schema、引用图、前置条件、审批新鲜度 | 只读检查并输出报告 |
| `ans run --task <id>` | 驱动批准范围内的托管任务 | 仅隔离工作区及授权发布通道 |
| `ans resume --run <id>` | 核验检查点后继续 | 不重复已确认的外部副作用 |
| `ans verify --task <id>` | 执行并解析批准的验证集合 | 仅隔离的测试环境 |
| `ans report --run <id>` | 导出审阅摘要和证据位置 | 不改变审批或业务状态 |
| `ans upgrade --plan` | 比较版本与文件所有权，产生迁移计划 | MVP 默认仅规划；应用迁移需批准 |

每个命令支持机器可读输出，统一字段至少包括：

```json
{
  "schemaVersion": "1",
  "status": "blocked",
  "code": "SOURCE_UNAVAILABLE",
  "message": "The pinned domain source cannot be read.",
  "details": [],
  "retryable": false,
  "nextAction": "Restore approved read access."
}
```

标准输出在 JSON 模式只能包含结果；进度写入标准错误或日志。不能通过解析自然语言“看上去成功”来判断状态。

退出语义建议：`0` 为该命令成功，`1` 为检查/验收失败，`2` 为配置或输入错误，`3` 为缺权限/缺审批/缺依赖等阻塞，`4` 为超时或预算耗尽。取消与信号退出保留平台语义，并在可写状态中记录原因。

工具失败、业务验证失败、尚未执行必须分别表达。成功的 `report` 命令不表示报告对应的任务成功。

## 6. 文件所有权与升级

每个生成文件在安装清单中带有所有权类别和基线摘要：

| 类别 | 例子 | 升级规则 |
|---|---|---|
| Managed | 生成的客户端入口、schema、适配元数据 | 基于旧基线做比较；检测手改，不能直接覆盖 |
| Seed-once | 初始业务代码、首次 README、初始测试 | 创建后归项目；框架升级不重新生成 |
| Project-owned | 业务规范、领域模型、实际代码、任务 | 只通过正常业务任务修改 |
| Derived | 索引、矩阵、上下文包、实现摘要 | 从权威输入重新生成；记录生成器版本 |
| Runtime | 缓存、临时环境、局部日志和运行 DB | 不作为业务源代码；按保留策略处理 |

升级采用旧模板基线、本地状态和新模板三方比较，先输出计划。冲突是需要解决的结果，不是“跳过后仍升级成功”。

对已有工程的改名、删除、schema 破坏性迁移必须显式展示。回滚通过已记录的迁移与 Git 变更进行，不能递归删除工作区或丢弃原有改动。

## 7. 发布单元和版本锁

独立仓库统一发布经过组合验证的：

```text
核心 CLI + schemas + skills + 方法包 + 技术栈包 + 校验器 + 迁移
```

可以拆分分发包，但首先共用发布清单和兼容矩阵，避免消费方自行组合未经验证的六个 HEAD。

业务 lock 记录实际版本、commit/digest、包来源和 profile 组合；生产应用的依赖仍保留在其原有包管理器锁文件中。

prompt 只是文本，不意味着修改一定低风险。行为变化需要回归评估；改变契约或门禁需要适当版本升级和用户确认。固定 prompt 版本也不能保证模型输出确定性，模型/工具版本要一并记录。

## 8. 从现有仓库接入

### 阶段一：只读映射

读取现有 `bc-config.yaml`、`.gitmodules`、工件目录和执行命令，生成接入差异报告。保留原路径、编号与 Git 历史。

检查真实来源路径、跨项目 URL、版本锁、状态映射、外部 ADR 可访问性。未决项进入阻塞或待确认列表。

### 阶段二：旁路验证

保留现有流程，新增只读 checker 与证据报告。先使用真实工程收集误报和漏报，再决定哪些规则成为强制门。

不把“检查器新增要求”自动解释成“现有业务事实需要改写”。

### 阶段三：限定托管

选择一个已批准、无未决外部契约的交付切片，使用隔离工作区完成代码与测试变更。通过后再扩大任务类型与仓库范围。

任何历史工件状态无法映射的情况都需要明确处理，不把未知状态默认为 Approved。

## 9. 独立仓库建立方式

完成 P0 评审后，再由用户指定托管位置、仓库名、可见性、许可证和所有者，建立独立仓库。

本目录的研究材料不应不加区分地原样公开。正式仓库应迁入通用设计，重写或经授权复用模板，使用合成数据和去组织化的示例；原有业务源码留在原仓库。
