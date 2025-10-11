"""Schema ingestion endpoint"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.deps import get_neo4j_session, get_db_connection, get_openai_client
from app.ingest.ddl_extract import SchemaExtractor
from app.ingest.to_neo4j import Neo4jSchemaLoader
from app.core.embedding import EmbeddingClient


router = APIRouter(prefix="/ingest", tags=["Ingestion"])


class IngestRequest(BaseModel):
    """Request to ingest schema"""
    db_name: str = "postgres"
    schema: Optional[str] = None
    clear_existing: bool = False


class IngestResponse(BaseModel):
    """Response from ingestion"""
    message: str
    status: str
    tables_loaded: int
    columns_loaded: int
    fks_loaded: int


async def run_ingestion(
    db_name: str,
    schema: Optional[str],
    clear_existing: bool,
    neo4j_session,
    db_conn,
    openai_client
):
    """Background task to run schema ingestion"""
    try:
        # Initialize clients
        embedding_client = EmbeddingClient(openai_client)
        loader = Neo4jSchemaLoader(neo4j_session, embedding_client)
        extractor = SchemaExtractor(db_conn)
        
        # Setup Neo4j schema
        await loader.setup_constraints_and_indexes()
        
        # Clear existing if requested
        if clear_existing:
            await loader.clear_schema(db_name)
        
        # Extract schema metadata
        tables = await extractor.extract_tables(schema)
        columns = await extractor.extract_columns(schema)
        foreign_keys = await extractor.extract_foreign_keys(schema)
        primary_keys = await extractor.extract_primary_keys(schema)
        
        # Load into Neo4j
        await loader.load_tables(tables, db_name)
        await loader.load_columns(columns, db_name)
        await loader.load_foreign_keys(foreign_keys, db_name)
        await loader.load_primary_keys(primary_keys, db_name)
        
        print(f"✓ Ingestion completed: {len(tables)} tables, {len(columns)} columns, {len(foreign_keys)} FKs")
        
    except Exception as e:
        print(f"✗ Ingestion failed: {str(e)}")
        raise


@router.post("", response_model=IngestResponse)
async def ingest_schema(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    neo4j_session=Depends(get_neo4j_session),
    db_conn=Depends(get_db_connection),
    openai_client=Depends(get_openai_client)
):
    """
    Ingest database schema into Neo4j graph.
    This is a long-running operation and will run in the background.
    """
    try:
        # Run synchronously for now (could be made async with task queue)
        embedding_client = EmbeddingClient(openai_client)
        loader = Neo4jSchemaLoader(neo4j_session, embedding_client)
        extractor = SchemaExtractor(db_conn)
        
        # Setup Neo4j schema
        await loader.setup_constraints_and_indexes()
        
        # Clear existing if requested
        if request.clear_existing:
            await loader.clear_schema(request.db_name)
        
        # Extract schema metadata
        tables = await extractor.extract_tables(request.schema)
        columns = await extractor.extract_columns(request.schema)
        foreign_keys = await extractor.extract_foreign_keys(request.schema)
        primary_keys = await extractor.extract_primary_keys(request.schema)
        
        # Load into Neo4j
        await loader.load_tables(tables, request.db_name)
        await loader.load_columns(columns, request.db_name)
        await loader.load_foreign_keys(foreign_keys, request.db_name)
        await loader.load_primary_keys(primary_keys, request.db_name)
        
        return IngestResponse(
            message="Schema ingestion completed successfully",
            status="success",
            tables_loaded=len(tables),
            columns_loaded=len(columns),
            fks_loaded=len(foreign_keys)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

