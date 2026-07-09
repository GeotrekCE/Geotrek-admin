import { getBodyForMutation, queryFnWithAuth } from "@/lib/api"
import { useMutation } from "@tanstack/react-query"
import type { ReportDataSchemaProps } from "@/schemas/data"

export default function useSyncInfrastructureMutation() {
  return useMutation({
    mutationKey: ["upSync", "report"],
    mutationFn: (data: ReportDataSchemaProps[]) =>
      Promise.all(
        data.map(async (body) => {
          const isPOST = body.appNewItem === true
          const promise = await queryFnWithAuth(
            `/report/drf/reports${!isPOST ? "/" + body.id : ""}`,
            {
              method: isPOST ? "POST" : "PATCH",
              searchParams: { format: "gtam" },
              body: JSON.stringify(getBodyForMutation(body)),
            }
          ).catch((error) => error)
          return { [body.id]: promise }
        })
      ),
  })
}
