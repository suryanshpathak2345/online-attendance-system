/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f5ff',
          100: '#e0ebff',
          200: '#c7d9fe',
          300: '#a4c0fd',
          400: '#7c9efb',
          500: '#537bf7',
          600: '#3559ed',
          700: '#2743db',
          800: '#2337b1',
          900: '#22328c',
        },
        status: {
          present: '#10b981',
          absent: '#ef4444',
          halfday: '#f59e0b',
          holiday: '#8b5cf6',
          cancelled: '#6b7280',
        }
      }
    },
  },
  plugins: [],
}
