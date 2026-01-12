"""
IvyQuest v10.0 - Narrative Evaluation Rubric
============================================

Rubric for evaluating NarrativeSynthesisAgent outputs.
Based on Jenny Duan's coaching methodology.
"""

# Dimension weights (must sum to 1.0)
NARRATIVE_WEIGHTS = {
    'authenticity': 0.25,
    'identity_integration': 0.25,
    'narrative_power': 0.20,
    'jenny_alignment': 0.15,
    'actionability': 0.15,
}

# Full rubric definitions
NARRATIVE_RUBRIC = {
    'authenticity': {
        'name': 'Authenticity',
        'description': 'How personal and specific is the narrative to this student?',
        'weight': 0.25,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Deeply personal, specific details, could only be about this student',
                'indicators': [
                    'Uses specific names, places, projects unique to student',
                    'Reflects genuine voice and perspective',
                    'Contains details that cannot be generic',
                    'Evokes emotional resonance',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Personal with some unique elements',
                'indicators': [
                    'Contains several specific details',
                    'Voice is mostly authentic',
                    'Some generic elements but core is personal',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Somewhat personal but has generic elements',
                'indicators': [
                    'Mix of specific and generic content',
                    'Could apply to students with similar backgrounds',
                    'Lacks distinctive voice',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Mostly generic with few personal touches',
                'indicators': [
                    'Relies on category descriptors (e.g., "STEM student")',
                    'Minimal specific details',
                    'Template-like feel',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Could apply to many students, lacks specificity',
                'indicators': [
                    'Entirely generic phrases',
                    'No personal details',
                    'Reads like a template',
                ]
            },
        }
    },
    'identity_integration': {
        'name': 'Identity Integration',
        'description': 'How well does the narrative integrate all identity elements?',
        'weight': 0.25,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Seamlessly integrates all identity elements into cohesive story',
                'indicators': [
                    'Cultural background woven naturally into narrative',
                    'All identity aspects complement each other',
                    'Creates unified, powerful identity statement',
                    'Identity elements enhance rather than distract',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Integrates most elements well',
                'indicators': [
                    'Most identity elements present and connected',
                    'Minor gaps in integration',
                    'Overall cohesive narrative',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Mentions elements but doesn\'t fully connect them',
                'indicators': [
                    'Identity elements listed but not synthesized',
                    'Some disconnection between aspects',
                    'Reads like checklist of attributes',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Misses some key elements',
                'indicators': [
                    'Important identity aspects omitted',
                    'Incomplete picture of student',
                    'Forced or awkward connections',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Misses or misrepresents major identity elements',
                'indicators': [
                    'Critical identity aspects ignored',
                    'Factual errors about student',
                    'Contradicts provided information',
                ]
            },
        }
    },
    'narrative_power': {
        'name': 'Narrative Power',
        'description': 'How compelling and memorable is the narrative?',
        'weight': 0.20,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Would immediately stand out to admissions officers',
                'indicators': [
                    'Memorable opening/hook',
                    'Clear, compelling arc',
                    'Emotionally resonant',
                    'Distinct from typical applications',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Strong and memorable',
                'indicators': [
                    'Good narrative structure',
                    'Engaging to read',
                    'Would be remembered positively',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Acceptable but not particularly memorable',
                'indicators': [
                    'Competent but forgettable',
                    'No major issues but no highlights',
                    'Blends in with typical applications',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Weak or confusing',
                'indicators': [
                    'Unclear narrative thread',
                    'Difficult to follow',
                    'Boring or clichéd',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Likely to hurt the application',
                'indicators': [
                    'Actively off-putting',
                    'Major structural problems',
                    'Would create negative impression',
                ]
            },
        }
    },
    'jenny_alignment': {
        'name': 'Jenny Alignment',
        'description': 'How well does output match Jenny Duan\'s coaching style?',
        'weight': 0.15,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Indistinguishable from Jenny\'s work',
                'indicators': [
                    'Same strategic approach',
                    'Similar depth of insight',
                    'Matching quality of synthesis',
                    'Equivalent actionability',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Very similar approach and quality',
                'indicators': [
                    'Follows Jenny\'s methodology',
                    'Similar level of personalization',
                    'Minor differences in execution',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Similar approach but different voice/depth',
                'indicators': [
                    'Uses same framework',
                    'Less nuanced execution',
                    'Recognizable but not matching quality',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Somewhat different methodology',
                'indicators': [
                    'Deviates from Jenny\'s approach',
                    'Different priorities or focus',
                    'Missing key Jenny techniques',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Completely different approach',
                'indicators': [
                    'Ignores Jenny\'s framework',
                    'Contradicts her methodology',
                    'Would require complete redo',
                ]
            },
        }
    },
    'actionability': {
        'name': 'Actionability',
        'description': 'How ready-to-use is the output?',
        'weight': 0.15,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Ready to use, provides clear direction',
                'indicators': [
                    'Can be used directly in applications',
                    'Clear guidance for next steps',
                    'Complete and polished',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Minor refinements needed',
                'indicators': [
                    'Nearly complete',
                    'Small tweaks required',
                    '90% ready to use',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Needs some work but usable foundation',
                'indicators': [
                    'Good starting point',
                    'Requires editing and refinement',
                    '70% complete',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Significant refinement required',
                'indicators': [
                    'Substantial gaps',
                    'Needs major revision',
                    'Only provides partial direction',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Too vague or wrong direction',
                'indicators': [
                    'Not usable as foundation',
                    'Wrong strategic direction',
                    'Would need to start over',
                ]
            },
        }
    },
}


def calculate_weighted_score(scores: dict) -> float:
    """
    Calculate weighted average score from dimension scores.

    Args:
        scores: Dict of dimension names to scores (1-5)

    Returns:
        Weighted average score (1.0-5.0)
    """
    total = 0.0
    weight_sum = 0.0

    for dimension, weight in NARRATIVE_WEIGHTS.items():
        if dimension in scores:
            total += scores[dimension] * weight
            weight_sum += weight

    return total / weight_sum if weight_sum > 0 else 0.0


def get_rubric_prompt_section(dimension: str) -> str:
    """
    Get the prompt section for a specific dimension.

    Args:
        dimension: The dimension name

    Returns:
        Formatted prompt section
    """
    if dimension not in NARRATIVE_RUBRIC:
        return ""

    rubric = NARRATIVE_RUBRIC[dimension]
    lines = [f"**{rubric['name'].upper()} (Weight: {int(rubric['weight'] * 100)}%)**"]

    for level, data in sorted(rubric['levels'].items(), reverse=True):
        lines.append(f"- {level}: {data['description']}")

    return "\n".join(lines)
