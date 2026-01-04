'use client';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, X, Sparkles, Lightbulb, Shield, FileText, CheckCircle2 } from 'lucide-react';
import { INSIGHT_ICONS } from '@/lib/constants/icons';

export type InsightSeverity = 'positive' | 'suggestion' | 'warning' | 'neutral';
export interface Insight { id: string; type: InsightSeverity; category: string; message: string; detail?: string; actionable: boolean; action?: { label: string; handler: string; }; }

interface InsightsPanelProps { insights: Insight[]; position?: 'bottom' | 'side'; title?: string; }

export function InsightsPanel({ insights, position = 'bottom', title = 'Insights' }: InsightsPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());
  const visibleInsights = insights.filter(i => !dismissedIds.has(i.id));
  if (visibleInsights.length === 0) return null;

  return (
    <div className={`rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden ${position === 'side' ? 'w-80 max-h-[400px]' : 'w-full max-h-[300px]'}`}>
      <button onClick={() => setIsExpanded(!isExpanded)} className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-[#641432]" />
          <span className="font-medium text-gray-900">{title}</span>
          <span className="px-2 py-0.5 text-xs rounded-full bg-gray-200 text-gray-600">{visibleInsights.length}</span>
        </div>
        <ChevronDown size={18} className={`text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
      </button>
      <AnimatePresence>
        {isExpanded && (
          <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-y-auto" style={{ maxHeight: position === 'side' ? '340px' : '240px' }}>
            <div className="p-3 space-y-2">
              {visibleInsights.map((insight, idx) => {
                const config = INSIGHT_ICONS[insight.type];
                const Icon = config.icon;
                return (
                  <motion.div key={insight.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }}
                    className="rounded-xl p-3 relative group" style={{ backgroundColor: config.bgColor }}>
                    <button onClick={() => setDismissedIds(prev => new Set([...prev, insight.id]))}
                      className="absolute top-2 right-2 p-1 rounded-full opacity-0 group-hover:opacity-100 hover:bg-white/50">
                      <X size={14} className="text-gray-400" />
                    </button>
                    <div className="flex gap-3">
                      <Icon size={18} style={{ color: config.color }} />
                      <div>
                        <span className="text-[10px] font-medium uppercase tracking-wider opacity-60 mb-1 block">{insight.category}</span>
                        <p className="text-sm text-gray-800">{insight.message}</p>
                        {insight.detail && <p className="text-xs text-gray-600 mt-1">{insight.detail}</p>}
                        {insight.actionable && insight.action && (
                          <button className="mt-2 text-xs font-medium flex items-center gap-1" style={{ color: config.color }}>
                            {insight.action.label} <CheckCircle2 size={12} />
                          </button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
export default InsightsPanel;
