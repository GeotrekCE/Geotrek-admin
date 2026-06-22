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

export default function SyncData() {
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
      title="Données embarquées"
      description={
        <>
          <p>
            Fiches métiers (signalétiques, signalements, interventions,
            aménagements) de la zone géographique sélectionnée"
          </p>
          {lastSync && bounds && (
            <div>
              <h4 className="my-4 font-bold text-accent-foreground">
                Zone géographique
              </h4>
              <Map
                className="pointer-none aspect-square max-h-80 touch-none"
                noControls
                initialViewState={{ bounds: bounds as LngLatBoundsLike }}
              />
              <h4 className="my-4 font-bold text-accent-foreground">
                Structure(s) gestionnaire(s)
              </h4>
              {structure === null ? "Toutes les structures" : "Ma structure"}
            </div>
          )}
        </>
      }
      noData="Aucune zone / structure n'a été définie"
      lastSync={lastSync}
      updatedStatus={getUpdatedStatus(lastSync, updateLimitation)}
      actions={
        <>
          <Link
            className={cn("w-full", buttonVariants())}
            to="/{-$locale}/sync/data"
          >
            {lastSync && bounds ? "Changer de zone" : "Choisir"}
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
      }
    />
  )
}
