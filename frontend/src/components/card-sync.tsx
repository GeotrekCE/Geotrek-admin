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

type CardSyncProps = React.ComponentProps<"div"> & {
  title: string
  description: string | React.ReactElement
  updatedStatus: "UPDATED" | "WARNING" | "EXPIRED"
  lastSync?: string
  actions: React.ReactElement
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

  function getAlertTitle() {
    if (!lastSync) {
      return noData
    }
    if (updatedStatus === "WARNING") {
      return "Une mise à jour est recommandée"
    }
    return "Une mise à jour est nécessaire"
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
        {online ? (
          actions
        ) : (
          <p>Vous êtes hors ligne et ne pouvez pas télécharger les données</p>
        )}
      </CardFooter>
    </Card>
  )
}
