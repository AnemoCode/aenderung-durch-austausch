/**
 * Overlytics — Tailwind CSS configuration
 *
 * Loaded synchronously before the Tailwind Play CDN script so every custom
 * utility is available on first render.
 *
 * Design tokens
 * ─────────────
 *  forest  #344945   Primary dark teal — text, buttons, sidebar, UI chrome
 *  cream   #F7F5F1   Page background — warm off-white
 *  beige   #E0DCD1   Borders and dividers — warm tan
 *  sage    #D5E3E8   Accent blue-grey — icon highlights, info banners
 *  wheat   #E4E3BC   Accent yellow-green — badges, warning banners
 *
 * All five colors integrate with Tailwind's opacity-modifier syntax
 * (e.g. `text-forest/60`, `bg-beige/10`) out of the box.
 *
 * NOTE: Tailwind's built-in palette (slate, rose, emerald, …) is preserved
 * via `extend` so error/success colours remain available.
 */

/* global tailwind */
tailwind.config = {
  theme: {
    extend: {

      // ── Brand colours ──────────────────────────────────────────────────────
      colors: {

        forest: {
          DEFAULT: '#344945',
          50:  '#eef4f2',
          100: '#d4e4e0',
          200: '#aacac3',
          300: '#76aba1',
          400: '#4e8b82',
          500: '#344945',   // ← base
          600: '#2b3c38',
          700: '#202d2a',
          800: '#151e1c',
          900: '#0b100f',
          950: '#050908',
        },

        cream: {
          DEFAULT: '#F7F5F1',
        },

        beige: {
          DEFAULT: '#E0DCD1',
          dark:    '#cac4b7',
        },

        sage: {
          DEFAULT: '#D5E3E8',
          dark:    '#b3cdd5',
        },

        wheat: {
          DEFAULT: '#E4E3BC',
          dark:    '#cecd9a',
        },

      },

      // ── Typography ─────────────────────────────────────────────────────────
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
        mono: [
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'Monaco',
          'Consolas',
          '"Liberation Mono"',
          '"Courier New"',
          'monospace',
        ],
      },

    },
  },

  plugins: [],
};
