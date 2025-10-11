# 🚀 Quick Start Guide

## 전제 조건

1. Docker 설치 확인
2. OpenAI API Key 준비
3. PostgreSQL 데이터베이스 (읽기 전용 계정)

## 1단계: 환경 설정

```bash
# 1. 환경 변수 파일 생성
cp .env.template .env

# 2. .env 파일 편집 (필수 항목)
# - OPENAI_API_KEY
# - TARGET_DB_HOST, TARGET_DB_NAME, TARGET_DB_USER, TARGET_DB_PASSWORD
```

## 2단계: Neo4j 시작

```bash
# Docker Compose로 Neo4j 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f neo4j

# Neo4j가 준비되면 (약 30초 소요)
# http://localhost:7474 에서 브라우저 확인 가능
# 로그인: neo4j / password123
```

## 3단계: Neo4j 스키마 초기화

```bash
# 벡터 인덱스 및 제약 조건 생성
uv run python scripts/init_schema.py
```

**출력 예시:**
```
[1/6] Executing: CREATE CONSTRAINT table_key IF NOT EXISTS...
  ✓ Success
[2/6] Executing: CREATE CONSTRAINT column_fqn IF NOT EXISTS...
  ✓ Success
...
✅ Schema initialization completed!
```

## 4단계: API 서버 시작

```bash
# 개발 모드로 실행
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**출력 예시:**
```
🚀 Starting Neo4j Text2SQL API...
✓ Connected to Neo4j at bolt://localhost:7687
✓ Target database: postgresql://localhost:5432/mydb
✓ Using LLM: gpt-4o-mini
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 5단계: 스키마 인제스천

브라우저에서 http://localhost:8000/docs 열기

또는 curl로:

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "db_name": "postgres",
    "schema": "public",
    "clear_existing": true
  }'
```

**예상 소요 시간:**
- 작은 스키마 (10-50 테이블): 1-3분
- 중간 스키마 (50-200 테이블): 5-10분
- 대형 스키마 (200+ 테이블): 10-30분

**성공 응답:**
```json
{
  "message": "Schema ingestion completed successfully",
  "status": "success",
  "tables_loaded": 45,
  "columns_loaded": 312,
  "fks_loaded": 28
}
```

## 6단계: 첫 질문하기!

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "사용자 테이블에서 최근 10명의 사용자를 보여줘",
    "limit": 10
  }' | jq .
```

또는 Swagger UI에서: http://localhost:8000/docs#/Query/ask_question_ask_post

## 🎯 테스트 쿼리 예시

### 간단한 조회
```json
{
  "question": "모든 고객 목록 보여줘",
  "limit": 20
}
```

### 집계 쿼리
```json
{
  "question": "카테고리별 주문 건수와 총 금액",
  "limit": 100
}
```

### 시간 범위 쿼리
```json
{
  "question": "지난 30일간 일별 매출 추이",
  "limit": 30
}
```

### 조인 쿼리
```json
{
  "question": "주문 금액이 가장 높은 고객 Top 10",
  "limit": 10
}
```

## 🔍 메타데이터 탐색

```bash
# 테이블 목록
curl "http://localhost:8000/meta/tables?limit=10" | jq .

# 테이블 검색
curl "http://localhost:8000/meta/tables?search=user" | jq .

# 특정 테이블의 컬럼
curl "http://localhost:8000/meta/tables/users/columns?schema=public" | jq .

# 컬럼 검색
curl "http://localhost:8000/meta/columns?search=email" | jq .
```

## 📊 응답 구조 이해하기

```json
{
  "sql": "생성된 SQL 쿼리",
  "table": {
    "columns": ["col1", "col2"],
    "rows": [[val1, val2], ...],
    "row_count": 10,
    "execution_time_ms": 45.2
  },
  "charts": [
    {
      "title": "차트 제목",
      "type": "bar",
      "description": "설명",
      "vega_lite": { /* Vega-Lite 스펙 */ }
    }
  ],
  "provenance": {
    "tables": ["사용된 테이블 목록"],
    "columns": ["사용된 컬럼 목록"],
    "neo4j_paths": ["조인 경로"],
    "vector_matches": [
      {"node": "Table:orders", "score": 0.82}
    ],
    "prompt_snapshot_id": "ps_..."
  },
  "perf": {
    "embedding_ms": 45,
    "graph_search_ms": 120,
    "llm_ms": 850,
    "sql_ms": 230,
    "total_ms": 1245
  }
}
```

## 🛠️ 트러블슈팅

### Neo4j 연결 실패
```bash
# Neo4j 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs neo4j

# 재시작
docker-compose restart neo4j
```

### API 서버 오류
```bash
# .env 파일 확인
cat .env

# 의존성 재설치
uv sync

# 로그 레벨 올려서 실행
uv run uvicorn app.main:app --log-level debug
```

### 스키마 인제스천 실패
- 대상 DB 연결 정보 확인
- 읽기 권한 확인
- OpenAI API Key 유효성 확인
- Neo4j 용량 확인 (docker stats)

### "No relevant tables found" 에러
- 스키마 인제스천이 완료되었는지 확인
- Neo4j 브라우저에서 데이터 확인: `MATCH (t:Table) RETURN count(t)`
- 질문을 더 구체적으로 작성

## 🔄 데이터 리프레시

```bash
# 스키마 재인제스천 (기존 데이터 삭제 후)
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "db_name": "postgres",
    "schema": "public",
    "clear_existing": true
  }'
```

## 📈 성능 팁

1. **임베딩 캐싱**: 동일 스키마는 재인제스천 불필요
2. **벡터 검색 튜닝**: `VECTOR_TOP_K` 값 조정 (기본 10)
3. **쿼리 복잡도 제한**: 조인이 많은 쿼리는 분할
4. **결과 행 제한**: `limit` 파라미터 적절히 설정

## 🎓 다음 단계

1. **피드백 제공**: 생성된 SQL 개선을 위해 피드백 제출
2. **커스터마이징**: `app/core/prompt.py`에서 프롬프트 조정
3. **시각화 확장**: Vega-Lite 스펙을 프론트엔드에서 렌더링
4. **모니터링**: 프로덕션 환경에서 성능 메트릭 추적

## 📚 추가 리소스

- API 문서: http://localhost:8000/docs
- Neo4j 브라우저: http://localhost:7474
- Vega-Lite 문서: https://vega.github.io/vega-lite/
- Neo4j 벡터 인덱스: https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/

---

문제가 있으신가요? GitHub Issues에 올려주세요! 🙋‍♂️

