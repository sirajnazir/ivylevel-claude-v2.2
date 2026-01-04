/**
 * Frame1Warmup Component
 * Welcome screen with name input + User Type selector for DualView.
 * @version 10.0
 */

'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Users, ArrowRight } from 'lucide-react';
import { useSessionStore, UserType } from '@/lib/store/useSessionStore';
import { BRAND_COLORS } from '@/lib/constants/brand';

interface Frame1WarmupProps {
  onComplete: () => void;
  initialName?: string;
}

export function Frame1Warmup({ onComplete, initialName = '' }: Frame1WarmupProps) {
  const [name, setName] = useState(initialName);
  const [showUserType, setShowUserType] = useState(false);
  const { userType, setUserType } = useSessionStore();

  // Show user type selector after name is entered
  useEffect(() => {
    if (name.trim().length >= 2 && !showUserType) {
      const timer = setTimeout(() => setShowUserType(true), 300);
      return () => clearTimeout(timer);
    }
  }, [name, showUserType]);

  const handleUserTypeSelect = (type: UserType) => {
    setUserType(type);
  };

  const canContinue = name.trim().length >= 2 && userType !== null;

  const handleContinue = () => {
    if (canContinue) {
      // Store name in profile (assuming useStudentStore exists)
      onComplete();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Hero */}
        <div className="text-center mb-8">
          <motion.h1
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold mb-3"
            style={{ color: BRAND_COLORS.primary }}
          >
            Welcome to IvyQuest
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-lg"
            style={{ color: BRAND_COLORS.textSecondary }}
          >
            Your personalized college admissions journey starts here
          </motion.p>
        </div>

        {/* Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="rounded-2xl p-8 shadow-xl"
          style={{
            backgroundColor: BRAND_COLORS.bgPrimary,
            border: `1px solid ${BRAND_COLORS.borderLight}`,
          }}
        >
          {/* Name Input */}
          <div className="mb-6">
            <label 
              htmlFor="name" 
              className="block text-sm font-medium mb-2"
              style={{ color: BRAND_COLORS.textSecondary }}
            >
              What's your name?
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your first name"
              className="w-full px-4 py-3 rounded-xl text-lg outline-none transition-all"
              style={{
                backgroundColor: BRAND_COLORS.bgPill,
                border: `2px solid ${name ? BRAND_COLORS.primary : BRAND_COLORS.borderLight}`,
                color: BRAND_COLORS.textPrimary,
              }}
              autoFocus
            />
          </div>

          {/* User Type Selector */}
          <AnimatePresence>
            {showUserType && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-6"
              >
                <label 
                  className="block text-sm font-medium mb-3"
                  style={{ color: BRAND_COLORS.textSecondary }}
                >
                  I am a...
                </label>
                <div className="flex gap-3">
                  <UserTypeButton
                    type="student"
                    label="Student"
                    icon={User}
                    selected={userType === 'student'}
                    onClick={() => handleUserTypeSelect('student')}
                    color={BRAND_COLORS.accent}
                  />
                  <UserTypeButton
                    type="parent"
                    label="Parent"
                    icon={Users}
                    selected={userType === 'parent'}
                    onClick={() => handleUserTypeSelect('parent')}
                    color={BRAND_COLORS.primary}
                  />
                </div>
                <p 
                  className="text-xs mt-2 text-center"
                  style={{ color: BRAND_COLORS.textMuted }}
                >
                  This helps us personalize your experience
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Continue Button */}
          <motion.button
            onClick={handleContinue}
            disabled={!canContinue}
            className="w-full py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: canContinue ? BRAND_COLORS.primary : BRAND_COLORS.bgPill,
              color: canContinue ? 'white' : BRAND_COLORS.textMuted,
            }}
            whileHover={canContinue ? { scale: 1.02 } : {}}
            whileTap={canContinue ? { scale: 0.98 } : {}}
          >
            {canContinue ? (
              <>
                Let's Begin
                <ArrowRight size={20} />
              </>
            ) : (
              'Enter your name to continue'
            )}
          </motion.button>
        </motion.div>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center mt-6 text-sm"
          style={{ color: BRAND_COLORS.textMuted }}
        >
          Takes about 10 minutes • Your data is private
        </motion.p>
      </motion.div>
    </div>
  );
}

interface UserTypeButtonProps {
  type: UserType;
  label: string;
  icon: React.ElementType;
  selected: boolean;
  onClick: () => void;
  color: string;
}

function UserTypeButton({ type, label, icon: Icon, selected, onClick, color }: UserTypeButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      className="flex-1 py-4 px-4 rounded-xl flex flex-col items-center gap-2 transition-all"
      style={{
        backgroundColor: selected ? `${color}15` : BRAND_COLORS.bgPill,
        border: `2px solid ${selected ? color : 'transparent'}`,
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div
        className="w-12 h-12 rounded-full flex items-center justify-center"
        style={{
          backgroundColor: selected ? color : BRAND_COLORS.borderLight,
        }}
      >
        <Icon size={24} color={selected ? 'white' : BRAND_COLORS.textMuted} />
      </div>
      <span
        className="font-medium"
        style={{ color: selected ? color : BRAND_COLORS.textSecondary }}
      >
        {label}
      </span>
    </motion.button>
  );
}

export default Frame1Warmup;
