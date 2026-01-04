/**
 * Frame 4: Your Strengths (Context)
 * Uses SVG icons instead of emoji - v11.0
 */
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, HelpCircle } from 'lucide-react';
import { StrengthSelector } from '@/components/ui/StrengthSelector';
import { FrameEdgeProgress } from '@/components/quest/EdgeProgress';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { EDGE_VALUES } from '@/lib/constants/edge';

interface Frame4ContextProps {
  onNext: (strengths: string[]) => void;
  onBack: () => void;
}

export function Frame4Context({ onNext, onBack }: Frame4ContextProps) {
  const [selectedStrengths, setSelectedStrengths] = useState<string[]>([]);
  const { edgePoints, maxFrameReached } = useSessionStore();

  const canContinue = selectedStrengths.length >= 2 && selectedStrengths.length <= 3;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto">
          <FrameEdgeProgress 
            frameNumber={4} 
            totalFrames={6} 
            edgeEarned={(maxFrameReached - 1) * EDGE_VALUES.frameComplete} 
          />
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Progress indicator */}
        <div className="flex items-center gap-2 mb-6">
          <span className="text-sm text-gray-500">Understanding You</span>
          <span className="text-sm text-gray-400">•</span>
          <span className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
            <Check size={12} className="text-white" />
          </span>
          <div className="w-8 h-0.5 bg-gray-300" />
          <span className="text-sm text-gray-500">2</span>
          <div className="w-8 h-0.5 bg-gray-300" />
          <span className="text-sm text-gray-500">3</span>
          <div className="w-8 h-0.5 bg-gray-300" />
          <span className="w-6 h-6 rounded-full bg-[#641432] flex items-center justify-center text-white text-xs font-medium">4</span>
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Your Strengths</h1>
        
        {/* Why we ask */}
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <HelpCircle size={20} className="text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900 mb-1">Why we ask about strengths</h3>
              <p className="text-sm text-blue-700">
                Top schools want students with clear "spikes" - areas where you excel. 
                We'll help you build activities around what you're naturally good at.
              </p>
            </div>
          </div>
        </div>

        {/* Question */}
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          What are you naturally good at? (Select your top 2-3)
        </h2>
        
        {/* Strength selector with SVG icons */}
        <StrengthSelector
          selected={selectedStrengths}
          onChange={setSelectedStrengths}
          maxSelections={3}
        />

        {/* Navigation */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-4">
          <div className="max-w-2xl mx-auto flex justify-between">
            <button
              onClick={onBack}
              className="px-6 py-3 text-gray-600 font-medium hover:text-gray-900"
            >
              Back
            </button>
            <button
              onClick={() => canContinue && onNext(selectedStrengths)}
              disabled={!canContinue}
              className="px-8 py-3 text-white font-medium rounded-xl bg-[#641432] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Frame4Context;
