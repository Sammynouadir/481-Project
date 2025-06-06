import { defineConfig } from "vite";

export default defineConfig({
  root: "src",
  base: "./",
  publicDir: "../public",
  build: {
    outDir: "../dist-renderer",
    emptyOutDir: true
  },
  server: {
    fs: {
      allow: ['..'],
    }
  }
});
