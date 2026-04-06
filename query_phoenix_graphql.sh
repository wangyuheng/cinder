#!/bin/bash
# Query Phoenix GraphQL API with correct schema

PHOENIX_URL="http://localhost:6006"

echo "============================================================"
echo "Querying Phoenix GraphQL API"
echo "============================================================"

# Query 1: Get projects
echo ""
echo "1. Getting projects..."
curl -s -X POST "${PHOENIX_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ projects { edges { node { id name } } } }"}'

# Query 2: Get spans for cinder project (project_id=2)
echo ""
echo ""
echo "2. Getting spans for cinder project..."
curl -s -X POST "${PHOENIX_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($projectId: ID!, $first: Int) { node(id: $projectId) { ... on Project { spans(first: $first) { edges { node { name kind startTime attributes } } } } } }",
    "variables": {"projectId": "UHJvamVjdDoy", "first": 20}
  }'

# Query 3: Get traces for cinder project
echo ""
echo ""
echo "3. Getting traces for cinder project..."
curl -s -X POST "${PHOENIX_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($projectId: ID!, $first: Int) { node(id: $projectId) { ... on Project { traces(first: $first) { edges { node { traceId startTime spanCount } } } } } }",
    "variables": {"projectId": "UHJvamVjdDoy", "first": 20}
  }'

echo ""
echo ""
echo "============================================================"
echo "Summary"
echo "============================================================"
echo "如果看到数据，说明 Phoenix 正常工作"
