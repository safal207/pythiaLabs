import { defineConfig, type Plugin } from "vite";

/**
 * Inline all emitted CSS into <head> and drop the <link rel="stylesheet">.
 * For a single-page site under ~10 KB CSS this removes a render-blocking
 * roundtrip and gives the fastest possible First Contentful Paint.
 */
function inlineCss(): Plugin {
  return {
    name: "inline-css",
    apply: "build",
    enforce: "post",
    generateBundle(_options, bundle) {
      const htmlFiles = Object.values(bundle).filter(
        (f): f is import("rollup").OutputAsset =>
          f.type === "asset" && f.fileName.endsWith(".html"),
      );
      const cssAssets = Object.values(bundle).filter(
        (f): f is import("rollup").OutputAsset =>
          f.type === "asset" && f.fileName.endsWith(".css"),
      );
      if (htmlFiles.length === 0 || cssAssets.length === 0) return;

      const cssContent = cssAssets
        .map((a) => (typeof a.source === "string" ? a.source : a.source.toString()))
        .join("\n");

      for (const html of htmlFiles) {
        let source =
          typeof html.source === "string" ? html.source : html.source.toString();
        // Drop stylesheet <link>s emitted by Vite
        source = source.replace(
          /<link[^>]+rel=["']stylesheet["'][^>]*>\s*/g,
          "",
        );
        // Inject inline <style> just before </head>
        source = source.replace(
          /<\/head>/i,
          `<style>${cssContent}</style></head>`,
        );
        html.source = source;
      }

      // Remove the now-unused CSS asset files from the bundle
      for (const a of cssAssets) {
        delete bundle[a.fileName];
      }
    },
  };
}

function injectBuildYear(): Plugin {
  return {
    name: "inject-build-year",
    transformIndexHtml(html) {
      return html.replace(/%BUILD_YEAR%/g, String(new Date().getFullYear()));
    },
  };
}

export default defineConfig({
  base: "./",
  plugins: [injectBuildYear(), inlineCss()],
  build: {
    target: "es2020",
    cssMinify: "lightningcss",
    minify: "esbuild",
    sourcemap: false,
    assetsInlineLimit: 4096,
    reportCompressedSize: false,
    cssCodeSplit: false,
    modulePreload: { polyfill: false },
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
});
