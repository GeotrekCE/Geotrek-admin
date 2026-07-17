import { db } from "@/lib/db"
import { redirect } from "@tanstack/react-router"
import { toast } from "sonner"
import { m } from "@/paraglide/messages"

export async function UpdateDataWarning() {
  const hasReferencesSettings = await db.appSync.get("references")
  const hasDataSettings = await db.appSync.get("data")
  if (!hasReferencesSettings || !hasDataSettings) {
    toast.info(
      <div>
        <p className="font-bold">{m["common.update-needed"]()}</p>
        <p>{m["common.update-needed-description"]()}</p>
      </div>,
      {
        position: "top-center",
      }
    )
    throw redirect({ to: "/{-$locale}/sync" })
  }
}
