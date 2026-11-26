import { test, expect } from "@playwright/test"
test.describe.configure({ mode: "serial" })
test.describe("navigate without data", () => {
  test("not to homepage", async ({ page }) => {
    await page.goto("./")
    await expect(
      page.getByRole("heading", { name: "Synchronization", exact: true })
    ).toBeVisible()
    await expect(page).toHaveURL("./sync")
    await expect(
      page.getByLabel("Notifications alt+T").getByText("An update is necessary")
    ).toBeVisible()
  })
  test("not to create page", async ({ page }) => {
    await page.goto("./create")
    await expect(
      page.getByRole("heading", { name: "Synchronization", exact: true })
    ).toBeVisible()
    await expect(page).toHaveURL("./sync")
    await expect(
      page.getByLabel("Notifications alt+T").getByText("An update is necessary")
    ).toBeVisible()
  })
  test("to settings", async ({ page }) => {
    await page.goto("./settings")
    await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible()
    await expect(page).toHaveURL("./settings")
  })

  test("to sync page", async ({ page }) => {
    await page.goto("./sync")
    await expect(
      page.getByRole("heading", { name: "Synchronization", exact: true })
    ).toBeVisible()
    await expect(page).toHaveURL("./sync")
  })
})

test.describe("store data", () => {
  test("referentiel", async ({ page }) => {
    await page.goto("./sync")
    // await expect(page.getByLabel("Missing configuration file")).toBeVisible()
    const promise = page.waitForResponse(
      (response) =>
        response.url().endsWith("/api/common/references/") &&
        response.status() === 200 &&
        response.request().method() === "GET"
    )
    await page.getByRole("button", { name: "Update", exact: true }).click()
    const response = await promise
    await expect(response.status()).toEqual(200)
    await expect(page.getByText("Saved references")).toBeVisible()
  })

  test("data", async ({ page }) => {
    await page.goto("./sync")
    await page.getByRole("link", { name: "Pick", exact: true }).nth(1).click()
    await expect(page).toHaveURL("./sync/data")
    await expect(
      page.getByRole("heading", { name: "Embedded Data", exact: true })
    ).toBeVisible()
    await page.getByRole("button", { name: "Zoom in", exact: true }).click()
    await page.getByRole("button", { name: "Zoom in", exact: true }).click()
    const promise = page.waitForResponse(
      (response) =>
        response.url().includes("/api/signage/drf/signages") &&
        response.status() === 200 &&
        response.request().method() === "GET"
    )
    await page
      .getByRole("button", { name: "Download data", exact: true })
      .click()
    const response = await promise
    await expect(response.status()).toEqual(200)
    await expect(page).toHaveURL("./sync")
    await expect(page.getByText("Data stored in the app")).toBeVisible()
    await expect(page.getByText("Change area")).toBeVisible()
  })
})

test.describe("navigate with data", () => {
  test.use({ storageState: "tests/playwright/.cache/with-data.json" })

  test("to homepage", async ({ page }) => {
    await page.goto("./")
    await expect(page).toHaveURL("./")
  })
  test("to create page", async ({ page }) => {
    await page.goto("./create")
    await expect(page).toHaveURL("./create")
  })
})
