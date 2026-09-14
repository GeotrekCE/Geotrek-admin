import { cn } from "@/lib/utils"
import { MapPin } from "lucide-react"
import { Layer, Marker, Source } from "react-map-gl/maplibre"

// TODO: use theme color
// customProperties and oklch color are not supported in maplibre-gl
// "#677331" === var(--primary)
const color = "#677331"

export default function LayerGeom({
  id,
  reference,
  geom,
  pictogram,
  isActive,
  ...props
}: {
  id?: number
  reference?: string
  geom: GeoJSON.Geometry
  pictogram?: { url?: string }
  isActive?: boolean
  onClick?: () => void
}) {
  if (geom.type === "LineString") {
    return (
      <Source type="geojson" data={geom}>
        <Layer
          id="lineString-layer"
          type="line"
          paint={{
            "line-color": color,
            "line-width": isActive ? 5 : 3,
          }}
          metadata={{
            reference,
            id,
          }}
        />
      </Source>
    )
  }

  // We display the first Point for others geom types
  const getCoordinates = (geometry: GeoJSON.Geometry): number[] => {
    if (geometry.type === "GeometryCollection") {
      return getCoordinates(geometry.geometries[0])
    }

    return geometry.coordinates.flat(Infinity) as number[]
  }

  const [longitude, latitude] = getCoordinates(geom)

  return (
    <Marker
      longitude={longitude}
      latitude={latitude}
      anchor="bottom"
      {...props}
    >
      <div className="grid items-center justify-center">
        <MapPin
          className={cn(
            "col-start-1 row-start-1 fill-white stroke-1 [&>circle]:hidden",
            isActive ? "size-12" : "size-10"
          )}
        />
        {pictogram?.url && (
          <img
            loading="lazy"
            src={pictogram?.url}
            alt=""
            className={cn(
              "col-start-1 row-start-1 m-auto",
              isActive ? "size-8" : "size-6"
            )}
          />
        )}
      </div>
    </Marker>
  )
}
