import * as React from "react"
import { useStore } from "@tanstack/react-form"
import Map from "@/components/map"
import { useAppSettings } from "@/hook/useAppSettings"
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
import { Button } from "../ui/button"

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
  const [lng, lat] = value
  const { data } = useAppSettings()
  const { bounds } = data?.syncData || {}

  const [isEditing, setEditing] = React.useState(false)
  console.log(icon)

  return (
    <FormFieldSet>
      <FormField>
        <FieldLabel htmlFor={id} className="font-normal text-accent-foreground">
          {label}
          {required && <Required />}
        </FieldLabel>

        <Map
          className="aspect-square max-h-80"
          initialViewState={{ bounds: bounds as LngLatBoundsLike }}
          maxBounds={bounds as LngLatBoundsLike}
          onClick={({ lngLat }) =>
            isEditing && field.handleChange([lngLat.lng, lngLat.lat])
          }
        >
          <Marker longitude={lng} latitude={lat} anchor="bottom">
            <div className="grid items-center justify-center">
              <MapPin
                className={cn(
                  "col-start-1 row-start-1 fill-white stroke-1 [&>circle]:hidden",
                  isEditing ? "size-12 fill-white/60" : "size-10"
                )}
              />
              {icon && (
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
        </Map>
        <FieldDescription className="text-end text-xs">
          Longitude : {lng.toFixed(5)}, Latitude: {lat.toFixed(5)}
        </FieldDescription>
        <Button
          variant="outline"
          type="button"
          onClick={() => setEditing((bool) => !bool)}
        >
          {isEditing ? "Revenir en consultation" : "Placer sur la carte"}
        </Button>
        {description && <FieldDescription>{description}</FieldDescription>}
      </FormField>
      <FormFieldError />
    </FormFieldSet>
  )
}

export const FormGeomField = createFormField(GeomField)
