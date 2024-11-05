import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',   // Inclui todos os arquivos relevantes para analisar classe CSS
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',  // Utiliza variáveis CSS para cores
        foreground: 'var(--foreground)',
      },
    },
  },
  plugins: [],
};

export default config;
