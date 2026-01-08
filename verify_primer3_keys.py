
import primer3
import sys

def test_keys():
    seq = "CCTCAGGTCACTCTTTGGCAACGACCCCTCGTCACAATAAAGATAGGGGGGCAACTAAAGGAAGCTCTATTAGATACAGGAGCAGATGATACAGTATTAGAAGAAATGAGTTTGCCAGGAAGATGGAAACCAAAAATGATAGGGGGAATTGGAGGTTTTATCAAAGTAAGACAGTATGATCAGATACTCATAGAAATCTGTGGACATAAAGCTATAGGTACAGTATTAGTAGGACCTACACCTGTCAACATAATTGGAAGAAATCTGTTGACTCAGATTGGTTGCACTTTAAATTTTCCC"
    
    seq_args = {
        'SEQUENCE_TEMPLATE': seq,
        'SEQUENCE_ID': "test"
    }
    
    # Base args that produce results
    base_args = {
        'PRIMER_TASK': 'generic',
        'PRIMER_PICK_INTERNAL_OLIGO': 1,
        'PRIMER_OPT_TM': 60.0,
        'PRIMER_MIN_TM': 57.0,
        'PRIMER_MAX_TM': 63.0,
        'PRIMER_PRODUCT_SIZE_RANGE': [[70, 200]],
    }
    
    # We want to force a FAIL by setting MIN_TM to 90.0
    # If the key is correct, Primer3 will see "Min Tm 90" and fail to find probes (Tm ~60).
    # If the key is ignored, Primer3 will ignore "Min Tm 90" and return probes (~60).
    
    candidate_keys = [
        "PRIMER_INTERNAL_OLIGO_MIN_TM", # V2 standard
        "PRIMER_INTERNAL_MIN_TM",       # V1/Legacy?
        "PRIMER_MIN_TM_INTERNAL",       # My guess
        "PRIMER_HYB_OLIGO_MIN_TM",      # Another alias?
    ]
    
    print(f"Base run (No Probe Constraints)...")
    res_base = primer3.bindings.design_primers(seq_args, base_args)
    count_base = res_base.get('PRIMER_PAIR_NUM_RETURNED', 0)
    print(f"Base count: {count_base}")
    if count_base > 0:
        print(f"Base Probe Tm: {res_base.get('PRIMER_INTERNAL_0_TM')}")

    for key in candidate_keys:
        print(f"\nTesting Key: {key} = 90.0")
        test_args = base_args.copy()
        test_args[key] = 90.0
        
        try:
            res = primer3.bindings.design_primers(seq_args, test_args)
            count = res.get('PRIMER_PAIR_NUM_RETURNED', 0)
            print(f"  Count: {count}")
            if count == 0:
                print("  -> RESULT: FAILURE (As Expected!) => Key is CORRECT")
            else:
                tm = res.get('PRIMER_INTERNAL_0_TM', 'N/A')
                print(f"  -> RESULT: SUCCESS (Unexpected) => Key is IGNORED. (Tm={tm})")
        except Exception as e:
            print(f"  -> ERROR: {e}")

if __name__ == "__main__":
    test_keys()
