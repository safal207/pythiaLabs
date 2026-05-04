import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  build: {
    target: "es2020",
    cssMinify: true,
    minify: "esbuild",
    sourcemap: false,
    assetsInlineLimit: 4096,
    reportCompressedSize: false,
  },
});
