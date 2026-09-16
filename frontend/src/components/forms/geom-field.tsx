import * as React from "react"
import { useSelector } from "@tanstack/react-form"
import Map from "@/components/map"
import { FieldDescription, FieldLabel } from "@/components/ui/field"
import {
  useFieldContext,
  FormFieldSet,
  FormField,
  FormFieldError,
  createFormField,
} from "@/components/ui/form-context"
import Required from "@/components/forms/required"
import { Button } from "@/components/ui/button"
import { m } from "@/paraglide/messages"
import { Alert, AlertTitle } from "@/components/ui/alert"
import * as z from "zod"
import type { geometrySchema } from "@/schemas/data"
import MapBboxDataLayer from "@/components/map-bbox-data-layer"
import useBounds from "@/hook/useBounds"
import MapElementsLayer from "../map-elements-layer"

type GeomFieldProps = {
  label: string
  description?: string
  required?: boolean
  reference: "signage" | "report" | "intervention" | "infrastructure"
  pictogram: { url?: string }
}

export function GeomField({
  label,
  description,
  required,
  reference,
  pictogram,
}: GeomFieldProps) {
  const id = React.useId()
  const field = useFieldContext()
  const value = useSelector(field.store, (s) => s.value) as z.infer<
    typeof geometrySchema
  >
  const [lng, lat] = (value.type === "Point" && value.coordinates) || []
  const bounds = useBounds(value)

  const [isEditing, setEditing] = React.useState(false)

  const isPoint = value.type === "Point"
  const isEditingPoint = isPoint && isEditing && lng && lat

  return (
    <FormFieldSet>
      <FormField>
        <FieldLabel htmlFor={id} className="font-normal text-accent-foreground">
          {label}
          {required && <Required />}
        </FieldLabel>

        {isPoint && (
          <Button
            type="button"
            onClick={() => setEditing((bool) => !bool)}
            data-testid={`field-${field.name}`}
          >
            {isEditing
              ? m["form.geom-action-cancel"]()
              : m["form.geom-action-select"]()}
          </Button>
        )}

        <Map
          className="aspect-square"
          initialViewState={{
            bounds: bounds && value.type !== "Point" ? bounds : undefined,
            longitude:
              value.type === "Point" ? value.coordinates[0] : undefined,
            latitude: value.type === "Point" ? value.coordinates[1] : undefined,
            zoom: 12,
          }}
          onClick={({ lngLat }) => {
            if (isEditing) {
              field.handleChange({
                type: "Point",
                coordinates: [lngLat.lng, lngLat.lat],
              })
              field.handleBlur()
            }
          }}
        >
          <MapBboxDataLayer />
          <MapElementsLayer
            active={{ reference, id: 1 }}
            elements={[
              {
                reference,
                geom: value as Parameters<
                  typeof MapElementsLayer
                >[0]["elements"][number]["geom"],
                pictogram,
                id: isEditingPoint ? 1 : undefined,
              },
            ]}
          />
        </Map>
        {isPoint && typeof lng === "number" && typeof lat === "number" && (
          <FieldDescription className="text-end text-xs">
            Longitude : {lng.toFixed(5)}, Lattitude : {lat.toFixed(5)}
          </FieldDescription>
        )}
        {!isPoint && (
          <Alert className="mt-4" variant="warning">
            <AlertTitle>{m["form.geom-linear-not-supported"]()}</AlertTitle>
          </Alert>
        )}
        {!isPoint && description && (
          <FieldDescription>{description}</FieldDescription>
        )}
      </FormField>
      <FormFieldError />
    </FormFieldSet>
  )
}

export const FormGeomField = createFormField(GeomField)
