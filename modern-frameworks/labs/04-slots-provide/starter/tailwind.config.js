/** @type {import('tailwindcss').Config} */

// Кольори та шрифти перенесено з theme/tokens.yaml спільної теми курсів.
// Акцент курсу «Сучасні каркаси web-додатків» — роль server (course.yaml),
// тому accent дорівнює бірюзовому. Інших джерел кольору в проєкті немає:
// компоненти беруть значення лише звідси.
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js}',
  ],
  theme: {
    extend: {
      colors: {
        ink: '#14161B',
        deep: '#1E2129',
        surface: '#F1F3F5',
        edge: '#DCE0E5',
        muted: '#6B7280',
        paper: '#FFFFFF',
        accent: '#2EC4B6',
        client: '#FF6B35',
      },
      fontFamily: {
        display: ['Unbounded', 'Cambria', 'serif'],
        body: ['"IBM Plex Sans"', 'Calibri', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"Courier New"', 'monospace'],
      },
    },
  },
  plugins: [],
}
