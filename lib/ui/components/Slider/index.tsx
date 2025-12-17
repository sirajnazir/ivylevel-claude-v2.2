/**
 * IvyQuest v3.0 — Slider Component
 * 
 * Range slider with marks and labels.
 * 
 * @version 1.0.0
 * @module components/Slider
 */

'use client';

import React, { useRef, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import type { SliderProps } from '../../types/ui.types';

// ============================================================================
// COMPONENT
// ============================================================================

const Slider: React.FC<SliderProps> = ({
  min,
  max,
  value,
  onChange,
  step = 1,
  marks,
  label,
  showValue = true,
  formatValue = (v) => String(v),
  disabled = false,
  className,
  id,
  'data-testid': dataTestId,
}) => {
  const trackRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const percentage = ((value - min) / (max - min)) * 100;
  
  // Calculate mark positions
  const markPositions = marks
    ? Array.isArray(marks)
      ? marks.map(m => ({ value: m, percent: ((m - min) / (max - min)) * 100 }))
      : Array.from({ length: Math.floor((max - min) / step) + 1 }, (_, i) => {
          const v = min + i * step;
          return { value: v, percent: ((v - min) / (max - min)) * 100 };
        })
    : [];
  
  // Handle click/drag
  const updateValue = useCallback((clientX: number) => {
    if (!trackRef.current || disabled) return;
    
    const rect = trackRef.current.getBoundingClientRect();
    const percent = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const rawValue = min + percent * (max - min);
    const steppedValue = Math.round(rawValue / step) * step;
    const clampedValue = Math.max(min, Math.min(max, steppedValue));
    
    onChange(clampedValue);
  }, [min, max, step, onChange, disabled]);
  
  const handleMouseDown = (e: React.MouseEvent) => {
    if (disabled) return;
    setIsDragging(true);
    updateValue(e.clientX);
    
    const handleMouseMove = (e: MouseEvent) => {
      updateValue(e.clientX);
    };
    
    const handleMouseUp = () => {
      setIsDragging(false);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };
  
  return (
    <div className={cn('w-full', disabled && 'opacity-50', className)}>
      {/* Label and value */}
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-2">
          {label && (
            <label className="text-sm font-medium text-slate-300">
              {label}
            </label>
          )}
          {showValue && (
            <span className="text-sm font-mono text-cyan-400">
              {formatValue(value)}
            </span>
          )}
        </div>
      )}
      
      {/* Track */}
      <div
        ref={trackRef}
        id={id}
        data-testid={dataTestId}
        className={cn(
          'relative h-2 rounded-full bg-slate-700 cursor-pointer',
          disabled && 'cursor-not-allowed'
        )}
        onMouseDown={handleMouseDown}
      >
        {/* Filled track */}
        <div
          className="absolute h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500"
          style={{ width: `${percentage}%` }}
        />
        
        {/* Marks */}
        {markPositions.map(({ value: markValue, percent }) => (
          <div
            key={markValue}
            className={cn(
              'absolute top-1/2 -translate-y-1/2 w-1 h-3 rounded-full',
              markValue <= value ? 'bg-cyan-300' : 'bg-slate-600'
            )}
            style={{ left: `${percent}%`, transform: 'translate(-50%, -50%)' }}
          />
        ))}
        
        {/* Thumb */}
        <motion.div
          className={cn(
            'absolute top-1/2 w-5 h-5 rounded-full',
            'bg-white shadow-lg shadow-black/20',
            'border-2 border-cyan-500',
            'transform -translate-x-1/2 -translate-y-1/2',
            isDragging && 'ring-4 ring-cyan-500/30'
          )}
          style={{ left: `${percentage}%` }}
          whileHover={!disabled ? { scale: 1.1 } : undefined}
          whileTap={!disabled ? { scale: 0.95 } : undefined}
        />
      </div>
      
      {/* Mark labels */}
      {marks && Array.isArray(marks) && (
        <div className="relative mt-2">
          {markPositions.map(({ value: markValue, percent }) => (
            <span
              key={markValue}
              className="absolute text-xs text-slate-500 transform -translate-x-1/2"
              style={{ left: `${percent}%` }}
            >
              {formatValue(markValue)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export { Slider };
export default Slider;
