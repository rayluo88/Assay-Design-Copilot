"""
Unit Tests for Reporter.

Validates the generation of human-readable output artifacts.
Ensures that:
1. `DesignArtifact` objects are successfully converted to Markdown strings.
2. Key information (best candidate index, scores) is present in the final report.
"""
from assay_copilot.reporter import MarkdownReporter
from assay_copilot.schema import DesignArtifact, DesignRequest, AssayType, DesignCandidate, Oligo, Strand, QCResult, QCStatus

def test_reporter_output():
    # Mock Data
    req = DesignRequest(target_sequence="AAA", name="TestRun")
    
    oligo = Oligo(sequence="A", tm=50, gc_percent=50, length=1, start=0, end=1, strand=Strand.PLUS)
    cand = DesignCandidate(
        forward_primer=oligo, reverse_primer=oligo, probe=None,
        amplicon_sequence="A", amplicon_size=10
    )
    
    qc = QCResult(status=QCStatus.PASS, checks={'ok': True}, score=1.0)
    
    artifact = DesignArtifact(
        request=req,
        candidates=[cand],
        qc_results={0: qc},
        best_candidate_index=0
    )
    
    # Execute
    reporter = MarkdownReporter()
    report = reporter.generate(artifact)
    
    # Verify
    assert "# Assay Design Report: TestRun" in report
    assert "**Best Candidate:** #1" in report
    assert "Pass" in report or "PASS" in report
