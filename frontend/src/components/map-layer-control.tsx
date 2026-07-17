import * as React from "react"
import { OfflinePlugin } from "@makina-corpus/maplibre-offline-pmtiles"
import { MapGLStyleSwitcher } from "map-gl-style-switcher/react-map-gl"
import "map-gl-style-switcher/dist/map-gl-style-switcher.css"
import { useMap } from "react-map-gl/maplibre"
import { useTheme } from "@/components/theme-provider"
import { useAppSettings } from "@/hook/useAppSettings"
import useLayers from "@/hook/useLayers"

const offlineManager = new OfflinePlugin()

export default function MapLayerControl({
  position,
}: {
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right"
}) {
  const {
    data: { currentLayer },
    setData,
  } = useAppSettings()

  const layers = useLayers()

  const { theme } = useTheme()
  const [activeStyleId, setActiveStyleId] = React.useState(
    layers.find((l) => l.id === currentLayer)?.id || layers[0]?.id
  )

  const map = useMap()

  if (!layers.length || layers.length < 2) return null

  return (
    <MapGLStyleSwitcher
      styles={layers}
      activeStyleId={activeStyleId}
      theme={theme === "system" ? "auto" : theme}
      position={position ?? "top-right"}
      onBeforeStyleChange={(from, to) => {
        if (!map.current) return
        if (!from.styleUrl.startsWith("offline-pmtiles://")) {
          map.current.getMap().setStyle({
            version: 8,
            sources: {},
            layers: [],
          })
        }
        if (from.styleUrl.startsWith("offline-pmtiles://")) {
          offlineManager.unloadMap(map.current.getMap(), from.id)
        }
        if (to.styleUrl.startsWith("offline-pmtiles://")) {
          offlineManager.loadMap(map.current.getMap(), to.id)
        }
        if (!to.styleUrl.startsWith("offline-pmtiles://")) {
          map.current.getMap().setStyle(to.styleUrl)
        }
        setActiveStyleId(to.id)
        setData({ currentLayer: to.id })
      }}
      showImages={false}
    />
  )
}
