/**
 * AssessmentTab - Main Assessment Results View
 * v12.0 - Matches original frontend specification
 */
'use client';

import { motion } from 'framer-motion';
import {
  Award, AlertTriangle, Target, TrendingUp, TrendingDown,
  GraduationCap, Users, Heart, Sparkles
} from 'lucide-react';
import { IvyScoreCard } from '@/components/dashboard/IvyScoreCard';
import { PillarScoresGrid } from '@/components/quest/PillarCard';
import { CategoryScoresQuadrant } from '@/components/quest/CircularProgressRing';
import { COLORS, STATUS_COLORS, GRADIENTS } from '@/lib/constants/design';

interface AssessmentData {
  ivyReadyScore: {
    overall: number;
    tier: string;
    changeVs180Days: number;
  };
  pillars: {
    aptitude: number;
    passion: number;
    service: number;
    identity: number;
  };
  dimensionalScores: Array<{
    dimension: string;
    score: number;
    tier: string;
  }>;
  strengths: Array<{
    title: string;
    roi: number;
    impact: string;
  }>;
  weakSpots: Array<{
    title: string;
    priority: 'P0' | 'P1' | 'P2';
    description: string;
  }>;
  admissionsRubric?: {
    academicIndex: number;
    extracurricularRating: number;
    personalQualities: number;
    recommendationStrength: number;
    overallAdmitProbability: number;
    targetSchools: string[];
  };
  criMultiplier?: number;
}

interface AssessmentTabProps {
  data: AssessmentData;
}

export function AssessmentTab({ data }: AssessmentTabProps) {
  return (
    <div className="max-w-[1400px] mx-auto px-8 py-8">
      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2fr) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Overall Score Card */}
          <IvyScoreCard
            score={data.ivyReadyScore.overall}
            changeVs180Days={data.ivyReadyScore.changeVs180Days}
            criMultiplier={data.criMultiplier}
          />

          {/* Pillar Scores with Animated Waves */}
          <section>
            <h2 className="text-lg font-semibold mb-4" style={{ color: COLORS.textHeading }}>
              Four Pillars of Excellence
            </h2>
            <PillarScoresGrid scores={data.pillars} size="md" />
          </section>

          {/* Dimensional Scores Grid */}
          {data.dimensionalScores && data.dimensionalScores.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-4" style={{ color: COLORS.textHeading }}>
                Dimensional Breakdown
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {data.dimensionalScores.map((dim, i) => (
                  <motion.div
                    key={dim.dimension}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="bg-white rounded-xl p-4 border"
                    style={{ borderColor: COLORS.borderDefault }}
                  >
                    <span className="text-xs font-medium" style={{ color: COLORS.textMuted }}>
                      {dim.dimension}
                    </span>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-2xl font-bold" style={{ color: COLORS.textHeading }}>
                        {dim.score}
                      </span>
                      <span className="text-sm" style={{ color: COLORS.textMuted }}>/100</span>
                    </div>
                    <span
                      className="inline-block mt-2 px-2 py-0.5 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: STATUS_COLORS.completed.bg,
                        color: STATUS_COLORS.completed.text,
                      }}
                    >
                      {dim.tier}
                    </span>
                  </motion.div>
                ))}
              </div>
            </section>
          )}

          {/* Strengths Section */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Award size={20} style={{ color: COLORS.success }} />
              <h2 className="text-lg font-semibold" style={{ color: COLORS.textHeading }}>
                Standout Strengths
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.strengths.map((strength, i) => (
                <motion.div
                  key={strength.title}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-white rounded-xl p-4 border-l-4"
                  style={{ borderColor: COLORS.success }}
                >
                  <h3 className="font-medium" style={{ color: COLORS.textHeading }}>
                    {strength.title}
                  </h3>
                  <div className="flex items-center gap-3 mt-2">
                    <span
                      className="px-2 py-0.5 rounded text-xs font-medium"
                      style={{ backgroundColor: '#dcfce7', color: COLORS.success }}
                    >
                      ROI: {strength.roi}x
                    </span>
                    <span className="text-sm" style={{ color: COLORS.textSecondary }}>
                      {strength.impact}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </section>

          {/* Weak Spots / Focus Areas */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle size={20} style={{ color: COLORS.warning }} />
              <h2 className="text-lg font-semibold" style={{ color: COLORS.textHeading }}>
                Focus Areas
              </h2>
            </div>
            <div className="space-y-3">
              {data.weakSpots.map((spot, i) => {
                const priorityColors = {
                  P0: { bg: '#fee2e2', text: '#dc2626', border: '#dc2626' },
                  P1: { bg: '#fef3c7', text: '#d97706', border: '#d97706' },
                  P2: { bg: '#f3f4f6', text: '#6b7280', border: '#6b7280' },
                };
                const colors = priorityColors[spot.priority];

                return (
                  <motion.div
                    key={spot.title}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="bg-white rounded-xl p-4 flex items-start gap-4"
                    style={{
                      borderLeft: `4px solid ${colors.border}`,
                      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                    }}
                  >
                    <span
                      className="px-2 py-1 rounded text-xs font-bold"
                      style={{ backgroundColor: colors.bg, color: colors.text }}
                    >
                      {spot.priority}
                    </span>
                    <div>
                      <h3 className="font-medium" style={{ color: COLORS.textHeading }}>
                        {spot.title}
                      </h3>
                      <p className="text-sm mt-1" style={{ color: COLORS.textSecondary }}>
                        {spot.description}
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </section>
        </div>

        {/* Right Column (1fr) */}
        <div className="space-y-6">
          {/* Central Score Visualization */}
          <div className="bg-white rounded-2xl p-6" style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
            <h3 className="text-sm font-medium mb-4" style={{ color: COLORS.textSecondary }}>
              Pillar Balance
            </h3>
            <CategoryScoresQuadrant
              scores={{
                aptitude: data.pillars.aptitude,
                passion: data.pillars.passion,
                service: data.pillars.service,
                identity: data.pillars.identity,
              }}
            />
          </div>

          {/* Admissions Rubric Correlation */}
          {data.admissionsRubric && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="rounded-2xl p-6 text-white"
              style={{ background: GRADIENTS.purple }}
            >
              <h3 className="font-semibold mb-4">Admissions Rubric Correlation</h3>

              <div className="space-y-3">
                <RubricItem
                  label="Academic Index"
                  value={data.admissionsRubric.academicIndex}
                />
                <RubricItem
                  label="Extracurricular Rating"
                  value={data.admissionsRubric.extracurricularRating}
                />
                <RubricItem
                  label="Personal Qualities"
                  value={data.admissionsRubric.personalQualities}
                />
                <RubricItem
                  label="Recommendation Strength"
                  value={data.admissionsRubric.recommendationStrength}
                />
              </div>

              <div className="mt-6 pt-4 border-t border-white/20">
                <span className="text-sm opacity-75">Overall Admit Probability</span>
                <div className="text-3xl font-bold mt-1">
                  {data.admissionsRubric.overallAdmitProbability}%
                </div>
              </div>

              {data.admissionsRubric.targetSchools.length > 0 && (
                <div className="mt-4">
                  <span className="text-sm opacity-75">Target Schools</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {data.admissionsRubric.targetSchools.map(school => (
                      <span
                        key={school}
                        className="px-2 py-1 rounded-full text-xs bg-white/20"
                      >
                        {school}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}

function RubricItem({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm opacity-75">{label}</span>
      <div className="flex items-center gap-2">
        <div className="w-24 h-2 rounded-full bg-white/20 overflow-hidden">
          <motion.div
            className="h-full bg-white rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${value}%` }}
            transition={{ duration: 1, delay: 0.5 }}
          />
        </div>
        <span className="text-sm font-medium w-8">{value}</span>
      </div>
    </div>
  );
}

export default AssessmentTab;
