# ⚡ Quick Test (5분 만에 시작하기)

Docker Compose로 PostgreSQL + Neo4j를 함께 실행하여 바로 테스트해보세요!

## 🚀 1분 설정

```bash
# 1. 환경 변수 파일 생성
cp env.test.example .env

# 2. .env 파일 열어서 OPENAI_API_KEY만 수정
# OPENAI_API_KEY=your-real-key-here
```

## 🐳 서비스 시작 (이미 완료!)

```bash
# 모든 서비스가 이미 실행 중입니다:
docker ps

# 예상 출력:
# postgres_text2sql  - Port 5432
# neo4j_text2sql     - Ports 7474, 7687
```

## ✅ 샘플 데이터 확인

```bash
# PostgreSQL 데이터 확인
docker exec postgres_text2sql psql -U testuser -d testdb -c "
SELECT 'Customers' AS table_name, COUNT(*) AS count FROM customers
UNION ALL SELECT 'Products', COUNT(*) FROM products
UNION ALL SELECT 'Orders', COUNT(*) FROM orders
UNION ALL SELECT 'Categories', COUNT(*) FROM categories
UNION ALL SELECT 'Reviews', COUNT(*) FROM reviews;
"
```

**샘플 데이터:**
- ✅ 카테고리: 8개 (Electronics, Books, Clothing, etc.)
- ✅ 상품: 50개
- ✅ 고객: 30명 (미국, 한국, 유럽, 아시아)
- ✅ 주문: 30건 (최근 6개월)
- ✅ 리뷰: 50개

## 📊 스키마 확인

```bash
# E-Commerce 데이터베이스 ERD:
# categories (카테고리)
#   ↓ (1:N)
# products (상품) ← reviews (리뷰) ← customers (고객)
#   ↓ (M:N)                              ↓ (1:N)
# order_items ← orders (주문) ───────────┘
```

## 🎯 다음 단계

### Step 1: Neo4j 스키마 초기화

```bash
# 새 터미널에서
uv run python scripts/init_schema.py
```

### Step 2: API 서버 시작

```bash
# 새 터미널에서
uv run python main.py
```

### Step 3: 스키마 인제스천

```bash
# 새 터미널에서 (2-3분 소요)
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "db_name": "testdb",
    "schema": "public",
    "clear_existing": true
  }' | jq .
```

### Step 4: 첫 질문!

```bash
# 간단한 조회
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "고객 목록 5명만 보여줘",
    "limit": 5
  }' | jq '.table'
```

## 🧪 테스트 쿼리 예시

### 쿼리 1: 카테고리별 상품 수
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "카테고리별 상품 개수", "limit": 10}' | jq .
```

### 쿼리 2: 최근 주문 Top 5
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "가장 최근 주문 5건", "limit": 5}' | jq '.table'
```

### 쿼리 3: 프리미엄 고객
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "프리미엄 회원 목록", "limit": 10}' | jq '.table'
```

### 쿼리 4: 인기 상품 (리뷰 기준)
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "리뷰가 가장 많은 상품 Top 5", "limit": 5}' | jq .
```

### 쿼리 5: 카테고리별 평균 가격
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "카테고리별 평균 상품 가격", "limit": 10}' | jq .
```

## 🌐 브라우저에서 테스트

### Swagger UI (추천)
http://localhost:8000/docs

### Neo4j Browser
http://localhost:7474
- Username: `neo4j`
- Password: `password123`

## 📝 샘플 질문 더 보기

이 데이터베이스로 시도해볼 수 있는 질문들:

**고객 분석**
- "국가별 고객 수"
- "가장 많이 구매한 고객 Top 10"
- "프리미엄 고객과 일반 고객의 평균 주문 금액"

**상품 분석**
- "Electronics 카테고리 상품 목록"
- "가장 비싼 상품 Top 5"
- "재고가 100개 미만인 상품"
- "리뷰 평점이 4.5 이상인 상품"

**주문 분석**
- "최근 7일간 일별 주문 건수"
- "주문 상태별 건수"
- "평균 주문 금액"
- "가장 많이 팔린 상품 Top 10"

**복합 분석**
- "한국 고객들이 가장 많이 구매한 카테고리"
- "프리미엄 회원의 평균 리뷰 점수"
- "지난달 매출이 가장 높았던 상품의 리뷰 평점"

## 🔄 재시작

```bash
# 모든 것을 재시작하려면
docker-compose restart

# 데이터까지 초기화하려면
docker-compose down -v
docker-compose up -d
```

## 🛑 정리

```bash
# 서비스 중지 (데이터 보존)
docker-compose down

# 완전 삭제 (데이터 포함)
docker-compose down -v
```

## 💡 팁

1. **빠른 테스트**: Swagger UI (http://localhost:8000/docs) 사용
2. **Neo4j 그래프 확인**: Neo4j Browser에서 `MATCH (n) RETURN n LIMIT 50`
3. **성능**: 첫 쿼리는 느릴 수 있음 (LLM 콜드 스타트)
4. **디버깅**: `docker-compose logs -f` 로 실시간 로그 확인

---

**문제가 생기면?** → `TEST_GUIDE.md` 참고

