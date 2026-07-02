import { useLocation, useNavigate } from "@tanstack/react-router"
import { useForm } from "@tanstack/react-form"
import * as z from "zod"
import { toast } from "sonner"
import { LogIn } from "lucide-react"
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
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

export default function Login() {
  const { login } = useAuth()
  const { search } = useLocation()
  const navigate = useNavigate()

  const form = useForm({
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
          return m["login.success"]()
        },
        error: ({ message }) => message,
        position: "top-center",
      })
    },
  })

  return (
    <section className="grid h-screen place-items-center">
      <Card className="w-full sm:max-w-md">
        <CardHeader>
          <CardTitle>{m["login.title"]()}</CardTitle>
          <CardDescription>{m["login.description"]()}</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            id="login-form"
            className="my-4"
            onSubmit={(event) => {
              event.preventDefault()
              form.handleSubmit()
            }}
          >
            <FieldGroup className="mb-4">
              <FieldSet>
                <FieldLegend className="mb-4">
                  {m["login.form.title"]()}
                </FieldLegend>
                <form.Field
                  name="username"
                  children={(field) => {
                    const isInvalid =
                      field.state.meta.isTouched && !field.state.meta.isValid
                    return (
                      <Field data-invalid={isInvalid}>
                        <FieldLabel htmlFor="username" className="font-normal">
                          {m["login.form.user-name.label"]()}
                        </FieldLabel>
                        <Input
                          name={field.name}
                          value={field.state.value}
                          onBlur={field.handleBlur}
                          onChange={(e) => field.handleChange(e.target.value)}
                          placeholder={m["login.form.user-name.placeholder"]()}
                          aria-invalid={isInvalid}
                          aria-required
                        />
                        {isInvalid && (
                          <FieldError errors={field.state.meta.errors} />
                        )}
                      </Field>
                    )
                  }}
                />
                <form.Field
                  name="password"
                  children={(field) => {
                    const isInvalid =
                      field.state.meta.isTouched && !field.state.meta.isValid
                    return (
                      <Field data-invalid={isInvalid}>
                        <FieldLabel htmlFor="password" className="font-normal">
                          {m["login.form.password.label"]()}
                        </FieldLabel>
                        <Input
                          id="password"
                          name={field.name}
                          value={field.state.value}
                          onBlur={field.handleBlur}
                          onChange={(e) => field.handleChange(e.target.value)}
                          placeholder={m["login.form.password.placeholder"]()}
                          aria-invalid={isInvalid}
                          aria-required
                          type="password"
                        />
                        {isInvalid && (
                          <FieldError errors={field.state.meta.errors} />
                        )}
                      </Field>
                    )
                  }}
                />
              </FieldSet>
            </FieldGroup>
          </form>
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
