"""
Unit Tests for Quality Control (QC) Engine.

Validates the logic for scoring and checking design candidates.
Tests scenarios including:
1. Hard failures (e.g., missing probes in qPCR).
2. Soft warnings (e.g., Tm imbalance between primers).
3. Score calculation logic (penalties).
"""
import pytest
from assay_copilot.qc import QCEngine
from assay_copilot.schema import DesignCandidate, Oligo, Strand, QCStatus

@pytest.fixture
def mock_oligo():
    return Oligo(
        sequence="ATCG", tm=60.0, gc_percent=50.0, 
        length=4, start=0, end=4, strand=Strand.PLUS
    )

@pytest.fixture
def qc_engine():
    return QCEngine()

def test_qc_missing_probe_penalty(qc_engine, mock_oligo):
    # Candidate without probe
    cand = DesignCandidate(
        forward_primer=mock_oligo,
        reverse_primer=mock_oligo,
        probe=None,
        amplicon_sequence="ATCG",
        amplicon_size=100
    )
    
    result = qc_engine.execute(cand)
    assert result.checks['has_probe'] is False
    assert result.score <= 0.5
    assert result.status == QCStatus.WARN

def test_qc_tm_balance(qc_engine, mock_oligo):
    # Create primers with large Tm diff
    fwd = mock_oligo.model_copy(update={'tm': 60.0})
    rev = mock_oligo.model_copy(update={'tm': 65.0}) # 5 degree diff
    
    cand = DesignCandidate(
        forward_primer=fwd,
        reverse_primer=rev,
        probe=mock_oligo,
        amplicon_sequence="ATCG",
        amplicon_size=100
    )
    
    result = qc_engine.execute(cand)
    assert result.checks['tm_balance'] == "WARN"
    # Should deduct points
    assert result.score < 1.0 
