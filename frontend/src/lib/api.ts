import {
  dataTagErrorSymbol,
  dataTagSymbol,
  onlineManager,
  useQuery,
  useQueryClient,
  type OmitKeyof,
  type QueryFunction,
  type UseQueryOptions,
} from "@tanstack/react-query"
import * as z from "zod"

export const API_URL = `${__HOST_URL__}/api`
class FetchError extends Error {
  constructor(
    public res: Response,
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
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
  })
  const json = await response.json()

  if (!response.ok) {
    throw new FetchError(response)
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
  const { access } = JSON.parse(localStorage.getItem("auth-token") || "{}")
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
  const queryClient = useQueryClient()
  const localData = queryClient.getQueryData(queryOptions.queryKey)
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
