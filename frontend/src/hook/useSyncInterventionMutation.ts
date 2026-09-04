import { useMutation } from "@tanstack/react-query"
import type { InterventionDataSchemaProps } from "@/schemas/data"
import { syncEntityData, type BodyForMutation } from "@/lib/sync"

export default function useSyncInterventionMutation() {
  return useMutation({
    mutationKey: ["upSync", "intervention"],
    mutationFn: async (data: InterventionDataSchemaProps[]) => {
      return Promise.all(
        data.map((body) =>
          syncEntityData(body as unknown as BodyForMutation, "intervention")
        )
      )
    },
  })
}
