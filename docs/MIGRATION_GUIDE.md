"""
Migration guide for progress tracking enhancement.
"""

# Progress Tracking Enhancement - Migration Guide

## Overview

This guide helps you migrate from the basic execution system to the enhanced progress tracking system.

## Breaking Changes

### Database Schema Changes

The `executions` table has been extended with new fields:

**Old Schema**:
```sql
CREATE TABLE executions (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    goal TEXT,
    task_tree TEXT,
    results TEXT,
    status TEXT,
    created_files TEXT,
    execution_time REAL
);
```

**New Schema**:
```sql
CREATE TABLE executions (
    -- ... existing fields ...
    phase_timestamps TEXT,    -- NEW
    progress_data TEXT,       -- NEW
    speed_metrics TEXT,       -- NEW
    estimation_data TEXT      -- NEW
);
```

### API Changes

#### New Endpoints

1. **SSE Progress Streaming**
   ```
   GET /api/executions/current/progress
   GET /api/executions/{id}/progress
   ```

2. **Statistics API**
   ```
   GET /api/executions/stats/estimation
   ```

#### Enhanced Endpoints

The `/api/executions/{id}` endpoint now returns additional fields:
```json
{
  "id": 123,
  "goal": "...",
  "status": "success",
  "phase_timestamps": {...},    // NEW
  "progress_data": {...},       // NEW
  "speed_metrics": {...}        // NEW
}
```

## Migration Steps

### Step 1: Backup Data (Optional)

If you want to preserve existing data:

```bash
# Backup database
cp ~/.cinder/executions.db ~/.cinder/executions.db.backup

# Export to JSON
cinder execution export --format json --output backup.json
```

### Step 2: Run Database Migration

```bash
# Apply migration (adds new fields)
python -m cinder_cli.executor.migrations.001_add_progress_tracking_fields

# Create statistics table
python -m cinder_cli.executor.migrations.002_create_execution_statistics_table
```

**Note**: Since we're not preserving old data, you can also delete the old database:
```bash
rm ~/.cinder/executions.db
```

The system will create a new database with the correct schema automatically.

### Step 3: Update Configuration

Add progress tracking configuration to your config file:

```yaml
# ~/.cinder/config.yaml
progress_tracking:
  enabled: true
  update_interval: 1
  batch_updates: true
  batch_interval: 5

estimation:
  enabled: true
  min_confidence: 0.2
  max_confidence: 0.95
  historical_weight: 0.7

database:
  wal_mode: true
  connection_pool: 5
  data_retention_days: 30

web:
  max_sse_connections: 10
  sse_timeout: 30
  heartbeat_interval: 15
```

### Step 4: Verify Migration

Test the migration:

```bash
# Check database schema
sqlite3 ~/.cinder/executions.db ".schema executions"

# Test execution
cinder execute "创建一个简单的Python程序"

# Check web dashboard
cinder server --open
```

## Configuration Changes

### New Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `progress_tracking.enabled` | bool | true | Enable/disable progress tracking |
| `progress_tracking.update_interval` | int | 1 | Progress update frequency (seconds) |
| `progress_tracking.batch_updates` | bool | true | Batch database writes |
| `estimation.enabled` | bool | true | Enable time estimation |
| `database.data_retention_days` | int | 30 | Days to keep execution data |
| `web.max_sse_connections` | int | 10 | Maximum concurrent SSE connections |

### Deprecated Options

None. All existing configuration options remain compatible.

## Code Changes

### For CLI Users

**No changes required**. The enhanced progress tracking is backward compatible.

Optional: Disable progress tracking if needed:
```bash
cinder config set progress_tracking.enabled false
```

### For API Users

**SSE Streaming** (New):
```python
import requests

# Stream progress updates
response = requests.get(
    'http://localhost:8000/api/executions/123/progress',
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        print(f"Progress: {data['progress_data']['overall_progress']}")
```

**Enhanced Execution Data**:
```python
import requests

response = requests.get('http://localhost:8000/api/executions/123')
execution = response.json()

# Access new fields
phase_timestamps = execution['phase_timestamps']
speed_metrics = execution['speed_metrics']
progress_data = execution['progress_data']
```

### For Python Developers

**Using Progress Tracker**:
```python
from cinder_cli.executor import AutonomousExecutor
from cinder_cli.config import Config

config = Config()
executor = AutonomousExecutor(config)

# Progress tracking is automatic
result = executor.execute("Your goal here")

# Access progress data
progress = executor.progress_tracker.get_progress()
print(f"Overall progress: {progress['overall_progress']}%")
```

**Custom Progress Listeners**:
```python
def my_progress_callback(progress_data):
    # Custom handling
    send_notification(progress_data)

executor.progress_broadcaster.add_listener(my_progress_callback)
```

## Troubleshooting

### Issue: Database Migration Fails

**Symptom**: Migration script throws error

**Solution**:
```bash
# Delete old database and start fresh
rm ~/.cinder/executions.db

# Run migration again
python -m cinder_cli.executor.migrations.001_add_progress_tracking_fields
```

### Issue: Progress Not Showing

**Symptom**: No progress updates visible

**Solution**:
```bash
# Check if progress tracking is enabled
cinder config get progress_tracking.enabled

# Enable if needed
cinder config set progress_tracking.enabled true
```

### Issue: SSE Connection Fails

**Symptom**: Web dashboard not receiving updates

**Solution**:
```bash
# Check server is running
curl http://localhost:8000/api/health

# Check SSE endpoint
curl -N http://localhost:8000/api/executions/current/progress
```

### Issue: Old Data Not Compatible

**Symptom**: Errors when accessing old executions

**Solution**:
```bash
# Old data is not compatible with new schema
# Either:
# 1. Delete old database
rm ~/.cinder/executions.db

# 2. Or export and reimport
cinder execution export --format json --output old_data.json
# Manually convert data format
# Import converted data
```

## Rollback

If you need to rollback to the previous version:

```bash
# Restore backup
cp ~/.cinder/executions.db.backup ~/.cinder/executions.db

# Or run rollback migration
python -m cinder_cli.executor.migrations.001_add_progress_tracking_fields down
python -m cinder_cli.executor.migrations.002_create_execution_statistics_table down
```

## Performance Considerations

### Database Size

The new fields add approximately 1-2KB per execution. For 1000 executions:
- Old size: ~500KB
- New size: ~2.5MB

### Memory Usage

Progress tracking adds minimal memory overhead:
- ProgressTracker: ~1KB
- TimeRecorder: ~2KB
- SpeedCalculator: ~1KB
- Total: ~4KB per execution

### Performance Impact

Progress tracking overhead is less than 5% of execution time:
- Without tracking: 100% execution time
- With tracking: ~105% execution time

## Getting Help

If you encounter issues during migration:

1. Check the troubleshooting section above
2. Review the logs: `~/.cinder/logs/`
3. Consult the documentation: `docs/PROGRESS_TRACKING_GUIDE.md`
4. Open an issue on GitHub with migration details

## Next Steps

After successful migration:

1. **Test the system**: Run a few test executions
2. **Configure settings**: Adjust configuration to your needs
3. **Monitor performance**: Check system metrics
4. **Explore features**: Try the web dashboard and API
5. **Provide feedback**: Report any issues or suggestions
