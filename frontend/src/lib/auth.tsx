import * as React from "react"
import { API_URL } from "@/lib/api"
import useTokens from "@/hook/useTokens"
import { toast } from "sonner"
import { m } from "@/paraglide/messages"

interface Tokens {
  accessToken: string
  refreshToken: string
}

interface AuthState {
  isAuthenticated: boolean
  tokens: Tokens | null
  login: (username: string, password: string) => Promise<void>
  logout: (isExpired?: boolean) => void
}

const AuthContext = React.createContext<AuthState | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { setAuthToken, clearAuthToken, ...tokens } = useTokens()
  const [isAuthenticated, setIsAuthenticated] = React.useState(
    tokens.accessToken !== null
  )
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

  const logout = (isExpired?: boolean) => {
    clearAuthToken()
    setIsAuthenticated(false)
    if (isExpired) {
      toast.info(m["settings.user.logout-fail"](), {
        position: "top-center",
      })
    } else {
      toast.success(m["settings.user.logout-success"](), {
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
