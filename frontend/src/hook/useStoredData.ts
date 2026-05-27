import { useAppSettings } from "@/hook/useAppSettings"
import { useDataQuery, type StoredData } from "@/hook/useDataQuery"
import { getPolygonFromBounds } from "@/lib/map"
import * as React from "react"
import { useReferencesQuery, type StoredReferences } from "./useReferencesQuery"
import type { DataSchemaPropsMixed } from "@/schemas/data"
import type { ListSearchParams } from "../routes/_authenticated/index"

function getElements(
  elements: StoredData,
  { references }: StoredReferences
): DataSchemaPropsMixed[] {
  const { common: _common, ...referencesMap } = references

  return Object.entries(elements.data)
    .map(([key, value]) =>
      (value.data?.data || []).filter(Boolean).map((item) => {
        const name = "name" in item ? item.name : undefined
        const element = {
          reference: key,
          name:
            name || key === "report"
              ? `Signalement (id: ${item.id})`
              : "Données sans nom",
          pictogram: {
            url: referencesMap[key as keyof typeof referencesMap]?.data
              ?.pictogram.url,
          },
          ...item,
        }
        return element as DataSchemaPropsMixed
      })
    )
    .flat()
}

export function useStoredData(filters: ListSearchParams) {
  const { data } = useAppSettings()
  const { q, type } = filters

  const { bounds, structure } = data?.syncData || {}
  const allReferences = useReferencesQuery()
  const allData = useDataQuery({
    bbox: bounds
      ? getPolygonFromBounds(bounds as [number, number, number, number])
      : undefined,
    structure: structure ?? undefined,
  })

  let result = React.useMemo(
    () => getElements(allData, allReferences),
    [allData, allReferences]
  )
  if (allData === undefined) {
    // Todo
    return allData
  }

  if (q) {
    result = result.filter(
      (item) =>
        item.name?.toLowerCase().includes(q.toLowerCase()) ||
        ("description" in item &&
          item.description?.toLowerCase().includes(q.toLowerCase()))
    )
  }

  if (type && type.length > 0) {
    result = result.filter((item) =>
      type.includes(item.reference as (typeof type)[number])
    )
  }

  // Sort by UPDATE_DATE DESC
  return result.sort((a, b) => b.date_update.localeCompare(a.date_update))
}

export function useStoredDataElement(type: string, id: number) {
  const { data } = useAppSettings()

  const { bounds, structure } = data?.syncData || {}
  const allReferences = useReferencesQuery()
  const allData = useDataQuery({
    bbox: bounds
      ? getPolygonFromBounds(bounds as [number, number, number, number])
      : undefined,
    structure: structure ?? undefined,
  })

  const result = React.useMemo(() => {
    const elements = getElements(allData, allReferences)
    return elements.find(
      (item) => item.reference === type && item.id === id
    ) as DataSchemaPropsMixed | undefined
  }, [allData, allReferences, type, id])

  return result
}
