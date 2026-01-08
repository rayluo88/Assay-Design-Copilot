# Assay Design Copilot: Logic Walkthrough

This document explains the internal execution flow of the **Assay Design Copilot** when running the demo command. Use this to explain the "How it Works" section during your interview.

## 1. The Entrypoint: `src/assay_copilot/main.py`

The execution starts here when you run:
```bash
python -m assay_copilot.main --sequence "..." --name "DemoRun"
```

**Logic Flow:**
1.  **Argument Parsing**: `Typer` parses the CLI arguments into a `sequence`, `name`, and `assay_type`.
2.  **Request Object**: A Pydantic `DesignRequest` model is instantiated. This validates the input (checking for empty strings, invalid characters, etc.) before any logic runs.
3.  **State Initialization**: An initial `AgentState` dictionary is created, holding the `request` and empty lists for `candidates` and `qc_results`.
4.  **Graph Invocation**: The application calls `app.invoke(initial_state)`. This hands control over to the **LangGraph Orchestrator** defined in `workflow.py`.

## 2. The Orchestrator: `src/assay_copilot/workflow.py`

This is the "Brain" of the agent. It defines a **State Graph** where data flows between nodes.

**The Graph Topology:**
`[Start] -> [Design Primers] -> [Design Probes] -> [Quality Control] -> [Finalize] -> [End]`

**Step-by-Step Execution:**

### Step A: Design Primers Node
- **Action**: Calls `Primer3Engine.execute(state.request)`.
- **Logic**: 
    - Translates high-level constraints (e.g., "qPCR", "Target 60°C Tm") into low-level Primer3 configuration dictionary.
    - Runs the external `primer3-py` C-library binding.
    - Parses the raw output dictionary into a list of structured `DesignCandidate` objects (Forward + Reverse primers).
- **Update**: The `state['candidates']` list is populated.

### Step B: Design Probes Node
- **Action**: Calls `RuleBasedProbeDesigner.execute(state.request, state.candidates)`.
- **Logic**:
    - Iterates through each candidate from Step A.
    - If the request is for "qPCR" (TaqMan), it attempts to find a compatible probe sequence between the primers.
    - It enforces rules like "Probe Tm must be ~10°C higher than primers".
- **Update**: The `probe` field of each `DesignCandidate` is updated.

### Step C: Quality Control (QC) Node
- **Action**: Calls `QCEngine.execute(candidate)`.
- **Logic**:
    - Checks for "Hard Failures" (e.g., Missing probe in a qPCR design).
    - Checks for "Soft Warnings" (e.g., Tm difference between Fwd/Rev > 2°C).
    - Calculates a specificity/penalty store (0.0 - 1.0).
- **Update**: Populates `state['qc_results']`.

## 3. Reporting: Back to `main.py`

Once the graph finishes execution, `main.py` takes the final state and:
1.  **JSON Dump**: Saves the raw `DesignArtifact` (pure data) to `artifact.json`.
2.  **Markdown Generation**: Uses `MarkdownReporter` to convert the data into a human-readable summary (`report.md`) containing:
    - Best candidate details.
    - QC warnings/errors.
    - Sequence visualization.

---

## 4. Troubleshooting Demo Failures

**Error**: `OSError: SEQUENCE_INCLUDED_REGION length < min PRIMER_PRODUCT_SIZE_RANGE`
- **Cause**: The input `--sequence` provided ("...") is shorter than the minimum product size (default ~70bp).
- **Fix**: Use a real sequence of at least 200bp.
- **Example Valid Input**:
  ```bash
  python -m assay_copilot.main --sequence "CCTCAGGTCACTCTTTGGCAACGACCCCTCGTCACAATAAAGATAGGGGGGCAACTAAAGGAAGCTCTATTAGATACAGGAGCAGATGATACAGTATTAGAAGAAATGAGTTTGCCAGGAAGATGGAAACCAAAAATGATAGGGGGAATTGGAGGTTTTATCAAAGTAAGACAGTATGATCAGATACTCATAGAAATCTGTGGACATAAAGCTATAGGTACAGTATTAGTAGGACCTACACCTGTCAACATAATTGGAAGAAATCTGTTGACTCAGATTGGTTGCACTTTAAATTTTCCC" --name "HIV_Pol_Demo"
  ```

---

## Key Talking Points for Interview

- **Separation of Concerns**: The CLI (`main.py`) handles I/O, while `workflow.py` handles logic. This makes the system scalable.
- **Stateful Execution**: `LangGraph` passes a `State` object around, meaning any node can access previous results. This is superior to rigid linear scripts.
- **Type Safety**: Data is validated at the edges (Entry) and between nodes using Pydantic, preventing "garbage in, garbage out".
