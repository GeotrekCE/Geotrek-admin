import { defineConfig, devices } from "@playwright/test"
import { loadEnv } from "vite"

const env = loadEnv("test", process.cwd(), "")
for (const [key, value] of Object.entries(env)) {
  if (process.env[key] === undefined) {
    process.env[key] = value
  }
}

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  reporter: "html",
  use: {
    baseURL: "https://test-admin.geotrek.fr/m/",
    serviceWorkers: "allow",
    ignoreHTTPSErrors: true,
    trace: "on-first-retry",
  },

  projects: [
    { name: "setup auth", testMatch: /auth\.setup\.ts/ },
    {
      name: "setup data",
      testMatch: /data\.setup\.ts/,
      use: {
        storageState: "playwright/.auth/user.json",
      },
      dependencies: ["setup auth"],
    },
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "playwright/.auth/user.json",
      },
      dependencies: ["setup auth", "setup data"],
    },

    {
      name: "firefox",
      use: {
        ...devices["Desktop Firefox"],
        storageState: "playwright/.auth/user.json",
      },
      dependencies: ["setup auth", "setup data"],
    },

    {
      name: "webkit",
      use: {
        ...devices["Desktop Safari"],
        storageState: "playwright/.auth/user.json",
      },
      dependencies: ["setup auth", "setup data"],
    },
  ],
})
