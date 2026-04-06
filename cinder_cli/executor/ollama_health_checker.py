"""
Ollama Health Checker - Checks Ollama service status.
"""

from __future__ import annotations

import httpx
from typing import Any


class OllamaHealthChecker:
    """Check Ollama service health and availability."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.timeout = 5.0

    def check_connection(self) -> dict[str, Any]:
        """
        Check if Ollama service is running and accessible.

        Returns:
            Dictionary with connection status
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/tags")
                
                if response.status_code == 200:
                    return {
                        "connected": True,
                        "status": "running",
                        "message": "Ollama service is running",
                    }
                else:
                    error_detail = ""
                    try:
                        error_body = response.text
                        if error_body:
                            error_detail = f" - {error_body}"
                    except Exception:
                        pass
                    return {
                        "connected": False,
                        "status": "error",
                        "status_code": response.status_code,
                        "message": f"Ollama returned status code {response.status_code}{error_detail}",
                    }
        except httpx.ConnectError as e:
            return {
                "connected": False,
                "status": "not_running",
                "message": f"Ollama service is not running. Please start Ollama first. Error: {str(e)}",
            }
        except httpx.TimeoutException:
            return {
                "connected": False,
                "status": "timeout",
                "message": f"Ollama service is not responding (timeout: {self.timeout}s)",
            }
        except Exception as e:
            return {
                "connected": False,
                "status": "error",
                "message": f"Failed to connect to Ollama: {str(e)}",
            }

    def check_model(self, model_name: str) -> dict[str, Any]:
        """
        Check if a specific model is available.

        Args:
            model_name: Name of the model to check

        Returns:
            Dictionary with model availability status
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/tags")
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    
                    if model_name in model_names:
                        return {
                            "available": True,
                            "message": f"Model '{model_name}' is available",
                        }
                    else:
                        return {
                            "available": False,
                            "message": f"Model '{model_name}' not found. Available models: {', '.join(model_names) if model_names else 'none'}",
                            "available_models": model_names,
                        }
                else:
                    error_detail = ""
                    try:
                        error_body = response.text
                        if error_body:
                            error_detail = f" - {error_body}"
                    except Exception:
                        pass
                    return {
                        "available": False,
                        "message": f"Failed to get model list (status {response.status_code}){error_detail}",
                    }
        except Exception as e:
            return {
                "available": False,
                "message": f"Failed to check model: {str(e)}",
            }

    def get_service_info(self) -> dict[str, Any]:
        """
        Get detailed Ollama service information.

        Returns:
            Dictionary with service information
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/version")
                
                if response.status_code == 200:
                    version_info = response.json()
                    return {
                        "connected": True,
                        "version": version_info.get("version", "unknown"),
                        "message": "Ollama service is running",
                    }
                else:
                    error_detail = ""
                    try:
                        error_body = response.text
                        if error_body:
                            error_detail = f" - {error_body}"
                    except Exception:
                        pass
                    return {
                        "connected": False,
                        "message": f"Failed to get version info (status {response.status_code}){error_detail}",
                    }
        except Exception as e:
            return {
                "connected": False,
                "message": f"Failed to get service info: {str(e)}",
            }

    def full_health_check(self, model_name: str | None = None) -> dict[str, Any]:
        """
        Perform a full health check including connection and model availability.

        Args:
            model_name: Optional model name to check

        Returns:
            Dictionary with complete health check results
        """
        connection_status = self.check_connection()
        
        if not connection_status["connected"]:
            result = {
                "healthy": False,
                "connection": connection_status,
                "recommendation": "Please start Ollama service: ollama serve",
            }
            if model_name:
                result["model"] = None
            return result
        
        model_status = None
        if model_name:
            model_status = self.check_model(model_name)
            
            if not model_status["available"]:
                return {
                    "healthy": False,
                    "connection": connection_status,
                    "model": model_status,
                    "recommendation": f"Please pull the model: ollama pull {model_name}",
                }
        
        result = {
            "healthy": True,
            "connection": connection_status,
            "recommendation": "All checks passed",
        }
        if model_status:
            result["model"] = model_status
        
        return result
