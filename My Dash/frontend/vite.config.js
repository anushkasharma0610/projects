import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Keep API calls and session cookies same-origin while developing with Vite.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
});
