## ADDED Requirements

### Requirement: 创建用户会话

系统 SHALL 在用户完成引导流程后创建会话。

#### Scenario: 会话创建
- **WHEN** 用户完成引导流程
- **THEN** 系统生成唯一的 session_id 并存储在 Cookie 中

#### Scenario: 会话 ID 格式
- **WHEN** 系统生成 session_id
- **THEN** session_id SHALL 使用 UUID v4 格式

#### Scenario: Cookie 设置
- **WHEN** 系统设置会话 Cookie
- **THEN** Cookie SHALL 包含：
  - HttpOnly 标志
  - Secure 标志（生产环境）
  - 过期时间（7 天）

### Requirement: 验证用户会话

系统 SHALL 在每次请求时验证用户会话。

#### Scenario: 有效会话
- **WHEN** 用户请求携带有效的 session_id
- **THEN** 系统允许访问

#### Scenario: 无效会话
- **WHEN** 用户请求携带无效的 session_id
- **THEN** 系统重定向到引导页面

#### Scenario: 过期会话
- **WHEN** 用户请求携带过期的 session_id
- **THEN** 系统清除 Cookie 并重定向到引导页面

#### Scenario: 缺少会话
- **WHEN** 用户请求不包含 session_id
- **THEN** 系统重定向到引导页面

### Requirement: 会话数据存储

系统 SHALL 在数据库中存储会话数据。

#### Scenario: 会话记录
- **WHEN** 创建会话时
- **THEN** 系统在 user_sessions 表中存储 session_id、user_id、created_at、expires_at

#### Scenario: 会话查询
- **WHEN** 验证会话时
- **THEN** 系统从数据库查询会话记录

#### Scenario: 会话清理
- **WHEN** 会话过期时
- **THEN** 系统自动清理过期会话记录

### Requirement: 会话过期管理

系统 SHALL 管理会话的过期时间。

#### Scenario: 默认过期时间
- **WHEN** 创建会话时
- **THEN** 会话默认过期时间为 7 天

#### Scenario: 可配置过期时间
- **WHEN** 管理员配置会话过期时间
- **THEN** 系统使用配置的过期时间

#### Scenario: 自动续期
- **WHEN** 用户活跃使用系统
- **THEN** 系统可选择性续期会话

### Requirement: 获取当前用户信息

系统 SHALL 提供获取当前登录用户信息的接口。

#### Scenario: 获取用户信息
- **WHEN** 客户端调用 GET /api/users/me
- **THEN** 系统返回当前用户的 id、name、onboarding_completed 等信息

#### Scenario: 未登录用户
- **WHEN** 未登录用户调用 GET /api/users/me
- **THEN** 系统返回 401 Unauthorized

### Requirement: 会话中间件

系统 SHALL 实现会话验证中间件。

#### Scenario: 中间件应用
- **WHEN** 请求到达受保护的路由
- **THEN** 中间件验证会话有效性

#### Scenario: 公开路由
- **WHEN** 请求到达公开路由（如 /onboarding、/api/health）
- **THEN** 中间件跳过会话验证

#### Scenario: 会话注入
- **WHEN** 会话验证成功
- **THEN** 中间件将用户信息注入请求上下文
