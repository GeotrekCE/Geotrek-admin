import { Link } from "@tanstack/react-router"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAppSettings } from "@/hook/useAppSettings"
import CardSync from "@/components/card-sync"
import { buttonVariants } from "@/components/ui/button"

export default function SyncMap() {
  const {
    data: { maps },
  } = useAppSettings()

  const hasData = maps?.layers?.length

  return (
    <CardSync
      className="my-4"
      title="Fonds cartographiques"
      noData="Fichiers cartographiques manquants"
      updatedStatus={hasData ? "UPDATED" : "EXPIRED"}
      lastSync={maps?.lastSync}
      description={
        <>
          <p>
            Fichiers tuiles cartographiques et choix des fonds de cartes
            embarqués en hors ligne (téléchargés en local)
          </p>
          {hasData && (
            <p className="mt-4 flex items-center gap-2 text-sm text-primary">
              <Check className="size-4" aria-hidden /> {maps?.layers?.length}{" "}
              fond(s) cartographique(s) embarqué(s)
            </p>
          )}
        </>
      }
      actions={
        <Link
          className={cn("w-full", buttonVariants())}
          to="/{-$locale}/sync/map"
        >
          {hasData ? "Modifier" : "Choisir"}
        </Link>
      }
    />
  )
}
