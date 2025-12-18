/**
 * IvyLevel Design System
 * Extracted from Figma design files (Dec 2024)
 * Apple Fitness/Watch inspired with IvyLevel branding
 */

export const IVYLEVEL_DESIGN = {
  // === COLORS ===
  colors: {
    // Primary Orange (Main brand color)
    primary: {
      main: '#FF4A23',
      light: '#FF7224',
      lighter: '#FF9924',
      dark: '#F56F0D',
      subtle: '#FFE6E0',
      cream: '#FFEBD3',
    },

    // Secondary Colors
    secondary: {
      yellow: '#FFBB00',
      yellowGold: '#EAB705',
      green: '#1DBF73',
      greenLight: '#15D77C',
      red: '#FB343E',
      redDark: '#BD2F11',
      coral: '#FF504F',
      peach: '#FFBB6D',
    },

    // Neutrals & Grays
    neutral: {
      offWhite: '#F5F4F3',
      lightGray: '#F7F8FA',
      gray100: '#F0F0F0',
      gray200: '#DFE0E4',
      gray300: '#9698A6',
      gray400: '#7B7E8F',
      gray500: '#616479',
      gray600: '#484848',
      gray700: '#020202',
      white: '#FDFDFD',
    },

    // Ring Colors (matching existing system)
    rings: {
      aptitude: {
        start: '#FF4A23',
        end: '#FF7224',
      },
      passion: {
        start: '#7B61FF',
        end: '#9B7FFF',
      },
      service: {
        start: '#1DBF73',
        end: '#15D77C',
      },
      identity: {
        start: '#55AAAA',
        end: '#CCE6E6',
      },
    },
  },

  // === GLASSMORPHISM ===
  glass: {
    // Primary glass (with stronger orange tint)
    primary: {
      background: 'rgba(255, 255, 255, 0.85)',
      backdropBlur: 'blur(32px)',
      border: '1px solid rgba(255, 255, 255, 0.4)',
      shadow: '0 12px 48px 0 rgba(255, 74, 35, 0.20)',
      borderRadius: '20px',
    },
    // Notification glass (most prominent - for floating notifications)
    notification: {
      background: 'rgba(255, 255, 255, 0.92)',
      backdropBlur: 'blur(40px)',
      border: '2px solid rgba(255, 255, 255, 0.6)',
      shadow: '0 16px 64px 0 rgba(255, 74, 35, 0.30)',
      glow: '0 0 40px rgba(255, 74, 35, 0.4)',
      borderRadius: '24px',
    },
    // Neutral glass
    neutral: {
      background: 'rgba(247, 248, 250, 0.8)',
      backdropBlur: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.4)',
      shadow: '0 4px 16px 0 rgba(97, 100, 121, 0.06)',
      borderRadius: '16px',
    },
    // Strong glass (more prominent)
    strong: {
      background: 'rgba(255, 255, 255, 0.85)',
      backdropBlur: 'blur(32px)',
      border: '1px solid rgba(255, 255, 255, 0.5)',
      shadow: '0 12px 48px 0 rgba(255, 74, 35, 0.12)',
      borderRadius: '24px',
    },
    // Subtle glass (background elements)
    subtle: {
      background: 'rgba(255, 255, 255, 0.5)',
      backdropBlur: 'blur(16px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      shadow: '0 2px 8px 0 rgba(0, 0, 0, 0.04)',
      borderRadius: '12px',
    },
  },

  // === TYPOGRAPHY ===
  typography: {
    fontFamily: {
      sans: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", system-ui, sans-serif',
      mono: 'ui-monospace, "SF Mono", "Menlo", "Monaco", monospace',
    },
    fontSize: {
      xs: '11px',
      sm: '13px',
      base: '15px',
      md: '15px',
      lg: '17px',
      xl: '20px',
      xxl: '24px',
      xxxl: '32px',
      display: '48px',
    },
    fontWeight: {
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
    },
  },

  // === SPACING (8px base) ===
  spacing: {
    px: '1px',
    0: '0',
    1: '4px',
    2: '8px',
    3: '12px',
    4: '16px',
    5: '20px',
    6: '24px',
    8: '32px',
    10: '40px',
    12: '48px',
    16: '64px',
    20: '80px',
    24: '96px',
  },

  // === BORDER RADIUS ===
  radius: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '20px',
    xxl: '24px',
    xxxl: '32px',
    full: '9999px',
  },

  // === SHADOWS ===
  shadows: {
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 2px 8px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 16px 0 rgba(0, 0, 0, 0.08)',
    lg: '0 8px 24px 0 rgba(0, 0, 0, 0.10)',
    xl: '0 12px 32px 0 rgba(0, 0, 0, 0.12)',
    xxl: '0 16px 48px 0 rgba(0, 0, 0, 0.15)',
    orange: '0 8px 24px 0 rgba(255, 74, 35, 0.25)',
    purple: '0 8px 24px 0 rgba(123, 97, 255, 0.25)',
    green: '0 8px 24px 0 rgba(29, 191, 115, 0.25)',
    glass: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
  },

  // === ANIMATION ===
  animation: {
    duration: {
      instant: '0.1s',
      fast: '0.2s',
      normal: '0.3s',
      slow: '0.5s',
      slower: '0.8s',
      ring: '1.5s',
    },
    easing: {
      standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
      decelerate: 'cubic-bezier(0, 0, 0.2, 1)',
      accelerate: 'cubic-bezier(0.4, 0, 1, 1)',
      sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
      spring: {
        type: 'spring' as const,
        damping: 20,
        stiffness: 300,
      },
      // Dramatic notification bounce
      notificationBounce: {
        type: 'spring' as const,
        damping: 15,
        stiffness: 400,
        mass: 0.8,
      },
    },
  },
} as const;
