## Context

当前 Cinder CLI 系统已经具备基本的任务执行能力，使用 Rich 库提供简单的进度指示器（旋转动画）。执行日志系统使用 SQLite 存储执行历史，但缺少详细的时间跟踪和实时进度更新能力。

**当前架构限制**：
- Rich Progress 仅显示旋转动画和阶段名称，缺少时间信息
- 执行器在执行过程中不记录中间状态
- 数据库 `executions` 表有 `execution_time` 字段但未被充分利用
- Web Dashboard 只能查询历史记录，无法实时监控执行过程
- 没有历史数据分析能力，无法提供时间预估

**技术约束**：
- 必须兼容现有的 Click + Rich CLI 架构
- Web 端使用 Next.js + React Query，需要考虑实时更新方案
- SQLite 数据库需要支持新的时间跟踪字段
- 执行器是单线程同步执行，需要考虑如何支持实时推送

## Goals / Non-Goals

**Goals:**
- 在 CLI 端提供详细的进度信息（进度条、时间、速度）
- 实现 Web 端的实时进度监控
- 建立完整的时间跟踪数据模型
- 提供智能的时间预估算法
- 收集历史数据支持性能分析

**Non-Goals:**
- 不改变执行器的核心执行逻辑（仍然是同步执行）
- 不实现分布式执行或并行处理
- 不修改现有的任务分解和代码生成算法
- 不实现执行暂停/恢复功能（超出范围）

## Decisions

### 1. CLI 进度展示方案

**决策**: 使用 Rich 的 Progress 扩展列功能

**理由**:
- Rich 原生支持 `TimeElapsedColumn` 和 `TimeRemainingColumn`
- 可以自定义列显示速度和百分比
- 与现有代码无缝集成
- 性能开销小

**替代方案考虑**:
- ❌ 使用第三方进度条库（如 tqdm）- 需要替换现有 Rich 代码，改动大
- ❌ 自己实现进度条 - 工作量大，不如使用成熟方案

**实现细节**:
```python
progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(complete_style="green", finished_style="bold green"),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
    TextColumn("[cyan]{task.fields[speed]:.2f} tasks/min"),
)
```

### 2. Web 实时更新方案

**决策**: 使用 Server-Sent Events (SSE)

**理由**:
- SSE 比 WebSocket 更简单，适合单向推送场景
- FastAPI 原生支持 SSE（通过 `StreamingResponse`）
- 前端 EventSource API 简单易用
- 不需要维护双向连接状态
- 自动重连机制

**替代方案考虑**:
- ❌ 轮询（Polling）- 延迟高，服务器压力大，用户体验差
- ❌ WebSocket - 实现复杂，需要维护连接状态，对于单向推送过于重量级

**实现细节**:
```python
from fastapi.responses import StreamingResponse
import asyncio

@router.get("/current/progress")
async def get_current_progress():
    async def event_stream():
        while True:
            progress_data = get_progress_state()
            yield f"data: {json.dumps(progress_data)}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
```

### 3. 数据模型设计

**决策**: 扩展现有 `executions` 表，添加阶段时间戳 JSON 字段

**理由**:
- 避免复杂的表关联
- 阶段时间戳是执行过程的元数据，适合 JSON 存储
- 查询简单，性能好
- 易于扩展新的阶段

**数据库 Schema 变更**:
```sql
ALTER TABLE executions ADD COLUMN phase_timestamps TEXT;
ALTER TABLE executions ADD COLUMN progress_data TEXT;
ALTER TABLE executions ADD COLUMN speed_metrics TEXT;
```

**阶段时间戳结构**:
```json
{
  "plan": {
    "start": "2026-04-04T20:00:00",
    "end": "2026-04-04T20:00:12",
    "duration": 12.5
  },
  "generation": {
    "start": "2026-04-04T20:00:12",
    "end": "2026-04-04T20:02:34",
    "duration": 142.0,
    "tasks_completed": 3,
    "tasks_total": 5
  }
}
```

### 4. 进度预估算法

**决策**: 混合预估策略（历史平均 + 实时动态调整）

**理由**:
- 纯历史平均在初期没有数据时不可用
- 纯实时预估在执行初期不准确
- 混合策略可以在不同阶段提供合理的预估

**算法流程**:
```
1. 初始预估（任务分解后）
   - 基于任务数量和复杂度
   - 如果有历史数据，参考相似任务的平均时间
   
2. 阶段预估（每个阶段开始时）
   - PLAN: 固定预估 10-15 秒
   - GENERATION: 任务数 × 平均任务时间（历史数据）
   - EVALUATION: 任务数 × 平均评估时间
   - DECISION: 固定预估 5-10 秒

3. 实时调整（执行过程中）
   - 每秒更新一次
   - 剩余时间 = (总任务 - 已完成任务) × 当前速度
   - 置信度随执行进度增加
```

**置信度计算**:
```python
confidence = min(0.3 + (completed_percentage * 0.7), 0.95)
# 初期 30% 置信度，随进度增加最高 95%
```

### 5. 执行器改造方案

**决策**: 在执行器中添加进度跟踪器（Progress Tracker）

**理由**:
- 不修改核心执行逻辑
- 通过回调机制实时更新进度
- 支持多个监听者（CLI 显示、Web 推送）

**架构设计**:
```
AutonomousExecutor
├── ProgressTracker (新增)
│   ├── update_progress(phase, task, progress)
│   ├── record_time(phase, event)
│   ├── calculate_speed()
│   └── estimate_remaining()
├── ProgressBroadcaster (新增)
│   ├── add_listener(callback)
│   ├── broadcast(progress_data)
│   └── notify_listeners()
└── 执行逻辑（保持不变）
```

**线程安全考虑**:
- 执行器是单线程同步执行，无需锁
- Web SSE 在独立线程中读取进度状态
- 使用线程安全的队列传递进度更新

### 6. 前端状态管理

**决策**: 使用 React Query + EventSource

**理由**:
- React Query 已在项目中使用
- EventSource API 简单，自动重连
- 可以结合 React Query 的缓存机制

**实现方案**:
```typescript
// 自定义 Hook
function useRealtimeProgress(executionId: string) {
  const [progress, setProgress] = useState(null)
  
  useEffect(() => {
    const eventSource = new EventSource(
      `/api/executions/${executionId}/progress`
    )
    
    eventSource.onmessage = (event) => {
      setProgress(JSON.parse(event.data))
    }
    
    return () => eventSource.close()
  }, [executionId])
  
  return progress
}
```

## Risks / Trade-offs

### 风险 1: SSE 连接管理复杂性
**风险**: 多个客户端同时连接可能导致资源消耗，连接断开需要重连

**缓解措施**:
- 实现连接超时机制（30分钟无活动自动断开）
- 客户端实现指数退避重连策略
- 限制单个执行的最大连接数（10个）
- 提供轮询作为降级方案

### 风险 2: 预估准确性不足
**风险**: 初期预估可能严重偏离实际，导致用户不信任

**缓解措施**:
- 显示置信度区间（如 "预计 5±2 分钟"）
- 在 UI 上明确标注"预估值，仅供参考"
- 随着执行进度动态调整，提高准确度
- 收集用户反馈，持续优化算法

### 风险 3: 数据库性能影响
**风险**: 频繁写入进度数据可能影响数据库性能

**缓解措施**:
- 进度数据先写入内存，每 5 秒批量写入数据库
- 使用 WAL 模式提高 SQLite 并发性能
- 定期清理旧的详细进度数据（保留 30 天）
- 提供配置选项关闭详细进度记录

### 风险 4: 向后兼容性
**风险**: 新字段可能导致旧版本客户端不兼容

**缓解措施**:
- 新增字段都有默认值，不影响旧代码
- API 返回数据保持向后兼容，新字段可选
- 提供数据迁移脚本，平滑升级
- 版本号标记 API 变更

### Trade-off 1: 实时性 vs 性能
**权衡**: 更频繁的进度更新提供更好的实时性，但会增加系统开销

**选择**: 
- CLI 端：每个阶段更新一次（最小开销）
- Web 端：每秒更新一次（平衡实时性和性能）
- 可配置更新频率

### Trade-off 2: 预估复杂度 vs 可维护性
**权衡**: 更复杂的预估算法可能更准确，但难以维护

**选择**:
- 采用简单但有效的混合策略
- 优先保证可维护性
- 预留扩展接口，未来可以优化算法

## Migration Plan

### 阶段 1: 数据库迁移（向后兼容）
1. 添加新字段到 `executions` 表（都有默认值）
2. 创建数据迁移脚本 `migrate_add_progress_fields.py`
3. 测试迁移脚本在备份数据库上的执行
4. 部署迁移，验证现有功能不受影响

### 阶段 2: CLI 端实现（独立功能）
1. 实现 ProgressTracker 类
2. 修改 AutonomousExecutor 集成进度跟踪
3. 更新 CLI 显示逻辑
4. 测试 CLI 功能，确保不影响执行逻辑

### 阶段 3: Web 端实现（依赖阶段 2）
1. 实现 SSE 端点
2. 更新前端组件支持实时更新
3. 添加前端可视化图表
4. 测试多客户端并发场景

### 阶段 4: 预估算法（依赖阶段 2、3）
1. 收集历史数据建立基准
2. 实现预估算法
3. 在 CLI 和 Web 端集成预估显示
4. 监控预估准确性，持续优化

### 回滚策略
- 每个阶段都可以独立回滚
- 数据库迁移通过删除新字段回滚
- CLI/Web 功能通过配置开关控制
- 保留旧版本的 API 端点

## Open Questions

1. **进度数据的保留策略**: 详细进度数据应该保留多久？30天是否合适？
   - 建议：提供配置选项，默认 30 天，用户可调整

2. **多执行并发支持**: 如果用户同时启动多个执行，如何区分和管理？
   - 建议：为每个执行分配唯一 ID，SSE 端点支持按 ID 订阅

3. **前端可视化图表类型**: 使用什么图表库和图表类型展示进度？
   - 建议：使用 Recharts，展示时间线图和速度趋势图

4. **预估算法的初始训练数据**: 新用户没有历史数据时如何提供预估？
   - 建议：使用内置的基准数据（基于测试和典型场景）

5. **移动端适配**: Web Dashboard 是否需要支持移动端实时查看？
   - 建议：响应式设计，SSE 在移动浏览器中同样支持
