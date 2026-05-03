## Why

当前 Cinder CLI 在执行任务时缺少关键的进度信息展示，用户无法了解执行速度、已耗时和预估剩余时间。这导致用户在长时间运行的任务中感到焦虑和不确定，无法合理安排时间。同时，Web Dashboard 只能查看历史记录，无法实时监控正在执行的任务，用户体验较差。

现在改进进度展示功能，可以显著提升用户体验，让用户对任务执行状态有清晰的掌控，增强系统的透明度和专业性。

## What Changes

### CLI 端增强
- 在 Rich Progress 中添加时间列（已耗时、预估剩余时间）
- 添加进度条显示百分比完成度
- 显示当前执行速度（任务/分钟、阶段完成速度）
- 在阶段级别展示详细进度信息
- 记录每个阶段的开始时间、结束时间和耗时

### Web Dashboard 实时化
- 实现基于 Server-Sent Events (SSE) 的实时进度推送
- 添加实时进度条和时间统计展示
- 展示阶段级别的执行进度
- 显示速度指标和历史对比
- 添加执行过程的可视化图表

### 数据层增强
- 记录每个执行阶段的详细时间戳
- 计算并存储执行速度指标
- 建立历史数据统计基础，支持预估计算
- 添加执行过程的中间状态记录

### 预估算法
- 基于历史数据计算平均执行时间
- 根据任务复杂度进行初始预估
- 实时动态调整预估时间
- 提供置信度区间显示

## Capabilities

### New Capabilities

- `cli-progress-display`: CLI 端的实时进度展示，包括进度条、时间统计、速度指标和阶段详情
- `web-realtime-progress`: Web Dashboard 的实时进度更新，基于 SSE 推送执行状态
- `execution-time-tracking`: 执行时间跟踪系统，记录各阶段的详细时间数据
- `progress-estimation`: 智能进度预估系统，基于历史数据和实时速度动态预测剩余时间

### Modified Capabilities

- `autonomous-executor`: 修改执行器以支持进度跟踪和时间记录，在执行过程中实时更新进度信息

## Impact

### 代码影响
- `cinder_cli/executor/autonomous_executor.py` - 添加进度跟踪和时间记录逻辑
- `cinder_cli/executor/execution_logger.py` - 增强日志记录，存储详细的时间数据
- `cinder_cli/cli.py` - 更新 CLI 命令以展示增强的进度信息
- `cinder_cli/web/server.py` - 添加 SSE 端点支持实时推送
- `cinder_cli/web/api/executions.py` - 添加实时进度 API
- `cinder_cli/web/frontend/app/executions/` - 更新前端组件展示实时进度

### 数据库影响
- 在 `executions` 表中添加阶段时间戳字段
- 添加执行统计表存储历史性能数据
- 可能需要数据迁移脚本

### API 影响
- 新增 `/api/executions/current/progress` SSE 端点
- 增强 `/api/executions/{id}` 返回详细的时间统计
- 新增 `/api/executions/stats/estimation` 提供预估数据

### 依赖影响
- 前端需要处理 SSE 连接和状态管理
- 可能需要添加前端图表库（如 Recharts）
- 后端需要支持 SSE 长连接管理

### 用户体验影响
- CLI 输出更加信息丰富，用户可以实时了解进度
- Web Dashboard 从静态历史查看变为实时监控工具
- 用户可以更好地规划时间，减少等待焦虑
- 提供历史数据对比，帮助用户了解性能趋势
