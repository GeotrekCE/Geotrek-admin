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

export function getFeatureCollection(
  data: Array<{
    id?: number
    reference?: string
    geom: GeoJSON.Geometry | null
    pictogram?: { url?: string }
  }>,
  active?: { id: number; reference: string }
) {
  return {
    type: "FeatureCollection",
    features: data.flatMap((item) => {
      if (!item.geom) {
        return []
      }

      return [
        {
          type: "Feature",
          id: `${item.reference}-${item.id || 1}`,
          geometry: item.geom,
          properties: {
            id: item.id,
            reference: item.reference || undefined,
            active:
              item.id === active?.id && item.reference === active?.reference,
            pictogram: item.pictogram?.url
              ? `pictogram-${item.reference}`
              : undefined,
          },
        },
      ]
    }),
  }
}
