export const AUTH_TOKENS_KEY = "gtam-auth-token"

export default function useTokens() {
  const storedToken = JSON.parse(localStorage.getItem(AUTH_TOKENS_KEY) || "{}")
  return {
    accessToken: storedToken.access || null,
    refreshToken: storedToken.refresh || null,
    setAuthToken: (tokens: { access: string; refresh: string }) => {
      localStorage.setItem(AUTH_TOKENS_KEY, JSON.stringify(tokens))
    },
    clearAuthToken: () => {
      localStorage.removeItem(AUTH_TOKENS_KEY)
    },
  }
}
