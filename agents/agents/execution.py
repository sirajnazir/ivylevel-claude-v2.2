"""
IvyQuest v10.0 Execution Agent (P0 CRITICAL)
============================================
Bridges the strategy-execution gap. Prevents 80% user abandonment.

Primitives:
- ACP-003: Crisis Alchemy Protocol (via LangGraph)
- ACP-004: Strategic Overwhelm (1.4x capacity, 73% completion target)
- ACP-007: Talk-First-Write-Second

Autonomy: MEDIUM for most actions, LOW for crises (HITL required)

Huda Benchmarks:
- Project Completion: >80% (Huda: 100%)
- Crisis Recovery: <72 hours (Huda: <2 hours)
- Task Completion: >70% (Huda: 73%)
- EDS: <50 (Huda: 12)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from .base import BaseAgent
from config import settings, AutonomyLevel
from tools.database import (
    supabase,
    get_profile,
    update_profile,
    get_projects,
    create_project,
    get_project_steps,
    create_project_steps,
    create_crisis,
    get_crisis,
    update_crisis,
)
from tools.cri import compute_eds
from graphs.crisis_alchemy import CrisisAlchemyGraph

import structlog

logger = structlog.get_logger()


class ExecutionAgent(BaseAgent):
    """
    Execution Agent: Bridges strategy-execution gap.

    Key Responsibilities:
    1. Project Scaffolding - Break projects into 20+ microsteps
    2. Crisis Alchemy - Transform crises into opportunities (LangGraph)
    3. Blocker Detection - Monitor for >5 days inactivity
    4. EDS Tracking - Compute Execution Debt Score weekly
    5. Talk-First-Write-Second - Voice-to-text essay support
    """

    def __init__(self):
        super().__init__(
            name="Execution",
            autonomy_level=AutonomyLevel.MEDIUM
        )
        self.crisis_graph = CrisisAlchemyGraph()
        self.blocker_threshold_days = settings.blocker_threshold_days

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Main processing entry point.

        Args:
            profile_id: Profile UUID
            **kwargs: Action-specific parameters

        Returns:
            Processing results
        """
        action = kwargs.get("action", "check_status")

        if action == "scaffold_project":
            return await self.scaffold_project(profile_id, kwargs.get("project_data", {}))
        elif action == "handle_crisis":
            return await self.handle_crisis(
                profile_id,
                kwargs.get("crisis_type", "blocker"),
                kwargs.get("description", ""),
                kwargs.get("urgency", 3)
            )
        elif action == "detect_blockers":
            return await self.detect_blockers(profile_id)
        elif action == "compute_eds":
            eds = await self.compute_eds(profile_id)
            return {"success": True, "eds": eds}
        else:
            return await self.check_status(profile_id)

    # =========================================
    # Project Scaffolding (ACP-004)
    # =========================================

    async def scaffold_project(
        self,
        profile_id: str,
        project_data: Dict
    ) -> Dict[str, Any]:
        """
        Break a project into microsteps with Strategic Overwhelm.

        ACP-004: Assign 1.4x tasks → expect 73% completion.
        This is BETTER than assigning fewer tasks.

        Args:
            profile_id: Profile UUID
            project_data: Project definition with name, type, description

        Returns:
            Created project with microsteps
        """
        self._log_start("scaffold_project", profile_id=profile_id)

        profile = await self._get_profile(profile_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        # Generate base steps (would use LLM in production)
        base_steps = self._generate_base_steps(project_data)

        # Apply Strategic Overwhelm (1.4x inflation)
        overwhelm_steps = self._apply_strategic_overwhelm(base_steps)

        # Create project record
        project = {
            "profile_id": profile_id,
            "name": project_data.get("name", "Untitled Project"),
            "description": project_data.get("description"),
            "type": project_data.get("type", "extracurricular"),
            "status": "planning",
            "scaffolded_by": "agent",
            "base_step_count": len(base_steps),
            "overwhelm_step_count": len(overwhelm_steps),
            "overwhelm_factor": settings.overwhelm_factor,
            "total_steps": len(overwhelm_steps),
            "touchpoints": project_data.get("touchpoints", []),
            "touchpoint_count": len(project_data.get("touchpoints", [])),
            "narrative_connection": project_data.get("narrative_connection"),
        }

        created_project = await create_project(project)
        if not created_project:
            return {"success": False, "error": "Failed to create project"}

        # Create step records
        step_records = []
        for i, step in enumerate(overwhelm_steps):
            step_records.append({
                "project_id": created_project["id"],
                "title": step["title"],
                "description": step.get("description"),
                "step_order": i + 1,
                "status": "pending",
                "target_date": step.get("target_date"),
                "difficulty": step.get("difficulty", 1.0),
                "estimated_hours": step.get("estimated_hours"),
                "is_stretch_goal": step.get("is_stretch", False),
                "is_milestone": step.get("is_milestone", False),
            })

        await create_project_steps(step_records)

        # Version state
        await self._version_state(
            profile_id,
            "project_scaffolded",
            {
                "project_id": created_project["id"],
                "project_name": project["name"],
                "base_steps": len(base_steps),
                "total_steps": len(overwhelm_steps),
                "overwhelm_factor": settings.overwhelm_factor,
            }
        )

        # Publish event
        await self._publish_event("GAMEPLAN_GENERATED", {
            "profileId": profile_id,
            "activities": [created_project],
            "seeds": []
        })

        self._log_complete("scaffold_project", profile_id=profile_id, project_id=created_project["id"])

        return {
            "success": True,
            "project": created_project,
            "microsteps": len(overwhelm_steps),
            "base_steps": len(base_steps),
            "overwhelm_factor": settings.overwhelm_factor,
            "expected_completion_rate": settings.target_completion_rate
        }

    def _generate_base_steps(self, project_data: Dict) -> List[Dict]:
        """
        Generate base microsteps for a project.

        In production, this would use GPT-4o to generate contextual steps.
        For now, generates template-based steps.
        """
        project_type = project_data.get("type", "extracurricular")

        # Template steps by project type
        templates = {
            "extracurricular": [
                {"title": "Define club/activity mission and goals", "difficulty": 0.5, "is_milestone": True},
                {"title": "Research similar organizations for inspiration", "difficulty": 0.3},
                {"title": "Draft constitution/bylaws", "difficulty": 0.8},
                {"title": "Recruit founding members (3-5 people)", "difficulty": 0.7},
                {"title": "Schedule first meeting", "difficulty": 0.3},
                {"title": "Create social media presence", "difficulty": 0.4},
                {"title": "Design logo and branding", "difficulty": 0.5},
                {"title": "Plan first event/workshop", "difficulty": 0.8, "is_milestone": True},
                {"title": "Execute first event", "difficulty": 1.0, "is_milestone": True},
                {"title": "Collect feedback and iterate", "difficulty": 0.4},
                {"title": "Document impact metrics", "difficulty": 0.5},
                {"title": "Plan membership growth strategy", "difficulty": 0.6},
            ],
            "research": [
                {"title": "Identify research question/hypothesis", "difficulty": 0.7, "is_milestone": True},
                {"title": "Literature review (10+ papers)", "difficulty": 1.0},
                {"title": "Design methodology", "difficulty": 0.8},
                {"title": "Set up research environment", "difficulty": 0.6},
                {"title": "Collect/generate data", "difficulty": 1.2, "is_milestone": True},
                {"title": "Analyze data", "difficulty": 1.0},
                {"title": "Draft results section", "difficulty": 0.8},
                {"title": "Write discussion and conclusion", "difficulty": 0.9},
                {"title": "Create visualizations", "difficulty": 0.5},
                {"title": "Write abstract", "difficulty": 0.4},
                {"title": "Get feedback from mentor", "difficulty": 0.3},
                {"title": "Revise based on feedback", "difficulty": 0.6},
                {"title": "Submit to competition/journal", "difficulty": 0.4, "is_milestone": True},
            ],
            "essay": [
                {"title": "Brainstorm essay topics (5-10 ideas)", "difficulty": 0.5},
                {"title": "Record voice memo about chosen topic", "difficulty": 0.3},
                {"title": "Transcribe and identify key themes", "difficulty": 0.4},
                {"title": "Create outline from themes", "difficulty": 0.5},
                {"title": "Write first draft (no editing)", "difficulty": 0.8, "is_milestone": True},
                {"title": "Let draft sit for 24 hours", "difficulty": 0.1},
                {"title": "Read aloud and note awkward parts", "difficulty": 0.4},
                {"title": "Revise for clarity and flow", "difficulty": 0.7},
                {"title": "Get feedback from trusted reader", "difficulty": 0.3},
                {"title": "Apply micro-edits (word choice)", "difficulty": 0.5},
                {"title": "Final proofread", "difficulty": 0.3},
                {"title": "Submit or save final version", "difficulty": 0.2, "is_milestone": True},
            ],
            "community": [
                {"title": "Identify community need", "difficulty": 0.5, "is_milestone": True},
                {"title": "Research existing solutions", "difficulty": 0.4},
                {"title": "Design service project", "difficulty": 0.7},
                {"title": "Create project timeline", "difficulty": 0.4},
                {"title": "Recruit volunteers", "difficulty": 0.6},
                {"title": "Secure resources/funding", "difficulty": 0.8},
                {"title": "Execute first service session", "difficulty": 1.0, "is_milestone": True},
                {"title": "Document with photos/video", "difficulty": 0.3},
                {"title": "Collect impact data", "difficulty": 0.5},
                {"title": "Write reflection", "difficulty": 0.4},
                {"title": "Plan sustainability/expansion", "difficulty": 0.6},
                {"title": "Create impact report", "difficulty": 0.5, "is_milestone": True},
            ],
        }

        base_steps = templates.get(project_type, templates["extracurricular"])

        # Add any custom steps from project data
        custom_steps = project_data.get("custom_steps", [])
        for step in custom_steps:
            base_steps.append({
                "title": step.get("title", "Custom step"),
                "description": step.get("description"),
                "difficulty": step.get("difficulty", 0.5),
            })

        return base_steps

    def _apply_strategic_overwhelm(self, base_steps: List[Dict]) -> List[Dict]:
        """
        Apply Strategic Overwhelm: inflate tasks by 1.4x.

        ACP-004: Assign 10 tasks → complete 7 is BETTER than
        assign 7 tasks → complete 5.

        Adds stretch goals and enhanced versions of base steps.
        """
        overwhelm_factor = settings.overwhelm_factor
        base_count = len(base_steps)
        target_count = int(base_count * overwhelm_factor)

        result = list(base_steps)

        # Add stretch goals to reach target
        stretch_index = 0
        while len(result) < target_count:
            # Create stretch versions of existing steps
            base_step = base_steps[stretch_index % base_count]
            stretch_step = {
                "title": f"Stretch: {base_step['title']} (enhanced)",
                "description": f"Optional enhancement: {base_step.get('description', '')}",
                "difficulty": base_step.get("difficulty", 0.5) * 0.5,  # Lower difficulty
                "is_stretch": True,
            }
            result.append(stretch_step)
            stretch_index += 1

        return result

    # =========================================
    # Crisis Alchemy (ACP-003) via LangGraph
    # =========================================

    async def handle_crisis(
        self,
        profile_id: str,
        crisis_type: str,
        description: str,
        urgency: int = 3
    ) -> Dict[str, Any]:
        """
        Execute Crisis Alchemy Protocol via LangGraph.

        CRITICAL: Uses LangGraph (NOT AutoGen) per v9.1 correction.

        4-Step Protocol:
        1. Validate (2s) - Acknowledge emotion immediately
        2. Act (10s) - One concrete micro-action
        3. Reframe (30s) - Find the opportunity angle
        4. Create (2min) - Design new activity/pivot

        Autonomy: LOW - Requires HITL approval within 1 hour.

        Args:
            profile_id: Profile UUID
            crisis_type: Type of crisis (blocker, rejection, etc.)
            description: Crisis description
            urgency: 1-5 urgency level

        Returns:
            Crisis record with proposed response
        """
        self._log_start("handle_crisis", profile_id=profile_id, crisis_type=crisis_type)

        # Create crisis record
        crisis_data = {
            "profile_id": profile_id,
            "type": crisis_type,
            "title": f"{crisis_type.capitalize()}: {description[:50]}...",
            "description": description,
            "urgency": self._map_urgency(urgency),
            "status": "detected",
            "detected_by": "agent",
            "requires_human_approval": True,
            "approval_deadline": self._get_hitl_deadline(),
        }

        crisis = await create_crisis(crisis_data)
        if not crisis:
            return {"success": False, "error": "Failed to create crisis record"}

        crisis_id = crisis["id"]

        # Run Crisis Alchemy via LangGraph (4-step protocol)
        try:
            alchemy_result = await self.crisis_graph.run({
                "crisis_id": crisis_id,
                "profile_id": profile_id,
                "type": crisis_type,
                "description": description,
                "urgency": urgency,
            })
        except Exception as e:
            self.logger.error("crisis_alchemy_failed", error=str(e))
            alchemy_result = self._generate_fallback_response(crisis_type, description)

        # Update crisis with proposed response
        await update_crisis(crisis_id, {
            "status": "proposed",
            "step1_validation": alchemy_result.get("step1_validation"),
            "step2_micro_action": alchemy_result.get("step2_micro_action"),
            "step3_reframe": alchemy_result.get("step3_reframe"),
            "step4_creation": alchemy_result.get("step4_creation"),
            "proposed_response": alchemy_result,
        })

        # Version state
        await self._version_state(
            profile_id,
            "crisis_detected",
            {
                "crisis_id": crisis_id,
                "type": crisis_type,
                "urgency": urgency,
                "proposed_response": alchemy_result,
            }
        )

        # Publish event
        await self._publish_event("CRISIS_DETECTED", {
            "profileId": profile_id,
            "crisisId": crisis_id,
            "severity": urgency,
            "type": crisis_type,
            "rationale": "Detected by Execution Agent"
        })

        self._log_complete("handle_crisis", profile_id=profile_id, crisis_id=crisis_id)

        # Return with HITL requirements
        return {
            "success": True,
            "crisis_id": crisis_id,
            "status": "awaiting_approval",
            "proposed_response": alchemy_result,
            "requires_human_approval": True,
            "approval_deadline": crisis_data["approval_deadline"],
            "message": "Crisis Alchemy complete. Awaiting coach approval."
        }

    def _map_urgency(self, numeric_urgency: int) -> str:
        """Map numeric urgency (1-5) to enum value."""
        mapping = {
            1: "low",
            2: "low",
            3: "medium",
            4: "high",
            5: "critical",
        }
        return mapping.get(numeric_urgency, "medium")

    def _generate_fallback_response(self, crisis_type: str, description: str) -> Dict:
        """Generate fallback response if LangGraph fails."""
        return {
            "step1_validation": {
                "message": "I hear you. This is a difficult situation, and it's okay to feel frustrated or overwhelmed.",
                "emotion_acknowledged": True,
            },
            "step2_micro_action": {
                "action": "Take 5 minutes to write down exactly what happened and how you feel about it.",
                "duration_minutes": 5,
            },
            "step3_reframe": {
                "opportunity_angle": "Every setback reveals a gap that can become your unique contribution.",
                "narrative_connection": "This experience will make your story more authentic.",
            },
            "step4_creation": {
                "activity_name": "Reflection and Pivot Planning",
                "description": "Document this experience and identify how it can inform your next step.",
                "first_step": "Schedule 30 minutes tomorrow to brainstorm alternative approaches.",
                "touchpoints": ["essay", "interview"],
            },
        }

    async def process_handoff(
        self,
        crisis_id: str,
        approved: bool,
        rationale: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process HITL approval/rejection for a crisis.

        Args:
            crisis_id: Crisis UUID
            approved: Whether the proposed response was approved
            rationale: Coach's rationale for decision

        Returns:
            Updated crisis status
        """
        crisis = await get_crisis(crisis_id)
        if not crisis:
            return {"success": False, "error": "Crisis not found"}

        profile_id = crisis["profile_id"]

        if approved:
            # Execute the approved response
            await update_crisis(crisis_id, {
                "status": "resolved",
                "approved_by": "coach",
                "approval_notes": rationale,
                "approval_timestamp": datetime.now().isoformat(),
                "reframed_opportunity": crisis.get("proposed_response", {}).get("step3_reframe", {}).get("opportunity_angle"),
            })

            # Version state with human override
            await self._version_state(
                profile_id,
                "crisis_resolved",
                {
                    "crisis_id": crisis_id,
                    "approved": True,
                    "rationale": rationale,
                    "resolution": crisis.get("proposed_response"),
                },
                created_by="human"
            )

            return {
                "success": True,
                "status": "resolved",
                "message": "Crisis response approved and executed."
            }
        else:
            # Escalate for manual handling
            await update_crisis(crisis_id, {
                "status": "escalated",
                "approval_notes": rationale,
            })

            await self._version_state(
                profile_id,
                "crisis_escalated",
                {"crisis_id": crisis_id, "rationale": rationale},
                created_by="human"
            )

            return {
                "success": True,
                "status": "escalated",
                "message": "Crisis escalated for manual intervention."
            }

    # =========================================
    # Blocker Detection
    # =========================================

    async def detect_blockers(self, profile_id: str) -> Dict[str, Any]:
        """
        Monitor for projects with >5 days inactivity.

        Publishes PROJECT_STALLED events for blocked projects.

        Args:
            profile_id: Profile UUID

        Returns:
            List of detected blockers
        """
        self._log_start("detect_blockers", profile_id=profile_id)

        # Get active projects
        projects = await get_projects(profile_id, status="active")
        blockers = []

        for project in projects:
            last_activity = project.get("last_activity_at")
            if not last_activity:
                continue

            # Parse datetime
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))

            days_stuck = (datetime.now(last_activity.tzinfo) - last_activity).days

            if days_stuck >= self.blocker_threshold_days:
                blocker = {
                    "project_id": project["id"],
                    "project_name": project["name"],
                    "days_stuck": days_stuck,
                    "type": "inactivity",
                    "completion_rate": project.get("completion_rate", 0),
                }
                blockers.append(blocker)

                # Publish stalled event
                eds = await self.compute_eds(profile_id)
                await self._publish_event("PROJECT_STALLED", {
                    "profileId": profile_id,
                    "projectId": project["id"],
                    "days": days_stuck,
                    "debt": eds,
                })

        self._log_complete("detect_blockers", profile_id=profile_id, blockers_found=len(blockers))

        return {
            "success": True,
            "blockers": blockers,
            "count": len(blockers),
        }

    # =========================================
    # EDS Computation
    # =========================================

    async def compute_eds(self, profile_id: str) -> float:
        """
        Compute Execution Debt Score.

        EDS = Σ(missed_microsteps × days_delayed × difficulty_weight)

        Target: EDS < 50 (Huda benchmark: 12)

        Args:
            profile_id: Profile UUID

        Returns:
            EDS value
        """
        eds = await compute_eds(profile_id)

        self.logger.info("eds_computed", profile_id=profile_id, eds=eds)

        return eds

    # =========================================
    # Status Check
    # =========================================

    async def check_status(self, profile_id: str) -> Dict[str, Any]:
        """
        Get overall execution status for a profile.

        Returns projects, crises, and EDS.
        """
        profile = await self._get_profile(profile_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        projects = await get_projects(profile_id)
        eds = await self.compute_eds(profile_id)

        active_projects = [p for p in projects if p.get("status") == "active"]
        completed_projects = [p for p in projects if p.get("status") == "completed"]

        return {
            "success": True,
            "profile_id": profile_id,
            "execution_debt": eds,
            "total_projects": len(projects),
            "active_projects": len(active_projects),
            "completed_projects": len(completed_projects),
            "eds_status": "healthy" if eds < 50 else "at_risk" if eds < 100 else "critical",
        }
