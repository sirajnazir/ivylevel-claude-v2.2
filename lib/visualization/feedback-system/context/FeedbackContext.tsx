/**
 * IvyQuest v3.0 — Feedback Context & Hooks
 * 
 * Central state management for feedback system.
 * 
 * @version 1.0.0
 * @module context/FeedbackContext
 */

'use client';

import React, { createContext, useContext, useReducer, useCallback, useMemo } from 'react';
import { generateFeedbackId } from '../utils/feedbackUtils';
import type {
  FeedbackContextValue,
  FeedbackProviderProps,
  FeedbackConfig,
  Toast,
  Hint,
  ScoreDelta,
  Achievement,
  MilestoneId,
} from '../types/feedback.types';
import type { ToastTypeId, ScoreCategory } from '../constants/feedback.constants';

// ============================================================================
// STATE TYPES
// ============================================================================

interface FeedbackState {
  toasts: Toast[];
  hints: Hint[];
  deltas: ScoreDelta[];
  achievements: Achievement[];
  completedMilestones: MilestoneId[];
}

type FeedbackAction =
  | { type: 'ADD_TOAST'; payload: Toast }
  | { type: 'REMOVE_TOAST'; payload: string }
  | { type: 'ADD_HINT'; payload: Hint }
  | { type: 'REMOVE_HINT'; payload: string }
  | { type: 'ADD_DELTA'; payload: ScoreDelta }
  | { type: 'REMOVE_DELTA'; payload: string }
  | { type: 'ADD_ACHIEVEMENT'; payload: Achievement }
  | { type: 'ADD_MILESTONE'; payload: MilestoneId }
  | { type: 'CLEAR_ALL' };

// ============================================================================
// INITIAL STATE
// ============================================================================

const initialState: FeedbackState = {
  toasts: [],
  hints: [],
  deltas: [],
  achievements: [],
  completedMilestones: [],
};

// ============================================================================
// REDUCER
// ============================================================================

function feedbackReducer(state: FeedbackState, action: FeedbackAction): FeedbackState {
  switch (action.type) {
    case 'ADD_TOAST':
      return {
        ...state,
        toasts: [...state.toasts, action.payload],
      };
    
    case 'REMOVE_TOAST':
      return {
        ...state,
        toasts: state.toasts.filter(t => t.id !== action.payload),
      };
    
    case 'ADD_HINT':
      return {
        ...state,
        hints: [...state.hints, action.payload],
      };
    
    case 'REMOVE_HINT':
      return {
        ...state,
        hints: state.hints.filter(h => h.id !== action.payload),
      };
    
    case 'ADD_DELTA':
      return {
        ...state,
        deltas: [...state.deltas, action.payload],
      };
    
    case 'REMOVE_DELTA':
      return {
        ...state,
        deltas: state.deltas.filter(d => d.id !== action.payload),
      };
    
    case 'ADD_ACHIEVEMENT':
      return {
        ...state,
        achievements: [...state.achievements, action.payload],
      };
    
    case 'ADD_MILESTONE':
      if (state.completedMilestones.includes(action.payload)) {
        return state;
      }
      return {
        ...state,
        completedMilestones: [...state.completedMilestones, action.payload],
      };
    
    case 'CLEAR_ALL':
      return {
        ...initialState,
        completedMilestones: state.completedMilestones, // Preserve milestones
        achievements: state.achievements, // Preserve achievements
      };
    
    default:
      return state;
  }
}

// ============================================================================
// CONTEXT
// ============================================================================

const FeedbackContext = createContext<FeedbackContextValue | null>(null);

// ============================================================================
// PROVIDER
// ============================================================================

const defaultConfig: FeedbackConfig = {
  maxToasts: 5,
  defaultDuration: 4000,
  enableSounds: true,
  enableHaptics: true,
  autoShowMilestones: true,
};

export const FeedbackProvider: React.FC<FeedbackProviderProps> = ({
  children,
  config = {},
}) => {
  const mergedConfig = { ...defaultConfig, ...config };
  const [state, dispatch] = useReducer(feedbackReducer, initialState);
  
  // Show score delta
  const showDelta = useCallback((
    delta: number,
    category: ScoreCategory,
    position: { x: number; y: number }
  ) => {
    const id = generateFeedbackId('delta');
    
    dispatch({
      type: 'ADD_DELTA',
      payload: { id, delta, category, position, timestamp: Date.now() },
    });
    
    // Auto-remove after animation
    setTimeout(() => {
      dispatch({ type: 'REMOVE_DELTA', payload: id });
    }, 2000);
  }, []);
  
  // Show toast
  const showToast = useCallback((
    type: ToastTypeId,
    title: string,
    message?: string,
    options?: Partial<Toast>
  ) => {
    const id = generateFeedbackId('toast');
    
    dispatch({
      type: 'ADD_TOAST',
      payload: {
        id,
        type,
        title,
        message,
        duration: options?.duration ?? mergedConfig.defaultDuration,
        dismissible: options?.dismissible ?? true,
        action: options?.action,
        createdAt: Date.now(),
      },
    });
  }, [mergedConfig.defaultDuration]);
  
  // Show achievement
  const showAchievement = useCallback((achievement: Achievement) => {
    dispatch({
      type: 'ADD_ACHIEVEMENT',
      payload: {
        ...achievement,
        unlockedAt: Date.now(),
      },
    });
  }, []);
  
  // Show milestone
  const showMilestone = useCallback((milestoneId: MilestoneId) => {
    dispatch({ type: 'ADD_MILESTONE', payload: milestoneId });
  }, []);
  
  // Show hint
  const showHint = useCallback((hint: Omit<Hint, 'id'>) => {
    const id = generateFeedbackId('hint');
    
    dispatch({
      type: 'ADD_HINT',
      payload: { ...hint, id },
    });
  }, []);
  
  // Dismiss toast
  const dismissToast = useCallback((id: string) => {
    dispatch({ type: 'REMOVE_TOAST', payload: id });
  }, []);
  
  // Dismiss hint
  const dismissHint = useCallback((id: string) => {
    dispatch({ type: 'REMOVE_HINT', payload: id });
  }, []);
  
  // Clear all
  const clearAll = useCallback(() => {
    dispatch({ type: 'CLEAR_ALL' });
  }, []);
  
  // Context value
  const value = useMemo<FeedbackContextValue>(() => ({
    ...state,
    showDelta,
    showToast,
    showAchievement,
    showMilestone,
    showHint,
    dismissToast,
    dismissHint,
    clearAll,
  }), [state, showDelta, showToast, showAchievement, showMilestone, showHint, dismissToast, dismissHint, clearAll]);
  
  return (
    <FeedbackContext.Provider value={value}>
      {children}
    </FeedbackContext.Provider>
  );
};

// ============================================================================
// HOOK: useFeedback
// ============================================================================

export function useFeedback(): FeedbackContextValue {
  const context = useContext(FeedbackContext);
  
  if (!context) {
    throw new Error('useFeedback must be used within a FeedbackProvider');
  }
  
  return context;
}

// ============================================================================
// HOOK: useScoreDelta
// ============================================================================

import { useState, useRef, useEffect } from 'react';
import type { UseScoreDeltaReturn, UseScoreDeltaOptions } from '../types/feedback.types';

export function useScoreDelta(
  category: ScoreCategory,
  options: UseScoreDeltaOptions = {}
): UseScoreDeltaReturn {
  const {
    initialScore = 0,
    animationDuration = 1500,
    minDelta = 1,
    onChange,
  } = options;
  
  const [currentScore, setCurrentScore] = useState(initialScore);
  const [previousScore, setPreviousScore] = useState(initialScore);
  const [delta, setDelta] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const trackChange = useCallback((newScore: number) => {
    const newDelta = newScore - currentScore;
    
    if (Math.abs(newDelta) >= minDelta) {
      setPreviousScore(currentScore);
      setCurrentScore(newScore);
      setDelta(newDelta);
      setIsAnimating(true);
      
      onChange?.(newDelta, category);
      
      // Clear animation after duration
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        setIsAnimating(false);
        setDelta(0);
      }, animationDuration);
    } else {
      setCurrentScore(newScore);
    }
  }, [currentScore, minDelta, animationDuration, category, onChange]);
  
  const reset = useCallback(() => {
    setCurrentScore(initialScore);
    setPreviousScore(initialScore);
    setDelta(0);
    setIsAnimating(false);
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  }, [initialScore]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return {
    currentScore,
    previousScore,
    delta,
    category,
    isAnimating,
    trackChange,
    reset,
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export { FeedbackContext };
export default FeedbackProvider;
