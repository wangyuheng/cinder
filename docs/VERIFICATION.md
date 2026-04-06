# 验证路径

## 快速验证（5分钟）

### 1. 检查服务状态

```bash
# 查看所有外部服务状态
cinder service status
```

预期输出：
```
============================================================
Service Status
============================================================

[Ollama]
  Status: ✓ Running
  URL: http://localhost:11434
  Models: X

[Docker]
  Status: ✓ Available

[Phoenix]
  Status: ✗ Not Running
  URL: http://localhost:6006
  Start: cinder service start-phoenix

============================================================
```

### 2. 启动 Phoenix

```bash
# 启动 Phoenix（首次会拉取 Docker 镜像）
cinder service start-phoenix
```

预期输出：
```
Pulling Phoenix Docker image: arizephoenix/phoenix:latest
...
Starting Phoenix container: cinder-phoenix

✓ Phoenix started successfully
  URL: http://localhost:6006
```

### 3. 验证 Phoenix 运行

```bash
# 检查 Phoenix 状态
cinder phoenix status

# 或访问 Web UI
open http://localhost:6006
```

### 4. 执行任务生成 Trace

```bash
# 执行一个简单任务
cinder execute "创建一个 Python Hello World 程序"
```

### 5. 查看 Trace 数据

```bash
# 列出最近的 trace
cinder trace list

# 查看具体 trace（替换 <trace-id>）
cinder trace show <trace-id>
```

### 6. 清理

```bash
# 停止 Phoenix
cinder service stop-phoenix
```

## 完整验证流程

### 前置条件检查

```bash
# 1. 检查 Docker
docker --version
docker info

# 2. 检查 Ollama
ollama --version
curl http://localhost:11434/api/tags

# 3. 如果 Ollama 未运行，启动它
ollama serve
```

### 服务管理验证

```bash
# 1. 检查服务状态
cinder service status

# 2. 启动 Phoenix
cinder service start-phoenix

# 3. 再次检查状态（应该显示 Phoenix 运行中）
cinder service status

# 4. 检查 Phoenix 详细状态
cinder phoenix status

# 5. 检查 Docker 容器
docker ps | grep cinder-phoenix

# 6. 查看容器日志
docker logs cinder-phoenix
```

### Trace 功能验证

```bash
# 1. 执行任务
cinder execute "创建一个计算器程序" --language python

# 2. 查看 trace 列表
cinder trace list --limit 10

# 3. 查看具体 trace（使用上面命令返回的 trace-id）
cinder trace show <trace-id> --format json

# 4. 查看 trace 统计
cinder trace stats

# 5. 搜索 trace
cinder trace search --query "计算器"

# 6. 导出 trace
cinder trace export <trace-id> --format json --output trace.json
cat trace.json

# 7. 导出所有 trace
cinder trace export --all --format json
```

### Phoenix UI 验证

```bash
# 1. 打开 Phoenix UI
open http://localhost:6006

# 2. 在 UI 中验证：
#    - 能看到 trace 数据
#    - 能看到 span 详情
#    - 能看到 LLM 调用信息
#    - 能看到 token 使用量
```

### 配置验证

```bash
# 1. 查看当前配置
cinder trace config --show

# 2. 禁用 tracing
cinder trace config --disable

# 3. 启用 tracing
cinder trace config --enable

# 4. 设置 endpoint（可选）
cinder trace config --endpoint http://localhost:6006
```

### 清理验证

```bash
# 1. 查看会删除哪些 trace（不实际删除）
cinder trace clean --older-than 30 --dry-run

# 2. 清理并备份
cinder trace clean --older-than 30 --backup

# 3. 停止 Phoenix
cinder service stop-phoenix

# 4. 验证容器已停止
docker ps -a | grep cinder-phoenix
```

## 脚本直接使用验证

```bash
# 1. 使用脚本检查状态
python scripts/services.py status

# 2. 使用脚本启动 Phoenix
python scripts/services.py start-phoenix

# 3. 使用脚本检查（JSON 输出）
python scripts/services.py check

# 4. 使用脚本停止 Phoenix
python scripts/services.py stop-phoenix
```

## 故障排查验证

### 场景 1: Docker 未运行

```bash
# 停止 Docker Desktop
# 然后尝试启动 Phoenix
cinder service start-phoenix

# 预期输出：错误提示 Docker 未运行
```

### 场景 2: Ollama 未运行

```bash
# 停止 Ollama
pkill ollama

# 检查状态
cinder service status

# 预期输出：Ollama 未运行
```

### 场景 3: 端口被占用

```bash
# 手动占用端口
python -m http.server 6006

# 尝试启动 Phoenix
cinder service start-phoenix

# 预期输出：启动失败，端口被占用
```

## 自动化脚本验证

创建测试脚本 `test_services.sh`:

```bash
#!/bin/bash

echo "Testing service management..."

# 检查服务
if ! python scripts/services.py check; then
    echo "Services not ready, starting..."
    python scripts/services.py start-phoenix
fi

# 等待服务就绪
sleep 5

# 运行测试
echo "Running tests..."
pytest tests/test_tracing.py

# 清理
echo "Cleaning up..."
python scripts/services.py stop-phoenix

echo "Done!"
```

运行：
```bash
chmod +x test_services.sh
./test_services.sh
```

## 验证清单

- [ ] Docker 已安装并运行
- [ ] Ollama 已安装并运行
- [ ] `cinder service status` 显示正确状态
- [ ] `cinder service start-phoenix` 成功启动 Phoenix
- [ ] Phoenix UI 可访问 (http://localhost:6006)
- [ ] 执行任务能生成 trace 数据
- [ ] `cinder trace list` 显示 trace 列表
- [ ] `cinder trace show` 显示 trace 详情
- [ ] `cinder trace stats` 显示统计信息
- [ ] `cinder trace export` 能导出数据
- [ ] `cinder service stop-phoenix` 成功停止 Phoenix
- [ ] 脚本 `scripts/services.py` 所有命令正常工作

## 常见问题

### Q1: Phoenix 启动很慢？

A: 首次启动需要拉取 Docker 镜像（约 500MB），可能需要几分钟。后续启动会很快。

### Q2: 看不到 trace 数据？

A: 检查：
1. Phoenix 是否运行：`cinder phoenix status`
2. Trace 目录是否有数据：`ls ~/.cinder/traces/`
3. Tracing 是否启用：`cinder trace config --show`

### Q3: 端口被占用怎么办？

A: 
```bash
# 查看占用端口的进程
lsof -i :6006

# 停止占用端口的进程
kill -9 <PID>
```

### Q4: 如何查看详细日志？

A:
```bash
# Phoenix 容器日志
docker logs cinder-phoenix

# Cinder 日志
tail -f ~/.cinder/cinder.log
```

## 下一步

验证通过后，可以：

1. **开始使用**: 正常使用 Cinder 执行任务
2. **配置优化**: 根据需求调整 tracing 配置
3. **集成到 CI/CD**: 在自动化流程中使用服务管理脚本
4. **监控设置**: 设置定期检查服务状态的定时任务
