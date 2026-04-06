#!/usr/bin/env python3
"""Query latest trace in cinder project."""

import sqlite3
import json

local_db_path = "/tmp/phoenix.db"

print("="*60)
print("Latest Trace in Cinder Project")
print("="*60)

conn = sqlite3.connect(local_db_path)
cursor = conn.cursor()

# Query latest trace in cinder project
cursor.execute("""
    SELECT t.id, t.trace_id, t.start_time, t.end_time
    FROM traces t
    JOIN projects p ON t.project_rowid = p.id
    WHERE p.name = 'cinder'
    ORDER BY t.start_time DESC
    LIMIT 1;
""")

trace = cursor.fetchone()
if trace:
    trace_id, trace_id_str, start_time, end_time = trace
    print(f"\nTrace ID: {trace_id_str}")
    print(f"Start Time: {start_time}")
    print(f"End Time: {end_time}")
    
    # Query spans in this trace
    print(f"\nSpans in this trace:")
    cursor.execute("""
        SELECT id, span_id, name, span_kind, start_time, end_time, attributes
        FROM spans
        WHERE trace_rowid = ?
        ORDER BY start_time;
    """, (trace_id,))
    
    spans = cursor.fetchall()
    print(f"Found {len(spans)} spans:")
    
    for i, span in enumerate(spans, 1):
        span_id, span_id_str, name, kind, start_time, end_time, attrs_json = span
        print(f"\n[{i}] Span:")
        print(f"  Span ID: {span_id_str}")
        print(f"  Name: {name if name else 'EMPTY'}")
        print(f"  Kind: {kind if kind else 'EMPTY'}")
        print(f"  Start Time: {start_time}")
        print(f"  End Time: {end_time}")
        
        if attrs_json:
            try:
                attrs = json.loads(attrs_json)
                print(f"  Attributes ({len(attrs)} items):")
                
                # Check for LLM attributes
                llm_attrs = {k: v for k, v in attrs.items() if k.startswith("llm.")}
                if llm_attrs:
                    print(f"    LLM Attributes:")
                    for k, v in llm_attrs.items():
                        print(f"      - {k}: {v}")
                
                # Check for cinder attributes
                cinder_attrs = {k: v for k, v in attrs.items() if k.startswith("cinder.")}
                if cinder_attrs:
                    print(f"    Cinder Attributes:")
                    for k, v in cinder_attrs.items():
                        print(f"      - {k}: {v}")
                
                # Show all attributes
                print(f"    All attributes:")
                for k, v in list(attrs.items())[:10]:
                    if isinstance(v, str) and len(v) > 50:
                        v = v[:50] + "..."
                    elif isinstance(v, dict):
                        v = json.dumps(v, ensure_ascii=False)[:50] + "..."
                    print(f"      - {k}: {v}")
            except Exception as e:
                print(f"  Attributes: Error parsing - {e}")
        else:
            print(f"  Attributes: EMPTY")
else:
    print("No traces found in cinder project")

conn.close()

print("\n" + "="*60)
print("Analysis")
print("="*60)
print("\n如果 span name 或 kind 为空，说明：")
print("1. OpenTelemetry span 创建时没有正确设置这些字段")
print("2. 或者 Phoenix 没有正确接收/存储这些字段")
print("3. 需要检查 LLMTracer 的实现")
