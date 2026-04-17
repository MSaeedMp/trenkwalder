import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { TanStackRouterVite } from "@tanstack/router-plugin/vite"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [
    TanStackRouterVite({ target: "react", autoCodeSplitting: true }),
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_API_URL || "http://localhost:8000",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("proxyRes", (proxyRes) => {
            // Disable buffering so streaming responses arrive chunk by chunk
            proxyRes.headers["cache-control"] = "no-cache"
            proxyRes.headers["x-accel-buffering"] = "no"
          })
        },
      },
    },
  },
})
