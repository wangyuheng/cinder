#!/usr/bin/env python3
"""Check all spans in Phoenix database."""

import sqlite3
from datetime import datetime

db_path = "/tmp/phoenix.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("Phoenix Database Summary")
print("="*60)

# Count spans
cursor.execute("SELECT COUNT(*) FROM spans;")
span_count = cursor.fetchone()[0]
print(f"\nTotal spans: {span_count}")

# Count traces
cursor.execute("SELECT COUNT(*) FROM traces;")
trace_count = cursor.fetchone()[0]
print(f"Total traces: {trace_count}")

# Get latest 5 spans
print(f"\nLatest 5 spans:")
cursor.execute("""
    SELECT s.id, s.name, s.span_kind, s.start_time, p.name as project_name
    FROM spans s
    JOIN traces t ON s.trace_rowid = t.id
    JOIN projects p ON t.project_rowid = p.id
    ORDER BY s.start_time DESC
    LIMIT 5;
""")

for row in cursor.fetchall():
    span_id, name, kind, start_time, project_name = row
    print(f"  ID: {span_id}, Name: {name}, Kind: {kind}, Project: {project_name}")
    print(f"    Start Time: {start_time}")

# Check for spans with openinference.span.kind
cursor.execute("""
    SELECT COUNT(*) FROM spans
    WHERE attributes LIKE '%openinference.span.kind%';
""")
openinference_count = cursor.fetchone()[0]
print(f"\nSpans with openinference.span.kind: {openinference_count}")

# Check for spans with llm.input_messages
cursor.execute("""
    SELECT COUNT(*) FROM spans
    WHERE attributes LIKE '%llm.input_messages%';
""")
input_messages_count = cursor.fetchone()[0]
print(f"Spans with llm.input_messages: {input_messages_count}")

conn.close()
