# Progress Tracking Enhancement - Developer Documentation

## Architecture Overview

The progress tracking system consists of several interconnected components:

```
┌─────────────────────────────────────────────────────────────┐
│                    Progress Tracking System                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Progress   │─────▶│   Progress   │─────▶│     Web      │
│   Tracker    │      │  Broadcaster │      │   Dashboard  │
└──────────────┘      └──────────────┘      └──────────────┘
       │                      │                      │
       │                      │                      │
       ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│    Time      │      │    Speed     │      │  Estimation  │
│   Recorder   │      │  Calculator  │      │    Engine    │
└──────────────┘      └──────────────┘      └──────────────┘
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  ExecutionLogger │
                    │   (Database)     │
                    └──────────────────┘
```

## Core Components

### 1. ProgressTracker

**Location**: `cinder_cli/executor/progress_tracker.py`

**Purpose**: Tracks execution progress state and calculates percentages.

**Key Methods**:
- `start_phase(phase)`: Begin tracking a new phase
- `update_phase_progress(progress)`: Update current phase progress
- `complete_phase(phase)`: Mark phase as complete
- `get_progress()`: Get current progress state

**Thread Safety**: Uses threading.Lock for thread-safe operations.

**Example**:
```python
tracker = ProgressTracker()
tracker.start_phase(ExecutionPhase.PLAN)
tracker.update_phase_progress(50.0)
progress = tracker.get_progress()
```

### 2. ProgressBroadcaster

**Location**: `cinder_cli/executor/progress_broadcaster.py`

**Purpose**: Manages progress listeners and broadcasts updates.

**Key Methods**:
- `add_listener(callback)`: Register a progress listener
- `remove_listener(callback)`: Unregister a listener
- `broadcast(progress_data)`: Send updates to all listeners

**Design Pattern**: Observer pattern with weak references.

**Example**:
```python
broadcaster = ProgressBroadcaster()

def my_callback(data):
    print(f"Progress: {data}")

broadcaster.add_listener(my_callback)
broadcaster.broadcast({"progress": 50})
```

### 3. TimeRecorder

**Location**: `cinder_cli/executor/time_recorder.py`

**Purpose**: Records timestamps for phases and tasks.

**Key Methods**:
- `start_phase(phase)`: Record phase start time
- `end_phase(phase)`: Record phase end time and calculate duration
- `start_task(task_id, description)`: Record task start
- `end_task(task_id)`: Record task end and calculate duration

**Data Structure**:
```python
{
  "plan": {
    "start": "2026-04-04T12:00:00",
    "end": "2026-04-04T12:00:15",
    "duration": 15.0
  }
}
```

### 4. SpeedCalculator

**Location**: `cinder_cli/executor/speed_calculator.py`

**Purpose**: Calculates execution speed metrics.

**Key Metrics**:
- Tasks per minute
- Average task time
- Phase-specific speeds

**Example**:
```python
calculator = SpeedCalculator()
calculator.start()
calculator.record_task_completed(duration=10.0)
speed = calculator.get_tasks_per_minute()  # e.g., 6.0 tasks/min
```

### 5. EstimationEngine

**Location**: `cinder_cli/executor/estimation_engine.py`

**Purpose**: Provides time estimation using multiple algorithms.

**Estimation Methods**:
1. **Initial estimation**: Based on task count and historical data
2. **Dynamic estimation**: Adjusts based on real-time progress
3. **Phase estimation**: Estimates for individual phases

**Confidence Calculation**:
```python
confidence = min(0.95, 0.3 + (progress / 100.0) * 0.65)
# Starts at 30%, increases to max 95%
```

### 6. ProgressSnapshot

**Location**: `cinder_cli/executor/progress_snapshot.py`

**Purpose**: Captures execution state at a point in time.

**Use Case**: Storing intermediate states for analysis or recovery.

## Database Schema

### executions Table (Enhanced)

```sql
CREATE TABLE executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    goal TEXT NOT NULL,
    task_tree TEXT,
    results TEXT,
    status TEXT NOT NULL,
    created_files TEXT,
    execution_time REAL,
    -- New fields
    phase_timestamps TEXT,    -- JSON: phase timing data
    progress_data TEXT,       -- JSON: progress snapshots
    speed_metrics TEXT,       -- JSON: speed calculations
    estimation_data TEXT      -- JSON: estimation history
);
```

### execution_statistics Table (New)

```sql
CREATE TABLE execution_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    goal_type TEXT,
    total_tasks INTEGER,
    execution_time REAL,
    phase_breakdown TEXT,     -- JSON: phase durations
    speed_metrics TEXT,       -- JSON: speed data
    quality_score REAL,
    success BOOLEAN
);
```

## Web API Endpoints

### SSE Endpoints

#### Stream Current Progress
```
GET /api/executions/current/progress
```

**Response**: Server-Sent Events stream
```
data: {"timestamp": 1234567890, "status": "active", "message": "..."}
```

#### Stream Execution Progress
```
GET /api/executions/{id}/progress
```

**Response**: SSE stream with execution-specific data
```
data: {"execution_id": 123, "status": "success", "progress_data": {...}}
```

### REST Endpoints

#### Get Estimation Statistics
```
GET /api/executions/stats/estimation
```

**Response**:
```json
{
  "statistics": {
    "total": 100,
    "avg_execution_time": 120.5,
    "avg_tasks_count": 5.2,
    "phase_statistics": {
      "plan": {"avg_duration": 15.0, "count": 100}
    }
  }
}
```

## Frontend Integration

### React Hook: useRealtimeProgress

**Location**: `cinder_cli/web/frontend/hooks/useRealtimeProgress.ts`

**Usage**:
```typescript
import { useRealtimeProgress } from '@/hooks/useRealtimeProgress'

function MyComponent() {
  const { progress, isConnected, error } = useRealtimeProgress(executionId)
  
  if (!isConnected) return <div>Connecting...</div>
  if (error) return <div>Error: {error}</div>
  
  return <div>Progress: {progress?.overall_progress}%</div>
}
```

**Features**:
- Automatic reconnection with exponential backoff
- Connection status tracking
- Error handling

### Components

#### RealtimeProgressBar
- Animated progress bar
- Phase indicators
- Speed and time display

#### PhaseTimeline
- Visual timeline of phases
- Status indicators
- Duration display

#### SpeedTrendChart
- Line chart using Recharts
- Historical speed visualization

## Performance Considerations

### Database Optimization

1. **Batch Updates**: Progress data is batched and written every 5 seconds
2. **WAL Mode**: Write-Ahead Logging for better concurrency
3. **Indexes**: Optimized indexes on timestamp and status fields

### SSE Optimization

1. **Connection Pooling**: Limit concurrent connections (default: 10)
2. **Timeout Management**: Auto-disconnect after 30 minutes
3. **Heartbeat**: Keep-alive messages every 15 seconds

### Memory Management

1. **Weak References**: ProgressBroadcaster uses WeakSet for listeners
2. **Snapshot Limits**: Only keep last 100 progress snapshots
3. **Data Retention**: Automatic cleanup of old data (default: 30 days)

## Testing Strategy

### Unit Tests

**Location**: `tests/test_progress_tracking.py`

**Coverage**:
- ProgressTracker state management
- ProgressBroadcaster listener management
- TimeRecorder timing accuracy
- SpeedCalculator calculations
- EstimationEngine algorithms

### Integration Tests

**Location**: `tests/test_executor_integration.py`

**Coverage**:
- End-to-end execution with progress tracking
- Database persistence
- SSE streaming
- Frontend-backend integration

### Performance Tests

**Location**: `tests/test_performance.py`

**Metrics**:
- Progress tracking overhead (< 5%)
- Database write performance
- SSE connection scalability
- Memory usage under load

## Configuration Options

### Progress Tracking

```yaml
progress_tracking:
  enabled: true
  update_interval: 1  # seconds
  batch_updates: true
  batch_interval: 5   # seconds
```

### Estimation

```yaml
estimation:
  enabled: true
  min_confidence: 0.2
  max_confidence: 0.95
  historical_weight: 0.7
```

### Database

```yaml
database:
  wal_mode: true
  connection_pool: 5
  data_retention_days: 30
```

### Web Server

```yaml
web:
  max_sse_connections: 10
  sse_timeout: 30  # minutes
  heartbeat_interval: 15  # seconds
```

## Extending the System

### Adding Custom Progress Listeners

```python
from cinder_cli.executor import AutonomousExecutor

class MyProgressListener:
    def __call__(self, progress_data):
        # Custom handling
        send_to_webhook(progress_data)
        write_to_log(progress_data)

executor = AutonomousExecutor(config)
executor.progress_broadcaster.add_listener(MyProgressListener())
```

### Custom Estimation Algorithms

```python
from cinder_cli.executor.estimation_engine import EstimationEngine

class MyEstimationEngine(EstimationEngine):
    def estimate_initial(self, tasks_count, goal_type=""):
        # Custom algorithm
        base_estimate = super().estimate_initial(tasks_count, goal_type)
        
        # Apply custom factors
        if goal_type == "web_app":
            base_estimate *= 1.5
        
        return base_estimate
```

### Custom Progress Display

```python
from cinder_cli.executor import ProgressTracker

class MyProgressDisplay:
    def __init__(self, tracker):
        self.tracker = tracker
    
    def render(self):
        progress = self.tracker.get_progress()
        # Custom rendering logic
        return f"[{progress['current_phase']}] {progress['overall_progress']:.0f}%"
```

## Troubleshooting Guide

### Common Issues

1. **Progress not updating**
   - Check if tracking is enabled
   - Verify database connection
   - Check thread safety

2. **SSE connection drops**
   - Check network stability
   - Verify timeout settings
   - Check connection limits

3. **Inaccurate estimates**
   - Verify historical data exists
   - Check estimation algorithm
   - Review confidence levels

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('cinder_cli.executor')
logger.setLevel(logging.DEBUG)
```

### Performance Profiling

Profile progress tracking overhead:

```python
import cProfile

profiler = cProfile.Profile()
profiler.enable()

# Run execution
executor.execute("test goal")

profiler.disable()
profiler.print_stats(sort='cumulative')
```

## Future Enhancements

### Planned Features

1. **Machine Learning Estimates**: Use ML for better predictions
2. **Distributed Tracking**: Support for distributed execution
3. **Advanced Analytics**: Deeper insights into execution patterns
4. **Custom Dashboards**: User-configurable monitoring views

### Contributing

When contributing to the progress tracking system:

1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Consider thread safety
5. Profile performance impact
