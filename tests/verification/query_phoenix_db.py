#!/usr/bin/env python3
"""Query Phoenix SQLite database directly."""

import sqlite3
import os
import json
import subprocess

print("="*60)
print("Copying Phoenix database from container")
print("="*60)

db_path_in_container = "/root/.phoenix/phoenix.db"
local_db_path = "/tmp/phoenix.db"

print(f"Copying from cinder-phoenix:{db_path_in_container} to {local_db_path}")

result = subprocess.run(
    ["docker", "cp", f"cinder-phoenix:{db_path_in_container}", local_db_path],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"Error copying database: {result.stderr}")
    print("\nTrying to list files in container...")
    result = subprocess.run(
        ["docker", "exec", "cinder-phoenix", "ls", "-la", "/root/.phoenix/"],
        capture_output=True,
        text=True
    )
    print(f"Files in /root/.phoenix/: {result.stdout}")
    print(f"Error: {result.stderr}")
    exit(1)

print(f"✓ Database copied successfully")

print("\n" + "="*60)
print("Querying Database")
print("="*60)

try:
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    
    print("\n1. Tables in database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n2. Projects:")
    try:
        cursor.execute("SELECT * FROM projects LIMIT 10;")
        projects = cursor.fetchall()
        cursor.execute("PRAGMA table_info(projects);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"  Columns: {columns}")
        for proj in projects:
            print(f"  - {proj}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n3. Traces:")
    try:
        cursor.execute("SELECT * FROM traces LIMIT 10;")
        traces = cursor.fetchall()
        cursor.execute("PRAGMA table_info(traces);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"  Columns: {columns}")
        for trace in traces[:5]:
            print(f"  - {trace}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n4. Spans:")
    try:
        cursor.execute("SELECT * FROM spans LIMIT 10;")
        spans = cursor.fetchall()
        cursor.execute("PRAGMA table_info(spans);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"  Columns: {columns}")
        
        for i, span in enumerate(spans[:5], 1):
            print(f"\n  [{i}] Span:")
            for j, col in enumerate(columns):
                value = span[j]
                if col == "attributes" and value:
                    try:
                        attrs = json.loads(value)
                        print(f"    {col}:")
                        for k, v in list(attrs.items())[:10]:
                            print(f"      - {k}: {v}")
                    except:
                        print(f"    {col}: {str(value)[:200]}")
                else:
                    print(f"    {col}: {value}")
    except Exception as e:
        print(f"  Error: {e}")
    
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
