import {
  dataTagErrorSymbol,
  dataTagSymbol,
  onlineManager,
  useQuery,
  type OmitKeyof,
  type QueryFunction,
  type UseQueryOptions,
} from "@tanstack/react-query"
import { getLocale } from "@/paraglide/runtime"
import * as z from "zod"
import { db } from "@/lib/db"
import { useLiveQuery } from "dexie-react-hooks"
import { AUTH_TOKENS_KEY } from "@/hook/useTokens"

export const API_URL = "/api"
export class FetchError extends Error {
  constructor(
    public res: Response & { message?: string },
    message?: string
  ) {
    super(message)
  }
}

export async function queryFn<T extends z.ZodObject | z.ZodArray>(
  url: string,
  {
    schema,
    searchParams,
    ...options
  }: RequestInit & { schema?: T; searchParams?: Record<string, string> } = {}
) {
  const urlSearchParams = searchParams
    ? `?${new URLSearchParams(searchParams).toString()}`
    : ""
  const response = await fetch(`${API_URL}${url}${urlSearchParams}`, {
    method: "GET",
    ...options,
    headers: {
      "Accept-Language": getLocale(),
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
  })
  const json = await response.json()

  if (!response.ok) {
    throw new FetchError(
      Object.assign(response, { message: JSON.stringify(json) })
    )
  }

  const schemaData = schema
    ? schema.safeParse(json)
    : { data: json, success: true, error: null }

  if (schema && !schemaData.success) {
    console.error("Schema validation error", schemaData.error)
    throw schemaData.error
  }

  if (Array.isArray(schemaData.data)) {
    return {
      data: schemaData.data,
    }
  }

  return schemaData.data
}

export async function queryFnWithAuth<T extends z.ZodObject | z.ZodArray>(
  url: string,
  {
    schema,
    searchParams,
    ...options
  }: RequestInit & { schema?: T; searchParams?: Record<string, string> } = {}
) {
  const { access } = JSON.parse(localStorage.getItem(AUTH_TOKENS_KEY) || "{}")
  const nextOptions = {
    ...options,
    headers: {
      Authorization: `Bearer ${access}`,
      ...(options?.headers ?? {}),
    },
  }
  return await queryFn<T>(url, { schema, searchParams, ...nextOptions })
}

export function useAppQuery<T>({
  queryOptions,
}: {
  queryOptions: OmitKeyof<UseQueryOptions<T, Error, T, string[]>, "queryFn"> & {
    queryFn?: QueryFunction<T, string[], never> | undefined
  } & {
    queryKey: string[] & {
      [dataTagSymbol]: T
      [dataTagErrorSymbol]: Error
    }
  }
}) {
  const localData = useLiveQuery(() => db.settings.get("settings"))
  const enabled = onlineManager.isOnline() && queryOptions.enabled !== false
  const query = useQuery({
    ...queryOptions,
    enabled,
  })
  if (!enabled && localData) {
    return {
      data: localData,
      error: null,
      isLoading: false,
      refetch: query.refetch,
    }
  }
  return query
}

export type BodyForMutation = Record<
  string,
  | null
  | string
  | number
  | { id: string; name: string }
  | { id: string; name: string }[]
>

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
