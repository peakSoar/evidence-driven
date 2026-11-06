# Harness 填写样例

本文件只作参照，不复制到目标仓库。模板给的是骨架，这里给的是“填到什么程度算填好了”。

规则只有一条：一段话读完之后，能回答“谁在哪做了什么，怎么验证”。答不上来就是没填好。

## 一、对照表

### 问题基线（`docs/改造计划与进度.md` 第 1 节）

不合格：

| 已确认问题 | 设计方向 | 责任阶段 |
| --- | --- | --- |
| 鉴权逻辑分散 | 统一鉴权入口 | S00 |

合格：

| 已确认问题 | 设计方向 | 责任阶段 |
| --- | --- | --- |
| 网关解析令牌后把身份写进请求头，下游再解析一次，两边各有一份关于头的约定 | 网关只验不改写，各服务用同一个 `AuthVerifier` 独立校验 | S00 |
| `docs/` 被 `.gitignore` 的 `**/docs` 忽略，文档不随仓库版本化 | 移除忽略规则，`docs/history/` 单独排除 | S00 |

差别在第二行能不能被验证：前者没法判断“做没做”，后者跑一次 `git ls-files docs` 就知道。

### 核心不变量（`AGENTS.md` 第 3 节）

不合格：

- 统一鉴权，避免重复实现。
- 注意会话安全。

合格：

- `AuthVerifier` 是验签与会话比对的唯一实现，网关 `LoginInterceptor` 与各服务 `AuthInterceptor` 都调它，不在应用内复制。
- 设备会话键固定 `auth:session:{userId}:{sid}`，有效期 24 小时；选身份时版本加一，Lua 脚本保留原剩余 TTL，切换身份不延长会话。
- VO 与 JWT 声明中的 ID 用 `String`，内部 `AuthSession` 与 `CurrentUser` 用 `Long`，转换只发生在边界。

这三条都写成了“改哪一行会破坏它”的形式。

### 边界（`docs/当前阶段与下一步.md` 的“必须保留的边界”）

不合格：

- 保持架构清晰，不要引入不必要的复杂度。

合格：

- 网关只验不改写，不向下游注入身份头；服务能脱离网关单独启动。
- 白名单只在 `AuthPaths.PUBLIC` 维护一份，不在各服务各写一份。
- 新增服务接入鉴权只需引 `archives-common` 的 `auth` 包并注册一个 `WebMvcConfigurer`。

### 验收证据（`docs/验收/当前验收.md` 第 3 节）

不合格：

| 层次 | 命令或操作 | 结果 | 证据说明 |
| --- | --- | --- | --- |
| 测试 | 跑了一下测试 | PASS | 测试通过 |

合格：

| 层次 | 命令或操作 | 结果 | 证据说明 |
| --- | --- | --- | --- |
| 定向测试 | `mvn -o -pl archives-system -am test` | PASS | `AuthInterceptorTest` 4/4，`DigitalArchivesApplicationTests` 1/1 |
| 全量构建 | `mvn -o clean install` | PASS | 12 个模块 BUILD SUCCESS，退出码 0 |
| 真实链路 | 网关 8080 + 服务 8081 + Redis 16379 | PASS | 9 个场景：无令牌、伪造签名、`ticket` 冒充、版本不符、身份不符、删会话重放、有效令牌、直连下游、无令牌直连 |

“跑了一下测试”不能算证据，因为没有命令、没有数量、退出码未知，下一个人无法复现，也无法判断它是不是昨天的数字。

### 阶段目标（`docs/阶段/Sxx-*.md` 第 1 节）

不合格：

- 优化用户登录流程，完善鉴权体系。

合格：

- 把网关与各服务的鉴权收敛到 `archives-common` 的 `AuthVerifier`，去掉身份头透传，使服务可以脱离网关单独启动联调。

判断标准：这个目标是 `DONE` 还是 `IN_PROGRESS`，能不能只看事实决定，不看措辞。

## 二、填好的 `AGENTS.md` 片段

下面是第 2、3 节的写法，可以直接对照结构，内容按目标仓库替换。

```markdown
## 2. 项目与架构边界

- 支持平台：JDK 21 服务端，Vue 3 前端，MySQL 8，Redis。
- 核心技术栈：Spring Boot 4.1.2、Spring Cloud 2025.1.2 网关（Server MVC 模型）、MyBatis（非 Plus）、Maven 多模块。
- 产品明确不支持：Spring Security 过滤器链、MyBatis-Plus、OpenFeign、注册中心之外的分布式组件。
- 数据保留范围：单库 `digital_archives`，档案文件走存储后端，库内只存 `storage_key`。
- 外部系统与联网边界：邮件走 SMTP，短信通道未接入。

## 3. 核心不变量

- `AuthVerifier` 是验签与会话比对的唯一 owner，网关和下游服务都调它。
- 网关只验不改写，不向下游注入身份头。
- `RedisKeyManage` 是 Redis 键的唯一来源，业务代码不拼字符串键。
- `CurrentUser` 在拦截器里组装，请求结束后清理 ThreadLocal。
```

## 三、填好的 `当前验收` 片段

```markdown
## 1. 验收结论

- 结论：`PASS`
- 阶段或任务：`S00`
- 状态：`DONE`
- 目标 HEAD：`c00bf1c`
- 分支：`master`

## 3. 实际验证

| 层次 | 命令或操作 | 结果 | 证据说明 |
| --- | --- | --- | --- |
| 定向测试 | `mvn -o -pl archives-system -am test` | PASS | 5 条用例全过，退出码 0 |
| 全量构建 | `mvn -o clean install` | PASS | 12 模块 BUILD SUCCESS |
| 差异检查 | `git diff --check` | PASS | 退出码 0，只有 CRLF 提示 |
| 真实链路 | 网关 8080 + 服务 8081 + MySQL 13306 + Redis 16379 | PASS | 登录、选身份、退出、鉴权 20 个场景，明细见下表 |

## 5. 未运行项与剩余风险

- 未运行：前端、档案、借阅、通知服务，本轮不涉及。
- 剩余风险：下游拒绝返回 HTTP 200 + `code=401`，与网关的真实 401 口径不同。
- 下一步：S01 开工前确认邀请表结构与有效期。
```

## 四、填好的接力片段

```markdown
## 最近完成

- `2026-11-06`：鉴权收口到 `archives-common` 的 `AuthVerifier`，网关与各服务各自验签、不传身份头，删除 `SpringUtil`、`AuthHeaders`、`UserSessionInterceptor`。
- `2026-11-06`：全模块 `mvn -o clean install` 通过，`AuthInterceptorTest` 4 条与上下文启动测试 1 条通过。
- `2026-11-05`：确认注册与部门邀请规则——注册即无部门普通员工，负责人发邀请，员工确认后加入，多部门邀请仅首次接受生效。
```

每条都以动词开头、带日期、能追溯到具体文件或命令。不写“完成了鉴权相关工作”这种句子，它对下一会话没有用。
