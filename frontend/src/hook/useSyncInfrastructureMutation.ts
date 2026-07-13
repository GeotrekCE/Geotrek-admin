import {
  getBodyForMutation,
  queryFnWithAuth,
  type BodyForMutation,
} from "@/lib/api"
import { useMutation } from "@tanstack/react-query"
import type { InfrastructureDataSchemaProps } from "@/schemas/data"

export default function useSyncInfrastructureMutation() {
  return useMutation({
    mutationKey: ["upSync", "infrastructures"],
    mutationFn: (data: InfrastructureDataSchemaProps[]) =>
      Promise.all(
        data.map(async (body) => {
          const isPOST = body.appNewItem === true
          const promise = await queryFnWithAuth(
            `/infrastructure/drf/infrastructures${!isPOST ? "/" + body.id : ""}`,
            {
              method: isPOST ? "POST" : "PATCH",
              searchParams: { format: "gtam" },
              body: JSON.stringify(
                getBodyForMutation(body as unknown as BodyForMutation)
              ),
            }
          ).catch((error) => error)
          return { [body.id]: promise }
        })
      ),
  })
}
