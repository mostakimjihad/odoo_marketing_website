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
        // Deep space backgrounds (not pure black)
        base:    '#06061A',
        surface: '#0B0B26',
        card:    '#0F0F2E',
        elevated:'#15163A',
        line:    'rgba(255, 255, 255, 0.08)',
        line2:   'rgba(255, 255, 255, 0.14)',

        // Text — high contrast on dark
        ink:     '#F8FAFC',
        ink2:    '#CBD5E1',
        ink3:    '#94A3B8',
        ink4:    '#64748B',

        // Neon brand
        indigo:  { 300: '#A5B4FC', 400: '#818CF8', 500: '#6366F1', 600: '#4F46E5' },
        cyan:    { 300: '#67E8F9', 400: '#22D3EE', 500: '#06B6D4' },
        magenta: { 300: '#F9A8D4', 400: '#F472B6', 500: '#EC4899' },
        lime:    { 400: '#A3E635', 500: '#84CC16' },

        success: '#10B981',
        danger:  '#F87171',
        warning: '#F59E0B',

        // Legacy aliases (light theme) — used by browser-frame mockups so
        // they look like real ERP app screens rendered inside the dark frame.
        brand:       '#6366F1',
        brandLine:   '#C7D2FE',
        brandSoft:   '#EEF2FF',
        teal:        '#22D3EE',
        tealLine:    '#A5F3FC',
        tealSoft:    '#ECFEFF',
        canvas:      '#F8FAFC',
        paper:       '#FFFFFF',
        accent:      '#22D3EE',
        accentDeep:  '#06B6D4',
        accentSoft:  'rgba(34, 211, 238, 0.12)',
        accentLine:  'rgba(34, 211, 238, 0.35)',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        tightest: '-0.04em',
        ultratight: '-0.03em',
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