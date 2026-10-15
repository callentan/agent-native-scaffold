---
schemaVersion: 1
id: REQ-NNN
kind: stakeholder-requirement
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# REQ-NNN：待填写

> 空白表单，不是已确认需求。先读[业务需求指引](../../stakeholder-requirements/README.md#req-writing)及[领域输入约定](../../stakeholder-requirements/README.md#domain-inputs)，按需复制到 `stakeholder-requirements\REQ-NNN-<slug>.md`。确认并替换 `PROJECT/CTX-NNN`、占位编号、标题与锚点，保留已有内容、核对实际落点的相对链接后删除本提示。

<a id="basis"></a>
## 来源依据

| 字段 | 内容 |
|---|---|
| 提出者、来源及可定位依据 | 待填写 |
| 记录日期与来源基线 | 待填写；没有确认不得写已批准 |
| 所属产品目标、用户或干系人 | 待填写：引用产品说明，不另写一份 PRD |
| 领域输入的业务含义与来源解释 | 待填写：适用的概念、上下文、CAP/UC、RULE/INV 或 QAS；原文链接只作导航，不适用需说明 |

身份、scope、内容状态及可解析上游只在 frontmatter 维护，字段依[元数据约定](../../domain-model/README.md#artifact-metadata)。正文不再维护另一份关系/状态表；未元数据化的旧领域来源仍用普通相对链接。确认声明需真实来源与被确认基线，不能由表单预填。

<a id="business-need"></a>
## 业务需要与范围

- 一项业务需要及理由：待填写。
- 适用对象、前提与范围：待填写。
- 非目标与约束来源：待填写。
- 未决事实及对本需求的影响：待填写。

规则正文留在领域模型；这里引用规则并说明业务需要，不重复维护规则数值或全文。

<a id="acceptance"></a>
## 业务验收

逐项复制以下块，使用带所属 REQ 的唯一 ID 和固定 ASCII 锚点，不能只有 `AC-01`。所有内容待填写，ID 示意不是正式验收。

<a id="req-nnn-ac-01"></a>
### REQ-NNN-AC-01：待填写

| 项目 | 内容 |
|---|---|
| 业务前提与场景范围 | 待填写 |
| 业务动作或触发 | 待填写 |
| 可观察的业务结果与判定标准 | 待填写 |
| 边界、例外或禁止的结果 | 待填写；未定义部分保持未决 |
| 相关规则/上下文及确认来源 | 待填写：ID、稳定链接与依据 |

此处不记录执行结果。VT 保存其业务验收目标，按完整 ID 反向查找；缺少 VT 或未执行都不是通过，软件检查通过也不自动证明本项成立。

<a id="changes"></a>
## 变更与未决项

| 日期与基线 | 改变或待确认的内容 | 来源、理由与确认状态 |
|---|---|---|
| 待填写 | 待填写 | 待确认 |

验收项撤销或改名时保留依据与历史引用，不复用旧 ID；变化后检查下游软件要求、设计与验证的语义影响。
