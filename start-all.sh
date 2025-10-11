#!/bin/bash

# Neo4j Text2SQL - 전체 시스템 시작 스크립트

echo "🚀 Starting Neo4j Text2SQL System..."
echo ""

# 1. Docker Compose (Neo4j + PostgreSQL)
echo "1️⃣ Starting Docker services (Neo4j + PostgreSQL)..."
docker-compose up -d
sleep 5
echo "   ✅ Docker services started"
echo ""

# 2. Backend API (FastAPI)
echo "2️⃣ Starting Backend API (port 8001)..."
cd /Users/uengine/neo4j_text2sql
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > api.log 2>&1 &
API_PID=$!
sleep 5
echo "   ✅ Backend API started (PID: $API_PID)"
echo ""

# 3. Frontend (Vue.js)
echo "3️⃣ Starting Frontend (port 3000)..."
cd /Users/uengine/neo4j_text2sql/frontend
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 3
echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

# 4. Gateway (Spring Cloud)
echo "4️⃣ Starting Gateway (port 9090)..."
cd /Users/uengine/neo4j_text2sql/gateway
./mvnw spring-boot:run > gateway.log 2>&1 &
GATEWAY_PID=$!
echo "   ✅ Gateway starting... (PID: $GATEWAY_PID)"
echo ""

echo "======================================"
echo "🎉 All services started!"
echo "======================================"
echo ""
echo "📍 Access URLs:"
echo "   🌐 Gateway (통합):  http://localhost:9090"
echo "   🎨 Frontend:        http://localhost:3000"
echo "   🔧 Backend API:     http://localhost:8001"
echo "   🗄️  Neo4j Browser:  http://localhost:7474"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f api.log"
echo "   Frontend: tail -f frontend/frontend.log"
echo "   Gateway:  tail -f gateway/gateway.log"
echo ""
echo "🛑 Stop all: ./stop-all.sh"
echo ""

