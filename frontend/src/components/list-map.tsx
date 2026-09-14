import * as React from "react"
import { useNavigate } from "@tanstack/react-router"
import type { MapLayerMouseEvent } from "react-map-gl/maplibre"
import { useList } from "@/lib/list"
import Map from "@/components/map"
import MapBboxDataLayer from "./map-bbox-data-layer"
import useBounds from "@/hook/useBounds"
import LayerGeom from "./layer-geom"

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

  const onClick = React.useCallback(
    (event: MapLayerMouseEvent) => {
      const feature = event.features && event.features[0]
      const metadata = feature?.layer.metadata

      if (
        metadata &&
        typeof metadata === "object" &&
        "id" in metadata &&
        "reference" in metadata &&
        typeof metadata.id === "number" &&
        typeof metadata.reference === "string"
      ) {
        const reference = metadata.reference as
          | "infrastructure"
          | "intervention"
          | "signage"
          | "report"

        navigate({
          to: ".",
          search: {
            ...filters,
            focusOn: {
              id: metadata.id,
              reference,
            },
          },
        })
      }
    },
    [filters, navigate]
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
      interactiveLayerIds={["lineString-layer"]}
      onClick={onClick}
      cursor={cursor}
      padding={{ top: 30, right: 10, bottom: 130, left: 10 }}
    >
      <MapBboxDataLayer />
      {elements.map((item) => {
        if (!item.geom) {
          return null
        }
        return (
          <LayerGeom
            key={`${item.reference}-${item.id}`}
            id={item.id}
            reference={item.reference}
            geom={item.geom}
            pictogram={item.pictogram}
            isActive={
              filters.focusOn?.id === item.id &&
              filters.focusOn?.reference === item.reference
            }
            onClick={() => {
              navigate({
                to: ".",
                search: {
                  ...filters,
                  focusOn: { id: item.id, reference: item.reference },
                },
              })
            }}
          />
        )
      })}
    </Map>
  )
}
