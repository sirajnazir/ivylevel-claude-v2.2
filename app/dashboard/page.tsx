/**
 * Command Deck Dashboard - v12.0
 * Tabbed interface matching original frontend specification
 */
'use client';

import { useState, useEffect, Suspense, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';
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

// ============================================================================
// SCORING CALCULATION FUNCTIONS (Same as Frame6ProfileReveal)
// ============================================================================

const hasValue = (val: any) => val !== null && val !== undefined && val !== 0 && val !== '';

function calculateAptitudeScore(profile: any): number {
  const apt = profile.aptitude;
  if (!apt) return 0;

  let total = 0;
  let count = 0;

  const gpa = apt.gpa_weighted ?? apt.gpa_unweighted;
  if (hasValue(gpa) && gpa > 0) {
    const gpaMax = apt.gpa_weighted ? 5.0 : 4.0;
    total += (gpa / gpaMax) * 100;
    count++;
  }

  if (hasValue(apt.sat_total) && apt.sat_total > 0) {
    total += (apt.sat_total / 1600) * 100;
    count++;
  }

  if (hasValue(apt.act_total) && apt.act_total > 0) {
    total += (apt.act_total / 36) * 100;
    count++;
  }

  if (hasValue(apt.ap_count) && apt.ap_count > 0) {
    total += Math.min((apt.ap_count / 12) * 100, 100);
    count++;
  }

  return count > 0 ? Math.round(total / count) : 0;
}

function calculatePassionScore(profile: any): number {
  const pass = profile.passion;
  if (!pass) return 0;

  let score = 0;

  const ecYears = pass.ec_commitment_years;
  if (hasValue(ecYears) && ecYears > 0) {
    score += Math.min((ecYears / 4) * 40, 40);
  }

  const leadership = pass.leadership_level;
  if (leadership && leadership !== 'PARTICIPANT') {
    score += 30;
  }

  const awards = pass.ec_awards;
  if (Array.isArray(awards) && awards.length > 0) {
    score += 30;
  }

  return Math.round(score);
}

function calculateServiceScore(profile: any): number {
  const community = profile.community;
  if (!community || !hasValue(community.service_hours) || community.service_hours === 0) {
    return 0;
  }
  return Math.round(Math.min((community.service_hours / 300) * 100, 100));
}

function calculateIdentityScore(profile: any): number {
  let score = 0;

  if (hasValue(profile.operating?.favoriteSubject)) {
    score += 25;
  }

  const strengths = profile.operating?.strengths;
  if (Array.isArray(strengths) && strengths.length > 0) {
    score += 25;
  }

  const career = profile.operating?.careerDirection;
  if (career && career !== 'no-idea' && career !== '') {
    score += 25;
  }

  if (profile.demographics?.first_gen === true) {
    score += 25;
  }

  return score;
}

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
  const results = useResultsStore((s) => s.results);
  const ivyScore = useResultsStore((s) => s.ivy_score);
  const helpingFactors = useResultsStore((s) => s.helping_factors);
  const holdingBackFactors = useResultsStore((s) => s.holding_back_factors);
  const schoolProbabilities = useResultsStore((s) => s.school_probabilities);
  const [activeTab, setActiveTab] = useState<TabId>('assessment');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect if assessment not complete
  useEffect(() => {
    if (mounted && !is_completed) {
      router.replace('/quest/1');
    }
  }, [is_completed, router, mounted]);

  const handleLogout = () => {
    router.push('/');
  };

  // Calculate dynamic assessment data from student profile
  const assessmentData = useMemo(() => {
    // Calculate pillar scores from the actual student profile
    const aptitudeScore = calculateAptitudeScore(studentProfile);
    const passionScore = calculatePassionScore(studentProfile);
    const serviceScore = calculateServiceScore(studentProfile);
    const identityScore = calculateIdentityScore(studentProfile);

    // Calculate overall score as average of pillars
    const overallScore = Math.round((aptitudeScore + passionScore + serviceScore + identityScore) / 4);
    const tier = getTierFromScore(overallScore);

    // Generate strengths from helping factors or profile analysis
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

    // Generate weak spots from holding back factors or profile gaps
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

    // Get target schools from school probabilities or profile
    const targetSchools = schoolProbabilities.length > 0
      ? schoolProbabilities.slice(0, 4).map((s) => s.school_id)
      : studentProfile.target_schools || ['Harvard', 'Stanford', 'MIT', 'Yale'];

    // Calculate admissions rubric metrics
    const avgProbability = schoolProbabilities.length > 0
      ? Math.round(schoolProbabilities.reduce((sum, s) => sum + (s.p_final || 0) * 100, 0) / schoolProbabilities.length)
      : Math.round(overallScore * 0.35); // Estimate based on overall score

    return {
      ivyReadyScore: {
        overall: overallScore,
        tier,
        changeVs180Days: 0, // TODO: Implement historical comparison
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
      criMultiplier: studentProfile.demographics?.first_gen ? 1.3 : 1.0,
    };
  }, [studentProfile, helpingFactors, holdingBackFactors, schoolProbabilities]);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'assessment':
        return <AssessmentTab data={assessmentData} />;
      case 'gameplan':
        return <GamePlanTab data={mockGamePlanData} />;
      case 'preparation':
        return <PreparationTab weeks={mockPreparationData.weeks} currentWeek={mockPreparationData.currentWeek} />;
      case 'growth':
        return <GrowthTab events={mockGrowthData.events} totalGrowth={mockGrowthData.totalGrowth} />;
      case 'multiagents':
        return <MultiAgentsTab />;
      default:
        return <AssessmentTab data={assessmentData} />;
    }
  };

  if (!mounted) {
    return <DashboardLoading />;
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
