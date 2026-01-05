/**
 * Command Deck Dashboard - v12.0
 * Tabbed interface matching original frontend specification
 */
'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { TabHeader } from '@/components/shared/TabHeader';
import { AssessmentTab } from '@/components/tabs/AssessmentTab';
import { GamePlanTab } from '@/components/tabs/GamePlanTab';
import { PreparationTab } from '@/components/tabs/PreparationTab';
import { GrowthTab } from '@/components/tabs/GrowthTab';
import { MultiAgentsTab } from '@/components/tabs/MultiAgentsTab';
import { type TabId, COLORS } from '@/lib/constants/design';

// Mock data - replace with API calls in production
const mockAssessmentData = {
  ivyReadyScore: {
    overall: 85,
    tier: 'GOLD',
    changeVs180Days: 12,
  },
  pillars: {
    aptitude: 95,
    passion: 100,
    service: 100,
    identity: 50,
  },
  dimensionalScores: [
    { dimension: 'Academic Rigor', score: 92, tier: 'Excellent' },
    { dimension: 'Leadership', score: 85, tier: 'Strong' },
    { dimension: 'Creativity', score: 78, tier: 'Good' },
    { dimension: 'Community Impact', score: 88, tier: 'Strong' },
    { dimension: 'Research', score: 72, tier: 'Developing' },
    { dimension: 'Athletics', score: 65, tier: 'Developing' },
    { dimension: 'Arts', score: 80, tier: 'Strong' },
    { dimension: 'Global Perspective', score: 75, tier: 'Good' },
  ],
  strengths: [
    { title: 'STEM Research Excellence', roi: 4.2, impact: 'High admission boost' },
    { title: 'Leadership in Robotics Club', roi: 3.8, impact: 'Strong spike demonstration' },
    { title: 'Community Tutoring Program', roi: 2.5, impact: 'Service differentiation' },
  ],
  weakSpots: [
    { title: 'Personal Essay Development', priority: 'P0' as const, description: 'Narrative needs stronger hook and personal voice' },
    { title: 'Arts/Humanities Balance', priority: 'P1' as const, description: 'Add humanities engagement to balance STEM focus' },
    { title: 'Interview Preparation', priority: 'P2' as const, description: 'Practice structured responses for school interviews' },
  ],
  admissionsRubric: {
    academicIndex: 94,
    extracurricularRating: 88,
    personalQualities: 72,
    recommendationStrength: 85,
    overallAdmitProbability: 28,
    targetSchools: ['MIT', 'Stanford', 'CMU', 'Berkeley'],
  },
  criMultiplier: 1.7,
};

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

  const renderTabContent = () => {
    switch (activeTab) {
      case 'assessment':
        return <AssessmentTab data={mockAssessmentData} />;
      case 'gameplan':
        return <GamePlanTab data={mockGamePlanData} />;
      case 'preparation':
        return <PreparationTab weeks={mockPreparationData.weeks} currentWeek={mockPreparationData.currentWeek} />;
      case 'growth':
        return <GrowthTab events={mockGrowthData.events} totalGrowth={mockGrowthData.totalGrowth} />;
      case 'multiagents':
        return <MultiAgentsTab />;
      default:
        return <AssessmentTab data={mockAssessmentData} />;
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
