"""
168-Hour Framework Module
Implements Jenny Duan's time audit and weekly planning methodology.

Key Insight: "Do you know how many hours are in a week? 168."
Formula: 168 - fixed_commitments - social_media = passion_hours (~26/week)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date, timedelta


@dataclass
class FixedAllocations:
    """Fixed time allocations that cannot be changed."""
    sleep: float
    school: float
    transport: float
    misc: float
    religious: float
    total: float


@dataclass
class SocialMediaAudit:
    """Social media time audit results."""
    current: float
    target: float
    recovered: float


@dataclass
class TimeAudit:
    """Complete time audit results."""
    total: int
    fixed: FixedAllocations
    social_media: SocialMediaAudit
    passion_hours_available: float
    daily_passion_hours: float
    homework_hours: float


@dataclass
class TimeBlock:
    """A time block in the daily schedule."""
    start: str
    end: str
    activity: str
    notes: str


@dataclass
class DailySchedule:
    """Daily schedule with time blocks."""
    blocks: List[TimeBlock]
    flexibility_note: str


@dataclass
class Task:
    """A task with priority and time estimate."""
    id: str
    name: str
    priority: str  # P0, P1, P2
    estimated_hours: float
    deadline: Optional[date] = None
    category: str = "general"
    completed: bool = False


@dataclass
class WeeklyPlan:
    """Weekly plan with P0/P1/P2 prioritization."""
    week_start: date
    p0_must_complete: List[Task]
    p1_should_complete: List[Task]
    p2_if_time_permits: List[Task]
    total_hours_estimated: float
    available_hours: float
    buffer_hours: float
    flexibility_note: str = "We'll try this for 2 weeks and adjust if needed"


class TimeAuditModule:
    """Implements Jenny's 168-hour framework."""

    OPENING_QUESTION = "Do you know how many hours are in a week?"
    TOTAL_HOURS = 168
    DEFAULT_SOCIAL_MEDIA_TARGET = 7  # 1 hour per day
    DEFAULT_HOMEWORK_HOURS = 14  # 2 hours per day

    DEFAULT_SCHEDULE: List[TimeBlock] = [
        TimeBlock("16:15", "17:15", "Clubs/Leadership", "Emails, planning, delegating"),
        TimeBlock("17:15", "19:15", "Homework", "2 hours with efficiency hacks"),
        TimeBlock("19:15", "20:15", "Project 1", "Primary passion project"),
        TimeBlock("20:15", "21:00", "Project 2", "Secondary passion"),
        TimeBlock("21:00", "21:30", "Dinner", "Family time"),
        TimeBlock("21:30", "22:30", "Applications/SAT", "Test prep or applications"),
        TimeBlock("22:30", "23:00", "Wind down", "Prepare for sleep"),
        TimeBlock("23:00", "07:00", "Sleep", "8 hours rest"),
    ]

    HOMEWORK_EFFICIENCY_HACKS: List[Dict[str, Any]] = [
        {
            "hack": "Read ahead",
            "description": "Do all reading at beginning of week",
            "benefit": "Can participate in class, retain more"
        },
        {
            "hack": "Strategic note-taking",
            "description": "Take strategic notes, not transcription",
            "jenny_quote": "I spent 1 hour/day taking notes, peers watched YouTube, same AP scores"
        },
        {
            "hack": "In-class productivity",
            "description": "Do homework during class when finished early",
            "benefit": "Homework done before leaving school"
        },
        {
            "hack": "Delegation",
            "for": "Club leaders",
            "description": "Delegate manual tasks to officers",
            "jenny_quote": "You're the president - your job is strategy, not making posters"
        }
    ]

    def calculate_available_time(
        self,
        sleep_hours: float = 8,
        school_hours: float = 7.5,
        commute_minutes: int = 30,
        religious_hours: float = 0,
        misc_hours: float = 3,
        social_media_hours_daily: float = 4,
        homework_hours_daily: float = 2
    ) -> TimeAudit:
        """Calculate available passion hours using Jenny's 168-hour formula."""
        # Weekly totals
        sleep_weekly = sleep_hours * 7
        school_weekly = school_hours * 5  # 5 school days
        transport_weekly = (commute_minutes * 2 * 5) / 60  # Round trip, 5 days
        misc_weekly = misc_hours * 7  # Daily misc (eating, getting ready, etc.)

        fixed = FixedAllocations(
            sleep=sleep_weekly,
            school=school_weekly,
            transport=transport_weekly,
            misc=misc_weekly,
            religious=religious_hours,
            total=sleep_weekly + school_weekly + transport_weekly + misc_weekly + religious_hours
        )

        # Social media audit
        social_media_current = social_media_hours_daily * 7
        social_media_target = self.DEFAULT_SOCIAL_MEDIA_TARGET
        hours_recovered = max(0, social_media_current - social_media_target)

        social_media = SocialMediaAudit(
            current=social_media_current,
            target=social_media_target,
            recovered=hours_recovered
        )

        # Calculate passion hours
        flexible_total = self.TOTAL_HOURS - fixed.total
        homework_weekly = homework_hours_daily * 7
        passion_hours = flexible_total - homework_weekly - social_media_target

        return TimeAudit(
            total=self.TOTAL_HOURS,
            fixed=fixed,
            social_media=social_media,
            passion_hours_available=passion_hours,
            daily_passion_hours=passion_hours / 7,
            homework_hours=homework_weekly
        )

    def generate_daily_schedule(
        self,
        gets_home_at: str = "16:15",
        custom_blocks: Optional[List[Dict[str, str]]] = None
    ) -> DailySchedule:
        """Generate Jenny's recommended daily schedule."""
        if custom_blocks:
            blocks = [TimeBlock(**b) for b in custom_blocks]
        else:
            blocks = list(self.DEFAULT_SCHEDULE)

        return DailySchedule(
            blocks=blocks,
            flexibility_note="We'll try this for 2 weeks and adjust if needed. "
                           "The first block can be a nap if you're exhausted!"
        )

    def generate_weekly_plan(
        self,
        tasks: List[Dict[str, Any]],
        available_hours: float = 26
    ) -> WeeklyPlan:
        """Generate P0/P1/P2 prioritized weekly plan."""
        task_objects = [
            Task(
                id=t.get("id", str(i)),
                name=t.get("name", "Task"),
                priority=t.get("priority", "P2"),
                estimated_hours=t.get("estimated_hours", 1),
                deadline=t.get("deadline"),
                category=t.get("category", "general"),
                completed=t.get("completed", False)
            )
            for i, t in enumerate(tasks)
        ]

        p0 = [t for t in task_objects if t.priority == "P0"]
        p1 = [t for t in task_objects if t.priority == "P1"]
        p2 = [t for t in task_objects if t.priority == "P2"]

        total_hours = sum(t.estimated_hours for t in task_objects)
        buffer = available_hours * 0.2  # 20% buffer for unexpected

        return WeeklyPlan(
            week_start=date.today() - timedelta(days=date.today().weekday()),
            p0_must_complete=p0,
            p1_should_complete=p1,
            p2_if_time_permits=p2,
            total_hours_estimated=total_hours,
            available_hours=available_hours,
            buffer_hours=buffer
        )

    def generate_walkthrough_script(self, audit: TimeAudit) -> str:
        """Generate Jenny's conversational walkthrough script."""
        return f"""Do you know how many hours are in a week? [Wait for answer: 168]

Perfect! Let's take a backwards approach. We have 168 hours, and we're going to allocate how many hours you want to spend on everything.

How many hours do you sleep? [{audit.fixed.sleep / 7:.0f}] Okay, {audit.fixed.sleep / 7:.0f} times 7 is {audit.fixed.sleep:.0f} hours. So you have {168 - audit.fixed.sleep:.0f} hours remaining.

How many hours are you in school? [{audit.fixed.school / 5:.1f} hours, 5 days] That's {audit.fixed.school:.1f} hours. Now we're at {168 - audit.fixed.sleep - audit.fixed.school:.1f} hours.

Transportation, eating, getting ready... let's subtract another {audit.fixed.transport + audit.fixed.misc:.0f} hours.

Now, here's the big one: how much time do you spend on social media? [{audit.social_media.current / 7:.0f} hours a day] That's {audit.social_media.current:.0f} hours a week!

I'm going to challenge you to spend 1 hour on social media every day. I understand that 0 is impossible because you need to stay connected with friends.

If we cut from {audit.social_media.current:.0f} hours to {audit.social_media.target:.0f} hours, that's giving you back {audit.social_media.recovered:.0f} hours!

You actually have about {audit.passion_hours_available:.0f} hours a week for your passion projects! That's way more than you thought, right?

That's about {audit.daily_passion_hours:.1f} hours per day for the things that matter to you.

What do you think? Does that feel manageable?"""

    def format_weekly_plan(self, plan: WeeklyPlan) -> str:
        """Format weekly plan in Jenny's style."""
        lines = ["Here's your game plan for this week:\n"]

        lines.append("**P0 - Must Complete:**")
        for task in plan.p0_must_complete:
            deadline = f" - Due {task.deadline}" if task.deadline else ""
            lines.append(f"- [ ] {task.name} ({task.estimated_hours}h){deadline}")

        lines.append("\n**P1 - Should Complete:**")
        for task in plan.p1_should_complete:
            lines.append(f"- [ ] {task.name} ({task.estimated_hours}h)")

        lines.append("\n**P2 - If Time Permits:**")
        for task in plan.p2_if_time_permits:
            lines.append(f"- [ ] {task.name} ({task.estimated_hours}h)")

        lines.append(f"\n**Time Budget:**")
        lines.append(f"- Total estimated: {plan.total_hours_estimated}h")
        lines.append(f"- Available this week: {plan.available_hours}h")
        lines.append(f"- Buffer: {plan.buffer_hours:.1f}h for unexpected things")
        lines.append(f"\n{plan.flexibility_note}")
        lines.append("\nDoes this feel manageable? What needs to shift?")

        return "\n".join(lines)

    def get_efficiency_hacks(self) -> List[Dict[str, Any]]:
        """Return homework efficiency hacks."""
        return self.HOMEWORK_EFFICIENCY_HACKS

    def to_dict(self, audit: TimeAudit) -> Dict[str, Any]:
        """Convert TimeAudit to dictionary for API response."""
        return {
            "total_hours": audit.total,
            "fixed_allocations": {
                "sleep": audit.fixed.sleep,
                "school": audit.fixed.school,
                "transport": audit.fixed.transport,
                "misc": audit.fixed.misc,
                "religious": audit.fixed.religious,
                "total": audit.fixed.total,
            },
            "social_media": {
                "current_weekly": audit.social_media.current,
                "target_weekly": audit.social_media.target,
                "hours_recovered": audit.social_media.recovered,
            },
            "passion_hours_available": audit.passion_hours_available,
            "daily_passion_hours": round(audit.daily_passion_hours, 1),
            "homework_hours": audit.homework_hours,
        }


__all__ = ['TimeAuditModule', 'TimeAudit', 'TimeBlock', 'DailySchedule', 'Task', 'WeeklyPlan']
