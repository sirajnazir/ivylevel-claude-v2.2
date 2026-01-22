/**
 * Entry Page
 * 
 * Simple redirect logic:
 * - If authenticated → Dashboard
 * - If not → Login
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthProvider';
import { Loader2, GraduationCap } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;
    
    if (isAuthenticated) {
      router.replace('/dashboard');
    } else {
      router.replace('/auth/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading while checking auth
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl">
          <GraduationCap className="w-12 h-12 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-4">IvyQuest</h1>
        <Loader2 className="w-6 h-6 text-purple-400 animate-spin mx-auto" />
      </div>
    </div>
  );
}
