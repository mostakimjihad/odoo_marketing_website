/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/**/*.py',
    './portfolio/**/*.py',
    './blog/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds — soft dark with a hint of warmth
        base:    '#0B1020',
        surface: '#121832',
        card:    '#161D3D',
        elevated:'#1B2347',
        line:    'rgba(255, 255, 255, 0.06)',
        line2:   'rgba(255, 255, 255, 0.12)',

        // Text — cool off-white, business-readable
        ink:     '#F5F7FA',
        ink2:    '#CBD5E1',
        ink3:    '#94A3B8',
        ink4:    '#64748B',

        // Primary brand — indigo (business SaaS feel)
        indigo:  { 300: '#A5B4FC', 400: '#818CF8', 500: '#6366F1', 600: '#4F46E5', 700: '#4338CA' },

        // Accents — teal for success / progress, emerald for live
        teal:    { 300: '#67E8F9', 400: '#22D3EE', 500: '#06B6D4' },
        emerald: { 400: '#34D399', 500: '#10B981' },

        success: '#10B981',
        danger:  '#EF4444',
        warning: '#F59E0B',

        // ERP app screen colors (browser-frame mockups)
        brand:       '#6366F1',
        brandLine:   '#C7D2FE',
        brandSoft:   '#EEF2FF',
        tealApp:     '#22D3EE',
        tealLine:    '#A5F3FC',
        tealSoft:    '#ECFEFF',
        canvas:      '#F8FAFC',
      },
      fontFamily: {
        display: ['Inter', 'system-ui', 'sans-serif'],
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        tightest: '-0.03em',
        ultratight: '-0.02em',
      },
      borderRadius: {
        none: '0',
        sm: '4px',
        DEFAULT: '6px',
        md: '6px',
        lg: '10px',
        xl: '12px',
        '2xl': '16px',
        '3xl': '20px',
      },
    },
  },
  corePlugins: {
    backdropBlur: false, backdropBrightness: false, backdropContrast: false,
    backdropGrayscale: false, backdropHueRotate: false, backdropInvert: false,
    backdropOpacity: false, backdropSaturate: false, backdropSepia: false,
    blur: false, brightness: false, contrast: false, grayscale: false,
    hueRotate: false, invert: false, saturate: false, sepia: false,
    dropShadow: false,
  },
  plugins: [],
}