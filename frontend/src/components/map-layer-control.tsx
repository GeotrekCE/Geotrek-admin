import * as React from "react"
import { OfflinePlugin } from "@makina-corpus/maplibre-offline-pmtiles"
import { MapGLStyleSwitcher } from "map-gl-style-switcher/react-map-gl"
import "map-gl-style-switcher/dist/map-gl-style-switcher.css"
import { useMap } from "react-map-gl/maplibre"
import { useTheme } from "@/components/theme-provider"
import { useAppSettings } from "@/hook/useAppSettings"
import useLayers from "@/hook/useLayers"
import { moveOfflineLayersBelowOtherLayers } from "@/lib/map"

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
      onBeforeStyleChange={async (from, to) => {
        if (!map.current) return

        const mapInstance = map.current.getMap()

        if (!from.styleUrl.startsWith("offline-pmtiles://")) {
          mapInstance.setStyle({
            version: 8,
            sources: {},
            layers: [],
          })
        }
        if (from.styleUrl.startsWith("offline-pmtiles://")) {
          offlineManager.toggleMap(mapInstance, from.id, false)
        }
        if (to.styleUrl.startsWith("offline-pmtiles://")) {
          const isLoaded = Boolean(mapInstance.getSource(`${to.id}-source`))
          if (isLoaded) {
            offlineManager.toggleMap(mapInstance, to.id, true)
          } else {
            await offlineManager.loadMap(mapInstance, to.id)
          }
          const offlineMapIds = layers
            .filter((layer) => layer.styleUrl.startsWith("offline-pmtiles://"))
            .map((layer) => layer.id)
          moveOfflineLayersBelowOtherLayers(mapInstance, offlineMapIds)
        }
        if (!to.styleUrl.startsWith("offline-pmtiles://")) {
          mapInstance.setStyle(to.styleUrl)
        }
        setActiveStyleId(to.id)
        setData({ currentLayer: to.id })
      }}
      showImages={false}
    />
  )
}
