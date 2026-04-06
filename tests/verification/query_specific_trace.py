#!/usr/bin/env python3
"""Query specific trace by trace ID."""

import sqlite3
import json

local_db_path = "/tmp/phoenix.db"
trace_id = "7c46a638feb2f30dbab7d68eaacd7dee"

print("="*60)
print(f"Querying Trace: {trace_id}")
print("="*60)

conn = sqlite3.connect(local_db_path)
cursor = conn.cursor()

# Query trace
print("\n1. Trace Info:")
cursor.execute("""
    SELECT t.id, t.trace_id, t.start_time, t.end_time, p.name as project_name
    FROM traces t
    JOIN projects p ON t.project_rowid = p.id
    WHERE t.trace_id = ?;
""", (trace_id,))

trace = cursor.fetchone()
if trace:
    print(f"  Trace ID: {trace[1]}")
    print(f"  Project: {trace[4]}")
    print(f"  Start Time: {trace[2]}")
    print(f"  End Time: {trace[3]}")
    
    trace_rowid = trace[0]
    
    # Query spans in this trace
    print(f"\n2. Spans in this trace:")
    cursor.execute("""
        SELECT id, span_id, name, span_kind, start_time, end_time, attributes
        FROM spans
        WHERE trace_rowid = ?
        ORDER BY start_time;
    """, (trace_rowid,))
    
    spans = cursor.fetchall()
    print(f"  Found {len(spans)} spans:")
    
    for i, span in enumerate(spans, 1):
        span_id, span_id_str, name, kind, start_time, end_time, attrs_json = span
        print(f"\n  [{i}] Span:")
        print(f"    ID: {span_id}")
        print(f"    Span ID: {span_id_str}")
        print(f"    Name: {name if name else 'EMPTY'}")
        print(f"    Kind: {kind if kind else 'EMPTY'}")
        print(f"    Start Time: {start_time}")
        print(f"    End Time: {end_time}")
        
        if attrs_json:
            try:
                attrs = json.loads(attrs_json)
                print(f"    Attributes ({len(attrs)} items):")
                for k, v in list(attrs.items())[:20]:
                    if isinstance(v, str) and len(v) > 100:
                        v = v[:100] + "..."
                    elif isinstance(v, dict):
                        v = json.dumps(v, ensure_ascii=False)[:100] + "..."
                    print(f"      - {k}: {v}")
            except Exception as e:
                print(f"    Attributes: Error parsing - {e}")
        else:
            print(f"    Attributes: EMPTY")
else:
    print(f"  ✗ Trace not found")

conn.close()

print("\n" + "="*60)
print("Analysis")
print("="*60)
print("\n问题分析：")
print("1. 检查 span name 是否为空")
print("2. 检查 span kind 是否为空")
print("3. 检查 attributes 是否为空")
print("4. 如果都为空，说明 OpenTelemetry span 创建有问题")
