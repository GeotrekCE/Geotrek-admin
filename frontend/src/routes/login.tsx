import { createFileRoute, redirect } from "@tanstack/react-router"
import Login from "@/components/login"
import InvalidConfiguration from "@/components/invalid-configuration"

export const Route = createFileRoute("/login")({
  validateSearch: (search) => ({
    redirect: (search.redirect as string) || "/",
  }),
  beforeLoad: ({ context, search }) => {
    if (context.auth.isAuthenticated) {
      throw redirect({ to: search.redirect })
    }
  },
  component: LoginComponent,
})

function LoginComponent() {
  if (!__HOST_URL__) {
    return <InvalidConfiguration />
  }
  return <Login />
}
