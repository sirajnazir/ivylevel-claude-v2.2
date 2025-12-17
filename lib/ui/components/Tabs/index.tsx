/**
 * IvyQuest v3.0 — Tabs Component
 * 
 * Tabbed navigation with animated indicator.
 * 
 * @version 1.0.0
 * @module components/Tabs
 */

'use client';

import React, { createContext, useContext, useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

// ============================================================================
// CONTEXT
// ============================================================================

interface TabsContextValue {
  value: string;
  onChange: (value: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

const useTabsContext = () => {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs components must be used within a Tabs provider');
  }
  return context;
};

// ============================================================================
// TYPES
// ============================================================================

export interface TabsProps {
  /** Default selected tab */
  defaultValue?: string;
  
  /** Controlled value */
  value?: string;
  
  /** Change handler */
  onChange?: (value: string) => void;
  
  /** Tab orientation */
  orientation?: 'horizontal' | 'vertical';
  
  /** Tab variant */
  variant?: 'line' | 'enclosed' | 'pills';
  
  /** Additional class */
  className?: string;
  
  /** Children */
  children: React.ReactNode;
}

export interface TabListProps {
  className?: string;
  children: React.ReactNode;
}

export interface TabTriggerProps {
  value: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}

export interface TabContentProps {
  value: string;
  className?: string;
  children: React.ReactNode;
}

// ============================================================================
// TABS ROOT
// ============================================================================

export const Tabs: React.FC<TabsProps> & {
  List: typeof TabList;
  Trigger: typeof TabTrigger;
  Content: typeof TabContent;
} = ({
  defaultValue,
  value: controlledValue,
  onChange,
  orientation = 'horizontal',
  variant = 'line',
  className,
  children,
}) => {
  const [uncontrolledValue, setUncontrolledValue] = useState(defaultValue || '');
  
  const value = controlledValue ?? uncontrolledValue;
  const handleChange = (newValue: string) => {
    setUncontrolledValue(newValue);
    onChange?.(newValue);
  };
  
  return (
    <TabsContext.Provider value={{ value, onChange: handleChange }}>
      <div
        className={cn(
          'w-full',
          orientation === 'vertical' && 'flex gap-4',
          className
        )}
        data-orientation={orientation}
        data-variant={variant}
      >
        {children}
      </div>
    </TabsContext.Provider>
  );
};

// ============================================================================
// TAB LIST
// ============================================================================

const TabList: React.FC<TabListProps> = ({ className, children }) => {
  const [indicatorStyle, setIndicatorStyle] = useState<{ left: number; width: number }>({ left: 0, width: 0 });
  const listRef = useRef<HTMLDivElement>(null);
  const { value } = useTabsContext();

  // Update indicator position
  useEffect(() => {
    if (!listRef.current) return;

    const activeTab = listRef.current.querySelector(`[data-value="${value}"]`) as HTMLElement;
    if (!activeTab) return;

    setIndicatorStyle({
      left: activeTab.offsetLeft,
      width: activeTab.offsetWidth,
    });
  }, [value]);

  return (
    <div
      ref={listRef}
      className={cn(
        'relative flex gap-1 border-b border-white/10',
        className
      )}
      role="tablist"
    >
      {children}

      {/* Animated indicator */}
      <motion.div
        className="absolute bottom-0 h-0.5 bg-cyan-500"
        initial={false}
        animate={{ left: indicatorStyle.left, width: indicatorStyle.width }}
        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
      />
    </div>
  );
};

// ============================================================================
// TAB TRIGGER
// ============================================================================

const TabTrigger: React.FC<TabTriggerProps> = ({
  value,
  disabled = false,
  icon,
  className,
  children,
}) => {
  const { value: selectedValue, onChange } = useTabsContext();
  const isSelected = value === selectedValue;
  
  return (
    <button
      type="button"
      role="tab"
      data-value={value}
      aria-selected={isSelected}
      disabled={disabled}
      onClick={() => !disabled && onChange(value)}
      className={cn(
        'relative px-4 py-2 text-sm font-medium transition-colors',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/50',
        isSelected
          ? 'text-cyan-400'
          : 'text-white/60 hover:text-white/80',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
    >
      <span className="flex items-center gap-2">
        {icon && <span className="flex-shrink-0">{icon}</span>}
        {children}
      </span>
    </button>
  );
};

// ============================================================================
// TAB CONTENT
// ============================================================================

const TabContent: React.FC<TabContentProps> = ({
  value,
  className,
  children,
}) => {
  const { value: selectedValue } = useTabsContext();
  
  if (value !== selectedValue) return null;
  
  return (
    <motion.div
      role="tabpanel"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={cn('pt-4', className)}
    >
      {children}
    </motion.div>
  );
};

// ============================================================================
// ATTACH SUBCOMPONENTS
// ============================================================================

Tabs.List = TabList;
Tabs.Trigger = TabTrigger;
Tabs.Content = TabContent;

export default Tabs;
