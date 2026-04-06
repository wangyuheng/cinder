# OpenSpec Directory

This directory contains OpenSpec-related specifications and change management for the Cinder project.

## Directory Structure

```
openspec/
├── specs/              # Current active specifications
│   ├── agent-orchestration/
│   ├── api-server/
│   ├── context-management/
│   ├── decision-agent/
│   ├── decision-logging/
│   ├── problem-guidance/
│   ├── proxy-decision-making/
│   ├── soul-confirmation/
│   ├── web-dashboard/
│   └── worker-agent/
├── changes/            # Change management
│   ├── archive/        # Archived/completed changes
│   ├── progress-tracking-enhancement/
│   └── strict-pge-executor-flow/
└── config.yaml         # OpenSpec configuration
```

## Purpose

### `/specs` - Active Specifications
Contains the current active specifications for different components of the Cinder system. Each spec defines:
- Component behavior
- API contracts
- Integration points
- Implementation requirements

### `/changes` - Change Management
Manages ongoing and completed changes to the system:

- **Active Changes**: Work-in-progress changes being developed
- **Archive**: Completed changes with full history and documentation

Each change includes:
- `proposal.md` - What and why
- `design.md` - How it will be implemented
- `tasks.md` - Implementation steps
- `specs/` - Detailed specifications

### `/config.yaml` - Configuration
OpenSpec tool configuration for this project.

## Usage

### Creating a New Change
Use the OpenSpec CLI or the `.trae/skills/openspec-propose` skill to create a new change:

```bash
openspec propose <change-name>
```

### Applying a Change
Use the OpenSpec CLI or the `.trae/skills/openspec-apply-change` skill:

```bash
openspec apply <change-name>
```

### Archiving a Completed Change
Use the OpenSpec CLI or the `.trae/skills/openspec-archive-change` skill:

```bash
openspec archive <change-name>
```

## Related Documentation

- [Architecture Documentation](../docs/ARCHITECTURE.md)
- [Development Guide](../docs/DEVELOPMENT.md)
- [Migration Guide](../docs/ARCHITECTURE_MIGRATION_GUIDE.md)

## Tools

This project uses OpenSpec for specification-driven development. The `.trae/skills/` directory contains additional skills for working with OpenSpec:

- `openspec-propose` - Create new change proposals
- `openspec-apply-change` - Implement changes
- `openspec-archive-change` - Archive completed changes
- `openspec-explore` - Explore and investigate problems
