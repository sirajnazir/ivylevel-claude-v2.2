"""
IvyQuest v10.0 - Awards Evaluation Rubric
=========================================

Rubric for evaluating AwardsAgent outputs.
"""

# Dimension weights (must sum to 1.0)
AWARDS_WEIGHTS = {
    'relevance': 0.25,
    'strategic_fit': 0.25,
    'achievability': 0.20,
    'comprehensiveness': 0.15,
    'rationale_quality': 0.15,
}

# Full rubric definitions
AWARDS_RUBRIC = {
    'relevance': {
        'name': 'Relevance',
        'description': 'How well do awards align with student\'s spike and narrative?',
        'weight': 0.25,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Perfect alignment with spike, narrative, and interests',
                'indicators': [
                    'Every award directly relates to student\'s core focus',
                    'Awards reinforce the narrative theme',
                    'Clear connection to demonstrated abilities',
                    'Would strengthen application coherence',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Strong alignment with minor exceptions',
                'indicators': [
                    'Most awards clearly relevant',
                    '1-2 awards slightly tangential',
                    'Overall supports narrative well',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Generally relevant but some mismatches',
                'indicators': [
                    'Core awards are relevant',
                    'Several awards don\'t connect to spike',
                    'Mixed coherence with narrative',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Limited relevance to student profile',
                'indicators': [
                    'Many awards don\'t fit student\'s focus',
                    'Appears to be generic list',
                    'Would dilute application focus',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Awards misaligned with student',
                'indicators': [
                    'Awards contradict student\'s direction',
                    'Wrong category entirely',
                    'Would confuse admissions officers',
                ]
            },
        }
    },
    'strategic_fit': {
        'name': 'Strategic Fit',
        'description': 'Would winning these strengthen the application?',
        'weight': 0.25,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Optimal strategic portfolio',
                'indicators': [
                    'High-impact awards for target schools',
                    'Fills gaps in current profile',
                    'Demonstrates progression and depth',
                    'Differentiates from similar applicants',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Strong strategic value',
                'indicators': [
                    'Would meaningfully improve application',
                    'Good mix of recognition types',
                    'Appropriate for target tier',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Moderate strategic value',
                'indicators': [
                    'Some awards add value',
                    'Others are neutral',
                    'Doesn\'t fully optimize opportunity',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Limited strategic impact',
                'indicators': [
                    'Low-prestige awards dominate',
                    'Missing high-impact opportunities',
                    'Doesn\'t address profile gaps',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Would not help application',
                'indicators': [
                    'Awards irrelevant to admissions',
                    'Time investment not justified',
                    'Would distract from better options',
                ]
            },
        }
    },
    'achievability': {
        'name': 'Achievability',
        'description': 'Is the likely/target/stretch balance realistic?',
        'weight': 0.20,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Perfect balance with accurate predictions',
                'indicators': [
                    'Likely awards are truly achievable',
                    'Target awards are realistic with effort',
                    'Stretch awards are ambitious but possible',
                    'Win probability estimates are accurate',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Good balance, mostly accurate',
                'indicators': [
                    'Categories largely appropriate',
                    'Minor miscategorization',
                    'Overall realistic expectations',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Reasonable but some miscategorization',
                'indicators': [
                    'Some awards in wrong tier',
                    'Expectations slightly off',
                    'Workable portfolio overall',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Imbalanced or unrealistic',
                'indicators': [
                    'Too many stretch awards',
                    'Likely awards are actually difficult',
                    'Could lead to burnout or disappointment',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Completely unrealistic expectations',
                'indicators': [
                    'Awards beyond student\'s capability',
                    'No achievable wins included',
                    'Would result in zero recognition',
                ]
            },
        }
    },
    'comprehensiveness': {
        'name': 'Comprehensiveness',
        'description': 'Are important awards missing?',
        'weight': 0.15,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Complete coverage of relevant awards',
                'indicators': [
                    'All major awards in category included',
                    'Good mix of levels (local to national)',
                    'Timeline-appropriate deadlines',
                    'No obvious omissions',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Good coverage with minor gaps',
                'indicators': [
                    'Most relevant awards included',
                    '1-2 minor omissions',
                    'Good variety overall',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Acceptable coverage',
                'indicators': [
                    'Core awards present',
                    'Some notable omissions',
                    'Limited variety in levels',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Significant gaps',
                'indicators': [
                    'Missing major awards',
                    'Limited to one category type',
                    'Incomplete research evident',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'Major omissions',
                'indicators': [
                    'Obvious high-value awards missing',
                    'Appears to be cursory list',
                    'Would need complete redo',
                ]
            },
        }
    },
    'rationale_quality': {
        'name': 'Rationale Quality',
        'description': 'Are the "why" explanations compelling?',
        'weight': 0.15,
        'levels': {
            5: {
                'label': 'Exceptional',
                'description': 'Compelling, personalized rationales',
                'indicators': [
                    'Clear connection to student\'s story',
                    'Strategic reasoning explained',
                    'Specific to student, not generic',
                    'Motivating and actionable',
                ]
            },
            4: {
                'label': 'Strong',
                'description': 'Good rationales with minor gaps',
                'indicators': [
                    'Most rationales are personalized',
                    'Clear reasoning provided',
                    'Some could be more specific',
                ]
            },
            3: {
                'label': 'Adequate',
                'description': 'Basic rationales provided',
                'indicators': [
                    'Rationales present but generic',
                    'Lack depth of analysis',
                    'Could apply to many students',
                ]
            },
            2: {
                'label': 'Weak',
                'description': 'Minimal or poor rationales',
                'indicators': [
                    'Many awards without explanation',
                    'Rationales are superficial',
                    'No strategic thinking evident',
                ]
            },
            1: {
                'label': 'Poor',
                'description': 'No useful rationales',
                'indicators': [
                    'Missing rationales entirely',
                    'Incorrect reasoning provided',
                    'Would confuse rather than help',
                ]
            },
        }
    },
}


def calculate_weighted_score(scores: dict) -> float:
    """Calculate weighted average score from dimension scores."""
    total = 0.0
    weight_sum = 0.0

    for dimension, weight in AWARDS_WEIGHTS.items():
        if dimension in scores:
            total += scores[dimension] * weight
            weight_sum += weight

    return total / weight_sum if weight_sum > 0 else 0.0
