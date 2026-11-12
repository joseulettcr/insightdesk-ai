import { defineConfig } from "vite";

export default defineConfig({
  oxc: {
    jsx: { runtime: "automatic" },
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
