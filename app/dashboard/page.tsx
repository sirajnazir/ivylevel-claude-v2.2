/**
 * Command Deck Dashboard Page
 * Post-assessment home for returning users.
 * Houses all v10.0 agent UIs in unified dashboard.
 * @version 10.0
 */

'use client';

import { Suspense, useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  LayoutDashboard, Target, AlertTriangle, ListTodo,
  Trophy, Radar, Sparkles, Phone, RefreshCw, Loader2
} from 'lucide-react';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { MissionControl } from '@/components/dashboard/MissionControl';
import { CrisisCenter } from '@/components/dashboard/CrisisCenter';
import { GamePlanFull } from '@/components/dashboard/GamePlanFull';
import { AwardTracker } from '@/components/dashboard/AwardTracker';
import { OpportunityRadar } from '@/components/dashboard/OpportunityRadar';
import { NarrativeLab } from '@/components/dashboard/NarrativeLab';
import { CoachConnect } from '@/components/dashboard/CoachConnect';
import { AIChatInterface } from '@/components/v10/AIChatInterface';
import { AISuggestionBubbles } from '@/components/v10/AISuggestionBubbles';
import { useCommandDeckData } from '@/lib/hooks/useAgentAPI';
import { useAgentDataCache } from '@/lib/store/useSessionStore';
import { getFeatureFlags } from '@/lib/config/featureFlags';
import { BRAND_COLORS } from '@/lib/constants/brand';

// Loading fallback for Suspense
function DashboardLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: BRAND_COLORS.bgSecondary }}>
      <div className="flex flex-col items-center gap-4">
        <Loader2 size={40} className="animate-spin" style={{ color: BRAND_COLORS.primary }} />
        <p className="text-sm" style={{ color: BRAND_COLORS.textSecondary }}>Loading Command Deck...</p>
      </div>
    </div>
  );
}

// Main dashboard content component
function DashboardContent() {
  const searchParams = useSearchParams();
  const startActionId = searchParams.get('startAction');
  const flags = getFeatureFlags();
  const agentCache = useAgentDataCache();

  const { loading, executionData, awardsData, opportunitiesData, fetchAll } = useCommandDeckData();
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock profile for demo (would come from store in real app)
  const mockProfile = {};

  // Fetch data on mount
  useEffect(() => {
    if (flags.v10Agents) {
      fetchAll(mockProfile);
    }
  }, [flags.v10Agents]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchAll(mockProfile);
    setIsRefreshing(false);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: BRAND_COLORS.bgSecondary }}>
      {/* Header */}
      <DashboardHeader
        cri={agentCache.cri}
        criBoost={agentCache.criBoostPercentage}
        archetype={agentCache.archetype}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Refresh Button */}
        <div className="flex justify-end mb-4">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || loading}
            className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
            style={{ color: BRAND_COLORS.textSecondary }}
          >
            <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Mission Control - Spans 2 columns */}
          <DashboardSection
            title="Mission Control"
            subtitle="Active projects & tasks"
            icon={Target}
            className="md:col-span-2"
            delay={0}
          >
            <MissionControl
              loading={loading}
              data={executionData}
              highlightActionId={startActionId}
            />
          </DashboardSection>

          {/* Crisis Center */}
          <DashboardSection
            title="Crisis Center"
            subtitle="Crisis alchemy responses"
            icon={AlertTriangle}
            delay={0.1}
          >
            <CrisisCenter />
          </DashboardSection>

          {/* Full Game Plan - Spans 2 columns */}
          <DashboardSection
            title="Full Game Plan"
            subtitle="All actions by phase"
            icon={ListTodo}
            className="md:col-span-2"
            delay={0.2}
          >
            <GamePlanFull />
          </DashboardSection>

          {/* Award Tracker */}
          <DashboardSection
            title="Award Tracker"
            subtitle="Matched scholarships"
            icon={Trophy}
            delay={0.3}
          >
            <AwardTracker
              loading={loading}
              data={awardsData}
            />
          </DashboardSection>

          {/* Opportunity Radar */}
          <DashboardSection
            title="Opportunity Radar"
            subtitle="Programs & competitions"
            icon={Radar}
            delay={0.4}
          >
            <OpportunityRadar
              loading={loading}
              data={opportunitiesData}
            />
          </DashboardSection>

          {/* Narrative Lab */}
          <DashboardSection
            title="Narrative Lab"
            subtitle="Your story DNA"
            icon={Sparkles}
            delay={0.5}
          >
            <NarrativeLab
              narrativeDna={agentCache.narrativeDna}
              archetype={agentCache.archetype}
              themes={agentCache.narrativeThemes}
            />
          </DashboardSection>

          {/* Coach Connect */}
          <DashboardSection
            title="Coach Connect"
            subtitle="Book a strategy call"
            icon={Phone}
            delay={0.6}
          >
            <CoachConnect />
          </DashboardSection>
        </div>
      </main>

      {/* Floating AI Elements */}
      {flags.aiChat && <AIChatInterface />}
      {flags.suggestions && <AISuggestionBubbles />}
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

interface DashboardSectionProps {
  title: string;
  subtitle: string;
  icon: React.ElementType;
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

function DashboardSection({
  title,
  subtitle,
  icon: Icon,
  children,
  className = '',
  delay = 0
}: DashboardSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`rounded-2xl bg-white border border-gray-200 shadow-sm overflow-hidden ${className}`}
    >
      {/* Section Header */}
      <div
        className="px-5 py-4 border-b border-gray-100 flex items-center gap-3"
        style={{ backgroundColor: BRAND_COLORS.bgSecondary }}
      >
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: BRAND_COLORS.primaryBg }}
        >
          <Icon size={20} style={{ color: BRAND_COLORS.primary }} />
        </div>
        <div>
          <h2 className="font-semibold text-gray-900">{title}</h2>
          <p className="text-xs text-gray-500">{subtitle}</p>
        </div>
      </div>

      {/* Section Content */}
      <div className="p-5">
        {children}
      </div>
    </motion.div>
  );
}
