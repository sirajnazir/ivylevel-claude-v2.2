# Ivylevel Design System Specification

**Extracted from:** `original-unified-frontend`
**Date:** December 15, 2025
**Purpose:** Complete UI/UX design specifications for IvyQuest v3.0 enhancement

---

## 1. Brand Identity

### Brand Name
- **Primary:** Ivylevel (stylized as "ivylevel")
- **Product Names:** Ivylevel Elite, IvyQuest
- **Taglines:** "Ivy+ Ready Score", "T20 Level"

### Logo System

#### Full Logo (92x27px)
SVG with ivy leaf + sparkle icon in coral (#FE4A22) + "ivylevel" text in burgundy (#641432)

```svg
<svg width="92" height="27" viewBox="0 0 92 27" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Ivy Leaf Icon -->
  <path d="M9.34866 11.2647V15.0609C9.75237 11.7555 12.5671 9.19429 15.9792 9.19429V16.771C15.9792 20.4644 12.9866 23.457 9.29325 23.457V21.2997C4.42835 21.2681 0.493347 17.3173 0.493347 12.4482V2.4093C5.382 2.4093 9.34866 6.37184 9.34866 11.2647Z" fill="#FE4A22"/>
  <!-- Sparkle -->
  <path d="M8.34308 3.04325C9.37714 2.4749 10.2275 1.62228 10.7924 0.586304C11.3598 1.62053 12.2135 2.47106 13.2492 3.03571C12.2143 3.60315 11.364 4.45602 10.7999 5.49266C10.232 4.45868 9.3788 3.60753 8.34308 3.04325Z" fill="#FE4A22"/>
  <!-- "ivylevel" text paths in #641432 -->
</svg>
```

#### Icon Only (16x24px)
Small ivy leaf + sparkle for favicons and compact spaces.

---

## 2. Color Palette

### Primary Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--ivy-primary` | `#FF4A23` | rgb(255, 74, 35) | Primary buttons, CTAs, highlights |
| `--ivy-primary-light` | `#ff6b4a` | rgb(255, 107, 74) | Hover states, gradients |
| `--ivy-primary-dark` | `#e6391a` | rgb(230, 57, 26) | Active/pressed states |

### Secondary Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--ivy-secondary` | `#641432` | rgb(100, 20, 50) | Headers, text, secondary buttons |
| `--ivy-secondary-light` | `#8a1d45` | rgb(138, 29, 69) | Hover states |
| `--ivy-secondary-dark` | `#4a0f24` | rgb(74, 15, 36) | Active states |

### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--ivy-success` | `#16a34a` | Success states, positive changes |
| `--ivy-success-light` | `#22c55e` | Success badges |
| `--ivy-warning` | `#d97706` | Warnings, attention |
| `--ivy-error` | `#dc2626` | Errors, destructive actions |
| `--ivy-info` | `#3b82f6` | Information, links |

### Gray Scale

| Token | Hex | Usage |
|-------|-----|-------|
| `--ivy-gray-50` | `#f9fafb` | Background, cards |
| `--ivy-gray-100` | `#f3f4f6` | Tertiary backgrounds |
| `--ivy-gray-200` | `#e5e7eb` | Borders, dividers |
| `--ivy-gray-300` | `#d1d5db` | Input borders |
| `--ivy-gray-400` | `#9ca3af` | Placeholder text |
| `--ivy-gray-500` | `#6b7280` | Secondary text |
| `--ivy-gray-600` | `#4b5563` | Body text |
| `--ivy-gray-700` | `#374151` | Headings |
| `--ivy-gray-800` | `#1f2937` | Dark backgrounds |
| `--ivy-gray-900` | `#111827` | Primary text |

### Accent Background Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Light Coral | `#FFE5DF` | Subtle primary backgrounds |
| Light Burgundy | `#F5E8E5` | Subtle secondary backgrounds |
| Success Light | `#dcfce7` | Success backgrounds |
| Warning Light | `#fef3c7` | Warning backgrounds |

### Gradients

```css
/* Background Gradient */
background: linear-gradient(135deg, #FFE5DF, #F5E8E5);

/* Primary Button Gradient */
background: linear-gradient(135deg, #FE4A22, #FF6B47);

/* Achievement Gold Gradient */
background: linear-gradient(135deg, #FFEEAA 4%, #F4D144 21%, #B5971E 67%, #D4B53B 93%);
```

---

## 3. Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;

/* Display font for special headings */
font-family: 'Inter', sans-serif;
```

### Font Sizes

| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--ivy-font-size-xs` | 0.75rem (12px) | 1rem | Small labels, badges |
| `--ivy-font-size-sm` | 0.875rem (14px) | 1.25rem | Body small, captions |
| `--ivy-font-size-base` | 1rem (16px) | 1.5rem | Body text |
| `--ivy-font-size-lg` | 1.125rem (18px) | 1.75rem | Lead text |
| `--ivy-font-size-xl` | 1.25rem (20px) | 1.75rem | Section headings |
| `--ivy-font-size-2xl` | 1.5rem (24px) | 2rem | Card titles |
| `--ivy-font-size-3xl` | 1.875rem (30px) | 2.25rem | Page headings |
| `--ivy-font-size-4xl` | 2.25rem (36px) | 2.5rem | Hero headings |

### Font Weights

| Token | Weight | Usage |
|-------|--------|-------|
| `--ivy-font-light` | 300 | Subtle text |
| `--ivy-font-normal` | 400 | Body text |
| `--ivy-font-medium` | 500 | Labels, navigation |
| `--ivy-font-semibold` | 600 | Buttons, subheadings |
| `--ivy-font-bold` | 700 | Headings, emphasis |

---

## 4. Spacing System

| Token | Size | Pixels |
|-------|------|--------|
| `--ivy-space-xs` | 0.25rem | 4px |
| `--ivy-space-sm` | 0.5rem | 8px |
| `--ivy-space-md` | 1rem | 16px |
| `--ivy-space-lg` | 1.5rem | 24px |
| `--ivy-space-xl` | 2rem | 32px |
| `--ivy-space-2xl` | 3rem | 48px |
| `--ivy-space-3xl` | 4rem | 64px |

---

## 5. Border Radius

| Token | Size | Usage |
|-------|------|-------|
| `--ivy-radius-sm` | 0.25rem (4px) | Badges, small elements |
| `--ivy-radius-md` | 0.375rem (6px) | Buttons, inputs |
| `--ivy-radius-lg` | 0.5rem (8px) | Cards, panels |
| `--ivy-radius-xl` | 0.75rem (12px) | Feature cards |
| `--ivy-radius-2xl` | 1rem (16px) | Modal dialogs |
| `--ivy-radius-full` | 9999px | Pills, avatars |

---

## 6. Shadow System

```css
/* Subtle shadow for cards */
--ivy-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);

/* Medium shadow for elevated elements */
--ivy-shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);

/* Large shadow for modals, dropdowns */
--ivy-shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);

/* Extra large shadow for hero cards */
--ivy-shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

/* Brand-colored shadows */
box-shadow: 0 4px 12px rgba(254, 74, 34, 0.3); /* Primary button */
box-shadow: 0 20px 40px rgba(100, 20, 50, 0.1); /* Card with burgundy tint */
```

---

## 7. Glassmorphism Effects

### Glass Card
```css
.ivy-glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 250ms ease-in-out;
}

.ivy-glass-card:hover {
  background: rgba(255, 255, 255, 0.85);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
```

### Brand-Colored Glass
```css
/* Primary glass effect */
.ivy-primary-glass {
  background: linear-gradient(135deg, rgba(255, 74, 35, 0.1) 0%, rgba(255, 74, 35, 0.05) 100%);
  border: 1px solid rgba(255, 74, 35, 0.2);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(255, 74, 35, 0.1);
}

/* Secondary glass effect */
.ivy-secondary-glass {
  background: linear-gradient(135deg, rgba(100, 20, 50, 0.1) 0%, rgba(100, 20, 50, 0.05) 100%);
  border: 1px solid rgba(100, 20, 50, 0.2);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(100, 20, 50, 0.1);
}
```

---

## 8. Component Patterns

### Primary Button
```css
.ivy-button-primary {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, #FE4A22, #FF6B47);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(254, 74, 34, 0.3);
}

.ivy-button-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(254, 74, 34, 0.4);
}
```

### Secondary Button
```css
.ivy-button-secondary {
  padding: 12px 24px;
  background-color: #641432;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.ivy-button-secondary:hover {
  background-color: #4A0F26;
}
```

### Tab Buttons
```css
.ivy-tab {
  padding: 12px 24px;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.ivy-tab.active {
  background-color: #FF4A23;
  color: white;
}
```

### Input Fields
```css
.ivy-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
}

.ivy-input:focus {
  border-color: #FE4A22;
}

/* Select styling */
.ivy-select {
  padding: 8px 16px;
  border: 1px solid #FFE5DF;
  border-radius: 6px;
  font-size: 14px;
}

.ivy-select:focus {
  border-color: #FF4A23;
}
```

### Cards
```css
.ivy-card {
  background: white;
  border-radius: 16px;
  padding: 48px;
  box-shadow: 0 20px 40px rgba(100, 20, 50, 0.1);
}

.ivy-feature-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ivy-feature-icon {
  width: 48px;
  height: 48px;
  background: rgba(254, 74, 34, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Score Display (IvyScoreCard style)
```css
.ivy-score-card {
  background-color: #ff504f;
  border: 5.59px solid #ffdcdb;
  border-radius: 22.37px;
  height: 200px;
  position: relative;
}

.ivy-score-number {
  color: #ffffff;
  font-family: "Inter", sans-serif;
  font-size: 69.9px;
  font-weight: 400;
  letter-spacing: -6.29px;
}

.ivy-achievement-badge {
  backdrop-filter: blur(30.76px);
  background-color: #ffffff;
  border-radius: 13.98px;
}
```

---

## 9. Animation System

### Transitions
```css
--ivy-transition-fast: 150ms ease-in-out;
--ivy-transition-normal: 250ms ease-in-out;
--ivy-transition-slow: 350ms ease-in-out;
```

### Keyframe Animations
```css
@keyframes ivyFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes ivySlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes ivySpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### Hover Effects
```css
/* Card lift effect */
.ivy-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--ivy-shadow-lg);
}

/* Button hover */
.ivy-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(254, 74, 34, 0.4);
}
```

---

## 10. Layout Patterns

### Container
```css
.ivy-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
```

### Two-Column Login Layout
```css
.ivy-login-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFE5DF, #F5E8E5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.ivy-login-container {
  max-width: 960px;
  width: 100%;
  display: flex;
  gap: 48px;
  align-items: center;
}

.ivy-login-form {
  flex: 1;
  background: white;
  border-radius: 16px;
  padding: 48px;
  box-shadow: 0 20px 40px rgba(100, 20, 50, 0.1);
}

.ivy-login-marketing {
  flex: 1;
  padding: 48px;
  color: #641432;
}
```

### Grid System
```css
.ivy-grid {
  display: grid;
  gap: 24px;
}

.ivy-grid-2 { grid-template-columns: repeat(2, 1fr); }
.ivy-grid-3 { grid-template-columns: repeat(3, 1fr); }
.ivy-grid-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 768px) {
  .ivy-grid-2, .ivy-grid-3, .ivy-grid-4 {
    grid-template-columns: 1fr;
  }
}
```

---

## 11. Responsive Breakpoints

| Breakpoint | Size | Usage |
|------------|------|-------|
| Mobile | < 480px | Phone portrait |
| Small | < 768px | Phone landscape, small tablets |
| Medium | < 1024px | Tablets |
| Large | < 1200px | Small desktops |
| XLarge | > 1200px | Desktops |

---

## 12. Icon System

### Icon Sizing
- Small: 16-20px
- Medium: 24px (default)
- Large: 42-48px (feature icons)

### Icon Style
- Stroke-based icons (Lucide React compatible)
- Stroke width: 2px
- Fill icons for brand elements

---

## 13. Usage Examples

### Hero Section Pattern
```jsx
<div style={{
  background: 'linear-gradient(135deg, #FFE5DF, #F5E8E5)',
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center'
}}>
  <div style={{
    textAlign: 'center',
    maxWidth: '800px'
  }}>
    <IvylevelLogo style={{ width: '92px', marginBottom: '24px' }} />
    <h1 style={{
      fontSize: '2.5rem',
      fontWeight: 'bold',
      color: '#641432',
      marginBottom: '16px'
    }}>
      Your Journey to Ivy+ Starts Here
    </h1>
    <button style={{
      background: 'linear-gradient(135deg, #FE4A22, #FF6B47)',
      color: 'white',
      padding: '14px 32px',
      borderRadius: '8px',
      border: 'none',
      fontSize: '16px',
      fontWeight: '600',
      boxShadow: '0 4px 12px rgba(254, 74, 34, 0.3)'
    }}>
      Begin Your Quest
    </button>
  </div>
</div>
```

---

## 14. Concentric Rings Animation System

The Ivylevel platform features a distinctive concentric rings visualization for displaying pillar scores. This is the core visual component for the student profile score display.

### Ring Configuration

| Ring Name | SVG Size | Stroke Width | Color | Purpose |
|-----------|----------|--------------|-------|---------|
| Aptitude | 895 | 69.8544 | `#FFBB6D` | Academic/intellectual skills |
| Passion | 1090 | 69.8544 | `#FF6E6D` | Interest/enthusiasm areas |
| Service | 1287 | 69.8544 | `#55AAAA` | Community/service involvement |
| Identity | 1482 | 69.8544 | `#979797` | Personal story/background |
| Ivy+ Score | 1750 | 100 | Gradient | Overall composite score |

### Ring Colors

```typescript
const ringColors = {
  aptitude: '#FFBB6D',   // Warm gold/amber
  passion: '#FF6E6D',    // Coral pink
  service: '#55AAAA',    // Teal
  identity: '#979797',   // Neutral gray
  background: '#E5E7EB', // Unfilled ring background
};
```

### Ivy+ Score Gradient Definition

The outer Ivy+ Score ring uses a special gradient for visual emphasis:

```jsx
<defs>
  <linearGradient
    id="paint0_linear_12076_3953"
    x1="-2642.5"
    y1="348.5"
    x2="2036"
    y2="73.5"
    gradientUnits="userSpaceOnUse"
  >
    <stop offset="0.597383" stopColor="#FF4A23" />
    <stop offset="0.633939" stopColor="#FF7224" stopOpacity="0.7" />
    <stop offset="0.665651" stopColor="#FF7224" stopOpacity="0.4" />
    <stop offset="0.721742" stopColor="white" stopOpacity="0.85" />
    <stop offset="0.766116" stopColor="white" />
    <stop offset="0.837615" stopColor="white" />
  </linearGradient>
</defs>
```

### Animation Technique

Uses SVG `strokeDashoffset` animation for smooth circular progress:

```tsx
// Animation style applied to each ring path
style={{
  strokeDasharray: '1',
  strokeDashoffset: 1 - pathLength, // pathLength = percentage/100
  transition: 'stroke-dashoffset 2s cubic-bezier(0.4, 0, 0.2, 1)',
}}

// pathLength calculation: score percentage as decimal (0-1)
// Example: 75% score = pathLength of 0.75
// strokeDashoffset = 1 - 0.75 = 0.25 (shows 75% filled)
```

### Container Structure

```tsx
// Main container dimensions
const containerStyle = {
  position: 'relative',
  width: '500px',
  height: '500px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

// Central profile image
const profileImageStyle = {
  position: 'absolute',
  width: '120px',
  height: '120px',
  borderRadius: '50%',
  objectFit: 'cover',
  zIndex: 10,
};
```

### Ring Path Structure (SVG)

Each ring consists of two paths:
1. **Background path** - Full circle in `#E5E7EB` (unfilled state)
2. **Progress path** - Partial circle showing score percentage

```tsx
// Background ring (always full)
<path
  d={pathData}
  fill="none"
  stroke="#E5E7EB"
  strokeWidth={ring.strokeWidth}
/>

// Animated progress ring
<path
  d={pathData}
  fill="none"
  stroke={ring.color}
  strokeWidth={ring.strokeWidth}
  pathLength="1"
  style={{
    strokeDasharray: '1',
    strokeDashoffset: 1 - (score / 100),
    transition: 'stroke-dashoffset 2s cubic-bezier(0.4, 0, 0.2, 1)',
  }}
/>
```

### Score Indicators (T20 / IVY+)

Position markers on the outer ring to indicate thresholds:

```tsx
// T20 indicator (positioned at score threshold on outer ring)
const T20Indicator = {
  position: 'absolute',
  background: 'white',
  borderRadius: '4px',
  padding: '4px 8px',
  fontSize: '12px',
  fontWeight: 'bold',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
};

// IVY+ indicator (similar, positioned at higher threshold)
// Positioned using trigonometric calculations based on score percentage
```

### Position Calculation for Indicators

```typescript
// Calculate position on ring circle for score indicator
const calculatePosition = (percentage: number, ringRadius: number) => {
  // Convert percentage to radians (starting from top, clockwise)
  const angle = (percentage / 100) * 2 * Math.PI - Math.PI / 2;

  return {
    x: Math.cos(angle) * ringRadius,
    y: Math.sin(angle) * ringRadius,
  };
};
```

### Complete Ring Component Structure

```tsx
const CircularProgress = ({ scores, profileImage }) => {
  const rings = [
    { name: 'Aptitude', size: 895, color: "#FFBB6D", strokeWidth: 69.8544 },
    { name: 'Passion', size: 1090, color: "#FF6E6D", strokeWidth: 69.8544 },
    { name: 'Service', size: 1287, color: "#55AAAA", strokeWidth: 69.8544 },
    { name: 'Identity', size: 1482, color: "#979797", strokeWidth: 69.8544 },
    { name: 'Ivy+ Score', size: 1750, strokeWidth: 100, useGradient: true },
  ];

  return (
    <div className="rings-container">
      <svg viewBox="0 0 500 500">
        <defs>
          {/* Ivy+ gradient definition */}
        </defs>

        {rings.map((ring, index) => (
          <g key={ring.name}>
            {/* Background ring */}
            <circle
              cx="250"
              cy="250"
              r={ring.size / 4}
              fill="none"
              stroke="#E5E7EB"
              strokeWidth={ring.strokeWidth / 4}
            />

            {/* Animated progress ring */}
            <circle
              cx="250"
              cy="250"
              r={ring.size / 4}
              fill="none"
              stroke={ring.useGradient ? "url(#paint0_linear_12076_3953)" : ring.color}
              strokeWidth={ring.strokeWidth / 4}
              pathLength="1"
              style={{
                strokeDasharray: '1',
                strokeDashoffset: 1 - (scores[ring.name] / 100),
                transition: 'stroke-dashoffset 2s cubic-bezier(0.4, 0, 0.2, 1)',
                transformOrigin: 'center',
                transform: 'rotate(-90deg)',
              }}
            />
          </g>
        ))}
      </svg>

      {/* Center profile image */}
      <img src={profileImage} className="center-profile" alt="Student" />

      {/* Score indicators */}
      <div className="t20-indicator">T20</div>
      <div className="ivy-indicator">IVY+</div>
    </div>
  );
};
```

### Animation Timing

| Property | Value | Description |
|----------|-------|-------------|
| Duration | 2s | Time for ring to animate from 0 to final value |
| Easing | `cubic-bezier(0.4, 0, 0.2, 1)` | Smooth deceleration curve |
| Delay | Staggered by ring index | Outer rings animate slightly after inner |

### CSS Keyframes Alternative

For CSS-only animation approach:

```css
@keyframes ringProgress {
  from {
    stroke-dashoffset: 1;
  }
  to {
    stroke-dashoffset: var(--target-offset);
  }
}

.ring-progress {
  animation: ringProgress 2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  --target-offset: 0.25; /* Set via inline style based on score */
}
```

---

*This design system specification was extracted from the original-unified-frontend codebase to ensure brand consistency across IvyQuest v3.0.*
