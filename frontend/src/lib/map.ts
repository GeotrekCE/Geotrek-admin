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
  return [sw.split(" "), ne.split(" ")].flat().map(Number) as [
    number,
    number,
    number,
    number,
  ]
}
