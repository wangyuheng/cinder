## ADDED Requirements

### Requirement: 上下文管理系统

系统 SHALL 实现上下文管理系统，维护全局状态和历史决策，支持 Decision Agent 的决策过程。

#### Scenario: 创建执行上下文

- **WHEN** Decision Agent 开始处理用户目标
- **THEN** 系统创建新的执行上下文
- **AND** 上下文包含用户目标、约束、初始状态
- **AND** 上下文分配唯一的执行 ID

#### Scenario: 更新执行上下文

- **WHEN** Decision Agent 做出决策或 Worker 返回结果
- **THEN** 系统更新执行上下文
- **AND** 上下文记录新的状态和数据
- **AND** 上下文保留历史记录

#### Scenario: 查询执行上下文

- **WHEN** Decision Agent 需要历史信息
- **THEN** 系统从上下文中查询相关数据
- **AND** 系统返回匹配的历史记录
- **AND** 系统支持按时间、类型过滤

### Requirement: 短期上下文管理

系统 SHALL 在内存中管理短期上下文，支持快速访问和频繁更新。

#### Scenario: 存储当前会话数据

- **WHEN** Decision Agent 在会话中产生数据
- **THEN** 系统将数据存储在内存中
- **AND** 数据包含对话历史、临时状态、中间结果
- **AND** 数据与会话 ID 关联

#### Scenario: 访问当前会话数据

- **WHEN** Decision Agent 需要当前会话的数据
- **THEN** 系统从内存中快速读取
- **AND** 系统返回最新的数据
- **AND** 访问时间 < 10ms

#### Scenario: 清理过期会话数据

- **WHEN** 会话结束或超时
- **THEN** 系统清理内存中的会话数据
- **AND** 系统保留必要的持久化数据
- **AND** 系统释放内存资源

### Requirement: 长期上下文管理

系统 SHALL 在 SQLite 中管理长期上下文，支持跨会话的数据持久化。

#### Scenario: 持久化历史决策

- **WHEN** Decision Agent 做出决策
- **THEN** 系统将决策记录到 SQLite
- **AND** 记录包含决策内容、理由、置信度、时间戳
- **AND** 记录与用户和 Soul profile 关联

#### Scenario: 持久化用户偏好

- **WHEN** 用户表达偏好或覆盖决策
- **THEN** 系统将偏好记录到 SQLite
- **AND** 记录包含偏好内容、上下文、时间戳
- **AND** 系统更新 Soul profile（如需要）

#### Scenario: 持久化项目信息

- **WHEN** 系统识别到项目相关信息
- **THEN** 系统将项目信息记录到 SQLite
- **AND** 记录包含项目路径、技术栈、配置
- **AND** 系统支持跨会话访问项目信息

#### Scenario: 查询历史决策

- **WHEN** Decision Agent 需要历史决策信息
- **THEN** 系统从 SQLite 查询
- **AND** 系统支持按时间范围、决策类型过滤
- **AND** 系统返回匹配的决策列表

### Requirement: 上下文同步

系统 SHALL 确保短期上下文和长期上下文的同步，避免数据不一致。

#### Scenario: 定期同步到持久化

- **WHEN** 短期上下文发生变化
- **THEN** 系统定期（如每 30 秒）同步到 SQLite
- **AND** 系统记录同步时间戳
- **AND** 系统处理同步冲突（如需要）

#### Scenario: 会话结束时同步

- **WHEN** 会话结束
- **THEN** 系统立即同步所有短期上下文到 SQLite
- **AND** 系统确保所有数据都已持久化
- **AND** 系统记录会话结束时间

#### Scenario: 恢复会话时加载

- **WHEN** 用户恢复中断的会话
- **THEN** 系统从 SQLite 加载长期上下文
- **AND** 系统重建短期上下文
- **AND** 系统恢复到中断前的状态

### Requirement: 上下文大小限制

系统 SHALL 限制上下文大小，避免内存耗尽和性能下降。

#### Scenario: 限制短期上下文大小

- **WHEN** 短期上下文超过限制（如 100MB）
- **THEN** 系统移除最旧的数据
- **AND** 系统保留关键数据（如当前状态）
- **AND** 系统记录清理事件

#### Scenario: 限制长期上下文保留时间

- **WHEN** 长期上下文超过保留时间（如 30 天）
- **THEN** 系统归档或删除旧数据
- **AND** 系统保留摘要信息
- **AND** 系统记录归档事件

#### Scenario: 压缩上下文数据

- **WHEN** 上下文数据包含大量重复或冗余信息
- **THEN** 系统压缩上下文数据
- **AND** 系统保留关键信息
- **AND** 系统记录压缩比例

### Requirement: 上下文隔离

系统 SHALL 确保不同用户和会话的上下文隔离，避免数据泄露。

#### Scenario: 用户间上下文隔离

- **WHEN** 多个用户使用系统
- **THEN** 每个用户的上下文相互隔离
- **AND** 用户 A 无法访问用户 B 的上下文
- **AND** 系统验证所有上下文访问请求

#### Scenario: 会话间上下文隔离

- **WHEN** 同一用户有多个并发会话
- **THEN** 每个会话的上下文相互隔离
- **AND** 会话 A 无法访问会话 B 的短期上下文
- **AND** 会话可以共享长期上下文（如用户偏好）

#### Scenario: 项目间上下文隔离

- **WHEN** 用户在不同项目中工作
- **THEN** 每个项目的上下文相互隔离
- **AND** 项目 A 无法访问项目 B 的上下文
- **AND** 系统根据项目路径隔离上下文

### Requirement: 上下文访问接口

系统 SHALL 提供统一的上下文访问接口，简化 Decision Agent 的使用。

#### Scenario: 读取上下文数据

- **WHEN** Decision Agent 调用 `context.get(key)`
- **THEN** 系统返回对应的值
- **AND** 如果值不存在，返回 None 或默认值
- **AND** 系统记录访问日志（如配置）

#### Scenario: 写入上下文数据

- **WHEN** Decision Agent 调用 `context.set(key, value)`
- **THEN** 系统存储键值对
- **AND** 系统更新上下文时间戳
- **AND** 系统触发同步（如需要）

#### Scenario: 查询历史数据

- **WHEN** Decision Agent 调用 `context.query(filter)`
- **THEN** 系统返回匹配的历史数据
- **AND** 系统支持按时间、类型、关键词过滤
- **AND** 系统支持分页和排序

#### Scenario: 清除上下文数据

- **WHEN** Decision Agent 调用 `context.clear()`
- **THEN** 系统清除当前会话的短期上下文
- **AND** 系统保留长期上下文
- **AND** 系统记录清除事件
