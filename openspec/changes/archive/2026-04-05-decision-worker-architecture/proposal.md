## Why

当前架构中，Decision 阶段仅作为流程的一个环节，缺乏主动性和智能性。Plan、Generate、Evaluation 三个阶段各自独立运行，缺乏统一的协调和决策机制。这导致：

1. **决策分散**：每个阶段都有自己的决策逻辑，缺乏全局视角
2. **角色混乱**：Decision 本应是"大脑"，但实际只处理代码接受/拒绝的简单决策
3. **交互能力不足**：无法主动询问用户、调整策略、处理复杂场景
4. **扩展性差**：难以支持技术选型、架构决策等需要人工判断的场景

现在是重构的最佳时机，因为系统已经具备 Soul profile 和决策基础设施，只需要重新定义角色和职责。

## What Changes

### 核心架构变更

- **引入双层 Agent Loop 架构**
  - Decision Agent：作为大脑/管理者，负责理解意图、做决策、调度 Worker、与用户交互
  - Worker Agent：作为执行者，负责 Plan → Generate → Evaluation 流程

- **重新定义 Decision 阶段**
  - 从"流程环节"升级为"智能代理"
  - 基于 Soul profile 做决策，扮演用户角色
  - 主动思考、询问、调整策略
  - 记录上下文和历史决策

- **简化 Worker 阶段**
  - Plan、Generate、 Evaluation 合并为 Worker Agent
  - 移除所有决策逻辑，只负责执行和报告
  - 返回客观数据，不包含"是否接受"等决策

### 新增能力

- **主动交互**：Decision Agent 可以主动询问用户，获取更多信息
- **上下文管理**：维护全局上下文，支持多轮对话和决策
- **策略调整**：根据执行结果动态调整策略
- **技术选型支持**：Worker 可以输出选项，Decision 做出选择

### **BREAKING** API 变更

- `AutonomousExecutor.execute()` 返回结构变更
- Decision 阶段输出格式扩展（支持 options/question 类型）
- Worker 阶段输出格式标准化（移除决策字段）

## Capabilities

### New Capabilities

- `decision-agent`: Decision Agent 作为智能代理的核心能力，包括理解意图、做决策、调度 Worker、与用户交互
- `worker-agent`: Worker Agent 作为执行者的能力，包括 Plan、Generate、Evaluation 的执行和报告
- `agent-orchestration`: Agent 编排能力，支持 Decision 和 Worker 之间的协作和通信
- `context-management`: 上下文管理能力，维护全局状态和历史决策

### Modified Capabilities

- `proxy-decision-making`: 扩展代理决策能力，支持更多决策类型（技术选型、架构决策等）
- `autonomous-executor`: 重构执行器，从单一流程变为 Agent 编排器

## Impact

### 代码影响

- **新增文件**：
  - `cinder_cli/agents/decision_agent.py`
  - `cinder_cli/agents/worker_agent.py`
  - `cinder_cli/agents/base.py`

- **重构文件**：
  - `cinder_cli/executor/autonomous_executor.py` - 简化为 Agent 编排器
  - `cinder_cli/executor/task_planner.py` - 移除决策逻辑
  - `cinder_cli/executor/code_generator.py` - 移除决策逻辑
  - `cinder_cli/executor/reflection_engine.py` - 移除决策逻辑
  - `cinder_cli/proxy_decision.py` - 扩展支持更多决策类型

- **测试文件**：
  - 新增 `tests/test_decision_agent.py`
  - 新增 `tests/test_worker_agent.py`
  - 更新 `tests/test_executor_flow.py`

### API 影响

- **BREAKING**: `AutonomousExecutor.execute()` 返回结构变更
  - 旧：`{"status": "success", "results": [...]}`
  - 新：`{"status": "success", "decision": {...}, "worker_result": {...}}`

- **BREAKING**: Decision 阶段输出格式扩展
  - 旧：`{"phase": "decision", "decisions": [...]}`
  - 新：`{"type": "decision|options|question", "data": {...}, "metadata": {...}}`

### 依赖影响

- 无新增外部依赖
- 内部依赖关系调整：各模块依赖 Agent 层而非直接相互依赖

### 性能影响

- LLM 调用次数可能增加 20-30%（Decision Agent 的思考过程）
- 执行时间可能增加 10-20%（增加了决策循环）
- 但整体质量提升，减少返工

### 向后兼容性

- **不兼容**：API 返回结构变更，需要更新调用方
- **迁移方案**：提供兼容层，支持旧 API 格式（deprecated）
