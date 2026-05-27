import { onlineManager } from "@tanstack/react-query"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export function ConnectionStatus({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const isOnline = onlineManager.isOnline()
  return (
    <div
      className={cn("flex items-center justify-between", className)}
      {...props}
    >
      <h2 className="text-xs uppercase">État de la connexion</h2>
      <Badge className="h-6 border-accent-foreground/10" variant="secondary">
        <span
          className={cn(
            "text-xl font-bold",
            isOnline ? "text-green-600" : "text-red-600"
          )}
          aria-hidden
        >
          •
        </span>
        <span>{isOnline ? "En ligne" : "Hors ligne"}</span>
      </Badge>
    </div>
  )
}
