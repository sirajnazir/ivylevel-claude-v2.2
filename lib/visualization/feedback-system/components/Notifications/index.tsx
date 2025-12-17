/**
 * IvyQuest v3.0 — Notification Components
 * 
 * Toast, Achievement, and system notifications.
 * 
 * @version 1.0.0
 * @module components/Notifications
 */

'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TOAST_CONFIG,
  ACHIEVEMENT_CONFIG,
} from '../../constants/feedback.constants';
import {
  getToastConfig,
  getAchievementRarityConfig,
} from '../../utils/feedbackUtils';
import type {
  ToastProps,
  ToastContainerProps,
  AchievementUnlockProps,
  Toast as ToastType,
} from '../../types/feedback.types';

// ============================================================================
// TOAST COMPONENT
// ============================================================================

const Toast: React.FC<ToastProps & { id?: string }> = ({
  type,
  title,
  message,
  duration,
  dismissible = true,
  action,
  onClose,
}) => {
  const config = getToastConfig(type);
  const effectiveDuration = duration ?? config.defaultDuration;
  
  // Auto-dismiss
  useEffect(() => {
    if (effectiveDuration > 0) {
      const timer = setTimeout(() => {
        onClose?.();
      }, effectiveDuration);
      return () => clearTimeout(timer);
    }
  }, [effectiveDuration, onClose]);
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 50, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 50, scale: 0.9 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className="relative w-80 rounded-lg shadow-lg overflow-hidden"
      style={{
        backgroundColor: config.backgroundColor,
        borderLeft: `4px solid ${config.borderColor}`,
      }}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Icon */}
          <span className="text-xl flex-shrink-0">{config.icon}</span>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <h4
              className="font-semibold text-sm"
              style={{ color: config.textColor }}
            >
              {title}
            </h4>
            {message && (
              <p
                className="text-sm mt-1 opacity-80"
                style={{ color: config.textColor }}
              >
                {message}
              </p>
            )}
            
            {/* Action button */}
            {action && (
              <button
                onClick={action.onClick}
                className="mt-2 text-sm font-medium hover:underline"
                style={{ color: config.borderColor }}
              >
                {action.label}
              </button>
            )}
          </div>
          
          {/* Dismiss button */}
          {dismissible && (
            <button
              onClick={onClose}
              className="flex-shrink-0 text-white/60 hover:text-white/90 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
      
      {/* Progress bar for auto-dismiss */}
      {effectiveDuration > 0 && (
        <motion.div
          className="absolute bottom-0 left-0 h-1"
          style={{ backgroundColor: config.borderColor }}
          initial={{ width: '100%' }}
          animate={{ width: '0%' }}
          transition={{ duration: effectiveDuration / 1000, ease: 'linear' }}
        />
      )}
    </motion.div>
  );
};

// ============================================================================
// TOAST CONTAINER
// ============================================================================

interface ToastContainerInternalProps extends ToastContainerProps {
  toasts: ToastType[];
  onDismiss: (id: string) => void;
}

const ToastContainer: React.FC<ToastContainerInternalProps> = ({
  toasts,
  onDismiss,
  maxVisible = TOAST_CONFIG.maxVisible,
  position = 'top-right',
}) => {
  const positionStyles: Record<string, React.CSSProperties> = {
    'top-right': { top: TOAST_CONFIG.position.top, right: TOAST_CONFIG.position.right },
    'top-left': { top: TOAST_CONFIG.position.top, left: TOAST_CONFIG.position.right },
    'bottom-right': { bottom: TOAST_CONFIG.position.top, right: TOAST_CONFIG.position.right },
    'bottom-left': { bottom: TOAST_CONFIG.position.top, left: TOAST_CONFIG.position.right },
  };
  
  const visibleToasts = toasts.slice(0, maxVisible);
  
  return (
    <div
      className="fixed z-50 flex flex-col gap-3"
      style={positionStyles[position]}
    >
      <AnimatePresence mode="popLayout">
        {visibleToasts.map((toast) => (
          <Toast
            key={toast.id}
            id={toast.id}
            type={toast.type}
            title={toast.title}
            message={toast.message}
            duration={toast.duration}
            dismissible={toast.dismissible}
            action={toast.action}
            onClose={() => onDismiss(toast.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};

// ============================================================================
// ACHIEVEMENT UNLOCK
// ============================================================================

const AchievementUnlock: React.FC<AchievementUnlockProps> = ({
  achievement,
  onDismiss,
  playSound = true,
  autoDismiss = true,
}) => {
  const rarityConfig = getAchievementRarityConfig(achievement.rarity);
  const animConfig = ACHIEVEMENT_CONFIG.animation;
  
  // Auto-dismiss
  useEffect(() => {
    if (autoDismiss) {
      const timer = setTimeout(() => {
        onDismiss?.();
      }, animConfig.entrance + animConfig.hold + animConfig.exit);
      return () => clearTimeout(timer);
    }
  }, [autoDismiss, animConfig, onDismiss]);
  
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Backdrop glow */}
      <motion.div
        className="absolute inset-0"
        style={{
          background: `radial-gradient(circle, ${rarityConfig.glowColor} 0%, transparent 70%)`,
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 0.6, 0.3] }}
        transition={{ duration: 1 }}
      />
      
      {/* Achievement card */}
      <motion.div
        className="relative rounded-xl p-6 text-center pointer-events-auto"
        style={{
          backgroundColor: rarityConfig.backgroundColor,
          border: `3px solid ${rarityConfig.borderColor}`,
          boxShadow: `0 0 40px ${rarityConfig.glowColor}`,
          minWidth: 280,
        }}
        initial={{ scale: 0, rotate: -10 }}
        animate={{ scale: 1, rotate: 0 }}
        exit={{ scale: 0, rotate: 10 }}
        transition={{
          type: 'spring',
          stiffness: 300,
          damping: 20,
          delay: 0.2,
        }}
      >
        {/* Rarity label */}
        <div
          className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
          style={{
            backgroundColor: rarityConfig.borderColor,
            color: '#FFFFFF',
          }}
        >
          {rarityConfig.label}
        </div>
        
        {/* Icon */}
        <motion.div
          className="text-5xl mb-3"
          initial={{ scale: 0 }}
          animate={{ scale: [0, 1.3, 1] }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          {achievement.icon}
        </motion.div>
        
        {/* Title */}
        <motion.h3
          className="text-xl font-bold text-white mb-2"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {achievement.title}
        </motion.h3>
        
        {/* Description */}
        <motion.p
          className="text-sm text-white/70"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          {achievement.description}
        </motion.p>
        
        {/* Dismiss button */}
        <motion.button
          className="mt-4 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          style={{
            backgroundColor: rarityConfig.borderColor,
            color: '#FFFFFF',
          }}
          onClick={onDismiss}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Awesome!
        </motion.button>
        
        {/* Sparkle particles */}
        <AnimatePresence>
          {Array.from({ length: 12 }).map((_, i) => {
            const angle = (i / 12) * Math.PI * 2;
            const distance = 100 + Math.random() * 50;
            
            return (
              <motion.div
                key={`sparkle-${i}`}
                className="absolute w-2 h-2 rounded-full"
                style={{
                  backgroundColor: rarityConfig.borderColor,
                  left: '50%',
                  top: '50%',
                }}
                initial={{ x: 0, y: 0, opacity: 0, scale: 0 }}
                animate={{
                  x: Math.cos(angle) * distance,
                  y: Math.sin(angle) * distance,
                  opacity: [0, 1, 0],
                  scale: [0, 1, 0],
                }}
                transition={{
                  duration: 1.5,
                  delay: 0.3 + i * 0.05,
                  ease: 'easeOut',
                }}
              />
            );
          })}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export { Toast, ToastContainer, AchievementUnlock };
export default Toast;
