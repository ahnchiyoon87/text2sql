# ✅ Gateway 문제 해결 완료!

## 🔧 수정 사항

### 문제
- Spring Cloud Gateway가 Vue dev server를 프록시하는 것이 복잡함
- Whitelabel Error Page 발생

### 해결책
Frontend를 **빌드(build)**하여 Gateway에서 **정적 파일로 서빙**

## 📁 변경된 구조

```
gateway/
├── src/main/resources/
│   ├── static/              # ← Frontend 빌드 파일
│   │   ├── index.html
│   │   └── assets/
│   └── application.yml
└── src/main/java/
    └── ...
```

## 🚀 이제 작동합니다!

### ✅ 확인된 기능

1. **Frontend 서빙**: http://localhost:9090/
   ```
   ✓ HTML 로드
   ✓ JavaScript 번들
   ✓ CSS 스타일
   ✓ Vue Router (/, /schema)
   ```

2. **Backend API**: http://localhost:9090/api/*
   ```
   ✓ /api/health → healthy
   ✓ /api/ask → SQL 생성
   ✓ /api/meta/tables → 테이블 목록
   ```

3. **CORS**: 완전 해결 ✅
   - 동일 도메인 (localhost:9090)
   - 브라우저 Same-Origin Policy 만족

## 🌐 접속

### **단일 URL로 모든 기능 사용**

```
http://localhost:9090
```

- 메인 화면: 자연어 질의
- 스키마 화면: /schema
- API: /api/*

## 🔄 Frontend 업데이트 방법

Frontend 코드를 수정한 후:

```bash
# 1. Frontend 재빌드
cd frontend
npm run build

# 2. Gateway static 폴더로 복사
cp -r dist/* ../gateway/src/main/resources/static/

# 3. Gateway 재시작
cd ../gateway
pkill -f "spring-boot:run"
mvn spring-boot:run > gateway.log 2>&1 &
```

## 📝 자동화 스크립트

```bash
# update-frontend.sh
#!/bin/bash
cd frontend
npm run build
cp -r dist/* ../gateway/src/main/resources/static/
echo "✅ Frontend updated in Gateway!"
```

## 🎯 개발 워크플로우

### 개발 중 (Hot Reload 필요)

```bash
# Frontend 직접 접속 (Vite dev server)
http://localhost:3000

# Backend API는 Vite 프록시 사용
# vite.config.ts의 proxy 설정 활용
```

### 테스트/프로덕션

```bash
# Gateway 통합 URL 사용
http://localhost:9090

# CORS 없는 환경에서 전체 테스트
```

## 🏗️ 최종 아키텍처

```
브라우저 (http://localhost:9090)
    ↓
┌─────────────────────────────────────┐
│  Spring Cloud Gateway (9090)         │
│                                      │
│  GET  /           → static/index.html│
│  GET  /assets/*   → static/assets/*  │
│  POST /api/ask    → FastAPI:8001/ask │
│  GET  /api/health → FastAPI:8001/health│
│                                      │
└──────────────┬───────────────────────┘
               │
               ↓
         FastAPI (8001)
               │
        ┌──────┼──────┐
        ↓      ↓      ↓
     Neo4j  PostgreSQL  OpenAI
```

## ✨ 장점

1. **단일 URL**: 하나의 도메인으로 통합
2. **CORS 해결**: 완전히 제거
3. **프로덕션 준비**: 배포 환경과 동일
4. **간단한 배포**: Gateway JAR 하나만 배포
5. **보안**: API 키 숨김 (Backend만 OpenAI 호출)

## 🎊 완료!

**이제 http://localhost:9090 으로 접속하시면 모든 기능을 사용하실 수 있습니다!**

```
✅ 자연어 질의
✅ SQL 자동 생성
✅ 결과 테이블
✅ 자동 차트
✅ 스키마 탐색
✅ ER Diagram
✅ CORS 문제 없음
```

---

**Happy Querying!** 🚀

