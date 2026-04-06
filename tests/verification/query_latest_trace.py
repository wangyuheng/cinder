#!/usr/bin/env python3
"""Query latest trace from database."""

import sqlite3
import json

db_path = "/tmp/phoenix.db"

print("="*60)
print("Querying Latest Trace")
print("="*60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get latest trace
cursor.execute("""
    SELECT t.id, t.trace_id, t.start_time
    FROM traces t
    JOIN projects p ON t.project_rowid = p.id
    WHERE p.name = 'cinder'
    ORDER BY t.start_time DESC
    LIMIT 1;
""")

trace = cursor.fetchone()
if trace:
    trace_rowid, trace_id_str, start_time = trace
    print(f"\nLatest Trace ID: {trace_id_str}")
    print(f"Start Time: {start_time}")
    
    # Get spans in this trace
    cursor.execute("""
        SELECT span_id, name, span_kind, parent_id, attributes
        FROM spans
        WHERE trace_rowid = ?
        ORDER BY start_time;
    """, (trace_rowid,))
    
    spans = cursor.fetchall()
    print(f"\nFound {len(spans)} spans:")
    
    for i, (span_id, name, kind, parent_id, attrs_json) in enumerate(spans, 1):
        print(f"\n[{i}] {name}")
        print(f"  Kind: {kind}")
        print(f"  Parent: {'ROOT' if not parent_id else parent_id}")
        
        if attrs_json:
            attrs = json.loads(attrs_json)
            
            # Check for openinference.span.kind
            oi_kind = attrs.get('openinference', {}).get('span', {}).get('kind', 'N/A')
            print(f"  OpenInference Kind: {oi_kind}")
            
            # Check for agent attributes
            agent_attrs = attrs.get('agent', {})
            if agent_attrs:
                print(f"  Agent attributes: {agent_attrs}")

conn.close()
