# Progress Tracking Enhancement - User Guide

## Overview

The progress tracking enhancement provides real-time visibility into task execution, including:

- **Real-time progress bars** with percentage completion
- **Time tracking** (elapsed and estimated remaining time)
- **Speed metrics** (tasks per minute)
- **Phase-level details** with timelines
- **Historical data analysis** for better estimations

## CLI Usage

### Basic Execution with Progress

```bash
cinder execute "创建一个Python计算器程序"
```

You'll see enhanced progress display:

```
⠼ GENERATION Phase
████████████░░░░░░░░ 60% | ⏱ 2:34 / 4:10 | 🚀 0.8 tasks/min
  ✓ Task 1: calculator.py (15秒)
  ⏳ Task 2: utils.py... (已用时 23秒)
  ⏸ Task 3: main.py
```

### Progress Information Explained

- **Progress Bar**: Visual representation of completion percentage
- **⏱ Time**: Elapsed time / Estimated remaining time
- **🚀 Speed**: Current execution speed in tasks per minute
- **📊 Tokens**: Input and output token usage
  - **in:X**: Input tokens (prompt tokens consumed)
  - **out:Y**: Output tokens (completion tokens generated)
  - **Z.Z tok/s**: Token generation speed (tokens per second)
- **Phase Indicators**: 
  - ✓ Completed phases
  - ⏳ Active phase
  - ⏸ Pending phases

### Disable Progress Tracking

If you prefer minimal output:

```bash
cinder config set progress_tracking false
```

## Web Dashboard Usage

### Real-time Monitoring

1. Start the web server:
   ```bash
   cinder server --open
   ```

2. Navigate to an execution detail page
3. Watch real-time progress updates automatically

### Progress Components

#### Real-time Progress Bar
- Animated progress bar
- Current phase indicator
- Speed metrics
- Estimated remaining time

#### Phase Timeline
- Visual timeline of all phases
- Duration for each phase
- Status indicators (completed, active, pending)

#### Speed Trend Chart
- Historical speed visualization
- Performance trends over time

### Monitoring Multiple Executions

The dashboard supports monitoring multiple concurrent executions:

1. Each execution has its own progress stream
2. Automatic reconnection on network issues
3. Offline status indicators

## Understanding Time Estimates

### Initial Estimates

When execution starts, the system provides an initial estimate based on:

- **Task count**: Number of tasks to execute
- **Historical data**: Average time for similar tasks
- **Confidence level**: Accuracy indicator (shown as ±range)

### Dynamic Adjustments

As execution progresses, estimates are refined:

- **Real-time speed**: Based on actual performance
- **Progress percentage**: More accurate as completion nears
- **Confidence increase**: Narrower range as more data available

### Confidence Indicators

- **20-30%**: Initial estimate, limited data
- **50-70%**: Moderate confidence, execution in progress
- **80-95%**: High confidence, near completion

## Historical Data Analysis

### Execution Statistics

View your execution statistics:

```bash
cinder execution stats
```

Output includes:
- Total executions
- Success rate
- Average execution time
- Average tasks per execution
- Phase duration statistics

### Pattern Analysis

Analyze your execution patterns:

```bash
cinder execution analyze
```

Provides insights on:
- Most common goal keywords
- Frequently created file types
- Hourly execution distribution
- Performance trends

## Configuration Options

### Progress Tracking Settings

```bash
# Enable/disable progress tracking
cinder config set progress_tracking true

# Set progress update frequency (seconds)
cinder config set progress_update_interval 1

# Enable/disable time estimation
cinder config set time_estimation true

# Set historical data retention (days)
cinder config set data_retention_days 30

# Enable/disable Ollama debug output (shows token details)
cinder config set ollama_debug true
```

### Token Tracking

Token tracking provides insights into LLM resource usage:

```bash
# View token statistics in execution summary
cinder execution stats

# Token metrics include:
# - Total input tokens (prompt tokens)
# - Total output tokens (completion tokens)
# - Token generation speed (tok/s)
# - Average tokens per call
```

**Token Display Format**:
- **Progress bar**: `in:800 out:450 83.3 tok/s`
  - Blue `in:X`: Input/prompt tokens
  - Green `out:Y`: Output/completion tokens
  - Magenta speed: Tokens per second

**Benefits**:
- Monitor LLM resource consumption
- Optimize prompt length (reduce input tokens)
- Track generation efficiency (output tokens per second)
- Cost estimation for API-based LLMs

### Performance Tuning

For optimal performance:

```bash
# Reduce database writes (batch updates)
cinder config set progress_batch_updates true

# Limit SSE connections
cinder config set max_sse_connections 10

# Set connection timeout (minutes)
cinder config set sse_timeout 30
```

## Troubleshooting

### Progress Not Updating

**Symptom**: Progress bar stuck or not showing updates

**Solutions**:
1. Check if progress tracking is enabled:
   ```bash
   cinder config get progress_tracking
   ```
2. Verify database is accessible:
   ```bash
   cinder execution list
   ```
3. Check terminal supports Rich output:
   ```bash
   cinder config set force_color true
   ```

### Web Dashboard Not Streaming

**Symptom**: Web dashboard shows static data, no real-time updates

**Solutions**:
1. Check browser console for SSE errors
2. Verify server is running:
   ```bash
   curl http://localhost:8000/api/health
   ```
3. Check firewall settings for SSE connections

### Inaccurate Time Estimates

**Symptom**: Time estimates are far from actual execution time

**Solutions**:
1. Build historical data: Run several executions first
2. Check historical statistics:
   ```bash
   cinder execution stats
   ```
3. Reset estimation model:
   ```bash
   cinder config set estimation_model_reset true
   ```

## Advanced Features

### Custom Progress Listeners

For programmatic access to progress updates:

```python
from cinder_cli.executor import AutonomousExecutor, ProgressBroadcaster

def my_progress_callback(progress_data):
    print(f"Progress: {progress_data['overall_progress']:.1f}%")

executor = AutonomousExecutor(config)
executor.progress_broadcaster.add_listener(my_progress_callback)

executor.execute("Your goal here")
```

### Export Progress Data

Export execution data for analysis:

```bash
# Export as JSON
cinder execution export --format json --output executions.json

# Export as CSV
cinder execution export --format csv --output executions.csv
```

### API Access

Access progress data via REST API:

```bash
# Get execution progress
curl http://localhost:8000/api/executions/123

# Stream real-time progress
curl -N http://localhost:8000/api/executions/123/progress

# Get estimation statistics
curl http://localhost:8000/api/executions/stats/estimation
```

## Best Practices

### For Better Estimates

1. **Run similar tasks**: Historical data improves accuracy
2. **Consistent environment**: Same machine, similar conditions
3. **Monitor trends**: Check statistics regularly

### For Optimal Performance

1. **Batch updates**: Enable batch database writes
2. **Limit connections**: Don't open too many SSE streams
3. **Clean old data**: Regularly archive old executions

### For Better User Experience

1. **Use web dashboard**: Real-time monitoring is easier
2. **Check estimates**: Plan time based on confidence levels
3. **Review statistics**: Understand your execution patterns

## FAQ

**Q: How accurate are time estimates?**
A: Accuracy improves with historical data. Initial estimates have 20-30% confidence, reaching 80-95% near completion.

**Q: Can I disable progress tracking?**
A: Yes, use `cinder config set progress_tracking false` for minimal output.

**Q: How much overhead does progress tracking add?**
A: Less than 5% execution time overhead. Database writes are batched for efficiency.

**Q: Can I access progress data programmatically?**
A: Yes, use the REST API or add custom progress listeners in Python.

**Q: How long is historical data retained?**
A: By default, 30 days. Configure with `data_retention_days` setting.

**Q: Does progress tracking work with all backends?**
A: Yes, it's backend-agnostic. Works with Ollama, Claude, or any other backend.
