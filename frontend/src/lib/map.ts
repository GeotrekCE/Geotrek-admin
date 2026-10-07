import type { LngLatBounds } from "maplibre-gl"

export function getPolygonFromBounds(
  bounds: LngLatBounds | [number, number, number, number]
) {
  const [x0, y0, x1, y1] = Array.isArray(bounds)
    ? bounds.flat()
    : bounds.toArray().flat()
  return `POLYGON((${x0.toFixed(5)} ${y0.toFixed(5)},${x1.toFixed(5)} ${y0.toFixed(5)},${x1.toFixed(5)} ${y1.toFixed(5)},${x0.toFixed(5)} ${y1.toFixed(5)}, ${x0.toFixed(5)} ${y0.toFixed(5)}))`
}

export function getBoundsFromPolygon(polygon: string) {
  const [sw, _, ne] = polygon.replace("POLYGON((", "").split(",")
  if (!sw && !ne) {
    return []
  }
  return [sw.split(" "), ne.split(" ")].flat().map(Number) as [
    number,
    number,
    number,
    number,
  ]
}

function getFirstPosition(
  geometry: GeoJSON.Geometry
): GeoJSON.Position | undefined {
  if (geometry.type === "GeometryCollection") {
    for (const child of geometry.geometries) {
      const position = getFirstPosition(child)
      if (position) return position
    }
    return undefined
  }

  let coordinates: unknown = geometry.coordinates
  while (
    Array.isArray(coordinates) &&
    !coordinates.every((coordinate) => typeof coordinate === "number")
  ) {
    coordinates = coordinates[0]
  }

  if (
    !Array.isArray(coordinates) ||
    typeof coordinates[0] !== "number" ||
    typeof coordinates[1] !== "number"
  ) {
    return undefined
  }

  return [coordinates[0], coordinates[1]]
}

export function getFeatureCollection(
  data: Array<{
    id?: number
    reference?: string
    geom: GeoJSON.Geometry | null
    pictogram?: { url?: string }
  }>,
  pointNonPointGeometries = false
) {
  return {
    type: "FeatureCollection",
    features: data.flatMap((item) => {
      if (!item.geom) {
        return []
      }

      let geometry = item.geom
      if (pointNonPointGeometries && geometry.type !== "Point") {
        const coordinates = getFirstPosition(geometry)
        if (!coordinates) return []
        geometry = { type: "Point", coordinates }
      }

      return [
        {
          type: "Feature",
          id: `${item.reference}-${item.id || 1}`,
          geometry,
          properties: {
            id: item.id,
            reference: item.reference || undefined,
            pictogram: item.pictogram?.url
              ? `pictogram-${item.reference}`
              : undefined,
          },
        },
      ]
    }),
  }
}
