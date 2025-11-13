# 👋 START HERE - Neo4j Text2SQL

## 🎊 시스템이 이미 실행 중입니다!

모든 서비스가 정상 작동하고 있으니 바로 사용하실 수 있습니다!

---

## 🌐 지금 바로 접속하세요!

### ⭐ 통합 URL (권장)

```
http://localhost:9090
```

이 URL 하나로 모든 기능을 사용할 수 있습니다:
- 🎨 Frontend UI (질의 + 스키마)
- 🔧 Backend API
- ✅ CORS 문제 없음

---

## 🎯 빠른 시작 (30초)

### 1️⃣ 브라우저 열기

```bash
open http://localhost:9090
```

### 2️⃣ 질문하기

질의 화면에서 예시 버튼 클릭 또는 직접 입력:
- "카테고리별 상품 개수"
- "프리미엄 회원 목록"
- "가장 비싼 상품 Top 5"

### 3️⃣ 결과 확인

- ✅ SQL 자동 생성
- ✅ 결과 테이블
- ✅ 자동 차트
- ✅ 성능 메트릭

### 4️⃣ 스키마 탐색

상단 메뉴에서 "스키마" 클릭:
- 테이블 목록
- 컬럼 정보
- **ER Diagram** 👈 시각적 스키마 구조

---

## 🎨 주요 기능

### 질의 화면 (/)

**입력**:
```
자연어 질문: "Electronics 카테고리에서 리뷰 평점 4점 이상인 상품"
```

**출력**:
1. **생성된 SQL** (복사 가능)
   ```sql
   SELECT p.name, AVG(r.rating) as avg_rating
   FROM products p
   JOIN reviews r ON p.product_id = r.product_id
   WHERE p.category_id = (SELECT id FROM categories WHERE name = 'Electronics')
   GROUP BY p.name
   HAVING AVG(r.rating) >= 4
   ```

2. **결과 테이블** (포맷팅, 실행 시간)

3. **자동 차트** (Bar, Line, Pie, Scatter)

4. **Provenance** (출처 정보)
   - 사용된 테이블
   - 사용된 컬럼
   - Neo4j 벡터 매칭 점수

5. **성능 메트릭**
   - 임베딩: 2초
   - 그래프 검색: 0.2초
   - LLM: 6초
   - SQL 실행: 0.04초

### 스키마 화면 (/schema)

**좌측 패널**:
- 테이블 목록 (7개)
- 검색 기능
- 클릭하여 상세 보기

**우측 패널**:
- 선택된 테이블의 모든 컬럼
- 데이터 타입
- PK 표시 (🔑)
- Nullable 여부

**하단**:
- **ER Diagram** (Mermaid)
  - 전체 스키마 시각화
  - 테이블 간 관계
  - FK 자동 표시

---

## 📊 샘플 데이터

현재 로드된 E-Commerce 데이터:

| 테이블 | 행수 | 설명 |
|--------|------|------|
| categories | 8 | 상품 카테고리 |
| products | 50 | 상품 정보 |
| customers | 30 | 고객 정보 (10개국) |
| orders | 30 | 주문 내역 |
| order_items | ~70 | 주문 상세 |
| reviews | 50 | 상품 리뷰 |

---

## 💬 질문 예시

### 간단한 조회
```
"고객 목록 10명"
"Electronics 카테고리 상품"
"프리미엄 회원만"
```

### 집계 쿼리
```
"카테고리별 상품 개수"
"국가별 고객 수"
"카테고리별 평균 가격"
```

### 조인 쿼리
```
"가장 많이 구매한 고객 Top 5"
"리뷰가 많은 상품 Top 10"
"한국 고객이 구매한 상품"
```

### 복합 분석
```
"프리미엄 회원의 평균 주문 금액"
"Electronics에서 평점 4점 이상인 상품"
"최근 30일 매출 추이"
```

---

## 🛠️ 시스템 관리

### 시작/종료

```bash
# 전체 시작 (처음 사용 시)
./start-all.sh

# 전체 종료
./stop-all.sh

# Gateway만 재시작
cd gateway && mvn spring-boot:run
```

### 상태 확인

```bash
# 헬스체크
curl http://localhost:9090/api/health

# Docker 서비스
docker ps

# 로그
tail -f api.log frontend/frontend.log gateway/gateway.log
```

---

## 📚 더 알아보기

| 문서 | 내용 |
|------|------|
| `COMPLETE.md` | ⭐ 전체 시스템 요약 |
| `README.md` | 프로젝트 개요 |
| `FRONTEND_GUIDE.md` | Vue.js 가이드 |
| `GATEWAY_GUIDE.md` | Spring Cloud Gateway |
| `TEST_GUIDE.md` | 테스트 방법 |

---

## 🎊 이제 사용하세요!

```
┌────────────────────────────────────┐
│                                    │
│   🌐 http://localhost:9090         │
│                                    │
│   자연어로 데이터베이스에          │
│   질문하고 즉시 결과를 받으세요!   │
│                                    │
│   ✨ Ready to use! ✨              │
│                                    │
└────────────────────────────────────┘
```

**Happy Querying!** 🚀

