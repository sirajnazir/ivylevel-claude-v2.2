# IvyLevel Agent Catalog

**Version:** v15.0.0
**Last Updated:** January 21, 2026

---

## Overview

IvyLevel uses a multi-agent architecture where specialized agents handle different coaching tasks. All agents are orchestrated through the main FastAPI application.

---

## Active Agents

### ExecutionChatAgent (v5.4)

**File:** `agents/execution_chat.py`
**Purpose:** Daily execution coaching and weekly planning

**Capabilities:**
- Weekly plan generation
- Task prioritization
- Deadline reminders
- Progress tracking
- EDS (Execution Distress Score) calculation

**Tools Available:**
- `get_weekly_plan` - Fetch current weekly plan
- `update_task_status` - Mark tasks complete
- `check_deadlines` - Check upcoming deadlines
- `get_eds_score` - Calculate distress score
- `get_game_plan_context` - Access strategic plan

**System Prompt Features:**
- Jenny voice (supportive, encouraging)
- Game plan context injection
- Coaching asset integration (E1-E22 techniques)

---

### GamePlanAgent

**File:** `agents/gameplan.py`
**Purpose:** Generate 4-year strategic roadmaps

**Capabilities:**
- Year-by-year planning
- Project recommendations
- Award/program suggestions
- Spike development strategy

**Input:** Profile data, assessment results
**Output:** Structured game plan with projects

---

### AwardsAgent

**File:** `agents/awards.py`
**Purpose:** Match students to scholarships and awards

**Capabilities:**
- Eligibility matching
- Deadline tracking
- Application strategy
- Prestige scoring

**Data Source:** `awards` table

---

### ProgramsAgent

**File:** `agents/programs.py`
**Purpose:** Recommend summer programs and opportunities

**Capabilities:**
- Program matching by interest
- Selectivity assessment
- Timeline planning
- Application guidance

**Data Source:** `opportunities` table

---

### AssessmentAgent

**File:** `agents/assessment.py`
**Purpose:** Process assessment frame responses

**Capabilities:**
- Score calculation
- Archetype detection
- Spike identification
- Narrative generation

---

### NarrativeSynthesis

**File:** `agents/narrative_synthesis.py`
**Purpose:** Generate spike narratives and summaries

**LLM:** Google Gemini (preferred) or OpenAI
**Output:** Compelling narrative text

---

### ExtracurricularsAgent

**File:** `agents/extracurriculars.py`
**Purpose:** Extracurricular activity coaching

**Capabilities:**
- EC recommendations
- Impact assessment
- Balance analysis
- Leadership opportunities

---

### OpportunityAgent

**File:** `agents/opportunity.py`
**Purpose:** Opportunity recommendations and matching

**Capabilities:**
- Summer program matching
- Research opportunity suggestions
- Internship recommendations

---

## Agent Architecture

### ReAct Pattern

All agents use the ReAct (Reasoning + Acting) pattern:

```
Observation → Thought → Action → Observation → ...
```

This enables:
- Tool usage based on context
- Multi-step reasoning
- Self-correction

### Memory Integration

Agents access memory through:
1. **Session memory** - Current conversation context
2. **Profile memory** - Student profile data
3. **Game plan memory** - Strategic context

---

## Adding New Agents

1. Create file in `agents/` directory
2. Inherit from base agent class
3. Define tools and system prompt
4. Register in `main.py`
5. Add API route if needed

**Template:**
```python
from agno import Agent, Tool

class NewAgent(Agent):
    def __init__(self):
        super().__init__(
            name="NewAgent",
            system_prompt="...",
            tools=[...]
        )
```

---

## Dormant Agents

### Letta Agents (`/letta/`)
- **Status:** Code complete, feature-flagged OFF
- **Enable:** Set `LETTA_ENABLED=true`
- **Purpose:** Advanced memory and A2A communication
- **Note:** Evaluation planned for v11.0
