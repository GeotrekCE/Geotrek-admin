import { useLocation, useNavigate } from "@tanstack/react-router"
import * as z from "zod"
import { toast } from "sonner"
import { LogIn } from "lucide-react"
import { Field, FieldGroup, FieldLegend, FieldSet } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useAuth } from "@/lib/auth"
import { m } from "@/paraglide/messages"
import { useAppForm, useFormFields } from "@/components/ui/tanstack-form"
import { useSettingsQuery } from "@/hook/useSettingsQuery"

export default function Login() {
  const { login } = useAuth()
  const { search } = useLocation()
  const navigate = useNavigate()
  const { refetch } = useSettingsQuery(false)

  const form = useAppForm({
    defaultValues: {
      username: "",
      password: "",
    },
    validators: {
      onSubmit: z.object({
        username: z
          .string()
          .min(1, m["login.form.user-name.required-message"]()),
        password: z
          .string()
          .min(1, m["login.form.password.required-message"]()),
      }),
    },
    onSubmit: async ({ value }) => {
      toast.promise(() => login(value.username, value.password), {
        id: "login",
        loading: m["login.loading"](),
        success: () => {
          navigate({ to: search.redirect || "/" })
          refetch()
          return m["login.success"]()
        },
        error: ({ message }) => message,
        position: "top-center",
      })
    },
  })

  const { FormTextField } = useFormFields<{
    username: string
    password: string
  }>()

  return (
    <section className="grid h-screen place-items-center">
      <Card className="w-full sm:max-w-md">
        <CardHeader>
          <CardTitle>{m["login.title"]()}</CardTitle>
          <CardDescription>{m["login.description"]()}</CardDescription>
        </CardHeader>
        <CardContent>
          <form.AppForm>
            <form.Form id="login-form" className="p-0" data-testid="login-form">
              <FieldGroup className="mb-4">
                <FieldSet>
                  <FieldLegend className="mb-4">
                    {m["login.form.title"]()}
                  </FieldLegend>

                  <FormTextField
                    name="username"
                    label={m["login.form.user-name.label"]()}
                    placeholder={m["login.form.user-name.placeholder"]()}
                    autoCapitalize="none"
                  />

                  <FormTextField
                    name="password"
                    label={m["login.form.password.label"]()}
                    placeholder={m["login.form.password.placeholder"]()}
                    type="password"
                  />
                </FieldSet>
              </FieldGroup>
            </form.Form>
          </form.AppForm>
        </CardContent>
        <CardFooter>
          <Field orientation="horizontal">
            <Button
              type="submit"
              className="w-full"
              size="lg"
              form="login-form"
            >
              <LogIn aria-hidden /> {m["login.form.submit"]()}
            </Button>
          </Field>
        </CardFooter>
      </Card>
    </section>
  )
}
