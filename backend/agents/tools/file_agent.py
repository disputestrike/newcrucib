"""
File system operations agent.
Can read, write, create, delete, move files and directories.
"""

from typing import Dict, Any
import os
from pathlib import Path
import shutil
from ..base_agent import BaseAgent, AgentValidationError
from ..registry import AgentRegistry


@AgentRegistry.register
class FileAgent(BaseAgent):
    """
    File system operations.
    """
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        super().__init__(llm_client, config)
        # Safety: restrict to workspace directory
        self.workspace = Path(config.get("workspace_dir", "./workspace"))
        self.workspace.mkdir(exist_ok=True)
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        super().validate_input(context)
        
        if "action" not in context:
            raise AgentValidationError(f"{self.name}: 'action' required")
        
        valid_actions = ["read", "write", "create_dir", "delete", "move", "list", "exists"]
        if context["action"] not in valid_actions:
            raise AgentValidationError(f"{self.name}: Invalid action")
        
        if context["action"] in ["read", "write", "delete", "move"] and "path" not in context:
            raise AgentValidationError(f"{self.name}: 'path' required")
        
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operation"""
        action = context["action"]
        path = context.get("path")
        
        try:
            # Make path relative to workspace for safety
            if path:
                full_path = self.workspace / path
            else:
                full_path = self.workspace
            
            if action == "read":
                if not full_path.exists():
                    return {"success": False, "error": "File not found"}
                
                content = full_path.read_text()
                return {
                    "success": True,
                    "path": str(path),
                    "content": content,
                    "size": len(content)
                }
            
            elif action == "write":
                content = context.get("content", "")
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                
                return {
                    "success": True,
                    "path": str(path),
                    "bytes_written": len(content)
                }
            
            elif action == "create_dir":
                full_path.mkdir(parents=True, exist_ok=True)
                return {
                    "success": True,
                    "path": str(path)
                }
            
            elif action == "delete":
                if full_path.is_file():
                    full_path.unlink()
                elif full_path.is_dir():
                    shutil.rmtree(full_path)
                
                return {
                    "success": True,
                    "path": str(path),
                    "deleted": True
                }
            
            elif action == "move":
                destination = context.get("destination")
                if not destination:
                    return {"success": False, "error": "destination required"}
                
                dest_path = self.workspace / destination
                shutil.move(str(full_path), str(dest_path))
                
                return {
                    "success": True,
                    "from": str(path),
                    "to": str(destination)
                }
            
            elif action == "list":
                if not full_path.is_dir():
                    return {"success": False, "error": "Not a directory"}
                
                files = [str(f.relative_to(self.workspace)) for f in full_path.iterdir()]
                return {
                    "success": True,
                    "path": str(path),
                    "files": files,
                    "count": len(files)
                }
            
            elif action == "exists":
                return {
                    "success": True,
                    "path": str(path),
                    "exists": full_path.exists(),
                    "is_file": full_path.is_file(),
                    "is_dir": full_path.is_dir()
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
