#!/usr/bin/env python3
"""Check all recent spans."""

import sqlite3
import json
from datetime import datetime

local_db_path = "/tmp/phoenix.db"

conn = sqlite3.connect(local_db_path)
cursor = conn.cursor()

print("="*60)
print("All Recent Spans (Latest 10)")
print("="*60)

cursor.execute("""
    SELECT s.id, s.name, s.span_kind, s.start_time, p.name as project_name
    FROM spans s
    JOIN traces t ON s.trace_rowid = t.id
    JOIN projects p ON t.project_rowid = p.id
    ORDER BY s.start_time DESC
    LIMIT 10;
""")

spans = cursor.fetchall()
for span in spans:
    span_id, name, kind, start_time, project_name = span
    print(f"\nID: {span_id}, Name: {name}, Kind: {kind}, Project: {project_name}")
    print(f"  Start Time: {start_time}")

conn.close()
