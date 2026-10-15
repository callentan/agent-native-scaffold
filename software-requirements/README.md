# 软件要求

SR 记录软件应怎样表现，包括边界、错误、接口约定和软件验收。它不是产品目标说明，也不是实施任务清单；上游依据是实际 REQ/UC/INV、相关 CAP/QAS 或明确维护请求。派生活动使用 [specify-feature](../.github/skills/specify-feature/SKILL.md#derive-requirements)，不是强制工件流水线。

<a id="sr-writing"></a>
## 从依据到软件验收

1. 读取[业务需求](../stakeholder-requirements/README.md)、[实际领域资料](../domain-model/README.md#optional-forms)或明确任务，核对范围、完整验收身份、原文与基线。UC 提供路径，INV 必须有源规则，CAP/上下文提供职责，QAS 提供有来源的质量判据；这些是适用输入，不要求每次补齐全部工件。
2. 需要独立规格时复制 [SR 表单](../_templates/items/software-requirement.md)，放入 `software-requirements\SR-NNN-<slug>.md`。按[元数据约定](../domain-model/README.md#artifact-metadata)在项目/上下文明确后填写 scope、身份及上游，初始为 draft。纯维护可沿用现有任务，不强建 REQ、SR 或 US，也不自动迁移旧资料。
3. 写清正常/允许、边界、拒绝、错误与禁止副作用的可观察行为；不把条件不满足与执行错误混为一谈。缺来源、未确认的 INV 或歧义只能产生候选/问题，不成为强制要求。协议、并发、资格失效和指标未定时分别记录缺口，不补技术默认值。
4. 对每项软件验收分配完整 ID 和固定 ASCII 锚点，例如 `SR-NNN-AC-01` 与 `sr-nnn-ac-01`。规则正文仍引用其来源，只补软件层可观察的判定条件，不在多处复制规则。
5. 在实施前按[覆盖检查](../verification/README.md#coverage-check)为验收项寻找或规划软件行为型 VT。边界或错误场景未覆盖时保留缺口，不能用一项正常路径检查代表全部行为。

<a id="traceability"></a>
## 引用与变更

新 SR 的 `upstream` 独占声明关系，使用来源的完整 `scope/id#anchor`；正文说明推导理由、来源原文/基线的阅读导航，不再维护第二张映射或内容状态表。仅写无所属工件的 `AC-01` 不足以定位。旧轻量来源与独立请求没有元数据时保留普通链接，身份缺失明确列出，不发明编号以便解析。

VT 直接引用 SR 验收项，不要求经过 US。查询某个 REQ 的下游时搜索 SR 的上游字段；查询某个 SR 的验证时搜索 VT 的目标字段，不再手工维护两套相反关系。

需求确认、软件实施和实际运行分别取证。表单完整、schema-valid 或上游写着 Approved 都不证明责任人确认；形成可实施要求前核对实际决定及适用基线。没有来源身份时可在获准笔记中整理已知行为，但不能宣称正式追溯完整。

```markdown
[SR-NNN-AC-01](SR-NNN-<slug>.md#sr-nnn-ac-01)
```

以上 ID 和链接只是占位语法。真实编号与锚点在工件创建时分配，改名同步修正链接，撤销验收保留依据且不复用 ID。语义变化按[影响检查](../verification/README.md#change-impact)处理，不因为链接仍可打开就沿用旧结果。

<a id="requirements"></a>
## 正式要求入口

当前尚无正式 SR。按需添加文件链接；业务验收仍归 REQ，软件验收归 SR，结果从 VT 和原始记录读取。
