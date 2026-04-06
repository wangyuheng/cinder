# Phoenix Trace Schema 实现总结

## ✅ 已完成的工作

### 1. 设计文档
创建了 [TRACE_SCHEMA_DESIGN.md](file:///Users/wangyuheng/code/github.com/wangyuheng/cinder/docs/TRACE_SCHEMA_DESIGN.md)，包含：
- Service 配置
- Span 类型设计
- Attributes 规范
- 命名约定

### 2. 代码实现

#### phoenix_tracer.py
- ✅ 更新 service name 为 `cinder`
- ✅ 添加 `service.namespace: cinder-cli`
- ✅ 使用 HTTP exporter (解决了 SSL 问题)

#### llm_tracer.py
- ✅ Span 命名: `llm.<model>.<phase>`
- ✅ 添加详细的 attributes:
  - `llm.system`: ollama
  - `llm.model`: 模型名称
  - `llm.prompt.length`: Prompt 长度
  - `cinder.phase`: 执行阶段
  - `agent.id`: Agent ID

#### agent_tracer.py
- ✅ Span 命名: `agent.<role>.<action>`
- ✅ 添加详细的 attributes:
  - `agent.id`: Agent ID
  - `agent.role`: Agent 角色
  - `agent.goal`: 执行目标
  - `agent.status`: 执行状态
  - `error.type` 和 `error.message`: 错误信息

#### Tool Call Spans
- ✅ Span 命名: `tool.<name>.<action>`
- ✅ 添加详细的 attributes:
  - `tool.name`: 工具名称
  - `tool.status`: 执行状态
  - `tool.duration.ms`: 执行时长
  - `tool.input.*`: 输入参数

### 3. 测试验证

创建了 [test_trace_schema.py](file:///Users/wangyuheng/code/github.com/wangyuheng/cinder/test_trace_schema.py)，测试通过：
- ✅ LLM Call Span
- ✅ Agent Execution Span
- ✅ Tool Call Span
- ✅ Nested Spans

## 📊 Span 命名规范

### LLM 调用
```
llm.<model>.<phase>

示例:
- llm.qwen3.5:0.8b.code_generation
- llm.qwen3.5:0.8b.goal_understanding
- llm.qwen3.5:0.8b.task_planning
```

### Agent 执行
```
agent.<role>.<action>

示例:
- agent.worker.execute_task
- agent.planner.decompose_goal
- agent.reflector.evaluate_result
```

### 工具调用
```
tool.<name>.<action>

示例:
- tool.file_operations.execute
- tool.code_generator.execute
- tool.test_runner.execute
```

## 🎯 Phoenix UI 展示

### 项目视图
- **项目名称**: cinder
- **服务列表**: cinder-cli
- **Trace 数量**: 实时统计
- **错误率**: 实时计算

### Span 过滤器
可以按以下维度过滤：
- `llm.model`: 模型名称
- `cinder.phase`: 执行阶段
- `agent.role`: Agent 角色
- `tool.name`: 工具名称
- `error.type`: 错误类型

### 聚合指标
- Token 使用量统计
- 执行时间分布
- 错误率趋势
- 质量评分分布

## 🔧 技术细节

### OpenTelemetry 配置
```python
resource = Resource(attributes={
    SERVICE_NAME: "cinder",
    "service.version": "3.0.0",
    "deployment.environment": "development",
    "service.namespace": "cinder-cli",
})

# 使用 HTTP exporter (避免 SSL 问题)
exporter = OTLPSpanExporter(
    endpoint="http://localhost:6006/v1/traces"
)
```

### Span Kind
- **CLIENT**: LLM 调用、工具调用（外部服务）
- **INTERNAL**: Agent 执行、内部处理

### Attributes 前缀
- `llm.*`: LLM 相关属性
- `agent.*`: Agent 相关属性
- `tool.*`: 工具相关属性
- `cinder.*`: Cinder 特定属性
- `error.*`: 错误信息

## 📝 使用示例

### 在代码中使用

```python
from cinder_cli.tracing import LLMTracer, AgentTracer

# LLM 调用
with llm_tracer.trace_llm_call(
    model="qwen3.5:0.8b",
    prompt="创建一个计算器",
    phase="code_generation",
    language="python",
) as record:
    record.response = "def calculator(): ..."
    record.total_tokens = 150

# Agent 执行
with agent_tracer.trace_agent_execution(
    agent_id="agent-1",
    agent_role="worker",
    goal="创建计算器程序",
):
    # 执行任务
    pass

# 工具调用
with agent_tracer.trace_tool_call(
    agent_id="agent-1",
    tool_name="file_operations",
    input_params={"file_path": "/tmp/calculator.py"},
):
    # 执行工具
    pass
```

## 🚀 下一步

### 可选增强
1. **添加更多 attributes**: 成本估算、质量评分等
2. **添加 Span Events**: 记录关键事件
3. **添加 Span Links**: 关联相关 spans
4. **添加 Metrics**: 性能指标收集

### 集成到实际执行
在 [autonomous_executor.py](file:///Users/wangyuheng/code/github.com/wangyuheng/cinder/cinder_cli/executor/autonomous_executor.py) 中：
- ✅ 已传递 tracer 到 CodeGenerator
- ✅ 已传递 tracer 到 TaskPlanner
- ✅ 已传递 tracer 到 ReflectionEngine

## ✅ 验证清单

- [x] Service name 设置为 `cinder`
- [x] Span 命名遵循规范
- [x] Attributes 包含完整信息
- [x] 错误处理正确
- [x] 嵌套 span 关系正确
- [x] 测试全部通过
- [x] Phoenix 可以接收数据

## 📚 相关文档

- [Trace Schema 设计](file:///Users/wangyuheng/code/github.com/wangyuheng/cinder/docs/TRACE_SCHEMA_DESIGN.md)
- [Phoenix 版本管理](file:///Users/wangyuheng/code/github.com/wangyuheng/cinder/docs/PHOENIX_VERSION.md)
- [环境管理](file:///Users/wangyuheng/code/github.com/wangyuheng/cinder/docs/ENVIRONMENT_MANAGEMENT.md)

## 🎉 总结

Phoenix trace schema 已经完全实现并测试通过！

**关键改进**:
1. 使用 HTTP exporter 解决 SSL 问题
2. 标准化的 span 命名规范
3. 丰富的 attributes 信息
4. 完整的错误处理
5. 支持嵌套 span 关系

**现在可以**:
- 在 Phoenix UI 中查看 trace 数据
- 按 model、phase、role 等过滤
- 分析 token 使用和执行时间
- 追踪错误和性能问题
