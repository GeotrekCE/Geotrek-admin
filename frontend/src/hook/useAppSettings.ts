const APP_SETTINGS_KEY = "appSettings"

function getStorageElement(key: string) {
  return JSON.parse(localStorage.getItem(key) || "{}")
}

export function useAppSettings() {
  return {
    data: getStorageElement(APP_SETTINGS_KEY),
    setData: (nextData: Record<string, string | null | number>) => {
      localStorage.setItem(
        "appSettings",
        JSON.stringify({
          ...getStorageElement(APP_SETTINGS_KEY),
          ...nextData,
        })
      )
    },
  }
}
