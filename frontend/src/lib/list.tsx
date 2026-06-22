import * as React from "react"
import type { DataSchemaPropsMixed } from "@/schemas/data"
import { useAppSettings } from "@/hook/useAppSettings"
import type { ListSearchParams } from "../routes/{-$locale}/_authenticated/index"

const SNAP_POINTS = ["9.5rem", 0.5, 1]

export type SnapPoint = (typeof SNAP_POINTS)[number]

interface ListState {
  snapPoints: SnapPoint[]
  snapPoint: SnapPoint
  setSnapPoint: React.Dispatch<React.SetStateAction<SnapPoint>>
  elements: DataSchemaPropsMixed[]
  filters: ListSearchParams
}

const ListContext = React.createContext<ListState | undefined>(undefined)

export function ListProvider({
  elements,
  filters,
  children,
}: {
  elements: DataSchemaPropsMixed[]
  filters: ListSearchParams
  children: React.ReactNode
}) {
  const { data, setData } = useAppSettings()

  const [snapPoint, _setSnapPoint] = React.useState<SnapPoint>(
    SNAP_POINTS[data.snapPointIndex || 0]
  )

  return (
    <ListContext.Provider
      value={{
        elements,
        filters,
        snapPoints: SNAP_POINTS,
        snapPoint,
        setSnapPoint: (
          value: SnapPoint | ((value: SnapPoint) => SnapPoint)
        ) => {
          const snapState =
            typeof value === "function" ? value(snapPoint) : value
          _setSnapPoint(snapState)
          setData({
            scrollPosition: null, //TODO
            snapPointIndex: SNAP_POINTS.indexOf(snapState),
          })
        },
      }}
    >
      {children}
    </ListContext.Provider>
  )
}

export function useList() {
  const context = React.useContext(ListContext)
  if (context === undefined) {
    throw new Error("useList must be used within an ListProvider")
  }
  return context
}
