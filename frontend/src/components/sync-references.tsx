import { useQueryClient } from "@tanstack/react-query"
import {
  COMMON_REFERENCES_QUERY_KEY,
  useReferencesQuery,
} from "@/hook/useReferencesQuery"
import CardSync from "@/components/card-sync"
import { getUpdatedStatus } from "@/lib/date"
import { useIntervalSync } from "@/hook/useSettingsQuery"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"

export default function SyncReferences() {
  const queryClient = useQueryClient()
  const { references, refetch } = useReferencesQuery()
  const { references: updateLimitation } = useIntervalSync()

  const dataSettings =
    references.common.data ||
    queryClient.getQueryData(COMMON_REFERENCES_QUERY_KEY)

  const lastSync = dataSettings?.lastSync

  return (
    <CardSync
      className="my-4"
      title="Référentiel de saisie"
      description="Fichiers de configuration du référentiel de saisie"
      noData="Fichier de configuration manquant"
      lastSync={lastSync}
      updatedStatus={getUpdatedStatus(lastSync, updateLimitation)}
      actions={
        <Button
          className="w-full"
          onClick={() => {
            refetch()
            toast.success("Référentiels de saisie synchronisés avec succès", {
              position: "top-center",
            })
          }}
        >
          Mettre à jour
        </Button>
      }
    />
  )
}
