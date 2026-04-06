#!/usr/bin/env python3
"""Query Phoenix SQLite database directly."""

import sqlite3
import json

local_db_path = "/tmp/phoenix.db"

print("="*60)
print("Querying Phoenix Database")
print("="*60)

conn = sqlite3.connect(local_db_path)
cursor = conn.cursor()

print("\n1. Count records in each table:")
tables = ["projects", "traces", "spans"]
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table};")
    count = cursor.fetchone()[0]
    print(f"  - {table}: {count} records")

print("\n2. Projects:")
cursor.execute("SELECT id, name, description FROM projects;")
projects = cursor.fetchall()
for proj in projects:
    print(f"  - ID: {proj[0]}, Name: {proj[1]}, Description: {proj[2]}")

print("\n3. Traces:")
cursor.execute("SELECT * FROM traces LIMIT 5;")
traces = cursor.fetchall()
if traces:
    cursor.execute("PRAGMA table_info(traces);")
    columns = [col[1] for col in cursor.fetchall()]
    for trace in traces:
        print(f"  - {dict(zip(columns, trace))}")
else:
    print("  No traces found")

print("\n4. Spans:")
cursor.execute("SELECT * FROM spans LIMIT 5;")
spans = cursor.fetchall()
if spans:
    cursor.execute("PRAGMA table_info(spans);")
    columns = [col[1] for col in cursor.fetchall()]
    for i, span in enumerate(spans, 1):
        print(f"\n  [{i}] Span:")
        span_dict = dict(zip(columns, span))
        print(f"    ID: {span_dict.get('id')}")
        print(f"    Name: {span_dict.get('name')}")
        print(f"    Kind: {span_dict.get('span_kind')}")
        print(f"    Span ID: {span_dict.get('span_id')}")
        print(f"    Trace ID: {span_dict.get('trace_rowid')}")
        
        if span_dict.get('attributes'):
            try:
                attrs = json.loads(span_dict['attributes'])
                print(f"    Attributes ({len(attrs)} items):")
                for k, v in list(attrs.items())[:15]:
                    print(f"      - {k}: {v}")
            except Exception as e:
                print(f"    Attributes: {span_dict['attributes'][:200]}")
else:
    print("  No spans found")

conn.close()

print("\n" + "="*60)
print("Summary")
print("="*60)
print("\n如果 traces 和 spans 表为空，说明：")
print("  1. OpenTelemetry exporter 没有成功发送数据到 Phoenix")
print("  2. 或者数据发送了但 Phoenix 没有正确接收")
print("  3. 需要检查 OpenTelemetry 配置和 Phoenix 的 OTLP 端点")
