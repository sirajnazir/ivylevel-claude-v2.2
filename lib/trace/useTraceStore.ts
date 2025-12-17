/**
 * Trace Store - Zustand store for trace state
 * Provides reactive state for debug overlay and trace visualization
 */

import { useEffect } from 'react';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { traceContext } from './TraceContext';
import type {
  TraceEvent,
  TraceSpan,
  TraceLevel,
  TraceDomain,
  DebugOverlayState,
} from './types';

// ============================================
// Store State Interface
// ============================================

interface TraceStoreState {
  // Events & Spans
  events: TraceEvent[];
  spans: TraceSpan[];

  // Debug Overlay State
  overlay: DebugOverlayState;

  // Actions - Events
  addEvent: (event: TraceEvent) => void;
  addSpan: (span: TraceSpan) => void;
  clearEvents: () => void;
  clearSpans: () => void;

  // Actions - Overlay
  toggleOverlay: () => void;
  setOverlayTab: (tab: DebugOverlayState['activeTab']) => void;
  setFilter: (filter: Partial<DebugOverlayState['filter']>) => void;
  togglePause: () => void;
  setMaxEvents: (max: number) => void;

  // Actions - Filtering
  filterByLevel: (levels: TraceLevel[]) => void;
  filterByDomain: (domains: TraceDomain[]) => void;
  setSearchQuery: (query: string) => void;

  // Computed
  getFilteredEvents: () => TraceEvent[];
  getFilteredSpans: () => TraceSpan[];
  getScoringEvents: () => TraceEvent[];
  getInputEvents: () => TraceEvent[];
  getStateEvents: () => TraceEvent[];
  getErrorEvents: () => TraceEvent[];
}

// ============================================
// Default State
// ============================================

const defaultOverlayState: DebugOverlayState = {
  isVisible: false,
  activeTab: 'events',
  filter: {
    levels: ['debug', 'info', 'warn', 'error'],
    domains: ['scoring', 'input', 'state', 'navigation', 'api', 'twin', 'validation', 'performance'],
    searchQuery: '',
  },
  isPaused: false,
  maxEvents: 500,
};

// ============================================
// Store Creation
// ============================================

export const useTraceStore = create<TraceStoreState>()(
  devtools(
    (set, get) => ({
      events: [],
      spans: [],
      overlay: defaultOverlayState,

      // Event Actions
      addEvent: (event) =>
        set((state) => {
          if (state.overlay.isPaused) return state;
          const newEvents = [...state.events, event].slice(-state.overlay.maxEvents);
          return { events: newEvents };
        }),

      addSpan: (span) =>
        set((state) => ({
          spans: [...state.spans.filter((s) => s.id !== span.id), span].slice(-100),
        })),

      clearEvents: () => set({ events: [] }),
      clearSpans: () => set({ spans: [] }),

      // Overlay Actions
      toggleOverlay: () =>
        set((state) => ({
          overlay: { ...state.overlay, isVisible: !state.overlay.isVisible },
        })),

      setOverlayTab: (tab) =>
        set((state) => ({
          overlay: { ...state.overlay, activeTab: tab },
        })),

      setFilter: (filter) =>
        set((state) => ({
          overlay: {
            ...state.overlay,
            filter: { ...state.overlay.filter, ...filter },
          },
        })),

      togglePause: () =>
        set((state) => ({
          overlay: { ...state.overlay, isPaused: !state.overlay.isPaused },
        })),

      setMaxEvents: (max) =>
        set((state) => ({
          overlay: { ...state.overlay, maxEvents: max },
        })),

      // Filter Actions
      filterByLevel: (levels) =>
        set((state) => ({
          overlay: {
            ...state.overlay,
            filter: { ...state.overlay.filter, levels },
          },
        })),

      filterByDomain: (domains) =>
        set((state) => ({
          overlay: {
            ...state.overlay,
            filter: { ...state.overlay.filter, domains },
          },
        })),

      setSearchQuery: (query) =>
        set((state) => ({
          overlay: {
            ...state.overlay,
            filter: { ...state.overlay.filter, searchQuery: query },
          },
        })),

      // Computed Getters
      getFilteredEvents: () => {
        const { events, overlay } = get();
        const { levels, domains, searchQuery } = overlay.filter;

        return events.filter((event) => {
          if (!levels.includes(event.level)) return false;
          if (!domains.includes(event.domain)) return false;
          if (searchQuery) {
            const searchLower = searchQuery.toLowerCase();
            const matchesMessage = event.message.toLowerCase().includes(searchLower);
            const matchesAction = event.action.toLowerCase().includes(searchLower);
            const matchesData = JSON.stringify(event.data || {})
              .toLowerCase()
              .includes(searchLower);
            if (!matchesMessage && !matchesAction && !matchesData) return false;
          }
          return true;
        });
      },

      getFilteredSpans: () => {
        const { spans, overlay } = get();
        const { domains, searchQuery } = overlay.filter;

        return spans.filter((span) => {
          if (!domains.includes(span.domain)) return false;
          if (searchQuery) {
            const searchLower = searchQuery.toLowerCase();
            if (!span.name.toLowerCase().includes(searchLower)) return false;
          }
          return true;
        });
      },

      getScoringEvents: () => get().events.filter((e) => e.domain === 'scoring'),
      getInputEvents: () => get().events.filter((e) => e.domain === 'input'),
      getStateEvents: () => get().events.filter((e) => e.domain === 'state'),
      getErrorEvents: () => get().events.filter((e) => e.level === 'error'),
    }),
    { name: 'TraceStore' }
  )
);

// ============================================
// Initialize Store Listeners
// ============================================

let isInitialized = false;

export function initializeTraceStore(): void {
  if (isInitialized) return;
  isInitialized = true;

  // Subscribe to trace context events
  traceContext.addListener((event) => {
    useTraceStore.getState().addEvent(event);
  });

  // Subscribe to span updates
  traceContext.addSpanListener((span) => {
    useTraceStore.getState().addSpan(span);
  });
}

// ============================================
// Keyboard Shortcut Hook
// ============================================

export function useTraceKeyboard(): void {
  useEffect(() => {
    // Register keyboard shortcut (Ctrl+Shift+D) to toggle overlay
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        useTraceStore.getState().toggleOverlay();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
}
