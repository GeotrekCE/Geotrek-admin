import { queryOptions } from "@tanstack/react-query"
import { queryFnWithAuth, useAppQuery } from "@/lib/api"
import { settingsSchema } from "@/schemas/settings"
import { DAY, HOUR } from "@/lib/date"

const DEFAULT_UPDATE_LIMITATION = 7 * DAY
export const SETTINGS_QUERY_KEY = ["settings"]

const options = queryOptions({
  queryKey: SETTINGS_QUERY_KEY,
  queryFn: () => queryFnWithAuth("/gtam/config/", { schema: settingsSchema }),
})

export function useSettingsQuery(isEnabled = true) {
  return useAppQuery({ queryOptions: { ...options, enabled: isEnabled } })
}

export function useSettingsQueryOfflineFirst() {
  return useSettingsQuery(false)
}

export function useIntervalSync() {
  const settings = useSettingsQueryOfflineFirst()
  return {
    data:
      // TODO: "data" key from API
      (settings?.data?.intervalSyncInHours?.references ?? 0 * HOUR) ||
      DEFAULT_UPDATE_LIMITATION,
    references:
      (settings?.data?.intervalSyncInHours?.references ?? 0 * HOUR) ||
      DEFAULT_UPDATE_LIMITATION,
  }
}
