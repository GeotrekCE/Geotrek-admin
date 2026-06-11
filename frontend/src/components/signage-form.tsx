import { toast } from "sonner"
import { signageDataSchema, type SignageDataSchemaProps } from "@/schemas/data"
import { FieldGroup } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import {
  useReferencesQuery,
  type StoredReferences,
} from "@/hook/useReferencesQuery"

import { useAppForm, useFormFields } from "./ui/tanstack-form"

export default function SignageForm({
  defaultValues,
  pictogram,
  isEdit,
}: {
  defaultValues: Omit<
    SignageDataSchemaProps[0],
    "id" | "date_insert" | "date_update" | "published"
  >
  pictogram?: { url?: string }
  isEdit?: boolean
}) {
  const validators = signageDataSchema.unwrap().omit({
    id: true,
    date_insert: true,
    date_update: true,
    published: true,
  })
  const form = useAppForm({
    defaultValues,
    validators: {
      onBlur: validators,
      onSubmit: validators,
    },
    onSubmit: ({ value }) => {
      toast(
        <pre className="max-h-80 w-max overflow-auto">
          {JSON.stringify(value, null, 2)}
        </pre>,
        {
          position: "top-center",
          dismissible: false,
        }
      )
    },
  })
  const { FormTextField, FormSelectField, FormTextareaField, FormGeomField } =
    useFormFields<SignageDataSchemaProps[0]>()

  const stored: StoredReferences = useReferencesQuery()

  const structureList = stored.references.common.data?.structure ?? []

  const typeList = stored.references.signage.data?.signagetype ?? []

  const conditionList = stored.references.signage.data?.signagecondition ?? []

  const sealingList = stored.references.signage.data?.sealing ?? []

  const accessList = stored.references.common.data?.accessmean ?? []

  const managerList = stored.references.common.data?.organism ?? []

  return (
    <form.AppForm>
      <form.Form>
        <FieldGroup className="mb-4">
          <FormTextField name="name" label="Nom" required />

          <FormSelectField name="type" label="Type" list={typeList} required />

          <FormSelectField
            name="structure"
            label="Structure liée"
            list={structureList}
            required
          />

          <FormTextareaField name="description" label="Description" />

          <FormGeomField
            name="api_geom.coordinates"
            label="Localisation"
            icon={pictogram}
            required
          />

          <FormSelectField
            name="conditions"
            label="État"
            list={conditionList}
            multiple
          />

          <FormTextField
            name="implantation_year"
            label="Année d'implantation"
            type="number"
            min="0"
          />

          <FormTextField name="code" label="Code" />

          <FormTextField
            name="printed_elevation"
            label="Altitude affichée"
            type="number"
            min="0"
          />

          <FormSelectField
            name="manager"
            label="Gestionnaire"
            list={managerList}
          />

          <FormSelectField
            name="sealing"
            label="Scellement"
            list={sealingList}
          />

          <FormSelectField
            name="access"
            label="Moyen d'accès"
            list={accessList}
          />

          <Button type="submit">
            {isEdit ? "Modifier" : "Créer"} la signalétique
          </Button>
        </FieldGroup>
      </form.Form>
    </form.AppForm>
  )
}
