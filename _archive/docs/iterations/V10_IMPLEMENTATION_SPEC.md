# IvyQuest v10.0 Implementation Specification

**Version:** 1.0
**Created:** 2026-01-10
**Status:** AWAITING APPROVAL
**Based On:** V10_GAP_ANALYSIS_V3_AGNO.md

---

## Implementation Decision Required

Before proceeding, the following architectural decision needs approval:

### Option A: Full Agno Migration (Recommended per V2 Spec)
- **Effort:** 7 weeks
- **Risk:** High (full framework change)
- **Benefit:** 529× performance improvement, native proactive workflows
- **Trade-off:** Complete rewrite of agent layer

### Option B: Incremental Enhancement (Pragmatic)
- **Effort:** 4 weeks
- **Risk:** Low (keep working code)
- **Benefit:** Faster delivery, less disruption
- **Trade-off:** Won't achieve Agno performance benefits

### Option C: Hybrid Approach (Balanced)
- **Effort:** 5 weeks
- **Risk:** Medium
- **Benefit:** Keep NarrativeSynthesis (working), migrate high-value agents
- **Trade-off:** Mixed architecture temporarily

**Recommendation:** Option C - Hybrid Approach

---

## Phase 1: Foundation & Quick Wins (Week 1)

### 1.1 Database Schema Updates

**Task 1.1.1:** Create evaluation tables
```sql
-- File: supabase/migrations/020_evaluation_schema.sql

-- Golden dataset for evaluation
CREATE TABLE IF NOT EXISTS evaluation_golden (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID,
  input_profile JSONB NOT NULL,
  expected_outputs JSONB NOT NULL,
  jenny_annotations JSONB,
  difficulty_tier VARCHAR(20) CHECK (difficulty_tier IN ('easy', 'medium', 'hard')),
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Evaluation run results
CREATE TABLE IF NOT EXISTS evaluation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id VARCHAR(100) NOT NULL,
  agent_version VARCHAR(50) NOT NULL,
  golden_id UUID REFERENCES evaluation_golden(id),
  actual_outputs JSONB NOT NULL,
  objective_scores JSONB,
  llm_judge_scores JSONB,
  overall_score FLOAT,
  passed BOOLEAN,
  duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Proactive workflow state
CREATE TABLE IF NOT EXISTS workflow_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  workflow_name VARCHAR(100) NOT NULL,
  last_run TIMESTAMPTZ,
  next_run TIMESTAMPTZ,
  run_count INTEGER DEFAULT 0,
  state JSONB DEFAULT '{}',
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(profile_id, workflow_name)
);

-- Add workflow preference columns to profiles
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS preferred_contact_time TIME DEFAULT '15:00';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{"email": true, "push": true, "sms": false}';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_golden ON evaluation_runs(golden_id);
CREATE INDEX IF NOT EXISTS idx_workflow_state_profile ON workflow_state(profile_id);
CREATE INDEX IF NOT EXISTS idx_workflow_state_next_run ON workflow_state(next_run) WHERE enabled = true;
```

**Estimated effort:** 0.5 days
**Priority:** P0
**Dependencies:** None

---

### 1.2 AssessmentContract Schema Enhancement

**Task 1.2.1:** Update TypeScript types
```typescript
// File: lib/types/assessmentContract.ts

export interface AssessmentContract {
  // Core identification
  profile_id: string;
  assessment_timestamp: string;
  version: string;

  // Pillar Scores (0-100 scale)
  scores: {
    aptitude: number;
    passion: number;
    community: number;
    narrative: number;
    overall: number;
  };

  // Dimensional breakdown for UI
  dimensional_breakdown: {
    dimension: string;
    score: number;
    weight: number;
    contributing_factors: string[];
  }[];

  // Narrative outputs (from NarrativeSynthesisAgent)
  narrative: {
    brand_statement: string;
    narrative_dna: string;
    first_principle: string;
    themes: string[];
    confidence: number;
  };

  // Raw profile data
  profile_data: {
    identity: IdentityData;
    operating: OperatingData;
    aptitude: AptitudeData;
    passion: PassionData;
    community: CommunityData;
  };

  // Archetype detection
  archetype: {
    id: string;
    label: string;
    confidence: number;
    rationale: string;
    secondary?: string;
  };

  // Gap analysis
  gaps: {
    id: string;
    priority: 'P1' | 'P2' | 'P3';
    pillar: 'aptitude' | 'passion' | 'community' | 'narrative';
    title: string;
    description: string;
    impact: number;
    suggested_actions: string[];
  }[];

  // Helping/Holding factors
  factors: {
    helping: { factor: string; impact: number; pillar: string }[];
    holding: { factor: string; impact: number; pillar: string }[];
  };

  // Hidden fields (internal only - never expose to UI)
  _hidden: {
    probabilities: Record<string, number>;
    hidden_target: string;
    cri: number;
    chetty_baseline: number;
  };

  // Agent coordination
  _agent_metadata: {
    processing_agent: string;
    processing_time_ms: number;
    requires_handoff: boolean;
    handoff_reason?: string;
  };
}
```

**Task 1.2.2:** Update results store
```typescript
// File: lib/store/useResultsStore.ts - Update imports and interface
import { AssessmentContract } from '@/lib/types/assessmentContract';

// Add to store interface
assessmentContract: AssessmentContract | null;
setAssessmentContract: (contract: AssessmentContract) => void;
```

**Estimated effort:** 1 day
**Priority:** P0
**Dependencies:** None

---

### 1.3 Fix Narrative Column Storage

**Task 1.3.1:** Add missing columns to profiles table
```sql
-- File: supabase/migrations/021_narrative_columns.sql

-- These columns are referenced but don't exist
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_brand_statement TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_dna TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_first_principle TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_themes JSONB DEFAULT '[]';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_confidence FLOAT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_updated_at TIMESTAMPTZ;

-- Create agent_state_versions if not exists (already referenced in code)
CREATE TABLE IF NOT EXISTS agent_state_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  agent VARCHAR(50) NOT NULL,
  state JSONB NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  event_type VARCHAR(100),
  created_by VARCHAR(50) DEFAULT 'agent',
  rationale TEXT,
  event_payload JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_state_versions_profile_agent
  ON agent_state_versions(profile_id, agent);
```

**Estimated effort:** 0.5 days
**Priority:** P0
**Dependencies:** None

---

## Phase 2: Agent Enhancements (Week 2-3)

### 2.1 Complete Awards Database Population

**Task 2.1.1:** Create awards seed data
```python
# File: agents/seeds/awards_data.py

AWARDS_DATABASE = [
    # National STEM Awards
    {
        "id": "ncwit-aic",
        "name": "NCWIT Award for Aspirations in Computing",
        "category": "STEM",
        "level": "national",
        "organization": "National Center for Women & IT",
        "historical_win_rate": 0.10,
        "prestige_score": 8,
        "effort_hours": 15,
        "considers_diversity": True,
        "deadline_month": 11,
        "eligibility": {"grades": [9, 10, 11, 12], "gender": "female"}
    },
    {
        "id": "regeneron-sts",
        "name": "Regeneron Science Talent Search",
        "category": "STEM",
        "level": "national",
        "organization": "Society for Science",
        "historical_win_rate": 0.02,
        "prestige_score": 10,
        "effort_hours": 200,
        "considers_diversity": False,
        "deadline_month": 11,
        "eligibility": {"grades": [12]}
    },
    # ... 200+ more awards
]
```

**Task 2.1.2:** Create seed script
```python
# File: agents/scripts/seed_awards.py
async def seed_awards():
    from seeds.awards_data import AWARDS_DATABASE
    from tools.database import get_supabase_client

    db = get_supabase_client()
    for award in AWARDS_DATABASE:
        db.table("awards").upsert(award, on_conflict="id").execute()
```

**Estimated effort:** 2 days
**Priority:** P1
**Dependencies:** None

---

### 2.2 Complete Opportunities Database Population

**Task 2.2.1:** Create opportunities seed data
```python
# File: agents/seeds/opportunities_data.py

OPPORTUNITIES_DATABASE = [
    # Elite Research Programs
    {
        "id": "rsi",
        "name": "Research Science Institute",
        "type": "research",
        "organization": "MIT/CEE",
        "focus_area": "STEM",
        "prestige_score": 10,
        "acceptance_rate": 0.03,
        "selectivity": "highly_selective",
        "duration": "6 weeks",
        "cost": "Free",
        "diversity_focus": True,
        "deadline_month": 1,
        "eligibility": {"grades": [11]}
    },
    # ... 500+ more opportunities
]
```

**Estimated effort:** 2 days
**Priority:** P1
**Dependencies:** None

---

### 2.3 Micro-Edit Mastery Implementation

**Task 2.3.1:** Create micro-edit patterns tool
```python
# File: agents/tools/micro_edits.py

MICRO_EDIT_PATTERNS = {
    # Limiting → Empowering language
    "can't afford": "family investment priorities",
    "failed": "learned from the experience",
    "rejected": "redirected toward",
    "struggle with": "am developing in",
    "weakness": "growth area",
    "average": "solid foundation in",
    "only": "focused on",
    "just": "",  # Remove minimizing language
    "but": "and",  # Transform contrast to addition

    # Passive → Active voice
    "was given": "earned",
    "was selected": "secured a position",
    "was taught": "learned",

    # Generic → Specific (patterns)
    "helped many people": "served [X] community members",
    "did research": "investigated [topic]",
    "worked hard": "dedicated [X] hours weekly",
}

def apply_micro_edits(text: str) -> dict:
    """
    Apply micro-edit patterns to transform limiting language.

    Returns:
        {
            "original": str,
            "edited": str,
            "changes": [{"from": str, "to": str, "reason": str}],
            "improvement_score": float
        }
    """
    edited = text
    changes = []

    for pattern, replacement in MICRO_EDIT_PATTERNS.items():
        if pattern.lower() in edited.lower():
            # Case-insensitive replacement
            import re
            edited = re.sub(
                re.escape(pattern),
                replacement,
                edited,
                flags=re.IGNORECASE
            )
            changes.append({
                "from": pattern,
                "to": replacement,
                "reason": "Transform limiting to empowering language"
            })

    improvement_score = len(changes) / max(len(text.split()), 1) * 10

    return {
        "original": text,
        "edited": edited,
        "changes": changes,
        "improvement_score": min(improvement_score, 1.0)
    }
```

**Task 2.3.2:** Add endpoint for micro-edits
```python
# Add to agents/main.py

@app.post("/agents/narrative/micro-edit")
async def apply_micro_edit(input: dict):
    """Apply micro-edit patterns to essay text."""
    from tools.micro_edits import apply_micro_edits
    text = input.get("text", "")
    return apply_micro_edits(text)
```

**Estimated effort:** 1 day
**Priority:** P2
**Dependencies:** None

---

## Phase 3: Proactive Workflows (Week 3-4)

### 3.1 Workflow Infrastructure

**Task 3.1.1:** Create workflow base class
```python
# File: agents/workflows/base.py

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio

from tools.database import get_supabase_client


class BaseWorkflow(ABC):
    """Base class for proactive workflows."""

    name: str
    schedule: str  # Cron expression or 'on_demand'

    def __init__(self):
        self.db = get_supabase_client()

    @abstractmethod
    async def should_run(self, profile_id: str) -> bool:
        """Check if workflow should run for this profile."""
        pass

    @abstractmethod
    async def execute(self, profile_id: str) -> Dict[str, Any]:
        """Execute the workflow."""
        pass

    async def get_state(self, profile_id: str) -> Dict:
        """Get workflow state for profile."""
        result = self.db.table("workflow_state").select("*").eq(
            "profile_id", profile_id
        ).eq("workflow_name", self.name).single().execute()
        return result.data if result.data else {}

    async def update_state(self, profile_id: str, state: Dict):
        """Update workflow state."""
        self.db.table("workflow_state").upsert({
            "profile_id": profile_id,
            "workflow_name": self.name,
            "last_run": datetime.now().isoformat(),
            "state": state,
            "run_count": state.get("run_count", 0) + 1,
            "updated_at": datetime.now().isoformat()
        }, on_conflict="profile_id,workflow_name").execute()

    async def send_notification(
        self,
        profile_id: str,
        title: str,
        message: str,
        notification_type: str = "info"
    ):
        """Send notification to student."""
        # Get profile notification preferences
        profile = self.db.table("profiles").select(
            "email, notification_preferences"
        ).eq("id", profile_id).single().execute()

        if not profile.data:
            return

        prefs = profile.data.get("notification_preferences", {})

        # Store notification in database
        self.db.table("notifications").insert({
            "profile_id": profile_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "read": False,
            "created_at": datetime.now().isoformat()
        }).execute()

        # TODO: Send email if prefs.get("email")
        # TODO: Send push if prefs.get("push")
```

**Estimated effort:** 1 day
**Priority:** P1
**Dependencies:** Task 1.1.1

---

### 3.2 Silence Detector Workflow

**Task 3.2.1:** Create silence detector workflow
```python
# File: agents/workflows/silence_detector.py

from datetime import datetime, timedelta
from typing import Dict, Any
from .base import BaseWorkflow


class SilenceDetectorWorkflow(BaseWorkflow):
    """
    Detect when students go silent and intervene proactively.

    Thresholds:
    - 3 days: Gentle nudge
    - 7 days: Concerned check-in
    - 14 days: Coach escalation
    """

    name = "silence_detector"
    schedule = "0 9 * * *"  # Daily at 9am

    THRESHOLDS = {
        "nudge": 3,
        "concern": 7,
        "escalate": 14
    }

    async def should_run(self, profile_id: str) -> bool:
        """Run if student has been inactive."""
        profile = self.db.table("profiles").select(
            "last_activity_at"
        ).eq("id", profile_id).single().execute()

        if not profile.data:
            return False

        last_activity = profile.data.get("last_activity_at")
        if not last_activity:
            return True

        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(
                last_activity.replace("Z", "+00:00")
            )

        days_silent = (datetime.now(last_activity.tzinfo) - last_activity).days
        return days_silent >= self.THRESHOLDS["nudge"]

    async def execute(self, profile_id: str) -> Dict[str, Any]:
        """Execute silence detection and intervention."""
        profile = self.db.table("profiles").select(
            "first_name, last_activity_at"
        ).eq("id", profile_id).single().execute()

        if not profile.data:
            return {"success": False, "error": "Profile not found"}

        first_name = profile.data.get("first_name", "there")
        last_activity = profile.data.get("last_activity_at")

        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(
                last_activity.replace("Z", "+00:00")
            )

        days_silent = (datetime.now(last_activity.tzinfo) - last_activity).days

        # Determine intervention level
        if days_silent >= self.THRESHOLDS["escalate"]:
            level = "escalate"
            title = f"We miss you, {first_name}!"
            message = (
                f"It's been {days_silent} days since we last connected. "
                "Your college journey doesn't pause, and neither should we. "
                "What's one small thing you could do today to move forward?"
            )
            # Also notify coach
            await self._escalate_to_coach(profile_id, days_silent)

        elif days_silent >= self.THRESHOLDS["concern"]:
            level = "concern"
            title = f"Checking in, {first_name}"
            message = (
                f"It's been about a week since we connected. "
                "Small steps daily beat big bursts weekly. "
                "What's blocking you right now?"
            )

        else:
            level = "nudge"
            title = f"Quick check-in, {first_name}"
            message = (
                "Just a gentle reminder that consistent progress wins. "
                "Got 10 minutes today? That's enough to move forward."
            )

        # Send notification
        await self.send_notification(
            profile_id,
            title,
            message,
            notification_type="silence_alert"
        )

        # Update workflow state
        await self.update_state(profile_id, {
            "last_intervention": datetime.now().isoformat(),
            "intervention_level": level,
            "days_silent": days_silent
        })

        return {
            "success": True,
            "level": level,
            "days_silent": days_silent,
            "message_sent": True
        }

    async def _escalate_to_coach(self, profile_id: str, days_silent: int):
        """Escalate to coach for intervention."""
        # Create coach notification/task
        self.db.table("coach_tasks").insert({
            "profile_id": profile_id,
            "task_type": "silence_intervention",
            "priority": "high",
            "description": f"Student silent for {days_silent} days",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }).execute()
```

**Estimated effort:** 1 day
**Priority:** P1
**Dependencies:** Task 3.1.1

---

### 3.3 Deadline Alert Workflow

**Task 3.3.1:** Create deadline alert workflow
```python
# File: agents/workflows/deadline_alerts.py

from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base import BaseWorkflow


class DeadlineAlertWorkflow(BaseWorkflow):
    """
    Send proactive alerts for upcoming deadlines.

    Alert windows:
    - 30 days: Start preparation
    - 7 days: Final push
    - 3 days: Urgent reminder
    """

    name = "deadline_alerts"
    schedule = "0 8 * * *"  # Daily at 8am

    ALERT_WINDOWS = [30, 7, 3]

    async def should_run(self, profile_id: str) -> bool:
        """Always run - will check for relevant deadlines."""
        return True

    async def execute(self, profile_id: str) -> Dict[str, Any]:
        """Check for upcoming deadlines and send alerts."""
        # Get student's target opportunities and awards
        opportunities = await self._get_tracked_opportunities(profile_id)
        awards = await self._get_tracked_awards(profile_id)

        all_deadlines = opportunities + awards
        alerts_sent = []

        now = datetime.now()

        for item in all_deadlines:
            deadline = item.get("deadline")
            if not deadline:
                continue

            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))

            days_until = (deadline - now).days

            # Check if we should alert
            for window in self.ALERT_WINDOWS:
                if days_until == window:
                    alert = await self._send_deadline_alert(
                        profile_id, item, days_until
                    )
                    alerts_sent.append(alert)
                    break

        # Update state
        await self.update_state(profile_id, {
            "last_check": now.isoformat(),
            "alerts_sent": len(alerts_sent)
        })

        return {
            "success": True,
            "alerts_sent": alerts_sent,
            "total_tracked": len(all_deadlines)
        }

    async def _send_deadline_alert(
        self,
        profile_id: str,
        item: Dict,
        days_until: int
    ) -> Dict:
        """Send alert for specific deadline."""
        item_name = item.get("name", "Unknown")
        item_type = item.get("type", "opportunity")

        if days_until == 30:
            title = f"30 days until {item_name} deadline"
            message = (
                f"Start preparing now! You have one month until the "
                f"{item_name} deadline. Begin gathering materials and "
                "drafting your application."
            )
            urgency = "low"
        elif days_until == 7:
            title = f"One week until {item_name}!"
            message = (
                f"Final push time! The {item_name} deadline is in 7 days. "
                "Time to finalize your application and get feedback."
            )
            urgency = "medium"
        else:  # 3 days
            title = f"URGENT: {item_name} due in 3 days"
            message = (
                f"Don't miss this! {item_name} is due in just 3 days. "
                "Submit early to avoid last-minute issues."
            )
            urgency = "high"

        await self.send_notification(
            profile_id,
            title,
            message,
            notification_type=f"deadline_{urgency}"
        )

        return {
            "item": item_name,
            "days_until": days_until,
            "urgency": urgency
        }

    async def _get_tracked_opportunities(self, profile_id: str) -> List[Dict]:
        """Get opportunities student is tracking."""
        result = self.db.table("student_opportunities").select(
            "*, opportunities(*)"
        ).eq("profile_id", profile_id).eq("status", "tracking").execute()

        return [
            {**r.get("opportunities", {}), "type": "opportunity"}
            for r in (result.data or [])
        ]

    async def _get_tracked_awards(self, profile_id: str) -> List[Dict]:
        """Get awards student is tracking."""
        result = self.db.table("student_awards").select(
            "*, awards(*)"
        ).eq("profile_id", profile_id).eq("status", "tracking").execute()

        return [
            {**r.get("awards", {}), "type": "award"}
            for r in (result.data or [])
        ]
```

**Estimated effort:** 1 day
**Priority:** P1
**Dependencies:** Task 3.1.1

---

### 3.4 Workflow Runner

**Task 3.4.1:** Create workflow runner/scheduler
```python
# File: agents/workflows/runner.py

import asyncio
from datetime import datetime
from typing import List
import structlog

from .silence_detector import SilenceDetectorWorkflow
from .deadline_alerts import DeadlineAlertWorkflow
from tools.database import get_supabase_client

logger = structlog.get_logger()

WORKFLOWS = [
    SilenceDetectorWorkflow(),
    DeadlineAlertWorkflow(),
]


async def run_workflows_for_profile(profile_id: str):
    """Run all applicable workflows for a single profile."""
    results = {}

    for workflow in WORKFLOWS:
        try:
            if await workflow.should_run(profile_id):
                result = await workflow.execute(profile_id)
                results[workflow.name] = result
                logger.info(
                    "workflow_executed",
                    workflow=workflow.name,
                    profile_id=profile_id,
                    result=result
                )
        except Exception as e:
            logger.error(
                "workflow_error",
                workflow=workflow.name,
                profile_id=profile_id,
                error=str(e)
            )
            results[workflow.name] = {"success": False, "error": str(e)}

    return results


async def run_all_workflows():
    """Run workflows for all active profiles."""
    db = get_supabase_client()

    # Get all active profiles
    profiles = db.table("profiles").select("id").eq(
        "is_active", True
    ).execute()

    if not profiles.data:
        logger.info("no_active_profiles")
        return

    logger.info("running_workflows", profile_count=len(profiles.data))

    for profile in profiles.data:
        await run_workflows_for_profile(profile["id"])
        await asyncio.sleep(0.1)  # Rate limiting


# Add endpoint to main.py
# @app.post("/agents/workflows/run")
# async def trigger_workflows(profile_id: str = None):
#     if profile_id:
#         return await run_workflows_for_profile(profile_id)
#     else:
#         await run_all_workflows()
#         return {"success": True, "message": "All workflows triggered"}
```

**Estimated effort:** 0.5 days
**Priority:** P1
**Dependencies:** Tasks 3.2.1, 3.3.1

---

## Phase 4: Evaluation Framework (Week 4-5)

### 4.1 Golden Dataset Creation

**Task 4.1.1:** Create golden dataset structure
```python
# File: agents/evaluation/golden_dataset.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import json


@dataclass
class GoldenExample:
    """Single golden example for evaluation."""

    profile_id: str
    input_profile: Dict                    # Full profile data
    expected_brand_statement: str          # Jenny's output
    expected_themes: List[str]             # Jenny's themes
    expected_first_principle: str          # Jenny's first principle
    expected_activities: List[Dict]        # Top 5 recommended activities
    expected_awards: List[str]             # Top 5 award recommendations
    quality_annotations: Dict              # Human quality ratings
    difficulty_tier: str                   # 'easy', 'medium', 'hard'
    notes: Optional[str] = None


# Initial golden dataset (from Jenny Duan's coaching)
GOLDEN_DATASET = [
    GoldenExample(
        profile_id="huda-golden-1",
        input_profile={
            "identity": {
                "first_name": "Huda",
                "grade": 10,
            },
            "operating": {
                "gender": "FEMALE",
                "culturalBackground": ["SOUTH_ASIAN"],
                "religion": "Muslim",
                "firstGeneration": True,
            },
            "aptitude": {
                "gpa_weighted": 3.9,
                "sat_total": 1570,
                "ap_count": 8,
            },
            "passion": {
                "spike_category": "STEM",
                "leadership_level": "FOUNDER_LOCAL",
                "brag_text": "Building apps to help underrepresented girls learn coding",
            },
            "community": {
                "service_hours": 350,
            }
        },
        expected_brand_statement=(
            "A South Asian Muslim innovator empowering girls through code, "
            "building pathways to STEM equity in her community and beyond."
        ),
        expected_themes=[
            "STEM Equity",
            "Community Empowerment",
            "Cultural Bridge-Building",
            "First-Generation Success",
            "Impact through Innovation"
        ],
        expected_first_principle=(
            "To dismantle barriers and create equitable access to STEM education "
            "for underrepresented girls, empowering them to become innovators."
        ),
        expected_activities=[
            {"name": "Girls Who Code Chapter", "type": "club", "touchpoints": 5},
            {"name": "CS Education Research", "type": "research", "touchpoints": 6},
            {"name": "Community Coding Workshops", "type": "service", "touchpoints": 4},
        ],
        expected_awards=[
            "NCWIT Award for Aspirations in Computing",
            "Google Code-in",
            "Congressional App Challenge",
        ],
        quality_annotations={
            "brand_statement_quality": 5,
            "theme_coherence": 5,
            "activity_alignment": 5,
            "award_fit": 4,
        },
        difficulty_tier="medium",
        notes="Strong profile with clear spike. Tests identity synthesis."
    ),
    # Add 19+ more golden examples...
]


def load_golden_dataset() -> List[GoldenExample]:
    """Load golden dataset from file or database."""
    return GOLDEN_DATASET


def save_golden_to_db(examples: List[GoldenExample], db):
    """Save golden examples to database."""
    for ex in examples:
        db.table("evaluation_golden").upsert({
            "profile_id": ex.profile_id,
            "input_profile": ex.input_profile,
            "expected_outputs": {
                "brand_statement": ex.expected_brand_statement,
                "themes": ex.expected_themes,
                "first_principle": ex.expected_first_principle,
                "activities": ex.expected_activities,
                "awards": ex.expected_awards,
            },
            "jenny_annotations": ex.quality_annotations,
            "difficulty_tier": ex.difficulty_tier,
        }, on_conflict="profile_id").execute()
```

**Estimated effort:** 3 days (including data collection)
**Priority:** P1
**Dependencies:** Task 1.1.1

---

### 4.2 LLM-as-Judge Implementation

**Task 4.2.1:** Create evaluation judges
```python
# File: agents/evaluation/llm_judge.py

from typing import Dict, Any
import json

# Try Gemini first, fallback to OpenAI
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    import os
    GOOGLE_API_KEY = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    USE_GEMINI = bool(GOOGLE_API_KEY)
except ImportError:
    USE_GEMINI = False


BRAND_STATEMENT_RUBRIC = """
You are an expert college admissions counselor evaluating a brand statement.

## Scoring Rubric (1-5):

1 (Poor): Generic statement that could apply to anyone. No unique identity.
2 (Below Average): Some personalization but missing key identity markers or spike.
3 (Average): Decent personalization, captures spike but lacks memorability.
4 (Good): Strong identity synthesis, memorable, threads identity through spike.
5 (Excellent): Instantly memorable, unique positioning, perfect narrative threading.

## Student Profile:
{profile_json}

## Brand Statement to Evaluate:
"{brand_statement}"

## Expected Brand Statement (Reference):
"{expected_brand_statement}"

## Your Evaluation:

Score (1-5):
Rationale (2-3 sentences):
Improvement Suggestions:
"""


class LLMJudge:
    """LLM-based evaluation judge."""

    def __init__(self):
        if USE_GEMINI:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.1
            )
        else:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    async def evaluate_brand_statement(
        self,
        profile: Dict,
        actual_brand_statement: str,
        expected_brand_statement: str
    ) -> Dict[str, Any]:
        """Evaluate brand statement quality."""
        prompt = BRAND_STATEMENT_RUBRIC.format(
            profile_json=json.dumps(profile, indent=2),
            brand_statement=actual_brand_statement,
            expected_brand_statement=expected_brand_statement
        )

        response = await self.llm.ainvoke(prompt)

        # Parse response
        content = response.content

        # Extract score (simple parsing)
        score = 3  # Default
        for line in content.split('\n'):
            if 'score' in line.lower() and ':' in line:
                try:
                    score = int(line.split(':')[1].strip()[0])
                except:
                    pass

        return {
            "score": score,
            "max_score": 5,
            "evaluation": content,
            "passed": score >= 4
        }

    async def evaluate_theme_coherence(
        self,
        profile: Dict,
        actual_themes: list,
        expected_themes: list
    ) -> Dict[str, Any]:
        """Evaluate theme coherence and coverage."""
        # Calculate overlap
        actual_set = set(t.lower() for t in actual_themes)
        expected_set = set(t.lower() for t in expected_themes)

        overlap = len(actual_set & expected_set)
        coverage = overlap / len(expected_set) if expected_set else 0

        return {
            "score": min(5, int(coverage * 5) + 1),
            "max_score": 5,
            "overlap_count": overlap,
            "coverage": coverage,
            "passed": coverage >= 0.6
        }


async def run_evaluation(
    golden_example: Dict,
    actual_outputs: Dict
) -> Dict[str, Any]:
    """Run full evaluation on a golden example."""
    judge = LLMJudge()

    results = {
        "golden_id": golden_example.get("profile_id"),
        "timestamp": datetime.now().isoformat(),
        "scores": {}
    }

    # Evaluate brand statement
    brand_eval = await judge.evaluate_brand_statement(
        golden_example.get("input_profile", {}),
        actual_outputs.get("brand_statement", ""),
        golden_example.get("expected_outputs", {}).get("brand_statement", "")
    )
    results["scores"]["brand_statement"] = brand_eval

    # Evaluate themes
    theme_eval = await judge.evaluate_theme_coherence(
        golden_example.get("input_profile", {}),
        actual_outputs.get("themes", []),
        golden_example.get("expected_outputs", {}).get("themes", [])
    )
    results["scores"]["themes"] = theme_eval

    # Calculate overall score
    scores = [v.get("score", 0) for v in results["scores"].values()]
    results["overall_score"] = sum(scores) / len(scores) if scores else 0
    results["passed"] = all(v.get("passed", False) for v in results["scores"].values())

    return results
```

**Estimated effort:** 2 days
**Priority:** P1
**Dependencies:** Task 4.1.1

---

### 4.3 Evaluation Pipeline

**Task 4.3.1:** Create evaluation runner
```python
# File: agents/evaluation/runner.py

import asyncio
from datetime import datetime
from typing import List, Dict
import structlog

from .golden_dataset import load_golden_dataset, GoldenExample
from .llm_judge import run_evaluation
from agents.narrative_synthesis import NarrativeSynthesisAgent
from tools.database import get_supabase_client

logger = structlog.get_logger()


async def evaluate_agent(
    agent_version: str,
    golden_examples: List[GoldenExample] = None
) -> Dict:
    """
    Run full evaluation of NarrativeSynthesisAgent against golden dataset.

    Returns:
        {
            "agent_version": str,
            "total_examples": int,
            "passed": int,
            "failed": int,
            "average_score": float,
            "results": [...],
            "summary": str
        }
    """
    db = get_supabase_client()
    agent = NarrativeSynthesisAgent()

    if golden_examples is None:
        golden_examples = load_golden_dataset()

    run_id = f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    results = []

    logger.info(
        "evaluation_started",
        run_id=run_id,
        agent_version=agent_version,
        example_count=len(golden_examples)
    )

    for example in golden_examples:
        try:
            # Create assessment contract from golden input
            assessment_contract = {
                "profile_data": example.input_profile,
                "scores": {"aptitude": 80, "passion": 90, "community": 70, "narrative": 50}
            }

            # Run agent
            start_time = datetime.now()
            actual_output = await agent.synthesize(
                example.profile_id,
                assessment_contract
            )
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Run evaluation
            eval_result = await run_evaluation(
                {
                    "profile_id": example.profile_id,
                    "input_profile": example.input_profile,
                    "expected_outputs": {
                        "brand_statement": example.expected_brand_statement,
                        "themes": example.expected_themes,
                    }
                },
                {
                    "brand_statement": actual_output.get("brand_statement", ""),
                    "themes": actual_output.get("themes", []),
                }
            )

            eval_result["duration_ms"] = duration_ms
            results.append(eval_result)

            # Store in database
            db.table("evaluation_runs").insert({
                "run_id": run_id,
                "agent_version": agent_version,
                "golden_id": example.profile_id,
                "actual_outputs": actual_output,
                "objective_scores": {},
                "llm_judge_scores": eval_result["scores"],
                "overall_score": eval_result["overall_score"],
                "passed": eval_result["passed"],
                "duration_ms": int(duration_ms)
            }).execute()

            logger.info(
                "example_evaluated",
                golden_id=example.profile_id,
                passed=eval_result["passed"],
                score=eval_result["overall_score"]
            )

        except Exception as e:
            logger.error(
                "evaluation_error",
                golden_id=example.profile_id,
                error=str(e)
            )
            results.append({
                "golden_id": example.profile_id,
                "error": str(e),
                "passed": False
            })

    # Calculate summary
    passed = sum(1 for r in results if r.get("passed", False))
    scores = [r.get("overall_score", 0) for r in results if "overall_score" in r]
    avg_score = sum(scores) / len(scores) if scores else 0

    summary = {
        "run_id": run_id,
        "agent_version": agent_version,
        "total_examples": len(golden_examples),
        "passed": passed,
        "failed": len(golden_examples) - passed,
        "pass_rate": passed / len(golden_examples) if golden_examples else 0,
        "average_score": avg_score,
        "results": results,
    }

    logger.info(
        "evaluation_completed",
        run_id=run_id,
        pass_rate=summary["pass_rate"],
        average_score=avg_score
    )

    return summary


# Add endpoint to main.py
# @app.post("/agents/evaluation/run")
# async def run_agent_evaluation(agent_version: str = "v10.0"):
#     return await evaluate_agent(agent_version)
```

**Estimated effort:** 1 day
**Priority:** P1
**Dependencies:** Tasks 4.1.1, 4.2.1

---

## Phase 5: Integration & Testing (Week 5-6)

### 5.1 API Endpoint Updates

**Task 5.1.1:** Add new endpoints to main.py
```python
# Add to agents/main.py

# Workflow endpoints
@app.post("/agents/workflows/run")
async def trigger_workflows(profile_id: str = None):
    """Manually trigger workflows."""
    from workflows.runner import run_workflows_for_profile, run_all_workflows

    if profile_id:
        return await run_workflows_for_profile(profile_id)
    else:
        await run_all_workflows()
        return {"success": True, "message": "All workflows triggered"}


@app.get("/agents/workflows/status/{profile_id}")
async def get_workflow_status(profile_id: str):
    """Get workflow status for a profile."""
    result = db.table("workflow_state").select("*").eq(
        "profile_id", profile_id
    ).execute()
    return {"workflows": result.data or []}


# Evaluation endpoints
@app.post("/agents/evaluation/run")
async def run_evaluation_suite(agent_version: str = "v10.0"):
    """Run full evaluation suite."""
    from evaluation.runner import evaluate_agent
    return await evaluate_agent(agent_version)


@app.get("/agents/evaluation/results/{run_id}")
async def get_evaluation_results(run_id: str):
    """Get results for a specific evaluation run."""
    result = db.table("evaluation_runs").select("*").eq(
        "run_id", run_id
    ).execute()
    return {"results": result.data or []}


# Micro-edit endpoint
@app.post("/agents/narrative/micro-edit")
async def apply_micro_edits(input: Dict):
    """Apply micro-edit patterns to text."""
    from tools.micro_edits import apply_micro_edits
    text = input.get("text", "")
    return apply_micro_edits(text)
```

**Estimated effort:** 0.5 days
**Priority:** P0
**Dependencies:** All previous phases

---

### 5.2 Next.js API Route Updates

**Task 5.2.1:** Add frontend proxy routes
```typescript
// File: app/api/agents/workflows/run/route.ts

import { NextResponse } from 'next/server';

const AGENT_API_URL = process.env.AGENT_SERVICE_URL || 'http://localhost:8001';

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const response = await fetch(`${AGENT_API_URL}/agents/workflows/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Workflow trigger failed' },
      { status: 500 }
    );
  }
}
```

**Estimated effort:** 1 day
**Priority:** P1
**Dependencies:** Task 5.1.1

---

### 5.3 End-to-End Testing

**Task 5.3.1:** Create integration test suite
```python
# File: agents/tests/test_e2e.py

import pytest
import asyncio
from agents.narrative_synthesis import NarrativeSynthesisAgent
from agents.assessment import AssessmentAgent
from evaluation.runner import evaluate_agent


@pytest.fixture
def test_profile():
    return {
        "profile_id": "test-huda-001",
        "assessment_contract": {
            "profile_data": {
                "operating": {
                    "gender": "FEMALE",
                    "culturalBackground": ["SOUTH_ASIAN"],
                    "religion": "Muslim",
                    "firstGeneration": True,
                },
                "aptitude": {
                    "gpa_weighted": 3.9,
                    "sat_total": 1570,
                    "ap_count": 8,
                },
                "passion": {
                    "spike_category": "STEM",
                    "leadership_level": "FOUNDER_LOCAL",
                    "brag_text": "Building apps to help underrepresented girls learn coding",
                },
                "community": {
                    "service_hours": 350,
                }
            },
            "scores": {
                "aptitude": 82,
                "passion": 97,
                "community": 59,
                "narrative": 50
            }
        }
    }


@pytest.mark.asyncio
async def test_narrative_synthesis(test_profile):
    """Test narrative synthesis generates valid output."""
    agent = NarrativeSynthesisAgent()

    result = await agent.synthesize(
        test_profile["profile_id"],
        test_profile["assessment_contract"]
    )

    assert result["success"] == True
    assert len(result["brand_statement"]) >= 50
    assert len(result["brand_statement"]) <= 200
    assert len(result["themes"]) >= 3
    assert result["confidence"] >= 0.7


@pytest.mark.asyncio
async def test_evaluation_pipeline():
    """Test evaluation pipeline runs successfully."""
    result = await evaluate_agent("test-v10.0")

    assert result["total_examples"] > 0
    assert result["pass_rate"] >= 0.8  # 80% pass rate required


@pytest.mark.asyncio
async def test_workflow_execution(test_profile):
    """Test workflow execution."""
    from workflows.runner import run_workflows_for_profile

    result = await run_workflows_for_profile(test_profile["profile_id"])

    # Should not error even if no actions taken
    assert isinstance(result, dict)
```

**Estimated effort:** 2 days
**Priority:** P0
**Dependencies:** All previous phases

---

## Summary: Complete Task List

### Week 1: Foundation
- [ ] 1.1.1 Create evaluation tables (0.5 days)
- [ ] 1.2.1 Update TypeScript types (0.5 days)
- [ ] 1.2.2 Update results store (0.5 days)
- [ ] 1.3.1 Add narrative columns (0.5 days)

### Week 2-3: Agent Enhancements
- [ ] 2.1.1 Create awards seed data (1 day)
- [ ] 2.1.2 Create seed script (0.5 days)
- [ ] 2.2.1 Create opportunities seed data (1 day)
- [ ] 2.3.1 Create micro-edit patterns tool (0.5 days)
- [ ] 2.3.2 Add micro-edit endpoint (0.5 days)

### Week 3-4: Proactive Workflows
- [ ] 3.1.1 Create workflow base class (1 day)
- [ ] 3.2.1 Create silence detector workflow (1 day)
- [ ] 3.3.1 Create deadline alert workflow (1 day)
- [ ] 3.4.1 Create workflow runner (0.5 days)

### Week 4-5: Evaluation Framework
- [ ] 4.1.1 Create golden dataset structure (1 day)
- [ ] 4.1.2 Populate golden dataset (2 days)
- [ ] 4.2.1 Create LLM-as-Judge (2 days)
- [ ] 4.3.1 Create evaluation runner (1 day)

### Week 5-6: Integration & Testing
- [ ] 5.1.1 Add new endpoints to main.py (0.5 days)
- [ ] 5.2.1 Add frontend proxy routes (1 day)
- [ ] 5.3.1 Create integration test suite (2 days)

**Total Estimated Effort:** 18.5 developer-days (~4 weeks)

---

## Approval Required

Please review and approve:

1. **Scope:** Is this the right set of features for the next phase?
2. **Priority:** Should any tasks be reordered?
3. **Framework Decision:** Option A, B, or C for Agno migration?
4. **Timeline:** 4-week delivery acceptable?

Once approved, implementation will begin with Phase 1 tasks.
