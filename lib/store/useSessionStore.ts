/**
 * Assessment Session Store (Zustand)
 * Manages the assessment flow state (frames, progress, quiz)
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export type FrameId = 1 | 2 | 3 | 4 | 5 | 6;

export interface FrameProgress {
  frame_id: FrameId;
  started_at: string | null;
  completed_at: string | null;
  cards_completed: number;
  total_cards: number;
  xp_earned: number;
}

export interface QuizAnswer {
  question_id: string;
  answer_value: string;
  points_earned: number;
  response_time_ms: number;
  answered_at: string;
}

interface SessionStoreState {
  // Session identity
  session_id: string;
  user_id: string | null;
  started_at: string;

  // Frame navigation
  current_frame: FrameId;
  current_card: number;
  frame_progress: Record<FrameId, FrameProgress>;

  // Quiz state (Frame 4)
  quiz_answers: QuizAnswer[];
  quiz_streak: number;
  quiz_total_xp: number;

  // Overall progress
  total_xp: number;
  is_completed: boolean;
  completed_at: string | null;

  // Actions
  setUserId: (userId: string) => void;
  goToFrame: (frame: FrameId) => void;
  nextFrame: () => void;
  prevFrame: () => void;
  setCurrentCard: (card: number) => void;
  nextCard: () => void;
  prevCard: () => void;
  startFrame: (frame: FrameId, totalCards: number) => void;
  completeCard: (xp: number) => void;
  completeFrame: () => void;
  addQuizAnswer: (answer: QuizAnswer) => void;
  incrementStreak: () => void;
  resetStreak: () => void;
  addXP: (xp: number) => void;
  completeAssessment: () => void;
  resetSession: () => void;
  getProgress: () => number; // 0-100
}

const createEmptyFrameProgress = (frame_id: FrameId): FrameProgress => ({
  frame_id,
  started_at: null,
  completed_at: null,
  cards_completed: 0,
  total_cards: 0,
  xp_earned: 0,
});

const FRAME_CARD_COUNTS: Record<FrameId, number> = {
  1: 4,  // Identity, Schools, Major, Certainty
  2: 5,  // GPA, Test, AP, Awards, Summary
  3: 10, // Spike, Leadership, EC, Projects, Research, Awards, Service, HS, Demographics, Summary
  4: 15, // Quiz questions
  5: 6,  // Score, Schools, Factors, Archetype, Twin, Summary
  6: 4,  // Top3, Grid, ROI, Action Plan
};

export const useSessionStore = create<SessionStoreState>()(
  devtools(
    persist(
      immer((set, get) => ({
        session_id: crypto.randomUUID(),
        user_id: null,
        started_at: new Date().toISOString(),
        current_frame: 1,
        current_card: 0,
        frame_progress: {
          1: createEmptyFrameProgress(1),
          2: createEmptyFrameProgress(2),
          3: createEmptyFrameProgress(3),
          4: createEmptyFrameProgress(4),
          5: createEmptyFrameProgress(5),
          6: createEmptyFrameProgress(6),
        },
        quiz_answers: [],
        quiz_streak: 0,
        quiz_total_xp: 0,
        total_xp: 0,
        is_completed: false,
        completed_at: null,

        setUserId: (userId) =>
          set((state) => {
            state.user_id = userId;
          }),

        goToFrame: (frame) =>
          set((state) => {
            state.current_frame = frame;
            state.current_card = 0;
          }),

        nextFrame: () =>
          set((state) => {
            if (state.current_frame < 6) {
              state.current_frame = (state.current_frame + 1) as FrameId;
              state.current_card = 0;
            }
          }),

        prevFrame: () =>
          set((state) => {
            if (state.current_frame > 1) {
              state.current_frame = (state.current_frame - 1) as FrameId;
              state.current_card = 0;
            }
          }),

        setCurrentCard: (card) =>
          set((state) => {
            state.current_card = card;
          }),

        nextCard: () =>
          set((state) => {
            const totalCards = state.frame_progress[state.current_frame].total_cards;
            if (state.current_card < totalCards - 1) {
              state.current_card++;
            }
          }),

        prevCard: () =>
          set((state) => {
            if (state.current_card > 0) {
              state.current_card--;
            }
          }),

        startFrame: (frame, totalCards) =>
          set((state) => {
            state.frame_progress[frame].started_at = new Date().toISOString();
            state.frame_progress[frame].total_cards = totalCards || FRAME_CARD_COUNTS[frame];
          }),

        completeCard: (xp) =>
          set((state) => {
            state.frame_progress[state.current_frame].cards_completed++;
            state.frame_progress[state.current_frame].xp_earned += xp;
            state.total_xp += xp;
          }),

        completeFrame: () =>
          set((state) => {
            state.frame_progress[state.current_frame].completed_at = new Date().toISOString();
          }),

        addQuizAnswer: (answer) =>
          set((state) => {
            state.quiz_answers.push(answer);
            state.quiz_total_xp += answer.points_earned;
            state.total_xp += answer.points_earned;
          }),

        incrementStreak: () =>
          set((state) => {
            state.quiz_streak++;
          }),

        resetStreak: () =>
          set((state) => {
            state.quiz_streak = 0;
          }),

        addXP: (xp) =>
          set((state) => {
            state.total_xp += xp;
          }),

        completeAssessment: () =>
          set((state) => {
            state.is_completed = true;
            state.completed_at = new Date().toISOString();
          }),

        resetSession: () =>
          set((state) => {
            state.session_id = crypto.randomUUID();
            state.started_at = new Date().toISOString();
            state.current_frame = 1;
            state.current_card = 0;
            state.frame_progress = {
              1: createEmptyFrameProgress(1),
              2: createEmptyFrameProgress(2),
              3: createEmptyFrameProgress(3),
              4: createEmptyFrameProgress(4),
              5: createEmptyFrameProgress(5),
              6: createEmptyFrameProgress(6),
            };
            state.quiz_answers = [];
            state.quiz_streak = 0;
            state.quiz_total_xp = 0;
            state.total_xp = 0;
            state.is_completed = false;
            state.completed_at = null;
          }),

        getProgress: () => {
          const state = get();
          let completed = 0;
          let total = 0;

          for (let i = 1; i <= 6; i++) {
            const frame = state.frame_progress[i as FrameId];
            completed += frame.cards_completed;
            total += frame.total_cards || FRAME_CARD_COUNTS[i as FrameId];
          }

          return total > 0 ? Math.round((completed / total) * 100) : 0;
        },
      })),
      {
        name: 'ivyquest-session',
        partialize: (state) => ({
          session_id: state.session_id,
          user_id: state.user_id,
          current_frame: state.current_frame,
          current_card: state.current_card,
          frame_progress: state.frame_progress,
          quiz_answers: state.quiz_answers,
          total_xp: state.total_xp,
          is_completed: state.is_completed,
        }),
      }
    ),
    { name: 'SessionStore' }
  )
);
