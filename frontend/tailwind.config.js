/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        soc: {
          bg: '#0b1020',
          panel: '#141b2d',
          panelSoft: '#1a2338',
          border: '#25304a',
          text: '#e6edf8',
          muted: '#91a0bf',
          critical: '#ff3b3b',
          high: '#ff8c00',
          medium: '#ffd60a',
          low: '#2ecc71',
          accent: '#3b82f6',
        },
      },
      boxShadow: {
        panel: '0 12px 28px rgba(0, 0, 0, 0.35)',
      },
      animation: {
        in: 'fadeIn 220ms ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0, transform: 'translateY(6px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
