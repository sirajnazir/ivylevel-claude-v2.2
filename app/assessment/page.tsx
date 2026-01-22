'use client';

import { useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSessionStore, useStudentStore, useResultsStore, useUIStore } from '@/lib/store';
import { AssessmentLayout } from '@/components/layout/AssessmentLayout';
import { Frame1Warmup } from '@/components/frames/Frame1Warmup';
import { Frame2Snapshot } from '@/components/frames/Frame2Snapshot';
import { Frame3Building } from '@/components/frames/Frame3Building';
import { Frame4Operating } from '@/components/frames/Frame4Operating';
import { Frame5Reveal } from '@/components/frames/Frame5Reveal';
import { Frame6PowerUps } from '@/components/frames/Frame6PowerUps';
import { saveAssessment } from '@/lib/services/assessmentService';
import { useAuth } from '@/lib/auth/AuthProvider';

export default function AssessmentPage() {
  const router = useRouter();
  const { user } = useAuth();
  const currentFrame = useSessionStore((s) => s.current_frame);
  const nextFrame = useSessionStore((s) => s.nextFrame);
  const sessionId = useSessionStore((s) => s.session_id);
  const profile = useStudentStore((s) => s.profile);
  const results = useResultsStore((s) => s.results);
  const setResults = useResultsStore((s) => s.setResults);
  const setLoading = useUIStore((s) => s.setLoading);
  const addToast = useUIStore((s) => s.addToast);

  // Score calculation function
  const calculateScores = useCallback(async () => {
    setLoading(true, 'Analyzing your profile...');
    try {
      const response = await fetch('/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile }),
      });

      if (!response.ok) {
        throw new Error('Scoring failed');
      }

      const data = await response.json();
      if (data.success && data.results) {
        setResults(data.results);
        return data.results;
      }
      throw new Error(data.error || 'Unknown error');
    } catch (error) {
      console.error('Scoring error:', error);
      addToast({
        type: 'error',
        title: 'Scoring Error',
        message: 'Failed to calculate scores. Please try again.',
      });
      return null;
    } finally {
      setLoading(false);
    }
  }, [profile, setResults, setLoading, addToast]);

  // Frame completion handlers
  const handleFrame1Complete = useCallback(() => {
    nextFrame();
  }, [nextFrame]);

  const handleFrame2Complete = useCallback(() => {
    nextFrame();
  }, [nextFrame]);

  const handleFrame3Complete = useCallback(() => {
    nextFrame();
  }, [nextFrame]);

  const handleFrame4Complete = useCallback(async () => {
    // Calculate scores before showing reveal
    const results = await calculateScores();
    if (results) {
      nextFrame();
    }
  }, [nextFrame, calculateScores]);

  const handleFrame5Complete = useCallback(() => {
    nextFrame();
  }, [nextFrame]);

  const handleFrame6Complete = useCallback(async () => {
    // Save assessment to Supabase before navigating to dashboard
    if (user?.id) {
      setLoading(true, 'Saving your assessment...');
      try {
        // Extract scores from AssessmentResults (results.ivy_ready_score is an object)
        // Convert to flat structure that saveAssessment expects
        const scores = results?.ivy_ready_score
          ? {
              aptitude: results.ivy_ready_score.category_scores.aptitude,
              passion: results.ivy_ready_score.category_scores.passion,
              community: results.ivy_ready_score.category_scores.community,
              identity: results.ivy_ready_score.category_scores.narrative,
              overall: results.ivy_ready_score.total_score,
              ivy_ready_score: results.ivy_ready_score.total_score,
            }
          : {
              aptitude: 0,
              passion: 0,
              community: 0,
              identity: 0,
              overall: 0,
              ivy_ready_score: 0,
            };

        const result = await saveAssessment({
          userId: user.id,
          sessionId: sessionId || profile.session_id,
          profile,
          scores,
          archetype: results?.archetype_detected,
        });

        if (result.success) {
          console.log('[Assessment] Saved successfully:', result.data?.id);
          addToast({
            type: 'success',
            title: 'Assessment Complete',
            message: 'Your profile has been saved!',
          });
        } else {
          console.error('[Assessment] Save failed:', result.error);
          addToast({
            type: 'error',
            title: 'Save Warning',
            message: 'Could not save to database, but you can continue.',
          });
        }
      } catch (error) {
        console.error('[Assessment] Save error:', error);
      } finally {
        setLoading(false);
      }
    }

    router.push('/dashboard');
  }, [router, user, sessionId, profile, results, setLoading, addToast]);

  return (
    <AssessmentLayout showPillarProgress={true}>
      {currentFrame === 1 && (
        <Frame1Warmup onComplete={handleFrame1Complete} />
      )}
      {currentFrame === 2 && (
        <Frame2Snapshot onComplete={handleFrame2Complete} />
      )}
      {currentFrame === 3 && (
        <Frame3Building onComplete={handleFrame3Complete} />
      )}
      {currentFrame === 4 && (
        <Frame4Operating onComplete={handleFrame4Complete} />
      )}
      {currentFrame === 5 && (
        <Frame5Reveal onComplete={handleFrame5Complete} />
      )}
      {currentFrame === 6 && (
        <Frame6PowerUps onComplete={handleFrame6Complete} />
      )}
    </AssessmentLayout>
  );
}
