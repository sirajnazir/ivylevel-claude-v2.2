/**
 * IvyQuest v3.0 — Toggle Component
 * 
 * Switch toggle for boolean values.
 * 
 * @version 1.0.0
 * @module components/Toggle
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import type { ToggleProps, Size } from '../../types/ui.types';

// ============================================================================
// STYLES
// ============================================================================

const sizeConfig: Record<Size, {
  track: string;
  thumb: string;
  translateX: number;
}> = {
  sm: {
    track: 'w-8 h-4',
    thumb: 'w-3 h-3',
    translateX: 16,
  },
  md: {
    track: 'w-11 h-6',
    thumb: 'w-5 h-5',
    translateX: 20,
  },
  lg: {
    track: 'w-14 h-7',
    thumb: 'w-6 h-6',
    translateX: 28,
  },
};

// ============================================================================
// COMPONENT
// ============================================================================

const Toggle: React.FC<ToggleProps> = ({
  checked,
  onChange,
  label,
  description,
  disabled = false,
  size = 'md',
  className,
  id,
  'data-testid': dataTestId,
}) => {
  const config = sizeConfig[size];
  
  const handleClick = () => {
    if (!disabled) {
      onChange(!checked);
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };
  
  return (
    <div className={cn('flex items-start gap-3', className)}>
      {/* Toggle switch */}
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        id={id}
        data-testid={dataTestId}
        disabled={disabled}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className={cn(
          'relative inline-flex flex-shrink-0 rounded-full',
          'transition-colors duration-200 ease-in-out',
          'focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-slate-900',
          config.track,
          checked ? 'bg-cyan-500' : 'bg-slate-600',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <motion.span
          className={cn(
            'rounded-full bg-white shadow-lg',
            'pointer-events-none',
            config.thumb
          )}
          initial={false}
          animate={{
            x: checked ? config.translateX : 2,
          }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          style={{ marginTop: 2 }}
        />
      </button>
      
      {/* Label and description */}
      {(label || description) && (
        <div className="flex flex-col">
          {label && (
            <span
              className={cn(
                'text-sm font-medium',
                disabled ? 'text-slate-500' : 'text-slate-200'
              )}
            >
              {label}
            </span>
          )}
          {description && (
            <span className="text-xs text-slate-500 mt-0.5">
              {description}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export { Toggle };
export default Toggle;
