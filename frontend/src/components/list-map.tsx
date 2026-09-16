import * as React from "react"
import { useNavigate } from "@tanstack/react-router"

import { type MapLayerMouseEvent } from "react-map-gl/maplibre"
import { useList } from "@/lib/list"
import Map from "@/components/map"
import MapBboxDataLayer from "./map-bbox-data-layer"
import MapElementsLayer, { MAP_ELEMENTS_LAYER_IDS } from "./map-elements-layer"
import useBounds from "@/hook/useBounds"

export default function ListMap() {
  const navigate = useNavigate()
  const {
    elements: { isPending, data: elements },
    filters,
    snapPoint,
    snapPoints,
  } = useList()

  const bounds = useBounds()

  const position = React.useMemo(() => {
    if (filters.focusOn) {
      return "16rem"
    } else if (snapPoint === snapPoints[0]) {
      return "5rem"
    } else {
      return "calc(50% - 2rem)"
    }
  }, [filters.focusOn, snapPoint, snapPoints])

  const [cursor, setCursor] = React.useState<string>("auto")

  const handleClick = React.useCallback(
    (
      id: number,
      reference: "infrastructure" | "intervention" | "signage" | "report"
    ) => {
      navigate({
        to: ".",
        search: {
          ...filters,
          focusOn: {
            id,
            reference,
          },
        },
      })
    },
    [filters, navigate]
  )

  const onClick = React.useCallback(
    (event: MapLayerMouseEvent) => {
      const feature = event.features && event.features[0]
      const properties = feature?.properties

      if (properties) {
        const reference = properties.reference as
          | "infrastructure"
          | "intervention"
          | "signage"
          | "report"

        handleClick(properties.id, reference)
      }
    },
    [handleClick]
  )

  const onMouseEnter = React.useCallback(() => setCursor("pointer"), [])
  const onMouseLeave = React.useCallback(() => setCursor("auto"), [])

  if (isPending) {
    return null
  }

  return (
    <Map
      initialViewState={{
        bounds: bounds || undefined,
      }}
      style={
        {
          "--ctrl-position": position,
        } as React.CSSProperties
      }
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      interactiveLayerIds={[...MAP_ELEMENTS_LAYER_IDS]}
      onClick={onClick}
      cursor={cursor}
      padding={{ top: 30, right: 10, bottom: 130, left: 10 }}
    >
      <MapBboxDataLayer />
      <MapElementsLayer elements={elements} active={filters.focusOn} />
    </Map>
  )
}
