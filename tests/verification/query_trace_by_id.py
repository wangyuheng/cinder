#!/usr/bin/env python3
"""Query specific trace by trace ID via Phoenix SDK."""

import sys
sys.path.insert(0, "/Users/wangyuheng/code/github.com/wangyuheng/cinder")

from phoenix.session.client import Client
from phoenix.trace.dsl import SpanQuery
import pandas as pd

trace_id = "46159675dda09a29091acb122120838e"

print("="*60)
print(f"Querying Trace: {trace_id}")
print("="*60)

try:
    client = Client(endpoint="http://localhost:6006")
    
    print("\n1. Getting all spans...")
    query = SpanQuery()
    all_spans_df = client.query_spans(query)
    
    if not all_spans_df.empty:
        print(f"Total spans: {len(all_spans_df)}")
        
        # Filter spans by trace_id
        print(f"\n2. Filtering spans by trace_id: {trace_id}")
        trace_spans = all_spans_df[all_spans_df['context.trace_id'] == trace_id]
        
        if not trace_spans.empty:
            print(f"Found {len(trace_spans)} spans in this trace")
            
            print("\n3. Span hierarchy:")
            for i, (idx, row) in enumerate(trace_spans.iterrows(), 1):
                name = row.get('name', 'N/A')
                kind = row.get('span_kind', 'N/A')
                parent_id = row.get('parent_id', None)
                indent = "  " if parent_id else ""
                print(f"{indent}[{i}] {name} (Kind: {kind})")
                
                # Check for agent attributes
                agent_attrs = {k: v for k, v in row.items() if 'agent' in k.lower() and pd.notna(v)}
                if agent_attrs:
                    print(f"{indent}  Agent attributes:")
                    for k, v in agent_attrs.items():
                        print(f"{indent}    - {k}: {v}")
        else:
            print(f"No spans found with trace_id: {trace_id}")
            
            # Show all trace IDs
            print("\nAvailable trace IDs:")
            trace_ids = all_spans_df['context.trace_id'].unique()
            for tid in trace_ids[:10]:
                print(f"  - {tid}")
    else:
        print("No spans found in database")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
