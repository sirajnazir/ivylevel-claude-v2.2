/**
 * IvyQuest v3.0 — Progress & Hint Components
 * 
 * Milestone and contextual hint UI.
 * 
 * @version 1.0.0
 * @module components/Progress
 */

'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MILESTONES, HINT_CONFIG } from '../../constants/feedback.constants';
import { getHintConfig } from '../../utils/feedbackUtils';
import type {
  MilestoneReachedProps,
  FrameCompleteProps,
  ContextualHintProps,
  BoosterSuggestionProps,
} from '../../types/feedback.types';

// ============================================================================
// MILESTONE REACHED
// ============================================================================

const MilestoneReached: React.FC<MilestoneReachedProps> = ({
  milestoneId,
  onComplete,
  skipAnimation = false,
}) => {
  const milestone = MILESTONES[milestoneId];
  
  useEffect(() => {
    if (skipAnimation) {
      onComplete?.();
      return;
    }
    
    const timer = setTimeout(() => {
      onComplete?.();
    }, 3000);
    
    return () => clearTimeout(timer);
  }, [skipAnimation, onComplete]);
  
  if (skipAnimation) return null;
  
  return (
    <motion.div
      className="fixed inset-0 z-40 flex items-center justify-center pointer-events-none"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Background flash */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-b from-cyan-500/20 to-transparent"
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 0.5, 0] }}
        transition={{ duration: 1 }}
      />
      
      {/* Milestone banner */}
      <motion.div
        className="relative bg-gradient-to-r from-cyan-600 to-blue-600 rounded-2xl px-8 py-6 text-center shadow-2xl"
        initial={{ scale: 0, y: 50 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0, y: -50 }}
        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      >
        {/* Icon */}
        <motion.div
          className="text-5xl mb-2"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 400 }}
        >
          {milestone.icon}
        </motion.div>
        
        {/* Title */}
        <motion.h3
          className="text-2xl font-bold text-white mb-1"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {milestone.title}
        </motion.h3>
        
        {/* Description */}
        <motion.p
          className="text-white/80 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {milestone.description}
        </motion.p>
        
        {/* Progress confetti */}
        {milestone.animation === 'confetti' && (
          <AnimatePresence>
            {Array.from({ length: 20 }).map((_, i) => (
              <motion.div
                key={`confetti-${i}`}
                className="absolute w-2 h-2 rounded-sm"
                style={{
                  backgroundColor: ['#FFD700', '#00D4FF', '#FF6B6B', '#4ADE80'][i % 4],
                  left: '50%',
                  top: '50%',
                }}
                initial={{ x: 0, y: 0, opacity: 1, rotate: 0 }}
                animate={{
                  x: (Math.random() - 0.5) * 300,
                  y: (Math.random() - 0.5) * 200,
                  opacity: 0,
                  rotate: Math.random() * 720,
                }}
                transition={{
                  duration: 1.5,
                  delay: 0.2 + i * 0.02,
                  ease: 'easeOut',
                }}
              />
            ))}
          </AnimatePresence>
        )}
      </motion.div>
    </motion.div>
  );
};

// ============================================================================
// FRAME COMPLETE
// ============================================================================

const FrameComplete: React.FC<FrameCompleteProps> = ({
  frameNumber,
  frameName,
  nextFrame,
  onContinue,
}) => {
  return (
    <motion.div
      className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-cyan-500/30"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 200 }}
    >
      {/* Checkmark */}
      <motion.div
        className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2, type: 'spring', stiffness: 400 }}
      >
        <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
        </svg>
      </motion.div>
      
      {/* Title */}
      <motion.h3
        className="text-xl font-bold text-white text-center mb-2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {frameName} Complete!
      </motion.h3>
      
      {/* Next frame preview */}
      {nextFrame && (
        <motion.div
          className="mt-4 p-4 bg-white/5 rounded-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-sm text-white/60 mb-1">Up Next:</p>
          <p className="text-white font-medium">{nextFrame.name}</p>
          <p className="text-sm text-white/50 mt-1">{nextFrame.description}</p>
        </motion.div>
      )}
      
      {/* Continue button */}
      <motion.button
        className="mt-6 w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg text-white font-semibold hover:from-cyan-600 hover:to-blue-600 transition-all"
        onClick={onContinue}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        Continue →
      </motion.button>
    </motion.div>
  );
};

// ============================================================================
// CONTEXTUAL HINT
// ============================================================================

const ContextualHint: React.FC<ContextualHintProps> = ({
  type,
  message,
  action,
  dismissible = true,
  onDismiss,
}) => {
  const config = getHintConfig(type);
  
  return (
    <motion.div
      className="relative rounded-lg p-4 shadow-lg"
      style={{
        backgroundColor: config.backgroundColor,
        borderLeft: `4px solid ${config.borderColor}`,
        maxWidth: HINT_CONFIG.position.maxWidth,
      }}
      initial={{ opacity: 0, x: -20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: -20, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <span className="text-xl flex-shrink-0">{config.icon}</span>
        
        {/* Content */}
        <div className="flex-1">
          <p className="text-sm text-white/90">{message}</p>
          
          {action && (
            <button
              onClick={action.onClick}
              className="mt-2 text-sm font-medium hover:underline"
              style={{ color: config.accentColor }}
            >
              {action.label} →
            </button>
          )}
        </div>
        
        {/* Dismiss */}
        {dismissible && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 text-white/40 hover:text-white/70 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </motion.div>
  );
};

// ============================================================================
// BOOSTER SUGGESTION
// ============================================================================

const BoosterSuggestion: React.FC<BoosterSuggestionProps> = ({
  booster,
  onApply,
  onDismiss,
}) => {
  return (
    <motion.div
      className="bg-gradient-to-br from-purple-900/90 to-indigo-900/90 backdrop-blur-sm rounded-xl p-4 border border-purple-500/30 shadow-lg"
      style={{ maxWidth: 320 }}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xl">🚀</span>
        <span className="text-sm font-semibold text-purple-300">Power-Up Suggestion</span>
      </div>
      
      {/* Booster info */}
      <h4 className="text-white font-bold mb-1">{booster.name}</h4>
      <p className="text-sm text-white/70 mb-3">{booster.description}</p>
      
      {/* Impact */}
      <div className="flex items-center gap-2 mb-4 p-2 bg-white/5 rounded-lg">
        <span className="text-green-400 font-bold">+{booster.impact}</span>
        <span className="text-sm text-white/60 capitalize">{booster.category} points</span>
      </div>
      
      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={onApply}
          className="flex-1 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg text-white text-sm font-medium hover:from-purple-600 hover:to-indigo-600 transition-all"
        >
          Apply
        </button>
        <button
          onClick={onDismiss}
          className="px-4 py-2 bg-white/10 rounded-lg text-white/70 text-sm hover:bg-white/20 transition-colors"
        >
          Skip
        </button>
      </div>
    </motion.div>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export { MilestoneReached, FrameComplete, ContextualHint, BoosterSuggestion };
