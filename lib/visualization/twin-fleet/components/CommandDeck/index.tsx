/**
 * IvyQuest v3.0 — Command Deck
 * 
 * Themed container with HUD for twin fleet visualization.
 * 
 * @version 1.0.0
 * @module components/CommandDeck/index
 */

'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  SCHOOL_COLORS,
  COMMAND_DECK_THEMES,
  HUD_CONFIG,
  type SchoolId,
  type ScoreTierId,
} from '../../constants/twin.constants';
import { withAlpha, getTierColors } from '../../utils/twinUtils';
import type { CommandDeckProps, DeckHUDProps, CategoryScores } from '../../types/twin.types';

// ============================================================================
// DECK BACKGROUND
// ============================================================================

const DeckBackground: React.FC<{
  theme: 'default' | SchoolId;
  children: React.ReactNode;
}> = ({ theme, children }) => {
  const themeConfig = theme === 'default' 
    ? COMMAND_DECK_THEMES.default 
    : {
        ...COMMAND_DECK_THEMES.default,
        background: SCHOOL_COLORS[theme]?.gradient || COMMAND_DECK_THEMES.default.background,
        accentColor: SCHOOL_COLORS[theme]?.accent || COMMAND_DECK_THEMES.default.accentColor,
      };
  
  return (
    <div
      className="relative w-full h-full overflow-hidden rounded-2xl"
      style={{
        background: themeConfig.background,
      }}
    >
      {/* Grid overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(${themeConfig.gridColor} 1px, transparent 1px),
            linear-gradient(90deg, ${themeConfig.gridColor} 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
        }}
      />
      
      {/* Vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at center, transparent 30%, rgba(0,0,0,0.4) 100%)',
        }}
      />
      
      {/* Scan lines (subtle) */}
      <div
        className="absolute inset-0 pointer-events-none opacity-5"
        style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.1) 2px, rgba(255,255,255,0.1) 4px)',
        }}
      />
      
      {/* Corner accents */}
      <svg className="absolute top-0 left-0 w-24 h-24 pointer-events-none">
        <path
          d="M 0 24 L 0 0 L 24 0"
          fill="none"
          stroke={themeConfig.accentColor}
          strokeWidth="2"
          opacity="0.5"
        />
      </svg>
      <svg className="absolute top-0 right-0 w-24 h-24 pointer-events-none">
        <path
          d="M 96 24 L 96 0 L 72 0"
          fill="none"
          stroke={themeConfig.accentColor}
          strokeWidth="2"
          opacity="0.5"
        />
      </svg>
      <svg className="absolute bottom-0 left-0 w-24 h-24 pointer-events-none">
        <path
          d="M 0 72 L 0 96 L 24 96"
          fill="none"
          stroke={themeConfig.accentColor}
          strokeWidth="2"
          opacity="0.5"
        />
      </svg>
      <svg className="absolute bottom-0 right-0 w-24 h-24 pointer-events-none">
        <path
          d="M 96 72 L 96 96 L 72 96"
          fill="none"
          stroke={themeConfig.accentColor}
          strokeWidth="2"
          opacity="0.5"
        />
      </svg>
      
      {children}
    </div>
  );
};

// ============================================================================
// DECK HUD
// ============================================================================

const DeckHUD: React.FC<DeckHUDProps> = ({
  ivyReadyScore,
  tier,
  categoryScores,
  selectedSchool,
  schoolProbability,
  styleMatch,
  position = 'bottom',
}) => {
  const tierColors = getTierColors(tier);
  const schoolColors = selectedSchool ? SCHOOL_COLORS[selectedSchool] : null;
  
  // Score bar component
  const ScoreBar: React.FC<{
    label: string;
    value: number;
    color: string;
  }> = ({ label, value, color }) => (
    <div className="flex items-center gap-2">
      <span className="text-xs text-white/50 w-20 uppercase tracking-wide">{label}</span>
      <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      <span className="text-xs font-mono text-white/70 w-8 text-right">
        {Math.round(value)}
      </span>
    </div>
  );
  
  const positionClasses = {
    top: 'top-4 left-4 right-4',
    bottom: 'bottom-4 left-4 right-4',
    left: 'top-4 bottom-4 left-4 w-48',
    right: 'top-4 bottom-4 right-4 w-48',
  };
  
  return (
    <motion.div
      className={`absolute ${positionClasses[position]} z-30`}
      initial={{ opacity: 0, y: position === 'bottom' ? 20 : position === 'top' ? -20 : 0 }}
      animate={{ opacity: HUD_CONFIG.hudOpacity, y: 0 }}
      transition={{ delay: 0.5, duration: 0.5 }}
    >
      <div className="bg-black/40 backdrop-blur-md rounded-xl border border-white/10 p-4">
        {/* Top section - Main score */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {/* Ivy+ Ready Score */}
            <div className="text-center">
              <div
                className="text-3xl font-bold"
                style={{ color: tierColors.primary }}
              >
                {Math.round(ivyReadyScore)}
              </div>
              <div className="text-xs text-white/40 uppercase tracking-wide">
                Ivy+ Ready
              </div>
            </div>
            
            {/* Tier badge */}
            <div
              className="px-2 py-1 rounded text-xs font-semibold uppercase"
              style={{
                backgroundColor: withAlpha(tierColors.primary, 0.2),
                color: tierColors.primary,
              }}
            >
              {tier}
            </div>
          </div>
          
          {/* Selected school info */}
          {selectedSchool && schoolColors && (
            <div className="text-right">
              <div
                className="text-lg font-semibold"
                style={{ color: schoolColors.primary }}
              >
                {schoolColors.name}
              </div>
              {schoolProbability !== undefined && (
                <div className="text-sm text-white/60">
                  {Math.round(schoolProbability)}% probability
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Category score bars */}
        {HUD_CONFIG.showScoreBars && (
          <div className="space-y-2">
            <ScoreBar
              label="Aptitude"
              value={categoryScores.aptitude}
              color={HUD_CONFIG.scoreBarColors.aptitude}
            />
            <ScoreBar
              label="Passion"
              value={categoryScores.passion}
              color={HUD_CONFIG.scoreBarColors.passion}
            />
            <ScoreBar
              label="Community"
              value={categoryScores.community}
              color={HUD_CONFIG.scoreBarColors.community}
            />
            <ScoreBar
              label="Operating"
              value={categoryScores.operating}
              color={HUD_CONFIG.scoreBarColors.operating}
            />
          </div>
        )}
        
        {/* Style match indicator */}
        {HUD_CONFIG.showStyleMatchIndicator && styleMatch !== undefined && (
          <div className="mt-4 pt-3 border-t border-white/10">
            <div className="flex items-center justify-between text-xs">
              <span className="text-white/50">Style Match</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${styleMatch * 100}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                  />
                </div>
                <span className="text-white/70 font-mono">
                  {Math.round(styleMatch * 100)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const CommandDeck: React.FC<CommandDeckProps> = ({
  studentName,
  ivyReadyScore,
  tier,
  categoryScores = { aptitude: 0, passion: 0, community: 0, operating: 0 },
  targetSchools,
  activeSchool = null,
  showHUD = true,
  showScoreBars = true,
  children,
  theme = 'default',
}) => {
  // Use active school as theme if available
  const effectiveTheme = activeSchool || theme;
  
  // Get school-specific data if selected
  const schoolProbability = undefined; // Would come from scores
  const styleMatch = undefined; // Would come from scores
  
  return (
    <DeckBackground theme={effectiveTheme}>
      {/* Header with student name */}
      <motion.div
        className="absolute top-4 left-1/2 -translate-x-1/2 z-30"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="px-4 py-2 bg-black/40 backdrop-blur-sm rounded-full border border-white/10">
          <span className="text-white/60 text-sm">
            {studentName}'s Fleet
          </span>
        </div>
      </motion.div>
      
      {/* Main content area */}
      <div className="absolute inset-0 pt-16 pb-32">
        {children}
      </div>
      
      {/* HUD */}
      {showHUD && (
        <DeckHUD
          ivyReadyScore={ivyReadyScore}
          tier={tier}
          categoryScores={categoryScores}
          selectedSchool={activeSchool}
          schoolProbability={schoolProbability}
          styleMatch={styleMatch}
          position="bottom"
        />
      )}
      
      {/* School count indicator */}
      <motion.div
        className="absolute top-4 right-4 z-30"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-center gap-2 px-3 py-1.5 bg-black/40 backdrop-blur-sm rounded-full border border-white/10">
          <span className="text-lg">🏫</span>
          <span className="text-white/80 text-sm font-medium">
            {targetSchools.length} schools
          </span>
        </div>
      </motion.div>
    </DeckBackground>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export default CommandDeck;
export { DeckBackground, DeckHUD };
