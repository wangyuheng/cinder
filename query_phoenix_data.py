#!/usr/bin/env python3
"""Query Phoenix data via GraphQL API."""

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

# Query 1: Get all projects
print("="*60)
print("1. Querying Projects")
print("="*60)

query = """
{
  projects {
    edges {
      node {
        id
        name
        description
        createdAt
      }
    }
  }
}
"""

result = query_phoenix(query)
if result:
    projects = result.get("data", {}).get("projects", {}).get("edges", [])
    print(f"\nFound {len(projects)} projects:")
    for edge in projects:
        project = edge.get("node", {})
        print(f"  - {project.get('name')} (ID: {project.get('id')})")

# Query 2: Get spans
print("\n" + "="*60)
print("2. Querying Spans")
print("="*60)

query = """
{
  spans(first: 20) {
    edges {
      node {
        spanId
        traceId
        name
        kind
        startTime
        endTime
        attributes
        resource {
          attributes
        }
      }
    }
  }
}
"""

result = query_phoenix(query)
if result:
    print(f"\nRaw result: {json.dumps(result, indent=2)[:500]}")
    
    if "errors" in result:
        print(f"\nGraphQL Errors: {result['errors']}")
    
    data = result.get("data")
    if data is None:
        print("\nNo data returned from query")
        spans = []
    else:
        spans = data.get("spans", {}).get("edges", [])
        print(f"\nFound {len(spans)} spans:")
        
        for i, edge in enumerate(spans[:10], 1):
            span = edge.get("node", {})
            print(f"\n[{i}] Span Details:")
            print(f"  Name: {span.get('name', 'N/A')}")
            print(f"  Kind: {span.get('kind', 'N/A')}")
            print(f"  Span ID: {span.get('spanId', 'N/A')}")
            print(f"  Trace ID: {span.get('traceId', 'N/A')}")
            
            attrs = span.get("attributes", {})
            if attrs:
                print(f"  Attributes ({len(attrs)} items):")
                
                llm_attrs = {k: v for k, v in attrs.items() if k.startswith("llm.")}
                if llm_attrs:
                    print(f"    LLM Attributes:")
                    for k, v in llm_attrs.items():
                        print(f"      - {k}: {v}")
                
                if "llm.prompt" in attrs:
                    print(f"    ✓ LLM Prompt: {attrs['llm.prompt'][:100]}...")
                else:
                    print(f"    ✗ LLM Prompt: NOT FOUND")
                
                if "llm.response" in attrs:
                    print(f"    ✓ LLM Response: {attrs['llm.response'][:100]}...")
                else:
                    print(f"    ✗ LLM Response: NOT FOUND")
                
                print(f"    All attributes:")
                for k, v in list(attrs.items())[:10]:
                    if isinstance(v, str) and len(v) > 50:
                        v = v[:50] + "..."
                    print(f"      - {k}: {v}")
            
            resource = span.get("resource", {})
            if resource:
                resource_attrs = resource.get("attributes", {})
                if resource_attrs:
                    print(f"  Resource:")
                    service_name = resource_attrs.get("service.name", "N/A")
                    print(f"    - service.name: {service_name}")
                    if service_name == "N/A" or service_name == "default":
                        print(f"    ⚠️  Service name is missing or default!")

# Query 3: Get traces
print("\n" + "="*60)
print("3. Querying Traces")
print("="*60)

query = """
{
  traces(first: 10, sort: {col: startTime, dir: desc}) {
    edges {
      node {
        traceId
        projectId
        startTime
        endTime
        spanCount
      }
    }
  }
}
"""

result = query_phoenix(query)
if result:
    traces = result.get("data", {}).get("traces", {}).get("edges", [])
    print(f"\nFound {len(traces)} traces:")
    for edge in traces[:5]:
        trace = edge.get("node", {})
        print(f"  - Trace ID: {trace.get('traceId')}")
        print(f"    Spans: {trace.get('spanCount')}")
        print(f"    Project ID: {trace.get('projectId')}")

# Summary
print("\n" + "="*60)
print("Summary")
print("="*60)

print("\nKey Findings:")
print("1. Check if service.name is set correctly (should be 'cinder' or 'cinder-test')")
print("2. Check if span.name is populated (should be like 'llm.qwen3.5:0.8b.code_generation')")
print("3. Check if span.kind is set (should be 'CLIENT' or 'INTERNAL')")
print("4. Check if LLM prompt and response are recorded in attributes")

print("\n" + "="*60)
print("Recommendations")
print("="*60)

print("\nIf LLM prompt/response are missing:")
print("  1. Check LLMTracer.record_response() is being called")
print("  2. Verify attributes are set on the span")
print("  3. Check if spans are being flushed properly")

print("\nIf service.name is 'default':")
print("  1. Check Resource creation in PhoenixTracer._init_tracer()")
print("  2. Verify TracerProvider is created with resource")
print("  3. Check if resource attributes are exported")
