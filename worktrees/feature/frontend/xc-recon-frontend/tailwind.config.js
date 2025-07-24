/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 基于项目现有配色系统
        primary: '#409EFF',
        secondary: '#2c3e50',
        success: '#00A870',
        warning: '#E6A23C',
        danger: '#F56C6C',
        info: '#909399',
        light: '#f5f7fa',
      }
    },
  },
  plugins: [],
}