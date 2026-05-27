const LOCAL_STORAGE_KEY = "auth-token"

export default function useTokens() {
  const storedToken = JSON.parse(
    localStorage.getItem(LOCAL_STORAGE_KEY) || "{}"
  )
  return {
    accessToken: storedToken.access || null,
    refreshToken: storedToken.refresh || null,
    setAuthToken: (tokens: { access: string; refresh: string }) => {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(tokens))
    },
    clearAuthToken: () => {
      localStorage.removeItem(LOCAL_STORAGE_KEY)
    },
  }
}
