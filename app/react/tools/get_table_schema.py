from typing import List

from app.react.tools.context import ToolContext
from app.react.tools.neo4j_utils import get_column_fk_relationships


async def execute(
    context: ToolContext,
    table_names: List[str],
) -> str:
    """Neo4j 에 저장된 테이블 스키마 정보를 조회한다."""
    column_relation_limit = context.scaled(context.column_relation_limit)

    query = """
    MATCH (t:Table)
    WHERE t.name IN $table_names
    OPTIONAL MATCH (t)-[:HAS_COLUMN]->(c:Column)
    WITH t, c
    ORDER BY c.name
    RETURN t.name AS table_name,
           t.schema AS table_schema,
           t.description AS table_description,
           collect({
               name: c.name,
               dtype: c.dtype,
               nullable: c.nullable,
               description: c.description,
               is_pk: c.is_pk
           }) AS columns
    """

    result = await context.neo4j_session.run(query, table_names=table_names)
    records = await result.data()

    result_parts: List[str] = ["<tool_result>"]

    for record in records:
        table_name = record["table_name"]
        table_schema = record.get("table_schema", "")
        table_description = record.get("table_description", "")
        columns = record["columns"]

        result_parts.append("<table>")
        result_parts.append(f"<name>{table_name}</name>")
        if table_description:
            result_parts.append(f"<description>{table_description}</description>")

        result_parts.append("<columns>")
        for col in columns:
            if not col["name"]:
                continue

            col_name = col["name"]
            col_dtype = col.get("dtype", "")
            col_nullable = str(col.get("nullable", True)).lower()
            col_description = col.get("description", "")
            is_pk = str(col.get("is_pk", False)).lower()

            if table_schema:
                fqn = f"{table_schema}.{table_name}.{col_name}"
            else:
                fqn = f"{table_name}.{col_name}"

            result_parts.append("<column>")
            result_parts.append(f"<fqn>{fqn}</fqn>")
            result_parts.append(f"<name>{col_name}</name>")
            if col_dtype:
                result_parts.append(f"<dtype>{col_dtype}</dtype>")
            result_parts.append(f"<nullable>{col_nullable}</nullable>")
            result_parts.append(f"<is_primary_key>{is_pk}</is_primary_key>")
            if col_description:
                result_parts.append(f"<description>{col_description}</description>")

            fk_relationships = await get_column_fk_relationships(
                context.neo4j_session,
                table_name,
                col_name,
                limit=column_relation_limit,
            )
            if fk_relationships:
                result_parts.append("<foreign_keys>")
                for fk in fk_relationships:
                    result_parts.append("<foreign_key>")
                    result_parts.append(f"<referenced_table>{fk['referenced_table']}</referenced_table>")
                    if fk.get("referenced_table_description"):
                        result_parts.append(
                            f"<referenced_table_description>{fk['referenced_table_description']}</referenced_table_description>"
                        )
                    result_parts.append(f"<referenced_column>{fk['referenced_column']}</referenced_column>")
                    if fk.get("referenced_column_description"):
                        result_parts.append(
                            f"<referenced_column_description>{fk['referenced_column_description']}</referenced_column_description>"
                        )
                    if fk.get("constraint_name"):
                        result_parts.append(f"<constraint_name>{fk['constraint_name']}</constraint_name>")
                    result_parts.append("</foreign_key>")
                result_parts.append("</foreign_keys>")

            result_parts.append("</column>")
        result_parts.append("</columns>")
        result_parts.append("</table>")

    result_parts.append("</tool_result>")
    return "\n".join(result_parts)

