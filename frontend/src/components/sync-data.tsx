import CardSync from "@/components/card-sync"
import Map from "@/components/map"
import { getUpdatedStatus } from "@/lib/date"
import { useIntervalSync } from "@/hook/useSettingsQuery"
import { Link } from "@tanstack/react-router"
import { Button, buttonVariants } from "@/components/ui/button"
import { useDataQuery } from "@/hook/useDataQuery"
import { cn } from "@/lib/utils"
import { getPolygonFromBounds } from "@/lib/map"
import type { LngLatBoundsLike } from "maplibre-gl"
import { db } from "@/lib/db"
import { useLiveQuery } from "dexie-react-hooks"
import { Alert, AlertTitle } from "./ui/alert"
import { CircleAlert } from "lucide-react"
import { m } from "@/paraglide/messages"

export default function SyncData({ hasAsyncData }: { hasAsyncData: boolean }) {
  const updateLimitation = useIntervalSync("data")

  const appSync = useLiveQuery(() => db.appSync.get("data"), [])

  const { bounds, structure, lastSync } = appSync || {}

  const { refetch } = useDataQuery({
    bbox: bounds
      ? getPolygonFromBounds(bounds as [number, number, number, number])
      : undefined,
    structure: structure ?? undefined,
  })

  return (
    <CardSync
      title={m["common.sync-data-title"]()}
      description={
        <>
          <p>{m["common.sync-data-description"]()}</p>
          {lastSync && bounds && (
            <div>
              <h4 className="my-4 font-bold text-accent-foreground">
                {m["common.sync-data-aera"]()}
              </h4>
              <Map
                className="pointer-none aspect-square max-h-80 touch-none"
                noControls
                initialViewState={{ bounds: bounds as LngLatBoundsLike }}
              />
              <h4 className="my-4 font-bold text-accent-foreground">
                {m["common.managing-structures"]()}
              </h4>
              {structure === null
                ? m["common.all-structures"]()
                : m["common.my-structure"]()}
            </div>
          )}
        </>
      }
      noData={m["common.sync-data-none"]()}
      lastSync={lastSync}
      updatedStatus={getUpdatedStatus(lastSync, updateLimitation)}
      actions={
        hasAsyncData ? (
          <>
            <Button className="w-full" disabled>
              {lastSync && bounds
                ? m["common.sync-data-edit-aera"]()
                : m["common.pick"]()}
            </Button>
            {lastSync && bounds && (
              <Button
                className="w-full"
                variant="outline"
                type="button"
                disabled
              >
                {m["common.sync-data-download"]()}
              </Button>
            )}
            <Alert
              variant="destructive"
              className="m-0 w-full border-0 bg-transparent p-0"
            >
              <CircleAlert aria-hidden />
              <AlertTitle>{m["common.update-needed-description"]()}</AlertTitle>
            </Alert>
          </>
        ) : (
          <>
            <Link
              className={cn("w-full", buttonVariants())}
              to="/{-$locale}/sync/data"
            >
              {lastSync && bounds
                ? m["common.sync-data-edit-aera"]()
                : m["common.pick"]()}
            </Link>
            {lastSync && bounds && (
              <Button
                className="w-full"
                variant="outline"
                onClick={refetch}
                type="button"
              >
                Re-télécharger les données
              </Button>
            )}
          </>
        )
      }
    />
  )
}
