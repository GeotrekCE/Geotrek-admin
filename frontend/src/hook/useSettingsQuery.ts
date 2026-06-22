import { queryOptions } from "@tanstack/react-query"
import { queryFnWithAuth, useAppQuery } from "@/lib/api"
import { settingsSchema } from "@/schemas/settings"
import { DAY, HOUR } from "@/lib/date"
import { db } from "@/lib/db"
import { useLiveQuery } from "dexie-react-hooks"

const DEFAULT_UPDATE_LIMITATION = 7 * DAY
export const SETTINGS_QUERY_KEY = ["settings"]

const options = queryOptions({
  queryKey: SETTINGS_QUERY_KEY,
  queryFn: async () => {
    const data = await queryFnWithAuth("/gtam/config/", {
      schema: settingsSchema,
    })
    await db.settings.put({ id: "settings", ...data })
    return data
  },
})

export function useSettingsQuery(isEnabled = true) {
  return useAppQuery({ queryOptions: { ...options, enabled: isEnabled } })
}

export function useSettingsQueryOfflineFirst() {
  return useSettingsQuery(false)
}

export function useIntervalSync(type: "data" | "references") {
  const settings = useLiveQuery(() => db.settings.get("settings"))
  return (
    (settings?.settings.intervalSyncInHours[type] ?? 0) * HOUR ||
    DEFAULT_UPDATE_LIMITATION
  )
}

export function usePermission() {
  const settings = useLiveQuery(() => db.settings.get("settings"))
  return (
    settings?.user.permissions || {
      signage: {
        create: false,
        read: false,
        update: false,
        delete: false,
      },
      infrastructure: {
        create: false,
        read: false,
        update: false,
        delete: false,
      },
      intervention: {
        create: false,
        read: false,
        update: false,
        delete: false,
      },
      report: {
        create: false,
        read: false,
        update: false,
        delete: false,
      },
    }
  )
}
