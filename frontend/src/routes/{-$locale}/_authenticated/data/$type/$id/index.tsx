import { createFileRoute } from "@tanstack/react-router"
import { UpdateDataWarning } from "@/components/update-data-warning"
import ReportDetail from "@/components/report-detail"
import SignageDetail from "@/components/signage-detail"
import InfrastructureDetail from "@/components/infrastructure-detail"
import NotFound from "@/components/not-found"
import InterventionDetail from "@/components/intervention-details"
import { usePermission } from "@/hook/useSettingsQuery"
import NotAllowed from "@/components/not-allowed"
export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/$id/"
)({
  beforeLoad: UpdateDataWarning,
  component: RouteComponent,
})

function RouteComponent() {
  const params = Route.useParams()
  const permissions = usePermission()

  if (params.type === "signage") {
    if (!permissions.signage.read) {
      return <NotAllowed />
    }
    return <SignageDetail {...params} />
  }

  if (params.type === "infrastructure") {
    if (!permissions.infrastructure.read) {
      return <NotAllowed />
    }
    return <InfrastructureDetail {...params} />
  }

  if (params.type === "intervention") {
    if (!permissions.intervention.read) {
      return <NotAllowed />
    }
    return <InterventionDetail {...params} />
  }

  if (params.type === "report") {
    if (!permissions.report.read) {
      return <NotAllowed />
    }
    return <ReportDetail {...params} />
  }

  return <NotFound />
}
