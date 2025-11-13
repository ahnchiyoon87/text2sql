from typing import List, Dict

from neo4j import AsyncSession


async def get_table_relationships(
    neo4j_session: AsyncSession,
    table_name: str,
    limit: int,
) -> List[Dict]:
    """
    특정 테이블과 연관된 다른 테이블 정보를 조회한다.
    기존 run_mocked_tools 로직을 재사용한다.
    """
    query = """
    MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c1:Column)-[fk:FK_TO]->(c2:Column)<-[:HAS_COLUMN]-(t2:Table)
    RETURN DISTINCT t2.name AS related_table,
           t2.description AS related_table_description,
           'foreign_key' AS relation_type,
           c1.name AS from_column,
           c1.description AS from_column_description,
           c2.name AS to_column,
           c2.description AS to_column_description
    LIMIT $limit
    """

    result = await neo4j_session.run(query, table_name=table_name, limit=limit)
    records = await result.data()

    relationships: List[Dict] = []
    for record in records:
        rel_info: Dict = {
            "related_table": record["related_table"],
            "relation_type": record["relation_type"],
            "from_column": record.get("from_column"),
            "to_column": record.get("to_column"),
        }
        if record.get("related_table_description"):
            rel_info["related_table_description"] = record["related_table_description"]
        if record.get("from_column_description"):
            rel_info["from_column_description"] = record["from_column_description"]
        if record.get("to_column_description"):
            rel_info["to_column_description"] = record["to_column_description"]
        relationships.append(rel_info)

    if len(relationships) < limit:
        reverse_query = """
        MATCH (t2:Table)-[:HAS_COLUMN]->(c2:Column)-[fk:FK_TO]->(c1:Column)<-[:HAS_COLUMN]-(t:Table {name: $table_name})
        RETURN DISTINCT t2.name AS related_table,
               t2.description AS related_table_description,
               'referenced_by' AS relation_type,
               c1.name AS from_column,
               c1.description AS from_column_description,
               c2.name AS to_column,
               c2.description AS to_column_description
        LIMIT $limit
        """

        reverse_result = await neo4j_session.run(
            reverse_query,
            table_name=table_name,
            limit=limit - len(relationships),
        )
        reverse_records = await reverse_result.data()

        for record in reverse_records:
            rel_info = {
                "related_table": record["related_table"],
                "relation_type": record["relation_type"],
                "from_column": record.get("from_column"),
                "to_column": record.get("to_column"),
            }
            if record.get("related_table_description"):
                rel_info["related_table_description"] = record["related_table_description"]
            if record.get("from_column_description"):
                rel_info["from_column_description"] = record["from_column_description"]
            if record.get("to_column_description"):
                rel_info["to_column_description"] = record["to_column_description"]
            relationships.append(rel_info)

    return relationships


async def get_column_fk_relationships(
    neo4j_session: AsyncSession,
    table_name: str,
    column_name: str,
    limit: int,
) -> List[Dict]:
    """특정 컬럼의 외래키 관계를 조회한다."""
    query = """
    MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c1:Column {name: $column_name})-[fk:FK_TO]->(c2:Column)<-[:HAS_COLUMN]-(t2:Table)
    RETURN t2.name AS referenced_table,
           t2.description AS referenced_table_description,
           c2.name AS referenced_column,
           c2.description AS referenced_column_description,
           fk.constraint AS constraint_name
    LIMIT $limit
    """

    result = await neo4j_session.run(
        query,
        table_name=table_name,
        column_name=column_name,
        limit=limit,
    )
    records = await result.data()

    fk_relationships: List[Dict] = []
    for record in records:
        fk_info: Dict = {
            "referenced_table": record["referenced_table"],
            "referenced_column": record["referenced_column"],
        }
        if record.get("referenced_table_description"):
            fk_info["referenced_table_description"] = record["referenced_table_description"]
        if record.get("referenced_column_description"):
            fk_info["referenced_column_description"] = record["referenced_column_description"]
        if record.get("constraint_name"):
            fk_info["constraint_name"] = record["constraint_name"]
        fk_relationships.append(fk_info)

    return fk_relationships

