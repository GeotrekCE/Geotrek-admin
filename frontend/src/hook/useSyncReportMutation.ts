import { useMutation } from "@tanstack/react-query"
import type { ReportDataSchemaProps } from "@/schemas/data"
import { syncEntityData, type BodyForMutation } from "@/lib/sync"

export default function useSyncReportMutation() {
  return useMutation({
    mutationKey: ["upSync", "report"],
    mutationFn: async (data: ReportDataSchemaProps[]) => {
      return Promise.all(
        data.map((body) =>
          syncEntityData(body as unknown as BodyForMutation, "report")
        )
      )
    },
  })
}
