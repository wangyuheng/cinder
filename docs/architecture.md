# Agent Architecture Design

## Overview

Cinder now uses a **dual-agent architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Dual-Agent Architecture                   │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │      User (Human)     │
                    └──────────┬───────────┘
                               │
                               │ Goals & Feedback
                               ▼
        ┌──────────────────────────────────────────┐
        │                                          │
        │    ┌────────────────────────────┐       │
        │    │   DECISION AGENT (Brain)    │       │
        │    │                            │       │
        │    │  • Understand user intent   │       │
        │    │  • Make decisions           │       │
        │    │  • Delegate to Worker       │       │
        │    │  • Evaluate results         │       │
        │    │  • Interact with user       │       │
        │    │                            │       │
        │    └──────────┬─────────────────┘       │
        │               │                          │
        │               │ Tasks & Commands         │
        │               ▼                          │
        │    ┌────────────────────────────┐       │
        │    │   WORKER AGENT (Executor)   │       │
        │    │                            │       │
        │    │  Plan → Generate → Eval    │       │
        │    │                            │       │
        │    │  • Decompose tasks         │       │
        │    │  • Generate code           │       │
        │    │  • Evaluate quality        │       │
        │    │                            │       │
        │    └──────────┬─────────────────┘       │
        │               │                          │
        │               │ Results & Reports        │
        │               ▼                          │
        │    ┌────────────────────────────┐       │
        │    │   DECISION AGENT (Brain)    │       │
        │    │                            │       │
        │    │  • Analyze results         │       │
        │    │  • Decide next action      │       │
        │    │  • Provide feedback        │       │
        │    │                            │       │
        │    └────────────────────────────┘       │
        │                                          │
        └──────────────────────────────────────────┘
```

## Core Components

### 1. Decision Agent (The Brain)

**Role**: Manager, Decision Maker, User Proxy

**Responsibilities**:
- Understand user intent and context
- Make decisions based on Soul profile
- Delegate tasks to Worker Agent
- Evaluate execution results
- Interact with user for clarifications
- Maintain global context

**State Machine**:
```
UNDERSTAND → ANALYZE → DECIDE → DELEGATE → EVALUATE → COMPLETE
                ↑                        ↓
                └────────────────────────┘
```

**Key Features**:
- **Intent Understanding**: Analyzes user goals and extracts requirements
- **Decision Making**: Uses Soul profile to make choices
- **Worker Orchestration**: Delegates tasks and manages execution
- **Result Evaluation**: Assesses quality and decides next actions
- **User Interaction**: Asks questions and provides explanations

### 2. Worker Agent (The Executor)

**Role**: Task Executor, Code Generator, Quality Reporter

**Responsibilities**:
- Execute Plan → Generate → Evaluation flow
- Return objective data (no decisions)
- Support outputting options for decision-making
- Report execution status and progress

**Execution Flow**:
```
Plan → Generate → Evaluate → (Iterate if needed)
```

**Key Features**:
- **Task Decomposition**: Breaks down goals into subtasks
- **Code Generation**: Creates code using LLM
- **Quality Evaluation**: Assesses generated code
- **Iteration Support**: Improves code based on feedback
- **Option Generation**: Can output choices for Decision Agent

### 3. Agent Orchestrator

**Role**: Communication Hub, Lifecycle Manager

**Responsibilities**:
- Manage agent communication
- Handle message passing
- Control agent lifecycle
- Support concurrent execution

**Key Features**:
- **Message Routing**: Routes messages between agents
- **Task Delegation**: Manages asynchronous task execution
- **Concurrency Control**: Limits concurrent workers
- **Logging & Tracking**: Records all communications

### 4. Context Manager

**Role**: State Management, Data Persistence

**Responsibilities**:
- Manage short-term context (memory)
- Manage long-term context (SQLite)
- Synchronize between storage layers
- Enforce size limits and cleanup

**Key Features**:
- **Dual Storage**: Memory for speed, SQLite for persistence
- **Context Isolation**: Separates user/session/project contexts
- **Auto-Sync**: Periodically syncs to persistent storage
- **Size Management**: Enforces limits and cleans old data

## Decision Types

The system supports multiple decision types:

### 1. Code Acceptance
- **When**: Worker completes code generation
- **Decision**: Accept, Improve, or Regenerate
- **Soul Rules**: Risk tolerance

### 2. Technology Choice
- **When**: Multiple tech options available
- **Decision**: Select best option
- **Soul Rules**: Risk tolerance, preferences

### 3. Architecture Decision
- **When**: Architecture choices needed
- **Decision**: Select architecture pattern
- **Soul Rules**: Structure preference

### 4. Implementation Decision
- **When**: Implementation approaches differ
- **Decision**: Choose implementation style
- **Soul Rules**: Detail orientation

## Message Flow

```
User Goal
    │
    ▼
Decision Agent (UNDERSTAND)
    │
    ▼
Decision Agent (ANALYZE)
    │
    ▼
Decision Agent (DECIDE)
    │
    ├─► Delegate Task
    │       │
    │       ▼
    │   Worker Agent (Plan)
    │       │
    │       ▼
    │   Worker Agent (Generate)
    │       │
    │       ▼
    │   Worker Agent (Evaluate)
    │       │
    │       ▼
    │   Result
    │       │
    └───────┘
    │
    ▼
Decision Agent (EVALUATE)
    │
    ├─► Quality OK? ──► COMPLETE
    │
    └─► Quality Low? ──► Loop back to ANALYZE
```

## Soul Profile Integration

Decision Agent uses Soul profile to make personalized decisions:

```python
soul_meta = {
    "traits": {
        "risk_tolerance": 50,      # 0-100: Conservative to Aggressive
        "structure": 50,            # 0-100: Flexible to Structured
        "detail_orientation": 50,   # 0-100: Simple to Detailed
    }
}
```

**Decision Rules**:
- **Risk Tolerance ≤ 38**: Conservative choices (low risk)
- **Risk Tolerance ≥ 66**: Aggressive choices (high risk)
- **Structure ≥ 65**: Prefer complex, structured solutions
- **Detail Orientation ≥ 65**: Prefer detailed implementations

## Benefits

### 1. Clear Separation of Concerns
- Decision Agent: Thinking and decision-making
- Worker Agent: Execution and reporting

### 2. Better Decision Quality
- Centralized decision logic
- Soul profile integration
- Context-aware choices

### 3. Improved Extensibility
- Easy to add new decision types
- Easy to add new execution capabilities
- Modular architecture

### 4. Enhanced User Experience
- Proactive user interaction
- Decision explanations
- Contextual awareness

## Migration from Legacy

See [Migration Guide](./ARCHITECTURE_MIGRATION_GUIDE.md) for details on migrating from the old architecture.
