import { db } from "@/lib/db"
import { useLiveQuery } from "dexie-react-hooks"
import { Source, Layer } from "react-map-gl/maplibre"
import type { FeatureCollection } from "geojson"
import { m } from "@/paraglide/messages"

export default function MapBboxDataLayer() {
  const appSync = useLiveQuery(() => db.appSync.get("data"))

  const { bounds } = appSync || {}

  if (bounds === undefined) {
    return null
  }

  const [lng1, lat1, lng2, lat2] = bounds

  const worldCoordinates = [
    [-180, -85.051129],
    [180, -85.051129],
    [180, 85.051129],
    [-180, 85.051129],
    [-180, -85.051129],
  ]

  const dataCoordinates = [
    [lng1, lat1],
    [lng2, lat1],
    [lng2, lat2],
    [lng1, lat2],
    [lng1, lat1],
  ]

  const outsideGeoJSON: FeatureCollection = {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {},
        geometry: {
          type: "Polygon",
          coordinates: [worldCoordinates, dataCoordinates],
        },
      },
    ],
  }

  const rectangleGeoJSON: FeatureCollection = {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {},
        geometry: {
          type: "Polygon",
          coordinates: [dataCoordinates],
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

  const color = "#777"

  return (
    <>
      <Source type="geojson" data={outsideGeoJSON}>
        <Layer
          id="rectangle-outside-fill"
          type="fill"
          paint={{
            "fill-color": "#000",
            "fill-opacity": 0.2,
          }}
        />
      </Source>
      <Source type="geojson" data={rectangleGeoJSON}>
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
    </>
  )
}
