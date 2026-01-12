/**
 * MultiAgentsTab - Multi-Agent Chat Interface + v13.3 Dashboard
 * v13.3 - 6-agent dashboard with ReAct, Memory, HITL integration
 * v2.0 - TimeAudit, AwardsPortfolio, CrisisAlchemy features (legacy)
 */
'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Loader2, Sparkles,
  Brain, Target, Award, BookOpen, Lightbulb
} from 'lucide-react';
import { COLORS, GRADIENTS } from '@/lib/constants/design';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useMultiAgentChat, type AgentType } from '@/lib/hooks/useAgents';

// v13.3 Components
import { AgentDashboardV13 } from '@/components/agents/AgentDashboardV13';
import { NotificationBell } from '@/components/shared/NotificationBell';
import { useProfileId } from '@/lib/store/useSessionStore';

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

  // v13.3 Features
  const [activeView, setActiveView] = useState<'dashboard' | 'chat'>('dashboard');
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
      {/* v13.3 Header with View Toggle and Notifications */}
      <div
        className="border-b px-6 py-4"
        style={{ backgroundColor: BRAND_COLORS.bgPrimary, borderColor: BRAND_COLORS.borderLight }}
      >
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-bold" style={{ color: BRAND_COLORS.textHeading }}>
              Multi-Agent Intelligence
            </h2>
            <span
              className="text-xs px-2 py-1 rounded-full"
              style={{ backgroundColor: BRAND_COLORS.primaryBg, color: BRAND_COLORS.primary }}
            >
              v13.3
            </span>
          </div>
          <div className="flex items-center gap-3">
            {/* Notifications */}
            <NotificationBell profileId={profileId} />

            {/* View Toggle */}
            <div
              className="flex rounded-lg p-1"
              style={{ backgroundColor: BRAND_COLORS.bgSecondary }}
            >
              <button
                onClick={() => setActiveView('dashboard')}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                style={{
                  backgroundColor: activeView === 'dashboard' ? BRAND_COLORS.bgPrimary : 'transparent',
                  color: activeView === 'dashboard' ? BRAND_COLORS.textHeading : BRAND_COLORS.textMuted,
                  boxShadow: activeView === 'dashboard' ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
                }}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveView('chat')}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                style={{
                  backgroundColor: activeView === 'chat' ? BRAND_COLORS.bgPrimary : 'transparent',
                  color: activeView === 'chat' ? BRAND_COLORS.textHeading : BRAND_COLORS.textMuted,
                  boxShadow: activeView === 'chat' ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
                }}
              >
                Chat
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* v13.3 Dashboard View */}
      {activeView === 'dashboard' && (
        <AgentDashboardV13
          profileId={profileId}
          onAgentChat={(agentType) => {
            setActiveAgent(agentType as AgentType);
            setActiveView('chat');
          }}
        />
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
