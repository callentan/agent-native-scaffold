# 通用工作入口

人和 Agent 使用同一套方法、事实与结果，方法正文只维护在[活动导航](README.md#activities)所列的实际 `SKILL.md` 中。

## 读取入口

1. 读 [README 项目登记](README.md#project)与当前任务的目标、范围、依据和完成条件；维护请求本身可以作依据，不强制创建 US。
2. 从 [README 活动导航](README.md#activities)选择对应方法，**显式读取完整 `SKILL.md`**，再读它链接的当前事实、指引和表单。文件名、链接或描述不是自动包含保证；没有原生发现时也沿这条路径读取。
3. 修改 Markdown 时读[文档规则](.github/instructions/docs.instructions.md)；修改任何测试时读[测试规则](.github/instructions/tests.instructions.md)。修改代码还须显式完整读[架构](.github/instructions/architecture.instructions.md)、[编码](.github/instructions/coding.instructions.md)和[安全规则](.github/instructions/security.instructions.md)，即使实际路径不匹配初始 globs。按实际项目补充匹配范围，不假设 `src` 是唯一代码位置或统一测试布局。
4. 写入前核对实际目录、Git 分支、commit、暂存区及未提交范围；保留所有者内容、已有规则位置和无关改动。

## 边界

- 只做获授权的任务。影响行为的事实缺失、来源不可读、冲突或授权不足时停止受影响的操作并说明，不把占位或提案当事实。
- [开发说明](docs/development.md)未配置时不自行选栈、安装依赖或生成项目；输入齐备的纯文档维护可继续。
- 初始生成使用 [generate-code](.github/skills/generate-code/SKILL.md)，既有代码/文档维护使用 [implement-task](.github/skills/implement-task/SKILL.md)；非空目标冲突要明确停写，跳过文件不等于生成完整。可选 [BC 配置](architecture/README.md#bc-configuration)不授予源写入或执行权限。
- 证据与影响按 [verify-change](.github/skills/verify-change/SKILL.md)处理；完成、暂停或接手按 [record-handoff](.github/skills/record-handoff/SKILL.md)处理。不补造结果，不复制权威记录或隐藏聊天依赖。

原生入口与观察状态见[接入说明](docs/agent-support.md)。角色不是独立人工批准者，也不自动组织团队；Markdown 规则不替代真实权限、sandbox 或 CI，外部操作仍须相应授权。
