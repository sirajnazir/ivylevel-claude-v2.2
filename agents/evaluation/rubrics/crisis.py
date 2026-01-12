"""
IvyQuest v10.0 - Crisis Alchemy Evaluation Rubric
=================================================

Rubric for evaluating Crisis Alchemy responses.
Based on Jenny Duan's 4-step crisis protocol:
1. Validate (2s) - Acknowledge emotion
2. Act (10s) - Micro-action to restore agency
3. Reframe (30s) - Find opportunity angle
4. Create (2min) - Design pivot activity
"""

# Dimension weights (must sum to 1.0)
CRISIS_WEIGHTS = {
    'validation_quality': 0.20,
    'micro_action_quality': 0.20,
    'reframe_quality': 0.20,
    'pivot_activity_quality': 0.25,
    'overall_tone': 0.15,
}

# Full rubric definitions
CRISIS_RUBRIC = {
    'validation_quality': {
        'name': 'Validation Quality',
        'description': 'Is it genuine acknowledgment without toxic positivity?',
        'weight': 0.20,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Perfect emotional attunement',
                'indicators': [
                    'Names the exact emotion the student is feeling',
                    'Acknowledges the validity of their experience',
                    'Creates genuine connection',
                    'No toxic positivity or dismissiveness',
                    'Warm but not patronizing',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Good emotional acknowledgment',
                'indicators': [
                    'Accurately identifies emotional state',
                    'Genuine validation provided',
                    'Minor room for improvement',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Basic validation present',
                'indicators': [
                    'Acknowledges difficulty but somewhat generic',
                    'Doesn\'t fully capture the emotion',
                    'Acceptable but not deeply connecting',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Insufficient or problematic validation',
                'indicators': [
                    'Rushes past the emotion',
                    'Slightly dismissive undertones',
                    'Misidentifies the core feeling',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Harmful or absent validation',
                'indicators': [
                    'Toxic positivity present',
                    'Dismisses student\'s feelings',
                    'Could make student feel worse',
                    'No acknowledgment of emotional state',
                ]
            },
        }
    },
    'micro_action_quality': {
        'name': 'Micro-Action Quality',
        'description': 'Is it truly small (<5 min) and does it restore agency?',
        'weight': 0.20,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Perfect micro-action',
                'indicators': [
                    'Truly achievable in under 5 minutes',
                    'Immediately restores sense of control',
                    'Directly relevant to the situation',
                    'Low barrier to start',
                    'Creates positive momentum',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Good micro-action with minor issues',
                'indicators': [
                    'Achievable and helpful',
                    'Good agency restoration',
                    'Slightly larger than ideal',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Acceptable action but not ideal',
                'indicators': [
                    'Action provided but not truly micro',
                    'May take 10-15 minutes',
                    'Helpful but not optimal',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Action too large or irrelevant',
                'indicators': [
                    'Requires significant time/effort',
                    'Doesn\'t address immediate need',
                    'Could feel overwhelming',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'No useful action or harmful',
                'indicators': [
                    'No action provided',
                    'Action is counterproductive',
                    'Would increase overwhelm',
                ]
            },
        }
    },
    'reframe_quality': {
        'name': 'Reframe Quality',
        'description': 'Is there a genuine opportunity angle without minimizing?',
        'weight': 0.20,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Brilliant reframe that transforms perspective',
                'indicators': [
                    'Genuine insight into opportunity',
                    'Doesn\'t minimize the setback',
                    'Specific to this situation',
                    'Feels authentic, not forced',
                    'Student would feel genuinely better',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Good reframe with genuine value',
                'indicators': [
                    'Valid opportunity identified',
                    'Respectful of the difficulty',
                    'Helpful new perspective',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Basic reframe that works',
                'indicators': [
                    'Some valid points',
                    'Somewhat generic',
                    'Acceptable but not inspiring',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Forced or dismissive reframe',
                'indicators': [
                    'Silver lining feels forced',
                    'May feel like minimizing',
                    'Generic platitudes',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Harmful or absent reframe',
                'indicators': [
                    'Toxic positivity',
                    'Dismisses real concerns',
                    'Could make student feel invalidated',
                    'No reframe attempted',
                ]
            },
        }
    },
    'pivot_activity_quality': {
        'name': 'Pivot Activity Quality',
        'description': 'Is the pivot concrete, achievable, and transformative?',
        'weight': 0.25,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Brilliant pivot that transforms setback',
                'indicators': [
                    'Concrete and actionable',
                    'Directly addresses the setback',
                    'Turns weakness into strength',
                    'Achievable with student\'s resources',
                    'Would genuinely improve application',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Good pivot with clear value',
                'indicators': [
                    'Concrete activity defined',
                    'Reasonable path forward',
                    'Addresses core issue',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Workable pivot but not optimal',
                'indicators': [
                    'Activity suggested but vague',
                    'Somewhat helpful direction',
                    'Could be more specific',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Vague or unrealistic pivot',
                'indicators': [
                    'Too vague to be actionable',
                    'Unrealistic for student\'s situation',
                    'Doesn\'t address the core issue',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'No useful pivot or harmful',
                'indicators': [
                    'No pivot activity provided',
                    'Suggested activity is counterproductive',
                    'Would waste student\'s time',
                ]
            },
        }
    },
    'overall_tone': {
        'name': 'Overall Tone',
        'description': 'Does it have Jenny-like warmth and directness?',
        'weight': 0.15,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Perfect Jenny tone - warm, direct, empowering',
                'indicators': [
                    'Warm but not saccharine',
                    'Direct without being harsh',
                    'Empowering, not paternalistic',
                    'Appropriate urgency for situation',
                    'Would feel like talking to a trusted mentor',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Good tone with Jenny qualities',
                'indicators': [
                    'Generally warm and supportive',
                    'Mostly direct and actionable',
                    'Minor tone adjustments needed',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Acceptable tone but somewhat generic',
                'indicators': [
                    'Professional but impersonal',
                    'Lacks Jenny\'s distinctive warmth',
                    'Functional but not inspiring',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Tone issues present',
                'indicators': [
                    'Too formal or too casual',
                    'Condescending undertones',
                    'Doesn\'t match situation urgency',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Harmful or inappropriate tone',
                'indicators': [
                    'Cold and robotic',
                    'Dismissive or judgmental',
                    'Would damage trust',
                    'Inappropriate for crisis situation',
                ]
            },
        }
    },
}


def calculate_weighted_score(scores: dict) -> float:
    """Calculate weighted average score from dimension scores."""
    total = 0.0
    weight_sum = 0.0

    for dimension, weight in CRISIS_WEIGHTS.items():
        if dimension in scores:
            total += scores[dimension] * weight
            weight_sum += weight

    return total / weight_sum if weight_sum > 0 else 0.0


def get_crisis_protocol_summary() -> str:
    """Get a summary of the Crisis Alchemy protocol."""
    return """
Crisis Alchemy Protocol (Jenny Duan Method):

1. VALIDATE (2 seconds)
   - Acknowledge the emotion genuinely
   - Name what the student is feeling
   - Create connection before moving forward

2. ACT (10 seconds)
   - Provide a micro-action (<5 min)
   - Restore sense of agency immediately
   - Low barrier, high impact

3. REFRAME (30 seconds)
   - Find the genuine opportunity angle
   - Don't minimize the setback
   - Specific to their situation

4. CREATE (2 minutes)
   - Design a pivot activity
   - Transform the setback into strength
   - Concrete, achievable, valuable
"""
