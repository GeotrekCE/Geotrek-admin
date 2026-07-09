import { getBodyForMutation, queryFnWithAuth } from "@/lib/api"
import { useMutation } from "@tanstack/react-query"
import type { InterventionDataSchemaProps } from "@/schemas/data"

export default function useSyncInterventionMutation() {
  return useMutation({
    mutationKey: ["upSync", "intervention"],
    mutationFn: (data: InterventionDataSchemaProps[]) =>
      Promise.all(
        data.map(async (body) => {
          const isPOST = body.appNewItem === true
          const promise = await queryFnWithAuth(
            `/intervention/drf/interventions${!isPOST ? "/" + body.id : ""}`,
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
