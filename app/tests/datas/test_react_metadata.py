# python -m pytest app/tests/datas/test_react_metadata.py -v

import pytest
import xml.etree.ElementTree as ET
from app.react.state import ReactMetadata, MetadataParseError


class TestReactMetadataInitialization:
    """ReactMetadata 초기화 테스트"""

    def test_default_initialization(self):
        """기본 초기화 시 모든 필드가 빈 리스트여야 함"""
        metadata = ReactMetadata()
        
        assert metadata.identified_tables == []
        assert metadata.identified_columns == []
        assert metadata.identified_values == []
        assert metadata.identified_relationships == []
        assert metadata.identified_constraints == []

    def test_initialization_with_data(self):
        """데이터를 포함한 초기화"""
        tables = [{"name": "users", "purpose": "store users", "key_columns": "id"}]
        columns = [{"table": "users", "name": "email", "data_type": "varchar", "purpose": "user email"}]
        
        metadata = ReactMetadata(
            identified_tables=tables,
            identified_columns=columns,
        )
        
        assert metadata.identified_tables == tables
        assert metadata.identified_columns == columns
        assert metadata.identified_values == []


class TestReactMetadataUpdateFromXml:
    """update_from_xml 메서드 테스트"""

    def test_update_from_empty_xml(self):
        """빈 XML 문자열 처리"""
        metadata = ReactMetadata()
        metadata.update_from_xml("")
        
        assert metadata.identified_tables == []

    def test_update_from_xml_with_tables(self):
        """테이블 정보가 포함된 XML 파싱"""
        xml_str = """
        <metadata>
            <identified_tables>
                <table>
                    <name>users</name>
                    <purpose>사용자 정보 저장</purpose>
                    <key_columns>user_id</key_columns>
                </table>
                <table>
                    <name>orders</name>
                    <purpose>주문 정보 저장</purpose>
                    <key_columns>order_id</key_columns>
                </table>
            </identified_tables>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str)
        
        assert len(metadata.identified_tables) == 2
        assert metadata.identified_tables[0]["name"] == "users"
        assert metadata.identified_tables[0]["purpose"] == "사용자 정보 저장"
        assert metadata.identified_tables[1]["name"] == "orders"

    def test_update_from_xml_with_columns(self):
        """컬럼 정보가 포함된 XML 파싱"""
        xml_str = """
        <metadata>
            <identified_columns>
                <column>
                    <table>users</table>
                    <name>email</name>
                    <data_type>VARCHAR(255)</data_type>
                    <purpose>사용자 이메일</purpose>
                </column>
            </identified_columns>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str)
        
        assert len(metadata.identified_columns) == 1
        assert metadata.identified_columns[0]["table"] == "users"
        assert metadata.identified_columns[0]["name"] == "email"
        assert metadata.identified_columns[0]["data_type"] == "VARCHAR(255)"

    def test_update_from_xml_with_values(self):
        """값 정보가 포함된 XML 파싱"""
        xml_str = """
        <metadata>
            <identified_values>
                <value>
                    <table>products</table>
                    <column>status</column>
                    <actual_value>active</actual_value>
                    <user_term>활성</user_term>
                </value>
            </identified_values>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str)
        
        assert len(metadata.identified_values) == 1
        assert metadata.identified_values[0]["table"] == "products"
        assert metadata.identified_values[0]["actual_value"] == "active"
        assert metadata.identified_values[0]["user_term"] == "활성"

    def test_update_from_xml_with_relationships(self):
        """관계 정보가 포함된 XML 파싱"""
        xml_str = """
        <metadata>
            <identified_relationships>
                <relationship>
                    <type>foreign_key</type>
                    <condition>orders.user_id = users.id</condition>
                    <tables>orders, users</tables>
                </relationship>
            </identified_relationships>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str)
        
        assert len(metadata.identified_relationships) == 1
        assert metadata.identified_relationships[0]["type"] == "foreign_key"
        assert metadata.identified_relationships[0]["condition"] == "orders.user_id = users.id"

    def test_update_from_xml_with_constraints(self):
        """제약 조건이 포함된 XML 파싱"""
        xml_str = """
        <metadata>
            <identified_constraints>
                <constraint>
                    <type>date_range</type>
                    <condition>date >= '2024-01-01'</condition>
                    <status>required</status>
                </constraint>
            </identified_constraints>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str)
        
        assert len(metadata.identified_constraints) == 1
        assert metadata.identified_constraints[0]["type"] == "date_range"
        assert metadata.identified_constraints[0]["status"] == "required"

    def test_update_from_xml_multiple_calls_accumulate(self):
        """여러 번 호출 시 데이터가 누적되어야 함"""
        xml_str1 = """
        <metadata>
            <identified_tables>
                <table>
                    <name>table1</name>
                    <purpose>purpose1</purpose>
                    <key_columns>id</key_columns>
                </table>
            </identified_tables>
        </metadata>
        """
        
        xml_str2 = """
        <metadata>
            <identified_tables>
                <table>
                    <name>table2</name>
                    <purpose>purpose2</purpose>
                    <key_columns>id</key_columns>
                </table>
            </identified_tables>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str1)
        metadata.update_from_xml(xml_str2)
        
        assert len(metadata.identified_tables) == 2
        assert metadata.identified_tables[0]["name"] == "table1"
        assert metadata.identified_tables[1]["name"] == "table2"

    def test_update_from_xml_skips_empty_entries(self):
        """빈 엔트리는 건너뛰어야 함"""
        xml_str = """
        <metadata>
            <identified_tables>
                <table>
                    <name></name>
                    <purpose></purpose>
                    <key_columns></key_columns>
                </table>
                <table>
                    <name>users</name>
                    <purpose>store users</purpose>
                    <key_columns>id</key_columns>
                </table>
            </identified_tables>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str)
        
        # 모든 필드가 비어있는 첫 번째 엔트리는 건너뛰고, 두 번째만 추가
        assert len(metadata.identified_tables) == 1
        assert metadata.identified_tables[0]["name"] == "users"

    def test_update_from_xml_handles_whitespace(self):
        """공백 문자 처리"""
        xml_str = """
        <metadata>
            <identified_tables>
                <table>
                    <name>  users  </name>
                    <purpose>  store users  </purpose>
                    <key_columns>  id  </key_columns>
                </table>
            </identified_tables>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str)
        
        # strip() 처리가 되어야 함
        assert metadata.identified_tables[0]["name"] == "users"
        assert metadata.identified_tables[0]["purpose"] == "store users"
        assert metadata.identified_tables[0]["key_columns"] == "id"

    def test_update_from_invalid_xml_raises_error(self):
        """잘못된 XML은 MetadataParseError를 발생시켜야 함"""
        invalid_xml = "<metadata><unclosed_tag>"
        
        metadata = ReactMetadata()
        with pytest.raises(MetadataParseError) as exc_info:
            metadata.update_from_xml(invalid_xml)
        
        assert "Failed to parse metadata XML" in str(exc_info.value)

    def test_update_from_xml_with_missing_fields(self):
        """일부 필드가 누락된 경우 처리"""
        xml_str = """
        <metadata>
            <identified_tables>
                <table>
                    <name>users</name>
                    <purpose></purpose>
                </table>
            </identified_tables>
        </metadata>
        """
        
        metadata = ReactMetadata()
        metadata.update_from_xml(xml_str)
        
        assert len(metadata.identified_tables) == 1
        assert metadata.identified_tables[0]["name"] == "users"
        assert metadata.identified_tables[0]["purpose"] == ""
        assert metadata.identified_tables[0]["key_columns"] == ""


class TestReactMetadataToXml:
    """to_xml 메서드 테스트"""

    def test_to_xml_empty_metadata(self):
        """빈 메타데이터를 XML로 변환"""
        metadata = ReactMetadata()
        xml_str = metadata.to_xml()
        
        root = ET.fromstring(xml_str)
        assert root.tag == "collected_metadata"
        assert len(list(root.find("identified_tables"))) == 0
        assert len(list(root.find("identified_columns"))) == 0

    def test_to_xml_with_tables(self):
        """테이블 정보를 XML로 변환"""
        metadata = ReactMetadata(
            identified_tables=[
                {"name": "users", "purpose": "사용자 저장", "key_columns": "id"}
            ]
        )
        xml_str = metadata.to_xml()
        
        root = ET.fromstring(xml_str)
        tables = root.find("identified_tables")
        table = tables.find("table")
        
        assert table.findtext("name") == "users"
        assert table.findtext("purpose") == "사용자 저장"
        assert table.findtext("key_columns") == "id"

    def test_to_xml_with_all_fields(self):
        """모든 필드가 포함된 XML 생성"""
        metadata = ReactMetadata(
            identified_tables=[{"name": "users", "purpose": "test", "key_columns": "id"}],
            identified_columns=[{"table": "users", "name": "email", "data_type": "varchar", "purpose": "email"}],
            identified_values=[{"table": "users", "column": "status", "actual_value": "active", "user_term": "활성"}],
            identified_relationships=[{"type": "fk", "condition": "a=b", "tables": "t1,t2"}],
            identified_constraints=[{"type": "date", "condition": "d>1", "status": "req"}],
        )
        xml_str = metadata.to_xml()
        
        root = ET.fromstring(xml_str)
        assert len(list(root.find("identified_tables"))) == 1
        assert len(list(root.find("identified_columns"))) == 1
        assert len(list(root.find("identified_values"))) == 1
        assert len(list(root.find("identified_relationships"))) == 1
        assert len(list(root.find("identified_constraints"))) == 1


class TestReactMetadataDictConversion:
    """to_dict / from_dict 메서드 테스트"""

    def test_to_dict_empty(self):
        """빈 메타데이터를 딕셔너리로 변환"""
        metadata = ReactMetadata()
        data = metadata.to_dict()
        
        assert data["identified_tables"] == []
        assert data["identified_columns"] == []
        assert data["identified_values"] == []
        assert data["identified_relationships"] == []
        assert data["identified_constraints"] == []

    def test_to_dict_with_data(self):
        """데이터가 있는 메타데이터를 딕셔너리로 변환"""
        tables = [{"name": "users", "purpose": "test", "key_columns": "id"}]
        metadata = ReactMetadata(identified_tables=tables)
        data = metadata.to_dict()
        
        assert data["identified_tables"] == tables

    def test_from_dict_none(self):
        """None에서 생성"""
        metadata = ReactMetadata.from_dict(None)
        
        assert metadata.identified_tables == []

    def test_from_dict_empty(self):
        """빈 딕셔너리에서 생성"""
        metadata = ReactMetadata.from_dict({})
        
        assert metadata.identified_tables == []

    def test_from_dict_with_data(self):
        """데이터가 있는 딕셔너리에서 생성"""
        data = {
            "identified_tables": [{"name": "users", "purpose": "test", "key_columns": "id"}],
            "identified_columns": [{"table": "users", "name": "email", "data_type": "varchar", "purpose": "test"}],
        }
        metadata = ReactMetadata.from_dict(data)
        
        assert len(metadata.identified_tables) == 1
        assert metadata.identified_tables[0]["name"] == "users"
        assert len(metadata.identified_columns) == 1

    def test_round_trip_to_dict_from_dict(self):
        """to_dict -> from_dict 왕복 변환"""
        original = ReactMetadata(
            identified_tables=[{"name": "users", "purpose": "사용자", "key_columns": "id"}],
            identified_values=[{"table": "products", "column": "status", "actual_value": "active", "user_term": "활성"}],
        )
        
        data = original.to_dict()
        restored = ReactMetadata.from_dict(data)
        
        assert restored.identified_tables == original.identified_tables
        assert restored.identified_values == original.identified_values
        assert restored.identified_columns == original.identified_columns


class TestReactMetadataComplexScenarios:
    """복잡한 시나리오 테스트"""

    def test_xml_round_trip(self):
        """XML 생성 후 파싱하여 데이터 복원"""
        original = ReactMetadata(
            identified_tables=[
                {"name": "users", "purpose": "사용자 정보", "key_columns": "user_id"},
                {"name": "orders", "purpose": "주문 정보", "key_columns": "order_id"},
            ],
            identified_columns=[
                {"table": "users", "name": "email", "data_type": "VARCHAR", "purpose": "이메일"},
            ],
        )
        
        # to_xml 생성
        xml_str = original.to_xml()
        
        # 새로운 인스턴스에서 파싱
        restored = ReactMetadata()
        restored.update_from_xml(xml_str)
        
        assert len(restored.identified_tables) == 2
        assert restored.identified_tables[0]["name"] == "users"
        assert restored.identified_tables[1]["name"] == "orders"
        assert len(restored.identified_columns) == 1

    def test_multiple_xml_updates_with_different_types(self):
        """다양한 타입의 XML을 여러 번 업데이트"""
        metadata = ReactMetadata()
        
        # 첫 번째 업데이트: 테이블
        metadata.update_from_xml("""
        <metadata>
            <identified_tables>
                <table>
                    <name>users</name>
                    <purpose>test</purpose>
                    <key_columns>id</key_columns>
                </table>
            </identified_tables>
        </metadata>
        """)
        
        # 두 번째 업데이트: 컬럼
        metadata.update_from_xml("""
        <metadata>
            <identified_columns>
                <column>
                    <table>users</table>
                    <name>email</name>
                    <data_type>varchar</data_type>
                    <purpose>email</purpose>
                </column>
            </identified_columns>
        </metadata>
        """)
        
        # 세 번째 업데이트: 값
        metadata.update_from_xml("""
        <metadata>
            <identified_values>
                <value>
                    <table>users</table>
                    <column>status</column>
                    <actual_value>active</actual_value>
                    <user_term>활성</user_term>
                </value>
            </identified_values>
        </metadata>
        """)
        
        assert len(metadata.identified_tables) == 1
        assert len(metadata.identified_columns) == 1
        assert len(metadata.identified_values) == 1

    def test_full_workflow(self):
        """전체 워크플로우 테스트: 생성 -> 업데이트 -> 변환 -> 복원"""
        # 1. 초기 생성
        metadata = ReactMetadata()
        
        # 2. XML 업데이트
        metadata.update_from_xml("""
        <metadata>
            <identified_tables>
                <table>
                    <name>products</name>
                    <purpose>상품 정보</purpose>
                    <key_columns>product_id</key_columns>
                </table>
            </identified_tables>
        </metadata>
        """)
        
        # 3. 딕셔너리로 변환
        data = metadata.to_dict()
        
        # 4. 딕셔너리에서 복원
        restored = ReactMetadata.from_dict(data)
        
        # 5. XML로 변환
        xml_str = restored.to_xml()
        root = ET.fromstring(xml_str)
        
        # 6. 검증
        tables = root.find("identified_tables")
        table = tables.find("table")
        assert table.findtext("name") == "products"
        assert table.findtext("purpose") == "상품 정보"

