'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/quest');
  }, [router]);

  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{ background: 'linear-gradient(135deg, #FFE5DF 0%, #F5E8E5 50%, #FFF8F6 100%)' }}
    >
      <div className="w-8 h-8 border-4 border-[#FF4A23] border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

// ============================================================================
// Demo Page (preserved for API testing)
// ============================================================================

import { useState } from 'react';
import type { StudentProfile, AssessmentResults } from '@/lib/types/student';

function DemoPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AssessmentResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Sample student profile for testing
  const sampleProfile: StudentProfile = {
    session_id: 'demo_' + Date.now(),
    timestamp: new Date().toISOString(),
    identity: {
      role: 'STUDENT',
      name: 'Demo Student',
      grade: 11,
    },
    target_schools: ['MIT', 'STANFORD', 'HARVARD', 'CALTECH'],
    intended_major: 'Computer Science',
    major_certainty: 'LIKELY',
    aptitude: {
      gpa_weighted: 4.0,
      gpa_normalized: null,
      gpa_unweighted: 3.95,
      sat_total: 1520,
      sat_normalized: null,
      act_total: null,
      act_normalized: null,
      test_optional: false,
      ap_count: 9,
      ap_avg_score: 4.5,
      rigor_normalized: null,
      ib_diploma: false,
      academic_awards: ['AP Scholar', 'State Science Fair'],
      awards_normalized: null,
    },
    passion: {
      spike_category: 'LEADER',
      leadership_level: 'SCHOOL_PRES',
      leadership_normalized: null,
      ec_commitment_years: 4,
      ec_hours_weekly: 12,
      commitment_normalized: null,
      project_impact: 200,
      project_normalized: null,
      project_description: 'Led robotics team to state finals',
      research_level: 'SCHOOL',
      research_normalized: null,
      ec_awards: ['STATE'],
      ec_awards_normalized: null,
      brag_text: 'Led robotics team to state finals and taught coding to 200+ kids',
      brag_nlp_extracted: null,
    },
    community: {
      service_leadership: 'LOCAL',
      service_normalized: null,
      service_hours: 150,
      hours_normalized: null,
      community_impact: 200,
      impact_normalized: null,
    },
    high_school: {
      hs_name: 'Monta Vista High School',
      hs_code: 'CA_MVHS',
      hs_type: 'PUBLIC',
      region: 'BAY_AREA',
      saturation_level: 'ULTRA',
      ivy_applicants_per_year: 250,
      saturation_adjustment: -0.08,
    },
    demographics: {
      ethnicity: 'ASIAN',
      ethnicity_multiplier: 0.85,
      first_gen: false,
      first_gen_multiplier: 1.0,
      legacy: false,
      legacy_schools: [],
      income_band: '150K_300K',
      income_top_1_percent: false,
      income_multiplier: 1.0,
      recruited_athlete: false,
      athlete_multiplier: 1.0,
    },
    major_context: {
      intended_major: 'Computer Science',
      major_certainty: 'LIKELY',
      major_multiplier: 0.70,
    },
    assessment_intelligence: {
      psychometrics: {
        grit_resilience: 0.85,
        introversion_extroversion: -0.3,
        coachability: 'HIGH',
        coachability_score: 0.85,
        vision_clarity: 0.75,
        identity_comfort: 0.80,
        maturity_level: 0.70,
        articulation_ability: 0.75,
        openness: 0.75,
        conscientiousness: 0.80,
        extraversion: 0.60,
        agreeableness: 0.70,
        neuroticism: 0.40,
      },
      time_management: {
        homework_hours_daily: 4,
        social_media_hours_daily: 2,
        ec_hours_weekly: 12,
        sleep_hours_daily: 7,
        committed_hours_weekly: 98,
        reclaimable_hours_weekly: 14,
        burnout_risk: 'MEDIUM',
      },
      hidden_capabilities: {
        hidden_technical_projects: ['Discord bot for study groups'],
        hobby_passions: ['Video game modding'],
        unconventional_interests: [],
      },
      family_context: {
        parent_archetype: 'BALANCED',
        academic_expectations: 'IVY_ONLY',
      },
      academic_intelligence: {
        grade_pattern_trajectory: 'STABLE',
        test_anxiety_indicator: 0.2,
      },
    },
  };

  const runScoring = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: sampleProfile }),
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results);
    } catch (err: any) {
      setError(err.message || 'Failed to calculate scores');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-display font-bold text-text-primary mb-4">
            IvyQuest v2.2
          </h1>
          <p className="text-xl text-text-secondary mb-2">
            Build Your Digital Twin Fleet
          </p>
          <p className="text-text-muted">
            Powered by IvyLevel Scoring Engine v6.0 with real Chetty 2023 data
          </p>
        </div>

        {/* Demo Section */}
        <div className="bg-background-elevated rounded-2xl border border-border-subtle p-8 mb-8">
          <h2 className="text-2xl font-semibold text-text-primary mb-4">
            Live Scoring Demo
          </h2>
          <p className="text-text-secondary mb-6">
            Click below to run the complete IvyLevel v6.0 scoring engine on a sample student profile.
            This demonstrates real probability calculations using:
          </p>
          <ul className="text-text-secondary space-y-2 mb-6">
            <li>• <strong>58 Layer 1 attributes</strong> normalized to 0.0-1.0 rubric scores</li>
            <li>• <strong>Real CDS 2025 data</strong>: Harvard 4.2%, Stanford 3.9%, MIT 5.7%</li>
            <li>• <strong>Chetty 2023 multipliers</strong>: Legacy 5x at Harvard, 0x at MIT</li>
            <li>• <strong>NSC saturation data</strong>: Monta Vista -8% adjustment</li>
            <li>• <strong>P_final formula</strong>: Sigmoid base × context multipliers capped at 95%</li>
          </ul>

          <button
            onClick={runScoring}
            disabled={loading}
            className="px-8 py-4 bg-primary-blue text-white rounded-xl font-semibold hover:bg-primary-blue-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105 hover:shadow-lg"
          >
            {loading ? 'Calculating Scores...' : 'Run Scoring Engine'}
          </button>

          {error && (
            <div className="mt-6 p-4 bg-error-red/10 border border-error-red/30 rounded-lg">
              <p className="text-error-red">Error: {error}</p>
            </div>
          )}
        </div>

        {/* Results Display */}
        {results && (
          <div className="space-y-6">
            {/* Ivy+ Ready Score */}
            <div className="bg-background-elevated rounded-2xl border border-border-subtle p-8">
              <h2 className="text-2xl font-semibold text-text-primary mb-6">
                Ivy+ Ready Score
              </h2>
              <div className="grid md:grid-cols-2 gap-8">
                <div className="text-center">
                  <div className="text-6xl font-bold text-success-green mb-2">
                    {results.ivy_ready_score.total_score}
                  </div>
                  <div className="text-text-muted">
                    {results.ivy_ready_score.percentile_rank.toFixed(0)}th percentile
                  </div>
                </div>
                <div className="space-y-3">
                  {Object.entries(results.ivy_ready_score.category_scores).map(([category, score]) => (
                    <div key={category}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-text-secondary capitalize">{category}</span>
                        <span className="text-text-primary font-semibold">{score}%</span>
                      </div>
                      <div className="h-2 bg-border-subtle rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-blue rounded-full transition-all duration-500"
                          style={{ width: `${score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* School Probabilities */}
            <div className="bg-background-elevated rounded-2xl border border-border-subtle p-8">
              <h2 className="text-2xl font-semibold text-text-primary mb-6">
                School-by-School Probabilities
              </h2>
              <div className="space-y-4">
                {results.school_probabilities.map((school) => (
                  <div key={school.school_id} className="bg-background-secondary rounded-xl p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-text-primary">
                          {school.school_name}
                        </h3>
                        <div className="text-sm text-text-muted mt-1">
                          Fit Level: <span className={`font-semibold ${
                            school.fit_level === 'BEST_FIT' ? 'text-success-green' :
                            school.fit_level === 'STRONG_FIT' ? 'text-primary-blue' :
                            school.fit_level === 'TOUGH' ? 'text-warning-amber' :
                            'text-error-red'
                          }`}>{school.fit_level.replace('_', ' ')}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-4xl font-mono font-bold text-primary-blue">
                          {(school.p_final * 100).toFixed(1)}%
                        </div>
                        <div className="text-xs text-text-muted">
                          {(school.above_base_rate * 100).toFixed(0)}% above base rate
                        </div>
                      </div>
                    </div>

                    <div className="h-3 bg-border-subtle rounded-full overflow-hidden mb-4">
                      <div
                        className="h-full bg-gradient-to-r from-primary-blue to-success-green rounded-full transition-all duration-700"
                        style={{ width: `${Math.min(school.p_final * 100, 100)}%` }}
                      />
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-text-secondary font-semibold mb-2">Why {school.school_name.split(' ')[0]} Likes You:</div>
                        <ul className="space-y-1">
                          {school.fit_reasons.map((reason, i) => (
                            <li key={i} className="text-success-green">• {reason}</li>
                          ))}
                        </ul>
                      </div>
                      {school.warnings.length > 0 && (
                        <div>
                          <div className="text-text-secondary font-semibold mb-2">Warnings:</div>
                          <ul className="space-y-1">
                            {school.warnings.map((warning, i) => (
                              <li key={i} className="text-warning-amber">⚠ {warning}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    <div className="mt-4 pt-4 border-t border-border-subtle grid grid-cols-3 gap-4 text-xs text-text-muted">
                      <div>
                        <div>Base (Sigmoid):</div>
                        <div className="font-mono text-text-primary">{(school.p_base * 100).toFixed(1)}%</div>
                      </div>
                      <div>
                        <div>With Context:</div>
                        <div className="font-mono text-text-primary">{(school.p_context * 100).toFixed(1)}%</div>
                      </div>
                      <div>
                        <div>Rubric Score:</div>
                        <div className="font-mono text-text-primary">{school.rubric_score}/6</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Diagnostics */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-background-elevated rounded-2xl border border-border-subtle p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  ✅ What's Helping
                </h3>
                <ul className="space-y-2">
                  {results.helping_factors.map((factor, i) => (
                    <li key={i} className="text-success-green text-sm">• {factor}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-background-elevated rounded-2xl border border-border-subtle p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  ⚠️ What's Holding Back
                </h3>
                <ul className="space-y-2">
                  {results.holding_back_factors.map((factor, i) => (
                    <li key={i} className="text-warning-amber text-sm">• {factor}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Archetype */}
            <div className="bg-background-elevated rounded-2xl border border-border-subtle p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Detected Archetype
              </h3>
              <p className="text-text-secondary">
                <span className="font-semibold text-primary-blue">{results.archetype_label}</span>
              </p>
              <p className="text-text-muted italic mt-2">
                "{results.narrative_tagline}"
              </p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-text-muted text-sm">
          <p>IvyQuest v2.2 | IvyLevel Scoring Engine v6.0</p>
          <p className="mt-2">
            Data Sources: Chetty (2023), CDS 2025, SFFA v. Harvard, NSC
          </p>
        </div>
      </div>
    </div>
  );
}
