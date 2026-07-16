import * as React from "react"
import { useLiveQuery } from "dexie-react-hooks"
import { useStore } from "@tanstack/react-form"
import Map from "@/components/map"
import type { LngLatBoundsLike } from "maplibre-gl"
import { FieldDescription, FieldLabel } from "@/components/ui/field"
import {
  useFieldContext,
  FormFieldSet,
  FormField,
  FormFieldError,
  createFormField,
} from "@/components/ui/form-context"
import Required from "./required"
import { Marker } from "react-map-gl/maplibre"
import { cn } from "@/lib/utils"
import { MapPin } from "lucide-react"
import { Button } from "@/components/ui/button"
import { db } from "@/lib/db"
import { m } from "@/paraglide/messages"
import { Alert, AlertTitle } from "@/components/ui/alert"

type GeomFieldProps = {
  label: string
  description?: string
  required?: boolean
  icon?: { url?: string }
}

export function GeomField({
  label,
  description,
  required,
  icon,
}: GeomFieldProps) {
  const id = React.useId()
  const field = useFieldContext()
  const value = useStore(field.store, (s) => s.value) as [number, number]
  const [lng, lat] = value || []
  const appSync = useLiveQuery(() => db.appSync.get("data"))
  const { bounds } = appSync || {}

  const [isEditing, setEditing] = React.useState(false)

  const isPoint = typeof lng === "number"

  return (
    <FormFieldSet>
      <FormField>
        <FieldLabel htmlFor={id} className="font-normal text-accent-foreground">
          {label}
          {required && <Required />}
        </FieldLabel>

        <Map
          className="aspect-square"
          initialViewState={{ bounds: bounds as LngLatBoundsLike }}
          maxBounds={bounds as LngLatBoundsLike}
          onClick={({ lngLat }) => {
            if (isEditing) {
              field.handleChange([lngLat.lng, lngLat.lat])
              field.handleBlur()
            }
          }}
        >
          {isPoint && !!lng && !!lat && (
            <Marker longitude={lng} latitude={lat} anchor="bottom">
              <div className="grid items-center justify-center">
                <MapPin
                  className={cn(
                    "col-start-1 row-start-1 fill-white stroke-1 [&>circle]:hidden",
                    isEditing ? "size-12 fill-white/60" : "size-10"
                  )}
                />
                {icon?.url && (
                  <img
                    loading="lazy"
                    src={icon.url}
                    alt=""
                    className={cn(
                      "col-start-1 row-start-1 m-auto",
                      isEditing ? "size-8" : "size-6"
                    )}
                  />
                )}
              </div>
            </Marker>
          )}
        </Map>
        {isPoint && !!lng && !!lat && (
          <FieldDescription className="text-end text-xs">
            Longitude : {lng.toFixed(5)}, Lattitude : {lat.toFixed(5)}
          </FieldDescription>
        )}
        {isPoint && (
          <Button
            variant="outline"
            type="button"
            onClick={() => setEditing((bool) => !bool)}
            data-testid={`field-${field.name}`}
          >
            {isEditing
              ? m["form.geom-action-cancel"]()
              : m["form.geom-action-select"]()}
          </Button>
        )}
        {(!isPoint || description) && (
          <FieldDescription>
            {!isPoint ? (
              <Alert className="mt-4" variant="warning">
                <AlertTitle>{m["form.geom-linear-not-supported"]()}</AlertTitle>
              </Alert>
            ) : (
              description
            )}
          </FieldDescription>
        )}
      </FormField>
      <FormFieldError />
    </FormFieldSet>
  )
}

export const FormGeomField = createFormField(GeomField)
