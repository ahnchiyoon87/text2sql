"""DDL extraction from PostgreSQL database"""
from typing import List, Dict, Any
import asyncpg

from app.config import settings


class SchemaExtractor:
    """Extract schema metadata from PostgreSQL"""
    
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
    
    async def extract_tables(self, schema: str = None) -> List[Dict[str, Any]]:
        """Extract table metadata"""
        schema = schema or settings.target_db_schema
        
        query = """
        SELECT 
            t.table_schema AS schema,
            t.table_name AS name,
            obj_description((quote_ident(t.table_schema)||'.'||quote_ident(t.table_name))::regclass) AS description,
            t.table_type AS table_type
        FROM information_schema.tables t
        WHERE t.table_schema = $1
          AND t.table_type IN ('BASE TABLE', 'VIEW')
        ORDER BY t.table_name
        """
        
        rows = await self.conn.fetch(query, schema)
        
        return [
            {
                "schema": row["schema"],
                "name": row["name"],
                "description": row["description"] or "",
                "table_type": row["table_type"]
            }
            for row in rows
        ]
    
    async def extract_columns(self, schema: str = None) -> List[Dict[str, Any]]:
        """Extract column metadata"""
        schema = schema or settings.target_db_schema
        
        query = """
        SELECT 
            c.table_schema AS schema,
            c.table_name AS table_name,
            c.column_name AS name,
            c.data_type AS dtype,
            c.is_nullable = 'YES' AS nullable,
            c.column_default AS default_value,
            col_description((quote_ident(c.table_schema)||'.'||quote_ident(c.table_name))::regclass, c.ordinal_position) AS description
        FROM information_schema.columns c
        WHERE c.table_schema = $1
        ORDER BY c.table_name, c.ordinal_position
        """
        
        rows = await self.conn.fetch(query, schema)
        
        return [
            {
                "schema": row["schema"],
                "table_name": row["table_name"],
                "name": row["name"],
                "dtype": row["dtype"],
                "nullable": row["nullable"],
                "default_value": row["default_value"],
                "description": row["description"] or ""
            }
            for row in rows
        ]
    
    async def extract_foreign_keys(self, schema: str = None) -> List[Dict[str, Any]]:
        """Extract foreign key constraints"""
        schema = schema or settings.target_db_schema
        
        query = """
        SELECT
            tc.table_schema AS from_schema,
            tc.table_name AS from_table,
            kcu.column_name AS from_column,
            ccu.table_schema AS to_schema,
            ccu.table_name AS to_table,
            ccu.column_name AS to_column,
            tc.constraint_name AS constraint_name,
            rc.update_rule AS on_update,
            rc.delete_rule AS on_delete
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        JOIN information_schema.referential_constraints AS rc
            ON rc.constraint_name = tc.constraint_name
            AND rc.constraint_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = $1
        ORDER BY tc.table_name, tc.constraint_name
        """
        
        rows = await self.conn.fetch(query, schema)
        
        return [
            {
                "from_schema": row["from_schema"],
                "from_table": row["from_table"],
                "from_column": row["from_column"],
                "to_schema": row["to_schema"],
                "to_table": row["to_table"],
                "to_column": row["to_column"],
                "constraint_name": row["constraint_name"],
                "on_update": row["on_update"],
                "on_delete": row["on_delete"]
            }
            for row in rows
        ]
    
    async def extract_primary_keys(self, schema: str = None) -> List[Dict[str, Any]]:
        """Extract primary key constraints"""
        schema = schema or settings.target_db_schema
        
        query = """
        SELECT
            tc.table_schema AS schema,
            tc.table_name AS table_name,
            kcu.column_name AS column_name,
            tc.constraint_name AS constraint_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = $1
        ORDER BY tc.table_name, kcu.ordinal_position
        """
        
        rows = await self.conn.fetch(query, schema)
        
        return [
            {
                "schema": row["schema"],
                "table_name": row["table_name"],
                "column_name": row["column_name"],
                "constraint_name": row["constraint_name"]
            }
            for row in rows
        ]
    
    async def extract_indexes(self, schema: str = None) -> List[Dict[str, Any]]:
        """Extract index information"""
        schema = schema or settings.target_db_schema
        
        query = """
        SELECT
            schemaname AS schema,
            tablename AS table_name,
            indexname AS index_name,
            indexdef AS definition
        FROM pg_indexes
        WHERE schemaname = $1
        ORDER BY tablename, indexname
        """
        
        rows = await self.conn.fetch(query, schema)
        
        return [
            {
                "schema": row["schema"],
                "table_name": row["table_name"],
                "index_name": row["index_name"],
                "definition": row["definition"]
            }
            for row in rows
        ]
    
    async def get_sample_values(
        self,
        table_name: str,
        column_name: str,
        limit: int = 5,
        schema: str = None
    ) -> List[Any]:
        """Get sample distinct values from a column (for embedding context)"""
        schema = schema or settings.target_db_schema
        
        try:
            query = f"""
            SELECT DISTINCT "{column_name}"
            FROM "{schema}"."{table_name}"
            WHERE "{column_name}" IS NOT NULL
            LIMIT $1
            """
            
            rows = await self.conn.fetch(query, limit)
            return [row[0] for row in rows]
        except Exception:
            # If error, return empty
            return []

