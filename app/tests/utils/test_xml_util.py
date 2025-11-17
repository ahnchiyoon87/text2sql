# python -m pytest app/tests/utils/test_xml_util.py -v

from app.react.utils.xml_util import XmlUtil


def test_sanitize_xml_text_escapes_bare_ampersands() -> None:
    raw = "price > 100 & status = 'active'"
    sanitized = XmlUtil.sanitize_xml_text(raw)

    assert sanitized == "price > 100 &amp; status = 'active'"


def test_sanitize_xml_text_preserves_cdata_sections() -> None:
    raw = "<![CDATA[price & cost]]> and summary & details"
    sanitized = XmlUtil.sanitize_xml_text(raw)

    assert sanitized == "<![CDATA[price & cost]]> and summary &amp; details"


def test_sanitize_xml_text_keeps_existing_entities() -> None:
    raw = "bread &amp; butter & sugar &#169;"
    sanitized = XmlUtil.sanitize_xml_text(raw)

    assert sanitized == "bread &amp; butter &amp; sugar &#169;"

