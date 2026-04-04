## Why

Cinder 目前是纯命令行工具，缺少可视化界面来管理和监控执行历史、Soul 配置和决策记录。用户需要通过命令行查看信息，体验不够直观。添加 Web 管理界面可以提升用户体验，让数据可视化更清晰，操作更便捷。

## What Changes

- 新增 `cinder server` 命令，启动本地 Web 服务
- 创建 Next.js 前端应用，提供现代化 Web UI
- 实现执行历史查看页面，支持列表、详情、统计
- 实现 Soul 配置管理页面，支持查看和编辑
- 实现执行任务触发页面，支持手动触发新任务
- 实现决策记录查看页面，支持列表和详情
- 采用极简现代风格设计 (Vercel/Linear 风格)

## Capabilities

### New Capabilities

- `web-dashboard`: Web 管理界面，提供执行历史、Soul 配置、任务触发、决策记录的可视化管理
- `api-server`: 后端 API 服务，提供 RESTful 接口供前端调用

### Modified Capabilities

无

## Impact

- 新增 `cinder_cli/web/` 目录存放 Web 相关代码
- 新增 `cinder server` CLI 命令
- 新增依赖: FastAPI (后端), next.js (前端)
- 现有功能不受影响，Web 界面为可选功能
- 本地服务默认端口: 3000 (前端), 8000 (后端 API)
