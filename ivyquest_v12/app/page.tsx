'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  
  useEffect(() => {
    // Check session storage for assessment state
    const sessionData = sessionStorage.getItem('ivyquest-session-v10');
    if (sessionData) {
      try {
        const session = JSON.parse(sessionData);
        if (session.state?.isComplete) {
          router.replace('/dashboard');
          return;
        }
        if (session.state?.maxFrameReached > 1) {
          router.replace(\`/quest/\${session.state.maxFrameReached}\`);
          return;
        }
      } catch (e) {}
    }
    router.replace('/quest/1');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-[#FFF5F2] flex items-center justify-center mx-auto mb-4">
          <Loader2 size={32} className="animate-spin text-[#641432]" />
        </div>
        <h1 className="text-xl font-bold text-[#641432] mb-2">IvyQuest</h1>
        <p className="text-gray-500 text-sm">Loading your journey...</p>
      </div>
    </div>
  );
}
