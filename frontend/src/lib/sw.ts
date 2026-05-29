import type {
  PrecacheEntry,
  RuntimeCaching,
  SerwistGlobalConfig,
} from "serwist"
import {
  ExpirationPlugin,
  NetworkOnly,
  Serwist,
  StaleWhileRevalidate,
} from "serwist"

const runtimeCaching: RuntimeCaching[] = import.meta.env.DEV
  ? [
      {
        matcher: /.*/i,
        handler: new NetworkOnly(),
      },
    ]
  : [
      {
        matcher: /\.(?:eot|otf|ttc|ttf|woff|woff2|font.css)$/i,
        handler: new StaleWhileRevalidate({
          cacheName: "static-font-assets",
          plugins: [
            new ExpirationPlugin({
              maxEntries: 4,
              maxAgeSeconds: 7 * 24 * 60 * 60, // 7 days
              maxAgeFrom: "last-used",
            }),
          ],
        }),
      },
      {
        matcher: /\.(?:js)$/i,
        handler: new StaleWhileRevalidate({
          cacheName: "static-js-assets",
          plugins: [
            new ExpirationPlugin({
              maxEntries: 32,
              maxAgeSeconds: 24 * 60 * 60, // 24 hours
              maxAgeFrom: "last-used",
            }),
          ],
        }),
      },
      {
        matcher: /\.(?:css)$/i,
        handler: new StaleWhileRevalidate({
          cacheName: "static-style-assets",
          plugins: [
            new ExpirationPlugin({
              maxEntries: 32,
              maxAgeSeconds: 24 * 60 * 60, // 24 hours
              maxAgeFrom: "last-used",
            }),
          ],
        }),
      },
    ]

declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: (PrecacheEntry | string)[] | undefined
  }
}

declare const self: ServiceWorkerGlobalScope

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching,
  fallbacks: {
    entries: [
      {
        url: `${import.meta.env.BASE_URL}index.html`,
        matcher({ request }) {
          return request.mode === "navigate"
        },
      },
    ],
  },
  precacheOptions: {
    navigateFallback: "/offline/index.html",
    navigateFallbackDenylist: [/^\/offline\/assets\//, /\.[a-zA-Z0-9]+$/],
  },
})

serwist.addEventListeners()
