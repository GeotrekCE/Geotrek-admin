import * as React from "react"
import { Layer, Source, useMap } from "react-map-gl/maplibre"
import type { Map as MapLibreMap } from "maplibre-gl"
import type { DataSchemaPropsMixed } from "@/schemas/data"
import { getFeatureCollection } from "@/lib/map"

export const MAP_ELEMENTS_LAYER_IDS = [
  "lineString-layer",
  "point-layer",
  "clusters",
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
    const urls = new Map<string, string>()

    elements.forEach((element) => {
      if (element.pictogram?.url) {
        urls.set(`pictogram-${element.reference}`, element.pictogram.url)
      }
    })

    return urls
  }, [elements])

  const loadImages = React.useCallback(
    async (map: MapLibreMap) => {
      await Promise.all(
        [...imageUrls].map(async ([id, url]) => {
          if (map.hasImage(id)) return

          const width = 40
          const height = 48
          const canvas = Object.assign(document.createElement("canvas"), {
            width,
            height,
          })
          const ctx = canvas.getContext("2d")
          if (!ctx) return

          const img = Object.assign(new Image(), {
            crossOrigin: "anonymous",
            src: url,
          })
          await img.decode()

          const centerX = width / 2
          const centerY = 18
          const radius = 15

          ctx.fillStyle = "#fff"
          ctx.beginPath()
          ctx.moveTo(centerX, height - 1)
          ctx.bezierCurveTo(18, 42, 5, 31, 5, centerY)
          ctx.arc(centerX, centerY, radius, Math.PI, 0, false)
          ctx.bezierCurveTo(35, 31, 22, 42, centerX, height - 1)
          ctx.closePath()
          ctx.fill()

          ctx.strokeStyle = "#000"
          ctx.lineWidth = 1
          ctx.stroke()

          ctx.save()
          ctx.beginPath()
          ctx.arc(centerX, centerY, radius - 1, 0, Math.PI * 2)
          ctx.clip()
          ctx.drawImage(img, 8, 10, 24, 24)
          ctx.restore()

          if (!map.hasImage(id)) {
            map.addImage(id, ctx.getImageData(0, 0, width, height))
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

      void loadImages(map)
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

  const colors = {
    theme: "#677331",
    themeLigthen: "#7c8846",
    themeDarken: "#3a4300",
  }

  return (
    <>
      <Source
        type="geojson"
        id="lines-source"
        data={
          getFeatureCollection(elements, active) as GeoJSON.FeatureCollection
        }
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
            "line-color": colors.theme,
            "line-width": ["case", ["get", "active"], 7, 5],
          }}
        />
      </Source>
      <Source
        type="geojson"
        id="points-source"
        cluster
        clusterMaxZoom={13}
        clusterRadius={50}
        data={
          getFeatureCollection(elements, active) as GeoJSON.FeatureCollection
        }
      >
        <Layer
          id="clusters"
          type="circle"
          filter={["has", "point_count"]}
          paint={{
            "circle-color": [
              "step",
              ["get", "point_count"],
              colors.themeLigthen,
              100,
              colors.theme,
              750,
              colors.themeDarken,
            ],
            "circle-radius": [
              "step",
              ["get", "point_count"],
              20,
              100,
              30,
              750,
              40,
            ],
          }}
        />

        <Layer
          id="cluster-count"
          type="symbol"
          filter={["has", "point_count"]}
          layout={{
            "text-field": "{point_count_abbreviated}",
            "text-size": 12,
          }}
        />

        <Layer
          id="point-layer"
          type="symbol"
          filter={["!=", ["geometry-type"], "LineString"]}
          layout={{
            "icon-image": ["get", "pictogram"],
            "icon-anchor": "bottom",
            "icon-size": ["case", ["get", "active"], 1.25, 1],
            "icon-allow-overlap": true,
          }}
        />
      </Source>
    </>
  )
}
