#!/usr/bin/env python3
"""Query specific trace by trace ID from database."""

import sqlite3
import json

trace_id = "46159675dda09a29091acb122120838e"
db_path = "/tmp/phoenix.db"

print("="*60)
print(f"Querying Trace: {trace_id}")
print("="*60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if trace exists
cursor.execute("SELECT COUNT(*) FROM traces WHERE trace_id = ?;", (trace_id,))
count = cursor.fetchone()[0]

if count > 0:
    print(f"\n✓ Found trace in database")
    
    # Get trace info
    cursor.execute("""
        SELECT t.id, t.trace_id, t.start_time, p.name as project_name
        FROM traces t
        JOIN projects p ON t.project_rowid = p.id
        WHERE t.trace_id = ?;
    """, (trace_id,))
    
    trace = cursor.fetchone()
    if trace:
        trace_rowid, trace_id_str, start_time, project_name = trace
        print(f"  Trace ID: {trace_id_str}")
        print(f"  Project: {project_name}")
        print(f"  Start Time: {start_time}")
        
        # Get spans in this trace
        print(f"\n2. Spans in this trace:")
        cursor.execute("""
            SELECT id, span_id, name, span_kind, parent_id, start_time, attributes
            FROM spans
            WHERE trace_rowid = ?
            ORDER BY start_time;
        """, (trace_rowid,))
        
        spans = cursor.fetchall()
        print(f"  Found {len(spans)} spans:")
        
        for i, span in enumerate(spans, 1):
            span_id, span_id_str, name, kind, parent_id, start_time, attrs_json = span
            indent = "  " if parent_id else ""
            print(f"\n{indent}[{i}] Span:")
            print(f"{indent}  Name: {name}")
            print(f"{indent}  Kind: {kind}")
            print(f"{indent}  Parent ID: {parent_id if parent_id else 'ROOT'}")
            print(f"{indent}  Start Time: {start_time}")
            
            if attrs_json:
                attrs = json.loads(attrs_json)
                
                # Check for agent attributes
                agent_attrs = {k: v for k, v in attrs.items() if 'agent' in k.lower()}
                if agent_attrs:
                    print(f"{indent}  Agent attributes:")
                    for k, v in agent_attrs.items():
                        print(f"{indent}    - {k}: {v}")
                
                # Check for openinference.span.kind
                if 'openinference' in attrs:
                    print(f"{indent}  OpenInference:")
                    print(f"{indent}    - span.kind: {attrs['openinference'].get('span', {}).get('kind', 'N/A')}")
else:
    print(f"\n✗ Trace not found in database")
    
    # Get latest traces
    print(f"\nLatest 10 traces:")
    cursor.execute("""
        SELECT t.trace_id, t.start_time, p.name as project_name
        FROM traces t
        JOIN projects p ON t.project_rowid = p.id
        ORDER BY t.start_time DESC
        LIMIT 10;
    """)
    
    traces = cursor.fetchall()
    for trace_id_str, start_time, project_name in traces:
        print(f"  - {trace_id_str} ({project_name}) at {start_time}")

conn.close()
