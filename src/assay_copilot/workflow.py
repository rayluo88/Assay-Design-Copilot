"""
Agent Workflow Orchestration.

Defines the `LangGraph` state machine that governs the assay design process.
It wires together the Primer Design, Probe Design, and QC steps into a coherent,
stateful execution graph (Plan -> Execute -> Verify).
"""
from typing import List, Dict, TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END

from .schema import DesignRequest, DesignCandidate, QCResult, DesignArtifact
from .primer3_engine import Primer3Engine
from .probe_designer import RuleBasedProbeDesigner
from .qc import QCEngine

# Define State
class AgentState(TypedDict):
    request: DesignRequest
    candidates: Annotated[List[DesignCandidate], operator.add]
    qc_results: Dict[int, QCResult]
    artifact: DesignArtifact

# Initialize Tools
# In a real framework, these would be injected or retrieved from Registry
primer_tool = Primer3Engine()
probe_tool = RuleBasedProbeDesigner()
qc_tool = QCEngine()

# Node Definitions
def node_design_primers(state: AgentState):
    print("--- Node: Design Primers ---")
    req = state['request']
    candidates = primer_tool.execute(req)
    # Filter candidates? For now just pass all
    return {"candidates": candidates}

def node_design_probes(state: AgentState):
    print("--- Node: Design Probes ---")
    candidates = state['candidates']
    req = state['request']
    
    # We need to mutate candidates to add probes if missing
    updated_candidates = []
    # Note: State is immutable-ish in some paradigms, but here we return updates.
    # However, 'candidates' is annotated with operator.add, so we might append?
    # Actually, we want to Replace or Modify. 
    # For MVP simplicity, we will assume we are rebuilding the list for the next step 
    # but LangGraph operator.add appends. 
    # Let's ignore the annotation for a moment and just return the new list to overwrite if we change the reducer.
    
    # Actually, let's keep it simple: just iterate and modify constraints
    # Is designing probes needed?
    for cand in candidates:
        if not cand.probe:
            cand.probe = probe_tool.execute(cand, req.target_sequence)
            
    # In LangGraph with operator.add, returning {"candidates": ...} would append.
    # We should probably have a reducer that replaces.
    # For this MVP code, I'll rely on object mutation (python list is mutable) 
    # or Assume the 'candidates' in state is the reference.
    return {} 

def node_qc_scoring(state: AgentState):
    print("--- Node: QC & Scoring ---")
    candidates = state['candidates']
    qc_map = {}
    for i, cand in enumerate(candidates):
        result = qc_tool.execute(cand)
        qc_map[i] = result
        
    return {"qc_results": qc_map}

def node_finalize_artifact(state: AgentState):
    print("--- Node: Finalize Artifact ---")
    
    # Find best candidate
    qc_results = state['qc_results']
    best_idx = -1
    best_score = -1.0
    
    for idx, res in qc_results.items():
        if res.status != "FAIL" and res.score > best_score:
            best_score = res.score
            best_idx = idx
            
    artifact = DesignArtifact(
        request=state['request'],
        candidates=state['candidates'],
        qc_results=qc_results,
        best_candidate_index=best_idx if best_idx != -1 else None,
        metadata={"generated_by": "AssayCopilot_v0.1"}
    )
    return {"artifact": artifact}

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("design_primers", node_design_primers)
workflow.add_node("design_probes", node_design_probes)
workflow.add_node("qc_scoring", node_qc_scoring)
workflow.add_node("finalize", node_finalize_artifact)

# Define Edges
workflow.set_entry_point("design_primers")
workflow.add_edge("design_primers", "design_probes")
workflow.add_edge("design_probes", "qc_scoring")
workflow.add_edge("qc_scoring", "finalize")
workflow.add_edge("finalize", END)

# Compile
app = workflow.compile()
