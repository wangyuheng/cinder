# 服务管理改造总结

## 改造目标

将 Phoenix 和 Ollama 作为外部依赖处理，通过独立脚本管理服务启动和检测。

## 改造内容

### 1. 创建服务管理脚本

**文件**: `scripts/services.py`

**功能**:
- 检查 Ollama 服务状态
- 检查 Phoenix 服务状态
- 通过 Docker 启动/停止 Phoenix
- 提供统一的服务状态检查接口

**命令**:
```bash
python scripts/services.py status          # 查看所有服务状态
python scripts/services.py start-phoenix   # 启动 Phoenix
python scripts/services.py stop-phoenix    # 停止 Phoenix
python scripts/services.py check           # JSON 格式输出（用于自动化）
```

### 2. 更新 PhoenixServer 类

**文件**: `cinder_cli/tracing/phoenix_server.py`

**改动**:
- 移除自动启动 Docker 的逻辑
- 只保留服务状态检测功能
- 添加启动提示信息

**设计理念**:
- Phoenix 是外部依赖，不应由应用自动启动
- 用户需要显式启动服务：`cinder service start-phoenix`
- 应用只负责检测和使用服务

### 3. 添加 CLI 命令

**文件**: `cinder_cli/cli.py`

**新增命令**:
```bash
# 服务管理
cinder service status              # 检查所有服务状态
cinder service start-phoenix       # 启动 Phoenix
cinder service stop-phoenix        # 停止 Phoenix

# Phoenix 状态检查（只检测，不启动）
cinder phoenix start               # 检查是否运行
cinder phoenix stop                # 检查是否运行
cinder phoenix status              # 查看详细状态
```

### 4. 更新文档

**文件**: `docs/OBSERVABILITY.md`

**更新内容**:
- 添加 Ollama 安装说明
- 更新服务启动流程
- 更新 CLI 命令参考
- 强调外部依赖的概念

**新增文件**: `scripts/README.md`
- 详细说明服务管理脚本的使用方法
- 提供故障排查指南
- 提供自动化示例

## 架构设计

### 外部依赖管理

```
┌─────────────────────────────────────────┐
│         Cinder Application              │
│                                         │
│  ┌──────────────┐  ┌────────────────┐  │
│  │   Ollama     │  │    Phoenix     │  │
│  │  (External)  │  │   (External)   │  │
│  └──────────────┘  └────────────────┘  │
│         │                   │          │
│         │                   │          │
│         ▼                   ▼          │
│  ┌──────────────────────────────────┐  │
│  │      Service Detection Only      │  │
│  │  - Check if running              │  │
│  │  - Get service URL               │  │
│  │  - Report status                 │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      Service Management Script          │
│         (scripts/services.py)           │
│                                         │
│  - Start/Stop services                  │
│  - Pull Docker images                   │
│  - Manage containers                    │
│  - Check service health                 │
└─────────────────────────────────────────┘
```

### 服务启动流程

```
用户操作
    │
    ├─> ollama serve                    # 手动启动 Ollama
    │
    └─> cinder service start-phoenix    # 启动 Phoenix
            │
            ├─> 检查 Docker 是否可用
            ├─> 拉取 Phoenix 镜像
            ├─> 启动 Phoenix 容器
            └─> 等待服务就绪
```

### 应用使用流程

```
Cinder 应用启动
    │
    ├─> 检测 Ollama 是否运行
    │   └─> 未运行: 提示用户启动
    │
    └─> 检测 Phoenix 是否运行
        └─> 未运行: 提示用户启动
```

## 优势

### 1. 清晰的职责分离

- **应用层**: 只负责检测和使用服务
- **管理层**: 负责启动和管理服务
- **用户层**: 明确知道需要启动哪些服务

### 2. 更好的可维护性

- 服务管理逻辑集中在一个脚本中
- 应用代码不包含服务启动逻辑
- 更容易调试和排查问题

### 3. 灵活的部署选项

- 可以在不同机器上运行服务
- 支持远程 Phoenix 服务器
- 支持不同的 Docker 配置

### 4. 更好的用户体验

- 明确的错误提示
- 统一的状态检查命令
- 详细的故障排查文档

## 使用示例

### 开发环境

```bash
# 1. 启动服务
ollama serve &
cinder service start-phoenix

# 2. 检查状态
cinder service status

# 3. 使用 Cinder
cinder execute "创建一个计算器"

# 4. 停止服务
cinder service stop-phoenix
```

### CI/CD 环境

```bash
# 在 CI 脚本中
python scripts/services.py start-phoenix
python scripts/services.py check || exit 1

# 运行测试
pytest tests/

# 清理
python scripts/services.py stop-phoenix
```

### 生产环境

```bash
# 使用远程 Phoenix 服务器
export PHOENIX_ENDPOINT=http://phoenix.example.com:6006

# 或在配置文件中设置
# ~/.cinder/config.yaml
tracing:
  phoenix_endpoint: http://phoenix.example.com:6006
```

## Docker 配置

### Phoenix 容器

- **镜像**: `arizephoenix/phoenix:latest`
- **容器名**: `cinder-phoenix`
- **端口**: `6006:6006`
- **数据卷**: `phoenix-data:/root/.phoenix`

### 手动管理

```bash
# 查看容器
docker ps -a | grep cinder-phoenix

# 查看日志
docker logs cinder-phoenix

# 进入容器
docker exec -it cinder-phoenix /bin/bash

# 备份数据
docker run --rm -v phoenix-data:/data -v $(pwd):/backup alpine tar czf /backup/phoenix-backup.tar.gz /data
```

## 迁移指南

### 从旧版本迁移

如果你之前使用的是自动启动 Phoenix 的版本：

1. **停止旧的 Phoenix 进程**:
   ```bash
   # 如果有运行中的 Phoenix，先停止
   docker stop cinder-phoenix
   docker rm cinder-phoenix
   ```

2. **使用新的启动方式**:
   ```bash
   cinder service start-phoenix
   ```

3. **更新脚本和自动化流程**:
   - 将自动启动改为手动启动
   - 添加服务状态检查

### 更新配置

无需更新配置文件，现有配置完全兼容。

## 故障排查

### Phoenix 无法启动

1. 检查 Docker 是否运行:
   ```bash
   docker info
   ```

2. 检查端口是否被占用:
   ```bash
   lsof -i :6006
   ```

3. 查看容器日志:
   ```bash
   docker logs cinder-phoenix
   ```

### Ollama 未运行

```bash
# 启动 Ollama
ollama serve

# 检查是否运行
curl http://localhost:11434/api/tags
```

### 服务状态检查失败

```bash
# 详细检查
python scripts/services.py status

# 检查网络连接
curl http://localhost:6006/healthz
curl http://localhost:11434/api/tags
```

## 后续改进

### 可能的增强功能

1. **健康检查增强**:
   - 添加更详细的健康检查
   - 支持自定义健康检查端点

2. **多环境支持**:
   - 支持开发、测试、生产环境配置
   - 支持不同的 Phoenix 实例

3. **监控集成**:
   - 集成 Prometheus metrics
   - 添加告警机制

4. **自动恢复**:
   - 检测到服务停止时自动重启
   - 支持服务降级策略

## 总结

通过这次改造，我们实现了：

✅ 清晰的外部依赖管理
✅ 统一的服务启动流程
✅ 更好的用户体验
✅ 更容易维护的代码结构
✅ 灵活的部署选项

所有改动都向后兼容，现有用户可以无缝升级。
