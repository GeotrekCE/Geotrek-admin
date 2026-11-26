import { test as setup, expect } from "@playwright/test"
import fs from "fs"
import path from "path"
import { fileURLToPath } from "url"

const username = process.env.PLAYWRIGHT_USERNAME
const password = process.env.PLAYWRIGHT_PASSWORD

if (!username || !password) {
  throw new Error(
    "Set PLAYWRIGHT_USERNAME and PLAYWRIGHT_PASSWORD to run authenticated Playwright tests."
  )
}

const authFile = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "../playwright/.auth/user.json"
)

setup("authenticate", async ({ page }) => {
  await page.goto("./settings")
  await page.getByTestId("field-username").fill(username)
  await page.getByTestId("field-password").fill(password)
  const promise = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/auth/token/") &&
      response.request().method() === "POST"
  )
  await page.locator("[type=submit]").click()
  const response = await promise
  await expect(response.status()).toEqual(200)
  await expect(page.getByText("Connection successful")).toBeVisible()
  await expect(page).toHaveURL("./settings")

  fs.mkdirSync(path.dirname(authFile), { recursive: true })
  await page.context().storageState({ path: authFile, indexedDB: true })
})
