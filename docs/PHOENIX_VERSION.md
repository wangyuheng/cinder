# Phoenix 版本管理

## 当前版本

Cinder 默认使用 **Phoenix latest** 版本（当前最新版本：13.23.0+）

## 版本选择

### 使用最新版本（推荐）

默认配置使用 `arizephoenix/phoenix:latest`，会自动使用最新稳定版本。

### 指定特定版本

如果需要使用特定版本，可以通过环境变量设置：

```bash
# 使用环境变量
export PHOENIX_DOCKER_IMAGE=arizephoenix/phoenix:version-13.23.0

# 启动 Phoenix
make start

# 或直接运行脚本
PHOENIX_DOCKER_IMAGE=arizephoenix/phoenix:version-13.23.0 ./scripts/services.sh start-phoenix
```

### 可用版本标签

| 标签 | 说明 |
|------|------|
| `latest` | 最新稳定版本（推荐） |
| `version-X.X.X` | 特定版本，如 `version-13.23.0` |
| `latest-nonroot` | 最新版本（非 root 权限） |
| `latest-debug` | 最新版本（调试模式） |

## 版本兼容性

### Phoenix 13.x 特性

Phoenix 13.x 版本包含以下新特性：

- **增强的 Tracing**: 更强大的 OpenTelemetry 支持
- **改进的 UI**: 更好的用户体验
- **性能优化**: 更快的查询和响应
- **新功能**: Prompt 管理、数据集版本控制等

### 版本升级

如果从旧版本升级：

```bash
# 1. 停止旧版本
make stop

# 2. 清理数据（可选）
docker volume rm phoenix-data

# 3. 启动新版本
make start
```

## 配置示例

### Makefile 中指定版本

```makefile
# 在 Makefile 顶部添加
PHOENIX_DOCKER_IMAGE ?= arizephoenix/phoenix:version-13.23.0
```

### Shell 脚本中指定版本

```bash
# 在脚本开头设置
export PHOENIX_DOCKER_IMAGE="arizephoenix/phoenix:version-13.23.0"
```

### Docker Compose 中指定版本

```yaml
services:
  phoenix:
    image: arizephoenix/phoenix:version-13.23.0
    ports:
      - "6006:6006"
      - "4317:4317"
```

## 版本检查

### 查看当前运行的版本

```bash
# 查看容器信息
docker inspect cinder-phoenix | grep Image

# 或查看 Phoenix UI
open http://localhost:6006
# 在 UI 右下角查看版本号
```

### 查看可用版本

```bash
# 查看 Docker Hub 上的标签
# https://hub.docker.com/r/arizephoenix/phoenix/tags
```

## 故障排查

### 版本不兼容

如果遇到版本不兼容问题：

1. **检查版本**:
   ```bash
   docker logs cinder-phoenix | grep version
   ```

2. **清理并重新启动**:
   ```bash
   make clean
   make start
   ```

3. **使用稳定版本**:
   ```bash
   PHOENIX_DOCKER_IMAGE=arizephoenix/phoenix:version-13.23.0 make start
   ```

### 数据迁移

如果需要保留数据升级版本：

```bash
# 1. 备份数据
docker run --rm -v phoenix-data:/data -v $(pwd):/backup alpine tar czf /backup/phoenix-backup.tar.gz /data

# 2. 升级版本
make stop
make start

# 3. 恢复数据（如需要）
docker run --rm -v phoenix-data:/data -v $(pwd):/backup alpine tar xzf /backup/phoenix-backup.tar.gz -C /
```

## 最佳实践

1. **生产环境**: 使用特定版本标签（如 `version-13.23.0`）
2. **开发环境**: 使用 `latest` 获取最新功能
3. **测试环境**: 与生产环境保持一致

## 相关链接

- [Phoenix GitHub](https://github.com/Arize-AI/phoenix)
- [Phoenix Docker Hub](https://hub.docker.com/r/arizephoenix/phoenix)
- [Phoenix 文档](https://docs.arize.com/phoenix)
- [Phoenix 更新日志](https://github.com/Arize-AI/phoenix/releases)
