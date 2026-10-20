---
name: update-template
description: Use when a template version changes, a project has owner edits against an old template, or explicitly selected BCs need proposals for versioned source scenarios.
---

# 模板更新与多目标提案

旧基线、当前所有者内容、新候选分别读取；**差异是提案，不是应用结果或传播授权**。人和 Agent 共用本方法，不依赖 prompt 或维护者 workflow。

## 输入

- 本次任务、允许的文件范围、读写权限和完成条件；[项目登记](../../../README.md#project)中的真实模板来源。
- 实际旧基线、本地项目、新候选的本地根、可读文件与版本；本地未提交修改、主动删除、业务数据和原规则位置。
- 多目标另需[登记契约](../../../docs/template-updates.md#registration)中的来源场景、允许文件、目标仓库/上下文、本地 checkout、准确版本及本次明确选择的目标。
- [维护工具环境](../../../docs/development.md#maintenance-tools)和本次输出位置；缺输入不以 HEAD、分支、空目录或第一个目标替代。

## 操作

1. 先读 [AGENTS](../../../AGENTS.md)、任务与实际资料，核对工作目录、分支、commit、index/工作文件和已有修改。只读源不回写；不整仓覆盖、不移动业务布局，也不把历史分发清单当作当前版本的文件范围。
2. 沿[工具契约](../../../docs/template-updates.md#api)核对三个根及实际原始字节；给了精确 Git/content 版本就验证，脏文件不能标成未经核对的 HEAD。默认/API 不写；仅显式新报告可落在所有受保护来源之外，已有报告不覆盖。
3. 运行同一 Python core 取得 `changes/conflicts/preserved`，逐项读路径、旧/本地/候选的版本与摘要或明确缺席、操作和理由。二进制、BOM、换行与本地主动删除不归一化；不自动合并、选 ours/theirs 或复活所有者已删内容。
4. 多目标按“来源场景 → 明确 BC → 允许文件 → 各自结果”检查；只读已存在的本地来源，不复制 model 或整仓。某目标 unavailable/conflict 不隐藏其他结果，也不能用少数成功宣称全批传播完成。
5. 下表停点按受影响目标保留。若以后操作原生 Git/平台，另取得**具体目标、版本和动作**的当前授权；先重读源版本及确切提案。配置、提案、`apply` 字样或本方法都不批准 clone/fetch、改文件、commit/push、PR 或合并；本工具没有这些操作。
6. 按 [verify-change](../verify-change/SKILL.md)核对实际结果/源保护，按 [record-handoff](../record-handoff/SKILL.md)链接提案与缺口；只记必要身份、摘要和诊断，不复制本地业务正文、秘密或完整聊天。

## 快速参考与停点

| 观察 | 本次产出与下一步 |
|---|---|
| `no-change` / 0 | 实际已对齐或仅保留所有者变化；不是一次应用/传播成功 |
| `proposed` / 0 | 可审阅的增/改/删提案；尚未修改目标 |
| `conflict` / 1 | 保留冲突及全部身份；停止该目标合入，需所有者决定 |
| `input-error` / 2、逐目标 `unavailable` | 保留缺根/版本/读取/登记/范围问题；停止该目标，补输入后重算 |
| 权限/范围不明，或非空且未获准修改的目标/输出 | 停写，不跳过冲突后报完成，不另建应用或执行器解阻 |

例如在仓库根、使用本次实际项目解释器：

```text
.venv\Scripts\python.exe -B -X utf8 .github\utilities\plan_template_update.py --registration "<本次本地登记.yaml>" --target "<明确目标ID>"
```

尖括号必须替换为实际输入；可重复 `--target`。三根模式、准确版本、16 类判定和新输出规则见[更新说明](../../../docs/template-updates.md)，不在本方法复制算法。

## 常见错误

缺旧基线不是“模板从未有文件”；不可读不是删除；本地专有文件不是过期模板。报告退出 0、文件存在或 workflow YAML 可解析，都不证明业务验收、人工批准、客户端发现或外部 fan-out 已运行。
