# 架构与决策

本目录记录必要的结构、约束及取舍。当前尚无已确认项目架构，不从目录名推导服务或代码分层；[业务上下文](../domain-model/README.md#contexts)不必与技术组件一一对应。

<a id="building-blocks"></a>
## 架构构件 ABB（按需）

当结构、职责、接口协作或设计约束需要单独说明时，使用 [ABB 表单](../_templates/items/architecture-building-block.md)，放入 `architecture\ABB-NNN-<slug>.md`。

- 记录上游 REQ/SR 或明确任务依据、相关业务边界与规则链接。
- 区分负责与不负责的事项、事实所有者、依赖与交互方向；设计假设和未决项不能写成业务事实。
- 说明设计约束的来源、备选方案与取舍，以及需要怎样验证。
- 需要独立核对的设计约束使用带所属工件的稳定标识和锚点，例如 `ABB-NNN-VC-01`、`abb-nnn-vc-01`。已有约束直接引用，避免再写一份。

设计验证按[验证层次](../verification/README.md#layers)选择合适的检查，不自动等同于 REQ 业务验收或 SR 软件行为验证。不为每次修改强制新建 ABB。

<a id="decisions"></a>
## 架构决策 ADR（按需）

只有真实决策需要保留背景、备选方案和历史时，才使用 [ADR 表单](../_templates/items/architecture-decision.md)。在创建第一份 `architecture\decisions\ADR-NNN-<slug>.md` 时再建立 `decisions\`，不预置空目录或虚假决策。

提案、已接受和已取代要区分。记录业务边界、上游依据、选择理由、代价、验证需要和确认依据；没有获授权者的决定时保持提案或未决。后续改变决定时追加新记录并链接前后关系，保留当时的依据与取舍，不重写旧历史。

## 维护入口

真实 ABB/ADR 创建后在这里添加链接。普通工作进度写[开发日志](../logs/README.md)，规则或需求变化按[语义影响检查](../verification/README.md#change-impact)复核设计及旧结果；不把日志当设计决策来源的替代品。
