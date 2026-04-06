# Phoenix Trace 数据结构设计

## 项目配置

### Service Name
- **名称**: `cinder`
- **描述**: Cinder CLI - AI Agent 执行框架

### Resource Attributes
```python
{
    "service.name": "cinder",
    "service.version": "3.0.0",
    "deployment.environment": "development",
    "service.namespace": "cinder-cli",
    "service.instance.id": "<execution-id>",
}
```

## Span 类型设计

### 1. LLM 调用 Span

**Span Kind**: `CLIENT` (表示客户端调用外部服务)

**Span Name 格式**: `llm.<model_name>.<phase>`

**示例**:
- `llm.qwen3.5:0.8b.code_generation`
- `llm.qwen3.5:0.8b.goal_understanding`
- `llm.qwen3.5:0.8b.task_planning`

**Attributes**:
```python
{
    # 基础信息
    "llm.system": "ollama",
    "llm.model": "qwen3.5:0.8b",
    "llm.request.type": "completion",
    
    # Prompt 信息
    "llm.prompt.encoded": False,
    "llm.prompt.length": 150,
    "llm.system_prompt.length": 80,
    
    # Token 统计
    "llm.usage.prompt_tokens": 50,
    "llm.usage.completion_tokens": 100,
    "llm.usage.total_tokens": 150,
    
    # 成本估算
    "llm.usage.cost": 0.0001,
    "llm.usage.cost_currency": "USD",
    
    # 模型参数
    "llm.temperature": 0.2,
    "llm.max_tokens": 4096,
    "llm.top_p": 0.9,
    
    # 执行阶段
    "cinder.phase": "code_generation",
    "cinder.language": "python",
    
    # 质量指标
    "cinder.quality_score": 0.85,
    "cinder.iteration": 1,
    "cinder.max_iterations": 3,
    
    # 错误信息（如果有）
    "error.type": "timeout",
    "error.message": "LLM request timeout",
}
```

### 2. Agent 执行 Span

**Span Kind**: `INTERNAL` (表示内部处理)

**Span Name 格式**: `agent.<role>.<action>`

**示例**:
- `agent.worker.execute_task`
- `agent.planner.decompose_goal`
- `agent.reflector.evaluate_result`

**Attributes**:
```python
{
    # Agent 信息
    "agent.id": "agent-1",
    "agent.role": "worker",
    "agent.name": "Code Generator",
    "agent.version": "3.0.0",
    
    # 执行信息
    "agent.goal": "创建一个计算器程序",
    "agent.task": "生成 Python 代码",
    "agent.status": "completed",
    
    # 执行统计
    "agent.tasks.total": 5,
    "agent.tasks.completed": 4,
    "agent.tasks.failed": 1,
    "agent.duration.ms": 5000,
    
    # 决策信息
    "agent.decision.type": "code_generation",
    "agent.decision.confidence": 0.9,
    "agent.decision.source": "llm",
    
    # Soul Profile
    "agent.soul.risk_level": "medium",
    "agent.soul.style": "concise",
    "agent.soul.focus": "quality",
}
```

### 3. 工具调用 Span

**Span Kind**: `CLIENT`

**Span Name 格式**: `tool.<tool_name>.<action>`

**示例**:
- `tool.file.write`
- `tool.code.execute`
- `tool.test.run`

**Attributes**:
```python
{
    # 工具信息
    "tool.name": "file_operations",
    "tool.action": "write",
    "tool.category": "file_system",
    
    # 输入输出
    "tool.input.file_path": "/path/to/file.py",
    "tool.input.file_size": 1024,
    "tool.output.success": True,
    "tool.output.message": "File created successfully",
    
    # 执行信息
    "tool.duration.ms": 50,
    "tool.retry.count": 0,
}
```

### 4. 任务规划 Span

**Span Kind**: `INTERNAL`

**Span Name**: `planning.decompose_goal`

**Attributes**:
```python
{
    # 规划信息
    "planning.goal": "创建一个计算器程序",
    "planning.strategy": "top_down",
    "planning.constraints": "python, concise",
    
    # 任务分解
    "planning.tasks.count": 5,
    "planning.tasks.parallel": False,
    "planning.complexity": "medium",
    
    # 依赖关系
    "planning.dependencies.count": 3,
    "planning.critical_path.length": 4,
}
```

### 5. 反思评估 Span

**Span Kind**: `INTERNAL`

**Span Name**: `reflection.evaluate_execution`

**Attributes**:
```python
{
    # 评估信息
    "reflection.type": "quality_check",
    "reflection.criteria": "code_quality, style, risk",
    
    # 评估结果
    "reflection.score": 0.85,
    "reflection.passed": True,
    "reflection.issues.count": 2,
    
    # 改进建议
    "reflection.suggestions.count": 3,
    "reflection.improvement.needed": False,
}
```

## Span Events

### LLM 调用事件
```python
{
    "name": "llm.content.completion",
    "timestamp": "2024-01-01T00:00:00Z",
    "attributes": {
        "content.prompt": "创建一个计算器",
        "content.completion": "def calculator(): ...",
        "content.finish_reason": "stop",
    }
}
```

### 错误事件
```python
{
    "name": "exception",
    "timestamp": "2024-01-01T00:00:00Z",
    "attributes": {
        "exception.type": "TimeoutError",
        "exception.message": "LLM request timeout",
        "exception.stacktrace": "...",
    }
}
```

## Span Links

### 关联关系
```python
{
    "links": [
        {
            "context": {"trace_id": "...", "span_id": "..."},
            "attributes": {
                "link.type": "parent_task",
                "link.description": "Generated from task planning",
            }
        }
    ]
}
```

## 完整示例

### 代码生成流程

```
cinder (service)
├── agent.worker.execute_task (span)
│   ├── llm.qwen3.5:0.8b.code_generation (span)
│   │   └── Events: llm.content.completion
│   ├── tool.file.write (span)
│   └── reflection.evaluate_execution (span)
│       └── Events: quality_check_complete
```

### Trace ID 传播

```python
# 主执行
with tracer.start_as_current_span("agent.worker.execute_task") as main_span:
    # 子操作
    with tracer.start_as_current_span("llm.qwen3.5:0.8b.code_generation") as llm_span:
        # 自动关联到父 span
        pass
```

## Phoenix UI 展示

### 项目视图
- **项目名称**: cinder
- **服务列表**: cinder-cli
- **Trace 数量**: 实时统计
- **错误率**: 实时计算

### Span 过滤器
按以下维度过滤：
- `llm.model`: 模型名称
- `cinder.phase`: 执行阶段
- `agent.role`: Agent 角色
- `tool.name`: 工具名称
- `error.type`: 错误类型

### 聚合指标
- Token 使用量统计
- 成本统计
- 执行时间分布
- 错误率趋势
- 质量评分分布

## 实现代码

### 更新 phoenix_tracer.py

```python
def _init_tracer(self) -> trace.Tracer:
    resource = Resource(attributes={
        SERVICE_NAME: "cinder",
        "service.version": "3.0.0",
        "deployment.environment": "development",
        "service.namespace": "cinder-cli",
    })
    
    provider = TracerProvider(resource=resource)
    
    endpoint = self.config.get_phoenix_endpoint()
    otlp_endpoint = f"{endpoint}/v1/traces"
    
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer("cinder")
```

### 更新 llm_tracer.py

```python
def trace_llm_call(
    self,
    model: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    model_params: Optional[dict] = None,
    phase: str = "unknown",
    **kwargs
) -> ContextManager:
    
    span_name = f"llm.{model}.{phase}"
    
    attributes = {
        "llm.system": "ollama",
        "llm.model": model,
        "llm.request.type": "completion",
        "llm.prompt.length": len(prompt),
        "cinder.phase": phase,
    }
    
    if system_prompt:
        attributes["llm.system_prompt.length"] = len(system_prompt)
    
    if model_params:
        attributes.update({
            f"llm.{k}": v for k, v in model_params.items()
        })
    
    # 添加额外属性
    for key, value in kwargs.items():
        attributes[f"cinder.{key}"] = value
    
    return self.tracer.start_as_current_span(
        span_name,
        kind=trace.SpanKind.CLIENT,
        attributes=attributes
    )
```

## 最佳实践

1. **命名规范**: 使用点分隔符，便于 Phoenix UI 分组和过滤
2. **属性前缀**: 使用 `llm.`、`cinder.`、`agent.` 等前缀区分不同类型
3. **单位标注**: 在属性名中包含单位，如 `duration.ms`、`cost.usd`
4. **错误处理**: 使用标准 OpenTelemetry 错误属性
5. **事件记录**: 记录关键事件，如 LLM 响应完成、工具执行结果

## 参考资源

- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/reference/specification/trace/semantic_conventions/)
- [Phoenix Documentation](https://docs.arize.com/phoenix)
- [LLM Observability Best Practices](https://opentelemetry.io/docs/reference/specification/trace/semantic_conventions/span-llm/)
