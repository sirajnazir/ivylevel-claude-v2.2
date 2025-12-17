/**
 * IvyQuest v3.0 — Quest Orchestrator
 *
 * Main navigation controller that renders the appropriate frame
 * and manages quest lifecycle.
 *
 * @version 1.0.0
 * @module controllers/QuestOrchestrator
 */

'use client';

import React, { useEffect, useCallback, useMemo, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuestMasterStore } from '../store/questStore.master';
import { useQuestNavigation } from '../hooks/useQuestNavigation';
import { useQuestProgress } from '../hooks/useQuestProgress';
import { useAutoRestore } from '../hooks/useQuestPersistence';
import type {
  FrameId,
  QuestOrchestratorProps,
  QuestCompletionResult,
  QuestScores,
} from '../types/integration.types';
import { FRAME_META } from '../types/integration.types';

// ============================================================================
// LOADING COMPONENT
// ============================================================================

function FrameLoading() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
    </div>
  );
}

// ============================================================================
// PROGRESS BAR COMPONENT
// ============================================================================

interface ProgressBarProps {
  currentFrame: FrameId;
  completedFrames: FrameId[];
  onFrameClick?: (frame: FrameId) => void;
}

function QuestProgressBar({
  currentFrame,
  completedFrames,
  onFrameClick,
}: ProgressBarProps) {
  const frames: FrameId[] = [0, 1, 2, 3, 4, 5];

  return (
    <div className="w-full px-4 py-3 bg-muted/30 border-b">
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        {frames.map((frameId, index) => {
          const meta = FRAME_META[frameId];
          const isComplete = completedFrames.includes(frameId);
          const isCurrent = currentFrame === frameId;
          const isAccessible = isComplete || isCurrent || frameId === 0;

          return (
            <React.Fragment key={frameId}>
              {/* Frame indicator */}
              <button
                onClick={() => isAccessible && onFrameClick?.(frameId)}
                disabled={!isAccessible}
                className={`
                  flex flex-col items-center gap-1 transition-all
                  ${isAccessible ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'}
                `}
              >
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center text-lg
                    transition-all duration-300
                    ${
                      isCurrent
                        ? 'bg-primary text-primary-foreground scale-110 shadow-lg'
                        : isComplete
                          ? 'bg-green-500 text-white'
                          : 'bg-muted text-muted-foreground'
                    }
                  `}
                  style={{
                    borderColor: isCurrent ? meta.color : undefined,
                    borderWidth: isCurrent ? 3 : 0,
                  }}
                >
                  {isComplete ? '✓' : meta.icon}
                </div>
                <span
                  className={`
                    text-xs font-medium
                    ${isCurrent ? 'text-foreground' : 'text-muted-foreground'}
                  `}
                >
                  {meta.name}
                </span>
              </button>

              {/* Connector line */}
              {index < frames.length - 1 && (
                <div
                  className={`
                    flex-1 h-0.5 mx-2 transition-colors duration-300
                    ${
                      completedFrames.includes(frameId)
                        ? 'bg-green-500'
                        : 'bg-muted'
                    }
                  `}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

// ============================================================================
// NAVIGATION CONTROLS
// ============================================================================

interface NavControlsProps {
  canGoNext: boolean;
  canGoPrev: boolean;
  onNext: () => void;
  onPrev: () => void;
  isLastFrame: boolean;
  isFirstFrame: boolean;
}

function NavigationControls({
  canGoNext,
  canGoPrev,
  onNext,
  onPrev,
  isLastFrame,
  isFirstFrame,
}: NavControlsProps) {
  return (
    <div className="flex justify-between items-center px-4 py-4 border-t bg-background">
      <button
        onClick={onPrev}
        disabled={!canGoPrev || isFirstFrame}
        className={`
          px-6 py-2 rounded-lg font-medium transition-all
          ${
            canGoPrev && !isFirstFrame
              ? 'bg-muted hover:bg-muted/80 text-foreground'
              : 'bg-muted/30 text-muted-foreground cursor-not-allowed'
          }
        `}
      >
        Previous
      </button>

      <button
        onClick={onNext}
        disabled={!canGoNext}
        className={`
          px-6 py-2 rounded-lg font-medium transition-all
          ${
            canGoNext
              ? 'bg-primary hover:bg-primary/90 text-primary-foreground'
              : 'bg-muted/30 text-muted-foreground cursor-not-allowed'
          }
        `}
      >
        {isLastFrame ? 'Complete Quest' : 'Continue'}
      </button>
    </div>
  );
}

// ============================================================================
// DEBUG PANEL
// ============================================================================

interface DebugPanelProps {
  state: ReturnType<typeof useQuestMasterStore.getState>;
}

function DebugPanel({ state }: DebugPanelProps) {
  return (
    <div className="fixed bottom-4 right-4 p-4 bg-black/90 text-green-400 text-xs font-mono rounded-lg max-w-sm max-h-64 overflow-auto z-50">
      <div className="font-bold mb-2">Debug Panel</div>
      <div>Frame: {state.navigation.currentFrame}</div>
      <div>Card: {state.navigation.currentCard}</div>
      <div>Completed: [{state.navigation.completedFrames.join(', ')}]</div>
      <div>Quest ID: {state.questId.slice(0, 8)}...</div>
      <div>Dirty: {state.persistence.isDirty ? 'Yes' : 'No'}</div>
      <div>
        Scores Calculated:{' '}
        {state.scores.calculatedAt ? 'Yes' : 'No'}
      </div>
    </div>
  );
}

// ============================================================================
// RESTORE DIALOG
// ============================================================================

interface RestoreDialogProps {
  onRestore: () => void;
  onStartFresh: () => void;
  savedAt: string;
  progress: number;
}

function RestoreDialog({
  onRestore,
  onStartFresh,
  savedAt,
  progress,
}: RestoreDialogProps) {
  const timeAgo = useMemo(() => {
    const saved = new Date(savedAt).getTime();
    const now = Date.now();
    const minutes = Math.round((now - saved) / 60000);

    if (minutes < 60) return `${minutes} minutes ago`;
    const hours = Math.round(minutes / 60);
    if (hours < 24) return `${hours} hours ago`;
    return `${Math.round(hours / 24)} days ago`;
  }, [savedAt]);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-background rounded-xl p-6 max-w-md w-full shadow-xl"
      >
        <h2 className="text-xl font-bold mb-2">Welcome Back!</h2>
        <p className="text-muted-foreground mb-4">
          We found a saved session from {timeAgo} ({progress}% complete).
          Would you like to continue where you left off?
        </p>

        <div className="flex gap-3">
          <button
            onClick={onRestore}
            className="flex-1 py-2 px-4 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            Continue
          </button>
          <button
            onClick={onStartFresh}
            className="flex-1 py-2 px-4 bg-muted text-foreground rounded-lg font-medium hover:bg-muted/80 transition-colors"
          >
            Start Fresh
          </button>
        </div>
      </motion.div>
    </div>
  );
}

// ============================================================================
// FRAME RENDERER
// ============================================================================

interface FrameRendererProps {
  frameId: FrameId;
  onComplete: () => void;
}

/**
 * Placeholder frame renderer - actual frame components should be imported
 * and rendered based on frameId
 */
function FrameRenderer({ frameId, onComplete }: FrameRendererProps) {
  const meta = FRAME_META[frameId];

  // In production, this would dynamically import and render
  // the actual frame component based on frameId
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <span className="text-4xl mb-2 block">{meta.icon}</span>
          <h1 className="text-2xl font-bold">{meta.name}</h1>
          <p className="text-muted-foreground">{meta.description}</p>
        </div>

        {/* Frame content placeholder */}
        <div className="bg-muted/20 rounded-xl p-8 min-h-[300px] flex items-center justify-center">
          <p className="text-muted-foreground">
            Frame {frameId} content - connect actual frame component here
          </p>
        </div>

        {/* Frame completion button (for testing) */}
        <div className="mt-8 text-center">
          <button
            onClick={onComplete}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            Complete Frame
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN ORCHESTRATOR
// ============================================================================

export function QuestOrchestrator({
  onComplete,
  onFrameChange,
  onScoreCalculated,
  initialState,
  autoRestore = true,
  showDebug = false,
}: QuestOrchestratorProps) {
  // Navigation
  const {
    currentFrame,
    completedFrames,
    canGoNext,
    canGoPrev,
    isFirstFrame,
    isLastFrame,
    goToFrame,
    nextFrame,
    prevFrame,
    markFrameComplete,
  } = useQuestNavigation();

  // Progress
  const { overallPercent, isComplete } = useQuestProgress();

  // Store state for debug
  const storeState = useQuestMasterStore.getState();

  // Auto-restore
  const [showRestoreDialog, setShowRestoreDialog] = React.useState(false);
  const [pendingSession, setPendingSession] = React.useState<{
    savedAt: string;
    progress: number;
  } | null>(null);

  const { restoreResult, session } = useAutoRestore({
    enabled: autoRestore,
    onRestoreAttempt: (result) => {
      if (result.success && result.session) {
        // Show dialog instead of auto-restoring
        setPendingSession({
          savedAt: result.session.savedAt,
          progress: Math.round(
            (result.session.state.navigation.completedFrames.length / 6) * 100
          ),
        });
        setShowRestoreDialog(true);
      }
    },
  });

  // Initialize quest if no restore
  useEffect(() => {
    if (!autoRestore || (restoreResult && !restoreResult.success)) {
      useQuestMasterStore.getState().initializeQuest();
    }
  }, [autoRestore, restoreResult]);

  // Apply initial state if provided
  useEffect(() => {
    if (initialState) {
      useQuestMasterStore.setState(initialState);
    }
  }, [initialState]);

  // Handle frame change callback
  const prevFrameRef = React.useRef(currentFrame);
  useEffect(() => {
    if (prevFrameRef.current !== currentFrame) {
      onFrameChange?.(prevFrameRef.current, currentFrame);
      prevFrameRef.current = currentFrame;
    }
  }, [currentFrame, onFrameChange]);

  // Handle score calculation callback
  useEffect(() => {
    const scores = storeState.scores;
    if (scores.calculatedAt) {
      onScoreCalculated?.(scores);
    }
  }, [storeState.scores, onScoreCalculated]);

  // Handle quest completion
  useEffect(() => {
    if (isComplete && onComplete) {
      const state = useQuestMasterStore.getState();
      const result: QuestCompletionResult = {
        questId: state.questId,
        studentName: state.frame0.studentName,
        targetSchools: state.frame0.targetSchools,
        scores: state.scores,
        selectedBoosters: state.frame5.selectedBoosters,
        actionPlan: state.frame5.actionPlan,
        completedAt: state.completedAt ?? new Date().toISOString(),
        duration: Math.round(
          (Date.now() - new Date(state.startedAt).getTime()) / 60000
        ),
      };
      onComplete(result);
    }
  }, [isComplete, onComplete]);

  // Navigation handlers
  const handleNext = useCallback(() => {
    if (isLastFrame) {
      useQuestMasterStore.getState().completeQuest();
    } else {
      nextFrame();
    }
  }, [isLastFrame, nextFrame]);

  const handleFrameComplete = useCallback(() => {
    markFrameComplete(currentFrame);
  }, [currentFrame, markFrameComplete]);

  // Restore handlers
  const handleRestore = useCallback(() => {
    setShowRestoreDialog(false);
    // Session already loaded by useAutoRestore
  }, []);

  const handleStartFresh = useCallback(() => {
    setShowRestoreDialog(false);
    useQuestMasterStore.getState().resetQuest();
    useQuestMasterStore.getState().initializeQuest();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Progress bar */}
      <QuestProgressBar
        currentFrame={currentFrame}
        completedFrames={completedFrames}
        onFrameClick={goToFrame}
      />

      {/* Frame content */}
      <div className="flex-1 overflow-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentFrame}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Suspense fallback={<FrameLoading />}>
              <FrameRenderer
                frameId={currentFrame}
                onComplete={handleFrameComplete}
              />
            </Suspense>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation controls */}
      <NavigationControls
        canGoNext={canGoNext}
        canGoPrev={canGoPrev}
        onNext={handleNext}
        onPrev={prevFrame}
        isLastFrame={isLastFrame}
        isFirstFrame={isFirstFrame}
      />

      {/* Restore dialog */}
      {showRestoreDialog && pendingSession && (
        <RestoreDialog
          onRestore={handleRestore}
          onStartFresh={handleStartFresh}
          savedAt={pendingSession.savedAt}
          progress={pendingSession.progress}
        />
      )}

      {/* Debug panel */}
      {showDebug && <DebugPanel state={storeState} />}
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default QuestOrchestrator;
