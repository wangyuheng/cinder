#!/usr/bin/env python3
"""Explore Phoenix API endpoints."""

import requests
import json

PHOENIX_URL = "http://localhost:6006"

endpoints = [
    "/",
    "/api",
    "/api/v1",
    "/graphql",
    "/v1/traces",
    "/healthz",
]

print("="*60)
print("Exploring Phoenix API Endpoints")
print("="*60)

for endpoint in endpoints:
    url = f"{PHOENIX_URL}{endpoint}"
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            content = response.text[:500]
            print(f"  Content: {content}")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")

print("\n" + "="*60)
print("Trying POST to /v1/traces")
print("="*60)

try:
    response = requests.post(
        f"{PHOENIX_URL}/v1/traces",
        json={"test": "data"},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")
