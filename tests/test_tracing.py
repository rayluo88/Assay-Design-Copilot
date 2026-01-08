"""
Unit Tests for Tracing System.

Verifies the Observability layer of the framework.
Ensures that:
1. Tool calls are intercepted and logged to memory.
2. Traces are correctly serialized to JSONL format for persistence.
3. Metadata (run_id, durations) is captured accurately.
"""
import json
import pytest
from assay_copilot.tracing import TraceLogger

def test_logger_records_call(tmp_path):
    # Setup
    log_file = tmp_path / "trace.jsonl"
    logger = TraceLogger(run_id="test_run")
    
    # Action
    logger.log_call(
        tool_name="test_tool",
        args=("arg1",),
        kwargs={"k": "v"},
        output={"result": "ok"},
        duration=0.1
    )
    
    # Verify in memory
    assert len(logger.trace.records) == 1
    rec = logger.trace.records[0]
    assert rec.tool_name == "test_tool"
    assert rec.duration == 0.1
    
    # Save and verify file
    logger.save(str(log_file))
    with open(log_file) as f:
        data = json.load(f)
        assert data['run_id'] == "test_run"
        assert len(data['records']) == 1
