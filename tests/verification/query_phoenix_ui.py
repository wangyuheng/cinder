#!/usr/bin/env python3
"""Query Phoenix via GraphQL to verify UI data."""

import requests
import json

PHOENIX_URL = "http://localhost:6006"

def query_phoenix(query):
    """Query Phoenix GraphQL API."""
    response = requests.post(
        f"{PHOENIX_URL}/graphql",
        json={"query": query},
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

print("="*60)
print("Querying Phoenix UI Data via GraphQL")
print("="*60)

# Query spans with project info
query = """
{
  spans(first: 5) {
    edges {
      node {
        spanId
        traceId
        name
        kind
        startTime
        attributes
        project {
          name
        }
      }
    }
  }
}
"""

result = query_phoenix(query)
if result:
    if "errors" in result:
        print(f"\nGraphQL Errors: {result['errors']}")
    elif "data" in result and result["data"]:
        spans = result["data"]["spans"]["edges"]
        print(f"\nFound {len(spans)} spans:")
        
        for i, edge in enumerate(spans, 1):
            span = edge["node"]
            print(f"\n[{i}] Span:")
            print(f"  Name: {span.get('name', 'N/A')}")
            print(f"  Kind: {span.get('kind', 'N/A')}")
            print(f"  Span ID: {span.get('spanId', 'N/A')}")
            print(f"  Project: {span.get('project', {}).get('name', 'N/A')}")
            
            attrs = span.get("attributes", {})
            if attrs:
                # Check for LLM attributes
                llm_attrs = {k: v for k, v in attrs.items() if k.startswith("llm.")}
                if llm_attrs:
                    print(f"  LLM Attributes:")
                    for k, v in llm_attrs.items():
                        if isinstance(v, str) and len(v) > 50:
                            v = v[:50] + "..."
                        print(f"    - {k}: {v}")
    else:
        print("No data returned from query")
else:
    print("Failed to query spans")

print("\n" + "="*60)
print("Summary")
print("="*60)
print("\nPhoenix UI 数据验证：")
print("1. 检查 span name 是否正确显示")
print("2. 检查 span kind 是否正确显示")
print("3. 检查项目名称是否正确")
print("4. 检查 LLM 属性是否正确")
