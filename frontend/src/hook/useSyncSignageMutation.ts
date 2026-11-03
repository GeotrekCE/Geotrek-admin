import { useMutation } from "@tanstack/react-query"
import type { SignageDataSchemaProps } from "@/schemas/data"
import { syncEntityData, type BodyForMutation } from "@/lib/sync"

export default function useSyncSignageMutation() {
  return useMutation({
    mutationKey: ["upSync", "signage"],
    mutationFn: async (data: SignageDataSchemaProps[]) => {
      return Promise.all(
        data.map((body) =>
          syncEntityData(body as unknown as BodyForMutation, "signage")
        )
      )
    },
  })
}
