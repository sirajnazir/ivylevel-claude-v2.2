"""
Program Redirect Module
Implements Jenny's "Just Be One" philosophy for expensive programs.

Core Principle: "If you want to be an entrepreneur, just be one.
Don't pay $8000 to learn how to have an idea."

Trigger: Program cost >= $5000
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class RedirectResponse:
    """Response for expensive program redirect."""
    should_redirect: bool
    program_name: str
    program_cost: int
    redirect_text: str
    free_alternatives: List[str]
    self_directed_option: str
    jenny_quote: str


class ProgramRedirectModule:
    """Implements Jenny's expensive program redirect logic."""

    COST_THRESHOLD = 5000

    REDIRECT_TEMPLATE = """If you want to be {teaches}, just be one! Don't pay ${cost:,} to learn how to have an idea - you already have ideas!

Use that {duration} for YOUR projects. What could you build with ${cost:,} and {duration}? That's {student_project} 2.0, a documentary series, an app with 10,000 users.

The program teaches you to be {teaches}; actually building something MAKES you one.

Consider these free alternatives instead:
{alternatives_formatted}

Or just spend the {duration} scaling your existing projects. {self_directed}

What sounds most exciting to you?"""

    FREE_ALTERNATIVES: Dict[str, List[str]] = {
        "entrepreneurship": [
            "Bank of America Student Leaders (they PAY you!)",
            "Start your own business instead",
            "DECA competitions (free entry)",
            "Network for Teaching Entrepreneurship (NFTE)"
        ],
        "cs": [
            "Kode with Klossy (free, 2 weeks)",
            "Girls Who Code Summer Immersion",
            "Google CSSI (free)",
            "AI4ALL (free)",
            "Code.org summer programs"
        ],
        "leadership": [
            "Notre Dame Leadership Seminars (free, 3 weeks)",
            "Bank of America Student Leaders",
            "Hugh O'Brien Youth Leadership (HOBY)",
            "Rotary Youth Leadership Awards (RYLA)"
        ],
        "stem": [
            "Research Science Institute (RSI) - free, highly selective",
            "MITES at MIT (free)",
            "Clark Scholars Program (free)",
            "Garcia Research Scholars (free)"
        ],
        "business": [
            "Knowledge at Wharton HS",
            "Booth School Business Programs",
            "Local startup incubators",
            "FBLA competitions"
        ],
        "general": [
            "Bank of America Student Leaders (paid!)",
            "Questbridge programs",
            "TASP (free, selective)",
            "Local community programs"
        ]
    }

    SELF_DIRECTED_SUGGESTIONS: Dict[str, str] = {
        "cs": "Publish your app on the App Store / Google Play and get 1000 users",
        "entrepreneurship": "Launch your business and get your first 100 customers",
        "film": "Create a documentary series and submit to 5 film festivals",
        "research": "Conduct independent research and submit to a journal",
        "leadership": "Start a community initiative that impacts 100+ people",
        "default": "Scale your existing project to 10x its current impact"
    }

    JENNY_NOTES: Dict[str, str] = {
        "kode_with_klossy": "I've done it twice, it's amazing for women in CS",
        "notre_dame_leadership": "I've done it before, pretty cool residential program",
        "rsi": "Most selective program in the country, but completely free",
        "bank_of_america": "They literally pay you AND it looks great on applications"
    }

    def should_redirect(self, program: Dict[str, Any]) -> bool:
        """Check if program should trigger redirect."""
        cost = program.get("cost_numeric", 0)
        if cost >= self.COST_THRESHOLD:
            return True

        # Also check string cost format
        cost_str = program.get("cost", "").lower()
        if any(f"${x}" in cost_str for x in range(5, 20)):  # $5k - $19k
            return True

        return program.get("redirect_trigger", False)

    def generate_redirect(
        self,
        program: Dict[str, Any],
        student: Dict[str, Any]
    ) -> RedirectResponse:
        """Generate Jenny-style redirect response for expensive program."""
        if not self.should_redirect(program):
            return RedirectResponse(
                should_redirect=False,
                program_name=program.get("name", ""),
                program_cost=program.get("cost_numeric", 0),
                redirect_text="",
                free_alternatives=[],
                self_directed_option="",
                jenny_quote=""
            )

        category = program.get("category", "general").lower()
        alternatives = self.FREE_ALTERNATIVES.get(
            category, self.FREE_ALTERNATIVES["general"]
        )

        spike = student.get("spike", "").lower()
        self_directed = self._get_self_directed(spike)

        alternatives_formatted = "\n".join(f"- {a}" for a in alternatives[:4])
        teaches = self._get_teaches(category)

        redirect_text = self.REDIRECT_TEMPLATE.format(
            teaches=teaches,
            cost=program.get("cost_numeric", self.COST_THRESHOLD),
            duration=program.get("duration", "4 weeks"),
            student_project=student.get("primary_project", "your project"),
            alternatives_formatted=alternatives_formatted,
            self_directed=self_directed
        )

        jenny_quote = (
            f"The program teaches you to be {teaches}; "
            "actually building something MAKES you one."
        )

        return RedirectResponse(
            should_redirect=True,
            program_name=program.get("name", ""),
            program_cost=program.get("cost_numeric", self.COST_THRESHOLD),
            redirect_text=redirect_text,
            free_alternatives=alternatives,
            self_directed_option=self_directed,
            jenny_quote=jenny_quote
        )

    def _get_self_directed(self, spike: str) -> str:
        """Get self-directed suggestion based on spike."""
        for key, suggestion in self.SELF_DIRECTED_SUGGESTIONS.items():
            if key in spike:
                return suggestion
        return self.SELF_DIRECTED_SUGGESTIONS["default"]

    def _get_teaches(self, category: str) -> str:
        """Get what the program category teaches."""
        teaches_map = {
            "entrepreneurship": "an entrepreneur",
            "cs": "a programmer",
            "leadership": "a leader",
            "business": "a business person",
            "stem": "a researcher",
            "film": "a filmmaker",
            "research": "a researcher"
        }
        return teaches_map.get(category, "an expert")

    def get_tier_recommendations(
        self,
        student: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get tiered program recommendations."""
        spike = student.get("spike", "").lower()

        recommendations: Dict[str, List[Dict[str, Any]]] = {
            "tier_1_selective_free": [],
            "tier_2_government": [],
            "tier_3_technical": [],
            "tier_4_redirect": []
        }

        # Tier 1: Highly selective free programs
        if "cs" in spike or "coding" in spike or "tech" in spike:
            recommendations["tier_1_selective_free"].extend([
                {
                    "name": "Kode with Klossy",
                    "fit": "CS + Women",
                    "jenny_note": self.JENNY_NOTES.get("kode_with_klossy")
                },
                {
                    "name": "Google CSSI",
                    "fit": "CS",
                    "jenny_note": "Very selective but great"
                },
                {
                    "name": "AI4ALL",
                    "fit": "AI/ML focus",
                    "jenny_note": "Great for underrepresented students in AI"
                }
            ])

        if "research" in spike or "science" in spike:
            recommendations["tier_1_selective_free"].extend([
                {
                    "name": "Research Science Institute (RSI)",
                    "fit": "Research-focused",
                    "jenny_note": self.JENNY_NOTES.get("rsi")
                },
                {
                    "name": "Clark Scholars Program",
                    "fit": "Research",
                    "jenny_note": "Free with stipend"
                }
            ])

        # Universal Tier 1 programs
        recommendations["tier_1_selective_free"].extend([
            {
                "name": "Bank of America Student Leaders",
                "fit": "Leadership + Service",
                "jenny_note": self.JENNY_NOTES.get("bank_of_america")
            },
            {
                "name": "Notre Dame Leadership Seminars",
                "fit": "Leadership",
                "jenny_note": self.JENNY_NOTES.get("notre_dame_leadership")
            }
        ])

        # Tier 2: Government-funded
        recommendations["tier_2_government"].extend([
            {
                "name": "NSLI-Y",
                "fit": "Language learning abroad",
                "jenny_note": "Full scholarship"
            },
            {
                "name": "Congress-Bundestag Youth Exchange",
                "fit": "German language/culture",
                "jenny_note": "Full year abroad, free"
            }
        ])

        # Tier 3: Technical/specialized
        if "cs" in spike:
            recommendations["tier_3_technical"].extend([
                {
                    "name": "Local hackathons",
                    "fit": "CS",
                    "jenny_note": "Free and builds portfolio"
                }
            ])

        return recommendations

    def format_alternatives(
        self,
        response: RedirectResponse,
        jenny_notes: bool = True
    ) -> str:
        """Format alternatives list with optional Jenny notes."""
        lines = ["**Free Alternatives:**\n"]

        for alt in response.free_alternatives:
            line = f"- {alt}"
            if jenny_notes:
                # Look up note by keyword
                for keyword, note in self.JENNY_NOTES.items():
                    if keyword.replace("_", " ") in alt.lower():
                        line += f" _{note}_"
                        break
            lines.append(line)

        lines.append(f"\n**Self-Directed Option:**\n{response.self_directed_option}")

        return "\n".join(lines)

    def to_dict(self, response: RedirectResponse) -> Dict[str, Any]:
        """Convert RedirectResponse to dictionary for API."""
        return {
            "should_redirect": response.should_redirect,
            "program_name": response.program_name,
            "program_cost": response.program_cost,
            "redirect_text": response.redirect_text,
            "free_alternatives": response.free_alternatives,
            "self_directed_option": response.self_directed_option,
            "jenny_quote": response.jenny_quote,
        }


__all__ = ['ProgramRedirectModule', 'RedirectResponse']
