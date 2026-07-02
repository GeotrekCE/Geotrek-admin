import * as React from "react"
import type { Dispatch, SetStateAction } from "react"
import { Check, Download, X } from "lucide-react"
import { cn } from "@/lib/utils"
import type { SettingsSchemaProps } from "@/schemas/settings"
import { Progress } from "@/components/ui/progress"
import { Sheet, SheetContent, SheetFooter } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { useQueries } from "@tanstack/react-query"
import { useOfflineMaps } from "@/hook/useOfflineMaps"
import { Spinner } from "@/components/ui/spinner"

export default function MapDownloadProgress({
  layers,
  layersName,
  open,
  setOpen,
  size,
}: {
  layers: SettingsSchemaProps["settings"]["maps"]["layers"]
  layersName: string[]
  open: boolean
  setOpen: Dispatch<SetStateAction<boolean>>
  size: string
}) {
  const { cancelDownload, currentProgress, downloadZone } = useOfflineMaps()

  const queries = useQueries({
    queries: layersName.map((layerName) => ({
      queryKey: ["offlineMap", layerName],
      queryFn: async () => {
        const layer = layers.find((layer) => layer.name === layerName)
        if (layer) {
          return downloadZone(layer)
        }
      },
      enabled: open,
    })),
  })

  const isAllSuccess = queries.every(({ isSuccess }) => isSuccess)
  const isFailed = queries.some(({ isError }) => isError)

  const refetch = React.useCallback(() => {
    queries.forEach((result) => result?.refetch())
  }, [queries])

  const getProgress = () => {
    if (isAllSuccess) {
      return 100
    }
    if (isFailed) {
      return 0
    }
    return currentProgress ?? 100
  }

  const progress = getProgress()

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetContent
        showCloseButton={false}
        className="z-60 h-full! w-full! max-w-full! overflow-auto"
      >
        <div className="p-4">
          <div
            className={cn(
              "mx-auto my-8 flex aspect-square max-w-50 items-center justify-center rounded-full bg-primary/30 text-primary",
              isAllSuccess && "bg-green-600/30 text-green-600",
              isFailed && "bg-destructive/30 text-destructive"
            )}
          >
            {isAllSuccess && (
              <Check aria-hidden className="size-1/2 stroke-1" />
            )}
            {isFailed && <X aria-hidden className="size-1/2 stroke-1" />}
            {!isFailed && !isAllSuccess && (
              <Download aria-hidden className="size-1/2 stroke-1" />
            )}
          </div>
          <p className="mb-4 text-center text-xl font-bold text-accent-foreground">
            {isAllSuccess && "Téléchargement terminé"}
            {isFailed &&
              "Échec du téléchargement des fonds et tuiles cartographiques"}
            {!isFailed &&
              !isAllSuccess &&
              "Téléchargement des tuiles et fonds cartographique sélectionnés"}
          </p>
          <div>
            <div className="my-2 flex flex-wrap items-center justify-between gap-2">
              <span className="font-bold text-primary">{progress}%</span>
              {parseFloat(size) > 0 && (
                <span>
                  {((parseFloat(size) / 100) * progress).toFixed(1)} / {size}
                </span>
              )}
            </div>
            <Progress value={progress} />
          </div>
        </div>
        <ul className="m-4">
          {queries.map((item, index) => (
            <li
              key={index}
              className={cn(
                "flex items-center gap-2 text-accent-foreground",
                item.isError && "text-destructive",
                item.isSuccess && "text-green-600"
              )}
            >
              {item.isPending && <Spinner aria-label="Chargement" role="img" />}
              {item.isError && (
                <X aria-label="Échec du chargement" role="img" />
              )}
              {item.isSuccess && (
                <Check aria-label="Chargement réussi" role="img" />
              )}{" "}
              {layersName[index]}
            </li>
          ))}
        </ul>
        <SheetFooter>
          {isAllSuccess && (
            <Button
              type="submit"
              className="w-full"
              onClick={() => setOpen(false)}
            >
              Fermer
            </Button>
          )}
          {isFailed && (
            <Button type="submit" className="w-full" onClick={refetch}>
              Relancer le téléchargement
            </Button>
          )}
          {!isAllSuccess && (
            <Button
              type="submit"
              className="w-full"
              variant="destructive"
              onClick={() => {
                cancelDownload()
                setOpen(false)
              }}
            >
              Annuler
            </Button>
          )}
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
