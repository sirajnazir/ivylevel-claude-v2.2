/**
 * UI Store (Zustand)
 * Manages UI state (modals, toasts, loading, sidebar)
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

export interface Modal {
  id: string;
  component: string; // Component name to render
  props?: Record<string, unknown>;
  onClose?: () => void;
}

interface UIStoreState {
  // Sidebar
  sidebar_open: boolean;
  sidebar_collapsed: boolean;

  // Modals
  modals: Modal[];
  active_modal: string | null;

  // Toasts
  toasts: Toast[];

  // Loading states
  is_loading: boolean;
  loading_message: string;

  // Mobile
  is_mobile: boolean;
  mobile_nav_open: boolean;

  // Theme
  theme: 'dark' | 'light';

  // Twin focus
  focused_school: string | null;

  // Actions - Sidebar
  toggleSidebar: () => void;
  openSidebar: () => void;
  closeSidebar: () => void;
  collapseSidebar: () => void;
  expandSidebar: () => void;

  // Actions - Modals
  openModal: (modal: Omit<Modal, 'id'>) => void;
  closeModal: (id?: string) => void;
  closeAllModals: () => void;

  // Actions - Toasts
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;

  // Actions - Loading
  setLoading: (loading: boolean, message?: string) => void;

  // Actions - Mobile
  setMobile: (isMobile: boolean) => void;
  toggleMobileNav: () => void;
  closeMobileNav: () => void;

  // Actions - Twin focus
  setFocusedSchool: (schoolId: string | null) => void;
}

export const useUIStore = create<UIStoreState>()(
  devtools(
    immer((set, get) => ({
      sidebar_open: true,
      sidebar_collapsed: false,
      modals: [],
      active_modal: null,
      toasts: [],
      is_loading: false,
      loading_message: '',
      is_mobile: false,
      mobile_nav_open: false,
      theme: 'dark',
      focused_school: null,

      // Sidebar
      toggleSidebar: () =>
        set((state) => {
          state.sidebar_open = !state.sidebar_open;
        }),
      openSidebar: () =>
        set((state) => {
          state.sidebar_open = true;
        }),
      closeSidebar: () =>
        set((state) => {
          state.sidebar_open = false;
        }),
      collapseSidebar: () =>
        set((state) => {
          state.sidebar_collapsed = true;
        }),
      expandSidebar: () =>
        set((state) => {
          state.sidebar_collapsed = false;
        }),

      // Modals
      openModal: (modal) =>
        set((state) => {
          const id = crypto.randomUUID();
          state.modals.push({ ...modal, id });
          state.active_modal = id;
        }),
      closeModal: (id) =>
        set((state) => {
          if (id) {
            state.modals = state.modals.filter((m) => m.id !== id);
          } else if (state.modals.length > 0) {
            state.modals.pop();
          }
          state.active_modal = state.modals.length > 0
            ? state.modals[state.modals.length - 1].id
            : null;
        }),
      closeAllModals: () =>
        set((state) => {
          state.modals = [];
          state.active_modal = null;
        }),

      // Toasts
      addToast: (toast) => {
        const id = crypto.randomUUID();
        set((state) => {
          state.toasts.push({ ...toast, id });
        });

        // Auto-remove after duration
        const duration = toast.duration ?? 5000;
        if (duration > 0) {
          setTimeout(() => {
            get().removeToast(id);
          }, duration);
        }

        return id;
      },
      removeToast: (id) =>
        set((state) => {
          state.toasts = state.toasts.filter((t) => t.id !== id);
        }),
      clearToasts: () =>
        set((state) => {
          state.toasts = [];
        }),

      // Loading
      setLoading: (loading, message = '') =>
        set((state) => {
          state.is_loading = loading;
          state.loading_message = message;
        }),

      // Mobile
      setMobile: (isMobile) =>
        set((state) => {
          state.is_mobile = isMobile;
          if (isMobile) {
            state.sidebar_open = false;
          }
        }),
      toggleMobileNav: () =>
        set((state) => {
          state.mobile_nav_open = !state.mobile_nav_open;
        }),
      closeMobileNav: () =>
        set((state) => {
          state.mobile_nav_open = false;
        }),

      // Twin focus
      setFocusedSchool: (schoolId) =>
        set((state) => {
          state.focused_school = schoolId;
        }),
    })),
    { name: 'UIStore' }
  )
);
