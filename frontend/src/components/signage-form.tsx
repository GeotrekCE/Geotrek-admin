import { toast } from "sonner"
import { signageDataSchema, type SignageDataSchemaProps } from "@/schemas/data"

import type {
  CommonReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import { db } from "@/lib/db"
import { FieldGroup } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { useAppForm, useFormFields } from "@/components/ui/tanstack-form"
import { useNavigate } from "@tanstack/react-router"
import { usePermission } from "@/hook/useSettingsQuery"
import { useLiveQuery } from "dexie-react-hooks"
import { m } from "@/paraglide/messages"

export default function SignageForm({
  defaultValues,
  isEdit,
  pictogram,
  references,
}: {
  defaultValues: SignageDataSchemaProps
  isEdit?: boolean
  pictogram?: { url?: string }
  references: [SignageReferencesSchemaProps, CommonReferencesSchemaProps]
}) {
  const navigate = useNavigate()

  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "signage",
        id: isEdit ? defaultValues.id : undefined,
      })
      .first()
  )

  const [
    { signagetype, signagecondition, sealing },
    { structure, accessmean, organism },
  ] = references

  const {
    id,
    date_insert,
    date_update: _dateUpdate,
    ...defaultValuesForForm
  } = defaultValues

  const validators = signageDataSchema.omit({
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
          reference: "signage",
        })
      }
      const nextId = isEdit
        ? await db.signageData.put({
            ...value,
            id,
            date_insert,
            date_update: new Date().toISOString(),
            appSynced: false,
          })
        : // @ts-expect-error "id" is auto-incremented in indexedDB
          await db.signageData.add({
            ...value,
            date_insert: new Date().toISOString(),
            date_update: new Date().toISOString(),
            appSynced: false,
            appNewItem: true,
          })

      navigate({
        to: "/{-$locale}/data/$type/$id",
        params: {
          type: "signage",
          id: nextId,
        },
      })

      toast.success(
        isEdit
          ? m["common.edit-success"]({
              item: `${m["content.signage"]()} "${value.name}"`,
            })
          : m["common.create-success"]({
              item: `${m["content.signage"]()} "${value.name}"`,
            }),
        {
          position: "top-center",
        }
      )
    },
  })
  const { FormTextField, FormSelectField, FormTextareaField, FormGeomField } =
    useFormFields<SignageDataSchemaProps>()

  const { can_bypass_structure, is_superuser } = usePermission()

  return (
    <form.AppForm>
      <form.Form>
        <FieldGroup className="mb-4">
          <FormTextField name="name" label={m["form.name"]()} required />

          <FormSelectField
            name="type"
            label={m["form.type"]()}
            list={signagetype}
            required
          />

          {can_bypass_structure && is_superuser && (
            <FormSelectField
              name="structure"
              label={m["form.structure"]()}
              list={structure}
              required
            />
          )}

          <FormTextareaField
            name="description"
            label={m["form.description"]()}
            isRTE
          />

          <FormGeomField
            name="geom"
            label={m["form.location"]()}
            icon={pictogram}
            required
          />

          <FormSelectField
            name="conditions"
            label={m["form.state"]()}
            list={signagecondition}
            multiple
          />

          <FormTextField
            name="implantation_year"
            label={m["form.implantation-year"]()}
            type="number"
            min="0"
          />

          <FormTextField name="code" label={m["content.code"]()} />

          <FormTextField
            name="printed_elevation"
            label={m["content.displayed-elevation"]()}
            type="number"
            min="0"
          />

          <FormSelectField
            name="manager"
            label={m["content.manager"]()}
            list={organism}
          />

          <FormSelectField
            name="sealing"
            label={m["content.sealing"]()}
            list={sealing}
          />

          <FormSelectField
            name="access"
            label={m["form.access"]()}
            list={accessmean}
          />

          <Button type="submit">
            {isEdit ? m["form.edit"]() : m["form.create"]()}{" "}
            {m["content.signage"]().toLowerCase()}
          </Button>
          {rawDataItem && (
            <Button
              type="button"
              variant="destructive"
              onClick={async () => {
                await db.rawData
                  .where({ reference: "signage", id: rawDataItem.id })
                  .delete()
                const { reference: _reference, ...restoredData } = rawDataItem
                await db.signageData.put(restoredData as SignageDataSchemaProps)
                toast.success(
                  m["common.restore-success"]({ item: m["content.signage"]() }),
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
