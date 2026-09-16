import * as React from "react"
import { Layer, Source, useMap } from "react-map-gl/maplibre"
import type { Map as MapLibreMap } from "maplibre-gl"
import type { DataSchemaPropsMixed } from "@/schemas/data"
import { getFeatureCollection } from "@/lib/map"

const PIN_IMAGE = "pin-image"
const pinImageUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="white" stroke="currentColor" stroke-width="0.6"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path></svg>
`)}`

export const MAP_ELEMENTS_LAYER_IDS = [
  "lineString-layer",
  "point-layer",
] as const

type MapElementsLayerProps = {
  elements: (Pick<DataSchemaPropsMixed, "geom" | "pictogram" | "reference"> & {
    id?: number
  })[]
  active?: { id: number; reference: string }
}

export default function MapElementsLayer({
  elements,
  active,
}: MapElementsLayerProps) {
  const { current: mapRef } = useMap()

  const imageUrls = React.useMemo(() => {
    const urls = new globalThis.Map<string, string>([[PIN_IMAGE, pinImageUrl]])

    elements.forEach((element) => {
      if (element.pictogram?.url) {
        urls.set(`pictogram-${element.reference}`, element.pictogram.url)
      }
    })

    return urls
  }, [elements])

  const loadImages = React.useCallback(
    async (map: MapLibreMap) => {
      if (!map.hasImage(PIN_IMAGE)) {
        const image = new Image()
        const promise = new Promise<void>((resolve) => {
          image.onload = () => resolve()
        })
        image.src = pinImageUrl
        await promise
        if (!map.hasImage(PIN_IMAGE)) {
          map.addImage(PIN_IMAGE, image)
        }
      }

      await Promise.all(
        [...imageUrls].map(async ([id, url]) => {
          if (!map.hasImage(id)) {
            const { data } = await map.loadImage(url)
            if (!map.hasImage(id)) {
              map.addImage(id, data)
            }
          }
        })
      )
    },
    [imageUrls]
  )

  React.useEffect(() => {
    const map = mapRef?.getMap()
    if (!map) return

    const onStyleImageMissing = ({ id }: { id: string }) => {
      const url = imageUrls.get(id)
      if (!url || map.hasImage(id)) return

      void map.loadImage(url).then(({ data }) => {
        if (!map.hasImage(id)) {
          map.addImage(id, data)
        }
      })
    }

    map.on("styleimagemissing", onStyleImageMissing)
    map.once("styledata", () => void loadImages(map))
    if (map.isStyleLoaded()) {
      void loadImages(map)
    }

    return () => {
      map.off("styleimagemissing", onStyleImageMissing)
    }
  }, [imageUrls, loadImages, mapRef])

  return (
    <Source
      type="geojson"
      data={getFeatureCollection(elements, active) as GeoJSON.FeatureCollection}
    >
      <Layer
        id="lineString-layer"
        filter={["==", ["geometry-type"], "LineString"]}
        type="line"
        layout={{
          "line-join": "round",
          "line-cap": "round",
        }}
        paint={{
          "line-color": "#677331",
          "line-width": ["case", ["get", "active"], 7, 5],
        }}
      />
      <Layer
        id="point-layer"
        type="symbol"
        filter={["!=", ["geometry-type"], "LineString"]}
        layout={{
          "icon-image": PIN_IMAGE,
          "icon-anchor": "bottom",
          "icon-size": ["case", ["get", "active"], 1.25, 1],
          "icon-allow-overlap": true,
        }}
      />
      <Layer
        id="point-pictogram-layer"
        type="symbol"
        filter={["!=", ["geometry-type"], "LineString"]}
        layout={{
          "icon-image": ["get", "pictogram"],
          "icon-anchor": "bottom",
          "icon-size": ["case", ["get", "active"], 0.6, 0.5],
          "icon-allow-overlap": true,
          "icon-offset": [0, -16],
        }}
      />
    </Source>
  )
}
