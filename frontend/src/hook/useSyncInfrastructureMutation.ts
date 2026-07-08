import { getBodyForMutation, queryFnWithAuth } from "@/lib/api"
import { useMutation } from "@tanstack/react-query"
import type { InfrastructureDataSchemaProps } from "@/schemas/data"

export default function useSyncInfrastructureMutation() {
  return useMutation({
    mutationKey: ["upSync", "infrastructures"],
    mutationFn: (data: InfrastructureDataSchemaProps[]) =>
      Promise.all(
        data.map((body) => {
          const isPOST = body.appNewItem === true
          return queryFnWithAuth(
            `/infrastructure/drf/infrastructures${!isPOST ? "/" + body.id : ""}`,
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
