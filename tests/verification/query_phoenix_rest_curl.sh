#!/bin/bash
# Query Phoenix via REST API using curl

PHOENIX_URL="http://localhost:6006"

echo "============================================================"
echo "Querying Phoenix via REST API"
echo "============================================================"

# Query 1: Get projects
echo ""
echo "1. Getting projects..."
curl -s "${PHOENIX_URL}/api/v1/projects" | jq .

# Query 2: Get spans for cinder project (project_id=2)
echo ""
echo "2. Getting spans for cinder project..."
curl -s "${PHOENIX_URL}/api/v1/projects/2/spans?limit=10" | jq .

# Query 3: Get traces for cinder project
echo ""
echo "3. Getting traces for cinder project..."
curl -s "${PHOENIX_URL}/api/v1/projects/2/traces?limit=10" | jq .

# Query 4: Try different endpoints
echo ""
echo "4. Trying /v1/spans..."
curl -s "${PHOENIX_URL}/v1/spans?limit=10" | jq .

echo ""
echo "============================================================"
echo "如果所有查询都失败，尝试直接查询数据库"
echo "============================================================"
