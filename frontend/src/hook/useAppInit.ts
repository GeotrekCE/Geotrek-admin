import * as React from "react"
import { getSerwist } from "virtual:serwist"
import { onlineManager } from "@tanstack/react-query"

export function useAppInit() {
  // Service worker
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
  React.useEffect(() => {
    onlineManager.setEventListener((setOnline) => {
      const handleOnline = () => {
        const ping = async () => {
          try {
            await fetch(`${import.meta.env.BASE_URL}ping`, {
              cache: "no-store",
              method: "HEAD",
            })
            setOnline(true)
          } catch {
            setOnline(false)
          }
        }
        ping()
      }

      handleOnline()

      window.addEventListener("online", handleOnline)
      window.addEventListener("offline", handleOnline)

      return () => {
        window.removeEventListener("online", handleOnline)
        window.removeEventListener("offline", handleOnline)
      }
    })
  }, [])
}
