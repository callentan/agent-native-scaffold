# 通用工作入口

人和 Agent 使用同一套仓库资料，不另建一份事实或结果。

## 开始前

1. 读 [README](README.md)，确认项目阶段、范围和未配置项。
2. 读当前任务的目标、范围、依据和完成条件；小维护请求或现有 issue 本身可以是任务依据，不强制创建 US。
3. 按任务读取[领域事实](domain-model/README.md)、[业务需求](stakeholder-requirements/README.md)、[软件要求](software-requirements/README.md)及[必要设计](architecture/README.md)。占位、提案和未决项不能当成已确认事实。
4. 读[真实开发说明](docs/development.md)、[验证指引](verification/README.md)和[相关日志](logs/README.md)，核对结果基线与待复核项。
5. 写入前检查当前工作目录、Git 分支、暂存区和未提交改动。保留无关修改，不自动覆盖已有 README、AGENTS 或其他规则。

## 工作与停止条件

- 只做当前任务所需的修改。缺少会改变行为的业务事实、必需资料不可读、事实冲突、修改冲突或授权不足时，停止受影响的操作并提出具体问题。
- 开发说明未配置时不自行选技术栈、安装依赖或生成项目；纯文档工作仍可按任务继续。
- 按[验收盘点与影响检查](verification/README.md#coverage-check)核对要求、VT 和基线；检查失败就报告，不删除要求或降低标准来抹平缺口。
- 只报告实际执行的检查。分清文档检查、业务验收、软件行为，以及 `not-run`、历史结果和当前适用性。
- 完成或暂停时用[日志表单](_templates/items/development-log.md)留下任务、变化、结果链接、缺口和下一步；不保存完整聊天、凭据或敏感输出。

不自动发现本文件的客户端，可显式读取它并沿链接取用所需资料，见[接入说明](docs/agent-support.md)。文件约定不替代客户端或平台的真实权限配置；外部操作仍须有相应授权。
