"""
Domain Models (Data Layer).

This module defines the Core Pydantic schemas (DesignRequest, DesignCandidate, QCResult, DesignArtifact)
that serve as the typed data contract passed between the Agent's tools and workflow nodes.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AssayType(str, Enum):
    qPCR = "qPCR"
    dPCR = "dPCR"

class Strand(str, Enum):
    PLUS = "+"
    MINUS = "-"

class DesignRequest(BaseModel):
    """Input request for assay design."""
    target_sequence: str = Field(..., description="Target DNA sequence in FASTA format or raw string")
    assay_type: AssayType = Field(default=AssayType.qPCR, description="Type of assay to design")
    target_tm: float = Field(default=60.0, description="Target melting temperature for primers")
    allowed_product_size: List[int] = Field(default=[70, 150], description="Range [min, max] for amplicon size")
    name: Optional[str] = Field(None, description="Optional name for the design job")

class Oligo(BaseModel):
    """Represents a single primer or probe."""
    sequence: str
    tm: float
    gc_percent: float
    length: int
    start: int
    end: int # Inclusive 0-based or 1-based? Let's assume 0-based [start, end) or similar. 
             # Primer3 uses (start, length). Let's stick to 0-based start, and calc end.
             # Actually, for clarity, let's store start/length.
    strand: Strand = Strand.PLUS

class DesignCandidate(BaseModel):
    """A complete assay candidate (pair + optional probe)."""
    forward_primer: Oligo
    reverse_primer: Oligo
    probe: Optional[Oligo] = None
    amplicon_sequence: str
    amplicon_size: int
    penalty: float = Field(0.0, description="Primer3 penalty or custom score (lower is better)")

class QCStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

class QCResult(BaseModel):
    """QC checks for a candidate."""
    status: QCStatus
    checks: Dict[str, Any] = Field(..., description="Key-value pair of check names and results")
    score: float = Field(1.0, description="Normalized score 0.0-1.0 (higher is better)")

class DesignArtifact(BaseModel):
    """Final output bundle for a design run."""
    request: DesignRequest
    candidates: List[DesignCandidate]
    qc_results: Dict[int, QCResult] = Field(..., description="Map candidate index to QC result")
    best_candidate_index: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
