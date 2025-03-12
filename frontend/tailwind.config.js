/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './public/index.html'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f0ff',
          100: '#cce0ff',
          200: '#99c2ff',
          300: '#66a3ff',
          400: '#3385ff',
          500: '#0066cc', // DEFAULT
          600: '#0052a3',
          700: '#003d7a',
          800: '#002952',
          900: '#001429',
        },
        secondary: {
          50: '#fff8e6',
          100: '#fff1cc',
          200: '#ffe499',
          300: '#ffd666',
          400: '#ffc933',
          500: '#ff9900', // DEFAULT
          600: '#cc7a00',
          700: '#995c00',
          800: '#663d00',
          900: '#331f00',
        },
        bitcoin: {
          50: '#fff7e6',
          100: '#ffefd0',
          200: '#ffe0a1',
          300: '#ffd072',
          400: '#ffc143',
          500: '#f7931a', // DEFAULT
          600: '#e57600',
          700: '#b25c00',
          800: '#7f4100',
          900: '#4c2700',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
    },
  },
  darkMode: 'class', // Enable dark mode with class strategy
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
