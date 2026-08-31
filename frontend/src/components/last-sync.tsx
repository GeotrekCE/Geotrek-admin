import * as React from "react"
import { getDurationLabel, isValidDate, SECOND } from "@/lib/date"

export default function LastSync({ date }: { date: string }) {
  const [dynamicDate, setDynamicDate] = React.useState(() =>
    getDurationLabel(date, "sync")
  )

  React.useEffect(() => {
    const updateDateLabel = () => {
      setDynamicDate(getDurationLabel(date, "sync"))
    }
    updateDateLabel()
    const id = setInterval(updateDateLabel, 60 * SECOND)
    return () => {
      clearInterval(id)
    }
  }, [date])

  if (!isValidDate(date) && !dynamicDate) {
    return null
  }
  return <p className="mt-1 font-mono text-xs italic">{dynamicDate}</p>
}
