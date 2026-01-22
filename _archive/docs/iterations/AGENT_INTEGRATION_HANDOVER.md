# Agent Integration Handover Package v1.0
## IvyQuest GamePlan Multi-Agent Platform

**Document Type**: Claude Code Implementation Instructions
**Version**: 1.0
**Date**: January 2026
**Prerequisite**: Strategic Intelligence Enrichment Complete (bb19028)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Implementation Scope](#3-implementation-scope)
4. [Phase 1: EC Agent Creation](#4-phase-1-ec-agent-creation)
5. [Phase 2: Awards Agent Enhancement](#5-phase-2-awards-agent-enhancement)
6. [Phase 3: Programs Agent Enhancement](#6-phase-3-programs-agent-enhancement)
7. [Phase 4: Orchestration Wiring](#7-phase-4-orchestration-wiring)
8. [Testing & Validation](#8-testing--validation)
9. [Guardrails & Best Practices](#9-guardrails--best-practices)

---

## 1. Executive Summary

### 1.1 Goal

Wire the GamePlan multi-agent system to produce intelligent, identity-driven recommendations using the newly enriched strategic intelligence data.

### 1.2 Data Flow

```
[Student Assessment]
        |
        v
   EC AGENT (runs first)
   - TYPE-013: Portfolio Optimization
   - TYPE-014: Narrative Synthesis
   - TYPE-015: Impact Assessment
        |
        | identity_synthesis (spike, archetype, pillars)
        v
   PARALLEL EXECUTION
   +----------------+  +------------------+
   | AWARDS AGENT   |  | PROGRAMS AGENT   |
   | Uses: identity |  | Uses: identity   |
   | + enriched DB  |  | + enriched DB    |
   +-------+--------+  +--------+---------+
           |                    |
           v                    v
        SYNTHESIS
   - Combine EC + Awards + Programs
   - Generate unified GamePlan
   - Timeline with milestones
```

### 1.3 Deliverables

| Phase | Deliverable | Priority |
|-------|-------------|----------|
| 1 | EC Agent (`extracurriculars_agent.py`) | P0 |
| 2 | Enhanced Awards Agent | P0 |
| 3 | Enhanced Programs Agent (renamed from Opportunity) | P0 |
| 4 | Orchestration in GamePlan Agent | P0 |
| 5 | Integration tests | P1 |

---

## 2. Current State Analysis

### 2.1 Existing Agent Files

```
agents/agents/
├── base.py                    # BaseAgent with state versioning
├── assessment_agent.py        # Student assessment
├── gameplan_agent.py          # Main orchestrator (needs wiring)
├── awards_agent.py            # Exists (needs enhancement)
├── opportunity_agent.py       # Rename to programs_agent.py
├── execution_agent.py         # Task execution
└── narrative_synthesis_agent.py # Narrative generation
```

### 2.2 Enriched Data Available

```
agents/seeds/enriched/
├── awards_enriched.json       # 97 awards with strategic intelligence
├── programs_enriched.json     # 58 programs with strategic intelligence
└── enrichment_metadata.json   # Tracking metadata
```

---

## 3. Implementation Scope

### 3.1 What TO Build

| Component | Description |
|-----------|-------------|
| EC Agent | New agent for portfolio analysis, narrative synthesis, impact assessment |
| Awards Agent Enhancement | Use enriched data, filter by identity/archetype, rank by fit |
| Programs Agent Enhancement | Use enriched data, filter by identity/archetype, recommend synergies |
| Orchestration | EC → parallel(Awards, Programs) → Synthesize |
| Identity Handoff | EC output feeds Awards/Programs inputs |

### 3.2 What NOT TO Build

| Don't Build | Reason |
|-------------|--------|
| New frameworks | Use existing BaseAgent |
| New LLM wrappers | Use existing ChatOpenAI |
| Custom orchestration | Keep simple async flow |
| Vector search | Not needed for 155 items |
| EQ layer | Parked for future phase |

---

*Full implementation specifications in handover document*
*See: AGENT_INTEGRATION_HANDOVER.md for complete code*
