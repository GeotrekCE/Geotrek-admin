import { toast } from "sonner"
import { reportDataSchema, type ReportDataSchemaProps } from "@/schemas/data"

import type { ReportReferencesSchemaProps } from "@/schemas/references"
import { db } from "@/lib/db"
import { FieldGroup } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { useAppForm, useFormFields } from "@/components/ui/tanstack-form"
import { useNavigate } from "@tanstack/react-router"
import { useLiveQuery } from "dexie-react-hooks"
import { m } from "@/paraglide/messages"

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
      if (isEdit && value.appNewItem !== true) {
        await db.rawData.add({
          ...defaultValues,
          reference: "report",
          appSynced: false,
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
            appSynced: false,
            appNewItem: true,
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
          ? m["common.edit-success"]({ item: m["content.report"]() })
          : m["common.create-success"]({ item: m["content.report"]() }),
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
          <FormTextField name="email" label={m["form.email"]()} type="email" />

          <FormTextareaField
            name="comment"
            label={m["form.description"]()}
            isRTE
          />

          <FormGeomField
            name="geom.coordinates"
            label={m["form.location"]()}
            icon={pictogram}
            required
          />

          <FormSelectField
            name="activity"
            label={m["form.activity"]()}
            list={reportactivity}
          />

          <FormSelectField
            name="category"
            label={m["form.category"]()}
            list={reportcategory}
          />

          <FormSelectField
            name="problem_magnitude"
            label={m["form.problem-magnitude"]()}
            list={reportproblemmagnitude}
          />

          <Button type="submit">
            {isEdit ? m["form.edit"]() : m["form.create"]()}{" "}
            {m["content.report"]().toLowerCase()}
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
                toast.success(
                  m["common.restore-success"]({ item: m["content.report"]() }),
                  {
                    position: "top-center",
                  }
                )
              }}
            >
              {m["content.restore-pending"]()}
            </Button>
          )}
        </FieldGroup>
      </form.Form>
    </form.AppForm>
  )
}
