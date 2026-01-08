# Product Requirements Document (PRD)
# Assay Design Copilot + Agent Framework (qPCR / dPCR)

**Version:** 0.1  
**Author:** Raymond Luo  
**Date:** January 2026  
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Purpose
Build an agentic “Assay Design Copilot” that automates qPCR/dPCR assay design end-to-end, powered by a reusable internal agent framework. The Copilot turns assay design from a manual, error-prone checklist into a reproducible pipeline that produces ranked designs plus an audit-ready design report.

### 1.2 Problem Statement
PCR assay design typically requires iterative, manual steps:
- Primer/probe design under multiple constraints (Tm, GC%, length, product size, structures)
- Specificity checks and binding-site mismatch assessment against evolving genomes
- Documentation of assumptions, parameters, and decisions for reproducibility

These steps are time-consuming, inconsistent across individuals, and hard to scale for high-throughput assay development.

### 1.3 Solution Overview
Deliver:
- A lightweight **agent framework** (tool registry + typed I/O + versioned artifacts + run tracing + replay + evaluation harness)
- An **Assay Design Copilot** agent that orchestrates tools to:
  - generate primers/probes
  - perform QC and scoring
  - run in-silico checks (pluggable)
  - produce a structured output bundle (JSON) and a human-readable report (Markdown/PDF-ready)

### 1.4 Success Metrics
- **Reproducibility:** each run produces a deterministic, replayable trace (inputs, parameters, tool calls, outputs)
- **Automation:** one command produces top-N assay candidates plus a report (no manual spreadsheet)
- **Integration-ready:** Copilot can be called headlessly (CLI/API) and integrated into existing primer design UI later
- **Upgrade-safe:** tool and dependency updates are version-pinned and regression-tested via the evaluation harness
- **Interview-ready:** demonstrates “framework building” + bioinformatics pipeline automation + applied AI/LLM readiness

### 1.5 Design Principles (Systems & Agents Era)
- **Systems over models:** treat models/tools as interchangeable engines; keep stable contracts and versioned artifacts
- **Goal → plan → tool-use → verify:** structure orchestration around an explicit agent loop (rule-based in MVP)
- **Deterministic core, optional LLM:** LLMs can summarize/explain but must not be required for design generation
- **Evaluation as a gate:** upgrades (tools/models/parameters) are validated via the evaluation harness
- **Offline-first & privacy-first:** run locally by default; network tools are opt-in and auditable

---

## 2. Users & Use Cases

### 2.1 Target Users
| User | Need | How Copilot Helps |
|------|------|-------------------|
| Assay development scientist | Fast, reliable candidate designs | Automates QC, applies best-practice rules consistently |
| Bioinformatics scientist | Scale to many targets | Batch runs + structured output + reproducible traces |
| ML/bioinformatics engineer | Integrate into pipelines | CLI/API interface + tool abstractions |

### 2.2 Key Use Cases
- **UC1: Design a qPCR TaqMan assay** from a target sequence with standard constraints and receive ranked candidates.
- **UC2: Design a dPCR assay** with constraints tuned for partition-based detection (same design primitives, different defaults).
- **UC3: Assess “assay drift”**: evaluate existing primers/probe against new genomes for binding-site mismatches.
- **UC4: Generate a design package**: shareable report + JSON bundle that can be reviewed by lab teams.

---

## 3. Scope

### 3.1 In Scope (MVP)
- CLI-driven Copilot flow for single target FASTA:
  - primer pair generation
  - probe generation (TaqMan)
  - QC + scoring + ranking
  - report generation (Markdown) and machine output (JSON)
- Agent framework core:
  - tool interface + registry
  - typed request/response schemas
  - run trace, artifact storage, replay
  - evaluation harness with a small suite of canned targets
- Pluggable hooks for optional steps (specificity/mismatch checks), even if MVP uses a minimal implementation.

### 3.2 Out of Scope (MVP)
- Wet-lab validation, LIMS integration
- Full-scale cloud orchestration (can be future extension)
- Large curated reference databases bundled in repo
- Production-grade security/compliance controls (design for extension)

---

## 4. Product Requirements

### 4.1 Assay Design Copilot (Functional Requirements)

#### F1: Inputs
- Accept FASTA (file or string)
- Accept configuration for:
  - assay type: `qPCR` or `dPCR`
  - primer constraints (Tm, length, GC%, product size)
  - probe constraints (length, GC%, homopolymers, 5' base, Tm delta vs primers)
  - “soft” vs “strict” behavior (warn vs fail) for QC thresholds

#### F2: Primer/Probe Design
- Generate primer pairs using Primer3 (or existing internal engine)
- Generate a TaqMan probe between primers
  - Prefer Primer3 internal oligo when available
  - Fallback to deterministic rule-based probe selection when Primer3 yields no candidates

#### F3: QC, Scoring, Ranking
- Compute QC metrics (Tm, GC, structures, dimers, product size, 3' end rules, probe rules)
- Provide:
  - overall status derived from QC checks
  - composite score with transparent breakdown
- Filter out designs that fail hard constraints (configurable)

#### F4: Report Generation
Generate:
- `report.md`: design summary, parameters, top-N table, and QC breakdown
- `artifacts.json`: structured machine output
- `trace.jsonl` (or similar): run trace of tool calls for replay/debug

#### F5: Batch Mode (Optional in MVP)
- Accept multi-sequence FASTA, emit per-target outputs to a run directory.

### 4.2 Agent Framework (Functional Requirements)

#### A1: Tool Abstraction
- Tools are pure functions with:
  - name, description
  - typed input schema and output schema
  - declared side effects (none, filesystem, network)
  - version + dependency metadata (e.g., Primer3 version, reference build ID)
- Tool execution records:
  - inputs, outputs, runtime, errors
  - tool version (and dependency versions when relevant)

#### A2: Orchestration
- Support a deterministic, rule-driven workflow (MVP)
- Structure orchestration as **plan → execute → verify** stages (rule-based in MVP; swappable later)
- Optional LLM integration point for:
  - summarization, explanation, and interactive “why”/“what-if”
  - never required for core assay generation

#### A3: Run Trace, Replay, and Artifacts
- Every run creates a run directory:
  - config snapshot
  - tool-call trace
  - final outputs
  - tool/dependency version snapshot (for upgrade-safe replay)
- Provide “replay” that re-executes tool calls without an LLM, verifying determinism.

#### A4: Evaluation Harness
- Define a small suite of “golden” targets with expected invariants:
  - design returns at least N candidates (or explicit “no designs” with reasons)
  - top candidate meets key QC requirements
- Provide a CLI command to run the suite and summarize results.
- Add a regression mode to compare artifacts across tool/version changes (detect behavior drift)

---

## 5. Non-Functional Requirements
- **Reproducibility:** same inputs/config yield identical outputs (within controlled versioning)
- **Observability:** traceability of decisions and tool results
- **Extensibility:** add tools (BLAST, MSA, variant scan) without changing orchestration core
- **Upgradeability:** safely adopt tool/model updates via version pinning + eval gating; avoid breaking artifact contracts
- **Offline-first option:** allow running without network; external tools can be disabled
- **Security/privacy:** avoid leaking sequences by default; keep runs local unless explicitly exported

---

## 6. System Design

### 6.1 High-Level Flow
1. Parse input FASTA and validate sequence
2. Design primer pairs
3. For each pair: design probe (Primer3 internal oligo → fallback rule-based)
4. Run QC checks and compute scores
5. Rank and filter candidates
6. Generate outputs (JSON + report + trace)

### 6.2 Interfaces

#### CLI (MVP)
Example commands:
- `assay-copilot design --fasta target.fasta --assay qPCR --out runs/2026-01-06/`
- `assay-copilot replay --run runs/2026-01-06/`
- `assay-copilot eval --suite small`

#### API (V1)
- A minimal Python API (importable) that returns the JSON artifact in-memory.

#### UI Integration (V2)
- Add a “Copilot” entrypoint in the existing primer design app as a thin adapter:
  - UI collects inputs and displays results
  - Copilot remains headless and produces the same artifact bundle

### 6.3 Tech Stack (2026 “Rising”)
- **Concept:** Compound AI System — deterministic assay pipeline + optional LLM/RAG layer, both governed by traces + eval gates.
- **Core runtime:** Python 3.11+; `uv` (or Poetry); Pydantic v2 schemas; Typer CLI.
- **Agent/workflow:** LangGraph for stateful orchestration (rule-driven planner in MVP).
- **RAG + optimization (optional):**
  - LlamaIndex for retrieval over assay guidelines, run artifacts, and reference notes.
  - DSPy for prompt/program optimization where LLM outputs are used.
- **LLM serving (optional):** Ollama (local/dev), vLLM or TGI (self-host/prod), or hosted APIs behind a provider interface.
- **Data:** Polars for dataframe operations; DuckDB for local analytics and metadata/vector storage; artifacts in JSON/Parquet; traces in JSONL.
- **Assay tooling:** Primer3 (`primer3-py`), Biopython; pluggable specificity tools (BLAST/k-mer scan) as separate tools with explicit side effects.
- **ML frameworks (future):** PyTorch or JAX for learned scoring/ranking; Mojo for performance-critical sequence scanning kernels.
- **Eval/observability:** evaluation harness + regression diffs; OpenTelemetry traces; optional dashboards (LangSmith, Weights & Biases).
- **Packaging/deployment:** FastAPI (service), Docker images; Kubernetes (V2) if scaling agent runs and/or LLM serving.

---

## 7. Implementation Plan

### Phase 0: Foundations (1–2 days)
- Define schemas for:
  - `DesignRequest`, `DesignCandidate`, `QCResult`, `DesignArtifact`
  - `ToolCallRecord`, `RunMetadata`
- Define artifact/schema versioning + compatibility policy; capture tool/dependency versions in `RunMetadata`
- Implement tool registry + trace writer + run directory layout

### Phase 1: Copilot MVP (2–4 days)
- Implement Copilot workflow in deterministic mode
- Integrate with existing primer/probe design engine as a tool dependency
- Implement report generator (Markdown)

### Phase 2: Evaluation + Replay (1–2 days)
- Add replay command
- Add evaluation suite + minimal assertions

### Phase 3: Integrations (future)
- UI integration into existing primer design app
- Optional LLM summarization/Q&A layer
- Optional specificity and mismatch tools:
  - k-mer screening, BLAST, MSA, lineage-aware mismatch reporting

---

## 8. Risks & Mitigations
- **Primer3 may yield no probe candidates** for some regions due to constraints  
  Mitigation: two-pass “relax and retry” + deterministic fallback; report explicit reasons.
- **Network-restricted environments** limit external database checks  
  Mitigation: pluggable tools; offline mode; allow user-provided reference FASTA.
- **Overreliance on LLM** can reduce reproducibility  
  Mitigation: core pipeline deterministic; LLM used only for summarization/explanations.
- **Tool/model churn introduces silent behavior drift**  
  Mitigation: pin versions in config; record versions in traces; run eval/regression before upgrades.

---

## 9. Appendix

### 9.1 Definitions
- **qPCR:** real-time PCR using fluorescence to quantify amplification.
- **dPCR:** partition-based PCR enabling absolute quantification by counting positive partitions.
- **Run trace:** a structured log of tool calls, inputs, outputs, and timings to support replay and audits.
