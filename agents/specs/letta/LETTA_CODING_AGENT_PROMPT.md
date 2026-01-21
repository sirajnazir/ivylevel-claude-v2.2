# IVYLEVEL LETTA IMPLEMENTATION - CODING AGENT PROMPT
## Strict Execution Protocol with Mandatory Analysis Phase

**Version:** 1.0
**Date:** January 2026
**Classification:** STRICT EXECUTION - NO DEVIATION ALLOWED

---

## ⚠️ CRITICAL: READ BEFORE ANY ACTION

This prompt governs the implementation of Letta-based autonomous agents for IvyLevel. You MUST follow this protocol exactly. Any deviation will result in rejected work.

**THE THREE PHASES ARE SEQUENTIAL AND GATED:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: ANALYSIS (MANDATORY FIRST)                                        │
│  ════════════════════════════════════                                       │
│  • Analyze current codebase thoroughly                                       │
│  • Compare against Letta proposal                                           │
│  • Document gaps, risks, conflicts                                          │
│  • Produce: LETTA_IMPLEMENTATION_ANALYSIS.md                                │
│                                                                              │
│  🛑 STOP - Wait for human approval before proceeding                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: REVIEW & APPROVAL (HUMAN GATE)                                    │
│  ═══════════════════════════════════════                                    │
│  • Human reviews analysis document                                          │
│  • Human approves, rejects, or requests changes                            │
│  • You DO NOT proceed until explicit "APPROVED" signal                      │
│                                                                              │
│  🛑 STOP - Do not write ANY implementation code until approved              │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: ADDITIVE IMPLEMENTATION (AFTER APPROVAL ONLY)                     │
│  ══════════════════════════════════════════════════════                     │
│  • Implement ONLY approved items                                            │
│  • ZERO modifications to existing files (except imports)                    │
│  • All new code in new files/directories                                    │
│  • Comprehensive testing before delivery                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: IMPACT, GAP & FEASIBILITY ANALYSIS

### 1.1 Objective

Before writing ANY implementation code, you must produce a comprehensive analysis document that critically evaluates the Letta implementation proposal against the actual current IvyLevel codebase.

### 1.2 Required Analysis Sections

Your analysis document (`LETTA_IMPLEMENTATION_ANALYSIS.md`) MUST contain ALL of the following sections:

#### Section A: Current Codebase Inventory

**You must thoroughly examine and document:**

```
DIRECTORIES TO ANALYZE:
├── agents/
│   ├── agents/                    # All existing agent files
│   ├── intelligence/              # Intelligence layer (from previous work)
│   │   ├── assets/               # 139 techniques, loader, CLI
│   │   ├── registry/             # AssetRegistry, AssetSelector
│   │   ├── primitives/           # CoachingAsset, Goal, etc.
│   │   └── graphs/               # Any existing graph implementations
│   ├── routers/                  # API endpoints
│   ├── services/                 # Existing services
│   └── models/                   # Pydantic models
├── supabase/
│   └── migrations/               # All database migrations
└── Any other relevant directories
```

**For each existing component, document:**
1. File path and purpose
2. Key classes/functions
3. Dependencies (imports)
4. Database tables used
5. External service integrations

#### Section B: Proposal vs Reality Comparison

**Create a detailed comparison table:**

| Proposal Element | Proposed Implementation | Current Reality | Gap/Conflict | Severity |
|-----------------|------------------------|-----------------|--------------|----------|
| Shared Memory Blocks | Letta memory_blocks | ? | ? | 🔴🟡🟢 |
| Agent-to-Agent Communication | Letta send_message tools | ? | ? | 🔴🟡🟢 |
| Background Monitoring | APScheduler service | ? | ? | 🔴🟡🟢 |
| HITL Approval | Custom tool + queue | ? | ? | 🔴🟡🟢 |
| 139 Techniques Integration | search_techniques tool | Already exists in intelligence/ | ? | 🔴🟡🟢 |
| Student Profiles | Letta memory block | Supabase student_profiles | ? | 🔴🟡🟢 |
| Assessment Frames 1-6 | Keep existing | ? | ? | 🔴🟡🟢 |
| ... | ... | ... | ... | ... |

**Severity Legend:**
- 🔴 CRITICAL: Blocks implementation or breaks existing functionality
- 🟡 MODERATE: Requires careful handling, potential conflicts
- 🟢 LOW: Minor or no issues

#### Section C: Conflict Analysis

**Identify ALL potential conflicts:**

```markdown
## C.1 Database Conflicts

For each proposed Letta feature, analyze:
- Does it require new tables? Which ones?
- Does it conflict with existing tables?
- Foreign key relationships affected?
- Data migration needed?

## C.2 API Endpoint Conflicts

- Existing endpoints that might conflict
- URL namespace collisions
- Authentication/authorization impacts

## C.3 Agent Logic Conflicts

- Existing agent implementations
- How they currently work
- What changes would break them
- What can safely coexist

## C.4 Service Conflicts

- Existing background services
- Scheduled jobs
- External API integrations

## C.5 Import/Dependency Conflicts

- Package version conflicts
- Circular import risks
- New dependencies required
```

#### Section D: Feasibility Assessment

**For each major component in the proposal:**

```markdown
## D.1 Letta Integration Feasibility

### Letta Cloud vs Self-Hosted
- Recommendation: [Cloud | Self-Hosted]
- Rationale: [Why]
- Cost implications: [Estimate]
- Infrastructure requirements: [List]

### Memory Block Schema
- Proposed schema fits student data: [Yes/No/Partially]
- Character limits sufficient: [Yes/No]
- Required modifications: [List]

### Agent Architecture
- 5 agents (Orchestrator, GamePlan, Execution, Awards, Essay) + 1 dormant (Assessment)
- Feasible with Letta: [Yes/No/Concerns]
- Performance implications: [Analysis]

## D.2 Integration with Existing 139 Techniques

Current state:
- Location: [Path]
- Format: [YAML/JSON/DB]
- Access method: [API/Direct]

Integration approach:
- [Describe how Letta agents will access techniques]
- [Any modifications needed to existing code]

## D.3 Assessment Frames 1-6 Preservation

Current flow:
- [Document exact current flow]
- [Entry points]
- [Data storage]

Proposed transition point:
- [Where Letta takes over]
- [How data flows from Frames to Letta]
- [Risk of breaking existing flow]

## D.4 Background Monitoring Feasibility

Current background jobs:
- [List any existing]

APScheduler integration:
- Deployment considerations
- Process management
- Failure handling
```

#### Section E: Risk Register

**Create comprehensive risk register:**

| Risk ID | Risk Description | Probability | Impact | Mitigation | Owner |
|---------|-----------------|-------------|--------|------------|-------|
| R001 | Letta service outage breaks coaching | Medium | Critical | Fallback to non-Letta flow | TBD |
| R002 | Memory block limits exceeded | High | Medium | Multiple blocks per category | TBD |
| R003 | Existing agent logic broken | Low | Critical | Additive-only implementation | TBD |
| R004 | Assessment Frames flow disrupted | Medium | Critical | Isolated transition point | TBD |
| R005 | Database schema conflicts | Medium | High | New tables only, no modifications | TBD |
| ... | ... | ... | ... | ... | ... |

#### Section F: Recommendations

**Provide your independent recommendations:**

```markdown
## F.1 Agreements with Proposal

[List aspects of the proposal you agree with and why]

## F.2 Disagreements with Proposal

[List aspects you disagree with, with technical justification]

## F.3 Suggested Modifications

[Propose specific changes to the implementation plan]

## F.4 Implementation Sequence

[Your recommended order of implementation, with rationale]

## F.5 Testing Strategy

[How each component should be tested before integration]
```

#### Section G: Additive Implementation Plan

**Detail exactly what will be ADDED (not modified):**

```markdown
## G.1 New Directories to Create

/agents/letta/
├── __init__.py
├── client.py                 # Letta client wrapper
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py       # Orchestrator agent config
│   ├── gameplan.py           # GamePlan agent config
│   ├── execution.py          # Execution agent config
│   ├── awards.py             # Awards agent config
│   ├── essay.py              # Essay agent config
│   └── assessment.py         # Assessment agent config (dormant)
├── memory/
│   ├── __init__.py
│   ├── blocks.py             # Memory block definitions
│   └── sync.py               # Sync with existing data
├── tools/
│   ├── __init__.py
│   ├── hitl.py               # HITL approval tool
│   ├── monitoring.py         # Deadline/opportunity tools
│   └── techniques.py         # Bridge to existing 139 techniques
├── services/
│   ├── __init__.py
│   ├── monitoring.py         # APScheduler service
│   └── transition.py         # Assessment Frames → Letta transition
└── routers/
    ├── __init__.py
    └── letta.py              # New API endpoints (namespaced)

## G.2 New Database Tables (Migrations)

[List exact new tables - NO modifications to existing]

## G.3 New Dependencies

[List new packages needed in requirements.txt]

## G.4 Configuration

[New environment variables, config files]
```

#### Section H: Pre-Implementation Checklist

**All items must be verified before Phase 3:**

```markdown
## H.1 Codebase Understanding

- [ ] I have read and understood ALL files in agents/agents/
- [ ] I have read and understood ALL files in agents/intelligence/
- [ ] I have read and understood ALL database migrations
- [ ] I have read and understood ALL API routers
- [ ] I have documented the Assessment Frames 1-6 flow completely

## H.2 Conflict Verification

- [ ] No proposed changes modify existing agent files
- [ ] No proposed changes modify existing database tables
- [ ] No proposed changes modify existing API endpoints
- [ ] No proposed changes break existing imports
- [ ] All new code is in isolated new directories

## H.3 Letta Compatibility

- [ ] Verified Letta API compatibility with proposed architecture
- [ ] Verified memory block limits are sufficient
- [ ] Verified agent-to-agent communication patterns work
- [ ] Verified tool registration process

## H.4 Testing Plan Ready

- [ ] Unit test strategy defined
- [ ] Integration test strategy defined
- [ ] Rollback plan documented
```

### 1.3 Analysis Document Delivery

**Upon completing Phase 1, you must:**

1. Create the file: `LETTA_IMPLEMENTATION_ANALYSIS.md`
2. Place it in: `/agents/specs/letta/`
3. Explicitly state: "PHASE 1 COMPLETE - AWAITING HUMAN APPROVAL"
4. **DO NOT** proceed to any implementation

---

## PHASE 2: HUMAN REVIEW GATE

### 2.1 Wait Protocol

After delivering the analysis document:

1. **STOP ALL IMPLEMENTATION WORK**
2. Wait for explicit human response
3. Human will respond with one of:
   - `APPROVED` - Proceed to Phase 3
   - `APPROVED WITH CHANGES: [list]` - Update analysis, then proceed
   - `REJECTED: [reason]` - Revise analysis, return to Phase 1
   - `QUESTIONS: [list]` - Answer questions, remain in Phase 2

### 2.2 What You May NOT Do During Phase 2

- ❌ Create any implementation files
- ❌ Write any agent code
- ❌ Create any database migrations
- ❌ Install any packages
- ❌ Modify any existing files
- ❌ "Pre-prepare" implementation code

### 2.3 What You MAY Do During Phase 2

- ✅ Answer clarifying questions
- ✅ Revise the analysis document
- ✅ Provide additional research
- ✅ Create diagrams or visualizations

---

## PHASE 3: ADDITIVE IMPLEMENTATION

### 3.1 Entry Criteria

You may ONLY enter Phase 3 when:

1. Human has explicitly said "APPROVED" or "APPROVED WITH CHANGES"
2. All requested changes have been incorporated
3. You have re-confirmed the Pre-Implementation Checklist

### 3.2 ABSOLUTE RULES - VIOLATION = IMMEDIATE REJECTION

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         IMPLEMENTATION RULES                                   ║
║                         ════════════════════                                   ║
║                                                                                ║
║  RULE 1: ZERO MODIFICATIONS TO EXISTING FILES                                 ║
║  ───────────────────────────────────────────                                  ║
║  • You may NOT modify any file in agents/agents/*.py                          ║
║  • You may NOT modify any file in agents/intelligence/*.py                    ║
║  • You may NOT modify any existing database migration                         ║
║  • You may NOT modify any existing router                                     ║
║  • You may NOT modify any existing service                                    ║
║  • You may NOT modify any existing model                                      ║
║                                                                                ║
║  EXCEPTION: Adding imports to __init__.py files ONLY if needed for            ║
║  new code to be importable, and ONLY with explicit documentation.             ║
║                                                                                ║
║  ─────────────────────────────────────────────────────────────────────────────║
║                                                                                ║
║  RULE 2: ALL NEW CODE IN NEW DIRECTORIES                                      ║
║  ───────────────────────────────────────                                      ║
║  • Create /agents/letta/ as the root for ALL Letta code                       ║
║  • No Letta code outside this directory                                       ║
║  • Clear separation from existing codebase                                    ║
║                                                                                ║
║  ─────────────────────────────────────────────────────────────────────────────║
║                                                                                ║
║  RULE 3: NEW DATABASE TABLES ONLY                                             ║
║  ───────────────────────────────                                              ║
║  • Create new migrations for new tables                                       ║
║  • Table names MUST be prefixed with "letta_" for clarity                     ║
║  • NO foreign keys to existing tables without explicit approval               ║
║  • NO modifications to existing table schemas                                 ║
║                                                                                ║
║  ─────────────────────────────────────────────────────────────────────────────║
║                                                                                ║
║  RULE 4: NAMESPACED API ENDPOINTS                                             ║
║  ───────────────────────────────                                              ║
║  • All new endpoints under /api/letta/ prefix                                 ║
║  • No collision with existing endpoints                                       ║
║  • New router file, not modifications to existing                             ║
║                                                                                ║
║  ─────────────────────────────────────────────────────────────────────────────║
║                                                                                ║
║  RULE 5: FEATURE FLAGS FOR ACTIVATION                                         ║
║  ─────────────────────────────────────                                        ║
║  • All Letta features behind feature flags                                    ║
║  • Default: DISABLED                                                          ║
║  • Can be enabled per-student or globally                                     ║
║  • Existing flow works unchanged when Letta disabled                          ║
║                                                                                ║
║  ─────────────────────────────────────────────────────────────────────────────║
║                                                                                ║
║  RULE 6: BRIDGE PATTERN FOR INTEGRATION                                       ║
║  ─────────────────────────────────────                                        ║
║  • Create bridge/adapter classes to connect to existing code                  ║
║  • Existing code calls INTO Letta (not Letta modifying existing)             ║
║  • Example: TechniqueBridge reads from existing 139 techniques                ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### 3.3 Implementation Order

**Follow this exact sequence:**

```
STEP 1: Directory Structure
─────────────────────────
Create empty directory structure with __init__.py files
Verify no conflicts with existing directories

STEP 2: Configuration & Dependencies
────────────────────────────────────
Add new dependencies to requirements.txt (new section, clearly marked)
Create Letta configuration module
Add environment variable documentation

STEP 3: Database Migrations
───────────────────────────
Create new migration file for letta_* tables
Tables: letta_agent_registry, letta_memory_snapshots, letta_approval_queue
Run migration, verify no impact on existing tables

STEP 4: Letta Client Wrapper
────────────────────────────
Create client.py with Letta client initialization
Add connection management
Add error handling and fallback logic

STEP 5: Memory Block Definitions
────────────────────────────────
Define all memory block schemas
Create sync utilities for existing student data
Implement StudentProfileBridge

STEP 6: Agent Configurations
────────────────────────────
Create each agent configuration file
Orchestrator → GamePlan → Execution → Awards → Essay → Assessment (dormant)
Include all instructions, tools, memory blocks

STEP 7: Custom Tools
────────────────────
HITL approval tool
Technique search bridge (connects to existing 139)
Monitoring tools (deadline, opportunity)

STEP 8: Background Monitoring Service
─────────────────────────────────────
APScheduler setup
Job definitions
Feature flag checks before any action

STEP 9: API Endpoints
─────────────────────
New router: /api/letta/*
Endpoints for chat, agent management, monitoring

STEP 10: Transition Logic
─────────────────────────
Assessment Frames completion → Letta agent creation
Feature flag gated
Preserves existing flow when disabled

STEP 11: Testing
────────────────
Unit tests for each new component
Integration tests for agent interactions
End-to-end test for student journey
Verify existing tests still pass

STEP 12: Documentation
──────────────────────
README for /agents/letta/
API documentation
Deployment guide
```

### 3.4 Code Quality Requirements

**Every file must include:**

```python
"""
Module: [module_name]
Purpose: [Clear description]
Created: [Date]
Author: Coding Agent

ADDITIVE IMPLEMENTATION - Does not modify any existing IvyLevel code.
Part of Letta integration layer.

Dependencies:
- [List all imports and why needed]

Integration Points:
- [How this connects to existing code, if at all]
"""
```

**Testing requirements:**

```python
# Every new module must have corresponding test file
# Test file location: /agents/letta/tests/

# Minimum test coverage:
# - All public functions
# - Error cases
# - Edge cases
# - Integration points
```

### 3.5 Delivery Checklist

**Before declaring implementation complete:**

```markdown
## Implementation Delivery Checklist

### Code Quality
- [ ] All files have proper docstrings
- [ ] No hardcoded values (use config/env vars)
- [ ] Error handling in place
- [ ] Logging added for debugging
- [ ] Type hints on all functions

### Rule Compliance
- [ ] ZERO existing files modified (verified)
- [ ] All new code in /agents/letta/
- [ ] All new tables prefixed with letta_
- [ ] All new endpoints under /api/letta/
- [ ] Feature flags implemented

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Existing tests still pass (no regression)
- [ ] Manual testing completed

### Documentation
- [ ] README.md in /agents/letta/
- [ ] API documentation
- [ ] Environment variable documentation
- [ ] Deployment instructions

### Rollback
- [ ] Feature flags allow complete disable
- [ ] No data dependencies that prevent rollback
- [ ] Documented rollback procedure
```

---

## REFERENCE: Proposal Documents

The Letta implementation proposal is contained in:

1. `IVYLEVEL_LETTA_IMPLEMENTATION_SPEC.md` - Full technical specification
2. `IVYLEVEL_LETTA_ARCHITECTURE_VISUAL.md` - Visual architecture diagrams
3. `IVYLEVEL_MULTI_AGENT_PLATFORM_EVALUATION.md` - Platform evaluation rationale

**Key points from proposal to validate:**

| Component | Proposal Says | Verify Against Reality |
|-----------|--------------|----------------------|
| Assessment Frames 1-6 | Keep existing, don't modify | Confirm exact current flow |
| Assessment Agent | DORMANT - pass-through only | Confirm no Assessment Agent exists yet |
| 139 Techniques | Already in intelligence/assets/ | Confirm location and format |
| Student Profiles | In Supabase | Confirm table schema |
| Existing Agents | In agents/agents/*.py | Document all 7 agents |
| Background Jobs | May not exist | Confirm any existing schedulers |

---

## SUMMARY: Your Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  START                                                                       │
│    │                                                                         │
│    ▼                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 1: Analyze codebase, compare to proposal, document everything   │  │
│  │          Output: LETTA_IMPLEMENTATION_ANALYSIS.md                     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│    │                                                                         │
│    ▼                                                                         │
│  🛑 STOP - Output: "PHASE 1 COMPLETE - AWAITING HUMAN APPROVAL"             │
│    │                                                                         │
│    │ [Wait for human response]                                              │
│    │                                                                         │
│    ▼                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 2: Human reviews, approves/rejects/requests changes             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│    │                                                                         │
│    │ [Only proceed when "APPROVED"]                                         │
│    │                                                                         │
│    ▼                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 3: Implement ADDITIVELY following strict rules                  │  │
│  │          • Zero modifications to existing code                        │  │
│  │          • All new code in /agents/letta/                            │  │
│  │          • Feature flags for activation                               │  │
│  │          • Comprehensive testing                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│    │                                                                         │
│    ▼                                                                         │
│  COMPLETE - Deliver tested, documented, additive implementation              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## FINAL REMINDER

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║   YOUR FIRST ACTION MUST BE PHASE 1 ANALYSIS.                                 ║
║                                                                                ║
║   DO NOT WRITE ANY IMPLEMENTATION CODE UNTIL APPROVED.                        ║
║                                                                                ║
║   IF YOU BREAK EXISTING FUNCTIONALITY, YOUR WORK WILL BE REJECTED.            ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```
