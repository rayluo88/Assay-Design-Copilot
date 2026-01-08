"""
Execution Tracing & Replay System.

Implements the core 'Framework' capability of recording tool execution.
It provides a `TraceLogger` to capture inputs, outputs, timestamps, and errors for every tool call,
enabling deterministic replay and audit trails.
"""
import json
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .tools import BaseTool

class ToolCallRecord(BaseModel):
    """Record of a single tool execution."""
    tool_name: str
    input_args: tuple
    input_kwargs: Dict[str, Any]
    output: Any
    timestamp: float
    duration: float
    error: Optional[str] = None

class RunTrace(BaseModel):
    """Complete trace of a run."""
    run_id: str
    timestamp: float
    records: List[ToolCallRecord] = []

class TraceLogger:
    """Logs tool execution to a trace."""
    
    def __init__(self, run_id: str):
        self.trace = RunTrace(run_id=run_id, timestamp=time.time())

    def log_call(self, tool_name: str, args: tuple, kwargs: Dict[str, Any], output: Any, duration: float, error: str = None):
        # We need to ensure args/kwargs/output are serializable
        # For MVP we assume Pydantic models, which are.
        record = ToolCallRecord(
            tool_name=tool_name,
            input_args=args,
            input_kwargs=kwargs,
            output=output, # Pydantic v2 usually handles this if we dump properly
            timestamp=time.time(),
            duration=duration,
            error=error
        )
        self.trace.records.append(record)

    def save(self, path: str):
        with open(path, 'w') as f:
            f.write(self.trace.model_dump_json(indent=2))

class TracedTool(BaseTool):
    """Wrapper to automatically log tool execution."""
    
    def __init__(self, tool: BaseTool, logger: TraceLogger):
        self.tool = tool
        self.logger = logger
        self._metadata = tool._metadata

    def define_metadata(self):
        return self.tool.define_metadata()

    def execute(self, *args, **kwargs) -> Any:
        start = time.time()
        error = None
        result = None
        try:
            result = self.tool.execute(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            raise e
        finally:
            duration = time.time() - start
            # Serialize result if likely Pydantic model
            log_output = result
            if hasattr(result, 'model_dump'):
                log_output = result.model_dump()
            elif isinstance(result, list) and result and hasattr(result[0], 'model_dump'):
                 log_output = [item.model_dump() for item in result]

            self.logger.log_call(
                tool_name=self.name,
                args=args, 
                kwargs=kwargs, 
                output=log_output,
                duration=duration,
                error=error
            )
