/**
 * IvyQuest v3.0 — Stepper Component
 * 
 * Step-by-step progress indicator.
 * 
 * @version 1.0.0
 * @module components/Stepper
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

// ============================================================================
// TYPES
// ============================================================================

export interface Step {
  /** Step label */
  label: string;
  
  /** Step description */
  description?: string;
  
  /** Step icon */
  icon?: React.ReactNode;
  
  /** Optional status override */
  status?: 'pending' | 'current' | 'complete' | 'error';
}

export interface StepperProps {
  /** Array of steps */
  steps: Step[];
  
  /** Current step index (0-based) */
  currentStep: number;
  
  /** Orientation */
  orientation?: 'horizontal' | 'vertical';
  
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  
  /** Show step numbers */
  showNumbers?: boolean;
  
  /** Allow clicking on steps */
  clickable?: boolean;
  
  /** Step click handler */
  onStepClick?: (stepIndex: number) => void;
  
  /** Additional class */
  className?: string;
}

// ============================================================================
// SIZE CONFIG
// ============================================================================

const sizeConfig = {
  sm: {
    circle: 'w-6 h-6',
    text: 'text-xs',
    label: 'text-sm',
    connector: 'h-0.5',
    connectorVertical: 'w-0.5',
    gap: 'gap-2',
  },
  md: {
    circle: 'w-8 h-8',
    text: 'text-sm',
    label: 'text-base',
    connector: 'h-0.5',
    connectorVertical: 'w-0.5',
    gap: 'gap-3',
  },
  lg: {
    circle: 'w-10 h-10',
    text: 'text-base',
    label: 'text-lg',
    connector: 'h-1',
    connectorVertical: 'w-1',
    gap: 'gap-4',
  },
};

// ============================================================================
// COMPONENT
// ============================================================================

export const Stepper: React.FC<StepperProps> = ({
  steps,
  currentStep,
  orientation = 'horizontal',
  size = 'md',
  showNumbers = true,
  clickable = false,
  onStepClick,
  className,
}) => {
  const config = sizeConfig[size];
  
  const getStepStatus = (index: number, step: Step): 'pending' | 'current' | 'complete' | 'error' => {
    if (step.status) return step.status;
    if (index < currentStep) return 'complete';
    if (index === currentStep) return 'current';
    return 'pending';
  };
  
  const getStatusColors = (status: string) => {
    switch (status) {
      case 'complete':
        return {
          bg: 'bg-green-500',
          border: 'border-green-500',
          text: 'text-white',
          label: 'text-green-400',
          connector: 'bg-green-500',
        };
      case 'current':
        return {
          bg: 'bg-cyan-500',
          border: 'border-cyan-500',
          text: 'text-white',
          label: 'text-cyan-400',
          connector: 'bg-white/20',
        };
      case 'error':
        return {
          bg: 'bg-red-500',
          border: 'border-red-500',
          text: 'text-white',
          label: 'text-red-400',
          connector: 'bg-white/20',
        };
      default:
        return {
          bg: 'bg-transparent',
          border: 'border-white/30',
          text: 'text-white/50',
          label: 'text-white/50',
          connector: 'bg-white/20',
        };
    }
  };
  
  if (orientation === 'vertical') {
    return (
      <div className={cn('flex flex-col', className)}>
        {steps.map((step, index) => {
          const status = getStepStatus(index, step);
          const colors = getStatusColors(status);
          const isLast = index === steps.length - 1;
          
          return (
            <div key={index} className="flex">
              {/* Circle and connector column */}
              <div className="flex flex-col items-center">
                {/* Circle */}
                <motion.button
                  type="button"
                  disabled={!clickable}
                  onClick={() => clickable && onStepClick?.(index)}
                  className={cn(
                    'flex items-center justify-center rounded-full border-2',
                    config.circle,
                    config.text,
                    colors.bg,
                    colors.border,
                    colors.text,
                    clickable && 'cursor-pointer hover:scale-110',
                    !clickable && 'cursor-default'
                  )}
                  whileHover={clickable ? { scale: 1.1 } : undefined}
                  whileTap={clickable ? { scale: 0.95 } : undefined}
                >
                  {status === 'complete' ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : status === 'error' ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  ) : step.icon ? (
                    step.icon
                  ) : showNumbers ? (
                    index + 1
                  ) : null}
                </motion.button>
                
                {/* Vertical connector */}
                {!isLast && (
                  <div className={cn('flex-1 my-2', config.connectorVertical, colors.connector)} />
                )}
              </div>
              
              {/* Content */}
              <div className={cn('ml-3 pb-8', isLast && 'pb-0')}>
                <p className={cn('font-medium', config.label, colors.label)}>
                  {step.label}
                </p>
                {step.description && (
                  <p className="text-sm text-white/50 mt-0.5">{step.description}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  }
  
  // Horizontal orientation
  return (
    <div className={cn('flex items-start', className)}>
      {steps.map((step, index) => {
        const status = getStepStatus(index, step);
        const colors = getStatusColors(status);
        const isLast = index === steps.length - 1;
        
        return (
          <div key={index} className={cn('flex items-start', !isLast && 'flex-1')}>
            {/* Step */}
            <div className={cn('flex flex-col items-center', config.gap)}>
              {/* Circle */}
              <motion.button
                type="button"
                disabled={!clickable}
                onClick={() => clickable && onStepClick?.(index)}
                className={cn(
                  'flex items-center justify-center rounded-full border-2',
                  config.circle,
                  config.text,
                  colors.bg,
                  colors.border,
                  colors.text,
                  clickable && 'cursor-pointer hover:scale-110',
                  !clickable && 'cursor-default'
                )}
                whileHover={clickable ? { scale: 1.1 } : undefined}
                whileTap={clickable ? { scale: 0.95 } : undefined}
              >
                {status === 'complete' ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : status === 'error' ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : step.icon ? (
                  step.icon
                ) : showNumbers ? (
                  index + 1
                ) : null}
              </motion.button>
              
              {/* Label */}
              <div className="text-center">
                <p className={cn('font-medium', config.label, colors.label)}>
                  {step.label}
                </p>
                {step.description && (
                  <p className="text-xs text-white/50 mt-0.5 max-w-[100px]">
                    {step.description}
                  </p>
                )}
              </div>
            </div>
            
            {/* Horizontal connector */}
            {!isLast && (
              <div className={cn(
                'flex-1 mx-2 mt-4',
                config.connector,
                colors.connector
              )} />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default Stepper;
