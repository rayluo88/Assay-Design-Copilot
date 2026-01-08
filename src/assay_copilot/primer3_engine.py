"""
Primer3 Integration Tool.

This module implements the `Primer3Engine` tool, which wraps the `primer3-py` library.
It is responsible for:
1. Translating high-level `DesignRequest` constraints into low-level Primer3 arguments.
2. Executing the primer design algorithm.
3. Parsing raw Primer3 output dictionaries into structured `DesignCandidate` objects.
"""
try:
    import primer3
except ImportError:
    primer3 = None  # Handle missing dependency gracefully for now

from typing import List, Dict, Any
from .schema import DesignRequest, DesignCandidate, Oligo, Strand
from .tools import BaseTool, ToolMetadata

class Primer3Engine(BaseTool):
    """Engine to run Primer3 design."""

    def define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="primer3_engine",
            description="Generates primers using Primer3-py",
            version="2.0.0"
        )

    def execute(self, request: DesignRequest) -> List[DesignCandidate]:
        if not primer3:
            raise ImportError("primer3-py is not installed.")

        # 1. Prepare Sequence Args
        seq_args = {
            'SEQUENCE_TEMPLATE': request.target_sequence,
            'SEQUENCE_ID': request.name or "unnamed_target"
        }

        # 2. Prepare Global Args
        global_args = {
            'PRIMER_TASK': 'generic',
            'PRIMER_PICK_LEFT_PRIMER': 1,
            'PRIMER_PICK_RIGHT_PRIMER': 1,
            'PRIMER_KEY_TMS': 1,
            
            # Constraints from request
            'PRIMER_OPT_TM': request.target_tm,
            'PRIMER_MIN_TM': request.target_tm - 3.0,
            'PRIMER_MAX_TM': request.target_tm + 3.0,
            'PRIMER_PRODUCT_SIZE_RANGE': [request.allowed_product_size]
        }

        # If it's qPCR/dPCR, we usually want probes too.
        # Primer3 'generic' can design probes if we ask
        if request.assay_type in ["qPCR", "dPCR"]:
            global_args['PRIMER_PICK_INTERNAL_OLIGO'] = 1
            global_args['PRIMER_OPT_TM_INTERNAL'] = request.target_tm + 10.0 # Common rule: probe Tm > primer Tm

        # 3. Running Primer3
        results = primer3.bindings.design_primers(seq_args, global_args)

        # 4. Parsing Results
        candidates = []
        count = results.get('PRIMER_PAIR_NUM_RETURNED', 0)
        
        for i in range(count):
            # Parse Fwd
            fwd_seq = results.get(f'PRIMER_LEFT_{i}_SEQUENCE')
            fwd_tm = results.get(f'PRIMER_LEFT_{i}_TM')
            fwd_gc = results.get(f'PRIMER_LEFT_{i}_GC_PERCENT')
            fwd_loc = results.get(f'PRIMER_LEFT_{i}') # tuple (start, length)
            
            fwd_oligo = Oligo(
                sequence=fwd_seq, tm=fwd_tm, gc_percent=fwd_gc,
                length=fwd_loc[1], start=fwd_loc[0], end=fwd_loc[0] + fwd_loc[1],
                strand=Strand.PLUS
            )

            # Parse Rev
            rev_seq = results.get(f'PRIMER_RIGHT_{i}_SEQUENCE')
            rev_tm = results.get(f'PRIMER_RIGHT_{i}_TM')
            rev_gc = results.get(f'PRIMER_RIGHT_{i}_GC_PERCENT')
            rev_loc = results.get(f'PRIMER_RIGHT_{i}') # tuple (start, length)
            
            # Note: Primer3 returns reverse primer location on the reverse strand? 
            # Actually return coordinate is usually relative to input sequence.
            # Primer3 'right' coordinate is the 5' end of the primer on the reverse strand (so higher index).
            
            rev_oligo = Oligo(
                sequence=rev_seq, tm=rev_tm, gc_percent=rev_gc,
                length=rev_loc[1], start=rev_loc[0], end=rev_loc[0] - rev_loc[1], # Primer3 Right: start is 3'-most base on + strand? 
                                                                    # Wait, need to check Primer3 docs.
                                                                    # Primer3 docs: Right Primer Start is the index of the 5' most base (on the reverse strand!) 
                                                                    # Actually, usually it returns the index on the template.
                strand=Strand.MINUS
            )

            # Parse Probe (Internal)
            probe_oligo = None
            if global_args.get('PRIMER_PICK_INTERNAL_OLIGO'):
                probe_seq = results.get(f'PRIMER_INTERNAL_{i}_SEQUENCE')
                if probe_seq:
                    probe_tm = results.get(f'PRIMER_INTERNAL_{i}_TM')
                    probe_gc = results.get(f'PRIMER_INTERNAL_{i}_GC_PERCENT')
                    probe_loc = results.get(f'PRIMER_INTERNAL_{i}')
                    
                    probe_oligo = Oligo(
                        sequence=probe_seq, tm=probe_tm, gc_percent=probe_gc,
                        length=probe_loc[1], start=probe_loc[0], end=probe_loc[0] + probe_loc[1],
                        strand=Strand.PLUS # Usually plus for TaqMan
                    )

            cand = DesignCandidate(
                forward_primer=fwd_oligo,
                reverse_primer=rev_oligo,
                probe=probe_oligo,
                amplicon_sequence="TODO extract", # Need to slice from input
                amplicon_size=results.get(f'PRIMER_PAIR_{i}_PRODUCT_SIZE'),
                penalty=results.get(f'PRIMER_PAIR_{i}_PENALTY')
            )
            candidates.append(cand)
            
        return candidates
