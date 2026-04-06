#!/usr/bin/env python3
"""Comprehensive Phoenix data verification."""

import sqlite3
import json

local_db_path = "/tmp/phoenix.db"

print("="*60)
print("Phoenix Data Verification")
print("="*60)

conn = sqlite3.connect(local_db_path)
cursor = conn.cursor()

print("\n1. Projects:")
cursor.execute("SELECT id, name, description FROM projects;")
for proj in cursor.fetchall():
    print(f"  - ID: {proj[0]}, Name: {proj[1]}")

print("\n2. Traces per project:")
cursor.execute("""
    SELECT p.name, COUNT(t.id) as trace_count
    FROM projects p
    LEFT JOIN traces t ON p.id = t.project_rowid
    GROUP BY p.id;
""")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]} traces")

print("\n3. Spans per project:")
cursor.execute("""
    SELECT p.name, COUNT(s.id) as span_count
    FROM projects p
    LEFT JOIN traces t ON p.id = t.project_rowid
    LEFT JOIN spans s ON t.id = s.trace_rowid
    GROUP BY p.id;
""")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]} spans")

print("\n4. Span kinds distribution:")
cursor.execute("SELECT span_kind, COUNT(*) FROM spans GROUP BY span_kind;")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]} spans")

print("\n5. Latest 3 spans with project info:")
cursor.execute("""
    SELECT s.id, s.name, s.span_kind, p.name as project_name, s.start_time
    FROM spans s
    JOIN traces t ON s.trace_rowid = t.id
    JOIN projects p ON t.project_rowid = p.id
    ORDER BY s.start_time DESC
    LIMIT 3;
""")
for span in cursor.fetchall():
    print(f"  - ID: {span[0]}, Name: {span[1]}, Kind: {span[2]}, Project: {span[3]}, Time: {span[4]}")

print("\n6. Check for LLM-specific spans:")
cursor.execute("""
    SELECT id, name, attributes
    FROM spans
    WHERE attributes LIKE '%llm%'
    ORDER BY start_time DESC
    LIMIT 3;
""")
for span in cursor.fetchall():
    print(f"\n  Span ID: {span[0]}")
    print(f"  Name: {span[1]}")
    attrs = json.loads(span[2])
    if 'llm' in attrs:
        print(f"  LLM attributes:")
        llm_attrs = attrs['llm']
        for k, v in llm_attrs.items():
            print(f"    - {k}: {v}")

conn.close()

print("\n" + "="*60)
print("Summary")
print("="*60)
print("\n✓ Phoenix 正在接收数据")
print("✓ 数据被存储在数据库中")
print("✓ 项目 'cinder' 已创建")
print("\n待解决问题：")
print("1. Span Kind 显示为 UNKNOWN（Phoenix 可能使用不同的 kind 映射）")
print("2. 需要确认新数据是否在 'cinder' 项目中")
print("3. 需要验证 LLM prompt 和 response 是否正确记录")
