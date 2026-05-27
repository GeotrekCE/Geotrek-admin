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
  return {
    define: {
      __HOST_URL__,
    },
    plugins: [
      paraglideVitePlugin({
        project: "./project.inlang",
        outdir: "./src/paraglide",
        outputStructure: "message-modules",
        strategy: ["cookie", "url", "preferredLanguage", "baseLocale"],
        urlPatterns: [
          {
            pattern: "/",
            localized: [
              ["fr", "/fr"],
              ["en", "/en"],
            ],
          },
          {
            pattern: "/:path(.*)?",
            localized: [
              ["fr", "/fr/:path(.*)?"],
              ["en", "/en/:path(.*)?"],
            ],
          },
        ],
      }),
      tanstackRouter({
        target: "react",
        autoCodeSplitting: true,
        basePath: !env.DEV && !!__HOST_URL__ ? `${__HOST_URL__}/offline` : "/",
      }),
      tailwindcss(),
      react(),
      serwist({
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
  }
})
