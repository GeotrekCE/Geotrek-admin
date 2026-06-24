import * as React from "react"
import * as z from "zod"
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
import { usePermission } from "@/hook/useSettingsQuery"
import { db } from "@/lib/db"
import { toast } from "sonner"
import { getBoundsFromPolygon } from "@/lib/map"

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
  params: {
    structure?: number
    bbox?: string
  } = {}
) {
  const bounds = getBoundsFromPolygon(params.bbox || "")

  const cleanParams = Object.fromEntries(
    Object.entries(params).filter(([_, value]) => !!value)
  )
  const { signage, infrastructure, intervention, report } = usePermission()
  const results = useQueries({
    queries: [
      {
        queryKey: INFRASTRUCTURE_DATA_QUERY_KEY,
        queryFn: () => {
          if (!infrastructure.read) {
            return null
          }
          const promise = queryFnWithAuth(
            "/infrastructure/drf/infrastructures",
            {
              schema: z.array(infrastructureDataSchema),
              searchParams: { format: "gtam", ...cleanParams },
            }
          )

          toast.promise(promise, {
            id: "sync-data",
            loading: "Chargement",
            success: (data) => {
              db.infrastructureData.clear()
              data.data.map((item: InfrastructureDataSchemaProps) =>
                db.infrastructureData.put(item)
              )
              db.appSync.put({
                id: "data",
                lastSync: new Date().toISOString(),
                bounds,
                structure: params.structure || null,
              })
              return "Données embarquées dans l'application"
            },
            error: (error) => {
              console.log(error)
              return "Erreur lors de l'ajout des données aménagements"
            },
            position: "top-center",
          })

          return promise
        },
        enabled: false,
      },
      {
        queryKey: SIGNAGE_DATA_QUERY_KEY,
        queryFn: () => {
          if (!signage.read) {
            return null
          }
          const promise = queryFnWithAuth("/signage/drf/signages", {
            schema: z.array(signageDataSchema),
            searchParams: { format: "gtam", ...cleanParams },
          })

          toast.promise(promise, {
            id: "sync-data",
            loading: "Chargement",
            success: (data) => {
              db.signageData.clear()
              data.data.map((item: SignageDataSchemaProps) =>
                db.signageData.put(item)
              )
              db.appSync.put({
                id: "data",
                lastSync: new Date().toISOString(),
                bounds,
                structure: params.structure || null,
              })
              return "Données embarquées dans l'application"
            },
            error: (error) => {
              console.log(error)
              return "Erreur lors de l'ajout des données signalétiques"
            },
            position: "top-center",
          })
          return promise
        },
        enabled: false,
      },
      {
        queryKey: INTERVENTION_DATA_QUERY_KEY,
        queryFn: () => {
          if (!intervention.read) {
            return null
          }
          const promise = queryFnWithAuth("/intervention/drf/interventions", {
            schema: z.array(interventionDataSchema),
            searchParams: { format: "gtam", ...cleanParams },
          })
          toast.promise(promise, {
            id: "sync-data",
            loading: "Chargement",
            success: (data) => {
              db.interventionData.clear()
              data.data.map((item: InterventionDataSchemaProps) =>
                db.interventionData.put(item)
              )
              db.appSync.put({
                id: "data",
                lastSync: new Date().toISOString(),
                bounds,
                structure: params.structure || null,
              })
              return "Données embarquées dans l'application"
            },
            error: (error) => {
              console.log(error)
              return "Erreur lors de l'ajout des données intervention"
            },
            position: "top-center",
          })
          return promise
        },
        enabled: false,
      },
      {
        queryKey: REPORT_DATA_QUERY_KEY,
        queryFn: () => {
          if (!report.read) {
            return null
          }
          const promise = queryFnWithAuth("/report/drf/reports", {
            schema: z.array(reportDataSchema),
            searchParams: { format: "gtam", ...cleanParams },
          })
          toast.promise(promise, {
            id: "sync-data",
            loading: "Chargement",
            success: (data) => {
              db.reportData.clear()
              data.data.map((item: ReportDataSchemaProps) =>
                db.reportData.put(item)
              )
              db.appSync.put({
                id: "data",
                lastSync: new Date().toISOString(),
                bounds,
                structure: params.structure || null,
              })
              return "Données embarquées dans l'application"
            },
            error: (error) => {
              console.log(error)
              return "Erreur lors de l'ajout des données signalement"
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
    results.forEach((result) => result?.refetch())
  }, [results])
  return {
    data: results,
    refetch,
  }
}
