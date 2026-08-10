import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/status": "http://127.0.0.1:8765",
      "/wave": "http://127.0.0.1:8765",
      "/gps": "http://127.0.0.1:8765",
      "/battery": "http://127.0.0.1:8765",
      "/solar": "http://127.0.0.1:8765",
      "/ai": "http://127.0.0.1:8765",
      "/api": "http://127.0.0.1:8765",
      "/models": "http://127.0.0.1:8765",
      "/logs": "http://127.0.0.1:8765"
    }
  }
});
