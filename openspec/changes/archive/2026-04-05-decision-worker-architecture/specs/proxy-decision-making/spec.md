## MODIFIED Requirements

### Requirement: 检测决策点

系统 SHALL 自动检测 agent 交互期间何时需要人工输入的决策，包括代码接受、技术选型、架构决策等多种类型。

#### Scenario: Agent 遇到模糊的用户请求

- **WHEN** agent 收到具有多种有效解释的用户请求
- **THEN** 系统将其识别为决策点
- **AND** 系统触发代理决策机制

#### Scenario: Agent 需要在选项之间选择

- **WHEN** agent 需要在多个行动选项之间选择
- **THEN** 系统根据 soul 偏好评估每个选项
- **AND** 系统根据风险级别做出决策或请求人工确认

#### Scenario: Agent 需要技术选型

- **WHEN** Worker Agent 提供多个技术选项
- **THEN** 系统将其识别为技术选型决策点
- **AND** 系统根据 Soul profile 的风险容忍度和偏好做决策

#### Scenario: Agent 需要架构决策

- **WHEN** 需要选择系统架构方案
- **THEN** 系统将其识别为架构决策点
- **AND** 系统根据 Soul profile 的结构偏好做决策

### Requirement: 将 soul 规则应用于决策

系统 SHALL 在做出代理决策时应用相关的 soul 规则，支持多种决策类型。

#### Scenario: 应用风险容忍度规则

- **WHEN** 做出涉及风险的决策
- **THEN** 系统检查用户的 risk_tolerance 特质
- **AND** 系统应用适当的风险规则（保守、平衡或激进）

#### Scenario: 应用沟通偏好规则

- **WHEN** 格式化响应或建议
- **THEN** 系统检查用户的 communication_preferences
- **AND** 系统相应地格式化输出（结构化、探索性或结论优先）

#### Scenario: 应用决策边界规则

- **WHEN** 做出跨越边界阈值的决策
- **THEN** 系统检查用户的 boundary_reminders
- **AND** 系统根据边界规则做出决策或升级给人工

#### Scenario: 应用结构偏好规则

- **WHEN** 做出架构或设计决策
- **THEN** 系统检查用户的 structure 特质
- **AND** 系统根据结构偏好选择方案（简单灵活 vs 复杂结构化）

#### Scenario: 应用细节导向规则

- **WHEN** 做出实现细节决策
- **THEN** 系统检查用户的 detail_orientation 特质
- **AND** 系统根据细节偏好选择方案（简洁 vs 详细）

## ADDED Requirements

### Requirement: 支持多种决策类型

系统 SHALL 支持多种决策类型，包括代码接受、技术选型、架构决策等。

#### Scenario: 代码接受决策

- **WHEN** Worker Agent 返回代码评估结果
- **THEN** Decision Agent 决定是否接受代码
- **AND** Decision Agent 基于 Soul profile 的风险容忍度做决策
- **AND** Decision Agent 记录决策理由

#### Scenario: 技术选型决策

- **WHEN** Worker Agent 提供多个技术选项
- **THEN** Decision Agent 选择最合适的选项
- **AND** Decision Agent 基于 Soul profile 的风险容忍度、结构偏好做决策
- **AND** Decision Agent 记录决策理由

#### Scenario: 架构决策

- **WHEN** 需要选择系统架构
- **THEN** Decision Agent 分析架构选项
- **AND** Decision Agent 基于 Soul profile 的结构偏好做决策
- **AND** Decision Agent 记录决策理由

#### Scenario: 实现方式决策

- **WHEN** 存在多种实现方式
- **THEN** Decision Agent 分析实现选项
- **AND** Decision Agent 基于 Soul profile 的细节导向做决策
- **AND** Decision Agent 记录决策理由

### Requirement: 与 Decision Agent 集成

系统 SHALL 将代理决策能力与 Decision Agent 集成，作为 Decision Agent 的核心决策引擎。

#### Scenario: Decision Agent 调用代理决策

- **WHEN** Decision Agent 需要做决策
- **THEN** Decision Agent 调用 ProxyDecisionMaker
- **AND** ProxyDecisionMaker 应用 Soul 规则
- **AND** ProxyDecisionMaker 返回决策结果

#### Scenario: Decision Agent 处理低置信度决策

- **WHEN** ProxyDecisionMaker 返回低置信度决策（< 0.5）
- **THEN** Decision Agent 询问用户确认
- **AND** Decision Agent 根据用户回答更新决策
- **AND** Decision Agent 记录用户偏好

#### Scenario: Decision Agent 处理高风险决策

- **WHEN** ProxyDecisionMaker 检测到高风险决策
- **THEN** Decision Agent 询问用户确认
- **AND** Decision Agent 提供决策上下文和风险说明
- **AND** Decision Agent 根据用户回答做最终决策

### Requirement: 决策上下文传递

系统 SHALL 在代理决策过程中传递完整的上下文信息。

#### Scenario: 传递任务上下文

- **WHEN** Decision Agent 调用代理决策
- **THEN** 系统传递任务描述、约束、目标
- **AND** 系统传递当前执行状态
- **AND** 系统传递历史决策（如相关）

#### Scenario: 传递选项信息

- **WHEN** Worker Agent 提供选项
- **THEN** 系统传递选项列表
- **AND** 系统传递每个选项的描述、优缺点、风险级别
- **AND** 系统传递选项的上下文信息

#### Scenario: 传递 Soul profile

- **WHEN** 做出代理决策
- **THEN** 系统传递用户的 Soul profile
- **AND** 系统传递相关的特质和偏好
- **AND** 系统传递自定义决策规则（如有）
