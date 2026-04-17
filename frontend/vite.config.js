import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  root: "./",

  plugins: [tailwindcss()],

  server: {
    port: 5173,
    cors: true,
    origin: "http://localhost:5173",
  },

  build: {
    outDir: "../app/static/dist",
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: "./src/main.js",
    },
  },
});
