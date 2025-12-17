/**
 * IvyQuest v3.0 — Fleet Display
 * 
 * Arranges base twin and school twins in various layouts.
 * 
 * @version 1.0.0
 * @module components/TwinFleet/FleetDisplay
 */

'use client';

import React, { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import BaseTwin from '../TwinAvatar/BaseTwin';
import SchoolTwin from './SchoolTwin';
import {
  FLEET_LAYOUTS,
  TWIN_SIZES,
  type SchoolId,
  type FleetLayoutId,
} from '../../constants/twin.constants';
import {
  calculateArcPositions,
  calculateGridPositions,
  calculateOrbitalPositions,
  staggerDelay,
} from '../../utils/twinUtils';
import type { FleetDisplayProps, SchoolTwinData } from '../../types/twin.types';

// ============================================================================
// COMPONENT
// ============================================================================

const FleetDisplay: React.FC<FleetDisplayProps> = ({
  baseTwin,
  schoolTwins,
  layout = 'arc',
  selectedSchool = null,
  onTwinSelect,
  showAll = true,
  maxDisplay = 10,
}) => {
  const [containerSize, setContainerSize] = useState({ width: 600, height: 400 });
  
  // Get layout config
  const layoutConfig = FLEET_LAYOUTS[layout];
  
  // Limit displayed twins
  const displayedTwins = showAll 
    ? schoolTwins.slice(0, maxDisplay) 
    : selectedSchool 
    ? schoolTwins.filter(t => t.schoolId === selectedSchool)
    : schoolTwins.slice(0, maxDisplay);
  
  // Calculate positions based on layout
  const positions = useMemo(() => {
    const count = displayedTwins.length;
    
    switch (layout) {
      case 'arc':
        return calculateArcPositions(
          count,
          containerSize.width / 2,
          containerSize.height * 0.3,
          containerSize.height * 0.25,
          -60,
          60
        );
      
      case 'grid':
        return calculateGridPositions(
          count,
          Math.min(4, count),
          containerSize.width * 0.15,
          containerSize.height * 0.1,
          containerSize.width * 0.2
        );
      
      case 'line':
        const spacing = containerSize.width / (count + 1);
        return displayedTwins.map((_, i) => ({
          x: spacing * (i + 1),
          y: containerSize.height * 0.3,
        }));
      
      case 'focus':
        if (selectedSchool) {
          // Selected twin in center, others orbit
          const selectedIndex = displayedTwins.findIndex(t => t.schoolId === selectedSchool);
          const others = displayedTwins.filter(t => t.schoolId !== selectedSchool);
          const orbitPositions = calculateOrbitalPositions(
            others.length,
            containerSize.width / 2,
            containerSize.height * 0.35,
            containerSize.width * 0.3,
            0
          );
          
          const positions: { x: number; y: number }[] = [];
          let orbitIndex = 0;
          
          for (let i = 0; i < displayedTwins.length; i++) {
            if (i === selectedIndex) {
              positions.push({
                x: containerSize.width / 2,
                y: containerSize.height * 0.35,
              });
            } else {
              positions.push(orbitPositions[orbitIndex++]);
            }
          }
          
          return positions;
        }
        
        // No selection, use arc
        return calculateArcPositions(
          count,
          containerSize.width / 2,
          containerSize.height * 0.3,
          containerSize.height * 0.25,
          -60,
          60
        );
      
      default:
        return calculateArcPositions(
          count,
          containerSize.width / 2,
          containerSize.height * 0.3,
          containerSize.height * 0.25,
          -60,
          60
        );
    }
  }, [layout, displayedTwins, containerSize, selectedSchool]);
  
  // Base twin position
  const baseTwinPosition = {
    x: (layoutConfig.baseTwinPosition?.x ?? 50) * containerSize.width / 100,
    y: (layoutConfig.baseTwinPosition?.y ?? 70) * containerSize.height / 100,
  };
  
  // Get school twin size based on selection state
  const getSchoolTwinSize = (schoolId: SchoolId) => {
    if (layout === 'focus' && selectedSchool) {
      return schoolId === selectedSchool ? 'lg' : 'sm';
    }
    return 'md';
  };
  
  return (
    <div
      className="relative w-full h-full min-h-[400px]"
      ref={(el) => {
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.width !== containerSize.width || rect.height !== containerSize.height) {
            setContainerSize({ width: rect.width, height: rect.height });
          }
        }
      }}
    >
      {/* Connection lines (optional) */}
      <svg
        className="absolute inset-0 pointer-events-none"
        style={{ width: '100%', height: '100%' }}
      >
        <defs>
          <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00D4FF" stopOpacity="0" />
            <stop offset="50%" stopColor="#00D4FF" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#00D4FF" stopOpacity="0" />
          </linearGradient>
        </defs>
        
        {/* Lines from base twin to school twins */}
        {positions.map((pos, i) => (
          <motion.line
            key={`line-${i}`}
            x1={baseTwinPosition.x}
            y1={baseTwinPosition.y - 40}
            x2={pos.x}
            y2={pos.y + 40}
            stroke="url(#connectionGradient)"
            strokeWidth="1"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.5 }}
            transition={{ delay: staggerDelay(i, 100) / 1000, duration: 0.5 }}
          />
        ))}
      </svg>
      
      {/* School twins */}
      <AnimatePresence mode="popLayout">
        {displayedTwins.map((twin, index) => (
          <motion.div
            key={twin.schoolId}
            className="absolute"
            initial={{ opacity: 0, scale: 0 }}
            animate={{
              opacity: 1,
              scale: 1,
              x: positions[index]?.x - TWIN_SIZES[getSchoolTwinSize(twin.schoolId)].width / 2,
              y: positions[index]?.y - TWIN_SIZES[getSchoolTwinSize(twin.schoolId)].height / 2,
            }}
            exit={{ opacity: 0, scale: 0 }}
            transition={{
              delay: staggerDelay(index, 100) / 1000,
              type: 'spring',
              stiffness: 200,
              damping: 20,
            }}
          >
            <SchoolTwin
              schoolId={twin.schoolId}
              probability={twin.probability}
              categoryScores={twin.categoryScores}
              styleMatch={twin.styleMatch}
              isSelected={twin.schoolId === selectedSchool}
              size={getSchoolTwinSize(twin.schoolId)}
              onClick={() => onTwinSelect?.(twin.schoolId)}
            />
          </motion.div>
        ))}
      </AnimatePresence>
      
      {/* Base twin (centered bottom) */}
      <motion.div
        className="absolute"
        style={{
          left: baseTwinPosition.x - TWIN_SIZES.lg.width / 2,
          top: baseTwinPosition.y - TWIN_SIZES.lg.height / 2,
        }}
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, type: 'spring', stiffness: 150 }}
      >
        <BaseTwin
          score={baseTwin.score}
          tier={baseTwin.tier}
          style={baseTwin.style}
          size="lg"
          isActive={true}
          showAura={true}
          showParticles={false}
        />
        
        {/* Base twin label */}
        <motion.div
          className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <span className="text-sm font-semibold text-white/60">Your Profile</span>
        </motion.div>
      </motion.div>
      
      {/* Layout indicator (dev only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute bottom-2 right-2 text-xs text-white/30">
          Layout: {layout}
        </div>
      )}
    </div>
  );
};

export default FleetDisplay;
