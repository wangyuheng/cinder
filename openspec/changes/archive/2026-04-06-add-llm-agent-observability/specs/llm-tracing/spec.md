## ADDED Requirements

### Requirement: LLM 调用追踪初始化

系统 SHALL 支持追踪所有 LLM 调用，包括 prompt、response 和相关元数据。

#### Scenario: 开始 LLM 调用追踪

- **WHEN** 系统调用 LLM API
- **THEN** 系统创建 LLM 调用 span
- **AND** span 记录调用开始时间
- **AND** span 记录模型名称

#### Scenario: 记录 LLM 调用上下文

- **WHEN** 系统追踪 LLM 调用
- **THEN** 系统记录调用所在的 Agent ID
- **AND** 系统记录调用所在的执行阶段
- **AND** 系统记录调用目的（如 "task_planning", "code_generation"）

### Requirement: Prompt 内容记录

系统 SHALL 记录完整的 prompt 内容，包括系统 prompt 和用户 prompt。

#### Scenario: 记录用户 prompt

- **WHEN** 系统调用 LLM API
- **THEN** 系统记录完整的用户 prompt 内容
- **AND** prompt 内容不被截断
- **AND** prompt 内容支持多行文本

#### Scenario: 记录系统 prompt

- **WHEN** 系统调用 LLM API 并提供系统 prompt
- **THEN** 系统记录完整的系统 prompt 内容
- **AND** 系统 prompt 与用户 prompt 分开存储

#### Scenario: 记录 prompt 模板变量

- **WHEN** 系统使用 prompt 模板
- **THEN** 系统记录模板名称
- **AND** 系统记录模板变量值
- **AND** 系统记录渲染后的完整 prompt

### Requirement: Response 内容记录

系统 SHALL 记录完整的 LLM response 内容。

#### Scenario: 记录 LLM response

- **WHEN** LLM API 返回响应
- **THEN** 系统记录完整的 response 内容
- **AND** response 内容不被截断
- **AND** response 内容支持多行文本

#### Scenario: 记录 LLM response 元数据

- **WHEN** LLM API 返回响应
- **THEN** 系统记录 response 的 finish_reason
- **AND** 系统记录 response 的 ID
- **AND** 系统记录 response 的创建时间

### Requirement: Token 使用量记录

系统 SHALL 记录 LLM 调用的 token 使用量。

#### Scenario: 记录 input tokens

- **WHEN** LLM API 返回 token 使用信息
- **THEN** 系统记录 input tokens 数量
- **AND** token 数量准确反映实际使用量

#### Scenario: 记录 output tokens

- **WHEN** LLM API 返回 token 使用信息
- **THEN** 系统记录 output tokens 数量
- **AND** token 数量准确反映实际使用量

#### Scenario: 记录 total tokens

- **WHEN** 系统记录 token 使用量
- **THEN** 系统计算并记录 total tokens
- **AND** total tokens = input tokens + output tokens

### Requirement: 模型参数记录

系统 SHALL 记录 LLM 调用的模型参数。

#### Scenario: 记录模型名称

- **WHEN** 系统调用 LLM API
- **THEN** 系统记录模型名称（如 "gpt-4", "qwen3.5:0.8b"）
- **AND** 模型名称准确反映实际使用的模型

#### Scenario: 记录模型参数

- **WHEN** 系统调用 LLM API 并指定参数
- **THEN** 系统记录 temperature 参数
- **AND** 系统记录 top_p 参数
- **AND** 系统记录 max_tokens 参数
- **AND** 系统记录其他自定义参数

### Requirement: 调用延迟记录

系统 SHALL 记录 LLM 调用的延迟信息。

#### Scenario: 记录调用开始时间

- **WHEN** 系统开始 LLM 调用
- **THEN** 系统记录调用开始时间戳

#### Scenario: 记录调用结束时间

- **WHEN** LLM 调用完成
- **THEN** 系统记录调用结束时间戳

#### Scenario: 计算调用延迟

- **WHEN** 系统记录调用时间
- **THEN** 系统计算调用延迟（毫秒）
- **AND** 延迟 = 结束时间 - 开始时间

### Requirement: 错误信息记录

系统 SHALL 记录 LLM 调用的错误信息。

#### Scenario: 记录 LLM 调用错误

- **WHEN** LLM API 调用失败
- **THEN** 系统记录错误类型
- **AND** 系统记录错误消息
- **AND** 系统记录错误堆栈（如果有）

#### Scenario: 记录 LLM API 限流错误

- **WHEN** LLM API 返回限流错误
- **THEN** 系统记录限流错误
- **AND** 系统记录重试次数
- **AND** 系统记录最终结果

### Requirement: 成本估算

系统 SHALL 估算 LLM 调用的成本。

#### Scenario: 估算 OpenAI 模型成本

- **WHEN** 系统记录 OpenAI 模型的 token 使用量
- **THEN** 系统根据模型定价估算成本
- **AND** 成本估算基于 input tokens 和 output tokens
- **AND** 成本以美元为单位

#### Scenario: 估算其他模型成本

- **WHEN** 系统记录其他模型的 token 使用量
- **THEN** 系统根据配置的定价估算成本
- **AND** 如果没有定价配置，系统标记为"未知"

### Requirement: LLM 调用上下文关联

系统 SHALL 将 LLM 调用与执行上下文关联。

#### Scenario: 关联到 Agent

- **WHEN** Agent 调用 LLM
- **THEN** 系统记录 Agent ID
- **AND** 系统记录 Agent 角色
- **AND** 系统记录 Agent 当前状态

#### Scenario: 关联到执行阶段

- **WHEN** 在特定执行阶段调用 LLM
- **THEN** 系统记录执行阶段名称
- **AND** 系统记录阶段开始时间
- **AND** 系统记录阶段进度

#### Scenario: 关联到任务

- **WHEN** 为特定任务调用 LLM
- **THEN** 系统记录任务 ID
- **AND** 系统记录任务描述
- **AND** 系统记录任务状态

### Requirement: LLM 调用搜索和过滤

系统 SHALL 支持搜索和过滤 LLM 调用记录。

#### Scenario: 按 prompt 内容搜索

- **WHEN** 用户在 Phoenix UI 中搜索 prompt 内容
- **THEN** 系统返回包含该内容的 LLM 调用
- **AND** 搜索支持模糊匹配
- **AND** 搜索结果按时间排序

#### Scenario: 按模型过滤

- **WHEN** 用户在 Phoenix UI 中按模型过滤
- **THEN** 系统只显示使用该模型的 LLM 调用
- **AND** 过滤支持多选

#### Scenario: 按时间范围过滤

- **WHEN** 用户在 Phoenix UI 中按时间范围过滤
- **THEN** 系统只显示指定时间范围内的 LLM 调用
- **AND** 时间范围支持相对时间（如"最近 24 小时"）
