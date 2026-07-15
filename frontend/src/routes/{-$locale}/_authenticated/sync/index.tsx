import Header from "@/components/header"
import { createFileRoute } from "@tanstack/react-router"
import { Download } from "lucide-react"
import { ConnectionStatus } from "@/components/connection-status"
import SyncReferences from "@/components/sync-references"
import SyncMap from "@/components/sync-map"
import SyncData from "@/components/sync-data"
import SyncUp from "@/components/sync-up"
import { useAsyncStoredData } from "@/hook/useStoredData"
import { m } from "@/paraglide/messages"

export const Route = createFileRoute("/{-$locale}/_authenticated/sync/")({
  component: Sync,
})

function Sync() {
  const asyncData = useAsyncStoredData()
  const hasAsyncData = (asyncData?.flat().length ?? 0) > 0

  return (
    <div>
      <Header title={m["menu.sync"]()} />
      <ConnectionStatus className="p-4" />

      <section className="m-4" id="sync-down">
        <h2 className="flex items-center gap-2 text-xl font-bold text-accent-foreground">
          <Download aria-hidden /> {m["common.sync-down-title"]()}
        </h2>

        <SyncReferences />

        <SyncMap />

        <SyncData hasAsyncData={hasAsyncData} />

        <SyncUp data={asyncData} />
      </section>
    </div>
  )
}
