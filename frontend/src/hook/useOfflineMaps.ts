import * as React from "react"
import {
  OfflinePlugin,
  OFFLINE_STATUS,
} from "@makina-corpus/maplibre-offline-pmtiles"
import type { SettingsSchemaProps } from "@/schemas/settings"
// import { storageManager } from "@/lib/storage"

export type MapZone = SettingsSchemaProps["settings"]["maps"]["layers"][0]

export interface OfflineZoneMetadata {
  id: string
  lastSync: string
  size?: number
}

export const offlineManager = new OfflinePlugin()

export function useOfflineMaps() {
  const mapZonesData: MapZone[] = []
  const [downloadedZonesMetadata, setDownloadedZonesMetadata] = React.useState<
    Record<string, OfflineZoneMetadata>
  >({})
  const [loadingZoneId, setLoadingZoneId] = React.useState<string | null>(null)
  const [currentProgress, setCurrentProgress] = React.useState<number | null>(
    null
  )
  const [mapZones, setMapZones] = React.useState<MapZone[]>(
    mapZonesData as MapZone[]
  )
  const [storageEstimate, setStorageEstimate] = React.useState<{
    used: number
    quota: number
    percent: number
  } | null>(null)
  const abortControllerRef = React.useRef<AbortController | null>(null)

  /**
   * Load metadata of already downloaded zones from local storage
   */
  async function loadMetadata() {
    // const metadata = await storageManager.adapter.get<
    //   Record<string, OfflineZoneMetadata>
    // >("offline_map_zones_metadata")
    // setDownloadedZonesMetadata(metadata || {})
  }

  /**
   * Save current metadata to local storage
   */
  async function saveMetadata() {
    // await storageManager.adapter.set(
    //   "offline_map_zones_metadata",
    //   downloadedZonesMetadata
    // )
  }

  /**
   * Update storage usage estimate
   */
  async function loadStorageEstimate() {
    setStorageEstimate(await offlineManager.getStorageUsage())
  }

  /**
   * Get the size of a remote file using a HEAD request
   */
  async function getRemoteSize(url: string): Promise<number | null> {
    try {
      const response = await fetch(url, {
        method: "HEAD",
        headers: {
          "Content-Type": "application/json",
        },
      })
      const size = response.headers.get("content-length")
      return size ? parseInt(size, 10) : null
    } catch (error) {
      console.warn(
        `[useOfflineMaps] Could not fetch remote size for ${url}`,
        error
      )
      return null
    }
  }

  /**
   * Download a map zone and store it for offline use
   */
  async function downloadZone(zone: MapZone) {
    setLoadingZoneId(zone.name)
    setCurrentProgress(0)
    abortControllerRef.current = new AbortController()
    try {
      // Get remote size for metadata if possible
      const size = await getRemoteSize(zone.pmtiles_url)

      // Use the library to download the map with native AbortSignal support
      await offlineManager.downloadMap(
        zone.pmtiles_url,
        zone.name,
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

      // Update local metadata
      setDownloadedZonesMetadata((prev) => ({
        ...prev,
        [zone.name]: {
          id: zone.name,
          lastSync: new Date().toISOString(),
          size: size || undefined,
        },
      }))
      await saveMetadata()
      await loadStorageEstimate()
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
      await saveMetadata()
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
    if (bytes === 0) return "0 B"
    const k = 1024
    const sizes = ["B", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  React.useEffect(() => {
    const init = async () => {
      await Promise.all([loadMetadata(), loadStorageEstimate()])
    }
    init()
  }, [])

  return {
    mapZones,
    setMapZones,
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
    loadMetadata,
    formatSize,
    getRemoteSize,
    loadStorageEstimate,
  }
}
