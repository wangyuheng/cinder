# Migration Guide: Legacy to Agent Architecture

## Overview

This guide helps you migrate from the legacy executor to the new dual-agent architecture.

## Key Changes

### 1. Architecture Change

**Legacy**:
```
Plan → Generate → Evaluation → Decision (simple)
```

**New**:
```
Decision Agent (Brain) ↔ Worker Agent (Executor)
```

### 2. API Changes

#### Executor Initialization

**Legacy**:
```python
from cinder_cli.executor.autonomous_executor import AutonomousExecutor

executor = AutonomousExecutor(config)
result = executor.execute(goal, mode, constraints)
```

**New**:
```python
from cinder_cli.executor.refactored_autonomous_executor import AutonomousExecutor

# Option 1: Use new architecture (recommended)
executor = AutonomousExecutor(config, legacy_mode=False)
result = executor.execute(goal, mode, constraints)

# Option 2: Use legacy mode (backward compatible)
executor = AutonomousExecutor(config, legacy_mode=True)
result = executor.execute(goal, mode, constraints)
```

#### Result Structure

**Legacy**:
```python
{
    "status": "success",
    "results": [
        {"subtask_id": "...", "code": "..."}
    ],
    "execution_flow": {
        "phases": [...]
    }
}
```

**New**:
```python
{
    "status": "success",
    "goal": "...",
    "decision": {...},
    "worker_result": {
        "output_type": "code",
        "data": {...},
        "quality_score": 0.85
    },
    "execution_flow": {
        "phases": [...]
    },
    "metadata": {
        "architecture": "dual-agent",
        "decision_loops": 2
    }
}
```

## Migration Steps

### Step 1: Update Imports

```python
# Old
from cinder_cli.executor.autonomous_executor import AutonomousExecutor

# New
from cinder_cli.executor.refactored_autonomous_executor import AutonomousExecutor
```

### Step 2: Test with Legacy Mode

```python
# Enable legacy mode for testing
executor = AutonomousExecutor(config, legacy_mode=True)
result = executor.execute(goal)

# Verify results match expected behavior
```

### Step 3: Switch to New Architecture

```python
# Use new architecture
executor = AutonomousExecutor(config, legacy_mode=False)
result = executor.execute(goal)

# Check new result structure
if result["metadata"]["architecture"] == "dual-agent":
    print("Using new architecture!")
```

### Step 4: Update Result Handling

```python
# Old way
for subtask_result in result["results"]:
    code = subtask_result["code"]
    # process code

# New way
worker_result = result["worker_result"]
if worker_result["output_type"] == "code":
    code = worker_result["data"]["code"]
    quality_score = worker_result["quality_score"]
    # process code with quality info
```

### Step 5: Leverage New Features

```python
# Access decision history
for decision in result["decision_history"]:
    print(f"Decision: {decision['decision_type']}")
    print(f"Confidence: {decision['confidence']}")
    print(f"Reasoning: {decision['reasoning']}")

# Get statistics
stats = executor.get_statistics()
print(f"Decision loops: {stats['decision_agent']['decision_loop_count']}")
```

## Breaking Changes

### 1. Result Structure
- **Old**: `results` array with subtask results
- **New**: `worker_result` object with quality metadata

### 2. Decision Output
- **Old**: Simple accept/reject in Decision phase
- **New**: Rich decision objects with reasoning and confidence

### 3. Context Management
- **Old**: No persistent context
- **New**: Context manager with SQLite persistence

## Compatibility Layer

The refactored executor provides backward compatibility:

```python
class AutonomousExecutor:
    def __init__(self, config: Config, legacy_mode: bool = False):
        if legacy_mode:
            # Use old implementation
            self._init_legacy_components()
        else:
            # Use new agent architecture
            self._init_agent_components()
```

## Feature Comparison

| Feature | Legacy | New Architecture |
|---------|--------|------------------|
| Decision Making | Simple | Soul-based, intelligent |
| Context | None | Persistent, multi-scope |
| User Interaction | Limited | Proactive, contextual |
| Decision Types | Code accept only | Multiple (tech, architecture, etc.) |
| Explanations | None | Full reasoning chain |
| Quality Metrics | Basic | Comprehensive |

## Common Issues

### Issue 1: Missing `results` field

**Problem**: Code expects `result["results"]` array

**Solution**: Use `result["worker_result"]` instead

```python
# Old
code = result["results"][0]["code"]

# New
code = result["worker_result"]["data"]["code"]
```

### Issue 2: Decision phase missing

**Problem**: Code expects `result["execution_flow"]["phases"]` to include Decision phase

**Solution**: Decisions are now in `result["decision_history"]`

```python
# Old
decision_phase = [p for p in result["execution_flow"]["phases"] if p["phase"] == "decision"]

# New
decisions = result["decision_history"]
```

### Issue 3: Context not persisting

**Problem**: Context lost between executions

**Solution**: Context manager now persists automatically

```python
# Context is automatically saved
executor = AutonomousExecutor(config, legacy_mode=False)
result1 = executor.execute("task 1")

# Context persists to next execution
result2 = executor.execute("task 2")  # Has context from task 1
```

## Rollback Plan

If issues arise, you can immediately rollback:

```python
# Switch back to legacy mode
executor = AutonomousExecutor(config, legacy_mode=True)
```

## Timeline

- **Phase 1** (Current): Both architectures available, legacy mode default
- **Phase 2** (Next release): New architecture default, legacy mode optional
- **Phase 3** (Future): Legacy mode deprecated, migration required

## Support

For migration assistance:
1. Check [Architecture Documentation](./architecture.md)
2. Review [Examples](./examples/)
3. Open an issue on GitHub
