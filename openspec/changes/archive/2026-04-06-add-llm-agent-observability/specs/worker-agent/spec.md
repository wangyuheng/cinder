## ADDED Requirements

### Requirement: Worker Agent 集成 Trace 追踪

系统 SHALL 允许 Worker Agent 集成 trace 追踪功能，记录执行过程和 LLM 调用。

#### Scenario: Worker Agent 初始化 trace

- **WHEN** Worker Agent 开始执行任务
- **THEN** Worker Agent 创建 trace context
- **AND** trace context 记录任务描述和约束
- **AND** trace context 记录 Agent ID 和角色

#### Scenario: Worker Agent 追踪执行阶段

- **WHEN** Worker Agent 执行 Plan/Generate/Evaluation 阶段
- **THEN** Worker Agent 为每个阶段创建 span
- **AND** span 记录阶段名称和开始时间
- **AND** span 记录阶段输入和输出

#### Scenario: Worker Agent 追踪 LLM 调用

- **WHEN** Worker Agent 调用 LLM（通过 CodeGenerator/TaskPlanner/ReflectionEngine）
- **THEN** Worker Agent 记录 LLM 调用详情
- **AND** 记录包括 prompt、response、tokens
- **AND** 记录包括模型参数和调用延迟

#### Scenario: Worker Agent 追踪工具调用

- **WHEN** Worker Agent 调用工具（如 Codex）
- **THEN** Worker Agent 创建工具调用 span
- **AND** span 记录工具名称和输入参数
- **AND** span 记录工具输出和执行时间

#### Scenario: Worker Agent 追踪决策过程

- **WHEN** Worker Agent 需要输出选项供 Decision Agent 选择
- **THEN** Worker Agent 记录决策类型
- **AND** Worker Agent 记录生成的选项列表
- **AND** Worker Agent 记录选项的详细描述

#### Scenario: Worker Agent 追踪错误

- **WHEN** Worker Agent 遇到错误
- **THEN** Worker Agent 记录错误详情
- **AND** 记录包括错误类型和消息
- **AND** 记录包括错误堆栈

#### Scenario: Worker Agent 追踪迭代执行

- **WHEN** Worker Agent 执行迭代生成
- **THEN** Worker Agent 记录每次迭代
- **AND** 记录包括迭代次数和质量分数
- **AND** 记录包括迭代改进内容

#### Scenario: Worker Agent 完成 trace

- **WHEN** Worker Agent 完成任务执行
- **THEN** Worker Agent 结束 trace
- **AND** trace 记录最终状态和结果
- **AND** trace 数据导出到 Phoenix

### Requirement: Worker Agent Trace 配置

系统 SHALL 允许配置 Worker Agent 的 trace 行为。

#### Scenario: 配置 Worker Agent trace 启用/禁用

- **WHEN** 用户在 cinder.yaml 中设置 worker_agent.tracing.enabled = false
- **THEN** Worker Agent 不记录 trace 数据
- **AND** Worker Agent 正常执行任务

#### Scenario: 配置 Worker Agent trace 详细程度

- **WHEN** 用户在 cinder.yaml 中设置 worker_agent.tracing.level = "debug"
- **THEN** Worker Agent 记录详细的 trace 信息
- **AND** 详细信息包括完整的 prompt 和 response
- **AND** 详细信息包括中间状态

### Requirement: Worker Agent Trace 数据关联

系统 SHALL 将 Worker Agent 的 trace 数据与执行上下文关联。

#### Scenario: 关联到执行 ID

- **WHEN** Worker Agent 执行任务
- **THEN** trace 数据关联到执行 ID
- **AND** 可以通过执行 ID 查询 trace

#### Scenario: 关联到任务 ID

- **WHEN** Worker Agent 执行特定任务
- **THEN** trace 数据关联到任务 ID
- **AND** 可以通过任务 ID 查询 trace

#### Scenario: 关联到 Soul Profile

- **WHEN** Worker Agent 使用 Soul Profile
- **THEN** trace 数据关联到 Soul Profile ID
- **AND** 可以分析不同 Soul Profile 的执行差异
