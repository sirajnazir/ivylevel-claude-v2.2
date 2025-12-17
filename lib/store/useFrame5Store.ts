/**
 * Frame 5: Power-Ups - Zustand Store
 * State management for booster recommendations and action plans
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import {
  generateBoosters,
  calculateProjectedScores,
  generateActionPlan,
  getBoostersByCategory,
  sortBoosters,
} from '@/lib/engines/boosterEngine';
import type { BoosterCategoryId } from '@/lib/constants/frame5.constants';
import type {
  Frame5Data,
  Frame5UIState,
  Frame5Validation,
  Frame5Inputs,
  Frame5StoreSlice,
  Booster,
} from '@/lib/types/frame5.types';

// ============================================================================
// INITIAL STATE
// ============================================================================

export const initialFrame5Data: Frame5Data = {
  inputs: null,
  boosters: [],
  selectedBoosters: [],
  actionPlan: null,
  projectedScores: null,
  isComplete: false,
  completedAt: null,
};

export const initialFrame5UI: Frame5UIState = {
  currentCard: 0,
  categoryFilter: null,
  sortBy: 'priority',
  expandedBoosterId: null,
  showCompletedBoosters: false,
};

export const initialFrame5Validation: Frame5Validation = {
  card1: { isValid: true },
  card2: { isValid: false, errors: ['Select at least 1 booster'] },
  card3: { isValid: true },
  card4: { isValid: true },
  isFrameComplete: false,
};

// ============================================================================
// CONSTANTS
// ============================================================================

const CARD_COUNT = 4;
const MAX_BOOSTERS = 10;

// ============================================================================
// FRAME 5 STORE
// ============================================================================

export const useFrame5Store = create<Frame5StoreSlice>()(
  immer((set, get) => ({
    // Initial state
    frame5Data: initialFrame5Data,
    frame5UI: initialFrame5UI,
    frame5Validation: initialFrame5Validation,

    // ========================================================================
    // DATA ACTIONS
    // ========================================================================

    initializeFrame5: (inputs: Frame5Inputs) => {
      // Generate boosters from inputs
      const result = generateBoosters(inputs);

      set((state) => {
        state.frame5Data.inputs = inputs;
        state.frame5Data.boosters = result.boosters;
        state.frame5Data.selectedBoosters = [];
        state.frame5Data.actionPlan = null;
        state.frame5Data.projectedScores = null;
        state.frame5Data.isComplete = false;
        state.frame5Data.completedAt = null;
      });

      console.log('[FRAME5.INIT] Initialized with inputs', {
        ivyReady: inputs.currentScores.ivyReady,
        yearsToApp: inputs.yearsToApp,
      });
      console.log('[FRAME5.INIT] Generated boosters', { count: result.boosters.length });
    },

    selectBooster: (boosterId: string) => {
      const { frame5Data } = get();

      // Check max selection limit
      if (frame5Data.selectedBoosters.length >= MAX_BOOSTERS) {
        console.log('[FRAME5.SELECT] Max boosters reached', { max: MAX_BOOSTERS });
        return;
      }

      // Check if already selected
      if (frame5Data.selectedBoosters.includes(boosterId)) {
        return;
      }

      set((state) => {
        state.frame5Data.selectedBoosters.push(boosterId);

        // Mark booster as selected
        const boosterIndex = state.frame5Data.boosters.findIndex(b => b.id === boosterId);
        if (boosterIndex !== -1) {
          state.frame5Data.boosters[boosterIndex].isSelected = true;
        }

        // Update validation
        state.frame5Validation.card2.isValid = true;
        state.frame5Validation.card2.errors = undefined;
      });

      // Recalculate projected scores
      get().updateProjectedScores();

      console.log('[FRAME5.SELECT]', boosterId, {
        totalSelected: get().frame5Data.selectedBoosters.length,
      });
    },

    deselectBooster: (boosterId: string) => {
      set((state) => {
        const index = state.frame5Data.selectedBoosters.indexOf(boosterId);
        if (index !== -1) {
          state.frame5Data.selectedBoosters.splice(index, 1);
        }

        // Mark booster as deselected
        const boosterIndex = state.frame5Data.boosters.findIndex(b => b.id === boosterId);
        if (boosterIndex !== -1) {
          state.frame5Data.boosters[boosterIndex].isSelected = false;
        }

        // Update validation
        if (state.frame5Data.selectedBoosters.length === 0) {
          state.frame5Validation.card2.isValid = false;
          state.frame5Validation.card2.errors = ['Select at least 1 booster'];
        }
      });

      // Recalculate projected scores
      get().updateProjectedScores();

      console.log('[FRAME5.DESELECT]', boosterId, {
        totalSelected: get().frame5Data.selectedBoosters.length,
      });
    },

    toggleBoosterComplete: (boosterId: string) => {
      set((state) => {
        const boosterIndex = state.frame5Data.boosters.findIndex(b => b.id === boosterId);
        if (boosterIndex !== -1) {
          state.frame5Data.boosters[boosterIndex].isCompleted =
            !state.frame5Data.boosters[boosterIndex].isCompleted;
        }
      });
    },

    generateActionPlan: () => {
      const { frame5Data } = get();
      if (!frame5Data.inputs || frame5Data.selectedBoosters.length === 0) {
        return;
      }

      // Get selected booster objects
      const selectedBoosterObjects = frame5Data.boosters.filter(b =>
        frame5Data.selectedBoosters.includes(b.id)
      );

      // Generate action plan
      const actionPlan = generateActionPlan(selectedBoosterObjects, frame5Data.inputs);

      set((state) => {
        state.frame5Data.actionPlan = actionPlan;
      });

      console.log('[FRAME5.ACTION_PLAN] Generated', {
        steps: actionPlan.totalSteps,
        weeks: actionPlan.estimatedWeeks,
      });
    },

    // Private helper to update projected scores
    updateProjectedScores: () => {
      const { frame5Data } = get();
      if (!frame5Data.inputs) return;

      if (frame5Data.selectedBoosters.length === 0) {
        set((state) => {
          state.frame5Data.projectedScores = null;
        });
        return;
      }

      // Get selected booster objects
      const selectedBoosterObjects = frame5Data.boosters.filter(b =>
        frame5Data.selectedBoosters.includes(b.id)
      );

      // Calculate projected scores
      const projectedScores = calculateProjectedScores(
        frame5Data.inputs,
        selectedBoosterObjects
      );

      set((state) => {
        state.frame5Data.projectedScores = projectedScores;
      });
    },

    // ========================================================================
    // UI ACTIONS
    // ========================================================================

    setFrame5Card: (card: number) => {
      if (card >= 0 && card < CARD_COUNT) {
        set((state) => {
          state.frame5UI.currentCard = card;
        });
        console.log('[FRAME5.CARD]', `Navigated to card: ${card}`);
      }
    },

    nextFrame5Card: () => {
      const { frame5UI, frame5Validation } = get();
      const currentCard = frame5UI.currentCard;

      // Check validation for current card
      const cardKey = `card${currentCard + 1}` as keyof typeof frame5Validation;
      if (cardKey !== 'isFrameComplete' && !frame5Validation[cardKey].isValid) {
        console.log('[FRAME5.NAV] Cannot advance - card not valid');
        return;
      }

      if (currentCard < CARD_COUNT - 1) {
        // Generate action plan when moving to card 4
        if (currentCard === 2) {
          get().generateActionPlan();
        }

        set((state) => {
          state.frame5UI.currentCard = currentCard + 1;
        });
      }
    },

    prevFrame5Card: () => {
      const { frame5UI } = get();
      if (frame5UI.currentCard > 0) {
        set((state) => {
          state.frame5UI.currentCard -= 1;
        });
      }
    },

    setCategoryFilter: (category: BoosterCategoryId | null) => {
      set((state) => {
        state.frame5UI.categoryFilter = category;
      });
    },

    setSortBy: (sortBy: Frame5UIState['sortBy']) => {
      set((state) => {
        state.frame5UI.sortBy = sortBy;
      });
    },

    setExpandedBooster: (boosterId: string | null) => {
      set((state) => {
        state.frame5UI.expandedBoosterId = boosterId;
      });
    },

    toggleShowCompleted: () => {
      set((state) => {
        state.frame5UI.showCompletedBoosters = !state.frame5UI.showCompletedBoosters;
      });
    },

    // ========================================================================
    // ACTION PLAN ACTIONS
    // ========================================================================

    toggleActionStep: (itemId: string) => {
      set((state) => {
        if (!state.frame5Data.actionPlan) return;

        const itemIndex = state.frame5Data.actionPlan.items.findIndex(
          item => item.id === itemId
        );

        if (itemIndex !== -1) {
          const wasCompleted = state.frame5Data.actionPlan.items[itemIndex].isCompleted;
          state.frame5Data.actionPlan.items[itemIndex].isCompleted = !wasCompleted;

          // Update completed steps count
          if (wasCompleted) {
            state.frame5Data.actionPlan.completedSteps -= 1;
          } else {
            state.frame5Data.actionPlan.completedSteps += 1;
          }
        }
      });
    },

    updateActionNotes: (itemId: string, notes: string) => {
      set((state) => {
        if (!state.frame5Data.actionPlan) return;

        const itemIndex = state.frame5Data.actionPlan.items.findIndex(
          item => item.id === itemId
        );

        if (itemIndex !== -1) {
          state.frame5Data.actionPlan.items[itemIndex].notes = notes;
        }
      });
    },

    // ========================================================================
    // LIFECYCLE ACTIONS
    // ========================================================================

    completeFrame5: () => {
      const { frame5Data } = get();

      set((state) => {
        state.frame5Data.isComplete = true;
        state.frame5Data.completedAt = new Date().toISOString();
        state.frame5Validation.isFrameComplete = true;
      });

      console.log('[FRAME5.COMPLETE]', {
        selectedBoosters: frame5Data.selectedBoosters,
        actionSteps: frame5Data.actionPlan?.totalSteps ?? 0,
      });
    },

    resetFrame5: () => {
      set((state) => {
        state.frame5Data = initialFrame5Data;
        state.frame5UI = initialFrame5UI;
        state.frame5Validation = initialFrame5Validation;
      });
      console.log('[FRAME5.RESET]');
    },
  }))
);

// ============================================================================
// SELECTOR HOOKS
// ============================================================================

export const useFrame5Card = () => useFrame5Store((s) => s.frame5UI.currentCard);
export const useFrame5Boosters = () => useFrame5Store((s) => s.frame5Data.boosters);
export const useFrame5SelectedBoosters = () => useFrame5Store((s) => s.frame5Data.selectedBoosters);
export const useFrame5ActionPlan = () => useFrame5Store((s) => s.frame5Data.actionPlan);
export const useFrame5ProjectedScores = () => useFrame5Store((s) => s.frame5Data.projectedScores);
export const useFrame5Inputs = () => useFrame5Store((s) => s.frame5Data.inputs);
export const useFrame5Validation = () => useFrame5Store((s) => s.frame5Validation);

/**
 * Get filtered and sorted boosters
 */
export const useFilteredBoosters = (): Booster[] => {
  const boosters = useFrame5Store((s) => s.frame5Data.boosters);
  const categoryFilter = useFrame5Store((s) => s.frame5UI.categoryFilter);
  const sortByValue = useFrame5Store((s) => s.frame5UI.sortBy);
  const showCompleted = useFrame5Store((s) => s.frame5UI.showCompletedBoosters);

  // Filter by category
  let filtered = getBoostersByCategory(boosters, categoryFilter);

  // Filter completed if needed
  if (!showCompleted) {
    filtered = filtered.filter(b => !b.isCompleted);
  }

  // Sort
  return sortBoosters(filtered, sortByValue);
};

/**
 * Get selected booster objects
 */
export const useSelectedBoosterObjects = (): Booster[] => {
  const boosters = useFrame5Store((s) => s.frame5Data.boosters);
  const selectedIds = useFrame5Store((s) => s.frame5Data.selectedBoosters);
  return boosters.filter(b => selectedIds.includes(b.id));
};

/**
 * Get top recommendations (first 3 by priority)
 */
export const useTopRecommendations = (): Booster[] => {
  const boosters = useFrame5Store((s) => s.frame5Data.boosters);
  return sortBoosters(boosters, 'priority').slice(0, 3);
};

export default useFrame5Store;
