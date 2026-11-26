import { test as setup, expect } from "@playwright/test"
import fs from "fs"
import path from "path"
import { fileURLToPath } from "url"

const dataState = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "../playwright/.cache/with-data.json"
)

setup("synchronize data for offline tests", async ({ page, context }) => {
  await page.goto("./sync")
  const promiseReferences = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/common/references/") &&
      response.request().method() === "GET"
  )
  await page.getByRole("button", { name: "Update", exact: true }).click()
  const responseReferences = await promiseReferences
  await expect(responseReferences.status()).toEqual(200)
  await expect(page.getByText("Saved references")).toBeVisible()

  await page.goto("./sync")
  await page.getByRole("link", { name: "Pick", exact: true }).nth(1).click()
  await expect(page).toHaveURL("./sync/data")
  await expect(
    page.getByRole("heading", { name: "Embedded Data", exact: true })
  ).toBeVisible()
  await page.getByRole("button", { name: "Zoom in", exact: true }).click()
  await page.getByRole("button", { name: "Zoom in", exact: true }).click()
  const promiseData = page.waitForResponse(
    (response) =>
      response.url().includes("/api/signage/drf/signages") &&
      response.status() === 200 &&
      response.request().method() === "GET"
  )
  await page.getByRole("button", { name: "Download data", exact: true }).click()
  const responseData = await promiseData
  await expect(responseData.status()).toEqual(200)
  await expect(page).toHaveURL("./sync")
  await expect(page.getByText("Data stored in the app")).toBeVisible()
  await expect(page.getByText("Change area")).toBeVisible()

  fs.mkdirSync(path.dirname(dataState), { recursive: true })
  await context.storageState({ path: dataState, indexedDB: true })
})
