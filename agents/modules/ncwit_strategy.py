"""
NCWIT Strategy Module
Specialized coaching for NCWIT Aspirations in Computing applications.

Core Insights:
- Focus on "tenacity in face of barriers to access"
- Vulnerability Formula: Background + Barrier + Persistence = Compelling
- Identity Multiplication: Layer ALL identity markers
- "Make them FEEL your story, not just understand it"
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class NCWITStrategy:
    """Complete NCWIT application strategy."""
    identity_layers: List[str]
    identity_multiplier_text: str
    vulnerability_angles: List[str]
    sensory_detail_suggestions: List[str]
    jenny_coaching_script: str
    essay_structure: Dict[str, Any]


class NCWITStrategyModule:
    """Specialized coaching for NCWIT Aspirations applications."""

    VULNERABILITY_FORMULA = "Background + Barrier + Persistence = Compelling Story"

    IDENTITY_MARKERS: List[str] = [
        "female", "woman", "muslim", "religious minority", "first-generation",
        "low-income", "immigrant", "new to community", "rural",
        "non-native english speaker", "person of color", "underrepresented minority",
        "lgbtq+", "disabled", "neurodivergent"
    ]

    SENSORY_PROMPTS: List[str] = [
        "Describe the moment you realized you were the only [identity] in the room",
        "What did it feel like when your idea was dismissed or stolen?",
        "Capture the physical sensation of isolation at your first hackathon",
        "Describe the exact moment you decided to persist anyway",
        "What does it feel like to code when no one believes you can?"
    ]

    ESSAY_STRUCTURE: Dict[str, Any] = {
        "question_1": {
            "prompt": "What sparked your interest in computing?",
            "word_limit": 500,
            "strategy": "Start with a specific moment, not 'I've always loved...'",
            "structure": [
                "Hook: Specific sensory moment that sparked interest",
                "Context: Your identity and background",
                "Barrier: What made this harder for you",
                "Persistence: How you overcame/worked through it",
                "Vision: Where this passion is taking you"
            ]
        },
        "question_2": {
            "prompt": "What have you been doing with technology?",
            "word_limit": 500,
            "strategy": "Focus on impact and scale, not just activities",
            "structure": [
                "Project/Activity with clear impact metrics",
                "Your unique role and contribution",
                "Challenges faced and overcome",
                "Growth and learning",
                "Future plans and vision"
            ]
        }
    }

    TRANSFORMATION_EXAMPLES: List[Dict[str, str]] = [
        {
            "before": "I was often the only girl in my CS classes",
            "after": "I counted the chairs before each CS class started - 24 seats, "
                    "23 taken by boys, and mine in the corner where I could code "
                    "without being watched.",
            "technique": "Sensory detail transforms generic statement into felt experience"
        },
        {
            "before": "I faced discrimination in tech",
            "after": "When the hackathon judge asked who actually wrote the code - "
                    "looking at my male teammate, not me - I felt my stomach drop. "
                    "My fingers were still raw from typing for 36 hours.",
            "technique": "Physical sensation + specific moment + contrast"
        }
    ]

    def generate_strategy(self, student: Dict[str, Any]) -> NCWITStrategy:
        """Generate personalized NCWIT strategy."""
        identity_layers = self._identify_layers(student)
        identity_text = self._format_identity_text(identity_layers)
        vulnerability_angles = self._identify_vulnerability_angles(student)
        sensory_suggestions = self._customize_sensory_prompts(student, identity_layers)
        coaching_script = self._generate_coaching_script(
            student, identity_layers, vulnerability_angles
        )

        return NCWITStrategy(
            identity_layers=identity_layers,
            identity_multiplier_text=identity_text,
            vulnerability_angles=vulnerability_angles,
            sensory_detail_suggestions=sensory_suggestions,
            jenny_coaching_script=coaching_script,
            essay_structure=self.ESSAY_STRUCTURE
        )

    def _identify_layers(self, student: Dict[str, Any]) -> List[str]:
        """Identify all applicable identity layers."""
        layers: List[str] = []
        student_identity = [i.lower() for i in student.get("identity", [])]
        identity_text = " ".join(student_identity)

        for marker in self.IDENTITY_MARKERS:
            if marker in identity_text:
                layers.append(marker)

        # Check specific fields
        if student.get("is_first_gen") and "first-generation" not in layers:
            layers.append("first-generation college student")
        if student.get("is_new_to_school"):
            layers.append("new to school/community")
        if student.get("is_immigrant"):
            layers.append("immigrant background")

        # Ensure "woman in CS" is included for NCWIT
        if not any(g in layers for g in ["female", "woman"]):
            layers.insert(0, "woman in CS")

        return layers

    def _format_identity_text(self, layers: List[str]) -> str:
        """Format identity layers into compelling text."""
        if len(layers) <= 1:
            return "a woman in CS"

        formatted = " ".join(layers[:3])
        comparison = self._get_rarity_comparison(layers)
        return f"a {formatted} - {comparison}"

    def _get_rarity_comparison(self, layers: List[str]) -> str:
        """Generate rarity comparison for identity multiplication."""
        layer_count = len(layers)
        if layer_count >= 4:
            return "that combination is incredibly rare in tech"
        elif layer_count >= 3:
            return "even more underrepresented than women CEOs"
        elif layer_count >= 2:
            return "a combination few in CS share"
        return "underrepresented in the field"

    def _identify_vulnerability_angles(self, student: Dict[str, Any]) -> List[str]:
        """Identify potential vulnerability angles for essays."""
        angles: List[str] = []
        experiences = student.get("experiences", [])
        experiences_text = " ".join(str(e) for e in experiences).lower()

        barrier_keywords = {
            "isolation": ["alone", "only one", "isolated", "excluded", "lonely"],
            "dismissal": ["dismissed", "ignored", "stolen", "credited", "overlooked"],
            "exclusion": ["excluded", "left out", "not invited", "rejected", "unwelcome"],
            "doubt": ["doubted", "questioned", "underestimated", "stereotyped"],
            "harassment": ["harassed", "bullied", "targeted", "attacked"]
        }

        for barrier, keywords in barrier_keywords.items():
            if any(kw in experiences_text for kw in keywords):
                angles.append(f"Experience with {barrier}")

        # Add default angles if none found
        if not angles:
            angles = [
                "Being underrepresented in CS spaces",
                "Navigating male-dominated environments",
                "Finding your voice in tech"
            ]

        return angles

    def _customize_sensory_prompts(
        self,
        student: Dict[str, Any],
        identity_layers: List[str]
    ) -> List[str]:
        """Customize sensory prompts for student's situation."""
        prompts: List[str] = []
        primary_identity = identity_layers[0] if identity_layers else "you"

        prompts.append(
            f"Describe the moment you realized you were the only {primary_identity} in the room"
        )
        prompts.append(
            "What did it feel like in your body when someone assumed you couldn't code?"
        )
        prompts.append(
            "Describe the exact moment you decided to persist despite [barrier]"
        )
        prompts.append(
            "What does success feel like now that you've proven them wrong?"
        )

        return prompts

    def _generate_coaching_script(
        self,
        student: Dict[str, Any],
        identity_layers: List[str],
        vulnerability_angles: List[str]
    ) -> str:
        """Generate Jenny-style coaching script for NCWIT."""
        identity_chain = ", ".join(identity_layers[:3])
        angle_suggestions = "\n".join(f"- {a}" for a in vulnerability_angles[:3])

        return f"""Your story isn't cliche - you're just not telling it with enough vulnerability yet!

Let's layer your unique identity markers: You're not just a girl in CS, you're {identity_chain}. That combination is incredibly rare and powerful.

Each layer reduces your competition pool. There are thousands of girls applying to NCWIT, but how many are {identity_chain}? You're competing against a much smaller group!

**Vulnerability angles we can explore:**
{angle_suggestions}

Now, the key technique: **Make them FEEL your experience, not just understand it.**

Instead of: "I was often the only girl in my CS classes"
Write: "I counted the chairs before each CS class started - 24 seats, 23 taken by boys, and mine in the corner where I could code without being watched."

That sensory detail - counting chairs, the corner seat - makes readers FEEL your isolation.

**{self.VULNERABILITY_FORMULA}**

Your background gives you unique perspective. The barriers you faced show tenacity. Your persistence despite everything is exactly what NCWIT wants to see.

Does that shift how you see your story? What specific moment stands out to you?"""

    def get_transformation_examples(self) -> List[Dict[str, str]]:
        """Return examples of transforming generic statements to sensory ones."""
        return self.TRANSFORMATION_EXAMPLES

    def format_essay_structure(self, question_num: int = 1) -> str:
        """Format essay structure guidance."""
        key = f"question_{question_num}"
        structure = self.ESSAY_STRUCTURE.get(key, self.ESSAY_STRUCTURE["question_1"])

        lines = [f"**{structure['prompt']}** ({structure['word_limit']} words)\n"]
        lines.append(f"Strategy: {structure['strategy']}\n")
        lines.append("Structure:")
        for i, point in enumerate(structure['structure'], 1):
            lines.append(f"  {i}. {point}")

        return "\n".join(lines)

    def to_dict(self, strategy: NCWITStrategy) -> Dict[str, Any]:
        """Convert NCWITStrategy to dictionary for API."""
        return {
            "identity_layers": strategy.identity_layers,
            "identity_multiplier_text": strategy.identity_multiplier_text,
            "vulnerability_angles": strategy.vulnerability_angles,
            "sensory_detail_suggestions": strategy.sensory_detail_suggestions,
            "jenny_coaching_script": strategy.jenny_coaching_script,
            "essay_structure": strategy.essay_structure,
            "vulnerability_formula": self.VULNERABILITY_FORMULA,
        }


__all__ = ['NCWITStrategyModule', 'NCWITStrategy']
