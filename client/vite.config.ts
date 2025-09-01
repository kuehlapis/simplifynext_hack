import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      '/download': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/download-file': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/artifacts': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/frontend-package': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/dashboard': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  plugins: [
    react()
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
