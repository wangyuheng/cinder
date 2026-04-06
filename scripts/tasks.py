"""
Cinder development tasks using Invoke.

Usage:
    inv --list          # List all tasks
    inv install         # Install dependencies
    inv dev             # Setup development environment
    inv status          # Check service status
    inv test            # Run tests
"""

from invoke import task


@task
def install(c):
    """Install dependencies"""
    print("📦 Installing dependencies...")
    c.run("python3 -m pip install -e '.[dev]'")
    print("✅ Installation complete!")


@task
def dev(c):
    """Setup development environment"""
    print("🚀 Setting up development environment...")
    c.run("./scripts/services.sh start-phoenix")
    print("✅ Development environment ready!")
    print("📊 Phoenix UI: http://localhost:6006")


@task
def status(c):
    """Check service status"""
    c.run("./scripts/services.sh status")


@task
def start(c):
    """Start Phoenix server"""
    c.run("./scripts/services.sh start-phoenix")


@task
def stop(c):
    """Stop Phoenix server"""
    c.run("./scripts/services.sh stop-phoenix")


@task
def logs(c):
    """View Phoenix logs"""
    c.run("docker logs -f cinder-phoenix")


@task
def test(c, coverage=True):
    """Run tests"""
    print("🧪 Running tests...")
    if coverage:
        c.run("python3 -m pytest tests/ -v --cov=cinder_cli")
    else:
        c.run("python3 -m pytest tests/ -v")


@task
def clean(c):
    """Clean up environment"""
    print("🧹 Cleaning up...")
    c.run("./scripts/services.sh stop-phoenix", warn=True)
    c.run("docker volume rm phoenix-data", warn=True)
    print("✅ Clean complete!")


@task
def format(c):
    """Format code"""
    print("🎨 Formatting code...")
    c.run("python3 -m black cinder_cli/ tests/")
    c.run("python3 -m isort cinder_cli/ tests/")
    print("✅ Format complete!")


@task
def lint(c):
    """Lint code"""
    print("🔍 Linting code...")
    c.run("python3 -m flake8 cinder_cli/ tests/")
    c.run("python3 -m mypy cinder_cli/")
    print("✅ Lint complete!")


@task(pre=[install, dev])
def setup(c):
    """Complete setup: install dependencies and start services"""
    print("✅ Complete setup finished!")
    print("📊 Phoenix UI: http://localhost:6006")
