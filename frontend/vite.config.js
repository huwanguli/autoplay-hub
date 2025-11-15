import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      // 代理所有以 /api 开头的请求
      '/api': {
        target: 'http://127.0.0.1:8000', // 你的Django后端地址
        changeOrigin: true, // 必须设置为 true
      },
      // 代理所有以 /media 开头的请求 (用于图片)
      '/media': {
        target: 'http://127.0.0.1:8000', // 你的Django后端地址
        changeOrigin: true, // 必须设置为 true
      },
    },
  },
})
