"""
Trace Exporter - Exports trace data in various formats.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter


class TraceExporter:
    """Exports trace data in various formats."""
    
    def __init__(self, export_dir: Optional[Path] = None):
        """
        Initialize Trace Exporter.
        
        Args:
            export_dir: Directory to export traces to
        """
        self.export_dir = export_dir or Path.home() / ".cinder" / "traces"
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_json(
        self,
        spans: list[ReadableSpan],
        output_file: Optional[Path] = None,
    ) -> Path:
        """
        Export traces to JSON format.
        
        Args:
            spans: List of spans to export
            output_file: Output file path (optional)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.export_dir / f"trace_{timestamp}.json"
        
        traces_data = []
        for span in spans:
            trace_data = {
                "trace_id": format(span.context.trace_id, "032x"),
                "span_id": format(span.context.span_id, "016x"),
                "parent_span_id": format(span.parent.span_id, "016x") if span.parent else None,
                "operation_name": span.name,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "attributes": dict(span.attributes) if span.attributes else {},
                "events": [
                    {
                        "name": event.name,
                        "timestamp": event.timestamp,
                        "attributes": dict(event.attributes) if event.attributes else {},
                    }
                    for event in span.events
                ],
                "status": {
                    "code": span.status.status_code.name,
                    "description": span.status.description,
                },
            }
            traces_data.append(trace_data)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(traces_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def export_to_otlp(
        self,
        spans: list[ReadableSpan],
        output_file: Optional[Path] = None,
    ) -> Path:
        """
        Export traces to OTLP format.
        
        Args:
            spans: List of spans to export
            output_file: Output file path (optional)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.export_dir / f"trace_{timestamp}.otlp.json"
        
        resource_spans = []
        
        for span in spans:
            span_data = {
                "traceId": format(span.context.trace_id, "032x"),
                "spanId": format(span.context.span_id, "016x"),
                "parentSpanId": format(span.parent.span_id, "016x") if span.parent else "",
                "name": span.name,
                "kind": span.kind.value,
                "startTimeUnixNano": span.start_time,
                "endTimeUnixNano": span.end_time,
                "attributes": [
                    {"key": k, "value": {"stringValue": str(v)}}
                    for k, v in (span.attributes or {}).items()
                ],
                "status": {
                    "code": span.status.status_code.value,
                    "message": span.status.description or "",
                },
            }
            resource_spans.append(span_data)
        
        otlp_data = {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": "cinder-cli"}}
                        ]
                    },
                    "scopeSpans": [
                        {
                            "scope": {"name": "cinder_cli"},
                            "spans": resource_spans,
                        }
                    ],
                }
            ]
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(otlp_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def export_batch(
        self,
        spans: list[ReadableSpan],
        format: str = "json",
    ) -> Path:
        """
        Export all traces to a compressed file.
        
        Args:
            spans: List of spans to export
            format: Export format ("json" or "otlp")
            
        Returns:
            Path to exported file
        """
        import tarfile
        import tempfile
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.export_dir / f"traces_{timestamp}.tar.gz"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            if format == "json":
                trace_file = self.export_to_json(spans, temp_path / "traces.json")
            else:
                trace_file = self.export_to_otlp(spans, temp_path / "traces.otlp.json")
            
            with tarfile.open(output_file, "w:gz") as tar:
                tar.add(trace_file, arcname=trace_file.name)
        
        return output_file
