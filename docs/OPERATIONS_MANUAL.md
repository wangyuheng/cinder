# Operations Manual - Progress Tracking System

## Overview

This manual provides operational guidance for the progress tracking system in Cinder CLI.

## System Components

### Core Services

1. **Progress Tracker Service**
   - Location: `cinder_cli/executor/progress_tracker.py`
   - Purpose: Tracks execution progress in real-time
   - Dependencies: None

2. **SSE Streaming Service**
   - Location: `cinder_cli/web/api/progress.py`
   - Purpose: Provides real-time progress updates via SSE
   - Dependencies: FastAPI, Progress Tracker

3. **Database Service**
   - Location: `cinder_cli/executor/execution_logger.py`
   - Purpose: Persists execution and progress data
   - Dependencies: SQLite

## Monitoring

### Health Checks

**Endpoint**: `GET /api/health`

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-04T12:00:00",
  "components": {
    "database": {"status": "healthy"},
    "progress_tracker": {"status": "healthy"}
  }
}
```

**Check Frequency**: Every 30 seconds

**Alert Conditions**:
- Status: "unhealthy"
- Response time > 5 seconds
- Any component status: "unhealthy"

### Performance Metrics

**Endpoint**: `GET /api/metrics`

**Key Metrics**:
- `total_executions`: Total number of executions
- `avg_execution_time`: Average execution duration
- `avg_tasks_count`: Average tasks per execution
- `phase_statistics`: Phase-level performance data

**Monitoring Dashboard**: Grafana or similar

**Alert Thresholds**:
- Avg execution time > 10 minutes
- Success rate < 90%
- SSE connection count > 8 (80% of max)

### Database Monitoring

**Database File**: `~/.cinder/executions.db`

**Key Metrics**:
- Database size
- Query performance
- Connection count

**Maintenance Tasks**:
```bash
# Check database size
ls -lh ~/.cinder/executions.db

# Check database integrity
sqlite3 ~/.cinder/executions.db "PRAGMA integrity_check;"

# Analyze query performance
sqlite3 ~/.cinder/executions.db "EXPLAIN QUERY PLAN SELECT * FROM executions WHERE status='success';"
```

## Maintenance

### Routine Maintenance

**Daily Tasks**:
- Monitor health check endpoints
- Review error logs
- Check connection counts

**Weekly Tasks**:
- Review performance metrics
- Analyze execution statistics
- Check database size

**Monthly Tasks**:
- Run data cleanup
- Archive old statistics
- Review retention settings

### Data Cleanup

**Automated Cleanup**:
```bash
# Run cleanup script
python -c "from cinder_cli.executor.data_cleanup import DataCleanup; from cinder_cli.config import Config; DataCleanup(Config()).run_maintenance()"
```

**Manual Cleanup**:
```bash
# Delete old executions (older than 30 days)
sqlite3 ~/.cinder/executions.db "DELETE FROM executions WHERE timestamp < datetime('now', '-30 days');"

# Vacuum database to reclaim space
sqlite3 ~/.cinder/executions.db "VACUUM;"
```

### Database Backup

**Backup Script**:
```bash
#!/bin/bash
# backup_cinder.sh

BACKUP_DIR="/backups/cinder"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_PATH="$HOME/.cinder/executions.db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp $DB_PATH $BACKUP_DIR/executions_$TIMESTAMP.db

# Compress backup
gzip $BACKUP_DIR/executions_$TIMESTAMP.db

# Keep only last 7 days of backups
find $BACKUP_DIR -name "executions_*.db.gz" -mtime +7 -delete

echo "Backup completed: executions_$TIMESTAMP.db.gz"
```

**Schedule**: Daily at 2 AM via cron

## Troubleshooting

### Common Issues

#### Issue: SSE Connections Not Working

**Symptoms**:
- Web dashboard not receiving updates
- Connection timeout errors

**Diagnosis**:
```bash
# Check if server is running
curl http://localhost:8000/api/health

# Test SSE endpoint
curl -N http://localhost:8000/api/executions/current/progress

# Check connection count
curl http://localhost:8000/api/metrics
```

**Resolution**:
1. Restart server: `cinder server --restart`
2. Check max connections setting
3. Clear stale connections

#### Issue: Database Performance Degradation

**Symptoms**:
- Slow query responses
- High disk I/O

**Diagnosis**:
```bash
# Check database size
ls -lh ~/.cinder/executions.db

# Check query performance
sqlite3 ~/.cinder/executions.db "EXPLAIN QUERY PLAN SELECT * FROM executions ORDER BY timestamp DESC LIMIT 100;"

# Check index usage
sqlite3 ~/.cinder/executions.db "PRAGMA index_list(executions);"
```

**Resolution**:
1. Run VACUUM: `sqlite3 ~/.cinder/executions.db "VACUUM;"`
2. Rebuild indexes: `sqlite3 ~/.cinder/executions.db "REINDEX;"`
3. Archive old data
4. Enable WAL mode

#### Issue: Progress Tracking Overhead

**Symptoms**:
- Slow execution times
- High CPU usage

**Diagnosis**:
```bash
# Check progress tracking status
cinder config get progress_tracking.enabled

# Monitor CPU usage
top -p $(pgrep -f cinder)

# Check update frequency
cinder config get progress_tracking.update_interval
```

**Resolution**:
1. Increase update interval: `cinder config set progress_tracking.update_interval 5`
2. Disable batch updates: `cinder config set progress_tracking.batch_updates false`
3. Disable progress tracking temporarily

### Performance Tuning

#### Database Optimization

**Enable WAL Mode**:
```bash
sqlite3 ~/.cinder/executions.db "PRAGMA journal_mode=WAL;"
```

**Optimize Settings**:
```bash
# Increase cache size
sqlite3 ~/.cinder/executions.db "PRAGMA cache_size=10000;"

# Enable synchronous mode
sqlite3 ~/.cinder/executions.db "PRAGMA synchronous=NORMAL;"
```

#### SSE Connection Optimization

**Configuration**:
```yaml
web:
  max_sse_connections: 10
  sse_timeout: 30
  heartbeat_interval: 15
```

**Monitoring**:
- Track connection count
- Monitor connection duration
- Check for connection leaks

## Security

### Access Control

**API Security**:
- Rate limiting enabled
- Connection limits enforced
- Input validation active

**Database Security**:
- File permissions: 600
- Location: `~/.cinder/` (user-only access)

### Data Privacy

**Retention Policy**:
- Default: 30 days
- Configurable per deployment

**Data Cleanup**:
- Automatic cleanup enabled
- Manual cleanup available

## Scaling

### Horizontal Scaling

**Load Balancer Setup**:
- Use Nginx or HAProxy
- Configure sticky sessions for SSE
- Health check endpoints

**Multiple Instances**:
- Share database via NFS
- Use connection pooling
- Monitor connection counts

### Vertical Scaling

**Resource Requirements**:
- CPU: 2 cores minimum
- Memory: 4GB minimum
- Disk: 10GB minimum

**Performance Tuning**:
- Increase max connections
- Optimize database settings
- Enable caching

## Disaster Recovery

### Backup Strategy

**Daily Backups**:
- Full database backup
- Compressed storage
- Off-site replication

**Recovery Procedure**:
```bash
# Stop services
cinder server --stop

# Restore database
gunzip -c /backups/cinder/executions_TIMESTAMP.db.gz > ~/.cinder/executions.db

# Verify integrity
sqlite3 ~/.cinder/executions.db "PRAGMA integrity_check;"

# Restart services
cinder server --start
```

### Failover Procedure

1. Monitor health checks
2. Detect failure
3. Switch to backup instance
4. Restore from backup if needed
5. Verify functionality

## Logging

### Log Locations

**Application Logs**: `~/.cinder/logs/`

**Log Files**:
- `cinder.log`: General application logs
- `progress.log`: Progress tracking logs
- `error.log`: Error logs

### Log Rotation

**Configuration**:
```bash
# /etc/logrotate.d/cinder
~/.cinder/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Log Analysis

**Error Analysis**:
```bash
# Count errors by type
grep "ERROR" ~/.cinder/logs/cinder.log | awk '{print $5}' | sort | uniq -c

# Find recent errors
tail -100 ~/.cinder/logs/error.log

# Search for specific error
grep "SSE connection failed" ~/.cinder/logs/*.log
```

## Support

### Diagnostic Information

**Collect Diagnostics**:
```bash
# System info
uname -a
python --version

# Cinder version
cinder --version

# Configuration
cinder config list

# Database stats
sqlite3 ~/.cinder/executions.db "SELECT COUNT(*) FROM executions;"

# Recent logs
tail -50 ~/.cinder/logs/cinder.log
```

### Contact Support

**Information Needed**:
- Error messages
- Log excerpts
- Configuration
- Steps to reproduce

**Support Channels**:
- GitHub Issues
- Documentation
- Community Forum
