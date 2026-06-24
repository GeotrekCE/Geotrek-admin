import * as React from "react"
import { useLiveQuery } from "dexie-react-hooks"
import { useNavigate } from "@tanstack/react-router"
import { MapPin } from "lucide-react"
import { Marker } from "react-map-gl/maplibre"
import { useList } from "@/lib/list"
import { cn } from "@/lib/utils"
import { db } from "@/lib/db"
import Map from "@/components/map"

export default function ListMap() {
  const navigate = useNavigate()
  const {
    elements: { isPending, data: elements },
    filters,
    snapPoint,
    snapPoints,
  } = useList()

  const appSync = useLiveQuery(() => db.appSync.get("data"))

  const { bounds } = appSync || {}

  const [lng1, lat1, lng2, lat2] = bounds || []

  const position = React.useMemo(() => {
    if (filters.focusOn) {
      return "16rem"
    } else if (snapPoint === snapPoints[0]) {
      return "5rem"
    } else {
      return "calc(50% - 2rem)"
    }
  }, [filters.focusOn, snapPoint, snapPoints])

  if (isPending) {
    return null
  }

  return (
    <Map
      maxBounds={
        bounds
          ? [
              [lng1, lat1],
              [lng2, lat2],
            ]
          : undefined
      }
      style={
        {
          "--ctrl-position": position,
        } as React.CSSProperties
      }
    >
      {elements
        .filter((item) => !!item?.api_geom)
        .map((item) => (
          <Marker
            key={`${item.reference}-${item.id}`}
            longitude={item.api_geom.coordinates[0]}
            latitude={item.api_geom.coordinates[1]}
            anchor="bottom"
            onClick={() => {
              navigate({
                to: ".",
                search: {
                  ...filters,
                  focusOn: { id: item.id, reference: item.reference },
                },
              })
            }}
          >
            <div className="grid items-center justify-center">
              <MapPin
                className={cn(
                  "col-start-1 row-start-1 fill-white stroke-1 [&>circle]:hidden",
                  filters.focusOn?.id === item.id &&
                    filters.focusOn?.reference === item.reference
                    ? "size-12"
                    : "size-10"
                )}
              />
              <img
                loading="lazy"
                src={item?.pictogram.url}
                alt=""
                className={cn(
                  "col-start-1 row-start-1 m-auto",
                  filters.focusOn?.id === item.id &&
                    filters.focusOn?.reference === item.reference
                    ? "size-8"
                    : "size-6"
                )}
              />
            </div>
          </Marker>
        ))}
    </Map>
  )
}
