# 🎨 Neo4j Text2SQL Frontend 가이드

## 🚀 빠른 시작

### 시스템 실행 순서

```bash
# 1. Neo4j + PostgreSQL (Docker Compose)
docker-compose up -d

# 2. API 서버 (포트 8001)
cd /Users/uengine/neo4j_text2sql
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 3. Vue 프론트엔드 (포트 3000)
cd frontend
npm run dev
```

### 접속 URL

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8001/docs
- 🗄️ **Neo4j Browser**: http://localhost:7474
- 🐘 **PostgreSQL**: localhost:5432

## 📱 화면 구성

### 1️⃣ 질의 화면 (메인)

**URL**: http://localhost:3000/

**기능**:
- 자연어 질문 입력창
- 예시 질문 버튼 (빠른 테스트)
- 생성된 SQL 표시 + 복사 버튼
- 출처 정보 (Provenance)
  - 사용된 테이블 목록
  - 사용된 컬럼 목록
  - Neo4j 벡터 매칭 점수
- 성능 메트릭
  - 임베딩 시간
  - 그래프 검색 시간
  - LLM 시간
  - SQL 실행 시간
  - 총 소요 시간
- 결과 테이블 (정렬, 포맷팅)
- 자동 차트 생성
  - Bar Chart
  - Line Chart
  - Pie Chart
  - Scatter Plot

**사용 흐름**:
```
질문 입력 → 생성 중... → SQL 표시 → 결과 확인 → 차트 선택
```

**예시 질문**:
- "카테고리별 상품 개수"
- "프리미엄 회원 목록"
- "가장 비싼 상품 Top 5"
- "국가별 고객 수"
- "최근 주문 10건"

### 2️⃣ 스키마 화면

**URL**: http://localhost:3000/schema

**기능**:
- **테이블 목록** (왼쪽 패널)
  - 검색 기능
  - 테이블명
  - 컬럼 개수
  - 설명 (있는 경우)
  
- **테이블 상세** (오른쪽 패널)
  - 컬럼 목록
  - 데이터 타입
  - Nullable 여부
  - PK 표시 (🔑)
  - 컬럼 설명

- **ER Diagram** (하단)
  - Mermaid로 렌더링
  - 전체 스키마 구조 시각화
  - 테이블 간 관계 자동 추정
  - FK 패턴 기반 연결 (*_id)

**사용 흐름**:
```
테이블 검색 → 테이블 선택 → 상세 정보 확인 → ER Diagram으로 전체 구조 파악
```

## 🎨 UI/UX 특징

### 디자인
- **모던 & 미니멀**: 깔끔한 UI
- **직관적**: 버튼과 레이아웃이 명확
- **반응형**: 다양한 화면 크기 지원
- **색상 테마**: 
  - Primary: Green (#4CAF50)
  - Background: Light Gray (#f5f7fa)
  - Text: Dark Gray (#333)

### 인터랙션
- **실시간 피드백**: 로딩 스피너, 상태 표시
- **호버 효과**: 버튼과 테이블 행
- **부드러운 전환**: CSS transitions
- **키보드 단축키**: Ctrl+Enter로 질문 제출

### 반응성
- **빠른 로딩**: Vite 기반 HMR
- **에러 처리**: 사용자 친화적 에러 메시지
- **상태 관리**: Pinia로 중앙 집중식 관리

## 🔧 기술 세부사항

### Vue 3 Composition API

```typescript
// 예시: QueryInput.vue
<script setup lang="ts">
import { ref } from 'vue'

const question = ref('')

function handleSubmit() {
  emit('submit', question.value)
}
</script>
```

### Pinia 스토어

```typescript
// stores/query.ts
export const useQueryStore = defineStore('query', () => {
  const currentResponse = ref<AskResponse | null>(null)
  
  async function ask(question: string) {
    const response = await apiService.ask({ question })
    currentResponse.value = response
  }
  
  return { currentResponse, ask }
})
```

### API 서비스

```typescript
// services/api.ts
export const apiService = {
  async ask(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask', request)
    return data
  }
}
```

### Vega-Lite 차트

```typescript
// ChartViewer.vue
import embed from 'vega-embed'

await embed(chartEl.value, vegaSpec, {
  actions: { export: true }
})
```

### Mermaid ER Diagram

```typescript
// ERDiagram.vue
function generateMermaidER(): string {
  let code = 'erDiagram\n'
  
  // 테이블 정의
  tables.forEach(table => {
    code += `    ${table.name} {\n`
    columns.forEach(col => {
      code += `        ${col.dtype} ${col.name}\n`
    })
    code += `    }\n`
  })
  
  // 관계 (FK 기반)
  code += `    ${parentTable} ||--o{ ${childTable} : "has"\n`
  
  return code
}
```

## 📊 데이터 흐름

```
[사용자 입력]
    ↓
[Vue Component]
    ↓
[Pinia Store]
    ↓
[API Service (Axios)]
    ↓
[FastAPI Backend] (localhost:8001)
    ↓
[Neo4j + PostgreSQL]
    ↓
[응답]
    ↓
[Pinia Store 업데이트]
    ↓
[Vue Component 리렌더링]
    ↓
[사용자에게 표시]
```

## 🎯 사용 시나리오

### 시나리오 1: 데이터 분석가
```
1. 프론트엔드 접속 (localhost:3000)
2. "지난달 카테고리별 매출"이라고 질문
3. 생성된 SQL 확인
4. 결과 테이블 검토
5. Bar Chart로 시각화
6. SQL 복사해서 보고서에 첨부
```

### 시나리오 2: 개발자
```
1. 스키마 화면 접속 (/schema)
2. 테이블 구조 탐색
3. ER Diagram으로 관계 파악
4. 특정 테이블 선택
5. 컬럼 정보 확인
6. FK 관계 이해
```

### 시나리오 3: 비즈니스 사용자
```
1. 예시 질문 버튼 클릭
2. 결과 확인
3. 차트 타입 변경
4. 다른 질문 시도
5. 데이터 기반 인사이트 도출
```

## 🐛 트러블슈팅

### 프론트엔드가 로드되지 않음
```bash
# 포트 확인
lsof -i :3000

# 프로세스 종료
kill -9 <PID>

# 재시작
cd frontend && npm run dev
```

### API 연결 실패
```bash
# 백엔드 상태 확인
curl http://localhost:8001/health

# 프록시 설정 확인
cat frontend/vite.config.ts
```

### 차트가 렌더링되지 않음
- 브라우저 콘솔 확인
- Vega-Lite 데이터 형식 확인
- 차트 타입과 데이터 호환성 확인

### ER Diagram이 표시되지 않음
- Mermaid 구문 오류 확인
- 브라우저 콘솔에서 에러 메시지 확인
- 테이블/컬럼 데이터 로드 확인

## 🚀 프로덕션 배포

```bash
# 1. 프론트엔드 빌드
cd frontend
npm run build

# 2. 빌드된 파일 (frontend/dist/)
# 3. Nginx/Apache로 서빙
# 4. API URL 환경 변수 설정

# Nginx 예시:
server {
  listen 80;
  root /path/to/frontend/dist;
  
  location /api {
    proxy_pass http://localhost:8001;
  }
}
```

## 📈 성능 최적화

- **Lazy Loading**: 라우트별 코드 스플리팅
- **API 캐싱**: 스키마 정보는 한 번만 로드
- **Debouncing**: 검색 입력 최적화
- **Virtual Scrolling**: 큰 테이블 최적화 (추후)

## 🎓 배운 점

1. **Vue 3 Composition API**: 재사용 가능한 로직
2. **TypeScript**: 타입 안전성
3. **Pinia**: 간단하고 강력한 상태 관리
4. **Vega-Lite**: 선언적 차트 생성
5. **Mermaid**: 다이어그램을 코드로 표현

---

**Happy Coding!** 🎉

