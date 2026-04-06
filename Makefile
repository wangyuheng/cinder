.PHONY: help install dev test clean status start stop logs

# Python interpreter
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

help:
	@echo "Cinder Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Setup development environment"
	@echo "  make test       - Run tests"
	@echo ""
	@echo "Services:"
	@echo "  make status     - Check service status"
	@echo "  make start      - Start Phoenix"
	@echo "  make stop       - Stop Phoenix"
	@echo "  make logs       - View logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Clean environment"
	@echo ""
	@echo "Alternative: Use 'inv --list' for Python-based tasks"

install:
	@echo "📦 Installing dependencies..."
	$(PIP) install -e ".[dev]"
	@echo "✅ Installation complete!"

dev:
	@echo "🚀 Setting up development environment..."
	@bash ./scripts/services.sh start-phoenix
	@echo ""
	@echo "✅ Development environment ready!"
	@echo "📊 Phoenix UI: http://localhost:6006"
	@echo "💡 Run 'make logs' to view Phoenix logs"

status:
	@bash ./scripts/services.sh status

start:
	@bash ./scripts/services.sh start-phoenix

stop:
	@bash ./scripts/services.sh stop-phoenix

logs:
	@docker logs -f cinder-phoenix

test:
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest tests/ -v --cov=cinder_cli

clean:
	@echo "🧹 Cleaning up..."
	@bash ./scripts/services.sh stop-phoenix
	@docker volume rm phoenix-data 2>/dev/null || true
	@echo "✅ Clean complete!"

format:
	@echo "🎨 Formatting code..."
	$(PYTHON) -m black cinder_cli/ tests/
	$(PYTHON) -m isort cinder_cli/ tests/
	@echo "✅ Format complete!"

lint:
	@echo "🔍 Linting code..."
	$(PYTHON) -m flake8 cinder_cli/ tests/
	$(PYTHON) -m mypy cinder_cli/
	@echo "✅ Lint complete!"
