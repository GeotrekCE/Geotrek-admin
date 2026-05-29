import * as React from "react"
import { getSerwist } from "virtual:serwist"
import { onlineManager } from "@tanstack/react-query"

export function useAppInit() {
  // PWA
  React.useEffect(() => {
    const loadSerwist = async () => {
      if ("serviceWorker" in navigator) {
        const serwist = await getSerwist()

        serwist?.addEventListener("installed", () => {
          console.log("Serwist installed!")
        })

        void serwist?.register()
      }
    }

    loadSerwist()
  }, [])

  // Online/Offline status
  onlineManager.setEventListener((setOnline) => {
    const handleOnline = () => setOnline(navigator.onLine)

    window.addEventListener("online", handleOnline)
    window.addEventListener("offline", handleOnline)

    return () => {
      window.removeEventListener("online", handleOnline)
      window.removeEventListener("offline", handleOnline)
    }
  })
}
