/**
 * IvyQuest v3.0 — Checkbox & Radio Components
 * 
 * Selection controls with animations.
 * 
 * @version 1.0.0
 * @module components/Checkbox
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

// ============================================================================
// CHECKBOX TYPES
// ============================================================================

export interface CheckboxProps {
  /** Checked state */
  checked?: boolean;
  
  /** Default checked (uncontrolled) */
  defaultChecked?: boolean;
  
  /** Change handler */
  onChange?: (checked: boolean) => void;
  
  /** Label text */
  label?: string;
  
  /** Description text */
  description?: string;
  
  /** Disabled state */
  isDisabled?: boolean;
  
  /** Indeterminate state */
  isIndeterminate?: boolean;
  
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  
  /** Color variant */
  color?: 'cyan' | 'green' | 'purple' | 'amber';
  
  /** Additional class */
  className?: string;
  
  /** Name attribute */
  name?: string;
  
  /** Value attribute */
  value?: string;
}

// ============================================================================
// CHECKBOX SIZE CONFIG
// ============================================================================

const checkboxSizeConfig = {
  sm: { box: 'w-4 h-4', icon: 'w-3 h-3', text: 'text-sm', gap: 'gap-2' },
  md: { box: 'w-5 h-5', icon: 'w-3.5 h-3.5', text: 'text-base', gap: 'gap-2.5' },
  lg: { box: 'w-6 h-6', icon: 'w-4 h-4', text: 'text-lg', gap: 'gap-3' },
};

// ============================================================================
// COLOR CONFIG
// ============================================================================

const colorConfig = {
  cyan: { bg: 'bg-cyan-500', border: 'border-cyan-500', ring: 'ring-cyan-500/30' },
  green: { bg: 'bg-green-500', border: 'border-green-500', ring: 'ring-green-500/30' },
  purple: { bg: 'bg-purple-500', border: 'border-purple-500', ring: 'ring-purple-500/30' },
  amber: { bg: 'bg-amber-500', border: 'border-amber-500', ring: 'ring-amber-500/30' },
};

// ============================================================================
// CHECKBOX COMPONENT
// ============================================================================

export const Checkbox: React.FC<CheckboxProps> = ({
  checked,
  defaultChecked,
  onChange,
  label,
  description,
  isDisabled = false,
  isIndeterminate = false,
  size = 'md',
  color = 'cyan',
  className,
  name,
  value,
}) => {
  const [internalChecked, setInternalChecked] = React.useState(defaultChecked || false);
  const isControlled = checked !== undefined;
  const isChecked = isControlled ? checked : internalChecked;
  
  const config = checkboxSizeConfig[size];
  const colors = colorConfig[color];
  
  const handleChange = () => {
    if (isDisabled) return;
    
    const newChecked = !isChecked;
    if (!isControlled) {
      setInternalChecked(newChecked);
    }
    onChange?.(newChecked);
  };
  
  return (
    <label
      className={cn(
        'flex items-start cursor-pointer',
        config.gap,
        isDisabled && 'cursor-not-allowed opacity-50',
        className
      )}
    >
      <input
        type="checkbox"
        checked={isChecked}
        onChange={handleChange}
        disabled={isDisabled}
        name={name}
        value={value}
        className="sr-only"
      />
      
      {/* Checkbox box */}
      <motion.div
        className={cn(
          'flex-shrink-0 flex items-center justify-center rounded border-2 transition-colors',
          config.box,
          isChecked || isIndeterminate
            ? cn(colors.bg, colors.border)
            : 'border-white/30 bg-transparent',
          !isDisabled && 'hover:border-white/50'
        )}
        whileTap={!isDisabled ? { scale: 0.9 } : undefined}
      >
        {/* Check icon */}
        {isChecked && !isIndeterminate && (
          <motion.svg
            className={cn('text-white', config.icon)}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={3}
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <motion.path
              d="M5 13l4 4L19 7"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </motion.svg>
        )}
        
        {/* Indeterminate icon */}
        {isIndeterminate && (
          <motion.div
            className="w-2/3 h-0.5 bg-white rounded-full"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
          />
        )}
      </motion.div>
      
      {/* Label */}
      {(label || description) && (
        <div className="flex flex-col">
          {label && (
            <span className={cn('text-white', config.text)}>{label}</span>
          )}
          {description && (
            <span className="text-sm text-white/50">{description}</span>
          )}
        </div>
      )}
    </label>
  );
};

// ============================================================================
// RADIO TYPES
// ============================================================================

export interface RadioProps {
  /** Checked state */
  checked?: boolean;
  
  /** Change handler */
  onChange?: (checked: boolean) => void;
  
  /** Label text */
  label?: string;
  
  /** Description text */
  description?: string;
  
  /** Disabled state */
  isDisabled?: boolean;
  
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  
  /** Color variant */
  color?: 'cyan' | 'green' | 'purple' | 'amber';
  
  /** Additional class */
  className?: string;
  
  /** Name attribute (for grouping) */
  name?: string;
  
  /** Value attribute */
  value?: string;
}

// ============================================================================
// RADIO COMPONENT
// ============================================================================

export const Radio: React.FC<RadioProps> = ({
  checked = false,
  onChange,
  label,
  description,
  isDisabled = false,
  size = 'md',
  color = 'cyan',
  className,
  name,
  value,
}) => {
  const config = checkboxSizeConfig[size];
  const colors = colorConfig[color];
  
  const handleChange = () => {
    if (isDisabled) return;
    onChange?.(true);
  };
  
  return (
    <label
      className={cn(
        'flex items-start cursor-pointer',
        config.gap,
        isDisabled && 'cursor-not-allowed opacity-50',
        className
      )}
    >
      <input
        type="radio"
        checked={checked}
        onChange={handleChange}
        disabled={isDisabled}
        name={name}
        value={value}
        className="sr-only"
      />
      
      {/* Radio circle */}
      <motion.div
        className={cn(
          'flex-shrink-0 flex items-center justify-center rounded-full border-2 transition-colors',
          config.box,
          checked
            ? cn(colors.border)
            : 'border-white/30',
          !isDisabled && 'hover:border-white/50'
        )}
        whileTap={!isDisabled ? { scale: 0.9 } : undefined}
      >
        {/* Inner dot */}
        <motion.div
          className={cn('rounded-full', colors.bg)}
          initial={false}
          animate={{
            width: checked ? '60%' : '0%',
            height: checked ? '60%' : '0%',
            opacity: checked ? 1 : 0,
          }}
          transition={{ duration: 0.15 }}
        />
      </motion.div>
      
      {/* Label */}
      {(label || description) && (
        <div className="flex flex-col">
          {label && (
            <span className={cn('text-white', config.text)}>{label}</span>
          )}
          {description && (
            <span className="text-sm text-white/50">{description}</span>
          )}
        </div>
      )}
    </label>
  );
};

// ============================================================================
// RADIO GROUP
// ============================================================================

export interface RadioGroupProps {
  /** Selected value */
  value?: string;
  
  /** Default value (uncontrolled) */
  defaultValue?: string;
  
  /** Change handler */
  onChange?: (value: string) => void;
  
  /** Radio options */
  options: Array<{
    value: string;
    label: string;
    description?: string;
    disabled?: boolean;
  }>;
  
  /** Group name */
  name?: string;
  
  /** Orientation */
  orientation?: 'horizontal' | 'vertical';
  
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  
  /** Color variant */
  color?: 'cyan' | 'green' | 'purple' | 'amber';
  
  /** Additional class */
  className?: string;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  value,
  defaultValue,
  onChange,
  options,
  name,
  orientation = 'vertical',
  size = 'md',
  color = 'cyan',
  className,
}) => {
  const [internalValue, setInternalValue] = React.useState(defaultValue || '');
  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;
  
  const handleChange = (optionValue: string) => {
    if (!isControlled) {
      setInternalValue(optionValue);
    }
    onChange?.(optionValue);
  };
  
  return (
    <div
      className={cn(
        'flex',
        orientation === 'vertical' ? 'flex-col gap-3' : 'flex-row gap-6',
        className
      )}
      role="radiogroup"
    >
      {options.map((option) => (
        <Radio
          key={option.value}
          checked={currentValue === option.value}
          onChange={() => handleChange(option.value)}
          label={option.label}
          description={option.description}
          isDisabled={option.disabled}
          size={size}
          color={color}
          name={name}
          value={option.value}
        />
      ))}
    </div>
  );
};

export default Checkbox;
