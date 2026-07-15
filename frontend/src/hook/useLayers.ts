import React from "react"
import { useAppSettings } from "./useAppSettings"
import type { StyleItem } from "map-gl-style-switcher/react-map-gl"
import { m } from "@/paraglide/messages"

export default function useLayers(): StyleItem[] {
  const {
    data: { maps },
  } = useAppSettings()

  return React.useMemo(() => {
    const defaultStyle: StyleItem = {
      id: "default",
      name: "Plan IGN",
      image: "",
      styleUrl:
        "https://data.geopf.fr/annexes/ressources/vectorTiles/styles/PLAN.IGN/standard.json",
    }
    if (!maps || !maps.layers || maps.layers.length < 1) return [defaultStyle]
    return [
      defaultStyle,
      ...maps.layers.map((layer: { id: string; name: string }) => ({
        id: layer.id,
        name: `${layer.name} (${m["common.offline"]()})`,
        styleUrl: `offline-pmtiles://${layer.id}`,
      })),
    ]
  }, [maps])
}
