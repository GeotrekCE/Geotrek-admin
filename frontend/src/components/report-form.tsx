import { toast } from "sonner"
import { reportDataSchema, type ReportDataSchemaProps } from "@/schemas/data"

import type { ReportReferencesSchemaProps } from "@/schemas/references"
import { db } from "@/lib/db"
import { FieldGroup } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { useAppForm, useFormFields } from "@/components/ui/tanstack-form"
import { useNavigate } from "@tanstack/react-router"
import { useLiveQuery } from "dexie-react-hooks"
import { dateCompare } from "@/lib/date"

export default function ReportForm({
  defaultValues,
  isEdit,
  pictogram,
  references,
}: {
  defaultValues: ReportDataSchemaProps
  isEdit?: boolean
  pictogram?: { url?: string }
  references: [ReportReferencesSchemaProps]
}) {
  const navigate = useNavigate()

  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "report",
        id: isEdit ? defaultValues.id : undefined,
      })
      .first()
  )
  const syncData = useLiveQuery(() => db.appSync.get("data"))

  const isAsyncItem =
    dateCompare(defaultValues.date_insert, syncData?.lastSync) > -1

  const [{ reportactivity, reportcategory, reportproblemmagnitude }] =
    references

  const {
    id,
    date_insert,
    date_update: _dateUpdate,
    ...defaultValuesForForm
  } = defaultValues

  const validators = reportDataSchema.omit({
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
      if (isEdit && !isAsyncItem) {
        await db.rawData.add({
          ...defaultValues,
          reference: "report",
          synced: false,
        })
      }
      const nextId = isEdit
        ? await db.reportData.put({
            ...value,
            id,
            date_insert,
            date_update: new Date().toISOString(),
          })
        : // @ts-expect-error "id" is auto-incremented in indexedDB
          await db.reportData.add({
            ...value,
            date_insert: new Date().toISOString(),
            date_update: new Date().toISOString(),
            synced: false,
          })

      navigate({
        to: "/{-$locale}/data/$type/$id",
        params: {
          type: "report",
          id: nextId,
        },
      })

      toast.success(
        isEdit
          ? "Le signalement a bien été modifié"
          : "Le signalement a bien été créé",
        {
          position: "top-center",
        }
      )
    },
  })
  const { FormTextField, FormSelectField, FormTextareaField, FormGeomField } =
    useFormFields<ReportDataSchemaProps>()

  return (
    <form.AppForm>
      <form.Form>
        <FieldGroup className="mb-4">
          <FormTextField name="email" label="Courriel" type="email" />

          <FormTextareaField name="comment" label="Description" isRTE />

          <FormGeomField
            name="geom.coordinates"
            label="Localisation"
            icon={pictogram}
            required
          />

          <FormSelectField
            name="activity"
            label="Activité"
            list={reportactivity}
          />

          <FormSelectField
            name="category"
            label="Catégorie"
            list={reportcategory}
          />

          <FormSelectField
            name="problem_magnitude"
            label="Amplitude du problème"
            list={reportproblemmagnitude}
          />

          <Button type="submit">
            {isEdit ? "Modifier" : "Créer"} le signalement
          </Button>

          {rawDataItem && (
            <Button
              type="button"
              variant="destructive"
              onClick={async () => {
                await db.rawData
                  .where({ reference: "report", id: rawDataItem.id })
                  .delete()
                const { reference: _reference, ...restoredData } = rawDataItem
                await db.reportData.put(restoredData as ReportDataSchemaProps)
                toast.success("Restoration du signalement terminée", {
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
