import { db } from "@/lib/db"
import { useLiveQuery } from "dexie-react-hooks"
import maplibregl, { type LngLatLike } from "maplibre-gl"

export default function useBounds(geom?: GeoJSON.Geometry) {
  const appSync = useLiveQuery(() => db.appSync.get("data"))
  const defaultBounds = appSync?.bounds

  if (!defaultBounds || geom?.type === "Point") {
    return undefined
  }

  if (
    !geom ||
    geom.type === "MultiLineString" ||
    geom.type === "MultiPolygon" ||
    geom.type === "MultiPoint" ||
    geom.type === "GeometryCollection"
  ) {
    const [lng1, lat1, lng2, lat2] = defaultBounds
    return new maplibregl.LngLatBounds([lng1, lat1, lng2, lat2])
  }

  const coordinates = geom.coordinates
  const bounds = coordinates.reduce(
    (bounds, coord) => {
      return bounds.extend(coord as [LngLatLike, LngLatLike])
    },
    new maplibregl.LngLatBounds(
      coordinates[0] as [LngLatLike, LngLatLike],
      coordinates[0] as [number, number]
    )
  )
  return bounds
}
