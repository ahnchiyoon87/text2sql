# 🧪 테스트 가이드

Docker Compose로 PostgreSQL + Neo4j를 함께 실행하여 전체 시스템을 테스트하는 가이드입니다.

## 📋 사전 준비

1. **Docker Desktop 실행** 확인
2. **OpenAI API Key** 준비

## 🚀 Step 1: 환경 설정

```bash
# 테스트 환경 변수 파일 복사
cp .env.test .env

# .env 파일을 열어서 OPENAI_API_KEY 수정
nano .env  # 또는 vi, code 등 사용
```

**필수 수정 사항:**
- `OPENAI_API_KEY=your-openai-api-key-here` ← 실제 키로 변경

## 🐳 Step 2: Docker Compose 시작

```bash
# 모든 서비스 시작 (Neo4j + PostgreSQL)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 상태 확인
docker ps
```

**예상 출력:**
```
CONTAINER ID   IMAGE                    STATUS         PORTS
xxx            neo4j:5.23-community     Up 30 seconds  0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
yyy            postgres:16-alpine       Up 30 seconds  0.0.0.0:5432->5432/tcp
```

## 🔍 Step 3: 데이터베이스 확인

### PostgreSQL 접속 테스트

```bash
# PostgreSQL 컨테이너에 접속
docker exec -it postgres_text2sql psql -U testuser -d testdb

# 테이블 확인
\dt

# 샘플 쿼리
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;

# 종료
\q
```

**예상 결과:**
- customers: 30 rows
- products: 50 rows
- orders: 30 rows
- order_items: ~70 rows
- categories: 8 rows

### Neo4j 브라우저 확인

1. 브라우저에서 http://localhost:7474 접속
2. 로그인:
   - Username: `neo4j`
   - Password: `password123`
3. 연결 확인

## 📊 Step 4: Neo4j 스키마 초기화

```bash
# Neo4j에 벡터 인덱스 및 제약 조건 생성
uv run python scripts/init_schema.py
```

**예상 출력:**
```
[1/6] Executing: CREATE CONSTRAINT table_key IF NOT EXISTS...
  ✓ Success
[2/6] Executing: CREATE CONSTRAINT column_fqn IF NOT EXISTS...
  ✓ Success
...
✅ Schema initialization completed!
```

## 🎯 Step 5: API 서버 시작

```bash
# 새 터미널에서 API 서버 실행
uv run python main.py
```

**예상 출력:**
```
🚀 Starting Neo4j Text2SQL API...
✓ Connected to Neo4j at bolt://localhost:7687
✓ Target database: postgresql://localhost:5432/testdb
✓ Using LLM: gpt-4o-mini
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 📥 Step 6: 스키마 인제스천

새 터미널을 열고:

```bash
# PostgreSQL 스키마를 Neo4j로 인제스천
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "db_name": "testdb",
    "schema": "public",
    "clear_existing": true
  }' | jq .
```

**예상 소요 시간:** 2-5분 (임베딩 생성 포함)

**성공 응답:**
```json
{
  "message": "Schema ingestion completed successfully",
  "status": "success",
  "tables_loaded": 7,
  "columns_loaded": 50,
  "fks_loaded": 6
}
```

## 💬 Step 7: 자연어 질의 테스트

### 테스트 1: 간단한 조회

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "고객 목록 10명만 보여줘",
    "limit": 10
  }' | jq .
```

### 테스트 2: 집계 쿼리

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "카테고리별 주문 금액 합계",
    "limit": 100
  }' | jq .
```

### 테스트 3: 조인 쿼리

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "가장 많이 구매한 고객 Top 5",
    "limit": 5
  }' | jq .
```

### 테스트 4: 시간 범위 쿼리

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "최근 30일간 일별 주문 건수",
    "limit": 30
  }' | jq .
```

### 테스트 5: 복잡한 분석

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "프리미엄 회원과 일반 회원의 평균 주문 금액 비교",
    "limit": 100
  }' | jq .
```

## 🎨 Step 8: Swagger UI에서 테스트

1. 브라우저에서 http://localhost:8000/docs 열기
2. `/ask` 엔드포인트 클릭
3. "Try it out" 클릭
4. Request body 입력:

```json
{
  "question": "Electronics 카테고리에서 가장 인기있는 상품 5개",
  "limit": 5
}
```

5. "Execute" 클릭

## 📊 응답 구조 확인

성공적인 응답은 다음을 포함합니다:

```json
{
  "sql": "SELECT p.name, COUNT(oi.id) AS order_count ...",
  "table": {
    "columns": ["name", "order_count"],
    "rows": [["Laptop Pro 15", 3], ...],
    "row_count": 5
  },
  "charts": [
    {
      "title": "상품별 주문 건수",
      "type": "bar",
      "vega_lite": { /* Vega-Lite spec */ }
    }
  ],
  "provenance": {
    "tables": ["public.products", "public.order_items"],
    "columns": ["products.name", "order_items.id"],
    "neo4j_paths": ["order_items -> products"],
    "vector_matches": [
      {"node": "Table:products", "score": 0.85}
    ]
  },
  "perf": {
    "embedding_ms": 42,
    "graph_search_ms": 95,
    "llm_ms": 920,
    "sql_ms": 18,
    "total_ms": 1075
  }
}
```

## 🔎 Neo4j에서 그래프 확인

Neo4j 브라우저 (http://localhost:7474)에서:

```cypher
// 모든 테이블 보기
MATCH (t:Table)
RETURN t
LIMIT 25

// 테이블과 컬럼 관계 보기
MATCH (t:Table)-[:HAS_COLUMN]->(c:Column)
WHERE t.name = 'orders'
RETURN t, c

// FK 관계 보기
MATCH (t1:Table)-[:FK_TO_TABLE]->(t2:Table)
RETURN t1, t2

// 벡터 검색 테스트 (임베딩이 필요하므로 실제로는 API에서 수행)
// CALL db.index.vector.queryNodes('table_vec_index', 10, [/* 벡터 */])
```

## 🧹 Step 9: 정리

### 서비스 중지

```bash
# API 서버 중지 (Ctrl+C)

# Docker 컨테이너 중지
docker-compose down

# 데이터까지 모두 삭제하려면
docker-compose down -v
```

### 재시작

```bash
# 다시 시작 (데이터 유지됨)
docker-compose up -d
uv run python main.py

# 인제스천은 이미 완료되어 있으므로 바로 질의 가능
```

## 📝 샘플 질문 예시

이 테스트 데이터베이스로 시도해볼 수 있는 질문들:

### 고객 분석
- "프리미엄 고객 목록"
- "국가별 고객 수"
- "가장 많이 구매한 고객 Top 10"
- "평균 구매 금액이 높은 국가"

### 상품 분석
- "재고가 부족한 상품 (100개 미만)"
- "카테고리별 평균 가격"
- "가장 비싼 상품 Top 5"
- "리뷰 평점이 높은 상품"

### 주문 분석
- "최근 7일간 일별 주문 건수"
- "주문 상태별 건수"
- "월별 매출 추이"
- "배송 완료까지 평균 소요 시간"

### 리뷰 분석
- "평점이 높은 상품 Top 10"
- "리뷰가 많은 상품"
- "카테고리별 평균 평점"

### 복합 분석
- "Electronics 카테고리에서 리뷰 평점 4.5 이상인 상품"
- "지난달 매출 Top 10 상품의 평균 리뷰 점수"
- "프리미엄 회원이 가장 많이 구매한 카테고리"

## ⚠️ 트러블슈팅

### PostgreSQL 연결 실패
```bash
# 컨테이너 로그 확인
docker-compose logs postgres

# 컨테이너 재시작
docker-compose restart postgres

# 포트 충돌 확인
lsof -i :5432
```

### Neo4j 연결 실패
```bash
# Neo4j 로그 확인
docker-compose logs neo4j

# 메모리 부족 시 docker-compose.yml에서 메모리 설정 조정
```

### 인제스천 실패
- OpenAI API Key 확인
- API 사용량 한도 확인
- 네트워크 연결 확인

### SQL 생성 품질 향상
- 질문을 더 구체적으로 작성
- 테이블 이름과 컬럼 이름 언급
- 예: "orders 테이블에서..." (X) → "주문 테이블에서..." (O)

## 📊 성능 벤치마크

테스트 환경에서의 예상 성능:

| 쿼리 유형 | 평균 응답 시간 |
|----------|--------------|
| 단순 조회 (SELECT) | 0.8-1.2초 |
| 집계 쿼리 (GROUP BY) | 1.0-1.5초 |
| 조인 쿼리 (2개 테이블) | 1.2-1.8초 |
| 복잡한 분석 (3+ 조인) | 1.5-2.5초 |

**구성 요소별 소요 시간:**
- 임베딩: 40-60ms
- Neo4j 검색: 80-150ms
- LLM SQL 생성: 800-1200ms
- PostgreSQL 실행: 10-100ms

---

**Happy Testing!** 🎉

문제가 발생하면 GitHub Issues에 올려주세요!

