import MapLibre, {
  GeolocateControl,
  NavigationControl,
  type MapProps,
} from "react-map-gl/maplibre"
import { useSettingsQueryOfflineFirst } from "@/hook/useSettingsQuery"
import "maplibre-gl/dist/maplibre-gl.css"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

export default function Map({
  className,
  style,
  children,
  noControls = false,
  ...props
}: MapProps & {
  className?: string
  style?: React.CSSProperties
  noControls?: boolean
}) {
  const { data, isLoading } = useSettingsQueryOfflineFirst()

  const classNameWrapper = "grid grow place-items-center bg-accent"
  const mapSettings = data?.settings?.maps.layers[0]

  if (isLoading) {
    return (
      <div className={classNameWrapper}>
        <Loader2 className="size-4 animate-spin" />
      </div>
    )
  }
  if (!mapSettings) {
    return null
  }

  return (
    <div
      className={cn(classNameWrapper, className)}
      style={
        style ||
        ({
          "--ctrl-position": 0,
        } as React.CSSProperties)
      }
    >
      <MapLibre
        initialViewState={{ ...mapSettings.options, ...props.initialViewState }}
        mapStyle="https://tiles.openfreemap.org/styles/liberty"
        scrollZoom={!noControls}
        touchPitch={!noControls}
        dragPan={!noControls}
        {...props}
      >
        {!noControls && (
          <>
            <GeolocateControl position="bottom-right" />
            <NavigationControl position="bottom-right" />
          </>
        )}
        {children}
      </MapLibre>
    </div>
  )
}
