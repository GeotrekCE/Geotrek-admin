import * as React from "react"
import { ZodError } from "zod"
import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query"
import { routeTree } from "./routeTree.gen"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client"
import { createAsyncStoragePersister } from "@tanstack/query-async-storage-persister"
import { compress, decompress } from "lz-string"
import { toast } from "sonner"
import { Toaster } from "@/components/ui/sonner"
import { API_URL } from "@/lib/api"
import { AuthProvider, useAuth } from "@/lib/auth"
import useTokens from "@/hook/useTokens"
import { deLocalizeUrl, localizeUrl } from "@/paraglide/runtime"
import { getSerwist } from "virtual:serwist"

// import { get, set, del, createStore, type UseStore } from "idb-keyval"

// function newIdbStorage(idbStore: UseStore): AsyncStorage {
//   return {
//     getItem: async (key) => await get(key, idbStore),
//     setItem: async (key, value) => await set(key, value, idbStore),
//     removeItem: async (key) => await del(key, idbStore),
//   }
// }

const persister = createAsyncStoragePersister(
  // {
  //   storage: newIdbStorage(createStore("db_GTAM", "store_name")),
  //   maxAge: 1000 * 60 * 60 * 12, // 12 hours
  // }
  {
    storage: window.localStorage, // TODO indexedDB V1 https://dexie.org/docs/API-Reference
    serialize: (data) =>
      import.meta.env.DEV
        ? JSON.stringify(data)
        : compress(JSON.stringify(data)),
    deserialize: (data) =>
      import.meta.env.DEV ? JSON.parse(data) : JSON.parse(decompress(data)),
  }
)

const router = createRouter({
  routeTree,
  scrollRestoration: true,
  context: {
    auth: undefined!,
    queryClient: undefined!,
  },
  defaultPreloadStaleTime: 0,
  defaultViewTransition: true,
  rewrite: {
    input: ({ url }) => deLocalizeUrl(url),
    output: ({ url }) => localizeUrl(url),
  },
})

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

function InnerApp() {
  const auth = useAuth()
  const { accessToken, refreshToken, setAuthToken } = useTokens()
  const [refreshingToken, setRefreshingToken] = React.useState(false)

  const refreshAuthToken = async () => {
    if (!refreshingToken && refreshToken) {
      try {
        setRefreshingToken(true)

        const response = await fetch(`${API_URL}/auth/refresh-token/`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh: refreshToken }),
        })

        if (!response.ok) {
          throw new Error("Failed to refresh token")
        }

        const token = await response.json()

        setAuthToken(token)
      } catch {
        auth.logout()
      } finally {
        setRefreshingToken(false)
      }
    }
    if (!refreshingToken && !refreshToken) {
      auth.logout(true)
    }
  }

  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            gcTime: Infinity,
            staleTime: Infinity,
            retry: 1,
            // retry = (failureCount, error) =>
            retryOnMount: false,
          },
        },
        mutationCache: new MutationCache({
          // onSuccess: (data) => {
          //   toast.success(data.message)
          // },
          onError: (error) => {
            toast.error(error.message)
          },
        }),
        queryCache: new QueryCache({
          onSettled: (data, error) => {
            if (error instanceof ZodError) {
              toast.error("Mismatching SCHEMAS between API and app", {
                position: "top-center",
              })
            }
            // @ts-expect-error - deal with API error shape
            if (error?.res?.status === 401) {
              refreshAuthToken()
              console.log("erreur de requête:", data, error)
            }
          },
        }),
      })
  )

  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister }}
      onSuccess={() => {
        // resume mutations after initial restore from localStorage was successful
        queryClient.resumePausedMutations().then(() => {
          queryClient.invalidateQueries()
        })
      }}
    >
      <RouterProvider router={router} context={{ auth, queryClient }} />
      <Toaster />
    </PersistQueryClientProvider>
  )
}

export function App() {
  React.useEffect(() => {
    const loadSerwist = async () => {
      if ("serviceWorker" in navigator) {
        const serwist = await getSerwist()

        serwist?.addEventListener("installed", () => {
          console.log("Serwist installed!")
        })

        void serwist?.register()
      }
    }

    loadSerwist()
  }, [])

  return (
    <AuthProvider>
      <InnerApp />
    </AuthProvider>
  )
}

export default App
