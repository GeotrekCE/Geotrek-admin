import * as React from "react"
import { useQueries, type UseQueryResult } from "@tanstack/react-query"
import { queryFnWithAuth } from "@/lib/api"
import {
  infrastructureDataSchema,
  interventionDataSchema,
  reportDataSchema,
  signageDataSchema,
  type InfrastructureDataSchemaProps,
  type InterventionDataSchemaProps,
  type ReportDataSchemaProps,
  type SignageDataSchemaProps,
} from "@/schemas/data"
import { useSettingsQueryOfflineFirst } from "@/hook/useSettingsQuery"

export const INFRASTRUCTURE_DATA_QUERY_KEY = ["data", "infrastructure"]
export const SIGNAGE_DATA_QUERY_KEY = ["data", "signage"]
export const INTERVENTION_DATA_QUERY_KEY = ["data", "intervention"]
export const REPORT_DATA_QUERY_KEY = ["data", "report"]

export type StoredData = {
  data: {
    infrastructure: UseQueryResult<{ data: InfrastructureDataSchemaProps }>
    signage: UseQueryResult<{ data: SignageDataSchemaProps }>
    intervention: UseQueryResult<{ data: InterventionDataSchemaProps }>
    report: UseQueryResult<{ data: ReportDataSchemaProps }>
  }
}

export function useDataQuery(
  params: { structure?: number; bbox?: string } = {}
) {
  const cleanParams = Object.fromEntries(
    Object.entries(params).filter(([_, value]) => !!value)
  )
  const settings = useSettingsQueryOfflineFirst()
  const {
    signage = {},
    infrastructure = {},
    intervention = {},
    report = {},
  } = settings?.data?.user.permissions || {}
  const results = useQueries({
    queries: [
      {
        queryKey: INFRASTRUCTURE_DATA_QUERY_KEY,
        queryFn: () =>
          infrastructure.read
            ? queryFnWithAuth("/infrastructure/drf/infrastructures", {
                schema: infrastructureDataSchema,
                searchParams: { format: "gtam", ...cleanParams },
              })
            : () => null,
        enabled: false,
      },
      {
        queryKey: SIGNAGE_DATA_QUERY_KEY,
        queryFn: () =>
          signage.read
            ? queryFnWithAuth("/signage/drf/signages", {
                schema: signageDataSchema,
                searchParams: { format: "gtam", ...cleanParams },
              })
            : () => null,
        enabled: false,
      },
      {
        queryKey: INTERVENTION_DATA_QUERY_KEY,
        queryFn: () =>
          intervention.read
            ? queryFnWithAuth("/intervention/drf/interventions", {
                schema: interventionDataSchema,
                searchParams: { format: "gtam", ...cleanParams },
              })
            : () => null,
        enabled: false,
      },
      {
        queryKey: REPORT_DATA_QUERY_KEY,
        queryFn: () =>
          report.read
            ? queryFnWithAuth("/report/drf/reports", {
                schema: reportDataSchema,
                searchParams: { format: "gtam", ...cleanParams },
              })
            : () => null,
        enabled: false,
      },
    ],
  })

  const refetch = React.useCallback(() => {
    results.forEach((result) => result?.refetch())
  }, [results])

  return {
    data: {
      infrastructure: results[0],
      signage: results[1],
      intervention: results[2],
      report: results[3],
    },
    refetch,
  }
}
