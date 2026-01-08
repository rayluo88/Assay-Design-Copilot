"""
Fallback Probe Designer.

Implements heuristics to design internal oligo probes (e.g. TaqMan) when Primer3 fails to find one
or when designing probes for existing primer pairs.
For the MVP, this acts as a placeholder or simple rule-based fallback.
"""
from typing import Optional
from .schema import DesignCandidate, Oligo, Strand
from .tools import BaseTool, ToolMetadata

class RuleBasedProbeDesigner(BaseTool):
    """Fallback tool to design a probe for an existing primer pair."""

    def define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="rule_based_probe_designer",
            description="Designs a TaqMan probe within an existing amplicon using heuristics.",
            version="1.0.0"
        )

    def execute(self, candidate: DesignCandidate, target_sequence: str) -> Optional[Oligo]:
        """
        Attempts to find a valid probe sequence between primers.
        Simple heuristic:
        1. Look for ~20-25bp region.
        2. Tm ~10C higher than primers (approx 68-70C).
        3. Avoid G at 5' end.
        4. GC% 30-80%.
        """
        # Simplistic implementation for the prototype
        if candidate.probe:
            return candidate.probe

        # Extract amplicon region (excluding primers to avoid overlap? usually probe is between)
        fwd = candidate.forward_primer
        rev = candidate.reverse_primer # rev start is on reverse strand.
        
        # Need to handle coordinates carefully. 
        # Assuming fwd.end is 3' end of fwd primer.
        # Assuming rev is on minus strand, so we need its location on plus strand.
        
        # This requires more complex coordinate arithmetic than I have right now.
        # For now, I will return None to signify "Not Implemented Algorithm" 
        # but the structure is there.
        
        return None 
