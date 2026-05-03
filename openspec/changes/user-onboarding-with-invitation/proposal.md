## Why

当前 Web Dashboard 允许用户直接访问所有功能，缺少必要的用户引导和身份验证流程。这导致：
1. 任何人都可访问系统，无法控制用户群体
2. 缺少用户信息收集，无法提供个性化体验
3. SOUL 问卷仅在 CLI 中实现，Web 界面只有简单的滑块配置，无法生成完整的个性化画像
4. 无法追踪用户行为和偏好

需要实现完整的用户引导流程，包括邀请码验证、用户信息收集和 SOUL 问卷，以提供受控的、个性化的用户体验。

## What Changes

### 新增功能
- 邀请码验证机制：用户首次访问时需要输入有效邀请码
- 用户信息收集：收集用户姓名等基本信息
- Web 版 SOUL 问卷：将 CLI 中的 6 题心理测评问卷移植到 Web 界面
- 用户会话管理：基于 Cookie 的会话机制，追踪用户引导流程完成状态
- 访问控制：未完成引导的用户将被重定向到引导页面

### 修改功能
- 修改首页访问逻辑：添加引导流程检查
- 扩展 SOUL 配置 API：支持问卷答案提交和画像生成
- 更新前端路由：添加引导流程相关页面

## Capabilities

### New Capabilities
- `invitation-code-validation`: 邀请码验证机制，支持单次和多次使用的邀请码
- `user-onboarding-flow`: 完整的用户引导流程，包括邀请码验证、信息收集和问卷
- `soul-questionnaire-web`: Web 版本的 SOUL 心理测评问卷，包含 6 个问题的交互式界面
- `user-session-management`: 基于会话的用户状态管理，追踪引导流程完成情况

### Modified Capabilities
- `api-server`: 扩展 API 以支持用户引导流程相关的端点

## Impact

### 后端影响
- 新增 SQLite 数据表：users, invitation_codes, user_sessions
- 新增 API 端点：
  - POST /api/invitations/validate - 验证邀请码
  - POST /api/users - 创建用户
  - GET /api/users/me - 获取当前用户信息
  - POST /api/soul/questionnaire - 提交问卷答案
  - GET /api/soul/questionnaire - 获取问卷问题
- 新增中间件：会话验证和引导流程检查

### 前端影响
- 新增页面：
  - /onboarding/invitation - 邀请码验证页
  - /onboarding/profile - 用户信息填写页
  - /onboarding/questionnaire - SOUL 问卷页
- 修改路由逻辑：添加引导流程守卫
- 更新 API 客户端：支持新的用户和问卷相关 API

### 数据存储
- 新增 SQLite 数据库文件（默认位置：~/.cinder/cinder.db）
- 数据迁移：创建必要的表结构

### 向后兼容性
- 现有的 CLI 功能不受影响
- 现有的 SOUL 配置 API 保持兼容
- 已有用户数据（soul.meta.yaml）可继续使用
