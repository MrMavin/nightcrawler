/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js,ts}",
    "./dist/**/*.{html,js}"
  ],
  theme: {
    extend: {
      colors: {
        'linkedin': {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#0073b1',
          600: '#005a85',
          700: '#1e40af',
        },
        'success': '#28a745',
        'danger': '#dc3545',
        'warning': '#ffc107'
      },
      fontFamily: {
        'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif']
      }
    },
  },
  plugins: [],
}