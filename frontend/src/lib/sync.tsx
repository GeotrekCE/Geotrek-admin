import { db } from "@/lib/db"
import { FetchError, queryFnWithAuth } from "@/lib/api"
import type { AttachmentsSchemaProps } from "@/schemas/attachments"
import { m } from "@/paraglide/messages"

export type BodyForMutation = Record<
  string,
  | null
  | string
  | number
  | { id: string; name: string }
  | { id: string; name: string }[]
  | { value: File | null }[]
>

export type SyncReference =
  | "signage"
  | "intervention"
  | "infrastructure"
  | "report"

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

  const rawBody = await db.rawData
    .where("reference")
    .equals(reference)
    .and((item) => item.id === body.id)
    .first()

  const data =
    rawBody === undefined
      ? body
      : Object.fromEntries(
          Object.entries(body).filter(([key, value]) => {
            const rawValue = (rawBody as Record<string, unknown>)[key]
            try {
              return JSON.stringify(rawValue) !== JSON.stringify(value)
            } catch {
              return rawValue !== value
            }
          })
        )

  const payload = getBodyForMutation(data as unknown as BodyForMutation)
  if (Object.keys(payload).length === 0) {
    return { method: "NONE" }
  }

  return {
    method: "PATCH",
    url: `${endpoint}/${body.id}`,
    payload,
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
            "attachments",
          ].includes(key) ||
          value === null
        ) {
          return null
        }
        if (Array.isArray(value)) {
          // This API is a mess for POST/PATCH
          if (["blades", "man_day"].includes(key)) {
            return [
              key,
              value.map((item) =>
                getBodyForMutation(item as unknown as BodyForMutation)
              ),
            ]
          }
          return [
            `${key}_id`,
            value.map((item) => (item as unknown as BodyForMutation).id),
          ]
        }
        if (typeof value === "object" && "id" in value) {
          return [`${key}_id`, value.id]
        }
        return [key, value]
      })
      .filter((item) => item !== null)
  )
}

async function syncAttachment(
  reference: SyncReference,
  id: number,
  file?: File | null
) {
  if (!(file instanceof File)) {
    return null
  }

  const formData = new FormData()
  formData.append("attachment_file", file)

  try {
    await queryFnWithAuth(`${endpointMap[reference]}/${id}/add-attachment`, {
      method: "POST",
      body: formData,
    })
    return null
  } catch (error) {
    return error instanceof FetchError && error.res.message
      ? `${JSON.parse(error.res.message)?.attachment_file}: ${file.name}`
      : m[`common.sync-up-error-attachment`]({ filename: file.name })
  }
}

async function syncAttachments(
  reference: SyncReference,
  id: number,
  attachments?: AttachmentsSchemaProps["attachments"]
) {
  const attachmentErrors: string[] = []
  const failedAttachments: { value: File | null }[] = []

  for (const attachment of attachments ?? []) {
    const error = await syncAttachment(reference, id, attachment?.value)
    if (error) {
      attachmentErrors.push(error)
      failedAttachments.push({ value: attachment?.value ?? null })
    }
  }

  return { attachmentErrors, failedAttachments }
}

export async function syncEntityData<
  T extends BodyForMutation & AttachmentsSchemaProps & { id?: number },
>(body: T, reference: SyncReference) {
  const attachments = body.attachments
  const req = await getRequestForSync(body, reference)

  if (req.method === "NONE") {
    if (body.id == null || !attachments?.length) {
      return
    }

    const result = await syncAttachments(reference, body.id, attachments)
    return {
      [body.id]: {
        ...body,
        ...result,
      },
    }
  }

  const response = await queryFnWithAuth(req.url, {
    method: req.method,
    searchParams: { format: "gtam" },
    body: JSON.stringify(req.payload),
  }).catch((error) => error)

  if (response instanceof FetchError) {
    return { [String(body.id)]: response }
  }

  const serverResponse = response as { id?: number }
  if (serverResponse.id == null || !attachments?.length) {
    return { [String(body.id)]: response }
  }

  const result = await syncAttachments(
    reference,
    serverResponse.id,
    attachments
  )

  return {
    [String(body.id)]: {
      ...serverResponse,
      ...result,
    },
  }
}
