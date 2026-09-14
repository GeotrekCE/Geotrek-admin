import Map from "@/components/map"
import { Alert, AlertTitle } from "@/components/ui/alert"
import { m } from "@/paraglide/messages"
import MapBboxDataLayer from "./map-bbox-data-layer"
import LayerGeom from "@/components/layer-geom"
import useBounds from "@/hook/useBounds"

export default function DetailMap({
  geom,
  pictogram,
}: {
  geom: GeoJSON.Geometry
  pictogram?: { url: string }
}) {
  const bounds = useBounds(geom)

  return (
    <>
      <Map
        className="pointer-none aspect-square touch-none"
        initialViewState={{
          bounds: bounds && geom.type !== "Point" ? bounds : undefined,
          longitude: geom.type === "Point" ? geom.coordinates[0] : undefined,
          latitude: geom.type === "Point" ? geom.coordinates[1] : undefined,
          zoom: 12,
        }}
      >
        <MapBboxDataLayer />
        <LayerGeom geom={geom} pictogram={pictogram} />
      </Map>
      {geom.type !== "Point" && (
        <Alert className="mt-4" variant="warning">
          <AlertTitle>{m["form.geom-linear-not-supported"]()}</AlertTitle>
        </Alert>
      )}
    </>
  )
}
