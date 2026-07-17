import { useAsyncStoredData } from "@/hook/useStoredData"
import { useAuth } from "@/lib/auth"
import { m } from "@/paraglide/messages"
import { Link } from "@tanstack/react-router"
import { ArrowDownUp, CircleAlert, Compass, Plus, Settings } from "lucide-react"

export function Navigation() {
  const { isAuthenticated } = useAuth()

  const asyncData = useAsyncStoredData()
  const hasAsyncData = (asyncData?.flat().length ?? 0) > 0

  if (!isAuthenticated) {
    return null
  }
  return (
    <nav
      role="navigation"
      className="offset-x-0 border-top sticky bottom-0 z-60 w-full border-t-2 bg-muted/80 py-4 supports-backdrop-filter:backdrop-blur-xs"
    >
      <ul className="flex items-center justify-around gap-2">
        <li>
          <Link className="group block" to="/{-$locale}">
            <Compass
              className="m-auto mb-1 size-6 group-hover:text-primary group-data-[status=active]:text-primary"
              aria-hidden
            />
            <span className="group-hover:text-accent-foreground group-data-[status=active]:text-accent-foreground">
              {m["menu.browse"]()}
            </span>
          </Link>
        </li>
        <li>
          <Link className="group block" to="/{-$locale}/create">
            <Plus
              className="m-auto mb-1 size-6 group-hover:text-primary group-data-[status=active]:text-primary"
              aria-hidden
            />
            <span className="group-hover:text-accent-foreground group-data-[status=active]:text-accent-foreground">
              {m["menu.create"]()}
            </span>
          </Link>
        </li>
        <li>
          <Link
            className="group relative block"
            to="/{-$locale}/sync"
            hash={hasAsyncData ? "sync-up" : ""}
          >
            <ArrowDownUp
              className="m-auto mb-1 size-6 group-hover:text-primary group-data-[status=active]:text-primary"
              aria-hidden
            />
            <span className="group-hover:text-accent-foreground group-data-[status=active]:text-accent-foreground">
              {m["menu.sync"]()}
              {hasAsyncData && (
                <CircleAlert
                  className="absolute inset-e-7 top-0 size-4 text-destructive"
                  role="img"
                  aria-label="Des éléments sont à synchroniser"
                />
              )}
            </span>
          </Link>
        </li>
        <li>
          <Link className="group block" to="/{-$locale}/settings">
            <Settings
              className="m-auto mb-1 size-6 group-hover:text-primary group-data-[status=active]:text-primary"
              aria-hidden
            />
            <span className="group-hover:text-accent-foreground group-data-[status=active]:text-accent-foreground">
              {m["menu.settings"]()}
            </span>
          </Link>
        </li>
      </ul>
    </nav>
  )
}
