import React from "react"
import { useAppSettings } from "./useAppSettings"
import type { StyleItem } from "map-gl-style-switcher/react-map-gl"
import { m } from "@/paraglide/messages"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"

export default function useLayers(): StyleItem[] {
  const {
    data: { map },
  } = useAppSettings()

  const settings = useLiveQuery(() => db.settings.get("settings"))

  return React.useMemo(() => {
    const onLineLayers = settings?.settings.map.layers.online.base_layers || []
    const defaultLayers = onLineLayers.map((layer) => ({
      id: layer.slug,
      name: layer.name,
      image: "",
      styleUrl: layer.url,
    }))

    if (defaultLayers.length === 0) {
      defaultLayers.push({
        id: "default-no-map",
        name: "Plan IGN",
        image: "",
        styleUrl:
          "https://data.geopf.fr/annexes/ressources/vectorTiles/styles/PLAN.IGN/standard.json",
      })
    }

    if (!map || !map.layers || map.layers.length < 1) return defaultLayers
    return [
      ...defaultLayers,
      ...map.layers.map((layer: { id: string; name: string }) => ({
        id: layer.id,
        name: `${layer.name} (${m["common.offline"]()})`,
        styleUrl: `offline-pmtiles://${layer.id}`,
      })),
    ]
  }, [map, settings?.settings.map.layers.online.base_layers])
}
