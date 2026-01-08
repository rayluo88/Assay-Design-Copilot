"""
Report Generator.

Converts the structured `DesignArtifact` (JSON data) into human-readable formats (Markdown).
Responsible for presenting the top candidates, scores, and detailed design parameters to the user.
"""
from .schema import DesignArtifact, QCStatus

class MarkdownReporter:
    """Generates a Markdown report from a DesignArtifact."""
    
    def generate(self, artifact: DesignArtifact) -> str:
        req = artifact.request
        lines = []
        lines.append(f"# Assay Design Report: {req.name}")
        lines.append(f"**Assay Type:** {req.assay_type.value}  ")
        lines.append(f"**Target Tm:** {req.target_tm} C  ")
        
        lines.append("\n## Top Candidates")
        
        if artifact.best_candidate_index is not None:
             # Display 1-based index for user friendliness
             lines.append(f"**Best Candidate:** #{artifact.best_candidate_index + 1}")
        else:
             lines.append("**Status:** No valid candidates found.")
             
        lines.append("\n| ID | Fwd Tm | Rev Tm | Probe Tm | Amplicon Size | Score | Status |")
        lines.append("|---|---|---|---|---|---|---|")
        
        for i, cand in enumerate(artifact.candidates):
            qc = artifact.qc_results.get(i)
            status = qc.status.value if qc else "N/A"
            score = f"{qc.score:.2f}" if qc else "N/A"
            
            fwd_tm = f"{cand.forward_primer.tm:.1f}"
            rev_tm = f"{cand.reverse_primer.tm:.1f}"
            probe_tm = f"{cand.probe.tm:.1f}" if cand.probe else "-"
            size = cand.amplicon_size
            
            # Bold the best row (apply formatting to each cell content)
            if i == artifact.best_candidate_index:
                row = f"| **{i + 1}** | **{fwd_tm}** | **{rev_tm}** | **{probe_tm}** | **{size}** | **{score}** | **{status}** |"
            else:
                row = f"| {i + 1} | {fwd_tm} | {rev_tm} | {probe_tm} | {size} | {score} | {status} |"
                
            lines.append(row)
            
        lines.append("\n## Design Details")
        for i, cand in enumerate(artifact.candidates):
            lines.append(f"\n### Candidate {i + 1}")
            lines.append("```")
            lines.append(f"Forward: {cand.forward_primer.sequence} ({cand.forward_primer.tm:.1f}C)")
            lines.append(f"Reverse: {cand.reverse_primer.sequence} ({cand.reverse_primer.tm:.1f}C)")
            if cand.probe:
                lines.append(f"Probe:   {cand.probe.sequence} ({cand.probe.tm:.1f}C)")
            lines.append(f"Amplicon: {cand.amplicon_size} bp")
            lines.append("```")
            
            if i in artifact.qc_results:
                lines.append("**QC Checks:**")
                lines.append("- " + str(artifact.qc_results[i].checks))
                
        return "\n".join(lines)
