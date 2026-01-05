'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthProvider';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { startFreshAssessment } from '@/lib/session/sessionManager';
import { EntryPortal } from '@/components/auth/EntryPortal';

export default function HomePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading, profile } = useAuth();
  const isCompleted = useSessionStore((s) => s.is_completed);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted || isLoading) return;

    // Check if user wants to start fresh (via ?fresh=1 query param)
    const shouldStartFresh = searchParams.get('fresh') === '1';

    if (shouldStartFresh) {
      // Clear all state and start new assessment
      startFreshAssessment({ redirectTo: '/quest/1' });
      return;
    }

    // If authenticated, redirect based on role
    if (isAuthenticated && profile) {
      switch (profile.role) {
        case 'admin':
          router.replace('/admin');
          break;
        case 'coach':
          router.replace('/coach');
          break;
        case 'student':
        default:
          // For students, check if assessment is complete
          if (isCompleted) {
            router.replace('/dashboard');
          } else {
            router.replace('/quest');
          }
          break;
      }
      return;
    }

    // Not authenticated - show EntryPortal (handled by render)
  }, [router, isAuthenticated, isLoading, profile, isCompleted, mounted, searchParams]);

  // Loading state
  if (isLoading || !mounted) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: 'linear-gradient(135deg, #FFE5DF 0%, #F5E8E5 50%, #FFF8F6 100%)' }}
      >
        <div className="w-8 h-8 border-4 border-[#FF4A23] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // If authenticated, show loading while redirecting
  if (isAuthenticated) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: 'linear-gradient(135deg, #FFE5DF 0%, #F5E8E5 50%, #FFF8F6 100%)' }}
      >
        <div className="w-8 h-8 border-4 border-[#FF4A23] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Not authenticated - show EntryPortal
  return <EntryPortal />;
}
