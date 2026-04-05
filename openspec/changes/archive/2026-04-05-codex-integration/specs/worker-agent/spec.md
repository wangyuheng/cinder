## ADDED Requirements

### Requirement: Worker Agent 支持选择执行器

系统 SHALL 允许 Worker Agent 根据配置选择使用 Codex 或 CodeGenerator 作为执行器。

#### Scenario: Worker Agent 使用 Codex 执行器

- **WHEN** Codex 集成已启用且任务适合 Codex
- **THEN** Worker Agent 使用 CodexIntegrationManager 执行任务
- **AND** Worker Agent 返回 Codex 执行结果
- **AND** Worker Agent 保持现有的 Plan → Generate → Evaluation 流程

#### Scenario: Worker Agent 使用 CodeGenerator 执行器

- **WHEN** Codex 集成未启用或任务不适合 Codex
- **THEN** Worker Agent 使用 CodeGenerator 执行任务
- **AND** Worker Agent 返回 CodeGenerator 执行结果
- **AND** Worker Agent 保持现有流程不变

#### Scenario: Worker Agent 执行器降级

- **WHEN** Codex 执行失败且降级已启用
- **THEN** Worker Agent 自动切换到 CodeGenerator
- **AND** Worker Agent 记录降级事件
- **AND** Worker Agent 继续执行任务

### Requirement: Worker Agent 传递上下文给 Codex

系统 SHALL 允许 Worker Agent 将 Soul profile 和决策上下文传递给 Codex。

#### Scenario: Worker Agent 传递 Soul profile

- **WHEN** Worker Agent 使用 Codex 执行任务
- **THEN** Worker Agent 将 Soul profile 特征传递给 CodexIntegrationManager
- **AND** Worker Agent 确保上下文格式正确
- **AND** Worker Agent 记录上下文传递日志

#### Scenario: Worker Agent 传递决策上下文

- **WHEN** Worker Agent 执行 Plan 阶段后
- **THEN** Worker Agent 将任务理解传递给 CodexIntegrationManager
- **AND** Worker Agent 包含质量要求
- **AND** Worker Agent 包含约束条件

## MODIFIED Requirements

### Requirement: Worker Agent 执行 Generate 阶段

系统 SHALL 实现 Worker Agent 作为系统的执行代理，负责执行 Plan、Generate、Evaluation 流程，并返回客观数据。

#### Scenario: Worker Agent 执行 Generate 阶段

- **WHEN** Worker Agent 完成任务分解
- **THEN** Worker Agent 根据配置选择执行器（CodeGenerator 或 Codex）
- **AND** Worker Agent 调用选定的执行器生成代码
- **AND** Worker Agent 返回生成的代码
- **AND** Worker Agent 不包含决策逻辑

#### Scenario: Worker Agent 执行 Generate 阶段 with Codex

- **WHEN** Worker Agent 使用 Codex 执行 Generate 阶段
- **THEN** Worker Agent 调用 CodexIntegrationManager
- **AND** Worker Agent 传递任务描述和上下文
- **AND** Worker Agent 接收 Codex 生成的代码
- **AND** Worker Agent 返回代码给 Decision Agent

### Requirement: Worker Agent 支持迭代执行

系统 SHALL 允许 Worker Agent 进行迭代执行，但由 Decision Agent 决定是否继续。

#### Scenario: Worker Agent 执行迭代生成 with Codex

- **WHEN** Decision Agent 要求 Worker Agent 改进代码且使用 Codex
- **THEN** Worker Agent 调用 CodexIntegrationManager 执行改进
- **AND** Worker Agent 传递上一次的结果和反馈
- **AND** Worker Agent 返回新的结果
- **AND** Worker Agent 不决定是否继续迭代

#### Scenario: Worker Agent 切换执行器迭代

- **WHEN** Codex 执行失败需要降级
- **THEN** Worker Agent 切换到 CodeGenerator 继续迭代
- **AND** Worker Agent 保持迭代上下文
- **AND** Worker Agent 记录执行器切换
