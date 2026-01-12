# Micro-Edit Mastery - ACP-008 Implementation
# File: agents/tools/micro_edits.py
#
# Language pattern replacements for essays and application materials
# "avoid" → "prioritize", "can't afford" → "family investment priorities"

from typing import Dict, List, Tuple
import re


# Micro-edit pattern library
# Format: (pattern, replacement, category, explanation)
MICRO_EDIT_PATTERNS: List[Tuple[str, str, str, str]] = [
    # Limiting language → Empowering language
    (r"\bcan't afford\b", "family investment priorities led us to", "financial", 
     "Reframes financial constraints as deliberate family choices"),
    
    (r"\bcouldn't afford\b", "prioritized other investments over", "financial",
     "Shifts from inability to strategic choice"),
    
    (r"\bpoor\b(?!\s+performance)", "resource-conscious", "financial",
     "Removes negative connotation while maintaining authenticity"),
    
    (r"\bno money\b", "limited resources", "financial",
     "Professional framing of financial situation"),
    
    # Negative framing → Positive framing
    (r"\bavoid\b", "prioritize alternatives to", "framing",
     "Shifts from avoidance to positive action"),
    
    (r"\bfailed\b", "learned from the experience of", "framing",
     "Growth mindset reframe"),
    
    (r"\bdidn't have\b", "sought creative alternatives to", "framing",
     "Shows resourcefulness"),
    
    (r"\bstruggles?\b", "navigates challenges in", "framing",
     "Active voice, shows agency"),
    
    (r"\bweak(?:ness)?\b", "area for growth", "framing",
     "Growth-oriented language"),
    
    (r"\bproblem\b", "opportunity for improvement", "framing",
     "Positive reframe"),
    
    # Passive → Active voice
    (r"\bwas given\b", "earned", "voice",
     "Shows agency and achievement"),
    
    (r"\bwas told\b", "learned", "voice",
     "Active learning stance"),
    
    (r"\bwas forced to\b", "chose to adapt by", "voice",
     "Demonstrates adaptability"),
    
    (r"\bhad to\b", "chose to", "voice",
     "Shows intentional decision-making"),
    
    # Undermining → Confident language
    (r"\bjust\b(?=\s+a)", "", "confidence",
     "Removes minimizing qualifier"),
    
    (r"\bonly\b(?=\s+\w+ed)", "", "confidence",
     "Removes achievement minimization"),
    
    (r"\bI think\b", "I believe", "confidence",
     "More confident stance"),
    
    (r"\bmaybe\b", "potentially", "confidence",
     "More professional uncertainty"),
    
    (r"\bkind of\b", "", "confidence",
     "Removes hedging"),
    
    (r"\bsort of\b", "", "confidence",
     "Removes hedging"),
    
    # Immigrant/First-gen experience reframes
    (r"\bimmigrant family\b", "family with international roots", "background",
     "Frames heritage as asset"),
    
    (r"\bdidn't speak English\b", "navigated multilingual environments", "background",
     "Highlights linguistic ability"),
    
    (r"\bforeign\b", "international", "background",
     "More positive framing"),
    
    (r"\bnon-native\b", "multilingual", "background",
     "Highlights skill rather than deficit"),
    
    # Work/Family responsibility reframes
    (r"\bhad to work\b", "contributed to family through work", "responsibility",
     "Frames work as contribution, not burden"),
    
    (r"\bhelp(?:ing)? (?:my )?parents\b", "supporting my family", "responsibility",
     "Shows maturity and responsibility"),
    
    (r"\btake care of\b", "provide support for", "responsibility",
     "Professional framing"),
    
    # Education barriers → Opportunities
    (r"\bunder-resourced school\b", "school where I learned to be resourceful", "education",
     "Highlights developed skill"),
    
    (r"\bbad school\b", "school with unique challenges", "education",
     "Neutral framing"),
    
    (r"\bdidn't offer\b", "inspired me to seek out", "education",
     "Shows initiative"),
    
    # Time constraints → Time management
    (r"\bno time\b", "learned to prioritize", "time",
     "Shows skill development"),
    
    (r"\btoo busy\b", "managed multiple commitments", "time",
     "Highlights capability"),
    
    # Health/Disability reframes
    (r"\bdespite my\b", "alongside my experience with", "health",
     "Removes adversarial framing"),
    
    (r"\bsuffer(?:ing)? from\b", "managing", "health",
     "Active, non-victim framing"),
]


def apply_micro_edits(text: str, return_details: bool = False) -> Dict:
    """
    Apply micro-edit patterns to text
    
    Args:
        text: Original text to edit
        return_details: If True, include detailed change information
    
    Returns:
        {
            "original": str,
            "edited": str,
            "changes": List[Dict],  # If return_details=True
            "change_count": int,
            "categories_affected": List[str]
        }
    """
    if not text:
        return {
            "original": "",
            "edited": "",
            "change_count": 0,
            "categories_affected": []
        }
    
    edited = text
    changes = []
    categories = set()
    
    for pattern, replacement, category, explanation in MICRO_EDIT_PATTERNS:
        # Find all matches before replacing
        matches = list(re.finditer(pattern, edited, re.IGNORECASE))
        
        if matches:
            for match in matches:
                original_text = match.group()
                
                # Preserve case of first letter
                if original_text[0].isupper() and replacement:
                    final_replacement = replacement[0].upper() + replacement[1:]
                else:
                    final_replacement = replacement
                
                changes.append({
                    "original": original_text,
                    "replacement": final_replacement if final_replacement else "(removed)",
                    "category": category,
                    "explanation": explanation,
                    "position": match.start()
                })
                categories.add(category)
            
            # Apply replacement
            edited = re.sub(pattern, replacement, edited, flags=re.IGNORECASE)
    
    # Clean up double spaces from removals
    edited = re.sub(r'\s+', ' ', edited).strip()
    
    result = {
        "original": text,
        "edited": edited,
        "change_count": len(changes),
        "categories_affected": list(categories)
    }
    
    if return_details:
        result["changes"] = changes
    
    return result


def get_micro_edit_suggestions(text: str) -> List[Dict]:
    """
    Get suggestions without applying them
    Useful for UI to show potential edits
    """
    if not text:
        return []
    
    suggestions = []
    
    for pattern, replacement, category, explanation in MICRO_EDIT_PATTERNS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        for match in matches:
            original_text = match.group()
            
            # Build context (20 chars before and after)
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end]
            
            suggestions.append({
                "original_phrase": original_text,
                "suggested_replacement": replacement if replacement else "(remove)",
                "category": category,
                "explanation": explanation,
                "context": f"...{context}...",
                "position": {
                    "start": match.start(),
                    "end": match.end()
                },
                "impact": "high" if category in ["financial", "framing", "voice"] else "medium"
            })
    
    return suggestions


def analyze_essay_language(text: str) -> Dict:
    """
    Analyze essay for language patterns and provide summary
    """
    if not text:
        return {"word_count": 0, "issues": [], "score": 100}
    
    result = apply_micro_edits(text, return_details=True)
    
    # Count issues by category
    category_counts = {}
    for change in result.get("changes", []):
        cat = change["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Calculate language score (100 = no issues)
    total_issues = result["change_count"]
    word_count = len(text.split())
    
    # Score based on issue density
    if word_count > 0:
        issue_rate = total_issues / word_count
        score = max(0, int(100 - (issue_rate * 1000)))  # Lose 1 point per issue per 100 words
    else:
        score = 100
    
    return {
        "word_count": word_count,
        "total_issues": total_issues,
        "issues_by_category": category_counts,
        "language_score": score,
        "recommendations": _generate_recommendations(category_counts),
        "can_improve": total_issues > 0,
        "sample_changes": result.get("changes", [])[:3]  # Top 3 examples
    }


def _generate_recommendations(category_counts: Dict) -> List[str]:
    """Generate recommendations based on issue categories"""
    recommendations = []
    
    if category_counts.get("financial", 0) > 0:
        recommendations.append(
            "Reframe financial constraints as family values and choices rather than limitations"
        )
    
    if category_counts.get("framing", 0) > 0:
        recommendations.append(
            "Shift from problem-focused to solution-focused language throughout"
        )
    
    if category_counts.get("voice", 0) > 0:
        recommendations.append(
            "Use active voice to demonstrate agency and ownership of your experiences"
        )
    
    if category_counts.get("confidence", 0) > 0:
        recommendations.append(
            "Remove hedging words and qualifiers that undermine your achievements"
        )
    
    if category_counts.get("background", 0) > 0:
        recommendations.append(
            "Present your cultural/immigrant background as a source of strength and unique perspective"
        )
    
    if not recommendations:
        recommendations.append("Your language is strong - focus on content and narrative flow")
    
    return recommendations


# Additional essay-specific patterns for different essay types
COMMON_APP_PATTERNS = [
    # Growth patterns for "challenge" essays
    (r"\bit was hard\b", "I grew through the challenge of", "growth",
     "Shows growth mindset"),
    
    (r"\bI overcame\b", "I developed resilience through", "growth",
     "Focuses on skill development"),
]


SUPPLEMENTAL_PATTERNS = [
    # "Why us" essay patterns
    (r"\bI want to go\b", "I am drawn to", "interest",
     "Shows genuine interest rather than desire"),
    
    (r"\bI would love\b", "I am excited to", "interest",
     "More confident expression"),
]


def apply_essay_specific_edits(text: str, essay_type: str = "common_app") -> Dict:
    """
    Apply essay-type specific edits in addition to base patterns
    
    Args:
        text: Original text
        essay_type: "common_app", "supplemental", "activities"
    
    Returns:
        Edited result with essay-specific changes
    """
    # First apply base edits
    result = apply_micro_edits(text, return_details=True)
    
    # Then apply essay-specific patterns
    edited = result["edited"]
    additional_changes = []
    
    patterns = []
    if essay_type == "common_app":
        patterns = COMMON_APP_PATTERNS
    elif essay_type == "supplemental":
        patterns = SUPPLEMENTAL_PATTERNS
    
    for pattern, replacement, category, explanation in patterns:
        matches = list(re.finditer(pattern, edited, re.IGNORECASE))
        
        if matches:
            for match in matches:
                additional_changes.append({
                    "original": match.group(),
                    "replacement": replacement,
                    "category": category,
                    "explanation": explanation
                })
            
            edited = re.sub(pattern, replacement, edited, flags=re.IGNORECASE)
    
    result["edited"] = edited
    result["change_count"] += len(additional_changes)
    if "changes" in result:
        result["changes"].extend(additional_changes)
    
    return result


# Export functions
__all__ = [
    "apply_micro_edits",
    "get_micro_edit_suggestions",
    "analyze_essay_language",
    "apply_essay_specific_edits",
    "MICRO_EDIT_PATTERNS"
]
