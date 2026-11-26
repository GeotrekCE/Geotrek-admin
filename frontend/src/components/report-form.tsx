import * as React from "react"
import { toast } from "sonner"
import { reportDataSchema, type ReportDataSchemaProps } from "@/schemas/data"

import type { ReportReferencesSchemaProps } from "@/schemas/references"
import { db } from "@/lib/db"
import { FieldGroup } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { useAppForm, useFormFields } from "@/components/ui/tanstack-form"
import { useNavigate } from "@tanstack/react-router"
import { m } from "@/paraglide/messages"
import { FormUploadGallery } from "@/components/form-upload-gallery"
import { type AttachmentsSchemaProps } from "@/schemas/attachments"
import { useIsFieldVisible } from "@/hook/useSettingsQuery"

export default function ReportForm({
  defaultValues,
  isEdit,
  pictogram,
  references,
}: {
  defaultValues: ReportDataSchemaProps & AttachmentsSchemaProps
  isEdit?: boolean
  pictogram: { url?: string }
  references: [ReportReferencesSchemaProps]
}) {
  const navigate = useNavigate()

  const [formIsDirty, setFormIsDirty] = React.useState(false)

  const [
    { reportactivity, reportcategory, reportproblemmagnitude, reportstatus },
  ] = references

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
    appSynced: true,
    appNewItem: true,
  })
  const handleChange = () => {
    setFormIsDirty(true)
  }
  const form = useAppForm({
    defaultValues: defaultValuesForForm,
    validators: {
      onBlur: validators,
      onSubmit: validators,
      onChange: handleChange,
    },
    onSubmit: async ({ value: { attachments: rawAttachments, ...value } }) => {
      setFormIsDirty(false)
      const attachments = rawAttachments?.filter(
        (attachment) => attachment.value !== null
      )
      const hasRawData = await db.rawData.get({ id, reference: "report" })
      if (isEdit && value.appNewItem !== true && !hasRawData) {
        await db.rawData.add({
          ...defaultValues,
          reference: "report",
        })
      }
      const nextId = isEdit
        ? await db.reportData.put({
            ...value,
            id,
            attachments,
            date_insert,
            date_update: new Date().toISOString(),
            appSynced: false,
          })
        : // @ts-expect-error "id" is auto-incremented in indexedDB
          await db.reportData.add({
            ...value,
            attachments,
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
  const isVisible = useIsFieldVisible("report")

  return (
    <form.AppForm>
      <form.Form>
        <FieldGroup className="mb-4">
          {isVisible("email") && (
            <FormTextField
              name="email"
              label={m["form.email"]()}
              type="email"
            />
          )}

          {isVisible("comment") && (
            <FormTextareaField
              name="comment"
              label={m["form.description"]()}
              isRTE
            />
          )}

          {isVisible("geom") && (
            <FormGeomField
              name="geom"
              label={m["form.location"]()}
              reference="report"
              pictogram={pictogram}
              required
            />
          )}

          {isVisible("activity") && (
            <FormSelectField
              name="activity"
              label={m["form.activity"]()}
              list={reportactivity}
            />
          )}

          {isVisible("category") && (
            <FormSelectField
              name="category"
              label={m["form.category"]()}
              list={reportcategory}
            />
          )}

          {isVisible("problem_magnitude") && (
            <FormSelectField
              name="problem_magnitude"
              label={m["form.problem-magnitude"]()}
              list={reportproblemmagnitude}
            />
          )}

          {isVisible("status") && (
            <FormSelectField
              name="status"
              label={m["form.status"]()}
              list={reportstatus}
            />
          )}

          <FormUploadGallery />

          <Button type="submit" className="h-12">
            {isEdit
              ? m["form.edit"]()
              : `${m["form.create"]()} ${m["content.report"]().toLowerCase()}`}
          </Button>

          {formIsDirty && (
            <Button
              onClick={(event) => {
                event.preventDefault()
                form.reset()
                setFormIsDirty(false)
              }}
              type="reset"
              variant="destructive"
              className="h-12"
            >
              {m["form.reset"]()}
            </Button>
          )}
        </FieldGroup>
      </form.Form>
    </form.AppForm>
  )
}
