import {
  createRootRouteWithContext,
  Outlet,
  redirect,
} from "@tanstack/react-router"
import type { QueryClient } from "@tanstack/react-query"
import { Navigation } from "@/components/navigation"
import { getLocale, shouldRedirect } from "@/paraglide/runtime"

interface AuthState {
  isAuthenticated: boolean
  tokens: { accessToken: string; refreshToken: string } | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

interface RouterContext {
  auth: AuthState
  queryClient: QueryClient
}

export const Route = createRootRouteWithContext<RouterContext>()({
  beforeLoad: async () => {
    document.documentElement.setAttribute("lang", getLocale())

    const decision = await shouldRedirect({
      url: window.location.pathname.replace(import.meta.env.BASE_URL, "/"),
    })

    if (decision.redirectUrl) {
      throw redirect({ href: decision.redirectUrl.href })
    }
  },
  component: () => (
    <div className="flex min-h-dvh flex-col">
      <main className="flex grow flex-col">
        <Outlet />
      </main>
      <Navigation />
    </div>
  ),
})
