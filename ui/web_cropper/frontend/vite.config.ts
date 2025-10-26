import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 统一 dev 端口 5173，并将构建产物输出到 dist/（与后端探测一致）
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      external: ['streamlit-component-lib'],
    },
  },
})
