import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f1f5ff',
          100: '#e0e7ff',
          500: '#4f46e5',
          700: '#4338ca'
        }
      }
    }
  },
  plugins: []
}

export default config
