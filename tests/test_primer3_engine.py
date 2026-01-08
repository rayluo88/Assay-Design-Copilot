"""
Unit Tests for Primer3 Engine.

Tests the integration with the external `primer3-py` library.
Strategy:
- Uses `unittest.mock` to mock the C-extension bindings, avoiding actual design computation.
- Verifies that `DesignRequest` parameters are correctly translated to Primer3 input arguments.
- Verifies that raw Primer3 output dicts are correctly parsed into `DesignCandidate` objects.
"""
import pytest
from unittest.mock import patch, MagicMock
from assay_copilot.primer3_engine import Primer3Engine
from assay_copilot.schema import AssayType, DesignRequest

@patch('assay_copilot.primer3_engine.primer3')
def test_primer3_execution_flow(mock_primer3_lib):
    # Setup mock return
    mock_primer3_lib.bindings.design_primers.return_value = {
        'PRIMER_PAIR_NUM_RETURNED': 1,
        'PRIMER_LEFT_0': (10, 20),
        'PRIMER_LEFT_0_TM': 60.0,
        'PRIMER_LEFT_0_GC_PERCENT': 50.0,
        'PRIMER_LEFT_0_SEQUENCE': "ATCG",
        'PRIMER_RIGHT_0': (100, 20),
        'PRIMER_RIGHT_0_TM': 60.0,
        'PRIMER_RIGHT_0_GC_PERCENT': 50.0,
        'PRIMER_RIGHT_0_SEQUENCE': "CGAT",
        'PRIMER_PAIR_0_PRODUCT_SIZE': 110,
        'PRIMER_PAIR_0_PENALTY': 0.1
    }

    engine = Primer3Engine()
    
    # Execute
    req = DesignRequest(
        target_sequence="A" * 200,
        assay_type=AssayType.qPCR,
        target_tm=60.0,
        name="test_target"
    )
    candidates = engine.execute(req)
    
    # Assertions
    assert len(candidates) == 1
    c = candidates[0]
    assert c.forward_primer.sequence == "ATCG"
    assert c.amplicon_size == 110
    
    # Verify call args
    args, _ = mock_primer3_lib.bindings.design_primers.call_args
    input_seqs = args[0]
    assert input_seqs['SEQUENCE_TEMPLATE'] == "A" * 200

def test_primer3_no_results():
    with patch('assay_copilot.primer3_engine.primer3') as mock_lib:
        mock_lib.bindings.design_primers.return_value = {
            'PRIMER_PAIR_NUM_RETURNED': 0
        }
        
        engine = Primer3Engine()
        req = DesignRequest(target_sequence="A" * 100, assay_type=AssayType.qPCR)
        candidates = engine.execute(req)
        assert len(candidates) == 0

def test_primer3_internal_tm_params():
    """Verify that qPCR request sets correct internal oligo (probe) Tm parameters."""
    with patch('assay_copilot.primer3_engine.primer3') as mock_lib:
        # Mock Return
        mock_lib.bindings.design_primers.return_value = {'PRIMER_PAIR_NUM_RETURNED': 0}
        
        engine = Primer3Engine()
        req = DesignRequest(
            target_sequence="A" * 200, 
            assay_type=AssayType.qPCR,
            target_tm=60.0
        )
        
        # Execute
        engine.execute(req)
        
        # Verify call args
        args, kwargs = mock_lib.bindings.design_primers.call_args
        global_args = args[1]
        
        # Check Probe Params
        assert global_args['PRIMER_PICK_INTERNAL_OLIGO'] == 1
        assert global_args['PRIMER_INTERNAL_OPT_TM'] == 70.0  # 60 + 10
        assert global_args['PRIMER_INTERNAL_MIN_TM'] == 65.0  # 60 + 5
        assert global_args['PRIMER_INTERNAL_MAX_TM'] == 75.0  # 60 + 15
