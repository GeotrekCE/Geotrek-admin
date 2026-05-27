import CardSync from "@/components/card-sync"
import Map from "@/components/map"
import { getUpdatedStatus } from "@/lib/date"
import { useIntervalSync } from "@/hook/useSettingsQuery"
import { Link } from "@tanstack/react-router"
import { useAppSettings } from "@/hook/useAppSettings"
import { Button, buttonVariants } from "@/components/ui/button"
import { useDataQuery } from "@/hook/useDataQuery"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { getPolygonFromBounds } from "@/lib/map"
import type { LngLatBoundsLike } from "maplibre-gl"

export default function SyncData() {
  const { data: updateLimitation } = useIntervalSync()
  const { data, setData } = useAppSettings()

  const { bounds, structure, lastSync } = data?.syncData || {}
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
          <Link className={cn("w-full", buttonVariants())} to="/sync/data">
            {lastSync && bounds ? "Changer de zone" : "Choisir"}
          </Link>
          {lastSync && bounds && (
            <Button
              className="w-full"
              variant="outline"
              onClick={() => {
                setData({
                  syncData: {
                    bounds,
                    structure: structure || null,
                    lastSync: new Date().toISOString(),
                  },
                })
                window.setTimeout(refetch, 1)
                toast.success(
                  "Données embarquées dans l'application avec succès",
                  {
                    position: "top-center",
                  }
                )
              }}
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
