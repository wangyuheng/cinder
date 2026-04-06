"""
Phoenix Server - Check Phoenix server status (external dependency).
"""

from __future__ import annotations

import logging
import subprocess
from typing import Optional

import requests

from .config import TracingConfig

logger = logging.getLogger(__name__)


class PhoenixServer:
    """
    Check Phoenix server status.
    
    Phoenix is an external dependency that should be started separately.
    Use `cinder service start-phoenix` or `python scripts/services.py start-phoenix`
    to start the Phoenix server.
    """
    
    DEFAULT_PORT = 6006
    DEFAULT_HOST = "localhost"
    DOCKER_IMAGE = "arizephoenix/phoenix:latest"
    CONTAINER_NAME = "cinder-phoenix"
    
    def __init__(self, config: TracingConfig):
        """
        Initialize Phoenix server manager.
        
        Args:
            config: Tracing configuration
        """
        self.config = config
        self.host = config.phoenix_host or self.DEFAULT_HOST
        self.port = config.phoenix_port or self.DEFAULT_PORT
    
    def start(self, background: bool = True) -> dict:
        """
        Check if Phoenix server is running.
        
        Phoenix should be started externally using:
        - `cinder service start-phoenix`
        - `python scripts/services.py start-phoenix`
        
        Returns:
            Dictionary with status and message
        """
        if self.is_running():
            url = self.get_url()
            logger.info(f"Phoenix server is running at {url}")
            return {
                "status": "already_running",
                "message": f"Phoenix server is running",
                "url": url
            }
        else:
            logger.warning("Phoenix server is not running")
            return {
                "status": "not_running",
                "message": "Phoenix server is not running. Start it with: cinder service start-phoenix",
                "url": self.get_url()
            }
    
    def stop(self) -> dict:
        """
        Check if Phoenix server is running.
        
        Phoenix should be stopped externally using:
        - `cinder service stop-phoenix`
        - `python scripts/services.py stop-phoenix`
        
        Returns:
            Dictionary with status and message
        """
        if not self.is_running():
            logger.info("Phoenix server is not running")
            return {
                "status": "not_running",
                "message": "Phoenix server is not running"
            }
        
        return {
            "status": "running",
            "message": "Phoenix server is running. Stop it with: cinder service stop-phoenix"
        }
    
    def status(self) -> dict:
        """
        Check Phoenix server status.
        
        Returns:
            Dictionary with status information
        """
        is_running = self.is_running()
        url = self.get_url() if is_running else None
        
        container_status = self._get_container_status()
        
        return {
            "running": is_running,
            "url": url,
            "container": self.CONTAINER_NAME,
            "container_status": container_status,
            "host": self.host,
            "port": self.port,
            "docker_image": self.DOCKER_IMAGE
        }
    
    def _get_container_status(self) -> Optional[str]:
        """Get container status."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Status}}", self.CONTAINER_NAME],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def is_running(self) -> bool:
        """
        Check if Phoenix server is running.
        
        Returns:
            True if server is running
        """
        try:
            url = f"http://{self.host}:{self.port}/healthz"
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_url(self) -> str:
        """
        Get Phoenix server URL.
        
        Returns:
            Phoenix server URL
        """
        return f"http://{self.host}:{self.port}"
