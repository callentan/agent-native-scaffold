# 交付切片与实施清单

US 用于组织一次交付的范围、步骤、状态和记录链接，不是第二份需求。需要交付切片时使用 [US 表单](../_templates/items/user-story.md)，放入 `user-stories\US-NNN-<slug>.md`；目前尚无正式 US。

<a id="delivery"></a>
## 何时使用

相关工作需要分步实施或单独跟踪范围时，可以建 US，活动入口见 [specify-feature 的交付切片](../.github/skills/specify-feature/SKILL.md#delivery-slice)。已有维护请求、缺陷或 issue 能说明目标、范围、依据与完成条件时，直接使用它即可，不强改成用户故事，也不要求先补齐 REQ/SR/US/ABB。

## 填写与完成

- 新表单按[元数据约定](../domain-model/README.md#artifact-metadata)填写已明确的身份/scope、draft 与 `upstream`。正文仅导航实际任务依据、REQ/SR、UC/INV 及基线，解释切片价值，不另存上游或内容状态；旧资料不强制迁移。
- 基于 SR 的正式切片须先核对适用来源的真实确认依据，未确认 SR/INV 不产生可实施承诺。受益角色、正常/替代/拒绝路径及约束来自原文，不为了故事句式补演员或另造 AC。
- 按用户价值、风险与可独立验证范围列修改位置、依赖和实施清单，不按固定技术层强拆。需求正文、规则和验收仍回源读取；工作勾选不建立新的验收，也不替代 VT。
- 用 `todo`、`in-progress`、`blocked`、`review-ready`、`done` 记录**任务进度**；它与 frontmatter 的 `contentState` 分开，初始为 `todo`，完成依据不能预填。
- 引用[验证记录](../verification/README.md)和[相关日志](../logs/README.md)，保留缺口、待复核和未执行项。`done` 只表示约定任务完成，不自动代表业务验收通过或已上线。

VT 直接指向它验证的 REQ、SR、必要设计或独立维护完成条件，US 不是必经追溯层。ABB 与 VT 只依赖各自需要的输入，不要求先完成 US 或互相等待。上游或切片范围变化时先核对验收、未知项与旧结果适用性，提出需确认的进度/范围修订，不自动改成已确认或以缩小范围掩盖缺口。
