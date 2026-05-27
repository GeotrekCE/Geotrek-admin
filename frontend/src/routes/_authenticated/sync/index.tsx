import Header from "@/components/header"
import { createFileRoute } from "@tanstack/react-router"
import { Download } from "lucide-react"
import { ConnectionStatus } from "@/components/connection-status"
import SyncReferences from "@/components/sync-references"
import SyncMap from "@/components/sync-map"
import SyncData from "@/components/sync-data"

export const Route = createFileRoute("/_authenticated/sync/")({
  component: Sync,
})

function Sync() {
  return (
    <div>
      <Header title="Synchronisation" />
      <ConnectionStatus className="p-4" />

      <section className="m-4">
        <h2 className="flex items-center gap-2 text-xl font-bold text-accent-foreground">
          <Download aria-hidden /> Synchronisation avant terrain
        </h2>

        <SyncReferences />

        <SyncMap />

        <SyncData />
      </section>
    </div>
  )
}
