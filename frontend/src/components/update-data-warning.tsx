import { db } from "@/lib/db"
import { redirect } from "@tanstack/react-router"
import { toast } from "sonner"

export async function UpdateDataWarning() {
  const hasReferencesSettings = await db.appSync.get("references")
  const hasDataSettings = await db.appSync.get("data")
  if (!hasReferencesSettings || !hasDataSettings) {
    toast.info(
      <div>
        <p className="font-bold">Une mise à jour est nécessaire</p>
        <p>
          Veuillez mettre à jour les données de référentiel de saisie avant
          votre sortie de terrain.
        </p>
      </div>,
      {
        position: "top-center",
      }
    )
    throw redirect({ to: "/{-$locale}/sync" })
  }
}
