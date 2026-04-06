# LLM Agent Observability

Cinder 提供了完整的 LLM Agent 可观测性解决方案，基于 Phoenix 进行 trace 数据的收集和可视化。

## 前置要求

### 外部依赖

Cinder 使用以下外部依赖：

1. **Ollama** - LLM 推理引擎
2. **Phoenix** - Trace 可视化平台（通过 Docker 运行）

### 安装 Docker

Phoenix 通过 Docker 运行，需要先安装 Docker：

- **安装 Docker**: https://docs.docker.com/get-docker/
- **验证安装**: 
  ```bash
  docker --version
  docker info
  ```

### 安装 Ollama

- **安装 Ollama**: https://ollama.ai/
- **启动 Ollama**: 
  ```bash
  ollama serve
  ```

## 快速开始

### 1. 检查服务状态

```bash
# 检查所有外部服务状态
cinder service status

# 或直接运行脚本
python scripts/services.py status
```

### 2. 启动 Phoenix 服务器

```bash
# 通过 CLI 启动 Phoenix
cinder service start-phoenix

# 或直接运行脚本
python scripts/services.py start-phoenix

# 检查 Phoenix 状态
cinder phoenix status

# 访问 Phoenix UI
open http://localhost:6006
```

### 3. 执行任务并记录 Trace

```bash
# 执行任务（自动记录 trace）
cinder execute "创建一个 Python Hello World 程序"

# 执行任务并指定语言
cinder execute "创建一个计算器" --language python
```

### 4. 查看 Trace 数据

```bash
# 列出最近的 trace
cinder trace list

# 查看具体 trace 详情
cinder trace show <trace-id>

# 查看 trace 统计
cinder trace stats
```

### 5. 导出 Trace 数据

```bash
# 导出单个 trace
cinder trace export <trace-id> --format json

# 导出所有 trace
cinder trace export --all --format json

# 导出为 OTLP 格式
cinder trace export <trace-id> --format otlp
```

### 6. 停止 Phoenix 服务器

```bash
# 停止服务器
cinder service stop-phoenix

# 或直接运行脚本
python scripts/services.py stop-phoenix
```

## CLI 命令参考

### 服务管理

#### `cinder service status`
检查所有外部服务状态

**示例**:
```bash
cinder service status
```

#### `cinder service start-phoenix`
启动 Phoenix 服务器（通过 Docker）

**示例**:
```bash
cinder service start-phoenix
```

#### `cinder service stop-phoenix`
停止 Phoenix 服务器

**示例**:
```bash
cinder service stop-phoenix
```

### Phoenix 状态检查

#### `cinder phoenix start`
检查 Phoenix 是否运行

**示例**:
```bash
cinder phoenix start
```

#### `cinder phoenix stop`
检查 Phoenix 是否运行

**示例**:
```bash
cinder phoenix stop
```

#### `cinder phoenix status`
检查 Phoenix 服务器状态

**示例**:
```bash
cinder phoenix status
```

### Trace 管理

#### `cinder trace list`
列出最近的 trace

**选项**:
- `--limit`: 显示数量（默认：10）
- `--format`: 输出格式（table/json）

**示例**:
```bash
cinder trace list
cinder trace list --limit 20 --format json
```

#### `cinder trace show <trace-id>`
显示 trace 详情

**选项**:
- `--format`: 输出格式（text/json）

**示例**:
```bash
cinder trace show abc123
cinder trace show abc123 --format json
```

#### `cinder trace export [trace-id]`
导出 trace 数据

**选项**:
- `--format`: 导出格式（json/otlp）
- `--output`: 输出文件路径
- `--all`: 导出所有 trace

**示例**:
```bash
cinder trace export abc123
cinder trace export abc123 --format otlp
cinder trace export --all --output traces.json
```

#### `cinder trace search`
搜索 trace

**选项**:
- `--query`: 搜索关键词
- `--agent-id`: 过滤 Agent ID
- `--from`: 开始日期（ISO 格式）
- `--to`: 结束日期（ISO 格式）

**示例**:
```bash
cinder trace search --query "hello"
cinder trace search --agent-id agent-1
```

#### `cinder trace stats`
显示 trace 统计信息

**示例**:
```bash
cinder trace stats
```

#### `cinder trace clean`
清理旧 trace 数据

**选项**:
- `--older-than`: 删除 N 天前的 trace
- `--dry-run`: 仅显示将删除的内容
- `--backup`: 清理前创建备份

**示例**:
```bash
cinder trace clean --older-than 30 --dry-run
cinder trace clean --older-than 7 --backup
```

#### `cinder trace config`
配置 trace 设置

**选项**:
- `--show`: 显示当前配置
- `--enable`: 启用 tracing
- `--disable`: 禁用 tracing
- `--endpoint`: 设置 Phoenix endpoint

**示例**:
```bash
cinder trace config --show
cinder trace config --enable
cinder trace config --endpoint http://localhost:6006
```

## 配置

### 配置文件

配置文件位于 `~/.cinder/config.yaml`：

```yaml
tracing:
  enabled: true
  phoenix_endpoint: ""
  phoenix_host: "localhost"
  phoenix_port: 6006
  sample_rate: 1.0
  retention_days: 30
```

### 配置项说明

- **enabled**: 是否启用 tracing（默认：true）
- **phoenix_endpoint**: Phoenix endpoint（可选，默认使用本地 Docker）
- **phoenix_host**: Phoenix 主机（默认：localhost）
- **phoenix_port**: Phoenix 端口（默认：6006）
- **sample_rate**: 采样率（0.0-1.0，默认：1.0）
- **retention_days**: Trace 保留天数（默认：30）

## Docker 镜像

Phoenix 使用以下 Docker 镜像：

- **镜像**: `arizephoenix/phoenix:latest`
- **容器名**: `cinder-phoenix`
- **数据卷**: `phoenix-data:/root/.phoenix`

### 手动管理 Docker 容器

```bash
# 查看容器状态
docker ps -a | grep cinder-phoenix

# 查看容器日志
docker logs cinder-phoenix

# 手动停止容器
docker stop cinder-phoenix

# 手动删除容器
docker rm cinder-phoenix

# 查看数据卷
docker volume ls | grep phoenix
```

## Trace 数据结构

### LLM 调用 Trace

每个 LLM 调用会记录以下信息：

```json
{
  "span_id": "abc123",
  "operation_name": "llm_call",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T00:00:05Z",
  "duration_ms": 5000,
  "attributes": {
    "llm.model": "qwen3.5:0.8b",
    "llm.prompt": "创建一个 Hello World 程序",
    "llm.system_prompt": "You are a helpful assistant",
    "llm.temperature": 0.2,
    "llm.input_tokens": 50,
    "llm.output_tokens": 100,
    "llm.total_tokens": 150,
    "phase": "code_generation"
  }
}
```

### Agent 执行 Trace

每个 Agent 执行会记录以下信息：

```json
{
  "span_id": "def456",
  "operation_name": "agent_execution",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T00:01:00Z",
  "duration_ms": 60000,
  "attributes": {
    "agent.id": "agent-1",
    "agent.role": "worker",
    "agent.goal": "创建计算器程序",
    "agent.status": "completed"
  }
}
```

## 故障排查

### Phoenix 无法启动

1. **检查 Docker 是否运行**:
   ```bash
   docker info
   ```

2. **检查端口是否被占用**:
   ```bash
   lsof -i :6006
   ```

3. **查看容器日志**:
   ```bash
   docker logs cinder-phoenix
   ```

4. **手动拉取镜像**:
   ```bash
   docker pull arizephoenix/phoenix:latest
   ```

### Trace 数据未记录

1. **检查 tracing 是否启用**:
   ```bash
   cinder trace config --show
   ```

2. **检查 Phoenix 是否运行**:
   ```bash
   cinder phoenix status
   ```

3. **检查 trace 目录**:
   ```bash
   ls -la ~/.cinder/traces/
   ```

### 清理数据

```bash
# 清理旧 trace
cinder trace clean --older-than 30 --backup

# 清理 Docker 数据
docker volume rm phoenix-data
```

## 最佳实践

1. **定期清理**: 使用 `cinder trace clean` 定期清理旧数据
2. **备份数据**: 清理前使用 `--backup` 选项
3. **监控统计**: 定期查看 `cinder trace stats` 了解使用情况
4. **导出重要数据**: 使用 `cinder trace export` 导出重要的 trace 数据

## 集成到代码

### 在自定义代码中使用 Tracer

```python
from cinder_cli.tracing import LLMTracer, TracingConfig

# 创建 tracer
config = TracingConfig()
tracer = LLMTracer()

# 记录 LLM 调用
with tracer.trace_llm_call(
    model="qwen3.5:0.8b",
    prompt="Hello World",
    model_params={"temperature": 0.7}
) as record:
    # 执行 LLM 调用
    response = llm_call()
    
    # 记录响应
    tracer.record_response(record, response, input_tokens=10, output_tokens=20)
```

## 参考资料

- [Phoenix 官方文档](https://phoenix.arize.com/)
- [OpenTelemetry 文档](https://opentelemetry.io/docs/)
- [Docker 文档](https://docs.docker.com/)
