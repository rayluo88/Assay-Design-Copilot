"""
CLI Entrypoint.

The command-line interface for the Assay Design Copilot.
It handles argument parsing, initializes the workflow state, triggers the `LangGraph` execution,
and saves the final artifacts and reports to disk.
"""
import warnings

# Suppress Pydantic V1 compatibility warnings from LangChain on newer Python versions
warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality.*")

import typer
import json
import os
from pathlib import Path
from .workflow import app, AgentState
from .schema import DesignRequest, AssayType, DesignArtifact
from .reporter import MarkdownReporter

cli = typer.Typer()

@cli.command()
def design(
    sequence: str = typer.Option(..., help="Target DNA sequence"),
    name: str = typer.Option("my_assay", help="Name of the design job"),
    assay_type: str = typer.Option("qPCR", help="Assay type (qPCR/dPCR)"),
    out_dir: str = typer.Option("./runs", help="Output directory")
):
    """Run the Assay Design Copilot."""
    
    # 1. Setup Run Dir
    run_dir = Path(out_dir) / name
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Create Request (with validation)
    try:
        req = DesignRequest(
            target_sequence=sequence,
            name=name,
            assay_type=AssayType(assay_type)
        )
    except Exception as e:
        print(f"[ERROR] Invalid Input: {e}")
        # Provide user-friendly hints for common errors
        if "too short" in str(e):
            print("HINT: Please provide a sequence of at least 100 base pairs.")
        if "invalid characters" in str(e):
            print("HINT: Valid characters are A, T, C, G, N (and IUPAC ambiguity codes). Numbers and whitespace are not allowed.")
        raise typer.Exit(code=1)
    
    # 3. Initialize State
    initial_state = AgentState(
        request=req,
        candidates=[],
        qc_results={},
        artifact=None
    )
    
    # 4. Run Workflow
    print(f"Starting design for {name} ({assay_type})...")
    final_state = app.invoke(initial_state)
    artifact: DesignArtifact = final_state['artifact']
    
    # 5. Save Artifacts
    # JSON
    with open(run_dir / "artifact.json", "w") as f:
        f.write(artifact.model_dump_json(indent=2))
        
    # Report
    reporter = MarkdownReporter()
    report_content = reporter.generate(artifact)
    with open(run_dir / "report.md", "w") as f:
        f.write(report_content)
        
    print(f"Done! Results saved to {run_dir}")
    if artifact.best_candidate_index is not None:
        print(f"Best Candidate Index: {artifact.best_candidate_index + 1}")
    else:
        print("Best Candidate Index: None")

if __name__ == "__main__":
    cli()
