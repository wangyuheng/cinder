#!/bin/bash
# Query Phoenix via REST API using curl (without jq)

PHOENIX_URL="http://localhost:6006"

echo "============================================================"
echo "Querying Phoenix via REST API (Raw Output)"
echo "============================================================"

# Query 1: Get projects
echo ""
echo "1. Getting projects..."
curl -s "${PHOENIX_URL}/api/v1/projects"

echo ""
echo ""
echo "2. Getting spans for cinder project (project_id=2)..."
curl -s "${PHOENIX_URL}/api/v1/projects/2/spans?limit=10"

echo ""
echo ""
echo "3. Getting traces for cinder project..."
curl -s "${PHOENIX_URL}/api/v1/projects/2/traces?limit=10"

echo ""
echo ""
echo "4. Trying GraphQL with minimal query..."
curl -s -X POST "${PHOENIX_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ projects { edges { node { name } } } }"}'

echo ""
echo ""
echo "5. Trying to get spans via GraphQL..."
curl -s -X POST "${PHOENIX_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "query GetSpans($first: Int) { spans(first: $first) { edges { node { name kind } } } }", "variables": {"first": 10}}'

echo ""
echo ""
echo "============================================================"
echo "如果所有查询都失败，检查 Phoenix 日志"
echo "============================================================"
docker logs cinder-phoenix --tail 20
