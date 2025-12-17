'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';
import { safeSortBy } from '@/lib/utils/safeValue';
import { useStudentStore, useSessionStore, useResultsStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Progress } from '@/components/ui/Progress';
import { ScoreRing, ScoreBadge } from '@/components/ui/ScoreRing';
import { SCHOOL_DATABASE } from '@/lib/data/schools';
import {
  Sparkles,
  Rocket,
  Target,
  TrendingUp,
  Trophy,
  GraduationCap,
  Play,
  RotateCcw,
  ArrowRight,
  ChevronRight,
  Zap,
  Star,
} from 'lucide-react';

export default function DashboardPage() {
  const profile = useStudentStore((s) => s.profile);
  const isCompleted = useSessionStore((s) => s.is_completed);
  const totalXP = useSessionStore((s) => s.total_xp);
  const resetSession = useSessionStore((s) => s.resetSession);
  const resetProfile = useStudentStore((s) => s.resetProfile);
  const clearResults = useResultsStore((s) => s.clearResults);

  const ivyScore = useResultsStore((s) => s.ivy_score);
  const schoolProbabilities = useResultsStore((s) => s.school_probabilities);
  const archetype = useResultsStore((s) => s.archetype_label);

  const handleReset = () => {
    resetSession();
    resetProfile();
    clearResults();
  };

  const hasResults = ivyScore !== null;
  const userName = profile.identity.name || 'Student';

  return (
    <div className="min-h-screen bg-background-primary">
      {/* Background effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-radial from-primary-blue/5 to-transparent" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#2A354408_1px,transparent_1px),linear-gradient(to_bottom,#2A354408_1px,transparent_1px)] bg-[size:64px_64px]" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-border-subtle bg-background-primary/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary-blue/20 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary-blue" />
              </div>
              <div>
                <h1 className="font-display font-bold text-text-primary">IvyQuest</h1>
                <p className="text-sm text-text-muted">v2.2</p>
              </div>
            </div>

            {/* XP Badge */}
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-warning-amber/10 border border-warning-amber/30">
              <Zap className="w-4 h-4 text-warning-amber" />
              <span className="font-semibold text-warning-amber">{totalXP} XP</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10 max-w-6xl mx-auto px-4 py-8">
        {/* Welcome section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-3xl font-display font-bold text-text-primary">
            {hasResults ? `Welcome back, ${userName}!` : `Hey ${userName || 'there'}!`}
          </h2>
          <p className="text-text-secondary mt-1">
            {hasResults
              ? 'Your Digital Twin Fleet is ready for review'
              : 'Let\'s build your Digital Twin Fleet'}
          </p>
        </motion.div>

        {/* Main CTA or Results */}
        {!hasResults ? (
          /* Start Assessment CTA */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card padding="lg" className="border-primary-blue/30 bg-gradient-to-br from-primary-blue/10 to-transparent">
              <CardContent>
                <div className="flex flex-col md:flex-row items-center gap-8">
                  <div className="flex-1 text-center md:text-left">
                    <h3 className="text-2xl font-display font-bold text-text-primary mb-2">
                      Start Your Assessment
                    </h3>
                    <p className="text-text-secondary mb-6">
                      Complete our 6-frame assessment to get your personalized Ivy+ Score,
                      school probabilities, and action plan. Takes about 15-20 minutes.
                    </p>
                    <ul className="space-y-2 mb-6">
                      {[
                        '58 attributes across 4 layers',
                        'Real CDS 2025 acceptance rates',
                        'Chetty 2023 ROI multipliers',
                        'Personalized booster recommendations',
                      ].map((item, i) => (
                        <li key={i} className="flex items-center gap-2 text-text-secondary">
                          <Star className="w-4 h-4 text-warning-amber" />
                          {item}
                        </li>
                      ))}
                    </ul>
                    <Link href="/assessment">
                      <Button size="lg" rightIcon={<Play className="w-5 h-5" />}>
                        Begin Assessment
                      </Button>
                    </Link>
                  </div>

                  <div className="flex-shrink-0">
                    <div className="w-40 h-40 rounded-full bg-primary-blue/20 flex items-center justify-center">
                      <Rocket className="w-20 h-20 text-primary-blue animate-float" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          /* Results Dashboard */
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Score Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="lg:col-span-1"
            >
              <Card padding="lg" className="h-full">
                <CardContent className="text-center">
                  <ScoreRing score={ivyScore.total_score} size="lg" animated={false} />
                  <div className="mt-4 space-y-1">
                    <p className="text-sm text-text-muted">Your Ivy+ Ready Score</p>
                    <div className="flex items-center justify-center gap-2">
                      <Trophy className="w-4 h-4 text-warning-amber" />
                      <span className="text-sm font-medium text-text-secondary">
                        Top {(100 - ivyScore.percentile_rank).toFixed(0)}% of applicants
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-6">
                    {[
                      { label: 'Aptitude', score: ivyScore.category_scores.aptitude },
                      { label: 'Passion', score: ivyScore.category_scores.passion },
                      { label: 'Community', score: ivyScore.category_scores.community },
                      { label: 'Narrative', score: ivyScore.category_scores.narrative },
                    ].map((cat) => (
                      <div key={cat.label} className="p-2 rounded-lg bg-background-secondary">
                        <div className="text-lg font-bold text-text-primary">{cat.score}%</div>
                        <div className="text-xs text-text-muted">{cat.label}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* School Probabilities */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="lg:col-span-2"
            >
              <Card padding="lg" className="h-full">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-primary-blue" />
                    School Probabilities
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {safeSortBy(schoolProbabilities, (s) => s.p_final, true)
                      .map((school) => {
                        const schoolData = SCHOOL_DATABASE[school.school_id];
                        return (
                          <div
                            key={school.school_id}
                            className="flex items-center gap-4 p-3 rounded-xl bg-background-secondary"
                          >
                            <div
                              className="w-10 h-10 rounded-lg flex items-center justify-center"
                              style={{ backgroundColor: schoolData?.twin_color || '#4A90D9' }}
                            >
                              <GraduationCap className="w-5 h-5 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-text-primary truncate">
                                {school.school_name}
                              </p>
                              <Progress
                                value={school.p_final * 100}
                                size="sm"
                                showValue={false}
                              />
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-text-primary">
                                {(school.p_final * 100).toFixed(0)}%
                              </div>
                              <ScoreBadge
                                score={Math.round(school.p_final * 100)}
                                size="sm"
                              />
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Archetype */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card padding="lg" className="h-full">
                <CardContent className="text-center py-6">
                  <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-primary-blue to-primary-blue-hover flex items-center justify-center mb-4">
                    <Star className="w-8 h-8 text-white" />
                  </div>
                  <p className="text-sm text-text-muted mb-1">Your Archetype</p>
                  <h3 className="text-xl font-display font-bold text-text-primary">
                    {archetype || 'Ambitious Achiever'}
                  </h3>
                </CardContent>
              </Card>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="lg:col-span-2"
            >
              <Card padding="lg" className="h-full">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Rocket className="w-5 h-5 text-success-green" />
                    Quick Actions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid sm:grid-cols-2 gap-3">
                    <Link href="/assessment">
                      <button className="w-full p-4 rounded-xl bg-background-secondary border border-border-subtle hover:border-primary-blue hover:bg-primary-blue/5 transition-all text-left group">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-primary-blue/20 flex items-center justify-center">
                              <TrendingUp className="w-5 h-5 text-primary-blue" />
                            </div>
                            <div>
                              <p className="font-medium text-text-primary">Update Profile</p>
                              <p className="text-sm text-text-muted">Retake assessment</p>
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-text-muted group-hover:text-primary-blue transition-colors" />
                        </div>
                      </button>
                    </Link>

                    <button
                      onClick={handleReset}
                      className="w-full p-4 rounded-xl bg-background-secondary border border-border-subtle hover:border-error-red hover:bg-error-red/5 transition-all text-left group"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-error-red/20 flex items-center justify-center">
                            <RotateCcw className="w-5 h-5 text-error-red" />
                          </div>
                          <div>
                            <p className="font-medium text-text-primary">Start Fresh</p>
                            <p className="text-sm text-text-muted">Reset all data</p>
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-text-muted group-hover:text-error-red transition-colors" />
                      </div>
                    </button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        )}

        {/* Info Cards */}
        {!hasResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid md:grid-cols-3 gap-4 mt-8"
          >
            {[
              {
                icon: Target,
                title: 'Real Data',
                description: 'CDS 2025 acceptance rates and Chetty 2023 mobility data',
              },
              {
                icon: TrendingUp,
                title: '58 Attributes',
                description: 'Comprehensive analysis across aptitude, passion, community',
              },
              {
                icon: Rocket,
                title: 'Action Plan',
                description: 'Personalized boosters to improve your chances',
              },
            ].map((item, i) => (
              <Card key={i} padding="md">
                <CardContent className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-primary-blue/20 flex items-center justify-center flex-shrink-0">
                    <item.icon className="w-5 h-5 text-primary-blue" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{item.title}</h3>
                    <p className="text-sm text-text-muted mt-1">{item.description}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 mt-12 py-6 border-t border-border-subtle">
        <div className="max-w-6xl mx-auto px-4 text-center text-sm text-text-muted">
          <p>IvyQuest v2.2 | IvyLevel Scoring Engine v6.0</p>
          <p className="mt-1">Data Sources: Chetty (2023), CDS 2025, SFFA v. Harvard, NSC</p>
        </div>
      </footer>
    </div>
  );
}
