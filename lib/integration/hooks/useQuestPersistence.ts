/**
 * IvyQuest v3.0 — Persistence Hook
 *
 * Provides auto-save, restore, and session management.
 *
 * @version 1.0.0
 * @module hooks/useQuestPersistence
 */

import { useEffect, useCallback, useState, useRef } from 'react';
import { useQuestMasterStore } from '../store/questStore.master';
import {
  selectIsDirty,
  selectLastSavedAt,
  selectQuestId,
} from '../store/questStore.selectors';
import {
  AutoSaveManager,
  attemptRestore,
  getSessionHistory,
  clearHistory,
  isStorageAvailable,
  getStorageSize,
  type RestoreResult,
} from '../store/questStore.persistence';
import type { SavedSession } from '../types/integration.types';

// ============================================================================
// TYPES
// ============================================================================

export interface UseQuestPersistenceReturn {
  // Status
  isDirty: boolean;
  lastSavedAt: string | null;
  questId: string;
  isAutoSaveEnabled: boolean;

  // Storage info
  storageAvailable: boolean;
  storageUsed: number;
  storageQuota: number;

  // Actions
  saveNow: () => void;
  loadSession: (questId?: string) => boolean;
  clearSession: () => void;
  exportSession: () => SavedSession;

  // History
  sessionHistory: SavedSession[];
  clearHistory: () => void;
  restoreFromHistory: (session: SavedSession) => boolean;

  // Auto-save control
  enableAutoSave: () => void;
  disableAutoSave: () => void;
}

export interface UseAutoRestoreOptions {
  enabled?: boolean;
  onRestoreAttempt?: (result: RestoreResult) => void;
  onRestoreSuccess?: (session: SavedSession) => void;
  onRestoreFailed?: (reason: string) => void;
  timeoutHours?: number;
}

// ============================================================================
// AUTO-SAVE HOOK
// ============================================================================

/**
 * Internal hook for managing auto-save
 */
function useAutoSave(enabled: boolean = true) {
  const autoSaveRef = useRef<AutoSaveManager | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!enabled) return;

    // Create and start auto-save manager
    const manager = new AutoSaveManager();
    autoSaveRef.current = manager;

    // Get the store instance
    const store = useQuestMasterStore;

    manager.start(store);
    setIsRunning(true);

    console.log('[PERSISTENCE] Auto-save enabled');

    return () => {
      manager.stop();
      autoSaveRef.current = null;
      setIsRunning(false);
      console.log('[PERSISTENCE] Auto-save disabled');
    };
  }, [enabled]);

  const saveNow = useCallback(() => {
    if (autoSaveRef.current) {
      const state = useQuestMasterStore.getState();
      autoSaveRef.current.saveNow(state);
    }
  }, []);

  return {
    isRunning,
    saveNow,
    manager: autoSaveRef.current,
  };
}

// ============================================================================
// MAIN PERSISTENCE HOOK
// ============================================================================

export function useQuestPersistence(
  autoSaveEnabled: boolean = true
): UseQuestPersistenceReturn {
  // Subscribe to persistence state
  const isDirty = useQuestMasterStore(selectIsDirty);
  const lastSavedAt = useQuestMasterStore(selectLastSavedAt);
  const questId = useQuestMasterStore(selectQuestId);

  // Get actions from store
  const loadSession = useQuestMasterStore((state) => state.loadSession);
  const clearSession = useQuestMasterStore((state) => state.clearSession);
  const exportSession = useQuestMasterStore((state) => state.exportSession);

  // Auto-save management
  const [isAutoSaveActive, setIsAutoSaveActive] = useState(autoSaveEnabled);
  const { saveNow, isRunning } = useAutoSave(isAutoSaveActive);

  // Storage info
  const [storageInfo, setStorageInfo] = useState(() => ({
    available: isStorageAvailable(),
    ...getStorageSize(),
  }));

  // Session history
  const [sessionHistory, setSessionHistory] = useState<SavedSession[]>(() =>
    getSessionHistory()
  );

  // Refresh storage info periodically
  useEffect(() => {
    const refreshStorageInfo = () => {
      setStorageInfo({
        available: isStorageAvailable(),
        ...getStorageSize(),
      });
      setSessionHistory(getSessionHistory());
    };

    // Refresh on mount and when dirty changes
    refreshStorageInfo();

    const interval = setInterval(refreshStorageInfo, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, [isDirty]);

  // Actions
  const enableAutoSave = useCallback(() => {
    setIsAutoSaveActive(true);
  }, []);

  const disableAutoSave = useCallback(() => {
    setIsAutoSaveActive(false);
  }, []);

  const handleClearHistory = useCallback(() => {
    clearHistory();
    setSessionHistory([]);
  }, []);

  const restoreFromHistory = useCallback(
    (session: SavedSession): boolean => {
      try {
        // Use the store's restore mechanism
        const store = useQuestMasterStore.getState();

        // Apply session state to store
        useQuestMasterStore.setState({
          questId: session.state.questId,
          version: session.state.version,
          startedAt: session.state.startedAt,
          lastUpdatedAt: new Date().toISOString(),
          navigation: session.state.navigation,
          frame0: session.state.frame0,
          frame1: session.state.frame1,
          frame2: session.state.frame2,
          frame3: session.state.frame3,
          frame4: session.state.frame4,
          frame5: session.state.frame5,
          scores: session.state.scores,
          isComplete: session.state.isComplete,
          completedAt: session.state.completedAt,
          persistence: {
            ...session.state.persistence,
            isDirty: false,
            lastSavedAt: new Date().toISOString(),
          },
        });

        console.log('[PERSISTENCE] Restored from history:', session.questId);
        return true;
      } catch (error) {
        console.error('[PERSISTENCE] Failed to restore from history:', error);
        return false;
      }
    },
    []
  );

  return {
    // Status
    isDirty,
    lastSavedAt,
    questId,
    isAutoSaveEnabled: isRunning,

    // Storage info
    storageAvailable: storageInfo.available,
    storageUsed: storageInfo.used,
    storageQuota: storageInfo.quota,

    // Actions
    saveNow,
    loadSession,
    clearSession,
    exportSession,

    // History
    sessionHistory,
    clearHistory: handleClearHistory,
    restoreFromHistory,

    // Auto-save control
    enableAutoSave,
    disableAutoSave,
  };
}

// ============================================================================
// AUTO-RESTORE HOOK
// ============================================================================

/**
 * Hook for automatically restoring session on mount
 */
export function useAutoRestore(options: UseAutoRestoreOptions = {}) {
  const {
    enabled = true,
    onRestoreAttempt,
    onRestoreSuccess,
    onRestoreFailed,
    timeoutHours = 24,
  } = options;

  const [restoreResult, setRestoreResult] = useState<RestoreResult | null>(null);
  const [isRestoring, setIsRestoring] = useState(false);
  const hasAttempted = useRef(false);

  useEffect(() => {
    if (!enabled || hasAttempted.current) return;

    hasAttempted.current = true;
    setIsRestoring(true);

    // Attempt restore
    const result = attemptRestore(undefined, timeoutHours);
    setRestoreResult(result);

    // Notify callback
    onRestoreAttempt?.(result);

    if (result.success && result.session) {
      // Apply restored state to store
      try {
        useQuestMasterStore.setState({
          questId: result.session.state.questId,
          version: result.session.state.version,
          startedAt: result.session.state.startedAt,
          lastUpdatedAt: new Date().toISOString(),
          navigation: result.session.state.navigation,
          frame0: result.session.state.frame0,
          frame1: result.session.state.frame1,
          frame2: result.session.state.frame2,
          frame3: result.session.state.frame3,
          frame4: result.session.state.frame4,
          frame5: result.session.state.frame5,
          scores: result.session.state.scores,
          isComplete: result.session.state.isComplete,
          completedAt: result.session.state.completedAt,
          persistence: {
            ...result.session.state.persistence,
            isDirty: false,
          },
        });

        console.log('[PERSISTENCE] Auto-restored session:', result.session.questId);
        onRestoreSuccess?.(result.session);
      } catch (error) {
        console.error('[PERSISTENCE] Auto-restore failed:', error);
        onRestoreFailed?.('Failed to apply restored state');
      }
    } else {
      onRestoreFailed?.(result.reason ?? 'Unknown error');
    }

    setIsRestoring(false);
  }, [enabled, timeoutHours, onRestoreAttempt, onRestoreSuccess, onRestoreFailed]);

  return {
    restoreResult,
    isRestoring,
    hasSession: restoreResult?.success ?? false,
    session: restoreResult?.session ?? null,
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default useQuestPersistence;
