## ADDED Requirements

### Requirement: Autonomous Executor 集成 Trace

系统 SHALL 允许 Autonomous Executor 集成 trace 追踪，记录整体执行流程。

#### Scenario: Autonomous Executor 初始化 trace

- **WHEN** Autonomous Executor 开始执行目标
- **THEN** Autonomous Executor 创建 trace context
- **AND** trace context 记录执行目标和模式
- **AND** trace context 记录执行开始时间

#### Scenario: Autonomous Executor 追踪执行阶段

- **WHEN** Autonomous Executor 执行不同阶段
- **THEN** Autonomous Executor 为每个阶段创建 span
- **AND** span 记录阶段名称（如 "task_planning", "code_generation", "evaluation"）
- **AND** span 记录阶段开始和结束时间

#### Scenario: Autonomous Executor 追踪 LLM 调用

- **WHEN** Autonomous Executor 通过 TaskPlanner、CodeGenerator 或 ReflectionEngine 调用 LLM
- **THEN** Autonomous Executor 记录 LLM 调用详情
- **AND** 记录包括 prompt、response、tokens
- **AND** 记录包括模型参数和调用延迟

#### Scenario: Autonomous Executor 追踪决策过程

- **WHEN** Autonomous Executor 进行代理决策
- **THEN** Autonomous Executor 记录决策类型
- **AND** Autonomous Executor 记录决策选项
- **AND** Autonomous Executor 记录决策结果和置信度

#### Scenario: Autonomous Executor 追踪错误

- **WHEN** Autonomous Executor 遇到错误
- **THEN** Autonomous Executor 记录错误详情
- **AND** 记录包括错误类型和消息
- **AND** 记录包括错误堆栈

#### Scenario: Autonomous Executor 完成 trace

- **WHEN** Autonomous Executor 完成目标执行
- **THEN** Autonomous Executor 结束 trace
- **AND** trace 记录最终状态和结果
- **AND** trace 数据导出到 Phoenix

### Requirement: Autonomous Executor Trace 配置

系统 SHALL 允许配置 Autonomous Executor 的 trace 行为。

#### Scenario: 配置 Autonomous Executor trace 启用/禁用

- **WHEN** 用户在 cinder.yaml 中设置 autonomous_executor.tracing.enabled = false
- **THEN** Autonomous Executor 不记录 trace 数据
- **AND** Autonomous Executor 正常执行目标

#### Scenario: 配置 Autonomous Executor trace 详细程度

- **WHEN** 用户在 cinder.yaml 中设置 autonomous_executor.tracing.level = "debug"
- **THEN** Autonomous Executor 记录详细的 trace 信息
- **AND** 详细信息包括完整的 prompt 和 response
- **AND** 详细信息包括中间状态

### Requirement: Autonomous Executor Trace 数据关联

系统 SHALL 将 Autonomous Executor 的 trace 数据与执行上下文关联。

#### Scenario: 关联到执行 ID

- **WHEN** Autonomous Executor 执行目标
- **THEN** trace 数据关联到执行 ID
- **AND** 可以通过执行 ID 查询 trace

#### Scenario: 关联到 Soul Profile

- **WHEN** Autonomous Executor 使用 Soul Profile
- **THEN** trace 数据关联到 Soul Profile ID
- **AND** 可以分析不同 Soul Profile 的执行差异

#### Scenario: 关联到执行模式

- **WHEN** Autonomous Executor 以特定模式执行（auto/interactive/dry-run）
- **THEN** trace 数据记录执行模式
- **AND** 可以按模式过滤和分析 trace

### Requirement: Autonomous Executor Trace 性能监控

系统 SHALL 通过 trace 监控 Autonomous Executor 的性能。

#### Scenario: 监控执行时间

- **WHEN** Autonomous Executor 执行目标
- **THEN** trace 记录总执行时间
- **AND** trace 记录各阶段执行时间
- **AND** trace 记录 LLM 调用时间占比

#### Scenario: 监控 token 使用量

- **WHEN** Autonomous Executor 执行目标
- **THEN** trace 记录总 token 使用量
- **AND** trace 记录各阶段 token 使用量
- **AND** trace 记录 token 使用效率

#### Scenario: 监控迭代次数

- **WHEN** Autonomous Executor 执行迭代生成
- **THEN** trace 记录总迭代次数
- **AND** trace 记录每次迭代的改进
- **AND** trace 记录迭代收敛情况

### Requirement: Autonomous Executor Trace 可视化

系统 SHALL 支持可视化 Autonomous Executor 的执行过程。

#### Scenario: 显示执行流程图

- **WHEN** 用户在 Phoenix UI 中查看 Autonomous Executor trace
- **THEN** UI 显示执行流程图
- **AND** 流程图显示各阶段的执行顺序
- **AND** 流程图显示各阶段的执行时间

#### Scenario: 显示决策树

- **WHEN** 用户在 Phoenix UI 中查看 Autonomous Executor trace
- **THEN** UI 显示决策树
- **AND** 决策树显示决策节点和分支
- **AND** 决策树显示决策结果

#### Scenario: 显示性能指标

- **WHEN** 用户在 Phoenix UI 中查看 Autonomous Executor trace
- **THEN** UI 显示性能指标
- **AND** 指标包括执行时间、token 使用量、迭代次数
- **AND** 指标支持与其他执行对比
