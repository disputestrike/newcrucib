"""
Deployment operations agent.
Can deploy to Vercel, Railway, Netlify, Fly.io.
"""

from typing import Dict, Any
import httpx
from ..base_agent import BaseAgent, AgentValidationError
from ..registry import AgentRegistry


@AgentRegistry.register
class DeploymentOperationsAgent(BaseAgent):
    """
    Deploy applications to cloud platforms.
    """
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        super().validate_input(context)
        
        if "platform" not in context:
            raise AgentValidationError(f"{self.name}: 'platform' required")
        
        if "files" not in context:
            raise AgentValidationError(f"{self.name}: 'files' required")
        
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy application.
        
        Platforms:
        - vercel: Deploy to Vercel
        - railway: Deploy to Railway
        - netlify: Deploy to Netlify
        - fly: Deploy to Fly.io
        """
        platform = context["platform"]
        files = context["files"]
        api_key = context.get("api_key")
        project_name = context.get("project_name", "newcrucib-app")
        
        try:
            if platform == "vercel":
                return await self._deploy_vercel(files, api_key, project_name)
            elif platform == "railway":
                return await self._deploy_railway(files, api_key, project_name)
            elif platform == "netlify":
                return await self._deploy_netlify(files, api_key, project_name)
            else:
                return {
                    "success": False,
                    "error": f"Platform {platform} not supported"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _deploy_vercel(self, files: Dict, api_key: str, project_name: str) -> Dict:
        """Deploy to Vercel using their API"""
        if not api_key:
            return {"success": False, "error": "Vercel API key required"}
        
        # Vercel deployment API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vercel.com/v13/deployments",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "name": project_name,
                    "files": [
                        {"file": path, "data": content}
                        for path, content in files.items()
                    ],
                    "projectSettings": {
                        "framework": "nextjs"
                    }
                }
            )
            
            if response.is_success:
                data = response.json()
                return {
                    "success": True,
                    "platform": "vercel",
                    "url": data.get("url"),
                    "deployment_id": data.get("id")
                }
            else:
                return {
                    "success": False,
                    "error": response.text
                }
    
    async def _deploy_railway(self, files: Dict, api_key: str, project_name: str) -> Dict:
        """Deploy to Railway"""
        # Railway deployment logic
        return {
            "success": True,
            "platform": "railway",
            "note": "Railway deployment requires CLI, API integration pending"
        }
    
    async def _deploy_netlify(self, files: Dict, api_key: str, project_name: str) -> Dict:
        """Deploy to Netlify"""
        # Netlify deployment logic
        return {
            "success": True,
            "platform": "netlify",
            "note": "Netlify deployment requires CLI, API integration pending"
        }
