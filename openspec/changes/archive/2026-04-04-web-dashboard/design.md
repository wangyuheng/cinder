## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cinder Web Dashboard                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────┐         ┌─────────────────┐              │
│   │   Next.js App   │ ◄─────► │   FastAPI       │              │
│   │   (Port 3000)   │  HTTP   │   (Port 8000)   │              │
│   └─────────────────┘         └────────┬────────┘              │
│                                        │                        │
│                                        ▼                        │
│   ┌─────────────────────────────────────────────────────┐      │
│   │              Existing Cinder Modules                │      │
│   │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │      │
│   │  │ ExecutionLog │  │   Config     │  │ DecisionDB│  │      │
│   │  └──────────────┘  └──────────────┘  └───────────┘  │      │
│   └─────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (极简现代风格)
- **State**: React Query (数据获取)
- **Language**: TypeScript

### Backend
- **Framework**: FastAPI
- **Template Engine**: Jinja2 (可选 SSR)
- **API Documentation**: OpenAPI/Swagger

### Integration
- 复用现有 `ExecutionLogger`, `Config`, `DecisionDatabase`
- 通过 Python API 直接调用，无需额外数据层

## Directory Structure

```
cinder_cli/
├── web/
│   ├── __init__.py
│   ├── server.py          # FastAPI 应用
│   ├── api/
│   │   ├── __init__.py
│   │   ├── executions.py  # 执行历史 API
│   │   ├── soul.py        # Soul 配置 API
│   │   ├── decisions.py   # 决策记录 API
│   │   └── tasks.py       # 任务触发 API
│   └── frontend/          # Next.js 应用 (可选: 独立仓库)
│       ├── app/
│       │   ├── page.tsx           # 首页仪表盘
│       │   ├── executions/
│       │   │   ├── page.tsx       # 执行列表
│       │   │   └── [id]/page.tsx  # 执行详情
│       │   ├── soul/
│       │   │   └── page.tsx       # Soul 配置
│       │   └── decisions/
│       │       └── page.tsx       # 决策记录
│       ├── components/
│       │   ├── ui/                # shadcn/ui 组件
│       │   ├── layout.tsx         # 布局组件
│       │   └── dashboard.tsx      # 仪表盘组件
│       └── lib/
│           └── api.ts             # API 客户端
```

## API Design

### Executions

```
GET    /api/executions           # 获取执行列表
GET    /api/executions/{id}      # 获取执行详情
POST   /api/executions           # 触发新执行
DELETE /api/executions/{id}      # 删除执行记录
GET    /api/executions/stats     # 获取执行统计
```

### Soul Configuration

```
GET    /api/soul                 # 获取 Soul 配置
PUT    /api/soul                 # 更新 Soul 配置
POST   /api/soul/init            # 初始化 Soul
```

### Decisions

```
GET    /api/decisions            # 获取决策列表
GET    /api/decisions/{id}       # 获取决策详情
GET    /api/decisions/stats      # 获取决策统计
```

## UI Design

### Design Principles
- **极简现代**: Vercel/Linear 风格，大量留白
- **暗色主题**: 默认暗色，支持亮色切换
- **响应式**: 支持桌面和移动端
- **快速**: 使用 SWR/React Query 优化数据加载

### Page Layout

```
┌────────────────────────────────────────────────────────────┐
│  Cinder Dashboard                    [🌙] [⚙️] [👤]        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 执行次数  │ │ 成功率   │ │ 决策数   │ │ 文件数   │      │
│  │   42     │ │  95%    │ │   128    │ │   156    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Recent Executions                      │  │
│  │  ─────────────────────────────────────────────────  │  │
│  │  ● 创建记账Web应用        2024-01-15  success       │  │
│  │  ● Python脚本生成         2024-01-14  success       │  │
│  │  ● API接口开发            2024-01-13  failed        │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Backend API (优先)
1. 创建 FastAPI 应用结构
2. 实现执行历史 API
3. 实现 Soul 配置 API
4. 实现决策记录 API

### Phase 2: Frontend (次优先)
1. 初始化 Next.js 项目
2. 配置 Tailwind + shadcn/ui
3. 实现页面组件
4. 集成 API

### Phase 3: CLI Integration
1. 添加 `cinder server` 命令
2. 配置端口和启动逻辑
3. 添加文档

## Configuration

```yaml
# ~/.cinder/config.yaml
web:
  enabled: true
  host: "localhost"
  frontend_port: 3000
  backend_port: 8000
  auto_open: true  # 启动时自动打开浏览器
```

## Risks and Mitigations

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| 端口冲突 | 低 | 支持配置端口，自动检测可用端口 |
| 大数据量加载慢 | 中 | 分页、虚拟滚动、缓存 |
| 前后端分离复杂 | 中 | 可选: 使用 Jinja2 SSR 简化 |
