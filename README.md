# Assay Design Copilot

An agentic framework for automating qPCR and dPCR assay design, featuring deterministic tool orchestration, execution tracing, and rigorous evaluation.

## Features

- **Automated Design**: Generates primer/probe candidates using `primer3-py`.
- **Agent Framework**: Built on `LangGraph`, separating "Plan", "Execute", and "Verify" steps.
- **Traceability**: Full execution logs (`trace.jsonl`) for audit and replay.
- **Evaluation**: Regression testing harness (`eval.py`) to ensure design quality.
- **Standardized Outputs**: Produces `artifact.json` and `report.md`.

## Installation

Requires Python 3.11+.

```bash
pip install -e ".[dev]"
```

## Usage

### 1. Design an Assay

Run the copilot to design primers for a target sequence:

```bash
python -m assay_copilot.main design \
  --sequence "TCGATCGTAGCTAGCTAGCATGCTAGCTAGCTAGCTAGCTAGCTAGCTCGATCGTAGCTAGCTAGCATGCTAGCTAGCTAGCTAGCTAGCTAGCTCGATCGTAGCTAGCTAGCATGCTAGCTAGCTAGCTAGCTAGCTAGCTCGATCGTAGC" \
  --name "MyAssay01" \
  --assay-type qPCR \
  --out-dir ./runs
```

This will create:
- `runs/MyAssay01/artifact.json`: Machine-readable output.
- `runs/MyAssay01/report.md`: Human-readable report.

### 2. Run Evaluation Suite

Validate the pipeline against the Golden Set:

```bash
python -m assay_copilot.eval
```

## Project Structure

- `src/assay_copilot/`: Source code.
  - `primer3_engine.py`: Primer3 integration.
  - `workflow.py`: Agent orchestration graph.
  - `schema.py`: Pydantic domain models.
  - `tracing.py`: Execution logging framework.
- `tests/`: Unit and integration tests.
