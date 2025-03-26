import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    hmr: {
      overlay: true, // Shows error overlay
      clientPort: 5173 // Port for HMR client
    },
    watch: {
      usePolling: true, // Useful for some systems
      interval: 100 // Polling interval
    }
  }
})
