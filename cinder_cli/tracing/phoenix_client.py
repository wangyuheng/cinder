"""
Phoenix Client - Manages connection to Phoenix server.
"""

from __future__ import annotations

import logging
from typing import Any

from .config import TracingConfig

logger = logging.getLogger(__name__)


class PhoenixClient:
    """Client for connecting to Phoenix server."""
    
    def __init__(self, config: TracingConfig):
        """
        Initialize Phoenix client.
        
        Args:
            config: Tracing configuration
        """
        self.config = config
        self._session = None
        self._connected = False
        
        if config.enabled:
            self._connect()
    
    def _connect(self) -> None:
        """Connect to Phoenix server."""
        try:
            import phoenix as px
            
            endpoint = self.config.get_phoenix_endpoint()
            logger.info(f"Connecting to Phoenix at {endpoint}")
            
            self._session = px.launch_app()
            self._connected = True
            
            logger.info("Successfully connected to Phoenix")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Phoenix: {e}")
            logger.info("Continuing in degraded mode (traces stored locally)")
            self._connected = False
    
    def is_connected(self) -> bool:
        """
        Check if connected to Phoenix server.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected
    
    def get_session(self) -> Any:
        """
        Get Phoenix session.
        
        Returns:
            Phoenix session object or None
        """
        return self._session
    
    def close(self) -> None:
        """Close Phoenix client connection."""
        if self._session:
            try:
                self._session.close()
            except Exception as e:
                logger.warning(f"Error closing Phoenix session: {e}")
        
        self._session = None
        self._connected = False
