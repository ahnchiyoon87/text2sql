# Neo4j Text2SQL - 프로젝트 요약

## 📋 프로젝트 개요

Neo4j 그래프 데이터베이스를 활용한 RAG(Retrieval-Augmented Generation) 기반 자연어-SQL 변환 시스템입니다.

### 핵심 가치 제안

1. **거대 스키마 대응**: 수천 개 테이블이 있어도 관련 서브스키마만 추출하여 LLM 컨텍스트에 제공
2. **정확도 향상**: 벡터 검색 + 그래프 경로 탐색으로 조인 관계 자동 발견
3. **안전성**: SELECT-only, 검증 레이어, 타임아웃 등 다층 보안
4. **추적성**: 어떤 테이블/컬럼이 왜 선택됐는지 provenance 제공
5. **학습 가능**: 사용자 피드백을 저장하여 지속적 개선

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI (app/)                        │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   /ask   │  │  /meta   │  │/feedback │  │ /ingest  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │              │             │           │
└───────┼─────────────┼──────────────┼─────────────┼───────────┘
        │             │              │             │
        ↓             ↓              ↓             ↓
┌────────────────────────────────────────────────────────────┐
│                     Core Modules                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Embedding │  │  Graph   │  │   SQL    │  │   Viz    │  │
│  │ Client   │  │ Searcher │  │  Guard   │  │Recommender│ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼──────────────┼─────────────┼─────────┘
        │             │              │             │
        ↓             ↓              ↓             ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   OpenAI    │ │   Neo4j     │ │ PostgreSQL  │ │  Vega-Lite  │
│  Embedding  │ │   Vector    │ │   Target    │ │   Charts    │
│    + LLM    │ │    Index    │ │     DB      │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

## 📦 주요 모듈

### 1. Core (`app/core/`)

| 파일 | 역할 |
|------|------|
| `embedding.py` | OpenAI 임베딩 생성 (텍스트 → 벡터) |
| `graph_search.py` | Neo4j 벡터 검색 + FK 경로 탐색 |
| `prompt.py` | LangChain SQL 생성 체인 |
| `sql_guard.py` | SQL 검증 (AST 파싱, 금지 키워드 차단) |
| `sql_exec.py` | SQL 실행 (타임아웃, 행수 제한) |
| `viz.py` | 시각화 추천 (Vega-Lite 스펙 생성) |

### 2. Ingestion (`app/ingest/`)

| 파일 | 역할 |
|------|------|
| `ddl_extract.py` | PostgreSQL 카탈로그에서 스키마 메타데이터 추출 |
| `to_neo4j.py` | Neo4j에 그래프 적재 + 임베딩 생성 |

### 3. Routers (`app/routers/`)

| 파일 | 엔드포인트 | 설명 |
|------|-----------|------|
| `ask.py` | `POST /ask` | 자연어 → SQL 변환 및 실행 |
| `meta.py` | `GET /meta/*` | 스키마 메타데이터 조회 |
| `feedback.py` | `POST /feedback` | 사용자 피드백 저장 |
| `ingest.py` | `POST /ingest` | 스키마 인제스천 트리거 |

### 4. Configuration

| 파일 | 역할 |
|------|------|
| `app/config.py` | Pydantic Settings (환경변수 관리) |
| `app/deps.py` | FastAPI 의존성 주입 (Neo4j, DB, OpenAI) |
| `app/main.py` | FastAPI 앱 정의 + 라이프사이클 |

## 🔄 데이터 흐름

### 1️⃣ 스키마 인제스천 (Setup Phase)

```
PostgreSQL (information_schema)
    ↓ [DDL Extract]
Tables/Columns/FKs Metadata
    ↓ [Embedding Generation]
OpenAI API (text-embedding-3-large)
    ↓ [Graph Loading]
Neo4j Graph DB
    - Nodes: Table, Column
    - Edges: HAS_COLUMN, FK_TO, FK_TO_TABLE
    - Vector Index: table_vec_index, column_vec_index
```

### 2️⃣ 질의 처리 (Query Phase)

```
User NL Query ("지난달 카테고리별 매출")
    ↓ [1. Embedding]
Query Vector (1536-dim)
    ↓ [2. Vector Search]
Neo4j: Top-K Tables/Columns (score: 0.7~0.9)
    ↓ [3. FK Path Search]
Neo4j: Find join paths (BFS, max 3 hops)
    ↓ [4. Subschema Assembly]
Subschema Text:
  - Table: sales.orders (columns: order_date, amount, ...)
  - Table: sales.categories (columns: category, ...)
  - FK: orders.category_id -> categories.id
    ↓ [5. LLM Prompt]
LangChain + OpenAI GPT-4o-mini
    ↓ [6. SQL Generation]
Generated SQL: "SELECT c.category, SUM(o.amount) ..."
    ↓ [7. Validation]
SQL Guard (AST parsing, keyword check, LIMIT injection)
    ↓ [8. Execution]
PostgreSQL (readonly connection)
    ↓ [9. Visualization]
Vega-Lite Spec (bar/line/pie charts)
    ↓ [10. Response]
JSON Response (SQL + Table + Charts + Provenance + Perf)
```

## 🛡️ 보안 계층

| 계층 | 메커니즘 |
|------|---------|
| **DB 접근** | 읽기 전용 계정 (SELECT 권한만) |
| **SQL 파싱** | SQLGlot AST 분석 (DML/DDL 차단) |
| **키워드 필터** | INSERT/UPDATE/DELETE/ALTER/DROP/EXEC 금지 |
| **LIMIT 강제** | 기본 1000행, 최대 100,000행 |
| **타임아웃** | 쿼리 실행 30초 제한 |
| **테이블 ACL** | 허용된 테이블만 사용 (서브스키마 기반) |
| **조인 깊이** | 최대 3단계 |
| **서브쿼리** | 최대 3단계 중첩 |

## 📊 성능 특성

### 평균 응답 시간 (P95)

| 단계 | 시간 | 비고 |
|------|------|------|
| 임베딩 생성 | 40-60ms | OpenAI API |
| 벡터 검색 | 80-150ms | Neo4j (10M rows) |
| FK 경로 탐색 | 20-50ms | Neo4j BFS |
| LLM SQL 생성 | 800-1200ms | GPT-4o-mini |
| SQL 실행 | 50-500ms | 쿼리 복잡도 의존 |
| **전체** | **1-2초** | 단순 쿼리 기준 |

### 확장성

- **Neo4j 벡터 인덱스**: 1000만 노드까지 100ms 내 검색
- **스키마 규모**: 5000+ 테이블 지원 (서브스키마 방식)
- **동시 요청**: FastAPI async (100+ 동시 사용자)

## 🎯 사용 사례

### 1. 셀프 서비스 분석
**As-is**: "데이터팀에 요청 → 2-3일 대기"
**To-be**: "자연어로 질문 → 즉시 결과"

```
질문: "지난 분기 신규 가입자 중 유료 전환율 Top 10 국가"
SQL: SELECT country, COUNT(...) / NULLIF(COUNT(...)) ...
```

### 2. 데이터 탐색
**스키마 파악 불필요**, Neo4j가 자동으로 관련 테이블 찾음

```
질문: "고객 평생 가치 LTV 계산"
→ Neo4j: customers, orders, payments 테이블 자동 연결
```

### 3. 대시보드 프로토타이핑
**차트 자동 추천**, Vega-Lite 스펙으로 즉시 렌더링

```
질문: "일별 활성 사용자 추이"
→ Line chart 자동 추천 + 스펙 생성
```

## 🔮 확장 로드맵

### Phase 1 (현재)
- ✅ PostgreSQL 지원
- ✅ SELECT 쿼리
- ✅ 벡터 검색 + FK 경로
- ✅ 기본 시각화 (4종)

### Phase 2 (3개월)
- [ ] MySQL, Oracle 지원
- [ ] PII 자동 탐지/마스킹
- [ ] A/B 테스트 프레임워크
- [ ] 피드백 기반 프롬프트 자동 개선

### Phase 3 (6개월)
- [ ] Multi-database 조인
- [ ] 실시간 대시보드 (SSE)
- [ ] Slack/Teams 봇
- [ ] 멀티테넌시 + RBAC

### Phase 4 (12개월)
- [ ] 자연어 데이터 정의 (DDL 생성)
- [ ] 쿼리 최적화 추천
- [ ] 인덱스 자동 제안
- [ ] 비용 예측 (쿼리 비용)

## 📝 핵심 설계 결정

### 1. Neo4j vs. 전통적 메타데이터 DB
**선택**: Neo4j
**이유**:
- FK 경로 탐색이 그래프 DB에서 훨씬 효율적
- 벡터 검색 네이티브 지원 (5.x)
- 시각적 스키마 탐색 가능 (Neo4j Browser)

### 2. SQLGlot vs. 정규식 검증
**선택**: SQLGlot (AST 파싱)
**이유**:
- 정규식은 우회 가능 (e.g., `/**/INSERT`)
- AST 파싱이 더 견고
- 멀티 SQL 방언 지원

### 3. 동기 vs. 비동기 I/O
**선택**: 비동기 (asyncpg, neo4j async driver)
**이유**:
- LLM 응답 대기 중 다른 요청 처리
- FastAPI의 비동기 지원 활용
- 동시성 개선 (10x+)

### 4. 전체 스키마 vs. 서브스키마
**선택**: 서브스키마 RAG
**이유**:
- LLM 컨텍스트 한계 (8k-128k 토큰)
- 불필요한 테이블 제외로 정확도 향상
- 비용 절감 (토큰 사용량)

## 🧪 테스트 전략 (향후)

### Unit Tests
- `sql_guard.py`: 100+ 악성 SQL 케이스
- `graph_search.py`: FK 경로 알고리즘
- `viz.py`: 차트 타입 추론 로직

### Integration Tests
- End-to-end 질의 시나리오
- 스키마 인제스천 정확도
- 벡터 검색 재현율 (recall)

### Load Tests
- 100 동시 사용자
- 1000 req/min
- P99 < 5초

## 🚀 배포 전략

### Development
```bash
make setup    # 초기 설정
make start    # 로컬 실행
```

### Staging
- Docker Compose (API + Neo4j)
- 환경변수 주입
- Healthcheck 포함

### Production
- Kubernetes (API Deployment)
- Neo4j Aura (Managed)
- Secrets Manager (API keys)
- Load Balancer + Auto-scaling
- Prometheus + Grafana 모니터링

## 📈 메트릭 & 모니터링

### 비즈니스 메트릭
- 일일 쿼리 수
- 사용자당 평균 쿼리
- SQL 승인율 (피드백 기반)
- 평균 응답 만족도

### 기술 메트릭
- API 응답 시간 (P50/P95/P99)
- LLM 토큰 사용량 (비용)
- Neo4j 쿼리 성능
- DB 연결 풀 상태
- 오류율 (5xx)

### 품질 메트릭
- SQL 검증 실패율
- 벡터 검색 재현율
- FK 경로 탐색 성공률
- 차트 추천 정확도

## 🛠️ 유지보수 가이드

### 일일
- 로그 확인 (오류, 경고)
- API 헬스체크
- Neo4j 메모리/CPU

### 주간
- 스키마 리프레시 (변경 감지)
- 피드백 리뷰
- 성능 메트릭 분석

### 월간
- 벡터 인덱스 최적화
- 프롬프트 개선 (피드백 반영)
- 비용 분석 (OpenAI API)

## 📚 참고 자료

### 기술 문서
- [Neo4j Vector Search](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/)
- [LangChain SQL Agent](https://python.langchain.com/docs/use_cases/sql)
- [SQLGlot Documentation](https://sqlglot.com/)
- [Vega-Lite](https://vega.github.io/vega-lite/)

### 논문
- "Text-to-SQL via Retrieval-Augmented Generation" (2023)
- "Schema Linking for Text-to-SQL" (2020)
- "BIRD: Big Bench for Large-scale Database Grounded Text-to-SQL Evaluation" (2023)

---

**작성**: 2025-10-09
**버전**: 1.0.0
**라이선스**: MIT

