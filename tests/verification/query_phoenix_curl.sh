#!/bin/bash
# Query Phoenix via GraphQL API using curl

PHOENIX_URL="http://localhost:6006"

echo "============================================================"
echo "Querying Phoenix via GraphQL API"
echo "============================================================"

# Query 1: Get projects
echo ""
echo "1. Getting projects..."
curl -s -X POST "${PHOENIX_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ projects { edges { node { id name } } } }"}' | jq .

# Query 2: Get spans with minimal fields
echo ""
echo "2. Getting spans..."
curl -s -X POST "${PHOENIX_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ spans(first: 10) { edges { node { name kind } } } }"}' | jq .

# Query 3: Get traces
echo ""
echo "3. Getting traces..."
curl -s -X POST "${PHOENIX_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ traces(first: 10) { edges { node { traceId } } } }"}' | jq .

echo ""
echo "============================================================"
echo "如果所有查询都返回错误，尝试检查 Phoenix 状态"
echo "============================================================"

# Check Phoenix health
echo ""
echo "4. Checking Phoenix health..."
curl -s "${PHOENIX_URL}/healthz"

echo ""
echo ""
echo "5. Checking Phoenix version..."
curl -s "${PHOENIX_URL}/arize_phoenix_version"
