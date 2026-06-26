import { toast } from "sonner"
import {
  infrastructureDataSchema,
  type InfrastructureDataSchemaProps,
} from "@/schemas/data"

import type {
  CommonReferencesSchemaProps,
  InfrastructureReferencesSchemaProps,
} from "@/schemas/references"
import { db } from "@/lib/db"
import { FieldGroup } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { useAppForm, useFormFields } from "@/components/ui/tanstack-form"
import { useNavigate } from "@tanstack/react-router"
import { usePermission } from "@/hook/useSettingsQuery"

export default function InfrastructureForm({
  defaultValues,
  isEdit,
  pictogram,
  references,
}: {
  defaultValues: InfrastructureDataSchemaProps
  isEdit?: boolean
  pictogram?: { url?: string }
  references: [InfrastructureReferencesSchemaProps, CommonReferencesSchemaProps]
}) {
  const navigate = useNavigate()

  const [
    {
      infrastructuretype,
      infrastructurecondition,
      infrastructuremaintenancedifficultylevel,
      infrastructureusagedifficultylevel,
    },
    { structure, accessmean },
  ] = references

  const {
    id,
    date_insert,
    date_update: _dateUpdate,
    ...defaultValuesForForm
  } = defaultValues

  const validators = infrastructureDataSchema.omit({
    id: true,
    date_insert: true,
    date_update: true,
  })
  const form = useAppForm({
    defaultValues: defaultValuesForForm,
    validators: {
      onBlur: validators,
      onSubmit: validators,
    },
    onSubmit: async ({ value }) => {
      const nextId = isEdit
        ? await db.infrastructureData.put({
            ...value,
            id,
            date_insert,
            date_update: new Date().toISOString(),
          })
        : // @ts-expect-error "id" is auto-incremented in indexedDB
          await db.infrastructureData.add({
            ...value,
            date_insert: new Date().toISOString(),
            date_update: new Date().toISOString(),
          })

      navigate({
        to: "/{-$locale}/data/$type/$id",
        params: {
          type: "infrastructure",
          id: nextId,
        },
      })

      toast.success(
        isEdit
          ? `L'aménagement "${value.name}" a bien été modifié`
          : `L'aménagement "${value.name}" a bien été créé`,
        {
          position: "top-center",
        }
      )
    },
  })
  const { FormTextField, FormSelectField, FormTextareaField, FormGeomField } =
    useFormFields<InfrastructureDataSchemaProps>()

  const { can_bypass_structure, is_superuser } = usePermission()

  return (
    <form.AppForm>
      <form.Form>
        <FieldGroup className="mb-4">
          <FormTextField name="name" label="Nom" required />

          <FormSelectField
            name="type"
            label="Type"
            list={infrastructuretype}
            required
          />

          {can_bypass_structure && is_superuser && (
            <FormSelectField
              name="structure"
              label="Structure liée"
              list={structure}
              required
            />
          )}

          <FormTextareaField name="description" label="Description" isRTE />

          <FormGeomField
            name="api_geom.coordinates"
            label="Localisation"
            icon={pictogram}
            required
          />

          <FormTextareaField name="accessibility" label="Accessibilité" isRTE />

          <FormSelectField
            name="conditions"
            label="État"
            list={infrastructurecondition}
            multiple
          />

          <FormSelectField
            name="access"
            label="Moyen d'accès"
            list={accessmean}
          />

          <FormTextField
            name="implantation_year"
            label="Année d'implantation"
            type="number"
            min="0"
          />

          <FormSelectField
            name="usage_difficulty"
            label="Niveau des usagers"
            list={infrastructureusagedifficultylevel}
            description="Niveau de dangerosité de l'aménagement pour les usagers"
          />

          <FormSelectField
            name="maintenance_difficulty"
            label="Niveau des interventions"
            list={infrastructuremaintenancedifficultylevel}
            description="Niveau de dangerosité des interventions d'entretien"
          />

          <Button type="submit">
            {isEdit ? "Modifier" : "Créer"} la signalétique
          </Button>
        </FieldGroup>
      </form.Form>
    </form.AppForm>
  )
}
