import * as React from "react"
import { getDurationLabel, isValidDate, SECOND } from "@/lib/date"
import { getLocale } from "@/paraglide/runtime"

export default function LastSync({ date }: { date: string }) {
  const [dynamicDate, setDate] = React.useState(
    getDurationLabel(
      new Date().getTime() - new Date(date).getTime(),
      getLocale()
    )
  )

  React.useEffect(() => {
    if (!isValidDate(date)) {
      return
    }
    const id = setInterval(() => {
      setDate(
        getDurationLabel(
          new Date().getTime() - new Date(date).getTime(),
          getLocale()
        )
      )
    }, 1 * SECOND)
    return () => {
      clearInterval(id)
    }
  }, [date])

  if (!isValidDate(date) && !dynamicDate) {
    return null
  }
  return (
    <p className="mt-1 font-mono text-xs italic">
      Dernière synchronisation il y a {dynamicDate}
    </p>
  )
}
