/**
 * IvyQuest v3.0 — Tooltip Component
 * 
 * Hover-triggered info popover.
 * 
 * @version 1.0.0
 * @module components/Tooltip
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../utils/cn';
import type { TooltipProps, TooltipPosition } from '../../types/ui.types';

// ============================================================================
// POSITION STYLES
// ============================================================================

const positionStyles: Record<TooltipPosition, {
  tooltip: string;
  arrow: string;
  initial: { opacity: number; y?: number; x?: number };
  animate: { opacity: number; y: number; x: number };
}> = {
  top: {
    tooltip: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    arrow: 'top-full left-1/2 -translate-x-1/2 border-t-slate-700 border-l-transparent border-r-transparent border-b-transparent',
    initial: { opacity: 0, y: 4 },
    animate: { opacity: 1, y: 0, x: 0 },
  },
  bottom: {
    tooltip: 'top-full left-1/2 -translate-x-1/2 mt-2',
    arrow: 'bottom-full left-1/2 -translate-x-1/2 border-b-slate-700 border-l-transparent border-r-transparent border-t-transparent',
    initial: { opacity: 0, y: -4 },
    animate: { opacity: 1, y: 0, x: 0 },
  },
  left: {
    tooltip: 'right-full top-1/2 -translate-y-1/2 mr-2',
    arrow: 'left-full top-1/2 -translate-y-1/2 border-l-slate-700 border-t-transparent border-b-transparent border-r-transparent',
    initial: { opacity: 0, x: 4 },
    animate: { opacity: 1, y: 0, x: 0 },
  },
  right: {
    tooltip: 'left-full top-1/2 -translate-y-1/2 ml-2',
    arrow: 'right-full top-1/2 -translate-y-1/2 border-r-slate-700 border-t-transparent border-b-transparent border-l-transparent',
    initial: { opacity: 0, x: -4 },
    animate: { opacity: 1, y: 0, x: 0 },
  },
};

// ============================================================================
// COMPONENT
// ============================================================================

const Tooltip: React.FC<TooltipProps> = ({
  content,
  position = 'top',
  delay = 300,
  disabled = false,
  children,
  className,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const posConfig = positionStyles[position];
  
  const showTooltip = () => {
    if (disabled) return;
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };
  
  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };
  
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return (
    <div
      className={cn('relative inline-flex', className)}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      {children}
      
      <AnimatePresence>
        {isVisible && (
          <motion.div
            className={cn(
              'absolute z-50 pointer-events-none',
              posConfig.tooltip
            )}
            initial={posConfig.initial}
            animate={posConfig.animate}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            {/* Tooltip content */}
            <div className={cn(
              'px-3 py-2 rounded-lg',
              'bg-slate-700 text-white text-sm',
              'shadow-lg shadow-black/20',
              'whitespace-nowrap'
            )}>
              {content}
            </div>
            
            {/* Arrow */}
            <div
              className={cn(
                'absolute w-0 h-0',
                'border-4',
                posConfig.arrow
              )}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export { Tooltip };
export default Tooltip;
