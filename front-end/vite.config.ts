import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({mode}) => {
  const env = loadEnv(mode, '.', '')
  const port = Number(env.VITE_DEV_SERVER_PORT || 5178)
  const host = env.VITE_DEV_SERVER_HOST || '127.0.0.1'
  const allowedHosts = (env.VITE_DEV_ALLOWED_HOSTS || 'app.local.cheburek-shop.com,localhost,127.0.0.1')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean)

  return {
    plugins: [react()],
    server: {
      watch: {
        usePolling: true,
      },
      host,
      strictPort: true,
      port,
      allowedHosts,
    },
    preview: {
      host,
      port,
      strictPort: true,
    },
  }
})
