
import pytest
from assay_copilot.qc import QCEngine
from assay_copilot.schema import DesignCandidate, Oligo, Strand

def test_qc_scoring_primer3_penalty():
    """Verify score is penalized by Primer3 penalty."""
    oligo = Oligo(sequence="A", tm=60, gc_percent=50, length=20, start=0, end=20, strand=Strand.PLUS)
    
    # Candidate with Penalty 1.0
    cand = DesignCandidate(
        forward_primer=oligo, reverse_primer=oligo, probe=oligo,
        amplicon_sequence="A", amplicon_size=100,
        penalty=1.0 # Should deduct 0.1
    )
    
    qc = QCEngine()
    result = qc.execute(cand)
    
    # Base: 1.0
    # Probe penalty: Avg TM=60 -> Optimal=70. Probe=60 -> Diff=10 -> Penalty=0.5
    # P3 penalty: 1.0 -> Penalty=0.1
    # Expected: 1.0 - 0.5 - 0.1 = 0.4
    
    assert result.checks['p3_penalty'] == 1.0
    assert result.score == pytest.approx(0.4)

def test_qc_scoring_probe_tm():
    """Verify score is penalized by Probe Tm deviation."""
    oligo = Oligo(sequence="A", tm=60, gc_percent=50, length=20, start=0, end=20, strand=Strand.PLUS)
    
    # Perfect Probe: Tm = 70 (Avg 60 + 10)
    probe_perfect = Oligo(sequence="A", tm=70, gc_percent=50, length=20, start=0, end=20, strand=Strand.PLUS)
    
    cand = DesignCandidate(
        forward_primer=oligo, reverse_primer=oligo, probe=probe_perfect,
        amplicon_sequence="A", amplicon_size=100,
        penalty=0.0
    )
    
    qc = QCEngine()
    result = qc.execute(cand)
    
    # Base: 1.0
    # Probe penalty: Diff=0 -> Penalty=0
    # P3 penalty: 0 -> Penalty=0
    # Expected: 1.0
    
    assert result.checks['probe_tm_diff'] == 0.0
    assert result.score == 1.0
