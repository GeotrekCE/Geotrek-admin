import { Marker } from "react-map-gl/maplibre"
import Map from "@/components/map"
import { Alert, AlertTitle } from "@/components/ui/alert"
import { m } from "@/paraglide/messages"
import MapBboxDataLayer from "./map-bbox-data-layer"
import { MapPin } from "lucide-react"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"

export default function DetailMap({
  geom,
  pictogram,
}: {
  geom: GeoJSON.Geometry
  pictogram?: { url: string }
}) {
  const appSync = useLiveQuery(() => db.appSync.get("data"))

  const { bounds } = appSync || {}

  const [lng1, lat1, lng2, lat2] = bounds || []

  return (
    <>
      <Map
        className="pointer-none aspect-square touch-none"
        initialViewState={{
          bounds: bounds
            ? [
                [lng1, lat1],
                [lng2, lat2],
              ]
            : undefined,
        }}
      >
        <MapBboxDataLayer />
        {geom.type === "Point" && (
          <Marker
            longitude={geom.coordinates[0]}
            latitude={geom.coordinates[1]}
            anchor="bottom"
          >
            <div className="grid items-center justify-center">
              <MapPin className="col-start-1 row-start-1 size-10 fill-white stroke-1 [&>circle]:hidden" />
              {pictogram && (
                <img
                  loading="lazy"
                  src={pictogram.url}
                  className="col-start-1 row-start-1 m-auto size-6"
                  alt=""
                />
              )}
            </div>
          </Marker>
        )}
      </Map>
      {geom.type !== "Point" && (
        <Alert className="mt-4" variant="warning">
          <AlertTitle>{m["form.geom-linear-not-supported"]()}</AlertTitle>
        </Alert>
      )}
    </>
  )
}
