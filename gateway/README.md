# Spring Cloud Gateway

모든 서비스를 단일 포트(9090)로 통합하는 API Gateway

## 아키텍처

```
http://localhost:9090
├── /              → Frontend (Vue.js)    localhost:3000
└── /api/*         → Backend API (FastAPI) localhost:8001
```

## 실행

```bash
# Maven으로 실행
./mvnw spring-boot:run

# 또는 jar 빌드 후 실행
./mvnw clean package
java -jar target/neo4j-text2sql-gateway-1.0.0.jar
```

## 접속

- **통합 URL**: http://localhost:9090
  - Frontend: http://localhost:9090/
  - API: http://localhost:9090/api/*

## CORS 설정

Gateway에서 CORS를 처리하므로, 모든 오리진에서 접근 가능합니다.

## 라우팅 규칙

1. `/api/**` → FastAPI (8001) - `/api` 제거 후 전달
2. 나머지 → Vue Frontend (3000)

