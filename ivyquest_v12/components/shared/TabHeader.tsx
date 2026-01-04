/**
 * TabHeader - Navigation Header with Tabs
 * v12.0 - Matches original frontend specification
 */
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Flame, Search, Bell, LogOut, User,
  BarChart3, Map, Calendar, TrendingUp, Video, Bot
} from 'lucide-react';
import { COLORS, TABS, type TabId } from '@/lib/constants/design';

const TAB_ICONS: Record<TabId, React.ReactNode> = {
  assessment: <BarChart3 size={16} />,
  gameplan: <Map size={16} />,
  preparation: <Calendar size={16} />,
  growth: <TrendingUp size={16} />,
  sessions: <Video size={16} />,
  multiagents: <Bot size={16} />,
};

interface TabHeaderProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  studentName?: string;
  onLogout?: () => void;
}

export function TabHeader({ activeTab, onTabChange, studentName = 'Student', onLogout }: TabHeaderProps) {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header 
      className="sticky top-0 z-50 bg-white border-b"
      style={{ 
        height: '64px',
        borderColor: COLORS.borderHeader,
      }}
    >
      <div className="h-full max-w-[1600px] mx-auto px-8 flex items-center justify-between">
        {/* Left: Logo + Tabs */}
        <div className="flex items-center gap-6">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: COLORS.primary }}
            >
              <Flame size={18} className="text-white" />
            </div>
            <span className="font-semibold text-lg" style={{ color: COLORS.textHeading }}>
              IvyQuest
            </span>
          </div>

          {/* Tab Navigation */}
          <nav className="flex items-center gap-1">
            {TABS.filter(t => t.enabled).map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors"
                style={{
                  color: activeTab === tab.id ? COLORS.primary : COLORS.textSecondary,
                  backgroundColor: activeTab === tab.id ? COLORS.primaryLight : 'transparent',
                }}
                whileHover={{ backgroundColor: activeTab === tab.id ? COLORS.primaryLight : COLORS.bgSubtle }}
                whileTap={{ scale: 0.98 }}
              >
                {TAB_ICONS[tab.id]}
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTabIndicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5"
                    style={{ backgroundColor: COLORS.primary }}
                  />
                )}
              </motion.button>
            ))}
          </nav>
        </div>

        {/* Right: Search + Actions */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative">
            <Search 
              size={16} 
              className="absolute left-3 top-1/2 -translate-y-1/2" 
              style={{ color: COLORS.textMuted }}
            />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-2 rounded-full text-sm border focus:outline-none focus:ring-2"
              style={{
                borderColor: COLORS.borderDefault,
                width: '200px',
              }}
            />
          </div>

          {/* Notifications */}
          <button 
            className="relative p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <Bell size={20} style={{ color: COLORS.textSecondary }} />
            <span 
              className="absolute top-1 right-1 w-2 h-2 rounded-full"
              style={{ backgroundColor: COLORS.primary }}
            />
          </button>

          {/* Profile */}
          <div className="flex items-center gap-2">
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center"
              style={{ backgroundColor: COLORS.bgSubtle }}
            >
              <User size={16} style={{ color: COLORS.textSecondary }} />
            </div>
            <span className="text-sm font-medium" style={{ color: COLORS.textPrimary }}>
              {studentName}
            </span>
          </div>

          {/* Logout */}
          <button 
            onClick={onLogout}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <LogOut size={20} style={{ color: COLORS.textSecondary }} />
          </button>
        </div>
      </div>
    </header>
  );
}

export default TabHeader;
