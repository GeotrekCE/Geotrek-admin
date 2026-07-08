import { getBodyForMutation, queryFnWithAuth } from "@/lib/api"
import { useMutation } from "@tanstack/react-query"
import type { ReportDataSchemaProps } from "@/schemas/data"

export default function useSyncInfrastructureMutation() {
  return useMutation({
    mutationKey: ["upSync", "report"],
    mutationFn: (data: ReportDataSchemaProps[]) =>
      Promise.all(
        data.map((body) => {
          const isPOST = body.appNewItem === true
          return queryFnWithAuth(
            `/report/drf/reports${!isPOST ? "/" + body.id : ""}`,
            {
              method: isPOST ? "POST" : "PATCH",
              searchParams: { format: "gtam" },
              body: JSON.stringify(getBodyForMutation(body)),
            }
          ).catch((error) => error)
        })
      ),
  })
}
