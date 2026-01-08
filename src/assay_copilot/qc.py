"""
Quality Control (QC) Engine.

Implements the logic for scoring and validating design candidates.
It checks for hard constraints (PASS/FAIL) and soft warnings (WARN)
to filter and rank the final candidates presented to the user.
"""
from typing import List
from .schema import DesignCandidate, QCResult, QCStatus
from .tools import BaseTool, ToolMetadata

class QCEngine(BaseTool):
    """Performs QC checks and scoring."""

    def define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="qc_engine",
            description="Calculates QC metrics and scores candidates.",
            version="1.0.0"
        )

    def execute(self, candidate: DesignCandidate) -> QCResult:
        checks = {}
        score = 1.0 # Start perfect
        
        # Check 1: Existence of Probe (if required)
        # We assume if it's passed here, we want to score it.
        if not candidate.probe:
            checks['has_probe'] = False
            score -= 0.5
        else:
            checks['has_probe'] = True

        # Check 2: Tm Difference
        fwd_tm = candidate.forward_primer.tm
        rev_tm = candidate.reverse_primer.tm
        tm_diff = abs(fwd_tm - rev_tm)
        checks['tm_diff'] = tm_diff
        
        if tm_diff > 2.0:
            checks['tm_balance'] = "WARN"
            score -= 0.1 * tm_diff
        else:
            checks['tm_balance'] = "PASS"

        # Determine Status
        if score < 0.5:
            status = QCStatus.FAIL
        elif score < 0.9:
            status = QCStatus.WARN
        else:
            status = QCStatus.PASS

        return QCResult(
            status=status,
            checks=checks,
            score=max(0.0, score)
        )
