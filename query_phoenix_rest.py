#!/usr/bin/env python3
"""Query Phoenix data via REST API."""

import requests
import json

PHOENIX_URL = "http://localhost:6006"

def get_projects():
    """Get all projects via REST API."""
    response = requests.get(f"{PHOENIX_URL}/api/v1/projects", timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting projects: {response.status_code}")
        print(response.text)
        return None

def get_traces(project_id):
    """Get traces for a project via REST API."""
    response = requests.get(
        f"{PHOENIX_URL}/api/v1/projects/{project_id}/traces",
        timeout=10
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting traces: {response.status_code}")
        print(response.text)
        return None

def get_spans(project_id, trace_id=None):
    """Get spans for a project via REST API."""
    url = f"{PHOENIX_URL}/api/v1/projects/{project_id}/spans"
    if trace_id:
        url += f"?trace_id={trace_id}"
    
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting spans: {response.status_code}")
        print(response.text)
        return None

print("="*60)
print("1. Querying Projects via REST API")
print("="*60)

projects = get_projects()
if projects:
    print(f"\nProjects data: {json.dumps(projects, indent=2)[:500]}")
    
    if isinstance(projects, dict) and "data" in projects:
        project_list = projects["data"]
    elif isinstance(projects, list):
        project_list = projects
    else:
        project_list = [projects] if projects else []
    
    print(f"\nFound {len(project_list)} projects:")
    for proj in project_list:
        if isinstance(proj, dict):
            print(f"  - {proj.get('name', 'N/A')} (ID: {proj.get('id', 'N/A')})")

print("\n" + "="*60)
print("2. Querying Traces via REST API")
print("="*60)

project_id = 1
traces = get_traces(project_id)
if traces:
    print(f"\nTraces data: {json.dumps(traces, indent=2)[:500]}")
    
    if isinstance(traces, dict) and "data" in traces:
        trace_list = traces["data"]
    elif isinstance(traces, list):
        trace_list = traces
    else:
        trace_list = [traces] if traces else []
    
    print(f"\nFound {len(trace_list)} traces:")
    for trace in trace_list[:5]:
        if isinstance(trace, dict):
            print(f"  - Trace ID: {trace.get('trace_id', trace.get('id', 'N/A'))}")
            print(f"    Spans: {trace.get('span_count', 'N/A')}")

print("\n" + "="*60)
print("3. Querying Spans via REST API")
print("="*60)

spans = get_spans(project_id)
if spans:
    print(f"\nSpans data: {json.dumps(spans, indent=2)[:1000]}")
    
    if isinstance(spans, dict) and "data" in spans:
        span_list = spans["data"]
    elif isinstance(spans, list):
        span_list = spans
    else:
        span_list = [spans] if spans else []
    
    print(f"\nFound {len(span_list)} spans:")
    for i, span in enumerate(span_list[:5], 1):
        if isinstance(span, dict):
            print(f"\n[{i}] Span Details:")
            print(f"  Name: {span.get('name', 'N/A')}")
            print(f"  Kind: {span.get('kind', 'N/A')}")
            print(f"  Span ID: {span.get('span_id', span.get('id', 'N/A'))}")
            print(f"  Trace ID: {span.get('trace_id', 'N/A')}")
            
            attrs = span.get("attributes", {})
            if attrs:
                print(f"  Attributes:")
                for k, v in list(attrs.items())[:10]:
                    if isinstance(v, str) and len(v) > 50:
                        v = v[:50] + "..."
                    print(f"    - {k}: {v}")

print("\n" + "="*60)
print("Summary")
print("="*60)
print("\nIf no data found:")
print("  1. Check if Phoenix is running: docker ps | grep phoenix")
print("  2. Check if traces were sent: look for logs in cinder execution")
print("  3. Verify OpenTelemetry exporter is configured correctly")
