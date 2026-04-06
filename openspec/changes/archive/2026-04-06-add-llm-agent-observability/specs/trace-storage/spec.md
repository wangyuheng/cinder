## ADDED Requirements

### Requirement: Trace 数据存储初始化

系统 SHALL 支持初始化 trace 数据存储，使用 Phoenix 管理的 SQLite 数据库。

#### Scenario: 初始化 Phoenix 数据库

- **WHEN** Phoenix 服务器首次启动
- **THEN** 系统创建 SQLite 数据库文件
- **AND** 数据库文件位于用户主目录的 .cinder 目录下
- **AND** 数据库文件名为 traces.db

#### Scenario: 创建 trace 数据表

- **WHEN** Phoenix 初始化数据库
- **THEN** 系统创建 traces 表
- **AND** 系统创建 spans 表
- **AND** 系统创建 llm_calls 表
- **AND** 系统创建必要的索引

### Requirement: Trace 数据持久化

系统 SHALL 支持持久化 trace 数据到 SQLite 数据库。

#### Scenario: 持久化 trace 元数据

- **WHEN** 系统创建新的 trace
- **THEN** 系统将 trace 元数据写入数据库
- **AND** 元数据包括 trace_id, goal, mode, start_time
- **AND** 写入操作是原子的

#### Scenario: 持久化 span 数据

- **WHEN** 系统创建新的 span
- **THEN** 系统将 span 数据写入数据库
- **AND** span 数据包括 span_id, operation_name, attributes
- **AND** 写入操作是原子的

#### Scenario: 持久化 LLM 调用数据

- **WHEN** 系统记录 LLM 调用
- **THEN** 系统将 LLM 调用数据写入数据库
- **AND** 数据包括 prompt, response, tokens
- **AND** 写入操作是原子的

### Requirement: Trace 数据查询

系统 SHALL 支持查询 trace 数据。

#### Scenario: 查询 trace 列表

- **WHEN** 用户请求 trace 列表
- **THEN** 系统从数据库查询 trace 列表
- **AND** 列表按时间倒序排列
- **AND** 列表支持分页

#### Scenario: 查询 trace 详情

- **WHEN** 用户请求特定 trace 的详情
- **THEN** 系统从数据库查询 trace 详情
- **AND** 详情包括所有相关的 spans
- **AND** 详情包括所有相关的 LLM 调用

#### Scenario: 查询 span 树

- **WHEN** 用户请求 trace 的 span 树
- **THEN** 系统从数据库查询所有 spans
- **AND** 系统构建 span 树结构
- **AND** 树结构反映父子关系

### Requirement: Trace 数据导出

系统 SHALL 支持导出 trace 数据为标准格式。

#### Scenario: 导出为 JSON 格式

- **WHEN** 用户执行 `cinder trace export <trace-id> --format json`
- **THEN** 系统导出 trace 数据为 JSON 格式
- **AND** JSON 格式符合 OpenTelemetry 标准
- **AND** JSON 文件包含完整的 trace 信息

#### Scenario: 导出为 OTLP 格式

- **WHEN** 用户执行 `cinder trace export <trace-id> --format otlp`
- **THEN** 系统导出 trace 数据为 OTLP 格式
- **AND** OTLP 格式可以被 Jaeger 等工具导入
- **AND** 导出文件为 protobuf 或 JSON 格式

#### Scenario: 导出所有 trace 数据

- **WHEN** 用户执行 `cinder trace export --all`
- **THEN** 系统导出所有 trace 数据
- **AND** 导出为压缩文件
- **AND** 压缩文件包含多个 trace 文件

### Requirement: Trace 数据清理

系统 SHALL 支持清理旧的 trace 数据。

#### Scenario: 自动清理旧数据

- **WHEN** trace 数据超过保留期限（默认 30 天）
- **THEN** 系统自动删除旧的 trace 数据
- **AND** 删除操作在后台执行
- **AND** 删除操作不影响系统性能

#### Scenario: 手动清理数据

- **WHEN** 用户执行 `cinder trace clean --before <date>`
- **THEN** 系统删除指定日期之前的 trace 数据
- **AND** 系统显示删除的数据量
- **AND** 删除操作不可逆

#### Scenario: 配置保留策略

- **WHEN** 用户在 cinder.yaml 中配置 tracing.retention_days
- **THEN** 系统按照配置的保留期限清理数据
- **AND** 默认保留期限为 30 天

### Requirement: Trace 数据备份

系统 SHALL 支持备份 trace 数据。

#### Scenario: 手动备份数据

- **WHEN** 用户执行 `cinder trace backup`
- **THEN** 系统创建数据库备份
- **AND** 备份文件包含时间戳
- **AND** 备份文件存储在 .cinder/backups 目录

#### Scenario: 自动定期备份

- **WHEN** 系统配置了自动备份
- **THEN** 系统定期创建数据库备份
- **AND** 备份频率可配置
- **AND** 备份文件自动清理旧版本

#### Scenario: 恢复备份数据

- **WHEN** 用户执行 `cinder trace restore <backup-file>`
- **THEN** 系统从备份文件恢复数据
- **AND** 系统验证备份文件完整性
- **AND** 恢复操作覆盖现有数据

### Requirement: Trace 数据压缩

系统 SHALL 支持压缩大型 trace 数据。

#### Scenario: 压缩 prompt 和 response

- **WHEN** prompt 或 response 内容超过 1KB
- **THEN** 系统自动压缩内容
- **AND** 压缩使用 gzip 算法
- **AND** 查询时自动解压

#### Scenario: 配置压缩阈值

- **WHEN** 用户在 cinder.yaml 中配置 tracing.compression_threshold
- **THEN** 系统按照配置的阈值压缩数据
- **AND** 默认阈值为 1KB

### Requirement: Trace 数据索引

系统 SHALL 为 trace 数据创建索引以提升查询性能。

#### Scenario: 创建时间索引

- **WHEN** 系统创建 trace 数据表
- **THEN** 系统在 timestamp 字段创建索引
- **AND** 索引提升按时间查询的性能

#### Scenario: 创建 trace_id 索引

- **WHEN** 系统创建 spans 表
- **THEN** 系统在 trace_id 字段创建索引
- **AND** 索引提升按 trace 查询的性能

#### Scenario: 创建 agent_id 索引

- **WHEN** 系统创建 spans 表
- **THEN** 系统在 agent_id 字段创建索引
- **AND** 索引提升按 Agent 查询的性能

### Requirement: Trace 数据统计

系统 SHALL 支持 trace 数据的统计分析。

#### Scenario: 统计 trace 数量

- **WHEN** 用户请求 trace 统计信息
- **THEN** 系统返回总 trace 数量
- **AND** 系统返回今日 trace 数量
- **AND** 系统返回本周 trace 数量

#### Scenario: 统计 token 使用量

- **WHEN** 用户请求 token 统计信息
- **THEN** 系统返回总 token 使用量
- **AND** 系统返回按模型分组的 token 使用量
- **AND** 系统返回按日期分组的 token 使用量

#### Scenario: 统计 Agent 执行情况

- **WHEN** 用户请求 Agent 统计信息
- **THEN** 系统返回 Agent 执行次数
- **AND** 系统返回 Agent 成功率
- **AND** 系统返回 Agent 平均执行时间

### Requirement: Trace 数据迁移

系统 SHALL 支持 trace 数据的迁移和升级。

#### Scenario: 数据库 schema 升级

- **WHEN** 系统升级到新版本
- **THEN** 系统自动升级数据库 schema
- **AND** 升级过程保留现有数据
- **AND** 升级失败时回滚

#### Scenario: 数据导入

- **WHEN** 用户执行 `cinder trace import <file>`
- **THEN** 系统从文件导入 trace 数据
- **AND** 文件格式支持 JSON 和 OTLP
- **AND** 导入时验证数据完整性
