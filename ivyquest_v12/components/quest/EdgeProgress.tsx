'use client';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Award } from 'lucide-react';
import { EDGE_TERMS, EDGE_ANIMATION, getEdgeTier, getEdgeProgress, formatEdge, type EdgeTier } from '@/lib/constants/edge';

interface EdgeProgressProps { points: number; variant?: 'full' | 'badge'; showTier?: boolean; }

export function EdgeProgress({ points, variant = 'full', showTier = true }: EdgeProgressProps) {
  const [displayedPoints, setDisplayedPoints] = useState(0);
  const tier = getEdgeTier(points);
  const { nextTier, progress } = getEdgeProgress(points);

  useEffect(() => {
    const startTime = Date.now();
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progressRatio = Math.min(elapsed / EDGE_ANIMATION.countDuration, 1);
      const eased = 1 - Math.pow(1 - progressRatio, 3);
      setDisplayedPoints(Math.round(points * eased));
      if (progressRatio < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [points]);

  if (variant === 'badge') {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#FEF3C7] text-[#D97706] text-sm font-medium">
        <Award size={14} /><span>{formatEdge(displayedPoints)} {EDGE_TERMS.singular}</span>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-[#FEF3C7] flex items-center justify-center">
            <Award size={20} className="text-[#D97706]" />
          </div>
          <div>
            <span className="text-sm text-gray-500">Your {EDGE_TERMS.adjective}</span>
            <motion.div key={displayedPoints} initial={{ scale: 1.1 }} animate={{ scale: 1 }} className="text-2xl font-bold text-[#D97706]">
              {formatEdge(displayedPoints)} {EDGE_TERMS.singular}
            </motion.div>
          </div>
        </div>
        {showTier && <div className="px-3 py-1 rounded-full text-sm font-medium" style={{ backgroundColor: tier.bgColor, color: tier.color }}>{tier.name}</div>}
      </div>
      {nextTier && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1"><span>{tier.name}</span><span>{nextTier.name}</span></div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div initial={{ width: 0 }} animate={{ width: `${progress}%` }} className="h-full rounded-full" style={{ backgroundColor: tier.color }} />
          </div>
          <p className="text-xs text-gray-500 mt-1">{nextTier.minEdge - points} {EDGE_TERMS.singular} to {nextTier.name}</p>
        </div>
      )}
    </div>
  );
}

export function FrameEdgeProgress({ frameNumber, totalFrames = 6, edgeEarned }: { frameNumber: number; totalFrames?: number; edgeEarned: number }) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-500">Frame {frameNumber} of {totalFrames}</span>
        <div className="flex gap-1">
          {[...Array(totalFrames)].map((_, i) => (
            <div key={i} className={`w-2 h-2 rounded-full ${i < frameNumber ? 'bg-[#641432]' : 'bg-gray-300'}`} />
          ))}
        </div>
      </div>
      <div className="h-4 w-px bg-gray-300" />
      <EdgeProgress points={edgeEarned} variant="badge" />
    </div>
  );
}
export default EdgeProgress;
