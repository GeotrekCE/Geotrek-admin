export const SECOND = 1000
export const MINUTE = 60 * SECOND
export const HOUR = 60 * MINUTE
export const DAY = 24 * HOUR
export const WEEK = 7 * DAY
export const MONTH = 4 * WEEK /* TODO: Better calculation */
export const YEAR = MONTH * 12

export function isValidDate(date: string) {
  return date && !Number.isNaN(new Date(date).getDate())
}

function isOutDated(date: string, timeInMS: number) {
  if (!isValidDate(date)) {
    return true
  }
  return new Date().getTime() - new Date(date).getTime() > timeInMS
}

export function dateCompare(firsDate: string, secondDate?: string) {
  if (!secondDate || !isValidDate(secondDate)) {
    return -Infinity
  }
  return new Date(firsDate).getTime() - new Date(secondDate).getTime()
}

export function getUpdatedStatus(date: string | undefined, timeInMS: number) {
  if (!date || !isValidDate(date)) {
    return "EXPIRED"
  }
  if (isOutDated(date, timeInMS / 2)) {
    return "WARNING"
  }
  if (isOutDated(date, timeInMS)) {
    return "EXPIRED"
  }
  return "UPDATED"
}

export function getDurationLabel(timeInMs: number, locale: string) {
  let diff = timeInMs

  const durationFormatter = new Intl.DurationFormat(locale, {
    style: "narrow",
  })

  const result = {
    years: 0,
    months: 0,
    weeks: 0,
    days: 0,
    hours: 0,
    minutes: 0,
  }

  if (diff >= YEAR) {
    result.years = Math.floor(diff / YEAR)
    diff -= result.years * YEAR
  }

  if (diff >= MONTH) {
    result.months = Math.floor(diff / MONTH)
    diff -= result.months * MONTH
  }

  if (diff >= WEEK) {
    result.weeks = Math.floor(diff / WEEK)
    diff -= result.weeks * WEEK
  }

  if (diff >= DAY) {
    result.days = Math.floor(diff / DAY)
    diff -= result.days * DAY
  }

  if (diff >= HOUR) {
    result.hours = Math.floor(diff / HOUR)
    diff -= result.hours * HOUR
  }

  if (diff >= MINUTE) {
    result.minutes = Math.floor(diff / MINUTE)
    diff -= result.minutes * MINUTE
  }

  return durationFormatter.format(result) || "moins d'une minute"
}
