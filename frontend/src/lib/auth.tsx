import * as React from "react"
import { API_URL } from "@/lib/api"
import useTokens from "@/hook/useTokens"
import { toast } from "sonner"
import { m } from "@/paraglide/messages"
import type { Query } from "@tanstack/react-query"
import { getLocale } from "@/paraglide/runtime"

interface Tokens {
  accessToken: string
  refreshToken: string
}

interface AuthState {
  isAuthenticated: boolean
  tokens: Tokens | null
  login: (username: string, password: string) => Promise<void>
  logout: (isExpired?: boolean) => void
  refreshAuthToken: (query: Query) => void
}

const AuthContext = React.createContext<AuthState | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { setAuthToken, clearAuthToken, ...tokens } = useTokens()
  const [isAuthenticated, setIsAuthenticated] = React.useState(
    tokens.accessToken !== null
  )
  const [refreshingToken, setRefreshingToken] = React.useState(false)

  const login = async (username: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/token/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    })

    if (response.ok) {
      const token = await response.json()
      setIsAuthenticated(true)
      // Store token for persistence
      setAuthToken(token)
      return token
    } else {
      return response.json().then((errorData) => {
        throw new Error(
          errorData.detail || "Echec de l'authentification, veuillez réessayer"
        )
      })
    }
  }

  const refreshAuthToken = async (query: Query) => {
    if (!refreshingToken && tokens.refreshToken) {
      try {
        setRefreshingToken(true)

        const response = await fetch(`${API_URL}/auth/refresh-token/`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${tokens.accessToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh: tokens.refreshToken }),
        })

        if (!response.ok) {
          throw new Error("Failed to refresh token")
        }

        const token = await response.json()

        setAuthToken(token)
        query.fetch()
      } catch {
        logout(true)
      } finally {
        setRefreshingToken(false)
      }
    }
    if (!refreshingToken && !tokens.refreshToken) {
      logout(true)
    }
  }

  const logout = (isExpired?: boolean) => {
    if (isExpired) {
      toast.info(m["settings.user.logout-fail"](), {
        id: "relogin",
        position: "top-center",
        dismissible: false,
        duration: Infinity,
        action: (
          <a
            className="whitespace-nowrap text-primary"
            href={`${import.meta.env.BASE_URL}${getLocale()}/login?redirect=${encodeURIComponent(window.location.pathname.replace(import.meta.env.BASE_URL, "/"))}`}
          >
            Se reconnecter
          </a>
        ),
      })
    } else {
      toast.success(m["settings.user.logout-success"](), {
        id: "login",
        position: "top-center",
      })
    }
    clearAuthToken()
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        tokens,
        login,
        logout,
        refreshAuthToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = React.useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
