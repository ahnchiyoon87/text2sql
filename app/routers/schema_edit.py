"""Schema editing endpoints for user customization"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.deps import get_neo4j_session


router = APIRouter(prefix="/schema-edit", tags=["Schema Editing"])


class TableUpdateRequest(BaseModel):
    """Request to update table metadata"""
    name: str
    schema: str = "public"
    description: Optional[str] = None


class ColumnUpdateRequest(BaseModel):
    """Request to update column metadata"""
    table_name: str
    table_schema: str = "public"
    column_name: str
    description: Optional[str] = None


class RelationshipRequest(BaseModel):
    """Request to add/update relationship"""
    from_table: str
    from_schema: str = "public"
    from_column: str
    to_table: str
    to_schema: str = "public"
    to_column: str
    relationship_type: str = "FK_TO_TABLE"  # FK_TO_TABLE, REFERENCES, etc.
    description: Optional[str] = None


class RelationshipResponse(BaseModel):
    """Response for relationship operations"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str
    description: Optional[str] = None
    created: bool


@router.put("/tables/{table_name}/description")
async def update_table_description(
    table_name: str,
    request: TableUpdateRequest,
    neo4j_session=Depends(get_neo4j_session)
):
    """Update table description"""
    query = """
    MATCH (t:Table {name: $table_name, schema: $schema})
    SET t.description = $description
    RETURN t.name AS name, t.description AS description
    """
    
    result = await neo4j_session.run(
        query, 
        table_name=table_name,
        schema=request.schema,
        description=request.description
    )
    
    records = await result.data()
    if not records:
        raise HTTPException(status_code=404, detail="Table not found")
    
    return {"message": "Table description updated", "data": records[0]}


@router.put("/tables/{table_name}/columns/{column_name}/description")
async def update_column_description(
    table_name: str,
    column_name: str,
    request: ColumnUpdateRequest,
    neo4j_session=Depends(get_neo4j_session)
):
    """Update column description"""
    query = """
    MATCH (t:Table {name: $table_name, schema: $schema})-[:HAS_COLUMN]->(c:Column {name: $column_name})
    SET c.description = $description
    RETURN c.name AS name, c.description AS description
    """
    
    result = await neo4j_session.run(
        query,
        table_name=table_name,
        schema=request.table_schema,
        column_name=column_name,
        description=request.description
    )
    
    records = await result.data()
    if not records:
        raise HTTPException(status_code=404, detail="Column not found")
    
    return {"message": "Column description updated", "data": records[0]}


@router.post("/relationships", response_model=RelationshipResponse)
async def add_relationship(
    request: RelationshipRequest,
    neo4j_session=Depends(get_neo4j_session)
):
    """Add a new relationship between tables"""
    
    # Check if both tables exist
    check_query = """
    MATCH (t1:Table {name: $from_table, schema: $from_schema})
    MATCH (t2:Table {name: $to_table, schema: $to_schema})
    RETURN t1.name AS from_table, t2.name AS to_table
    """
    
    check_result = await neo4j_session.run(
        check_query,
        from_table=request.from_table,
        from_schema=request.from_schema,
        to_table=request.to_table,
        to_schema=request.to_schema
    )
    
    check_records = await check_result.data()
    if not check_records:
        raise HTTPException(status_code=404, detail="One or both tables not found")
    
    # Check if relationship already exists
    existing_query = """
    MATCH (t1:Table {name: $from_table, schema: $from_schema})-[r:FK_TO_TABLE]->(t2:Table {name: $to_table, schema: $to_schema})
    WHERE r.from_column = $from_column AND r.to_column = $to_column
    RETURN r
    """
    
    existing_result = await neo4j_session.run(
        existing_query,
        from_table=request.from_table,
        from_schema=request.from_schema,
        to_table=request.to_table,
        to_schema=request.to_schema,
        from_column=request.from_column,
        to_column=request.to_column
    )
    
    existing_records = await existing_result.data()
    if existing_records:
        return RelationshipResponse(
            from_table=request.from_table,
            from_column=request.from_column,
            to_table=request.to_table,
            to_column=request.to_column,
            relationship_type=request.relationship_type,
            description=request.description,
            created=False
        )
    
    # Create the relationship
    create_query = """
    MATCH (t1:Table {name: $from_table, schema: $from_schema})
    MATCH (t2:Table {name: $to_table, schema: $to_schema})
    CREATE (t1)-[r:FK_TO_TABLE {
        from_column: $from_column,
        to_column: $to_column,
        relationship_type: $relationship_type,
        description: $description,
        user_added: true
    }]->(t2)
    RETURN r
    """
    
    create_result = await neo4j_session.run(
        create_query,
        from_table=request.from_table,
        from_schema=request.from_schema,
        to_table=request.to_table,
        to_schema=request.to_schema,
        from_column=request.from_column,
        to_column=request.to_column,
        relationship_type=request.relationship_type,
        description=request.description
    )
    
    await create_result.data()
    
    return RelationshipResponse(
        from_table=request.from_table,
        from_column=request.from_column,
        to_table=request.to_table,
        to_column=request.to_column,
        relationship_type=request.relationship_type,
        description=request.description,
        created=True
    )


@router.delete("/relationships")
async def remove_relationship(
    from_table: str,
    from_schema: str = "public",
    from_column: str = None,
    to_table: str = None,
    to_schema: str = "public",
    to_column: str = None,
    neo4j_session=Depends(get_neo4j_session)
):
    """Remove a relationship (only user-added ones)"""
    
    if from_column and to_table and to_column:
        # Remove specific relationship
        query = """
        MATCH (t1:Table {name: $from_table, schema: $from_schema})-[r:FK_TO_TABLE]->(t2:Table {name: $to_table, schema: $to_schema})
        WHERE r.from_column = $from_column AND r.to_column = $to_column AND r.user_added = true
        DELETE r
        RETURN count(r) AS deleted_count
        """
        
        params = {
            "from_table": from_table,
            "from_schema": from_schema,
            "from_column": from_column,
            "to_table": to_table,
            "to_schema": to_schema,
            "to_column": to_column
        }
    else:
        # Remove all user-added relationships for the table
        query = """
        MATCH (t1:Table {name: $from_table, schema: $from_schema})-[r:FK_TO_TABLE]->(t2:Table)
        WHERE r.user_added = true
        DELETE r
        RETURN count(r) AS deleted_count
        """
        
        params = {
            "from_table": from_table,
            "from_schema": from_schema
        }
    
    result = await neo4j_session.run(query, **params)
    records = await result.data()
    
    deleted_count = records[0]["deleted_count"] if records else 0
    
    return {"message": f"Removed {deleted_count} relationship(s)"}


@router.get("/relationships/user-added")
async def list_user_added_relationships(
    neo4j_session=Depends(get_neo4j_session)
):
    """List all user-added relationships"""
    query = """
    MATCH (t1:Table)-[r:FK_TO_TABLE]->(t2:Table)
    WHERE r.user_added = true
    RETURN t1.name AS from_table,
           t1.schema AS from_schema,
           r.from_column AS from_column,
           t2.name AS to_table,
           t2.schema AS to_schema,
           r.to_column AS to_column,
           r.relationship_type AS relationship_type,
           r.description AS description
    ORDER BY t1.name, r.from_column
    """
    
    result = await neo4j_session.run(query)
    records = await result.data()
    
    return {
        "relationships": [
            {
                "from_table": r["from_table"],
                "from_schema": r["from_schema"],
                "from_column": r["from_column"],
                "to_table": r["to_table"],
                "to_schema": r["to_schema"],
                "to_column": r["to_column"],
                "relationship_type": r["relationship_type"],
                "description": r.get("description")
            }
            for r in records
        ]
    }
