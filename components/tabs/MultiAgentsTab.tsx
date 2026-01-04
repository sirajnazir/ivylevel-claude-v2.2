/**
 * MultiAgentsTab - Multi-Agent Chat Interface
 * v12.0 - Matches original frontend specification
 */
'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Bot, User, Loader2, Sparkles,
  Brain, Target, Award, BookOpen, Lightbulb
} from 'lucide-react';
import { COLORS, GRADIENTS } from '@/lib/constants/design';

interface Agent {
  id: string;
  name: string;
  specialty: string;
  icon: React.ReactNode;
  color: string;
}

interface Message {
  id: string;
  agentId: string;
  content: string;
  timestamp: Date;
  isUser: boolean;
}

const AGENTS: Agent[] = [
  { id: 'strategist', name: 'Strategist', specialty: 'Long-term planning', icon: <Target size={16} />, color: '#667eea' },
  { id: 'advisor', name: 'Academic Advisor', specialty: 'Course selection', icon: <Brain size={16} />, color: '#8b5cf6' },
  { id: 'awards', name: 'Awards Scout', specialty: 'Scholarships & competitions', icon: <Award size={16} />, color: '#f59e0b' },
  { id: 'narrative', name: 'Story Coach', specialty: 'Personal narrative', icon: <BookOpen size={16} />, color: '#10b981' },
  { id: 'creative', name: 'Innovation Guide', specialty: 'Unique opportunities', icon: <Lightbulb size={16} />, color: '#ec4899' },
];

export function MultiAgentsTab() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeAgents, setActiveAgents] = useState<string[]>(['strategist']);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      agentId: 'user',
      content: input,
      timestamp: new Date(),
      isUser: true,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate multi-agent responses
    for (const agentId of activeAgents) {
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

      const agent = AGENTS.find(a => a.id === agentId);
      if (!agent) continue;

      const agentMessage: Message = {
        id: `${Date.now()}-${agentId}`,
        agentId,
        content: getAgentResponse(agentId, input),
        timestamp: new Date(),
        isUser: false,
      };

      setMessages(prev => [...prev, agentMessage]);
    }

    setIsLoading(false);
  };

  const toggleAgent = (agentId: string) => {
    setActiveAgents(prev =>
      prev.includes(agentId)
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  return (
    <div className="h-[calc(100vh-64px)] flex">
      {/* Agent Selector Sidebar */}
      <div className="w-64 border-r bg-gray-50 p-4" style={{ borderColor: COLORS.borderDefault }}>
        <h3 className="text-sm font-semibold mb-4" style={{ color: COLORS.textHeading }}>
          Active Agents
        </h3>
        <div className="space-y-2">
          {AGENTS.map(agent => (
            <button
              key={agent.id}
              onClick={() => toggleAgent(agent.id)}
              className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors text-left ${
                activeAgents.includes(agent.id) ? 'bg-white shadow-sm' : 'hover:bg-white/50'
              }`}
              style={{
                borderLeft: activeAgents.includes(agent.id) ? `3px solid ${agent.color}` : '3px solid transparent',
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
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <Sparkles size={48} style={{ color: COLORS.textMuted }} className="mx-auto mb-4" />
              <h3 className="font-semibold" style={{ color: COLORS.textHeading }}>
                Multi-Agent Intelligence
              </h3>
              <p className="text-sm mt-2" style={{ color: COLORS.textSecondary }}>
                Ask a question and get perspectives from multiple specialized agents
              </p>
            </div>
          )}

          <AnimatePresence>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-2 text-sm"
              style={{ color: COLORS.textMuted }}
            >
              <Loader2 size={16} className="animate-spin" />
              Agents are thinking...
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
              placeholder="Ask your agents anything..."
              className="flex-1 px-4 py-3 rounded-xl border focus:outline-none focus:ring-2 focus:ring-purple-500"
              style={{ borderColor: COLORS.borderDefault }}
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="p-3 rounded-xl text-white disabled:opacity-50 transition-colors"
              style={{ background: GRADIENTS.purple }}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
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
  if (!agent) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: `${agent.color}20` }}
      >
        <span style={{ color: agent.color }}>{agent.icon}</span>
      </div>
      <div className="max-w-xl">
        <span
          className="text-xs font-medium"
          style={{ color: agent.color }}
        >
          {agent.name}
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

// Mock responses
function getAgentResponse(agentId: string, query: string): string {
  const responses: Record<string, string> = {
    strategist: `Based on your profile, I recommend focusing on building a clear narrative spike. Consider deepening your involvement in your strongest activity area over the next 6 months.`,
    advisor: `For your academic trajectory, I suggest balancing rigor with strategic course selection. Advanced courses in your interest areas will strengthen your application.`,
    awards: `I've identified several competitions and scholarships that match your profile. The deadline for the national competition in your field is coming up in 8 weeks.`,
    narrative: `Your unique story has compelling elements. Let's work on connecting your experiences into a cohesive narrative that showcases your growth and potential impact.`,
    creative: `Have you considered creating a project that combines your interests? An innovative initiative could set you apart and demonstrate leadership.`,
  };
  return responses[agentId] || 'I\'m here to help with your college journey.';
}

export default MultiAgentsTab;
