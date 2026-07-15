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
import { m } from "@/paraglide/messages"

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
          ? m["common.edit-success"]({
              item: `${m["content.intervention"]()} "${value.name}"`,
            })
          : m["common.create-success"]({
              item: `${m["content.intervention"]()} "${value.name}"`,
            }),
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
          <FormTextField name="name" label={m["form.name"]()} required />

          <FormSelectField
            name="type"
            label={m["form.type"]()}
            list={interventiontype}
          />

          <FormCheckboxField
            name="subcontracting"
            label={m["form.outsourcing"]()}
          />

          {can_bypass_structure && is_superuser && (
            <FormSelectField
              name="structure"
              label={m["form.structure"]()}
              list={structure}
              required
            />
          )}

          <FormTextField
            name="begin_date"
            label={m["form.begin-date"]()}
            type="date"
            required
          />

          <FormTextField
            name="end_date"
            label={m["form.end-date"]()}
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
            label={m["form.status"]()}
            list={interventionstatus}
            required
          />

          <FormTextareaField
            name="description"
            label={m["form.description"]()}
            isRTE
          />

          <FormGeomField
            name="geom.coordinates"
            label={m["form.location"]()}
            icon={pictogram}
            required
            description={m["form.geom-description"]()}
          />

          <FormSelectField
            name="disorders"
            label={m["form.state"]()}
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

          <FormTextField
            name="width"
            label={m["form.width"]()}
            type="number"
            min="0"
          />

          <FormTextField
            name="height"
            label={m["form.height"]()}
            type="number"
            min="0"
          />

          <FormSelectField
            name="stake"
            label={m["form.stake"]()}
            list={stake}
          />

          <FormSelectField
            name="access"
            label={m["form.access"]()}
            list={accessmean}
          />

          <form.Field name="man_day" mode="array">
            {(field) => (
              <fieldset className="flex flex-col flex-wrap items-start">
                <legend className="mt-3">{m["form.man-days"]()}</legend>
                {field.state.value?.map((_item, index: number) => (
                  <div key={index} className="items-starts my-3 flex gap-5">
                    <FormTextField
                      name={`man_day[${index}].nb_days`}
                      label={m["form.time-in-days"]()}
                      type="number"
                      className="w-40"
                      step="0.01"
                    />

                    <FormSelectField
                      name={`man_day[${index}].job`}
                      label={m["form.job"]()}
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

                      <span className="sr-only">{m["form.remove"]()}</span>
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
                  {m["form.add"]()}
                </Button>
              </fieldset>
            )}
          </form.Field>

          <Button type="submit">
            {isEdit ? m["form.edit"]() : m["form.create"]()}{" "}
            {m["content.intervention"]().toLowerCase()}
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
                toast.success(
                  m["common.restore-success"]({
                    item: m["content.intervention"](),
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
