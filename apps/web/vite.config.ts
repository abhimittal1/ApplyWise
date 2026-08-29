import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({ mode }) => {
  const rootDir = path.resolve(__dirname, '../..');
  const env = loadEnv(mode, rootDir, '');
  const apiUrl = env.VITE_API_URL || process.env.VITE_API_URL || '';

  return {
    envDir: rootDir,
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      watch: {
        usePolling: true,
      },
      ...(apiUrl
        ? {
            proxy: {
              '/api': {
                target: apiUrl,
                changeOrigin: true,
                secure: false,
              },
            },
          }
        : {}),
    },
  };
});
