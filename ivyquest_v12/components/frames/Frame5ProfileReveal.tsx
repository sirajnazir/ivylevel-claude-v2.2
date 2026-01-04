/**
 * Frame 5: Profile Reveal
 * v12.0 - With animated wave pillar score cards
 */
'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ChevronRight, TrendingUp, Award, AlertTriangle } from 'lucide-react';
import { PillarScoresGrid, PillarCard } from '@/components/quest/PillarCard';
import { IvyScoreCard } from '@/components/dashboard/IvyScoreCard';
import { CategoryScoresQuadrant } from '@/components/quest/CircularProgress';
import { FrameEdgeProgress } from '@/components/quest/EdgeProgress';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { EDGE_VALUES } from '@/lib/constants/edge';
import { COLORS, GRADIENTS } from '@/lib/constants/design';

interface ProfileData {
  overallScore: number;
  criMultiplier: number;
  pillars: {
    aptitude: number;
    passion: number;
    service: number;
    identity: number;
  };
  archetype: string;
  narrativeDna: string;
  strengths: string[];
  gaps: string[];
}

interface Frame5ProfileRevealProps {
  profileData: ProfileData;
  onNext: () => void;
  onBack: () => void;
}

export function Frame5ProfileReveal({ profileData, onNext, onBack }: Frame5ProfileRevealProps) {
  const [revealStage, setRevealStage] = useState(0);
  const { edgePoints, maxFrameReached } = useSessionStore();

  // Staged reveal animation
  useEffect(() => {
    const stages = [0, 1, 2, 3, 4];
    let currentIndex = 0;

    const timer = setInterval(() => {
      currentIndex++;
      if (currentIndex < stages.length) {
        setRevealStage(stages[currentIndex]);
      } else {
        clearInterval(timer);
      }
    }, 800);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen" style={{ backgroundColor: COLORS.bgPage }}>
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white border-b px-4 py-3" style={{ borderColor: COLORS.borderDefault }}>
        <div className="max-w-4xl mx-auto">
          <FrameEdgeProgress 
            frameNumber={5} 
            totalFrames={6} 
            edgeEarned={(maxFrameReached - 1) * EDGE_VALUES.frameComplete} 
          />
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Title Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div 
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-white mb-4"
            style={{ background: GRADIENTS.purple }}
          >
            <Sparkles size={16} />
            <span className="text-sm font-medium">Profile Analysis Complete</span>
          </div>
          <h1 className="text-3xl font-bold" style={{ color: COLORS.textHeading }}>
            Your Ivy+ Profile
          </h1>
          <p className="text-sm mt-2" style={{ color: COLORS.textSecondary }}>
            Here's what we discovered about your unique strengths
          </p>
        </motion.div>

        {/* Overall Score */}
        <AnimatePresence>
          {revealStage >= 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="mb-8"
            >
              <IvyScoreCard 
                score={profileData.overallScore}
                criMultiplier={profileData.criMultiplier}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Four Pillars with Animated Wave Cards */}
        <AnimatePresence>
          {revealStage >= 1 && (
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="mb-8"
            >
              <h2 className="text-lg font-semibold mb-4 text-center" style={{ color: COLORS.textHeading }}>
                Four Pillars of Excellence
              </h2>
              <PillarScoresGrid scores={profileData.pillars} size="lg" />
            </motion.section>
          )}
        </AnimatePresence>

        {/* Archetype & Narrative DNA */}
        <AnimatePresence>
          {revealStage >= 2 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="grid md:grid-cols-2 gap-6 mb-8"
            >
              {/* Archetype */}
              <div 
                className="rounded-2xl p-6 text-white"
                style={{ background: GRADIENTS.purple }}
              >
                <h3 className="text-sm font-medium opacity-75 mb-2">Your Archetype</h3>
                <p className="text-2xl font-bold">{profileData.archetype}</p>
              </div>

              {/* Narrative DNA */}
              <div 
                className="bg-white rounded-2xl p-6 border"
                style={{ borderColor: COLORS.borderDefault }}
              >
                <h3 className="text-sm font-medium mb-2" style={{ color: COLORS.textMuted }}>
                  Narrative DNA
                </h3>
                <p className="text-sm" style={{ color: COLORS.textSecondary }}>
                  {profileData.narrativeDna}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Strengths */}
        <AnimatePresence>
          {revealStage >= 3 && (
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="mb-8"
            >
              <div className="flex items-center gap-2 mb-4">
                <Award size={20} style={{ color: COLORS.success }} />
                <h2 className="text-lg font-semibold" style={{ color: COLORS.textHeading }}>
                  Standout Strengths
                </h2>
              </div>
              <div className="flex flex-wrap gap-3">
                {profileData.strengths.map((strength, i) => (
                  <motion.span
                    key={strength}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.1 }}
                    className="px-4 py-2 rounded-full text-sm font-medium"
                    style={{ 
                      backgroundColor: '#dcfce7',
                      color: COLORS.success,
                    }}
                  >
                    {strength}
                  </motion.span>
                ))}
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Focus Areas (Gaps) */}
        <AnimatePresence>
          {revealStage >= 4 && (
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="mb-8"
            >
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle size={20} style={{ color: COLORS.warning }} />
                <h2 className="text-lg font-semibold" style={{ color: COLORS.textHeading }}>
                  Focus Areas
                </h2>
              </div>
              <div className="flex flex-wrap gap-3">
                {profileData.gaps.map((gap, i) => (
                  <motion.span
                    key={gap}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.1 }}
                    className="px-4 py-2 rounded-full text-sm font-medium"
                    style={{ 
                      backgroundColor: '#fef3c7',
                      color: '#d97706',
                    }}
                  >
                    {gap}
                  </motion.span>
                ))}
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Score Quadrant Visualization */}
        <AnimatePresence>
          {revealStage >= 4 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex justify-center mb-8"
            >
              <div className="bg-white rounded-2xl p-6" style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
                <h3 className="text-sm font-medium mb-4 text-center" style={{ color: COLORS.textMuted }}>
                  Pillar Balance
                </h3>
                <CategoryScoresQuadrant
                  aptitude={profileData.pillars.aptitude}
                  passion={profileData.pillars.passion}
                  service={profileData.pillars.service}
                  identity={profileData.pillars.identity}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navigation */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t px-4 py-4" style={{ borderColor: COLORS.borderDefault }}>
          <div className="max-w-4xl mx-auto flex justify-between">
            <button
              onClick={onBack}
              className="px-6 py-3 font-medium hover:opacity-80"
              style={{ color: COLORS.textSecondary }}
            >
              Back
            </button>
            <button
              onClick={onNext}
              disabled={revealStage < 4}
              className="flex items-center gap-2 px-8 py-3 text-white font-medium rounded-xl disabled:opacity-50 transition-all"
              style={{ background: revealStage >= 4 ? GRADIENTS.purple : COLORS.textMuted }}
            >
              See Your Action Plan
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Frame5ProfileReveal;
