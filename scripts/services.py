#!/usr/bin/env python3
"""
Service Manager - Manage external dependencies (Ollama, Phoenix).
"""

from __future__ import annotations

import subprocess
import sys
import time
from typing import Optional

import requests


class ServiceManager:
    """Manage external services."""
    
    OLLAMA_HOST = "http://localhost:11434"
    PHOENIX_HOST = "http://localhost:6006"
    PHOENIX_DOCKER_IMAGE = "arizephoenix/phoenix:latest"
    PHOENIX_CONTAINER_NAME = "cinder-phoenix"
    
    def check_ollama(self) -> dict:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.OLLAMA_HOST}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "running": True,
                    "url": self.OLLAMA_HOST,
                    "models": len(models)
                }
        except:
            pass
        
        return {
            "running": False,
            "url": self.OLLAMA_HOST,
            "message": "Ollama is not running"
        }
    
    def check_phoenix(self) -> dict:
        """Check if Phoenix is running."""
        try:
            response = requests.get(f"{self.PHOENIX_HOST}/healthz", timeout=2)
            if response.status_code == 200:
                return {
                    "running": True,
                    "url": self.PHOENIX_HOST,
                    "container": self.PHOENIX_CONTAINER_NAME
                }
        except:
            pass
        
        return {
            "running": False,
            "url": self.PHOENIX_HOST,
            "message": "Phoenix is not running"
        }
    
    def check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def start_phoenix(self) -> dict:
        """Start Phoenix via Docker."""
        if not self.check_docker():
            return {
                "success": False,
                "message": "Docker is not installed or not running"
            }
        
        result = self.check_phoenix()
        if result["running"]:
            return {
                "success": True,
                "message": "Phoenix is already running",
                "url": result["url"]
            }
        
        print(f"Pulling Phoenix Docker image: {self.PHOENIX_DOCKER_IMAGE}")
        pull_result = subprocess.run(
            ["docker", "pull", self.PHOENIX_DOCKER_IMAGE],
            capture_output=True,
            text=True
        )
        
        if pull_result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to pull Docker image: {pull_result.stderr}"
            }
        
        subprocess.run(
            ["docker", "rm", "-f", self.PHOENIX_CONTAINER_NAME],
            capture_output=True
        )
        
        print(f"Starting Phoenix container: {self.PHOENIX_CONTAINER_NAME}")
        run_result = subprocess.run(
            [
                "docker", "run", "-d",
                "--name", self.PHOENIX_CONTAINER_NAME,
                "-p", "6006:6006",
                "-v", "phoenix-data:/root/.phoenix",
                self.PHOENIX_DOCKER_IMAGE
            ],
            capture_output=True,
            text=True
        )
        
        if run_result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to start container: {run_result.stderr}"
            }
        
        time.sleep(3)
        
        result = self.check_phoenix()
        if result["running"]:
            return {
                "success": True,
                "message": "Phoenix started successfully",
                "url": result["url"]
            }
        else:
            return {
                "success": False,
                "message": "Phoenix container started but service not responding"
            }
    
    def stop_phoenix(self) -> dict:
        """Stop Phoenix container."""
        result = subprocess.run(
            ["docker", "stop", self.PHOENIX_CONTAINER_NAME],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            subprocess.run(
                ["docker", "rm", self.PHOENIX_CONTAINER_NAME],
                capture_output=True
            )
            return {
                "success": True,
                "message": "Phoenix stopped successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to stop Phoenix"
            }
    
    def check_all(self) -> dict:
        """Check all services."""
        return {
            "ollama": self.check_ollama(),
            "phoenix": self.check_phoenix(),
            "docker": self.check_docker()
        }
    
    def print_status(self):
        """Print service status."""
        print("\n" + "="*60)
        print("Service Status")
        print("="*60)
        
        ollama = self.check_ollama()
        print(f"\n[Ollama]")
        print(f"  Status: {'✓ Running' if ollama['running'] else '✗ Not Running'}")
        print(f"  URL: {ollama['url']}")
        if ollama['running']:
            print(f"  Models: {ollama['models']}")
        else:
            print(f"  Start: ollama serve")
        
        docker = self.check_docker()
        print(f"\n[Docker]")
        print(f"  Status: {'✓ Available' if docker else '✗ Not Available'}")
        
        phoenix = self.check_phoenix()
        print(f"\n[Phoenix]")
        print(f"  Status: {'✓ Running' if phoenix['running'] else '✗ Not Running'}")
        print(f"  URL: {phoenix['url']}")
        if phoenix['running']:
            print(f"  Container: {phoenix['container']}")
        else:
            print(f"  Start: cinder service start-phoenix")
        
        print("\n" + "="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Cinder services")
    parser.add_argument(
        "command",
        choices=["status", "start-phoenix", "stop-phoenix", "check"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    if args.command == "status":
        manager.print_status()
    elif args.command == "check":
        result = manager.check_all()
        print(result)
        sys.exit(0 if result["ollama"]["running"] else 1)
    elif args.command == "start-phoenix":
        result = manager.start_phoenix()
        if result["success"]:
            print(f"\n✓ {result['message']}")
            if "url" in result:
                print(f"  URL: {result['url']}")
        else:
            print(f"\n✗ {result['message']}")
            sys.exit(1)
    elif args.command == "stop-phoenix":
        result = manager.stop_phoenix()
        if result["success"]:
            print(f"\n✓ {result['message']}")
        else:
            print(f"\n✗ {result['message']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
