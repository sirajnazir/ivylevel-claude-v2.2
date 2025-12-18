'use client';

import { create } from 'zustand';
import type { RealtimeInsight } from '@/lib/insights/realtimeInsights';

interface NotificationState {
  queue: RealtimeInsight[];
  current: RealtimeInsight | null;
  isVisible: boolean;
  addNotification: (insight: RealtimeInsight) => void;
  showNext: () => void;
  dismiss: () => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  queue: [],
  current: null,
  isVisible: false,

  addNotification: (insight) => {
    const { queue, current } = get();

    // Check for duplicate (same metricType = same metric category)
    const isDuplicate =
      (current && current.metricType === insight.metricType) ||
      queue.some(n => n.metricType === insight.metricType);

    if (isDuplicate) {
      // Replace existing in queue with updated insight
      const filteredQueue = queue.filter(n => n.metricType !== insight.metricType);

      // If currently showing the same metric type, dismiss and show new one
      if (current && current.metricType === insight.metricType) {
        set({ queue: [...filteredQueue, insight] });
        get().dismiss();
      } else {
        set({ queue: [...filteredQueue, insight] });
      }
    } else {
      // Add to queue
      set({ queue: [...queue, insight] });
    }

    // If nothing showing, show immediately
    if (!get().current) {
      get().showNext();
    }
  },

  showNext: () => {
    const { queue } = get();
    if (queue.length === 0) {
      set({ current: null, isVisible: false });
      return;
    }

    // Take first from queue
    const [next, ...rest] = queue;
    set({
      current: next,
      queue: rest,
      isVisible: true,
    });

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      const { current } = get();
      // Only dismiss if this is still the current notification
      if (current && current.id === next.id) {
        get().dismiss();
      }
    }, 5000);
  },

  dismiss: () => {
    set({ isVisible: false });

    // Wait for exit animation, then show next
    setTimeout(() => {
      set({ current: null });
      get().showNext();
    }, 300);
  },

  clearAll: () => {
    set({
      queue: [],
      current: null,
      isVisible: false,
    });
  },
}));
