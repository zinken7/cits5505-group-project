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
      input: {
        main:          "./src/main.js",
        topbar_search: "./src/pages/topbar_search.js",
        chat_modal:    "./src/pages/chat_modal.js",
        dashboard:   "./src/pages/dashboard.js",
        explore:     "./src/pages/explore.js",
        profile:     "./src/pages/profile.js",
        detail:      "./src/pages/detail.js",
        categories:  "./src/pages/categories.js",
        landing:     "./src/pages/landing.js",
        chat:        "./src/pages/chat.js",
        search:      "./src/pages/search.js",
      },
    },
  },
});
