import { createFileRoute } from "@tanstack/react-router"
import { UpdateDataWarning } from "@/components/update-data-warning"
import ReportDetail from "@/components/report-detail"
import SignageDetail from "@/components/signage-detail"
import InfrastructureDetail from "@/components/infrastructure-detail"
import NotFound from "@/components/not-found"
import InterventionDetail from "@/components/intervention-details"
export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/$id/"
)({
  beforeLoad: UpdateDataWarning,
  component: RouteComponent,
})

function RouteComponent() {
  const params = Route.useParams()

  if (params.type === "signage") {
    return <SignageDetail {...params} />
  }

  if (params.type === "infrastructure") {
    return <InfrastructureDetail {...params} />
  }

  if (params.type === "intervention") {
    return <InterventionDetail {...params} />
  }

  if (params.type === "report") {
    return <ReportDetail {...params} />
  }

  return <NotFound />
}
