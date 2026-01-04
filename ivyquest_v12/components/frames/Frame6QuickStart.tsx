/**
 * Frame 6: Quick Start (Top 3 Actions)
 * Uses SVG icons and Edge points - v11.0
 */
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Share2, ExternalLink, ArrowRight } from 'lucide-react';
import { ActionCard, type ActionData } from '@/components/ui/ActionCard';
import { EdgeProgress } from '@/components/quest/EdgeProgress';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { EDGE_VALUES, EDGE_TERMS } from '@/lib/constants/edge';

interface Frame6QuickStartProps {
  actions: ActionData[];
  onComplete: () => void;
  onShare?: () => void;
}

export function Frame6QuickStart({ actions, onComplete, onShare }: Frame6QuickStartProps) {
  const [isSharing, setIsSharing] = useState(false);
  const { edgePoints, userType, completeAssessment } = useSessionStore();

  const top3Actions = actions.slice(0, 3);
  const totalEdgeEarned = 5 * EDGE_VALUES.frameComplete;

  const handleShare = async () => {
    setIsSharing(true);
    try {
      // Call share API
      const response = await fetch('/api/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          studentName: 'Student',
          profileSnapshot: {},
          scores: { overall: 85, cri: 1.7, categories: {} },
          topActions: top3Actions,
        }),
      });
      const data = await response.json();
      if (data.shareUrl) {
        await navigator.clipboard.writeText(data.shareUrl);
        alert('Share link copied to clipboard!');
      }
    } catch (e) {
      console.error('Share error:', e);
    }
    setIsSharing(false);
  };

  const handleContinue = () => {
    completeAssessment();
    onComplete();
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FFF5F2] to-white">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Celebration header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 text-green-700 text-sm font-medium mb-4">
            ✓ Assessment Complete
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Your Game Plan is Ready!
          </h1>
          <p className="text-gray-600">
            Here are your top 3 actions to start building your {EDGE_TERMS.adjective.toLowerCase()} edge.
          </p>
        </motion.div>

        {/* Edge earned */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <EdgeProgress points={totalEdgeEarned} variant="full" showTier={true} />
        </motion.div>

        {/* Top 3 Actions with SVG icons */}
        <div className="space-y-4 mb-8">
          <h2 className="text-lg font-semibold text-gray-900">Quick Wins - Start Today</h2>
          {top3Actions.map((action, index) => (
            <motion.div
              key={action.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <ActionCard action={action} number={index + 1} />
            </motion.div>
          ))}
        </div>

        {/* Share with parent */}
        {userType === 'student' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="bg-gray-50 rounded-2xl p-4 mb-8"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">Share with Parent</h3>
                <p className="text-sm text-gray-500">Get them on board with your plan</p>
              </div>
              <button
                onClick={handleShare}
                disabled={isSharing}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100"
              >
                <Share2 size={16} />
                {isSharing ? 'Sharing...' : 'Share'}
              </button>
            </div>
          </motion.div>
        )}

        {/* Continue to Command Deck */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="text-center"
        >
          <button
            onClick={handleContinue}
            className="inline-flex items-center gap-2 px-8 py-4 text-white font-medium rounded-xl bg-[#641432] hover:bg-[#7a1a3d] transition-colors"
          >
            Go to Command Deck
            <ArrowRight size={18} />
          </button>
          <p className="text-sm text-gray-500 mt-3">
            Access your full game plan, awards, opportunities, and more
          </p>
        </motion.div>
      </div>
    </div>
  );
}

export default Frame6QuickStart;
