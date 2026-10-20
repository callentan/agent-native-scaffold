---
schemaVersion: 1
id: SWAS-NNN
kind: architecture-specification
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# SWAS-NNN：待填写

> 可选架构规格汇编，不是架构批准、风险接受或发布证明。先读[SWAS 指引](../../architecture/README.md#architecture-specifications)及[元数据约定](../../domain-model/README.md#artifact-metadata)，按需复制到 `architecture\SWAS-NNN-<slug>.md`。项目/上下文明确后替换占位并删除本提示，核对实际落点的相对链接。

<a id="basis"></a>
## 汇编范围与原始基线

| 字段 | 内容 |
|---|---|
| 目的、使用范围与非目标 | 待填写 |
| 本次实际读取范围、源版本/摘要基线 | 待填写；原文件不可读或基线未知须逐项说明 |
| 记录日期与编制者 | 待填写；内容状态及确认声明归 frontmatter |
| 完整性限制与必要决定 | 待填写；缺源时只能交付部分说明 |

frontmatter 的 `upstream` 声明实际工件引用；正文只解释与导航来源，不再维护一份关系或批准表。已有派生 model 可作入口，但须回原文核对基线；没有 model 不制造导出结果，也不回写只读领域源。

<a id="perspectives"></a>
## 架构说明

| 关注面 | 实际原文/基线的导航及必要解释 | 缺项与受阻结论 |
|---|---|---|
| 业务：目标、上下文、能力与责任 | 待填写领域/REQ 来源 | 待填写 |
| 逻辑：构件、依赖、接口与决策 | 待填写 ABB/ADR 来源 | 待填写 |
| 运行：场景、参与者、事件与失败边界 | 待填写 UC/SEQ/接口来源 | 待填写 |
| 部署：实际环境、节点/进程分配与约束 | 待填写现有部署/环境来源；没有则不可用 | 待填写 |

逻辑构件不推出部署拓扑。语言、框架、端点、容器、安全分类和服务保证只有实际选定或提供时才引用；未知项不补成“常规架构”。

<a id="views"></a>
## 九类来源视图的完整性

沿用[model 契约](../../.github/contracts/README.md)的九个视图语义，但本表不是第二份 model：只保留可读性、原文导航/基线和缺口，不复制领域正文、canonical 关系清单或实际结果。

`available` 表示所需来源可读完整，至少有一处可核对引用；`partial` 表示已有部分引用且有具体缺口；`unverified` 表示来源缺失、不可读或基线不能核实，不能声称已取得引用。三者均不等于 `pass`、批准或已发布。缺必需主输入是输入错误，不伪装成可选视图缺失。可选视图缺失仍保留该行；不适用也须有范围依据，不能仅以空白排除。

| 视图 | 本次可读性 | 已核对原文与基线的导航 | 具体缺口/适用范围 |
|---|---|---|---|
| requirements | unverified | 尚未提供 | 待补 REQ/SR/UC 的实际位置与基线 |
| stories | unverified | 尚未提供 | 待核实是否采用 US；未采用不妨碍直接 SR/VT |
| architecture | unverified | 尚未提供 | 待补 ABB/ADR/集成依据 |
| sequences | unverified | 尚未提供 | 待补 SEQ、参与者和契约 |
| verification | unverified | 尚未提供 | 待补计划/实际报告及各自基线；文件存在不等于执行 |
| quality | unverified | 尚未提供 | 待补 QAS、响应度量与测量依据 |
| governance | unverified | 尚未提供 | 待核实适用治理来源与决定依据 |
| risk | unverified | 尚未提供 | 待核实适用风险/控制来源；不自行评估可接受性 |
| release | unverified | 尚未提供 | 待补版本/变更控制与实际发布记录 |

采用真正的 model 数据时，`artifactRefs` / `evidenceRefs` / `gaps` 的形状以现有 schema 为准，`unverified` 用空引用和具体 gap，`partial` 保留已核对引用及缺项。这里的阅读导航不代替数据校验，也不声称有导出器。

<a id="review"></a>
## 审阅、风险与验证限制

- 原要求、设计约束和实际 VT 的阅读入口：待填写；结果回原记录，不汇总成“全部通过”。
- 未确认的决策、缺失视图及需谁补什么：待填写。
- 旧新基线差异、受影响的图/要求/验证及待复核入口：待填写。
- 本次交付格式与实际检查：待填写；本表只提供 Markdown，不提供 PDF/演示 renderer，未执行的导出标 `not-run`。

内容自称 Approved、目录齐全或图能渲染都不能认证批准。只有可定位且针对本基线的实际决定才能形成确认声明；缺风险、发布或验证来源时不能编造结论。
