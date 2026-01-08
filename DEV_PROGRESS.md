# Development Progress: Assay Design Copilot

**Goal:** Build an agentic "Assay Design Copilot" that automates qPCR/dPCR assay design, powered by a reusable internal agent framework.

**Status Legend:**

- [ ] Todo

- [/] In Progress

- [X] Done

---

## Phase 1: Project Foundations & Infrastructure

*Goal: Set up the repository, Python environment, and core data models.*

- [x] **1.1: Project Initialization**
  - [x] Initialize Python project (pyproject.toml/requirements.txt).
  - [x] Set up directory structure (`src/`, `tests/`, `experiments/`).
  - [x] Configure `pytest` and linting (check for pre-commit hooks).
- [x] **1.2: Domain Modeling (Pydantic Schemas)**
  - [x] Define `DesignRequest` (inputs, constraints, assay type).
  - [x] Define `DesignCandidate` (primers, probes, coordinates, Tm).
  - [x] Define `QCResult` (validity status, warnings, scores).
  - [x] Define `DesignArtifact` (final output bundle structure).
- [x] **1.3: Tooling Abstractions**
  - [x] Define `BaseTool` interface (inputs, outputs, side-effects).
  - [x] Implement `ToolRegistry` for dynamic tool loading.

## Phase 2: Core Assay Design Logic

*Goal: Implement the deterministic "tools" that the agent will orchestrate.*

- [x] **2.1: Primer3 Integration (The Engine)**
  - [x] Implement `Primer3Wrapper` tool (inputs: sequence + constraints).
  - [x] Handle Primer3 config generation from high-level `DesignRequest`.
  - [x] Parse Primer3 output into `DesignCandidate` objects.
- [x] **2.2: Probe Design Strategies**
  - [x] Implement "Internal Oligo" extraction from Primer3 results.
  - [x] Implement "Fallback" heuristic tool for designing probes if Primer3 fails (rule-based selection).
- [x] **2.3: QC & Scoring Tools**
  - [x] Implement `calculate_qc_metrics` tool (Tm, GC, hairpin checks via Primer3-py or biopython).
  - [x] Implement `rank_candidates` logic (scoring function).

## Phase 3: The Agent Framework

*Goal: Build the "ML Framework" components (Traceability, Replay).*

- [x] **3.1: Execution Tracing**
  - [x] Implement `TraceLogger` to record every tool call (args, result, timestamp).
  - [x] Define `Trace` schema (JSONL support).
- [x] **3.2: Replay Engine**
  - [x] Implement `ReplayExecutor` that can re-run a trace without re-computing (mocking) or re-run deterministically.
- [x] **3.3: Task/Run Management**
  - [x] Implement `RunManager` to handle file I/O, artifacts directory creation (`runs/YYYY-MM-DD/`).

## Phase 4: Copilot Orchestration

*Goal: Wire tools together into the Agent workflow.*

- [x] **4.1: Workflow Definition (LangGraph)**
  - [x] Define the State Graph (Input -> Design -> QC -> Filter -> Output).
  - [x] Implement the "Planner" node (currently rule-based: "If qPCR, do X; if dPCR, do Y").
- [x] **4.2: Application Entrypoint**
  - [x] Create `copilot.py` / CLI entrypoint (`typer` or `click`).
  - [x] wire up `design` command to run the graph.

## Phase 5: Reporting & Evaluation

*Goal: Prove quality and visualize results.*

- [x] **5.1: Report Generation**
  - [x] Implement `MarkdownReporter` (converts `DesignArtifact` to `report.md`).
  - [x] Implement JSON export.
- [x] **5.2: Evaluation Harness**
  - [x] Define "Golden Set" of inputs with known good outputs.
  - [x] Implement `eval.py` to run batches and assert pass rates.

## Phase 6: Documentation & Demo Prep

*Goal: Ready for the interview.*

- [x] **6.1: README & Usage Docs**
- [x] **6.2: Demo Script Verification** (Ensure `design` command works live).
