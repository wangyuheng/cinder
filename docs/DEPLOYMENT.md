# Cinder Web Dashboard 部署指南

## 本地开发

### 后端服务

```bash
# 安装依赖
pip install -e .

# 启动 API 服务
cinder server

# 或指定端口
cinder server --port 9000
```

### 前端开发

```bash
# 进入前端目录
cd cinder_cli/web/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm run start
```

## 生产部署

### 方案一：独立部署

#### 后端部署

```bash
# 使用 uvicorn 直接运行
uvicorn cinder_cli.web.server:create_app --factory --host 0.0.0.0 --port 8000

# 使用 gunicorn + uvicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker cinder_cli.web.server:create_app --factory
```

#### 前端部署

```bash
# 构建
cd cinder_cli/web/frontend
npm run build

# 使用 nginx 托管静态文件
# 或使用 next.js 内置服务器
npm run start
```

### 方案二：Docker 部署

创建 `Dockerfile`:

```dockerfile
# 后端
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["uvicorn", "cinder_cli.web.server:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

创建 `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ~/.cinder:/root/.cinder

  frontend:
    build: ./cinder_cli/web/frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### 方案三：反向代理

使用 Nginx 作为反向代理：

```nginx
server {
    listen 80;
    server_name cinder.example.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 环境变量配置

```bash
# 后端配置
export CINDER_HOST=0.0.0.0
export CINDER_PORT=8000

# 前端配置
export NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 安全配置

### 生产环境建议

1. **启用 HTTPS**: 使用 Let's Encrypt 或其他 SSL 证书
2. **限制访问**: 使用防火墙限制访问 IP
3. **认证**: 添加用户认证机制（可选）
4. **CORS**: 配置正确的 CORS 策略

### 修改 CORS 配置

编辑 `cinder_cli/web/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # 替换为实际域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 性能优化

### 后端优化

```bash
# 使用多 worker
uvicorn cinder_cli.web.server:create_app --factory --workers 4

# 启用缓存
# 在代码中添加缓存逻辑
```

### 前端优化

```bash
# 启用静态导出
# next.config.js
module.exports = {
  output: 'export',
  images: {
    unoptimized: true,
  },
}
```

## 监控和日志

### 查看日志

```bash
# 后端日志
cinder server 2>&1 | tee server.log

# 使用 systemd 管理服务
journalctl -u cinder-server -f
```

### 健康检查

```bash
# API 健康检查
curl http://localhost:8000/api/health

# 前端健康检查
curl http://localhost:3000
```

## 故障排除

### 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000

# 终止进程
kill -9 <PID>
```

### 前端无法连接后端

1. 检查后端是否正常运行
2. 检查 CORS 配置
3. 检查 API 地址是否正确

### 数据不显示

1. 确保已执行过 `cinder execute`
2. 检查数据库文件是否存在
3. 检查文件权限
