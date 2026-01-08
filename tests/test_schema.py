"""
Unit Tests for Domain Models (Schema).

Validates the Pydantic data models used throughout the application.
Ensures that:
1. Default values (e.g., qPCR assay type) are correctly populated.
2. Required fields (like target sequence) raise validation errors if missing.
3. Nested objects (Oligo) constitute valid structures.
"""
import pytest
from pydantic import ValidationError
from assay_copilot.schema import DesignRequest, AssayType, Oligo, Strand

def test_design_request_defaults():
    req = DesignRequest(target_sequence="A" * 100)
    assert req.assay_type == AssayType.qPCR
    assert req.target_tm == 60.0

def test_design_request_validation():
    """Test validation of target_sequence."""
    # 1. Valid Sequence
    req = DesignRequest(target_sequence="A" * 100)
    assert req.target_sequence == "A" * 100
    
    # 2. Sanitization (whitespace + lowercase)
    req = DesignRequest(target_sequence="  atcg" * 25 + "  ")
    assert " " not in req.target_sequence
    assert req.target_sequence.isupper()
    
    # 3. Too Short
    with pytest.raises(ValidationError) as exc:
        DesignRequest(target_sequence="ACGT")
    assert "too short" in str(exc.value)
    
    # 4. Invalid Characters
    with pytest.raises(ValidationError) as exc:
        DesignRequest(target_sequence=("A" * 100) + "1")
    assert "invalid characters" in str(exc.value)

def test_oligo_creation():
    oligo = Oligo(
        sequence="ATCG",
        tm=60.0,
        gc_percent=50.0,
        length=4,
        start=0,
        end=4,
        strand=Strand.PLUS
    )
    assert oligo.sequence == "ATCG"
    assert oligo.strand == "+"
