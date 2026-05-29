import Header from "@/components/header"
import { useTheme } from "@/components/theme-provider"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { useSettingsQuery } from "@/hook/useSettingsQuery"
import { setLocale, getLocale } from "@/paraglide/runtime"
import { useAuth } from "@/lib/auth"

import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { m } from "@/paraglide/messages"

export const Route = createFileRoute("/{-$locale}/_authenticated/settings")({
  component: RouteComponent,
})

function RouteComponent() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const { data } = useSettingsQuery()
  const { theme, setTheme } = useTheme()
  const name =
    `${data?.user?.firstName || ""} ${data?.user?.lastName || ""}`.trim() ||
    data?.user?.userName
  return (
    <div>
      <Header title={m["settings.title"]()} />
      <section className="m-4 text-center">
        <h2>
          <span className="block font-bold text-accent-foreground">{name}</span>
        </h2>
        <Button
          className="mx-auto mt-4 block"
          variant="outline"
          onClick={() => {
            logout()
            navigate({
              to: "/{-$locale}/login",
              search: {
                redirect: window.location.pathname.replace(
                  import.meta.env.BASE_URL,
                  "/"
                ),
              },
            })
          }}
        >
          {m["settings.user.logout"]()}
        </Button>
      </section>

      <Card className="m-4">
        <CardHeader>
          <CardTitle>{m["settings.preferences.title"]()}</CardTitle>
        </CardHeader>
        <CardContent>
          <h3 className="my-3 font-bold">
            {m["settings.preferences.theme.title"]()}
          </h3>
          <ToggleGroup
            className="mb-8 bg-background p-1"
            size="lg"
            spacing={2}
            value={[theme]}
            onValueChange={(value) =>
              setTheme(value[0] as "dark" | "light" | "system")
            }
          >
            <ToggleGroupItem
              className="data-pressed:bg-primary data-pressed:text-primary-foreground"
              value="light"
            >
              {m["settings.preferences.theme.light"]()}
            </ToggleGroupItem>
            <ToggleGroupItem
              className="data-pressed:bg-primary data-pressed:text-primary-foreground"
              value="dark"
            >
              {m["settings.preferences.theme.dark"]()}
            </ToggleGroupItem>
            <ToggleGroupItem
              className="data-pressed:bg-primary data-pressed:text-primary-foreground"
              value="system"
            >
              {m["settings.preferences.theme.system"]()}
            </ToggleGroupItem>
          </ToggleGroup>

          <h3 className="my-3 font-bold">
            {m["settings.preferences.lang.title"]()}
          </h3>
          <ToggleGroup
            className="mt-2 bg-background p-1"
            size="lg"
            spacing={2}
            defaultValue={[getLocale()]}
            onValueChange={(value) => {
              setLocale(value[0] as "en" | "fr")
            }}
          >
            <ToggleGroupItem
              className="data-pressed:bg-primary data-pressed:text-primary-foreground"
              value="fr"
              lang="fr"
            >
              Français
            </ToggleGroupItem>
            <ToggleGroupItem
              className="data-pressed:bg-primary data-pressed:text-primary-foreground"
              value="en"
              lang="en"
            >
              English
            </ToggleGroupItem>
          </ToggleGroup>
        </CardContent>
      </Card>
    </div>
  )
}
