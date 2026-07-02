import * as React from "react"
import { ZodError } from "zod"
import {
  MutationCache,
  Query,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { routeTree } from "./routeTree.gen"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { toast } from "sonner"
import { Toaster } from "@/components/ui/sonner"
import { AuthProvider, useAuth } from "@/lib/auth"
import { deLocalizeUrl, localizeUrl } from "@/paraglide/runtime"
import { useAppInit } from "@/hook/useAppInit"

const router = createRouter({
  basepath: import.meta.env.BASE_URL,
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

  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            gcTime: Infinity,
            staleTime: Infinity,
            retry: 0,
            retryOnMount: false,
          },
        },
        mutationCache: new MutationCache({
          onError: (error) => {
            toast.error(error.message)
          },
        }),
        queryCache: new QueryCache({
          onSettled: (_data, error, query) => {
            if (error instanceof ZodError) {
              toast.error("Mismatching SCHEMAS between API and app", {
                position: "top-center",
              })
              return
            }
            // @ts-expect-error - deal with API error shape
            if (error?.res?.status === 401) {
              auth.refreshAuthToken(query as Query)
              return
            }
            if (error) {
              toast.error("Une erreur s'est produite", {
                position: "top-center",
                description: error.message,
              })
              return
            }
          },
        }),
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} context={{ auth, queryClient }} />
      <Toaster />
    </QueryClientProvider>
  )
}

export function App() {
  useAppInit()

  return (
    <AuthProvider>
      <InnerApp />
    </AuthProvider>
  )
}

export default App
