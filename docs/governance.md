# 可选治理与决定记录

本页是字段与归属指引，不是一套审批流程。只有当前任务存在适用政策、责任人要求或需要独立引用的决定时，才采用下列表单；小维护可以继续使用原任务与日志，不补造 QMS、组织角色或批准实例。表单存在不表示本项目属于医疗产品，也不引入临床、监管或风险分类。

<a id="records"></a>
## 按实际需要选用记录

| 需要保留的资料 | 表单与默认正式落点 | 共用方法 |
|---|---|---|
| 人工审阅、发现及有来源的决定；适用时记录 waiver | [审阅记录](../_templates/items/review-record.md)；`verification\REVIEW-NNN-<slug>.md` | [verify-change](../.github/skills/verify-change/SKILL.md#domain-review)，默认只读 |
| 工具用途、评价范围与实际授权来源 | [工具资格与使用](../_templates/items/tool-qualification.md)；`verification\TQ-NNN-<slug>.md` | [verify-change](../.github/skills/verify-change/SKILL.md)，字段见 [AI 工具说明](ai-tooling.md) |
| 有来源的用途、用户、环境、范围内外与变更提案 | [Intended Use](../_templates/items/intended-use.md)；`domain-model\IU-NNN-<slug>.md` | [define-requirements](../.github/skills/define-requirements/SKILL.md#intended-use) |
| 外部风险分析、控制与决定的引用 | [风险控制引用](../_templates/items/risk-control.md)；`domain-model\RC-NNN-<slug>.md` | [verify-change 的影响检查](../.github/skills/verify-change/SKILL.md#impact) |

这些是按需落点，不要求新建空目录；已有项目位置和原所有者保持不变。初次整理已提供的用途资料可按[访谈与事实整理](../.github/skills/define-requirements/SKILL.md#interview)保留草稿；**修订**仍需现有完整文件、原基线与实际授权，不能用新表单替代缺失原文。审阅模式只返回发现，不因存在表单而获得执行或保存记录的权限。

<a id="ownership"></a>
## 字段只由一处拥有

| 信息 | 唯一归属与阅读方式 |
|---|---|
| 本记录的身份、scope、内容声明和实际正式关系 | [现有 frontmatter](../domain-model/README.md#artifact-metadata)；正文不另列 ID、contentState 或关系镜像 |
| 原始政策、用途、风险分析及接受决定 | 实际来源的所有者与固定基线；本地表单记录必要说明和定位，不接管外部权威 |
| 审阅对象、判据、发现及决定边界 | 审阅记录正文；`decision` 的“审阅结论”不是 contentState，也不是 VT 结果 |
| 工具配置、拟议用途、评价与适用性 | 工具使用记录；原始评价步骤、观察和结果仍回 VT/实际报告读取 |
| REQ/SR/设计要求与验证结果 | 各自原工件；审阅不能改写其结果、缩小验收范围或把缺测试写成通过 |
| 交接与派生视图 | [日志](../logs/README.md)只留入口；model/SWAS 只引用来源及基线，不复制决定或风险正文 |

只有真实来源关系才加 `upstream`；只有实际验收目标及独立判据才加 `targets`。审阅对象或外部文件未采用元数据时保留普通文件/章节导航，不发明 canonical ID。下游影响是待办与阅读入口，不在多处维护相反关系表。同号异 scope 必须按完整 `scope/id#anchor` 定位，不能借另一个上下文的决定确认本对象。

<a id="decisions"></a>
## 决定、确认与 waiver

- 新表单保持 `draft`。实际审阅者、决定者的姓名/角色声明、责任依据、决定原文、日期、对象基线和适用范围分别需要来源；Agent 自审不得称为独立人工审阅。缺谁、缺什么证据、阻塞哪个结论要明确。
- `confirmed` 必须按现有契约提供 `confirmation.by/reference/baseline`，只在 frontmatter 保存本记录的确认声明。记录被确认不等于其中的工具被批准或风险被接受；原决定也可能是拒绝或要求补充。schema 只检查声明形状，不认证身份、权限或签名，实际决定仍须回原文核对。
- waiver 仅在确有适用要求及授权决定时记录：被豁免条款及其基线、理由、范围/期限或失效条件、补偿措施来源、具名决定与需复核项。没有授权者或证据就是提案，不能用空表、勾选、`Approved`、`Reviewed-by`、角色名称或 commit trailer 替代。
- 对象、要求、工具版本/配置、用途或政策基线变化时，保留原决定和证据，按[影响方法](../.github/skills/verify-change/SKILL.md#impact)重新判断适用性。旧通过不自动成为新通过，也不能被改写成历史失败。

<a id="intended-use"></a>
## Intended Use 与外部风险边界

用途记录说明实际目的、使用者、环境、范围及排除用途，区分现行来源与候选变更。只有来源确实涉及患者、临床、安全或监管时才记录相应来源，不预填产品声明、医疗分类或 RA 批准。未知环境、约束、负责政策或决定阻塞受影响的用途确认；已知部分可保留草稿并列出需谁补充什么。

范围或安全相关变化沿实际上下文、REQ/QAS、SR、设计、接口/消费者、风险与验证追踪，列章节级差异、升级需要和未执行项。升级对象及条件以本项目真实政策为准；没有该政策就请求责任人确定，不能自行分级或默认所有项目走同一链。

风险控制表单只引用实际外部分析、控制所有者、要求/设计/验证和接受或拒绝决定。不计算风险，不填默认严重度或残余分值，不声称满足某法律标准。来源未提供、不可读或决定缺失时，明确记录可访问性、定位线索、责任缺口和被阻塞判断；不存在的本地文件用文字描述，不造可点击的假证据。

<a id="source-views"></a>
## 使用既有模型来源接口

需要 model 时按[现有来源契约](../.github/contracts/README.md#model-sources)显式选择原工件及真实字节/对象基线，不另抄汇总数据。直接 Markdown 读取下列原所有者字段；保留锚点与二列表格标签：

| 原记录 | 必要的源位置 |
|---|---|
| review-record | `decision` 下的“审阅结论”“限制与说明” |
| risk-control | `analysis` 下的“控制前风险”、`control` 正文、`residual` 下的“残余风险”，以及实际 REQ/VT 来源 |

未知值写明“未提供：具体缺项”或“未知：原因”，不为取得 `available` 补造结论、风险数字或反向关系。可读但缺字段/关联是 `partial`；可选来源未提供、不可读或基线不可核实是 `unverified`。必要主输入错误仍失败。工具资格表可作治理关联来源，但不能仅凭它替代直接 governance 需要的审阅记录；按实际关系选择来源，不为导出创造审批链。视图 `available` 也只表示所查来源完整，不是实质批准。

<a id="limits"></a>
## 记录与执行权限

只留[最小工具/任务/决定指针](ai-tooling.md#minimal-record)，不要求完整会话、凭据、患者或生产数据。敏感来源沿原获准入口访问，记录其访问限制，不为可追溯性复制敏感内容。

执行、保存记录、修改来源与外部通知分别服从本次授权；Markdown、表单、只读意图不是 ACL、sandbox、客户端或平台门禁。按[交接方法](../.github/skills/record-handoff/SKILL.md)链接实际结果与缺口，不把 Agent 观察当真实人工参与或原生权限测试。
