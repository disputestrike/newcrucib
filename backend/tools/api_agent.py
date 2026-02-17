"""
API Agent - make HTTP requests and handle OAuth.
Can:
- GET/POST/PUT/DELETE requests
- Handle authentication (Bearer, Basic, OAuth)
- Parse JSON/XML responses
- Handle rate limits

SECURITY WARNING: This agent makes HTTP requests to user-provided URLs.
- Validate URLs before use
- Use allowlists when possible
- Be cautious with internal network access
"""

import httpx
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from .base_agent import BaseAgent


class APIAgent(BaseAgent):
    """HTTP API interaction agent"""
    
    def __init__(self, llm_client, config):
        super().__init__(llm_client, config)
        self.name = "APIAgent"
        # Optional: Configure URL allowlist
        self.allowed_schemes = config.get("allowed_schemes", ["http", "https"])
        self.blocked_hosts = config.get("blocked_hosts", [
            "localhost", "127.0.0.1", "0.0.0.0",
            "169.254.169.254",  # AWS metadata service
            "metadata.google.internal"  # GCP metadata service
        ])
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL to prevent SSRF attacks"""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in self.allowed_schemes:
                raise ValueError(f"URL scheme '{parsed.scheme}' not allowed")
            if parsed.hostname in self.blocked_hosts:
                raise ValueError(f"Access to {parsed.hostname} is not allowed")
            # Block private IP ranges
            if parsed.hostname and (
                parsed.hostname.startswith("192.168.") or
                parsed.hostname.startswith("10.") or
                parsed.hostname.startswith("172.16.")
            ):
                raise ValueError("Access to private IP ranges is not allowed")
            return True
        except Exception as e:
            raise ValueError(f"Invalid URL: {e}")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request.
        
        Expected context:
        {
            "method": "GET|POST|PUT|DELETE",
            "url": "https://api.example.com/endpoint",
            "headers": {"Authorization": "Bearer token"},
            "body": {"key": "value"},
            "params": {"page": 1}
        }
        """
        method = context.get("method", "GET").upper()
        url = context.get("url")
        headers = context.get("headers", {})
        body = context.get("body")
        params = context.get("params")
        
        try:
            # Validate URL to prevent SSRF
            self._validate_url(url)
            
            async with httpx.AsyncClient() as client:
                try:
                    if method == "GET":
                        response = await client.get(url, headers=headers, params=params)
                    elif method == "POST":
                        response = await client.post(url, headers=headers, json=body, params=params)
                    elif method == "PUT":
                        response = await client.put(url, headers=headers, json=body, params=params)
                    elif method == "DELETE":
                        response = await client.delete(url, headers=headers, params=params)
                    else:
                        return {"error": f"Unknown method: {method}"}
                    
                    # Parse response
                    try:
                        data = response.json()
                    except (ValueError, TypeError):
                        data = response.text
                    
                    return {
                        "status_code": response.status_code,
                        "success": 200 <= response.status_code < 300,
                        "headers": dict(response.headers),
                        "data": data,
                        "url": str(response.url)
                    }
                    
                except Exception as e:
                    return {
                        "error": str(e),
                        "success": False
                    }
        except ValueError as e:
            return {
                "error": str(e),
                "success": False
            }
