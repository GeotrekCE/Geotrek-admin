import { CircleAlert } from "lucide-react"
import { Alert, AlertTitle } from "@/components/ui/alert"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"
import LastSync from "@/components/last-sync"
import useOnline from "@/hook/useOnline"
import { m } from "@/paraglide/messages"
import { usePermission } from "@/hook/useSettingsQuery"

type CardSyncProps = React.ComponentProps<"div"> & {
  title: string
  description: string | React.ReactElement
  updatedStatus: "UPDATED" | "WARNING" | "EXPIRED"
  lastSync?: string
  actions: React.ReactElement | null
  noData: string
}

export default function CardSync({
  title,
  description,
  updatedStatus,
  className,
  lastSync,
  actions,
  noData,
}: CardSyncProps) {
  const warning = updatedStatus !== "UPDATED" || lastSync === undefined
  const online = useOnline()
  const permissions = usePermission()

  const hasPermissionsToRead =
    permissions.infrastructure.read ||
    permissions.signage.read ||
    permissions.intervention.read ||
    permissions.report.read

  function getAlertTitle() {
    if (!lastSync) {
      return noData
    }
    if (updatedStatus === "WARNING") {
      return m["common.update-recommended"]()
    }
    return m["common.update-needed"]()
  }

  return (
    <Card
      className={cn(
        updatedStatus === "EXPIRED" &&
          "border border-destructive bg-destructive/20 text-accent-foreground",
        updatedStatus === "WARNING" &&
          "border border-yellow-500 bg-yellow-500/20 text-accent-foreground",
        className
      )}
    >
      <CardHeader>
        <CardTitle>
          <h3>{title}</h3>
        </CardTitle>
        <CardDescription className={cn(warning && "text-accent-foreground")}>
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {warning && (
          <Alert
            variant={updatedStatus === "WARNING" ? "warning" : "destructive"}
            className="m-0 w-full border-0 bg-transparent p-0"
          >
            <CircleAlert aria-hidden />
            <AlertTitle>{getAlertTitle()}</AlertTitle>
          </Alert>
        )}
        {!!lastSync && <LastSync date={lastSync} />}
      </CardContent>
      <CardFooter className="flex-col gap-4">
        {hasPermissionsToRead && online && actions}
        {hasPermissionsToRead && !online && (
          <p>{m["common.offline-cannot-sync"]()}</p>
        )}
        {!hasPermissionsToRead && <p>{m["common.sync-no-rights"]()}</p>}
      </CardFooter>
    </Card>
  )
}
