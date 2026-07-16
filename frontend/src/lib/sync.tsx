import { db } from "@/lib/db"

export type BodyForMutation = Record<
  string,
  | null
  | string
  | number
  | { id: string; name: string }
  | { id: string; name: string }[]
>

const endpointMap: Record<string, string> = {
  signage: "/signage/drf/signages",
  intervention: "/intervention/drf/interventions",
  infrastructure: "/infrastructure/drf/infrastructures",
  report: "/report/drf/reports",
}

export type SyncRequestResult =
  | { method: "POST"; url: string; payload: unknown }
  | { method: "PATCH"; url: string; payload: unknown }
  | { method: "NONE" }

export async function getRequestForSync(
  body: BodyForMutation & { id?: number; appNewItem?: boolean },
  reference: string
): Promise<SyncRequestResult> {
  const endpoint = endpointMap[reference]
  if (!endpoint) {
    return { method: "NONE" }
  }

  const isPOST = body.appNewItem === true
  if (isPOST) {
    return {
      method: "POST",
      url: endpoint,
      payload: getBodyForMutation(body as unknown as BodyForMutation),
    }
  }

  // For PATCH: only send changed keys compared to rawData
  const rawBody = await db.rawData.get({
    reference,
    id: body.id,
  })

  const data = Object.fromEntries(
    Object.entries(body).filter(([key, value]) => {
      const rawValue = (rawBody as Record<string, unknown>)[key]
      try {
        return JSON.stringify(rawValue) !== JSON.stringify(value)
      } catch {
        return rawValue !== value
      }
    })
  )

  if (Object.keys(data).length === 0) {
    return { method: "NONE" }
  }

  return {
    method: "PATCH",
    url: `${endpoint}/${body.id}`,
    payload: getBodyForMutation(data as unknown as BodyForMutation),
  }
}

export function getBodyForMutation(
  body: BodyForMutation
): Record<
  string,
  null | string | number | string[] | number[] | { id: string; name: string }[]
> {
  return Object.fromEntries(
    Object.entries(body)
      .map(([key, value]) => {
        if (
          [
            "id",
            "date_insert",
            "date_update",
            "appSynced",
            "appNewItem",
          ].includes(key) ||
          value === null
        ) {
          return null
        }
        if (Array.isArray(value)) {
          // This API is a mess for POST/PATCH
          if (["blades", "man_day"].includes(key)) {
            return [key, value.map((item) => getBodyForMutation(item))]
          }
          return [`${key}_id`, value.map((item) => item.id)]
        }
        if (typeof value === "object" && "id" in value) {
          return [`${key}_id`, value.id]
        }
        return [key, value]
      })
      .filter((item) => item !== null)
  )
}
