# 🌉 Spring Cloud Gateway 가이드

## 개요

Spring Cloud Gateway를 사용하여 Frontend와 Backend API를 단일 포트(9090)로 통합합니다.

## 아키텍처

```
┌─────────────────────────────────────────────────────┐
│          http://localhost:9090 (Gateway)            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  GET  /            → Frontend (Vue.js) :3000       │
│  GET  /schema      → Frontend (Vue.js) :3000       │
│  POST /api/ask     → Backend (FastAPI) :8001       │
│  GET  /api/meta/*  → Backend (FastAPI) :8001       │
│  ...                                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 장점

### 1. CORS 문제 해결
- 모든 서비스가 동일 도메인(localhost:9090)
- Gateway에서 CORS 처리
- 브라우저의 Same-Origin Policy 이슈 없음

### 2. 단일 진입점
- 하나의 URL로 모든 서비스 접근
- 프론트엔드 설정 단순화
- 배포 환경 변경 용이

### 3. 로드 밸런싱 (향후)
- 여러 백엔드 인스턴스 분산
- 헬스체크 통합
- 장애 격리

## 실행 방법

### 방법 1: 전체 시스템 자동 시작

```bash
./start-all.sh
```

이 스크립트는 다음을 자동으로 실행합니다:
1. Docker (Neo4j + PostgreSQL)
2. Backend API (FastAPI)
3. Frontend (Vue.js)
4. Gateway (Spring Cloud)

### 방법 2: Gateway만 수동 실행

```bash
cd gateway

# Maven으로 실행
./mvnw spring-boot:run

# 또는 jar 빌드 후 실행
./mvnw clean package
java -jar target/neo4j-text2sql-gateway-1.0.0.jar
```

## 접속 방법

### Gateway를 통한 접속 (권장)

```
http://localhost:9090
```

이 URL 하나로 모든 기능 사용 가능:
- Frontend UI
- Backend API (/api/*)

### 직접 접속 (개발 시)

- Frontend: http://localhost:3000
- Backend: http://localhost:8001
- Neo4j: http://localhost:7474

## 라우팅 규칙

| 경로 패턴 | 대상 서비스 | 변환 |
|----------|------------|------|
| `/api/**` | Backend (8001) | `/api` 제거 |
| `/**` | Frontend (3000) | 그대로 전달 |

### 예시

```
요청: http://localhost:9090/api/ask
  ↓ Gateway 라우팅
전달: http://localhost:8001/ask

요청: http://localhost:9090/schema
  ↓ Gateway 라우팅
전달: http://localhost:3000/schema
```

## 설정 파일

### application.yml

```yaml
server:
  port: 9090  # Gateway 포트

spring:
  cloud:
    gateway:
      routes:
        - id: frontend
          uri: http://localhost:3000
          predicates:
            - Path=/**
            - Not=/api/**
        
        - id: api
          uri: http://localhost:8001
          predicates:
            - Path=/api/**
          filters:
            - StripPrefix=1  # /api 제거
```

## CORS 설정

Gateway에서 모든 CORS 처리:

```java
@Bean
public CorsWebFilter corsWebFilter() {
    CorsConfiguration corsConfig = new CorsConfiguration();
    corsConfig.addAllowedOrigin("*");
    corsConfig.addAllowedMethod("*");
    corsConfig.addAllowedHeader("*");
    
    // ...
}
```

## 로그 확인

```bash
# Gateway 로그
tail -f gateway/gateway.log

# 실시간 디버그 로그
cd gateway
./mvnw spring-boot:run -Dspring-boot.run.arguments="--logging.level.org.springframework.cloud.gateway=DEBUG"
```

## 트러블슈팅

### Gateway가 시작되지 않음

```bash
# 포트 사용 확인
lsof -i :9090

# 기존 프로세스 종료
kill -9 <PID>
```

### 백엔드/프론트엔드 연결 실패

```bash
# 각 서비스 상태 확인
curl http://localhost:8001/health  # Backend
curl http://localhost:3000         # Frontend

# 서비스 재시작
./stop-all.sh
./start-all.sh
```

### CORS 오류 여전히 발생

1. Gateway를 통해 접속하는지 확인 (9090 포트)
2. 브라우저 캐시 삭제
3. Gateway 로그에서 CORS 필터 동작 확인

## 성능 고려사항

### 지연 시간

Gateway를 거치면 약간의 오버헤드 발생:
- 일반적으로 1-5ms 추가
- 비동기/논블로킹 처리로 최소화

### 최적화 팁

1. **Keep-Alive 연결**: HTTP 연결 재사용
2. **커넥션 풀**: 백엔드 연결 풀 관리
3. **타임아웃 설정**: 적절한 타임아웃 값

```yaml
spring:
  cloud:
    gateway:
      httpclient:
        connect-timeout: 1000
        response-timeout: 5s
        pool:
          max-connections: 500
```

## 프로덕션 배포

### 1. 프로파일 분리

```yaml
# application-prod.yml
server:
  port: 80

spring:
  cloud:
    gateway:
      routes:
        - id: frontend
          uri: http://frontend-service:3000
        - id: api
          uri: http://api-service:8001
```

### 2. Docker 컨테이너

```dockerfile
FROM openjdk:17-jdk-slim
COPY target/neo4j-text2sql-gateway-1.0.0.jar app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

### 3. Kubernetes

```yaml
apiVersion: v1
kind: Service
metadata:
  name: gateway
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 9090
  selector:
    app: gateway
```

## 모니터링

### Spring Boot Actuator

`pom.xml`에 추가:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

엔드포인트:
- Health: `http://localhost:9090/actuator/health`
- Metrics: `http://localhost:9090/actuator/metrics`
- Routes: `http://localhost:9090/actuator/gateway/routes`

## 보안

### 1. Rate Limiting

```java
@Bean
public KeyResolver userKeyResolver() {
    return exchange -> Mono.just(
        exchange.getRequest()
            .getRemoteAddress()
            .getAddress()
            .getHostAddress()
    );
}
```

### 2. API 키 검증

```java
.route("api", r -> r.path("/api/**")
    .filters(f -> f
        .stripPrefix(1)
        .filter(new ApiKeyFilter()))  // Custom filter
    .uri("http://localhost:8001"))
```

## 대안: Nginx

Spring Cloud Gateway 대신 Nginx를 사용할 수도 있습니다:

```nginx
server {
    listen 9090;
    
    location /api/ {
        proxy_pass http://localhost:8001/;
    }
    
    location / {
        proxy_pass http://localhost:3000/;
    }
}
```

Nginx가 더 가볍고 빠르지만, Spring 생태계 통합은 Spring Cloud Gateway가 유리합니다.

---

**Gateway로 모든 서비스를 하나로!** 🌉

