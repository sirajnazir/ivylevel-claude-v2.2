/**
 * Digital Twin Store (Zustand)
 * Manages the Digital Twin Fleet state for all target schools
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { twinLogger } from '@/lib/trace';

// ============================================
// Type Definitions
// ============================================

export type GearTier =
  | 'rusty'
  | 'bronze'
  | 'iron'
  | 'silver'
  | 'gold'
  | 'diamond'
  | 'legendary'
  | 'mythic';

export type GearSlot =
  | 'helmet'    // Academic achievement
  | 'armor'     // Standardized tests
  | 'weapon'    // Spike/passion
  | 'shield'    // Community service
  | 'boots'     // Leadership
  | 'accessory'; // Special factors (legacy, athlete, etc.)

export interface GearItem {
  slot: GearSlot;
  tier: GearTier;
  name: string;
  attribute: string;
  value: number;
  description: string;
  equippedAt: number;
}

export interface DigitalTwin {
  schoolId: string;
  schoolName: string;
  schoolColor: string;
  gear: Record<GearSlot, GearItem | null>;
  profileStrength: number;
  acceptanceProbability: number;
  isActive: boolean;
  lastUpdated: number;
  animationState: 'idle' | 'equipping' | 'celebrating' | 'analyzing';
}

export interface TwinFleet {
  twins: Record<string, DigitalTwin>;
  activeTwinId: string | null;
  focusedTwinId: string | null;
}

// ============================================
// Gear Tier Thresholds
// ============================================

const GEAR_TIERS: { tier: GearTier; minValue: number; maxValue: number }[] = [
  { tier: 'mythic', minValue: 0.95, maxValue: 1.0 },
  { tier: 'legendary', minValue: 0.85, maxValue: 0.95 },
  { tier: 'diamond', minValue: 0.75, maxValue: 0.85 },
  { tier: 'gold', minValue: 0.60, maxValue: 0.75 },
  { tier: 'silver', minValue: 0.45, maxValue: 0.60 },
  { tier: 'iron', minValue: 0.30, maxValue: 0.45 },
  { tier: 'bronze', minValue: 0.15, maxValue: 0.30 },
  { tier: 'rusty', minValue: 0, maxValue: 0.15 },
];

export function getGearTier(normalizedValue: number): GearTier {
  for (const { tier, minValue, maxValue } of GEAR_TIERS) {
    if (normalizedValue >= minValue && normalizedValue <= maxValue) {
      return tier;
    }
  }
  return 'rusty';
}

// ============================================
// Gear Slot Mappings
// ============================================

const SLOT_CONFIGS: Record<GearSlot, { attribute: string; baseName: string }> = {
  helmet: { attribute: 'GPA', baseName: 'Scholar\'s Crown' },
  armor: { attribute: 'Test Scores', baseName: 'Academic Plate' },
  weapon: { attribute: 'Spike/Passion', baseName: 'Passion Blade' },
  shield: { attribute: 'Community', baseName: 'Service Shield' },
  boots: { attribute: 'Leadership', baseName: 'Leader\'s Greaves' },
  accessory: { attribute: 'Special Factors', baseName: 'Legacy Charm' },
};

function createGearItem(
  slot: GearSlot,
  normalizedValue: number,
  specificAttribute?: string
): GearItem {
  const tier = getGearTier(normalizedValue);
  const config = SLOT_CONFIGS[slot];
  const tierPrefix: Record<GearTier, string> = {
    rusty: 'Rusty',
    bronze: 'Bronze',
    iron: 'Iron',
    silver: 'Silver',
    gold: 'Golden',
    diamond: 'Diamond',
    legendary: 'Legendary',
    mythic: 'Mythic',
  };

  return {
    slot,
    tier,
    name: `${tierPrefix[tier]} ${config.baseName}`,
    attribute: specificAttribute || config.attribute,
    value: normalizedValue,
    description: getGearDescription(slot, tier, normalizedValue),
    equippedAt: Date.now(),
  };
}

function getGearDescription(slot: GearSlot, tier: GearTier, value: number): string {
  const percentage = Math.round(value * 100);
  const descriptions: Record<GearSlot, Record<GearTier, string>> = {
    helmet: {
      mythic: `Top 1% academic performance (${percentage}%)`,
      legendary: `Exceptional academic standing (${percentage}%)`,
      diamond: `Outstanding grades (${percentage}%)`,
      gold: `Strong academic record (${percentage}%)`,
      silver: `Solid academics (${percentage}%)`,
      iron: `Decent grades (${percentage}%)`,
      bronze: `Room for improvement (${percentage}%)`,
      rusty: `Needs attention (${percentage}%)`,
    },
    armor: {
      mythic: `Perfect or near-perfect scores`,
      legendary: `Outstanding test performance`,
      diamond: `Excellent standardized scores`,
      gold: `Strong test scores`,
      silver: `Solid performance`,
      iron: `Average scores`,
      bronze: `Below average`,
      rusty: `Significant gap`,
    },
    weapon: {
      mythic: `World-class expertise in your spike`,
      legendary: `National recognition in passion area`,
      diamond: `Significant achievements`,
      gold: `Clear dedicated passion`,
      silver: `Growing expertise`,
      iron: `Developing interests`,
      bronze: `Exploring options`,
      rusty: `Finding your path`,
    },
    shield: {
      mythic: `Transformative community impact`,
      legendary: `Significant organizational change`,
      diamond: `Strong leadership in service`,
      gold: `Consistent meaningful service`,
      silver: `Regular volunteer engagement`,
      iron: `Some community involvement`,
      bronze: `Limited service experience`,
      rusty: `Opportunity to contribute`,
    },
    boots: {
      mythic: `Exceptional multi-org leadership`,
      legendary: `Significant leadership roles`,
      diamond: `Strong leadership presence`,
      gold: `Clear leadership experience`,
      silver: `Growing leadership skills`,
      iron: `Some leadership exposure`,
      bronze: `Emerging leader`,
      rusty: `Leadership potential`,
    },
    accessory: {
      mythic: `Exceptional special factors`,
      legendary: `Strong special factors`,
      diamond: `Notable advantages`,
      gold: `Positive factors`,
      silver: `Some advantages`,
      iron: `Neutral factors`,
      bronze: `Few special factors`,
      rusty: `Standard profile`,
    },
  };

  return descriptions[slot][tier];
}

// ============================================
// Store State Interface
// ============================================

interface TwinStoreState {
  fleet: TwinFleet;
  isInitialized: boolean;

  // Fleet Management
  initializeTwin: (schoolId: string, schoolName: string, schoolColor: string) => void;
  removeTwin: (schoolId: string) => void;
  clearFleet: () => void;

  // Twin Selection
  setActiveTwin: (schoolId: string | null) => void;
  setFocusedTwin: (schoolId: string | null) => void;

  // Gear Management
  equipGear: (schoolId: string, slot: GearSlot, normalizedValue: number, attribute?: string) => void;
  updateAllGear: (schoolId: string, values: Partial<Record<GearSlot, number>>) => void;

  // Score Updates
  updateTwinScores: (schoolId: string, profileStrength: number, probability: number) => void;

  // Animation State
  setAnimationState: (schoolId: string, state: DigitalTwin['animationState']) => void;

  // Getters
  getTwin: (schoolId: string) => DigitalTwin | undefined;
  getActiveTwin: () => DigitalTwin | undefined;
  getAllTwins: () => DigitalTwin[];
  getTwinCount: () => number;
}

// ============================================
// Default Twin
// ============================================

function createDefaultTwin(schoolId: string, schoolName: string, schoolColor: string): DigitalTwin {
  return {
    schoolId,
    schoolName,
    schoolColor,
    gear: {
      helmet: null,
      armor: null,
      weapon: null,
      shield: null,
      boots: null,
      accessory: null,
    },
    profileStrength: 0,
    acceptanceProbability: 0,
    isActive: true,
    lastUpdated: Date.now(),
    animationState: 'idle',
  };
}

// ============================================
// Store Creation
// ============================================

export const useTwinStore = create<TwinStoreState>()(
  devtools(
    persist(
      immer((set, get) => ({
        fleet: {
          twins: {},
          activeTwinId: null,
          focusedTwinId: null,
        },
        isInitialized: false,

        // Fleet Management
        initializeTwin: (schoolId, schoolName, schoolColor) =>
          set((state) => {
            if (!state.fleet.twins[schoolId]) {
              state.fleet.twins[schoolId] = createDefaultTwin(schoolId, schoolName, schoolColor);

              // Set as active if first twin
              if (Object.keys(state.fleet.twins).length === 1) {
                state.fleet.activeTwinId = schoolId;
              }

              twinLogger.logFleetUpdate(Object.keys(state.fleet.twins), 'add');
            }
            state.isInitialized = true;
          }),

        removeTwin: (schoolId) =>
          set((state) => {
            delete state.fleet.twins[schoolId];

            // Clear active/focused if removed
            if (state.fleet.activeTwinId === schoolId) {
              const remaining = Object.keys(state.fleet.twins);
              state.fleet.activeTwinId = remaining[0] || null;
            }
            if (state.fleet.focusedTwinId === schoolId) {
              state.fleet.focusedTwinId = null;
            }

            twinLogger.logFleetUpdate(Object.keys(state.fleet.twins), 'remove');
          }),

        clearFleet: () =>
          set((state) => {
            state.fleet.twins = {};
            state.fleet.activeTwinId = null;
            state.fleet.focusedTwinId = null;
          }),

        // Twin Selection
        setActiveTwin: (schoolId) =>
          set((state) => {
            state.fleet.activeTwinId = schoolId;
          }),

        setFocusedTwin: (schoolId) =>
          set((state) => {
            state.fleet.focusedTwinId = schoolId;
          }),

        // Gear Management
        equipGear: (schoolId, slot, normalizedValue, attribute) =>
          set((state) => {
            const twin = state.fleet.twins[schoolId];
            if (!twin) return;

            const previousGear = twin.gear[slot];
            const newGear = createGearItem(slot, normalizedValue, attribute);
            twin.gear[slot] = newGear;
            twin.lastUpdated = Date.now();
            twin.animationState = 'equipping';

            twinLogger.logGearUpgrade({
              schoolId,
              schoolName: twin.schoolName,
              gearSlot: slot,
              gearTier: newGear.tier,
              previousGear: previousGear?.name,
              newGear: newGear.name,
              attribute: newGear.attribute,
              attributeValue: normalizedValue,
            });

            // Reset animation after delay
            setTimeout(() => {
              const store = get();
              const currentTwin = store.fleet.twins[schoolId];
              if (currentTwin?.animationState === 'equipping') {
                set((s) => {
                  const t = s.fleet.twins[schoolId];
                  if (t) t.animationState = 'idle';
                });
              }
            }, 1500);
          }),

        updateAllGear: (schoolId, values) =>
          set((state) => {
            const twin = state.fleet.twins[schoolId];
            if (!twin) return;

            (Object.entries(values) as [GearSlot, number][]).forEach(([slot, value]) => {
              if (value !== undefined) {
                const newGear = createGearItem(slot, value);
                twin.gear[slot] = newGear;
              }
            });
            twin.lastUpdated = Date.now();
          }),

        // Score Updates
        updateTwinScores: (schoolId, profileStrength, probability) =>
          set((state) => {
            const twin = state.fleet.twins[schoolId];
            if (!twin) return;

            twin.profileStrength = profileStrength;
            twin.acceptanceProbability = probability;
            twin.lastUpdated = Date.now();
          }),

        // Animation State
        setAnimationState: (schoolId, animationState) =>
          set((state) => {
            const twin = state.fleet.twins[schoolId];
            if (!twin) return;

            twin.animationState = animationState;

            twinLogger.logAnimation(schoolId, animationState, 0);
          }),

        // Getters
        getTwin: (schoolId) => get().fleet.twins[schoolId],
        getActiveTwin: () => {
          const { fleet } = get();
          return fleet.activeTwinId ? fleet.twins[fleet.activeTwinId] : undefined;
        },
        getAllTwins: () => Object.values(get().fleet.twins),
        getTwinCount: () => Object.keys(get().fleet.twins).length,
      })),
      {
        name: 'ivyquest-twin-fleet',
        partialize: (state) => ({
          fleet: state.fleet,
          isInitialized: state.isInitialized,
        }),
      }
    ),
    { name: 'TwinStore' }
  )
);

// ============================================
// Selector Hooks
// ============================================

export const useActiveTwin = () => useTwinStore((s) => s.getActiveTwin());
export const useTwin = (schoolId: string) => useTwinStore((s) => s.fleet.twins[schoolId]);
export const useAllTwins = () => useTwinStore((s) => s.getAllTwins());
export const useTwinGear = (schoolId: string) =>
  useTwinStore((s) => s.fleet.twins[schoolId]?.gear);
