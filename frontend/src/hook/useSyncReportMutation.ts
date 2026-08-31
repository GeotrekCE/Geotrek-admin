import { useMutation } from "@tanstack/react-query"
import type { ReportDataSchemaProps } from "@/schemas/data"
import { queryFnWithAuth } from "@/lib/api"
import { getRequestForSync, type BodyForMutation } from "@/lib/sync"

export default function useSyncReportMutation() {
  return useMutation({
    mutationKey: ["upSync", "report"],
    mutationFn: async (data: ReportDataSchemaProps[]) => {
      return Promise.all(
        data.map(async (body) => {
          const req = await getRequestForSync(
            body as unknown as BodyForMutation,
            "report"
          )

          if (req.method === "NONE") {
            return { [body.id]: body }
          }

          const promise = await queryFnWithAuth(req.url, {
            method: req.method,
            searchParams: { format: "gtam" },
            body: JSON.stringify(req.payload),
          }).catch((error) => error)
          return { [body.id]: promise }
        })
      )
    },
  })
}
