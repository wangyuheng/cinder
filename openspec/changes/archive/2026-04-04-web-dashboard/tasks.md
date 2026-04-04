## 1. 项目结构和依赖

- [x] 1.1 创建 web 模块目录结构 (cinder_cli/web/)
- [x] 1.2 添加 FastAPI 和 uvicorn 依赖到 pyproject.toml
- [x] 1.3 创建 Next.js 前端项目 (cinder_cli/web/frontend/)
- [x] 1.4 配置 Tailwind CSS 和 shadcn/ui
- [x] 1.5 更新 .gitignore 添加 web 相关文件

## 2. 后端 API 服务

- [x] 2.1 创建 FastAPI 应用框架 (server.py)
- [x] 2.2 实现 CORS 配置
- [x] 2.3 实现错误处理中间件
- [x] 2.4 实现执行历史 API (api/executions.py)
- [x] 2.5 实现 Soul 配置 API (api/soul.py)
- [x] 2.6 实现决策记录 API (api/decisions.py)
- [x] 2.7 实现任务触发 API (api/tasks.py)
- [x] 2.8 实现 API 文档 (OpenAPI/Swagger)

## 3. 前端页面开发

- [x] 3.1 创建布局组件 (layout.tsx)
- [x] 3.2 创建仪表盘首页 (app/page.tsx)
- [x] 3.3 创建执行历史页面 (app/executions/page.tsx)
- [x] 3.4 创建执行详情页面 (app/executions/[id]/page.tsx)
- [x] 3.5 创建 Soul 配置页面 (app/soul/page.tsx)
- [x] 3.6 创建决策记录页面 (app/decisions/page.tsx)
- [x] 3.7 创建任务触发页面 (app/tasks/page.tsx)

## 4. 前端组件开发

- [x] 4.1 创建 UI 组件库 (components/ui/)
- [x] 4.2 创建仪表盘卡片组件 (components/dashboard/stats-card.tsx)
- [x] 4.3 创建执行列表组件 (components/executions/list.tsx)
- [x] 4.4 创建执行详情组件 (components/executions/detail.tsx)
- [x] 4.5 创建 Soul 配置表单组件 (components/soul/form.tsx)
- [x] 4.6 创建决策列表组件 (components/decisions/list.tsx)
- [x] 4.7 创建主题切换组件 (components/theme-toggle.tsx)

## 5. API 集成

- [x] 5.1 创建 API 客户端 (lib/api.ts)
- [x] 5.2 实现执行历史数据获取
- [x] 5.3 实现 Soul 配置数据获取和更新
- [x] 5.4 实现决策记录数据获取
- [x] 5.5 实现任务触发功能
- [x] 5.6 实现错误处理和重试逻辑

## 6. CLI 命令集成

- [x] 6.1 添加 `cinder server` 命令
- [x] 6.2 实现端口配置和检测
- [x] 6.3 实现自动打开浏览器功能
- [x] 6.4 实现前后端同时启动
- [x] 6.5 添加停止服务功能

## 7. 测试

- [x] 7.1 编写后端 API 单元测试
- [x] 7.2 编写前端组件测试
- [x] 7.3 编写 E2E 测试
- [x] 7.4 测试响应式布局
- [x] 7.5 测试暗色/亮色主题切换

## 8. 文档

- [x] 8.1 更新 README.md 添加 Web 界面说明
- [x] 8.2 创建 Web 界面使用指南
- [x] 8.3 创建 API 文档
- [x] 8.4 创建部署指南
