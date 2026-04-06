#!/usr/bin/env python3
"""Check latest span attributes in detail."""

import sqlite3
import json

db_path = "/tmp/phoenix.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("Latest Span Attributes (Detailed)")
print("="*60)

# Get latest LLM span
cursor.execute("""
    SELECT s.id, s.name, s.span_kind, s.attributes, s.start_time
    FROM spans s
    JOIN traces t ON s.trace_rowid = t.id
    JOIN projects p ON t.project_rowid = p.id
    WHERE p.name = 'cinder' AND s.name LIKE 'llm.%'
    ORDER BY s.start_time DESC
    LIMIT 1;
""")

span = cursor.fetchone()
if span:
    span_id, name, kind, attrs_json, start_time = span
    print(f"\nLatest LLM Span:")
    print(f"  ID: {span_id}")
    print(f"  Name: {name}")
    print(f"  Kind: {kind}")
    print(f"  Start Time: {start_time}")
    
    if attrs_json:
        attrs = json.loads(attrs_json)
        print(f"\n  All attributes ({len(attrs)} items):")
        for k, v in sorted(attrs.items()):
            if isinstance(v, str) and len(v) > 100:
                v = v[:100] + "..."
            print(f"    - {k}: {v}")

# Get latest phase span
cursor.execute("""
    SELECT s.id, s.name, s.span_kind, s.attributes, s.start_time
    FROM spans s
    JOIN traces t ON s.trace_rowid = t.id
    JOIN projects p ON t.project_rowid = p.id
    WHERE p.name = 'cinder' AND s.name LIKE 'agent.phase.%'
    ORDER BY s.start_time DESC
    LIMIT 1;
""")

span = cursor.fetchone()
if span:
    span_id, name, kind, attrs_json, start_time = span
    print(f"\nLatest Phase Span:")
    print(f"  ID: {span_id}")
    print(f"  Name: {name}")
    print(f"  Kind: {kind}")
    print(f"  Start Time: {start_time}")
    
    if attrs_json:
        attrs = json.loads(attrs_json)
        print(f"\n  All attributes ({len(attrs)} items):")
        for k, v in sorted(attrs.items()):
            print(f"    - {k}: {v}")

conn.close()
