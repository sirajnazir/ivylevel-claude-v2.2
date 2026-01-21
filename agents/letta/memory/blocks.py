"""
Memory Block Definitions
========================

Defines the structure of Letta memory blocks for IvyLevel agents.

Each block has:
- name: Unique identifier
- description: Human-readable description
- schema: Structure of the block content
- max_chars: Letta memory limit (default 5000)
- build_fn: Function to build block content from Supabase data
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime
import json


@dataclass
class MemoryBlock(ABC):
    """Base class for Letta memory blocks."""

    name: str
    description: str
    max_chars: int = 5000

    @abstractmethod
    def build(self, data: Dict[str, Any]) -> str:
        """Build the memory block content from source data."""
        pass

    def truncate(self, content: str) -> str:
        """Truncate content to fit within max_chars limit."""
        if len(content) <= self.max_chars:
            return content

        # Truncate with ellipsis indicator
        truncate_at = self.max_chars - 20
        return content[:truncate_at] + "\n...[truncated]"


@dataclass
class StudentProfileBlock(MemoryBlock):
    """
    Student profile memory block.

    Contains core student attributes from the profiles table:
    - Basic info (name, grade, school type)
    - Academic profile (GPA, test scores, course rigor)
    - Archetype and CRI score
    - Target schools and intended major
    """

    name: str = "student_profile"
    description: str = "Core student attributes and assessment results"

    def build(self, data: Dict[str, Any]) -> str:
        """Build student profile block from profile data."""
        profile = data.get("profile", {})
        assessment = data.get("assessment", {})

        lines = [
            "# Student Profile",
            "",
            f"**Name:** {profile.get('name', 'Unknown')}",
            f"**Grade:** {profile.get('grade', 'N/A')}",
            f"**School Type:** {profile.get('school_type', 'N/A')}",
            "",
            "## Academic Profile",
            f"- GPA: {profile.get('gpa', 'N/A')}",
            f"- Test Scores: {self._format_test_scores(profile.get('test_scores', {}))}",
            f"- Course Rigor: {profile.get('course_rigor', 'N/A')}",
            "",
            "## Assessment Results",
            f"- Archetype: {assessment.get('archetype', 'Undetermined')}",
            f"- CRI Score: {assessment.get('cri_score', 'N/A')}",
            f"- Narrative DNA: {assessment.get('narrative_dna', 'Pending')[:200]}",
            "",
            "## Goals",
            f"- Target Schools: {', '.join(profile.get('target_schools', [])[:5])}",
            f"- Intended Major: {profile.get('intended_major', 'Undecided')}",
            "",
            "## Key Strengths",
        ]

        strengths = assessment.get("strengths", [])
        for strength in strengths[:5]:
            lines.append(f"- {strength}")

        content = "\n".join(lines)
        return self.truncate(content)

    def _format_test_scores(self, scores: Dict[str, Any]) -> str:
        """Format test scores for display."""
        if not scores:
            return "N/A"

        parts = []
        if "sat" in scores:
            parts.append(f"SAT: {scores['sat']}")
        if "act" in scores:
            parts.append(f"ACT: {scores['act']}")
        if "ap_count" in scores:
            parts.append(f"APs: {scores['ap_count']}")

        return ", ".join(parts) if parts else "N/A"


@dataclass
class CoachingHistoryBlock(MemoryBlock):
    """
    Coaching history memory block.

    Contains recent coaching interactions:
    - Recent conversations (last 5)
    - Key decisions made
    - Techniques used and effectiveness
    - Learned patterns about the student
    """

    name: str = "coaching_history"
    description: str = "Recent coaching interactions and learned patterns"

    def build(self, data: Dict[str, Any]) -> str:
        """Build coaching history block from interaction data."""
        interactions = data.get("recent_interactions", [])
        patterns = data.get("learned_patterns", [])
        techniques = data.get("techniques_used", [])

        lines = [
            "# Coaching History",
            "",
            "## Recent Interactions",
        ]

        for i, interaction in enumerate(interactions[:5], 1):
            lines.append(f"\n### Interaction {i} ({interaction.get('date', 'Unknown')})")
            lines.append(f"- Topic: {interaction.get('topic', 'General')}")
            lines.append(f"- Outcome: {interaction.get('outcome', 'N/A')}")
            lines.append(f"- Summary: {interaction.get('summary', '')[:150]}")

        lines.extend([
            "",
            "## Learned Patterns",
        ])

        for pattern in patterns[:5]:
            lines.append(f"- {pattern.get('type', 'Unknown')}: {pattern.get('observation', '')[:100]}")

        lines.extend([
            "",
            "## Effective Techniques",
        ])

        for tech in techniques[:5]:
            lines.append(f"- {tech.get('name', 'Unknown')} (effectiveness: {tech.get('effectiveness', 'N/A')})")

        content = "\n".join(lines)
        return self.truncate(content)


@dataclass
class ActiveGameplanBlock(MemoryBlock):
    """
    Active gameplan memory block.

    Contains current strategic plan:
    - Active goals and milestones
    - Current phase (junior year prep, senior year apps, etc.)
    - P0/P1/P2 priorities
    - Upcoming deadlines
    """

    name: str = "active_gameplan"
    description: str = "Current strategic plan and priorities"

    def build(self, data: Dict[str, Any]) -> str:
        """Build active gameplan block from gameplan data."""
        gameplan = data.get("gameplan", {})
        tasks = data.get("tasks", [])

        lines = [
            "# Active GamePlan",
            "",
            f"**Phase:** {gameplan.get('phase', 'Initial Planning')}",
            f"**Created:** {gameplan.get('created_at', 'N/A')[:10]}",
            f"**Status:** {gameplan.get('status', 'Active')}",
            "",
            "## Strategic Focus",
            gameplan.get("strategic_focus", "Building strong foundation for applications"),
            "",
            "## P0 Tasks (Critical)",
        ]

        p0_tasks = [t for t in tasks if t.get("priority") == "P0"]
        for task in p0_tasks[:5]:
            status_icon = "✅" if task.get("status") == "completed" else "⬜"
            lines.append(f"- {status_icon} {task.get('title', 'Unknown')}")
            if task.get("due_date"):
                lines.append(f"  Due: {task['due_date'][:10]}")

        lines.extend([
            "",
            "## P1 Tasks (Important)",
        ])

        p1_tasks = [t for t in tasks if t.get("priority") == "P1"]
        for task in p1_tasks[:5]:
            status_icon = "✅" if task.get("status") == "completed" else "⬜"
            lines.append(f"- {status_icon} {task.get('title', 'Unknown')}")

        lines.extend([
            "",
            "## Milestones",
        ])

        milestones = gameplan.get("milestones", [])
        for ms in milestones[:5]:
            lines.append(f"- {ms.get('name', 'Unknown')}: {ms.get('status', 'Pending')}")

        content = "\n".join(lines)
        return self.truncate(content)


@dataclass
class OutcomeTrackerBlock(MemoryBlock):
    """
    Outcome tracker memory block.

    Tracks goal progress and achievements:
    - Active goals and their status
    - Recent achievements/wins
    - Goals at risk
    - Success metrics
    """

    name: str = "outcome_tracker"
    description: str = "Goal progress, achievements, and success metrics"

    def build(self, data: Dict[str, Any]) -> str:
        """Build outcome tracker block from goals and achievements data."""
        goals = data.get("goals", [])
        achievements = data.get("achievements", [])
        at_risk = data.get("at_risk_goals", [])

        lines = [
            "# Outcome Tracker",
            "",
            "## Active Goals",
        ]

        for goal in goals[:5]:
            progress = goal.get("progress", 0)
            progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
            lines.append(f"- {goal.get('primary_outcome', 'Unknown')}")
            lines.append(f"  Progress: [{progress_bar}] {progress}%")

        lines.extend([
            "",
            "## Recent Achievements",
        ])

        for ach in achievements[:5]:
            lines.append(f"- 🏆 {ach.get('title', 'Unknown')} ({ach.get('date', 'N/A')[:10]})")

        if at_risk:
            lines.extend([
                "",
                "## ⚠️ Goals at Risk",
            ])
            for goal in at_risk[:3]:
                lines.append(f"- {goal.get('primary_outcome', 'Unknown')}")
                lines.append(f"  Reason: {goal.get('risk_reason', 'Deadline approaching')}")

        lines.extend([
            "",
            "## Success Metrics",
            f"- Goals Completed: {data.get('goals_completed', 0)}",
            f"- Tasks Completed This Month: {data.get('tasks_completed_month', 0)}",
            f"- Avg Task Completion Rate: {data.get('completion_rate', 'N/A')}%",
        ])

        content = "\n".join(lines)
        return self.truncate(content)


@dataclass
class DeadlineStateBlock(MemoryBlock):
    """
    Deadline state memory block.

    Tracks upcoming deadlines:
    - Application deadlines
    - Task due dates
    - Important milestones
    - Urgency levels
    """

    name: str = "deadline_state"
    description: str = "Upcoming deadlines and time-sensitive items"

    def build(self, data: Dict[str, Any]) -> str:
        """Build deadline state block from deadline data."""
        deadlines = data.get("deadlines", [])
        overdue = data.get("overdue_tasks", [])
        upcoming = data.get("upcoming_7_days", [])

        lines = [
            "# Deadline State",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]

        if overdue:
            lines.extend([
                "## ⚠️ OVERDUE",
            ])
            for item in overdue[:5]:
                lines.append(f"- ❗ {item.get('title', 'Unknown')} (due: {item.get('due_date', 'N/A')[:10]})")

        lines.extend([
            "",
            "## Due This Week",
        ])

        for item in upcoming[:5]:
            days_left = item.get("days_until_due", "?")
            urgency = "🔴" if days_left <= 2 else "🟡" if days_left <= 5 else "🟢"
            lines.append(f"- {urgency} {item.get('title', 'Unknown')} ({days_left} days)")

        lines.extend([
            "",
            "## Application Deadlines",
        ])

        app_deadlines = [d for d in deadlines if d.get("type") == "application"]
        for dl in app_deadlines[:5]:
            lines.append(f"- {dl.get('school', 'Unknown')}: {dl.get('deadline', 'N/A')[:10]}")
            lines.append(f"  Type: {dl.get('round', 'Regular Decision')}")

        lines.extend([
            "",
            "## Upcoming Milestones",
        ])

        milestone_deadlines = [d for d in deadlines if d.get("type") == "milestone"]
        for dl in milestone_deadlines[:5]:
            lines.append(f"- {dl.get('title', 'Unknown')}: {dl.get('deadline', 'N/A')[:10]}")

        content = "\n".join(lines)
        return self.truncate(content)


# Global registry of all memory blocks
MEMORY_BLOCKS: Dict[str, MemoryBlock] = {
    "student_profile": StudentProfileBlock(),
    "coaching_history": CoachingHistoryBlock(),
    "active_gameplan": ActiveGameplanBlock(),
    "outcome_tracker": OutcomeTrackerBlock(),
    "deadline_state": DeadlineStateBlock(),
}


def get_memory_block(name: str) -> Optional[MemoryBlock]:
    """Get a memory block by name."""
    return MEMORY_BLOCKS.get(name)


def get_all_block_names() -> List[str]:
    """Get all memory block names."""
    return list(MEMORY_BLOCKS.keys())
