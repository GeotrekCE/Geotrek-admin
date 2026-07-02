import maplibregl, { type MapLibreEvent } from "maplibre-gl"
import { useLiveQuery } from "dexie-react-hooks"
import { Loader2 } from "lucide-react"
import { OfflinePlugin } from "@makina-corpus/maplibre-offline-pmtiles"
import MapLibre, {
  GeolocateControl,
  NavigationControl,
  type MapProps,
} from "react-map-gl/maplibre"
import "maplibre-gl/dist/maplibre-gl.css"
import { cn } from "@/lib/utils"
import { db } from "@/lib/db"
import { useAppSettings } from "@/hook/useAppSettings"
import useLayers from "@/hook/useLayers"
import LayerControl from "@/components/map-layer-control"

OfflinePlugin.registerProtocol(maplibregl)

const offlineManager = new OfflinePlugin()

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

  const layers = useLayers()

  const {
    data: { currentLayer },
  } = useAppSettings()

  const currentLayerSettings =
    layers.find((l) => l.id === currentLayer) || layers[0]

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
        {...props}
        initialViewState={{ ...mapSettings.options, ...props.initialViewState }}
        scrollZoom={!noControls}
        touchPitch={!noControls}
        dragPan={!noControls}
        onLoad={(event: MapLibreEvent) => {
          props.onLoad?.(event)
          document
            .querySelector(".maplibregl-ctrl-attrib")
            ?.classList.remove("maplibregl-compact-show")
          if (currentLayerSettings.styleUrl.startsWith("offline-pmtiles://")) {
            offlineManager.loadMap(event.target, currentLayerSettings.id)
          } else {
            event.target.setStyle(currentLayerSettings.styleUrl)
          }
        }}
      >
        <LayerControl position="bottom-left" />
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
