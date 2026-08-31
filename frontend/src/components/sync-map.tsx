import { Link } from "@tanstack/react-router"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAppSettings } from "@/hook/useAppSettings"
import CardSync from "@/components/card-sync"
import { buttonVariants } from "@/components/ui/button"
import { m } from "@/paraglide/messages"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"

export default function SyncMap() {
  const {
    data: { map },
  } = useAppSettings()

  const settings = useLiveQuery(() => db.settings.get("settings"))

  const offlineLayers = settings?.settings?.map.layers.offline ?? []

  const hasData = map?.layers?.length

  return (
    <CardSync
      className="my-4"
      title={m["common.sync-map-title"]()}
      noData={
        offlineLayers.length > 0
          ? m["common.sync-map-none"]()
          : m["common.sync-no-configured-map"]()
      }
      updatedStatus={
        hasData || offlineLayers.length === 0 ? "UPDATED" : "EXPIRED"
      }
      lastSync={map?.lastSync}
      description={
        <>
          <p>{m["common.sync-map-description"]()} </p>
          {hasData && (
            <p className="mt-4 flex items-center gap-2 text-sm text-primary">
              <Check className="size-4" aria-hidden />
              {m["common.map-layers-count"]({
                count: map?.layers?.length ?? 0,
              })}
            </p>
          )}
        </>
      }
      actions={
        offlineLayers.length > 0 ? (
          <Link
            className={cn("w-full", buttonVariants())}
            to="/{-$locale}/sync/map"
          >
            {hasData ? m["common.edit"] : m["common.pick"]}
          </Link>
        ) : null
      }
    />
  )
}
