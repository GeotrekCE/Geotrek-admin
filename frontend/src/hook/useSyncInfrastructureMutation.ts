import { useMutation } from "@tanstack/react-query"
import type { InfrastructureDataSchemaProps } from "@/schemas/data"
import { syncEntityData, type BodyForMutation } from "@/lib/sync"

export default function useSyncInfrastructureMutation() {
  return useMutation({
    mutationKey: ["upSync", "infrastructures"],
    mutationFn: async (data: InfrastructureDataSchemaProps[]) => {
      return Promise.all(
        data.map((body) =>
          syncEntityData(body as unknown as BodyForMutation, "infrastructure")
        )
      )
    },
  })
}
