import * as React from "react"
import * as z from "zod"
import { toast } from "sonner"
import { Check } from "lucide-react"
import { useLiveQuery } from "dexie-react-hooks"
import { createFileRoute } from "@tanstack/react-router"
import { useForm, useStore } from "@tanstack/react-form"
import { db } from "@/lib/db"
import { useAppSettings } from "@/hook/useAppSettings"
import { useOfflineMaps } from "@/hook/useOfflineMaps"
import Header from "@/components/header"
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import MapDownloadProgress from "@/components/map-download-progress"

export const Route = createFileRoute("/{-$locale}/_authenticated/sync/map")({
  component: RouteComponent,
})

function RouteComponent() {
  const settings = useLiveQuery(() => db.settings.get("settings"))
  const {
    data: { maps },
    removeMapLayer,
  } = useAppSettings()

  const layers = settings?.settings?.maps.layers ?? []

  const mapsAlreadyDownloaded = maps?.layers ?? []

  const mapsToDownload = layers.filter(
    (layer: { name: string }) =>
      !mapsAlreadyDownloaded.some(
        (downloadedLayer: { name: string }) =>
          downloadedLayer.name === layer.name
      )
  )

  const [open, setOpen] = React.useState(false)

  const { deleteZone, formatSize } = useOfflineMaps()

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
    onSubmit: () => {
      setOpen(true)
    },
  })

  const getTotalSize = (layersName: string[]) => {
    const selectedLayers = layersName
      .map((name) => layers.find((layer) => layer.name === name))
      .filter((layer) => layer !== undefined)
    const totalSize = selectedLayers.reduce(
      (sum, layer) => sum + (layer["content-length"] ?? 0),
      0
    )
    return totalSize
  }
  const layersName = useStore(form.store, (state) => state.values.layers)

  return (
    <div>
      <Header title="Fonds de cartes et tuiles" withBackbutton />

      <MapDownloadProgress
        layers={layers}
        layersName={layersName}
        open={open}
        setOpen={setOpen}
        size={formatSize(getTotalSize(layersName))}
      />

      {mapsAlreadyDownloaded.length > 0 && (
        <div className="m-4">
          <h2 className="mb-2 text-xl font-bold text-accent-foreground">
            Fonds cartographiques déjà téléchargés
          </h2>
          <ul>
            {mapsAlreadyDownloaded.map(
              ({ id, name }: { id: string; name: string }) => (
                <li className="my-1 flex items-center gap-2" key={id}>
                  <Check className="size-4" />
                  {name}
                  <span className="text-xs text-muted-foreground">
                    ({formatSize(getTotalSize([name]))})
                  </span>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => {
                      toast.promise(() => deleteZone(id), {
                        loading: "Suppression en cours...",
                        success: () => {
                          removeMapLayer(id)
                          return "Suppression terminée"
                        },
                        error: ({ message }) => message,
                        position: "top-center",
                      })
                    }}
                  >
                    Supprimer
                  </Button>
                </li>
              )
            )}
          </ul>
        </div>
      )}
      {mapsToDownload.length > 0 && (
        <form
          onSubmit={(event) => {
            event.preventDefault()
            form.handleSubmit()
          }}
        >
          <fieldset className="m-4">
            <legend className="my-4 text-xl font-bold text-accent-foreground">
              Sélectionnez les fonds cartographiques à télécharger
            </legend>
            <form.Field
              name="layers"
              children={(field) => {
                const isInvalid =
                  field.state.meta.isTouched && !field.state.meta.isValid
                return (
                  <FieldGroup className="gap-3">
                    <fieldset>
                      {mapsToDownload.map((layer) => (
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

                            <span className="text-xs text-muted-foreground">
                              ({formatSize(getTotalSize([layer.name]))})
                            </span>
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
            {layersName.length > 0 && (
              <Button type="submit" aria-describedby="submit-helptext">
                Télécharger
              </Button>
            )}
            {layersName.length > 0 && (
              <p
                id="submit-helptext"
                className="text-center text-sm text-muted-foreground"
              >
                Taille estimée : {formatSize(getTotalSize(layersName))}
              </p>
            )}
          </Field>
        </form>
      )}
    </div>
  )
}
