from typing import List, Set, Tuple

from app.core.sql_guard import SQLGuard
from app.react.tools.context import ToolContext


def _quote_identifier(identifier: str) -> str:
    """schema.table 혹은 table 형식을 적절히 이스케이프한다."""
    parts = [part for part in identifier.split(".") if part]
    if not parts:
        return '""'
    return ".".join(f'"{part}"' for part in parts)


async def execute(
    context: ToolContext,
    table_name: str,
    column_name: str,
    search_keywords: List[str],
) -> str:
    """특정 컬럼에서 키워드와 매칭되는 값을 조회한다."""
    value_limit = context.scaled(context.value_limit)
    sanitized_table = SQLGuard.sanitize_identifier(table_name)
    sanitized_column = SQLGuard.sanitize_identifier(column_name)

    result_parts: List[str] = [
        "<tool_result>",
        f"<target_table>{sanitized_table}</target_table>",
        f"<target_column>{sanitized_column}</target_column>",
    ]

    seen_rows: Set[Tuple] = set()

    qualified_table = _quote_identifier(sanitized_table)
    qualified_column = _quote_identifier(sanitized_column)

    try:
        default_sql = f"SELECT * FROM {qualified_table} LIMIT {value_limit}"
        default_rows = await context.db_conn.fetch(default_sql)

        result_parts.append('<rows type="default">')
        for row in default_rows:
            row_tuple = tuple(row.values())
            if row_tuple in seen_rows:
                continue
            seen_rows.add(row_tuple)
            result_parts.append("<row>")
            for col_name, col_value in row.items():
                if col_value is None:
                    continue
                value_str = str(col_value).strip()
                if not value_str:
                    continue
                result_parts.append(f"<{col_name}>{value_str}</{col_name}>")
            result_parts.append("</row>")
        result_parts.append("</rows>")
    except Exception as exc:
        result_parts.append(f'<rows type="default"><error>{str(exc)}</error></rows>')

    for keyword in search_keywords:
        try:
            query_sql = (
                f"SELECT * FROM {qualified_table} "
                f"WHERE {qualified_column}::text ILIKE $1 LIMIT {value_limit}"
            )
            query_rows = await context.db_conn.fetch(query_sql, f"%{keyword}%")

            result_parts.append(f'<rows type="query" used_keyword="{keyword}">')
            for row in query_rows:
                row_tuple = tuple(row.values())
                if row_tuple in seen_rows:
                    continue
                seen_rows.add(row_tuple)
                result_parts.append("<row>")
                for col_name, col_value in row.items():
                    if col_value is None:
                        continue
                    value_str = str(col_value).strip()
                    if not value_str:
                        continue
                    result_parts.append(f"<{col_name}>{value_str}</{col_name}>")
                result_parts.append("</row>")
            result_parts.append("</rows>")
        except Exception as exc:
            result_parts.append(
                f'<rows type="query" used_keyword="{keyword}"><error>{str(exc)}</error></rows>'
            )

    result_parts.append("</tool_result>")
    return "\n".join(result_parts)

