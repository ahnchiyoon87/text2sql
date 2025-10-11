#!/bin/bash
# Frontend 업데이트 자동화 스크립트

echo "🔨 Building Frontend..."
cd frontend
VITE_API_URL=/api npm run build

echo "📦 Copying to Gateway..."
cp -r dist/* ../gateway/src/main/resources/static/

echo "🔄 Restarting Gateway..."
cd ..
pkill -f "spring-boot:run"
sleep 2
cd gateway
mvn spring-boot:run > gateway.log 2>&1 &

echo ""
echo "✅ Frontend updated!"
echo "🌐 Access: http://localhost:9090"
