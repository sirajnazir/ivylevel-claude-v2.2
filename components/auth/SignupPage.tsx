/**
 * Signup Page
 * 
 * Role-aware registration form with email/password + profile info.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  GraduationCap, 
  Users, 
  Shield, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff,
  User,
  ArrowLeft,
  Loader2,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { useAuth } from '@/lib/auth/AuthProvider';
import { USER_ROLES, type UserRole } from '@/types/auth';

// =============================================================================
// SIGNUP PAGE
// =============================================================================

export function SignupPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signUp, isLoading, isAuthenticated, error: authError } = useAuth();

  // Form state
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    grade: '',
    highSchool: '',
    organization: '',
    acceptTerms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  // Get role from URL
  const roleParam = searchParams.get('role') as UserRole | null;
  const role: UserRole = roleParam && roleParam in USER_ROLES ? roleParam : 'student';
  const roleConfig = USER_ROLES[role];

  // Role icons
  const roleIcons: Record<UserRole, React.ReactNode> = {
    student: <GraduationCap className="w-6 h-6" />,
    coach: <Users className="w-6 h-6" />,
    admin: <Shield className="w-6 h-6" />,
  };

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  // Update form field
  const updateField = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  // Password strength indicator
  const getPasswordStrength = (pwd: string): { score: number; label: string; color: string } => {
    let score = 0;
    if (pwd.length >= 8) score++;
    if (pwd.length >= 12) score++;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++;
    if (/\d/.test(pwd)) score++;
    if (/[^a-zA-Z0-9]/.test(pwd)) score++;

    if (score <= 2) return { score, label: 'Weak', color: 'bg-red-500' };
    if (score <= 3) return { score, label: 'Fair', color: 'bg-yellow-500' };
    if (score <= 4) return { score, label: 'Good', color: 'bg-blue-500' };
    return { score, label: 'Strong', color: 'bg-green-500' };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  // Validate form
  const validateForm = (): string | null => {
    if (!formData.firstName.trim()) return 'First name is required';
    if (!formData.lastName.trim()) return 'Last name is required';
    if (!formData.email.trim()) return 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) return 'Invalid email address';
    if (formData.password.length < 8) return 'Password must be at least 8 characters';
    if (formData.password !== formData.confirmPassword) return 'Passwords do not match';
    if (!formData.acceptTerms) return 'You must accept the terms and conditions';
    if (role === 'student' && !formData.grade) return 'Please select your grade';
    return null;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await signUp(formData.email, formData.password, role, {
        first_name: formData.firstName,
        last_name: formData.lastName,
        grade: role === 'student' ? parseInt(formData.grade) : undefined,
        high_school: formData.highSchool || undefined,
        organization: formData.organization || undefined,
      });

      if (result.error) {
        setError(result.error);
        setIsSubmitting(false);
        return;
      }

      // Success
      setSuccess(true);
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      setIsSubmitting(false);
    }
  };

  // Success state
  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-pink-50 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center"
        >
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Account Created!</h1>
          <p className="text-gray-600 mb-6">
            Please check your email to verify your account before signing in.
          </p>
          <Link
            href={`/auth/login?role=${role}`}
            className="inline-block px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
          >
            Go to Sign In
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-pink-50 flex items-center justify-center p-6">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-0 w-96 h-96 bg-purple-200 rounded-full filter blur-3xl opacity-30" />
        <div className="absolute bottom-1/4 right-0 w-96 h-96 bg-pink-200 rounded-full filter blur-3xl opacity-30" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative w-full max-w-lg"
      >
        {/* Back button */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to portal
        </Link>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div 
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-4"
              style={{ backgroundColor: `${roleConfig.color}15`, color: roleConfig.color }}
            >
              {roleIcons[role]}
              <span className="font-medium">{roleConfig.label} Registration</span>
            </div>

            <h1 className="text-2xl font-bold text-gray-900 mb-2">Create your account</h1>
            <p className="text-gray-600">Join IvyQuest to start your journey</p>
          </div>

          {/* Error display */}
          {(error || authError) && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-red-700 text-sm">{error || authError}</p>
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">First name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => updateField('firstName', e.target.value)}
                    placeholder="John"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={isSubmitting}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Last name</label>
                <input
                  type="text"
                  value={formData.lastName}
                  onChange={(e) => updateField('lastName', e.target.value)}
                  placeholder="Doe"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  placeholder="you@example.com"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            {/* Role-specific fields */}
            {role === 'student' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Grade</label>
                  <select
                    value={formData.grade}
                    onChange={(e) => updateField('grade', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={isSubmitting}
                  >
                    <option value="">Select grade</option>
                    <option value="9">9th Grade</option>
                    <option value="10">10th Grade</option>
                    <option value="11">11th Grade</option>
                    <option value="12">12th Grade</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">High School</label>
                  <input
                    type="text"
                    value={formData.highSchool}
                    onChange={(e) => updateField('highSchool', e.target.value)}
                    placeholder="Optional"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            )}

            {role === 'coach' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Organization</label>
                <input
                  type="text"
                  value={formData.organization}
                  onChange={(e) => updateField('organization', e.target.value)}
                  placeholder="Company or school name"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  disabled={isSubmitting}
                />
              </div>
            )}

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => updateField('password', e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  disabled={isSubmitting}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {/* Password strength indicator */}
              {formData.password && (
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${passwordStrength.color} transition-all`}
                      style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-500">{passwordStrength.label}</span>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Confirm password</label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => updateField('confirmPassword', e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                disabled={isSubmitting}
              />
            </div>

            {/* Terms */}
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.acceptTerms}
                onChange={(e) => updateField('acceptTerms', e.target.checked)}
                className="w-4 h-4 mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-600">
                I agree to the{' '}
                <a href="/terms" className="text-purple-600 hover:text-purple-700">Terms of Service</a>
                {' '}and{' '}
                <a href="/privacy" className="text-purple-600 hover:text-purple-700">Privacy Policy</a>
              </span>
            </label>

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting || isLoading}
              className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {isSubmitting || isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Already have an account?{' '}
              <Link
                href={`/auth/login?role=${role}`}
                className="text-purple-600 hover:text-purple-700 font-medium"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default SignupPage;
