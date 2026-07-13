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
import { m } from "@/paraglide/messages"
import { usePermission } from "@/hook/useSettingsQuery"

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

  const permissions = usePermission()

  const hasPermissionsToCreate =
    permissions.infrastructure.create ||
    permissions.signage.create ||
    permissions.intervention.create ||
    permissions.report.create

  return (
    <Card className="my-4 border border-destructive bg-destructive/20 text-accent-foreground">
      <CardHeader>
        <CardTitle>
          <h3 className="flex gap-3">
            <CircleAlert aria-hidden className="text-destructive" />
            {m["common.items-count"]({ count: totalCount })}{" "}
            {m["content.not-synced"]().toLowerCase()}
          </h3>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="mb-4 flex flex-col gap-3">
          {signageCount > 0 && (
            <li>{m["common.signage-count"]({ count: signageCount })}</li>
          )}
          {interventionCount > 0 && (
            <li>
              {m["common.intervention-count"](
                { count: interventionCount },
                { locale: "fr" }
              )}
            </li>
          )}
          {infrastructureCount > 0 && (
            <li>
              {m["common.infrastructure-count"]({ count: infrastructureCount })}
            </li>
          )}
          {reportCount > 0 && (
            <li>{m["common.report-count"]({ count: reportCount })}</li>
          )}
        </ul>
        {hasPermissionsToCreate && (
          <Link
            className={cn("w-full", buttonVariants())}
            to="/{-$locale}/sync/upload"
          >
            {m["common.send-data"]()}
          </Link>
        )}
        {!hasPermissionsToCreate && <p>{m["common.sync-no-rights"]()}</p>}
      </CardContent>
    </Card>
  )
}

export default function SyncUp({ data }: { data?: Data }) {
  const hasAsyncData = data && (data?.flat().length ?? 0) > 0
  return (
    <section className="my-4" id="sync-up">
      <h2 className="flex items-center gap-2 text-xl font-bold text-accent-foreground">
        <Upload aria-hidden /> {m["common.sync-up-title"]()}
      </h2>
      {hasAsyncData && <Message data={data} />}
      {!hasAsyncData && (
        <p className="my-4 text-sm text-muted-foreground">
          {m["common.sync-up-no-data"]()}
        </p>
      )}
    </section>
  )
}
