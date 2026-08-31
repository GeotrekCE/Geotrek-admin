import type {
  DataSchemaPropsMixed,
  InfrastructureDataSchemaProps,
  InterventionDataSchemaProps,
  ReportDataSchemaProps,
  SignageDataSchemaProps,
} from "@/schemas/data"
import type { ListSearchParams } from "../routes/{-$locale}/_authenticated/index"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import type { EntityTable } from "dexie"
import type {
  InfrastructureReferencesSchemaProps,
  InterventionReferencesSchemaProps,
  ReportReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"

export function useStoredData({ q, type }: ListSearchParams) {
  const references = useLiveQuery(() =>
    db.references.bulkGet([
      "intervention",
      "signage",
      "report",
      "infrastructure",
    ])
  )
  const [intervention, signage, report, infrastructure] =
    (references as
      | [
          InterventionReferencesSchemaProps,
          SignageReferencesSchemaProps,
          ReportReferencesSchemaProps,
          InfrastructureReferencesSchemaProps,
        ]
      | undefined) || []

  const queries = useLiveQuery(() => {
    const results = []
    if (!type || type?.includes("signage")) {
      results.push({ collection: db.signageData, reference: signage })
    }
    if (!type || type?.includes("intervention")) {
      results.push({
        collection: db.interventionData,
        reference: intervention,
      })
    }
    if (!type || type?.includes("infrastructure")) {
      results.push({
        collection: db.infrastructureData,
        reference: infrastructure,
      })
    }
    if (!type || type?.includes("report")) {
      results.push({ collection: db.reportData, reference: report })
    }
    return Promise.all(
      results.map(
        async ({
          collection,
          reference,
        }: {
          collection: EntityTable<
            | SignageDataSchemaProps
            | InfrastructureDataSchemaProps
            | InterventionDataSchemaProps
            | ReportDataSchemaProps
          >
          reference?:
            | InterventionReferencesSchemaProps
            | SignageReferencesSchemaProps
            | ReportReferencesSchemaProps
            | InfrastructureReferencesSchemaProps
        }) => {
          if (collection.name === "reportData") {
            return collection.toArray((data) =>
              data.map((item) => ({
                ...item,
                name: `Signalement (id: ${item.id})`,
                reference: collection.name.replace("Data", ""),
                pictogram: { url: reference?.pictogram.url },
              }))
            )
          }
          if (!q) {
            return collection.toArray((data) =>
              data.map((item) => ({
                ...item,
                reference: collection.name.replace("Data", ""),
                pictogram: { url: reference?.pictogram.url },
              }))
            )
          }
          return (
            collection as EntityTable<
              | SignageDataSchemaProps
              | InfrastructureDataSchemaProps
              | InterventionDataSchemaProps
            >
          )
            .filter(
              (data) =>
                data.name.toLowerCase().includes(q.toLowerCase()) ||
                data.description.toLowerCase().includes(q.toLowerCase())
            )
            .toArray((data) =>
              data.map((item) => ({
                ...item,
                reference: collection.name.replace("Data", ""),
                pictogram: { url: reference?.pictogram.url },
              }))
            )
        }
      )
    )
  }, [references, type, q])

  if (!queries) {
    return { isPending: true, data: [] }
  }

  return {
    isPending: false,
    data: (queries as unknown as DataSchemaPropsMixed[])
      .flat()
      .sort((a, b) => b.date_update.localeCompare(a.date_update)),
  }
}

export function useStoredDataElement(type: string, id: number) {
  return useLiveQuery(async () => {
    if (type === "signage") {
      return db.signageData.get({ id })
    }
    if (type === "intervention") {
      return db.interventionData.get({ id })
    }
    if (type === "infrastructure") {
      return db.infrastructureData.get({ id })
    }
    return db.reportData.get({ id })
  }, [type, id])
}

export function useAsyncStoredData() {
  const syncData = useLiveQuery(() => db.appSync.get("data"))
  const data = useLiveQuery(async () => {
    if (!syncData) {
      return undefined
    }
    const collections = await Promise.all([
      db.signageData
        .filter(({ appSynced }) => appSynced === false)
        .reverse()
        .sortBy("date_update"),
      db.interventionData
        .filter(({ appSynced }) => appSynced === false)
        .reverse()
        .sortBy("date_update"),
      db.infrastructureData
        .filter(({ appSynced }) => appSynced === false)
        .reverse()
        .sortBy("date_update"),
      db.reportData
        .filter(({ appSynced }) => appSynced === false)
        .reverse()
        .sortBy("date_update"),
    ])
    return collections
  }, [syncData])
  return data
}
