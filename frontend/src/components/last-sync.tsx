import * as React from "react"
import { getDurationLabel, isValidDate, SECOND } from "@/lib/date"
import { getLocale } from "@/paraglide/runtime"
import { m } from "@/paraglide/messages"

export default function LastSync({ date }: { date: string }) {
  const [dynamicDate, setDynamicDate] = React.useState(() =>
    getDurationLabel(
      new Date().getTime() - new Date(date).getTime(),
      getLocale()
    )
  )

  React.useEffect(() => {
    if (!isValidDate(date)) {
      return
    }
    const updateDateLabel = () => {
      setDynamicDate(
        getDurationLabel(
          new Date().getTime() - new Date(date).getTime(),
          getLocale()
        )
      )
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
  return (
    <p className="mt-1 font-mono text-xs italic">
      {m["common.last-synced"]({
        date: dynamicDate,
      })}
    </p>
  )
}
