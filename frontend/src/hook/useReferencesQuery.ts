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
import { usePermission } from "@/hook/useSettingsQuery"
import { db } from "@/lib/db"
import { toast } from "sonner"

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
  const { signage, infrastructure, intervention, report } = usePermission()
  const references = useQueries({
    queries: [
      {
        queryKey: COMMON_REFERENCES_QUERY_KEY,
        queryFn: () => {
          if (
            !infrastructure.read &&
            !signage.read &&
            !intervention.read &&
            !report.read
          ) {
            return null
          }
          const promise = queryFnWithAuth("/common/references/", {
            schema: commonReferencesSchema,
          })
          toast.promise(promise, {
            id: "sync-ref",
            loading: "Chargement",
            success: (data) => {
              console.log(data, "data")
              db.references.put({ id: "common", ...data })
              return "Références enregistrées"
            },
            error: (error) => {
              console.log(error)
              return "Erreur lors de l'ajout des références communes"
            },
            position: "top-center",
          })
          return promise
        },
        enabled: false,
      },
      {
        queryKey: INFRASTRUCTURE_REFERENCES_QUERY_KEY,
        queryFn: () => {
          if (!infrastructure.read) {
            return null
          }
          const promise = queryFnWithAuth("/infrastructure/references/", {
            schema: infrastructureReferencesSchema,
          })
          toast.promise(promise, {
            id: "sync-ref",
            loading: "Chargement",
            success: (data) => {
              console.log(data, "data")
              db.references.put({ id: "infrastructure", ...data })
              db.appSync.put({
                id: "references",
                lastSync: new Date().toISOString(),
              })
              return "Références enregistrées"
            },
            error: (error) => {
              console.log(error)
              return "Erreur lors de l'ajout des références aménagements"
            },
            position: "top-center",
          })
          return promise
        },
        enabled: false,
      },
      {
        queryKey: SIGNAGE_REFERENCES_QUERY_KEY,
        queryFn: () => {
          if (!signage.read) {
            return null
          }
          const promise = queryFnWithAuth("/signage/references/", {
            schema: signageReferencesSchema,
          })
          toast.promise(promise, {
            id: "sync-ref",
            loading: "Chargement",
            success: (data) => {
              console.log(data, "data")
              db.references.put({ id: "signage", ...data })
              db.appSync.put({
                id: "references",
                lastSync: new Date().toISOString(),
              })
              return "Références enregistrées"
            },
            error: (error) => {
              console.log(error)
              return "Erreur lors de l'ajout des références signalétiques"
            },
            position: "top-center",
          })
          return promise
        },
        enabled: false,
      },
      {
        queryKey: INTERVENTION_REFERENCES_QUERY_KEY,
        queryFn: () => {
          if (!intervention.read) {
            return null
          }
          const promise = queryFnWithAuth("/intervention/references/", {
            schema: interventionReferencesSchema,
          })
          toast.promise(promise, {
            id: "sync-ref",
            loading: "Chargement",
            success: (data) => {
              console.log(data, "data")
              db.references.put({ id: "intervention", ...data })
              db.appSync.put({
                id: "references",
                lastSync: new Date().toISOString(),
              })
              return "Références enregistrées"
            },
            error: (error) => {
              console.log(error, "error")
              return "Erreur lors de l'ajout des références signalétiques"
            },
            position: "top-center",
          })
          return promise
        },
        enabled: false,
      },
      {
        queryKey: REPORT_REFERENCES_QUERY_KEY,
        queryFn: () => {
          if (!report.read) {
            return null
          }
          const promise = queryFnWithAuth("/report/references/", {
            schema: reportReferencesSchema,
          })
          toast.promise(promise, {
            id: "sync-ref",
            loading: "Chargement",
            success: (data) => {
              console.log(data, "data")
              db.references.put({
                id: "report",
                ...data,
              })
              db.appSync.put({
                id: "references",
                lastSync: new Date().toISOString(),
              })
              return "Références enregistrées"
            },
            error: (error) => {
              console.log(error)
              return "Erreur lors de l'ajout des références signalements"
            },
            position: "top-center",
          })

          return promise
        },
        enabled: false,
      },
    ],
  })

  const refetch = React.useCallback(() => {
    references.forEach((result) => result?.refetch())
  }, [references])

  return {
    references,
    refetch,
  }
}
