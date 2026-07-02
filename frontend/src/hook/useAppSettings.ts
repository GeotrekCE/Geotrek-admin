const APP_SETTINGS_KEY = "gtam-app-settings"

function getStorageElement(key: string) {
  return JSON.parse(localStorage.getItem(key) || "{}")
}

export function useAppSettings() {
  function setData(nextData: Record<string, unknown>) {
    localStorage.setItem(
      APP_SETTINGS_KEY,
      JSON.stringify({
        ...getStorageElement(APP_SETTINGS_KEY),
        ...nextData,
      })
    )
  }

  function addMapLayer(key: string, mapData: Record<string, unknown>) {
    const data = getStorageElement(APP_SETTINGS_KEY)
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
        maps: {
          ...data.maps,
          layers: updatedLayers,
          lastSync: new Date().toISOString(),
        },
      })
    } else {
      setData({
        maps: {
          layers: [{ ...mapData, id: key }],
          lastSync: new Date().toISOString(),
        },
      })
    }
  }

  function removeMapLayer(key: string) {
    const data = getStorageElement(APP_SETTINGS_KEY)
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
    data: getStorageElement(APP_SETTINGS_KEY),
    setData,
    removeMapLayer,
    addMapLayer,
  }
}
