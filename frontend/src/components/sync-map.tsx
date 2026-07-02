import CardSync from "@/components/card-sync"
import { buttonVariants } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Link } from "@tanstack/react-router"

export default function SyncMap() {
  return (
    <CardSync
      className="my-4"
      title="Fonds cartographiques"
      description="Fichiers tuiles cartographiques et choix des fonds de cartes embarqués en hors ligne (téléchargés en local)"
      noData="Fichiers cartographiques manquants"
      updatedStatus="EXPIRED"
      actions={
        <Link
          className={cn("w-full", buttonVariants())}
          to="/{-$locale}/sync/map"
        >
          {/* {lastSync && bounds ? "Modifier" : "Choisir"} */}
          Choisir
        </Link>
      }
    />
  )
}
