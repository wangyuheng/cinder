#!/usr/bin/env python3
"""Verify trace data in Phoenix."""

import requests
import json

# Check Phoenix health
try:
    response = requests.get("http://localhost:6006/healthz", timeout=5)
    print(f"✓ Phoenix health check: {response.status_code}")
except Exception as e:
    print(f"✗ Phoenix health check failed: {e}")
    exit(1)

# Check Phoenix version
try:
    response = requests.get("http://localhost:6006/version", timeout=5)
    if response.status_code == 200:
        print(f"✓ Phoenix version: {response.text.strip()}")
except:
    pass

# Check if we can query traces
try:
    # Phoenix GraphQL endpoint
    query = """
    {
        spans(first: 10) {
            edges {
                node {
                    spanId
                    operationName
                    startTime
                }
            }
        }
    }
    """
    
    response = requests.post(
        "http://localhost:6006/graphql",
        json={"query": query},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        spans = data.get("data", {}).get("spans", {}).get("edges", [])
        print(f"✓ Found {len(spans)} spans in Phoenix")
        
        if spans:
            print("\nRecent spans:")
            for edge in spans[:5]:
                span = edge.get("node", {})
                print(f"  - {span.get('operationName', 'unknown')} ({span.get('spanId', 'N/A')})")
    else:
        print(f"✗ Failed to query spans: {response.status_code}")
        
except Exception as e:
    print(f"✗ Failed to query Phoenix: {e}")

print("\n✓ Verification complete!")
print("Open http://localhost:6006 to view traces in Phoenix UI")
