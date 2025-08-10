/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4dabf7',
          DEFAULT: '#339af0',
          dark: '#1c7ed6',
        },
        secondary: {
          light: '#ced4da',
          DEFAULT: '#adb5bd',
          dark: '#868e96',
        },
        success: '#2b8a3e',
        warning: '#e8590c',
        danger: '#e03131',
        info: '#1864ab',
        background: {
          light: '#f8f9fa',
          dark: '#212529',
        },
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
