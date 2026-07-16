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
import { useLiveQuery } from "dexie-react-hooks"
import { m } from "@/paraglide/messages"

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

  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "infrastructure",
        id: isEdit ? defaultValues.id : undefined,
      })
      .first()
  )

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
      if (isEdit && value.appNewItem !== true) {
        await db.rawData.put({
          ...defaultValues,
          reference: "infrastructure",
        })
      }
      const nextId = isEdit
        ? await db.infrastructureData.put({
            ...value,
            id,
            date_insert,
            date_update: new Date().toISOString(),
            appSynced: false,
          })
        : // @ts-expect-error "id" is auto-incremented in indexedDB
          await db.infrastructureData.add({
            ...value,
            date_insert: new Date().toISOString(),
            date_update: new Date().toISOString(),
            appSynced: false,
            appNewItem: true,
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
          ? m["common.edit-success"]({
              item: `${m["content.infrastructure"]()} "${value.name}"`,
            })
          : m["common.create-success"]({
              item: `${m["content.infrastructure"]()} "${value.name}"`,
            }),
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
          <FormTextField name="name" label={m["form.name"]()} required />

          <FormSelectField
            name="type"
            label={m["form.type"]()}
            list={infrastructuretype}
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

          <FormTextareaField
            name="accessibility"
            label={m["form.accessibility"]()}
            isRTE
          />

          <FormSelectField
            name="conditions"
            label={m["form.state"]()}
            list={infrastructurecondition}
            multiple
          />

          <FormSelectField
            name="access"
            label={m["form.access"]()}
            list={accessmean}
          />

          <FormTextField
            name="implantation_year"
            label={m["form.implantation-year"]()}
            type="number"
            min="0"
          />

          <FormSelectField
            name="usage_difficulty"
            label={m["form.user-level"]()}
            list={infrastructureusagedifficultylevel}
            description={m["form.user-level-description"]()}
          />

          <FormSelectField
            name="maintenance_difficulty"
            label={m["form.maintenance-level"]()}
            list={infrastructuremaintenancedifficultylevel}
            description={m["form.maintenance-level-description"]()}
          />

          <Button type="submit">
            {isEdit ? m["form.edit"]() : m["form.create"]()}{" "}
            {m["content.infrastructure"]().toLowerCase()}
          </Button>
          {rawDataItem && (
            <Button
              type="button"
              variant="destructive"
              onClick={async () => {
                await db.rawData
                  .where({ reference: "infrastructure", id: rawDataItem.id })
                  .delete()
                const { reference: _reference, ...restoredData } = rawDataItem
                await db.infrastructureData.put(
                  restoredData as InfrastructureDataSchemaProps
                )
                toast.success(
                  m["common.restore-success"]({
                    item: m["content.infrastructure"](),
                  }),
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
