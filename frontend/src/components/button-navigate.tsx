import * as React from "react"
import { Send } from "lucide-react"
import { buttonVariants } from "@/components/ui/button"
import { cn } from "cn"

export default function ButtonNavigate({
  position,
  className,
}: {
  position?: GeoJSON.Position
  className?: string
}) {
  const href = React.useMemo(() => {
    if (!position) {
      return null
    }
    const [longitude, latitude] = position

    const userAgent = navigator.userAgent || navigator.vendor

    if (/iPad|iPhone|iPod|Android/.test(userAgent)) {
      return `geo:${latitude},${longitude}`
    }
    return `https://www.openstreetmap.org/directions?to=${latitude}%2C${longitude}`
  }, [position])

  if (!href) {
    return null
  }

  return (
    <a
      href={href}
      className={cn(
        buttonVariants({ variant: "outline" }),
        "border-2 border-primary text-primary",
        className
      )}
    >
      <Send aria-hidden /> Itinéraire
    </a>
  )
}
