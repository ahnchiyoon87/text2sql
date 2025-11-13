from typing import List, Set

from app.core.embedding import EmbeddingClient
from app.core.graph_search import GraphSearcher
from app.react.tools.context import ToolContext
from app.react.tools.neo4j_utils import get_table_relationships


async def execute(
    context: ToolContext,
    keywords: List[str],
) -> str:
    """
    Neo4j 스키마 그래프에서 키워드와 유사한 테이블을 검색한다.
    결과는 prompt.xml 지시에 맞춰 XML 문자열로 반환한다.
    """
    table_top_k = context.scaled(context.table_top_k)
    relation_limit = context.scaled(context.table_relation_limit)

    embedding_client = EmbeddingClient(context.openai_client)
    query_embeddings = await embedding_client.embed_batch(keywords)
    searcher = GraphSearcher(context.neo4j_session)

    result_parts: List[str] = ["<tool_result>"]
    output_table_names: Set[str] = set()

    for keyword, embedding in zip(keywords, query_embeddings):
        matches = await searcher.search_tables(embedding, k=table_top_k)
        result_parts.append(f'<related_tables used_keyword="{keyword}">')

        for match in matches:
            if match.name in output_table_names:
                continue

            result_parts.append("<table>")
            result_parts.append(f"<name>{match.name}</name>")
            if match.description:
                result_parts.append(f"<description>{match.description}</description>")

            relationships = await get_table_relationships(
                context.neo4j_session,
                match.name,
                limit=relation_limit,
            )
            if relationships:
                result_parts.append("<relationships>")
                for rel in relationships:
                    result_parts.append("<relationship>")
                    result_parts.append(f"<related_table>{rel['related_table']}</related_table>")
                    if rel.get("related_table_description"):
                        result_parts.append(
                            f"<related_table_description>{rel['related_table_description']}</related_table_description>"
                        )
                    result_parts.append(f"<relation_type>{rel['relation_type']}</relation_type>")
                    if rel.get("from_column"):
                        result_parts.append(f"<from_column>{rel['from_column']}</from_column>")
                    if rel.get("from_column_description"):
                        result_parts.append(
                            f"<from_column_description>{rel['from_column_description']}</from_column_description>"
                        )
                    if rel.get("to_column"):
                        result_parts.append(f"<to_column>{rel['to_column']}</to_column>")
                    if rel.get("to_column_description"):
                        result_parts.append(
                            f"<to_column_description>{rel['to_column_description']}</to_column_description>"
                        )
                    result_parts.append("</relationship>")
                result_parts.append("</relationships>")

            result_parts.append("</table>")
            output_table_names.add(match.name)

        result_parts.append("</related_tables>")

    result_parts.append("</tool_result>")
    return "\n".join(result_parts)

