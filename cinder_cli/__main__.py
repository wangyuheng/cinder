"""
Allow running cinder_cli as a module: python -m cinder_cli
"""

from cinder_cli.cli import main

if __name__ == "__main__":
    main()
