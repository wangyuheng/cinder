## ADDED Requirements

### Requirement: CLI trace 列表命令

系统 SHALL 提供 CLI 命令列出最近的 trace 记录。

#### Scenario: 列出最近的 trace

- **WHEN** 用户执行 `cinder trace list`
- **THEN** 系统显示最近 20 条 trace 记录
- **AND** 每条记录显示 trace_id, goal, status, timestamp
- **AND** 记录按时间倒序排列

#### Scenario: 列出指定数量的 trace

- **WHEN** 用户执行 `cinder trace list --limit 50`
- **THEN** 系统显示最近 50 条 trace 记录
- **AND** 记录按时间倒序排列

#### Scenario: 按状态过滤 trace

- **WHEN** 用户执行 `cinder trace list --status completed`
- **THEN** 系统只显示状态为 "completed" 的 trace
- **AND** 过滤支持多个状态值

#### Scenario: 按时间范围过滤 trace

- **WHEN** 用户执行 `cinder trace list --since "2024-01-01"`
- **THEN** 系统只显示指定日期之后的 trace
- **AND** 时间范围支持相对时间（如 "7d", "24h"）

### Requirement: CLI trace 详情命令

系统 SHALL 提供 CLI 命令显示 trace 的详细信息。

#### Scenario: 显示 trace 基本信息

- **WHEN** 用户执行 `cinder trace show <trace-id>`
- **THEN** 系统显示 trace 基本信息
- **AND** 信息包括 trace_id, goal, mode, status
- **AND** 信息包括 start_time, end_time, duration

#### Scenario: 显示 trace span 树

- **WHEN** 用户执行 `cinder trace show <trace-id> --tree`
- **THEN** 系统以树形结构显示所有 spans
- **AND** 树形结构显示父子关系
- **AND** 每个 span 显示名称和持续时间

#### Scenario: 显示 trace LLM 调用

- **WHEN** 用户执行 `cinder trace show <trace-id> --llm-calls`
- **THEN** 系统显示所有 LLM 调用
- **AND** 每个调用显示模型名称和 token 使用量
- **AND** 每个调用显示 prompt 和 response 摘要

#### Scenario: 显示完整 trace 详情

- **WHEN** 用户执行 `cinder trace show <trace-id> --full`
- **THEN** 系统显示完整的 trace 详情
- **AND** 详情包括所有 span 的完整信息
- **AND** 详情包括所有 LLM 调用的完整内容

### Requirement: CLI trace 导出命令

系统 SHALL 提供 CLI 命令导出 trace 数据。

#### Scenario: 导出为 JSON 格式

- **WHEN** 用户执行 `cinder trace export <trace-id>`
- **THEN** 系统导出 trace 数据为 JSON 文件
- **AND** 文件名为 trace_<trace-id>_<timestamp>.json
- **AND** 文件保存在当前目录

#### Scenario: 导出为 OTLP 格式

- **WHEN** 用户执行 `cinder trace export <trace-id> --format otlp`
- **THEN** 系统导出 trace 数据为 OTLP 格式
- **AND** 文件可以被 Jaeger 等工具导入

#### Scenario: 导出所有 trace

- **WHEN** 用户执行 `cinder trace export --all`
- **THEN** 系统导出所有 trace 数据
- **AND** 导出为压缩文件
- **AND** 压缩文件名为 traces_<timestamp>.tar.gz

#### Scenario: 导出到指定路径

- **WHEN** 用户执行 `cinder trace export <trace-id> --output /path/to/file.json`
- **THEN** 系统导出 trace 数据到指定路径
- **AND** 如果路径不存在，系统创建目录

### Requirement: CLI Phoenix 启动命令

系统 SHALL 提供 CLI 命令启动 Phoenix 服务器。

#### Scenario: 启动 Phoenix 服务器

- **WHEN** 用户执行 `cinder phoenix start`
- **THEN** 系统启动 Phoenix 服务器
- **AND** 服务器监听默认端口 6006
- **AND** 系统显示访问 URL

#### Scenario: 指定端口启动

- **WHEN** 用户执行 `cinder phoenix start --port 8080`
- **THEN** 系统在指定端口启动 Phoenix 服务器
- **AND** 系统显示访问 URL

#### Scenario: 后台启动 Phoenix

- **WHEN** 用户执行 `cinder phoenix start --daemon`
- **THEN** 系统在后台启动 Phoenix 服务器
- **AND** 系统显示进程 ID
- **AND** 系统显示如何停止服务器

#### Scenario: Phoenix 已在运行

- **WHEN** 用户执行 `cinder phoenix start`
- **AND** Phoenix 服务器已在运行
- **THEN** 系统提示服务器已在运行
- **AND** 系统显示访问 URL

### Requirement: CLI Phoenix 停止命令

系统 SHALL 提供 CLI 命令停止 Phoenix 服务器。

#### Scenario: 停止 Phoenix 服务器

- **WHEN** 用户执行 `cinder phoenix stop`
- **THEN** 系统停止 Phoenix 服务器
- **AND** 系统确认服务器已停止

#### Scenario: 强制停止 Phoenix

- **WHEN** 用户执行 `cinder phoenix stop --force`
- **THEN** 系统强制停止 Phoenix 服务器
- **AND** 系统终止相关进程

### Requirement: CLI trace 清理命令

系统 SHALL 提供 CLI 命令清理旧的 trace 数据。

#### Scenario: 清理旧数据

- **WHEN** 用户执行 `cinder trace clean --before "2024-01-01"`
- **THEN** 系统删除指定日期之前的 trace 数据
- **AND** 系统显示删除的数据量
- **AND** 系统请求用户确认

#### Scenario: 清理所有数据

- **WHEN** 用户执行 `cinder trace clean --all`
- **THEN** 系统删除所有 trace 数据
- **AND** 系统请求用户确认
- **AND** 系统显示删除的数据量

#### Scenario: 清理失败数据

- **WHEN** 用户执行 `cinder trace clean --status error`
- **THEN** 系统只删除状态为 "error" 的 trace
- **AND** 系统显示删除的数据量

### Requirement: CLI trace 统计命令

系统 SHALL 提供 CLI 命令显示 trace 统计信息。

#### Scenario: 显示总体统计

- **WHEN** 用户执行 `cinder trace stats`
- **THEN** 系统显示总体统计信息
- **AND** 统计包括总 trace 数量
- **AND** 统计包括成功率
- **AND** 统计包括平均执行时间

#### Scenario: 显示 token 统计

- **WHEN** 用户执行 `cinder trace stats --tokens`
- **THEN** 系统显示 token 使用统计
- **AND** 统计包括总 token 使用量
- **AND** 统计包括按模型分组的 token 使用量
- **AND** 统计包括估算成本

#### Scenario: 显示 Agent 统计

- **WHEN** 用户执行 `cinder trace stats --agents`
- **THEN** 系统显示 Agent 执行统计
- **AND** 统计包括每个 Agent 的执行次数
- **AND** 统计包括每个 Agent 的成功率
- **AND** 统计包括每个 Agent 的平均执行时间

### Requirement: CLI trace 搜索命令

系统 SHALL 提供 CLI 命令搜索 trace 数据。

#### Scenario: 按 prompt 内容搜索

- **WHEN** 用户执行 `cinder trace search "create function"`
- **THEN** 系统搜索包含该内容的 trace
- **AND** 搜索范围包括 prompt 和 response
- **AND** 搜索结果按相关性排序

#### Scenario: 按 Agent ID 搜索

- **WHEN** 用户执行 `cinder trace search --agent worker_1`
- **THEN** 系统搜索该 Agent 的所有 trace
- **AND** 搜索结果按时间排序

#### Scenario: 按 trace ID 搜索

- **WHEN** 用户执行 `cinder trace search --id trace_abc123`
- **THEN** 系统显示该 trace 的详情
- **AND** 等同于 `cinder trace show trace_abc123`

### Requirement: CLI trace 对比命令

系统 SHALL 提供 CLI 命令对比两个 trace。

#### Scenario: 对比两个 trace

- **WHEN** 用户执行 `cinder trace diff <trace-id-1> <trace-id-2>`
- **THEN** 系统显示两个 trace 的差异
- **AND** 差异包括执行时间差异
- **AND** 差异包括 token 使用量差异
- **AND** 差异包括 LLM 调用次数差异

#### Scenario: 对比 trace 结构

- **WHEN** 用户执行 `cinder trace diff <trace-id-1> <trace-id-2> --structure`
- **THEN** 系统显示两个 trace 的结构差异
- **AND** 差异包括 span 树结构差异
- **AND** 差异包括决策路径差异

### Requirement: CLI trace 监控命令

系统 SHALL 提供 CLI 命令实时监控 trace。

#### Scenario: 实时监控 trace

- **WHEN** 用户执行 `cinder trace monitor`
- **THEN** 系统实时显示新的 trace
- **AND** 显示包括 trace_id, goal, status
- **AND** 按 Ctrl+C 退出监控

#### Scenario: 监控特定 Agent

- **WHEN** 用户执行 `cinder trace monitor --agent worker_1`
- **THEN** 系统只显示该 Agent 的 trace
- **AND** 实时更新显示

### Requirement: CLI 配置管理

系统 SHALL 提供 CLI 命令管理 trace 配置。

#### Scenario: 显示当前配置

- **WHEN** 用户执行 `cinder trace config show`
- **THEN** 系统显示当前 trace 配置
- **AND** 配置包括是否启用 trace
- **AND** 配置包括 Phoenix 服务器地址
- **AND** 配置包括保留期限

#### Scenario: 修改配置

- **WHEN** 用户执行 `cinder trace config set enabled false`
- **THEN** 系统修改配置
- **AND** 系统保存配置到 cinder.yaml
- **AND** 系统显示修改后的配置
