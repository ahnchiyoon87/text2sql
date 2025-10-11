"""SQL execution with safety and timeout"""
import asyncio
from typing import List, Dict, Any
import asyncpg

from app.config import settings


class SQLExecutionError(Exception):
    """Raised when SQL execution fails"""
    pass


class SQLExecutor:
    """Execute SQL queries with safety constraints"""
    
    def __init__(self):
        self.timeout = settings.sql_timeout_seconds
        self.max_rows = settings.sql_max_rows
    
    async def execute_query(
        self,
        conn: asyncpg.Connection,
        sql: str
    ) -> Dict[str, Any]:
        """
        Execute SQL query and return results with metadata.
        
        Returns:
            {
                "columns": List[str],
                "rows": List[List[Any]],
                "row_count": int,
                "execution_time_ms": float
            }
        """
        import time
        start_time = time.time()
        
        try:
            # Execute with timeout
            rows = await asyncio.wait_for(
                conn.fetch(sql),
                timeout=self.timeout
            )
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Check row count limit
            if len(rows) > self.max_rows:
                raise SQLExecutionError(
                    f"Query returned too many rows: {len(rows)} (max: {self.max_rows})"
                )
            
            # Extract columns and data
            columns = list(rows[0].keys()) if rows else []
            data = [list(row.values()) for row in rows]
            
            return {
                "columns": columns,
                "rows": data,
                "row_count": len(rows),
                "execution_time_ms": round(execution_time_ms, 2)
            }
            
        except asyncio.TimeoutError:
            raise SQLExecutionError(
                f"Query execution timeout after {self.timeout} seconds"
            )
        except asyncpg.PostgresError as e:
            raise SQLExecutionError(f"Database error: {str(e)}")
        except Exception as e:
            raise SQLExecutionError(f"Execution failed: {str(e)}")
    
    async def explain_query(
        self,
        conn: asyncpg.Connection,
        sql: str
    ) -> List[Dict[str, Any]]:
        """Get query execution plan"""
        explain_sql = f"EXPLAIN (FORMAT JSON) {sql}"
        
        try:
            result = await conn.fetchval(explain_sql)
            return result
        except Exception as e:
            # If EXPLAIN fails, return empty
            return []
    
    @staticmethod
    def format_results_for_json(results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for JSON serialization"""
        # Convert any non-serializable types
        formatted_rows = []
        for row in results["rows"]:
            formatted_row = []
            for value in row:
                if value is None:
                    formatted_row.append(None)
                elif isinstance(value, (str, int, float, bool)):
                    formatted_row.append(value)
                else:
                    # Convert other types to string
                    formatted_row.append(str(value))
            formatted_rows.append(formatted_row)
        
        return {
            **results,
            "rows": formatted_rows
        }

