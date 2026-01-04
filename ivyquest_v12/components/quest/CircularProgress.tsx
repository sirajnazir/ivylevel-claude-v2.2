'use client';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CATEGORY_SCORE_ICONS } from '@/lib/constants/icons';

interface CircularProgressProps {
  value: number; max?: number; size?: number; strokeWidth?: number; color?: string;
  showValue?: boolean; animated?: boolean; label?: string; duration?: number;
}

export function CircularProgress({ value, max = 100, size = 120, strokeWidth = 10, color = '#641432',
  showValue = true, animated = true, label, duration = 1500 }: CircularProgressProps) {
  const [progress, setProgress] = useState(animated ? 0 : value);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const percentage = Math.min(100, Math.max(0, (progress / max) * 100));
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  useEffect(() => {
    if (!animated) { setProgress(value); return; }
    const startTime = Date.now();
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progressRatio = Math.min(elapsed / duration, 1);
      setProgress(value * (1 - Math.pow(1 - progressRatio, 3)));
      if (progressRatio < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [value, animated, duration]);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="#E5E7EB" strokeWidth={strokeWidth} />
        <motion.circle cx={size/2} cy={size/2} r={radius} fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset}
          initial={{ strokeDashoffset: circumference }} animate={{ strokeDashoffset }} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {showValue && <span className="text-2xl font-bold" style={{ color }}>{Math.round(progress)}</span>}
        {label && <span className="text-xs text-gray-500 mt-0.5">{label}</span>}
      </div>
    </div>
  );
}

export function CategoryScoreRing({ category, score, size = 100 }: { category: 'aptitude'|'passion'|'service'|'identity'; score: number; size?: number }) {
  const config = CATEGORY_SCORE_ICONS[category];
  const Icon = config.icon;
  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <CircularProgress value={score} size={size} color={config.color} showValue={true} />
        <div className="absolute inset-0 flex items-center justify-center">
          <Icon size={size * 0.2} style={{ color: config.color }} className="mb-8" />
        </div>
      </div>
      <span className="text-sm font-medium text-gray-700 mt-2">{config.label}</span>
    </div>
  );
}

export function CategoryScoresQuadrant({ scores, size = 80 }: { scores: { aptitude: number; passion: number; service: number; identity: number }; size?: number }) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <CategoryScoreRing category="aptitude" score={scores.aptitude} size={size} />
      <CategoryScoreRing category="passion" score={scores.passion} size={size} />
      <CategoryScoreRing category="service" score={scores.service} size={size} />
      <CategoryScoreRing category="identity" score={scores.identity} size={size} />
    </div>
  );
}
export default CircularProgress;
