import * as z from "zod"
import { createFileRoute } from "@tanstack/react-router"
import Header from "@/components/header"
import { SETTINGS_QUERY_KEY } from "@/hook/useSettingsQuery"
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { useForm } from "@tanstack/react-form"
import { useQueryClient } from "@tanstack/react-query"
import type { SettingsSchemaProps } from "@/schemas/settings"
// import { toast } from "sonner"
import { Checkbox } from "@/components/ui/checkbox"
import { useOfflineMaps } from "@/hook/useOfflineMaps"

export const Route = createFileRoute("/_authenticated/sync/map")({
  component: RouteComponent,
})

function RouteComponent() {
  const queryClient = useQueryClient()
  const settings =
    queryClient.getQueryData<SettingsSchemaProps>(SETTINGS_QUERY_KEY)

  const layers = settings?.settings?.maps.layers ?? []

  const {
    // getRemoteSize, formatSize,
    downloadZone,
  } = useOfflineMaps()

  const form = useForm({
    defaultValues: {
      layers: [] as string[],
    },
    validators: {
      onSubmit: z.object({
        layers: z
          .array(z.string())
          .min(1, "Veuillez sélectionner au moins un fond cartographique")
          .refine(
            (value) =>
              value.every((task) => layers.some((t) => t.name === task)),
            {
              message: "Fond cartographique non valide.",
            }
          ),
      }),
    },
    onSubmit: async ({ value }) => {
      await Promise.all(
        value.layers.map((layerName) => {
          const layer = layers.find((l) => l.name === layerName)
          return layer && downloadZone(layer)
        })
      )
      // toast.success("Cartes embarquées dans l'application avec succès", {
      //   position: "top-center",
      // })
      // router.invalidate()
      // navigate({ to: "/sync" })
    },
  })
  return (
    <div>
      <Header title="Fonds de cartes et tuiles" withBackbutton />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          form.handleSubmit()
        }}
      >
        <fieldset className="m-4">
          <legend className="my-4 font-bold text-accent-foreground uppercase">
            Sélectionnez les fonds cartographiques
          </legend>
          <form.Field
            name="layers"
            children={(field) => {
              const isInvalid =
                field.state.meta.isTouched && !field.state.meta.isValid
              return (
                <FieldGroup className="gap-3">
                  <fieldset>
                    {layers.map((layer) => (
                      <Field
                        key={layer.name}
                        orientation="horizontal"
                        data-invalid={isInvalid}
                      >
                        <Checkbox
                          id={`layer-${layer.name}`}
                          name={field.name}
                          aria-invalid={isInvalid}
                          defaultChecked={field.state.value.includes(
                            layer.name
                          )}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              field.pushValue(layer.name)
                            } else {
                              const index = field.state.value.indexOf(
                                layer.name
                              )
                              if (index > -1) {
                                field.removeValue(index)
                              }
                            }
                          }}
                        />
                        <FieldLabel
                          htmlFor={`layer-${layer.name}`}
                          className="font-normal"
                        >
                          {layer.name}
                          {/* {getRemoteSize(layer.json_style_url) && (
                            <span className="text-sm text-muted-foreground">
                              ({formatSize(getRemoteSize(layer.json_style_url))}
                              )
                            </span>
                          )} */}
                        </FieldLabel>
                      </Field>
                    ))}
                    {isInvalid && (
                      <FieldError
                        className="mt-4"
                        errors={field.state.meta.errors}
                      />
                    )}
                  </fieldset>
                </FieldGroup>
              )
            }}
          />
        </fieldset>

        <Field className="p-4">
          <Button type="submit" aria-describedby="submit-helptext">
            Télécharger
          </Button>
          <p
            id="submit-helptext"
            className="text-center text-sm text-muted-foreground"
          >
            Taille estimée : TODO <abbr title="Mégaoctets">Mo</abbr>
          </p>
        </Field>
      </form>
    </div>
  )
}
