import { useLiveQuery } from "dexie-react-hooks"
import { useReferencesQuery } from "@/hook/useReferencesQuery"
import CardSync from "@/components/card-sync"
import { getUpdatedStatus } from "@/lib/date"
import { useIntervalSync } from "@/hook/useSettingsQuery"
import { Button } from "@/components/ui/button"
import { db } from "@/lib/db"

export default function SyncReferences() {
  const { refetch } = useReferencesQuery()
  const updateLimitation = useIntervalSync("references")
  const appSync = useLiveQuery(() => db.appSync.get("references"))
  const lastSync = appSync?.lastSync

  return (
    <CardSync
      className="my-4"
      title="Référentiel de saisie"
      description="Fichiers de configuration du référentiel de saisie"
      noData="Fichier de configuration manquant"
      lastSync={lastSync}
      updatedStatus={getUpdatedStatus(lastSync, updateLimitation)}
      actions={
        <Button className="w-full" onClick={refetch}>
          Mettre à jour
        </Button>
      }
    />
  )
}
