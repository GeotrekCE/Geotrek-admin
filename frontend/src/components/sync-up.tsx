import { CircleAlert, Upload } from "lucide-react"
import type {
  InfrastructureDataSchemaProps,
  InterventionDataSchemaProps,
  ReportDataSchemaProps,
  SignageDataSchemaProps,
} from "@/schemas/data"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { buttonVariants } from "@/components/ui/button"
import { Link } from "@tanstack/react-router"

type Data = [
  SignageDataSchemaProps[],
  InterventionDataSchemaProps[],
  InfrastructureDataSchemaProps[],
  ReportDataSchemaProps[],
]

function Message({
  data: [signageData, interventionData, InfrastructureData, ReportData],
}: {
  data: Data
}) {
  const signageCount = signageData.length
  const interventionCount = interventionData.length
  const infrastructureCount = InfrastructureData.length
  const reportCount = ReportData.length
  const totalCount =
    signageCount + interventionCount + infrastructureCount + reportCount
  return (
    <Card className="my-4 border border-destructive bg-destructive/20 text-accent-foreground">
      <CardHeader>
        <CardTitle>
          <h3 className="flex gap-3">
            <CircleAlert aria-hidden className="text-destructive" />
            {totalCount} élément(s) non synchronisé(s)
          </h3>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="mb-4 flex flex-col gap-3">
          {signageCount > 0 && <li>{signageCount} signalétique(s)</li>}
          {interventionCount > 0 && (
            <li>{interventionCount} intervention(s)</li>
          )}
          {infrastructureCount > 0 && (
            <li>{infrastructureCount} aménagement(s)</li>
          )}
          {reportCount > 0 && <li>{reportCount} signalement(s)</li>}
        </ul>
        <Link
          className={cn("w-full", buttonVariants())}
          to="/{-$locale}/sync/upload"
        >
          Envoyer mes données
        </Link>
      </CardContent>
    </Card>
  )
}

export default function SyncUp({ data }: { data?: Data }) {
  const hasAsyncData = data && (data?.flat().length ?? 0) > 0
  return (
    <section className="my-4">
      <h2 className="flex items-center gap-2 text-xl font-bold text-accent-foreground">
        <Upload aria-hidden /> Mes relevés de terrain
      </h2>
      {hasAsyncData && <Message data={data} />}
      {!hasAsyncData && (
        <div className="m-4">
          <p className="text-sm text-muted-foreground">
            Aucun relevé de terrain n'a été crée ou modifié depuis la dernière
            synchronisation.
          </p>
        </div>
      )}
    </section>
  )
}
