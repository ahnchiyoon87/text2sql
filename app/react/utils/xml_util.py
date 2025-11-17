import re
from typing import Pattern


class XmlUtil:
    """XML 관련 유틸리티 함수 모음."""

    _CDATA_PATTERN: Pattern[str] = re.compile(r"<!\[CDATA\[.*?\]\]>", re.DOTALL)
    _AMP_PATTERN: Pattern[str] = re.compile(
        r"&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z0-9_]+;)"
    )

    @staticmethod
    def sanitize_xml_text(xml_text: str) -> str:
        """
        Escape bare ampersands outside CDATA sections to avoid XML parsing failures.
        """
        if "&" not in xml_text:
            return xml_text

        sanitized_parts = []
        last_idx = 0

        for match in XmlUtil._CDATA_PATTERN.finditer(xml_text):
            unsafe_chunk = xml_text[last_idx:match.start()]
            sanitized_parts.append(XmlUtil._AMP_PATTERN.sub("&amp;", unsafe_chunk))
            sanitized_parts.append(match.group(0))
            last_idx = match.end()

        tail = xml_text[last_idx:]
        sanitized_parts.append(XmlUtil._AMP_PATTERN.sub("&amp;", tail))

        return "".join(sanitized_parts)

