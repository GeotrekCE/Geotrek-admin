import * as React from "react"
import { onlineManager } from "@tanstack/react-query"

export default function useOnline() {
  const isOnline = onlineManager.isOnline()
  const [online, setOnline] = React.useState(isOnline)

  React.useEffect(() => {
    const unsubscribe = onlineManager.subscribe(setOnline)
    return () => unsubscribe()
  }, [])

  return online
}
