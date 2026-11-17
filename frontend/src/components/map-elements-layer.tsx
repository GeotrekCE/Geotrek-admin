import * as React from "react"
import { Layer, Source, useMap } from "react-map-gl/maplibre"
import type {
  Map as MapLibreMap,
  PropertyValueSpecification,
} from "maplibre-gl"
import type { DataSchemaPropsMixed } from "@/schemas/data"
import { getFeatureCollection } from "@/lib/map"

type MapElementFocus = {
  id: number
  reference: "infrastructure" | "intervention" | "signage" | "report"
}

type MapPointProperties = {
  id?: number
  reference?: string
  pictogram?: string
  members?: MapElementFocus[]
  isActive?: boolean
  [key: string]: unknown
}

type MapPointFeature = GeoJSON.Feature<GeoJSON.Point, MapPointProperties>

export const MAP_ELEMENTS_LAYER_IDS = [
  "lineString-layer",
  "point-layer",
  "clusters",
] as const

type MapElementsLayerProps = {
  elements: (Pick<DataSchemaPropsMixed, "geom" | "pictogram" | "reference"> & {
    id?: number
  })[]
  active?: MapElementFocus | MapElementFocus[]
}

function drawPin(ctx: CanvasRenderingContext2D) {
  const centerX = 20
  const centerY = 18
  const radius = 15

  ctx.fillStyle = "#fff"
  ctx.beginPath()
  ctx.moveTo(centerX, 47)
  ctx.bezierCurveTo(18, 42, 5, 31, 5, centerY)
  ctx.arc(centerX, centerY, radius, Math.PI, 0, false)
  ctx.bezierCurveTo(35, 31, 22, 42, centerX, 47)
  ctx.closePath()
  ctx.fill()

  ctx.strokeStyle = "#000"
  ctx.lineWidth = 1
  ctx.stroke()
}

export default function MapElementsLayer({
  elements,
  active,
}: MapElementsLayerProps) {
  const { current: mapRef } = useMap()
  const activeElements = React.useMemo(
    () => (Array.isArray(active) ? active : active ? [active] : []),
    [active]
  )
  const activeExpression: PropertyValueSpecification<boolean> = [
    "in",
    ["concat", ["get", "reference"], "-", ["to-string", ["get", "id"]]],
    [
      "literal",
      activeElements.map(({ id, reference }) => `${reference}-${id}`),
    ],
  ] as const

  const points = React.useMemo(
    () =>
      (
        getFeatureCollection(elements, true) as GeoJSON.FeatureCollection<
          GeoJSON.Point,
          MapPointProperties
        >
      ).features,
    [elements]
  )

  const [pointData, setPointData] = React.useState<
    GeoJSON.FeatureCollection<GeoJSON.Point, MapPointProperties>
  >(() => ({ type: "FeatureCollection", features: points }))

  React.useEffect(() => {
    const map = mapRef?.getMap()
    if (!map) return

    const updatePointData = () => {
      if (map.getZoom() < 14) {
        setPointData({
          type: "FeatureCollection",
          features: points.map((feature) => ({
            ...feature,
            properties: {
              ...feature.properties,
              isActive: activeElements.some(
                (element) =>
                  element.id === feature.properties.id &&
                  element.reference === feature.properties.reference
              ),
            },
          })),
        })
        return
      }

      const positions = points.map((feature) =>
        map.project(feature.geometry.coordinates as [number, number])
      )
      const parents = points.map((_, index) => index)
      const find = (index: number): number => {
        if (parents[index] !== index) {
          parents[index] = find(parents[index])
        }
        return parents[index]
      }
      const join = (first: number, second: number) => {
        parents[find(second)] = find(first)
      }
      const cells = new Map<string, number[]>()

      for (let index = 0; index < points.length; index += 1) {
        const point = points[index]
        if (
          typeof point.properties.id !== "number" ||
          !point.properties.reference
        ) {
          continue
        }

        const { x, y } = positions[index]
        const cellX = Math.floor(x / 40)
        const cellY = Math.floor(y / 48)
        const key = `${cellX}:${cellY}`
        const sameCell = cells.get(key)
        if (sameCell?.length) {
          join(index, sameCell[0])
        }

        for (let dx = -1; dx <= 1; dx += 1) {
          for (let dy = -1; dy <= 1; dy += 1) {
            if (dx === 0 && dy === 0) continue
            const nearby = cells.get(`${cellX + dx}:${cellY + dy}`)
            if (!nearby) continue

            for (const candidate of nearby) {
              if (
                Math.abs(x - positions[candidate].x) < 40 &&
                Math.abs(y - positions[candidate].y) < 48
              ) {
                join(index, candidate)
                break
              }
            }
          }
        }

        if (sameCell) {
          sameCell.push(index)
        } else {
          cells.set(key, [index])
        }
      }

      const groupedPoints = new Map<number, MapPointFeature[]>()
      points.forEach((feature, index) => {
        const groupId =
          typeof feature.properties.id === "number" &&
          feature.properties.reference
            ? find(index)
            : index
        const group = groupedPoints.get(groupId) ?? []
        group.push(feature)
        groupedPoints.set(groupId, group)
      })

      const features = [...groupedPoints.values()].map((group) => {
        const feature = group[0]
        if (group.length === 1) {
          return {
            ...feature,
            properties: {
              ...feature.properties,
              isActive: activeElements.some(
                (element) =>
                  element.id === feature.properties.id &&
                  element.reference === feature.properties.reference
              ),
            },
          }
        }

        const members = group.map((member) => ({
          id: member.properties.id as number,
          reference: member.properties
            .reference as MapElementFocus["reference"],
        }))

        return {
          ...feature,
          properties: {
            ...feature.properties,
            pictogram: `overlap-count-${members.length}`,
            members,
            isActive: members.some((member) =>
              activeElements.some(
                (element) =>
                  element.id === member.id &&
                  element.reference === member.reference
              )
            ),
          },
        }
      })

      setPointData({ type: "FeatureCollection", features })
    }

    updatePointData()
    map.on("moveend", updatePointData)
    map.on("resize", updatePointData)

    return () => {
      map.off("moveend", updatePointData)
      map.off("resize", updatePointData)
    }
  }, [activeElements, mapRef, points])

  const overlapCounts = React.useMemo(
    () =>
      pointData.features.flatMap((feature) =>
        feature.properties.members ? [feature.properties.members.length] : []
      ),
    [pointData]
  )

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

          drawPin(ctx)

          ctx.save()
          ctx.beginPath()
          ctx.arc(width / 2, 18, 14, 0, Math.PI * 2)
          ctx.clip()
          ctx.drawImage(img, 8, 10, 24, 24)
          ctx.restore()

          if (!map.hasImage(id)) {
            map.addImage(id, ctx.getImageData(0, 0, width, height))
          }
        })
      )

      for (const count of overlapCounts) {
        const id = `overlap-count-${count}`
        if (map.hasImage(id)) continue

        const canvas = Object.assign(document.createElement("canvas"), {
          width: 40,
          height: 48,
        })
        const ctx = canvas.getContext("2d")
        if (!ctx) continue

        drawPin(ctx)
        ctx.fillStyle = "#000"
        ctx.font = `${count > 9 ? 10 : 12}px sans-serif`
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"
        ctx.fillText(String(count), 20, 22)
        map.addImage(id, ctx.getImageData(0, 0, canvas.width, canvas.height))
      }
    },
    [imageUrls, overlapCounts]
  )

  React.useEffect(() => {
    const map = mapRef?.getMap()
    if (!map) return

    const onStyleImageMissing = ({ id }: { id: string }) => {
      const url = imageUrls.get(id)
      if ((!url && !id.startsWith("overlap-count-")) || map.hasImage(id)) {
        return
      }

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
        data={getFeatureCollection(elements) as GeoJSON.FeatureCollection}
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
            "line-width": ["case", activeExpression, 7, 5],
          }}
        />
      </Source>
      <Source
        type="geojson"
        id="points-source"
        cluster
        clusterMaxZoom={13}
        clusterRadius={50}
        data={pointData}
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
          paint={{
            "text-color": "#fff",
          }}
        />

        <Layer
          id="point-layer"
          type="symbol"
          layout={{
            "icon-image": ["get", "pictogram"],
            "icon-anchor": "bottom",
            "icon-size": ["case", ["==", ["get", "isActive"], true], 1.25, 1],
            "icon-allow-overlap": true,
          }}
        />
      </Source>
    </>
  )
}
