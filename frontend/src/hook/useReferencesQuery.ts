import * as React from "react"
import { useQueries, type UseQueryResult } from "@tanstack/react-query"
import { queryFnWithAuth } from "@/lib/api"
import {
  commonReferencesSchema,
  infrastructureReferencesSchema,
  interventionReferencesSchema,
  reportReferencesSchema,
  signageReferencesSchema,
  type CommonReferencesSchemaProps,
  type InfrastructureReferencesSchemaProps,
  type InterventionReferencesSchemaProps,
  type ReportReferencesSchemaProps,
  type SignageReferencesSchemaProps,
} from "@/schemas/references"
import { useSettingsQueryOfflineFirst } from "@/hook/useSettingsQuery"

export type StoredReferences = {
  references: {
    common: UseQueryResult<CommonReferencesSchemaProps>
    infrastructure: UseQueryResult<InfrastructureReferencesSchemaProps>
    signage: UseQueryResult<SignageReferencesSchemaProps>
    intervention: UseQueryResult<InterventionReferencesSchemaProps>
    report: UseQueryResult<ReportReferencesSchemaProps>
  }
}

export const COMMON_REFERENCES_QUERY_KEY = ["references", "common"]
export const INFRASTRUCTURE_REFERENCES_QUERY_KEY = [
  "references",
  "infrastructure",
]
export const SIGNAGE_REFERENCES_QUERY_KEY = ["references", "signage"]
export const INTERVENTION_REFERENCES_QUERY_KEY = ["references", "intervention"]
export const REPORT_REFERENCES_QUERY_KEY = ["references", "report"]

export function useReferencesQuery() {
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
        queryKey: COMMON_REFERENCES_QUERY_KEY,
        queryFn: () =>
          infrastructure.read ||
          signage.read ||
          intervention.read ||
          report.read
            ? queryFnWithAuth("/common/references/", {
                schema: commonReferencesSchema,
              })
            : () => null,
        enabled: false,
      },
      {
        queryKey: INFRASTRUCTURE_REFERENCES_QUERY_KEY,
        queryFn: () =>
          infrastructure.read
            ? queryFnWithAuth("/infrastructure/references/", {
                schema: infrastructureReferencesSchema,
              })
            : () => null,
        enabled: false,
      },
      {
        queryKey: SIGNAGE_REFERENCES_QUERY_KEY,
        queryFn: () =>
          signage.read
            ? queryFnWithAuth("/signage/references/", {
                schema: signageReferencesSchema,
              })
            : () => null,
        enabled: false,
      },
      {
        queryKey: INTERVENTION_REFERENCES_QUERY_KEY,
        queryFn: () =>
          intervention.read
            ? queryFnWithAuth("/intervention/references/", {
                schema: interventionReferencesSchema,
              })
            : () => null,
        enabled: false,
      },
      {
        queryKey: REPORT_REFERENCES_QUERY_KEY,
        queryFn: () =>
          report.read
            ? queryFnWithAuth("/report/references/", {
                schema: reportReferencesSchema,
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
    references: {
      common: results[0],
      infrastructure: results[1],
      signage: results[2],
      intervention: results[3],
      report: results[4],
    },
    refetch,
  }
}
