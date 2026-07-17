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
    if (data.map && data.map.layers) {
      let updatedLayers = []
      if (data.map.layers.some((layer: { id: string }) => layer.id === key)) {
        updatedLayers = data.map.layers.map((layer: { id: string }) =>
          layer.id === key ? { ...layer, ...mapData } : layer
        )
      } else {
        updatedLayers = [...data.map.layers, { ...mapData, id: key }]
      }
      setData({
        map: {
          ...data.map,
          layers: updatedLayers,
          lastSync: new Date().toISOString(),
        },
      })
    } else {
      setData({
        map: {
          layers: [{ ...mapData, id: key }],
          lastSync: new Date().toISOString(),
        },
      })
    }
  }

  function removeMapLayer(key: string) {
    const data = getStorageElement(APP_SETTINGS_KEY)
    if (data.map && data.map.layers) {
      setData({
        map: {
          ...data.map,
          layers: data.map.layers.filter(
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
