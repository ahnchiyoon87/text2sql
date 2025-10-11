# Neo4j Text2SQL Frontend

Vue 3 + TypeScript 기반 프론트엔드

## 🎨 주요 기능

### 1. 질의 화면 (/)
- 자연어 질문 입력
- 생성된 SQL 확인
- 결과 테이블 표시
- 자동 차트 생성 (Vega-Lite)
- Provenance 정보 (어떤 테이블/컬럼이 사용되었는지)
- 성능 메트릭 (각 단계별 소요 시간)

### 2. 스키마 화면 (/schema)
- 전체 테이블 목록
- 테이블 상세 정보 (컬럼, 타입, Nullable)
- **ER Diagram** (Mermaid 기반)
  - 자동 관계 추정 (FK 패턴)
  - 시각적 스키마 구조
  - 상호작용 가능

## 🚀 실행

```bash
# 설치
npm install

# 개발 서버 (포트 3000)
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 미리보기
npm run preview
```

## 📁 프로젝트 구조

```
frontend/
├── src/
│   ├── components/          # Vue 컴포넌트
│   │   ├── QueryInput.vue   # 질의 입력
│   │   ├── ResultTable.vue  # 결과 테이블
│   │   ├── ChartViewer.vue  # 차트 뷰어 (Vega-Lite)
│   │   └── ERDiagram.vue    # ER 다이어그램 (Mermaid)
│   ├── views/               # 페이지 뷰
│   │   ├── QueryView.vue    # 메인 질의 화면
│   │   └── SchemaView.vue   # 스키마 관리 화면
│   ├── stores/              # Pinia 스토어
│   │   ├── query.ts         # 질의 상태 관리
│   │   └── schema.ts        # 스키마 상태 관리
│   ├── services/            # API 서비스
│   │   └── api.ts           # API 클라이언트
│   ├── router/              # Vue Router
│   │   └── index.ts
│   ├── App.vue              # 루트 컴포넌트
│   └── main.ts              # 엔트리 포인트
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## 🔧 기술 스택

- **Vue 3** (Composition API)
- **TypeScript**
- **Pinia** (상태 관리)
- **Vue Router** (라우팅)
- **Vite** (번들러)
- **Axios** (HTTP 클라이언트)
- **Vega-Lite** (차트)
- **Mermaid** (ER Diagram)

## 🌐 API 연동

백엔드 API는 프록시를 통해 연결됩니다:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## 📊 ER Diagram 특징

- **Mermaid.js** 사용
- 자동 관계 추정:
  - `*_id` 패턴으로 FK 탐지
  - 테이블 간 연결 자동 생성
- 컬럼 정보 표시:
  - PK 표시 (🔑)
  - 데이터 타입
  - Nullable 여부
- 반응형 레이아웃
- 클릭 상호작용

## 🎯 사용 예시

### 1. 자연어 질의
```
카테고리별 상품 개수
→ SQL 자동 생성
→ 결과 테이블
→ 차트 자동 추천 (Bar, Pie 등)
```

### 2. 스키마 탐색
```
테이블 목록 → 테이블 선택 → 컬럼 상세
ER Diagram으로 전체 구조 파악
```

## 🔒 환경 변수

`.env` 파일:
```bash
VITE_API_URL=http://localhost:8001
```

## 📱 반응형 디자인

- 데스크톱 최적화
- 태블릿 지원
- 모바일 레이아웃 (추후 개선)

## 🚧 향후 개선사항

- [ ] 스키마 편집 기능 (테이블/컬럼 추가/수정/삭제)
- [ ] 쿼리 히스토리 저장 (LocalStorage)
- [ ] 다크 모드
- [ ] 차트 커스터마이징
- [ ] SQL 문법 하이라이팅
- [ ] 자동 완성 (테이블/컬럼명)
- [ ] 피드백 UI 개선
- [ ] 실시간 쿼리 실행 상태
- [ ] 더 풍부한 ER Diagram (줌, 패닝, 레이아웃 옵션)

## 📄 라이선스

MIT

