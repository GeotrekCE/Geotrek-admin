import { Plus } from "lucide-react"
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
            </ul>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                field.pushValue({ value: null })
              }}
              className="flex size-30 items-center justify-center rounded-lg bg-primary/15"
            >
              <Plus className="size-8 text-primary/90" aria-hidden />
              <span className="sr-only">
                {m["form.attachments-photo-add"]()}
              </span>
            </Button>
          </div>
        )}
      </form.AppField>
    </fieldset>
  )
}
