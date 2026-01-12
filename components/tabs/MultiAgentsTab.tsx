/**
 * MultiAgentsTab - Multi-Agent Chat Interface + v13.0 Dashboard
 * v13.0 - Full agent card suite with ReAct + Memory integration
 * v2.0 - TimeAudit, AwardsPortfolio, CrisisAlchemy features
 */
'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Bot, User, Loader2, Sparkles,
  Brain, Target, Award, BookOpen, Lightbulb, Flame, Clock, Activity
} from 'lucide-react';
import { COLORS, GRADIENTS } from '@/lib/constants/design';
import { useMultiAgentChat, type AgentType } from '@/lib/hooks/useAgents';

// v2.0 Components
import { TimeAuditCardV2 } from '@/components/agents/TimeAuditCardV2';
import { AwardsPortfolioCardV2 } from '@/components/agents/AwardsPortfolioCardV2';
import { CrisisAlchemyModal } from '@/components/agents/CrisisAlchemyModal';
import { useAgentV2Health } from '@/lib/hooks/useAgentV2';
import { useProfileId } from '@/lib/store/useSessionStore';

// v13.0 Components
import { NarrativeSynthesisCard } from '@/components/agents/NarrativeSynthesisCard';
import { WeeklyPlanCard } from '@/components/agents/WeeklyPlanCard';
import { NCWITStrategyCard } from '@/components/agents/NCWITStrategyCard';
import { OpportunitiesCard } from '@/components/agents/OpportunitiesCard';

interface Agent {
  id: AgentType;
  name: string;
  specialty: string;
  icon: React.ReactNode;
  color: string;
}

const AGENTS: Agent[] = [
  { id: 'strategist', name: 'Strategist', specialty: 'Long-term planning', icon: <Target size={16} />, color: '#667eea' },
  { id: 'academic', name: 'Academic Advisor', specialty: 'Course selection', icon: <Brain size={16} />, color: '#8b5cf6' },
  { id: 'awards', name: 'Awards Scout', specialty: 'Scholarships & competitions', icon: <Award size={16} />, color: '#f59e0b' },
  { id: 'narrative', name: 'Story Coach', specialty: 'Personal narrative', icon: <BookOpen size={16} />, color: '#10b981' },
  { id: 'opportunity', name: 'Innovation Guide', specialty: 'Unique opportunities', icon: <Lightbulb size={16} />, color: '#ec4899' },
];

export function MultiAgentsTab() {
  // Use real multi-agent chat hook
  const {
    messages: chatMessages,
    activeAgent,
    setActiveAgent,
    isProcessing,
    sendMessage,
    clearMessages,
  } = useMultiAgentChat();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // v2.0 Features
  const [showCrisisModal, setShowCrisisModal] = useState(false);
  const [activeView, setActiveView] = useState<'dashboard' | 'chat'>('dashboard');
  const v2Health = useAgentV2Health();
  const profileId = useProfileId();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;

    const message = input;
    setInput('');

    // Send message via real hook (calls backend API)
    await sendMessage(message);
  };

  const selectAgent = (agentId: AgentType) => {
    setActiveAgent(agentId);
  };

  // Transform chat messages to display format
  const displayMessages = chatMessages.map((msg) => ({
    id: msg.id,
    agentId: msg.role === 'user' ? 'user' : (msg.agentType || activeAgent),
    content: msg.content,
    timestamp: new Date(msg.timestamp),
    isUser: msg.role === 'user',
  }));

  return (
    <div className="min-h-[calc(100vh-64px)]">
      {/* v2.0 Header with Backend Status and View Toggle */}
      <div className="bg-white border-b px-6 py-4" style={{ borderColor: COLORS.borderDefault }}>
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-bold" style={{ color: COLORS.textHeading }}>
              Multi-Agent Intelligence
            </h2>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
              <div className={`w-2 h-2 rounded-full ${
                v2Health.data?.status === 'healthy' ? 'bg-green-500' :
                v2Health.isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
              }`} />
              <span className="text-xs text-gray-600">
                v2.0: {v2Health.data?.status || (v2Health.isLoading ? 'connecting...' : 'offline')}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCrisisModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm font-medium"
            >
              <Flame size={16} />
              Crisis Help
            </button>
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveView('dashboard')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeView === 'dashboard' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-600'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveView('chat')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeView === 'chat' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-600'
                }`}
              >
                Chat
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* v13.0 Dashboard View */}
      {activeView === 'dashboard' && (
        <div className="p-6 max-w-6xl mx-auto space-y-6">
          {/* Row 1: Narrative + Awards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <NarrativeSynthesisCard />
            <AwardsPortfolioCardV2
              studentProfile={{
                spike: 'general',
                identity: [],
                activities: [],
                has_working_project: false,
              }}
            />
          </div>

          {/* Row 2: Time Audit + Weekly Plan */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TimeAuditCardV2 />
            <WeeklyPlanCard />
          </div>

          {/* Row 3: NCWIT + Opportunities */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <NCWITStrategyCard />
            <OpportunitiesCard
              studentProfile={{
                spike: 'general',
                primary_project: undefined,
              }}
            />
          </div>
        </div>
      )}

      {/* Chat View */}
      {activeView === 'chat' && (
    <div className="h-[calc(100vh-140px)] flex">
      {/* Agent Selector Sidebar */}
      <div className="w-64 border-r bg-gray-50 p-4" style={{ borderColor: COLORS.borderDefault }}>
        <h3 className="text-sm font-semibold mb-4" style={{ color: COLORS.textHeading }}>
          Select Agent
        </h3>
        <p className="text-xs mb-4" style={{ color: COLORS.textMuted }}>
          Choose an agent to chat with. Each agent specializes in different aspects.
        </p>
        <div className="space-y-2">
          {AGENTS.map(agent => (
            <button
              key={agent.id}
              onClick={() => selectAgent(agent.id)}
              className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors text-left ${
                activeAgent === agent.id ? 'bg-white shadow-sm' : 'hover:bg-white/50'
              }`}
              style={{
                borderLeft: activeAgent === agent.id ? `3px solid ${agent.color}` : '3px solid transparent',
              }}
            >
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ backgroundColor: `${agent.color}20` }}
              >
                <span style={{ color: agent.color }}>{agent.icon}</span>
              </div>
              <div>
                <span className="text-sm font-medium" style={{ color: COLORS.textHeading }}>
                  {agent.name}
                </span>
                <p className="text-xs" style={{ color: COLORS.textMuted }}>
                  {agent.specialty}
                </p>
              </div>
              {activeAgent === agent.id && (
                <span className="ml-auto text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: agent.color, color: 'white' }}>
                  Active
                </span>
              )}
            </button>
          ))}
        </div>

        {displayMessages.length > 0 && (
          <button
            onClick={clearMessages}
            className="mt-4 w-full text-xs py-2 rounded border"
            style={{ borderColor: COLORS.borderDefault, color: COLORS.textMuted }}
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {displayMessages.length === 0 && (
            <div className="text-center py-16">
              <Sparkles size={48} style={{ color: COLORS.textMuted }} className="mx-auto mb-4" />
              <h3 className="font-semibold" style={{ color: COLORS.textHeading }}>
                Multi-Agent Intelligence
              </h3>
              <p className="text-sm mt-2" style={{ color: COLORS.textSecondary }}>
                Ask a question and get advice from {AGENTS.find(a => a.id === activeAgent)?.name || 'the agent'}
              </p>
              <p className="text-xs mt-2" style={{ color: COLORS.textMuted }}>
                Connected to real backend agents via /api/agents
              </p>
            </div>
          )}

          <AnimatePresence>
            {displayMessages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </AnimatePresence>

          {isProcessing && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-2 text-sm"
              style={{ color: COLORS.textMuted }}
            >
              <Loader2 size={16} className="animate-spin" />
              {AGENTS.find(a => a.id === activeAgent)?.name || 'Agent'} is thinking...
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t p-4" style={{ borderColor: COLORS.borderDefault }}>
          <div className="flex items-center gap-3 max-w-3xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={`Ask ${AGENTS.find(a => a.id === activeAgent)?.name || 'the agent'} anything...`}
              className="flex-1 px-4 py-3 rounded-xl border focus:outline-none focus:ring-2 focus:ring-purple-500"
              style={{ borderColor: COLORS.borderDefault }}
              disabled={isProcessing}
            />
            <button
              onClick={handleSend}
              disabled={isProcessing || !input.trim()}
              className="p-3 rounded-xl text-white disabled:opacity-50 transition-colors"
              style={{ background: GRADIENTS.purple }}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
      )}

      {/* Crisis Alchemy Modal */}
      <CrisisAlchemyModal
        isOpen={showCrisisModal}
        onClose={() => setShowCrisisModal(false)}
        studentProfile={{ spike: 'general' }}
      />
    </div>
  );
}

interface DisplayMessage {
  id: string;
  agentId: string;
  content: string;
  timestamp: Date;
  isUser: boolean;
}

function MessageBubble({ message }: { message: DisplayMessage }) {
  if (message.isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-end"
      >
        <div
          className="max-w-xl px-4 py-3 rounded-2xl rounded-br-sm text-white"
          style={{ background: GRADIENTS.purple }}
        >
          {message.content}
        </div>
      </motion.div>
    );
  }

  const agent = AGENTS.find(a => a.id === message.agentId);
  // Fallback to strategist if agent not found
  const displayAgent = agent || AGENTS[0];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: `${displayAgent.color}20` }}
      >
        <span style={{ color: displayAgent.color }}>{displayAgent.icon}</span>
      </div>
      <div className="max-w-xl">
        <span
          className="text-xs font-medium"
          style={{ color: displayAgent.color }}
        >
          {displayAgent.name}
        </span>
        <div
          className="mt-1 px-4 py-3 rounded-2xl rounded-tl-sm bg-white border"
          style={{ borderColor: COLORS.borderDefault }}
        >
          {message.content}
        </div>
      </div>
    </motion.div>
  );
}

export default MultiAgentsTab;
