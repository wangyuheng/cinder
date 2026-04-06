## Context

### 当前状态

Cinder 系统当前拥有基础的追踪机制：

- **TokenTracker**：记录 LLM 调用的 token 使用量，但缺少 prompt/response 内容
- **ProgressTracker**：追踪执行进度和阶段，但不记录具体行为
- **ExecutionLogger**：记录执行历史到 SQLite，但不包含详细的 LLM 调用信息

这些组件提供了基础的监控能力，但无法满足深入调试和分析的需求。

### 技术约束

- **Python 3.10+**：需要使用现代 Python 特性
- **轻量级部署**：避免引入复杂的依赖和部署要求
- **向后兼容**：不能破坏现有功能
- **可选功能**：trace 功能应该可以通过配置禁用

### 相关技术

- **OpenTelemetry**：业界标准的可观测性框架
- **Phoenix**：专为 LLM/Agent 设计的开源可观测性平台
- **OTLP**：OpenTelemetry Protocol，用于导出 trace 数据

## Goals / Non-Goals

### Goals

1. **完整的 LLM 调用追踪**
   - 记录完整的 prompt 和 response 内容
   - 记录 token 使用量（input/output）
   - 记录模型参数（temperature, top_p, etc.）
   - 记录调用延迟和错误信息

2. **详细的 Agent 行为追踪**
   - 追踪 Agent 决策过程和推理路径
   - 追踪工具调用链路和参数
   - 追踪状态转换和错误恢复
   - 支持多 Agent 协作场景

3. **易用的可视化界面**
   - 集成 Phoenix Web UI
   - 支持搜索、过滤、对比 trace
   - 支持数据导出和分析

4. **灵活的部署方式**
   - 支持本地模式（无需额外服务器）
   - 支持远程模式（连接到远程 Phoenix 服务器）
   - 支持禁用 trace 功能

5. **标准化的数据格式**
   - 使用 OpenTelemetry 标准格式
   - 兼容第三方工具（Jaeger, Grafana, etc.）
   - 支持自定义导出器

### Non-Goals

1. **不实现分布式追踪**
   - 当前系统是单进程应用，不需要分布式追踪
   - 未来可以扩展支持

2. **不实现实时监控告警**
   - 当前重点是事后分析，不是实时监控
   - 可以在未来集成 Prometheus/Grafana

3. **不实现自动化性能优化**
   - 追踪数据用于人工分析，不自动调整参数
   - 可以在未来实现智能调优

4. **不实现用户权限管理**
   - 当前是个人工具，不需要多用户支持
   - Phoenix 支持用户管理，但不在当前范围

## Decisions

### 决策 1: 选择 Phoenix 作为可观测性平台

**选择**: Phoenix (Arize AI)

**理由**:
- ✅ 专为 LLM/Agent 设计，开箱即用
- ✅ 完全开源，MIT 协议，可自托管
- ✅ 轻量级部署，单 Python 包，无需数据库
- ✅ 美观的 Web UI，功能完善
- ✅ 原生支持 OpenTelemetry 标准
- ✅ 活跃的社区和良好的文档

**替代方案**:

1. **LangSmith**
   - ❌ 商业产品，收费
   - ❌ 云端托管，数据隐私问题
   - ✅ 功能强大，文档完善

2. **自建系统**
   - ❌ 需要大量开发工作
   - ❌ 需要自己实现 UI
   - ✅ 完全控制

3. **Jaeger + 自定义 UI**
   - ❌ 需要自己实现 LLM 特定功能
   - ❌ UI 不够友好
   - ✅ 成熟的 trace 系统

### 决策 2: 使用 OpenTelemetry 标准

**选择**: OpenTelemetry SDK + OTLP 协议

**理由**:
- ✅ 业界标准，社区支持
- ✅ 兼容多种后端（Phoenix, Jaeger, Grafana）
- ✅ 丰富的 SDK 和工具
- ✅ 未来可扩展性强

**替代方案**:

1. **自定义 trace 格式**
   - ❌ 不兼容第三方工具
   - ❌ 需要自己实现导出器
   - ✅ 完全控制

2. **直接使用 Phoenix SDK**
   - ❌ 锁定到 Phoenix 平台
   - ❌ 未来迁移困难
   - ✅ 更简单的集成

### 决策 3: Trace 数据存储在 Phoenix 管理的 SQLite

**选择**: 让 Phoenix 管理 trace 数据存储

**理由**:
- ✅ Phoenix 自动管理数据库
- ✅ 无需额外的数据库配置
- ✅ 数据与 Phoenix UI 紧密集成
- ✅ 简化部署和维护

**替代方案**:

1. **存储在 Cinder 的 SQLite 数据库**
   - ❌ 需要自己实现数据模型
   - ❌ 需要自己实现查询接口
   - ✅ 数据集中管理

2. **存储在独立的 PostgreSQL**
   - ❌ 增加部署复杂度
   - ❌ 资源消耗大
   - ✅ 支持大规模数据

### 决策 4: Trace 功能默认启用，可配置禁用

**选择**: 默认启用，通过配置禁用

**理由**:
- ✅ 提供开箱即用的体验
- ✅ 大多数用户需要 trace 功能
- ✅ 性能开销小（< 5%）
- ✅ 可以通过配置灵活控制

**替代方案**:

1. **默认禁用**
   - ❌ 需要用户手动启用
   - ❌ 降低可观测性
   - ✅ 零性能开销（如果不需要）

2. **强制启用**
   - ❌ 不够灵活
   - ❌ 无法适应特殊场景
   - ✅ 确保数据完整性

### 决策 5: 分层架构设计

**选择**: 三层架构

```
┌─────────────────────────────────────────┐
│  Application Layer                      │
│  (WorkerAgent, AutonomousExecutor)      │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Tracing Layer                          │
│  (PhoenixTracer, TraceContext)          │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Storage Layer                          │
│  (Phoenix + SQLite)                     │
└─────────────────────────────────────────┘
```

**理由**:
- ✅ 关注点分离，易于维护
- ✅ 可以独立测试每一层
- ✅ 未来可以替换存储层
- ✅ 应用层代码简洁

**替代方案**:

1. **单层架构**
   - ❌ 代码耦合，难以维护
   - ❌ 难以测试
   - ✅ 实现简单

2. **四层架构（增加 API 层）**
   - ❌ 过度设计
   - ❌ 增加复杂度
   - ✅ 更清晰的抽象

## Architecture

### 模块结构

```
cinder_cli/
├── tracing/
│   ├── __init__.py
│   ├── phoenix_tracer.py      # Phoenix 集成
│   ├── trace_context.py       # Trace 上下文管理
│   ├── llm_tracer.py          # LLM 调用追踪
│   ├── agent_tracer.py        # Agent 行为追踪
│   └── config.py              # Trace 配置
├── agents/
│   └── worker_agent.py        # 集成 trace
├── executor/
│   ├── autonomous_executor.py # 集成 trace
│   ├── code_generator.py      # 集成 trace
│   ├── task_planner.py        # 集成 trace
│   └── reflection_engine.py   # 集成 trace
└── cli.py                     # 添加 trace 命令
```

### 数据流

```
1. 用户执行命令
   ↓
2. AutonomousExecutor 开始 trace
   ↓
3. WorkerAgent 执行任务，记录决策和工具调用
   ↓
4. CodeGenerator/TaskPlanner 调用 LLM，记录 prompt/response
   ↓
5. Trace 数据导出到 Phoenix
   ↓
6. 用户通过 Phoenix UI 或 CLI 查看 trace
```

### Trace 数据模型

```python
# Trace (一次完整执行)
{
  "trace_id": "trace_abc123",
  "execution_id": 123,
  "goal": "Create a calculator",
  "mode": "auto",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T00:00:05Z",
  "status": "completed",
  "metadata": {...}
}

# Span (执行节点)
{
  "span_id": "span_123",
  "trace_id": "trace_abc123",
  "parent_span_id": null,
  "operation_name": "agent.execution",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T00:00:05Z",
  "attributes": {
    "agent.id": "worker_1",
    "agent.role": "code_generator",
    "agent.goal": "Create a calculator"
  }
}

# LLM Call (LLM 调用)
{
  "call_id": "call_123",
  "span_id": "span_456",
  "model": "qwen3.5:0.8b",
  "prompt": "Write a function...",
  "response": "def hello():...",
  "input_tokens": 150,
  "output_tokens": 200,
  "duration_ms": 1234,
  "model_params": {"temperature": 0.7}
}
```

## Risks / Trade-offs

### 风险 1: 性能开销

**风险**: Trace 记录会增加执行延迟

**影响**: 预计 3-5% 的性能开销

**缓解措施**:
- 使用 BatchSpanProcessor 异步导出
- 提供配置选项禁用 trace
- 优化 trace 数据结构，减少内存占用
- 定期清理旧的 trace 数据

### 风险 2: 存储空间

**风险**: Trace 数据会占用磁盘空间

**影响**: 每个 trace 约 10-50KB，大量执行会占用空间

**缓解措施**:
- Phoenix 自动管理存储
- 提供数据清理工具
- 支持导出和归档旧数据
- 可以配置保留策略

### 风险 3: 数据隐私

**风险**: Prompt 和 response 可能包含敏感信息

**影响**: 敏感信息被记录到 trace 中

**缓解措施**:
- 提供配置选项禁用内容记录
- 支持数据脱敏功能
- 本地存储，不上传云端
- 提供数据清理工具

### 风险 4: 依赖管理

**风险**: 新增依赖可能引入兼容性问题

**影响**: 依赖冲突、版本问题

**缓解措施**:
- 使用虚拟环境隔离
- 明确指定依赖版本
- 定期更新依赖
- 提供依赖检查工具

### 权衡 1: 功能 vs 简洁

**选择**: 优先功能完整性

**权衡**:
- ✅ 提供完整的 trace 功能
- ❌ 增加代码复杂度
- ✅ 提升可观测性
- ❌ 增加维护成本

### 权衡 2: 标准 vs 定制

**选择**: 使用 OpenTelemetry 标准

**权衡**:
- ✅ 兼容第三方工具
- ✅ 社区支持
- ❌ 学习曲线
- ❌ 可能的限制

### 权衡 3: 本地 vs 远程

**选择**: 优先本地模式

**权衡**:
- ✅ 简化部署
- ✅ 数据隐私
- ❌ 不支持多机协作
- ❌ 数据不集中

## Migration Plan

### 阶段 1: 准备阶段（1-2 天）

1. **安装依赖**
   ```bash
   pip install arize-phoenix opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
   ```

2. **创建 tracing 模块**
   - 创建 `cinder_cli/tracing/` 目录
   - 实现基础类和接口

3. **更新配置**
   - 添加 trace 相关配置项
   - 更新 `cinder.yaml` 示例

### 阶段 2: 核心实现（3-5 天）

1. **实现 PhoenixTracer**
   - Phoenix 集成
   - OpenTelemetry 初始化
   - Trace 上下文管理

2. **实现 LLM Tracing**
   - 封装 LLM 调用追踪
   - 记录 prompt/response
   - 记录 token 和延迟

3. **实现 Agent Tracing**
   - 追踪 Agent 决策
   - 追踪工具调用
   - 追踪状态转换

### 阶段 3: 集成阶段（2-3 天）

1. **集成到 WorkerAgent**
   - 修改 `worker_agent.py`
   - 添加 trace 调用

2. **集成到 AutonomousExecutor**
   - 修改 `autonomous_executor.py`
   - 添加 trace 调用

3. **集成到其他模块**
   - 修改 `code_generator.py`
   - 修改 `task_planner.py`
   - 修改 `reflection_engine.py`

### 阶段 4: CLI 和测试（2-3 天）

1. **添加 CLI 命令**
   - `cinder trace list`
   - `cinder trace show`
   - `cinder trace export`
   - `cinder phoenix start`

2. **编写测试**
   - 单元测试
   - 集成测试
   - 端到端测试

3. **编写文档**
   - 用户指南
   - API 文档
   - 示例代码

### 阶段 5: 部署和验证（1-2 天）

1. **本地测试**
   - 运行测试套件
   - 手动测试各种场景

2. **性能测试**
   - 测量性能开销
   - 优化瓶颈

3. **文档完善**
   - 更新 README
   - 添加使用示例

### 回滚策略

如果出现严重问题，可以：

1. **禁用 trace 功能**
   ```yaml
   # cinder.yaml
   tracing:
     enabled: false
   ```

2. **卸载依赖**
   ```bash
   pip uninstall arize-phoenix opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
   ```

3. **回退代码**
   ```bash
   git revert <commit-hash>
   ```

## Open Questions

1. **Trace 数据保留策略**
   - 问题：应该保留多长时间的 trace 数据？
   - 选项：7 天、30 天、90 天、永久
   - 建议：默认 30 天，可配置

2. **敏感信息处理**
   - 问题：如何处理 prompt 中的敏感信息？
   - 选项：完全记录、脱敏记录、不记录内容
   - 建议：默认完全记录，提供脱敏选项

3. **多进程支持**
   - 问题：是否需要支持多进程 trace？
   - 选项：当前不支持、未来支持
   - 建议：当前不支持，记录为未来改进项

4. **自定义导出器**
   - 问题：是否需要支持自定义导出器？
   - 选项：仅支持 OTLP、支持自定义
   - 建议：当前仅支持 OTLP，未来可扩展

5. **Trace 采样策略**
   - 问题：是否需要采样策略以减少数据量？
   - 选项：全量记录、采样记录
   - 建议：当前全量记录，未来可添加采样

## Success Criteria

实施成功的标准：

1. **功能完整性**
   - ✅ 所有 LLM 调用被追踪
   - ✅ 所有 Agent 决策被记录
   - ✅ Phoenix UI 可以正常查看
   - ✅ CLI 命令正常工作

2. **性能指标**
   - ✅ 性能开销 < 5%
   - ✅ 内存增加 < 50MB
   - ✅ 启动时间增加 < 1s

3. **用户体验**
   - ✅ 文档清晰易懂
   - ✅ 配置简单
   - ✅ 错误提示友好

4. **代码质量**
   - ✅ 测试覆盖率 > 80%
   - ✅ 无严重 bug
   - ✅ 代码符合规范
