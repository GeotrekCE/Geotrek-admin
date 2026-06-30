import * as React from "react"
import {
  OfflinePlugin,
  OFFLINE_STATUS,
} from "@makina-corpus/maplibre-offline-pmtiles"
import type { SettingsSchemaProps } from "@/schemas/settings"
import { useQueryClient } from "@tanstack/react-query"

export type MapZone = SettingsSchemaProps["settings"]["maps"]["layers"][0]

export interface OfflineZoneMetadata {
  id: string
  lastSync: string
}

export const OFFLINE_MAP_QUERY_KEY = ["offlinemap"]
export const offlineManager = new OfflinePlugin()

export function useOfflineMaps() {
  const queryClient = useQueryClient()
  // const mapZonesData: MapZone[] = []
  const metadata = queryClient.getQueryData<
    Record<string, OfflineZoneMetadata>
  >(OFFLINE_MAP_QUERY_KEY)
  const [downloadedZonesMetadata, setDownloadedZonesMetadata] = React.useState<
    Record<string, OfflineZoneMetadata>
  >(metadata ?? ({} as Record<string, OfflineZoneMetadata>))
  const [loadingZoneId, setLoadingZoneId] = React.useState<string | null>(null)
  const [currentProgress, setCurrentProgress] = React.useState<number | null>(
    null
  )
  // const [mapZones, setMapZones] = React.useState<MapZone[]>(
  //   mapZonesData as MapZone[]
  // )
  const [storageEstimate, setStorageEstimate] = React.useState<{
    used: number
    quota: number
    percent: number
  } | null>(null)
  const abortControllerRef = React.useRef<AbortController | null>(null)

  /**
   * Update storage usage estimate
   */
  async function loadStorageEstimate() {
    setStorageEstimate(await offlineManager.getStorageUsage())
  }

  /**
   * Download a map zone and store it for offline use
   */
  async function downloadZone(zone: MapZone) {
    setLoadingZoneId(zone.name)
    setCurrentProgress(0)
    abortControllerRef.current = new AbortController()
    try {
      // Use the library to download the map with native AbortSignal support
      await offlineManager.downloadMap(
        zone.pmtiles_url,
        zone.name.replaceAll(" ", "-"),
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

      queryClient.setQueryData(
        OFFLINE_MAP_QUERY_KEY,
        (prevData: Record<string, OfflineZoneMetadata> = {}) => ({
          ...prevData,
          [zone.name.replaceAll(" ", "-")]: {
            id: zone.name.replaceAll(" ", "-"),
            lastSync: new Date().toISOString(),
          },
        })
      )
      // await saveMetadata()
      await loadStorageEstimate()
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
      // Library removeMap takes (mapInstance, name, onProgress)
      // We don't have a map instance here, we just want to clear storage
      await offlineManager.removeMap(null, zoneId)
      setDownloadedZonesMetadata((prev) => {
        const newMetadata = { ...prev }
        delete newMetadata[zoneId]
        return newMetadata
      })
      // await saveMetadata()
      await loadStorageEstimate()
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
    mapZones: metadata,
    // setMapZones,
    downloadedZonesMetadata,
    setDownloadedZonesMetadata,
    loadingZoneId,
    setLoadingZoneId,
    currentProgress,
    setCurrentProgress,
    storageEstimate,
    setStorageEstimate,
    downloadZone,
    deleteZone,
    cancelDownload,
    // loadMetadata,
    formatSize,
    loadStorageEstimate,
    loadMap: offlineManager.loadMap,
  }
}
