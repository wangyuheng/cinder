# Phoenix Trace 数据验证指南

## 问题诊断

你遇到的问题：
- Span 名称和 Kind 为空
- 数据显示在 "default" 项目而不是 "cinder" 项目

## 原因分析

Phoenix 13.x 版本的项目管理方式：
1. **项目自动创建**: Phoenix 根据 `service.name` 自动创建项目
2. **默认项目**: 如果没有收到 `service.name`，数据会进入 "default" 项目
3. **Span Kind**: Phoenix UI 可能不显示某些字段，但数据已正确存储

## 验证步骤

### 1. 运行测试脚本

```bash
cd /Users/wangyuheng/code/github.com/wangyuheng/cinder
source .venv/bin/activate
python check_phoenix_data.py
```

### 2. 打开 Phoenix UI

```
http://localhost:6006
```

### 3. 查看项目

在左侧边栏点击 **"Projects"**，你应该看到：
- `cinder-test` 项目（如果 service.name 正确传递）
- 或 `default` 项目（如果 service.name 未传递）

### 4. 查看项目详情

点击项目名称，然后：
1. 点击 **"Traces"** 标签
2. 你应该看到 trace 列表
3. 点击某个 trace 查看详情

### 5. 查看 Span 详情

在 trace 详情页面，你应该看到：
- **Span 名称**: `llm.qwen3.5:0.8b.code_generation`
- **Span Kind**: `Client`（在详情中显示）
- **Attributes**: 包含 `llm.model`, `llm.system` 等

## 常见问题解决

### 问题 1: 数据在 default 项目

**原因**: Phoenix 没有收到 `service.name`

**解决方案**:
```python
# 确保 Resource 包含 service.name
resource = Resource.create({
    "service.name": "cinder",  # 必须设置
    "service.version": "3.0.0",
})

provider = TracerProvider(resource=resource)
```

### 问题 2: Span Kind 为空

**原因**: Phoenix UI 可能不显示 Kind，但数据已存储

**验证方法**:
1. 点击 span 查看详情
2. 在 "Attributes" 部分查找 `span.kind` 或 `kind`
3. 或使用 GraphQL API 查询

### 问题 3: Span 名称不显示

**原因**: 可能是 UI 显示问题

**验证方法**:
1. 使用 GraphQL API 查询
2. 检查导出的 JSON 数据

## 使用 GraphQL API 查询

### 查询所有项目

```bash
curl -X POST http://localhost:6006/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ projects { edges { node { name id } } } }"}'
```

### 查询 Spans

```bash
curl -X POST http://localhost:6006/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ spans(first: 10) { edges { node { name kind spanId attributes } } } }"}'
```

## Phoenix UI 功能说明

### Projects 页面
- 显示所有项目（按 service.name 分组）
- 点击项目查看该服务的所有 traces

### Traces 页面
- 显示 trace 列表
- 每个 trace 包含多个 spans
- 可以按时间、持续时间过滤

### Span 详情
- **Name**: Span 名称（如 `llm.qwen3.5:0.8b.code_generation`）
- **Kind**: Span 类型（Client, Server, Internal 等）
- **Attributes**: 所有属性（模型、tokens、参数等）
- **Events**: Span 事件
- **Links**: 关联的其他 spans

## 验证数据完整性

### 1. 检查 Service Name

在 Phoenix UI 中：
1. 点击项目名称
2. 查看 "Service" 字段
3. 应该显示 `cinder` 或 `cinder-test`

### 2. 检查 Span Kind

在 Span 详情中：
1. 查找 "Kind" 字段
2. 应该显示 `Client` 或 `Internal`
3. 如果不显示，检查 Attributes

### 3. 检查 Attributes

在 Span 详情的 "Attributes" 部分：
- `llm.model`: 模型名称
- `llm.system`: ollama
- `cinder.phase`: 执行阶段
- `llm.usage.total_tokens`: Token 使用量

## 数据导出验证

### 导出为 JSON

```bash
# 使用 Cinder CLI
cinder trace export <trace-id> --format json

# 或直接查询
curl http://localhost:6006/v1/traces > traces.json
```

### 检查导出数据

```python
import json

with open('traces.json') as f:
    data = json.load(f)
    
    for span in data.get('spans', []):
        print(f"Name: {span.get('name')}")
        print(f"Kind: {span.get('kind')}")
        print(f"Attributes: {span.get('attributes')}")
```

## 调试技巧

### 1. 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 检查网络请求

```bash
# 监控 OTLP 请求
docker logs -f cinder-phoenix | grep "POST /v1/traces"
```

### 3. 验证 Exporter

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(
    endpoint="http://localhost:6006/v1/traces",
)

# 测试连接
try:
    # 创建测试 span
    exporter.export([test_span])
    print("✓ Exporter working")
except Exception as e:
    print(f"✗ Exporter failed: {e}")
```

## Phoenix 版本兼容性

### Phoenix 13.x 变化

1. **项目管理**: 自动按 service.name 分组
2. **UI 改进**: 新的 trace 可视化
3. **API 变化**: GraphQL API 更新

### 兼容性检查

```bash
# 检查 Phoenix 版本
curl http://localhost:6006/version

# 或查看容器日志
docker logs cinder-phoenix | grep "version"
```

## 最佳实践

### 1. 始终设置 Service Name

```python
resource = Resource.create({
    "service.name": "cinder",
    "service.namespace": "cinder-cli",
    "service.version": "3.0.0",
})
```

### 2. 使用标准 Span Kind

```python
from opentelemetry import trace

# LLM 调用
span = tracer.start_span(
    "llm.call",
    kind=trace.SpanKind.CLIENT,
)

# Agent 执行
span = tracer.start_span(
    "agent.execute",
    kind=trace.SpanKind.INTERNAL,
)
```

### 3. 添加有意义的 Attributes

```python
span.set_attribute("llm.model", "qwen3.5:0.8b")
span.set_attribute("llm.system", "ollama")
span.set_attribute("cinder.phase", "code_generation")
```

## 下一步

如果数据仍然不正确：

1. **检查 Phoenix 日志**:
   ```bash
   docker logs cinder-phoenix --tail 100
   ```

2. **重启 Phoenix**:
   ```bash
   make stop
   make start
   ```

3. **清理数据**:
   ```bash
   docker volume rm phoenix-data
   make start
   ```

4. **联系支持**:
   - Phoenix GitHub: https://github.com/Arize-AI/phoenix
   - Phoenix 文档: https://docs.arize.com/phoenix

## 总结

Phoenix UI 可能不直接显示某些字段，但数据已正确存储。通过：
1. GraphQL API 查询
2. Span 详情查看
3. 数据导出验证

可以确认数据的完整性。
