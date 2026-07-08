import { toast } from "sonner"
import {
  interventionDataSchema,
  type InterventionDataSchemaProps,
} from "@/schemas/data"

import type {
  CommonReferencesSchemaProps,
  InterventionReferencesSchemaProps,
} from "@/schemas/references"
import { db } from "@/lib/db"
import { FieldGroup } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { useAppForm, useFormFields } from "@/components/ui/tanstack-form"
import { useNavigate } from "@tanstack/react-router"
import { FormCheckboxField } from "./forms"
import { Trash } from "lucide-react"
import { usePermission } from "@/hook/useSettingsQuery"
import { useLiveQuery } from "dexie-react-hooks"

export default function InterventionForm({
  defaultValues,
  isEdit,
  pictogram,
  references,
}: {
  defaultValues: InterventionDataSchemaProps
  isEdit?: boolean
  pictogram?: { url?: string }
  references: [InterventionReferencesSchemaProps, CommonReferencesSchemaProps]
}) {
  const navigate = useNavigate()

  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "intervention",
        id: isEdit ? defaultValues.id : undefined,
      })
      .first()
  )

  const [
    {
      interventiontype,
      interventiondisorder,
      interventionjob,
      interventionstatus,
      stake,
    },
    { accessmean, structure },
  ] = references

  const {
    id,
    date_insert,
    date_update: _dateUpdate,
    ...defaultValuesForForm
  } = defaultValues

  const validators = interventionDataSchema.omit({
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
      if (isEdit && value.appNewItem !== true) {
        await db.rawData.put({
          ...defaultValues,
          reference: "intervention",
        })
      }
      const nextId = isEdit
        ? await db.interventionData.put({
            ...value,
            id,
            date_insert,
            date_update: new Date().toISOString(),
            appSynced: false,
          })
        : // @ts-expect-error "id" is auto-incremented in indexedDB
          await db.interventionData.add({
            ...value,
            date_insert: new Date().toISOString(),
            date_update: new Date().toISOString(),
            appSynced: false,
            appNewItem: true,
          })

      navigate({
        to: "/{-$locale}/data/$type/$id",
        params: {
          type: "intervention",
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
    useFormFields<InterventionDataSchemaProps>()

  const { can_bypass_structure, is_superuser } = usePermission()

  return (
    <form.AppForm>
      <form.Form>
        <FieldGroup className="mb-4">
          <FormTextField name="name" label="Nom" required />

          <FormSelectField name="type" label="Type" list={interventiontype} />

          <FormCheckboxField name="subcontracting" label="Sous-traitance" />

          {can_bypass_structure && is_superuser && (
            <FormSelectField
              name="structure"
              label="Structure liée"
              list={structure}
              required
            />
          )}

          <FormTextField
            name="begin_date"
            label="Date de début"
            type="date"
            required
          />

          <FormTextField
            name="end_date"
            label="Date de fin"
            type="date"
            validators={{
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              onBlur({ value, fieldApi }: { value: string; fieldApi: any }) {
                const beginDateValue = fieldApi.form.getFieldValue("begin_date")
                if (
                  beginDateValue &&
                  value &&
                  value.localeCompare(beginDateValue) === -1
                ) {
                  return {
                    message: "La date de début est après la date de fin",
                  }
                }
                return null
              },
            }}
          />

          <FormSelectField
            name="status"
            label="Statut"
            list={interventionstatus}
            required
          />

          <FormTextareaField name="description" label="Description" isRTE />

          <FormGeomField
            name="geom.coordinates"
            label="Localisation"
            icon={pictogram}
            required
            description="Les interventions de type linéaire ne sont pas encore pris en charge."
          />

          <FormSelectField
            name="disorders"
            label="État"
            list={interventiondisorder}
            multiple
          />

          {/* <FormTextField
            name="length"
            label="Longueur"
            type="number"
            min="0"
            readOnly
            description="Valeur calculée automatiquement"
          /> */}

          <FormTextField name="width" label="Largeur" type="number" min="0" />

          <FormTextField name="height" label="Hauteur" type="number" min="0" />

          <FormSelectField name="stake" label="Enjeu" list={stake} />

          <FormSelectField
            name="access"
            label="Moyen d'accès"
            list={accessmean}
          />

          <form.Field name="man_day" mode="array">
            {(field) => (
              <fieldset className="flex flex-col flex-wrap items-start">
                <legend className="mt-3">Jours-Hommes</legend>
                {field.state.value?.map((_item, index: number) => (
                  <div key={index} className="items-starts my-3 flex gap-5">
                    <FormTextField
                      name={`man_day[${index}].nb_days`}
                      label="Temps en jours"
                      type="number"
                      className="w-40"
                      step="0.01"
                    />

                    <FormSelectField
                      name={`man_day[${index}].job`}
                      label="Fonction"
                      list={interventionjob}
                      className="w-full"
                      required
                    />

                    <Button
                      className="mt-8"
                      type="button"
                      variant="destructive"
                      size="icon"
                      onClick={() => {
                        field.removeValue(index)
                      }}
                    >
                      <Trash aria-hidden />

                      <span className="sr-only">Enlever</span>
                    </Button>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    field.pushValue({
                      job: interventionjob[0],
                      nb_days: 0,
                    })
                  }}
                >
                  Ajouter
                </Button>
              </fieldset>
            )}
          </form.Field>

          <Button type="submit">
            {isEdit ? "Modifier" : "Créer"} l'intervention
          </Button>

          {rawDataItem && (
            <Button
              type="button"
              variant="destructive"
              onClick={async () => {
                await db.rawData
                  .where({ reference: "intervention", id: rawDataItem.id })
                  .delete()
                const { reference: _reference, ...restoredData } = rawDataItem
                await db.interventionData.put(
                  restoredData as InterventionDataSchemaProps
                )
                toast.success("Restoration de l'intervention terminée", {
                  position: "top-center",
                })
              }}
            >
              Annuler les modifications en attente
            </Button>
          )}
        </FieldGroup>
      </form.Form>
    </form.AppForm>
  )
}
