'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute
      requireAuth={true}
      redirectTo="/auth/login?role=student"
      loadingMessage="Loading your dashboard..."
    >
      {children}
    </ProtectedRoute>
  );
}
