import { useLiveQuery } from "dexie-react-hooks"
import { useReferencesQuery } from "@/hook/useReferencesQuery"
import CardSync from "@/components/card-sync"
import { getUpdatedStatus } from "@/lib/date"
import { useIntervalSync } from "@/hook/useSettingsQuery"
import { Button } from "@/components/ui/button"
import { db } from "@/lib/db"
import { m } from "@/paraglide/messages"

export default function SyncReferences() {
  const { refetch } = useReferencesQuery()
  const updateLimitation = useIntervalSync("references")
  const appSync = useLiveQuery(() => db.appSync.get("references"))
  const lastSync = appSync?.lastSync

  return (
    <CardSync
      className="my-4"
      title={m["common.sync-reference-title"]()}
      description={m["common.sync-reference-description"]()}
      noData={m["common.sync-reference-none"]()}
      lastSync={lastSync}
      updatedStatus={getUpdatedStatus(lastSync, updateLimitation)}
      actions={
        <Button className="w-full" onClick={refetch}>
          {m["common.update"]()}
        </Button>
      }
    />
  )
}
