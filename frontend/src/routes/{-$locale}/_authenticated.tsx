import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/{-$locale}/_authenticated")({
  beforeLoad: ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: "/{-$locale}/login",
        search: { redirect: location.href },
      })
    }
  },
})
