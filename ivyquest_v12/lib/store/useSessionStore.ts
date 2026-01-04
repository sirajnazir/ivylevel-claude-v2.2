/**
 * Session Store - v11.0
 * With Edge points and routing integration
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { EDGE_VALUES } from '@/lib/constants/edge';

interface SessionState {
  currentFrame: number;
  maxFrameReached: number;
  isComplete: boolean;
  completedAt: string | null;
  userType: 'student' | 'parent';
  edgePoints: number;
  profile: any;
  setCurrentFrame: (frame: number) => void;
  setMaxFrameReached: (frame: number) => void;
  setUserType: (type: 'student' | 'parent') => void;
  completeAssessment: () => void;
  addEdge: (amount: number) => void;
  completeFrame: () => void;
  setProfile: (profile: any) => void;
  reset: () => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      currentFrame: 1,
      maxFrameReached: 1,
      isComplete: false,
      completedAt: null,
      userType: 'student',
      edgePoints: 0,
      profile: null,

      setCurrentFrame: (frame) => set({ 
        currentFrame: frame,
        maxFrameReached: Math.max(get().maxFrameReached, frame)
      }),
      
      setMaxFrameReached: (frame) => set({ maxFrameReached: frame }),
      
      setUserType: (type) => set({ userType: type }),
      
      completeAssessment: () => set({ 
        isComplete: true, 
        completedAt: new Date().toISOString(),
        edgePoints: get().edgePoints + EDGE_VALUES.assessmentComplete
      }),
      
      addEdge: (amount) => set({ edgePoints: get().edgePoints + amount }),
      
      completeFrame: () => {
        const state = get();
        set({ 
          edgePoints: state.edgePoints + EDGE_VALUES.frameComplete,
          maxFrameReached: Math.max(state.maxFrameReached, state.currentFrame + 1)
        });
      },
      
      setProfile: (profile) => set({ profile }),
      
      reset: () => set({
        currentFrame: 1,
        maxFrameReached: 1,
        isComplete: false,
        completedAt: null,
        userType: 'student',
        edgePoints: 0,
        profile: null,
      }),
    }),
    { name: 'ivyquest-session-v11' }
  )
);
