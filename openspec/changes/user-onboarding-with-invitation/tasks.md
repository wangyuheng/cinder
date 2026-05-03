## 1. 数据库初始化

- [x] 1.1 创建数据库模型文件 (cinder_cli/database/models.py)
- [x] 1.2 定义 User 模型（id、name、created_at、soul_path、onboarding_completed）
- [x] 1.3 定义 InvitationCode 模型（code、is_single_use、used_count、max_uses、created_at、is_active）
- [x] 1.4 定义 UserSession 模型（session_id、user_id、created_at、expires_at）
- [x] 1.5 定义 QuestionnaireAnswer 模型（id、user_id、question_key、choice、reason、created_at）
- [x] 1.6 创建数据库初始化脚本 (cinder_cli/database/init_db.py)
- [x] 1.7 实现数据库连接管理器 (cinder_cli/database/connection.py)
- [x] 1.8 配置数据库路径（默认 ~/.cinder/cinder.db）
- [x] 1.9 编写数据库初始化单元测试

## 2. 邀请码管理

- [x] 2.1 创建邀请码配置文件模板 (examples/invitations.yaml)
- [x] 2.2 实现邀请码加载器 (cinder_cli/invitation/loader.py)
- [x] 2.3 实现邀请码验证器 (cinder_cli/invitation/validator.py)
- [x] 2.4 实现邀请码使用记录功能
- [x] 2.5 编写邀请码验证单元测试
- [x] 2.6 编写邀请码加载单元测试

## 3. 用户管理 API

- [x] 3.1 创建用户 API 路由文件 (cinder_cli/web/api/users.py)
- [x] 3.2 实现 POST /api/users 端点（创建用户）
- [x] 3.3 实现 GET /api/users/me 端点（获取当前用户信息）
- [x] 3.4 实现用户数据访问层 (cinder_cli/database/user_dao.py)
- [x] 3.5 添加用户创建验证（姓名长度 1-50 字符）
- [x] 3.6 编写用户 API 单元测试

## 4. 邀请码验证 API

- [x] 4.1 创建邀请码 API 路由文件 (cinder_cli/web/api/invitations.py)
- [x] 4.2 实现 POST /api/invitations/validate 端点
- [x] 4.3 实现邀请码验证逻辑
- [x] 4.4 返回适当的错误消息（无效、已禁用、已使用、达到上限）
- [x] 4.5 编写邀请码 API 单元测试

## 5. SOUL 问卷 API

- [x] 5.1 扩展现有 soul API 文件 (cinder_cli/web/api/soul.py)
- [x] 5.2 实现 GET /api/soul/questionnaire 端点（获取问卷问题）
- [x] 5.3 实现 POST /api/soul/questionnaire 端点（提交问卷答案）
- [x] 5.4 实现 GET /api/soul/questionnaire/progress 端点（获取问卷进度）
- [x] 5.5 实现 DELETE /api/soul/questionnaire/progress 端点（清除问卷进度）
- [x] 5.6 实现问卷答案数据访问层 (cinder_cli/database/questionnaire_dao.py)
- [x] 5.7 实现特质分数计算逻辑（复用 question_guide.py 的逻辑）
- [x] 5.8 实现 soul.md 和 soul.meta.yaml 文件生成
- [x] 5.9 编写问卷 API 单元测试

## 6. 会话管理

- [x] 6.1 创建会话管理模块 (cinder_cli/web/session.py)
- [x] 6.2 实现会话创建功能（生成 UUID v4）
- [x] 6.3 实现会话验证功能
- [x] 6.4 实现会话清理功能（删除过期会话）
- [x] 6.5 创建会话中间件 (cinder_cli/web/middleware/session.py)
- [x] 6.6 实现会话 Cookie 设置（HttpOnly、Secure、过期时间）
- [x] 6.7 实现会话数据访问层 (cinder_cli/database/session_dao.py)
- [x] 6.8 编写会话管理单元测试

## 7. 访问控制中间件

- [x] 7.1 创建引导流程检查中间件 (cinder_cli/web/middleware/onboarding.py)
- [x] 7.2 实现引导流程状态检查逻辑
- [x] 7.3 配置公开路由列表（/onboarding、/api/invitations、/api/health）
- [x] 7.4 实现未授权访问重定向逻辑
- [x] 7.5 集成会话验证和引导流程检查
- [x] 7.6 编写中间件单元测试

## 8. 前端 - 邀请码验证页面

- [x] 8.1 创建邀请码验证页面 (cinder_cli/web/frontend/app/onboarding/invitation/page.tsx)
- [x] 8.2 实现邀请码输入表单组件
- [x] 8.3 实现邀请码验证 API 调用
- [x] 8.4 实现验证成功后的跳转逻辑
- [x] 8.5 实现错误消息显示
- [x] 8.6 添加页面样式（使用 Tailwind CSS）

## 9. 前端 - 用户信息填写页面

- [x] 9.1 创建用户信息填写页面 (cinder_cli/web/frontend/app/onboarding/profile/page.tsx)
- [x] 9.2 实现姓名输入表单组件
- [x] 9.3 实现用户创建 API 调用
- [x] 9.4 实现表单验证（姓名长度 1-50 字符）
- [x] 9.5 实现提交成功后的跳转逻辑
- [x] 9.6 添加页面样式

## 10. 前端 - SOUL 问卷页面

- [x] 10.1 创建问卷页面 (cinder_cli/web/frontend/app/onboarding/questionnaire/page.tsx)
- [x] 10.2 实现问题展示组件（显示标题、提示、选项）
- [x] 10.3 实现选项选择组件（单选按钮）
- [x] 10.4 实现原因输入组件（可选）
- [x] 10.5 实现进度指示器组件（问题 X/6）
- [x] 10.6 实现上一题/下一题导航按钮
- [x] 10.7 实现问卷进度保存和恢复
- [x] 10.8 实现问卷提交 API 调用
- [x] 10.9 实现问卷完成后的跳转逻辑
- [x] 10.10 添加页面样式和动画效果

## 11. 前端 - 路由守卫

- [x] 11.1 创建 Next.js 中间件文件 (cinder_cli/web/frontend/middleware.ts)
- [x] 11.2 实现会话检查逻辑
- [x] 11.3 实现引导流程状态检查逻辑
- [x] 11.4 配置公开路由和受保护路由
- [x] 11.5 实现重定向逻辑
- [x] 11.6 测试路由守卫功能

## 12. 前端 - API 客户端更新

- [x] 12.1 更新 API 客户端 (cinder_cli/web/frontend/lib/api.ts)
- [x] 12.2 添加邀请码验证 API 调用函数
- [x] 12.3 添加用户管理 API 调用函数
- [x] 12.4 添加问卷相关 API 调用函数
- [x] 12.5 实现会话 Cookie 处理

## 13. 服务器集成

- [x] 13.1 更新 FastAPI 服务器配置 (cinder_cli/web/server.py)
- [x] 13.2 注册新的 API 路由（invitations、users）
- [x] 13.3 添加会话中间件
- [x] 13.4 添加引导流程检查中间件
- [x] 13.5 配置数据库初始化（启动时创建表）
- [x] 13.6 更新 CORS 配置（允许 Cookie）

## 14. 配置管理

- [x] 14.1 更新配置文件格式 (cinder_cli/config.py)
- [x] 14.2 添加数据库路径配置项
- [x] 14.3 添加会话过期时间配置项
- [x] 14.4 添加邀请码配置文件路径配置项
- [x] 14.5 创建默认配置文件模板

## 15. 集成测试

- [x] 15.1 编写端到端引导流程测试
- [x] 15.2 测试邀请码验证流程
- [x] 15.3 测试用户信息填写流程
- [x] 15.4 测试问卷完成流程
- [x] 15.5 测试会话管理功能
- [x] 15.6 测试访问控制功能
- [x] 15.7 测试问卷进度保存和恢复
- [x] 15.8 测试个性化画像生成

## 16. 文档和示例

- [ ] 16.1 更新 README 文档
- [ ] 16.2 编写用户引导流程使用指南
- [ ] 16.3 编写邀请码管理文档
- [ ] 16.4 创建示例邀请码配置文件
- [ ] 16.5 编写 API 文档
- [ ] 16.6 更新架构文档

## 17. 部署和迁移

- [x] 17.1 编写数据库迁移脚本
- [x] 17.2 测试向后兼容性（现有 soul.meta.yaml 文件）
- [x] 17.3 编写回滚脚本
- [ ] 17.4 测试生产环境部署
- [ ] 17.5 编写部署检查清单
