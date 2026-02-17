"""
Database operations agent.
Can execute SQL queries, create tables, manage data.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentValidationError
from ..registry import AgentRegistry


@AgentRegistry.register
class DatabaseOperationsAgent(BaseAgent):
    """
    Execute database operations.
    Supports PostgreSQL, MySQL, SQLite.
    """
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        super().validate_input(context)
        
        if "query" not in context and "action" not in context:
            raise AgentValidationError(f"{self.name}: 'query' or 'action' required")
        
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute database operation.
        
        Actions:
        - query: Execute SELECT query
        - execute: Execute INSERT/UPDATE/DELETE
        - create_table: Create table from schema
        - migrate: Run migration
        """
        action = context.get("action", "query")
        query = context.get("query")
        db_url = context.get("database_url", "sqlite:///./test.db")
        
        try:
            # Use SQLAlchemy for database operations
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine(db_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            if action == "query":
                result = session.execute(text(query))
                rows = [dict(row._mapping) for row in result]
                
                return {
                    "success": True,
                    "rows": rows,
                    "count": len(rows)
                }
            
            elif action == "execute":
                result = session.execute(text(query))
                session.commit()
                
                return {
                    "success": True,
                    "rows_affected": result.rowcount
                }
            
            elif action == "create_table":
                schema = context.get("schema")
                # Execute CREATE TABLE statement
                session.execute(text(schema))
                session.commit()
                
                return {
                    "success": True,
                    "table_created": True
                }
            
            session.close()
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
