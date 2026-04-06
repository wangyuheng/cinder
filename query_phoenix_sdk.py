#!/usr/bin/env python3
"""Query Phoenix using Python SDK and check LLM attributes."""

import sys
sys.path.insert(0, "/Users/wangyuheng/code/github.com/wangyuheng/cinder")

from phoenix.session.client import Client
from phoenix.trace.dsl import SpanQuery
import pandas as pd

print("="*60)
print("Querying Phoenix via Python SDK")
print("="*60)

try:
    client = Client(endpoint="http://localhost:6006")
    
    print("\n1. Getting all spans...")
    query = SpanQuery()
    spans_df = client.query_spans(query)
    
    if not spans_df.empty:
        print(f"Found {len(spans_df)} spans")
        
        print("\nDataFrame columns:")
        cols = spans_df.columns.tolist()
        print(cols)
        
        print("\nLLM-related columns:")
        llm_cols = [col for col in cols if 'llm' in col.lower()]
        print(llm_cols)
        
        print("\nFirst 5 LLM spans:")
        llm_spans = spans_df[spans_df['name'].str.startswith('llm.')]
        
        for i, (idx, row) in enumerate(llm_spans.head(5).iterrows(), 1):
            print(f"\n[{i}] Span:")
            print(f"  Name: {row.get('name', 'N/A')}")
            print(f"  Kind: {row.get('span_kind', 'N/A')}")
            print(f"  Start Time: {row.get('start_time', 'N/A')}")
            
            print(f"  LLM Attributes:")
            
            # Check for llm.input_messages
            if 'attributes.llm' in row:
                llm_attrs = row['attributes.llm']
                print(f"    attributes.llm: {llm_attrs}")
            
            # Check for llm.system
            if 'attributes.llm.system' in row:
                print(f"    ✓ llm.system: {row['attributes.llm.system']}")
            
            # Check for all llm columns
            for col in llm_cols:
                if col in row and pd.notna(row[col]):
                    value = row[col]
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"    {col}: {value}")
    else:
        print("No spans found")
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("\n✓ Phoenix 正常工作，查询到数据")
    print("✓ 检查 LLM attributes 是否包含 input/output messages")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
