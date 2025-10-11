#!/bin/bash
# Sample API queries for testing

API_URL="http://localhost:8000"

echo "=== Neo4j Text2SQL Sample Queries ==="
echo

# 1. Health check
echo "1. Health Check"
curl -s "$API_URL/health" | jq .
echo
echo

# 2. List tables
echo "2. List Tables"
curl -s "$API_URL/meta/tables?limit=5" | jq .
echo
echo

# 3. Ask a question (example)
echo "3. Ask Question"
curl -s -X POST "$API_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me the first 10 users",
    "limit": 10
  }' | jq .
echo
echo

# 4. Feedback stats
echo "4. Feedback Stats"
curl -s "$API_URL/feedback/stats" | jq .
echo

echo "=== Done ==="

