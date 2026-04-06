#!/usr/bin/env python3
"""Verify OpenInference attributes in Phoenix database."""

import sqlite3
import json

local_db_path = "/tmp/phoenix.db"

print("="*60)
print("Verifying OpenInference Attributes in Phoenix")
print("="*60)

conn = sqlite3.connect(local_db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT s.id, s.name, s.span_kind, s.attributes, s.start_time
    FROM spans s
    JOIN traces t ON s.trace_rowid = t.id
    JOIN projects p ON t.project_rowid = p.id
    WHERE p.name = 'cinder'
    ORDER BY s.start_time DESC
    LIMIT 1;
""")

span = cursor.fetchone()
if span:
    span_id, name, kind, attrs_json, start_time = span
    print(f"\nLatest Span in Cinder Project:")
    print(f"  ID: {span_id}")
    print(f"  Name: {name}")
    print(f"  Kind: {kind}")
    print(f"  Start Time: {start_time}")
    
    if attrs_json:
        attrs = json.loads(attrs_json)
        print(f"\n  Attributes:")
        
        if "openinference.span.kind" in attrs:
            print(f"    ✓ openinference.span.kind: {attrs['openinference.span.kind']}")
        else:
            print(f"    ✗ openinference.span.kind: NOT FOUND")
        
        if "llm.input_messages" in attrs:
            print(f"    ✓ llm.input_messages:")
            input_messages = attrs["llm.input_messages"]
            if isinstance(input_messages, str):
                input_messages = json.loads(input_messages)
            for msg in input_messages:
                content = msg.get('content', '')
                print(f"      - role: {msg.get('role')}, content: {content[:50]}...")
        else:
            print(f"    ✗ llm.input_messages: NOT FOUND")
        
        if "llm.output_messages" in attrs:
            print(f"    ✓ llm.output_messages:")
            output_messages = attrs["llm.output_messages"]
            if isinstance(output_messages, str):
                output_messages = json.loads(output_messages)
            for msg in output_messages:
                content = msg.get('content', '')
                print(f"      - role: {msg.get('role')}, content: {content[:50]}...")
        else:
            print(f"    ✗ llm.output_messages: NOT FOUND")
        
        token_attrs = {k: v for k, v in attrs.items() if k.startswith("llm.token_count.")}
        if token_attrs:
            print(f"    ✓ Token counts:")
            for k, v in token_attrs.items():
                print(f"      - {k}: {v}")
        else:
            print(f"    ✗ Token counts: NOT FOUND")
        
        print(f"\n  All attributes:")
        for k, v in list(attrs.items())[:20]:
            if isinstance(v, str) and len(v) > 100:
                v = v[:100] + "..."
            print(f"    - {k}: {v}")
else:
    print("No spans found in cinder project")

conn.close()

print("\n" + "="*60)
print("Summary")
print("="*60)
print("\n✓ 如果所有关键属性都存在，说明 OpenInference 集成成功")
print("✓ Phoenix UI 应该能正确显示 LLM prompt 和 response")
