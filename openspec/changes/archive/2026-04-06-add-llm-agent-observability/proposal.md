## Why

当前 Cinder 系统缺乏对 LLM 调用和 Agent 行为的详细追踪能力。虽然存在基础的 TokenTracker 和 ProgressTracker，但无法深入了解执行过程中的关键细节：

- **LLM 调用内容不可见**：无法查看完整的 prompt/response，难以调试和优化 prompt
- **Agent 决策过程不透明**：无法追踪 Agent 的决策路径、工具调用链路和状态转换
- **缺乏可视化工具**：没有统一的界面查看和分析执行过程
- **难以对比和评估**：无法对比不同执行的差异，难以进行 A/B 测试和效果评估

这些问题严重影响了系统的可调试性、可优化性和可维护性。现在引入完整的可观测性系统，可以显著提升开发效率和系统质量。

## What Changes

集成 Phoenix (Arize AI) 作为 LLM/Agent 可观测性平台，建立完整的 trace 系统：

### 新增功能

- **Phoenix 集成**：集成开源的 Phoenix 平台，提供开箱即用的 trace 可视化
- **LLM 调用追踪**：记录完整的 prompt/response、token 使用量、模型参数、调用延迟
- **Agent 行为追踪**：追踪 Agent 决策过程、工具调用链路、状态转换、错误信息
- **Trace 存储**：使用 OpenTelemetry 标准格式存储 trace 数据，兼容第三方工具
- **Web Dashboard**：通过 Phoenix UI 查看、搜索、分析 trace 数据
- **CLI 输出**：支持在命令行查看 trace 摘要和详情
- **数据导出**：支持导出 trace 数据为 JSON 格式

### 修改内容

- **WorkerAgent**：集成 trace 追踪，记录执行过程和 LLM 调用
- **AutonomousExecutor**：集成 trace 追踪，记录整体执行流程
- **CodeGenerator**：记录代码生成过程中的 LLM 调用
- **TaskPlanner**：记录任务规划过程中的 LLM 调用
- **ReflectionEngine**：记录评估过程中的 LLM 调用

## Capabilities

### New Capabilities

- `phoenix-integration`: Phoenix 平台集成，包括安装、配置、启动和连接
- `llm-tracing`: LLM 调用追踪，记录 prompt/response、token 使用、模型参数
- `agent-tracing`: Agent 行为追踪，记录决策过程、工具调用、状态转换
- `trace-storage`: Trace 数据存储，使用 OpenTelemetry 标准格式，支持导出
- `trace-cli`: CLI 命令支持，查看 trace 列表、详情、导出数据

### Modified Capabilities

- `worker-agent`: 集成 trace 追踪，记录执行过程和 LLM 调用（需要修改 spec）
- `autonomous-executor`: 集成 trace 追踪，记录整体执行流程（需要修改 spec）

## Impact

### 代码影响

- **新增模块**：`cinder_cli/tracing/` 模块，包含 Phoenix 集成和 trace 管理
- **修改模块**：
  - `cinder_cli/agents/worker_agent.py`：集成 trace 追踪
  - `cinder_cli/executor/autonomous_executor.py`：集成 trace 追踪
  - `cinder_cli/executor/code_generator.py`：记录 LLM 调用
  - `cinder_cli/executor/task_planner.py`：记录 LLM 调用
  - `cinder_cli/executor/reflection_engine.py`：记录 LLM 调用
  - `cinder_cli/cli.py`：添加 trace 相关 CLI 命令

### API 影响

- **新增 CLI 命令**：
  - `cinder trace list`：列出最近的 trace
  - `cinder trace show <trace-id>`：显示 trace 详情
  - `cinder trace export <trace-id>`：导出 trace 数据
  - `cinder phoenix start`：启动 Phoenix 服务器

### 依赖影响

- **新增依赖**：
  - `arize-phoenix`：Phoenix 平台
  - `opentelemetry-api`：OpenTelemetry API
  - `opentelemetry-sdk`：OpenTelemetry SDK
  - `opentelemetry-exporter-otlp`：OTLP exporter

### 系统影响

- **部署要求**：需要启动 Phoenix 服务器（可选，默认使用本地模式）
- **存储需求**：trace 数据存储在本地 SQLite 数据库（Phoenix 管理）
- **性能影响**：trace 记录会带来轻微性能开销（预计 < 5%）
- **资源消耗**：Phoenix 服务器需要约 200MB 内存

### 兼容性

- **向后兼容**：所有变更向后兼容，不影响现有功能
- **可选功能**：Phoenix 集成是可选的，可以通过配置禁用
- **数据迁移**：不需要数据迁移，trace 数据独立存储
