# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-01-XX

### Added

#### Dual-Agent Architecture
- **Decision Agent**: Intelligent decision-making agent that acts as the brain of the system
  - Understands user intent and context
  - Makes decisions based on Soul profile
  - Delegates tasks to Worker Agent
  - Evaluates execution results
  - Interacts with user for clarifications
  - State machine for decision flow (UNDERSTAND → ANALYZE → DECIDE → DELEGATE → EVALUATE → COMPLETE)

- **Worker Agent**: Task execution agent that focuses on execution
  - Executes Plan → Generate → Evaluation flow
  - Returns objective data without making decisions
  - Supports outputting options for decision-making
  - Reports execution status and progress

- **Agent Orchestrator**: Communication hub between agents
  - Manages agent communication and message passing
  - Controls agent lifecycle
  - Supports concurrent execution
  - Logs and tracks all messages

- **Context Manager**: State management system
  - Short-term context (in-memory) for fast access
  - Long-term context (SQLite) for persistence
  - Auto-sync between storage layers
  - Context isolation (user/session/project)
  - Size management and cleanup

#### Extended Decision Types
- **Code Acceptance**: Accept, improve, or regenerate code based on quality
- **Technology Choice**: Select technologies based on risk tolerance
- **Architecture Decision**: Choose architecture patterns based on structure preference
- **Implementation Decision**: Select implementation approaches based on detail orientation

#### Enhanced Soul Profile Integration
- Extended SoulRuleEngine with structure preference rules
- Extended SoulRuleEngine with detail orientation rules
- Decision context passing mechanism
- Decision explanation and reasoning

### Changed

#### BREAKING: API Changes
- `AutonomousExecutor.execute()` return structure changed
  - Old: `{"status": "success", "results": [...]}`
  - New: `{"status": "success", "decision": {...}, "worker_result": {...}}`
- Decision phase output format extended to support multiple types
- Worker phase output format standardized (removed decision fields)

#### Refactored Components
- `AutonomousExecutor` simplified to agent orchestrator
- Backward compatibility layer with `legacy_mode` parameter
- New/old API format conversion utilities

### Improved

#### Decision Quality
- Centralized decision logic in Decision Agent
- Soul profile integration for personalized decisions
- Context-aware decision making
- Decision explanations with reasoning chain

#### User Experience
- Proactive user interaction
- Decision explanations
- Contextual awareness across sessions
- Better error handling and recovery

#### Architecture
- Clear separation of concerns (Decision vs Execution)
- Better extensibility for new decision types
- Modular architecture for easy maintenance
- Improved testability

### Performance

#### Monitoring
- LLM call tracking and metrics
- Decision loop counting
- Context size monitoring
- Execution time tracking

#### Optimization
- Context caching to reduce LLM calls
- Decision caching for repeated scenarios
- Optimized prompt engineering

### Documentation

#### New Documentation
- Architecture design document
- Migration guide from legacy to new architecture
- Usage examples for different scenarios
- API documentation updates

#### Examples
- Simple task execution example
- Technology choice decision example
- Architecture decision example
- Integration examples

### Testing

#### New Tests
- Unit tests for Decision Agent
- Unit tests for Worker Agent
- Unit tests for Agent Orchestrator
- Unit tests for Context Manager
- Integration tests for agent collaboration
- Scenario tests for different decision types

### Migration

#### Compatibility Layer
- `legacy_mode` parameter for backward compatibility
- Result format conversion utilities
- Gradual migration path

#### Migration Guide
- Step-by-step migration instructions
- Breaking changes documentation
- Common issues and solutions
- Rollback plan

## [2.0.0] - 2024-XX-XX

### Added
- Initial autonomous executor implementation
- Plan → Generate → Evaluation → Decision flow
- Soul profile integration
- Proxy decision making
- Decision logging

## [1.0.0] - 2024-XX-XX

### Added
- Initial CLI implementation
- Soul profile generation
- Basic task execution
- Configuration management
