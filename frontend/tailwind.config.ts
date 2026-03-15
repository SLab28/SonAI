import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{ts,tsx}', './index.html'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        sonai: {
          source: '#6b7280',     // grey
          transform: '#3b82f6',  // blue
          measure: '#22c55e',    // green
          infer: '#f59e0b',      // amber
          compose: '#a855f7',    // purple
          render: '#ef4444',     // red
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
