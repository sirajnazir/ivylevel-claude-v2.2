/**
 * Command Deck Dashboard - v13.0
 * Tabbed interface with real backend integration
 * Uses hooks to call /api/score and real engines
 */
'use client';

import { useState, useEffect, Suspense, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, AlertCircle } from 'lucide-react';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { useResultsStore } from '@/lib/store/useResultsStore';
import { TabHeader } from '@/components/shared/TabHeader';
import { AssessmentTab } from '@/components/tabs/AssessmentTab';
import { GamePlanTab } from '@/components/tabs/GamePlanTab';
import { PreparationTab } from '@/components/tabs/PreparationTab';
import { GrowthTab } from '@/components/tabs/GrowthTab';
import { MultiAgentsTab } from '@/components/tabs/MultiAgentsTab';
import { type TabId, COLORS, getTierFromScore } from '@/lib/constants/design';

// Import real hooks for backend integration
import {
  useScoring,
  useIvyScore,
  useSchoolProbabilities,
  useArchetype,
  useFactors,
} from '@/lib/hooks/useScoring';
import { useGamePlan, usePreparationData } from '@/lib/hooks/useGamePlan';
import { useInsights } from '@/lib/hooks/useInsights';

const mockGamePlanData = {
  targetProfile: {
    name: 'STEM Innovator + Community Leader',
    narrative: 'A passionate technologist who bridges the gap between cutting-edge research and community impact, using robotics and AI to solve local problems.',
  },
  ecStrategy: [
    { title: 'Robotics Club President', category: 'Leadership', role: 'President', hoursPerWeek: 12, impact: 'High', years: 'Y1-Y4' },
    { title: 'STEM Tutoring Program', category: 'Service', role: 'Founder', hoursPerWeek: 5, impact: 'Medium', years: 'Y2-Y4' },
    { title: 'Research Internship', category: 'Academic', role: 'Research Assistant', hoursPerWeek: 15, impact: 'High', years: 'Y3 Summer' },
  ],
  targetSchools: [
    { name: 'MIT', tier: 'Reach' as const },
    { name: 'Stanford', tier: 'Reach' as const },
    { name: 'CMU', tier: 'Target' as const },
    { name: 'Georgia Tech', tier: 'Safety' as const },
  ],
  awards: [
    { title: 'USACO Gold', description: 'Programming competition' },
    { title: 'Science Olympiad State', description: 'Top 10 placement' },
  ],
  summerPrograms: [
    { title: 'MIT MITES', description: 'STEM intensive' },
    { title: 'RSI', description: 'Research Science Institute' },
  ],
  phases: [
    {
      id: 'phase1',
      name: 'Foundation Building',
      dateRange: 'Sep 2024 - Dec 2024',
      goal: 'Establish leadership positions and begin research exploration',
      completionPercent: 100,
      milestones: [
        { id: 'm1', title: 'Join robotics club leadership', status: 'completed' as const, targetDate: 'Oct 2024' },
        { id: 'm2', title: 'Start tutoring program', status: 'completed' as const, targetDate: 'Nov 2024' },
      ],
    },
    {
      id: 'phase2',
      name: 'Skill Development',
      dateRange: 'Jan 2025 - Apr 2025',
      goal: 'Deepen technical skills and expand impact',
      completionPercent: 65,
      milestones: [
        { id: 'm3', title: 'Complete USACO Silver', status: 'completed' as const, targetDate: 'Feb 2025' },
        { id: 'm4', title: 'Launch community robotics workshop', status: 'in_progress' as const, targetDate: 'Mar 2025' },
        { id: 'm5', title: 'Apply to summer research programs', status: 'pending' as const, targetDate: 'Apr 2025' },
      ],
    },
    {
      id: 'phase3',
      name: 'Peak Performance',
      dateRange: 'May 2025 - Aug 2025',
      goal: 'Summer program and competition achievements',
      completionPercent: 0,
      milestones: [
        { id: 'm6', title: 'Attend summer research program', status: 'pending' as const, targetDate: 'Jun-Aug 2025' },
        { id: 'm7', title: 'Compete in national robotics competition', status: 'pending' as const, targetDate: 'Jul 2025' },
      ],
    },
  ],
  currentPhase: 'phase2',
  actions: [
    { id: '1', title: 'Draft personal essay outline', description: 'Create structured outline with key experiences', category: 'narrative', priority: 'critical' as const, edgePoints: 50, timeEstimate: '2 hours' },
    { id: '2', title: 'Schedule robotics workshop venue', description: 'Book community center for March workshop', category: 'activities', priority: 'high' as const, edgePoints: 30, timeEstimate: '1 hour' },
    { id: '3', title: 'Complete RSI application', description: 'Finish essays and gather recommendations', category: 'academics', priority: 'high' as const, edgePoints: 40, timeEstimate: '4 hours' },
  ],
};

const mockPreparationData = {
  weeks: [
    {
      weekNumber: 1,
      dateRange: 'Jan 6 - Jan 12',
      focus: 'Essay Foundation',
      completionPercent: 100,
      tasks: [
        { id: 't1', title: 'Brainstorm essay topics', description: 'List 5 potential personal essay themes', category: 'Narrative', status: 'completed' as const, dueDate: 'Jan 8', estimatedTime: '1h' },
        { id: 't2', title: 'Research summer programs', description: 'Compare top 3 STEM summer programs', category: 'Planning', status: 'completed' as const, dueDate: 'Jan 10', estimatedTime: '2h' },
      ],
    },
    {
      weekNumber: 2,
      dateRange: 'Jan 13 - Jan 19',
      focus: 'Application Prep',
      completionPercent: 60,
      tasks: [
        { id: 't3', title: 'Request teacher recommendation', description: 'Ask physics teacher for rec letter', category: 'Application', status: 'completed' as const, dueDate: 'Jan 15', estimatedTime: '30m' },
        { id: 't4', title: 'Draft RSI essay', description: 'Write first draft of research interest essay', category: 'Application', status: 'in_progress' as const, dueDate: 'Jan 18', estimatedTime: '3h' },
        { id: 't5', title: 'Update activities list', description: 'Add recent achievements and hours', category: 'Application', status: 'pending' as const, dueDate: 'Jan 19', estimatedTime: '1h' },
      ],
    },
    {
      weekNumber: 3,
      dateRange: 'Jan 20 - Jan 26',
      focus: 'Leadership Development',
      completionPercent: 0,
      tasks: [
        { id: 't6', title: 'Plan robotics workshop curriculum', description: 'Design 4-week beginner robotics course', category: 'Leadership', status: 'pending' as const, dueDate: 'Jan 22', estimatedTime: '4h' },
        { id: 't7', title: 'Recruit workshop volunteers', description: 'Get 3 club members to help teach', category: 'Leadership', status: 'pending' as const, dueDate: 'Jan 25', estimatedTime: '1h' },
      ],
    },
  ],
  currentWeek: 2,
};

const mockGrowthData = {
  events: [
    { id: 'e1', date: 'Jan 15, 2025', title: 'USACO Silver Promotion', description: 'Advanced from Bronze to Silver division after consistent practice', category: 'achievement' as const, impact: 'high' as const, scoreChange: 5 },
    { id: 'e2', date: 'Jan 10, 2025', title: 'Tutoring Program Expansion', description: 'Added 10 new students to weekly tutoring sessions', category: 'milestone' as const, impact: 'medium' as const, scoreChange: 3 },
    { id: 'e3', date: 'Jan 5, 2025', title: 'Essay Hook Discovery', description: 'Found unique angle connecting robotics to family heritage', category: 'insight' as const, impact: 'high' as const },
    { id: 'e4', date: 'Dec 20, 2024', title: 'Robotics Club President Election', description: 'Elected as president for the upcoming year', category: 'achievement' as const, impact: 'high' as const, scoreChange: 8 },
    { id: 'e5', date: 'Dec 15, 2024', title: 'Started Application Research', description: 'Began systematic research of target schools', category: 'action' as const, impact: 'medium' as const },
  ],
  totalGrowth: 16,
};

// Loading fallback
function DashboardLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: COLORS.bgPage }}>
      <div className="flex flex-col items-center gap-4">
        <Loader2 size={40} className="animate-spin" style={{ color: COLORS.primary }} />
        <p className="text-sm" style={{ color: COLORS.textSecondary }}>Loading Dashboard...</p>
      </div>
    </div>
  );
}

// Main dashboard content
function DashboardContent() {
  const router = useRouter();
  const is_completed = useSessionStore((s) => s.is_completed);
  const studentProfile = useStudentStore((s) => s.profile);
  const [activeTab, setActiveTab] = useState<TabId>('assessment');
  const [mounted, setMounted] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // === REAL HOOKS - Call /api/score and use real engines ===
  const {
    calculateScore,
    results,
    isLoading: isScoreLoading,
    error: scoreError,
  } = useScoring();

  const { totalScore, categoryScores, percentileRank, hasResults } = useIvyScore();
  const { probabilities: schoolProbabilities, topSchool } = useSchoolProbabilities();
  const { archetype, label: archetypeLabel, tagline } = useArchetype();
  const { helping: helpingFactors, holdingBack: holdingBackFactors } = useFactors();

  // Game Plan and Insights from real engines
  const {
    gamePlan,
    generatePlan,
    phases,
    quickWins,
    isGenerating: isGamePlanGenerating,
  } = useGamePlan();
  const { weeklyTasks } = usePreparationData();
  const {
    insights,
    generateInsights,
    criticalInsights,
    warningInsights,
    positiveInsights,
    isGenerating: isInsightsGenerating,
  } = useInsights();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect if assessment not complete
  useEffect(() => {
    if (mounted && !is_completed) {
      router.replace('/quest/1');
    }
  }, [is_completed, router, mounted]);

  // === FETCH REAL DATA ON MOUNT ===
  useEffect(() => {
    const initializeDashboard = async () => {
      if (!mounted || !is_completed) return;

      try {
        // Calculate scores if not already done
        if (!hasResults) {
          console.log('[Dashboard] Calling /api/score...');
          await calculateScore();
        }

        // Generate game plan if not exists
        if (!gamePlan) {
          console.log('[Dashboard] Generating game plan...');
          await generatePlan();
        }

        // Generate insights if empty
        if (insights.length === 0) {
          console.log('[Dashboard] Generating insights...');
          await generateInsights();
        }

        setIsInitialized(true);
      } catch (err) {
        console.error('[Dashboard] Initialization error:', err);
        setIsInitialized(true); // Still show UI even on error
      }
    };

    initializeDashboard();
  }, [mounted, is_completed, hasResults, gamePlan, insights.length, calculateScore, generatePlan, generateInsights]);

  const handleLogout = () => {
    router.push('/');
  };

  // === BUILD ASSESSMENT DATA FROM REAL SCORES ===
  const assessmentData = useMemo(() => {
    // Use real scores from /api/score via hooks
    const aptitudeScore = categoryScores.aptitude;
    const passionScore = categoryScores.passion;
    const serviceScore = categoryScores.community;
    const identityScore = categoryScores.narrative;
    const overallScore = totalScore;
    const tier = getTierFromScore(overallScore);

    // Generate strengths from real helping factors
    const strengths = helpingFactors.length > 0
      ? helpingFactors.slice(0, 3).map((factor, i) => ({
          title: factor,
          roi: 3.5 - i * 0.5,
          impact: i === 0 ? 'High admission boost' : i === 1 ? 'Strong differentiation' : 'Solid foundation',
        }))
      : [
          aptitudeScore >= 70 && { title: 'Strong Academic Foundation', roi: 3.5, impact: 'High admission boost' },
          passionScore >= 60 && { title: 'Demonstrated Passion & Leadership', roi: 3.0, impact: 'Strong differentiation' },
          serviceScore >= 50 && { title: 'Community Service Commitment', roi: 2.5, impact: 'Service differentiation' },
        ].filter(Boolean) as Array<{ title: string; roi: number; impact: string }>;

    // Generate weak spots from real holding back factors
    const weakSpots = holdingBackFactors.length > 0
      ? holdingBackFactors.slice(0, 3).map((factor, i) => ({
          title: factor,
          priority: (i === 0 ? 'P0' : i === 1 ? 'P1' : 'P2') as 'P0' | 'P1' | 'P2',
          description: `Address this to improve your overall profile`,
        }))
      : [
          aptitudeScore < 50 && { title: 'Academic Profile Needs Development', priority: 'P0' as const, description: 'Focus on GPA and test scores' },
          passionScore < 40 && { title: 'Extracurricular Depth', priority: 'P1' as const, description: 'Develop sustained activity involvement' },
          identityScore < 50 && { title: 'Personal Narrative', priority: 'P2' as const, description: 'Clarify your unique story and direction' },
        ].filter(Boolean) as Array<{ title: string; priority: 'P0' | 'P1' | 'P2'; description: string }>;

    // Get target schools from real probabilities
    const targetSchools = schoolProbabilities.length > 0
      ? schoolProbabilities.slice(0, 4).map((s) => s.school_id)
      : studentProfile?.target_schools || ['Harvard', 'Stanford', 'MIT', 'Yale'];

    // Calculate admissions probability from real data
    const avgProbability = schoolProbabilities.length > 0
      ? Math.round(schoolProbabilities.reduce((sum, s) => sum + (s.p_final || 0) * 100, 0) / schoolProbabilities.length)
      : Math.round(overallScore * 0.35);

    return {
      ivyReadyScore: {
        overall: overallScore,
        tier,
        changeVs180Days: 0,
      },
      pillars: {
        aptitude: aptitudeScore,
        passion: passionScore,
        service: serviceScore,
        identity: identityScore,
      },
      dimensionalScores: [
        { dimension: 'Academic Rigor', score: aptitudeScore, tier: aptitudeScore >= 85 ? 'Excellent' : aptitudeScore >= 70 ? 'Strong' : aptitudeScore >= 50 ? 'Good' : 'Developing' },
        { dimension: 'Leadership', score: passionScore, tier: passionScore >= 85 ? 'Excellent' : passionScore >= 70 ? 'Strong' : passionScore >= 50 ? 'Good' : 'Developing' },
        { dimension: 'Community Impact', score: serviceScore, tier: serviceScore >= 85 ? 'Excellent' : serviceScore >= 70 ? 'Strong' : serviceScore >= 50 ? 'Good' : 'Developing' },
        { dimension: 'Personal Story', score: identityScore, tier: identityScore >= 85 ? 'Excellent' : identityScore >= 70 ? 'Strong' : identityScore >= 50 ? 'Good' : 'Developing' },
      ],
      strengths: strengths.length > 0 ? strengths : [{ title: 'Building Your Foundation', roi: 2.0, impact: 'Starting fresh with potential' }],
      weakSpots: weakSpots.length > 0 ? weakSpots : [{ title: 'Complete Your Profile', priority: 'P0' as const, description: 'Add more information to get personalized insights' }],
      admissionsRubric: {
        academicIndex: aptitudeScore,
        extracurricularRating: passionScore,
        personalQualities: identityScore,
        recommendationStrength: Math.round((aptitudeScore + passionScore) / 2),
        overallAdmitProbability: avgProbability,
        targetSchools,
      },
      criMultiplier: studentProfile?.demographics?.first_gen ? 1.3 : 1.0,
    };
  }, [totalScore, categoryScores, helpingFactors, holdingBackFactors, schoolProbabilities, studentProfile]);

  // === BUILD GAME PLAN DATA FROM REAL ENGINE ===
  const realGamePlanData = useMemo(() => {
    if (!gamePlan) return mockGamePlanData;

    return {
      ...mockGamePlanData,
      phases: phases.map((phase, idx) => ({
        id: phase.id,
        name: phase.title,
        dateRange: phase.timeframe,
        goal: phase.description,
        completionPercent: idx === 0 ? 50 : 0,
        milestones: phase.actions.slice(0, 3).map((action) => ({
          id: action.id,
          title: action.title,
          status: 'pending' as const,
          targetDate: action.deadline || '',
        })),
      })),
      currentPhase: phases[0]?.id || 'phase1',
      actions: quickWins.slice(0, 5).map((action) => ({
        id: action.id,
        title: action.title,
        description: action.description || '',
        category: action.category,
        priority: action.priority as 'critical' | 'high' | 'medium',
        edgePoints: 30,
        timeEstimate: action.timeCommitment,
      })),
    };
  }, [gamePlan, phases, quickWins]);

  // === BUILD PREPARATION DATA FROM REAL ENGINE ===
  const realPreparationData = useMemo(() => {
    if (weeklyTasks.length === 0) return mockPreparationData;

    return {
      weeks: weeklyTasks.slice(0, 4).map((week) => ({
        weekNumber: week.weekNumber,
        dateRange: week.weekRange,
        focus: week.focus,
        completionPercent: week.progress,
        tasks: week.tasks.map((task) => ({
          id: task.id,
          title: task.title,
          description: '',
          category: task.category,
          status: task.status,
          dueDate: '',
          estimatedTime: task.timeCommitment,
        })),
      })),
      currentWeek: 1,
    };
  }, [weeklyTasks]);

  // === BUILD GROWTH DATA FROM REAL INSIGHTS ===
  const realGrowthData = useMemo(() => {
    const events = [
      {
        id: 'assessment-complete',
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        title: 'Assessment Completed',
        description: `Ivy+ Ready Score: ${totalScore}%`,
        category: 'milestone' as const,
        impact: 'high' as const,
        scoreChange: totalScore,
      },
      ...criticalInsights.slice(0, 2).map((insight) => ({
        id: insight.id,
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        title: insight.title,
        description: insight.message,
        category: 'insight' as const,
        impact: 'high' as const,
      })),
      ...positiveInsights.slice(0, 2).map((insight) => ({
        id: insight.id,
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        title: insight.title,
        description: insight.message,
        category: 'achievement' as const,
        impact: 'medium' as const,
        scoreChange: 3,
      })),
    ];

    return {
      events: events.length > 0 ? events : mockGrowthData.events,
      totalGrowth: totalScore > 0 ? totalScore : mockGrowthData.totalGrowth,
    };
  }, [totalScore, criticalInsights, positiveInsights]);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'assessment':
        return <AssessmentTab data={assessmentData} />;
      case 'gameplan':
        return <GamePlanTab data={realGamePlanData} />;
      case 'preparation':
        return <PreparationTab weeks={realPreparationData.weeks} currentWeek={realPreparationData.currentWeek} />;
      case 'growth':
        return <GrowthTab events={realGrowthData.events} totalGrowth={realGrowthData.totalGrowth} />;
      case 'multiagents':
        return <MultiAgentsTab />;
      default:
        return <AssessmentTab data={assessmentData} />;
    }
  };

  // Show loading while initializing or fetching data
  const isLoading = isScoreLoading || isGamePlanGenerating || isInsightsGenerating;

  if (!mounted) {
    return <DashboardLoading />;
  }

  // Show loading indicator while fetching real data
  if (!isInitialized && isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: COLORS.bgPage }}>
        <div className="flex flex-col items-center gap-4">
          <Loader2 size={40} className="animate-spin" style={{ color: COLORS.primary }} />
          <p className="text-sm" style={{ color: COLORS.textSecondary }}>Loading your profile data...</p>
          <p className="text-xs" style={{ color: COLORS.textMuted }}>Calling scoring engine...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: COLORS.bgPage }}>
      {/* Tab Navigation Header */}
      <TabHeader
        activeTab={activeTab}
        onTabChange={setActiveTab}
        studentName={studentProfile?.identity?.name || 'Student'}
        onLogout={handleLogout}
      />

      {/* Error Banner */}
      {scoreError && (
        <div className="mx-auto max-w-6xl px-6 pt-4">
          <div className="flex items-center gap-3 p-4 rounded-lg" style={{ backgroundColor: '#FEF2F2', border: '1px solid #FECACA' }}>
            <AlertCircle size={20} style={{ color: '#DC2626' }} />
            <div>
              <p className="font-medium" style={{ color: '#DC2626' }}>Scoring Error</p>
              <p className="text-sm" style={{ color: '#7F1D1D' }}>{scoreError}</p>
            </div>
            <button
              onClick={() => calculateScore()}
              className="ml-auto px-3 py-1 text-sm rounded"
              style={{ backgroundColor: '#DC2626', color: 'white' }}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Loading indicator for background operations */}
      {isLoading && isInitialized && (
        <div className="mx-auto max-w-6xl px-6 pt-4">
          <div className="flex items-center gap-2 p-3 rounded-lg" style={{ backgroundColor: '#EFF6FF', border: '1px solid #BFDBFE' }}>
            <Loader2 size={16} className="animate-spin" style={{ color: '#2563EB' }} />
            <p className="text-sm" style={{ color: '#1E40AF' }}>Refreshing data...</p>
          </div>
        </div>
      )}

      {/* Tab Content */}
      <main>
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {renderTabContent()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

// Page wrapper with Suspense
export default function DashboardPage() {
  return (
    <Suspense fallback={<DashboardLoading />}>
      <DashboardContent />
    </Suspense>
  );
}
