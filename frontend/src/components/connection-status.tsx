import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import useOnline from "@/hook/useOnline"
import { m } from "@/paraglide/messages"

export function ConnectionStatus({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const online = useOnline()

  return (
    <div
      className={cn("flex items-center justify-between", className)}
      {...props}
    >
      <h2 className="text-xs uppercase">{m["common.connection-status"]()}</h2>
      <Badge className="h-6 border-accent-foreground/10" variant="secondary">
        <span
          className={cn(
            "text-xl font-bold",
            online ? "text-green-600" : "text-red-600"
          )}
          aria-hidden
        >
          •
        </span>
        <span>{online ? m["common.online"]() : m["common.offline"]()}</span>
      </Badge>
    </div>
  )
}
