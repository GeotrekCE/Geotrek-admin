import { Button } from "@/components/ui/button"
import { useFormContext } from "@/components/ui/form-context"
import { FormFileUploadField } from "@/components/forms/file-upload-field"
import { m } from "@/paraglide/messages"

export function FormUploadGallery() {
  const form = useFormContext()

  return (
    <fieldset className="my-8">
      <legend className="mb-2 text-xl font-bold text-accent-foreground">
        {m["form.attachments-photo-title"]()}
      </legend>
      <form.AppField name="attachments" mode="array">
        {(field) => (
          <div className="flex flex-wrap gap-4">
            <ul className="contents">
              {field.state.value?.map((_item: null | File, index: number) => (
                <li key={index} className="flex flex-col items-center gap-2">
                  <FormFileUploadField
                    name={`attachments[${index}].value`}
                    label={`${m["form.attachments-photo-item"]()} ${index + 1}`}
                    accept="image/*"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      field.removeValue(index)
                    }}
                  >
                    {m["common.delete"]()}
                  </Button>
                </li>
              ))}
              <li className="col-span-full text-sm text-accent-foreground">
                <FormFileUploadField
                  name={`attachments[${field.state.value?.length || 0}].value`}
                  label={`${m["form.attachments-photo-item"]()} ${field.state.value?.length ? field.state.value.length + 1 : 1}`}
                  accept="image/*"
                  onChangeCapture={() => {
                    field.pushValue({ value: null })
                  }}
                />
              </li>
            </ul>
          </div>
        )}
      </form.AppField>
    </fieldset>
  )
}
