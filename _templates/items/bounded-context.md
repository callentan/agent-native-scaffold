---
schemaVersion: 1
id: CTX-NNN
kind: bounded-context
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# CTX-NNN：待填写上下文

> 可选空表单，不是服务划分决定。先读[上下文指引](../../domain-model/README.md#contexts)及[元数据约定](../../domain-model/README.md#artifact-metadata)。按需复制到 `domain-model\CTX-NNN-<slug>.md`；确认并替换 `PROJECT/CTX-NNN`、ID、标题和锚点，修正相对链接，保留原有内容后删除本提示。一个上下文足够时继续使用原 README。

<a id="basis"></a>
## 来源与认识边界

- 已知业务事实及来源定位、日期或版本：待填写。
- 推导候选及推导依据：待填写。
- 未决问题及需要谁确认：待填写；上下文不默认对应一个服务或仓库。

可解析上游只在 frontmatter 声明，正文说明来源与当前责任判断。

<a id="responsibilities"></a>
## 职责与不负责事项

| 责任信息 | 内容 |
|---|---|
| 负责的业务能力与决定 | 待填写 |
| 明确不负责的事项 | 待填写 |
| 业务责任人与权限依据 | 待填写 |
| 关键术语及在此边界内的含义 | 待填写；与其他上下文不同的含义要说明 |
| 相关概念、规则与不变量的含义 | 待填写；链接原文，不复制规则 |

<a id="owned-facts"></a>
## 拥有并维护的事实

| 事实及业务含义 | 可改变它的业务动作 | 约束与来源 | 未决的生命周期问题 |
|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 |

<a id="consumed-facts"></a>
## 使用但不拥有的事实

| 提供方 → 本上下文 | 所用信息及含义 | 事实所有者 | 使用条件、时效和失败约定的来源 |
|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待确认；消费信息不授予修改权 |

对外提供的信息在[定向交换](../../domain-model/README.md#exchanges)或实际 context map 中说明方向；这些导航不是另一套上游映射。

<a id="questions"></a>
## 边界争议与变化

- 已知事实与候选边界之间的差异：待填写。
- 跨上下文政策、词义或归属缺口；责任人与 BL 导航：待填写。
- 旧新基线、变更依据及影响：待填写；未经确认不移动已有工件。
