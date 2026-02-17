"""
API integration agent.
Can make HTTP requests, handle authentication, call external APIs.
"""

from typing import Dict, Any
import httpx
from backend.agents.base_agent import BaseAgent, AgentValidationError
from backend.agents.registry import AgentRegistry


@AgentRegistry.register
class APIAgent(BaseAgent):
    """
    HTTP API calls and integrations.
    """
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        super().validate_input(context)
        
        if "url" not in context:
            raise AgentValidationError(f"{self.name}: 'url' required")
        
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request.
        
        Supports:
        - GET, POST, PUT, DELETE, PATCH
        - Headers, auth, JSON/form data
        - Query parameters
        """
        url = context["url"]
        method = context.get("method", "GET").upper()
        headers = context.get("headers", {})
        data = context.get("data")
        params = context.get("params")
        auth = context.get("auth")  # ("username", "password")
        timeout = context.get("timeout", 30)
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if data and method != "GET" else None,
                    params=params,
                    auth=auth
                )
                
                # Try to parse as JSON
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                return {
                    "success": response.is_success,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "data": response_data,
                    "url": str(response.url)
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
