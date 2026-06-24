import type { MapLibreEvent } from "maplibre-gl"
import { useLiveQuery } from "dexie-react-hooks"
import { Loader2 } from "lucide-react"
import MapLibre, {
  GeolocateControl,
  NavigationControl,
  type MapProps,
} from "react-map-gl/maplibre"
import "maplibre-gl/dist/maplibre-gl.css"
import { cn } from "@/lib/utils"
import { db } from "@/lib/db"

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
  const settings = useLiveQuery(() => db.settings.get("settings"))
  const classNameWrapper = "grid grow place-items-center bg-accent"
  const mapSettings = settings?.settings.maps.layers[0]

  if (!settings) {
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
        onLoad={(event: MapLibreEvent) => {
          props.onLoad?.(event)
          document
            .querySelector(".maplibregl-ctrl-attrib")
            ?.classList.remove("maplibregl-compact-show")
        }}
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
