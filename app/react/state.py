import base64
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class MetadataParseError(Exception):
    """LLM 이 반환한 metadata XML 파싱 실패"""


@dataclass
class ReactMetadata:
    identified_tables: List[Dict[str, Any]] = field(default_factory=list)
    identified_columns: List[Dict[str, Any]] = field(default_factory=list)
    identified_values: List[Dict[str, Any]] = field(default_factory=list)
    identified_relationships: List[Dict[str, Any]] = field(default_factory=list)
    identified_constraints: List[Dict[str, Any]] = field(default_factory=list)

    def update_from_xml(self, metadata_xml: str) -> None:
        if not metadata_xml.strip():
            return

        try:
            element = ET.fromstring(metadata_xml)
        except ET.ParseError as exc:
            raise MetadataParseError(f"Failed to parse metadata XML: {exc}") from exc

        self._extend_collection(element.find("identified_tables"), self.identified_tables, ["name", "purpose", "key_columns"])
        self._extend_collection(
            element.find("identified_columns"),
            self.identified_columns,
            ["table", "name", "data_type", "purpose"],
        )
        self._extend_collection(
            element.find("identified_values"),
            self.identified_values,
            ["table", "column", "actual_value", "user_term"],
        )
        self._extend_collection(
            element.find("identified_relationships"),
            self.identified_relationships,
            ["type", "condition", "tables"],
        )
        self._extend_collection(
            element.find("identified_constraints"),
            self.identified_constraints,
            ["type", "condition", "status"],
        )

    def to_xml(self) -> str:
        root = ET.Element("collected_metadata")

        self._append_collection(root, "identified_tables", "table", self.identified_tables)
        self._append_collection(root, "identified_columns", "column", self.identified_columns)
        self._append_collection(root, "identified_values", "value", self.identified_values)
        self._append_collection(root, "identified_relationships", "relationship", self.identified_relationships)
        self._append_collection(root, "identified_constraints", "constraint", self.identified_constraints)

        return ET.tostring(root, encoding="unicode")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identified_tables": self.identified_tables,
            "identified_columns": self.identified_columns,
            "identified_values": self.identified_values,
            "identified_relationships": self.identified_relationships,
            "identified_constraints": self.identified_constraints,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ReactMetadata":
        if not data:
            return cls()
        return cls(
            identified_tables=data.get("identified_tables", []),
            identified_columns=data.get("identified_columns", []),
            identified_values=data.get("identified_values", []),
            identified_relationships=data.get("identified_relationships", []),
            identified_constraints=data.get("identified_constraints", []),
        )

    @staticmethod
    def _extend_collection(
        parent: Optional[ET.Element],
        target: List[Dict[str, Any]],
        fields: List[str],
    ) -> None:
        if parent is None:
            return
        for child in list(parent):
            entry: Dict[str, Any] = {}
            for field_name in fields:
                entry[field_name] = (child.findtext(field_name) or "").strip()
            if any(entry.values()):
                target.append(entry)

    @staticmethod
    def _append_collection(
        root: ET.Element,
        collection_tag: str,
        item_tag: str,
        items: List[Dict[str, Any]],
    ) -> None:
        collection_el = ET.SubElement(root, collection_tag)
        for item in items:
            item_el = ET.SubElement(collection_el, item_tag)
            for key, value in item.items():
                child = ET.SubElement(item_el, key)
                child.text = str(value)


@dataclass
class ReactSessionState:
    user_query: str
    dbms: str
    remaining_tool_calls: int
    partial_sql: str
    current_tool_result: str
    metadata: ReactMetadata = field(default_factory=ReactMetadata)
    iteration: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_query": self.user_query,
            "dbms": self.dbms,
            "remaining_tool_calls": self.remaining_tool_calls,
            "partial_sql": self.partial_sql,
            "current_tool_result": self.current_tool_result,
            "metadata": self.metadata.to_dict(),
            "iteration": self.iteration,
        }

    def to_token(self) -> str:
        payload = json.dumps(self.to_dict(), ensure_ascii=False)
        return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")

    @classmethod
    def from_token(cls, token: str) -> "ReactSessionState":
        payload = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        data = json.loads(payload)
        metadata = ReactMetadata.from_dict(data.get("metadata"))
        return cls(
            user_query=data["user_query"],
            dbms=data["dbms"],
            remaining_tool_calls=data["remaining_tool_calls"],
            partial_sql=data["partial_sql"],
            current_tool_result=data.get("current_tool_result", "<tool_result/>"),
            metadata=metadata,
            iteration=data.get("iteration", 0),
        )

    @classmethod
    def new(
        cls,
        user_query: str,
        dbms: str,
        remaining_tool_calls: int,
        partial_sql: str = "SELECT PLACEHOLDER_COLUMNS FROM PLACEHOLDER_TABLE",
    ) -> "ReactSessionState":
        return cls(
            user_query=user_query,
            dbms=dbms,
            remaining_tool_calls=remaining_tool_calls,
            partial_sql=partial_sql,
            current_tool_result="<tool_result/>",
        )

