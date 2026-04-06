#!/usr/bin/env python3
"""Query all traces to find the latest one."""

import sqlite3
import json

local_db_path = "/tmp/phoenix.db"

print("="*60)
print("All Traces in Database")
print("="*60)

conn = sqlite3.connect(local_db_path)
cursor = conn.cursor()

# Query all traces
cursor.execute("""
    SELECT t.id, t.trace_id, t.start_time, p.name as project_name
    FROM traces t
    JOIN projects p ON t.project_rowid = p.id
    ORDER BY t.start_time DESC
    LIMIT 20;
""")

traces = cursor.fetchall()
print(f"\nFound {len(traces)} traces (latest 20):")

for i, trace in enumerate(traces, 1):
    trace_id, trace_id_str, start_time, project_name = trace
    print(f"\n[{i}] Trace:")
    print(f"  ID: {trace_id}")
    print(f"  Trace ID: {trace_id_str}")
    print(f"  Project: {project_name}")
    print(f"  Start Time: {start_time}")

# Check if the specific trace exists
target_trace_id = "7c46a638feb2f30dbab7d68eaacd7dee"
cursor.execute("SELECT COUNT(*) FROM traces WHERE trace_id = ?;", (target_trace_id,))
count = cursor.fetchone()[0]
print(f"\n\nTarget trace {target_trace_id}: {'FOUND' if count > 0 else 'NOT FOUND'}")

# Query all spans
cursor.execute("SELECT COUNT(*) FROM spans;")
span_count = cursor.fetchone()[0]
print(f"\nTotal spans in database: {span_count}")

conn.close()
