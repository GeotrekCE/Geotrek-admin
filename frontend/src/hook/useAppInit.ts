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
    const check = async () => {
      try {
        await fetch(`${import.meta.env.DEV ? "/" : "/offline/"}ping`, {
          cache: "no-store",
          method: "HEAD",
        })
        setOnline(true)
      } catch {
        setOnline(false)
      }
    }

    window.addEventListener("online", check)
    window.addEventListener("offline", () => setOnline(false))

    const interval = setInterval(check, 30000)
    check()

    return () => {
      window.removeEventListener("online", check)
      window.removeEventListener("offline", () => setOnline(false))
      clearInterval(interval)
    }
  })
}
