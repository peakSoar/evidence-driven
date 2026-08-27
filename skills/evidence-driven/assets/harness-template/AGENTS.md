# {{PROJECT_NAME}} AI Harness 项目指南

## 1. 固定恢复入口

进行产品、实现、测试、构建或验收工作前，必须按以下顺序恢复上下文：

1. 阅读根级 `AGENTS.md`。
2. 阅读 `docs/改造计划与进度.md`，确认唯一当前阶段和状态。
3. 阅读 `docs/当前阶段与下一步.md`。
4. 只读取《改造计划与进度》指向的当前阶段文件。
5. 只读取该阶段列出的源码、测试和《验证规则》条目。
6. 核对 `git status --short`、当前 HEAD、分支、预存修改和阶段状态。

聊天摘要只能帮助定位，不能覆盖状态权威、接力信息和磁盘事实。《当前验收》是最近验证快照，不是阶段状态权威。

纯 Git 操作只需读取本文件并核对 HEAD、分支和工作区。没有活动阶段时，不为普通查询或局部低风险任务创建阶段。

## 2. 项目与架构边界

- 支持平台：{{SUPPORTED_PLATFORMS}}。
- 核心技术栈：{{TECH_STACK}}。
- 产品明确不支持：{{NON_GOALS}}。
- 数据保留范围：{{DATA_RETENTION_BOUNDARY}}。
- 外部系统与联网边界：{{EXTERNAL_SYSTEM_BOUNDARY}}。

改变支持平台、核心技术栈、数据保留范围、安全边界、外部系统或联网能力前，必须说明产品、安全、迁移和验证影响并获得用户确认。

## 3. Owner 与核心不变量

先根据当前源码填写，不要把目标架构写成已存在事实。

- {{DOMAIN_OWNER}} 拥有 {{DOMAIN_RULES}}。
- {{PERSISTENCE_OWNER}} 是 {{PERSISTED_STATE}} 的唯一持久化 owner。
- {{TRANSPORT_OWNER}} 只负责 {{TRANSPORT_RESPONSIBILITIES}}，不得复制领域规则。
- {{UI_OWNER}} 只拥有展示投影、输入草稿和显示格式化，不建立第二份领域数据库。
- {{CONTRACT_SOURCE}} 是跨边界 DTO 的契约源，其他类型由生成或漂移检查维护。
- {{RESOURCE_OWNER}} 独占 {{EXCLUSIVE_RESOURCE}}，其他线程或进程只通过 {{COORDINATION_MECHANISM}} 交互。
- 敏感信息不得进入日志、fixture、测试快照、验收文档或错误输出。

同一业务规则、状态或序列化行为只能有一个 owner。跨边界传递数据和结果，不复制算法。只有多个当前调用方共享相同不变量，或事务、并发、资源释放和安全边界需要集中时才新增抽象。

## 4. 事实等级与开工审计

关键结论必须标注：

- `CONFIRMED`：源码、测试、运行结果等多类证据交叉确认。
- `CODE_CONFIRMED`：当前源码或测试直接确认。
- `DATA_CONFIRMED`：本轮数据库、日志或运行产物直接确认。
- `STRONG_INFERENCE`：多项证据支持，但缺少一个直接闭环。
- `HYPOTHESIS`：待验证假设。

`HYPOTHESIS` 不得驱动长期或不可逆生产设计。修改生产代码前必须：

1. 找到字段和状态的 producer。
2. 找到聚合、映射、去重、队列、事务或替换等 transition。
3. 找到真正作业务决定的 consumer。
4. 确认规则和状态的唯一 owner。
5. 区分数据现象、环境问题和代码原因。
6. 检查现有测试是在保护目标行为还是固化旧错误。
7. 先建立 characterization fixture 和目标不变量测试，再修改生产实现。
8. 文档与源码不一致时先勘误文档，不得为了符合旧文档修改正确源码。

阶段开工输出至少列出：HEAD、分支、预存工作区、已确认事实、文档差异、证据不足项、固化旧错误的测试、拟新增 fixture、实际修改边界和验证计划。

## 5. 文档权威

| 文档 | 唯一职责 |
| --- | --- |
| `docs/改造计划与进度.md` | 问题基线、目标边界、当前阶段、唯一状态表、依赖和导航 |
| `docs/当前阶段与下一步.md` | 最近会话继续点；不拥有阶段状态 |
| `docs/阶段/Sxx-*.md` | 当前阶段的问题证据、范围、测试、验收和退出条件 |
| `docs/验证规则.md` | 通用验证闭环、状态边界、命令和人工操作矩阵 |
| `docs/验收/当前验收.md` | 最近一次实际执行证据；每轮整体覆盖 |

Git 历史保存旧验收和文档差异，不新增累积式验收记录目录。

## 6. 状态机和任务边界

阶段状态只允许：`NOT_STARTED`、`IN_PROGRESS`、`HUMAN_ACTION_REQUIRED`、`BLOCKED`、`DONE`、`REOPENED`。

```text
NOT_STARTED -> IN_PROGRESS -> DONE
IN_PROGRESS -> HUMAN_ACTION_REQUIRED -> IN_PROGRESS
IN_PROGRESS <-> BLOCKED
DONE -> REOPENED -> IN_PROGRESS -> DONE
```

同一时刻只允许一个活动阶段。当前阶段未 `DONE` 时不得进入下一阶段。新证据推翻已完成 owner 时，必须重开最早责任阶段，不能在后继阶段复制临时规则。

普通局部、低风险、单会话任务不建立阶段、不改变已完成阶段状态。跨会话、跨模块、高风险、发布或需要人工操作的工作才建立阶段。

## 7. 测试和反馈闭环

每个生产阶段必须遵循：

```text
冻结现状
-> characterization fixture
-> 目标红灯
-> 最小实现
-> 定向绿灯
-> 受影响回归
-> 静态与契约门禁
-> 必要真实产品验收
-> 覆盖当前验收
-> 阶段退出或反馈回流
```

实现或回归失败留在 `IN_PROGRESS`；环境或权限失败进入 `BLOCKED`；需要用户真实操作进入 `HUMAN_ACTION_REQUIRED`；新证据推翻前置 owner 时进入 `REOPENED`。

## 8. 人机权限边界

AI 可以执行：{{AI_ALLOWED_ACTIONS}}。

以下操作必须由用户明确授权：{{USER_AUTHORIZATION_REQUIRED_ACTIONS}}。

需要人工操作时，AI 必须先完成自动验证和前置核验，把阶段设为 `HUMAN_ACTION_REQUIRED`，写明精确动作、目标、禁止动作和恢复检查，然后停止。用户完成后恢复 `IN_PROGRESS`，AI 只读验收，不修改数据制造通过。

## 9. 工作区纪律

- 不自动提交、push、发布、部署、创建 PR 或切换分支，除非用户明确要求。
- 不回滚、覆盖、清理、重新 stage 或混入用户已有修改。
- 只修改当前阶段或当前任务明确允许的范围；无关问题只记录。
- 不静默吞错；错误必须说明事实、影响和下一步。
- 新增依赖前说明必要性、维护状态、许可证、锁定版本和替代方案。
- 收工前运行阶段要求的测试、静态门禁、`git diff --check` 和 `git status --short`，并整体覆盖《当前验收》。

## 10. 项目专项规则

{{PROJECT_SPECIFIC_RULES}}
