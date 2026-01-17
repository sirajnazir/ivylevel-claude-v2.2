"""
Pattern I3: Goal Monitoring
v5.4 True Autonomous Agents

USP: Progress tracking toward admission goals.
BUILD, not buy - custom goal intelligence.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class GoalStatus(str, Enum):
    """Status of a goal."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AT_RISK = "at_risk"
    ON_TRACK = "on_track"
    COMPLETED = "completed"
    MISSED = "missed"


class GoalCategory(str, Enum):
    """Categories of admission goals."""
    IDENTITY = "identity"           # Develop spike/narrative
    ACTIVITIES = "activities"       # Build activity portfolio
    ACADEMICS = "academics"         # Maintain/improve GPA
    TESTING = "testing"            # SAT/ACT scores
    AWARDS = "awards"              # Win recognitions
    PROGRAMS = "programs"          # Summer programs
    ESSAYS = "essays"              # Write compelling essays
    RECOMMENDATIONS = "recommendations"  # Secure strong recs


class Goal(BaseModel):
    """A tracked goal."""
    id: str
    category: GoalCategory
    title: str
    description: str = ""
    target_date: Optional[datetime] = None
    status: GoalStatus = GoalStatus.NOT_STARTED
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GoalProgressReport(BaseModel):
    """Summary of goal progress for a student."""
    profile_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    overall_progress: float = Field(ge=0.0, le=100.0)
    overall_status: GoalStatus
    goals_by_category: Dict[str, List[Goal]]
    at_risk_goals: List[Goal]
    upcoming_milestones: List[Dict[str, Any]]
    recommendations: List[str]


# Goal templates by grade (USP)
GOAL_TEMPLATES_BY_GRADE = {
    9: [
        {
            "category": GoalCategory.ACTIVITIES,
            "title": "Explore 3-4 potential activity areas",
            "description": "Try different activities to find your interests",
        },
        {
            "category": GoalCategory.ACADEMICS,
            "title": "Establish strong academic foundation",
            "description": "Build study habits and aim for high GPA",
        },
    ],
    10: [
        {
            "category": GoalCategory.IDENTITY,
            "title": "Identify emerging spike area",
            "description": "Start focusing on 1-2 areas of deep interest",
        },
        {
            "category": GoalCategory.ACTIVITIES,
            "title": "Deepen commitment in key activities",
            "description": "Move from participation to impact/leadership",
        },
        {
            "category": GoalCategory.TESTING,
            "title": "Take PSAT and analyze results",
            "description": "Identify areas for SAT/ACT preparation",
        },
    ],
    11: [
        {
            "category": GoalCategory.IDENTITY,
            "title": "Crystallize unique narrative",
            "description": "Define spike and connecting pillars",
        },
        {
            "category": GoalCategory.ACTIVITIES,
            "title": "Achieve leadership positions",
            "description": "Move into leadership roles in key activities",
        },
        {
            "category": GoalCategory.TESTING,
            "title": "Complete standardized testing",
            "description": "Achieve target SAT/ACT scores",
        },
        {
            "category": GoalCategory.PROGRAMS,
            "title": "Apply to summer programs",
            "description": "Participate in selective summer opportunities",
        },
        {
            "category": GoalCategory.AWARDS,
            "title": "Pursue relevant recognitions",
            "description": "Apply for awards aligned with spike",
        },
    ],
    12: [
        {
            "category": GoalCategory.ESSAYS,
            "title": "Complete personal statement",
            "description": "Write compelling Common App essay",
        },
        {
            "category": GoalCategory.ESSAYS,
            "title": "Complete supplemental essays",
            "description": "Tailor essays for each school",
        },
        {
            "category": GoalCategory.RECOMMENDATIONS,
            "title": "Secure strong recommendations",
            "description": "Request and guide recommenders",
        },
        {
            "category": GoalCategory.ACTIVITIES,
            "title": "Demonstrate continued commitment",
            "description": "Maintain senior year activities",
        },
    ],
}


class GoalMonitor:
    """
    Monitors progress toward admission goals.

    USP: Proactive detection of at-risk goals.

    Key features:
    1. Grade-appropriate goal templates
    2. Progress tracking with milestones
    3. At-risk detection with interventions
    4. Personalized recommendations
    """

    def __init__(self, supabase_client=None):
        """
        Initialize goal monitor.

        Args:
            supabase_client: Optional Supabase client for persistence
        """
        self.supabase = supabase_client

    async def initialize_goals(
        self,
        profile_id: str,
        grade: int,
        existing_goals: Optional[List[Goal]] = None,
    ) -> List[Goal]:
        """
        Initialize goals for a student based on grade.

        Args:
            profile_id: Student's profile ID
            grade: Current grade level
            existing_goals: Any goals already set

        Returns:
            Complete list of goals
        """
        existing_ids = {g.id for g in (existing_goals or [])}
        goals = list(existing_goals or [])

        # Add grade-appropriate template goals
        templates = GOAL_TEMPLATES_BY_GRADE.get(grade, [])
        for i, template in enumerate(templates):
            goal_id = f"{profile_id}_{grade}_{template['category'].value}_{i}"
            if goal_id not in existing_ids:
                goals.append(Goal(
                    id=goal_id,
                    category=template["category"],
                    title=template["title"],
                    description=template["description"],
                ))

        logger.info(f"Initialized {len(goals)} goals for profile {profile_id}")
        return goals

    def assess_goal_status(
        self,
        goal: Goal,
        current_date: datetime,
        context: Dict[str, Any],
    ) -> GoalStatus:
        """
        Assess current status of a goal.

        USP: Smart status detection based on progress and timeline.
        """
        # Already terminal?
        if goal.status in [GoalStatus.COMPLETED, GoalStatus.MISSED]:
            return goal.status

        # Check if completed
        if goal.progress_percentage >= 100:
            return GoalStatus.COMPLETED

        # Not started?
        if goal.progress_percentage == 0:
            if goal.target_date:
                days_until = (goal.target_date - current_date).days
                if days_until < 7:
                    return GoalStatus.AT_RISK  # Deadline soon, not started
            return GoalStatus.NOT_STARTED

        # In progress - check if on track
        if goal.target_date:
            days_until = (goal.target_date - current_date).days
            total_days = (goal.target_date - goal.created_at).days

            if total_days > 0:
                expected_progress = ((total_days - days_until) / total_days) * 100
                progress_gap = expected_progress - goal.progress_percentage

                if progress_gap > 20:
                    return GoalStatus.AT_RISK  # Significantly behind
                elif days_until < 0:
                    return GoalStatus.MISSED  # Past deadline
                elif progress_gap > 10:
                    return GoalStatus.IN_PROGRESS  # Slightly behind
                else:
                    return GoalStatus.ON_TRACK

        # No deadline - just check progress
        if goal.progress_percentage >= 50:
            return GoalStatus.ON_TRACK
        elif len(goal.blockers) > 0:
            return GoalStatus.AT_RISK
        else:
            return GoalStatus.IN_PROGRESS

    def update_goal_progress(
        self,
        goal: Goal,
        new_progress: float,
        milestone_completed: Optional[str] = None,
    ) -> Goal:
        """
        Update goal progress.

        Args:
            goal: Goal to update
            new_progress: New progress percentage
            milestone_completed: Optional milestone that was completed

        Returns:
            Updated goal
        """
        goal.progress_percentage = min(100.0, max(0.0, new_progress))
        goal.updated_at = datetime.utcnow()

        if milestone_completed:
            for milestone in goal.milestones:
                if milestone.get("name") == milestone_completed:
                    milestone["completed"] = True
                    milestone["completed_at"] = datetime.utcnow().isoformat()

        # Update status
        goal.status = self.assess_goal_status(
            goal,
            datetime.utcnow(),
            {},
        )

        if goal.progress_percentage >= 100:
            goal.status = GoalStatus.COMPLETED
            logger.info(f"Goal {goal.id} completed!")

        return goal

    def add_blocker(
        self,
        goal: Goal,
        blocker: str,
    ) -> Goal:
        """Add a blocker to a goal."""
        if blocker not in goal.blockers:
            goal.blockers.append(blocker)
            goal.status = GoalStatus.AT_RISK
            goal.updated_at = datetime.utcnow()
        return goal

    def resolve_blocker(
        self,
        goal: Goal,
        blocker: str,
    ) -> Goal:
        """Resolve a blocker on a goal."""
        if blocker in goal.blockers:
            goal.blockers.remove(blocker)
            goal.updated_at = datetime.utcnow()
            # Re-assess status
            goal.status = self.assess_goal_status(goal, datetime.utcnow(), {})
        return goal

    async def generate_progress_report(
        self,
        profile_id: str,
        goals: List[Goal],
        student_context: Dict[str, Any],
    ) -> GoalProgressReport:
        """
        Generate comprehensive progress report.

        USP: Actionable insights, not just data.
        """
        now = datetime.utcnow()

        # Update all goal statuses
        for goal in goals:
            goal.status = self.assess_goal_status(goal, now, student_context)

        # Calculate overall progress
        if goals:
            overall_progress = sum(g.progress_percentage for g in goals) / len(goals)
        else:
            overall_progress = 0

        # Determine overall status
        at_risk_count = sum(1 for g in goals if g.status == GoalStatus.AT_RISK)
        completed_count = sum(1 for g in goals if g.status == GoalStatus.COMPLETED)

        if at_risk_count > len(goals) * 0.3:
            overall_status = GoalStatus.AT_RISK
        elif completed_count == len(goals):
            overall_status = GoalStatus.COMPLETED
        elif overall_progress >= 70:
            overall_status = GoalStatus.ON_TRACK
        else:
            overall_status = GoalStatus.IN_PROGRESS

        # Group by category
        goals_by_category: Dict[str, List[Goal]] = {}
        for goal in goals:
            cat = goal.category.value
            if cat not in goals_by_category:
                goals_by_category[cat] = []
            goals_by_category[cat].append(goal)

        # Find at-risk goals
        at_risk_goals = [g for g in goals if g.status == GoalStatus.AT_RISK]

        # Find upcoming milestones
        upcoming_milestones = []
        for goal in goals:
            for milestone in goal.milestones:
                if not milestone.get("completed"):
                    upcoming_milestones.append({
                        "goal_id": goal.id,
                        "goal_title": goal.title,
                        "milestone": milestone.get("name"),
                        "due_date": milestone.get("due_date"),
                    })

        # Generate recommendations (USP)
        recommendations = self._generate_recommendations(
            goals,
            at_risk_goals,
            student_context,
        )

        return GoalProgressReport(
            profile_id=profile_id,
            overall_progress=overall_progress,
            overall_status=overall_status,
            goals_by_category=goals_by_category,
            at_risk_goals=at_risk_goals,
            upcoming_milestones=upcoming_milestones[:5],  # Top 5
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        goals: List[Goal],
        at_risk_goals: List[Goal],
        student_context: Dict[str, Any],
    ) -> List[str]:
        """
        Generate actionable recommendations.

        USP: Personalized advice based on goal status.
        """
        recommendations = []

        # At-risk goals get priority recommendations
        for goal in at_risk_goals:
            if goal.blockers:
                recommendations.append(
                    f"Resolve blocker for '{goal.title}': {goal.blockers[0]}"
                )
            elif goal.progress_percentage < 25:
                recommendations.append(
                    f"Start making progress on '{goal.title}' - you're behind schedule"
                )
            else:
                recommendations.append(
                    f"Accelerate work on '{goal.title}' to get back on track"
                )

        # Category-specific recommendations
        for category, category_goals in self._group_by_category(goals).items():
            avg_progress = sum(g.progress_percentage for g in category_goals) / len(category_goals)

            if avg_progress < 30 and category == GoalCategory.IDENTITY.value:
                recommendations.append(
                    "Focus on identity development - this forms the foundation of your application"
                )
            elif avg_progress < 30 and category == GoalCategory.ACTIVITIES.value:
                recommendations.append(
                    "Prioritize deepening commitment in your key activities"
                )

        # Grade-specific recommendations
        grade = student_context.get("grade", 11)
        if grade == 11:
            testing_goals = [g for g in goals if g.category == GoalCategory.TESTING]
            if testing_goals and all(g.progress_percentage < 50 for g in testing_goals):
                recommendations.append(
                    "Junior year is critical for SAT/ACT - prioritize test preparation"
                )

        return recommendations[:5]  # Top 5 recommendations

    def _group_by_category(self, goals: List[Goal]) -> Dict[str, List[Goal]]:
        """Group goals by category."""
        result: Dict[str, List[Goal]] = {}
        for goal in goals:
            cat = goal.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(goal)
        return result


# Convenience functions
async def get_goal_progress(
    supabase_client,
    profile_id: str,
    grade: int,
) -> GoalProgressReport:
    """
    Quick helper to get goal progress report.

    Usage:
        report = await get_goal_progress(supabase, profile_id, 11)
    """
    monitor = GoalMonitor(supabase_client)
    goals = await monitor.initialize_goals(profile_id, grade)
    return await monitor.generate_progress_report(profile_id, goals, {"grade": grade})
