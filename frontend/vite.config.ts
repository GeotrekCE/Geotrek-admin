import path from "path"
import { serwist } from "@serwist/vite"
import { paraglideVitePlugin } from "@inlang/paraglide-js"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { tanstackRouter } from "@tanstack/router-plugin/vite"
import { defineConfig, loadEnv } from "vite"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "")
  const __HOST_URL__ = JSON.stringify(env.HOST_URL)
  const basePath =
    !env.APP_ENV || env.APP_ENV.startsWith("dev") ? "/" : "/offline/"
  return {
    define: {
      __HOST_URL__,
    },
    base: basePath,
    plugins: [
      paraglideVitePlugin({
        project: "./project.inlang",
        outdir: "./src/paraglide",
        outputStructure: "message-modules",
        strategy: ["cookie", "url", "preferredLanguage", "baseLocale"],
        urlPatterns: [
          {
            pattern: basePath,
            localized: [
              ["fr", `${basePath}fr`],
              ["en", `${basePath}en`],
            ],
          },
          {
            pattern: `${basePath}:path(.*)?`,
            localized: [
              ["fr", `${basePath}fr/:path(.*)?`],
              ["en", `${basePath}en/:path(.*)?`],
            ],
          },
        ],
      }),
      tanstackRouter({
        target: "react",
        autoCodeSplitting: true,
      }),
      tailwindcss(),
      react(),
      serwist({
        base: basePath,
        swSrc: "src/lib/sw.ts",
        swDest: "sw.js",
        globDirectory: "dist",
        injectionPoint: "self.__SW_MANIFEST",
        rollupFormat: "iife",
      }),
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      proxy: {
        "/api": {
          target: env.HOST_URL || "http://localhost:8000",
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
