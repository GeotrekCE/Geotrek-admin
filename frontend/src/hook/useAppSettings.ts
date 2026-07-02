const APP_SETTINGS_KEY = "appSettings"

function getStorageElement(key: string) {
  return JSON.parse(localStorage.getItem(key) || "{}")
}

export function useAppSettings() {
  const data = getStorageElement(APP_SETTINGS_KEY)

  function setData(nextData: Record<string, string | null | number>) {
    localStorage.setItem(
      APP_SETTINGS_KEY,
      JSON.stringify({
        ...getStorageElement(APP_SETTINGS_KEY),
        ...nextData,
      })
    )
  }

  function addMapLayer(key: string, mapData: Record<string, unknown>) {
    if (data.maps && data.maps.layers) {
      let updatedLayers = []
      if (data.maps.layers.some((layer: { id: string }) => layer.id === key)) {
        updatedLayers = data.maps.layers.map((layer: { id: string }) =>
          layer.id === key ? { ...layer, ...mapData } : layer
        )
      } else {
        updatedLayers = [...data.maps.layers, { ...mapData, id: key }]
      }
      setData({
        maps: { ...data.maps, layers: updatedLayers },
      })
    }
  }

  function removeMapLayer(key: string) {
    if (data.maps && data.maps.layers) {
      setData({
        maps: {
          ...data.maps,
          layers: data.maps.layers.filter(
            (layer: { id: string }) => layer.id !== key
          ),
        },
      })
    }
  }

  return {
    data,
    setData,
    removeMapLayer,
    addMapLayer,
  }
}
