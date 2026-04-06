# Development Guide

## Quick Start

### Using Makefile (Recommended)

```bash
# View all commands
make help

# Setup development environment
make install
make dev

# Check service status
make status

# Run tests
make test

# Clean up
make clean
```

### Using Invoke (Python-native)

```bash
# Install invoke
pip install invoke

# View all tasks
inv --list

# Setup development environment
inv install
inv dev

# Check service status
inv status

# Run tests
inv test

# Clean up
inv clean
```

## Development Setup

### Prerequisites

1. **Python 3.9+**
   ```bash
   python --version
   ```

2. **Docker**
   ```bash
   docker --version
   docker info
   ```

3. **Ollama**
   ```bash
   # Install: https://ollama.ai/
   ollama serve
   ```

### Installation

```bash
# Clone repository
git clone <repository-url>
cd cinder

# Install dependencies
make install
# or
pip install -e ".[dev]"

# Setup development environment
make dev
# or
inv dev
```

## Service Management

### External Services

Cinder uses two external services:

1. **Ollama** - LLM inference engine
   - URL: http://localhost:11434
   - Start: `ollama serve`

2. **Phoenix** - Trace visualization
   - URL: http://localhost:6006
   - Start: `make start` or `inv start`

### Service Commands

```bash
# Check all services
make status

# Start Phoenix
make start

# Stop Phoenix
make stop

# View Phoenix logs
make logs

# Clean environment
make clean
```

## Development Workflow

### 1. Start Development

```bash
# Setup environment
make dev

# Check services are running
make status
```

### 2. Run Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_tracing.py -v

# Run with coverage
pytest tests/ --cov=cinder_cli --cov-report=html
```

### 3. Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
mypy cinder_cli/
```

### 4. Clean Up

```bash
# Clean environment
make clean
```

## Project Structure

```
cinder/
├── Makefile              # Task runner (primary)
├── tasks.py              # Invoke tasks (Python-native)
├── pyproject.toml        # Project configuration
├── scripts/
│   └── services.sh       # Service management script
├── cinder_cli/
│   ├── cli.py           # CLI entry point
│   ├── tracing/         # Tracing module
│   └── ...
├── tests/
│   └── ...
└── docs/
    ├── DEVELOPMENT.md   # This file
    ├── OBSERVABILITY.md # Tracing guide
    └── ...
```

## Available Commands

### Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all commands |
| `make install` | Install dependencies |
| `make dev` | Setup development environment |
| `make test` | Run tests |
| `make status` | Check service status |
| `make start` | Start Phoenix |
| `make stop` | Stop Phoenix |
| `make logs` | View Phoenix logs |
| `make clean` | Clean environment |
| `make format` | Format code |
| `make lint` | Lint code |

### Invoke Tasks

| Task | Description |
|------|-------------|
| `inv --list` | List all tasks |
| `inv install` | Install dependencies |
| `inv dev` | Setup development environment |
| `inv test` | Run tests |
| `inv status` | Check service status |
| `inv start` | Start Phoenix |
| `inv stop` | Stop Phoenix |
| `inv logs` | View Phoenix logs |
| `inv clean` | Clean environment |
| `inv format` | Format code |
| `inv lint` | Lint code |

## Troubleshooting

### Services Not Running

```bash
# Check service status
make status

# Start Ollama
ollama serve

# Start Phoenix
make start
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i :6006
lsof -i :11434

# Kill the process
kill -9 <PID>
```

### Docker Issues

```bash
# Check Docker status
docker info

# View Phoenix logs
make logs

# Restart Phoenix
make stop
make start
```

### Clean Installation

```bash
# Remove all data
make clean

# Reinstall
make install
make dev
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: make install
      
      - name: Start services
        run: make start
      
      - name: Run tests
        run: make test
      
      - name: Stop services
        run: make stop
```

## Additional Resources

- [Observability Guide](./OBSERVABILITY.md) - Tracing and monitoring
- [Service Management](./SERVICE_MANAGEMENT.md) - Detailed service management
- [Verification Guide](./VERIFICATION.md) - Verification procedures
