import * as React from "react"
import * as z from "zod"
import { createFileRoute, useNavigate, useRouter } from "@tanstack/react-router"
import Header from "@/components/header"
import Map from "@/components/map"
import { SETTINGS_QUERY_KEY } from "@/hook/useSettingsQuery"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Field, FieldLabel } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { useForm } from "@tanstack/react-form"
import { cn } from "@/lib/utils"
import type { ViewStateChangeEvent } from "react-map-gl/maplibre"
import type { LngLatBoundsLike, MapLibreEvent } from "maplibre-gl"
import { useDataQuery } from "@/hook/useDataQuery"
import { getBoundsFromPolygon, getPolygonFromBounds } from "@/lib/map"
import { useQueryClient } from "@tanstack/react-query"
import type { SettingsSchemaProps } from "@/schemas/settings"
import { useAppSettings } from "@/hook/useAppSettings"
import { toast } from "sonner"

export const Route = createFileRoute("/_authenticated/sync/data")({
  component: RouteComponent,
})

function RouteComponent() {
  const queryClient = useQueryClient()
  const settings =
    queryClient.getQueryData<SettingsSchemaProps>(SETTINGS_QUERY_KEY)

  const minZoom = settings?.settings?.maps.localOptions.minZoom ?? 10
  const attachedStructure = settings?.user.attachedStructure.id

  const { data: appConfig, setData: setAppConfig } = useAppSettings()
  const [currentZoom, setZoom] = React.useState<number>(0)
  const [queryParams, setParams] = React.useState<
    Record<string, string | number>
  >({})
  const { refetch } = useDataQuery(queryParams)
  const router = useRouter()
  const navigate = useNavigate()

  const isNotEnoughtZoomed = currentZoom < minZoom

  const form = useForm({
    defaultValues: {
      bbox: "",
      structure:
        appConfig?.syncData.structure !== null && attachedStructure
          ? "own"
          : "all",
    },
    validators: {
      onSubmit: z.object({
        bbox: z.string().min(1),
        structure: z.string(),
      }),
    },
    onSubmit: async ({ value }) => {
      const params: { bbox: string; structure?: number } = {
        bbox: value.bbox,
      }
      if (value.structure === "own") {
        params.structure = attachedStructure
      }
      setParams(params)
      setAppConfig({
        syncData: {
          bounds: getBoundsFromPolygon(value.bbox) ?? null,
          structure: params.structure ?? null,
          lastSync: new Date().toISOString(),
        },
      })
      window.setTimeout(refetch, 1)
      toast.success("Données embarquées dans l'application avec succès", {
        position: "top-center",
      })
      router.invalidate()
      navigate({ to: "/sync" })
    },
  })

  const handleMapInit = React.useCallback(
    (event: MapLibreEvent) => {
      if (appConfig?.syncData?.bounds) {
        event.target.fitBounds(appConfig.syncData.bounds as LngLatBoundsLike)
      }
      setZoom(event.target.getZoom())
      form.setFieldValue("bbox", getPolygonFromBounds(event.target.getBounds()))
    },
    [appConfig, form]
  )

  const handleMapChange = React.useCallback(
    (event: ViewStateChangeEvent) => {
      setZoom(event.viewState.zoom)
      form.setFieldValue("bbox", getPolygonFromBounds(event.target.getBounds()))
    },
    [form]
  )

  return (
    <div>
      <Header title="Données embarquées" withBackbutton />

      <form
        onSubmit={(event) => {
          event.preventDefault()
          if (!isNotEnoughtZoomed) {
            form.handleSubmit()
          }
        }}
      >
        <fieldset>
          <legend className="m-4 font-bold text-accent-foreground uppercase">
            Zone géographique
          </legend>
          <div className="max-h-screen/2 bg-accent">
            <Map
              className="min-size-20 mx-auto aspect-square max-h-[calc(100dvh-18rem)]"
              onLoad={handleMapInit}
              onDragEnd={handleMapChange}
              onZoom={handleMapChange}
            >
              {isNotEnoughtZoomed && (
                <div className="absolute inset-x-3 top-2 z-10 rounded-xl bg-background px-4 py-2 text-xs">
                  Zone trop large - Zoomez sur la carte pour accéder au
                  téléchargement des données
                </div>
              )}
            </Map>
            <form.Field
              name="bbox"
              children={(field) => {
                return (
                  <input
                    type="hidden"
                    name={field.name}
                    value={field.state.value}
                  />
                )
              }}
            />
          </div>
        </fieldset>
        <fieldset className="m-4">
          <legend className="my-4 font-bold text-accent-foreground uppercase">
            Structure
          </legend>
          <form.Field
            name="structure"
            children={(field) => {
              return (
                <RadioGroup
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onValueChange={field.handleChange}
                >
                  <Field orientation="horizontal">
                    <RadioGroupItem value="own" id="own-structure" />
                    <FieldLabel htmlFor="own-structure" className="font-normal">
                      Ma structure
                    </FieldLabel>
                  </Field>
                  <Field orientation="horizontal">
                    <RadioGroupItem value="all" id="all-structure" />
                    <FieldLabel htmlFor="all-structure" className="font-normal">
                      Toutes les structures
                    </FieldLabel>
                  </Field>
                </RadioGroup>
              )
            }}
          />
        </fieldset>

        <Field className="p-4">
          <Button
            type="submit"
            aria-disabled={isNotEnoughtZoomed}
            variant={isNotEnoughtZoomed ? "outline" : "default"}
            className={cn(isNotEnoughtZoomed && "bg-accent")}
            aria-describedby="submit-helptext"
          >
            Télécharger les données
          </Button>
          <p
            id="submit-helptext"
            className={cn(
              "text-center text-sm text-muted-foreground",
              !isNotEnoughtZoomed && "hidden"
            )}
          >
            Le volume de données sélectionné est trop important
          </p>
        </Field>
      </form>
    </div>
  )
}
