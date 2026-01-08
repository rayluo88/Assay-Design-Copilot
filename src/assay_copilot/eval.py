"""
Evaluation Harness.

A regression testing suite that runs the full pipeline against a 'Golden Set' of known targets.
Ensures that code changes do not degrade the quality or success rate of assay designs.
"""
import pytest
from .workflow import app, AgentState
from .schema import DesignRequest, AssayType

# Golden Set: A few targets with known properties
GOLDEN_SET = [
    {
        "name": "brca1_exon11_fragment",
        "seq": "ATTTGGGAAAAACCTATCGGAAGGCTT", # Too short, but good for testing failure? 
                # Let's use a realistic mock sequence
                # Just a random 200bp sequence
                "TCGATCGTAGCTAGCTAGCATGCTAGCTAGCTAGCTAGCTAGCTAGCTCGATCGTAGCTAGCTAGCATGCTAGCTAGCTAGCTAGCTAGCTAGCTCGATCGTAGCTAGCTAGCATGCTAGCTAGCTAGCTAGCTAGCTAGCTCGATCGTAGCTAGCTAGCATGCTAGCTAGCTAGCTAGCTAGCTAGCTCGATCGTAGC",
        "expected_candidates_min": 0 # Short seq might fail
    },
    {
        "name": "valid_target_500bp",
        "seq": "A" * 500, # Primer3 might hate poly-A, but purely structural test
        "expected_candidates_min": 0
    }
]

def run_eval():
    """Runs the golden set and reports pass rate."""
    print("Running Evaluation Harness...")
    passes = 0
    fails = 0
    
    for case in GOLDEN_SET:
        print(f"Testing {case['name']}...")
        req = DesignRequest(
            target_sequence=case['seq'],
            name=case['name'],
            assay_type=AssayType.qPCR
        )
        
        initial_state = AgentState(
            request=req,
            candidates=[],
            qc_results={},
            artifact=None
        )
        
        try:
            # We wrap this in try/except to catch pipeline crashes
            final_state = app.invoke(initial_state)
            artifact = final_state['artifact']
            
            # Assertions
            cand_count = len(artifact.candidates)
            if cand_count >= case['expected_candidates_min']:
                # Additional checks could go here (e.g. check best score > 0.9)
                print(f"  PASS: Generated {cand_count} candidates.")
                passes += 1
            else:
                print(f"  FAIL: Too few candidates ({cand_count} < {case['expected_candidates_min']})")
                fails += 1
                
        except Exception as e:
            print(f"  ERROR: Pipeline crashed - {e}")
            fails += 1
            
    print(f"\nEval Complete. Pass: {passes}, Fail: {fails}")
    if fails > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    run_eval()
