"""Dependency injection for FastAPI"""
from typing import AsyncGenerator
from neo4j import AsyncGraphDatabase, AsyncDriver
import asyncpg
from openai import AsyncOpenAI

from app.config import settings


class Neo4jConnection:
    """Neo4j connection manager"""
    
    def __init__(self):
        self.driver: AsyncDriver | None = None
    
    async def connect(self):
        """Initialize Neo4j driver"""
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
    
    async def close(self):
        """Close Neo4j driver"""
        if self.driver:
            await self.driver.close()
            self.driver = None
    
    async def get_session(self):
        """Get Neo4j session"""
        if not self.driver:
            await self.connect()
        return self.driver.session()


# Global instances
neo4j_conn = Neo4jConnection()
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


async def get_neo4j_session():
    """FastAPI dependency for Neo4j session"""
    session = await neo4j_conn.get_session()
    try:
        yield session
    finally:
        await session.close()


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency for target database connection"""
    conn = await asyncpg.connect(
        host=settings.target_db_host,
        port=settings.target_db_port,
        database=settings.target_db_name,
        user=settings.target_db_user,
        password=settings.target_db_password,
    )
    try:
        yield conn
    finally:
        await conn.close()


async def get_openai_client():
    """FastAPI dependency for OpenAI client"""
    return openai_client

