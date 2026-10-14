# 软件要求

SR 记录软件应怎样表现，包括边界、错误、接口约定和软件验收。它不是产品目标说明，也不是实施任务清单；上游依据是已有 REQ 或明确的维护请求、issue 等任务。

<a id="sr-writing"></a>
## 从依据到软件验收

1. 读取[业务需求](../stakeholder-requirements/README.md)或明确任务，记录可定位的来源与完成条件。涉及业务时同时读取[领域规则和上下文](../domain-model/README.md)，缺失行为事实先确认。
2. 需要独立规格时复制 [SR 表单](../_templates/items/software-requirement.md)，放入 `software-requirements\SR-NNN-<slug>.md`。纯维护可沿用现有任务，不强建 REQ、SR 或 US。
3. 写清正常行为、前置条件、边界、错误处理和禁止的副作用；记录上下文责任、输入输出、接口对方及未决约定。没有确定的实现或接口不要预填。
4. 对每项软件验收分配完整 ID 和固定 ASCII 锚点，例如 `SR-NNN-AC-01` 与 `sr-nnn-ac-01`。规则正文仍引用其来源，只补软件层可观察的判定条件，不在多处复制规则。
5. 在实施前按[覆盖检查](../verification/README.md#coverage-check)为验收项寻找或规划软件行为型 VT。边界或错误场景未覆盖时保留缺口，不能用一项正常路径检查代表全部行为。

<a id="traceability"></a>
## 引用与变更

SR 是上游关系的维护位置：写明 REQ 的具体验收项，或明确任务的完成条件与来源。仅写无所属工件的 `AC-01` 不足以定位。

VT 直接引用 SR 验收项，不要求经过 US。查询某个 REQ 的下游时搜索 SR 的上游字段；查询某个 SR 的验证时搜索 VT 的目标字段，不再手工维护两套相反关系。

```markdown
[SR-NNN-AC-01](SR-NNN-<slug>.md#sr-nnn-ac-01)
```

以上 ID 和链接只是占位语法。真实编号与锚点在工件创建时分配，改名同步修正链接，撤销验收保留依据且不复用 ID。语义变化按[影响检查](../verification/README.md#change-impact)处理，不因为链接仍可打开就沿用旧结果。

<a id="requirements"></a>
## 正式要求入口

当前尚无正式 SR。按需添加文件链接；业务验收仍归 REQ，软件验收归 SR，结果从 VT 和原始记录读取。
