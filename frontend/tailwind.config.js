module.exports = {
  content: [
    '../templates/**/*.html',
    '../**/templates/**/*.html',
    './src/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: '#A8E6CF',
        'text-primary': '#243B4A',
        'text-secondary': '#5A6F7D',
        'primary-light': '#D5F5E8',
        'primary-dark': '#7DD9BB',
        secondary: '#FFD3B6',
        'secondary-light': '#FFE5D9',
        'secondary-dark': '#FFB894',
        accent: '#FFAAA5',
        'accent-light': '#FFCCC7',
        'accent-dark': '#FF8A84',
        neutral: '#FFFDF8',
        surface: '#FFFFFF',
        'surface-alt': '#FFFBF7',
        border: '#E8D5C8',
        'border-light': '#F0E8E0',
        'card': '#FFFFFF'
      },
      boxShadow: {
        'card': '0 6px 18px rgba(36,59,74,0.06)'
      }
    }
  },
  plugins: []
}
