# Cinder Web Dashboard

Cinder Web Dashboard 是一个现代化的 Web 管理界面，用于可视化管理执行历史、Soul 配置、决策记录和任务触发。

## 快速开始

### 一键启动（推荐）

使用启动脚本自动启动前后端服务：

```bash
# 基本启动
./scripts/start-web.sh

# 自定义端口
./scripts/start-web.sh --backend-port 9000 --frontend-port 3001

# 自动打开浏览器
./scripts/start-web.sh --open

# 查看帮助
./scripts/start-web.sh --help
```

启动后会自动：
- ✅ 启动后端 API 服务（默认端口 8000）
- ✅ 启动前端开发服务器（默认端口 3000）
- ✅ 实时追踪日志（彩色输出）
- ✅ 通过颜色和前缀区分前后端日志

**日志输出示例：**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                           实时日志
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[BACKEND]  INFO:     Started server process [12345]      (明亮青色)
[FRONTEND] ready - started server on 0.0.0.0:3000       (明亮绿色)
```

按 `Ctrl+C` 可优雅停止所有服务。

### 单独启动服务

#### 启动后端 API

```bash
# 启动 API 服务 (默认端口 8000)
cinder server

# 指定端口
cinder server --port 9000

# 自动打开浏览器
cinder server --open
```

#### 启动前端

```bash
# 进入前端目录
cd cinder_cli/web/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 功能模块

### 仪表盘

- 执行统计概览
- 最近执行列表
- 快速操作入口

### 执行历史

- 查看所有执行记录
- 按状态筛选
- 查看执行详情
- 查看创建的文件

### Soul 配置

- 查看当前 Soul 配置
- 调整性格特质
- 保存配置更改

### 决策记录

- 查看所有决策历史
- 查看置信度分布
- 查看决策详情

### 任务触发

- 手动触发新执行
- 选择执行模式
- 查看执行结果

## API 端点

### 执行历史

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/executions` | 获取执行列表 |
| GET | `/api/executions/{id}` | 获取执行详情 |
| GET | `/api/executions/stats` | 获取执行统计 |
| DELETE | `/api/executions/{id}` | 删除执行记录 |

### Soul 配置

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/soul` | 获取 Soul 配置 |
| PUT | `/api/soul` | 更新 Soul 配置 |
| POST | `/api/soul/init` | 初始化 Soul |

### 决策记录

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/decisions` | 获取决策列表 |
| GET | `/api/decisions/{id}` | 获取决策详情 |
| GET | `/api/decisions/stats` | 获取决策统计 |

### 任务触发

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/tasks` | 触发新任务 |
| GET | `/api/tasks/modes` | 获取可用模式 |

## 技术栈

### 后端

- **FastAPI** - 现代 Python Web 框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证

### 前端

- **Next.js 14** - React 框架
- **Tailwind CSS** - 样式框架
- **React Query** - 数据获取
- **Lucide Icons** - 图标库

## 配置

在 `~/.cinder/config.yaml` 中配置 Web 服务：

```yaml
web:
  enabled: true
  host: "localhost"
  frontend_port: 3000
  backend_port: 8000
  auto_open: true
```

## 开发

### 项目结构

```
cinder_cli/web/
├── __init__.py
├── server.py           # FastAPI 应用
└── api/
    ├── __init__.py
    ├── executions.py   # 执行历史 API
    ├── soul.py         # Soul 配置 API
    ├── decisions.py    # 决策记录 API
    └── tasks.py        # 任务触发 API

cinder_cli/web/frontend/
├── app/
│   ├── page.tsx        # 首页
│   ├── executions/     # 执行历史页面
│   ├── soul/           # Soul 配置页面
│   ├── decisions/      # 决策记录页面
│   └── tasks/          # 任务触发页面
└── components/
    ├── layout.tsx      # 布局组件
    ├── dashboard/      # 仪表盘组件
    └── theme-toggle.tsx # 主题切换
```

### 运行测试

```bash
# 运行 API 测试
pytest tests/test_web_api.py -v

# 运行所有测试
pytest tests/ -v
```

## 故障排除

### 端口被占用

```bash
# 检查端口占用
lsof -i :8000

# 使用其他端口
cinder server --port 9000
```

### 前端无法连接后端

检查 API 地址配置是否正确，默认为 `http://localhost:8000`。

### 数据不显示

确保已执行过 `cinder execute` 命令，数据库中有执行记录。
