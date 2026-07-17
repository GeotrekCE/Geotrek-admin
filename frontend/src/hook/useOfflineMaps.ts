import * as React from "react"
import {
  OfflinePlugin,
  OFFLINE_STATUS,
} from "@makina-corpus/maplibre-offline-pmtiles"
import type { SettingsSchemaProps } from "@/schemas/settings"
import { useAppSettings } from "@/hook/useAppSettings"

export type MapZone =
  SettingsSchemaProps["settings"]["map"]["layers"]["offline"][0]

export type OfflineZoneMetadata = {
  id: string
  lastSync: string
}

export const OFFLINE_MAP_QUERY_KEY = ["offlinemap"]

export const offlineManager = new OfflinePlugin()

export function useOfflineMaps() {
  const { addMapLayer, removeMapLayer } = useAppSettings()

  const [loadingZoneId, setLoadingZoneId] = React.useState<string | null>(null)
  const [currentProgress, setCurrentProgress] = React.useState<number | null>(
    null
  )

  const [storageEstimate, setStorageEstimate] = React.useState<{
    used: number
    quota: number
    percent: number
  } | null>(null)
  const abortControllerRef = React.useRef<AbortController | null>(null)

  /**
   * Download a map zone and store it for offline use
   */
  async function downloadZone(zone: MapZone) {
    setLoadingZoneId(zone.name)
    setCurrentProgress(0)
    abortControllerRef.current = new AbortController()
    const id = zone.id.toString()
    try {
      // Use the library to download the map with native AbortSignal support
      await offlineManager.downloadMap(
        zone.pmtiles_url,
        id,
        (p) => {
          if (p.code === OFFLINE_STATUS.PROGRESS && p.progress !== undefined) {
            setCurrentProgress(
              typeof p.progress === "string"
                ? parseFloat(p.progress)
                : p.progress
            )
          }
        },
        zone.json_style_url,
        { signal: abortControllerRef.current?.signal }
      )

      addMapLayer(id, { ...zone, id })

      return true
    } catch (error: AbortController["signal"]["reason"]) {
      if (error.name === "AbortError" || error.message === "Aborted") {
        console.log(
          `[useOfflineMaps] Download of zone ${zone.name} was cancelled`
        )
      } else {
        console.error(
          `[useOfflineMaps] Failed to download zone ${zone.name}`,
          error
        )
        throw error
      }
    } finally {
      setLoadingZoneId(null)
      setCurrentProgress(null)
      abortControllerRef.current = null
    }
  }

  /**
   * Cancel the current download
   */
  function cancelDownload() {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }

  /**
   * Delete a downloaded map zone
   */
  async function deleteZone(zoneId: string) {
    setLoadingZoneId(zoneId)
    try {
      await offlineManager.removeMap(null, zoneId)
      removeMapLayer(zoneId)
    } catch (error) {
      console.error(`[useOfflineMaps] Failed to delete zone ${zoneId}`, error)
      throw error
    } finally {
      setLoadingZoneId(null)
    }
  }

  /**
   * Format bytes to a human-readable string
   */
  function formatSize(bytes?: number): string {
    if (bytes === undefined || bytes === null) return "?"
    if (bytes === 0) return "0 octet"
    const k = 1000
    const sizes = ["octets", "Ko", "Mo", "Go"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  return {
    loadingZoneId,
    setLoadingZoneId,
    currentProgress,
    setCurrentProgress,
    storageEstimate,
    setStorageEstimate,
    downloadZone,
    deleteZone,
    cancelDownload,
    formatSize,
    loadMap: offlineManager.loadMap,
  }
}
