import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import monacoEditorPlugin from 'vite-plugin-monaco-editor';
import { resolve } from 'path';

const frontendPort = Number(process.env.FRONTEND_PORT || process.env.PORT || 3000);

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    (monacoEditorPlugin as any).default({})
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  optimizeDeps: {
    exclude: ['lucide-vue-next'],
  },
  server: {
    host: true,
    port: frontendPort,
    ...(process.env.BACKEND_URL && {
      proxy: {
        '/api': {
          target: process.env.BACKEND_URL,
          changeOrigin: true,
          ws: true,
        },
      },
    }),
  },
  preview: {
    host: true,
    port: frontendPort,
  },
});
