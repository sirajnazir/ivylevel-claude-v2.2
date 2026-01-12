"""
Crisis Alchemy Module
Implements Jenny's 4-step crisis response protocol.

Protocol:
1. VALIDATE - Acknowledge the pain genuinely
2. ACT - Provide immediate micro-action (2 min)
3. REFRAME - Shift perspective on the situation
4. CREATE - Propose pivot that creates opportunity

Core Principle: Transform every setback into a stronger application story.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re


@dataclass
class CrisisResponse:
    """Complete crisis alchemy response."""
    crisis_type: str
    validation: str
    micro_action: str
    reframe: str
    pivot_activity: Dict[str, Any]
    transformation: Dict[str, str]
    full_response: str


class CrisisAlchemyModule:
    """Implements Jenny's 4-step Crisis Alchemy protocol."""

    CRISIS_PATTERNS: Dict[str, List[str]] = {
        "rejection": [
            "rejected", "didn't get", "wasn't accepted", "turned down",
            "not selected", "denied", "waitlisted"
        ],
        "exclusion": [
            "excluded", "left out", "not invited", "ignored", "kicked out",
            "removed", "banned"
        ],
        "creative_block": [
            "can't write", "stuck", "writer's block", "blank", "overwhelmed",
            "don't know what", "paralyzed"
        ],
        "comparison": [
            "compared to", "not as good as", "they have", "everyone else",
            "behind", "not enough", "inferior"
        ],
        "identity_attack": [
            "called me", "slur", "harassed", "bullied", "targeted",
            "discriminated", "stereotype"
        ],
        "failure": [
            "failed", "bombed", "messed up", "ruined", "disaster",
            "didn't work", "fell apart"
        ],
        "deadline": [
            "deadline", "due soon", "running out of time", "too late",
            "behind schedule", "won't finish"
        ]
    }

    TRANSFORMATION_PATTERNS: Dict[str, Dict[str, str]] = {
        "rejection": {
            "from": "Program rejection",
            "to": "Program founder"
        },
        "exclusion": {
            "from": "Victim of exclusion",
            "to": "Founder of inclusive space"
        },
        "creative_block": {
            "from": "Writer's block",
            "to": "Verbal fluency unlocked"
        },
        "comparison": {
            "from": "Comparison victim",
            "to": "Unique value recognizer"
        },
        "identity_attack": {
            "from": "Harassment victim",
            "to": "Culture transformer"
        },
        "failure": {
            "from": "Failure experience",
            "to": "Learning catalyst"
        },
        "deadline": {
            "from": "Deadline panic",
            "to": "Focused prioritization"
        }
    }

    RESPONSE_TEMPLATES: Dict[str, Dict[str, str]] = {
        "rejection": {
            "validation": "That rejection stings, especially after all the effort you put in. "
                         "It's completely valid to feel disappointed and doubt yourself right now.",
            "micro_action": "Right now, take 2 minutes to write down three specific things "
                           "you learned while preparing that application. Just bullet points.",
            "reframe": "The preparation you did isn't wasted - it's a foundation. And now "
                      "you have free time to create something even more impressive that YOU control.",
            "pivot_template": "What if instead of attending the program, you CREATE your own version? "
                            "Recruit 5 students, run 4 workshops, build something together."
        },
        "exclusion": {
            "validation": "That's absolutely terrible and definitely against school policy. "
                         "You have every right to feel betrayed.",
            "micro_action": "Talk to your leadership teacher on Monday about this. "
                           "They need to know what happened.",
            "reframe": "And honestly? I wouldn't want to be in a club with people who would do this. "
                      "This is a toxic environment.",
            "pivot_template": "What if instead of fighting to be part of something broken, "
                            "you created something better? Start a new club where YOU set the culture."
        },
        "creative_block": {
            "validation": "I can hear you have a real vision - the structure is just getting in the way. "
                         "The ideas are there.",
            "micro_action": "Let's forget about writing. Just talk to me. Tell me the story "
                           "like you're explaining it to a friend.",
            "reframe": "Your verbal clarity is amazing. Writing anxiety is blocking what you already know.",
            "pivot_template": "We're going to use TALK FIRST WRITE SECOND. "
                            "You talk, I'll help transcribe, then we polish together."
        },
        "comparison": {
            "validation": "I understand why that feels impressive from outside. "
                         "It's natural to compare yourself.",
            "micro_action": "Let's look at what YOU'VE actually built. Pull up your project stats.",
            "reframe": "They're doing generic work; you're creating something unique. "
                      "The specificity of what you've built beats generality.",
            "pivot_template": "Focus your energy on growing YOUR project, not chasing a narrative "
                            "that doesn't fit you. SPECIFICITY BEATS GENERALITY."
        },
        "identity_attack": {
            "validation": "That experience was real and painful. Being targeted for your identity "
                         "is harassment. Your feelings are valid.",
            "micro_action": "What happened AFTER that incident? What did you do next?",
            "reframe": "What if the attacker was your accidental cheerleader? "
                      "The one who pushed you to change the culture?",
            "pivot_template": "The story isn't 'I was harassed' - it's "
                            "'Harassment sparked my mission to transform the culture.'"
        },
        "failure": {
            "validation": "That's really tough. When something you've worked on doesn't work out, "
                         "it's okay to feel frustrated and disappointed.",
            "micro_action": "Take 2 minutes right now to write down ONE thing that did work, "
                           "even partially. What's one small win from this experience?",
            "reframe": "This failure just eliminated one path that doesn't work. "
                      "You now have information most people don't have.",
            "pivot_template": "What did this teach you that you can apply to version 2.0? "
                            "Every founder fails first - the question is what you build next."
        },
        "deadline": {
            "validation": "Deadline stress is real. The pressure you're feeling makes complete sense.",
            "micro_action": "Let's list everything that's due. Just dump it all out - "
                           "2 minutes, no judgment.",
            "reframe": "We can't do everything, and that's okay. Let's figure out what's "
                      "actually mission-critical vs nice-to-have.",
            "pivot_template": "Here's the plan: P0 tasks get done no matter what. "
                            "P1 gets done if possible. P2 gets cut. What's your P0?"
        }
    }

    PIVOT_ACTIVITIES: Dict[str, Dict[str, Any]] = {
        "rejection": {
            "name": "Create Your Own Program",
            "description": "Start {student_project} Summer Camp",
            "steps": [
                "Recruit 5 students",
                "Design 4 workshop sessions",
                "Build together",
                "Document everything"
            ],
            "impact": "Transforms 'rejected from program' into 'founded a program'",
            "time_to_start": "This week"
        },
        "exclusion": {
            "name": "Found Inclusive Alternative",
            "description": "Start an inclusive club",
            "steps": [
                "Find 3-5 like-minded students",
                "Draft constitution",
                "Get advisor",
                "Host first meeting"
            ],
            "impact": "Transforms 'excluded' into 'founder of inclusive space'",
            "time_to_start": "Next week"
        },
        "creative_block": {
            "name": "Talk First Write Second Session",
            "description": "Voice memo to draft conversion",
            "steps": [
                "Record yourself for 5 minutes",
                "Transcribe key points",
                "Organize",
                "Polish"
            ],
            "impact": "Bypass writing anxiety entirely",
            "time_to_start": "Right now"
        },
        "comparison": {
            "name": "Double Down on Your Unique Value",
            "description": "Scale {student_project}",
            "steps": [
                "Set 10x goal",
                "Identify one lever",
                "Document progress",
                "Ignore comparisons"
            ],
            "impact": "SPECIFICITY BEATS GENERALITY",
            "time_to_start": "Today"
        },
        "identity_attack": {
            "name": "Transform Harm into Mission",
            "description": "Build spaces that prevent what happened to you",
            "steps": [
                "Document experience",
                "Identify needed change",
                "Create project/club",
                "Become the mentor you needed"
            ],
            "impact": "Transforms 'victim of harassment' into 'culture transformer'",
            "time_to_start": "This month"
        },
        "failure": {
            "name": "Build Version 2.0",
            "description": "Apply learnings to improved approach",
            "steps": [
                "Document what went wrong",
                "Identify root cause",
                "Design improvements",
                "Start small test"
            ],
            "impact": "Transforms failure into iteration",
            "time_to_start": "After processing"
        },
        "deadline": {
            "name": "Strategic Triage",
            "description": "Focus only on what matters most",
            "steps": [
                "List all tasks",
                "Categorize P0/P1/P2",
                "Cut P2 entirely",
                "Execute P0 first"
            ],
            "impact": "Replace panic with clarity",
            "time_to_start": "Right now"
        }
    }

    def detect_crisis_type(self, description: str) -> str:
        """Detect crisis type from description."""
        description_lower = description.lower()
        for crisis_type, patterns in self.CRISIS_PATTERNS.items():
            if any(pattern in description_lower for pattern in patterns):
                return crisis_type
        return "general"

    def generate_response(
        self,
        crisis_type: str,
        description: str,
        student: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> CrisisResponse:
        """Generate complete crisis alchemy response."""
        context = context or {}

        # Get template or use rejection as default
        template = self.RESPONSE_TEMPLATES.get(
            crisis_type, self.RESPONSE_TEMPLATES["rejection"]
        )

        validation = template["validation"]
        micro_action = template["micro_action"]
        reframe = self._fill_template(template["reframe"], context, student)
        pivot_text = self._fill_template(template["pivot_template"], context, student)

        pivot_activity = self._generate_pivot_activity(crisis_type, student, context)
        transformation = self.TRANSFORMATION_PATTERNS.get(
            crisis_type, {"from": "Setback", "to": "Growth opportunity"}
        )

        full_response = f"""{validation}

{micro_action}

{reframe}

{pivot_text}

How does that sound?"""

        return CrisisResponse(
            crisis_type=crisis_type,
            validation=validation,
            micro_action=micro_action,
            reframe=reframe,
            pivot_activity=pivot_activity,
            transformation=transformation,
            full_response=full_response
        )

    def _fill_template(
        self,
        template: str,
        context: Dict[str, Any],
        student: Dict[str, Any]
    ) -> str:
        """Fill template with context and student info."""
        result = template

        # Fill context variables
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", str(value))

        # Fill student variables
        student_vars = {
            "student_project": student.get("primary_project", "your project"),
            "student_spike": student.get("spike", "your focus area"),
            "student_name": student.get("name", "you")
        }
        for key, value in student_vars.items():
            result = result.replace(f"{{{key}}}", str(value))

        # Remove any unfilled placeholders
        result = re.sub(r'\{[^}]+\}', '', result)

        return result

    def _generate_pivot_activity(
        self,
        crisis_type: str,
        student: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate specific pivot activity."""
        pivot = self.PIVOT_ACTIVITIES.get(crisis_type, {
            "name": "Find the Learning",
            "description": "Extract value from the experience",
            "steps": ["Write what happened", "Identify lesson", "Move forward"],
            "impact": "Growth mindset activation",
            "time_to_start": "When ready"
        })

        # Customize description with student info
        if "{student_project}" in pivot.get("description", ""):
            pivot = dict(pivot)
            pivot["description"] = pivot["description"].replace(
                "{student_project}",
                student.get("primary_project", "your project")
            )

        return pivot

    def format_crisis_response(self, response: CrisisResponse) -> str:
        """Format crisis response for display."""
        lines = [
            "**Step 1: VALIDATE** (2 seconds)",
            response.validation,
            "",
            "**Step 2: ACT** (2 minutes)",
            response.micro_action,
            "",
            "**Step 3: REFRAME** (30 seconds)",
            response.reframe,
            "",
            "**Step 4: CREATE** (2 minutes)",
            f"**{response.pivot_activity.get('name', 'Next Step')}**",
            response.pivot_activity.get('description', ''),
            "",
            "Steps:",
        ]

        for step in response.pivot_activity.get('steps', []):
            lines.append(f"  - {step}")

        lines.extend([
            "",
            f"**Transformation:** {response.transformation['from']} → {response.transformation['to']}",
            "",
            "How does that sound?"
        ])

        return "\n".join(lines)

    def to_dict(self, response: CrisisResponse) -> Dict[str, Any]:
        """Convert CrisisResponse to dictionary for API."""
        return {
            "crisis_type": response.crisis_type,
            "validation": response.validation,
            "micro_action": response.micro_action,
            "reframe": response.reframe,
            "pivot_activity": response.pivot_activity,
            "transformation": response.transformation,
            "full_response": response.full_response,
        }


__all__ = ['CrisisAlchemyModule', 'CrisisResponse']
