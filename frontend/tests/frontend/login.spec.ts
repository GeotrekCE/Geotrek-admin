import { test, expect } from "@playwright/test"

// Clean session before testing
test.use({ storageState: { cookies: [], origins: [] } })

test("try to go to settings", async ({ page }) => {
  await page.goto("./settings")
  await expect(page.getByTestId("login-form")).toBeVisible()
  await expect(page).toHaveURL("./login?redirect=%2Fsettings")
})
test("wrong authentication", async ({ page }) => {
  await page.goto("./settings")
  const promise = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/auth/token/") &&
      response.status() === 401 &&
      response.request().method() === "POST"
  )
  await page.getByTestId("field-username").fill("Test")
  await page.getByTestId("field-password").fill("Test")
  await page.locator("[type=submit]").click()
  const response = await promise
  await expect(response.status()).toEqual(401)
  await expect(
    page.getByText("No active account found with the given credentials")
  ).toBeVisible()
  await expect(page).toHaveURL("./login?redirect=%2Fsettings")
})

// Authenticate test is runned from auth.setup.ts
