#!/usr/bin/env python3
"""Check latest spans in Phoenix database."""

import sqlite3
import json

local_db_path = "/tmp/phoenix.db"

conn = sqlite3.connect(local_db_path)
cursor = conn.cursor()

print("="*60)
print("Latest Spans in Phoenix Database")
print("="*60)

cursor.execute("""
    SELECT id, name, span_kind, span_id, attributes, start_time
    FROM spans
    ORDER BY id DESC
    LIMIT 5;
""")

spans = cursor.fetchall()

for i, span in enumerate(spans, 1):
    span_id, name, kind, span_id_str, attrs_json, start_time = span
    print(f"\n[{i}] Span ID: {span_id}")
    print(f"  Name: {name}")
    print(f"  Kind: {kind}")
    print(f"  Span ID: {span_id_str}")
    print(f"  Start Time: {start_time}")
    
    if attrs_json:
        try:
            attrs = json.loads(attrs_json)
            print(f"  Attributes:")
            
            # Check for service.name
            if "service.name" in attrs:
                print(f"    ✓ service.name: {attrs['service.name']}")
            else:
                print(f"    ✗ service.name: NOT FOUND")
            
            # Check for llm attributes
            llm_attrs = {k: v for k, v in attrs.items() if k.startswith("llm.")}
            if llm_attrs:
                print(f"    LLM Attributes:")
                for k, v in llm_attrs.items():
                    print(f"      - {k}: {v}")
            
            # Show all attributes
            print(f"    All attributes:")
            for k, v in list(attrs.items())[:10]:
                print(f"      - {k}: {v}")
        except Exception as e:
            print(f"  Attributes: {attrs_json[:200]}")

conn.close()

print("\n" + "="*60)
print("Analysis")
print("="*60)
print("\n问题分析：")
print("1. Span Kind 为 UNKNOWN：需要检查 OpenTelemetry span kind 是否正确设置")
print("2. 项目为 default：需要检查 service.name 是否正确传递到 Phoenix")
print("\n解决方案：")
print("1. 确保 span 创建时设置正确的 kind")
print("2. 确保使用 arize-phoenix-otel 包来正确设置项目名称")
