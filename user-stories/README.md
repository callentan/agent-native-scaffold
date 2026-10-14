# 交付切片与实施清单

US 用于组织一次交付的范围、步骤、状态和记录链接，不是第二份需求。需要交付切片时使用 [US 表单](../_templates/items/user-story.md)，放入 `user-stories\US-NNN-<slug>.md`；目前尚无正式 US。

<a id="delivery"></a>
## 何时使用

相关工作需要分步实施或单独跟踪范围时，可以建 US。已有维护请求、缺陷或 issue 能说明目标、范围、依据与完成条件时，直接使用它即可，不强改成用户故事，也不要求先补齐 REQ/SR/US/ABB。

## 填写与完成

- 链接实际任务依据、[业务需求](../stakeholder-requirements/README.md)或[软件要求](../software-requirements/README.md)，说明本次包含和不包含什么。
- 列出要修改的资料或项目、依赖与实施清单；需求正文、规则和验收条件仍回源读取。清单是工作进度，不是新增一套产品验收。
- 可用 `todo`、`in-progress`、`blocked`、`review-ready`、`done` 记录任务状态；初始为 `todo`，完成依据不能预填。
- 引用[验证记录](../verification/README.md)和[相关日志](../logs/README.md)，保留缺口、待复核和未执行项。`done` 只表示约定任务完成，不自动代表业务验收通过或已上线。

VT 直接指向它验证的 REQ、SR、必要设计或独立维护完成条件，US 不是必经追溯层。任务范围变化时先确认依据，再核对验收与影响，不以缩小任务范围掩盖真实缺口。
