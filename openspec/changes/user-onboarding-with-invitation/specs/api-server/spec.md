## ADDED Requirements

### Requirement: 邀请码验证 API

系统 SHALL 提供邀请码验证的 REST API 端点。

#### Scenario: 验证邀请码
- **WHEN** 客户端发送 POST /api/invitations/validate 及邀请码
- **THEN** 系统验证邀请码有效性并返回验证结果

#### Scenario: 验证成功响应
- **WHEN** 邀请码验证成功
- **THEN** 系统返回 200 状态及验证成功消息

#### Scenario: 验证失败响应
- **WHEN** 邀请码验证失败
- **THEN** 系统返回 400 状态及错误消息

### Requirement: 用户管理 API

系统 SHALL 提供用户管理的 REST API 端点。

#### Scenario: 创建用户
- **WHEN** 客户端发送 POST /api/users 及用户信息（姓名）
- **THEN** 系统创建用户并返回用户 ID

#### Scenario: 获取当前用户信息
- **WHEN** 客户端请求 GET /api/users/me
- **THEN** 系统返回当前登录用户的信息（id、name、onboarding_completed）

#### Scenario: 未登录用户访问
- **WHEN** 未登录用户请求 GET /api/users/me
- **THEN** 系统返回 401 Unauthorized

### Requirement: SOUL 问卷 API

系统 SHALL 提供 SOUL 问卷的 REST API 端点。

#### Scenario: 获取问卷问题
- **WHEN** 客户端请求 GET /api/soul/questionnaire
- **THEN** 系统返回所有 6 个问题的完整内容（标题、提示、选项）

#### Scenario: 提交问卷答案
- **WHEN** 客户端发送 POST /api/soul/questionnaire 及答案
- **THEN** 系统保存答案并返回成功状态

#### Scenario: 获取问卷进度
- **WHEN** 客户端请求 GET /api/soul/questionnaire/progress
- **THEN** 系统返回当前用户的问卷进度（已完成的问题数、当前问题）

#### Scenario: 清除问卷进度
- **WHEN** 客户端发送 DELETE /api/soul/questionnaire/progress
- **THEN** 系统清除当前用户的问卷进度

#### Scenario: 生成个性化画像
- **WHEN** 用户完成所有问题并提交
- **THEN** 系统生成 soul.md 和 soul.meta.yaml 文件

### Requirement: 会话管理中间件

系统 SHALL 实现会话验证中间件。

#### Scenario: 验证会话
- **WHEN** 请求到达受保护的 API 端点
- **THEN** 中间件验证 Cookie 中的 session_id

#### Scenario: 会话有效
- **WHEN** 会话验证成功
- **THEN** 请求继续处理并注入用户信息

#### Scenario: 会话无效
- **WHEN** 会话验证失败
- **THEN** 系统返回 401 Unauthorized

#### Scenario: 公开端点
- **WHEN** 请求到达公开端点（如 /api/invitations/validate、/api/health）
- **THEN** 中间件跳过会话验证

### Requirement: 数据库集成

系统 SHALL 集成 SQLite 数据库存储用户数据。

#### Scenario: 数据库初始化
- **WHEN** API 服务器启动
- **THEN** 系统创建必要的数据库表（users、invitation_codes、user_sessions、questionnaire_answers）

#### Scenario: 数据库连接
- **WHEN** API 处理请求
- **THEN** 系统连接到 SQLite 数据库（默认位置：~/.cinder/cinder.db）

#### Scenario: 数据库错误处理
- **WHEN** 数据库操作失败
- **THEN** 系统返回 500 状态并记录错误日志
