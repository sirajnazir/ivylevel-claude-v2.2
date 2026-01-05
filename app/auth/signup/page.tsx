import { Suspense } from 'react';
import { SignupPage } from '@/components/auth/SignupPage';
import { RedirectIfAuthenticated } from '@/components/auth/ProtectedRoute';

export default function Signup() {
  return (
    <RedirectIfAuthenticated>
      <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-8 w-8 border-t-2 border-purple-600" /></div>}>
        <SignupPage />
      </Suspense>
    </RedirectIfAuthenticated>
  );
}
