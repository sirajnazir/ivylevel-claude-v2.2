/**
 * IvyQuest v3.0 — Persistence Layer
 *
 * localStorage sync, auto-save, and session management.
 *
 * @version 1.0.0
 * @module store/questStore.persistence
 */

import type {
  QuestStore,
  SavedSession,
  PersistenceConfig,
} from '../types/integration.types';

// ============================================================================
// CONSTANTS
// ============================================================================

const DEFAULT_CONFIG: PersistenceConfig = {
  storageKey: 'ivyquest_v3_current',
  debounceMs: 500,
  maxHistoryItems: 10,
  sessionTimeoutHours: 24,
};

const HISTORY_KEY = 'ivyquest_v3_history';

// ============================================================================
// DEBOUNCE UTILITY
// ============================================================================

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number
): T & { cancel: () => void } {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  const debounced = ((...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, wait);
  }) as T & { cancel: () => void };

  debounced.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  return debounced;
}

// ============================================================================
// STORAGE HELPERS
// ============================================================================

export function isStorageAvailable(): boolean {
  try {
    const test = '__storage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
}

export function getStorageSize(): { used: number; quota: number } {
  if (!isStorageAvailable()) {
    return { used: 0, quota: 0 };
  }

  let used = 0;
  for (const key in localStorage) {
    if (Object.prototype.hasOwnProperty.call(localStorage, key)) {
      used += localStorage.getItem(key)?.length ?? 0;
    }
  }

  const quota = 5 * 1024 * 1024;

  return { used, quota };
}

// ============================================================================
// SESSION MANAGEMENT
// ============================================================================

export function saveToStorage(key: string, data: unknown): boolean {
  if (!isStorageAvailable()) {
    console.warn('[STORAGE] localStorage not available');
    return false;
  }

  try {
    const serialized = JSON.stringify(data);
    localStorage.setItem(key, serialized);
    return true;
  } catch (error) {
    console.error('[STORAGE] Failed to save', error);
    return false;
  }
}

export function loadFromStorage<T>(key: string): T | null {
  if (!isStorageAvailable()) {
    return null;
  }

  try {
    const serialized = localStorage.getItem(key);
    if (!serialized) return null;
    return JSON.parse(serialized) as T;
  } catch (error) {
    console.error('[STORAGE] Failed to load', error);
    return null;
  }
}

export function removeFromStorage(key: string): boolean {
  if (!isStorageAvailable()) {
    return false;
  }

  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error('[STORAGE] Failed to remove', error);
    return false;
  }
}

// ============================================================================
// SESSION HISTORY
// ============================================================================

export function getSessionHistory(): SavedSession[] {
  return loadFromStorage<SavedSession[]>(HISTORY_KEY) ?? [];
}

export function addToHistory(
  session: SavedSession,
  maxItems: number = 10
): void {
  const history = getSessionHistory();

  const filtered = history.filter((s) => s.questId !== session.questId);
  filtered.unshift(session);
  const limited = filtered.slice(0, maxItems);

  saveToStorage(HISTORY_KEY, limited);
}

export function clearHistory(): void {
  removeFromStorage(HISTORY_KEY);
}

// ============================================================================
// SESSION VALIDATION
// ============================================================================

export function isSessionExpired(
  session: SavedSession,
  timeoutHours: number = 24
): boolean {
  const savedTime = new Date(session.savedAt).getTime();
  const now = Date.now();
  const hoursOld = (now - savedTime) / (1000 * 60 * 60);

  return hoursOld > timeoutHours;
}

export function isSessionValid(
  session: SavedSession,
  currentVersion: string
): boolean {
  if (session.version !== currentVersion) {
    console.warn('[PERSIST] Version mismatch', {
      saved: session.version,
      current: currentVersion,
    });
  }

  if (!session.questId || !session.state) {
    return false;
  }

  return true;
}

// ============================================================================
// AUTO-SAVE MANAGER
// ============================================================================

export class AutoSaveManager {
  private config: PersistenceConfig;
  private debouncedSave: ReturnType<typeof debounce>;
  private unsubscribe: (() => void) | null = null;

  constructor(config: Partial<PersistenceConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.debouncedSave = debounce(
      this.save.bind(this),
      this.config.debounceMs
    );
  }

  start(store: {
    getState: () => QuestStore;
    subscribe: (listener: () => void) => () => void;
  }) {
    if (this.unsubscribe) {
      console.warn('[AUTOSAVE] Already started');
      return;
    }

    console.log('[AUTOSAVE] Starting auto-save');

    this.unsubscribe = store.subscribe(() => {
      const state = store.getState();

      if (state.persistence.isDirty) {
        this.debouncedSave(state);
      }
    });
  }

  stop() {
    if (this.unsubscribe) {
      this.unsubscribe();
      this.unsubscribe = null;
      this.debouncedSave.cancel();
      console.log('[AUTOSAVE] Stopped');
    }
  }

  private save(state: QuestStore) {
    const session: SavedSession = {
      questId: state.persistence.questId,
      state: {
        questId: state.questId,
        version: state.version,
        startedAt: state.startedAt,
        lastUpdatedAt: state.lastUpdatedAt,
        navigation: state.navigation,
        frame0: state.frame0,
        frame1: state.frame1,
        frame2: state.frame2,
        frame3: state.frame3,
        frame4: state.frame4,
        frame5: state.frame5,
        scores: state.scores,
        isComplete: state.isComplete,
        completedAt: state.completedAt,
        persistence: {
          ...state.persistence,
          lastSavedAt: new Date().toISOString(),
          isDirty: false,
        },
      },
      savedAt: new Date().toISOString(),
      version: state.version,
    };

    const success = saveToStorage(this.config.storageKey, session);

    if (success) {
      console.log('[AUTOSAVE] Saved', session.questId);
    }
  }

  saveNow(state: QuestStore) {
    this.debouncedSave.cancel();
    this.save(state);
  }
}

// ============================================================================
// SESSION RESTORE
// ============================================================================

export interface RestoreResult {
  success: boolean;
  session: SavedSession | null;
  reason?: string;
}

export function attemptRestore(
  storageKey: string = DEFAULT_CONFIG.storageKey,
  timeoutHours: number = DEFAULT_CONFIG.sessionTimeoutHours,
  currentVersion: string = '3.0.0'
): RestoreResult {
  const session = loadFromStorage<SavedSession>(storageKey);

  if (!session) {
    return { success: false, session: null, reason: 'No saved session found' };
  }

  if (isSessionExpired(session, timeoutHours)) {
    addToHistory(session);
    removeFromStorage(storageKey);
    return { success: false, session, reason: 'Session expired' };
  }

  if (!isSessionValid(session, currentVersion)) {
    return { success: false, session, reason: 'Invalid session data' };
  }

  return { success: true, session };
}

// ============================================================================
// EXPORTS
// ============================================================================

export { DEFAULT_CONFIG, debounce };

export default {
  isStorageAvailable,
  getStorageSize,
  saveToStorage,
  loadFromStorage,
  removeFromStorage,
  getSessionHistory,
  addToHistory,
  clearHistory,
  isSessionExpired,
  isSessionValid,
  attemptRestore,
  AutoSaveManager,
};
