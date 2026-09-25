/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class", // disabled / not using dark mode
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        surface: "#FFFFFF",
        border: "#E2E8F0",
        miroNavy: "#050038",
        miroBlue: {
          DEFAULT: "#4262ff",
          hover: "#3151eb",
          light: "#eef2ff",
        },
        miroYellow: {
          DEFAULT: "#ffd02f",
          hover: "#f5c518",
          light: "#fff9e6",
        },
        miroGray: {
          50: "#fafbfc",
          100: "#f4f5f7",
          200: "#e6e8ec",
          300: "#d1d5db",
          400: "#9ca3af",
          500: "#5e6573",
          600: "#4b5563",
          700: "#374151",
          800: "#1f2937",
          900: "#050038",
        },
        primary: {
          50: "#EEF2FF",
          100: "#E0E7FF",
          500: "#4262ff",
          600: "#3151eb",
          700: "#243ec4",
        },
      },
    },
  },
  plugins: [],
};

