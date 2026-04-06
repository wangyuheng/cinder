# Service Management Scripts

这个目录包含用于管理 Cinder 外部依赖的脚本。

## services.py

管理外部服务（Ollama 和 Phoenix）。

### 用法

```bash
# 检查所有服务状态
python scripts/services.py status

# 启动 Phoenix 服务器
python scripts/services.py start-phoenix

# 停止 Phoenix 服务器
python scripts/services.py stop-phoenix

# 检查服务（返回 JSON，用于自动化）
python scripts/services.py check
```

### 命令说明

#### `status`

显示所有外部服务的详细状态信息：

- **Ollama**: 检查是否运行，显示可用模型数量
- **Docker**: 检查是否可用
- **Phoenix**: 检查是否运行，显示容器状态

示例输出：
```
============================================================
Service Status
============================================================

[Ollama]
  Status: ✓ Running
  URL: http://localhost:11434
  Models: 3

[Docker]
  Status: ✓ Available

[Phoenix]
  Status: ✓ Running
  URL: http://localhost:6006
  Container: cinder-phoenix

============================================================
```

#### `start-phoenix`

通过 Docker 启动 Phoenix 服务器：

1. 检查 Docker 是否可用
2. 检查 Phoenix 是否已运行
3. 拉取 Phoenix Docker 镜像（如果需要）
4. 启动 Phoenix 容器
5. 等待服务就绪

Docker 镜像：`arizephoenix/phoenix:latest`
容器名称：`cinder-phoenix`

#### `stop-phoenix`

停止并移除 Phoenix 容器。

#### `check`

返回 JSON 格式的服务状态，用于自动化脚本：

```json
{
  "ollama": {
    "running": true,
    "url": "http://localhost:11434",
    "models": 3
  },
  "phoenix": {
    "running": true,
    "url": "http://localhost:6006",
    "container": "cinder-phoenix"
  },
  "docker": true
}
```

退出码：
- 0: 所有服务运行正常
- 1: 有服务未运行

### 通过 CLI 使用

也可以通过 Cinder CLI 调用这些功能：

```bash
# 检查服务状态
cinder service status

# 启动 Phoenix
cinder service start-phoenix

# 停止 Phoenix
cinder service stop-phoenix

# 检查 Phoenix 状态
cinder phoenix status
```

### 外部依赖说明

#### Ollama

- **用途**: LLM 推理引擎
- **安装**: https://ollama.ai/
- **启动**: `ollama serve`
- **检测**: `GET http://localhost:11434/api/tags`

#### Phoenix

- **用途**: Trace 可视化平台
- **运行方式**: Docker 容器
- **镜像**: `arizephoenix/phoenix:latest`
- **端口**: 6006
- **数据卷**: `phoenix-data:/root/.phoenix`

### 手动管理 Docker

如果需要手动管理 Phoenix Docker 容器：

```bash
# 查看容器状态
docker ps -a | grep cinder-phoenix

# 查看容器日志
docker logs cinder-phoenix

# 手动启动容器
docker run -d \
  --name cinder-phoenix \
  -p 6006:6006 \
  -v phoenix-data:/root/.phoenix \
  arizephoenix/phoenix:latest

# 手动停止容器
docker stop cinder-phoenix

# 手动删除容器
docker rm cinder-phoenix

# 查看数据卷
docker volume ls | grep phoenix

# 删除数据卷（会清除所有 trace 数据）
docker volume rm phoenix-data
```

### 故障排查

#### Ollama 未运行

```
[Ollama]
  Status: ✗ Not Running
  URL: http://localhost:11434
  Start: ollama serve
```

解决方法：
```bash
ollama serve
```

#### Docker 未安装

```
[Docker]
  Status: ✗ Not Available
```

解决方法：
1. 安装 Docker: https://docs.docker.com/get-docker/
2. 启动 Docker Desktop 或 Docker daemon

#### Phoenix 启动失败

检查 Docker 日志：
```bash
docker logs cinder-phoenix
```

常见问题：
- 端口被占用：`lsof -i :6006`
- 镜像拉取失败：检查网络连接
- 容器启动失败：检查 Docker 资源限制

### 自动化示例

在 CI/CD 或自动化脚本中使用：

```bash
#!/bin/bash

# 检查服务状态
if ! python scripts/services.py check; then
    echo "Services not ready"
    exit 1
fi

# 启动 Phoenix（如果未运行）
python scripts/services.py start-phoenix

# 运行测试
pytest tests/

# 停止 Phoenix
python scripts/services.py stop-phoenix
```
