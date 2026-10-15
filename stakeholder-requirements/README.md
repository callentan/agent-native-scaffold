# 产品说明与业务需求

本目录承接 PRD：产品目标、用户、范围和约束在此维护；每个 REQ 只记录一项业务需求及其业务验收。领域规则归[领域模型](../domain-model/README.md)，软件行为归[软件要求](../software-requirements/README.md)，不把整份 PRD 当成一条 REQ。

<a id="product"></a>
## 产品说明（待填写）

| 内容 | 已确认信息或待确认问题 |
|---|---|
| 产品目标、要解决的问题与价值 | 待填写 |
| 用户、使用者及相关干系人 | 待填写 |
| 业务成功的观察依据 | 待填写，不能预填已达成 |
| 范围内事项 | 待填写 |
| 范围外事项 | 待填写 |
| 业务、合规及交付约束 | 待确认 |
| 事实来源、确认人和日期 | 待填写 |
| 未决问题、影响及需谁确认 | 待填写 |

本栏未填不是“没有限制”。缺少影响行为的事实时先澄清；只影响以后工作的未决项可保留，并说明不阻塞当前任务的依据。

<a id="req-writing"></a>
## 编写一项 REQ

1. 查找现有需求与[领域事实](../domain-model/README.md#sources)，确认来源、当前状态、适用上下文和规则。不要把提案自动改成已批准。
2. 需要新需求时使用 [REQ 表单](../_templates/items/stakeholder-requirement.md)，放入 `stakeholder-requirements\REQ-NNN-<slug>.md`。`NNN` 与 `<slug>` 是占位，编号在创建真实工件时分配。
3. 写一项业务需要、适用范围、非目标和可观察的业务验收。引用领域规则，不重复维护其数值或全文；验收说明在什么条件下如何判断目标满足。
4. 每个验收项使用完整 ID 与稳定 ASCII 锚点，例如 `REQ-NNN-AC-01` 对应 `req-nnn-ac-01`。多个验收项逐项编号，调整措辞保留 ID；撤销项保留变更依据，旧号不复用。
5. 按[验证指引](../verification/README.md#coverage-check)从全部验收项查找业务验收型 VT。SR 的测试通过不能自动证明 REQ 业务验收通过。

正式文件间的链接形式如下，仅为语法示意，不是现有需求：

```markdown
[REQ-NNN-AC-01](REQ-NNN-<slug>.md#req-nnn-ac-01)
```

SR 自己保存上游 REQ 链接，VT 自己保存目标链接；需要查下游时反向搜索，不在 REQ 再维护一套映射或验证结果。独立维护请求可以直接作为任务依据，不必制造 REQ。

<a id="domain-inputs"></a>
## 采用可选领域输入

来源较多时可引用已有 SD/CTX、CAP、UC、RULE、INV 与 QAS；表单和默认落点见[领域工件指引](../domain-model/README.md#strategic-forms)。它们不是 REQ 的强制前置链，轻量 README 中的已有规则仍是有效来源。REQ 说明业务需要和验收，领域事实及规则正文仍回原所有者读取。

新 [REQ 表单](../_templates/items/stakeholder-requirement.md)用 frontmatter 声明身份、scope、内容状态和上游；正文只说明来源为何支持本需求。按[元数据约定](../domain-model/README.md#artifact-metadata)替换占位，不自动转换旧 REQ，不改已有验收 ID/锚点。没有元数据的旧来源保留普通链接，不编造 canonical key。需求未决与业务来源缺口要明确到责任人，不能以填写齐全代替确认。

本任务确有用途或风险依据时，引用[可选 Intended Use/风险控制资料](../domain-model/README.md#governance-forms)及其原来源/决定基线，产品说明不另抄用途或风险正文。未知环境、范围限制或负责政策阻塞相关需求确认；候选变更先按[用途修订](../.github/skills/define-requirements/SKILL.md#intended-use)列影响，不默认新产品声明或法规分类。

<a id="quality-inputs"></a>
## 质量属性输入

需要独立质量要求时使用 [QAS 表单](../_templates/items/quality-attribute-scenario.md)，放入 `stakeholder-requirements\QAS-NNN-<slug>.md`；不把质量指标另存到领域规则或产品说明中。

- 分开填写刺激源、刺激、环境、对象、响应和响应度量，说明每项来源与适用范围。
- 度量要有可观察标准、单位/统计口径或其他判定方式及其依据。没有数值或方法时保留 `draft`、具体缺口和需谁确认，不补常见 SLA、监管分类或平台保证。
- QAS 的独立判据使用其 owner-qualified 验收 ID/锚点；[业务场景或 VT](../verification/README.md#domain-scenarios)引用具体条目。非行为关注点只保留规格与待补输入，不强造可执行场景。
- 要求基线变化时复核 UC、设计与验证的语义影响，原执行基线及结果保留。QAS 填写或 schema 校验不代表质量验收通过。

<a id="requirements"></a>
## 正式需求入口

当前尚无正式 REQ。创建真实需求后在这里追加其文件链接；正文、验收项和状态以各 REQ 为准，覆盖缺口见[验证索引](../verification/README.md#coverage-index)。
