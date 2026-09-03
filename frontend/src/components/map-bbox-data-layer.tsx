import { db } from "@/lib/db"
import { useLiveQuery } from "dexie-react-hooks"
import { Source, Layer } from "react-map-gl/maplibre"
import type { FeatureCollection } from "geojson"
import { m } from "@/paraglide/messages"

export default function MapBboxDataLayer() {
  const appSync = useLiveQuery(() => db.appSync.get("data"))

  const { bounds } = appSync || {}

  const [lng1, lat1, lng2, lat2] = bounds || []

  if (bounds === undefined) {
    return null
  }

  const rectangleGeoJSON: FeatureCollection = {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {},
        geometry: {
          type: "Polygon",
          coordinates: [
            [
              [lng1, lat1],
              [lng2, lat1],
              [lng2, lat2],
              [lng1, lat2],
              [lng1, lat1],
            ],
          ],
        },
      },
      {
        type: "Feature",
        properties: {},
        geometry: {
          type: "Point",
          coordinates: [lng1, lat2],
        },
      },
    ],
  }
  // TODO: use theme color
  // customProperties and oklch color are not supported in maplibre-gl
  // "#677331" === var(--primary)
  const color = "#677331"

  return (
    <Source id="my-rectangle" type="geojson" data={rectangleGeoJSON}>
      <Layer
        id="rectangle-outline"
        type="line"
        paint={{
          "line-color": color,
          "line-width": 2,
        }}
      />
      <Layer
        id="rectangle-label"
        type="symbol"
        filter={["==", "$type", "Point"]}
        layout={{
          "text-field": m["common.map-bbox"](),
          "text-size": 16,
          "text-max-width": 50,
          "text-offset": [0, -0.5],
          "text-anchor": "bottom-left",
          "text-pitch-alignment": "viewport",
          "text-rotation-alignment": "map",
        }}
        paint={{
          "text-color": color,
          "text-halo-color": "#ffffff",
          "text-halo-width": 2,
        }}
      />
    </Source>
  )
}
