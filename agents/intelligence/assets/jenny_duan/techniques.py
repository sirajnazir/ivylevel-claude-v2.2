"""
Jenny Duan's Coaching Techniques - Converted to CoachingAssets

These are the actual coaching techniques that have proven effective,
encoded as assets that can be selected and tracked for effectiveness.

Source: Jenny Duan's coaching methodology, validated through years of
helping students win awards and gain admission to top schools.
"""

from ...primitives import (
    CoachingAsset,
    AssetType,
    AssetDomain,
    TriggerCondition,
    Applicability,
    Provenance,
)


def create_jenny_techniques():
    """Create Jenny Duan's coaching technique assets."""
    return [
        # =================================================================
        # 3x TIME BUFFER
        # =================================================================
        CoachingAsset(
            name="3x Time Buffer",
            asset_type=AssetType.TECHNIQUE,
            domain=AssetDomain.EXECUTION,
            secondary_domains=[AssetDomain.STRATEGY],
            tags=["time_management", "planning", "realistic_estimates", "jenny_duan"],
            content={
                "description": "Apply realistic time estimates by multiplying student estimates by a buffer based on task type. Students chronically underestimate how long tasks take.",
                "methodology": {
                    "principle": "Students underestimate by 2-3x. Adjust estimates to prevent missed deadlines and reduce stress.",
                    "multipliers": {
                        "essay": 3.0,
                        "research": 2.5,
                        "creative": 3.0,
                        "admin": 2.0,
                        "default": 2.5,
                    },
                    "application": [
                        "Get student's estimate",
                        "Apply appropriate multiplier",
                        "Schedule with buffer included",
                        "Set intermediate checkpoints",
                    ],
                },
                "example": {
                    "student_estimate": "4 hours for essay",
                    "buffered_estimate": "12 hours (3x)",
                    "schedule": "3 hours/week for 4 weeks",
                },
                "why_it_works": "Removes the stress of 'running out of time' and allows for iteration and improvement.",
            },
            trigger_config=TriggerCondition(
                event_types=["project_planning", "deadline_setting", "time_estimation"],
                lifecycle_stages=["planning", "execution"],
            ),
            applicability=Applicability(
                grade_levels=[9, 10, 11, 12],
                archetypes=["sprinter", "perfectionist", "balanced"],  # Most useful for these
            ),
            provenance=Provenance(
                source="jenny_duan",
                author="Jenny Duan",
                version_notes="Core technique from Jenny's methodology",
            ),
        ),

        # =================================================================
        # CELEBRATION CALIBRATION
        # =================================================================
        CoachingAsset(
            name="Celebration Calibration",
            asset_type=AssetType.TECHNIQUE,
            domain=AssetDomain.EMOTIONAL,
            secondary_domains=[AssetDomain.EXECUTION],
            tags=["motivation", "celebration", "milestone", "positive_reinforcement", "jenny_duan"],
            content={
                "description": "Celebrate wins proportional to their difficulty and significance. Not all wins deserve the same celebration.",
                "methodology": {
                    "principle": "Match celebration intensity to achievement significance to maintain motivation without cheapening real wins.",
                    "levels": {
                        "micro": {
                            "threshold": "<0.5 difficulty",
                            "response": "Step completed. Keep the momentum!",
                            "actions": ["brief acknowledgment"],
                        },
                        "minor": {
                            "threshold": "0.5-1.0 difficulty",
                            "response": "Nice work! You're making real progress.",
                            "actions": ["positive reinforcement", "note progress"],
                        },
                        "major": {
                            "threshold": "1.0-1.5 difficulty",
                            "response": "Major milestone achieved! Document this win.",
                            "actions": ["detailed acknowledgment", "document for applications", "share with support network"],
                        },
                        "breakthrough": {
                            "threshold": ">=1.5 difficulty",
                            "response": "Outstanding achievement! This sets you apart.",
                            "actions": ["full celebration", "strategic documentation", "application narrative update"],
                        },
                    },
                    "score_calculation": [
                        "Start with task difficulty",
                        "Multiply by 1.5 if milestone",
                        "Multiply by 1.3 if stretch goal",
                        "Multiply by 1.1 if completed early",
                    ],
                },
                "why_it_works": "Prevents celebration fatigue while ensuring significant wins get proper recognition.",
            },
            trigger_config=TriggerCondition(
                event_types=["task_completion", "milestone_reached", "award_won", "goal_achieved"],
                lifecycle_stages=["execution", "completion"],
            ),
            applicability=Applicability(
                grade_levels=[9, 10, 11, 12],
            ),
            provenance=Provenance(
                source="jenny_duan",
                author="Jenny Duan",
                version_notes="Calibrated celebration system",
            ),
        ),

        # =================================================================
        # SILENCE DETECTION
        # =================================================================
        CoachingAsset(
            name="Silence Detection",
            asset_type=AssetType.TECHNIQUE,
            domain=AssetDomain.EMOTIONAL,
            secondary_domains=[AssetDomain.EXECUTION],
            tags=["engagement", "check_in", "support", "proactive", "jenny_duan"],
            content={
                "description": "Detect when a student has been quiet too long and intervene appropriately. Silence often indicates struggle.",
                "methodology": {
                    "principle": "Silence is a signal. Different durations require different responses.",
                    "thresholds": {
                        "warning": {
                            "days": "3-6",
                            "severity": "low",
                            "nudge": "Just checking in! Small steps daily beat big bursts weekly.",
                            "action": "gentle_reminder",
                        },
                        "concern": {
                            "days": "7-13",
                            "severity": "medium",
                            "nudge": "It's been a week. What's one small thing you could do today?",
                            "action": "personalized_check_in",
                        },
                        "critical": {
                            "days": "14+",
                            "severity": "high",
                            "nudge": "We haven't heard from you in over 2 weeks. Is everything okay?",
                            "action": "direct_outreach",
                        },
                    },
                    "response_adaptation": "Adapt message tone based on student's communication style preference.",
                },
                "why_it_works": "Catches disengagement early, prevents ghosting, shows students they're supported.",
            },
            trigger_config=TriggerCondition(
                event_types=["scheduled_check", "inactivity_detected"],
                lifecycle_stages=["execution", "any"],
            ),
            applicability=Applicability(
                grade_levels=[9, 10, 11, 12],
            ),
            provenance=Provenance(
                source="jenny_duan",
                author="Jenny Duan",
                version_notes="Proactive engagement technique",
            ),
        ),

        # =================================================================
        # CRISIS ALCHEMY (4-Step Protocol)
        # =================================================================
        CoachingAsset(
            name="Crisis Alchemy Protocol",
            asset_type=AssetType.FRAMEWORK,
            domain=AssetDomain.EMOTIONAL,
            secondary_domains=[AssetDomain.STRATEGY, AssetDomain.EXECUTION],
            tags=["crisis", "rejection", "failure", "resilience", "pivot", "jenny_duan"],
            content={
                "description": "Transform crises into opportunities through a 4-step protocol. Rejection becomes a pivot to something stronger.",
                "methodology": {
                    "principle": "Every setback contains the seed of an opportunity. The key is rapid response with emotional validation first.",
                    "steps": {
                        "step1_validate": {
                            "duration": "2 seconds",
                            "action": "Acknowledge emotion immediately",
                            "template": "I hear you. This is difficult, and your feelings are valid.",
                            "goal": "Student feels heard before problem-solving begins",
                        },
                        "step2_act": {
                            "duration": "10 seconds",
                            "action": "Provide one concrete micro-action",
                            "template": "Right now, do this one thing: [specific small action]",
                            "goal": "Prevent paralysis, create forward momentum",
                        },
                        "step3_reframe": {
                            "duration": "30 seconds",
                            "action": "Find the opportunity angle",
                            "template": "Here's what this opens up for you: [opportunity]",
                            "goal": "Shift from loss to possibility",
                        },
                        "step4_create": {
                            "duration": "2 minutes",
                            "action": "Design new activity or pivot",
                            "template": "Let's create something from this. What if we [new direction]?",
                            "goal": "Channel energy into proactive creation",
                        },
                    },
                    "crisis_types": ["rejection", "failure", "blocker", "overwhelm", "deadline_miss"],
                },
                "example": {
                    "crisis": "Rejected from research program",
                    "step1": "I know this hurts. You put a lot into that application.",
                    "step2": "Send a thank-you email to the program asking for feedback.",
                    "step3": "This rejection reveals a gap - independent research shows more initiative than program participation.",
                    "step4": "Let's design your own research project with a mentor you recruit yourself.",
                },
                "why_it_works": "Combines emotional intelligence with action orientation. Prevents spiraling while channeling energy productively.",
            },
            trigger_config=TriggerCondition(
                event_types=["crisis_detected", "rejection_reported", "failure_reported", "overwhelm_detected"],
                emotional_states=["distressed", "disappointed", "anxious", "overwhelmed"],
            ),
            applicability=Applicability(
                grade_levels=[9, 10, 11, 12],
            ),
            provenance=Provenance(
                source="jenny_duan",
                author="Jenny Duan",
                version_notes="ACP-003: Crisis Alchemy Protocol",
            ),
        ),

        # =================================================================
        # STRATEGIC OVERWHELM
        # =================================================================
        CoachingAsset(
            name="Strategic Overwhelm",
            asset_type=AssetType.TECHNIQUE,
            domain=AssetDomain.EXECUTION,
            secondary_domains=[AssetDomain.STRATEGY],
            tags=["task_management", "productivity", "stretch_goals", "jenny_duan"],
            content={
                "description": "Assign 1.4x tasks because completing 73% of 10 tasks is better than 70% of 7 tasks.",
                "methodology": {
                    "principle": "Controlled overwhelm produces more output than comfortable pacing.",
                    "math": {
                        "overwhelm_factor": 1.4,
                        "target_completion_rate": 0.73,
                        "example": {
                            "base_tasks": 7,
                            "inflated_tasks": 10,
                            "expected_completion": 7.3,
                            "net_gain": 2.3,
                        },
                    },
                    "application": [
                        "Calculate base task count",
                        "Multiply by 1.4",
                        "Add stretch versions of key tasks",
                        "Set expectations that not all will complete",
                        "Celebrate stretch completions especially",
                    ],
                    "guardrails": [
                        "Monitor for actual overwhelm (not productive)",
                        "Adjust factor based on student archetype",
                        "Lower for students with low overwhelm tolerance",
                    ],
                },
                "why_it_works": "People rise to expectations. Setting higher expectations produces higher output, even with lower completion rate.",
            },
            trigger_config=TriggerCondition(
                event_types=["project_planning", "task_assignment", "sprint_planning"],
                lifecycle_stages=["planning"],
            ),
            applicability=Applicability(
                grade_levels=[10, 11, 12],  # Not for freshmen
                archetypes=["achiever", "sprinter", "balanced"],  # Not for perfectionists
                exclude_conditions=["low_overwhelm_tolerance", "burnout_risk"],
            ),
            provenance=Provenance(
                source="jenny_duan",
                author="Jenny Duan",
                version_notes="ACP-004: Strategic Overwhelm",
            ),
        ),

        # =================================================================
        # TALK-FIRST-WRITE-SECOND
        # =================================================================
        CoachingAsset(
            name="Talk-First-Write-Second",
            asset_type=AssetType.TECHNIQUE,
            domain=AssetDomain.ESSAYS,
            secondary_domains=[AssetDomain.EXECUTION],
            tags=["essay_writing", "brainstorming", "blank_page", "creative", "jenny_duan"],
            content={
                "description": "Overcome the blank page problem by speaking first, then transcribing and refining.",
                "methodology": {
                    "principle": "Speaking is easier than writing. Start with voice, convert to text.",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Record voice memo about the topic",
                            "duration": "5-10 minutes",
                            "guidance": "Just talk. Don't worry about structure.",
                        },
                        {
                            "step": 2,
                            "action": "Transcribe the recording",
                            "duration": "Automated",
                            "guidance": "Use transcription service or app.",
                        },
                        {
                            "step": 3,
                            "action": "Identify key themes and stories",
                            "duration": "15 minutes",
                            "guidance": "Highlight the gold in the transcript.",
                        },
                        {
                            "step": 4,
                            "action": "Create outline from themes",
                            "duration": "20 minutes",
                            "guidance": "Structure emerges from content.",
                        },
                        {
                            "step": 5,
                            "action": "Write first draft (no editing)",
                            "duration": "1 hour",
                            "guidance": "Get it down, then get it good.",
                        },
                    ],
                },
                "why_it_works": "Bypasses perfectionism that blocks writing. Voice captures authentic stories.",
            },
            trigger_config=TriggerCondition(
                event_types=["essay_start", "writing_block", "brainstorming"],
                lifecycle_stages=["planning", "execution"],
            ),
            applicability=Applicability(
                grade_levels=[10, 11, 12],
            ),
            provenance=Provenance(
                source="jenny_duan",
                author="Jenny Duan",
                version_notes="ACP-007: Talk-First-Write-Second",
            ),
        ),

        # =================================================================
        # HUDA BENCHMARK
        # =================================================================
        CoachingAsset(
            name="Huda Benchmark",
            asset_type=AssetType.REFERENCE,
            domain=AssetDomain.ASSESSMENT,
            secondary_domains=[AssetDomain.STRATEGY],
            tags=["benchmark", "ideal_student", "calibration", "jenny_duan"],
            content={
                "description": "The Huda Benchmark - metrics from an ideal student execution profile for calibration.",
                "metrics": {
                    "execution_debt_score": {
                        "huda_value": 12,
                        "threshold_healthy": 50,
                        "threshold_at_risk": 100,
                        "calculation": "SUM(missed_steps * days_delayed * difficulty)",
                    },
                    "project_completion_rate": {
                        "huda_value": 1.0,
                        "threshold_healthy": 0.8,
                        "threshold_at_risk": 0.6,
                    },
                    "crisis_recovery_time_hours": {
                        "huda_value": 2,
                        "threshold_healthy": 72,
                        "threshold_at_risk": 168,
                    },
                    "task_completion_rate": {
                        "huda_value": 0.73,
                        "threshold_healthy": 0.7,
                        "threshold_at_risk": 0.5,
                    },
                },
                "usage": "Compare student metrics against Huda benchmark to identify areas for improvement.",
            },
            trigger_config=TriggerCondition(
                event_types=["assessment", "progress_review", "calibration"],
                lifecycle_stages=["assessment", "review"],
            ),
            applicability=Applicability(
                grade_levels=[9, 10, 11, 12],
            ),
            provenance=Provenance(
                source="jenny_duan",
                author="Jenny Duan",
                version_notes="Calibration benchmark from ideal student profile",
            ),
        ),
    ]


# Export the techniques for seeding
JENNY_TECHNIQUES = create_jenny_techniques()
